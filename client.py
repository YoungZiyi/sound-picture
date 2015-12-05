#!/usr/bin/env python 
from socket import *
from bxtcommon import *
import string
from struct import pack, unpack
import socket

BUFSIZ = 1024
ADDR = (SERVER_HOST, SERVER_PORT) 

tcpCliSock = socket.socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
print "Connecting..."

while(1):
    data = raw_input('> ') 
    if not data: 
    	print "No data to send"
        break 
    #ip = "10.0.0.100"
    #ip_in_int = unpack("!I", socket.inet_aton(ip))[0];
    #ip_in_str = pack("!i",ip_in_int)
    #print type(ip_in_str)
    #data = ip_in_str+data
    tcpCliSock.send(data)
    #recved = tcpCliSock.recv(BUFSIZ)
    #print recved.strip()

print "Exiting..."
tcpCliSock.close()
