"""
Google Calendar Agent - Manage calendar events and scheduling using the Google Calendar API
"""
import json
import logging
from base.agent_framework import Agent, Tool
from agents.google.google_auth import get_google_service
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class GoogleCalendarManager:
    """Manages calendar events via the Google Calendar API."""
    def __init__(self):
        # NOTE: This call will trigger the OAuth flow if 'token.json' is missing
        self.service = get_google_service('calendar', 'v3')
        self.calendar_id = 'primary'

    def get_events(self, days: int = 3) -> list:
        """Fetch calendar events for the next specified number of days."""
        now = datetime.now(pytz.utc).isoformat()
        time_max = (datetime.now(pytz.utc) + timedelta(days=days)).isoformat()

        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No upcoming events found in the next {days} days."
        
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            output.append({
                "id": event['id'],
                "summary": event.get('summary', 'No Title'),
                "start": start,
                "end": end,
            })
        
        return output
        

    def schedule_event(self, summary: str, start_time: str, duration: int) -> str:
        """Schedule a new event on the calendar."""
        try:
            # Check if start_time is timezone-aware
            if not any(tz_info in start_time for tz_info in ['+', '-']):
                 raise ValueError("Start time is not timezone-aware.")
            
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(minutes=duration)
            
            event_body = {
                'summary': summary,
                'start': {'dateTime': start_dt.isoformat()},
                'end': {'dateTime': end_dt.isoformat()},
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event_body
            ).execute()
            
            return f"Event '{event.get('summary')}' successfully scheduled. Start time: {event['start'].get('dateTime')}."
            
        except ValueError as e:
            return f"Error: {e}. Start time MUST be a full ISO format string (e.g., 2025-10-26T16:00:00-04:00) with a timezone."
        except Exception as e:
            return f"Error scheduling event: {e}"


    def get_busy_times(self) -> list:
        """Get all scheduled (busy) time slots in the next 7 days."""
        now = datetime.now(pytz.utc)
        time_max = (now + timedelta(days=7)).isoformat()
        
        body = {
            "timeMin": now.isoformat(),
            "timeMax": time_max,
            "items": [{"id": self.calendar_id}]
        }
        
        response = self.service.freebusy().query(body=body).execute()
        
        busy = response['calendars'][self.calendar_id]['busy']
        
        if not busy:
            return "You are completely free for the next 7 days!"
            
        return busy

    def find_free_slot(self, duration: int = 60) -> str:
        """Find the next available free time slot of a given duration."""
        return "Tool Not Implemented: Use 'get_busy_times' and check the schedule yourself. Automatic free slot detection is not yet built."


# --- AGENT INITIALIZATION ---

try:
    calendar_manager = GoogleCalendarManager()
except Exception as e:
    logger.error(f"Failed to initialize GoogleCalendarManager: {e}")
    _cal_init_error = str(e)  # capture before 'e' is deleted by Python 3 scoping rules
    class DummyManager:
        def __init__(self): pass
        def get_events(self, days: int = 3): return f"ERROR: Calendar API setup failed. {_cal_init_error}"
        def schedule_event(self, *args): return f"ERROR: Calendar API setup failed. {_cal_init_error}"
        def get_busy_times(self): return f"ERROR: Calendar API setup failed. {_cal_init_error}"
        def find_free_slot(self, *args): return "Tool Disabled: Authentication Error."

    calendar_manager = DummyManager()


# Define Tools
calendar_tools = [
    Tool("get_events", 
         "Get all scheduled events from Google Calendar for the next N days. Defaults to 3 days.", 
         calendar_manager.get_events, 
         {"days": "int (optional, number of days to look ahead)"}),
    
    Tool("schedule_event", 
         "Schedule a new event on Google Calendar. Start time MUST be a full ISO format string (e.g., 2025-10-26T16:00:00-04:00) with a timezone.", 
         calendar_manager.schedule_event, 
         {"summary": "str (required)", 
          "start_time": "str (required, ISO format with timezone)", 
          "duration": "int (required, minutes)"}),
    
    Tool("get_busy_times", 
         "Get all scheduled (busy) time slots in the next 7 days to check for availability.", 
         calendar_manager.get_busy_times, 
         {}),
    
    Tool("find_free_slot", 
         "Find the next available free time slot of a given duration.", 
         calendar_manager.find_free_slot, 
         {"duration": "int (minutes, optional)"}),
]

# Create agent
calendar_agent = Agent(
    name="Calendar Assistant",
    role="Google Calendar Manager",
    tools=calendar_tools,
    system_instructions="You are a specialized Google Calendar management assistant connected to the live API. Help users schedule events and check their availability. For scheduling, you must get the summary, a timezone-aware ISO format start time, and a duration in minutes. Use 'get_busy_times' to check for availability."
)


if __name__ == "__main__":
    # Test calendar agent
    print("\n" + "=" * 70)
    print("CALENDAR AGENT - Interactive Demo")
    print("=" * 70)
    
    # NOTE: You must use a current, timezone-aware ISO format string for scheduling!
    tomorrow_morning = "2025-10-27T10:00:00-04:00" 
    
    test_requests = [
        "What's on my calendar for the next 2 days?",
        f"Schedule a 45-minute meeting called 'Sprint Planning' starting at {tomorrow_morning}",
        "Am I busy tomorrow afternoon?",
    ]
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * (len(request) + 6))
        # CORRECTED to use think_and_act
        response = calendar_agent.think_and_act(request, verbose=True)
        print(f"\nAgent: {response}")