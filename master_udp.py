from functools import reduce
from dateutil import parser 
import concurrent.futures
import threading 
import datetime 
import socket 
import time 
import os
from clock import Clock

# define a local clock for the master node
master_clock = Clock()

# datastructure used to store client address and clock data 
client_data = {} 

master_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
average_clock_difference = 0
sync_round_time = 0
time_dif_threshold = datetime.timedelta(0, 2) # Threshold of 2 seconds
synchronized_time = None


# nested thread function used to receive clock time from a connected client
def startRecieveingClockTime(clock_time_string, addr): 
 
		# recieve clock time 
		# clock_time_string = connector.recv(1024).decode() 
		slave_address = str(addr[0]) + ":" + str(addr[1]) 
		clock_time = parser.parse(clock_time_string) 
		clock_time_diff = master_clock.getTime() - clock_time 

		client_data[slave_address] = { 
					"clock_time"	 : clock_time, 
					"time_difference" : clock_time_diff, 
					# "connector"	 : connector 
					"address": addr # address stored in tuple format to be used while sending over UDP
					} 


# master thread function used to open portal for accepting clients over given port
def startConnecting(): 
	
	# fetch clock time at slaves / clients 
	while True: 

		clock_time_string, slave_address = master_server.recvfrom(1024)
		clock_time_string = clock_time_string.decode()


		# print(str(slave_address[0]) + ":" + str(slave_address[1]) + " got connected successfully") 

		current_thread = threading.Thread( 
						target = startRecieveingClockTime, 
						args = (clock_time_string, slave_address, )) 
		current_thread.start() 


# subroutine function used to fetch average clock difference 
def getAverageClockDiff(): 

	current_client_data = client_data.copy() 

	# Create a list of time differences using only those that lie within the given threshold
	time_difference_list = list(client['time_difference'] for client_addr, client in current_client_data.items() if client["time_difference"] < time_dif_threshold and client["time_difference"] > -time_dif_threshold) 

	# print("Time Difference List: " + str(time_difference_list[0]) + "\n")								
	sum_of_clock_difference = sum(time_difference_list, datetime.timedelta(0, 0)) 

	_average_clock_difference = sum_of_clock_difference / (len(time_difference_list) + 1) # Plus 1 to account for the time difference of the master node clock

	return _average_clock_difference 


# Update the clock of master node
def updateMasterClock():
	master_clock.setTime(synchronized_time)
	print("Updated master node with time:\t\t" + str(synchronized_time))

# Send the synchronized clock time to each slave node
def sendSynchronizedTime(slave_data):
	
	try:
		master_server.sendto(str(synchronized_time).encode(), slave_data["address"])
		print("Synchronized time sent to:\t\t" + str(slave_data["address"][0]) + ":" + str(slave_data["address"][1]))
	except Exception as e: 
		print("Something went wrong while sending synchronized time through " + str(slave_data["address"][0]) + ":" + str(slave_data["address"][1])) 
		print("Error:" + e)


# Master sync thread function used to generate cycles of clock synchronization in the network
def synchronizeAllClocks(): 

	while True: 
		global client_data
		print("New synchroniztion cycle started...") 
		print("Number of clients to be synchronized:\t" + str(len(client_data)), end="\n\n")
		if len(client_data) > 0: 
			# 
			 
			global average_clock_difference
			global sync_round_time
			global synchronized_time
			average_clock_difference = getAverageClockDiff()
			
			sync_round_time = master_clock.getTime()
			synchronized_time = sync_round_time + average_clock_difference

			# Spawn a new thread to update the master node's clock with the synchronized time
			update_master_thread = threading.Thread(target = updateMasterClock, args=())
			update_master_thread.start()

			# Spawn threads to simultaneously send synchronized times to each slave node
			slaves_data = [client[1] for client in client_data.items()] 
			with concurrent.futures.ThreadPoolExecutor(max_workers=len(client_data)) as executor:
				executor.map(sendSynchronizedTime, slaves_data)

			client_data = {} 			# Clean up the data about each client after every round of synchronization
			update_master_thread.join() # Wait for updation of master node's clock before ending the round of synchronization
		else : 
			print("No client data." + " Synchronization not applicable.") 

		print("\n\n") 

		# Start a new synchronization round every 5 seconds
		time.sleep(5) 

# function used to initiate the Clock Server / Master Node 
def initiateMasterNode(port = 8080): 

	
	master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 	
	master_server.bind(('127.0.0.1', port)) 

	print("Master node started at 127.0.0.1:" + str(port) + "\n") 

	# start making connections 
	master_thread = threading.Thread(target = startConnecting) 
	master_thread.start() 

	# start synchroniztion 
	print("Starting synchronization parallely...\n") 
	sync_thread = threading.Thread(target = synchronizeAllClocks) 
	sync_thread.start() 

	master_thread.join()
	sync_thread.join()



# Driver function 
if __name__ == '__main__': 

	# Trigger the Master Node Clock 
	initiateMasterNode(port = 8080) 