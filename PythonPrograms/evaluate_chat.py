import time
import threading
import ollama
import os

# Function to read the content from a file
def read_input_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to get a response from the llama3 model
def get_response_from_llama3(input_text):
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': input_text}])
    return response['message']['content']

# Function to process the chat file
def process_chat_file(input_file_path, guidance_file_path, output_file_path):
    # Read the guidance message from the file
    guidance_message = read_input_file(guidance_file_path)

    # Read the input from the file
    input_text = read_input_file(input_file_path)

    # Prepend the guidance message to the input text
    combined_text = f"{guidance_message}\n{input_text}"

    # Get the response from the llama3 model
    response = get_response_from_llama3(combined_text)

    # Save the response to an external file
    with open(output_file_path, 'w') as file:
        file.write(response)

    print(f"Response has been written to {output_file_path}")

# Background thread function to check for file updates
def monitor_file(input_file_path, guidance_file_path, output_file_path, interval=6):
    last_modified_time = 0
    while True:
        current_modified_time = os.path.getmtime(input_file_path)
        if current_modified_time != last_modified_time:
            print(f"{input_file_path} has been modified.")
            process_chat_file(input_file_path, guidance_file_path, output_file_path)
            last_modified_time = current_modified_time
        time.sleep(interval)

def main():
    # Paths to the input files
    input_file_path = '../TextFiles/patient-therapist-chat.txt'
    guidance_file_path = '../TextFiles/ai-prompt.txt'
    output_file_path = '../TextFiles/mqtt-message.txt'

    # Start the background thread to monitor the file
    monitor_thread = threading.Thread(target=monitor_file, args=(input_file_path, guidance_file_path, output_file_path))
    monitor_thread.daemon = True
    monitor_thread.start()

    print(f"Monitoring {input_file_path} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the monitor.")
        # Stop the thread gracefully if needed (not strictly necessary with daemon threads)

if __name__ == '__main__':
    main()

