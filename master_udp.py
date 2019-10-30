from functools import reduce
from dateutil import parser 
import threading 
import datetime 
import socket 
import time 


# datastructure used to store client address and clock data 
client_data = {} 


''' nested thread function used to receive 
	clock time from a connected client '''
def startRecieveingClockTime(clock_time_string, addr): 

	while True: 
		# recieve clock time 
		# clock_time_string = connector.recv(1024).decode() 
		slave_address = str(addr[0]) + ":" + str(addr[1]) 
		clock_time = parser.parse(clock_time_string) 
		clock_time_diff = datetime.datetime.now() - clock_time 

		client_data[slave_address] = { 
					"clock_time"	 : clock_time, 
					"time_difference" : clock_time_diff, 
					# "connector"	 : connector 
					"address": addr
					} 

		print("Client Data updated with: "+ str(slave_address), end = "\n\n") 
		time.sleep(5) 


''' master thread function used to open portal for 
	accepting clients over given port '''
def startConnecting(master_server): 
	
	# fetch clock time at slaves / clients 
	while True: 
		# accepting a client / slave clock client 
		# master_slave_connector, addr = master_server.accept() 

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

	time_difference_list = list(client['time_difference'] for client_addr, client in client_data.items()) 
									

	sum_of_clock_difference = sum(time_difference_list, datetime.timedelta(0, 0)) 

	average_clock_difference = sum_of_clock_difference / len(client_data) 

	return average_clock_difference 


''' master sync thread function used to generate 
	cycles of clock synchronization in the network '''
def synchronizeAllClocks(master_server): 

	while True: 

		print("New synchroniztion cycle started.") 
		print("Number of clients to be synchronized: " + str(len(client_data))) 

		if len(client_data) > 0: 

			average_clock_difference = getAverageClockDiff() 

			for client_addr, client in client_data.items(): 
				try: 
					synchronized_time = datetime.datetime.now() + average_clock_difference 

					# client['connector'].send(str(synchronized_time).encode()) 
					master_server.sendto(str(synchronized_time).encode(), client["address"])

				except Exception as e: 
					print("Something went wrong while " + "sending synchronized time " + "through " + str(client_addr)) 
					print(e)

		else : 
			print("No client data." + " Synchronization not applicable.") 

		print("\n\n") 

		time.sleep(5) 


# function used to initiate the Clock Server / Master Node 
def initiateClockServer(port = 8080): 

	master_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	print("Socket at master node created successfully\n") 
		
	master_server.bind(('', port)) 

	# Start listening to requests 
	# master_server.listen(10) 
	print("Clock server started...\n") 

	# start making connections 
	print("Starting to make connections...\n") 
	master_thread = threading.Thread(target = startConnecting, args = (master_server, )) 
	master_thread.start() 

	# start synchroniztion 
	print("Starting synchronization parallely...\n") 
	sync_thread = threading.Thread(target = synchronizeAllClocks, args = (master_server, )) 
	sync_thread.start() 



# Driver function 
if __name__ == '__main__': 

	# Trigger the Clock Server 
	initiateClockServer(port = 8080) 
