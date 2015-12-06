#!/usr/bin/env python 
from socket import *
import string
from struct import pack, unpack
import socket
import signal
from Message import *


socket.setdefaulttimeout(3)

exit_flag = False
def signal_handler(signum, frame):
	global exit_flag
	exit_flag = True
	print "receive a signal %d, exit_flag = %d"%(signum, is_exit)
signal.signal(signal.SIGINT, signal_handler)

BUFSIZ = 1024
ADDR = (SERVER_HOST, SERVER_PORT) 

tcpCliSock = socket.socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
print "Connecting..."


print "Recving..."
recved = tcpCliSock.recv(BUFSIZ)
print "Recv ", recved.strip()
	
data = raw_input('> ')
if not data:
	print "No data to send"
	exit(-1)
ip_in_int = unpack("!I", socket.inet_aton(data))[0];
ip_in_str = pack("!i",ip_in_int)
hex_msg = ':'.join(x.encode('hex') for x in ip_in_str)
print hex_msg
tcpCliSock.send(ip_in_str)
	
while(not exit_flag):
	data = raw_input('> ')
	if not data:
		print "No data to send"
		break
	tcpCliSock.send(data)

print "Exiting..."
tcpCliSock.close()
