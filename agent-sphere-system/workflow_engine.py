"""
Workflow Engine - Create, manage, and execute multi-agent workflows
Allows users to define complex workflows that orchestrate multiple agents
"""

import json
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Status of a workflow task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowTask:
    """Represents a single task in a workflow"""
    def __init__(self, task_id: str, agent_name: str, request: str, 
                 retry_count: int = 1, on_failure: str = "stop"):
        self.task_id = task_id
        self.agent_name = agent_name
        self.request = request
        self.retry_count = retry_count
        self.on_failure = on_failure  # "stop" or "continue"
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        self.start_time = None
        self.end_time = None
    
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
            "duration_seconds": self.get_duration()
        }


class Workflow:
    """Represents a complete workflow"""
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.tasks: List[WorkflowTask] = []
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = "draft"  # draft, running, completed, failed
        self.execution_log = []
        self.context = {}  # Shared data between tasks
    
    def add_task(self, task: WorkflowTask):
        """Add a task to the workflow"""
        self.tasks.append(task)
    
    def add_tasks(self, tasks: List[WorkflowTask]):
        """Add multiple tasks to the workflow"""
        self.tasks.extend(tasks)
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
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
            "completed_tasks": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks if t.status == TaskStatus.FAILED]),
            "duration_seconds": self.get_duration(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tasks": [t.to_dict() for t in self.tasks]
        }


class WorkflowEngine:
    """Executes workflows with multiple agents"""
    
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
        """Execute a workflow and return results"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": f"Workflow '{workflow_id}' not found"}
        
        workflow.status = "running"
        workflow.started_at = datetime.now()
        workflow.log_event("workflow_started", f"Executing workflow: {workflow.name}")
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"Executing Workflow: {workflow.name}")
            print(f"{'=' * 70}")
            print(f"Total tasks: {len(workflow.tasks)}\n")
        
        results = []
        
        for i, task in enumerate(workflow.tasks, 1):
            if verbose:
                print(f"[Task {i}/{len(workflow.tasks)}] {task.task_id}")
                print(f"  Agent: {task.agent_name}")
                print(f"  Request: {task.request[:60]}...")
            
            # Execute task
            task_result = self._execute_task(task, workflow, verbose)
            results.append(task_result)
            
            # Check for failure and on_failure action
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
            print(f"Tasks: {len(workflow.tasks)} total")
            print(f"  ✅ Completed: {len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED])}")
            print(f"  ❌ Failed: {len([t for t in workflow.tasks if t.status == TaskStatus.FAILED])}")
            print(f"  ⏭️  Skipped: {len([t for t in workflow.tasks if t.status == TaskStatus.SKIPPED])}\n")
        
        return {
            "success": workflow.status == "completed",
            "workflow_id": workflow_id,
            "status": workflow.status,
            "duration_seconds": workflow.get_duration(),
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
        
        completed = len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in workflow.tasks if t.status == TaskStatus.FAILED])
        pending = len([t for t in workflow.tasks if t.status == TaskStatus.PENDING])
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "total_tasks": len(workflow.tasks),
            "completed": completed,
            "failed": failed,
            "pending": pending,
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
        
        for task in workflow.tasks:
            duration = task.get_duration() or 0
            total_duration += duration
            task_reports.append({
                "task_id": task.task_id,
                "agent": task.agent_name,
                "status": task.status.value,
                "duration_seconds": duration,
                "attempts": task.attempts,
                "result_preview": str(task.result)[:100] if task.result else None,
                "error": task.error
            })
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "overall_status": workflow.status,
            "total_duration_seconds": total_duration,
            "tasks": task_reports,
            "success_rate": len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED]) / len(workflow.tasks) * 100 if workflow.tasks else 0
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()


if __name__ == "__main__":
    # Demo workflow execution
    print("=" * 70)
    print("WORKFLOW ENGINE DEMO")
    print("=" * 70)
    
    # Register agents
    from home_agent import home_agent
    from calendar_agent import calendar_agent
    from finance_agent import finance_agent
    
    workflow_engine.register_agent("home", home_agent)
    workflow_engine.register_agent("calendar", calendar_agent)
    workflow_engine.register_agent("finance", finance_agent)
    
    # Create a sample workflow
    workflow = workflow_engine.create_workflow(
        "morning_setup",
        "Morning Setup Workflow",
        "Complete morning routine automation"
    )
    
    # Add tasks
    workflow.add_tasks([
        WorkflowTask("task_1", "home", "Turn on all lights and set temperature to 72"),
        WorkflowTask("task_2", "home", "Start the coffee maker"),
        WorkflowTask("task_3", "calendar", "Show me my calendar for today"),
        WorkflowTask("task_4", "calendar", "Check unread emails"),
        WorkflowTask("task_5", "finance", "Show my financial summary"),
    ])
    
    # Execute workflow
    result = workflow_engine.execute_workflow("morning_setup", verbose=True)
    
    # Get execution report
    print("\nEXECUTION REPORT:")
    print("=" * 70)
    report = workflow_engine.get_execution_report("morning_setup")
    print(json.dumps(report, indent=2))