# -*- coding: utf-8 -*-
#!/usr/bin/env python
import socket
import time
import binascii
from Message import *
'''
send_msg = covert2Hex(INSTRUCTION_DEVICE_RESET)
print send_msg
exit('bye')
'''
listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSock.bind(("", 6001))
listenSock.listen(15)

(newsock, address) = listenSock.accept()
newsock.setblocking(1)
print "ACCEPT a connection from ", address
client_ip = address[0]
client_port = address[1]
#马上发送一个复位指令
send_msg = covert2Hex(INSTRUCTION_DEVICE_RESET)
newsock.send(send_msg)

recv_buff = newsock.recv(4)

print recv_buff
for x in recv_buff:
	print x.encode("hex")

#print join(x.encode('hex') for x in recv_buff)
newsock.close()
print "bye"