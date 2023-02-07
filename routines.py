import inspect
import time
import sys
import os
from datetime import datetime, timedelta

class Routine(object):
	def __init__(self):
		self.routine = []
		self.data = []
		self.routine_per_min = 1

	def addTask(self,name,function,update_per_min=1440):
		#if variable is not a function return false
		if not inspect.isfunction(function): return False
		#if name is not a string return false
		if not isinstance(name, str): return False
		#define temp dict
		task = {}
		# add function and time to routine
		task['name'] = name
		task['function'] = function
		task['update_per_min'] = timedelta(minutes=update_per_min)
		task['timestamp'] = datetime.now()-timedelta(minutes=update_per_min)
		task['data'] = None
		task['ready'] = True

		#append routine to the update router
		self.routine.append(task)

	def runRoutine(self):
		print("====================")
		print("Running Routine at {}...".format(datetime.now()))
		print("====================")
		for task in self.routine:
			print("*{}".format(task['name']))
			#if timestamp is not initiated, initiate it and update
			if not isinstance(task['timestamp'], datetime):
				print("{}: Timestamp not found, initiating...".format(task['name']))
				task['timestamp'] = datetime.now()
			# time since last updated + the amount of minutes until it needs to update
			time_to_update = task['timestamp']+task['update_per_min']
			#test
			print(datetime.now())
			print(time_to_update)
			# if its been more than 'update_per_min' since the last update then update
			if  datetime.now() >= time_to_update:
				#try:
				print("Ready to update, updating...")
				task['data'] = task['function']()
				# add update per minutes as int to data
				task['data']['update_per_min'] = round(task['update_per_min'].seconds/60)
				#Set Task ready (not ready to update) to True
				task['data']['ready'] = True
				# Debug print task data
				print(task['data'])
				print("----------------------")
				task['timestamp'] = datetime.now()
				#except Exception as e:
					#print(e)
				continue
			#not ready
			#Set Task ready (not ready to update) to False
			task['data']['ready'] = False
			print("Not ready to update!")
			print("----------------------")
	
	def loopRoutine(self):
		while True:
			self.runRoutine()
			time.sleep(self.routine_per_min*60)

	def getRoutine(self):
		return self.routine

	def getRoutineData(self):
		routine_data = {}
		for task in self.routine:
			routine_data[task['name']] = task['data']
		return routine_data
