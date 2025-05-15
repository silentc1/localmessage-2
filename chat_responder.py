import socket
import threading
import json
import pyDes
import base64
from colorama import Fore, Style
from utils import CHAT_PORT, log_message, get_timestamp

class ChatResponder:
    def __init__(self):
        self.socket = None
        self.running = False
        self.thread = None
        self.log_file = "chat_history.log"

    def start(self):
        """Start the chat responder service."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', CHAT_PORT))
        self.socket.listen(5)
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"{Fore.GREEN}Chat responder started on port {CHAT_PORT}{Style.RESET_ALL}")

    def _handle_connection(self, conn, addr):
        """Handle an incoming connection."""
        try:
            data = conn.recv(1024).decode()
            message = json.loads(data)
            
            if not message:
                return
            
            if "encryptedmessage" in message:
                print(f"\n{Fore.CYAN}Incoming secure chat request from {addr[0]}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Enter your encryption key (will be padded to 24 bytes):{Style.RESET_ALL} ", end="")
                encryption_key = input()
                
                print(f"{Fore.GREEN}Secure connection established with {addr[0]}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Waiting for messages...{Style.RESET_ALL}")
                
                # Keep TCP session open and handle multiple messages
                while True:
                    try:
                        # Wait for encrypted message
                        data = conn.recv(1024).decode()
                        if not data:
                            break
                            
                        message = json.loads(data)
                        
                        if "encryptedmessage" in message:
                            # Decrypt message
                            b64_encoded = message["encryptedmessage"]
                            encoded_msg = base64.b64decode(b64_encoded)
                            decrypted_message = pyDes.triple_des(encryption_key.ljust(24)).decrypt(encoded_msg, padmode=2).decode()
                            print(f"\n{Fore.GREEN}Received encrypted message from {addr[0]}:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Message: {decrypted_message}{Style.RESET_ALL}")
                            log_message(self.log_file, get_timestamp(), addr[0], decrypted_message, "RECEIVED")
                    except Exception as e:
                        print(f"{Fore.RED}Error receiving message: {e}{Style.RESET_ALL}")
                        break
            
            elif "unencryptedmessage" in message:
                print(f"\n{Fore.YELLOW}Received message from {addr[0]}:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Message: {message['unencryptedmessage']}{Style.RESET_ALL}")
                log_message(self.log_file, get_timestamp(), addr[0], message["unencryptedmessage"], "RECEIVED")
                
        except Exception as e:
            print(f"{Fore.RED}Error handling connection: {e}{Style.RESET_ALL}")
        finally:
            conn.close()

    def _listen_loop(self):
        """Continuously listen for incoming connections."""
        while self.running:
            try:
                conn, addr = self.socket.accept()
                threading.Thread(target=self._handle_connection, args=(conn, addr)).start()
            except Exception as e:
                if self.running:
                    print(f"{Fore.RED}Error accepting connection: {e}{Style.RESET_ALL}")

    def stop(self):
        """Stop the chat responder service."""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join() 