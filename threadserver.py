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

			# 服务器工作流程：
			# 	被动：
			# 		1.收到设备发来的指令
			# 		2.识别设备？
			# 		3.根据逻辑反馈给设备
			# 	主动：
			# 		1.发送指令到指定设备
			# 		2.接收设备反馈
			# 		

			# 握手反馈
			if (event == EVENT_SHAKEHANDS_RES):
				# 当前设备握手正常
				current_device.status = AVAILABLE
			# 调宽反馈
			elif (event == EVENT_SETWIDTH_RES):
				# 当前设备调宽正常
				current_device.status = AVAILABLE
			# 复位后返回当前状态
			elif (event == STATUS_AVAILABLE):
				# 当前设备空闲
				current_device.status = AVAILABLE
			elif (event == STATUS_GETITEM_FINISHED):
				# 当前设备接板完成（忙碌）
				current_device.status = WAITING
			elif (event == STATUS_TESTING):
				# 当前设备测试中
				current_device.status = TESTING
			elif (event == STATUS_BROKEN):
				# 当前设备处于故障状态
				current_device.status = BROKEN
			elif (event == STATUS_READYFOR_SENDITEM):
				# 当前设备测试完成准备送板
				current_device.status = WAITING
			elif (event == STATUS_SENDITEM_FINISHED):
				# 当前设备送板完成
				current_device.status = AVAILABLE
			elif (event == STATUS_BUSY):
				# 当前设备忙碌
				current_device.status = BUSY
			# 空闲/正常
			elif (event == EVENT_AVAILABLE):
				# 当前设备空闲/正常
				current_device.status = AVAILABLE
			# 接板完成
			elif (event == EVENT_GETITEM_FINISHED):
				# 如果是接驳台，那就看系一个设备的状态，如果下一个设备的状态为AVAILABLE，就给当前设备发一个设备向前送板指令
				# 如果是ICT/FT测试设备，就将当前设备状态设为TESTING（不对！如果是测试设备，那设备开始测试的时候会发一条测试中的指令！）
				# 那么要是是测试设备发送该指令作何处理呢？首先，测试设备接板完成后到测试中间会有一段间隙（必然），这段间隙中的设备状态应当设为忙碌，然后设备会自动开始测试，一旦开始测试，设备就会发送测试中指令给服务器，我们再将它的状态设为TESTING，直到它测试完成发其他指令
				# 暂存机有单独的接板完成指令
				# 移载不需要发接板完成指令
				# 结论：识别设备，做出相应的反馈
				# 问题：如何识别设备
				if (current_device == 接驳台):
					if (next_device.stauts == AVAILABLE):
						sendToPeer(current_device, DEVICE_SENDITEM)
					else:
						current_device.status = WAITING
				elif (current_device == ICT测试):
					current_device.status = BUSY
			# 送板完成
			elif (event == EVENT_SENDITEM_FINISHED):
				# 当前设备送板完成
				# 这个没什么好说的，直接将当前设备状态设为空闲
				current_device.status = AVAILABLE
			# 缓存机接板完成/空闲
			elif (event == EVENT_HUANCUNJI_GETITEM_FINISHED):
				# 缓存机接板完成/空闲？难道说缓存机接板完成立即变成空闲状态？
				# 缓存机还有好多疑问，按顺序来应该走ICT，先空着这里
			# 准备好接OK板
			elif (event == EVENT_READYFOR_GETITEM_OK):
			# 准备好接NG板
			elif (event == EVENT_READYFOR_GETITEM_NG):
			# 缓存机接板忙
			elif (event == EVENT_HUANCUNJI_BUSY):
				# 怎么样才会触发缓存机发送该指令？


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
	