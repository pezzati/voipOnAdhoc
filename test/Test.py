import netifaces
from socket import *
from struct import pack
import struct
MESSAGE_TYPE = {0: 'Exit', 1: 'Text', 2: 'Routing'}


class Message():
    def __init__(self, packet_id=0, msg_type=0, src_id='0', dst_id='0', status=0, content=''):
        self.packet_id = packet_id
        self.type = msg_type
        self.src_id = src_id
        #self.scr_id_len = len(str(src_id))
        self.dst_id = dst_id
        #self.dst_id_len = len(self.dst_id)
        self.status = status
        self.msg_len = len(str(content))
        self.payload = str(content)

    def get_packed(self):
        data = pack('!IBBBBH', self.packet_id, self.type, self.src_id, self.dst_id, self.status, self.msg_len)
        data += self.payload.encode('utf-8')
        return data

    def build_by_data(self, data):
        header = data[:10]
        packet_id, msg_type, source, dst, sts, length = struct.unpack('!IBBBBH', header)
        body = data[10:10 + length]
        #print(body.decode('utf-8'))
        self.type = msg_type
        self.msg_len = length
        self.src_id = source
        #self.scr_id_len = src_id_length
        self.dst_id = dst
        #self.dst_id_len = dst_id_length
        self.status = sts
        self.payload = body.decode('utf-8')
        #return Message(owner_id.decode("utf-8"), msg_type, body.decode('utf-8'))

    def __str__(self):
        return '{} message from {}: {}'.format(MESSAGE_TYPE[self.type], self.src_id, self.payload)


class IDInfo():
    def __init__(self, base):
        self.base_id = base

    def build_id(self, given_id):
        res = int(given_id)
        res <<= 24
        res += self.base_id
        self.base_id += 1
        return res

generator = IDInfo(0)
cs = socket(AF_INET, SOCK_DGRAM)
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), 54545))

msg = Message(packet_id=generator.build_id(2), msg_type=1, src_id=2, dst_id=255, status=0, content='This is a test')
print(msg.get_packed())
cs.sendto(msg.get_packed(), (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
msg.type = 0
msg.packet_id = generator.build_id(2)
cs.sendto(msg.get_packed(), (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
#print('This is a test\n test2'.encode())
cs.close()
