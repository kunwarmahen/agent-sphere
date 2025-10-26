"""
=============================================================================
              EXAMPLE USAGE PATTERNS - How to Use the Agents
=============================================================================

This file shows various patterns for using the multi-agent system.
"""

# ============================================================================
# EXAMPLE 1: Simple Single-Turn Interaction
# ============================================================================

def example_simple_interaction():
    """Most basic usage - ask agent something and get response"""
    from agents.home_agent import home_agent
    
    print("=" * 70)
    print("Example 1: Simple Single-Turn Interaction")
    print("=" * 70)
    
    # Ask the agent something
    response = home_agent.think_and_act("Turn on all the lights in my house")
    print(f"Agent response: {response}")


# ============================================================================
# EXAMPLE 2: Multi-Turn Conversation
# ============================================================================

def example_multi_turn_conversation():
    """Agent maintains context across multiple turns"""
    from agents.calendar_agent import calendar_agent
    
    print("\n" + "=" * 70)
    print("Example 2: Multi-Turn Conversation with Memory")
    print("=" * 70)
    
    # First turn
    print("\nUser: What meetings do I have today?")
    response1 = calendar_agent.think_and_act("What meetings do I have today?")
    print(f"Agent: {response1}\n")
    
    # Second turn - agent remembers context
    print("User: Can you add another meeting at 3 PM?")
    response2 = calendar_agent.think_and_act("Add a meeting with Sarah at 3 PM for 1 hour")
    print(f"Agent: {response2}\n")
    
    # Third turn - continues conversation
    print("User: Show me my busy times")
    response3 = calendar_agent.think_and_act("Show me all my busy times this week")
    print(f"Agent: {response3}\n")
    
    # Clear memory for next interaction
    calendar_agent.clear_memory()


# ============================================================================
# EXAMPLE 3: Working with Multiple Agents
# ============================================================================

def example_multiple_agents():
    """Coordinate between different agents"""
    from agents.home_agent import home_agent
    from agents.calendar_agent import calendar_agent
    from agents.finance_agent import finance_agent
    
    print("\n" + "=" * 70)
    print("Example 3: Coordinating Multiple Agents")
    print("=" * 70)
    
    # Home agent prepares for meeting
    print("\n[Preparing for a meeting...]")
    print("\n1. Home Agent - Setting up home:")
    response1 = home_agent.think_and_act(
        "I have a client meeting in 30 minutes. Make sure my home looks presentable - "
        "dim the lights to 60% brightness and set a pleasant temperature"
    )
    print(f"   {response1}\n")
    home_agent.clear_memory()
    
    # Calendar agent checks schedule
    print("2. Calendar Agent - Checking meeting details:")
    response2 = calendar_agent.think_and_act(
        "When is my next client meeting and who is attending?"
    )
    print(f"   {response2}\n")
    calendar_agent.clear_memory()
    
    # Finance agent tracks meeting expense
    print("3. Finance Agent - Logging expense:")
    response3 = finance_agent.think_and_act(
        "I spent $85 on refreshments for the client meeting"
    )
    print(f"   {response3}\n")
    finance_agent.clear_memory()


# ============================================================================
# EXAMPLE 4: Error Handling and Edge Cases
# ============================================================================

def example_error_handling():
    """Gracefully handle errors and edge cases"""
    from agents.home_agent import home_agent
    
    print("\n" + "=" * 70)
    print("Example 4: Error Handling")
    print("=" * 70)
    
    # Try invalid room
    print("\n1. Invalid room name:")
    response = home_agent.think_and_act("Turn on lights in the observatory")
    print(f"   Agent: {response}\n")
    home_agent.clear_memory()
    
    # Try invalid temperature
    print("2. Out-of-range temperature:")
    response = home_agent.think_and_act("Set thermostat to 120 degrees")
    print(f"   Agent: {response}\n")
    home_agent.clear_memory()
    
    # Try non-existent tool
    print("3. Invalid request:")
    response = home_agent.think_and_act("Turn into a time machine")
    print(f"   Agent: {response}\n")
    home_agent.clear_memory()


# ============================================================================
# EXAMPLE 5: Complex Workflow - Morning Routine Automation
# ============================================================================

def example_morning_routine():
    """Complex workflow: Complete morning routine"""
    from agents.home_agent import home_agent
    from agents.calendar_agent import calendar_agent
    from agents.finance_agent import finance_agent
    
    print("\n" + "=" * 70)
    print("Example 5: Complete Morning Routine Workflow")
    print("=" * 70)
    
    print("\n[7:00 AM - Wake up and start morning routine]\n")
    
    # Step 1: Wake up the home
    print("Step 1: Home automation wakes up the house")
    response = home_agent.think_and_act(
        "It's morning! Turn on all lights, set temperature to 72, "
        "and start the coffee maker"
    )
    print(f"   {response[:100]}...\n")
    home_agent.clear_memory()
    
    # Step 2: Check calendar for today
    print("Step 2: Check today's schedule")
    response = calendar_agent.think_and_act(
        "Good morning! What's on my calendar for today? "
        "Do I have any important meetings?"
    )
    print(f"   {response[:100]}...\n")
    calendar_agent.clear_memory()
    
    # Step 3: Check emails
    print("Step 3: Check important emails")
    response = calendar_agent.think_and_act(
        "Show me any unread emails from my boss or important clients"
    )
    print(f"   {response[:100]}...\n")
    calendar_agent.clear_memory()
    
    # Step 4: Financial check
    print("Step 4: Quick financial status")
    response = finance_agent.think_and_act(
        "What's my financial summary? Am I on track with my budget?"
    )
    print(f"   {response[:100]}...\n")
    finance_agent.clear_memory()
    
    print("[Morning routine complete!]\n")


# ============================================================================
# EXAMPLE 6: Data Extraction and Analysis
# ============================================================================

def example_data_analysis():
    """Use agents to analyze and extract data"""
    from agents.finance_agent import finance_agent
    
    print("\n" + "=" * 70)
    print("Example 6: Financial Analysis and Insights")
    print("=" * 70)
    
    print("\n1. Get spending breakdown:")
    response = finance_agent.think_and_act(
        "Analyze my spending for the last month. "
        "Where am I spending the most money?"
    )
    print(f"   {response}\n")
    finance_agent.clear_memory()
    
    print("2. Investment performance check:")
    response = finance_agent.think_and_act(
        "How are my investments doing? "
        "Which ones are performing well and which are underperforming?"
    )
    print(f"   {response}\n")
    finance_agent.clear_memory()
    
    print("3. Goal progress tracking:")
    response = finance_agent.think_and_act(
        "Show me my financial goals and how much progress I've made. "
        "Which goal am I closest to completing?"
    )
    print(f"   {response}\n")
    finance_agent.clear_memory()


# ============================================================================
# EXAMPLE 7: Using Verbose Mode for Debugging
# ============================================================================

def example_verbose_mode():
    """See the agent's reasoning process"""
    from agents.home_agent import home_agent
    
    print("\n" + "=" * 70)
    print("Example 7: Verbose Mode - See Agent's Reasoning")
    print("=" * 70)
    
    print("\nRequest: 'Prepare home for dinner guests'\n")
    
    response = home_agent.think_and_act(
        "I have dinner guests arriving in an hour. "
        "Make the house look nice and comfortable.",
        verbose=True  # Show step-by-step reasoning
    )
    
    print(f"\nFinal response: {response}\n")
    home_agent.clear_memory()


# ============================================================================
# EXAMPLE 8: Custom Agent Integration
# ============================================================================

def example_custom_tool_integration():
    """Example of how to add custom tools to an agent"""
    from base.agent_framework import Agent, Tool
    
    print("\n" + "=" * 70)
    print("Example 8: Creating Custom Tools and Agent")
    print("=" * 70)
    
    # Define custom functions
    def weather_check(location: str) -> str:
        """Simulated weather check"""
        return f"Weather in {location}: 72°F, Sunny, Humidity 45%"
    
    def get_recommendations(category: str) -> str:
        """Simulated recommendation engine"""
        recommendations = {
            "movies": "Dune 2, Oppenheimer, Killers of the Flower Moon",
            "restaurants": "Italian Bistro, Asian Fusion, Steakhouse",
            "activities": "Hiking, Museum visit, Movie night"
        }
        return recommendations.get(category, "No recommendations available")
    
    # Create custom tools
    custom_tools = [
        Tool(
            "check_weather",
            "Check weather for a location",
            weather_check,
            {"location": "str"}
        ),
        Tool(
            "get_recommendations",
            "Get recommendations for movies, restaurants, or activities",
            get_recommendations,
            {"category": "str (movies/restaurants/activities)"}
        ),
    ]
    
    # Create custom agent
    custom_agent = Agent(
        name="PlannnerBot",
        role="Event and Activity Planner",
        tools=custom_tools,
        system_instructions="Help users plan events and activities by checking weather and recommending places."
    )
    
    # Use the custom agent
    print("\n1. Planning an outdoor activity:")
    response = custom_agent.think_and_act(
        "I want to plan an outdoor activity this weekend. "
        "What's the weather like and what activities would you recommend?"
    )
    print(f"   {response}\n")
    custom_agent.clear_memory()
    
    print("2. Planning dinner and entertainment:")
    response = custom_agent.think_and_act(
        "Suggest a restaurant and something to do after dinner"
    )
    print(f"   {response}\n")
    custom_agent.clear_memory()


# ============================================================================
# EXAMPLE 9: Sequential Task Execution
# ============================================================================

def example_sequential_tasks():
    """Execute a sequence of related tasks"""
    from agents.finance_agent import finance_agent
    
    print("\n" + "=" * 70)
    print("Example 9: Sequential Financial Task Execution")
    print("=" * 70)
    
    tasks = [
        "Check my current account balances",
        "I just bought $50 of groceries",
        "I spent $25 on a book for entertainment",
        "Analyze my spending in these two categories",
        "Should I be worried about my grocery budget?",
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task}")
        response = finance_agent.think_and_act(task)
        print(f"Result: {response[:150]}...")
    
    finance_agent.clear_memory()


# ============================================================================
# EXAMPLE 10: Batch Processing
# ============================================================================

def example_batch_processing():
    """Process multiple similar requests"""
    from agents.home_agent import home_agent
    
    print("\n" + "=" * 70)
    print("Example 10: Batch Processing - Control Multiple Devices")
    print("=" * 70)
    
    devices_to_control = [
        ("Turn on the TV", home_agent),
        ("Start the coffee maker", home_agent),
        ("Set lights to 75% brightness in living room", home_agent),
        ("Check home status", home_agent),
    ]
    
    for request, agent in devices_to_control:
        print(f"\n→ {request}")
        response = agent.think_and_act(request)
        print(f"  ✓ {response[:80]}...")
        agent.clear_memory()


# ============================================================================
# MAIN - Run all examples
# ============================================================================

def main():
    """Run selected examples"""
    print("\n" + "=" * 70)
    print("             MULTI-AGENT SYSTEM - USAGE EXAMPLES")
    print("=" * 70)
    
    examples = [
        ("Simple interaction", example_simple_interaction),
        ("Multi-turn conversation", example_multi_turn_conversation),
        ("Multiple agents", example_multiple_agents),
        ("Error handling", example_error_handling),
        ("Morning routine workflow", example_morning_routine),
        ("Data analysis", example_data_analysis),
        ("Verbose mode", example_verbose_mode),
        ("Custom tools", example_custom_tool_integration),
        ("Sequential tasks", example_sequential_tasks),
        ("Batch processing", example_batch_processing),
    ]
    
    while True:
        print("\nSelect an example to run:\n")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print(f"  {len(examples) + 1}. Run all examples")
        print(f"  {len(examples) + 2}. Exit\n")
        
        choice = input("Enter choice: ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(examples) + 1:
                for name, func in examples:
                    try:
                        func()
                    except Exception as e:
                        print(f"Error running {name}: {e}")
                    input("\n[Press Enter to continue...]")
            elif 1 <= choice_num <= len(examples):
                examples[choice_num - 1][1]()
            elif choice_num == len(examples) + 2:
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a number")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()