from Network import *
from Model import *
import sys
from sys import stdin

main_id = int(sys.argv[1])
main_port = 54545
if len(sys.argv) > 2:
    main_port = int(sys.argv[2])
net = Network(54545)
#net.broadcast(Message(my_id=6524, msg_type=1, content='peyman ezzati').get_packed())
#net.send('192.168.199.77',Message(my_id=6524, msg_type=1, content='direct').get_packed())
listener = Listener(name='listener', port_num=main_port, my_id=main_id, network=net)
listener.start()

id_generate = IDInfo(0)


def get_id():
    return id_generate.build_id(main_id)


while True:
    if listener.terminate:
        break
    cmd = stdin.readline()[:-1]
    if listener.terminate:
        break
    if cmd != 'Exit' and cmd != 'exit':
        #cmd pattern <dst id> <msg>
        cmd_array = cmd.split(' ')
        dst = int(cmd_array[0])
        msg = cmd_array[1]

        msg = Message(packet_id=get_id(), msg_type=1, src_id=main_id, dst_id=dst, content=cmd)
        if dst in ARP_QUEUE:
            ARP_QUEUE[dst].append(msg)
        else:
            ARP_QUEUE[dst] = [msg]

        temp_id = get_id()
        arp_msg = Message(packet_id=temp_id, msg_type=2, src_id=main_id, dst_id=dst)
        listener.add_id(temp_id)
        net.broadcast(arp_msg.get_packed())
    else:
        temp_id = get_id()
        msg = Message(packet_id=temp_id, msg_type=0, src_id=main_id, dst_id=BROADCAST, content=cmd)
        listener.add_id(temp_id)
        net.broadcast(msg.get_packed())
        break
net.terminate()