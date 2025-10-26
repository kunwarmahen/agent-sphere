"""
Pre-built Workflow Templates - FIXED VERSION with proper task linking
"""

from workflow.workflow_engine import WorkflowEngine, WorkflowTask, Workflow
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
        
        # Create tasks
        wake_home = WorkflowTask("wake_home", "home", 
                                "Good morning! Turn on all the lights and set temperature to 72 degrees")
        coffee = WorkflowTask("coffee", "home", 
                            "Start the coffee maker")
        check_calendar = WorkflowTask("check_calendar", "calendar", 
                                     "What are my important meetings today?")
        check_emails = WorkflowTask("check_emails", "calendar", 
                                   "Show me unread emails from my boss or important contacts")
        financial_check = WorkflowTask("financial_check", "finance", 
                                      "What's my financial summary for today?")
        
        # Link tasks sequentially
        wake_home.next_task_id = "coffee"
        coffee.next_task_id = "check_calendar"
        check_calendar.next_task_id = "check_emails"
        check_emails.next_task_id = "financial_check"
        
        # Add to workflow
        workflow.add_task(wake_home, is_start=True)
        workflow.add_task(coffee)
        workflow.add_task(check_calendar)
        workflow.add_task(check_emails)
        workflow.add_task(financial_check)
        
        return workflow
    
    @staticmethod
    def create_evening_winddown(engine: WorkflowEngine) -> Workflow:
        """Template: Evening Winddown - Prepare home for evening"""
        workflow = engine.create_workflow(
            "evening_winddown",
            "Evening Winddown",
            "Prepare home for evening and review the day"
        )
        
        lock_secure = WorkflowTask("lock_secure", "home", 
                                  "Lock all doors and close the garage for the night")
        adjust_lighting = WorkflowTask("adjust_lighting", "home", 
                                      "Dim all lights to 40% brightness for a relaxing evening")
        set_temperature = WorkflowTask("set_temperature", "home", 
                                      "Set thermostat to 70 degrees for sleeping")
        day_review = WorkflowTask("day_review", "calendar", 
                                 "Show me what I accomplished today from my calendar")
        financial_review = WorkflowTask("financial_review", "finance", 
                                       "How much did I spend today? Am I on budget?")
        
        # Link tasks
        lock_secure.next_task_id = "adjust_lighting"
        adjust_lighting.next_task_id = "set_temperature"
        set_temperature.next_task_id = "day_review"
        day_review.next_task_id = "financial_review"
        
        # Add to workflow
        workflow.add_task(lock_secure, is_start=True)
        workflow.add_task(adjust_lighting)
        workflow.add_task(set_temperature)
        workflow.add_task(day_review)
        workflow.add_task(financial_review)
        
        return workflow
    
    @staticmethod
    def create_work_day_start(engine: WorkflowEngine) -> Workflow:
        """Template: Work Day Start - Get ready for focused work"""
        workflow = engine.create_workflow(
            "work_day_start",
            "Work Day Start",
            "Prepare for a productive work day"
        )
        
        prepare_office = WorkflowTask("prepare_office", "home", 
                                     "Turn on office lights to 80% brightness and set comfortable temperature")
        check_schedule = WorkflowTask("check_schedule", "calendar", 
                                     "What meetings do I have today? When is my first meeting?")
        email_status = WorkflowTask("email_status", "calendar", 
                                   "How many unread emails do I have? Summarize urgent ones")
        financial_goals = WorkflowTask("financial_goals", "finance", 
                                      "Show my financial goals progress")
        
        # Link tasks
        prepare_office.next_task_id = "check_schedule"
        check_schedule.next_task_id = "email_status"
        email_status.next_task_id = "financial_goals"
        
        # Add to workflow
        workflow.add_task(prepare_office, is_start=True)
        workflow.add_task(check_schedule)
        workflow.add_task(email_status)
        workflow.add_task(financial_goals)
        
        return workflow
    
    @staticmethod
    def create_guest_arrival(engine: WorkflowEngine) -> Workflow:
        """Template: Guest Arrival - Quick home preparation"""
        workflow = engine.create_workflow(
            "guest_arrival",
            "Guest Arrival",
            "Quickly prepare home for guests"
        )
        
        brighten_home = WorkflowTask("brighten_home", "home", 
                                    "Turn on all lights in living room and entry area")
        set_ambiance = WorkflowTask("set_ambiance", "home", 
                                   "Set temperature to 73 degrees for comfort")
        tidy_devices = WorkflowTask("tidy_devices", "home", 
                                   "Turn off TV and make sure home looks presentable")
        schedule_guest = WorkflowTask("schedule_guest", "calendar", 
                                     "Add guest visit to calendar for next 3 hours")
        
        # Link tasks
        brighten_home.next_task_id = "set_ambiance"
        set_ambiance.next_task_id = "tidy_devices"
        tidy_devices.next_task_id = "schedule_guest"
        
        # Add to workflow
        workflow.add_task(brighten_home, is_start=True)
        workflow.add_task(set_ambiance)
        workflow.add_task(tidy_devices)
        workflow.add_task(schedule_guest)
        
        return workflow
    
    @staticmethod
    def create_monthly_financial_review(engine: WorkflowEngine) -> Workflow:
        """Template: Monthly Financial Review - Deep dive into finances"""
        workflow = engine.create_workflow(
            "monthly_financial_review",
            "Monthly Financial Review",
            "Complete monthly financial analysis and planning"
        )
        
        account_check = WorkflowTask("account_check", "finance", 
                                    "Show me all my account balances and net worth")
        spending_analysis = WorkflowTask("spending_analysis", "finance", 
                                        "Analyze my spending this month by category")
        investments = WorkflowTask("investments", "finance", 
                                  "How are my investments performing?")
        goals_progress = WorkflowTask("goals_progress", "finance", 
                                     "Show me my financial goals and progress")
        savings_projection = WorkflowTask("savings_projection", "finance", 
                                         "If I save $500 per month, where will I be in a year?")
        budget_review = WorkflowTask("budget_review", "finance", 
                                    "Which categories am I over budget in?")
        
        # Link tasks
        account_check.next_task_id = "spending_analysis"
        spending_analysis.next_task_id = "investments"
        investments.next_task_id = "goals_progress"
        goals_progress.next_task_id = "savings_projection"
        savings_projection.next_task_id = "budget_review"
        
        # Add to workflow
        workflow.add_task(account_check, is_start=True)
        workflow.add_task(spending_analysis)
        workflow.add_task(investments)
        workflow.add_task(goals_progress)
        workflow.add_task(savings_projection)
        workflow.add_task(budget_review)
        
        return workflow
    
    @staticmethod
    def create_weekend_planning(engine: WorkflowEngine) -> Workflow:
        """Template: Weekend Planning - Plan your weekend"""
        workflow = engine.create_workflow(
            "weekend_planning",
            "Weekend Planning",
            "Plan your weekend activities"
        )
        
        week_review = WorkflowTask("week_review", "calendar", 
                                  "What events are scheduled for this weekend?")
        email_catch_up = WorkflowTask("email_catch_up", "calendar", 
                                     "Show me any important emails I might have missed")
        free_time = WorkflowTask("free_time", "calendar", 
                                "What are my free time slots this weekend?")
        spending_budget = WorkflowTask("spending_budget", "finance", 
                                      "How much budget do I have left for entertainment this month?")
        home_prep = WorkflowTask("home_prep", "home", 
                                "Ensure home is comfortable for the weekend")
        
        # Link tasks
        week_review.next_task_id = "email_catch_up"
        email_catch_up.next_task_id = "free_time"
        free_time.next_task_id = "spending_budget"
        spending_budget.next_task_id = "home_prep"
        
        # Add to workflow
        workflow.add_task(week_review, is_start=True)
        workflow.add_task(email_catch_up)
        workflow.add_task(free_time)
        workflow.add_task(spending_budget)
        workflow.add_task(home_prep)
        
        return workflow
    
    @staticmethod
    def create_meeting_preparation(engine: WorkflowEngine) -> Workflow:
        """Template: Meeting Preparation - Get ready for important meeting"""
        workflow = engine.create_workflow(
            "meeting_preparation",
            "Meeting Preparation",
            "Prepare home office for important meeting"
        )
        
        office_setup = WorkflowTask("office_setup", "home", 
                                   "Turn on office lights to 90% brightness")
        temperature = WorkflowTask("temperature", "home", 
                                  "Set temperature to 72 degrees for optimal focus")
        meeting_details = WorkflowTask("meeting_details", "calendar", 
                                      "Show me the details of my next meeting - who's attending and when")
        relevant_emails = WorkflowTask("relevant_emails", "calendar", 
                                      "Show me recent emails from the meeting attendees")
        
        # Link tasks
        office_setup.next_task_id = "temperature"
        temperature.next_task_id = "meeting_details"
        meeting_details.next_task_id = "relevant_emails"
        
        # Add to workflow
        workflow.add_task(office_setup, is_start=True)
        workflow.add_task(temperature)
        workflow.add_task(meeting_details)
        workflow.add_task(relevant_emails)
        
        return workflow
    
    @staticmethod
    def create_vacation_preparation(engine: WorkflowEngine) -> Workflow:
        """Template: Vacation Preparation - Prepare before leaving"""
        workflow = engine.create_workflow(
            "vacation_preparation",
            "Vacation Preparation",
            "Prepare home before leaving for vacation"
        )
        
        secure_home = WorkflowTask("secure_home", "home", 
                                  "Lock all doors and garage. Turn off all lights. Set thermostat to 65 degrees")
        turn_off_devices = WorkflowTask("turn_off_devices", "home", 
                                       "Turn off TV and other smart devices")
        vacation_schedule = WorkflowTask("vacation_schedule", "calendar", 
                                        "Show my vacation schedule and important dates")
        vacation_fund = WorkflowTask("vacation_fund", "finance", 
                                    "How much have I saved for my vacation fund?")
        set_ooo = WorkflowTask("set_ooo", "calendar", 
                              "Reminder to set out of office for vacation period")
        
        # Link tasks
        secure_home.next_task_id = "turn_off_devices"
        turn_off_devices.next_task_id = "vacation_schedule"
        vacation_schedule.next_task_id = "vacation_fund"
        vacation_fund.next_task_id = "set_ooo"
        
        # Add to workflow
        workflow.add_task(secure_home, is_start=True)
        workflow.add_task(turn_off_devices)
        workflow.add_task(vacation_schedule)
        workflow.add_task(vacation_fund)
        workflow.add_task(set_ooo)
        
        return workflow
    
    @staticmethod
    def create_health_check_day(engine: WorkflowEngine) -> Workflow:
        """Template: Health Check Day - Review wellness and habits"""
        workflow = engine.create_workflow(
            "health_check_day",
            "Health Check Day",
            "Review health, budget, and daily habits"
        )
        
        schedule_check = WorkflowTask("schedule_check", "calendar", 
                                     "Do I have any health-related appointments scheduled?")
        budget_health = WorkflowTask("budget_health", "finance", 
                                    "How much have I spent on health and wellness this month?")
        home_comfort = WorkflowTask("home_comfort", "home", 
                                   "Ensure home temperature and lighting are optimal for wellness")
        
        # Link tasks
        schedule_check.next_task_id = "budget_health"
        budget_health.next_task_id = "home_comfort"
        
        # Add to workflow
        workflow.add_task(schedule_check, is_start=True)
        workflow.add_task(budget_health)
        workflow.add_task(home_comfort)
        
        return workflow
    
    @staticmethod
    def create_productivity_boost(engine: WorkflowEngine) -> Workflow:
        """Template: Productivity Boost - Optimize for deep work"""
        workflow = engine.create_workflow(
            "productivity_boost",
            "Productivity Boost",
            "Optimize environment for deep, focused work"
        )
        
        focus_lighting = WorkflowTask("focus_lighting", "home", 
                                     "Set office lights to 100% brightness for maximum focus")
        focus_temp = WorkflowTask("focus_temp", "home", 
                                 "Set temperature to 70 degrees - optimal for focus")
        clear_schedule = WorkflowTask("clear_schedule", "calendar", 
                                     "Block 3 hours for focused work. Do I have conflicting meetings?")
        email_summary = WorkflowTask("email_summary", "calendar", 
                                    "Quick summary of emails - any urgent items I need to address first?")
        
        # Link tasks
        focus_lighting.next_task_id = "focus_temp"
        focus_temp.next_task_id = "clear_schedule"
        clear_schedule.next_task_id = "email_summary"
        
        # Add to workflow
        workflow.add_task(focus_lighting, is_start=True)
        workflow.add_task(focus_temp)
        workflow.add_task(clear_schedule)
        workflow.add_task(email_summary)
        
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
        for task_id, task in workflow.tasks.items():
            print(f"  • {task.task_id}: {task.request[:60]}...")
            if task.next_task_id:
                print(f"    → Next: {task.next_task_id}")
        
        # Execute
        print("\n" + "=" * 70)
        print("Executing workflow...")
        result = engine.execute_workflow(workflow.workflow_id, verbose=True)