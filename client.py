#!/usr/bin/env python 
from socket import *
from bxtcommon import *

BUFSIZ = 1024
ADDR = (SERVER_HOST, SERVER_PORT) 

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
print "Connecting..."

while(1):
    data = raw_input('> ') 
    if not data: 
        break 
    tcpCliSock.send('%s\r\n' % data) 
    data = tcpCliSock.recv(BUFSIZ) 
    print data.strip() 

print "Exiting..."
tcpCliSock.close()