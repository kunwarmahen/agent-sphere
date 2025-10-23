"""
Interactive Workflow Builder - Create workflows through an intuitive CLI interface
"""

import json
from workflow_engine import WorkflowEngine, WorkflowTask, Workflow
from typing import Optional, List


class WorkflowBuilder:
    """Interactive workflow creation and management"""
    
    def __init__(self, engine: WorkflowEngine):
        self.engine = engine
        self.current_workflow: Optional[Workflow] = None
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def print_menu(self, options: List[tuple]):
        """Print formatted menu"""
        for key, label in options:
            print(f"  {key}. {label}")
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation"""
        while True:
            value = input(f"\n{prompt}: ").strip()
            if value or not required:
                return value
            print("This field is required. Please try again.")
    
    def create_workflow_interactive(self):
        """Interactive workflow creation"""
        self.print_header("CREATE NEW WORKFLOW")
        
        workflow_id = self.get_input("Enter workflow ID (e.g., 'morning_routine')")
        
        # Check if ID already exists
        if self.engine.get_workflow(workflow_id):
            print(f"⚠️  Workflow '{workflow_id}' already exists!")
            return
        
        name = self.get_input("Enter workflow name (e.g., 'Morning Routine')")
        description = self.get_input("Enter description (optional)", required=False)
        
        # Create workflow
        workflow = self.engine.create_workflow(workflow_id, name, description)
        self.current_workflow = workflow
        
        print(f"\n✅ Workflow '{name}' created!")
        print(f"   ID: {workflow_id}")
        
        # Add tasks
        self.add_tasks_interactive(workflow)
    
    def add_tasks_interactive(self, workflow: Workflow):
        """Interactive task addition"""
        self.print_header("ADD TASKS TO WORKFLOW")
        print("\nAvailable agents:")
        print("  • home - Home Automation (JARVIS)")
        print("  • calendar - Calendar & Email (Assistant)")
        print("  • finance - Financial Planning (FinanceBot)")
        
        task_count = 0
        
        while True:
            print(f"\n--- Task {task_count + 1} ---")
            
            agent_name = self.get_input(
                "Enter agent name (home/calendar/finance) or 'done' to finish"
            ).lower()
            
            if agent_name == 'done':
                break
            
            if agent_name not in ['home', 'calendar', 'finance']:
                print("❌ Invalid agent. Please use: home, calendar, or finance")
                continue
            
            task_id = self.get_input(f"Enter task ID (e.g., 'task_{task_count + 1}')")
            request = self.get_input("Enter the request for this agent")
            
            retry_count_str = self.get_input(
                "Enter retry count if task fails (default: 1)", 
                required=False
            )
            retry_count = int(retry_count_str) if retry_count_str else 1
            
            on_failure = self.get_input(
                "On failure: 'stop' to halt workflow or 'continue' (default: stop)",
                required=False
            ).lower() or "stop"
            
            if on_failure not in ['stop', 'continue']:
                on_failure = "stop"
            
            # Add task
            task = WorkflowTask(task_id, agent_name, request, retry_count, on_failure)
            workflow.add_task(task)
            task_count += 1
            
            print(f"✅ Task '{task_id}' added!")
        
        if task_count > 0:
            print(f"\n✅ Workflow ready! {task_count} tasks added.")
            self.current_workflow = workflow
        else:
            print("\n⚠️  No tasks added to workflow.")
    
    def view_workflow(self, workflow_id: str = None):
        """View workflow details"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        workflow = self.engine.get_workflow(workflow_id)
        
        if not workflow:
            print(f"❌ Workflow '{workflow_id}' not found")
            return
        
        self.print_header(f"WORKFLOW: {workflow.name}")
        print(f"\nID: {workflow.workflow_id}")
        print(f"Description: {workflow.description}")
        print(f"Status: {workflow.status}")
        print(f"Created: {workflow.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTasks ({len(workflow.tasks)} total):")
        
        for i, task in enumerate(workflow.tasks, 1):
            print(f"\n  {i}. [{task.status.value.upper()}] {task.task_id}")
            print(f"     Agent: {task.agent_name}")
            print(f"     Request: {task.request[:60]}..." if len(task.request) > 60 else f"     Request: {task.request}")
            print(f"     Retry: {task.retry_count}, On Failure: {task.on_failure}")
            if task.result:
                print(f"     Result: {str(task.result)[:60]}...")
    
    def list_workflows(self):
        """List all workflows"""
        self.print_header("ALL WORKFLOWS")
        
        workflows = self.engine.list_workflows()
        
        if not workflows:
            print("\n📭 No workflows created yet")
            return
        
        for i, w in enumerate(workflows, 1):
            status_emoji = "✅" if w["status"] == "completed" else "❌" if w["status"] == "failed" else "⏳"
            print(f"\n{i}. {status_emoji} {w['name']} ({w['workflow_id']})")
            print(f"   Status: {w['status']}")
            print(f"   Tasks: {w['task_count']} total, {w['completed_tasks']} completed, {w['failed_tasks']} failed")
            if w['duration_seconds']:
                print(f"   Duration: {w['duration_seconds']:.2f}s")
    
    def execute_workflow_interactive(self, workflow_id: str = None):
        """Execute workflow with confirmation"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        workflow = self.engine.get_workflow(workflow_id)
        
        if not workflow:
            print(f"❌ Workflow '{workflow_id}' not found")
            return
        
        self.print_header(f"EXECUTE WORKFLOW: {workflow.name}")
        print(f"\n📋 Workflow Details:")
        print(f"   Tasks: {len(workflow.tasks)}")
        for task in workflow.tasks:
            print(f"   • {task.task_id} ({task.agent_name}): {task.request[:50]}...")
        
        confirm = input("\n\nProceed with execution? (yes/no): ").lower()
        
        if confirm in ['yes', 'y']:
            print("\n⏳ Executing workflow...")
            result = self.engine.execute_workflow(workflow_id, verbose=True)
            
            if result["success"]:
                print("\n✅ Workflow completed successfully!")
            else:
                print("\n❌ Workflow failed!")
            
            return result
        else:
            print("\n⏹️  Execution cancelled")
            return None
    
    def view_workflow_status(self, workflow_id: str = None):
        """View current workflow status"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        status = self.engine.get_workflow_status(workflow_id)
        
        if "error" in status:
            print(f"❌ {status['error']}")
            return
        
        self.print_header(f"WORKFLOW STATUS: {status['name']}")
        print(f"\nStatus: {status['status']}")
        print(f"Progress: {status['progress_percent']:.1f}%")
        print(f"\nTasks:")
        print(f"  ✅ Completed: {status['completed']}/{status['total_tasks']}")
        print(f"  ❌ Failed: {status['failed']}/{status['total_tasks']}")
        print(f"  ⏳ Pending: {status['pending']}/{status['total_tasks']}")
    
    def view_execution_report(self, workflow_id: str = None):
        """View detailed execution report"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        report = self.engine.get_execution_report(workflow_id)
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        self.print_header(f"EXECUTION REPORT: {report['name']}")
        print(f"\nOverall Status: {report['overall_status']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        print(f"Total Duration: {report['total_duration_seconds']:.2f}s")
        
        print(f"\nTask Details:")
        for task in report['tasks']:
            status_icon = "✅" if task['status'] == "completed" else "❌" if task['status'] == "failed" else "⏳"
            print(f"\n  {status_icon} {task['task_id']}")
            print(f"     Agent: {task['agent']}")
            print(f"     Status: {task['status']}")
            print(f"     Duration: {task['duration_seconds']:.2f}s")
            print(f"     Attempts: {task['attempts']}/{task.get('retry_count', 1)}")
            if task['result_preview']:
                print(f"     Result: {task['result_preview']}...")
            if task['error']:
                print(f"     Error: {task['error']}")
    
    def export_workflow_interactive(self, workflow_id: str = None):
        """Export workflow to JSON file"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        
        try:
            json_str = self.engine.export_workflow(workflow_id)
            
            filename = f"workflow_{workflow_id}.json"
            with open(filename, 'w') as f:
                f.write(json_str)
            
            print(f"✅ Workflow exported to '{filename}'")
            return filename
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def import_workflow_interactive(self):
        """Import workflow from JSON file"""
        self.print_header("IMPORT WORKFLOW")
        
        filename = self.get_input("Enter JSON filename (e.g., 'workflow_morning.json')")
        
        try:
            with open(filename, 'r') as f:
                json_str = f.read()
            
            workflow = self.engine.import_workflow(json_str)
            if workflow:
                self.current_workflow = workflow
                print(f"✅ Workflow '{workflow.name}' imported successfully!")
            else:
                print("❌ Failed to import workflow")
        except FileNotFoundError:
            print(f"❌ File '{filename}' not found")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def delete_workflow_interactive(self, workflow_id: str = None):
        """Delete a workflow"""
        if not workflow_id and not self.current_workflow:
            print("❌ No workflow selected")
            return
        
        workflow_id = workflow_id or self.current_workflow.workflow_id
        workflow = self.engine.get_workflow(workflow_id)
        
        if not workflow:
            print(f"❌ Workflow '{workflow_id}' not found")
            return
        
        confirm = input(f"\nAre you sure you want to delete '{workflow.name}'? (yes/no): ").lower()
        
        if confirm in ['yes', 'y']:
            del self.engine.workflows[workflow_id]
            if self.current_workflow and self.current_workflow.workflow_id == workflow_id:
                self.current_workflow = None
            print("✅ Workflow deleted")
        else:
            print("⏹️  Deletion cancelled")
    
    def interactive_menu(self):
        """Main interactive menu loop"""
        print("\n" + "=" * 70)
        print("         WORKFLOW BUILDER - Interactive Workflow Creation")
        print("=" * 70)
        
        while True:
            print(f"\n{'─' * 70}")
            if self.current_workflow:
                print(f"Current Workflow: {self.current_workflow.name} ({self.current_workflow.workflow_id})")
            else:
                print("No workflow selected")
            print(f"{'─' * 70}\n")
            
            print("Main Menu:")
            self.print_menu([
                ('1', 'Create New Workflow'),
                ('2', 'Select Existing Workflow'),
                ('3', 'View Current Workflow'),
                ('4', 'Add Tasks to Current Workflow'),
                ('5', 'Execute Workflow'),
                ('6', 'View Workflow Status'),
                ('7', 'View Execution Report'),
                ('8', 'List All Workflows'),
                ('9', 'Export Workflow'),
                ('10', 'Import Workflow'),
                ('11', 'Delete Workflow'),
                ('12', 'Exit'),
            ])
            
            choice = input("\nSelect option (1-12): ").strip()
            
            if choice == '1':
                self.create_workflow_interactive()
            elif choice == '2':
                self.list_workflows()
                workflow_id = input("\nEnter workflow ID to select: ").strip()
                workflow = self.engine.get_workflow(workflow_id)
                if workflow:
                    self.current_workflow = workflow
                    print(f"✅ Workflow '{workflow.name}' selected")
                else:
                    print("❌ Workflow not found")
            elif choice == '3':
                self.view_workflow()
            elif choice == '4':
                if self.current_workflow:
                    self.add_tasks_interactive(self.current_workflow)
                else:
                    print("❌ No workflow selected. Create or select one first.")
            elif choice == '5':
                self.execute_workflow_interactive()
            elif choice == '6':
                self.view_workflow_status()
            elif choice == '7':
                self.view_execution_report()
            elif choice == '8':
                self.list_workflows()
            elif choice == '9':
                self.export_workflow_interactive()
            elif choice == '10':
                self.import_workflow_interactive()
            elif choice == '11':
                self.delete_workflow_interactive()
            elif choice == '12':
                print("\nGoodbye! 👋\n")
                break
            else:
                print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    # Initialize workflow engine
    from home_agent import home_agent
    from calendar_agent import calendar_agent
    from finance_agent import finance_agent
    
    engine = WorkflowEngine()
    engine.register_agent("home", home_agent)
    engine.register_agent("calendar", calendar_agent)
    engine.register_agent("finance", finance_agent)
    
    # Create and run builder
    builder = WorkflowBuilder(engine)
    
    try:
        builder.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye! 👋\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()