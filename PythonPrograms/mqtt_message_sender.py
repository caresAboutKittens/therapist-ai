import time
import threading
import os
import paho.mqtt.client as mqtt

def format_message(summary):
    return f"""
Patient may be in a critical mental condition. Immediate professional help may be advised.

Summary of discussion had with Patient:
-
{summary}
-
"""

def scan_for_threat(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        if '##@@## THREAT ##@@##' in content:
            summary_start = content.find('--') + 2
            summary = content[summary_start:].strip()
            final_message = format_message(summary)
            print(final_message)

            # MQTT part (commented out for now)
            # client = mqtt.Client()
            # client.connect("mqtt_broker_address", 1883, 60)
            # client.publish("threat/topic", final_message)
            # client.disconnect()

        else:
            print('All good.')

    except FileNotFoundError:
        print(f"The file at path {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Background thread function to check for file updates
def monitor_file(file_path, interval=5):
    last_modified_time = 0
    while True:
        current_modified_time = os.path.getmtime(file_path)
        if current_modified_time != last_modified_time:
            print(f"{file_path} has been modified.")
            scan_for_threat(file_path)
            last_modified_time = current_modified_time
        time.sleep(interval)

if __name__ == "__main__":
    file_path = '../TextFiles/mqtt-message.txt'

    # Start the background thread to monitor the file
    monitor_thread = threading.Thread(target=monitor_file, args=(file_path,))
    monitor_thread.daemon = True
    monitor_thread.start()

    print(f"Monitoring {file_path} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the monitor.")
        # Stop the thread gracefully if needed (not strictly necessary with daemon threads)

