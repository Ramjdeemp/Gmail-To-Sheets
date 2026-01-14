import os
import json
import sys
from config import STATE_FILE
from src.gmail_service import get_gmail_service, fetch_unread_messages, get_message, mark_as_read
from src.email_parser import parse_message
from src.sheets_service import append_rows

def load_state():
    if not os.path.exists(STATE_FILE):
        return {'processed_ids': []}
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def main():
    service = get_gmail_service()
    message_ids = fetch_unread_messages(service)
    if not message_ids:
        print("No unread messages found.")
        return

    state = load_state()
    processed = set(state.get('processed_ids', []))
    rows_to_append = []
    newly_processed = []

    for msg_id in message_ids:
        if msg_id in processed:
            print(f"Skipping already-processed message: {msg_id}")
            continue
        raw = get_message(service, msg_id)
        parsed = parse_message(raw)
        # prepare row [From, Subject, Date, Content]
        rows_to_append.append([parsed['from'], parsed['subject'], parsed['date'], parsed['body']])
        newly_processed.append(msg_id)

    if rows_to_append:
        append_rows(rows_to_append)
        # mark as read only after successful append
        for msg_id in newly_processed:
            try:
                mark_as_read(service, msg_id)
            except Exception as e:
                print(f"Failed to mark {msg_id} as read: {e}")

        # update and save state
        processed.update(newly_processed)
        state['processed_ids'] = list(processed)
        save_state(state)
        print(f"Appended {len(rows_to_append)} rows and updated state.")
    else:
        print("No new rows to append.")

if __name__ == "__main__":
    main()
