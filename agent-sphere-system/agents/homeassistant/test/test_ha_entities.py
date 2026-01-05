#!/usr/bin/env python3
"""
Quick script to see all your Home Assistant entities
"""
from agents.homeassistant.home_assistant_api import HomeAssistantClient

client = HomeAssistantClient()

# Get all entities
all_entities = client._call_ha_api("states")

if isinstance(all_entities, dict) and 'error' in all_entities:
    print(f"Error: {all_entities['error']}")
    exit(1)

# Filter and display climate entities (thermostats)
print("\n" + "="*70)
print("CLIMATE ENTITIES (Thermostats)")
print("="*70)

climate_entities = [e for e in all_entities if e.get('entity_id', '').startswith('climate.')]

if not climate_entities:
    print("No climate entities found!")
else:
    for entity in climate_entities:
        entity_id = entity.get('entity_id')
        state = entity.get('state')
        attrs = entity.get('attributes', {})

        print(f"\n📊 {entity_id}")
        print(f"   State: {state}")
        print(f"   Friendly Name: {attrs.get('friendly_name', 'N/A')}")
        print(f"   Current Temp: {attrs.get('current_temperature', 'N/A')}°")
        print(f"   Target Temp: {attrs.get('temperature', 'N/A')}°")
        print(f"   Mode: {attrs.get('hvac_mode', 'N/A')}")
        print(f"   Humidity: {attrs.get('current_humidity', 'N/A')}%")

print("\n" + "="*70)
print(f"Total climate entities found: {len(climate_entities)}")
print("="*70)

# Also show other entity types for reference
print("\n" + "="*70)
print("SUMMARY OF ALL ENTITIES")
print("="*70)

entity_types = {}
for entity in all_entities:
    entity_id = entity.get('entity_id', '')
    domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'
    entity_types[domain] = entity_types.get(domain, 0) + 1

for domain, count in sorted(entity_types.items()):
    print(f"  {domain}: {count}")
