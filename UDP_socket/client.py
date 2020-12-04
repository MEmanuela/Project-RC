import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Client: Socket Created')

host = 'localhost'
port = 5433
message = 'Hello'

try:
    print('Client: ' + message)
    client_socket.sendto(message.encode(), (host, 5435))

    data, server = client_socket.recvfrom(4096)
    data = data.decode()
    print('Client: ' + data)

finally:
    print('Client: Closing socket')
    client_socket.close()