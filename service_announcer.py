import socket
import time
import threading
import json
from utils import BROADCAST_IP, BROADCAST_PORT, BROADCAST_INTERVAL

class ServiceAnnouncer:
    def __init__(self):
        self.username = None
        self.socket = None
        self.running = False
        self.thread = None

    def start(self):
        """Start the service announcer."""
        if not self.username:
            self.username = input("Please enter your username: ")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.running = True
        self.thread = threading.Thread(target=self._broadcast_loop)
        self.thread.daemon = True
        self.thread.start()

    def _broadcast_loop(self):
        """Continuously broadcast presence in the network."""
        while self.running:
            try:
                # Create message with exactly the required format
                message = json.dumps({"username": self.username})
                self.socket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))
                time.sleep(BROADCAST_INTERVAL)
            except Exception as e:
                print(f"Error broadcasting presence: {e}")
                time.sleep(1)

    def stop(self):
        """Stop the service announcer."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join() 