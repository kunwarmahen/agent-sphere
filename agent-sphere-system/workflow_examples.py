"""
Workflow Examples - Practical examples of creating and executing workflows
Shows various patterns and use cases for the workflow system
"""

from workflow_engine import WorkflowEngine, WorkflowTask
from workflow_templates import WorkflowTemplates
from home_agent import home_agent
from calendar_agent import calendar_agent
from finance_agent import finance_agent


# Setup engine once
def setup_engine():
    """Initialize workflow engine with agents"""
    engine = WorkflowEngine()
    engine.register_agent("home", home_agent)
    engine.register_agent("calendar", calendar_agent)
    engine.register_agent("finance", finance_agent)
    return engine


# ============================================================================
# EXAMPLE 1: Simple Single-Task Workflow
# ============================================================================

def example_1_simple_workflow():
    """Most basic workflow - single task"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Single-Task Workflow")
    print("=" * 70)
    
    engine = setup_engine()
    
    # Create workflow with one task
    workflow = engine.create_workflow(
        "simple_lights",
        "Turn On Lights",
        "Simple workflow to turn on lights"
    )
    
    # Add single task
    task = WorkflowTask(
        task_id="turn_on_lights",
        agent_name="home",
        request="Turn on all the lights in my house"
    )
    workflow.add_task(task)
    
    # Execute
    print("\nExecuting simple workflow...")
    result = engine.execute_workflow("simple_lights", verbose=False)
    
    print(f"\nResult: {result['success']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")


# ============================================================================
# EXAMPLE 2: Multi-Task Workflow (Same Agent)
# ============================================================================

def example_2_multi_task_workflow():
    """Multiple tasks with the same agent"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Task Workflow (Same Agent)")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "home_setup",
        "Complete Home Setup",
        "Multiple home automation tasks"
    )
    
    # Add multiple tasks for same agent
    tasks = [
        WorkflowTask("t1", "home", "Turn on all lights"),
        WorkflowTask("t2", "home", "Set temperature to 72 degrees"),
        WorkflowTask("t3", "home", "Lock the doors"),
        WorkflowTask("t4", "home", "Turn on the coffee maker"),
    ]
    
    workflow.add_tasks(tasks)
    
    print(f"\nWorkflow: {workflow.name}")
    print(f"Tasks: {len(workflow.tasks)}")
    
    result = engine.execute_workflow("home_setup", verbose=True)
    
    print(f"\nCompleted: {len([t for t in workflow.tasks if t.status.value == 'completed'])}/{len(workflow.tasks)}")


# ============================================================================
# EXAMPLE 3: Multi-Agent Workflow
# ============================================================================

def example_3_multi_agent_workflow():
    """Tasks executed by different agents"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multi-Agent Workflow")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "morning_comprehensive",
        "Comprehensive Morning",
        "Home + Calendar + Finance"
    )
    
    # Mix of agents
    tasks = [
        WorkflowTask("home1", "home", "Good morning! Turn on all lights and set temperature to 72"),
        WorkflowTask("home2", "home", "Start the coffee maker"),
        WorkflowTask("cal1", "calendar", "What meetings do I have today?"),
        WorkflowTask("cal2", "calendar", "Show me unread emails"),
        WorkflowTask("fin1", "finance", "What's my financial summary?"),
    ]
    
    workflow.add_tasks(tasks)
    
    print(f"\nWorkflow: {workflow.name}")
    print(f"Tasks across {len(set(t.agent_name for t in workflow.tasks))} agents")
    
    result = engine.execute_workflow("morning_comprehensive", verbose=True)


# ============================================================================
# EXAMPLE 4: Workflow with Retry Logic
# ============================================================================

def example_4_retry_logic():
    """Tasks with retry logic for resilience"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Workflow with Retry Logic")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "resilient_workflow",
        "Resilient Workflow",
        "Tasks with retry capability"
    )
    
    # Tasks with different retry strategies
    tasks = [
        WorkflowTask(
            "critical_task",
            "home",
            "Turn on lights",
            retry_count=3,  # Retry 3 times
            on_failure="stop"  # Stop if all retries fail
        ),
        WorkflowTask(
            "regular_task",
            "calendar",
            "Show my schedule",
            retry_count=2,
            on_failure="continue"  # Continue even if fails
        ),
    ]
    
    workflow.add_tasks(tasks)
    
    print("\nTasks with retry logic:")
    for task in workflow.tasks:
        print(f"  {task.task_id}: retry={task.retry_count}, on_failure={task.on_failure}")
    
    result = engine.execute_workflow("resilient_workflow", verbose=False)


# ============================================================================
# EXAMPLE 5: Workflow with Failure Handling
# ============================================================================

def example_5_failure_handling():
    """Different failure strategies"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Workflow with Failure Handling")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "robust_workflow",
        "Robust Workflow",
        "Demonstrates failure handling"
    )
    
    tasks = [
        WorkflowTask(
            "important_1",
            "finance",
            "Show account balances",
            on_failure="stop"  # Critical - stop if fails
        ),
        WorkflowTask(
            "optional_1",
            "home",
            "Turn on TV",
            on_failure="continue"  # Optional - continue if fails
        ),
        WorkflowTask(
            "important_2",
            "calendar",
            "Show calendar",
            on_failure="stop"  # Critical - stop if fails
        ),
    ]
    
    workflow.add_tasks(tasks)
    
    print("\nFailure Strategy:")
    print("  Critical tasks (finance, calendar): STOP on failure")
    print("  Optional tasks (home devices): CONTINUE on failure")
    
    result = engine.execute_workflow("robust_workflow", verbose=False)
    
    if result["success"]:
        print("\n✅ Workflow completed successfully")
    else:
        print("\n❌ Workflow failed or stopped")


# ============================================================================
# EXAMPLE 6: Complex Real-World Workflow
# ============================================================================

def example_6_complex_workflow():
    """Complex workflow for a complete scenario"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complex Real-World Workflow - Vacation Preparation")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "vacation_prep_complex",
        "Vacation Preparation",
        "Complete workflow to prepare for vacation"
    )
    
    tasks = [
        # Phase 1: Secure home
        WorkflowTask(
            "phase1_secure",
            "home",
            "Lock all doors and garage for vacation",
            on_failure="stop"  # Critical
        ),
        WorkflowTask(
            "phase1_devices",
            "home",
            "Turn off TV and all smart devices",
            on_failure="continue"
        ),
        WorkflowTask(
            "phase1_temp",
            "home",
            "Set thermostat to 65 degrees to save energy",
            on_failure="continue"
        ),
        
        # Phase 2: Schedule review
        WorkflowTask(
            "phase2_vacation_dates",
            "calendar",
            "Show my vacation period and dates",
            on_failure="stop"
        ),
        WorkflowTask(
            "phase2_important_dates",
            "calendar",
            "Show any important dates I'll miss",
            on_failure="continue"
        ),
        
        # Phase 3: Financial preparation
        WorkflowTask(
            "phase3_vacation_fund",
            "finance",
            "How much have I saved in my vacation fund?",
            on_failure="continue"
        ),
        WorkflowTask(
            "phase3_budget_check",
            "finance",
            "Am I within budget for vacation spending?",
            on_failure="continue"
        ),
    ]
    
    workflow.add_tasks(tasks)
    
    print(f"\nWorkflow Phases:")
    print(f"  Phase 1: Home Security (3 tasks)")
    print(f"  Phase 2: Schedule Review (2 tasks)")
    print(f"  Phase 3: Financial Check (2 tasks)")
    print(f"  Total: {len(workflow.tasks)} tasks")
    
    result = engine.execute_workflow("vacation_prep_complex", verbose=True)
    
    # Get report
    report = engine.get_execution_report("vacation_prep_complex")
    print(f"\n📊 Execution Report:")
    print(f"   Success Rate: {report['success_rate']:.1f}%")
    print(f"   Total Duration: {report['total_duration_seconds']:.2f}s")


# ============================================================================
# EXAMPLE 7: Sequential Workflow with Dependencies
# ============================================================================

def example_7_sequential_workflow():
    """Workflow where order matters"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Sequential Workflow with Dependencies")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "sequential_workflow",
        "Sequential Workflow",
        "Tasks depend on previous execution"
    )
    
    tasks = [
        # Step 1: Get schedule
        WorkflowTask(
            "step1_get_schedule",
            "calendar",
            "What are my meetings today?"
        ),
        
        # Step 2: Prepare environment based on schedule
        WorkflowTask(
            "step2_prepare_office",
            "home",
            "Prepare office - full brightness, comfortable temperature"
        ),
        
        # Step 3: Review financial impact
        WorkflowTask(
            "step3_check_meeting_budget",
            "finance",
            "Do I have budget for any meeting expenses?"
        ),
        
        # Step 4: Get emails about meetings
        WorkflowTask(
            "step4_meeting_emails",
            "calendar",
            "Show me emails related to today's meetings"
        ),
    ]
    
    workflow.add_tasks(tasks)
    
    print("\nExecution Order:")
    for i, task in enumerate(workflow.tasks, 1):
        print(f"  {i}. {task.task_id} ({task.agent_name})")
    
    result = engine.execute_workflow("sequential_workflow", verbose=False)


# ============================================================================
# EXAMPLE 8: Using Pre-built Templates
# ============================================================================

def example_8_use_templates():
    """How to use pre-built templates"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Using Pre-built Templates")
    print("=" * 70)
    
    engine = setup_engine()
    
    # Show available templates
    templates = WorkflowTemplates.list_templates()
    print(f"\nAvailable Templates: {len(templates)}\n")
    
    for i, template in enumerate(templates[:3], 1):  # Show first 3
        print(f"{i}. {template['name']}")
        print(f"   {template['description']}")
        print(f"   Tasks: {template['tasks']}\n")
    
    # Create from template
    print("Creating 'Morning Routine' from template...\n")
    workflow = WorkflowTemplates.create_from_template(engine, "morning_routine")
    
    if workflow:
        print(f"✅ Workflow created: {workflow.name}")
        print(f"   ID: {workflow.workflow_id}")
        print(f"   Tasks: {len(workflow.tasks)}")
        
        print("\n   Tasks:")
        for task in workflow.tasks:
            print(f"   • {task.task_id}: {task.request[:50]}...")


# ============================================================================
# EXAMPLE 9: Workflow with Context Sharing
# ============================================================================

def example_9_workflow_context():
    """Using workflow context to share data"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Workflow Context")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "context_workflow",
        "Workflow with Shared Context",
        "Demonstrates workflow context"
    )
    
    # Set context
    workflow.context["user_name"] = "John"
    workflow.context["budget_limit"] = 500
    workflow.context["priority"] = "high"
    
    print("\nWorkflow Context:")
    for key, value in workflow.context.items():
        print(f"  {key}: {value}")
    
    tasks = [
        WorkflowTask("t1", "home", "Set up my home office"),
        WorkflowTask("t2", "calendar", "Show today's high priority meetings"),
        WorkflowTask("t3", "finance", "Show spending within budget limit"),
    ]
    
    workflow.add_tasks(tasks)
    
    result = engine.execute_workflow("context_workflow", verbose=False)
    
    print(f"\nContext remains available throughout workflow execution")


# ============================================================================
# EXAMPLE 10: Export and Import Workflows
# ============================================================================

def example_10_export_import():
    """Save and load workflows"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Export and Import Workflows")
    print("=" * 70)
    
    engine = setup_engine()
    
    # Create workflow
    workflow = engine.create_workflow(
        "reusable_workflow",
        "Reusable Workflow",
        "Workflow that can be saved and reused"
    )
    
    tasks = [
        WorkflowTask("t1", "home", "Turn on lights"),
        WorkflowTask("t2", "calendar", "Show schedule"),
        WorkflowTask("t3", "finance", "Check balance"),
    ]
    
    workflow.add_tasks(tasks)
    
    # Export to JSON
    print("\n1. Exporting workflow to JSON...")
    json_str = engine.export_workflow("reusable_workflow")
    
    with open("workflow_reusable.json", "w") as f:
        f.write(json_str)
    
    print("   ✅ Exported to: workflow_reusable.json")
    
    # Show JSON preview
    import json
    data = json.loads(json_str)
    print(f"\n2. Workflow JSON Structure:")
    print(f"   ID: {data['workflow_id']}")
    print(f"   Name: {data['name']}")
    print(f"   Tasks: {data['task_count']}")
    
    # Import from JSON
    print(f"\n3. Importing workflow from JSON...")
    with open("workflow_reusable.json", "r") as f:
        imported_json = f.read()
    
    imported_workflow = engine.import_workflow(imported_json)
    
    if imported_workflow:
        print(f"   ✅ Imported: {imported_workflow.name}")
        print(f"   Tasks: {len(imported_workflow.tasks)}")


# ============================================================================
# EXAMPLE 11: Performance Analysis
# ============================================================================

def example_11_performance_analysis():
    """Analyze workflow performance"""
    print("\n" + "=" * 70)
    print("EXAMPLE 11: Performance Analysis")
    print("=" * 70)
    
    engine = setup_engine()
    
    workflow = engine.create_workflow(
        "performance_workflow",
        "Performance Test",
        "Workflow for performance analysis"
    )
    
    tasks = [
        WorkflowTask("task_1", "home", "Turn on lights"),
        WorkflowTask("task_2", "calendar", "Show schedule"),
        WorkflowTask("task_3", "finance", "Check balance"),
        WorkflowTask("task_4", "home", "Set temperature"),
        WorkflowTask("task_5", "calendar", "Check emails"),
    ]
    
    workflow.add_tasks(tasks)
    
    print(f"\nExecuting {len(workflow.tasks)} tasks...")
    result = engine.execute_workflow("performance_workflow", verbose=False)
    
    # Get detailed report
    report = engine.get_execution_report("performance_workflow")
    
    print(f"\n📊 Performance Report:")
    print(f"   Total Duration: {report['total_duration_seconds']:.2f}s")
    print(f"   Success Rate: {report['success_rate']:.1f}%")
    print(f"   Average Task Duration: {report['total_duration_seconds'] / len(report['tasks']):.2f}s")
    
    print(f"\n   Per-Task Analysis:")
    for task in report['tasks']:
        print(f"   • {task['task_id']}: {task['duration_seconds']:.2f}s ({task['status']})")


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Run examples"""
    print("\n" + "=" * 70)
    print("              WORKFLOW EXAMPLES & USE CASES")
    print("=" * 70)
    
    examples = [
        ("Simple Single-Task Workflow", example_1_simple_workflow),
        ("Multi-Task Workflow (Same Agent)", example_2_multi_task_workflow),
        ("Multi-Agent Workflow", example_3_multi_agent_workflow),
        ("Workflow with Retry Logic", example_4_retry_logic),
        ("Workflow with Failure Handling", example_5_failure_handling),
        ("Complex Real-World Workflow", example_6_complex_workflow),
        ("Sequential Workflow", example_7_sequential_workflow),
        ("Using Pre-built Templates", example_8_use_templates),
        ("Workflow Context", example_9_workflow_context),
        ("Export and Import Workflows", example_10_export_import),
        ("Performance Analysis", example_11_performance_analysis),
    ]
    
    while True:
        print("\nSelect an example:\n")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print(f"  {len(examples) + 1}. Run All Examples")
        print(f"  {len(examples) + 2}. Exit\n")
        
        choice = input("Enter choice: ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(examples) + 1:
                for name, func in examples:
                    try:
                        func()
                        input("\n[Press Enter to continue...]")
                    except Exception as e:
                        print(f"❌ Error: {e}")
            elif 1 <= choice_num <= len(examples):
                try:
                    examples[choice_num - 1][1]()
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
            elif choice_num == len(examples) + 2:
                print("\nGoodbye!")
                break
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()