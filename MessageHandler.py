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
	writeInfo("CLIENT: [%s] SENT: [%s]" % (current_device.name, event))

	# RES_STATUS_BUSY
	if (event == RES_STATUS_BUSY):
		if(current_device not in [device_sbjok, device_sbjng]):
			return
	# EVENT_AVAILABLE, RES_STATUS_AVAILABLE
	if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE]):
		current_device.ChangeStatusTo(S_IDLE)
		# jbt and shj dont need to check previous device's status
		if (current_device not in [device_jbt0, device_sbjng, device_sbjok]):
			if (current_device in [device_yz]):
				# preparing for recving when start yz
				current_device.SendInstructionPrepareToRecvItem()
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				if (current_device in [device_hcj, device_yz]):
					# preparing for recving when reboot yz
					current_device.SendInstructionPrepareToRecvItem()
				else:
					previous_device.SendInstructionSendItem()
		return
	# EVENT_GETITEM_FINISHED
	#if (event == EVENT_GETITEM_FINISHED):
	#	if (current_device not in [device_yz, device_sbjng,device_sbjok]):
	#		return
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
					#previous_device.SendInstructionSendItem()
					current_device.SendInstructionPrepareToRecvItem()
				return
	# EVENT_DEVICE_WARNING_2
	if (event == EVENT_DEVICE_WARNING_2):
		# 这时急停报警按钮
		current_device.ChangeStatusTo(S_BROKEN)
		print "WARNING: [%s] STOPED SUDDENLY" % current_device.name
		writeWarning("[%s] STOPED SUDDENLY" % current_device.name)
		return

	if (current_device == device_jbt0):
		# jbt flow
		print "WARNING: [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
		writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device in [device_ict, device_ft]):
		# ICT/FT flow
		if (event == EVENT_GETITEM_FINISHED):
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)		# set device status
			current_device.ChangeItemStatusTo(ITEM_STATUS_OK)		# set item status
			next_device.SendInstructionPrepareToRecvItem()			# tell next device to prepare to recv item
		elif (event == EVENT_READYFOR_SENDITEM_NG):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			current_device.ChangeItemStatusTo(ITEM_STATUS_NG)
			next_device.SendInstructionPrepareToRecvItem()
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device == device_hcj):
		# hcj flow
		if (event == EVENT_READYFOR_GETITEM):
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			if (previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
				current_device.ChangeStatusTo(S_IDLE)
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	
	

	elif (current_device == device_yz):
		# YZ flow
		if(event == EVENT_READYFOR_GETITEM_LEFT):
			# YZ ready for get item. (in left side)
			if(current_device.status != S_PREPARING_TO_RECV):
				print "WARNING: [%s] REPORT EVENT_READYFOR_GETITEM_LEFT FROM STATUS [%d]" % (current_device.name, current_device.status)
			if(current_device.prepare_count == 1):
				current_device.ChangeStatusTo(S_HALF_READY_TO_RECV_ITEM)
				if(previous_device.status == S_READY_TO_SEND_ITEM):
					current_device.SendInstructionPrepareToRecvItem()
			elif(current_device.prepare_count == 2):
				current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
				# you better do not check the previous device's status, it may changed by another item
				#if(previous_device.status == S_READY_TO_SEND_ITEM):
				previous_device.SendInstructionSendItem()
				#else:
				#	print "WARNNING: YZ IS READY TO RECV ITEM, BUT THE FT IS NOT READY TO SEND ITEM. ANYBODY STEAL THE ITEM?"
		elif(event==EVENT_GETITEM_FINISHED):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			# 此处要判断板子状态的接板机是否空闲
			print "DDDDDDDDDDDDDDD", current_device.item_status, current_device.item_status
			ok_idle = (current_device.item_status == ITEM_STATUS_OK and device_sbjok.status == S_IDLE)
			ng_idle = (current_device.item_status in [ITEM_STATUS_NG, ITEM_STATUS_UNKNOWN] and device_sbjng.status == S_IDLE)
			if(ok_idle or ng_idle):
				current_device.SendInstructionSendItem()
		elif(event==EVENT_SENDITEM_FINISHED):
			if(current_device.status != S_SENDING):
				print "WARN: [%s]'s STATUS JUMPED FROM [%d] TO S_IDLE" %(current_device.name, current_device.status)
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			#移栽机把板子送走了, 应该让它马上准备接板, 以优化效率
			current_device.SendInstructionPrepareToRecvItem()
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
	elif (current_device in [device_sbjok, device_sbjng]):
		writeInfo("CLIENT [%s] SENT: [%s]" % (current_device.name, event))
		if(event == RES_STATUS_BUSY):
			# 碰到移载机左端感应器就会回忙，表示开始接板
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif(event == EVENT_AVAILABLE):
			# 离开移载机右端感应器就会发空闲，表示收板完成
			current_device.ChangeStatusTo(S_IDLE)
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
	else:
		print "WARNING: DEVICE IS NOT RECOGNIZED [%s]" % device.name
