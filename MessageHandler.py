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
			# 空闲
			current_device.ChangeStatusTo(S_IDLE)
		elif (event == EVENT_GETITEM_FINISHED):
			# 板子碰到接驳台左端感应器发“接板完成”消息，并设为有板状态
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif (event == EVENT_READYFOR_SENDITEM):
			# 板子碰到接驳台左端感应器发“准备好送板”消息，并设为准备好送板状态
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 如果下一个设备的状态为空闲或准备好接板，则给接驳台发送板指令
			if (next_device.status in [S_IDLE, S_READY_TO_RECV_ITEM]):
				current_device.SendInstructionSendItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			# 当板子离开接驳台右端感应器时发“送板完成”消息，并设为空闲状态
			current_device.ChangeStatusTo(S_IDLE)
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_ict):
		#TODO ICT
		if (event == EVENT_AVAILABLE):
			# 空闲消息
			current_device.ChangeStatusTo(S_IDLE)
			# 只要ICT处于空闲状态，以及接驳台处于准备好送板状态，就给接驳台发送板指令
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_GETITEM_FINISHED):
			# 板子离开ICT接驳台左端感应器发“接板完成”消息，并把ICT状态设为有板状态
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# ICT测试板子OK发“测试OK 准备送板”消息
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_OK
			item_status = ITEM_STATUS_OK
			current_device.changItemStatusTo(item_status)
			# 给缓存机发“缓存机向后接OK板”指令
			next_device.SendInstructionPrepareToRecvItem()
		elif (event == EVENT_READYFOR_SENDITEM_NG):
			# ICT测试板子NG发“测试NG 准备送板”消息
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_NG
			item_status = ITEM_STATUS_NG
			current_device.changItemStatusTo(item_status)
			# 给缓存机发“缓存机向后接NG板”指令
			next_device.SendInstructionPrepareToRecvItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			# 板子离开ICT测试机箱右端感应器发“送板完成”消息，设状态为空闲
			current_device.ChangeStatusTo(S_IDLE)
			# 机器空闲时检查前一个设备的状态是否为“准备好送板”，如果是，则给前一个设备发“送板指令”
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_hcj):
		if (event == EVENT_AVAILABLE):
			# 空闲，将缓存机状态设为空闲，并检查前一个设备是否处于准备好送板状态
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_READYFOR_GETITEM):
			# ICT给缓存机发“缓存机向后OK/NG板”，缓存机回复准备好接板，将缓存机状态设为准备好接板
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			# 检查前一个设备是否处于准备好送板状态，如果是，给它发送板指令
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_READYFOR_SENDITEM):
			# TODO 如果是NG板，缓存完毕后没有任何消息给出，如何修改缓存机状态？
			# 板子走到缓存接驳台右端感应器发“准备送板”消息，将缓存机状态设为准备好送板
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 检查下一个设备是否处于准备好接板或空闲状态，if so，给缓存机发送板指令
			if (next_device.status in [S_IDLE, S_READY_TO_RECV_ITEM]):
				current_device.SendInstructionSendItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			# 板子离开缓存接驳台右端感应器发“送板完成”消息，将缓存机状态设为空闲
			current_device.ChangeStatusTo(S_IDLE)
			# 检查前一个设备是否处于准备好送板状态
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_DEVICE_WARNING_2):
			# TODO 设备紧急停止
			print "device stoped!"
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_ft):
		# FT flow
		if (event == EVENT_AVAILABLE):
			# 空闲
			current_device.ChangeStatusTo(S_IDLE)
			# 只要FT处于空闲状态，以及缓存机处于准备好送板状态，就给缓存机发送板指令
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif (event == EVENT_GETITEM_FINISHED):
			# 板子离开FT接驳台左端感应器发“接板完成”消息，并把FT状态设为有板状态
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# FT测试板子OK发“测试OK 准备送板”消息
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_OK
			item_status = ITEM_STATUS_OK
			current_device.changItemStatusTo(item_status)
			# 给移载机发 到中间向后接板指令
			next_device.SendInstructionPrepareToRecvItem()
		elif (event == EVENT_READYFOR_SENDITEM_NG):
			# FT测试板子NG，给移载机发 到中间向后接板指令
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_NG
			item_status = ITEM_STATUS_NG
			current_device.changItemStatusTo(item_status)
			# 给移载机发 到中间向后接板指令
			next_device.SendInstructionPrepareToRecvItem()
		elif (event == EVENT_SENDITEM_FINISHED):
			# 板子离开FT测试机箱右端感应器发“送板完成”消息，设状态为空闲
			current_device.ChangeStatusTo(S_IDLE)
			# 机器空闲时检查前一个设备的状态是否为“准备好送板”，如果是，则给前一个设备发“送板指令”
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		else:
			print "Event [%s] is not recognized for device [%s]" % (event, current_device.name)
	elif (current_device == device_yz):
		# YZ flow
		if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE]):
			# 空闲，将移载机状态设为空闲，并检查前一个设备是否处于准备好送板状态
			current_device.ChangeStatusTo(S_IDLE)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		elif(event == EVENT_READYFOR_GETITEM_LEFT):
			# 移栽机报告已经到达中间
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
					current_device.SendInstructionSendItem()
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




		
		
		
		
		