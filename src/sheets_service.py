from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
from google.auth.transport.requests import Request
from config import CREDENTIALS_PATH, SHEETS_TOKEN_PATH, SPREADSHEET_ID, SHEET_NAME

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    creds = None
    if os.path.exists(SHEETS_TOKEN_PATH):
        with open(SHEETS_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(SHEETS_TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service

def append_rows(values):
    """
    values: list of rows, each row is list of cell values
    """
    service = get_sheets_service()
    range_name = f"{SHEET_NAME}!A:D"
    body = {
        'values': values
    }
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return result
    except HttpError as err:
        # bubble up so caller can decide what to do
        raise
