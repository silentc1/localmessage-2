import json
import time
from datetime import datetime
import os

# Constants
BROADCAST_IP = "192.168.1.255"
BROADCAST_PORT = 6000
CHAT_PORT = 6001
BROADCAST_INTERVAL = 8  # seconds
ONLINE_THRESHOLD = 10  # seconds
DISCOVERY_THRESHOLD = 900  # 15 minutes

def create_json_message(message_type, content):
    """Create a JSON message with the specified type and content."""
    if message_type == "presence":
        return json.dumps({"username": content})
    elif message_type == "key":
        return json.dumps({"key": content})
    elif message_type == "encrypted":
        return json.dumps({"encryptedmessage": content})
    elif message_type == "unencrypted":
        return json.dumps({"unencryptedmessage": content})
    return None

def parse_json_message(message):
    """Parse a JSON message and return its contents."""
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return None

def log_message(log_file, timestamp, username, message, direction):
    """Log a message to the chat history file."""
    with open(log_file, "a") as f:
        f.write(f"{timestamp} | {username} | {message} | {direction}\n")

def get_timestamp():
    """Get current timestamp in a readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_user_online(last_seen):
    """Check if a user is online based on their last seen timestamp."""
    return (time.time() - last_seen) <= ONLINE_THRESHOLD

def is_user_discovered(last_seen):
    """Check if a user is within the discovery threshold."""
    return (time.time() - last_seen) <= DISCOVERY_THRESHOLD 