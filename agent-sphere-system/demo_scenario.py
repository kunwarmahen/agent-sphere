"""
Real-World Scenario Demo - Orchestrates multiple AI agents for a complex workflow
Scenario: A busy professional's morning routine with multi-agent coordination
"""

import sys
from home_agent import home_agent, controller as home_controller
from calendar_agent import calendar_agent, manager as calendar_manager
from finance_agent import finance_agent, planner as finance_planner


class ScenarioDemo:
    """Orchestrates a realistic multi-agent scenario"""
    
    @staticmethod
    def print_section(title: str):
        """Print formatted section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    @staticmethod
    def print_agent_response(agent_name: str, response: str):
        """Print agent response with formatting"""
        print(f"\n[{agent_name}]: {response}\n")
    
    @staticmethod
    def scenario_morning_routine():
        """Scenario 1: Complete morning routine with multiple agents"""
        
        ScenarioDemo.print_section("SCENARIO 1: Smart Morning Routine")
        print("\nTime: 7:00 AM - It's Monday morning and you wake up...")
        
        # Step 1: Check home automation
        print("\n--- 1. Smart Home Automation ---")
        response = home_agent.think_and_act(
            "Good morning! Turn on all the lights in my home and set the thermostat to 72 degrees",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Home Agent", response)
        home_agent.clear_memory()
        
        # Step 2: Check calendar and emails
        print("\n--- 2. Calendar & Email Check ---")
        response = calendar_agent.think_and_act(
            "Do I have any important meetings today? What time is my standup?",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Calendar Agent", response)
        calendar_agent.clear_memory()
        
        # Step 3: Coffee maker automation
        print("\n--- 3. Kitchen Automation ---")
        response = home_agent.think_and_act(
            "Turn on the coffee maker, I need it ready in 5 minutes",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Home Agent", response)
        home_agent.clear_memory()
        
        # Step 4: Email check
        print("\n--- 4. Important Messages ---")
        response = calendar_agent.think_and_act(
            "Show me any unread emails, especially from my boss",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Calendar Agent", response)
        calendar_agent.clear_memory()
        
        print("\n✓ Morning routine complete!")
    
    @staticmethod
    def scenario_financial_planning():
        """Scenario 2: Financial planning and budgeting"""
        
        ScenarioDemo.print_section("SCENARIO 2: Monthly Financial Planning")
        print("\nTime: 9:00 PM - End of the month, reviewing finances...")
        
        # Step 1: Financial summary
        print("\n--- 1. Financial Overview ---")
        response = finance_agent.think_and_act(
            "Give me a complete overview of my financial situation",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        # Step 2: Spending analysis
        print("\n--- 2. Spending Analysis ---")
        response = finance_agent.think_and_act(
            "Analyze my spending this month. Am I over budget in any categories?",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        # Step 3: Investment check
        print("\n--- 3. Investment Performance ---")
        response = finance_agent.think_and_act(
            "How are my investments performing? Any gains or losses?",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        # Step 4: Goals progress
        print("\n--- 4. Financial Goals ---")
        response = finance_agent.think_and_act(
            "Show me my financial goals and how much progress I've made",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        # Step 5: Savings projection
        print("\n--- 5. Future Projections ---")
        response = finance_agent.think_and_act(
            "If I can save $600 per month, where will I be in 2 years?",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        print("\n✓ Financial review complete!")
    
    @staticmethod
    def scenario_busy_day():
        """Scenario 3: Managing a complex busy day"""
        
        ScenarioDemo.print_section("SCENARIO 3: Complex Busy Day Management")
        print("\nTime: 10:00 AM - Coordinating multiple tasks...")
        
        # Step 1: Secure home before leaving
        print("\n--- 1. Home Security Before Leaving ---")
        response = home_agent.think_and_act(
            "I'm heading out for the day. Lock the door and garage. Turn off all lights and set thermostat to 68 degrees.",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Home Agent", response)
        home_agent.clear_memory()
        
        # Step 2: Schedule a meeting
        print("\n--- 2. Schedule New Meeting ---")
        response = calendar_agent.think_and_act(
            "I need to schedule a 1-hour client meeting tomorrow at 2 PM. Find my next available slot and add it to my calendar.",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Calendar Agent", response)
        calendar_agent.clear_memory()
        
        # Step 3: Log expense
        print("\n--- 3. Log Daily Expense ---")
        response = finance_agent.think_and_act(
            "I just spent $45 on lunch with a client at a restaurant",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        # Step 4: Send follow-up email
        print("\n--- 4. Send Professional Email ---")
        response = calendar_agent.think_and_act(
            "Send an email to the client confirming our meeting tomorrow at 2 PM in Conference Room B",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Calendar Agent", response)
        calendar_agent.clear_memory()
        
        print("\n✓ Day successfully coordinated!")
    
    @staticmethod
    def scenario_emergency_response():
        """Scenario 4: Emergency response - high-paced situation"""
        
        ScenarioDemo.print_section("SCENARIO 4: Emergency Response Scenario")
        print("\nTime: 6:30 PM - Guest arriving in 30 minutes, system shutdown...")
        
        # Step 1: Emergency home prep
        print("\n--- 1. Quick Home Preparation ---")
        response = home_agent.think_and_act(
            "My parents are arriving in 30 minutes! Turn on all the lights, set temperature to 74, unlock the garage door, and make sure the TV is off",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Home Agent", response)
        home_agent.clear_memory()
        
        # Step 2: Update schedule
        print("\n--- 2. Calendar Update ---")
        response = calendar_agent.think_and_act(
            "Block 2 hours starting now for family time. Show me my status for today.",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Calendar Agent", response)
        calendar_agent.clear_memory()
        
        # Step 3: Report spending
        print("\n--- 3. Quick Budget Check ---")
        response = finance_agent.think_and_act(
            "I spent $120 on groceries for tonight's dinner. Am I still within my grocery budget?",
            verbose=False
        )
        ScenarioDemo.print_agent_response("Finance Agent", response)
        finance_agent.clear_memory()
        
        print("\n✓ Emergency response complete! Home ready for guests!")
    
    @staticmethod
    def print_current_state():
        """Print current state of all systems"""
        
        ScenarioDemo.print_section("CURRENT SYSTEM STATE")
        
        # Home state
        print("\n🏠 HOME AUTOMATION:")
        print(f"   Lights Status: {home_controller.lights}")
        print(f"   Thermostat: {home_controller.thermostat['target_temp']}°F (Current: {home_controller.thermostat['current_temp']}°F)")
        print(f"   Door Locked: {home_controller.security['door_locked']}")
        print(f"   Devices: {[f"{k}: {v['on']}" for k, v in home_controller.devices.items()]}")
        
        # Calendar state
        print("\n📅 CALENDAR & EMAIL:")
        print(f"   Unread Emails: {len([e for e in calendar_manager.emails if not e['read']])}")
        print(f"   Upcoming Events: {len([e for e in calendar_manager.calendar])}")
        
        # Financial state
        print("\n💰 FINANCES:")
        total = sum(finance_planner.accounts.values())
        print(f"   Total Net Worth: ${total:,.2f}")
        print(f"   Accounts: {[(k, f'${v:,.2f}') for k, v in finance_planner.accounts.items()]}")
        print(f"   Active Goals: {len([g for g in finance_planner.financial_goals if g['current'] < g['target']])}")


def main():
    """Run all scenarios"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  MULTI-AGENT AI SYSTEM - REAL-WORLD SCENARIOS DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print("\nThis demo showcases a coordinated multi-agent system handling")
    print("home automation, calendar/email management, and financial planning.")
    
    # Run scenarios
    try:
        ScenarioDemo.scenario_morning_routine()
        input("\n[Press Enter to continue to next scenario...]")
        
        ScenarioDemo.scenario_financial_planning()
        input("\n[Press Enter to continue to next scenario...]")
        
        ScenarioDemo.scenario_busy_day()
        input("\n[Press Enter to continue to next scenario...]")
        
        ScenarioDemo.scenario_emergency_response()
        input("\n[Press Enter to see final system state...]")
        
        ScenarioDemo.print_current_state()
        
        print("\n" + "=" * 80)
        print("✓ All scenarios completed successfully!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-agent coordination")
        print("  ✓ Tool usage and execution")
        print("  ✓ Reasoning and decision-making")
        print("  ✓ Real-world task management")
        print("  ✓ State management and memory")
        print("\nNext Steps:")
        print("  1. Extend agents with more tools")
        print("  2. Add real API integrations (Google Calendar, Gmail, etc.)")
        print("  3. Implement persistent storage")
        print("  4. Create custom agents for your use cases")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError running scenarios: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()