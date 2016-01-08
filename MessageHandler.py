# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pdb

from Message import *
from Device import *
from BxtException import *
from BxtLogger import *

def handle_msg(current_device, event):
	previous_device = current_device.previous
	next_device = current_device.next
	
	# log all event
	writeInfo("CLIENT [%s] SENT: [%s]" % (current_device.name, event))

	# RES_STATUS_BUSY
	if (event == RES_STATUS_BUSY):
		if(current_device not in [device_sbjok, device_sbjng]):
			#RES_STATUS_BUSY is discarded 
			return
	# EVENT_AVAILABLE, RES_STATUS_AVAILABLE
	if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE]):
		# 无论哪个设备发的首先都把它设为空闲状态
		current_device.ChangeStatusTo(S_IDLE)
		# 如果这个设备不是接驳台或收板机，则需要判断上一个设备是否处于准备好送板状态，如果是，给上一个设备发送板指令
		if (current_device not in [device_jbt0, device_sbjng,device_sbjok]):
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
		return
	# EVENT_GETITEM_FINISHED
	if (event == EVENT_GETITEM_FINISHED):
		if (current_device not in [device_yz, device_sbjng,device_sbjok]):
			return
	# EVENT_READYFOR_SENDITEM
	if (event == EVENT_READYFOR_SENDITEM):
		if (current_device in [device_jbt0, device_hcj]):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 如果下一个设备的状态为空闲或准备好接板，则给当前设备发送板指令
			if (next_device.status in [S_IDLE, S_READY_TO_RECV_ITEM]):
				current_device.SendInstructionSendItem()
		return
	# EVENT_SENDITEM_FINISHED
	if (event == EVENT_SENDITEM_FINISHED):
		# 首先把当前设备状态设为空闲
		if (current_device not in [device_sbjng, device_sbjok]):
			current_device.ChangeStatusTo(S_IDLE)
			if (current_device in [device_jbt0]):
				return
			if (current_device not in [device_yz]):
				if (previous_device.status == S_READY_TO_SEND_ITEM):
					previous_device.SendInstructionSendItem()
				return
	# EVENT_DEVICE_WARNING_2
	if (event == EVENT_DEVICE_WARNING_2):
		# 这时急停报警按钮
		current_device.ChangeStatusTo(S_BROKEN)
		print "WARNING: [%s] STOPED SUDDENLY" % current_device.name
		writeWarning("[%s] STOPED SUDDENLY" % current_device.name)

	if (current_device == device_jbt0):
		# Handle unknow message sent from Jiebotai0
		print "WARNING: [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
		writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device in [device_ict, device_ft]):
		# ICT/FT flow
		if (event == EVENT_READYFOR_SENDITEM_OK):
			# ICT测试板子OK发“测试OK 准备送板”消息
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_OK
			item_status = ITEM_STATUS_OK
			current_device.ChangeItemStatusTo(item_status)
			# 给缓存机发“缓存机向后接OK板”指令
			print "INFO: SERVER SENT TO [%s] -> INSTRUCTION_HCJ_RECV_ITEM_OK" % next_device.name
			next_device.SendInstructionPrepareToRecvItem()
		elif (event == EVENT_READYFOR_SENDITEM_NG):
			# ICT测试板子NG发“测试NG 准备送板”消息
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 设板子状态为ITEM_STATUS_NG
			item_status = ITEM_STATUS_NG
			current_device.ChangeItemStatusTo(item_status)
			# 给缓存机发“缓存机向后接NG板”指令
			print "INFO: SERVER SENT TO [%s]: INSTRUCTION_HCJ_RECV_ITEM_NG" % next_device.name
			next_device.SendInstructionPrepareToRecvItem()
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device == device_hcj):
		# hcj flow
		if (event == EVENT_READYFOR_GETITEM):
			# TODO 如果是NG板，缓存完毕后没有任何消息给出，如何修改缓存机状态？刘工说，给缓存机发“缓存机准备好接OK/NG板”指令后，如果缓存机没有准备好就不会发任何消息，直到缓存机准备好才会发准备好接板消息，所以，如果缓存机接的是NG板，给前一个设备发送板指令后，板子接板完成后直接将缓存机状态改为空闲即可
			# ICT给缓存机发“缓存机向后OK/NG板”，缓存机回复准备好接板，将缓存机状态设为准备好接板
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			# 检查前一个设备是否处于准备好送板状态，如果是，给它发送板指令
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
				current_device.ChangeStatusTo(S_IDLE)
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	
	

	elif (current_device == device_yz):
		# YZ flow
		writeInfo("CLIENT [%s] SENT: [%s]" % (current_device.name, event))
		if(event == EVENT_READYFOR_GETITEM_LEFT):
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
					print "WARNNING: YZ IS READY TO RECV ITEM, BUT THE FT IS NOT READY TO SEND ITEM. ANYBODY STEAL THE ITEM?"
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
				print "WARN: [%s]'s STATUS JUMPED FROM [%d] TO S_IDLE" %(current_device.name, current_device.status)
			#移栽机把板子送走了, 应该让它马上准备接板, 以优化效率
			current_device.SendInstructionPrepareToRecvItem()
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
	elif (current_device in [device_sbjok, device_sbjng]):
		writeInfo("CLIENT [%s] SENT: [%s]" % (current_device.name, event))
		if(event == RES_STATUS_BUSY):
			#TODO 收板机最好不要只给BUSY指令, 而是给一个开始收板指令
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif(event == EVENT_AVAILABLE):
			current_device.ChangeStatusTo(S_IDLE)
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
	else:
		print "WARNING: DEVICE IS NOT RECOGNIZED [%s]" % device.name
