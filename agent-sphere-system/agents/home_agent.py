"""
Home Automation Agent - Smart home control with real-time device management via Home Assistant API
"""
import json
import logging
from base.agent_framework import Agent, Tool
from datetime import datetime
from typing import List, Any
# --- NEW IMPORT ---
# Replace the local manager with the Home Assistant Client
from agents.homeassistant.home_assistant_api import HomeAssistantClient 

logger = logging.getLogger(__name__)

# --- AGENT INITIALIZATION ---

try:
    # Initialize the Home Assistant Client (This is the actual integration)
    controller = HomeAssistantClient() 
except Exception as e:
    logger.error(f"Failed to initialize HomeAssistantClient: {e}")
    # Fallback dummy manager if API initialization fails
    class DummyController:
        def get_status(self, *args): return "ERROR: Home Assistant API setup failed."
        def control_device(self, *args): return "ERROR: Home Assistant API setup failed."
        def create_scene(self, *args): return "Tool Disabled: API Error."
        def execute_scene(self, *args): return "ERROR: Home Assistant API setup failed."
        def get_scenes(self): return []
        def delete_scene(self, *args): return "Tool Disabled: API Error."
        def get_activity_log(self): return []
    
    controller = DummyController()

# Define Tools
home_tools = [
    Tool("get_status",
         "Get the current state and attributes of a specific device entity (e.g., 'light.living_room_light') or 'all' devices.",
         controller.get_status,
         {"entity_id": "str (optional, Home Assistant entity ID, e.g., 'light.living_room_light', defaults to 'all')"}),

    Tool("control_device",
         "Send a service call command to control a device. REQUIRED for all control operations (turn on/off, set temperature, etc.). Examples: control lights, thermostats, locks, switches.",
         controller.control_device,
         {"entity_id": "str (required, e.g., 'climate.thermostat_2' for upstairs thermostat, 'light.bedroom' for bedroom light)",
          "domain": "str (required, entity type: 'climate' for thermostats, 'light' for lights, 'lock' for locks, 'switch' for switches)",
          "service": "str (required, action: 'set_temperature' for thermostats, 'turn_on'/'turn_off' for lights/switches, 'lock'/'unlock' for locks)",
          "service_data": "dict (optional, extra params as dict, e.g., {'temperature': 72} for thermostats, {'brightness_pct': 50} for lights)"}),

    Tool("execute_scene",
        "Execute a Home Assistant Scene or Script entity.",
        controller.execute_scene,
        {"scene_entity_id": "str (required, e.g., 'scene.good_night', 'script.morning_routine')"}),

    Tool("get_scenes",
        "Get all available Scene and Script entity IDs.",
        controller.get_scenes,
        {}),
        
    Tool("get_activity_log",
         "Fetches recent device activity history.",
         controller.get_activity_log,
         {}),
]

# Create agent
home_agent = Agent(
    name="Home Assistant Agent",
    role="Home Assistant Control Manager",
    tools=home_tools,
    system_instructions="""You are a smart home assistant connected to the Home Assistant REST API.

CRITICAL INSTRUCTIONS:
1. When the user asks you to CONTROL a device (turn on, turn off, set temperature, etc.), you MUST use the 'control_device' tool, NOT just 'get_status'.
2. Use 'get_status' ONLY to check current state, not to control devices.
3. When responding to status queries, provide CONCISE, NATURAL LANGUAGE answers. Never dump raw JSON to the user!

4. CRITICAL - Exact Entity IDs (use these EXACT strings):
   LIGHTS:
   - Stairs Light: light.lights (NOT light.stairs or light.stair)
   - Living Room: light.living_room_lights
   - Kitchen: light.kitchen_lights
   - Master Bedroom: light.master_bedroom_lights
   - Drawing Room: light.drawingroom_lights
   - Guest Room: light.guestroom_lights
   - Piano Light: light.piano_light_socket
   - Under Cabinet: light.under_cabinet_lights_socket

   FANS:
   - Living Room Fan: fan.living_room_fan
   - Guest Room Fan: fan.guest_room_fan
   - Purple Room Fan: fan.purple_room_fan
   - Orange Room Fan: fan.orange_room_fan
   - Master Bedroom Fan: fan.master_bedroom_fan

   SWITCHES:
   - Washer: switch.washer_power
   - Dryer: switch.dryer_power
   - Fountain: switch.fountain_socket
   - Fountain Light: switch.fountain_light_socket
   - Fireplace: switch.fireplace_socket

   THERMOSTATS:
   - Downstairs: climate.thermostat
   - Upstairs: climate.thermostat_2

5. For status queries (e.g., "is the master bedroom fan on?"):
   STEP 1: Identify the exact entity_id from the list above
   STEP 2: Use get_status(entity_id="fan.master_bedroom_fan") with the SPECIFIC entity
   STEP 3: Parse the response and give a simple answer like "Yes, the master bedroom fan is on" or "No, it's off"

   DO NOT use get_status(entity_id="all") for simple status queries! Only use "all" when you truly don't know the entity ID.

6. When you don't know the exact entity ID:
   STEP 1: Use get_status(entity_id="all") to list all entities
   STEP 2: Find the entity with matching friendly_name
   STEP 3: Use that EXACT entity_id in your control command
   STEP 4: Provide a CONCISE summary to the user, not the raw JSON dump!

7. Always execute the command when asked - don't just report what you see!

To control a thermostat:
   - Use control_device with domain="climate", service="set_temperature", service_data={"temperature": XX}
   - For "upstairs" thermostat, use entity_id="climate.thermostat_2"
   - For "downstairs" thermostat, use entity_id="climate.thermostat"

To control a fan:
   - Use control_device with domain="fan", service="turn_on" or "turn_off"
   - To set speed: service="turn_on", service_data={"percentage": XX} (0-100)

EXAMPLES:

STATUS QUERIES (checking state):
User: "Is the master bedroom fan on?"
→ get_status(entity_id="fan.master_bedroom_fan")
→ Response: "Yes, the master bedroom fan is currently on" (or "No, it's off")

User: "What's the temperature upstairs?"
→ get_status(entity_id="climate.thermostat_2")
→ Response: "The upstairs thermostat is currently 72°F with a target of 70°F"

CONTROL COMMANDS (changing state):
User: "Set upstairs thermostat to 72"
→ control_device(entity_id="climate.thermostat_2", domain="climate", service="set_temperature", service_data={"temperature": 72})

User: "Turn on bedroom light"
→ control_device(entity_id="light.master_bedroom_lights", domain="light", service="turn_on")

User: "Turn off stairs light"
→ control_device(entity_id="light.lights", domain="light", service="turn_off")
   (Note: It's light.lights, NOT light.stairs!)

User: "Turn on the washer"
→ control_device(entity_id="switch.washer_power", domain="switch", service="turn_on")

User: "Turn on the master bedroom fan"
→ control_device(entity_id="fan.master_bedroom_fan", domain="fan", service="turn_on")

User: "Turn on office light" (unknown entity)
→ STEP 1: get_status(entity_id="all") to find the entity
→ STEP 2: Search for "office" in friendly names
→ STEP 3: control_device with the found entity_id
"""
)


if __name__ == "__main__":
    # Test home automation
    print("\n" + "=" * 70)
    print("HOME ASSISTANT AGENT - Interactive Demo (ACTUAL API IMPLEMENTATION)")
    print("=" * 70)
    
    # --- NOTE: You MUST change 'light.kitchen' and 'climate.home_thermostat' to your actual entity IDs ---
    test_requests = [
        "What's the status of all my devices?",
        "Turn on the kitchen light with 80% brightness",
        "Set the thermostat to 72 degrees in cool mode",
        "Execute the 'scene.good_night' scene",
    ]
    
    # Example control parameters for the LLM to choose:
    # "Turn on the kitchen light with 80% brightness" -> 
    #   control_device(entity_id="light.kitchen", domain="light", service="turn_on", service_data={"brightness_pct": 80})
    # "Set the thermostat to 72 degrees in cool mode" -> 
    #   control_device(entity_id="climate.home_thermostat", domain="climate", service="set_hvac_mode", service_data={"hvac_mode": "cool"}) AND 
    #   control_device(entity_id="climate.home_thermostat", domain="climate", service="set_temperature", service_data={"temperature": 72})
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * 70)
        result = home_agent.think_and_act(request, verbose=True)
        print(f"\nAgent Final Response: {result}")