
import sys
import socket

# GLOBAL VARIABLES ***************************************************
stationName = ""
tcp_port = -1
udp_port = -1
neighbours = []



# ARGUMENTS **********************************************************
argcount = len(sys.argv)
arglist = []

for arg in sys.argv:
	print(str(arg))
	arglist.append(str(arg))
	

i= -1;
for item in arglist:
	i = i+1
	if(i == 0):
		stationName = item
		
	elif(i == 1):
		tcp_port = int(item)
		
	elif(i ==2):
		udp_port = int(item)
	
	# UDP Ports of the neighbouring stations
	else:
		neighbours.append(int(item))
		
		
		



# NETWORKING *********************************************************

# create a socket
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


# server adress to connect to
server_addressUDP = ('localhost', udp_port)


# bind socket to adress and port number 
sockUDP.bind(server_addressUDP)


while True:
	# **************** UDP ********************************

	#UDP - Accept Message
	udp_data, udp_addr = sockUDP.recvfrom(1024)
	
	print("Message: ", udp_data.decode("utf-8"))
	

