#!/usr/bin/env python3
"""
Test script to verify Home Agent can properly control thermostats
"""
from agents.home_agent import home_agent

print("\n" + "="*70)
print("TESTING HOME AGENT - THERMOSTAT CONTROL")
print("="*70)

test_commands = [
    "What's the current status of the upstairs thermostat?",
    "Set the upstairs thermostat to 72 degrees",
]

for command in test_commands:
    print(f"\n{'='*70}")
    print(f"USER: {command}")
    print(f"{'='*70}")

    response = home_agent.think_and_act(command, verbose=True)

    print(f"\n{'='*70}")
    print(f"AGENT RESPONSE:")
    print(f"{'='*70}")
    print(response)
    print()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nExpected behavior:")
print("1. First query should use get_status to check current state")
print("2. Second query should use control_device to actually set temperature")
print("="*70)
