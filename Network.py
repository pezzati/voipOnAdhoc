import netifaces
from socket import *
import struct
from Model import *


class Network():
    def __init__(self, port):
        self.port = port
        self.cs = socket(AF_INET, SOCK_DGRAM)
        self.cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), self.port))

    def broadcast(self, data):
        self.cs.sendto(data,
                       (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.port))

    def terminate(self):
        self.cs.close()


def get_message(data):
    header = data[:9]
    msg_type, id_length, msg_length=struct.unpack('!BII', header)
    #print('type:{} length:{}'.format(msg_type, id_length))
    owner_id=data[9:id_length+9]
    #print(owner_id.decode("utf-8"))
    body=data[id_length+9:id_length+9+msg_length]
    #print(body.decode('utf-8'))
    return Message(owner_id.decode("utf-8"), msg_type, body.decode('utf-8'))