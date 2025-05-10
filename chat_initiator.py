import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
from utils import CHAT_PORT, create_json_message, parse_json_message, log_message, get_timestamp
import time

class ChatInitiator:
    def __init__(self, peer_discovery):
        self.peer_discovery = peer_discovery
        self.log_file = "chat_history.log"

    def display_online_users(self):
        """Display list of online users."""
        peers = self.peer_discovery.get_online_peers()
        if not peers:
            print("No users are currently online.")
            return

        print("\nOnline Users:")
        for ip, data in peers.items():
            if time.time() - data["last_seen"] <= 900:  # 15 minutes threshold
                status = "(Online)" if time.time() - data["last_seen"] <= 10 else "(Away)"
                print(f"{data['username']} {status}")

    def initiate_chat(self):
        """Initiate a chat session with a peer."""
        self.display_online_users()
        target_username = input("\nEnter username to chat with: ")
        target_ip = self.peer_discovery.get_peer_ip(target_username)
        
        if not target_ip:
            print(f"User {target_username} is not available.")
            return

        secure = input("Would you like to chat securely? (yes/no): ").lower() == "yes"
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_ip, CHAT_PORT))
                
                if secure:
                    # Implement Diffie-Hellman key exchange
                    p, g = 19, 2
                    private_key = int(input("Enter your private key (number): "))
                    public_key = pow(g, private_key, p)
                    
                    # Send public key
                    s.send(create_json_message("key", str(public_key)).encode())
                    
                    # Receive peer's public key
                    data = s.recv(1024).decode()
                    peer_public_key = int(parse_json_message(data)["key"])
                    
                    # Calculate shared secret
                    shared_secret = pow(peer_public_key, private_key, p)
                    key = hashlib.sha256(str(shared_secret).encode()).digest()
                    
                    # Get message from user
                    message = input("Enter your message: ")
                    
                    # Encrypt and send message
                    cipher = AES.new(key, AES.MODE_CBC)
                    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
                    encrypted_message = cipher.iv + ct_bytes
                    s.send(create_json_message("encrypted", encrypted_message.hex()).encode())
                else:
                    message = input("Enter your message: ")
                    s.send(create_json_message("unencrypted", message).encode())
                
                # Log the sent message
                log_message(self.log_file, get_timestamp(), target_username, message, "SENT")
                
        except Exception as e:
            print(f"Error initiating chat: {e}")

    def display_chat_history(self):
        """Display chat history."""
        try:
            with open(self.log_file, "r") as f:
                print("\nChat History:")
                print(f.read())
        except FileNotFoundError:
            print("No chat history available.") 