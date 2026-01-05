"""
Google Authentication Module - Handles OAuth 2.0 flow for Google APIs.
"""
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
# calendar - full calendar access (includes events, freebusy, settings)
# gmail.readonly - read emails
# gmail.send - send emails
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_google_service(api_name: str, api_version: str):
    """
    Handles the authentication flow and returns a connected Google API service object.
    Requires 'credentials.json' in the same directory.
    """
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                print(f"\n--- Starting Google OAuth Flow for {api_name} ---")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                # Ensure we run this only once, the credentials object holds scopes for both
                creds = flow.run_local_server(port=0)
                print("--- OAuth Flow Complete ---")
            except FileNotFoundError:
                raise Exception("Missing 'credentials.json'. Please follow the setup steps.")
            except Exception as e:
                raise Exception(f"OAuth flow failed: {e}")

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build(api_name, api_version, credentials=creds)
    return service

if __name__ == '__main__':
    # Simple test to ensure authentication works
    try:
        # This will trigger the OAuth flow if token.json doesn't exist
        calendar_service = get_google_service('calendar', 'v3')
        print(f"Successfully connected to Google Calendar API: {calendar_service.__dict__.get('_baseUrl')}")
        
        gmail_service = get_google_service('gmail', 'v1')
        print(f"Successfully connected to Gmail API: {gmail_service.__dict__.get('_baseUrl')}")
    except FileNotFoundError as e:
        print(f"ERROR: Missing authentication file. Make sure 'credentials.json' is in the root directory. Details: {e}")
    except Exception as e:
        print(f"An error occurred during authentication: {e}")