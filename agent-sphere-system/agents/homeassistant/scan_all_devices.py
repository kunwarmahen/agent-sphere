#!/usr/bin/env python3
"""
Scan all Home Assistant devices to help create friendly name mappings
"""
from agents.homeassistant.home_assistant_api import HomeAssistantClient

client = HomeAssistantClient()
all_entities = client._call_ha_api("states")

if isinstance(all_entities, dict) and 'error' in all_entities:
    print(f"Error: {all_entities['error']}")
    exit(1)

# Categorize entities
categories = {
    'lights': [],
    'switches': [],
    'locks': [],
    'covers': [],
    'fans': [],
    'media_players': [],
    'sensors': [],
    'binary_sensors': [],
    'cameras': [],
    'climate': [],
}

for entity in all_entities:
    entity_id = entity.get('entity_id', '')
    state = entity.get('state', 'unknown')
    attrs = entity.get('attributes', {})
    friendly_name = attrs.get('friendly_name', entity_id)

    domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'

    if domain == 'light':
        categories['lights'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'switch':
        categories['switches'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'lock':
        categories['locks'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'cover':
        categories['covers'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'fan':
        categories['fans'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'media_player':
        categories['media_players'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'climate':
        categories['climate'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state,
            'temp': attrs.get('current_temperature', 'N/A')
        })
    elif domain == 'camera':
        categories['cameras'].append({
            'id': entity_id,
            'name': friendly_name
        })
    elif domain == 'sensor':
        categories['sensors'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })
    elif domain == 'binary_sensor':
        categories['binary_sensors'].append({
            'id': entity_id,
            'name': friendly_name,
            'state': state
        })

# Print organized report
print("\n" + "="*80)
print("HOME ASSISTANT DEVICES - ORGANIZED BY TYPE")
print("="*80)

for category, items in categories.items():
    if items:
        print(f"\n{'='*80}")
        print(f"{category.upper().replace('_', ' ')} ({len(items)})")
        print("="*80)
        for item in items:
            if 'temp' in item:
                print(f"  {item['id']:<40} | {item['name']:<30} | {item['state']:<10} | {item['temp']}°")
            else:
                state_str = item.get('state', '')
                print(f"  {item['id']:<40} | {item['name']:<30} | {state_str}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
for category, items in categories.items():
    if items:
        print(f"  {category.replace('_', ' ').title():<20}: {len(items)}")
