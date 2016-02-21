from struct import pack


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
