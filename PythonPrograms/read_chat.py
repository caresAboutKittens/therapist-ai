import sqlite3
import json
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path to the database file
db_path = '/var/lib/docker/volumes/open-webui/_data/webui.db'
# Path to the output text file
output_file_path = '../TextFiles/patient-therapist-chat.txt'

def fetch_latest_chat_data():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch the latest chat data based on created_at
    cursor.execute("SELECT chat FROM chat ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()

    # Close the connection
    conn.close()

    return row

def parse_chat_data(row):
    if not row:
        return []

    chat_json = row[0]
    chat_data = json.loads(chat_json)
    messages = chat_data.get('messages', [])
    last_messages = messages[-8:]  # Get only the last 4 interactions
    conversation = [(msg['role'], msg['content']) for msg in last_messages]
    return conversation

def write_conversation_to_file(conversation):
    with open(output_file_path, 'w') as f:
        for role, message in conversation:
            role_label = "Patient" if role == "user" else "Therapist"
            f.write(f"{role_label}:\n{message}\n\n")

def process_new_chat():
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    row = fetch_latest_chat_data()
    conversation = parse_chat_data(row)
    write_conversation_to_file(conversation)

class DatabaseChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == db_path:
            process_new_chat()

if __name__ == "__main__":
    # Initial processing
    process_new_chat()

    # Set up the file system watcher
    event_handler = DatabaseChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(db_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

