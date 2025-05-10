from service_announcer import ServiceAnnouncer
from peer_discovery import PeerDiscovery
from chat_initiator import ChatInitiator
from chat_responder import ChatResponder
import sys

def main():
    # Initialize components
    service_announcer = ServiceAnnouncer()
    peer_discovery = PeerDiscovery()
    chat_initiator = ChatInitiator(peer_discovery)
    chat_responder = ChatResponder()

    try:
        # Start all services
        service_announcer.start()
        peer_discovery.start()
        chat_responder.start()

        print("\nP2P Chat Application Started!")
        print("Available commands:")
        print("1. Users - View online users")
        print("2. Chat - Start a chat session")
        print("3. History - View chat history")
        print("4. Exit - Quit the application")

        while True:
            command = input("\nEnter command: ").lower()
            
            if command == "users":
                chat_initiator.display_online_users()
            elif command == "chat":
                chat_initiator.initiate_chat()
            elif command == "history":
                chat_initiator.display_chat_history()
            elif command == "exit":
                break
            else:
                print("Invalid command. Please try again.")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        service_announcer.stop()
        peer_discovery.stop()
        chat_responder.stop()
        print("Application stopped.")

if __name__ == "__main__":
    main() 