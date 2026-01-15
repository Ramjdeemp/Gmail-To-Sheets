# Gmail to Google Sheets Automation

## Overview
This project is a Python automation that reads unread Gmail emails and appends their data into a Google Sheets spreadsheet. It uses OAuth 2.0 for secure authentication, handles real-world email formats, and prevents duplicate entries using persistent state tracking.

---

## 1. High-Level Architecture Diagram
```
+------------------+
|      Gmail       |
|  (Unread Emails) |
+--------+---------+
         |
         | Gmail API (OAuth 2.0)
         v
+----------------------+
|  gmail_service.py    |
|  - Authenticates     |
|  - Fetches messages  |
+----------+-----------+
           |
           v
+----------------------+
|  email_parser.py     |
|  - MIME decoding     |
|  - HTML → Text       |
+----------+-----------+
           |
           v
+----------------------+
| sheets_service.py    |
|  - Authenticates     |
|  - Appends rows      |
+----------+-----------+
           |
           v
+----------------------+
|   Google Sheets      |
| (Append-only table)  |
+----------------------+

Note: The architecture diagram is a textual representation used for clarity. The system design, logic, and implementation were done by me. 

## Control + State Management

main.py
* Orchestrates the workflow
* Uses state.json to prevent duplicates
```

---

## 2. Step-by-Step Setup Instructions

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:
```env
SPREADSHEET_ID=your_google_sheet_id
SHEET_NAME=Sheet1
```

---

### Step 3: Google Cloud Setup

1. Create a Google Cloud project
2. Enable the following APIs:
   * Gmail API
   * Google Sheets API
3. Configure OAuth Consent Screen:
   * Audience: External
   * Add your Gmail account as a **test user**
4. Create OAuth Client:
   * Application type: Desktop App
5. Download OAuth credentials and place them at:
```
credentials/credentials.json
```

---

### Step 4: Run the Script

From the project root directory:
```bash
py -m src.main
```

**First run:**
* Browser opens for OAuth consent
* Tokens are stored locally

**Subsequent runs:**
* No browser interaction required
* Only new unread emails are processed

---

## 3. Core Explanations

### OAuth Flow Used

This project uses Google OAuth 2.0 **Installed App Flow** via `InstalledAppFlow.run_local_server()`.

* User authorizes access in the browser
* Google redirects to a local callback server
* Access and refresh tokens are stored locally
* Tokens are reused and refreshed automatically

This avoids storing passwords and follows Google-recommended security practices.

---

### Duplicate Prevention Logic

Each Gmail email has a unique `messageId`.

* After processing an email, its `messageId` is stored in `state.json`
* Before processing, the script checks whether the ID already exists
* If found, the email is skipped

This ensures:
* No duplicate rows
* Safe re-runs
* Crash-resilient execution

This design makes the script **idempotent**.

---

### State Persistence Method

State is persisted using a local JSON file (`state.json`):

* Stores processed Gmail message IDs
* Lightweight and portable
* Suitable for single-user automation

If scaled to multiple users or machines, this could be replaced with a database.

---

## 4. Challenge Faced and Solution

### Challenge: OAuth Flow Blocking Execution

During development, the script sometimes appeared to hang due to OAuth flows waiting indefinitely for browser authorization callbacks.

**Solution:**
* Correctly configured OAuth consent screen
* Added the Gmail account as a test user
* Cleared stale token files and re-authorized
* Verified both Gmail and Sheets OAuth flows independently

This ensured stable authentication behavior across runs.

---

## 5. Limitations of the Solution

* Designed for a single Gmail account
* Uses local JSON state (not suitable for distributed execution)
* Poll-based execution (manual or scheduled)
* Google Sheets is used for reporting, not as a database
* No real-time push notifications from Gmail

These tradeoffs were intentional given the scope of the assignment.

---

## Conclusion

This project demonstrates secure OAuth integration, real-world API handling, stateful automation, and safe re-runnable design using Python and Google APIs.
