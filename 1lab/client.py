import socket
import os
import json
import signal
from datetime import datetime
from logger import get_logger

logger = get_logger("client")

class ProcessClient:
    def __init__(self, host="localhost", port=9000):
        
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
  
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def disconnect(self):
      
        if self.socket:
            self.socket.close()
            self.socket = None
            logger.info("Disconnected from server")

    def refresh_process_info(self, format_type="json"):
        
        try:
            command = f"update {format_type}"
            self.socket.send(command.encode())
           
            size = int(self.socket.recv(1024).decode())
            
            self.socket.send(b"ACK")
            
            received_data = b""
            while len(received_data) < size:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                received_data += chunk
            
            current_date = datetime.now().strftime("%d-%m-%Y")
            current_time = datetime.now().strftime("%H:%M:%S")
            directory = f"./{current_date}"
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            filename = f"{directory}/{current_time}.{format_type}"
            with open(filename, 'wb') as f:
                f.write(received_data)
            
            logger.info(f"Process information saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error refreshing process information: {str(e)}")
            raise

    def send_signal(self, pid, signal_name):
        
        try:
            command = f"signal {pid} {signal_name}"
            self.socket.send(command.encode())
            response = self.socket.recv(1024).decode()
            logger.info(f"Signal command response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error sending signal: {str(e)}")
            raise

def print_header():
    
    print("\n" + "="*60)
    print("║" + " "*18 + "Process Manager Client" + " "*18 + "║")
    print("="*60 + "\n")

def print_menu():
    
    print("\nAvailable Commands:")
    print("  1. Refresh Process Information")
    print("  2. Send Signal to Process")
    print("  3. Exit")
    print("\nEnter your choice (1-3): ", end="")

def handle_refresh_command(client):
   
    print("\nSelect format:")
    print("  1. JSON")
    print("  2. XML")
    choice = input("\nEnter format choice (1-2): ")
    
    format_type = "json" if choice == "1" else "xml"
    try:
        filename = client.refresh_process_info(format_type)
        print(f"\n✓ Process information saved to: {filename}")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

def handle_signal_command(client):
    
    print("\nAvailable Signals:")
    print("  1. SIGTERM (Termination request)")
    print("  2. SIGKILL (Force kill)")
    
    pid = input("\nEnter Process ID: ")
    signal_choice = input("Enter signal choice (1-2): ")
    
    signal_map = {
        "1": "SIGTERM",
        "2": "SIGKILL"
    }
    
    if signal_choice in signal_map:
        try:
            response = client.send_signal(pid, signal_map[signal_choice])
            print(f"\n✓ {response}")
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
    else:
        print("\n✗ Invalid signal choice")

def main():
    
    client = ProcessClient()
    
    try:
        client.connect()
        
        while True:
            print_header()
            print_menu()
            
            choice = input()
            
            if choice == "1":
                handle_refresh_command(client)
            elif choice == "2":
                handle_signal_command(client)
            elif choice == "3":
                print("\nExiting...")
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
