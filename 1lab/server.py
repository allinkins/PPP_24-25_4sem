import socket
import json
import threading
from process_manager import ProcessManager
from logger import get_logger

logger = get_logger("server")

class ProcessServer:
    def __init__(self, host="0.0.0.0", port=9000):
        
        self.host = host
        self.port = port
        self.process_manager = ProcessManager()
        self.server_socket = None

    def start(self):
      
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            while True:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
                
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            self.stop()
            raise

    def stop(self):
        
        if self.server_socket:
            self.server_socket.close()
            logger.info("Server stopped")

    def handle_client(self, client_socket, address):
       
        try:
            while True:
                
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                logger.info(f"Received command from {address}: {data}")
                              
                command_parts = data.strip().split()
                command = command_parts[0].lower()
                
                response = None
                
                if command == "update":
                   
                    format_type = command_parts[1] if len(command_parts) > 1 else "json"
                    filename = self.process_manager.save_process_info(format_type)
                    
                    
                    with open(filename, 'rb') as f:
                        file_content = f.read()                   
                  
                    size_info = str(len(file_content)).encode()
                    client_socket.send(size_info)
                                      
                    client_socket.recv(1024)                    
                   
                    client_socket.send(file_content)
                    logger.info(f"Sent updated process information to {address}")
                    
                elif command == "signal":
                   
                    if len(command_parts) != 3:
                        response = "Error: Invalid signal command format. Use: signal <pid> <signal_name>"
                    else:
                        try:
                            pid = command_parts[1]
                            signal_name = command_parts[2].upper()
                            response = self.process_manager.send_signal_to_process(pid, signal_name)
                        except Exception as e:
                            response = f"Error: {str(e)}"
                    
                   
                    client_socket.send(response.encode())
                    
                else:
                    response = f"Error: Unknown command '{command}'"
                    client_socket.send(response.encode())
                
        except Exception as e:
            logger.error(f"Error handling client {address}: {str(e)}")
        finally:
            client_socket.close()
            logger.info(f"Connection closed with {address}")

def main():
   
    server = ProcessServer()
    try:
        logger.info("Starting process information server...")
        server.start()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        server.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        server.stop()

if __name__ == "__main__":
    main()
