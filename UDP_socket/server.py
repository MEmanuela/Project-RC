import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Server: Socket Created')

host = 'localhost'
port = 5435
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_socket.bind((host, port))
print('Server: Socket connected to ' + host)

funny_message = ', This is a funny message!'

while 1:
  data, addr = server_socket.recvfrom(4096)

  if data:
      print('Server: Sending the funny message')
      server_socket.sendto(data + (funny_message.encode()), addr)