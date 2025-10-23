"""
Pre-built Workflow Templates - Ready-to-use workflows for common scenarios
Users can use these as templates or inspiration for creating their own workflows
"""

from workflow_engine import WorkflowEngine, WorkflowTask, Workflow
from typing import List


class WorkflowTemplates:
    """Collection of pre-built workflow templates"""
    
    @staticmethod
    def create_morning_routine(engine: WorkflowEngine) -> Workflow:
        """Template: Morning Routine - Automate your morning"""
        workflow = engine.create_workflow(
            "morning_routine",
            "Morning Routine",
            "Automate your complete morning routine"
        )
        
        tasks = [
            WorkflowTask("wake_home", "home", 
                        "Good morning! Turn on all the lights, set temperature to 72 degrees"),
            WorkflowTask("coffee", "home", 
                        "Start the coffee maker"),
            WorkflowTask("check_calendar", "calendar", 
                        "What are my important meetings today?"),
            WorkflowTask("check_emails", "calendar", 
                        "Show me unread emails from my boss or important contacts"),
            WorkflowTask("financial_check", "finance", 
                        "What's my financial summary for today?"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_evening_winddown(engine: WorkflowEngine) -> Workflow:
        """Template: Evening Winddown - Prepare home for evening"""
        workflow = engine.create_workflow(
            "evening_winddown",
            "Evening Winddown",
            "Prepare home for evening and review the day"
        )
        
        tasks = [
            WorkflowTask("lock_secure", "home", 
                        "Lock all doors and close the garage for the night"),
            WorkflowTask("adjust_lighting", "home", 
                        "Dim all lights to 40% brightness for a relaxing evening"),
            WorkflowTask("set_temperature", "home", 
                        "Set thermostat to 70 degrees for sleeping"),
            WorkflowTask("day_review", "calendar", 
                        "Show me what I accomplished today from my calendar"),
            WorkflowTask("financial_review", "finance", 
                        "How much did I spend today? Am I on budget?"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_work_day_start(engine: WorkflowEngine) -> Workflow:
        """Template: Work Day Start - Get ready for focused work"""
        workflow = engine.create_workflow(
            "work_day_start",
            "Work Day Start",
            "Prepare for a productive work day"
        )
        
        tasks = [
            WorkflowTask("prepare_office", "home", 
                        "Turn on office lights to 80% brightness and set comfortable temperature"),
            WorkflowTask("check_schedule", "calendar", 
                        "What meetings do I have today? When is my first meeting?"),
            WorkflowTask("email_status", "calendar", 
                        "How many unread emails do I have? Summarize urgent ones"),
            WorkflowTask("financial_goals", "finance", 
                        "Show my financial goals progress"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_guest_arrival(engine: WorkflowEngine) -> Workflow:
        """Template: Guest Arrival - Quick home preparation"""
        workflow = engine.create_workflow(
            "guest_arrival",
            "Guest Arrival",
            "Quickly prepare home for guests"
        )
        
        tasks = [
            WorkflowTask("brighten_home", "home", 
                        "Turn on all lights in living room and entry area"),
            WorkflowTask("set_ambiance", "home", 
                        "Set temperature to 73 degrees for comfort"),
            WorkflowTask("tidy_devices", "home", 
                        "Turn off TV and make sure home looks presentable"),
            WorkflowTask("schedule_guest", "calendar", 
                        "Add guest visit to calendar for next 3 hours"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_monthly_financial_review(engine: WorkflowEngine) -> Workflow:
        """Template: Monthly Financial Review - Deep dive into finances"""
        workflow = engine.create_workflow(
            "monthly_financial_review",
            "Monthly Financial Review",
            "Complete monthly financial analysis and planning"
        )
        
        tasks = [
            WorkflowTask("account_check", "finance", 
                        "Show me all my account balances and net worth"),
            WorkflowTask("spending_analysis", "finance", 
                        "Analyze my spending this month by category"),
            WorkflowTask("investments", "finance", 
                        "How are my investments performing?"),
            WorkflowTask("goals_progress", "finance", 
                        "Show me my financial goals and progress"),
            WorkflowTask("savings_projection", "finance", 
                        "If I save $500 per month, where will I be in a year?"),
            WorkflowTask("budget_review", "finance", 
                        "Which categories am I over budget in?"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_weekend_planning(engine: WorkflowEngine) -> Workflow:
        """Template: Weekend Planning - Plan your weekend"""
        workflow = engine.create_workflow(
            "weekend_planning",
            "Weekend Planning",
            "Plan your weekend activities"
        )
        
        tasks = [
            WorkflowTask("week_review", "calendar", 
                        "What events are scheduled for this weekend?"),
            WorkflowTask("email_catch_up", "calendar", 
                        "Show me any important emails I might have missed"),
            WorkflowTask("free_time", "calendar", 
                        "What are my free time slots this weekend?"),
            WorkflowTask("spending_budget", "finance", 
                        "How much budget do I have left for entertainment this month?"),
            WorkflowTask("home_prep", "home", 
                        "Ensure home is comfortable for the weekend"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_meeting_preparation(engine: WorkflowEngine) -> Workflow:
        """Template: Meeting Preparation - Get ready for important meeting"""
        workflow = engine.create_workflow(
            "meeting_preparation",
            "Meeting Preparation",
            "Prepare home office for important meeting"
        )
        
        tasks = [
            WorkflowTask("office_setup", "home", 
                        "Turn on office lights to 90% brightness"),
            WorkflowTask("temperature", "home", 
                        "Set temperature to 72 degrees for optimal focus"),
            WorkflowTask("meeting_details", "calendar", 
                        "Show me the details of my next meeting - who's attending and when"),
            WorkflowTask("relevant_emails", "calendar", 
                        "Show me recent emails from the meeting attendees"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_vacation_preparation(engine: WorkflowEngine) -> Workflow:
        """Template: Vacation Preparation - Prepare before leaving"""
        workflow = engine.create_workflow(
            "vacation_preparation",
            "Vacation Preparation",
            "Prepare home before leaving for vacation"
        )
        
        tasks = [
            WorkflowTask("secure_home", "home", 
                        "Lock all doors and garage. Turn off all lights. Set thermostat to 65 degrees"),
            WorkflowTask("turn_off_devices", "home", 
                        "Turn off TV and other smart devices"),
            WorkflowTask("vacation_schedule", "calendar", 
                        "Show my vacation schedule and important dates"),
            WorkflowTask("vacation_fund", "finance", 
                        "How much have I saved for my vacation fund?"),
            WorkflowTask("set_ooo", "calendar", 
                        "Set out of office for my vacation period"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_health_check_day(engine: WorkflowEngine) -> Workflow:
        """Template: Health Check Day - Review wellness and habits"""
        workflow = engine.create_workflow(
            "health_check_day",
            "Health Check Day",
            "Review health, budget, and daily habits"
        )
        
        tasks = [
            WorkflowTask("schedule_check", "calendar", 
                        "Do I have any health-related appointments scheduled?"),
            WorkflowTask("budget_health", "finance", 
                        "How much have I spent on health and wellness this month?"),
            WorkflowTask("home_comfort", "home", 
                        "Ensure home temperature and lighting are optimal for wellness"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def create_productivity_boost(engine: WorkflowEngine) -> Workflow:
        """Template: Productivity Boost - Optimize for deep work"""
        workflow = engine.create_workflow(
            "productivity_boost",
            "Productivity Boost",
            "Optimize environment for deep, focused work"
        )
        
        tasks = [
            WorkflowTask("focus_lighting", "home", 
                        "Set office lights to 100% brightness for maximum focus"),
            WorkflowTask("focus_temp", "home", 
                        "Set temperature to 70 degrees - optimal for focus"),
            WorkflowTask("clear_schedule", "calendar", 
                        "Block 3 hours for focused work. Do I have conflicting meetings?"),
            WorkflowTask("email_summary", "calendar", 
                        "Quick summary of emails - any urgent items I need to address first?"),
        ]
        
        workflow.add_tasks(tasks)
        return workflow
    
    @staticmethod
    def list_templates() -> List[dict]:
        """List all available templates"""
        return [
            {
                "id": "morning_routine",
                "name": "Morning Routine",
                "description": "Automate your complete morning routine",
                "tasks": 5
            },
            {
                "id": "evening_winddown",
                "name": "Evening Winddown",
                "description": "Prepare home for evening and review the day",
                "tasks": 5
            },
            {
                "id": "work_day_start",
                "name": "Work Day Start",
                "description": "Get ready for a productive work day",
                "tasks": 4
            },
            {
                "id": "guest_arrival",
                "name": "Guest Arrival",
                "description": "Quickly prepare home for guests",
                "tasks": 4
            },
            {
                "id": "monthly_financial_review",
                "name": "Monthly Financial Review",
                "description": "Complete monthly financial analysis and planning",
                "tasks": 6
            },
            {
                "id": "weekend_planning",
                "name": "Weekend Planning",
                "description": "Plan your weekend activities",
                "tasks": 5
            },
            {
                "id": "meeting_preparation",
                "name": "Meeting Preparation",
                "description": "Get ready for important meeting",
                "tasks": 4
            },
            {
                "id": "vacation_preparation",
                "name": "Vacation Preparation",
                "description": "Prepare home before leaving for vacation",
                "tasks": 5
            },
            {
                "id": "health_check_day",
                "name": "Health Check Day",
                "description": "Review wellness and daily habits",
                "tasks": 3
            },
            {
                "id": "productivity_boost",
                "name": "Productivity Boost",
                "description": "Optimize environment for deep, focused work",
                "tasks": 4
            },
        ]
    
    @staticmethod
    def create_from_template(engine: WorkflowEngine, template_id: str) -> Workflow:
        """Create a workflow from a template"""
        templates = {
            "morning_routine": WorkflowTemplates.create_morning_routine,
            "evening_winddown": WorkflowTemplates.create_evening_winddown,
            "work_day_start": WorkflowTemplates.create_work_day_start,
            "guest_arrival": WorkflowTemplates.create_guest_arrival,
            "monthly_financial_review": WorkflowTemplates.create_monthly_financial_review,
            "weekend_planning": WorkflowTemplates.create_weekend_planning,
            "meeting_preparation": WorkflowTemplates.create_meeting_preparation,
            "vacation_preparation": WorkflowTemplates.create_vacation_preparation,
            "health_check_day": WorkflowTemplates.create_health_check_day,
            "productivity_boost": WorkflowTemplates.create_productivity_boost,
        }
        
        if template_id not in templates:
            return None
        
        return templates[template_id](engine)


if __name__ == "__main__":
    # Demo template usage
    from workflow_engine import WorkflowEngine
    from home_agent import home_agent
    from calendar_agent import calendar_agent
    from finance_agent import finance_agent
    
    # Setup engine
    engine = WorkflowEngine()
    engine.register_agent("home", home_agent)
    engine.register_agent("calendar", calendar_agent)
    engine.register_agent("finance", finance_agent)
    
    print("=" * 70)
    print("WORKFLOW TEMPLATES DEMO")
    print("=" * 70)
    
    # Show available templates
    print("\nAvailable Templates:")
    for template in WorkflowTemplates.list_templates():
        print(f"\n  • {template['name']} ({template['id']})")
        print(f"    {template['description']}")
        print(f"    Tasks: {template['tasks']}")
    
    # Create and execute a template
    print("\n" + "=" * 70)
    print("Creating Morning Routine template...")
    workflow = WorkflowTemplates.create_from_template(engine, "morning_routine")
    
    if workflow:
        print(f"\n✅ Workflow created: {workflow.name}")
        print(f"Tasks: {len(workflow.tasks)}")
        
        # Show tasks
        print("\nWorkflow Tasks:")
        for task in workflow.tasks:
            print(f"  • {task.task_id}: {task.request[:60]}...")
        
        # Execute
        print("\n" + "=" * 70)
        print("Executing workflow...")
        result = engine.execute_workflow(workflow.workflow_id, verbose=True)