from enum import IntEnum
import socket
import binascii
from binascii import unhexlify
from random import randrange
import ipaddress
import logging as logD
import logging as logEC
import logging as logES

class MessageType(IntEnum):
    NONE = 0
    DHCPDISCOVER = 1
    DHCPOFFER = 2
    DHCPREQUEST = 3
    DHCPDECLINE = 4
    DHCPACK = 5
    DHCPNAK = 6
    DHCPRELEASE = 7
    DHCPINFORM = 8


class Opcode(IntEnum):
    NONE = 0
    REQUEST = 1
    REPLY = 2

class Options(IntEnum):
    PADDING = 0
    SUBNETMASK = 1
    ROUTER = 3
    SERVERNAME = 5
    DNS = 6
    BROADCASTADDR = 28
    REQUESTEDIP = 50
    LEASETIME = 51
    MESSTYPE = 53
    PARAMREQLIST = 55
    RENEWTIME = 58
    REBINDTIME = 59
    CLIENTID = 61
    END = 255

MAGIC_COOKIE = b'\x63\x82\x53\x63'

PacketFields = [
    {'id': 'op', 'name': 'opcode', 'length': 1, 'type': 'int'},
    {'id': 'htype', 'name': 'hardwareType', 'length': 1, 'type': 'int'},
    {'id': 'hlen', 'name': 'hardwareAddressLength', 'length': 1, 'type': 'int'},
    {'id': 'hops', 'name': 'hops', 'length': 1, 'type': 'int'},
    {'id': 'xid', 'name': 'transactionID', 'length': 4, 'type': 'hex'},
    {'id': 'secs', 'name': 'secondsElapsed', 'length': 2, 'type': 'int'},
    {'id': 'flags', 'name': 'bootFlags', 'length': 2, 'type': 'hex'},
    {'id': 'ciaddr', 'name': 'clientIPAddress', 'length': 4, 'type': 'ip'},
    {'id': 'yiaddr', 'name': 'yourIPAddress', 'length': 4, 'type': 'ip'},
    {'id': 'siaddr', 'name': 'serverIPAddress', 'length': 4, 'type': 'ip'},
    {'id': 'giaddr', 'name': 'gatewayIPAddress', 'length': 4, 'type': 'ip'},
    {'id': 'chaddr', 'name': 'clientHardwareAddress', 'length': 16, 'type': 'mac'},
    {'id': 'sname', 'name': 'serverName', 'length': 64, 'type': 'str'},
    {'id': 'filename', 'name': 'bootFilename', 'length': 128, 'type': 'str'},
    {'id': 'magic_cookie', 'name': 'magic_cookie', 'length': 4, 'type': 'hex'},
]

OptFields = [
    {'id': Options.MESSTYPE, 'name': 'messType', 'length': 1, 'type': 'int'},
    {'id': Options.LEASETIME, 'name': 'leaseTime', 'length': 4, 'type': 'int'},
    {'id': Options.RENEWTIME, 'name': 'renewTime', 'length': 4, 'type': 'int'},
    {'id': Options.REBINDTIME, 'name': 'rebindTime', 'length': 4, 'type': 'int'},
]

RequestedOptFields = [
    {'id': Options.ROUTER, 'name': 'router', 'length': 0, 'type': 'str'},
    {'id': Options.SERVERNAME, 'name': 'serverName', 'length': 0, 'type': 'str'},
    {'id': Options.DNS, 'name': 'dns', 'length': 0, 'type': 'str'},
    {'id': Options.SUBNETMASK, 'name': 'subnetMask', 'length': 4, 'type': 'ip'},
    {'id': Options.BROADCASTADDR, 'name': 'broadcast', 'length': 4, 'type': 'ip'},
    {'id': Options.REQUESTEDIP, 'name': 'yourIPAddress', 'length': 4, 'type': 'ip'}
]

class Encode:
    @staticmethod
    def int(value: int, length: int = 1) -> bytes:
        return value.to_bytes(length, 'big')

    @staticmethod
    def hex(value, length: int = 4) -> bytes:
        #temp = bytes.fromhex(str(value)[2:])
        return value.to_bytes(length, 'big')

    @staticmethod
    def ip(value: str, length: int = 4) -> bytes:
        return socket.inet_aton(value)

    @staticmethod
    def str(value: str, length: int) -> bytes:
        temp = str.encode(value)
        return temp + (length - len(temp)) * b'\x00'

    @staticmethod
    def mac(value: str, length: int = 6) -> bytes:
        result = bytes.fromhex(value.replace(':', '').lower())
        return result + (length - result.__len__()) * b'\x00'


class Decode:
    @staticmethod
    def int(value: bytes) -> int:
        return int.from_bytes(value, byteorder='big', signed=False)

    @staticmethod
    def hex(value: bytes) -> int:
        return int.from_bytes(value, byteorder='big', signed=False)

    @staticmethod
    def ip(value: bytes) -> str:
        int_array = [int(x) for x in value]
        ip = '.'.join(str(x) for x in int_array)
        return str(ip)

    @staticmethod
    def str(value: bytes) -> str:
        result = value.decode("utf-8")
        return result.replace('\0', '')

    @staticmethod
    def mac(value: bytes) -> str:
        int_array = [int(x) for x in value]
        mac = ':'.join("{:0>2s}".format(hex(x)[2:]) for x in int_array)
        return mac

class PACKET:
    def __init__(self, data, opcode=Opcode.NONE, messType=MessageType.NONE, leaseTime=None, options=None, serverMode=False):
        if data:
            self.opcode = Opcode(Decode.int(data[0:1])) 
            self.hardwareType = Decode.int(data[1:2])
            self.hardwareAddressLength = Decode.int(data[2:3])
            self.hops = Decode.int(data[3:4])
            self.transactionID = Decode.hex(data[4:8])
            self.secondsElapsed = Decode.int(data[8:10]) 
            self.bootFlags = Decode.hex(data[10:12]) 
            self.clientIPAddress = Decode.ip(data[12:16]) 
            self.yourIPAddress = Decode.ip(data[16:20])
            self.serverIPAddress = Decode.ip(data[20:24])
            self.gatewayIPAddress = Decode.ip(data[24:28])
            self.clientHardwareAddress = Decode.mac(data[28:34])
            self.serverName = Decode.str(data[44:108]) 
            self.bootFilename = Decode.str(data[108:236]) 
            self.magic_cookie = Decode.int(data[236:240]) 
        else:
            self.opcode = opcode
            self.hardwareType = 1
            self.hardwareAddressLength = 6
            self.hops = 0
            self.transactionID = randrange(0x1_00_00_00_00)    #generate transaction random number
            self.secondsElapsed = 0
            self.bootFlags = 0x0
            self.clientIPAddress = '0.0.0.0'     #'1.2.3.4'
            self.yourIPAddress = '0.0.0.0'       #'5.6.7.8'
            self.serverIPAddress = '0.0.0.0'     #'9.10.11.12'
            self.gatewayIPAddress = '0.0.0.0'    #'1.2.3.4'
            self.clientHardwareAddress = '12:07:00:ac:dc:ff'
            self.serverName = 'DHCP Server'
            self.bootFilename = ''
            self.magic_cookie = int.from_bytes(MAGIC_COOKIE, byteorder='big')

        #dhcp options
        self.messType = messType
        self.subnetMask = None
        self.broadcast = None
        self.leaseTime = leaseTime
        if self.leaseTime is None:
            self.renewTime = None
            self.rebindTime = None
        else:
            self.renewTime = leaseTime // 2
            self.rebindTime = (7 * leaseTime) // 8

        # if in packet constructor are explicitly specified any options = required options => must add them to the packet
        if options:
            self.setRequestedOpt(options)
        else:
            # just basic configuration of the packet, the client does not want to know more - self sufficient brat
            self._requestOpt = []
            self.requestOptFlag = False

        self.serverMode = serverMode

        # client requests options
        self.dns = None
        self.router = None
        if data:
            self.decodeOpt(data[240:])

    def setRequestedOpt(self, options):
        self._requestOpt = list(set(options))
        self.requestOptFlag = True

    def setSubnetMask(self, subnetMask):
        try:
            int(subnetMask)
            net = ipaddress.ip_network('192.178.2.55/{}'.format(subnetMask), strict=False)
            self.subnetMask = str(net.netmask)
        except (ValueError, TypeError):
            self.subnetMask = subnetMask

    def setLeaseTime(self, leaseTime):
        self.leaseTime = leaseTime
        if self.leaseTime is None:
            self.renewTime = None
            self.rebindTime = None
        else:
            self.renewTime = leaseTime // 2
            self.rebindTime = (7 * leaseTime) // 8

    def decodeOpt(self, dataOptions):
        byte = 0
        byteValue = 0
        while byte < dataOptions.__len__() and dataOptions[byte] != 255:
            try:
                byteValue = dataOptions[byte]
                if byteValue == 55:
                    optLength = dataOptions[byte + 1]
                    byte += 2
                    for evrByte in dataOptions[byte: byte + optLength]:
                        self._requestOpt.append(int(evrByte))
                    byte += optLength
                    continue
                try:
                    option = next(item for item in OptFields if item['id'] == Options(byteValue))
                except StopIteration:
                    option = next(item for item in RequestedOptFields if item['id'] == Options(byteValue))
                    self._requestOpt.append(int(byteValue))
                optLength = option['length'] if option['length'] != 0 else dataOptions[byte + 1]
                byte += 2
                decoding = getattr(Decode, option['type'])
                setattr(self, option['name'], decoding(dataOptions[byte: byte + optLength]))
                byte += optLength
            except ValueError:
                #Received package from another server
                logD.info("Decoding -> Dhcp option {} is unknown for me".format(byteValue))
                break

    def encodeOpt(self):
        data = b''
        for option in PacketFields:
            value = getattr(self, option['name'])
            length = option['length']
            encoding = getattr(Encode, option['type'])
            data += encoding(value, length)
        for option in OptFields:
            value = getattr(self, option['name'])
            length = option['length']
            if value is not None:
                encoding = getattr(Encode, option['type'])
                data += Encode.int(option['id']) + Encode.int(length) + encoding(value, length)
        #dhcp request parameters according to server mode
        if not self.serverMode and self.requestOptFlag:    #client mode - send request bytes - field 55
            requestID = 0
            if self._requestOpt:
                try:
                    data += Encode.int(55) + Encode.int(len(self._requestOpt))
                    for requestID in self._requestOpt:
                        data += Encode.int(requestID)
                except ValueError:
                    # Received package from another server
                    logEC.info("Encoding (client mode)-> Dhcp option {} is unknown for me".format(requestID))
        elif self.serverMode:                       #server mode - send requested options
            requestID = 0
            try:
                if self._requestOpt:
                    for requestID in self._requestOpt:
                        try:
                            item = [item for item in RequestedOptFields if item['id'] == requestID][0]
                        except (ValueError, IndexError):
                            #if that option is in dhcp options fields, continue, because we already send it
                            item = [item for item in OptFields if item['id'] == requestID][0]
                            continue
                        value = getattr(self, item['name'])
                        length = item['length'] if item['length'] != 0 else len(value)
                        if value is not None:
                            encoding = getattr(Encode, item['type'])
                            data += Encode.int(item['id']) + Encode.int(length) + encoding(value, length)
            except (ValueError, IndexError):
                logES.info("Encoding (server mode)-> Dhcp option {} is unknown for me".format(requestID))

        data += Encode.int(Options.END)
        return data

    def __str__(self):
        string = ""
        string += "------Packet Info-------\n"
        string += "Opcode : {}\n".format(self.opcode.name)
        string += "Hardware Type : {}\n".format(self.hardwareType)
        string += "Hardware Address Length : 0x{}\n".format(self.hardwareAddressLength)
        string += "Hops : {}\n".format(self.hops)
        string += "Transaction Number : {}\n".format(hex(self.transactionID))
        string += "Seconds Elapsed : {}\n".format(self.secondsElapsed)
        string += "Boot Flags : {}\n".format(self.bootFlags)
        string += "Client Ip Address : {}\n".format(self.clientIPAddress)
        string += "Your Ip Address : {}\n".format(self.yourIPAddress)
        string += "Server Ip Address : {}\n".format(self.serverIPAddress)
        string += "Gateway Ip Address : {}\n".format(self.gatewayIPAddress)
        string += "Client Hardware Address : {}\n".format(self.clientHardwareAddress)
        string += "Server Name : {}\n".format(self.serverName)
        string += "Boot Filename : {}\n".format(self.bootFilename)
        string += "Magic Cookie : {}\n".format(hex(self.magic_cookie))
        string += "--Options\n"
        if self.messType == None:
            string += ""
        else:
            string += "Message Type : {}\n".format(MessageType(self.messType).name)
        if self.leaseTime == None:
            string += ""
        else:
            string += "Lease Time : {}\n".format(self.leaseTime)
        if self.renewTime == None:
            string += ""
        else:
            string += "Renewal Time : {}\n".format(self.renewTime)
        if self.rebindTime == None:
            string += ""
        else:
            string += "Rebinding Time : {}\n".format(self.rebindTime)

        string += "--Requests\n"
        print(self._requestOpt)
        if self._requestOpt and self.serverMode:
            for request in self._requestOpt:
                string += "{}\n".format(Options(request).name)
        elif self._requestOpt and not self.serverMode:
            if self.broadcast and Options.BROADCASTADDR in self._requestOpt:
                string += "Broadcast Address : {}\n".format(self.broadcast)
            if self.subnetMask and Options.SUBNETMASK in self._requestOpt:
                string += "Subnet Mask : {}\n".format(self.subnetMask)
            if self.dns and Options.DNS in self._requestOpt:
                string += "DNS : {}\n".format(self.dns)
            if self.serverName and Options.SERVERNAME in self._requestOpt:
                string += "Server name : {}\n".format(self.serverName)
            if self.router and Options.ROUTER in self._requestOpt:
                string += "Router : {}\n".format(self.router)
            if self.yourIPAddress and self.yourIPAddress != '0.0.0.0' and Options.REQUESTEDIP in self._requestOpt:
                string += "Requested Ip Address : {}\n".format(self.yourIPAddress)
        return string
