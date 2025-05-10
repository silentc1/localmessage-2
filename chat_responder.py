import socket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
from colorama import Fore, Style
from utils import CHAT_PORT, parse_json_message, log_message, get_timestamp, create_json_message

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
            message = parse_json_message(data)
            
            if not message:
                return
            
            if "key" in message:
                print(f"\n{Fore.CYAN}Incoming secure chat request from {addr[0]}{Style.RESET_ALL}")
                # Handle Diffie-Hellman key exchange
                p, g = 19, 2
                private_key = 7  # Fixed private key for simplicity
                public_key = pow(g, private_key, p)
                
                # Send our public key
                conn.send(create_json_message("key", str(public_key)).encode())
                
                # Calculate shared secret
                peer_public_key = int(message["key"])
                shared_secret = pow(peer_public_key, private_key, p)
                key = hashlib.sha256(str(shared_secret).encode()).digest()
                
                # Wait for encrypted message
                data = conn.recv(1024).decode()
                message = parse_json_message(data)
                
                if "encryptedmessage" in message:
                    # Decrypt message
                    encrypted_data = bytes.fromhex(message["encryptedmessage"])
                    iv = encrypted_data[:16]
                    ct = encrypted_data[16:]
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted_message = unpad(cipher.decrypt(ct), AES.block_size).decode()
                    print(f"\n{Fore.GREEN}Received encrypted message from {addr[0]}:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Message: {decrypted_message}{Style.RESET_ALL}")
                    log_message(self.log_file, get_timestamp(), addr[0], decrypted_message, "RECEIVED")
            
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