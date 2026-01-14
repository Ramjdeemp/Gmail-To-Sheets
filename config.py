from dotenv import load_dotenv
import os

load_dotenv()

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

# Local state + credentials
STATE_FILE = "state.json"
CREDENTIALS_PATH = "credentials/credentials.json"  # DO NOT COMMIT

# Token files for the two different OAuth flows
GMAIL_TOKEN_PATH = "token_gmail.pickle"
SHEETS_TOKEN_PATH = "token_sheets.pickle"
