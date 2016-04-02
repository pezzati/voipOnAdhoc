import datetime
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
    def __init__(self, name, port_num, my_id, network):
        threading.Thread.__init__(self, name=name)
        self.node_id = my_id
        self.net = network
        self.rec_msgs = []

        self.file_name = 'log/outputs/'
        self.file_name += str(my_id)
        self.file_name += '_'
        time = str(datetime.datetime.now())
        time = time.split('.')[0]
        time = time.replace(' ', '_')
        self.file_name += time
        self.file_name += '.log'
        self.output_file = open(self.file_name, 'w')
        self.output_file.close()

        self.terminate = False

        self.port = port_num
        self.listener_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            self.listener_socket.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.port))
        except:
            self.listener_socket.close()
            raise Exception('Cant run Listener for {}'.format(self.port))

    def run(self):
        #output_file = open(self.file_name, 'w')
        while True:
            data = self.listener_socket.recv(1024)
            self.output_file = open(self.file_name, 'a')
            msg = Message()
            msg.build_by_data(data)
            self.output_file.write(str(datetime.datetime.now()))
            self.output_file.write('\t')
            self.output_file.write(msg.__str__())
            print(msg.__str__())
            #if MESSAGE_TYPE[msg.type] == 'Exit':
            #    break
            if self.handle(msg) == -1:
                self.output_file.close()
                break
            self.output_file.close()
        self.listener_socket.close()
        self.output_file.close()
        print('Listener closed')

    def handle(self, msg):
        if MESSAGE_TYPE[msg.type] == 'Exit':
            print('Exit received, see you later. Press Enter to exit.')
            self.terminate = True
            self.output_file.write('\tProgram terminated\n')
            return -1
        if MESSAGE_TYPE[msg.type] == 'Text':
            if msg.packet_id in self.rec_msgs:
                self.output_file.write('\tDrop the message\n')
                return 0
            self.output_file.write('\tMessage broadcast\n')
            self.rec_msgs.append(msg.packet_id)
            self.net.broadcast(msg.get_packed())
            return 0
        #if MESSAGE_TYPE[msg.type] == 'Routing':

    def add_id(self, msg_id):
        self.rec_msgs.append(msg_id)