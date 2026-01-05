"""
Test script to verify the fan status query fix
"""
import sys
sys.path.append('/home/mahen/Documents/ai/agent/agent-sphere/agent-sphere-system')

from agents.home_agent import home_agent

print("Testing fan status query fix...")
print("=" * 70)

# Test the exact query the user reported
test_query = "Hey is master bedroom fan on?"
print(f"\nUser: {test_query}")
print("-" * 70)

result = home_agent.think_and_act(test_query, verbose=True)
print(f"\n{'='*70}")
print(f"Agent Response: {result}")
print("=" * 70)

# Verify it's a concise response, not a JSON dump
if len(result) > 500:
    print("\n⚠️  WARNING: Response is too long! Agent may still be dumping JSON.")
    print(f"Response length: {len(result)} characters")
else:
    print(f"\n✅ Response looks good! Length: {len(result)} characters")
