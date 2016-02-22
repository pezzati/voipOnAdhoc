import netifaces
from socket import *
import struct
from Model import *
import threading
#import socket


class Network():
    def __init__(self, port):
        self.br_port = port
        self.cs = socket(AF_INET, SOCK_DGRAM)
        self.cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #self.cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), self.port))

    def broadcast(self, data):
        self.cs.sendto(data,
                       (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.br_port))

    def terminate(self):
        self.cs.close()

    def send(self, dst, data, port=None):
        if port is None:
            port = self.br_port
        #try:
        #    socket.inet_aton(dst)
        #except socket.error:
        #    raise Exception('Dst doesnt match with IP pattern')
        try:
            self.cs.sendto(data, (dst, port))
        except:
            raise Exception('Cant send packer to {}'.format(dst))


class Listener(threading.Thread):
    def __init__(self, name, port_num):
        threading.Thread.__init__(self, name=name)
        self.port = port_num
        self.listener_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            self.listener_socket.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.port))
        except:
            self.listener_socket.close()
            raise Exception('Cant run Listener for {}'.format(self.port))

    def run(self):
        while True:
            data=self.listener_socket.recv(1024)
            msg=Message()
            msg.build_by_data(data)
            print(msg.__str__())
            if MESSAGE_TYPE[msg.type] == 'Exit':
                break
            #TODO Message Handler
        self.listener_socket.close()
        print('Listener closed')