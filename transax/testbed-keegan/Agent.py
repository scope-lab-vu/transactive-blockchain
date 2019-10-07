import string;
import json
import sys
import zmq
import fncs
import time
import os
import numpy as np
if sys.platform != 'win32':
	import resource

class Agent():
	def __init__(self, time):
		self.time_stop = int(time)
		self.time_granted = 0


		if os.getenv('RIAPS')=='True':
			self.RIAPS = True
			print("RIAPS: %s" %(self.RIAPS==True))
		else:
			self.RIAPS = False
			print("RIAPS: %s" %(self.RIAPS==True))

		fncs.initialize()

		self.batt_charges = {}
		self.solar_power = {}
		self.batt_power = {}
		self.prev_batt_commands = {}

		self.mainLoop()

	def getBattNum(self, req_batt_num):
		first = req_batt_num[0:1]
		second = req_batt_num[1:3]
		if (second[0] == '0'):
			second = second[1]
		return 'b' + first + 'm' + second

	def tradeResp(self):
		print(self.time_granted, self.request, flush=True)

		req_batt_num = self.msg['ID']
		m_batt_num = self.getBattNum(req_batt_num)
		keyname = m_batt_num + '_solar_power'

		if(keyname in self.solar_power):
			#Solar power is negative in GridLabD
			batt_out = self.msg['power'] + self.solar_power[keyname][-1]
			print('msg[\'power\']: ', str(self.msg['power']),flush=True)
			print('solar power:', self.solar_power[keyname][-1],flush=True)
			print('batt_out:', str(batt_out),flush=True)
		else:
			batt_out = 0

		fncs.publish(m_batt_num + '_batt_P_Out', str(batt_out))
		self.prev_batt_commands[m_batt_num] = batt_out
		print('fncs published:', m_batt_num + '_batt_P_Out', str(batt_out))
		self.server.send_pyobj('Trade Posted') 

	def chargeResp(self):
		print(self.time_granted, self.request, flush=True)
		req_batt_num = self.msg['ID']
		m_batt_num = self.getBattNum(req_batt_num)
		keyname = m_batt_num + '_batt_charge'
		if(keyname in self.batt_charges):
			charge = self.batt_charges[keyname]
		else:
			charge = 0

		keyname = m_batt_num
		if(keyname in self.prev_batt_commands):
			battCMD = self.prev_batt_commands[keyname]
		else:
			battCMD = 0

		keyname = m_batt_num + '_solar_power'
		if(keyname in self.solar_power):
			solarActual = np.mean(self.solar_power[keyname]).item()
		else:
			solarActual = 0

		keyname = m_batt_num + '_batt_power'
		if(keyname in self.batt_power):
			battActual = np.mean(self.batt_power[keyname][1:]).item() #Command takes one time step to actuate
		else:
			battActual = 0

		# print("charge: %s" %charge)
		# print("battCMD: %s" %battCMD)
		# print("solarActual: %s" %solarActual)
		# print("battActual: %s" %battActual)
		# print("\n")
		
		# print("charge: %s" %type(charge))
		# print("battCMD: %s" %type(battCMD))
		# print("solarActual: %s" %type(solarActual))
		# print("battActual: %s" %type(battActual))
		# print("\n")

		# print("charge: %s" %type(charge))
		# print("battCMD: %s" %type(battCMD))
		# print("solarActual: %s" %type(-solarActual))
		# print("battActual: %s" %type(-battActual))
		# print("\n")

		response = {
		"perUnitCharge":charge,
		"solarActual": -solarActual, #Average power over last interval
		"battActual" : -battActual, #Average power over last interval
		"battCMD" : battCMD, #The P_Out issued in previous interval
		"OHLcurrent" : 0, #TODO Current through the overhead line
		}

		self.server.send_pyobj(response)

	def mainLoop(self):
		if(self.RIAPS):
			self.context = zmq.Context(1)
			self.server = self.context.socket(zmq.REP)
			self.server.bind("tcp://*:5555")

			while self.time_granted < self.time_stop:
				events = fncs.get_events()
				for topic in events:
					value = fncs.get_value(topic)
					#Collect Most recent charge data
					if('batt_charge' in topic):
						self.batt_charges[topic] = float(value.split(" ")[0][1:])
					if('solar_power' in topic):
						if topic in self.solar_power:
							self.solar_power[topic].append(float(value.split(' ')[0]))
						else:
							self.solar_power[topic] = [float(value.split(' ')[0])]
					if('batt_power' in topic):
						if topic in self.batt_power:
							self.batt_power[topic].append(float(value.split(' ')[0]))
						else:
							self.batt_power[topic] = [float(value.split(' ')[0])]
				if('step' in events):
					self.request = ''
					while(self.request != 'step'):
						self.msg = self.server.recv_pyobj()
						self.request = self.msg['request']
						if (self.request == 'postTrade'):
							self.tradeResp()
						if (self.request == 'charge'):
							self.chargeResp()
					print(self.time_granted, self.request, flush=True)
					print("solar_power: ", self.solar_power)
					print("batt_power: ", self.batt_power)
					self.solar_power = {}
					self.batt_power = {}
					self.time_granted = fncs.time_request(self.time_stop)
					self.server.send_pyobj('Step Granted')
					
				else:
					self.time_granted = fncs.time_request(self.time_stop)
					print("Simulation Continue, new time_granted:", str(self.time_granted))

			self.server.close()
			self.context.term()
			print('zmq Closed', flush=True)

		else:
			while self.time_granted < self.time_stop:
				self.time_granted = fncs.time_request(self.time_stop)
				events = fncs.get_events()
				for topic in events:
					value = fncs.get_value(topic)
					#Collect Most recent charge data
					if('batt_charge' in topic):
						self.batt_charges[topic] = value
					if('solar_power' in topic):
						self.solar_power[topic] = value



		print('End of Simulation', flush=True)
		fncs.finalize()

		if sys.platform != 'win32':
			usage = resource.getrusage(resource.RUSAGE_SELF)
			RESOURCES = [
			('ru_utime', 'User time'),
			('ru_stime', 'System time'),
			('ru_maxrss', 'Max. Resident Set Size'),
			('ru_ixrss', 'Shared Memory Size'),
			('ru_idrss', 'Unshared Memory Size'),
			('ru_isrss', 'Stack Size'),
			('ru_inblock', 'Block inputs'),
			('ru_oublock', 'Block outputs')]
			print('Resource usage:')
			for name, desc in RESOURCES:
				print('  {:<25} ({:<10}) = {}'.format(desc, name, getattr(usage, name)))

mAgent = Agent(sys.argv[1])