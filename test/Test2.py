import netifaces
from socket import *
import struct


s=socket(AF_INET, SOCK_DGRAM)
s.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
while True:
    data= s.recv(1024)
    print(data)
    header = data[:9]
    msg_type, id_length, msg_length=struct.unpack('!BII', header)
    print('type:{} length:{}'.format(msg_type, id_length))
    owner_id=data[9:id_length+9]
    print(owner_id.decode("utf-8"))
    body=data[id_length+9:id_length+9+msg_length]
    print(body.decode('utf-8'))
    #msg_type, length , content= struct.unpack('!BI', data)
    #print('type:{} length:{}'.format(msg_type, length))
    #body = s.recv(length - 1)
    ##content = struct.unpack('!p', body)
    ##m=s.recvfrom(2048)
    #print(body)
s.close()