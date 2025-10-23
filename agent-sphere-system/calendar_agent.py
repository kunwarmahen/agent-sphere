"""
Calendar & Email Agent - Manage emails, calendar events, and scheduling
"""
import json
from agent_framework import Agent, Tool
from datetime import datetime, timedelta


class CalendarEmailManager:
    """Manages emails and calendar events"""
    def __init__(self):
        self.emails = [
            {
                "id": 1,
                "from": "boss@company.com",
                "subject": "Project Alpha - Status Update Required",
                "body": "Can you provide an update on the current sprint?",
                "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "read": False,
                "starred": False
            },
            {
                "id": 2,
                "from": "sarah@friends.com",
                "subject": "Coffee tomorrow?",
                "body": "Are you free for coffee at 3 PM tomorrow?",
                "date": (datetime.now() - timedelta(hours=5)).isoformat(),
                "read": False,
                "starred": True
            },
            {
                "id": 3,
                "from": "notifications@github.com",
                "subject": "[GitHub] New Pull Request",
                "body": "Someone commented on your PR",
                "date": (datetime.now() - timedelta(days=1)).isoformat(),
                "read": True,
                "starred": False
            }
        ]
        
        self.calendar = [
            {
                "id": 1,
                "title": "Team Standup",
                "start": (datetime.now() + timedelta(hours=1)).isoformat(),
                "duration": 30,
                "location": "Conference Room A",
                "attendees": ["team@company.com"],
                "description": "Daily team sync"
            },
            {
                "id": 2,
                "title": "Lunch with Client",
                "start": (datetime.now() + timedelta(hours=5)).isoformat(),
                "duration": 60,
                "location": "Downtown Bistro",
                "attendees": ["client@external.com"],
                "description": "Discuss new features"
            },
            {
                "id": 3,
                "title": "Project Review",
                "start": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                "duration": 90,
                "location": "Conference Room B",
                "attendees": ["team@company.com", "manager@company.com"],
                "description": "Quarterly project review"
            }
        ]
        
        self.sent_emails = []
        self.email_log = []
    
    def read_emails(self, limit: int = 5, unread_only: bool = True) -> str:
        """Read emails with optional filtering"""
        emails = self.emails
        
        if unread_only:
            emails = [e for e in emails if not e["read"]]
        
        emails = sorted(emails, key=lambda x: x["date"], reverse=True)[:limit]
        
        for email in emails:
            email["read"] = True
        
        return json.dumps({
            "count": len(emails),
            "emails": [{k: v for k, v in e.items() if k != "body"} for e in emails]
        })
    
    def get_email_details(self, email_id: int) -> str:
        """Get full email details"""
        for email in self.emails:
            if email["id"] == email_id:
                email["read"] = True
                return json.dumps(email)
        return json.dumps({"error": f"Email {email_id} not found"})
    
    def send_email(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Send an email"""
        email = {
            "id": len(self.emails) + len(self.sent_emails) + 1,
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "body": body,
            "date": datetime.now().isoformat(),
            "status": "sent"
        }
        self.sent_emails.append(email)
        self.email_log.append({"type": "sent", "to": to, "subject": subject, "timestamp": datetime.now().isoformat()})
        return f"Email sent to {to} with subject: '{subject}'"
    
    def reply_to_email(self, email_id: int, reply_body: str) -> str:
        """Reply to an email"""
        for email in self.emails:
            if email["id"] == email_id:
                reply = {
                    "in_reply_to": email_id,
                    "to": email["from"],
                    "subject": f"Re: {email['subject']}",
                    "body": reply_body,
                    "date": datetime.now().isoformat(),
                    "status": "sent"
                }
                self.sent_emails.append(reply)
                self.email_log.append({"type": "reply", "to": email["from"], "timestamp": datetime.now().isoformat()})
                return f"Reply sent to {email['from']}"
        return f"Email {email_id} not found"
    
    def get_calendar_events(self, days_ahead: int = 7) -> str:
        """Get upcoming calendar events"""
        now = datetime.now()
        future_cutoff = now + timedelta(days=days_ahead)
        
        upcoming = [
            e for e in self.calendar
            if datetime.fromisoformat(e["start"]) <= future_cutoff
        ]
        
        upcoming = sorted(upcoming, key=lambda x: x["start"])
        
        return json.dumps({
            "count": len(upcoming),
            "events": upcoming
        })
    
    def schedule_event(self, title: str, start_time: str, duration: int, 
                      location: str = "", attendees: list = None, description: str = "") -> str:
        """Schedule a new calendar event"""
        try:
            # Validate start_time format
            datetime.fromisoformat(start_time)
        except ValueError:
            return "Invalid time format. Use ISO format: YYYY-MM-DD HH:MM:SS"
        
        event = {
            "id": len(self.calendar) + 1,
            "title": title,
            "start": start_time,
            "duration": duration,
            "location": location,
            "attendees": attendees or [],
            "description": description
        }
        self.calendar.append(event)
        self.email_log.append({"type": "event_created", "title": title, "timestamp": datetime.now().isoformat()})
        
        return f"Event '{title}' scheduled for {start_time} (Duration: {duration} min)"
    
    def reschedule_event(self, event_id: int, new_start_time: str) -> str:
        """Reschedule an existing event"""
        for event in self.calendar:
            if event["id"] == event_id:
                old_time = event["start"]
                event["start"] = new_start_time
                self.email_log.append({
                    "type": "event_rescheduled",
                    "event": event["title"],
                    "old_time": old_time,
                    "new_time": new_start_time,
                    "timestamp": datetime.now().isoformat()
                })
                return f"Event '{event['title']}' rescheduled to {new_start_time}"
        return f"Event {event_id} not found"
    
    def delete_event(self, event_id: int) -> str:
        """Delete a calendar event"""
        for i, event in enumerate(self.calendar):
            if event["id"] == event_id:
                deleted_title = event["title"]
                self.calendar.pop(i)
                self.email_log.append({"type": "event_deleted", "title": deleted_title, "timestamp": datetime.now().isoformat()})
                return f"Event '{deleted_title}' deleted"
        return f"Event {event_id} not found"
    
    def get_busy_times(self) -> str:
        """Get busy times in the next 7 days"""
        now = datetime.now()
        week_ahead = now + timedelta(days=7)
        
        busy = [
            {"date": e["start"].split("T")[0], "time": e["start"].split("T")[1], "event": e["title"]}
            for e in self.calendar
            if datetime.fromisoformat(e["start"]) <= week_ahead
        ]
        
        return json.dumps({"busy_times": busy})
    
    def find_free_slot(self, duration: int = 60) -> str:
        """Find next available free time slot"""
        now = datetime.now()
        
        for i in range(7):
            check_time = now + timedelta(days=i, hours=9)
            check_time = check_time.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # Check if this slot is free
            is_free = True
            for event in self.calendar:
                event_start = datetime.fromisoformat(event["start"])
                event_end = event_start + timedelta(minutes=event["duration"])
                check_end = check_time + timedelta(minutes=duration)
                
                if not (check_end <= event_start or check_time >= event_end):
                    is_free = False
                    break
            
            if is_free:
                return f"Next available slot: {check_time.isoformat()} for {duration} minutes"
        
        return "No free slots available in the next 7 days"
    
    def get_activity_log(self, limit: int = 10) -> str:
        """Get email and calendar activity log"""
        return json.dumps(self.email_log[-limit:])


# Initialize manager
manager = CalendarEmailManager()

# Create tools
calendar_tools = [
    Tool("read_emails", 
         "Read unread emails with optional limit", 
         manager.read_emails, 
         {"limit": "int (optional)", "unread_only": "bool (optional)"}),
    
    Tool("get_email_details", 
         "Get full details of a specific email", 
         manager.get_email_details, 
         {"email_id": "int"}),
    
    Tool("send_email", 
         "Send an email to recipient(s)", 
         manager.send_email, 
         {"to": "str", "subject": "str", "body": "str", "cc": "str (optional)", "bcc": "str (optional)"}),
    
    Tool("reply_to_email", 
         "Reply to an email", 
         manager.reply_to_email, 
         {"email_id": "int", "reply_body": "str"}),
    
    Tool("get_calendar_events", 
         "Get upcoming calendar events", 
         manager.get_calendar_events, 
         {"days_ahead": "int (optional)"}),
    
    Tool("schedule_event", 
         "Schedule a new calendar event", 
         manager.schedule_event, 
         {"title": "str", "start_time": "str (ISO format)", "duration": "int (minutes)", 
          "location": "str (optional)", "attendees": "list (optional)", "description": "str (optional)"}),
    
    Tool("reschedule_event", 
         "Reschedule an existing event", 
         manager.reschedule_event, 
         {"event_id": "int", "new_start_time": "str (ISO format)"}),
    
    Tool("delete_event", 
         "Delete a calendar event", 
         manager.delete_event, 
         {"event_id": "int"}),
    
    Tool("get_busy_times", 
         "Get all busy times in the next week", 
         manager.get_busy_times, 
         {}),
    
    Tool("find_free_slot", 
         "Find the next available free time slot", 
         manager.find_free_slot, 
         {"duration": "int (minutes, optional)"}),
    
    Tool("get_activity_log", 
         "Get email and calendar activity history", 
         manager.get_activity_log, 
         {"limit": "int (optional)"}),
]

# Create agent
calendar_agent = Agent(
    name="Assistant",
    role="Calendar & Email Manager",
    tools=calendar_tools,
    system_instructions="You are a calendar and email management assistant. Help users manage their communications and schedule efficiently. When scheduling events, use ISO format for dates."
)


if __name__ == "__main__":
    # Test calendar agent
    print("=" * 70)
    print("CALENDAR & EMAIL AGENT - Interactive Demo")
    print("=" * 70)
    
    test_requests = [
        "Show me my unread emails",
        "What's on my calendar for the next 3 days?",
        "When am I free for a 1-hour meeting?",
        "Send an email to alice@company.com saying I'll be late to the meeting",
        "Schedule a meeting with the team at 2 PM tomorrow for 1 hour"
    ]
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * 70)
        result = calendar_agent.think_and_act(request, verbose=False)
        print(f"Agent: {result}\n")
        calendar_agent.clear_memory()