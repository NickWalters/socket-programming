#!/usr/bin/env python

import sys
import socket
from datetime import datetime

# GLOBAL VARIABLES ***************************************************

fullCommand = ''
stationName = ""
tcp_port = -1
udp_port = -1
neighbours = []

routes = []

# client request
requestHeader = ""
destinationStation = ""
departureTime = ""

# ARGUMENTS **********************************************************

argcount = len(sys.argv)
arglist = []

for arg in sys.argv:
	arglist.append(str(arg))
	fullCommand += str(arg) + ' '


i = -1;
for item in arglist:
	i = i+1
	if(i == 0):
		continue
		
	elif(i == 1):
		stationName = item
		
	elif(i == 2):
		tcp_port = int(item)
		print(tcp_port)
		
	elif(i == 3):
		udp_port = int(item)
	
	# UDP Ports of the neighbouring stations
	else:
		neighbours.append(int(item))
		

# READING STATION INFO ***********************************************

filename = "tt-" + stationName + ".txt"
file1 = open(filename,"r")

for line in file1:
	routes.append(line.rstrip('\n').split(','))
routes.remove(routes[0])
file1.close()



def checkDirectRoute(station):
	if(len(destinationStation) > 0):
		for route in routes:
			if(station == route[4]):
				return True
		return False
	else:
		print("Error: There was no request from the Client to go Anywhere")



		
		
# Finds the closest/nearest bus or train from this current station
# needs to be a direct route	
# @return 	returns a route, which is a list
def nextAvailableRoute(current_time, destinationStation):
	possibleBoardingTimes = []
	
	if(len(destinationStation) > 0):
		for this_route in reversed(routes):
			if(this_route[4] == destinationStation):
				# current time
				now = datetime.now()
				my_time_string = "".join((current_time, ":00"))
				my_datetime = datetime.strptime(my_time_string, "%H:%M:%S")
				my_datetime = now.replace(hour=my_datetime.time().hour, minute=my_datetime.time().minute, second=my_datetime.time().second, microsecond=0)
					
				# departure time above current time?
				now2 = datetime.now()
				my_time_string2 = "".join((this_route[0], ":00"))
				this_datetime = datetime.strptime(my_time_string2, "%H:%M:%S")
				this_datetime = now2.replace(hour=this_datetime.time().hour, minute=this_datetime.time().minute, second=this_datetime.time().second, microsecond=0)

					
				# checks if this departure time is above current time
				if(this_datetime >= my_datetime):
					possibleBoardingTimes.append(this_route)
						
		if(len(possibleBoardingTimes) > 0):
			possibleBoardingTimes.reverse()
			return possibleBoardingTimes[0]
		else:
			print("Error: There is route that is beyond the current time. You have either missed the last bus, or there is no direct route")
	else:
		print("Error: There was no request from the Client to go Anywhere")

# NETWORKING *********************************************************

# output message
msg = '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: Closed

<html>
<body>
<h2>Welcome to Public Transport Navigation Service</h2>
<h4> Your route is as follows: <h4>
<hr>
'''

msg_end = '''</body>
</html>'''

# create a socket
sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


# server address to connect to
server_addressTCP = ('localhost', tcp_port)
server_addressUDP = ('localhost', udp_port)


# bind socket to adress and port number 
sockTCP.bind(server_addressTCP)
sockUDP.bind(server_addressUDP)


# wait for connections (clients)
print("Waiting for connections...")
print(" ")
sockTCP.listen(220)

request = ''

client_sock, client_addr = sockTCP.accept()
	
print("Now Connected to:", client_addr)
print('')
	
data, addr = client_sock.recvfrom(1024)

if not data:
	udp_data, udp_addr = sockUDP.recvfrom(1024)
	if not udp_data:
		print("---------Didn't Recieve Any Data")
	else:
		# found UDP Data
		data = udp_data
		print("Received (UDP): \n" + data.decode())
else:
	#found TCP Data
	print("Received (TCP): \n" + data.decode())
	
		
	dataList = data.decode().split('\n')
	head = dataList[0]
	if(len(requestHeader) == 0):
		requestHeader = head
		requestInfo = head.split(' ')
		request_uri = requestInfo[1]
		
		
		# get the Destination Station from recieved request
		ls = request_uri.split('=')
		ls.remove(ls[0])
		part = "".join(ls)
		ls2 = part.split('&')
			
		destinationStation = str(ls2[0])
		
		# get the Departure Time for the recieved request
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		departureTime = current_time[0:5]
		
		"""
		departureTime = ls2[1].replace("leave", "").replace("%3A", ":")
		"""
		
		if(checkDirectRoute(destinationStation)):
			route = nextAvailableRoute(departureTime, destinationStation)
				
			boardTime = route[0]
			transportNumber = route[1]
			stopPlatform = route[2]
			arrivalTime = route[3]
				
			bodyMsg = ''' 
			<p>There is a direct route to your desired station<p>
			<h2>from {} to: {} </h2>
			<div style="background-color:lightyellow; border-style: solid" align="middle" class="center">
			<p><font color="red">Board Bus/Train number <strong>{}</strong> at: </font></p>
			<p> Time: {} </p>
			<p> Station: {} </p>
			<p> Platform/Stand: {} </p>
				
			<hr>
			<p><font color="red"><strong>Arrival Time: </strong></font>{}</p>
			<p> Station: {} </p>
			'''.format(stationName, destinationStation, transportNumber, boardTime, stationName, stopPlatform, arrivalTime, destinationStation)
				
			msg = " ".join((msg, bodyMsg, msg_end))
			
		else:
			# requires transfer to different station
			for neighbour in neighbours:
				# The server adress to connect to
				neighbour_address = ('localhost', neighbour)
				
				# append to current protocol/URL
				h = requestHeader.split(" ")
				uri = h[1]
				new_uri = "".join((uri, "&through=", stationName))
				new_requestHeader = " ".join((h[0], new_uri, h[2]))
				# send request to UDP of neighbour
				sockUDP.sendto(new_requestHeader.encode(), neighbour_address)
	
client_sock.send(msg.encode())
	
print("msg sent: \n" + msg)
	
# and closing connection, as we stated before
client_sock.close()