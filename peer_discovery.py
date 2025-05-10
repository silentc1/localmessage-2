import socket
import threading
import time
import json
from utils import BROADCAST_PORT, is_user_discovered

class PeerDiscovery:
    def __init__(self):
        self.peers = {}  # {ip: {"username": str, "last_seen": float}}
        self.socket = None
        self.running = False
        self.thread = None

    def start(self):
        """Start the peer discovery service."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', BROADCAST_PORT))
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()

    def _listen_loop(self):
        """Continuously listen for peer announcements."""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message and "username" in message:
                    ip = addr[0]  # Get IP from the UDP packet
                    username = message["username"]
                    
                    if ip not in self.peers:
                        print(f"{username} is online")
                    
                    self.peers[ip] = {
                        "username": username,
                        "last_seen": time.time()
                    }
            except Exception as e:
                print(f"Error in peer discovery: {e}")

    def get_online_peers(self):
        """Get list of online peers."""
        current_time = time.time()
        return {
            ip: data for ip, data in self.peers.items()
            if is_user_discovered(data["last_seen"])
        }

    def get_peer_ip(self, username):
        """Get IP address of a peer by username."""
        for ip, data in self.peers.items():
            if data["username"] == username and is_user_discovered(data["last_seen"]):
                return ip
        return None

    def stop(self):
        """Stop the peer discovery service."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join() 