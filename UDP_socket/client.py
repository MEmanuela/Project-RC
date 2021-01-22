import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Client: Socket Created')

#host = 'localhost'
#port = 5433
#message = 'Hello'

client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client_socket.bind(("", 37020))
while True:
    # Thanks @seym45 for a fix
    data, addr = client_socket.recvfrom(1024)
    print("received message: %s"%data)