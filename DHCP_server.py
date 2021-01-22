import socket
import datetime
import time
import json
import logging as log
import math
import ipaddress
import tkinter as tk
from DHCP_packet import PACKET, MessageType, Opcode
import select

sPort = 67
cPort = 68
MAX_BYTES = 1024
recvTimeout = 5

class DHCP_Server:
    def __init__(self, gui = None):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.destination = (('255.255.255.255', cPort))
        self.ip = '0.0.0.0'
        self.name = None
        self.pool = {}
        self.IPstart = None
        self.subnetMask = None
        self.broadcast = None
        self.router = '127.0.0.1'
        self.dns = 'RC-project.com'
        self.leaseTime = None
        self.renewalTime = None
        self.rebindingTime = None
        self.reserved = {}
        self.runFlag = True
        self.shut_down = True
        self.gui = gui
        self.showPacketsDebug = False

    def setServerName(self, name):
        self.name = name

    def setServerLeaseTime(self, time):
        self.leaseTime = time
        self.renewalTime = time//2
        self.rebindingTime = (7*time)//8
    
    @staticmethod
    def getPool(startingAddress, mask):
        pool = {}
        nrOfAddresses = 2 ** (32 - mask) - 2 
        ip_1, ip_2, ip_3, ip_4 = [int(s) for s in startingAddress.split('.')]
        ip_1, ip_2, ip_3, ip_4 = DHCP_Server.ipSplitter(ip_1, ip_2, ip_3, ip_4)
        for i in range(nrOfAddresses):
            pool.update({"{}.{}.{}.{}".format(ip_1, ip_2, ip_3, ip_4): {'mac': None, 'time': None}})
            ip_1, ip_2, ip_3, ip_4 = DHCP_Server.ipSplitter(ip_1, ip_2, ip_3, ip_4)
        broadcast = "{}.{}.{}.{}".format(ip_1, ip_2, ip_3, ip_4)
        return pool, broadcast

    def setAddressPool(self, startingAddress, mask):
        self.IPstart = startingAddress
        self.subnetMask = mask
        self.pool, self.broadcast = self.getPool(self.IPstart, self.subnetMask)
        # TO:DO if address is reserved delete from pool
        print(self.pool)

    def ipSplitter(IP1, IP2, IP3, IP4, UP = 256, DOWN = 0):
            IP4 += 1
            if IP4 == UP:
                IP4 = DOWN
                IP3 += 1
            if IP3 == UP:
                IP3 = DOWN
                IP2 += 1
            if IP2 == UP:
                IP2 = DOWN
                IP1 += 1
            if IP1 == UP:
                IP1 = DOWN
            return IP1, IP2, IP3, IP4

    def _sendOffer(self, packet):
        packet.messType = MessageType.DHCPOFFER
        # check is MAC in reserved
        reservation = self._getReserved(packet.clientHardwareAddress)
        if reservation:
            self.debug("Offering the reserved IP address")
            packet.yourIPAddress = reservation
            packet.leaseTime = None
        else:
            freeAddress = self.getNotReservedAddress()
            if freeAddress is not None:
                packet.yourIPAddress = freeAddress
            else:
                self.debug("Can't offer any ip.")
                return
        self.debug("I can hear you! My IP address is " + self.ip + ". I can lease an IP address to you.")
        self.debugPacket(packet)
        mess = packet.encodeOpt()
        self.server_socket.sendto(mess, self.destination)

    def _sendAcknowledge(self, packet):
        self.debug("Sure. I can lease you all network configuration data, including your IP address.")
        packet.messType = MessageType.DHCPACK
        packet.clientIPAddress = packet.yourIPAddress
        self.pool.update({packet.clientIPAddress: {'mac': packet.clientHardwareAddress, 'time': datetime.datetime.now()}})
        reservation = self._getReserved(packet.clientHardwareAddress)
        if reservation:
            self.reserved.update({packet.clientIPAddress: packet.clientHardwareAddress})
            self.pool.update({packet.clientIPAddress: {'mac': packet.clientHardwareAddress, 'time': None}})
        #self.server_socket.send(packet.encode(), self.port)
        self.debugPacket(packet)
        #if self.gui:
        #   self.gui.updateFramesPool()

        mess = packet.encodeOpt()
        self.server_socket.sendto(mess, self.destination)

    def _sendNacknowledge(self, packet):
        self.debug("Sorry, I changed my mind, I can not lease you the IP address I offered 2 seconds ago.")
        packet.messType = MessageType.DHCPNAK
        self.debugPacket(packet)

        mess = packet.encodeOpt()
        self.server_socket.sendto(mess, self.destination)

    def _addPacketOptions(self, packet):
        packet.opcode = Opcode.REQUEST
        packet.setLeaseTime(self.leaseTime)
        packet.serverName = self.name
        packet.broadcast = self.broadcast
        packet.setSubnetMask(self.subnetMask)
        packet.router = self.router
        packet.dns = self.dns

    def _response(self, data: bytes):
        packet = PACKET(data, serverMode=True)
        print(packet)
        if packet.opcode != Opcode.REQUEST:
            return
        if packet.messType == MessageType.DHCPDISCOVER:
            self.debug("Hello. Any DHCP server available out there? Answer me if you hear me!", endLine=True)
            self.debugPacket(packet)

            if self._macReserved(packet.clientHardwareAddress):
                self.debug("The chaddr {} has a reserved IP address".format(packet.clientHardwareAddress), afterEndLine=True)
                packet.yourIPAddress = self._getReserved(packet.clientHardwareAddress)
                packet.leaseTime = None
                self._sendAcknowledge(packet)
            else:
                self._addPacketOptions(packet)
                self._sendOffer(packet)

        elif packet.messType == MessageType.DHCPREQUEST:
            self.debug("Thank you for your response. Then can you lease the IP address to me?" , endLine=True)
            self.debugPacket(packet)

            self._addPacketOptions(packet)
            if packet.yourIPAddress == '0.0.0.0':
                ipToCheck = packet.clientIPAddress #client is already using the address
            else:
                ipToCheck = packet.yourIPAddress #client needs an address
            if ipToCheck not in self.pool.keys():
                self.debug("{} is not in my pool".format(ipToCheck), afterEndLine=True)
                self._sendNacknowledge(packet)
            elif self.ipNotReserved(ipToCheck):
                if self._macReserved(packet.clientHardwareAddress):
                    self.debug("The chaddr {} has a reserved IP address".format(packet.clientHardwareAddress), afterEndLine=True)
                    self._sendNacknowledge(packet)
                else:
                    #self.debug("The chaddr {} is now owner of the IP address {}".format(packet.clientHardwareAddress, ipToCheck), afterEndLine=True)
                    self._sendAcknowledge(packet)
            else:
                if self.pool[ipToCheck]['mac'] == packet.clientHardwareAddress:
                    self.debug("Updating the lease time for mac {}".format(packet.clientHardwareAddress), afterEndLine=True)
                    self._sendAcknowledge(packet)
                else:
                    self.debug("The IP address {} is taken by another client".format(ipToCheck), afterEndLine=True)
                    self._sendNacknowledge(packet)
        elif packet.messType == MessageType.DHCPDECLINE:
            self.debug("DHCP DECLINE received", endLine=True)
            self.debugPacket(packet)
        elif packet.messType == MessageType.DHCPRELEASE:
            self.debug("DHCP RELEASE received", endLine=True)
            self.pool.update({packet.clientIPAddress: {'mac': None, 'time': None}})
            #self.gui.updateFramesPool()
            self.debugPacket(packet)
        elif packet.messType == MessageType.DHCPINFORM:
            self.debug("DHCP INFORM received", endLine=True)
            self.debugPacket(packet)

    def _getReserved(self, macToCheck):
        if macToCheck in self.reserved.values():
            for ip, mac in self.reserved.items():
                if mac == macToCheck:
                    return ip
        return None

    def _macReserved(self, mac):
        return any(mac in ip_info.values() for ip_info in self.pool.values())

    def getNotReservedAddress(self):
        print(self.pool)
        for ip, ip_info in self.pool.items():
            if ip_info['mac'] is None:
                return ip
        return None

    def ipNotReserved(self, ip):
        if self.pool[ip]['mac'] is None:
            return True
        return False

    def setFlag(self, param):
        self.runFlag = param

    def startServer(self):
        self.debug("{} has started".format(self.name))
        try:
            self.server_socket.bind(('', sPort))
        except OSError:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.server_socket.bind(('', sPort))
        self.shut_down = False

        import threading
        update_pool_thread = threading.Thread(target=self._updatePool)
        update_pool_thread.daemon = True
        update_pool_thread.start()

        while self.runFlag:
            self.debug("{} is waiting for requests ...".format(self.name))
            ready = select.select([self.server_socket], [], [], recvTimeout)
            if ready[0]:
                data, address = self.server_socket.recvfrom(MAX_BYTES)
                print(address)
                self.debug("{} is analyzing the request".format(self.name))
                self._response(data)
        self.shut_down = True
        self.debug("{} is saving address pool to 'pool.json'".format(self.name))
        self.savePool()
        self.debug("{} has stopped".format(self.name))

    def _updatePool(self, tSleep=3):
        while self.runFlag:
            for ip, ip_info in self.pool.items():
                if ip_info['mac'] is not None and ip_info['time'] is not None:
                    if float(self.leaseTime) <= (datetime.datetime.now() - ip_info['time']).total_seconds():
                        self.debug("Lease time of {} for user {} has expired".format(ip, ip_info['mac']), afterEndLine=True)
                        self.pool.update({ip: {'mac': None, 'time': None}})
                        #self.gui.updateFramesPool()
            time.sleep(tSleep)

    def savePool(self):
        with open('pool.json', 'w') as file:
            log.info("Saving clients status...")
            file.write(json.dumps(self.pool, indent=2, sort_keys=True, default=str))
        with open('reserved.json', 'w') as file:
            log.info("Saving reserved addresses...")
            file.write(json.dumps(self.reserved, indent=2, sort_keys=True, default=str))
    
    def loadPool(self):
        try:
            with open('pool.json', 'r') as file:
                log.info("Loading clients status from pool.json")
                self.pool = json.load(file)
                for item in self.pool.values():
                    if item not in self.reserved.values():
                        if item['time'] is not None:
                        #creates a datetime object from the given string
                            item['time'] = datetime.datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S.%f')
                self.subnetMask = 32 - int(math.log(len(self.pool.keys()) + 2, 2))
                start = ipaddress.IPv4Address(list(self.pool.keys())[0])
                net = ipaddress.IPv4Network(list(self.pool.keys())[0] + '/' + str(self.subnetMask), False)
                self.IPstart = str(ipaddress.IPv4Address(int(start) & int(net.netmask)))
                self.broadcast = str(net.broadcast_address)
                log.info("Setting mask: {}".format(self.subnetMask))
                log.info("Setting network address: {}".format(self.IPstart))
                log.info("Setting network broadcast address: {}".format(self.broadcast))

            with open('reserved.json', 'r') as file:
                log.info("Loading reserved addresess from reserved.json")
                self.reserved = json.load(file)
        except json.decoder.JSONDecodeError:
            log.info("JSON corrupted or empty")

# interface connection
    def debug(self, param, endLine = False, afterEndLine = False):
        if self.gui:
            datetime_object = datetime.datetime.now()
            printable = "{} : {}\n".format(datetime_object, param)
            if endLine:
                self.gui.frames['open_server'].status_viewer_pool_text.insert(tk.END, "\n")
            self.gui.frames['open_server'].status_viewer_pool_text.insert(tk.END, printable)
            if afterEndLine:
                self.gui.frames['open_server'].status_viewer_pool_text.insert(tk.END, "\n")
        log.info(param)

    def debugPacket(self, packet):
        if self.gui and self.showPacketsDebug:
            self.gui.frames['open_server'].status_viewer_pool_text.insert(tk.END, '\n' + str(packet) + '\n')


        