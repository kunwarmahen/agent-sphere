#!/usr/bin/env python3
"""
Test stairs light control through agent
"""
from agents.home_agent import home_agent

print("\n" + "="*70)
print("TESTING STAIRS LIGHT CONTROL")
print("="*70)

# Test getting status
print("\n1. Checking current status...")
print("-"*70)
response = home_agent.think_and_act("What's the status of the stairs light?", verbose=True)
print(f"\nAgent: {response}")

# Test turning off
print("\n" + "="*70)
print("2. Turning OFF stairs light...")
print("-"*70)
response = home_agent.think_and_act("Turn off the stairs light", verbose=True)
print(f"\nAgent: {response}")

# Check status again
print("\n" + "="*70)
print("3. Checking status after turning off...")
print("-"*70)
response = home_agent.think_and_act("What's the status of the stairs light?", verbose=True)
print(f"\nAgent: {response}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
