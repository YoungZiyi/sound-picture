# -*- coding: utf-8 -*-

import SocketServer 
import thread
import socket
import time
from bxtcommon import *
import string

class MyRequestHandler(SocketServer.BaseRequestHandler): 
	def handle(self):
		print 'Connected from ', self.client_address
		while 1:
			event = self.request.recv(1024)
			client_address = self.client_address
			client_ip = client_address[0]
			client_port = client_address[1]
			
			if(client_ip == "127.0.0.1"):
				#TODO The localhost client is debugging, Use the identifier in the msg header
				pass
			print "recv [%s] from [%s] \t"% (client_ip, event)
			
			#Get the device object to this IP address
			current_device = getDeviceByIP(client_ip)
			if(not current_device):
				print "No valid device to this address [%s]"%client_ip
				continue
			previous_device = current_device.previous
			if(event == None):
				print "No valid msg from this address [%s]"%client_ip
				continue
			if(event == "reset"):
				print "Command [reset] is received"
				self.server.shutdown()
				break
			# 工作原理：
			# 设备根据各种 感应器/测试元件 反馈的信号向服务器发送相关协议码（主动）
			# 服务器根据设备发来的信号根据业务逻辑反馈相关的协议码（被动）
			# 服务器发送查询设备状态协议码（主动）
			# 设备根据服务器发送的协议码做出相应的动作或反馈（被动）

			# 接驳台0：	初始化状态为 空闲/正常->服务器记录设备状态为 STATUS_AVAILABLE
			#				收到服务器指令（设备当前状态查询 51 c4 00 15）->表示服务器主动发送查询协议码->发送（空闲/准备好接板52 c4 01 17）
			#				前激光感应器反馈信号->表示正在接板->发送 ？->（此处应记录设备状态为 STATUS_RECVING）
			#				收到服务器指令（设备当前状态查询 51 c4 00 15）->表示服务器主动发送查询协议码->发送 ？
			#				前激光感应器停止反馈->表示接板完成->发送（接板完成 52 c4 02 18/52 c1 f1 04 ？）->服务器记录设备状态为 STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			#				收到服务器指令（设备当前状态查询 51 c4 00 15）->表示服务器主动发送查询协议码->发送（准备好了送板52 c4 05 1b）
			#				收到服务器指令（设备向前送板 51 c1 00 12）->表示服务器命令设备开始送板
			#				后激光感应器反馈信号->表示正在送板->发送 ？->（此处应记录设备状态为 STATUS_SENDING）
			#				收到服务器指令（设备当前状态查询 51 c4 00 15）->表示服务器主动发送查询协议码->发送 ？
			#				后激光感应器停止发聩->表示送板完成->发送（送板完成 52 c4 06 1c/52 c1 f2 05 ？）->服务器记录设备状态为 STATUS_AVAILABLE

			# 握手反馈
			if (event == EVENT_SHAKEHANDS_RES):
				# 当前设备握手正常，处于正常/空闲
				# 设置状态为STATUS_AVAILABLE
				current_device.status = STATUS_AVAILABLE
			# 调宽反馈
			elif (event == EVENT_SETWIDTH_RES):
				# 当前设备调宽正常，回归正常/空闲
				# 设置状态为STATUS_AVAILABLE
				current_device.status = STATUS_AVAILABLE
			# 复位后返回当前状态
			elif (event == EVENT_RESET_STATUS_RES):
				# 当前设备复位正常，回归正常/空闲
				# 设置状态为STATUS_AVAILABLE
				current_device.status = STATUS_AVAILABLE
			# 空闲/正常 or 送板完成 or 准备好接(OK/NG)板
			elif(event == EVENT_AVAILABLE or event == EVENT_COMMON_AVAILABLE or event == EVENT_COMMON_SENDITEM_FINISHED or event == EVENT_SENDITEM_FINISHED or event == EVENT_READYFOR_GETITEM_OK or event == EVENT_READYFOR_GETITEM_NG):
				current_device.status = STATUS_AVAILABLE;
				previous_device = current_device.previous;
				if(previous_device.status == STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE):
					sendToPeer(previous_device, IST_SENDITEM)
					previous_device.status = STATUS_SENDING
					current_device.status = STATUS_RECVING
			# 接板完成
			elif (event == EVENT_GETITEM_FINISHED):
				current_device.status = STATUS_BUSY
			# 缓存机接板完成
			elif (event == EVENT_HUANCUNJI_GETITEM_FINISHED):
				current_device.status = STATUS_BUSY
			# 缓存机接板忙
			elif (event == EVENT_HUANCUNJI_BUSY):
				current_device.status = STATUS_BUSY
				previous_device = current_device.previous
				previous_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			# 缓存机接板故障
			elif (event == EVENT_HUANCUNJI_GETITEM_ERROR):
				current_device.status = STATUS_BROKEN
				previous_device = current_device.previous
				previous_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			# 已到达中间准备好接板
			elif (event == EVENT_READYFOR_GETITEM_MIDDLE):
				current_device.status = STATUS_AVAILABLE
			# 已到达左端准备好接板
			# 已到达右端准备好接板
			# 测试中

			
			# 测试OK，准备送板
			elif (event == EVENT_READYFOR_SENDITEM_OK):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, HUANCUNJI_GETITEM_OK)
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			# 测试NG，准备送板
			elif (event == EVENT_READYFOR_SENDITEM_NG):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, HUANCUNJI_GETITEM_NG)
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			# 准备送板
			elif (event == EVENT_COMMON_READYFOR_SENDITEM):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, IST_SENDITEM)
					current_device.status = STATUS_SENDING
					next_device.status = STATUS_RECVING
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			elif event == "YIZAI_PrepareGetItemFinish":
				response = "FT01_GiveItem"
			elif event == "FT01_GiveItemFinish":
				item = ft01.popItem()
				yizai.pushItem(item)
				#Here we should check if thers is a item with the ft01
				if(item.status == "OK"):
					response = "YIZAI_Move_LEFT"
				else:
					response = "YIZAI_Move_RIGHT"
			elif ("SBJ_PrepareGetItemFinish" in event):
				response = "YIZAI_GiveItem"
			else:
				response = "UNKNOWN MESSAGE: "
				response += event
			self.request.sendall(response)

def InitDeviceList():
	Connect(None, device_jbt0)
	Connect(device_jbt0, device_ict)
	Connect(device_ict, device_hcj)
	Connect(device_hcj, device_jbt1)
	Connect(device_jbt1, device_ft)
	Connect(device_ft, device_yz)
	Connect(device_yz, device_ngsbj)
	Connect(device_yz, device_oksbj)
	Connect(device_ngsbj, None)
	Connect(device_oksbj, None)


if __name__ == "__main__":
	print 'To define global variables'
	


	InitDeviceList()
	
	print 'To start TCPServer'
	ADDR = (SERVER_HOST, SERVER_PORT)
	tcpServ = SocketServer.ThreadingTCPServer(ADDR, MyRequestHandler) 
	print 'Waiting for connection'
	tcpServ.serve_forever()
	
	print "I am quitting"
	tcpServ.server_close()
	