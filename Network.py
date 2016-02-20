import netifaces
from socket import *


class Network():
    def __init__(self, port):
        self.port = port
        self.cs = socket(AF_INET, SOCK_DGRAM)
        self.cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), self.port))

    def broadcast(self, msg):
        self.cs.sendto('msg'.encode(),
                       (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.port))

    def terminate(self):
        self.cs.close()