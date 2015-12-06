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
		if (event == RES_STATUS_BUSY):
			if(current_device not in [device_sbjok, device_sbjng]):
				#RES_STATUS_BUSY is discarded 
				return
				
		
		if (current_device == device_jbt0):
			# Handle message sent from Jiebotai0
			if (event == EVENT_AVAILABLE):
				current_device.ChangeStatusTo(S_IDLE)
			elif (event == EVENT_GETITEM_FINISHED):
				current_device.ChangeStatusTo(S_WITH_ITEM)
			elif (event == EVENT_READYFOR_SENDITEM):
				current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
				if (matchStatus(next_device.status, S_IDLE)):
					current_device.SendInstructionSendItem()
			elif (event == EVENT_SENDITEM_FINISHED):
				current_device.ChangeStatusTo(S_IDLE)
			else:
				print "Event [%s] is not recognized for device [%s]" % [event, current_device.name]
		elif (current_device in [device_ict, device_ft]):
			if (event in [EVENT_AVAILABLE, EVENT_SENDITEM_FINISHED, RES_STATUS_AVAILABLE, RES_STATUS_SENDITEM_FINISHED]):
				current_device.ChangeStatusTo(S_IDLE)
				if (matchStatus(previous_device.status, S_READY_TO_SEND_ITEM)):
					previous_device.SendInstructionSendItem()
			elif (event in [EVENT_GETITEM_FINISHED, EVENT_TESTING]):
				current_device.ChangeStatusTo(S_TESTING)
			elif (event in [EVENT_READYFOR_SENDITEM_OK, EVENT_READYFOR_SENDITEM_NG]):
				# 测试机器已经测试完毕一块板子
				if(current_device.status == S_READY_TO_SEND_ITEM):
					#上一块板子还没送出去
					print "WARN: One more item testing finished when the last item has not been sent in device [%s]" % current_device.name
				current_device.ChangeStatusTo(S_READY_TO_SEND_ITEM)
				current_device.changItemStatusTo(event == EVENT_READYFOR_SENDITEM_OK ? ITEM_STATUS_OK : ITEM_STATUS_NG)
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
						2. 测试机上的板子被人手工拿走了
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
			pass
		elif (current_device == device_yz):
			if(event == EVENT_READYFOR_GETITEM_RIGHT):
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
				cmd = INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM
				if(current_device.item_status == ITEM_STATUS_OK):
					cmd = INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM 
				current_device.SendInstruction(cmd)
				current_device.ChangeStatusTo(S_SENDING)
			elif(event==EVENT_SENDITEM_FINISHED):
				if(current_device.status != S_SENDING):
					print "WARN: [%s]'s status jumped from [%d] to S_IDLE" %(current_device.name, current_device.status)
				current_device.ChangeStatusTo(S_IDLE)
				#移栽机把板子送走了, 应该让它马上准备接板, 以优化效率
				current_device.SendInstructionPrepareToRecvItem()
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
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				