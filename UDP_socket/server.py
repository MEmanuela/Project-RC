import socket
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Server: Socket Created')

#host = 'localhost'
#port = 5435
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#server_socket.bind((host, port))
#print('Server: Socket connected to ' + host)

#funny_message = ', This is a funny message!'

server_socket.settimeout(0.2)
message = b'your very important message'
while True:
    server_socket.sendto(message, ('<broadcast>', 37020))
    print("message sent!")
    time.sleep(1)