from apparmor.ui import raw_input
from Network import *
from Model import *
import sys

main_id = sys.argv[1]
main_port = 54545
if len(sys.argv) > 2:
    main_port = int(sys.argv[2])
net = Network(54545)
#net.broadcast(Message(my_id=6524, msg_type=1, content='peyman ezzati').get_packed())
#net.send('192.168.199.77',Message(my_id=6524, msg_type=1, content='direct').get_packed())
listener = Listener(name='listener', port_num=main_port, my_id=main_id, network=net)
listener.start()

id_generate = ID_info(0)
while True:
    cmd = raw_input()
    if cmd != 'Exit':
        msg = Message(id_generate(main_id), msg_type=1, content=cmd)
        net.broadcast(msg.get_packed())
    else:
        msg = Message(id_generate(main_id), msg_type=0, content=cmd)
        net.broadcast(msg.get_packed())
        break
net.terminate()