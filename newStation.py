#!/usr/bin/python

import socket
import sys
from datetime import datetime
from select import select 
import time

routes = []
destination_info = []
back_port = []
neighbour_name = []


string_info = ""
destinationStation = ""
udp_info = ""
websiteIP = "localhost"

today = True
direct = False
tcp_conn = False
udp_conn = False

target = 0
tcp_port = 0
udp_port = 0
udp_neighbour_port = 0

MAX_PACKET = 45432
HEADERSIZE = 10

# ARGUMENTS **********************************************************

argcount = len(sys.argv)
arglist = []

for arg in sys.argv:
	arglist.append(str(arg))

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

udp_neighbour_port = sys.argv[4:]


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
		print("\n\n\n\n\n")
		for item in reversed(routes):
			print(item)
		print("\n\n\n\n\n")
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
	else:
		print("Error: There was no request from the Client to go Anywhere")
		
		
		

# NETWORKING *********************************************************


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

# the different tcp/udp sockets to read from, using select()
inputs = [sockTCP, sockUDP]
outputs = []
message_q = {}

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
</body>
</html>
'''


while inputs:
	readable, writable, exceptions = select(inputs, [], [])
	for sock in readable:
		# Check if socket is TCP
		if sock is sockTCP:
			client_sock, client_addr = sockTCP.accept()
			print("(TCP) Now Connected to:", client_addr)
			if client_sock:
				# recieve the data (and adress) from client
				data, addr = client_sock.recvfrom(1024)
				
				dataList = data.decode().split('\n')
				head = dataList[0]
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
				
				direct = checkDirectRoute(destinationStation)
				
				# destination_info.clear()
				
				if(direct):
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
					inputs.clear()
					client_sock.send(msg.encode())
					client_sock.close()
				else:
					# there is no direct route, requires transfer
					for neigh in udp_neighbour_port:
						sockUDP.sendto("request_station".encode(), ('localhost', int(neigh)))
				
				
		# UDP socket
		if sock is sockUDP:
			udp_conn = True
			data, addr = sockUDP.recvfrom(1024)
			print("(UDP) Now Connected to:", addr)
				