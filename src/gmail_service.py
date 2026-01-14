from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import base64
from config import CREDENTIALS_PATH, GMAIL_TOKEN_PATH  # <-- correct import

# scopes: modify so we can mark read
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists(GMAIL_TOKEN_PATH):
        with open(GMAIL_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GMAIL_TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_unread_messages(service, max_results=100):
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX','UNREAD'],
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    return [m['id'] for m in messages]

def get_message(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    return msg

def mark_as_read(service, msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
