from functools import reduce
from dateutil import parser 
import concurrent.futures
import threading 
import datetime 
import socket 
import time 


# datastructure used to store client address and clock data 
client_data = {} 

master_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
average_clock_difference = 0
sync_round_time = 0
time_dif_threshold = datetime.timedelta(0, 0, 2000000) # Threshold of 2 seconds


# nested thread function used to receive clock time from a connected client
def startRecieveingClockTime(clock_time_string, addr): 
 
		# recieve clock time 
		# clock_time_string = connector.recv(1024).decode() 
		slave_address = str(addr[0]) + ":" + str(addr[1]) 
		clock_time = parser.parse(clock_time_string) 
		clock_time_diff = datetime.datetime.now() - clock_time 

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


		print(str(slave_address[0]) + ":" + str(slave_address[1]) + " got connected successfully") 

		current_thread = threading.Thread( 
						target = startRecieveingClockTime, 
						args = (clock_time_string, slave_address, )) 
		current_thread.start() 


# subroutine function used to fetch average clock difference 
def getAverageClockDiff(): 

	current_client_data = client_data.copy() 

	# Create a list of time differences using only those that lie with the given threshold
	time_difference_list = list(client['time_difference'] for client_addr, client in current_client_data.items() if client["time_difference"] < time_dif_threshold) 

	print(time_difference_list)								
	sum_of_clock_difference = sum(time_difference_list, datetime.timedelta(0, 0)) 

	_average_clock_difference = sum_of_clock_difference / len(time_difference_list) 

	return _average_clock_difference 


def sendSynchronizedTime(slave_data):
	synchronized_time = sync_round_time + average_clock_difference
	try:
		master_server.sendto(str(synchronized_time).encode(), slave_data["address"])
	except Exception as e: 
		print("Something went wrong while sending synchronized time through " + str(slave_data["address"])) 
		print("Error:" + e)


# master sync thread function used to generate cycles of clock synchronization in the network
def synchronizeAllClocks(): 

	while True: 
		global client_data
		print("New synchroniztion cycle started.") 
		print("Number of clients to be synchronized: " + str(len(client_data))) 

		if len(client_data) > 0: 
			global average_clock_difference
			global sync_round_time
			average_clock_difference = getAverageClockDiff()
			slaves_data = [client[1] for client in client_data.items()] 
			sync_round_time = datetime.datetime.now()
			with concurrent.futures.ThreadPoolExecutor(max_workers=len(client_data)) as executor:
				executor.map(sendSynchronizedTime, slaves_data)

			client_data = {} # Clean up the data about each client after every round of synchronization
		else : 
			print("No client data." + " Synchronization not applicable.") 

		print("\n\n") 

		time.sleep(5) 


# function used to initiate the Clock Server / Master Node 
def initiateClockServer(port = 8080): 

	
	master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	print("Socket at master node created successfully\n") 
		
	master_server.bind(('', port)) 

	print("Clock server started...\n") 

	# start making connections 
	print("Starting to make connections...\n") 
	master_thread = threading.Thread(target = startConnecting) 
	master_thread.start() 

	# start synchroniztion 
	print("Starting synchronization parallely...\n") 
	sync_thread = threading.Thread(target = synchronizeAllClocks) 
	sync_thread.start() 



# Driver function 
if __name__ == '__main__': 

	# Trigger the Clock Server 
	initiateClockServer(port = 8080) 
