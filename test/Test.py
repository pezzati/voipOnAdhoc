import netifaces
from socket import *

class Message():
    def __init__(self, my_id, msg_type, content):
        self.type = msg_type
        self.msg_len = len(str(content))
        self.owner_id = str(my_id)
        self.id_len = len(str(my_id))
        self.payload = str(content)

    def get_packed(self):
        data = pack('!BII', self.type, self.id_len, self.msg_len)
        data += self.owner_id.encode('utf-8')
        data += self.payload.encode('utf-8')
        return data

#print(netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0])
#print(netifaces.gateways()[netifaces.AF_INET][0])
from struct import pack

cs = socket(AF_INET, SOCK_DGRAM)
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), 54545))

msg = Message(6524,1,'This is a test')
print(msg.get_packed())
cs.sendto(msg.get_packed(), (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
msg.type=0
cs.sendto(msg.get_packed(), (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
#print('This is a test\n test2'.encode())
cs.close()
