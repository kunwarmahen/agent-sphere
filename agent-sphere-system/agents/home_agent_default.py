"""
Home Automation Agent - Smart home control with real-time device management
"""
import json
from base.agent_framework import Agent, Tool
from datetime import datetime


class SmartHomeController:
    """Manages all smart home devices and their states"""
    def __init__(self):
        self.lights = {
            "living_room": {"on": False, "brightness": 0, "color_temp": 4000},
            "bedroom": {"on": False, "brightness": 0, "color_temp": 3000},
            "kitchen": {"on": False, "brightness": 0, "color_temp": 5000},
            "bathroom": {"on": False, "brightness": 0, "color_temp": 4000}
        }
        self.thermostat = {"current_temp": 72, "target_temp": 72, "mode": "auto", "humidity": 45}
        self.security = {"door_locked": True, "garage_open": False, "motion_detected": False}
        self.devices = {
            "tv": {"on": False, "volume": 0, "input": "hdmi1"},
            "coffee_maker": {"on": False, "brew_type": "regular"},
            "washing_machine": {"on": False, "cycle": None},
            "refrigerator": {"on": False, "temp": 38, "alert": False}
        }
        self.automation_rules = []
        self.device_log = []
    
    def log_action(self, action: str, device: str, details: str = ""):
        """Log all device actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.device_log.append({
            "timestamp": timestamp,
            "action": action,
            "device": device,
            "details": details
        })
    
    def toggle_light(self, room: str, state: bool = None, brightness: int = None, color_temp: int = None) -> str:
        if room not in self.lights:
            return f"Room '{room}' not found. Available: {list(self.lights.keys())}"
        
        light = self.lights[room]
        
        if state is not None:
            light["on"] = state
        else:
            light["on"] = not light["on"]
        
        if brightness is not None and 0 <= brightness <= 100:
            light["brightness"] = brightness if light["on"] else 0
        
        if color_temp is not None and 2700 <= color_temp <= 6500:
            light["color_temp"] = color_temp
        
        self.log_action("toggle", room, f"on={light['on']}, brightness={light['brightness']}")
        
        status = f"Light in {room} turned {'on' if light['on'] else 'off'}"
        if light["on"]:
            status += f" (brightness: {light['brightness']}%, color temp: {light['color_temp']}K)"
        return status
    
    def set_thermostat(self, target_temp: int, mode: str = None) -> str:
        if not 60 <= target_temp <= 85:
            return "Temperature must be between 60-85°F"
        
        self.thermostat["target_temp"] = target_temp
        if mode and mode in ["heat", "cool", "auto"]:
            self.thermostat["mode"] = mode
        
        self.log_action("thermostat", "hvac", f"target={target_temp}°F, mode={self.thermostat['mode']}")
        
        return f"Thermostat set to {target_temp}°F in {self.thermostat['mode']} mode"
    
    def get_thermostat_status(self) -> str:
        return json.dumps(self.thermostat)
    
    def control_device(self, device: str, on: bool = None) -> str:
        if device not in self.devices:
            return f"Device '{device}' not found. Available: {list(self.devices.keys())}"
        
        dev = self.devices[device]
        
        if on is not None:
            dev["on"] = on
        else:
            dev["on"] = not dev["on"]
        
        self.log_action("device_control", device, f"state={'on' if dev['on'] else 'off'}")
        
        return f"{device.replace('_', ' ').title()} turned {'on' if dev['on'] else 'off'}"
    
    def lock_door(self, lock: bool = True) -> str:
        self.security["door_locked"] = lock
        self.log_action("security", "door", f"{'locked' if lock else 'unlocked'}")
        return f"Door is now {'locked' if lock else 'unlocked'}"
    
    def control_garage(self, open_garage: bool) -> str:
        self.security["garage_open"] = open_garage
        self.log_action("security", "garage", f"{'opened' if open_garage else 'closed'}")
        return f"Garage is now {'open' if open_garage else 'closed'}"
    

    def get_home_status(self) -> str:
        lights_status = {room: light["on"] for room, light in self.lights.items()}
        devices_status = {device: {"on": dev["on"]} for device, dev in self.devices.items()}
        
        return json.dumps({
            "lights": lights_status,
            "thermostat": self.thermostat,
            "security": self.security,
            "devices": devices_status
        })
    
    # def create_scene(self, scene_name: str, actions: list) -> str:
    #     """Create automation scene"""
    #     self.automation_rules.append({"scene": scene_name, "actions": actions})
    #     return f"Scene '{scene_name}' created with {len(actions)} actions"
    
    def activate_scene(self, scene_name: str) -> str:
        """Activate a predefined scene"""
        for rule in self.automation_rules:
            if rule["scene"] == scene_name:
                return f"Scene '{scene_name}' activated with actions: {rule['actions']}"
        return f"Scene '{scene_name}' not found"
    
    def get_device_log(self, limit: int = 10) -> str:
        """Get recent device actions"""
        return json.dumps(self.device_log[-limit:])
    
    def create_scene(self, scene_name: str, actions: list) -> str:
        """Create an automation scene with predefined actions"""
        if not hasattr(self, 'scenes'):
            self.scenes = {}
        
        self.scenes[scene_name] = {
            "name": scene_name,
            "actions": actions,
            "created_at": datetime.now().isoformat(),
            "execution_count": 0
        }
        
        self.log_action("scene_created", scene_name, f"with {len(actions)} actions")
        return f"Scene '{scene_name}' created with {len(actions)} actions"


    def execute_scene(self, scene_name: str) -> str:
        """Execute a predefined scene"""
        if not hasattr(self, 'scenes'):
            return f"Scene '{scene_name}' not found. No scenes created yet."
        
        if scene_name not in self.scenes:
            available = list(self.scenes.keys())
            return f"Scene '{scene_name}' not found. Available scenes: {available}"
        
        scene = self.scenes[scene_name]
        results = []
        
        try:
            for action_str in scene["actions"]:
                try:
                    # Parse and execute the action string
                    # e.g., "toggle_light(room='bedroom', state=True, brightness=10, color_temp=2700)"
                    result = self._execute_action_string(action_str)
                    results.append(f"✓ {result}")
                except Exception as e:
                    results.append(f"✗ Error: {str(e)}")
            
            scene["execution_count"] += 1
            self.log_action("scene_executed", scene_name, f"with {len(results)} actions")
            
            return f"Scene '{scene_name}' executed:\n" + "\n".join(results)
        
        except Exception as e:
            self.log_action("scene_execution_failed", scene_name, str(e))
            return f"Error executing scene: {str(e)}"


    def _execute_action_string(self, action_str: str) -> str:
        """Parse and execute an action string"""
        import re
        
        # Parse function call: function_name(param1=value1, param2=value2)
        match = re.match(r'(\w+)\((.*)\)', action_str.strip())
        if not match:
            raise ValueError(f"Invalid action format: {action_str}")
        
        function_name = match.group(1)
        params_str = match.group(2)
        
        # Parse parameters
        params = {}
        # Handle quoted strings in parameters
        param_pattern = r"(\w+)=(?:'([^']*)'|\"([^\"]*)\"|(\d+\.?\d*)|(\w+))"
        
        for param_match in re.finditer(param_pattern, params_str):
            key = param_match.group(1)
            value = (param_match.group(2) or param_match.group(3) or 
                    param_match.group(4) or param_match.group(5))
            
            # Convert to appropriate type
            if value.lower() in ('true', 'false'):
                params[key] = value.lower() == 'true'
            elif value.replace('.', '').isdigit():
                params[key] = int(value) if '.' not in value else float(value)
            else:
                params[key] = value
        
        # Execute the function
        if function_name == "toggle_light":
            return self.toggle_light(**params)
        elif function_name == "set_thermostat":
            return self.set_thermostat(**params)
        elif function_name == "control_device":
            return self.control_device(**params)
        elif function_name == "lock_door":
            return self.lock_door(**params)
        elif function_name == "control_garage":
            return self.control_garage(**params)
        else:
            raise ValueError(f"Unknown function: {function_name}")


    def get_scenes(self) -> str:
        """Get all available scenes"""
        if not hasattr(self, 'scenes'):
            return json.dumps({"scenes": [], "message": "No scenes created yet"})
        
        scenes_list = []
        for name, scene in self.scenes.items():
            scenes_list.append({
                "name": name,
                "action_count": len(scene["actions"]),
                "executions": scene["execution_count"],
                "created_at": scene["created_at"],
                "actions": scene["actions"]
            })
        
        return json.dumps({"scenes": scenes_list})


    def delete_scene(self, scene_name: str) -> str:
        """Delete a scene"""
        if not hasattr(self, 'scenes') or scene_name not in self.scenes:
            return f"Scene '{scene_name}' not found"
        
        del self.scenes[scene_name]
        self.log_action("scene_deleted", scene_name, "")
        return f"Scene '{scene_name}' deleted"



# Initialize controller
controller = SmartHomeController()

# Create tools
home_tools = [
    Tool("toggle_light", 
         "Toggle light on/off in a room, optionally set brightness (0-100) and color temperature (2700-6500K)", 
         controller.toggle_light, 
         {"room": "str", "state": "bool (optional)", "brightness": "int (0-100, optional)", "color_temp": "int (2700-6500, optional)"}),
    
    Tool("set_thermostat", 
         "Set target temperature and HVAC mode", 
         controller.set_thermostat, 
         {"target_temp": "int (60-85)", "mode": "str (heat/cool/auto, optional)"}),
    
    Tool("get_thermostat_status", 
         "Get current thermostat and temperature status", 
         controller.get_thermostat_status, 
         {}),
    
    Tool("control_device", 
         "Turn smart devices on/off (tv, coffee_maker, washing_machine, refrigerator)", 
         controller.control_device, 
         {"device": "str", "on": "bool (optional)"}),
    
    Tool("lock_door", 
         "Lock or unlock front door", 
         controller.lock_door, 
         {"lock": "bool"}),
    
    Tool("control_garage", 
         "Open or close garage door", 
         controller.control_garage, 
         {"open_garage": "bool"}),
    
    Tool("get_home_status", 
         "Get complete status of all home devices", 
         controller.get_home_status, 
         {}),
    
    # Tool("create_scene", 
    #      "Create a new automation scene with predefined actions", 
    #      controller.create_scene, 
    #      {"scene_name": "str", "actions": "list"}),
    
    Tool("activate_scene", 
         "Activate a predefined scene", 
         controller.activate_scene, 
         {"scene_name": "str"}),
    
    Tool("get_device_log", 
         "Get recent device activity log", 
         controller.get_device_log, 
         {"limit": "int (optional)"}),

    Tool("create_scene",
        "Create an automation scene with multiple actions",
        controller.create_scene,
        {"scene_name": "str", "actions": "list of action strings"}),

    Tool("execute_scene",
        "Execute a previously created scene",
        controller.execute_scene,
        {"scene_name": "str"}),

    Tool("get_scenes",
        "Get all available scenes",
        controller.get_scenes,
        {}),

    Tool("delete_scene",
        "Delete a scene",
        controller.delete_scene,
        {"scene_name": "str"}),         
]

# Create agent
home_agent = Agent(
    name="JARVIS",
    role="Home Automation Manager",
    tools=home_tools,
    system_instructions="You are a smart home assistant. Help users control their home efficiently. When controlling multiple devices, do it step by step."
)


if __name__ == "__main__":
    # Test home automation
    print("=" * 70)
    print("HOME AUTOMATION AGENT - Interactive Demo")
    print("=" * 70)
    
    test_requests = [
        "What's the current status of my home?",
        "Turn on the living room lights with 80% brightness",
        "Set the temperature to 75 degrees in cooling mode",
        "Turn on the coffee maker and TV",
        "Lock the door and close the garage",
        "Show me recent device activity"
    ]
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * 70)
        result = home_agent.think_and_act(request, verbose=False)
        print(f"Agent: {result}\n")
        home_agent.clear_memory()