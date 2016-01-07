# -*- coding: utf-8 -*-
#!/usr/bin/env python

import socket
import select
from struct import pack, unpack
import signal
import pdb

from Message import *
from Device import *
from BxtException import *
from MessageHandler import *
import RunningMode
import binascii
from BxtLogger import *




def main():
	listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSock.bind(("", SERVER_PORT))
	listenSock.listen(15)
	listenSock.setblocking(1)
	#TODO  此处要设置默认socket超时时间

	readlist = [listenSock]
	exceptionlist = [listenSock]
	while not RunningMode.flag_exit:
		(sread, swrite, sexc) =  select.select(readlist, [], exceptionlist, RunningMode.checkInterval); 
		#TODO 此处可以加上定时任务.
		checkTime = time.time()
		for device in IP_Device_Map.values():
			if(checkTime - device.status_start_time > RunningMode.timeoutTime):
				#该设备维持一个状态超过了15s
				if(device.status in [S_RECVING]):
					print "WARN: reset [%s] " % device.name
					print device
					device.SendInstruction(INSTRUCTION_DEVICE_RESET)
					device.Reset()
		
		for sock in sread:
			try:
				if sock == listenSock:
					#收到一个新的TCP连接请求
					(newsock, address) = listenSock.accept()
					newsock.setblocking(1)
					print "ACCEPT a connection from ", address
					client_ip = address[0]
					client_port = address[1]
					#马上发送一个复位指令
					newsock.send(INSTRUCTION_DEVICE_RESET)
					
					#此处假定一次能收到整个包, 基本是成立的
					recv_buff = newsock.recv(RunningMode.recv_buff_size)
	
					#如果处于debugging模式，则socket客户端头部会发送一个IP地址， 以替换127.0.0.1
					if(RunningMode.debugging):
						client_ip = socket.inet_ntoa(recv_buff[:4])
						recv_buff = recv_buff[4:]
						print "Now client_ip is ", client_ip, " and recv_buff is ", ' '.join(x.encode('hex') for x in recv_buff)
					
					#包不合法, 扔弃, 但是不断开TCP连接
					if(not verifyPacket(recv_buff)):
						print "WARN: Invalid Packet from [%s]" % (client_ip)
						continue
					current_device = getDeviceByIP(client_ip)
					if(not current_device):
						print "No valid device to this address [%s]"%client_ip
						newsock.close()
						continue
					else:
						#手工处理初始化状态
						current_device.sock = newsock
						current_device.ChangeStatusTo(S_IDLE)
						#select监听这个socket
						readlist.append(newsock)
						exceptionlist.append(newsock)
						print "Accept socket for device ", current_device.name
				else:
					print "msg from client"
					#业务socket发送的消息
					current_device = getDeviceBySocket(sock)
					if(not current_device):
						print "unknown msg from unknown source"
						readlist.remove(sock)
						exceptionlist.remove(sock)
						sock.close()
						continue
					recv_buff = sock.recv(8)
					if recv_buff == "":
						print "Client %s closed the connection" % (current_device.name)
						current_device.sock = None
						readlist.remove(sock)
						exceptionlist.remove(sock)
						sock.close()
						continue
					
					#如果处于debugging模式，则socket客户端头部会发送一个IP地址， 以替换127.0.0.1
					if(RunningMode.debugging):
						client_ip = socket.inet_ntoa(recv_buff[:4])
						recv_buff = recv_buff[4:]
						
					#包不合法, 扔弃, 但是不断开TCP连接
					if(not verifyPacket(recv_buff)):
						print "WARN: Invalid Packet from [%s:%s]" % (current_device.name, client_ip)
						continue
					
					hex_msg = ' '.join(x.encode('hex') for x in recv_buff)
					print "Client %s sent: [%s] "% (current_device.name, hex_msg)
					
					#真正的业务处理在这里
					handle_msg(current_device, hex_msg)
			except BxtException, e:
				print e
				continue

		for sock in sexc:
			try:
				if sock == listenSock:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					print "Too bad, the listen socket is broken"
					RunningMode.flag_exit = True
				else:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					print "socket ", sock, "is broken "
					sock.close()
					readlist.remove(sock)
					exceptionlist.remove(sock)
			except BxtException:
				continue

				

	
if __name__ == "__main__":
	
	signal.signal(signal.SIGINT, RunningMode.signal_handler)
	main()




	
