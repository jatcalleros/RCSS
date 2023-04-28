import socket

server_ip = '192.168.1.2'
server_port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Server listening on {server_ip}:{server_port}")

while True:
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    data = conn.recv(1024)
    message = data.decode('utf-8')
    print(f"Received message: {message}")

    conn.close()
