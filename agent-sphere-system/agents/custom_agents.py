"""
custom_agents.py - Updated with persistence support
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List
from base.agent_framework import Agent, Tool
from store.storage_backends import get_storage_backend



# Import persistence functions
try:
    from store.persistence import save_custom_agents, load_custom_agents
except ImportError:
    print("⚠️ persistence.py not found. Custom agents will not be saved/loaded from disk.")
    # Fallback if persistence.py doesn't exist
    def save_custom_agents(data):
        return False
    def load_custom_agents():
        return {}


class CustomAgentManager:
    """Manages user-created and published agents with persistence"""
    
    def __init__(self):
        # Use storage backend instead of direct file I/O
        self.storage = get_storage_backend()
        
        # Load existing agents from storage
        loaded_data = self.storage.load_agents()
        self.custom_agents = loaded_data.get("custom_agents", {})
        self.published_agents = loaded_data.get("published_agents", {})
        self.agent_marketplace = loaded_data.get("agent_marketplace", [])
        
        print(f"✅ Loaded {len(self.custom_agents)} custom agents")
        print(f"✅ Loaded {len(self.agent_marketplace)} marketplace agents")
    
    def _save_to_disk(self):
        """Save current state using storage backend"""
        data = {
            "custom_agents": self.custom_agents,
            "published_agents": self.published_agents,
            "agent_marketplace": self.agent_marketplace
        }
        return self.storage.save_agents(data)
    
    def create_agent(self, agent_config: Dict) -> Dict:
        """Create a new custom agent from configuration"""
        try:
            agent_id = str(uuid.uuid4())[:8]
            
            agent_data = {
                "id": agent_id,
                "name": agent_config.get("name", "Untitled Agent"),
                "role": agent_config.get("role", "Custom Agent"),
                "description": agent_config.get("description", ""),
                "system_instructions": agent_config.get("system_instructions", ""),
                "tools": agent_config.get("tools", []),
                "created_by": agent_config.get("created_by", "unknown"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "published": False,
                "version": "1.0.0",
                "tags": agent_config.get("tags", []),
                "status": "draft"
            }
            
            self.custom_agents[agent_id] = agent_data
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "agent_id": agent_id,
                "message": f"Agent '{agent_data['name']}' created successfully",
                "agent": agent_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create agent"
            }
    
    def get_agent(self, agent_id: str) -> Dict:
        """Get a specific agent"""
        if agent_id in self.custom_agents:
            return self.custom_agents[agent_id]
        return None
    
    def update_agent(self, agent_id: str, updates: Dict) -> Dict:
        """Update an existing agent"""
        try:
            if agent_id not in self.custom_agents:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            agent = self.custom_agents[agent_id]
            
            # Only allow updates to specific fields
            updateable_fields = ["name", "role", "description", "system_instructions", 
                                "tools", "tags"]
            
            for field in updateable_fields:
                if field in updates:
                    agent[field] = updates[field]
            
            agent["updated_at"] = datetime.now().isoformat()
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Agent updated successfully",
                "agent": agent
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_agent(self, agent_id: str) -> Dict:
        """Delete a custom agent"""
        try:
            if agent_id not in self.custom_agents:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            if self.custom_agents[agent_id]["published"]:
                return {
                    "success": False,
                    "error": "Cannot delete published agents. Unpublish first."
                }
            
            del self.custom_agents[agent_id]
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Agent deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def publish_agent(self, agent_id: str) -> Dict:
        """Publish an agent to the marketplace"""
        try:
            if agent_id not in self.custom_agents:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            agent = self.custom_agents[agent_id]
            
            # Validate agent before publishing
            if not agent.get("name") or not agent.get("role"):
                return {
                    "success": False,
                    "error": "Agent must have name and role before publishing"
                }
            
            agent["published"] = True
            agent["status"] = "published"
            agent["published_at"] = datetime.now().isoformat()
            
            # Add to marketplace
            marketplace_entry = {
                "id": agent_id,
                "name": agent["name"],
                "role": agent["role"],
                "description": agent["description"],
                "created_by": agent["created_by"],
                "published_at": agent["published_at"],
                "version": agent["version"],
                "tags": agent["tags"],
                "downloads": 0,
                "rating": 0,
                "reviews": []
            }
            
            self.published_agents[agent_id] = agent
            self.agent_marketplace.append(marketplace_entry)
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": f"Agent '{agent['name']}' published successfully",
                "agent": agent
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def unpublish_agent(self, agent_id: str) -> Dict:
        """Unpublish an agent from the marketplace"""
        try:
            if agent_id not in self.custom_agents:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            agent = self.custom_agents[agent_id]
            agent["published"] = False
            agent["status"] = "draft"
            
            if agent_id in self.published_agents:
                del self.published_agents[agent_id]
            
            self.agent_marketplace = [
                a for a in self.agent_marketplace if a["id"] != agent_id
            ]
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Agent unpublished successfully",
                "agent": agent
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_my_agents(self, user_id: str) -> List[Dict]:
        """Get all agents created by a user"""
        return [
            agent for agent in self.custom_agents.values()
            if agent["created_by"] == user_id
        ]
    
    def get_marketplace_agents(self, tags: List[str] = None) -> List[Dict]:
        """Get all published agents, optionally filtered by tags"""
        marketplace = self.agent_marketplace
        
        if tags:
            marketplace = [
                agent for agent in marketplace
                if any(tag in agent["tags"] for tag in tags)
            ]
        
        return marketplace
    
    def install_agent(self, agent_id: str, user_id: str) -> Dict:
        """Install a published agent for a user"""
        try:
            if agent_id not in self.published_agents:
                return {
                    "success": False,
                    "error": "Agent not found in marketplace"
                }
            
            original_agent = self.published_agents[agent_id]
            
            # Create a copy for the user
            user_agent_id = f"{user_id}_{agent_id}"
            user_agent = original_agent.copy()
            user_agent["id"] = user_agent_id
            user_agent["installed_by"] = user_id
            user_agent["installed_at"] = datetime.now().isoformat()
            user_agent["original_agent_id"] = agent_id
            
            self.custom_agents[user_agent_id] = user_agent
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": f"Agent '{original_agent['name']}' installed successfully",
                "agent": user_agent
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def rate_agent(self, agent_id: str, rating: int, review: str = "") -> Dict:
        """Rate and review a published agent"""
        try:
            if agent_id not in self.agent_marketplace:
                return {
                    "success": False,
                    "error": "Agent not found"
                }
            
            if not 1 <= rating <= 5:
                return {
                    "success": False,
                    "error": "Rating must be between 1 and 5"
                }
            
            marketplace_entry = next(
                (a for a in self.agent_marketplace if a["id"] == agent_id),
                None
            )
            
            if not marketplace_entry:
                return {
                    "success": False,
                    "error": "Agent not found in marketplace"
                }
            
            review_entry = {
                "rating": rating,
                "review": review,
                "timestamp": datetime.now().isoformat()
            }
            
            marketplace_entry["reviews"].append(review_entry)
            
            # Update average rating
            ratings = [r["rating"] for r in marketplace_entry["reviews"]]
            marketplace_entry["rating"] = sum(ratings) / len(ratings)
            marketplace_entry["downloads"] += 1
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Rating submitted successfully",
                "average_rating": marketplace_entry["rating"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Initialize the manager (will load from disk automatically)
custom_agent_manager = CustomAgentManager()

# ToolBuilder class remains the same...
class ToolBuilder:
    """Helper class to build and manage tools for custom agents"""
    
    AVAILABLE_TOOLS = {
        # ... (keep existing AVAILABLE_TOOLS dictionary)
    }
    
    @staticmethod
    def get_available_tools():
        """Get all available tools"""
        return ToolBuilder.AVAILABLE_TOOLS
    
    @staticmethod
    def get_tools_by_category(category):
        """Get tools for a specific category"""
        return {
            name: tool for name, tool in ToolBuilder.AVAILABLE_TOOLS.items()
            if tool["category"] == category
        }
    
    @staticmethod
    def validate_tool(tool_name):
        """Check if a tool exists"""
        return tool_name in ToolBuilder.AVAILABLE_TOOLS
    
    @staticmethod
    def get_tool_info(tool_name):
        """Get detailed tool information"""
        if tool_name in ToolBuilder.AVAILABLE_TOOLS:
            return ToolBuilder.AVAILABLE_TOOLS[tool_name]
        return None