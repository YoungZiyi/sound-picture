# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pdb

from Message import *
from Device import *
from BxtException import *
from BxtLogger import *

def handle_msg(current_device, event):
	#messages beginning with 52 d3 are messages for device debugging. Just ignore them.
	if(event[:5] =="52 d3"):
		return
	if(event_name_map.has_key(event)):
		writeInfo("DEVICE: [%s] EVENT: [%s] DEVICE_STATUS: [%d] ITEM_STATUS: [%d] " % (current_device.name, event_name_map[event], current_device.status, current_device.item_status))
	else:
		writeInfo("DEVICE: [%s] EVENT: [%s] DEVICE_STATUS: [%d] ITEM_STATUS: [%d] " % (current_device.name, event, current_device.status, current_device.item_status))

	#Messages beginningwith 52 c3 are warn messages
	if(event[:5] == "53 c3"):
		#TODO. More attention should be paid to this status
		current_device.ChangeStatusTo(S_BROKEN)
		writeWarning("[%s] reported warn [%s]" % current_device.name, event)
		return

	# RES_STATUS_BUSY
	if (event == RES_STATUS_BUSY and (current_device not in [device_sbjng])):	
		#Ignore this event for every device except device_sbjng
		return

	if(current_device in [device_ict]):
		if (event in [EVENT_READYFOR_SENDITEM_OK, EVENT_READYFOR_SENDITEM_NG, EVENT_READYFOR_SENDITEM]):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			#If the next device is available, then instruct it to recv item.
			if(device_yz1.status in [S_IDLE, S_PREPARING_TO_RECV]):
				device_yz1._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM)
			elif(device_yz1.status in [S_READY_TO_RECV_ITEM]):
				device_ict._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
				device_ict.ChangeStatusTo(S_SENDING)
		elif (event == EVENT_SENDITEM_FINISHED):
			device_yz1.ChangeItemStatusTo(current_device.item_status)
			current_device.ChangeStatusTo(S_IDLE)	
		else:
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif(current_device == device_yz1):
		if(event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE, EVENT_SENDITEM_FINISHED]):
			#Prepare to recv item in advance
			current_device._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM)
			current_device.status = S_PREPARING_TO_RECV
		elif(event in [EVENT_READYFOR_GETITEM_RIGHT]):
			if(current_device.status not in [S_PREPARING_TO_RECV]):
				writeWarning("[%s] send event EVENT_READYFOR_GETITEM_RIGHT while its status is [%d]" % (current_device.name, current_device.status))
			
			current_device.ChangeStatusTo(S_READY_TO_RECV_ITEM)
			if(device_ict.status == S_READY_TO_SEND_ITEM):
				device_ict._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
				device_ict.ChangeStatusTo(S_SENDING)
				device_yz1.ChangeStatusTo(S_RECVING)
			else:
				writeInfo("YZ1 is ready to recv, but [%s] is of status [%d]."%(device_ict.name, device_ict.status))
				device_yz1.ChangeStatusTo(S_IDLE)
		elif(event==EVENT_GETITEM_FINISHED):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			if(device_ft1.status == S_IDLE):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM)
				current_device.ChangeStatusTo(S_SENDING)
				device_ft1.ChangeStatusTo(S_RECVING)
			elif(device_ft2.status == S_IDLE):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM)
				current_device.ChangeStatusTo(S_SENDING)
				device_ft2.ChangeStatusTo(S_RECVING)
			else:
				writeInfo("%s is waiting for an available FT" % (current_device.name))
		else:
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif(current_device in [device_ft1, device_ft2]):
		if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE, EVENT_SENDITEM_FINISHED]):
			if(event in [EVENT_SENDITEM_FINISHED]):
				device_yz2.ChangeItemStatusTo(current_device.item_status)
			current_device.ChangeStatusTo(S_IDLE)
			#Check if the previous device is waiting for this device
			if(device_yz1.status == S_READY_TO_SEND_ITEM):
				if(current_device == device_ft1):
					device_yz1._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM)
				else:
					device_yz1._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM)
				device_yz1.ChangeStatusTo(S_SENDING)
				current_device.ChangeStatusTo(S_RECVING)
		elif(event == EVENT_GETITEM_FINISHED):
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif(event in [EVENT_READYFOR_SENDITEM_NG, EVENT_READYFOR_SENDITEM_OK]):
			current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
			if(event == EVENT_READYFOR_SENDITEM_OK):
				current_device.ChangeItemStatusTo(ITEM_STATUS_OK)
			else:
				current_device.ChangeItemStatusTo(ITEM_STATUS_NG)
			if(current_device == device_ft1):
				if(device_yz2.status in [S_IDLE]):
					device_yz2._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM)
					device_yz2.direction = DIRECTION_RIGHT
				#TODO 下面这个分支应该不会发生， 因为yz2不会停留在S_READY_TO_RECV_ITEM状态
				elif(device_yz2.status in [S_READY_TO_RECV_ITEM] and device_yz2.direction == DIRECTION_RIGHT):
					current_device._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					current_device.ChangeStatusTo(S_SENDING)
					device_yz2.ChangeStatusTo(S_RECVING)
				else:
					writeInfo("%s is waiting for yz2 to be available" % (current_device.name))
			else:
				if(device_yz2.status in [S_IDLE]):
					device_yz2._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM)
					device_yz2.direction = DIRECTION_LEFT
				#TODO 下面这个分支应该不会发生， 因为yz2不会停留在S_READY_TO_RECV_ITEM状态
				elif(device_yz2.status in [S_READY_TO_RECV_ITEM] and device_yz2.direction == DIRECTION_LEFT):
					current_device._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					current_device.ChangeStatusTo(S_SENDING)
					device_yz2.ChangeStatusTo(S_RECVING)
				else:
					writeInfo("%s is waiting for yz2 to be available" % (current_device.name))
		else:
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device in [device_yz2]):
		if (event in [EVENT_AVAILABLE, RES_STATUS_AVAILABLE, EVENT_SENDITEM_FINISHED]):
			if(device_ft1.status == S_READY_TO_SEND_ITEM):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM)
				current_device.ChangeStatusTo(S_PREPARING_TO_RECV)
				current_device.direction = DIRECTION_RIGHT				
			elif(device_ft2.status == S_READY_TO_SEND_ITEM):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM)
				current_device.ChangeStatusTo(S_PREPARING_TO_RECV)
				current_device.direction = DIRECTION_LEFT
			else:
				current_device.ChangeStatusTo(S_IDLE)
				current_device.direction = DIRECTION_UNKNOWN
		elif(event in [EVENT_READYFOR_GETITEM_LEFT, EVENT_READYFOR_GETITEM_RIGHT]):
			#TODO There should be some status assertion
			if(current_device.direction == DIRECTION_RIGHT):
				if(device_ft1.status == S_READY_TO_SEND_ITEM):
					device_ft1._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					device_ft1.ChangeStatusTo(S_SENDING)
					current_device.ChangeStatusTo(S_RECVING)
				else:
					writeWarning("YZ2 IS READY TO RECV ITEM, BUT THE [%s] IS of status [%d]."%(device_ft1.name, device_ft1.status))
					#Change it status to idle so the other FT device can use the YZ device if they need.
					current_device.ChangeStatusTo(S_IDLE)	#TODO 此处应该给触发对另外一个ft机器是否READY_TO_SEND的检查
			elif(current_device.direction == DIRECTION_LEFT):
				if(device_ft2.status == S_READY_TO_SEND_ITEM):
					device_ft2._SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					device_ft2.ChangeStatusTo(S_SENDING)
					current_device.ChangeStatusTo(S_RECVING)
				else:
					writeWarning("YZ2 IS READY TO RECV ITEM, BUT THE [%s] IS of status [%d]."%(device_ft2.name, device_ft2.status))
					#Change it status to idel so the other FT device can use the YZ device if they need.
					current_device.ChangeStatusTo(S_IDLE)	#TODO 此处应该给触发对上位机的检查
			else:
				writeWarning("[%s] reported [%s] but with a bad direction [%d]" % (current_device.name, event, current_device.direction))
		elif(event == EVENT_GETITEM_FINISHED):
			if(current_device.item_status == ITEM_STATUS_OK):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM)
				current_device.ChangeStatusTo(S_SENDING)
			elif(device_sbjng.status == S_IDLE):
				current_device._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM)
				current_device.ChangeStatusTo(S_SENDING)
				device_sbjng.ChangeStatusTo(S_RECVING)
			else:
				#Do nothing but wait. device_sbjng will check the status 
				current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
		else:
			writeWarning("[%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name))
	elif (current_device in [device_sbjng]):
		if(event == RES_STATUS_BUSY):
			current_device.ChangeStatusTo(S_WITH_ITEM)
		elif(event == EVENT_AVAILABLE):
			current_device.ChangeStatusTo(S_IDLE)
			if (device_yz2.status == S_READY_TO_SEND_ITEM):
				device_yz2._SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM)
				current_device.ChangeStatusTo(S_SENDING)
				device_sbjng.ChangeStatusTo(S_RECVING)
		else:
			print "WARNING: EVENT [%s] IS NOT RECOGNIZED FOR DEVICE [%s]" % (event, current_device.name)
	else:
		print "WARNING: DEVICE IS NOT RECOGNIZED [%s]" % device.name
