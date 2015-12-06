# -*- coding: utf-8 -*-
#!/usr/bin/env python

import pdb

from Message import *
from Device import *
from BxtException import *

def handle_msg(current_device, event):
		previous_device = current_device.previous
		next_device = current_device.next
		
		# TODO STATUS_BUSY
		if (event == STATUS_BUSY):
			pass

		# Handle message sent from Jiebotai0
		if (current_device == device_jbt0):
			if (event == EVENT_AVAILABLE):
				current_device.ChangStatusTo(S_IDLE)
			elif (event == EVENT_GETITEM_FINISHED):
				current_device.ChangStatusTo(S_WITH_ITEM)
			elif (event == EVENT_READYFOR_SENDITEM):
				current_device.ChangStatusTo(S_WAITING)
				if (matchStatus(next_device.status, S_IDLE)):
					current_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
			elif (event == EVENT_SENDITEM_FINISHED):
				current_device.ChangStatusTo(S_IDLE)

		if (current_device == device_ict):
			if (event in [EVENT_AVAILABLE, EVENT_SENDITEM_FINISHED, RES_STATUS_AVAILABLE, RES_STATUS_SENDITEM_FINISHED]):
				if (matchStatus(previous_device.status, S_WAITING)):
					previous_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
			elif (event in [EVENT_GETITEM_FINISHED, EVENT_TESTING]):
				current_device.ChangStatusTo(S_TESTING)
			elif (event == EVENT_READYFOR_SENDITEM_OK):
				current_device.ChangStatusTo(S_WAITING)# the status must specify the item's testing result OK
				current_device.changItemStatusTo(ITEM_STATUS_OKAY)
				if (matchStatus(next_device.status, S_IDLE)):	#此处我们暂不实现在缓存机的优化
					current_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
			elif (event == EVENT_READYFOR_SENDITEM_NG):
				current_device.ChangStatusTo(S_WAITING)# the status must specify the item's testing result NG
				if (matchStatus(next_device.status, S_IDLE)):
					current_device.SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
					current_device.ChangStatusTo(S_SENDING)
			elif (event == EVENT_SENDITEM_FINISHED):
				current_device.