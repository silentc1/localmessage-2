import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import time
from colorama import Fore, Style
from utils import CHAT_PORT, create_json_message, parse_json_message, log_message, get_timestamp

class ChatInitiator:
    def __init__(self, peer_discovery):
        self.peer_discovery = peer_discovery
        self.log_file = "chat_history.log"

    def display_online_users(self):
        """Display list of online users."""
        peers = self.peer_discovery.get_online_peers()
        if not peers:
            print(f"{Fore.YELLOW}No users are currently online.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}Online Users:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'Username':<20} {'Status':<10}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*30}{Style.RESET_ALL}")
        
        for ip, data in peers.items():
            if time.time() - data["last_seen"] <= 900:  # 15 minutes threshold
                status = f"{Fore.GREEN}(Online){Style.RESET_ALL}" if time.time() - data["last_seen"] <= 10 else f"{Fore.YELLOW}(Away){Style.RESET_ALL}"
                print(f"{data['username']:<20} {status}")

    def initiate_chat(self):
        """Initiate a chat session with a peer."""
        self.display_online_users()
        print(f"\n{Fore.CYAN}Enter username to chat with:{Style.RESET_ALL} ", end="")
        target_username = input()
        target_ip = self.peer_discovery.get_peer_ip(target_username)
        
        if not target_ip:
            print(f"{Fore.RED}User {target_username} is not available.{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Would you like to chat securely? (yes/no):{Style.RESET_ALL} ", end="")
        secure = input().lower() == "yes"
        
        try:
            if secure:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((target_ip, CHAT_PORT))
                    
                    print(f"\n{Fore.GREEN}Initiating secure chat session...{Style.RESET_ALL}")
                    # Implement Diffie-Hellman key exchange
                    p, g = 19, 2
                    print(f"{Fore.CYAN}Enter your private key (number):{Style.RESET_ALL} ", end="")
                    private_key = int(input())
                    public_key = pow(g, private_key, p)
                    
                    # Send first number in exact required format
                    s.send(json.dumps({"key": str(public_key)}).encode())
                    
                    # Receive peer's public key
                    data = s.recv(1024).decode()
                    peer_public_key = int(json.loads(data)["key"])
                    
                    # Calculate shared secret
                    shared_secret = pow(peer_public_key, private_key, p)
                    key = hashlib.sha256(str(shared_secret).encode()).digest()
                    
                    print(f"\n{Fore.GREEN}Secure connection established!{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Type your message and press Enter to send.{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Type 'exit' to end the chat session.{Style.RESET_ALL}")
                    
                    # Keep TCP session open and allow continuous message exchange
                    while True:
                        message = input()
                        
                        if message.lower() == 'exit':
                            break
                            
                        # Encrypt and send message in exact required format
                        cipher = AES.new(key, AES.MODE_CBC)
                        ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
                        encrypted_message = cipher.iv + ct_bytes
                        s.send(json.dumps({"encryptedmessage": encrypted_message.hex()}).encode())
                        
                        # Log the sent message
                        log_message(self.log_file, get_timestamp(), target_username, message, "SENT")
                        print(f"{Fore.GREEN}Message sent successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Initiating unsecure chat session...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Type your message and press Enter to send.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Type 'exit' to end the chat session.{Style.RESET_ALL}")
                
                while True:
                    message = input()
                    
                    if message.lower() == 'exit':
                        break
                    
                    # Create new TCP connection for each message
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            s.connect((target_ip, CHAT_PORT))
                            s.send(json.dumps({"unencryptedmessage": message}).encode())
                            log_message(self.log_file, get_timestamp(), target_username, message, "SENT")
                            print(f"{Fore.GREEN}Message sent successfully!{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}Error sending message: {e}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error initiating chat: {e}{Style.RESET_ALL}")

    def display_chat_history(self):
        """Display chat history."""
        try:
            with open(self.log_file, "r") as f:
                print(f"\n{Fore.GREEN}Chat History:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'Timestamp':<20} {'Username':<15} {'Message':<30} {'Direction':<10}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'-'*75}{Style.RESET_ALL}")
                for line in f:
                    timestamp, username, message, direction = line.strip().split(" | ")
                    direction_color = Fore.GREEN if direction == "SENT" else Fore.YELLOW
                    print(f"{timestamp:<20} {username:<15} {message:<30} {direction_color}{direction}{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.YELLOW}No chat history available.{Style.RESET_ALL}") 