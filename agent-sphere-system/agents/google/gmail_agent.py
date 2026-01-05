"""
Gmail Agent - Manage and read emails using Google's Gmail API
"""
import json
import logging
import os
# Assuming base.agent_framework is available
from base.agent_framework import Agent, Tool 
from agents.google.google_auth import get_google_service
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

class GmailManager:
    """Manages email interactions via the Gmail API."""
    def __init__(self):
        # NOTE: This call will trigger the OAuth flow if 'token.json' is missing
        self.service = get_google_service('gmail', 'v1')
        self.user_id = 'me' 

    def _get_message_body(self, message) -> str:
        """Utility to decode the email body from its payload parts."""
        payload = message.get('payload')
        parts = payload.get('parts', [])
        
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return urlsafe_b64decode(data).decode('utf-8')
                    
        return "No easily readable text body content found."


    def get_unread_emails(self, limit: int = 5) -> list:
        """Fetch the latest unread emails from Gmail."""
        response = self.service.users().messages().list(
            userId=self.user_id,
            labelIds=['UNREAD'],
            maxResults=limit
        ).execute()
        
        messages = response.get('messages', [])
        if not messages:
            return "No unread emails found."
        
        unread_list = []
        for msg in messages:
            msg_data = self.service.users().messages().get(
                userId=self.user_id, id=msg['id'], format='metadata'
            ).execute()
            
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            unread_list.append({
                "id": msg['id'],
                "from": sender,
                "subject": subject,
                "snippet": msg_data['snippet'],
                "date": date
            })
            
        return unread_list
        

    def read_email(self, email_id: str) -> str:
        """Fetch the full content of a specific email by its ID and mark it as read."""
        # 1. Fetch the full message
        message = self.service.users().messages().get(
            userId=self.user_id,
            id=email_id,
            format='full'
        ).execute()

        # 2. Extract details
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        body = self._get_message_body(message)

        # 3. Mark as read (Remove 'UNREAD' label)
        self.service.users().messages().modify(
            userId=self.user_id,
            id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return f"Subject: {subject}\nFrom: {sender}\n---\nBody:\n{body[:500]}..." 

    def send_email(self, recipient: str, subject: str, body: str) -> str:
        """
        Draft and send an email via Gmail using MIME and Base64 encoding.
        Requires 'https://www.googleapis.com/auth/gmail.send' scope.
        """
        try:
            # 1. Create the MIME message
            message = MIMEText(body)
            message['to'] = recipient
            message['from'] = self.user_id # 'me' resolves to the authenticated user's email
            message['subject'] = subject

            # 2. Encode the message into a base64urlsafe string
            raw_message = urlsafe_b64encode(message.as_bytes()).decode()

            # 3. Send the message via the API
            send_message = (
                self.service.users()
                .messages()
                .send(userId=self.user_id, body={'raw': raw_message})
                .execute()
            )
            
            return f"Email successfully sent to {recipient}. Message ID: {send_message['id']}"

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return f"ERROR: Failed to send email. Check recipient address and ensure you have the 'gmail.send' scope authorized. Details: {e}"        
    
    def get_activity_log(self, limit: int = 10) -> list:
        """Get the recent email activity history (last N messages received)."""
        response = self.service.users().messages().list(
            userId=self.user_id,
            maxResults=limit
        ).execute()
        
        messages = response.get('messages', [])
        if not messages:
            return "No recent emails found."
            
        return [f"Message ID: {msg['id']}" for msg in messages]

# --- AGENT INITIALIZATION ---

try:
    gmail_manager = GmailManager()
except Exception as e:
    logger.error(f"Failed to initialize GmailManager: {e}")
    class DummyManager:
        def __init__(self): pass
        def get_unread_emails(self, limit: int = 5): return f"ERROR: Gmail API setup failed. {e}"
        def read_email(self, email_id: str): return f"ERROR: Gmail API setup failed. {e}"
        def send_email(self, *args): return "Tool Disabled: Authentication Error."
        def get_activity_log(self, *args): return f"ERROR: Gmail API setup failed. {e}"
    
    gmail_manager = DummyManager()


# Define Tools
gmail_tools = [
    Tool("get_unread_emails", 
         "Retrieve a list of unread emails from Gmail", 
         gmail_manager.get_unread_emails, 
         {"limit": "int (optional, max number of emails)"}),
    
    Tool("read_email", 
         "Fetch the body of a specific email by its string ID and mark it as read", 
         gmail_manager.read_email, 
         {"email_id": "str (required, the ID of the email)"}),
    
    Tool("send_email", 
         "Send a new email to a recipient (currently disabled/placeholder)", 
         gmail_manager.send_email, 
         {"recipient": "str (required, email address)", 
          "subject": "str (required)", 
          "body": "str (required)"}),
    
    Tool("get_activity_log", 
         "Get the recent email activity history (last 10 received messages)", 
         gmail_manager.get_activity_log, 
         {"limit": "int (optional)"}),
]

# Create agent
gmail_agent = Agent(
    name="Gmail Assistant",
    role="Gmail & Email Manager",
    tools=gmail_tools,
   system_instructions="You are a specialized email management assistant connected to the live Gmail API. Help users READ, SEND, and manage emails. Use 'get_unread_emails' or 'send_email' as needed."
)

if __name__ == "__main__":
    # Test gmail agent
    print("\n" + "=" * 70)
    print("GMAIL AGENT - Interactive Demo")
    print("=" * 70)
    
    # test_requests = [
    #     "Show me my 3 latest unread emails",
    #     # NOTE: You must manually replace the ID below with a real, unread ID from the tool output!
    #     # "Read the email with ID <REPLACE_WITH_REAL_ID_HERE>", 
    #     "What are my most recent email activities?",
    #     "Can you send an email to m_intu@yahoo.com about a test?"
    # ]
    
    from datetime import datetime
    test_requests = [
        "Show me my 1 latest unread email",
        f"Send an email to m_intu@yahoo.com with the subject 'Agent Test' and the body 'This is a test message from the new Gmail Agent, sent at {datetime.now()}.'",
        "What are my most recent email activities?",
    ]
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * (len(request) + 6))
        # CORRECTED to use think_and_act
        response = gmail_agent.think_and_act(request, verbose=False)
        print(f"\nAgent: {response}")