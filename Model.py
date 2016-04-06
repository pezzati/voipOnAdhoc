from struct import pack
import struct

MESSAGE_TYPE = {0: 'Exit', 1: 'Text', 2: 'ARP'}
BROADCAST = 255
last_id = 0


class Message():
    def __init__(self, packet_id=0, msg_type=0, src_id='0', dst_id='0', status=0, content=''):
        self.packet_id = packet_id
        self.type = msg_type
        self.src_id = src_id
        #self.scr_id_len = len(str(src_id))
        self.dst_id = dst_id
        self.target_id = dst_id
        #self.dst_id_len = len(self.dst_id)
        self.status = status
        self.msg_len = len(str(content))
        self.payload = content
        self.ttl = 255
        self.asker = self.src_id

    def get_packed(self):
        if MESSAGE_TYPE[self.type] != 'ARP':
            data = pack('!IBBBBH', self.packet_id, self.type, self.src_id, self.dst_id, self.status, self.msg_len)
            data += str(self.payload).encode('utf-8')
        else:
            #if self.status == 0:
            data = pack('!IBBBBBBB', self.packet_id, self.type, self.src_id, BROADCAST, self.status, self.ttl,
                        self.asker, self.target_id)
            #if self.status == 1:
            #    data = pack('!IBBBBBBB', self.packet_id, self.type, self.src_id, BROADCAST, self.status, self.ttl,
            #                self.target_id, self.asker)
        return data

    def build_by_data(self, data):
        top_header = data[:6]
        packet_id, msg_type = struct.unpack('!IB', top_header)
        if MESSAGE_TYPE[msg_type] == 'ARP':
            header = data[6:11]
            source, dst, sts, ttl, asker, target = struct.unpack('!BBBBBB', header)
            self.type = msg_type
            self.src_id = source
            self.dst_id = dst
            self.status = sts
            self.ttl = ttl
            self.asker = asker
            self.target_id = target
        else:
            header = data[6:10]
            source, dst, sts, length = struct.unpack('!BBBH', header)
            body = data[10:10 + length]
            self.type = msg_type
            self.msg_len = length
            self.src_id = source
            self.dst_id = dst
            self.status = sts
            self.payload = body.decode('utf-8')

    def __str__(self):
        if MESSAGE_TYPE[self.type] != 'ARP':
            return '{} message from {}: {}'.format(MESSAGE_TYPE[self.type], self.src_id, self.payload)
        return 'Who knows where is {}? Tell {}'.format(self.dst_id, self.src_id)


class IDInfo():
    def __init__(self, base):
        self.base_id = base

    def build_id(self, given_id):
        res = int(given_id)
        res <<= 24
        res += self.base_id
        self.base_id += 1
        return res


class RoutingNode(object):
    def __init__(self, source, destination, ttl, next):
        #self.target = target
        #self.asker = asker
        #self.ttl_asker = ttl_asker
        #self.ttl_target = ttl_target
        #self.next_asker = next_asker
        #self.next_target = next_target
        self.src = source
        self.dst = destination
        self.ttl = ttl
        self.next = next


#
#class RoutingTempNode(object):
#    def __init__(self, target, ttl, tells):
#        self.target = target
#        self.asker
#        self.ttl = ttl
#        self.tells = tells