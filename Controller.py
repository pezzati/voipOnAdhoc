from Network import *
from Model import *
import sys

main_id = sys.argv[1]
main_port = 54545
if len(sys.argv) > 2:
    main_port = int(sys.argv[1])
net=Network(54545)
#net.broadcast(Message(my_id=6524, msg_type=1, content='peyman ezzati').get_packed())
#net.send('192.168.199.77',Message(my_id=6524, msg_type=1, content='direct').get_packed())
listener = Listener(name='listener', port_num=main_port, my_id=main_id)
listener.start()