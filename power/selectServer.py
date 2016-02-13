# -*- coding: utf-8 -*-
#!/usr/bin/env python

import socket
import select
from struct import pack, unpack
import signal
import pdb
import binascii

from Message import *
from Device import *
from BxtException import *
from MessageHandler import *
import RunningMode
from BxtLogger import *




def main():
	writeInfo("The server is starting");
	listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSock.bind(("", SERVER_PORT))
	listenSock.listen(15)
	listenSock.setblocking(0)

	readlist = [listenSock]
	exceptionlist = [listenSock]

	while not RunningMode.flag_exit:
		(sread, swrite, sexc) =  select.select(readlist, [], exceptionlist, RunningMode.checkInterval); 
		checkTime = time.time()
		# check status remains time
		for device in IP_Device_Map.values():
			if(checkTime - device.status_start_time > RunningMode.timeoutTime):
				if(device.status in [S_RECVING]):
					device.SendInstruction(INSTRUCTION_DEVICE_RESET)
					# use ParitialReset so that won't reset the previous and next device
					device.ParitialReset()
		
		for sock in sread:
			try:
				if sock == listenSock:
					#收到一个新的TCP连接请求
					(newsock, address) = listenSock.accept()
					client_ip = address[0]
					client_port = address[1]
					writeInfo("ACCEPT A CONNECTION FROM IP:[%s] PORT:[%s]" % (client_ip, client_port))
					newsock.setblocking(0)
					
					current_device = getDeviceByIP(client_ip)
					if(not current_device):
						writeWarning("INVALID DEVICE TO THIS ADDRESS [%s]" % client_ip)
						newsock.close()
						continue

					#马上发送一个复位指令
					newsock.send(convert2Hex(INSTRUCTION_DEVICE_RESET))
					writeInfo("SERVER sent INSTRUCTION_DEVICE_RESET to [%s]" % (current_device.name))
					current_device.sock = newsock
					current_device.ChangeStatusTo(S_IDLE)
					#select监听这个socket
					readlist.append(newsock)
					exceptionlist.append(newsock)
					writeInfo("ACCEPT SOCKET FOR DEVICE [%s]" % current_device.name)
				else:
					# 通过socket IP地址判断设备
					current_device = getDeviceBySocket(sock)
					if(not current_device):
						writeWarning("UNKNOW SOURCE")
						readlist.remove(sock)
						exceptionlist.remove(sock)
						sock.close()
						continue
					try:
						recv_buff = sock.recv(8)
					except:
						continue
					if recv_buff == "":
						writeWarning("CLIENT [%s] HAS BEEN DISCONNECTED" % (current_device.name))
						current_device.sock = None
						readlist.remove(sock)
						exceptionlist.remove(sock)
						sock.close()
						continue
					
					#如果处于debugging模式，则socket客户端头部会发送一个IP地址， 以替换127.0.0.1
					if(RunningMode.debugging):
						client_ip = socket.inet_ntoa(recv_buff[:4])
						recv_buff = recv_buff[4:]
					
					total_hex_msg = ' '.join(x.encode('hex') for x in recv_buff)
					writeWarning("Total Msg [%s] from [%s]"%(total_hex_msg, current_device.name))
					
					recv_buff_len = len(recv_buff)
					if( recv_buff_len % 4 == 0):
						msg_count = recv_buff_len/4
						for i in range(0, msg_count):
							msg_buff = recv_buff[4*i:4*i+4]
							hex_msg = ' '.join(x.encode('hex') for x in msg_buff)
							writeWarning("Msg[%d] [%s] from [%s]"%(i, hex_msg, current_device.name))
							#真正的业务处理在这里
							handle_msg(current_device, hex_msg)
					else:
						hex_msg = ' '.join(x.encode('hex') for x in recv_buff)
						writeWarning("msg length is invalid [%s]" % (hex_msg))
			except BxtException, e:
				writeWarning(e)
				continue
			except Exception, e:
				writeWarning(e)
				continue

		for sock in sexc:
			try:
				if sock == listenSock:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					writeWarning("TOO BAD, THE LISTEN SOCKET IS BROKEN")
					RunningMode.flag_exit = True
				else:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					writeDebug("SOCKET [", sock, "] IS BROKEN")
					sock.close()
					readlist.remove(sock)
					exceptionlist.remove(sock)
			except BxtException:
				continue

				

	
if __name__ == "__main__":
	
	signal.signal(signal.SIGINT, RunningMode.signal_handler)
	main()
