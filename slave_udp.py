from timeit import default_timer as timer 
from dateutil import parser 
import threading 
import datetime 
import socket 
import time 
import argparse
from clock import Clock

# Get parser argument for drift rate
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-d", "--drift_rate", type=float, default=1, help="Drift rate of the slave clock [Optional: Defaults to 1]")

args = arg_parser.parse_args()

# Define local clock for slave node
slave_clock = Clock(drift_rate = args.drift_rate)

# client thread function used to send time at client side 
def startSendingTime(slave_client, server_address): 

	while True: 
		# provide server with clock time at the client 
		slave_client.sendto(str(slave_clock.getTime()).encode(), server_address) 

		# print("\nRecent time sent successfully") 
		time.sleep(5) 

# Update slave node's clock with synchronized time
def updateSlaveClock(synchronized_time):

    print("Slave node time BEFORE synchronization:\t" + str(slave_clock.getTime()))
    slave_clock.setTime(synchronized_time)
    print("Slave node time AFTER synchronization:\t" + str(synchronized_time) + "\n\n")

# client thread function used to receive synchronized time 
def startReceivingTime(slave_client): 

    while True: 
		# receive data from the server 
        receivedTime, address = slave_client.recvfrom(1024)
        synchronized_time = parser.parse(receivedTime) 
        updateSlaveClock(synchronized_time)

        # print("Synchronized time at the client is: " + str(synchronized_time), end = "\n\n") 


# Function used to Synchronize slave process clock 
def initiateSlaveNode(master_port = 8080): 

    slave_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		 
		
	# define the master node address
    server_address = ('127.0.0.1', master_port)

    print("Slave node started...", end="\n\n")

	# start sending time to server 
    # print("Starting to receive time from server\n") 
    send_time_thread = threading.Thread(target = startSendingTime, args = (slave_client, server_address, )) 
    send_time_thread.start() 


	# start recieving synchronized from server 
    # print("Starting to recieving " + "synchronized time from server\n") 
    receive_time_thread = threading.Thread(target = startReceivingTime, args = (slave_client, )) 
    receive_time_thread.start() 


# Driver function 
if __name__ == '__main__': 

	# initialize the Slave / Client 
	initiateSlaveNode(master_port = 8080) 
