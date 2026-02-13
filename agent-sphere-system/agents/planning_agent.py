"""
Updated planning_agent.py - Orchestrates both built-in and custom agents
"""


import json
import re
from typing import Dict, List, Optional
from base.agent_framework import Agent, Tool
import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"
API_BASE_URL = "http://localhost:5000/api"  # For calling custom agent endpoints


class LLMSequentialOrchestrator:
    """Uses LLM to coordinate both built-in and custom agents sequentially"""
    
    def __init__(self, agents_dict: Dict[str, Agent], custom_agents_manager=None):
        self.agents = agents_dict  # Built-in agents
        self.custom_agents_manager = custom_agents_manager  # Custom agents
        self.execution_log = []
        self.max_steps = 5
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """Call LLM via router (Ollama/Claude/GPT-4o/Gemini with failover)"""
        try:
            from llm.llm_router import llm_router
            return llm_router.chat(messages)
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def analyze_request(self, user_request: str) -> Dict:
        """Analyze request to determine which agents are needed"""
        available_agents = list(self.agents.keys())
        available_custom_agents = []
        
        if self.custom_agents_manager:
            custom_agents = self.custom_agents_manager.custom_agents.values()
            available_custom_agents = [
                {"id": a["id"], "name": a["name"], "role": a["role"]}
                for a in custom_agents
                if a.get("status") == "published"
            ]
        
        custom_agents_text = ""
        if available_custom_agents:
            custom_agents_text = "\n\nCustom Agents:\n"
            for agent in available_custom_agents:
                custom_agents_text += f"- {agent['name']} ({agent['id']}): {agent['role']}\n"
        
        analysis_prompt = f"""You are an intelligent task orchestrator. Analyze the user request and determine:
1. Which agent(s) should be called and in what order
2. The reasoning for this sequence
3. What each agent should do

Available Built-in AGENTS:
- home: Control smart home devices, lights, thermostat, security
- calendar: Manage calendar events, emails, scheduling
- finance: Handle budgets, transactions, investments, financial goals
{custom_agents_text}

User Request: "{user_request}"

IMPORTANT: When responding with agent names, use the EXACT names or IDs from the lists above.

Respond in this exact JSON format (no markdown, just raw JSON):
{{
  "reasoning": "Brief explanation of why this approach",
  "agents_needed": ["agent_id_or_name"],
  "execution_steps": [
    {{
      "step": 1,
      "agent": "exact_agent_id_or_name",
      "task": "What this agent should do",
      "context": "Any specific context or instructions"
    }}
  ]
}}"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a task orchestration AI. Always respond with valid JSON only. Use exact agent names from the provided list."
            },
            {
                "role": "user",
                "content": analysis_prompt
            }
        ]
        
        llm_response = self._call_ollama(messages)
        analysis = self._parse_analysis(llm_response, user_request)
        
        return analysis
    
    def _parse_analysis(self, llm_response: str, user_request: str) -> Dict:
        """Parse LLM response"""
        analysis = {
            "user_request": user_request,
            "detected_agents": [],
            "execution_steps": [],
            "reasoning": "",
            "llm_analysis": llm_response
        }
        
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                llm_plan = json.loads(json_str)
                
                analysis["reasoning"] = llm_plan.get("reasoning", "")
                analysis["detected_agents"] = llm_plan.get("agents_needed", [])
                
                valid_steps = llm_plan.get("execution_steps", [])
                if valid_steps:
                    analysis["execution_steps"] = valid_steps
                else:
                    analysis["execution_steps"] = [{
                        "step": 1,
                        "agent": "home",
                        "task": "Handle user request",
                        "context": user_request
                    }]
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            analysis["execution_steps"] = [{
                "step": 1,
                "agent": "home",
                "task": "Handle user request",
                "context": user_request
            }]
        
        return analysis
    

    def execute_sequential_plan(self, plan: Dict) -> Dict:
        """Execute agents sequentially"""
        results = {
            "steps_executed": [],
            "final_response": "",
            "success": True,
            "errors": []
        }
        
        context = f"User Request: {plan['user_request']}\n\n"
        original_user_request = plan['user_request']  # Store original request
        
        for step_index, step in enumerate(plan["execution_steps"][:self.max_steps]):
            try:
                agent_id = step.get("agent")
                task = step.get("task")
                step_context = step.get("context", "")
                
                # Clean up agent_id and try multiple lookup strategies
                import re
                original_agent_id = agent_id
                
                # Strategy 1: Try to extract ID from parentheses (e.g., "Hello World (a74fba99)")
                id_match = re.search(r'\(([a-f0-9]{8})\)', agent_id)
                if id_match:
                    agent_id = id_match.group(1)
                    logger.info(f"[AGENT LOOKUP] Extracted ID from parentheses: {agent_id}")
                
                agent = None
                agent_type = None
                
                # Strategy 2: Check if it's a built-in agent (exact match)
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    agent_type = "built-in"
                    logger.info(f"[AGENT LOOKUP] Found built-in agent: {agent_id}")
                
                # Strategy 3: Check if it's a custom agent by ID
                elif self.custom_agents_manager:
                    custom_agent = self.custom_agents_manager.get_agent(agent_id)
                    if custom_agent:
                        agent = custom_agent
                        agent_type = "custom"
                        logger.info(f"[AGENT LOOKUP] Found custom agent by ID: {agent_id}")
                    else:
                        # Strategy 4: Try finding by name (case-insensitive, exact match)
                        agent_name_lower = agent_id.lower().strip()
                        original_name_lower = original_agent_id.lower().strip()
                        
                        for ca in self.custom_agents_manager.custom_agents.values():
                            ca_name = ca.get("name", "").lower().strip()
                            
                            # Try matching against both the processed and original agent_id
                            if ca_name == agent_name_lower or ca_name == original_name_lower:
                                agent = ca
                                agent_type = "custom"
                                agent_id = ca.get("id")  # Use ID for API call
                                logger.info(f"[AGENT LOOKUP] Found custom agent by name: '{ca.get('name')}' -> ID: {agent_id}")
                                break
                        
                        # Strategy 5: Try partial name matching (if name is contained in agent_id or vice versa)
                        if not agent:
                            for ca in self.custom_agents_manager.custom_agents.values():
                                ca_name = ca.get("name", "").lower().strip()
                                
                                if ca_name in original_name_lower or original_name_lower in ca_name:
                                    agent = ca
                                    agent_type = "custom"
                                    agent_id = ca.get("id")
                                    logger.info(f"[AGENT LOOKUP] Found custom agent by partial match: '{ca.get('name')}' -> ID: {agent_id}")
                                    break
                
                if not agent:
                    # List available agents for debugging
                    available = list(self.agents.keys())
                    if self.custom_agents_manager:
                        custom = [(ca.get('id'), ca.get('name')) for ca in self.custom_agents_manager.custom_agents.values()]
                        logger.error(f"[AGENT LOOKUP] Failed to find agent '{original_agent_id}'")
                        logger.error(f"[AGENT LOOKUP] Available built-in: {available}")
                        logger.error(f"[AGENT LOOKUP] Available custom: {custom}")
                    raise ValueError(f"Agent '{original_agent_id}' not found. Available: {available}, Custom: {[c[1] for c in custom] if self.custom_agents_manager else []}")
                
                # Build message
                # CRITICAL: Custom agents ALWAYS get the original user request
                if agent_type == "custom":
                    step_message = original_user_request
                    logger.info(f"[CUSTOM AGENT] Sending original request to {agent_id}: {step_message}")
                else:
                    # Built-in agents use accumulated context
                    if step_index > 0:
                        step_message = f"{context}\n\nTask: {task}\nContext: {step_context}"
                    else:
                        step_message = step_context or original_user_request
                    logger.info(f"[BUILT-IN AGENT] Sending to {agent_id}: {step_message[:100]}...")
                
                # Execute based on agent type
                if agent_type == "built-in":
                    agent_response = agent.think_and_act(step_message, verbose=False)
                    if hasattr(agent, 'clear_memory'):
                        agent.clear_memory()
                
                elif agent_type == "custom":
                    # Call custom agent via API with original request
                    agent_response = self._call_custom_agent(agent_id, step_message)
                
                step_result = {
                    "step": step_index + 1,
                    "agent": agent_id,
                    "agent_type": agent_type,
                    "task": task,
                    "response": agent_response,
                    "status": "completed"
                }
                results["steps_executed"].append(step_result)
                
                context += f"\nStep {step_index + 1} ({agent_type} agent: {agent_id}) - {task}:\n{agent_response}"
            
            except Exception as e:
                error_msg = f"Error in step {step_index + 1} ({step.get('agent')}): {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["steps_executed"].append({
                    "step": step_index + 1,
                    "agent": step.get("agent"),
                    "task": step.get("task"),
                    "error": error_msg,
                    "status": "failed"
                })
        
        results["final_response"] = self._synthesize_response(results["steps_executed"])
        results["success"] = len(results["errors"]) == 0
        
        return results        
    
    def _call_custom_agent(self, agent_id: str, message: str) -> str:
        """Call a custom agent via API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/agents/custom/{agent_id}/chat",
                json={"message": message},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response from agent")
        except Exception as e:
            logger.error(f"Error calling custom agent {agent_id}: {str(e)}")
            raise ValueError(f"Failed to execute custom agent {agent_id}: {str(e)}")
    
    def _synthesize_response(self, steps: List[Dict]) -> str:
        """Combine agent responses into one coherent answer"""
        if not steps:
            return "No steps were executed"
        
        if len(steps) == 1:
            step = steps[0]
            if step["status"] == "completed":
                return step.get("response", "Task completed")
            else:
                return step.get("error", "Task failed")
        
        synthesis = "I've completed your request in multiple steps:\n\n"
        
        for step in steps:
            if step["status"] == "completed":
                agent_type = step.get("agent_type", "unknown")
                synthesis += f"**Step {step['step']} ({agent_type} agent: {step['agent']}):** {step['task']}\n"
                synthesis += f"Result: {step['response']}\n\n"
            else:
                synthesis += f"**Step {step['step']} ({step['agent']}):** {step['task']}\n"
                synthesis += f"Error: {step.get('error', 'Unknown error')}\n\n"
        
        return synthesis.strip()


def create_llm_orchestrator(agents_dict: Dict[str, Agent], custom_agents_manager=None) -> LLMSequentialOrchestrator:
    """Factory function - supports both built-in and custom agents"""
    return LLMSequentialOrchestrator(agents_dict, custom_agents_manager)