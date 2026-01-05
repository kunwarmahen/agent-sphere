"""
Home Assistant API Client - Connects to a live Home Assistant instance.
Requires a running Home Assistant instance and a Long-Lived Access Token.
"""
import requests
import json
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- Configuration from .env ---
HA_BASE_URL = os.getenv("HA_BASE_URL", "http://localhost:8123/api")
HA_ACCESS_TOKEN = os.getenv("HA_ACCESS_TOKEN", "")

# Thermostat Configuration
# Option 1: Show all thermostats (set to None or empty list)
# Option 2: Show specific thermostats only (list of entity IDs)
# Example: THERMOSTATS_TO_SHOW = ["climate.thermostat", "climate.thermostat_2"]
THERMOSTATS_TO_SHOW = None  # None = show all, or specify list like ["climate.thermostat"]

# Friendly name mappings for easier agent control
THERMOSTAT_ALIASES = {
    "downstairs": "climate.thermostat",
    "upstairs": "climate.thermostat_2",
    "main floor": "climate.thermostat",
    "second floor": "climate.thermostat_2",
}

LIGHT_ALIASES = {
    "living room": "light.living_room_lights",
    "kitchen": "light.kitchen_lights",
    "master bedroom": "light.master_bedroom_lights",
    "bedroom": "light.master_bedroom_lights",
    "drawing room": "light.drawingroom_lights",
    "guest room": "light.guestroom_lights",
    "stairs": "light.lights",
    "stairs light": "light.lights",
    "stairway": "light.lights",
    "piano": "light.piano_light_socket",
    "under cabinet": "light.under_cabinet_lights_socket",
    "cabinet": "light.under_cabinet_lights_socket",
}

SWITCH_ALIASES = {
    "washer": "switch.washer_power",
    "dryer": "switch.dryer_power",
    "fountain": "switch.fountain_socket",
    "fountain light": "switch.fountain_light_socket",
    "fireplace": "switch.fireplace_socket",
}

FAN_ALIASES = {
    "living room fan": "fan.living_room_fan",
    "guest room fan": "fan.guest_room_fan",
    "purple room fan": "fan.purple_room_fan",
    "orange room fan": "fan.orange_room_fan",
    "master bedroom fan": "fan.master_bedroom_fan",
}
# ---------------------

class HomeAssistantClient:
    """Handles communication with the Home Assistant REST API."""
    def __init__(self):
        if HA_ACCESS_TOKEN == "YOUR_LONG_LIVED_ACCESS_TOKEN":
            logger.warning("Home Assistant token is not configured. Tools will fail.")
        
        self.headers = {
            "Authorization": f"Bearer {HA_ACCESS_TOKEN}",
            "content-type": "application/json",
        }
        logger.info(f"Initialized Home Assistant Client for {HA_BASE_URL}")

    def _call_ha_api(self, endpoint: str, data: Dict = None) -> Dict:
        """Helper for making API calls to Home Assistant."""
        url = f"{HA_BASE_URL}/{endpoint}"
        try:
            if data:
                response = requests.post(url, headers=self.headers, data=json.dumps(data), timeout=5)
            else:
                response = requests.get(url, headers=self.headers, timeout=5)
            
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            error = f"API Error: {e.response.status_code} - {e.response.text[:100]}..."
            logger.error(error)
            return {"error": error}
        except requests.exceptions.RequestException as e:
            error = f"Connection Error: Could not connect to Home Assistant at {HA_BASE_URL}. Is it running? Details: {e}"
            logger.error(error)
            return {"error": error}
        except json.JSONDecodeError:
            return {"error": "API returned invalid JSON."}

    # --- Public Methods Matching Agent Tools ---

    def get_status(self, entity_id: str = "all") -> Any:
        """Gets the current state of a specific entity or all entities."""
        if entity_id == "all":
            # /api/states returns all entity states
            return self._call_ha_api("states")
        
        # /api/states/<entity_id> returns one entity state
        result = self._call_ha_api(f"states/{entity_id}")
        if isinstance(result, dict) and 'error' not in result:
            return {
                "entity_id": result.get('entity_id'),
                "state": result.get('state'),
                "attributes": result.get('attributes')
            }
        return result

    def control_device(self, entity_id: str, domain: str, service: str, service_data: Dict = None) -> str:
        """
        Sends a control command (service call) to a specific device.
        Requires domain (e.g., 'light'), service (e.g., 'turn_on'), and data.
        """
        # Home Assistant uses a domain/service structure for control
        endpoint = f"services/{domain}/{service}"
        
        # Prepare the payload
        data = {"entity_id": entity_id}
        if service_data:
            data.update(service_data)
            
        result = self._call_ha_api(endpoint, data=data)
        
        if 'error' in result:
            return f"Error controlling {entity_id}: {result['error']}"
        
        return f"Successfully called service {domain}.{service} on {entity_id}."

    def create_scene(self, scene_name: str, actions: List[Dict]) -> str:
        """Creates an automation or script (Home Assistant's scene equivalent)."""
        return "Tool Not Implemented: Creating complex automations is beyond a simple API call. Please use the Home Assistant UI."

    def execute_scene(self, scene_entity_id: str) -> str:
        """Executes a previously created scene entity (script or scene)."""
        # Calls the homeassistant.turn_on service on the scene/script entity
        return self.control_device(
            entity_id=scene_entity_id,
            domain="homeassistant",
            service="turn_on"
        )
        
    def get_scenes(self) -> str:
        """Returns a list of available scenes/scripts from the API in JSON format."""
        all_states = self._call_ha_api("states")
        scenes_list = {"scenes": []}

        if isinstance(all_states, list):
            for state in all_states:
                entity_id = state.get('entity_id', '')
                if entity_id.startswith(('scene.', 'script.')):
                    # Extract scene info
                    attributes = state.get('attributes', {})
                    scene_name = entity_id.split('.')[1]
                    scenes_list["scenes"].append({
                        "name": scene_name,
                        "entity_id": entity_id,
                        "actions": [entity_id],  # Just the entity ID for compatibility
                        "action_count": 1,
                        "executions": 0,  # Can't track this from HA API
                        "friendly_name": attributes.get('friendly_name', scene_name)
                    })

        return json.dumps(scenes_list)

    def delete_scene(self, scene_entity_id: str) -> str:
        """Deletes a scene via API."""
        return "Tool Not Implemented: Deleting entities is a high-risk operation and is disabled for safety."

    def get_activity_log(self) -> Any:
        """Fetches recent device activity (HA History API)."""
        # This requires the /api/history/period endpoint, which is complex.
        return self._call_ha_api("history/period")

    # ===== COMPATIBILITY METHODS FOR API SERVER =====

    def get_home_status(self) -> str:
        """
        Get home status in the format expected by the frontend.
        Transforms Home Assistant entities into the legacy format.
        """
        all_entities = self._call_ha_api("states")

        if isinstance(all_entities, dict) and 'error' in all_entities:
            # Return a minimal valid structure on error
            return json.dumps({
                "lights": {},
                "thermostat": {"current_temp": 0, "target_temp": 0, "mode": "off", "humidity": 0},
                "thermostats": [],
                "security": {"door_locked": False, "garage_open": False, "motion_detected": False},
                "devices": {},
                "error": all_entities['error']
            })

        # Initialize status structure
        status = {
            "lights": {},
            "switches": {},
            "fans": {},
            "thermostat": {"current_temp": 0, "target_temp": 0, "mode": "off", "humidity": 0},
            "thermostats": [],  # List of all thermostats
            "security": {"door_locked": False, "garage_open": False, "motion_detected": False},
            "devices": {},  # Legacy support
            "media_players": {},
        }

        # Parse entities
        for entity in all_entities:
            entity_id = entity.get('entity_id', '')
            state = entity.get('state', 'unknown')
            attributes = entity.get('attributes', {})

            # Lights
            if entity_id.startswith('light.'):
                # Skip unavailable lights
                if state == 'unavailable':
                    continue
                light_key = entity_id.replace('light.', '')
                status["lights"][light_key] = {
                    "on": (state == 'on'),
                    "name": attributes.get('friendly_name', light_key.replace('_', ' ').title()),
                    "brightness": attributes.get('brightness', 0) if state == 'on' else 0
                }

            # Climate/Thermostat
            elif entity_id.startswith('climate.'):
                # Check if we should include this thermostat
                if THERMOSTATS_TO_SHOW is None or entity_id in THERMOSTATS_TO_SHOW:
                    thermostat_data = {
                        "entity_id": entity_id,
                        "name": attributes.get('friendly_name', entity_id.split('.')[1].replace('_', ' ').title()),
                        "current_temp": attributes.get('current_temperature', 0),
                        "target_temp": attributes.get('temperature', 0),
                        "mode": state,  # The state itself is the mode
                        "humidity": attributes.get('current_humidity', 0)
                    }
                    status["thermostats"].append(thermostat_data)

                    # Set the first thermostat as the primary for backward compatibility
                    if not status["thermostat"]["current_temp"]:
                        status["thermostat"] = {
                            "current_temp": thermostat_data["current_temp"],
                            "target_temp": thermostat_data["target_temp"],
                            "mode": thermostat_data["mode"],
                            "humidity": thermostat_data["humidity"]
                        }

            # Locks
            elif entity_id.startswith('lock.') and 'door' in entity_id:
                status["security"]["door_locked"] = (state == 'locked')

            # Garage/Covers
            elif entity_id.startswith('cover.') and 'garage' in entity_id:
                status["security"]["garage_open"] = (state == 'open')

            # Motion sensors
            elif entity_id.startswith('binary_sensor.') and 'motion' in entity_id:
                status["security"]["motion_detected"] = (state == 'on')

            # Switches
            elif entity_id.startswith('switch.'):
                if state == 'unavailable':
                    continue
                switch_key = entity_id.replace('switch.', '')
                status["switches"][switch_key] = {
                    "on": (state == 'on'),
                    "name": attributes.get('friendly_name', switch_key.replace('_', ' ').title())
                }
                # Also add to legacy devices for backward compatibility
                status["devices"][switch_key] = {"on": (state == 'on')}

            # Fans
            elif entity_id.startswith('fan.'):
                if state == 'unavailable':
                    continue
                fan_key = entity_id.replace('fan.', '')
                status["fans"][fan_key] = {
                    "on": (state == 'on'),
                    "name": attributes.get('friendly_name', fan_key.replace('_', ' ').title()),
                    "speed": attributes.get('percentage', 0) if state == 'on' else 0
                }

            # Media Players
            elif entity_id.startswith('media_player.'):
                if state == 'unavailable':
                    continue
                player_key = entity_id.replace('media_player.', '')
                status["media_players"][player_key] = {
                    "state": state,
                    "name": attributes.get('friendly_name', player_key.replace('_', ' ').title()),
                    "volume": attributes.get('volume_level', 0)
                }

        return json.dumps(status)

    def toggle_light(self, room: str, state: bool = None, brightness: int = None, color_temp: int = None) -> str:
        """Toggle a light with optional brightness and color temperature."""
        entity_id = f"light.{room}"

        if state is None:
            # Get current state to toggle
            current = self._call_ha_api(f"states/{entity_id}")
            if isinstance(current, dict) and current.get('state') == 'on':
                state = False
            else:
                state = True

        # Prepare service data
        service_data = {}
        if brightness is not None:
            service_data['brightness_pct'] = brightness
        if color_temp is not None:
            service_data['color_temp'] = color_temp

        # Call appropriate service
        service = 'turn_on' if state else 'turn_off'
        return self.control_device(entity_id, 'light', service, service_data)

    def set_thermostat(self, temperature: int, mode: str = None, entity_id: str = None) -> str:
        """Set thermostat temperature and mode."""
        climate_entity = entity_id

        # Check if entity_id is an alias (e.g., "upstairs", "downstairs")
        if climate_entity and climate_entity.lower() in THERMOSTAT_ALIASES:
            climate_entity = THERMOSTAT_ALIASES[climate_entity.lower()]
            logger.info(f"Resolved thermostat alias '{entity_id}' to '{climate_entity}'")

        # If no specific entity_id provided, find the first climate entity
        if not climate_entity:
            all_entities = self._call_ha_api("states")

            if isinstance(all_entities, list):
                for entity in all_entities:
                    if entity.get('entity_id', '').startswith('climate.'):
                        # Filter by THERMOSTATS_TO_SHOW if configured
                        if THERMOSTATS_TO_SHOW is None or entity['entity_id'] in THERMOSTATS_TO_SHOW:
                            climate_entity = entity['entity_id']
                            break

        if not climate_entity:
            return "No climate entity found in Home Assistant"

        results = []

        # Set temperature
        temp_result = self.control_device(
            climate_entity,
            'climate',
            'set_temperature',
            {'temperature': temperature}
        )
        results.append(temp_result)

        # Set mode if provided
        if mode:
            mode_result = self.control_device(
                climate_entity,
                'climate',
                'set_hvac_mode',
                {'hvac_mode': mode}
            )
            results.append(mode_result)

        return " | ".join(results)

    def lock_door(self, lock: bool = True) -> str:
        """Lock or unlock the door."""
        # Find lock entity
        all_entities = self._call_ha_api("states")
        lock_entity = None

        if isinstance(all_entities, list):
            for entity in all_entities:
                entity_id = entity.get('entity_id', '')
                if entity_id.startswith('lock.') and 'door' in entity_id:
                    lock_entity = entity_id
                    break

        if not lock_entity:
            return "No door lock entity found in Home Assistant"

        service = 'lock' if lock else 'unlock'
        return self.control_device(lock_entity, 'lock', service)

    def control_garage(self, open_garage: bool) -> str:
        """Open or close the garage."""
        # Find garage cover entity
        all_entities = self._call_ha_api("states")
        garage_entity = None

        if isinstance(all_entities, list):
            for entity in all_entities:
                entity_id = entity.get('entity_id', '')
                if entity_id.startswith('cover.') and 'garage' in entity_id:
                    garage_entity = entity_id
                    break

        if not garage_entity:
            return "No garage cover entity found in Home Assistant"

        service = 'open_cover' if open_garage else 'close_cover'
        return self.control_device(garage_entity, 'cover', service)

    def get_device_log(self, limit: int = 10) -> str:
        """Get recent device activity log."""
        # Return history data if available
        history = self.get_activity_log()
        if isinstance(history, list):
            return json.dumps(history[-limit:])
        return json.dumps([])

    def get_thermostat_status(self) -> str:
        """Get thermostat status."""
        all_entities = self._call_ha_api("states")

        if isinstance(all_entities, list):
            for entity in all_entities:
                if entity.get('entity_id', '').startswith('climate.'):
                    attrs = entity.get('attributes', {})
                    return json.dumps({
                        "current_temp": attrs.get('current_temperature', 0),
                        "target_temp": attrs.get('temperature', 0),
                        "mode": attrs.get('hvac_mode', 'off'),
                        "humidity": attrs.get('current_humidity', 0)
                    })

        return json.dumps({"current_temp": 0, "target_temp": 0, "mode": "off", "humidity": 0})