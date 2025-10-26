"""
Advanced Workflow Engine - Conditional branching, logic evaluation, and multi-path workflows
Fixed version with proper task execution
"""

import json
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import re


class TaskStatus(Enum):
    """Status of a workflow task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ConditionOperator(Enum):
    """Operators for condition evaluation"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex_match"
    SUCCESS = "success"
    FAILURE = "failure"


class Condition:
    """Represents a condition for branching"""
    def __init__(self, 
                 field: str, 
                 operator: ConditionOperator, 
                 value: Any = None,
                 task_id: str = None):
        self.field = field
        self.operator = operator
        self.value = value
        self.task_id = task_id
    
    def evaluate(self, context: Dict, task_result: Any = None) -> bool:
        """Evaluate the condition against context and task result"""
        try:
            # Get the actual value to compare
            if self.task_id and f"task_{self.task_id}_result" in context:
                actual_value = context[f"task_{self.task_id}_result"]
            elif self.field in context:
                actual_value = context[self.field]
            elif task_result is not None:
                actual_value = task_result
            else:
                actual_value = None
            
            # Evaluate based on operator
            if self.operator == ConditionOperator.EQUALS:
                return actual_value == self.value
            elif self.operator == ConditionOperator.NOT_EQUALS:
                return actual_value != self.value
            elif self.operator == ConditionOperator.GREATER_THAN:
                return float(actual_value) > float(self.value)
            elif self.operator == ConditionOperator.LESS_THAN:
                return float(actual_value) < float(self.value)
            elif self.operator == ConditionOperator.CONTAINS:
                return self.value in str(actual_value)
            elif self.operator == ConditionOperator.NOT_CONTAINS:
                return self.value not in str(actual_value)
            elif self.operator == ConditionOperator.REGEX_MATCH:
                return bool(re.search(self.value, str(actual_value)))
            elif self.operator == ConditionOperator.SUCCESS:
                return actual_value is not None and "error" not in str(actual_value).lower()
            elif self.operator == ConditionOperator.FAILURE:
                return actual_value is None or "error" in str(actual_value).lower()
            
            return False
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False


class Branch:
    """Represents a conditional branch with multiple tasks"""
    def __init__(self, 
                 branch_id: str,
                 name: str,
                 condition: Condition = None,
                 tasks: List['WorkflowTask'] = None):
        self.branch_id = branch_id
        self.name = name
        self.condition = condition
        self.tasks = tasks or []
        self.executed = False
    
    def add_task(self, task: 'WorkflowTask'):
        """Add a task to this branch"""
        self.tasks.append(task)
    
    def should_execute(self, context: Dict, task_result: Any = None) -> bool:
        """Check if this branch should execute"""
        if self.condition is None:
            return True
        return self.condition.evaluate(context, task_result)


class WorkflowTask:
    """Represents a single task in a workflow with branching support"""
    def __init__(self, 
                 task_id: str, 
                 agent_name: str, 
                 request: str, 
                 retry_count: int = 1, 
                 on_failure: str = "stop",
                 branches: List[Branch] = None,
                 next_task_id: str = None):
        self.task_id = task_id
        self.agent_name = agent_name
        self.request = request
        self.retry_count = retry_count
        self.on_failure = on_failure
        self.branches = branches or []
        self.next_task_id = next_task_id
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        self.start_time = None
        self.end_time = None
    
    def add_branch(self, branch: Branch):
        """Add a conditional branch to this task"""
        self.branches.append(branch)
    
    def get_next_branch(self, context: Dict) -> Optional[Branch]:
        """Determine which branch to take based on conditions"""
        for branch in self.branches:
            if branch.should_execute(context, self.result):
                return branch
        return None
    
    def get_duration(self) -> Optional[float]:
        """Get task execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "request": self.request,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "retry_count": self.retry_count,
            "duration_seconds": self.get_duration(),
            "has_branches": len(self.branches) > 0,
            "num_branches": len(self.branches)
        }


class Workflow:
    """Represents a complete workflow with branching support"""
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.tasks: Dict[str, WorkflowTask] = {}
        self.start_task_id: str = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = "draft"
        self.execution_log = []
        self.context = {}
        self.execution_path = []
    
    def add_task(self, task: WorkflowTask, is_start: bool = False):
        """Add a task to the workflow"""
        self.tasks[task.task_id] = task
        if is_start or self.start_task_id is None:
            self.start_task_id = task.task_id
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def log_event(self, event: str, details: str = ""):
        """Log workflow event"""
        timestamp = datetime.now().isoformat()
        self.execution_log.append({
            "timestamp": timestamp,
            "event": event,
            "details": details
        })
    
    def get_duration(self) -> Optional[float]:
        """Get total workflow duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict:
        """Convert workflow to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "task_count": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            "duration_seconds": self.get_duration(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_path": self.execution_path,
            "tasks": [t.to_dict() for t in self.tasks.values()]
        }


class WorkflowEngine:
    """Executes workflows with branching and conditional logic"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.agents: Dict[str, Any] = {}
        self.history: List[Dict] = []
    
    def register_agent(self, agent_name: str, agent_instance):
        """Register an agent with the engine"""
        self.agents[agent_name] = agent_instance
        return f"Agent '{agent_name}' registered"
    
    def create_workflow(self, workflow_id: str, name: str, description: str = "") -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(workflow_id, name, description)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict]:
        """List all workflows"""
        return [w.to_dict() for w in self.workflows.values()]
    
    def execute_workflow(self, workflow_id: str, verbose: bool = False) -> Dict:
        """Execute a workflow with branching logic - FIXED VERSION"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_id}' not found"}
        
        workflow.status = "running"
        workflow.started_at = datetime.now()
        workflow.log_event("workflow_started", f"Executing workflow: {workflow.name}")
        workflow.execution_path = []
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"Executing Workflow: {workflow.name}")
            print(f"{'=' * 70}")
        
        # Determine starting point
        if workflow.start_task_id and workflow.start_task_id in workflow.tasks:
            current_task_id = workflow.start_task_id
        elif len(workflow.tasks) > 0:
            # Fallback: use first task
            current_task_id = list(workflow.tasks.keys())[0]
        else:
            workflow.status = "failed"
            workflow.completed_at = datetime.now()
            return {"success": False, "error": "No tasks in workflow"}
        
        if verbose:
            print(f"Start Task: {current_task_id}\n")
        
        results = []
        visited = set()  # Prevent infinite loops
        
        while current_task_id and current_task_id not in visited:
            visited.add(current_task_id)
            task = workflow.get_task(current_task_id)
            
            if not task:
                workflow.log_event("error", f"Task {current_task_id} not found")
                break
            
            workflow.execution_path.append(current_task_id)
            
            if verbose:
                print(f"[Task] {task.task_id}")
                print(f"  Agent: {task.agent_name}")
                print(f"  Request: {task.request[:60]}...")
            
            # Execute task
            task_result = self._execute_task(task, workflow, verbose)
            results.append(task_result)
            
            # Store result in context
            workflow.context[f"task_{task.task_id}_result"] = task.result
            workflow.context[f"task_{task.task_id}_status"] = task.status.value
            
            # Check for failure
            if task.status == TaskStatus.FAILED:
                workflow.log_event("task_failed", f"Task {task.task_id} failed")
                if task.on_failure == "stop":
                    workflow.status = "failed"
                    workflow.completed_at = datetime.now()
                    workflow.log_event("workflow_failed", "Workflow stopped due to task failure")
                    if verbose:
                        print(f"  ❌ Task failed. Stopping workflow.\n")
                    break
                else:
                    if verbose:
                        print(f"  ⚠️  Task failed but continuing workflow.\n")
            else:
                if verbose:
                    print(f"  ✅ Task completed\n")
            
            # Determine next task
            next_task_id = None
            
            # Check if task has branches
            if task.branches and len(task.branches) > 0:
                next_branch = task.get_next_branch(workflow.context)
                if next_branch:
                    next_branch.executed = True
                    workflow.log_event("branch_taken", f"Executing branch: {next_branch.name}")
                    
                    if verbose:
                        print(f"  ↳ Taking branch: {next_branch.name}")
                    
                    # Execute all tasks in the branch
                    for branch_task in next_branch.tasks:
                        if branch_task.task_id in visited:
                            continue
                        visited.add(branch_task.task_id)
                        workflow.execution_path.append(branch_task.task_id)
                        
                        if verbose:
                            print(f"    [Branch Task] {branch_task.task_id}")
                        
                        branch_result = self._execute_task(branch_task, workflow, verbose)
                        results.append(branch_result)
                        
                        workflow.context[f"task_{branch_task.task_id}_result"] = branch_task.result
                        workflow.context[f"task_{branch_task.task_id}_status"] = branch_task.status.value
                        
                        if branch_task.status == TaskStatus.FAILED and branch_task.on_failure == "stop":
                            workflow.status = "failed"
                            current_task_id = None
                            break
                    
                    if current_task_id is not None:
                        next_task_id = task.next_task_id
            else:
                # No branches, follow next_task_id
                next_task_id = task.next_task_id
            
            current_task_id = next_task_id
        
        # Mark workflow as completed
        if workflow.status != "failed":
            workflow.status = "completed"
        
        workflow.completed_at = datetime.now()
        workflow.log_event("workflow_completed", f"Workflow completed with status: {workflow.status}")
        
        # Clear agent memory
        for agent in self.agents.values():
            if hasattr(agent, 'clear_memory'):
                agent.clear_memory()
        
        if verbose:
            print(f"{'=' * 70}")
            print(f"Workflow Execution Summary")
            print(f"{'=' * 70}")
            print(f"Status: {workflow.status}")
            print(f"Duration: {workflow.get_duration():.2f} seconds")
            print(f"Tasks Executed: {len(workflow.execution_path)}")
            print(f"Execution Path: {' → '.join(workflow.execution_path)}")
            completed_count = len([t for t in workflow.tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_count = len([t for t in workflow.tasks.values() if t.status == TaskStatus.FAILED])
            print(f"  ✅ Completed: {completed_count}")
            print(f"  ❌ Failed: {failed_count}\n")
        
        return {
            "success": workflow.status == "completed",
            "workflow_id": workflow_id,
            "status": workflow.status,
            "duration_seconds": workflow.get_duration(),
            "execution_path": workflow.execution_path,
            "results": results
        }
    
    def _execute_task(self, task: WorkflowTask, workflow: Workflow, verbose: bool = False) -> Dict:
        """Execute a single task with retry logic"""
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        agent = self.agents.get(task.agent_name)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent '{task.agent_name}' not found"
            task.end_time = datetime.now()
            return task.to_dict()
        
        # Execute task with retry
        for attempt in range(1, task.retry_count + 1):
            task.attempts = attempt
            try:
                result = agent.think_and_act(task.request, verbose=False)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now()
                workflow.log_event("task_completed", f"Task {task.task_id} completed successfully")
                return task.to_dict()
            except Exception as e:
                task.error = str(e)
                if attempt < task.retry_count:
                    if verbose:
                        print(f"    Attempt {attempt} failed, retrying...")
                    workflow.log_event("task_retry", f"Task {task.task_id} retry attempt {attempt}")
                else:
                    task.status = TaskStatus.FAILED
                    task.end_time = datetime.now()
                    workflow.log_event("task_failed", f"Task {task.task_id} failed after {attempt} attempts")
        
        return task.to_dict()
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get current status of a workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": f"Workflow '{workflow_id}' not found"}
        
        completed = len([t for t in workflow.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in workflow.tasks.values() if t.status == TaskStatus.FAILED])
        pending = len([t for t in workflow.tasks.values() if t.status == TaskStatus.PENDING])
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "total_tasks": len(workflow.tasks),
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "execution_path": workflow.execution_path,
            "progress_percent": (completed / len(workflow.tasks) * 100) if workflow.tasks else 0
        }
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict]:
        """Get execution history for a workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return []
        return workflow.execution_log
    
    def export_workflow(self, workflow_id: str) -> str:
        """Export workflow as JSON"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return json.dumps({"error": f"Workflow '{workflow_id}' not found"})
        return json.dumps(workflow.to_dict(), indent=2)
    
    def import_workflow(self, workflow_json: str) -> Optional[Workflow]:
        """Import workflow from JSON"""
        try:
            data = json.loads(workflow_json)
            workflow = self.create_workflow(
                data["workflow_id"],
                data["name"],
                data.get("description", "")
            )
            
            for task_data in data.get("tasks", []):
                task = WorkflowTask(
                    task_data["task_id"],
                    task_data["agent_name"],
                    task_data["request"],
                    task_data.get("retry_count", 1),
                    task_data.get("on_failure", "stop")
                )
                workflow.add_task(task)
            
            return workflow
        except Exception as e:
            print(f"Error importing workflow: {e}")
            return None
    
    def get_execution_report(self, workflow_id: str) -> Dict:
        """Get detailed execution report"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": f"Workflow '{workflow_id}' not found"}
        
        task_reports = []
        total_duration = 0
        
        for task in workflow.tasks.values():
            duration = task.get_duration() or 0
            total_duration += duration
            task_reports.append({
                "task_id": task.task_id,
                "agent": task.agent_name,
                "status": task.status.value,
                "duration_seconds": duration,
                "attempts": task.attempts,
                "has_branches": len(task.branches) > 0,
                "result_preview": str(task.result)[:100] if task.result else None,
                "error": task.error
            })
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "overall_status": workflow.status,
            "total_duration_seconds": total_duration,
            "execution_path": workflow.execution_path,
            "tasks": task_reports,
            "success_rate": len([t for t in workflow.tasks.values() if t.status == TaskStatus.COMPLETED]) / len(workflow.tasks) * 100 if workflow.tasks else 0
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()


if __name__ == "__main__":
    print("=" * 70)
    print("ADVANCED WORKFLOW ENGINE - FIXED VERSION")
    print("=" * 70)
    
    from home_agent import home_agent
    from calendar_agent import calendar_agent
    from finance_agent import finance_agent
    
    workflow_engine.register_agent("home", home_agent)
    workflow_engine.register_agent("calendar", calendar_agent)
    workflow_engine.register_agent("finance", finance_agent)
    
    # Create simple sequential workflow
    workflow = workflow_engine.create_workflow(
        "test_workflow",
        "Test Sequential Workflow",
        "Testing fixed execution"
    )
    
    # Create linked tasks
    task1 = WorkflowTask("task1", "home", "Turn on living room lights")
    task2 = WorkflowTask("task2", "home", "Set temperature to 72 degrees")
    task3 = WorkflowTask("task3", "calendar", "What's on my calendar today?")
    
    # Link them
    task1.next_task_id = "task2"
    task2.next_task_id = "task3"
    
    # Add to workflow
    workflow.add_task(task1, is_start=True)
    workflow.add_task(task2)
    workflow.add_task(task3)
    
    # Execute
    print("\n")
    result = workflow_engine.execute_workflow("test_workflow", verbose=True)
    
    print("\nEXECUTION REPORT:")
    print("=" * 70)
    report = workflow_engine.get_execution_report("test_workflow")
    print(json.dumps(report, indent=2))