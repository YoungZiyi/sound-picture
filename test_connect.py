import socket
import time

ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSock.bind(("", 6001))
ServerSock.listen(15)
(NewSock, addr) = ServerSock.accept()

time.sleep(5)

print "connect to ", addr
print "sending..."

sendLength = NewSock.send("51 c0 01 12")

time.sleep(5)

print "sending %s bytes successfully" % (sendLength)
print "recving..."

getMsg = NewSock.recv(1024)

print "get it: %s" % (getMsg)