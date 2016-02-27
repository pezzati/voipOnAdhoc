from struct import pack
import struct

MESSAGE_TYPE = {0: 'Exit', 1: 'Text'}
last_id = 0

class Message():
    def __init__(self, my_id='0', msg_type=0, content=''):
        self.type = msg_type
        my_id += '_'
        my_id += str(last_id)
        last_id += 1
        self.owner_id = str(my_id)
        self.id_len = len(str(my_id))
        self.msg_len = len(str(content))
        self.payload = str(content)

    def get_packed(self):
        data = pack('!BII', self.type, self.id_len, self.msg_len)
        data += self.owner_id.encode('utf-8')
        data += self.payload.encode('utf-8')
        return data

    def build_by_data(self, data):
        header = data[:9]
        msg_type, id_length, msg_length = struct.unpack('!BII', header)
        #print('type:{} length:{}'.format(msg_type, id_length))
        owner_id = data[9:id_length + 9]
        #print(owner_id.decode("utf-8"))
        body = data[id_length + 9:id_length + 9 + msg_length]
        #print(body.decode('utf-8'))
        self.type = msg_type
        self.msg_len = msg_length
        self.owner_id = owner_id.decode("utf-8")
        self.id_len = id_length
        self.payload = body.decode('utf-8')
        #return Message(owner_id.decode("utf-8"), msg_type, body.decode('utf-8'))

    def __str__(self):
        return '{} message from {}: {}'.format(MESSAGE_TYPE[self.type], self.owner_id, self.payload)


class ID_info():
    def __init__(self, base):
        self.base_id = base

    def build_id(self, given_id):
        res = str(given_id)
        res += '-'
        res += str(self.base_id)
        self.base_id += 1
        return res

    def extract_id(self, given_id):
        return given_id.split('-')