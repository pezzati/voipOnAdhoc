import netifaces
from socket import *

#print(netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0])
#print(netifaces.gateways()[netifaces.AF_INET][0])

cs = socket(AF_INET, SOCK_DGRAM)
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
cs.bind((netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('addr'), 54545))
cs.sendto('This is a test'.encode(), (netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0].get('broadcast'), 54545))
cs.close()
