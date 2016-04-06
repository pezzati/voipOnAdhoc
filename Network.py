import datetime
import netifaces
from socket import *
import struct
from Model import *
import threading
from Controller import get_id
#import socket

Routing_table = {}
ARP_QUEUE = {}


def standard_tuple(arg1, arg2):
    if arg1 > arg2:
        return (arg2,arg1)
    return (arg1,arg2)



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
            self.listener_socket.bind(
                (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), self.port))
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
        if msg.packet_id in self.rec_msgs:
            self.output_file.write('\tDrop the message\n')
            return 0
        if MESSAGE_TYPE[msg.type] == 'Exit':
            print('Exit received, see you later. Press Enter to exit.')
            self.terminate = True
            self.output_file.write('\tProgram terminated\n')
            return -1
        if MESSAGE_TYPE[msg.type] == 'Text':
            self.output_file.write('\tMessage broadcast\n')
            self.rec_msgs.append(msg.packet_id)
            self.net.broadcast(msg.get_packed())
            return 0
        if MESSAGE_TYPE[msg.type] == 'ARP':
            if msg.ttl <= 0:
                return 0
            if msg.dst_id != self.node_id and msg.dst_id != BROADCAST:
                self.output_file.write('\tMsg doesnt belong, DROPPED\n')
                return 0
            #ARP Request
            #key_tuple = standard_tuple(msg.asker, msg.target_id)
            typical_tuple = (msg.asker, msg.target_id)
            reverse_tuple = (msg.target_id, msg.asker)
            if msg.status == 0:
                # This node is target
                if msg.target_id == self.node_id:
                    #Received it before
                    if reverse_tuple in Routing_table:
                        if Routing_table[reverse_tuple].ttl >= msg.ttl:
                            self.output_file.write('\tARP with ttl {} for asker {} DROPPED\n'.format(msg.ttl,
                                                                                                     msg.asker))
                        else:
                            Routing_table[reverse_tuple].ttl = msg.ttl
                            Routing_table[reverse_tuple].next = msg.src_id

                            msg.packet_id = get_id()
                            msg.ttl = 255
                            msg.dst_id = msg.src_id
                            msg.src_id = self.node_id
                            msg.status = 1
                            self.send_msg(msg)
                            self.output_file.write('\tARP response sent to {} for asker {}\n'.format(msg.src_id,
                                                                                                     msg.asker))
                        return 0
                    #New ARP
                    Routing_table[reverse_tuple] = RoutingNode(source=msg.target_id, destination=msg.asker,
                                                               ttl=msg.ttl, next=msg.src_id)
                    msg.packet_id = get_id()
                    msg.ttl = 255
                    msg.dst_id = msg.src_id
                    msg.src_id = self.node_id
                    temp = msg.target_id
                    msg.target_id = msg.asker
                    msg.asker = temp
                    msg.status = 1
                    self.send_msg(msg)
                    self.output_file.write('\tNew ARP answer sent to {} for asker \n'.format(msg.dst_id, msg.asker))
                    return 0
                #broadcast the ARP
                else:
                    if typical_tuple in Routing_table:
                        if Routing_table[typical_tuple].ttl >= msg.ttl:
                            self.output_file.write('\tARP with ttl {} for asker {} DROPPED\n'.format(msg.ttl,
                                                                                                     msg.asker))
                            return 0
                        else:
                            Routing_table[typical_tuple].ttl = msg.ttl
                            Routing_table[reverse_tuple].next = msg.src_id
                            self.output_file.write('\tARP request with ttl {} broadcast for {}\n'.format(msg.ttl - 1,
                                                                                                         msg.target_id))
                    else:
                        Routing_table[typical_tuple] = RoutingNode(source=msg.asker, destination=msg.target_id,
                                                                   ttl=msg.ttl, next=-1)
                        Routing_table[reverse_tuple] = RoutingNode(source=msg.target_id, destination=msg.asker,
                                                                   ttl=-1, next=msg.src_id)
                        self.output_file.write('\tNew ARP request with ttl {} broadcast for {}\n'.format(msg.ttl - 1,
                                                                                                       msg.target_id))
                    msg.packet_id = get_id()
                    msg.ttl -= 1
                    msg.src_id = self.node_id
                    self.send_msg(msg)
                    return 0
            #ARP response
            if msg.status == 1:
                #This node is the asker
                if msg.target_id == self.node_id:
                    #Reveived it before
                    if reverse_tuple in Routing_table:
                        if Routing_table[reverse_tuple]. ttl >= msg.ttl:
                            self.output_file.write('\tARP response with ttl {} DROPPED\n'.format(msg.ttl))
                            return 0
                        else:
                            self.output_file.write('\tARP response with ttl {} accepted\n'.format(msg.ttl))
                            Routing_table[reverse_tuple].ttl = msg.ttl
                            Routing_table[reverse_tuple].next = msg.src_id
                            self.send_arp_queue(msg.asker)
                            return 1
                    else:
                        self.output_file.write('\tNew ARP response with ttl {} accepted\n'.format(msg.ttl))
                        Routing_table[reverse_tuple] = RoutingNode(source=msg.target_id, destination=msg.asker,
                                                                   ttl=msg.ttl, next=msg.src_id)
                        self.send_arp_queue(msg.asker)
                        return 1
                else:
                    if typical_tuple not in Routing_table:
                        self.output_file.write('\tWrong ARP DROPPED\n')
                        return 0
                    if msg.ttl > Routing_table[typical_tuple].ttl:
                        Routing_table[reverse_tuple].next = msg.src_id
                        Routing_table[typical_tuple].ttl = msg.ttl

                        msg.packet_id = get_id()
                        msg.ttl -= 1
                        msg.src_id = self.node_id
                        msg.dst_id = Routing_table[typical_tuple].next

                        self.output_file.write('\tARP response with ttl {} accepted and tell {}\n'.format(msg.ttl,
                                                                                                          msg.dst_id))
                        self.send_msg(msg)
                        return 0

    def add_id(self, msg_id):
        self.rec_msgs.append(msg_id)

    def send_msg(self, msg):
        self.add_id(msg.packet_id)
        self.net.broadcast(msg)

    def send_arp_queue(self, dst):
        if dst not in ARP_QUEUE or len(ARP_QUEUE) == 0:
            return
        self.send_msg(ARP_QUEUE[dst][0])