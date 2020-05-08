#!/usr/bin/env python

import sys
import socket
from datetime import datetime
from select import select
import time

# GLOBAL VARIABLES ***************************************************

fullCommand = ''
stationName = ""
originalUDP = ""
tcp_port = -1
udp_port = -1
neighbours = []

routes = []

# client request
requestHeader = ""
destinationStation = ""
departureTime = ""
arrivTime = ""

UDPconnected = False
TCPconnected = False

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


# FUNCTIONS **********************************************************

def checkDirectRoute(station):
	print(station)
	print(len(station))
	for route in routes:
		print("------------------------")
		print(route[4])
		print(len(route[4]))
		if(station == route[4]):
			print("found direct route")
			return True
	print("didnt find direct route")
	return False



		
		
# Finds the closest/nearest bus or train from this current station
# needs to be a direct route	
# @return 	returns a route, which is a list
def nextAvailableRoute(current_time, destnStation):
	possibleBoardingTimes = []
	print("test1")
	if(len(destnStation) > 0):
		print("test2")
		for this_route in reversed(routes):
			if(this_route[4] == destnStation):
				print("test3")
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
					print("test4")
						
		if(len(possibleBoardingTimes) > 0):
			possibleBoardingTimes.reverse()
			for time in possibleBoardingTimes:
				print(time)
			return possibleBoardingTimes[0]
		else:
			print("Error: There is route that is beyond the current time. You have either missed the last bus, or there is no direct route")
	else:
		print("Error: There was no request from the Client to go Anywhere")
		


def namesOfNeighbours():
	namesOfNeighboursList = []
	for route in routes:
		if(len(namesOfNeighboursList) == 0):
			namesOfNeighboursList.append(route[4])
		else:
			count = 0
			for i in range(len(namesOfNeighboursList)):
				if(route[4] == namesOfNeighboursList[i]):
					count += 1
			if(count == 0):
				namesOfNeighboursList.append(route[4])
	return namesOfNeighboursList
	
	
def getOriginalUDP(uri):
	ls = uri.split("#")
	if(len(ls) == 2):
		return ls[1]
	else:
		return originalUDP


def destStation(uri):
	ls = uri.split("=")
	ls.remove(ls[0])
	tmp = ls[0]
	if(tmp.find("&through") != -1):
	    tmp = tmp.replace("&through", "")
	return(tmp)
	

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
			TCPconnected = True
			client_sock, client_addr = sockTCP.accept()
			originalUDP = str(udp_port)
			print("(TCP) Now Connected to:", client_addr)
			if client_sock:
				data, addr = client_sock.recvfrom(1024)
				print(data)
				
				dataList = data.decode().split('\n')
				head = dataList[0]
				originalTCP = dataList[1].replace("Host: localhost:", "")
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
						arrivTime = route[3]
							
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
						<p>END<p>
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
						
						neighbourStns = namesOfNeighbours()
						temp_route = nextAvailableRoute(departureTime, neighbourStns[0])
							
				#SCAN ALL NEIGHBOURS *************************************************
						for i in range(len(neighbourStns)):
							thisNeigh = neighbours[i]
							
							# extract how long it takes to get to neighbour (and other info)
							tmp_route = nextAvailableRoute(departureTime, neighbourStns[i])
							
							boardTime = tmp_route[0]
							transportNumber = tmp_route[1]
							stopPlatform = tmp_route[2]
							arrivalTime = tmp_route[3]
							arrivTime = tmp_route[3]
							
							# The server adress to connect to
							neighbour_address = ('localhost', thisNeigh)
							
							# append to current protocol/URL
							lines = requestHeader.split("\r")
							h = lines[0].split(" ")
							this_uri = str(h[1])
							new_uri = "".join((this_uri, "&through=", stationName, "%", departureTime, ">", arrivalTime, "#", originalUDP))
								
							
							requestHeader = requestHeader.replace(this_uri, new_uri)
							
							bodyMsg = '''
							<p>You Require Transfer(s)<p>
							<h2>from {} to: {} </h2>
							<div style="background-color:lightyellow; border-style: solid" align="middle" class="center">
							<p><font color="red">Board Bus/Train number <strong>{}</strong> at: </font></p>
							<p> Time: {} </p>
							<p> Station: {} </p>
							<p> Platform/Stand: {} </p>
								
							<hr>
							<p><font color="red"><strong>Arrival Time: </strong></font>{}</p>
							<p> Station: {} </p>
							</div>
							'''.format(stationName, neighbourStns[i], transportNumber, boardTime, stationName, stopPlatform, arrivalTime, neighbourStns[i])
							
							# send request to UDP of neighbour
							sockUDP.sendto(requestHeader.encode(), neighbour_address)
							
							originalUDP = getOriginalUDP(new_uri)
							if(udp_port != originalUDP):
								# send transfer information to client
								sockUDP.sendto(bodyMsg.encode(), ('localhost', int(originalUDP)))
							
							
		else:
			# UDP Connection
			UDPconnected = True
			data, addr = sockUDP.recvfrom(1024)
			print("(UDP) Now Connected to:", addr)
			print(data.decode())
			print("__________________")
			
			if(data.decode().find("<p>") != -1):
				msg_body = data.decode()
				msg = " ".join((msg, msg_body))
				print("********************************")
				print(msg)
				print("********************************")
			else:
				# currently at a transfer station
				lines = data.decode().split('\r')
				h = lines[0].split(" ")
				uri = h[1]
				startTime = ""
				
				if(uri.rfind(">") != -1):
					index = uri.rfind(">")
					end_index = uri.rfind("#")
					startTime = uri[index+1: end_index]
				else:
					print("Error: There is no '>' arrival time")
				
				
				destStn = destStation(uri)
				if(checkDirectRoute(str(destStn))):
					route = nextAvailableRoute(startTime, destStn)
					
					boardTime = route[0]
					transportNumber = route[1]
					stopPlatform = route[2]
					arrivalTime = route[3]
					arrivTime = route[3]
				
					bodyMsg = '''
					<h2>from {} to: {} </h2>
					<div style="background-color:lightblue; border-style: solid" align="middle" class="center">
					<p><font color="red">Board Bus/Train number <strong>{}</strong> at: </font></p>
					<p> Time: {} </p>
					<p> Station: {} </p>
					<p> Platform/Stand: {} </p>
						
					<hr>
					<p><font color="red"><strong>Arrival Time: </strong></font>{}</p>
					<p> Station: {} </p>
					</div>
					<p>END<p>'''.format(stationName, destStn, transportNumber, boardTime, stationName, stopPlatform, arrivalTime, destStn)
					
					print(bodyMsg)
					
					originalUDP = getOriginalUDP(uri)
					if(udp_port != originalUDP):
						# send transfer information to client
						sockUDP.sendto(bodyMsg.encode(), ('localhost', int(originalUDP)))
				
				
				

	if(TCPconnected and (msg.find("<p>END<p>") != -1)):
		msg = "".join((msg, msg_end))
		client_sock.send(msg.encode())
		client_sock.close()