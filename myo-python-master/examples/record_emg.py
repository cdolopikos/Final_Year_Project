'''

Aston University 

Copyright (c) 2019 Jhonatan Kobylarz

'''

from collections import deque
from threading import Lock, Thread

import time
import myo
import numpy as np
import pandas as pd

class Listener(myo.DeviceListener):
	
	def __init__(self):
		self.lock = Lock()
		self.emg_data = []
	
	def get_emg_data(self):
		#print(self.emg_data)
		with self.lock:
			return list(self.emg_data)

	def on_connected(self, event):
		event.device.stream_emg(True)

	def on_emg(self, event):
		with self.lock:
			self.emg_data.append(event.emg)

class Saving(object):
	
	def __init__(self, listener):
		self.emg_data = listener.emg_data
		self.listener = listener

	def main(self):

		# Defining the file name

		name = input("Name:")
		state = input("State: (fist, open_fingers, wave_in, wave_out)")
		turn = input("Turn:")
		full_name = name + "-" + state + "-" + turn + ".csv"
		input("Press Enter to start recording...")

		noise = pd.Series(0)

		time_step = time.time()
		emg_data = []

		# Recording the EMG data

		while(time.time() - time_step < 60):
			emg_data=(self.listener.get_emg_data())
			print(time.time() - time_step)
			#print(emg_data)

		# Creating the dataset

		emg_data_series = pd.DataFrame(emg_data)
		print(emg_data_series.head())
		print(emg_data_series.tail())
		
		#emg_data_series.drop([1,3,5,7], axis=1, inplace = True) # Comment this if you want 8 channels to be recorded

		emg_data_series.insert(0 , 'timestamps', range(1, len(emg_data_series)+1))
		emg_data_series['timestamps'] = emg_data_series['timestamps'].apply(lambda x: x*0.005)

		full_data = pd.concat([emg_data_series,noise], axis=1, sort = False)
		
		full_data.fillna(0, inplace = True)
		print(full_data)

		# Choose one and comment the other
		# Record 8 channels
		full_data.to_csv(full_name, index = None, header=['timestamp','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','noise'])
		
		# Record 4 channels
		#full_data.to_csv(full_name, index = None, header=['timestamp','ch1','ch3','ch5','ch7','noise'])

		print("\nCompleted Successfully\n")
		print(f"Thanks for {state} EMG data, {name}!!")
		print("\n- Aston University\n")

		


if __name__ == '__main__':
	myo.init('/Users/cmdgr/Code/myo_sdk/myo.framework/myo')
	hub = myo.Hub()
	listener = Listener()
	with hub.run_in_background(listener.on_event):
		Saving(listener).main()
