import socket
import threading
import select

# Configuration
LOAD_BALANCER_HOST = '0.0.0.0'
LOAD_BALANCER_PORT = 8080

# The "Backend Nodes" we are balancing traffic between
# (In a real scenario, these would be your local Flask/Django apps on ports 5000, 5001)
# For this demo, we can just point to external IPs or local ports.
SERVER_POOL = [
    ('www.google.com', 80),
    ('www.example.com', 80)
]

# Round Robin Index
current_server_index = 0
index_lock = threading.Lock()

def get_next_server():
    """Selects the next backend server using Round-Robin algorithm."""
    global current_server_index
    with index_lock:
        server = SERVER_POOL[current_server_index]
        current_server_index = (current_server_index + 1) % len(SERVER_POOL)
    return server

def handle_client(client_socket):
    """Forwards client request to the selected backend server."""
    backend_host, backend_port = get_next_server()
    
    try:
        # Connect to the backend server
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect((backend_host, backend_port))
        
        # Bridge the two connections (Client <-> LB <-> Backend)
        # using 'select' to handle bidirectional data flow
        sockets = [client_socket, backend_socket]
        
        while True:
            # Wait for data to be ready on either socket
            readable, _, _ = select.select(sockets, [], [])
            
            if client_socket in readable:
                data = client_socket.recv(4096)
                if len(data) == 0: break # Client disconnected
                backend_socket.sendall(data)
                
            if backend_socket in readable:
                data = backend_socket.recv(4096)
                if len(data) == 0: break # Backend disconnected
                client_socket.sendall(data)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        backend_socket.close()

def start_load_balancer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOAD_BALANCER_HOST, LOAD_BALANCER_PORT))
    server.listen(5)
    print(f"[*] Load Balancer running on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")
    
    while True:
        client_sock, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        # Handle each request in a new thread (Concurrency)
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()

if __name__ == "__main__":
    start_load_balancer()