# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pdb

from Message import *
from Device import *
from BxtException import *
from BxtLogger import *

def handle_msg(current_device, event):
	#TODO
	'''
		1. 每个设备都要处理 EVENT_AVAILABLE消息
	'''
	previous_device = current_device.previous
	next_device = current_device.next
	
	# TODO STATUS_BUSY
	if (event == RES_STATUS_BUSY):
		if(current_device not in [device_sbjok, device_sbjng]):
			#RES_STATUS_BUSY is discarded 
			return
	
	if (current_device == device_jbt0):
		# Handle message sent from Jiebotai0
		if (event == EVENT_AVAILABLE):
			#writeInfo("[%s]EVENT->EVENT_AVAILABLE"%current_device.name)
			current_device.ChangeStatusTo(S_IDLE)
		elif (event == EVENT_GETITEM_FINISHED):
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif (event == EVENT_READYFOR_SENDITEM):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			if (next_device.status in [S_IDLE, S_READY_TO_RECV_ITEM]):
				current_device.SendInstructionSendItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			current_device.ChangeStatusTo(S_IDLE)
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_ict):
		#TODO ICT
		if (event == EVENT_AVAILABLE):
			current_device.ChangeStatusTo(S_IDLE)
			# 只要ICT处于空闲状态，以及接驳台处于准备好送板状态，就给接驳台发送板指令
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		if (event == EVENT_GETITEM_FINISHED):
			# 只要ICT收板完成，就把ICT状态设为准备好送板
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
		if (event EVENT_SENDITEM_FINISHED):
			# 刘工说ICT送板完成后会发空闲消息
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()


		
	elif (current_device in [device_ict, device_ft]):
		if (event == EVENT_ASK_FOR_ITEM):
			#测试机自己有Cache, 可能在任何一个状态中, 主动问板子
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				#备份当前设备的状态
				current_status = current_device.status
				current_item_status = current_device.item_status
				#这个函数会改变当前设备的状态
				previous_device.SendInstructionSendItem()
				#恢复原先的状态
				current_device.ChangeStatusTo(current_status)
				current_device.ChangeItemStatusTo(current_item_status)
		elif (event in [EVENT_AVAILABLE, EVENT_SENDITEM_FINISHED, RES_STATUS_AVAILABLE, RES_STATUS_SENDITEM_FINISHED]):
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event in [EVENT_GETITEM_FINISHED, EVENT_TESTING]):
			current_device.ChangeStatusTo(S_TESTING)
		elif (event in [EVENT_READYFOR_SENDITEM_OK, EVENT_READYFOR_SENDITEM_NG]):
			# 测试机器已经测试完毕一块板子
			if(current_device.status == S_READY_TO_SEND_ITEM):
				#上一块板子还没送出去
				print "WARN: One more item testing finished when the last item has not been sent in device [%s]" % current_device.name
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			item_status = ITEM_STATUS_NG
			if(event == EVENT_READYFOR_SENDITEM_OK):
				item_status = ITEM_STATUS_OK
			current_device.changItemStatusTo(item_status)
			if (next_device.status in [S_IDLE, S_PREPARING_TO_RECV, S_HALF_READY_TO_RECV_ITEM]):
				if(next_device.status == S_PREPARING_TO_RECV):
					print "WARN: YZ is preparing right now"
				# 移栽机空闲之后会处于S_HALF_READY_TO_RECV_ITEM状态, 以节省时间.
				# 此处我们暂不实现在缓存机的优化
				next_device.SendInstructionPrepareToRecvItem()
			elif (next_device.status == S_READY_TO_RECV_ITEM):
				'''
					测试机刚刚测试好, 还没发指令让下一个机器准备, 下一个机器就已经准备好了, 那就直接送板吧.
					这种情况可能发生在如下场景:
					1. 前面的移栽机/缓存机正在准备接板, 
					2. 测试机上的板子被人手工拿走了,
					3. 测试机给服务器发送一个"送板完成"的消息, 
					4. 服务器指挥测试机继续测试,
					5. 移栽机/缓存机准备完毕, 
					6. 测试机测试完毕, 发现前面的移栽机/缓存级已经准备好了
					TODO 需要确认该场景的可能性, 以及item_status在传递的时候能否保持正确.
				'''
				current_device.SendInstructionSendItem()
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_hcj):
		if (event == EVENT_AVAILABLE):
			# 空闲，将缓存机状态设为空闲，并检查前一个设备是否处于准备好送板状态
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_READYFOR_GETITEM):
			# 准备好接板，将缓存机状态设为准备好接板，并检查前一个设备是否处于准备好送板状态
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_READYFOR_SENDITEM):
			# 准备送板，将缓存机状态设为准备好送板，并检查下一个设备是否处于准备好接板或空闲状态
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			if (next_device.status in [S_IDLE, S_READY_TO_RECV_ITEM]):
				current_device.SendInstructionSendItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			# 送板完成，将缓存机状态设为空闲，并检查前一个设备是否处于准备好送板状态
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_DEVICE_WARNING_2):
			# TODO 设备紧急停止
			print "device stoped!"
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_yz):
		#移栽机的流程
		if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE]):
			#EVENT_AVAILABLE只在启动的时候发送
			current_device.ChangeStatusTo(S_IDLE)				
		elif(event == EVENT_READYFOR_GETITEM_RIGHT):
			#移栽机报告已经到达右边
			if(current_device.status != S_PREPARING_TO_RECV):
					print "WARN: yz [%s] report EVENT_READYFOR_GETITEM_RIGHT from status [%d]" % (current_device.name, current_device.status)
			if(current_device.prepare_count == 1):
				#第一次到达算HALF_READY, 第二次才算READY
				current_device.ChangeStatusTo(S_HALF_READY_TO_RECV_ITEM)
				if(previous_device.status == S_READY_TO_SEND_ITEM):
					#后面的机器在等待, 需要马上来第二次
					current_device.SendInstructionPrepareToRecvItem()
			elif(current_device.prepare_count == 2):
				#移栽机第二次报告已经到达右边
				current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
				if(previous_device.status != S_READY_TO_SEND_ITEM):
					#TODO 确认下如果后面的机器没有READY_TO_SEND, 怎么处理?
					print "WARN: yizaiji is ready to recv item, but the FT is not ready to send item. anybody steal the item?"
				else:
					#让后面的机器送板
					previous_device.SendInstructionSendItem()
		elif(event==EVENT_GETITEM_FINISHED):
			#移栽机收到板子, 默认送去NG收板机
			#TODO 此处要判断前面的对应板子状态的接板机是否空闲
			ok_idle = (current_device.item_status == ITEM_STATUS_OK and device_sbjok.status == S_IDLE)
			ng_idle = (current_device.item_status == ITEM_STATUS_NG and device_sbjng.status == S_IDLE)
			if(ok_idle or ng_idle):
				current_device.SendInstructionSendItem()
		elif(event==EVENT_SENDITEM_FINISHED):
			if(current_device.status != S_SENDING):
				print "WARN: [%s]'s status jumped from [%d] to S_IDLE" %(current_device.name, current_device.status)
			current_device.ChangeStatusTo(S_IDLE)
			#移栽机把板子送走了, 应该让它马上准备接板, 以优化效率
			current_device.SendInstructionPrepareToRecvItem()
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device in [device_sbjok, device_sbjng]):
		if(event == RES_STATUS_BUSY):
			#TODO 收板机最好不要只给BUSY指令, 而是给一个开始收板指令
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif(event == EVENT_AVAILABLE):
			current_device.ChangeStatusTo(S_IDLE)
		else:
			print "Event [%s] is not recognized for device [%s]" % [event, current_device.name]
	else:
		print "Device is not recognized %s" % device.name




		
		
		
		
		