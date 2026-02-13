"""
Google Unified Agent - Combines Gmail and Google Calendar functionality
"""
import json
import logging
from base.agent_framework import Agent, Tool
from agents.google.google_calendar_agent import calendar_manager
from agents.google.gmail_agent import gmail_manager

logger = logging.getLogger(__name__)

class UnifiedGoogleManager:
    """Unified manager that combines Gmail and Calendar functionality."""
    def __init__(self):
        self.calendar = calendar_manager
        self.gmail = gmail_manager

    # ===== GMAIL METHODS =====

    def read_emails(self, limit: int = 5, unread_only: bool = True) -> str:
        """Read emails from Gmail."""
        if unread_only:
            emails = self.gmail.get_unread_emails(limit)
        else:
            emails = self.gmail.get_activity_log(limit)

        if isinstance(emails, str):
            # Error string from DummyManager or API failure — wrap as JSON
            return json.dumps({"count": 0, "emails": [], "error": emails})

        return json.dumps({
            "count": len(emails),
            "emails": emails
        })

    def get_email_details(self, email_id: str) -> str:
        """Get full email details by ID."""
        return self.gmail.read_email(email_id)

    def send_email(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        """Send an email via Gmail."""
        # Gmail API doesn't support CC/BCC through our current implementation
        # We'll just use the recipient field
        return self.gmail.send_email(to, subject, body)

    def reply_to_email(self, email_id: str, reply_body: str) -> str:
        """Reply to an email (simplified - sends a new email)."""
        # For now, this would require fetching the original email details
        # and sending a new email with Re: prefix
        return "Tool Not Implemented: Use 'send_email' to send a reply manually."

    # ===== CALENDAR METHODS =====

    def get_calendar_events(self, days_ahead: int = 7) -> str:
        """Get upcoming calendar events from Google Calendar."""
        try:
            events = self.calendar.get_events(days_ahead)

            if isinstance(events, str):
                return json.dumps({
                    "count": 0,
                    "events": [],
                    "message": events
                })

            return json.dumps({
                "count": len(events),
                "events": events,
                "success": True
            })
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return json.dumps({
                "count": 0,
                "events": [],
                "success": False,
                "error": str(e)
            })

    def schedule_event(self, title: str, start_time: str, duration: int,
                      location: str = "", attendees: list = None, description: str = "") -> str:
        """Schedule a new event on Google Calendar."""
        # Note: Google Calendar API doesn't use 'title', it uses 'summary'
        return self.calendar.schedule_event(title, start_time, duration)

    def reschedule_event(self, event_id: str, new_start_time: str) -> str:
        """Reschedule an existing event."""
        return "Tool Not Implemented: Use Google Calendar UI to reschedule events."

    def delete_event(self, event_id: str) -> str:
        """Delete a calendar event."""
        return "Tool Not Implemented: Use Google Calendar UI to delete events."

    def get_busy_times(self) -> str:
        """Get all busy times from Google Calendar."""
        busy = self.calendar.get_busy_times()
        if isinstance(busy, str):
            return busy
        return json.dumps({"busy_times": busy})

    def find_free_slot(self, duration: int = 60) -> str:
        """Find the next available free time slot."""
        return self.calendar.find_free_slot(duration)

    def get_activity_log(self, limit: int = 10) -> str:
        """Get combined email and calendar activity."""
        # Return recent emails as activity
        return self.gmail.get_activity_log(limit)


# Initialize unified manager
manager = UnifiedGoogleManager()

# Create tools combining both Gmail and Calendar
unified_tools = [
    # ===== EMAIL TOOLS =====
    Tool("read_emails",
         "Read emails from Gmail. By default shows only unread emails.",
         manager.read_emails,
         {"limit": "int (optional, default 5)", "unread_only": "bool (optional, default True)"}),

    Tool("get_email_details",
         "Get full details of a specific email by its ID",
         manager.get_email_details,
         {"email_id": "str (required, the Gmail message ID)"}),

    Tool("send_email",
         "Send an email via Gmail",
         manager.send_email,
         {"to": "str (required, recipient email)", "subject": "str (required)", "body": "str (required)",
          "cc": "str (optional, not implemented)", "bcc": "str (optional, not implemented)"}),

    Tool("reply_to_email",
         "Reply to an email (currently not implemented)",
         manager.reply_to_email,
         {"email_id": "str", "reply_body": "str"}),

    # ===== CALENDAR TOOLS =====
    Tool("get_calendar_events",
         "Get upcoming events from Google Calendar",
         manager.get_calendar_events,
         {"days_ahead": "int (optional, number of days to look ahead, default 7)"}),

    Tool("schedule_event",
         "Schedule a new event on Google Calendar. IMPORTANT: start_time MUST be in ISO format with timezone (e.g., '2025-01-05T14:00:00-05:00')",
         manager.schedule_event,
         {"title": "str (required, event title/summary)",
          "start_time": "str (required, ISO format with timezone)",
          "duration": "int (required, duration in minutes)",
          "location": "str (optional, not implemented)",
          "attendees": "list (optional, not implemented)",
          "description": "str (optional, not implemented)"}),

    Tool("reschedule_event",
         "Reschedule an existing event (not implemented)",
         manager.reschedule_event,
         {"event_id": "str", "new_start_time": "str"}),

    Tool("delete_event",
         "Delete a calendar event (not implemented)",
         manager.delete_event,
         {"event_id": "str"}),

    Tool("get_busy_times",
         "Get all busy time slots in the next 7 days",
         manager.get_busy_times,
         {}),

    Tool("find_free_slot",
         "Find the next available free time slot",
         manager.find_free_slot,
         {"duration": "int (minutes, optional)"}),

    Tool("get_activity_log",
         "Get recent email activity history",
         manager.get_activity_log,
         {"limit": "int (optional, default 10)"}),
]

# Create unified agent
calendar_agent = Agent(
    name="Google Assistant",
    role="Gmail & Google Calendar Manager",
    tools=unified_tools,
    system_instructions="""You are a specialized assistant connected to Google Gmail and Google Calendar APIs.

CRITICAL INSTRUCTIONS:

1. EMAIL MANAGEMENT:
   - Use 'read_emails' to check unread emails
   - Use 'get_email_details' with the email ID to read full email content
   - Use 'send_email' to send new emails
   - Email IDs are strings, not integers!

2. CALENDAR MANAGEMENT:
   - Use 'get_calendar_events' to check upcoming events
   - Use 'schedule_event' to create new events
   - IMPORTANT: When scheduling events, start_time MUST be in ISO format with timezone
   - Example: "2025-01-05T14:00:00-05:00" (year-month-day T hour:minute:second timezone)
   - Use 'get_busy_times' to check availability

3. RESPONSE FORMAT:
   - Provide CONCISE, NATURAL LANGUAGE answers
   - Never dump raw JSON to the user
   - Parse the tool results and present them in a user-friendly way

EXAMPLES:

User: "Do I have any unread emails?"
→ read_emails(limit=5, unread_only=True)
→ Response: "Yes, you have 3 unread emails: 1) From John about Project Update, 2) From Sarah about Meeting..."

User: "What's on my calendar tomorrow?"
→ get_calendar_events(days_ahead=1)
→ Response: "You have 2 events tomorrow: 1) Team Standup at 9:00 AM, 2) Client Meeting at 2:00 PM"

User: "Schedule a meeting called 'Review' tomorrow at 2pm for 30 minutes"
→ schedule_event(title="Review", start_time="2025-01-06T14:00:00-05:00", duration=30)
→ Response: "I've scheduled 'Review' for tomorrow at 2:00 PM for 30 minutes"
"""
)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GOOGLE UNIFIED AGENT - Interactive Demo")
    print("=" * 70)

    test_requests = [
        "Do I have any unread emails?",
        "What's on my calendar for the next 3 days?",
        "Am I busy tomorrow?",
    ]

    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * 70)
        result = calendar_agent.think_and_act(request, verbose=True)
        print(f"\nAgent: {result}\n")
        calendar_agent.clear_memory()
