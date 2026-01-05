"""
Test script to verify the agent framework can parse different action formats
"""
import sys
sys.path.append('/home/mahen/Documents/ai/agent/agent-sphere/agent-sphere-system')

from base.agent_framework import Agent, Tool
from agents.home_agent import home_agent

print("Testing action parsing with different formats...")
print("=" * 70)

# Test the _parse_action method directly
test_cases = [
    {
        "name": "JSON format (preferred)",
        "response": '{"action": "get_status", "parameters": {"entity_id": "fan.master_bedroom_fan"}}',
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    },
    {
        "name": "Python function call format",
        "response": 'get_status(entity_id="fan.master_bedroom_fan")',
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    },
    {
        "name": "Python function call with single quotes",
        "response": "get_status(entity_id='fan.master_bedroom_fan')",
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    },
    {
        "name": "TOOL/PARAMS format",
        "response": 'TOOL: get_status\nPARAMS: {"entity_id": "fan.master_bedroom_fan"}',
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    },
    {
        "name": "Mixed text with JSON",
        "response": 'I will check the status now. {"action": "get_status", "parameters": {"entity_id": "fan.master_bedroom_fan"}}',
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    },
    {
        "name": "Mixed text with Python call",
        "response": 'Let me check: get_status(entity_id="fan.master_bedroom_fan")',
        "expected_action": "get_status",
        "expected_entity": "fan.master_bedroom_fan"
    }
]

print("\nTesting _parse_action method:")
print("-" * 70)

for test in test_cases:
    result = home_agent._parse_action(test["response"])

    if result:
        action = result.get("action")
        entity = result.get("parameters", {}).get("entity_id")

        success = (action == test["expected_action"] and entity == test["expected_entity"])
        status = "✅ PASS" if success else "❌ FAIL"

        print(f"\n{status} - {test['name']}")
        print(f"  Input: {test['response'][:60]}...")
        print(f"  Parsed: action={action}, entity_id={entity}")
    else:
        print(f"\n❌ FAIL - {test['name']}")
        print(f"  Input: {test['response'][:60]}...")
        print(f"  Parsed: None (couldn't parse)")

print("\n" + "=" * 70)
print("All parsing tests complete!")
