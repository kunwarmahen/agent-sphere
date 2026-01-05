"""
templates.py - Pre-built Agent Templates Library
"""

from typing import Dict, List
from store.config import Config
import json

class AgentTemplate:
    """Represents a reusable agent template"""
    
    def __init__(self, template_id: str, name: str, role: str, description: str,
                 system_instructions: str, tools: List[str], tags: List[str],
                 category: str, difficulty: str = "beginner"):
        self.template_id = template_id
        self.name = name
        self.role = role
        self.description = description
        self.system_instructions = system_instructions
        self.tools = tools
        self.tags = tags
        self.category = category
        self.difficulty = difficulty
    
    def to_dict(self):
        return {
            "template_id": self.template_id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "system_instructions": self.system_instructions,
            "tools": self.tools,
            "tags": self.tags,
            "category": self.category,
            "difficulty": self.difficulty
        }
    
    def create_agent_config(self, user_id: str = "default_user"):
        """Convert template to agent config for creation"""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "system_instructions": self.system_instructions,
            "tools": self.tools,
            "tags": self.tags,
            "created_by": user_id
        }


class AgentTemplateLibrary:
    """Manages collection of pre-built agent templates"""
    
    def __init__(self):
        self.templates = {}
        self._load_builtin_templates()
        self._load_custom_templates()
    
    def _load_builtin_templates(self):
        """Load built-in templates"""
        
        # 1. Text Processing Agent
        self.templates["text_processor"] = AgentTemplate(
            template_id="text_processor",
            name="Text Processor Pro",
            role="Text Processing Specialist",
            description="Advanced text processing with uppercase, lowercase, word count, and character analysis",
            system_instructions="You are a text processing specialist. Analyze and transform text using your tools. Provide clear, formatted results.",
            tools=["toggle_light", "set_thermostat"],  # Replace with actual tool IDs
            tags=["text", "processing", "analysis", "transformation"],
            category="Utility",
            difficulty="beginner"
        )
        
        # 2. Customer Support Agent
        self.templates["customer_support"] = AgentTemplate(
            template_id="customer_support",
            name="Customer Support Assistant",
            role="Customer Service Representative",
            description="Handle customer inquiries, check order status, and provide support using email and calendar tools",
            system_instructions="You are a friendly customer support agent. Help customers with their questions, check their calendar for appointments, and send follow-up emails. Always be polite and professional.",
            tools=["send_email", "schedule_event", "get_calendar_events"],
            tags=["support", "customer", "email", "calendar"],
            category="Business",
            difficulty="intermediate"
        )
        
        # 3. Home Automation Agent
        self.templates["smart_home"] = AgentTemplate(
            template_id="smart_home",
            name="Smart Home Manager",
            role="Home Automation Specialist",
            description="Control lights, thermostat, and devices. Create scenes and automation routines.",
            system_instructions="You are a smart home automation expert. Control home devices efficiently, suggest energy-saving settings, and create convenient automation scenes based on user preferences.",
            tools=["toggle_light", "set_thermostat", "control_device", "lock_door"],
            tags=["home", "automation", "iot", "smart-home"],
            category="Home",
            difficulty="beginner"
        )
        
        # 4. Financial Advisor Agent
        self.templates["financial_advisor"] = AgentTemplate(
            template_id="financial_advisor",
            name="Personal Financial Advisor",
            role="Financial Planning Specialist",
            description="Track expenses, analyze spending patterns, and provide financial advice",
            system_instructions="You are a knowledgeable financial advisor. Help users track their expenses, analyze spending patterns, and provide actionable financial advice. Always explain financial concepts clearly.",
            tools=["get_account_balance", "record_transaction", "get_financial_summary"],
            tags=["finance", "money", "budgeting", "advisor"],
            category="Finance",
            difficulty="intermediate"
        )
        
        # 5. Meeting Scheduler Agent
        self.templates["meeting_scheduler"] = AgentTemplate(
            template_id="meeting_scheduler",
            name="Meeting Scheduler Pro",
            role="Professional Meeting Coordinator",
            description="Schedule meetings, find free slots, send invitations, and manage calendar conflicts",
            system_instructions="You are an efficient meeting coordinator. Find optimal meeting times, send professional invitations, and help manage calendars. Always confirm details with users before scheduling.",
            tools=["schedule_event", "get_calendar_events", "send_email"],
            tags=["calendar", "meetings", "scheduling", "productivity"],
            category="Productivity",
            difficulty="beginner"
        )
        
        # 6. Data Analyst Agent
        self.templates["data_analyst"] = AgentTemplate(
            template_id="data_analyst",
            name="Data Analysis Assistant",
            role="Data Analyst",
            description="Analyze data, generate reports, and provide insights from financial and usage data",
            system_instructions="You are a data analyst. Examine data patterns, calculate statistics, and provide clear insights. Present findings in an easy-to-understand format with key takeaways.",
            tools=["get_financial_summary", "get_account_balance"],
            tags=["data", "analysis", "reporting", "statistics"],
            category="Analytics",
            difficulty="advanced"
        )
        
        # 7. Morning Routine Agent
        self.templates["morning_routine"] = AgentTemplate(
            template_id="morning_routine",
            name="Morning Routine Assistant",
            role="Morning Routine Coordinator",
            description="Check calendar, read emails, control home devices for morning preparation",
            system_instructions="You are a morning routine assistant. Help users start their day by checking their calendar, summarizing important emails, and preparing their home environment (lights, temperature, etc.).",
            tools=["get_calendar_events", "toggle_light", "set_thermostat"],
            tags=["routine", "morning", "automation", "productivity"],
            category="Lifestyle",
            difficulty="beginner"
        )
        
        # 8. Security Monitor Agent
        self.templates["security_monitor"] = AgentTemplate(
            template_id="security_monitor",
            name="Home Security Monitor",
            role="Security Monitoring Specialist",
            description="Monitor home security, control locks, and send alerts about unusual activity",
            system_instructions="You are a home security specialist. Monitor security status, control locks, and alert users about any concerns. Prioritize safety and provide clear security recommendations.",
            tools=["lock_door", "send_email"],
            tags=["security", "monitoring", "safety", "alerts"],
            category="Security",
            difficulty="intermediate"
        )
        
        # 9. Email Assistant Agent
        self.templates["email_assistant"] = AgentTemplate(
            template_id="email_assistant",
            name="Email Management Assistant",
            role="Email Manager",
            description="Read, summarize, and respond to emails. Draft professional communications.",
            system_instructions="You are an email management expert. Help users read and understand their emails, draft professional responses, and organize their inbox efficiently.",
            tools=["send_email"],
            tags=["email", "communication", "productivity", "organization"],
            category="Productivity",
            difficulty="beginner"
        )
        
        # 10. Budget Tracker Agent
        self.templates["budget_tracker"] = AgentTemplate(
            template_id="budget_tracker",
            name="Budget Tracking Specialist",
            role="Personal Budget Manager",
            description="Track spending, categorize expenses, and help users stay within budget",
            system_instructions="You are a budget tracking specialist. Help users record transactions, categorize spending, and provide insights on their financial habits. Encourage responsible spending.",
            tools=["record_transaction", "get_financial_summary"],
            tags=["budget", "finance", "tracking", "expenses"],
            category="Finance",
            difficulty="beginner"
        )
    
    def _load_custom_templates(self):
        """Load user-created templates from disk"""
        templates_file = Config.TEMPLATES_DIR / "custom_templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r') as f:
                    custom_data = json.load(f)
                    for template_data in custom_data.get("templates", []):
                        template = AgentTemplate(**template_data)
                        self.templates[template.template_id] = template
                print(f"✅ Loaded {len(custom_data.get('templates', []))} custom templates")
            except Exception as e:
                print(f"Error loading custom templates: {e}")
    
    def save_custom_template(self, template: AgentTemplate) -> bool:
        """Save a user-created template"""
        templates_file = Config.TEMPLATES_DIR / "custom_templates.json"
        
        try:
            # Load existing
            custom_templates = []
            if templates_file.exists():
                with open(templates_file, 'r') as f:
                    data = json.load(f)
                    custom_templates = data.get("templates", [])
            
            # Add or update
            existing_index = next(
                (i for i, t in enumerate(custom_templates) if t["template_id"] == template.template_id),
                None
            )
            
            if existing_index is not None:
                custom_templates[existing_index] = template.to_dict()
            else:
                custom_templates.append(template.to_dict())
            
            # Save
            with open(templates_file, 'w') as f:
                json.dump({"templates": custom_templates}, f, indent=2)
            
            # Update in-memory
            self.templates[template.template_id] = template
            return True
        
        except Exception as e:
            print(f"Error saving custom template: {e}")
            return False
    
    def get_template(self, template_id: str) -> AgentTemplate:
        """Get a specific template"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: str = None, difficulty: str = None) -> List[Dict]:
        """List all templates with optional filtering"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category.lower() == category.lower()]
        
        if difficulty:
            templates = [t for t in templates if t.difficulty.lower() == difficulty.lower()]
        
        return [t.to_dict() for t in templates]
    
    def get_categories(self) -> List[str]:
        """Get all template categories"""
        categories = set(t.category for t in self.templates.values())
        return sorted(list(categories))
    
    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template.to_dict())
        
        return results
    
    def create_agent_from_template(self, template_id: str, custom_agent_manager, 
                                   user_id: str = "default_user") -> Dict:
        """Create an agent from a template"""
        template = self.get_template(template_id)
        
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_id}' not found"
            }
        
        # Create agent config from template
        agent_config = template.create_agent_config(user_id)
        
        # Use the custom agent manager to create
        result = custom_agent_manager.create_agent(agent_config)
        
        if result["success"]:
            result["message"] = f"Agent created from template '{template.name}'"
            result["template_used"] = template_id
        
        return result


# Initialize global template library
agent_template_library = AgentTemplateLibrary()