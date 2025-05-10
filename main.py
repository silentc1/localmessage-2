from service_announcer import ServiceAnnouncer
from peer_discovery import PeerDiscovery
from chat_initiator import ChatInitiator
from chat_responder import ChatResponder
from colorama import init, Fore, Back, Style
import sys
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*50}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'P2P Chat Application':^50}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}\n")

def print_menu():
    """Print the main menu."""
    print(f"\n{Fore.GREEN}Available Commands:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} {Fore.WHITE}Users{Style.RESET_ALL} - View online users")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} {Fore.WHITE}Chat{Style.RESET_ALL} - Start a chat session")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} {Fore.WHITE}History{Style.RESET_ALL} - View chat history")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} {Fore.WHITE}Exit{Style.RESET_ALL} - Quit the application")
    print(f"\n{Fore.CYAN}Enter command number or name:{Style.RESET_ALL} ", end="")

def main():
    # Initialize colorama
    init()
    
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

        clear_screen()
        print_header()
        print(f"{Fore.GREEN}Application started successfully!{Style.RESET_ALL}")

        while True:
            print_menu()
            command = input().lower().strip()
            
            if command in ['1', 'users']:
                clear_screen()
                print_header()
                chat_initiator.display_online_users()
            elif command in ['2', 'chat']:
                clear_screen()
                print_header()
                chat_initiator.initiate_chat()
            elif command in ['3', 'history']:
                clear_screen()
                print_header()
                chat_initiator.display_chat_history()
            elif command in ['4', 'exit']:
                print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
                break
            else:
                print(f"\n{Fore.RED}Invalid command. Please try again.{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
    finally:
        # Cleanup
        service_announcer.stop()
        peer_discovery.stop()
        chat_responder.stop()
        print(f"{Fore.GREEN}Application stopped.{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 