# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pdb

from Message import *
from Device import *
from BxtException import *

def handle_msg(current_device, event):
		previous_device = current_device.previous
		next_device = current_device.next
		# 空闲状态，或者送板完成状态
		if(event == EVENT_AVAILABLE or event == STATUS_AVAILABLE or event == STATUS_SENDITEM_FINISHED or event == EVENT_SENDITEM_FINISHED):
			current_device.status = S_AVAILABLE
			#如果上一个设备在等待本设备， 此时我们可以开始上一个设备往本设备送板的动作了
			if(previous_device.status == S_WAITING):
				if(current_device == device_yz):
					#如果本设备是移栽机， 则需要先让本设备移动到右边
					current_device.SendInstruction(YIZAI_MOVE_RIGHT_AND_RECV_ITEM)
					current_device.status = S_MOVING
				elif(current_device == device_hcj):
					#如果本设备是缓存机，则需要先辨别上一个设备的板子是OK还是NG的， 以给本设备发送不同的指令
					if(previous_device.item_status == ITEM_STATUS_OK):
						current_device.SendInstruction(INSTRUCTION_HUANCUNJI_GETITEM_OK)
						current_device.status = S_RECVING
					elif(previous_device.item_status == ITEM_STATUS_NG):
						current_device.SendInstruction(INSTRUCTION_HUANCUNJI_GETITEM_NG)
						current_device.status = S_RECVING
					else:
						print "ERROR. Item status is unknow. [%d]" % ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN
						current_device.status = ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN
				else:
					#对于其他设备，让上一个设备直接送板
					previous_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					current_device.status = S_RECVING
		elif (event == EVENT_SHAKEHANDS_RES):
			# 当前设备握手正常
			pass
		elif (event == EVENT_SETWIDTH_RES):
			# 当前设备调宽正常
			pass
		elif (event == STATUS_GETITEM_FINISHED):
			# 如果是接驳台，那就看下一个设备的状态，如果下一个设备的状态为AVAILABLE，就给当前设备发一个设备向前送板指令
			# 缓存机有单独的接板完成指令
			# 如果是移载
			# 结论：识别设备，做出相应的反馈
			# 问题：如何识别设备（根据ip地址）
			# 当前设备接板完成（忙碌）
			current_device.status = S_WITH_ITEM
			if(current_device == device_yz):
				if(current_device.item_status == ITEM_STATUS_NOT_KNOWN):
					raise ExceptionItemStatusUnknown("device_yz")
				elif(current_device.item_status == ITEM_STATUS_OK):
					current_device.SendInstruction(YIZAI_MOVE_RIGHT_AND_SEND_ITEM)
				else:
					current_device.SendInstruction(YIZAI_MOVE_LEFT_AND_SEND_ITEM)
			current_device.status = S_WAITING
		elif (event == STATUS_TESTING):
			# 当前设备测试中
			current_device.status = S_TESTING
		elif (event == STATUS_BROKEN):
			# 当前设备处于故障状态
			current_device.status = S_BROKEN
		elif (event == STATUS_READYFOR_SENDITEM):
			# 当前设备测试完成准备送板
			current_device.status = S_WAITING
		elif (event == STATUS_BUSY):
			# 当前设备忙碌
			current_device.status = S_BUSY
		# 缓存机接板完成/空闲
		elif (event == EVENT_HUANCUNJI_GETITEM_FINISHED):
			# 缓存机接板完成/空闲？难道说缓存机接板完成立即变成空闲状态？
			# 缓存机还有好多疑问，按顺序来应该走ICT，先空着这里
			# 准备好接OK板
			pass
		elif (event == EVENT_READYFOR_GETITEM_OK or event == EVENT_READYFOR_GETITEM_NG):
			#缓存机准备接收来自ICT机的OK/NG的板子
			#这是对 INSTRUCTION_HUANCUNJI_GETITEM_OK/NG 的响应
			assert (previous_device == device_ict)
			previous_device.SendInstruction(INSTRUCTION_HUANCUNJI_GETITEM_OK)
		elif (event == EVENT_HUANCUNJI_BUSY):
			current_device.status = S_BUSY;
		elif (event == EVENT_HUANCUNJI_GETITEM_ERROR):
			# 缓存机故障
			current_device.status = S_BROKEN
		
		elif (event == EVENT_READYFOR_GETITEM_MIDDLE):
			# 已到达中间准备好接板
			# 在这个拓扑中不应该有这个消息
			current_device.status = S_BROKEN
			raise ExceptionUnsupportedMsg("EVENT_READYFOR_GETITEM_MIDDLE");
		elif (event == EVENT_READYFOR_GETITEM_LEFT):
			# 已到达左端准备好接板
			# 在这个拓扑中不应该有这个消息
			current_device.status = S_BROKEN
			raise ExceptionUnsupportedMsg("EVENT_READYFOR_GETITEM_MIDDLE");
		elif (event == EVENT_READYFOR_GETITEM_RIGHT):
			# 已到达右端准备好接板
			current_device.status = S_MOVING
		elif (event == EVENT_TESTING):
			# ICT/FT开始测试工作
			# 那么给它们设为TESTING状态
			current_device.status = TESTING
		# 测试OK，准备送板
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# 准备送OK板
			# 要明确通知下一个设备接OK板，并将当前和下一个设备状态设为BUSY
			current_device.item_status = OK
			if(not (next_device.status == S_AVAILABLE)): 
				current_device.status = S_WAITING
			else:
				if(next_device == device_hcj):
					pass
				elif(next_device == device_yz):
					pass
				else:
					current_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					current_device.status = S_SENDING
				next_device.status = BUSY
		# 测试NG，准备送板
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# 准备送NG板
			# 要明确通知下一个设备接NG板，并将当前和下一个设备状态设为BUSY
			if (next_device.status == AVAILABLE):
				sendToPeer(current_device, DEVICE_SENDITEM)
				current_device.status = BUSY
				if (next_device == device_hcj):
					sendToPeer(next_device, HUANCUNJI_GETITEM_NG)
				if (next_device == device_yz):
					sendToPeer(next_device, YIZAI_GETITEM_RIGHT)
				next_device.status = BUSY
		# 准备送板（无测试）
		elif (event == EVENT_READYFOR_SENDITEM):
			pass
			# 无测试怎么通知后一个设备接板？
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_1):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_2):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_3):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_4):
			pass
		# 缓存机未准备好
		elif (event == EVENT_HUANCUNJI_NOTREADY):
			pass
		else:
			response = "UNKNOWN MESSAGE: "
			response += event
		self.request.sendall(response)