"""
=============================================================================
        MULTI-AGENT AI SYSTEM - MAIN ENTRY POINT WITH WORKFLOWS
=============================================================================

Main file that integrates agents, workflows, and workflow templates.
"""

import sys
from agent_framework import Agent
from home_agent import home_agent
from calendar_agent import calendar_agent
from finance_agent import finance_agent
from workflow_engine import WorkflowEngine
from workflow_builder import WorkflowBuilder
from workflow_templates import WorkflowTemplates


# Setup workflow engine
workflow_engine = WorkflowEngine()
workflow_engine.register_agent("home", home_agent)
workflow_engine.register_agent("calendar", calendar_agent)
workflow_engine.register_agent("finance", finance_agent)

workflow_builder = WorkflowBuilder(workflow_engine)


def print_menu():
    """Display main menu"""
    print("\n" + "=" * 70)
    print("      MULTI-AGENT AI SYSTEM WITH WORKFLOW ORCHESTRATION")
    print("=" * 70)
    print("\nSelect an option:\n")
    print("  1. Interact with Individual Agents")
    print("  2. Create & Execute Custom Workflows")
    print("  3. Use Workflow Templates")
    print("  4. Manage Workflows")
    print("  5. Run Pre-built Scenarios")
    print("  6. Exit\n")


def interact_with_agent(agent: Agent, agent_name: str):
    """Interactive loop with an agent"""
    print(f"\n{'=' * 70}")
    print(f"Interacting with {agent_name}")
    print(f"{'=' * 70}")
    print("\nType your requests in natural language. Type 'back' to return to main menu.\n")
    
    while True:
        user_input = input(f"You: ").strip()
        
        if user_input.lower() == 'back':
            agent.clear_memory()
            break
        
        if not user_input:
            continue
        
        print(f"\n[{agent_name} thinking...]")
        response = agent.think_and_act(user_input, verbose=False)
        print(f"\n{agent_name}: {response}\n")


def agents_menu():
    """Agent selection menu"""
    print("\n" + "=" * 70)
    print("INDIVIDUAL AGENT INTERACTION")
    print("=" * 70)
    print("\nSelect an agent:\n")
    print("  1. Home Automation Agent (JARVIS)")
    print("  2. Calendar & Email Agent (Assistant)")
    print("  3. Financial Planning Agent (FinanceBot)")
    print("  4. Back to main menu\n")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        interact_with_agent(home_agent, "JARVIS (Home Automation)")
    elif choice == '2':
        interact_with_agent(calendar_agent, "Assistant (Calendar & Email)")
    elif choice == '3':
        interact_with_agent(finance_agent, "FinanceBot (Financial Planning)")
    elif choice == '4':
        return
    else:
        print("\n❌ Invalid choice. Please try again.")


def workflow_creation_menu():
    """Workflow creation menu"""
    print("\n" + "=" * 70)
    print("WORKFLOW CREATION & EXECUTION")
    print("=" * 70)
    print("\nSelect an option:\n")
    print("  1. Create New Workflow")
    print("  2. List All Workflows")
    print("  3. View Workflow Details")
    print("  4. Execute Workflow")
    print("  5. Export Workflow")
    print("  6. Import Workflow")
    print("  7. Back to main menu\n")
    
    choice = input("Enter your choice (1-7): ").strip()
    
    if choice == '1':
        workflow_builder.create_workflow_interactive()
    elif choice == '2':
        workflow_builder.list_workflows()
    elif choice == '3':
        workflow_id = input("\nEnter workflow ID: ").strip()
        workflow_builder.view_workflow(workflow_id)
    elif choice == '4':
        workflow_id = input("\nEnter workflow ID to execute: ").strip()
        workflow_builder.execute_workflow_interactive(workflow_id)
    elif choice == '5':
        workflow_id = input("\nEnter workflow ID to export: ").strip()
        workflow_builder.export_workflow_interactive(workflow_id)
    elif choice == '6':
        workflow_builder.import_workflow_interactive()
    elif choice == '7':
        return
    else:
        print("\n❌ Invalid choice. Please try again.")


def templates_menu():
    """Workflow templates menu"""
    print("\n" + "=" * 70)
    print("WORKFLOW TEMPLATES")
    print("=" * 70)
    print("\nAvailable templates:\n")
    
    templates = WorkflowTemplates.list_templates()
    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template['name']}")
        print(f"     {template['description']}")
    
    print(f"\n  {len(templates) + 1}. Back to main menu\n")
    
    choice = input(f"Select a template (1-{len(templates) + 1}): ").strip()
    
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(templates):
            template_id = templates[choice_num - 1]['id']
            
            # Create workflow from template
            workflow = WorkflowTemplates.create_from_template(workflow_engine, template_id)
            
            if workflow:
                print(f"\n✅ Workflow '{workflow.name}' created from template!")
                print(f"   ID: {workflow.workflow_id}")
                print(f"   Tasks: {len(workflow.tasks)}")
                
                # Ask to execute
                execute = input("\nExecute this workflow now? (yes/no): ").lower()
                if execute in ['yes', 'y']:
                    print("\n⏳ Executing workflow...")
                    result = workflow_engine.execute_workflow(workflow.workflow_id, verbose=True)
                    
                    if result["success"]:
                        print("\n✅ Workflow completed successfully!")
                    else:
                        print("\n❌ Workflow failed!")
        elif choice_num == len(templates) + 1:
            return
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Please enter a valid number")


def workflow_management_menu():
    """Workflow management menu"""
    print("\n" + "=" * 70)
    print("WORKFLOW MANAGEMENT")
    print("=" * 70)
    print("\nSelect an option:\n")
    print("  1. View All Workflows")
    print("  2. View Workflow Status")
    print("  3. View Execution Report")
    print("  4. Delete Workflow")
    print("  5. Back to main menu\n")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == '1':
        workflow_builder.list_workflows()
    elif choice == '2':
        workflow_id = input("\nEnter workflow ID: ").strip()
        workflow_builder.view_workflow_status(workflow_id)
    elif choice == '3':
        workflow_id = input("\nEnter workflow ID: ").strip()
        workflow_builder.view_execution_report(workflow_id)
    elif choice == '4':
        workflow_id = input("\nEnter workflow ID to delete: ").strip()
        workflow_builder.delete_workflow_interactive(workflow_id)
    elif choice == '5':
        return
    else:
        print("\n❌ Invalid choice. Please try again.")


def scenarios_menu():
    """Pre-built scenarios menu"""
    try:
        from demo_scenario import ScenarioDemo
        
        print("\n" + "=" * 70)
        print("PRE-BUILT SCENARIOS")
        print("=" * 70)
        print("\nSelect a scenario:\n")
        print("  1. Morning Routine")
        print("  2. Financial Planning")
        print("  3. Busy Day Management")
        print("  4. Emergency Response")
        print("  5. Back to main menu\n")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            ScenarioDemo.scenario_morning_routine()
        elif choice == '2':
            ScenarioDemo.scenario_financial_planning()
        elif choice == '3':
            ScenarioDemo.scenario_busy_day()
        elif choice == '4':
            ScenarioDemo.scenario_emergency_response()
        elif choice == '5':
            return
        else:
            print("\n❌ Invalid choice")
    except ImportError:
        print("❌ Error: demo_scenario.py not found")


def main():
    """Main interactive loop"""
    print("\n" + "=" * 70)
    print("     MULTI-AGENT AI FRAMEWORK WITH WORKFLOW ORCHESTRATION")
    print("         Powered by Ollama Qwen2.5:14b")
    print("=" * 70)
    print("\nWelcome! This system demonstrates AI agents and workflows for:")
    print("  • Home automation")
    print("  • Calendar & email management")
    print("  • Financial planning")
    print("  • Complex multi-agent workflows")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            agents_menu()
        elif choice == '2':
            workflow_creation_menu()
        elif choice == '3':
            templates_menu()
        elif choice == '4':
            workflow_management_menu()
        elif choice == '5':
            scenarios_menu()
        elif choice == '6':
            print("\n🎉 Thank you for using the Multi-Agent AI System!")
            print("Goodbye! 👋\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye! 👋\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()