# P2P Chat Application

A peer-to-peer chat application that allows users to discover and chat with other users in the same local network.

## Features

- Automatic peer discovery in the local network
- Real-time user status (Online/Away)
- Secure chat using Diffie-Hellman key exchange and AES encryption
- Chat history logging
- Simple command-line interface

## Requirements

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - cryptography
  - pycryptodome

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. When prompted, enter your username

3. Available commands:
   - `users` - View list of online users
   - `chat` - Start a chat session with another user
   - `history` - View chat history
   - `exit` - Quit the application

## Chat Features

### Secure Chat
When initiating a chat, you can choose to use secure communication:
1. Select "yes" when asked about secure chat
2. Enter a private key (number) for Diffie-Hellman key exchange
3. Type your message
4. The message will be encrypted using AES before transmission

### Unsecure Chat
For regular chat:
1. Select "no" when asked about secure chat
2. Type your message
3. The message will be sent as plain text

## Notes

- The application uses UDP broadcast on port 6000 for peer discovery
- Chat communication uses TCP on port 6001
- User status is updated every 8 seconds
- Users are considered "Away" if no message is received for 10 seconds
- Users are removed from the list if no message is received for 15 minutes 