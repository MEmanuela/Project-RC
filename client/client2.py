import select
import socket
import sys
import os


scriptpath = "../"

# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(scriptpath))

from DHCP_packet import PACKET, MessageType, Opcode, Options
from DHCP_server import log

serverPort = 67
clientPort = 68
MAX_BYTES = 1024

UDP_IP = '0.0.0.0'
UDP_PORT = 68

def client_2():
    dst = ('<broadcast>', serverPort)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, clientPort))

    log.info("Sending DHCP_DISCOVER packet:")

    #Here we manipulate our packet
    packet = PACKET(None)
    packet.opcode = Opcode.REQUEST
    packet.messType = MessageType.DHCPDISCOVER
    packet.clientHardwareAddress = '00:00:00:00:00:09'
    #packet.yourIPAddress = '10.1.0.124'

    print(packet)
    message = packet.encodeOpt()
    sock.sendto(message, dst)

    log.info("UDP target ip {}".format(UDP_IP))
    log.info("UDP target port {}".format(UDP_PORT))

    try:
        while True:
            r, _, _ = select.select([sock], [], [], 3)
            if not r:
                log.info("Nu s-a receptionat nimic de la server")
                break
            else:
                data = sock.recv(MAX_BYTES)
                packet_received = PACKET(data)
                if packet_received.messType == MessageType.DHCPOFFER:
                    log.info("Offer received")
                    print(packet_received)
                elif packet_received.messType == MessageType.DHCPACK:
                    log.info("Acknowledge received")
                    print(packet_received)
                elif packet_received.messType == MessageType.DHCPNAK:
                    log.info("Negative Acknowledge received")
                    print(packet_received)
    except socket.timeout as e:
        print("Timpul de asteptare a expirat.")
        sock.close()
        exit(1)
    sock.close()


if __name__=='__main__':
    client_2()