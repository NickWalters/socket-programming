#!/usr/bin/env python

import sys
import socket
from datetime import datetime
from select import select

# GLOBAL VARIABLES ***************************************************

fullCommand = ''
stationName = ""
originalTCP = ""
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
			for time in possibleBoardingTimes:
				print(time)
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
sockTCP.listen(20)

request = ''

input = [sockTCP, sockUDP]
outputs = []

while True:
	readable, writable, exceptions = select(input, [], [])
	
	for sock in readable:
		if sock is sockTCP:
			# TCP Connection
			client_sock, client_addr = sockTCP.accept()
			print("(TCP) Now Connected to:", client_addr)
			if client_sock:
				data, addr = client_sock.recvfrom(1024)
				print(data)
				
				dataList = data.decode().split('\n')
				head = dataList[0]
				originalTCP = dataList[1].replace("Host: localhost:", "")
				print("***************************************************")
				print(originalTCP)
				print("***************************************************")
				if(len(requestHeader) == 0):
					requestHeader = data.decode()
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
						ls = requestHeader.split("\n")
						h = ls[0]
						uri = h[1]
						
						# get the Departure Time based on current time
						if(uri.find("&") == -1):
							now = datetime.now()
							current_time = now.strftime("%H:%M:%S")
							departureTime = current_time[0:5]
						else:
							# get time of arrival at transferred station (new departure time)
							index = uri.rfind("%")
							end_index = uri.rfind("!")
							ct = uri[index+1: end_index]
							departureTime = ct
							
						if(checkDirectRoute(destinationStation)):
							print("is direct (through transfer)")
							route = nextAvailableRoute(departureTime, destinationStation)
							boardTime = route[0]
							transportNumber = route[1]
							stopPlatform = route[2]
							arrivalTime = route[3]
							
							stop = stopPlatform
							busNum = transportNumber
							arrivTime = arrivTime
						else:
							# no direct route, must transfer
							for neighbour in neighbours:
								# The server adress to connect to
								neighbour_address = ('localhost', neighbour)
							
								# append to current protocol/URL
								lines = requestHeader.split("\r")
								h = lines[0].split(" ")
								this_uri = str(h[1])
								new_uri = "".join((this_uri, "&through=", stationName, "%", departureTime, "!"))
								
							
								requestHeader = requestHeader.replace(this_uri, new_uri)
								print("************************************")
								print(requestHeader)
								print("************************************")
								# send request to UDP of neighbour
								sockUDP.sendto(requestHeader.encode(), neighbour_address)
							
		else:
			# UDP Connection
			data, addr = sockUDP.recvfrom(1024)
			print("(UDP) Now Connected to:", addr)
			print(data.decode())
			print("__________________")
			
			if(len(requestHeader) == 0):
				requestHeader = data.decode()
				head = data.decode().split(' ')
				request_uri = head[1]
				ls = request_uri.split('=')
				ls.remove(ls[0])
				part = "".join(ls)
				ls2 = part.split('&through')
				for item in ls2:
					print("---")
					print(item)
				
				destinationStation = str(ls2[0])
				
				#if(checkDirectRoute(destinationStation)):
	
	
	
	client_sock.send(msg.encode())
	client_sock.close()