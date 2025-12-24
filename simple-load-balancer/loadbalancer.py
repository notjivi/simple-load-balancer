import socket
import threading
import select

LOAD_BALANCER_HOST = '0.0.0.0'
LOAD_BALANCER_PORT = 8080

SERVER_POOL = [
    ('www.google.com', 80),
    ('www.example.com', 80)
]

current_server_index = 0
index_lock = threading.Lock()

def get_next_server():
    global current_server_index
    with index_lock:
        server = SERVER_POOL[current_server_index]
        current_server_index = (current_server_index + 1) % len(SERVER_POOL)
    return server

def handle_client(client_socket):
    backend_host, backend_port = get_next_server()
    
    try:
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect((backend_host, backend_port))
        
        sockets = [client_socket, backend_socket]
        
        while True:
            readable, _, _ = select.select(sockets, [], [])
            
            if client_socket in readable:
                data = client_socket.recv(4096)
                if len(data) == 0: break 
                backend_socket.sendall(data)
                
            if backend_socket in readable:
                data = backend_socket.recv(4096)
                if len(data) == 0: break 
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
        
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()

if __name__ == "__main__":
    start_load_balancer()