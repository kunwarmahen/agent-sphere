"""
Core AI Agent Framework - The foundation for all agents
"""
import json
import re
from typing import Any, Callable, Dict, List, Optional
import requests

# Configure Ollama connection
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"


class Tool:
    """Represents a tool the agent can use"""
    def __init__(self, name: str, description: str, func: Callable, params: Dict):
        self.name = name
        self.description = description
        self.func = func
        self.params = params
    
    def execute(self, **kwargs) -> str:
        """Execute the tool and return result"""
        try:
            result = self.func(**kwargs)
            return json.dumps({"success": True, "result": result})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class Agent:
    """Core AI Agent that reasons and uses tools"""
    def __init__(self, name: str, role: str, tools: List[Tool], system_instructions: str = ""):
        self.name = name
        self.role = role
        self.tools = {tool.name: tool for tool in tools}
        self.memory = []
        self.max_iterations = 10
        self.system_instructions = system_instructions
    
    def _format_tools(self) -> str:
        """Format available tools for the prompt"""
        tools_desc = "Available tools:\n"
        for tool_name, tool in self.tools.items():
            tools_desc += f"\n- {tool_name}: {tool.description}\n"
            tools_desc += f"  Parameters: {json.dumps(tool.params)}\n"
        return tools_desc
    
    def _extract_json_object(self, text: str) -> Optional[Dict]:
        """Extract JSON object from text by finding matching braces"""
        try:
            # Find the first opening brace
            start_idx = text.find('{')
            if start_idx == -1:
                return None
            
            # Count braces to find the matching closing brace
            brace_count = 0
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found matching closing brace
                        json_str = text[start_idx:i+1]
                        return json.loads(json_str)
            
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def _parse_action(self, response: str) -> Optional[Dict]:
        """Parse agent's response to extract action"""
        # First, try to extract and parse JSON object with proper brace matching
        json_obj = self._extract_json_object(response)
        
        if json_obj and "action" in json_obj:
            return json_obj
        
        # Fallback: look for TOOL: name and PARAMS: pattern
        tool_match = re.search(r'TOOL:\s*(\w+)', response)
        params_match = re.search(r'PARAMS:\s*({.*?})', response, re.DOTALL)
        
        if tool_match:
            tool_name = tool_match.group(1)
            params = {}
            if params_match:
                try:
                    params = json.loads(params_match.group(1))
                except json.JSONDecodeError:
                    pass
            return {"action": tool_name, "parameters": params}
        
        return None
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """Call local Ollama Qwen model"""
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running on http://localhost:11434"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def think_and_act(self, user_request: str, verbose: bool = False) -> str:
        """Main agent loop: think, decide, act"""
        self.memory.append({"role": "user", "content": user_request})
        
        base_prompt = f"""You are {self.name}, a {self.role} agent.
Your goal is to help the user by using the available tools.

{self._format_tools()}

When you need to use a tool, respond with a JSON block like this:
{{"action": "tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}

Think through the problem step by step. Only output one action at a time.
After using a tool, wait for the result before deciding the next action."""
        
        if self.system_instructions:
            base_prompt += f"\n\nAdditional Instructions:\n{self.system_instructions}"
        
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n[Iteration {iteration + 1}]")
            
            # Build messages
            messages = [{"role": "system", "content": base_prompt}] + self.memory
            
            # Get model response
            response = self._call_ollama(messages)
            
            if verbose:
                print(f"Agent: {response[:200]}...")
            
            self.memory.append({"role": "assistant", "content": response})
            
            # Check if action is needed
            action = self._parse_action(response)
            
            if not action:
                # No more actions needed, return final response
                return response
            
            tool_name = action.get("action")
            params = action.get("parameters", {})
            
            if tool_name not in self.tools:
                error_msg = f"Tool '{tool_name}' not found"
                if verbose:
                    print(f"Error: {error_msg}")
                self.memory.append({"role": "user", "content": f"Error: {error_msg}"})
                continue
            
            # Execute tool
            if verbose:
                print(f"Using tool: {tool_name} with params: {params}")
            
            tool_result = self.tools[tool_name].execute(**params)
            self.memory.append({"role": "user", "content": f"Tool result: {tool_result}"})
        
        return "Max iterations reached"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory = []