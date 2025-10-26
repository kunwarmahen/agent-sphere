"""
dynamic_tools.py - Dynamic Tool Creation and Management System
Add this to your project
"""

import json
import uuid
import requests
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Import persistence functions
try:
    from store.persistence import save_custom_tools, load_custom_tools
except ImportError:
    print("⚠️ persistence.py not found. Custom tools will not be saved/loaded from disk.")
    # Fallback if persistence.py doesn't exist
    def save_custom_tools(data):
        return False
    def load_custom_tools():
        return {}

class DynamicToolBuilder:
    """Allows users to create custom tools with various integration types"""
    
    INTEGRATION_TYPES = {
        "http": "HTTP/REST API Integration",
        "mcp": "Model Context Protocol (MCP) Server",
        "webhook": "Webhook Integration",
        "custom_code": "Custom Python Code"
    }
    
    def __init__(self):
        # Load existing tools from disk
        self.custom_tools = load_custom_tools()
        self.tool_templates = {}
        
        print(f"✅ Loaded {len(self.custom_tools)} custom tools from disk")
    
    def _save_to_disk(self):
        """Save current tools to disk"""
        return save_custom_tools(self.custom_tools)
    
    def create_tool(self, tool_config: Dict) -> Dict:
        """Create a new custom tool"""
        try:
            tool_id = str(uuid.uuid4())[:8]
            
            # Validate required fields
            required_fields = ["name", "description", "integration_type", "created_by"]
            for field in required_fields:
                if field not in tool_config:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            if tool_config["integration_type"] not in self.INTEGRATION_TYPES:
                return {
                    "success": False,
                    "error": f"Invalid integration type. Must be one of: {list(self.INTEGRATION_TYPES.keys())}"
                }
            
            tool_data = {
                "id": tool_id,
                "name": tool_config["name"],
                "description": tool_config["description"],
                "integration_type": tool_config["integration_type"],
                "created_by": tool_config["created_by"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "config": tool_config.get("config", {}),
                "parameters": tool_config.get("parameters", {}),
                "status": "draft",
                "test_result": None,
                "version": "1.0.0"
            }
            
            self.custom_tools[tool_id] = tool_data
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "tool_id": tool_id,
                "message": f"Tool '{tool_data['name']}' created successfully",
                "tool": tool_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def update_tool(self, tool_id: str, updates: Dict) -> Dict:
        """Update an existing tool"""
        try:
            if tool_id not in self.custom_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            tool = self.custom_tools[tool_id]
            
            # Update allowed fields
            updateable_fields = ["name", "description", "config", "parameters"]
            for field in updateable_fields:
                if field in updates:
                    tool[field] = updates[field]
            
            tool["updated_at"] = datetime.now().isoformat()
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Tool updated successfully",
                "tool": tool
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_tool(self, tool_id: str, test_input: Dict) -> Dict:
        """Test a tool with sample input"""
        try:
            if tool_id not in self.custom_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            tool = self.custom_tools[tool_id]
            integration_type = tool["integration_type"]
            
            if integration_type == "http":
                result = self._test_http_tool(tool, test_input)
            elif integration_type == "mcp":
                result = self._test_mcp_tool(tool, test_input)
            elif integration_type == "webhook":
                result = self._test_webhook_tool(tool, test_input)
            elif integration_type == "custom_code":
                result = self._test_custom_code_tool(tool, test_input)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown integration type: {integration_type}"
                }
            
            tool["test_result"] = result
            tool["updated_at"] = datetime.now().isoformat()
            self._save_to_disk()  # 💾 Save to disk
            
            return result
        except Exception as e:
            logger.error(f"Error testing tool: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _test_http_tool(self, tool: Dict, test_input: Dict) -> Dict:
        """Test HTTP/REST API integration"""
        try:
            config = tool["config"]
            
            # Validate HTTP config
            required_http_fields = ["url", "method"]
            for field in required_http_fields:
                if field not in config:
                    return {
                        "success": False,
                        "error": f"Missing required HTTP config: {field}"
                    }
            
            url = config["url"]
            method = config["method"].upper()
            headers = config.get("headers", {"Content-Type": "application/json"})
            
            # Make request
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=test_input, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=test_input, headers=headers, timeout=10)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}"
                }
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text,
                "message": "HTTP request successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_mcp_tool(self, tool: Dict, test_input: Dict) -> Dict:
        """Test MCP Server integration"""
        try:
            config = tool["config"]
            
            # Validate MCP config
            required_mcp_fields = ["server_url", "method"]
            for field in required_mcp_fields:
                if field not in config:
                    return {
                        "success": False,
                        "error": f"Missing required MCP config: {field}"
                    }
            
            # For MCP, construct the call
            server_url = config["server_url"]
            method = config["method"]
            
            # Example MCP call format
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": test_input,
                "id": 1
            }
            
            response = requests.post(
                f"{server_url}/call",
                json=payload,
                timeout=10
            )
            
            return {
                "success": True,
                "response": response.json(),
                "message": "MCP call successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_webhook_tool(self, tool: Dict, test_input: Dict) -> Dict:
        """Test Webhook integration"""
        try:
            config = tool["config"]
            
            if "webhook_url" not in config:
                return {
                    "success": False,
                    "error": "Missing webhook_url in config"
                }
            
            webhook_url = config["webhook_url"]
            headers = config.get("headers", {"Content-Type": "application/json"})
            
            response = requests.post(
                webhook_url,
                json=test_input,
                headers=headers,
                timeout=10
            )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Webhook call successful"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_custom_code_tool(self, tool: Dict, test_input: Dict) -> Dict:
        """Test Custom Python Code integration"""
        try:
            config = tool["config"]
            
            if "code" not in config:
                return {
                    "success": False,
                    "error": "Missing code in config"
                }
            
            code = config["code"]
            
            # Create safe execution environment
            safe_dict = {
                "input": test_input,
                "result": None,
                "print": print
            }
            
            # Execute code (CAUTION: Only in controlled environment)
            exec(code, safe_dict)
            
            return {
                "success": True,
                "result": safe_dict.get("result"),
                "message": "Custom code executed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    def publish_tool(self, tool_id: str) -> Dict:
        """Publish a tool for use"""
        try:
            if tool_id not in self.custom_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            tool = self.custom_tools[tool_id]
            
            # Validate tool before publishing
            if not tool.get("name") or not tool.get("description"):
                return {
                    "success": False,
                    "error": "Tool must have name and description"
                }
            
            tool["status"] = "published"
            tool["published_at"] = datetime.now().isoformat()
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Tool published successfully",
                "tool": tool
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_tool(self, tool_id: str) -> Dict:
        """Delete a tool"""
        try:
            if tool_id not in self.custom_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            del self.custom_tools[tool_id]
            self._save_to_disk()  # 💾 Save to disk
            
            return {
                "success": True,
                "message": "Tool deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tool(self, tool_id: str) -> Dict:
        """Get tool details"""
        return self.custom_tools.get(tool_id)
    
    def get_user_tools(self, user_id: str) -> List[Dict]:
        """Get all tools created by a user"""
        return [
            tool for tool in self.custom_tools.values()
            if tool["created_by"] == user_id
        ]
    
    def execute_tool(self, tool_id: str, params: Dict) -> Dict:
        """Execute a published tool"""
        try:
            if tool_id not in self.custom_tools:
                return {
                    "success": False,
                    "error": "Tool not found"
                }
            
            tool = self.custom_tools[tool_id]
            
            if tool["status"] != "published":
                return {
                    "success": False,
                    "error": "Tool is not published"
                }
            
            integration_type = tool["integration_type"]
            
            if integration_type == "http":
                result = self._execute_http_tool(tool, params)
            elif integration_type == "mcp":
                result = self._execute_mcp_tool(tool, params)
            elif integration_type == "webhook":
                result = self._execute_webhook_tool(tool, params)
            elif integration_type == "custom_code":
                result = self._execute_custom_code_tool(tool, params)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown integration type: {integration_type}"
                }
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_http_tool(self, tool: Dict, params: Dict) -> Dict:
        """Execute HTTP tool - same as test"""
        return self._test_http_tool(tool, params)
    
    def _execute_mcp_tool(self, tool: Dict, params: Dict) -> Dict:
        """Execute MCP tool - same as test"""
        return self._test_mcp_tool(tool, params)
    
    def _execute_webhook_tool(self, tool: Dict, params: Dict) -> Dict:
        """Execute webhook tool - same as test"""
        return self._test_webhook_tool(tool, params)
    
    def _execute_custom_code_tool(self, tool: Dict, params: Dict) -> Dict:
        """Execute custom code tool - same as test"""
        return self._test_custom_code_tool(tool, params)


# Initialize
dynamic_tool_builder = DynamicToolBuilder()