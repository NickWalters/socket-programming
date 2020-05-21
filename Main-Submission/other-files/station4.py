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
names = []

routes = []

# client request
requestHeader = ""
destinationStation = ""
departureTime = ""
arrivTime = ""
working_withUDP = -1
neighbourIncrement = 0

UDPconnected = False
TCPconnected = False

workingWithURI = ""

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
	for route in routes:
		if(station == route[4]):
			print("found direct route")
			return True
	print("didnt find direct route")
	return False



		
		
# Finds the closest/nearest bus or train from this current station
# needs to be a direct route	
# @return 	returns a route, which is a list
def nextAvailableRoute(current_time, destnStation):
	print("@@@")
	print(current_time)
	possibleBoardingTimes = []
	if(len(destnStation) > 0):
		for this_route in reversed(routes):
			if(this_route[4] == destnStation):
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
			for item in possibleBoardingTimes:
				print("*********************")
				print item
			return possibleBoardingTimes[0]
		else:
			print("Error: There is route that is beyond the current time. You have either missed the last bus, or there is no direct route")
			return -1
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
	print(ls[1])
	return ls[1]


def destStation(uri):
	ls = uri.split("=")
	ls.remove(ls[0])
	tmp = ls[0]
	if(tmp.find("&through") != -1):
	    tmp = tmp.replace("&through", "")
	return(tmp)
	

def scanAllNeighbours(checkmsg, index):
	neighbourStns = namesOfNeighbours()
	for stn in neighbourStns:
		print(stn)
		print("------------------------")
	for i in range(len(neighbourStns)):
		if(index == i):
			thisNeigh = neighbours[i] # UDP of Neighbour
			neighName = neighbourStns[i] # name of neighbour
			sockUDP.sendto(checkmsg.encode(), ('localhost', thisNeigh))
		else:
			continue


def getNeighbour():
	neighbourStns = namesOfNeighbours()



def arrivalTime(uri):
	if(uri.rfind(">") != -1):
		index = uri.rfind(">")
		end_index = index + 6
		startTime = uri[index+1: end_index]
		return startTime
	else:
		return -1
		

def uriContainsTransferStations(uri):
	ls = uri.split("&through=")
	ls.remove(ls[0])
	stns = []

	for item in ls:
		if(item.find("%") != -1):
			end_index = item.find("%")
			stn = item[0:end_index]
			stns.append(stn)
			
		elif(item.find("|") != -1):
			end_index = item.find("|")
			stn = item[0:end_index]
			stns.append(stn)
	return stns
	

# NETWORKING *********************************************************


# output message
msg = '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: Closed

<html>
<body>
<h2>Welcome to Transperth</h2>
<img src="https://cdn.businessnews.com.au/styles/wabn_kb_company_logo/public/transperth.jpg?itok=8dMAeY3K" alt="transperth" width="384" height="80">
<h4> Your route is as follows: <h4>
<hr>
'''

trs_msg = '''<p></p>'''

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

inputs = [sockTCP, sockUDP]
outputs = []

while inputs:
	readable, writable, exceptions = select(inputs, [], [])
	
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
						print("This is a testing line")
						route = nextAvailableRoute(departureTime, destinationStation)
							
						boardTime = route[0]
						transportNumber = route[1]
						stopPlatform = route[2]
						arrivalTime = route[3]
						arrivTime = route[3]
							
						bodyMsg = '''
						<p>START</p>
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
						<p>END</p>
						'''.format(stationName, destinationStation, transportNumber, boardTime, stationName, stopPlatform, arrivalTime, destinationStation)
							
						msg = " ".join((msg, bodyMsg, msg_end))
					else:
						# requires transfer to different station
						uri = request_uri
						
						# get the Departure Time based on current time
						now = datetime.now()
						current_time = now.strftime("%H:%M:%S")
						# departureTime = current_time[0:5]
						
						
						# Get a list of all the neighbours
						nms = namesOfNeighbours()
						dstn = nms[neighbourIncrement]
						
						# calculate a route to the neighbour
						rt = nextAvailableRoute(departureTime, dstn)
						arvl = rt[3]
						transportNumber = rt[1]
						stopPlatform = rt[2]
						
						new_uri = "".join((uri, "&through=", stationName, ">", arvl, "#", str(udp_port), "#"))
						
						workingWithURI = new_uri
						# if i am dealing with multiple station transfers, I need to strip this station information from the URI if there is no route through this station
							
				#SCAN A NEIGHBOUR *************************************************
						# scanAllNeighbours(new_uri, neighbourIncrement)		
						sockUDP.sendto(new_uri.encode(), ('localhost', neighbours[neighbourIncrement]))
							
							
							
		else:
			# UDP Connection
			UDPconnected = True
			data, addr = sockUDP.recvfrom(1024)
			working_withUDP = addr
			uri = data.decode()
			print("(UDP) Now Connected to:", addr)
			print(data.decode())
			print("__________________")
			
			
			# If the recieved data contains HTML, then choose how to display it
			if(uri.find("<p>") != -1):
				if(uri.find("<p>START</p>") != -1):
					msg_body = uri
					msg = " ".join((msg, msg_body))
					print(msg)
				elif(uri.find("<p>END</p>") != -1):
					if(trs_msg.find("<p>END</p>") != -1):
						# do nothing, already have the finished tag
						a = 1+1
					else:
						msg_body = uri
						trs_msg = " ".join((trs_msg, msg_body))
						print(msg)
				
			elif(uri.find("~Finished") != -1):
				end = uri.rfind("|")
				tmp = uri
				print(tmp + "\n\n\n\n\n")
				dstn = tmp[0:end]
				
				now = datetime.now()
				current_time = now.strftime("%H:%M:%S")
				departureTime = current_time[0:5]
				
				transfer_stns = uriContainsTransferStations(tmp)
				numTransfers = len(transfer_stns) - 2

				bMsg = '''
				<p>START</p>
				<p>You Require Transfer(s)<p>
				<div style="background-color:lightyellow; border-style: solid" align="middle" class="center">
				<h2>Starting Station : {} </h2>
				<h3>Starting Time: {} </h3>
				<p></p>
				<p> We will find the next bus from {}, according to the Current Time (now) </p>
				</div>
				'''.format(stationName, departureTime, stationName)
				# msg = "".join((msg, bMsg))
				orgi = getOriginalUDP(uri)
				if(orgi == udp_port):
					msg = "".join((msg, bMsg))
				else:
					sockUDP.sendto(bMsg.encode(), ('localhost', int(orgi)))
			
			if(len(names) < len(neighbours)):
				recv_uri = uri
				for neigh in neighbours:
					if(len(neighbours) == 1 and (neigh == working_withUDP[1])):
						print("test 1")
						sockUDP.sendto(uri.encode(), ('localhost', neigh))
						continue
					else:
						print("test 3")
						name_msg = uri + "}" + stationName + ":" + str(udp_port) + "]"
						sockUDP.sendto(name_msg.encode(), ('localhost', neigh))
				
			if(uri.find("}") != -1):
				ind = uri.rfind("}")
				end = uri.rfind("]")		
				sName = uri[ind+1:end]

				count = 0
				for nm in names:
					if(nm == sName):
						count += 1
						break
				if(count == 0):
					names.append(sName)
				
				while(uri.rfind("}") != -1):
					ind = uri.rfind("}")
					end = uri.rfind("]")
					rm_string = uri[ind:end+1]
					uri = uri.replace(rm_string, "")
					
			
			if(len(names) == len(neighbours) and uri.find("<p>") == -1):
				print("\n Names: \n")
				print(names)
				print("\n Neighbours: \n")
				print(neighbours)
				print("\n")
				print(uri)
				
				if(len(neighbours) == 1 and (neighbours[0] == working_withUDP[1])):
					sockUDP.sendto(uri.encode(), working_withUDP)		
				else:
					destinationStation = destStation(uri)
					if(checkDirectRoute(destinationStation)):
						cur_time = arrivalTime(uri)
						route_final = nextAvailableRoute(cur_time, destinationStation)
						new_arvl = route_final[3]
						
						inx = uri.rfind(">")
						old_arvl = uri[inx+1: inx+6]
						uri = uri.replace(old_arvl, new_arvl)
						
						oUDP = getOriginalUDP(uri)
						msgSend = "".join((uri, "&through=", stationName, "~Finished"))
						sockUDP.sendto("<p>more info...</p><p>END</p>".encode(), ('localhost', int(oUDP)))
						sockUDP.sendto(msgSend.encode(), ('localhost', int(oUDP)))
					else:
						for neigh in names:
							splitter = neigh.rfind(":")
							end = neigh.rfind("]")
							
							n_name = neigh[0:splitter]
							n_udp = neigh[splitter+1:end]
							
							if(n_udp == working_withUDP[1]):
								continue
							else:
								cur_time = arrivalTime(uri)
								if(cur_time == -1):
									now = datetime.now()
									current_time = now.strftime("%H:%M:%S")
									# cur_time = current_time[0:5]
									cur_time = "06:05"
								
								print("\n\nI wanna go to: " + n_name + "\n\n")
								rt = nextAvailableRoute(cur_time, n_name)
								if(rt != -1):
									arvTime = rt[3]
									uri = uri.replace(cur_time, arvTime)
									new_uri = "".join((uri, "&through=", stationName))
									sockUDP.sendto(new_uri.encode(), ('localhost', int(n_udp)))
								else:
									continue
						
											
					
				
							
			
				
				
				
				
	if(TCPconnected and (msg.find("<p>END</p>") != -1) and (msg.find("<p>START</p>") != -1)):
		# display direct html
		msg = "".join((msg, trs_msg, msg_end))
		client_sock.send(msg.encode())
		client_sock.close()
			
	elif(TCPconnected and (trs_msg.find("<p>END</p>") != -1) and (msg.find("<p>START</p>") != -1)):
		# display transfer html
		msg = "".join((msg, trs_msg, msg_end))
		client_sock.send(msg.encode())
		client_sock.close()