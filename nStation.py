#!/usr/bin/env python3
import socket
import sys
import datetime
from select import select 
#Initialise
HEADERSIZE = 10
MAX_PACKET = 32768
routes = []
str_data = ""
destination_info = []
back_port = []
udp_data = ""
finish_flag =0
today_bus_available = True
Direct_flag = False
TCP_connect = False
UDP_connect = False
host = "localhost"
destination_name = ""
targetFound = 0


TCP_port = 0
UDP_port = 0
UDP_neighb_port = 0

station_name = sys.argv[1]
TCP_port = int(sys.argv[2])
UDP_port = int(sys.argv[3])
UDP_neighb_port = sys.argv[4:]
UDP_neighb_name = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, TCP_port))
s.listen(5)

# Read Station data
def readfile(station):
	f = open("tt-"+station+".txt", "r")
	for i in f:
		routes.append(i.rstrip('\n').split(','))
	routes.remove(routes[0])
	f.close()

readfile(station_name)

# UDP/IP
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_udp.bind((host, UDP_port))

# Sockets which expect to read
inputs = [s,s_udp]
# Sockets which expect to write
outputs = []
# Outgoing message queues
message_queues = {}

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
	readable,writeable,exceptional = select(inputs,outputs,inputs)
	for each_sock in readable:
		# Check if is TCP socket
		if each_sock is s:
			connect_client, addr = s.accept()
			print(f'the address {addr} now connected!') 
			data = connect_client.recv(MAX_PACKET).decode()
			if not data:
				print("no data received")
			else:
				print("=======DATA FROM CLIENT===========: \n" + data)

			data = data.split("\n")
			data = data[0].split(" ")
			data = data[1]
			data = data.split("=")
			data = data[1]
			data = data.split("&")
			data = data[0]
			print("The data is----->", data )
			# Get destination name
			# url_specific = data
			# start = url_specific.find("to=") + len("to=")-1
			# end = url_specific.find("&")
			destination_name = data

			# Get leave time
			now_time = datetime.datetime.now()
			current_time = now_time.strftime("%H:%M")

			# Check if the destination is direct( one ride via bus/train), return "None" if not direct
			print("My route data is --------------->", routes)
			print("My destination name is ----------->", destination_name)

			for i in routes:
				if destination_name==i[4]:
					Direct_flag = True

			
			print("The first Direct flag is ----------->", Direct_flag)

			destination_info.clear()


			# Check nearest depature time, if it's direct must have direct neighbour. If not, choose data and send to neighbour
			if(Direct_flag):
				for i in routes:
					# Noticed that there is not new line at the end of txt file
					a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
					a =a.split(" ")[1]
					print("___________TESTING LINE _______________")
					print(a)
					print("___________TESTING LINE _______________")

					if (a>current_time and destination_name==i[4]):
						print("destination info : ")
						destination_info.append(i)
			else:
				for i in routes:
					# Noticed that there is not new line at the end of txt file
					a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
					a =a.split(" ")[1]
					if (a>current_time):
						destination_info.append(i)

			print("Now the destination data is -------------->", destination_info)

			# Today don't have no more bus
			if(len(destination_info)==0 ):
				for i in routes:
					if(destination_name==i[4]):
						print("True the destination data is empty")
						today_bus_available = False
						destination_info.append(i)
						break
					else:
						destination_info.append(routes[0])

			# If there are direct destination

			if Direct_flag:
				leave_time = destination_info[0][0]
				vehicle_number = destination_info[0][1]
				platform = destination_info[0][2]
				arrive_time = destination_info[0][3]
			else:
				leave_time = " "
				vehicle_number = " "
				platform = " "
				arrive_time = destination_info[0][3]

			# Check if it is Direct route or not
			if Direct_flag:
				if(today_bus_available):
					body_data= '''
					<h4>From {Start}, Vehicle {vehicle} at Platform {plf} , Departure Time : {Lv_time}. Arrive Time at {end}: {arv_time}</h4>
					'''.format(Start=station_name, end=destination_name, time=current_time,YorN=Direct_flag ,vehicle=vehicle_number, plf=platform, Lv_time=leave_time ,arv_time=arrive_time)
					print("yes goes first")
					message = "".join((msg,body_data))
				else:
					print("Current time no bus")
					body_data= '''
					<h4>-------------------------------------------------</h4>
					<h4>Today is not bus available after 10pm.</4>
					<h4>-------------------------------------------------</h4>
					<h4>Tomorrow earliest bus route shows below:</h4>
					<h4>From {Start}, Vehicle {vehicle} at Platform {plf} , Departure Time : {Lv_time}. Arrive Time at {end}: {arv_time}</h4>
					'''.format(Start=station_name, end=destination_name, time=current_time,YorN=Direct_flag ,vehicle=vehicle_number, plf=platform, Lv_time=leave_time ,arv_time=arrive_time)
					message = "".join((msg,body_data))
				inputs.clear()
				print("[Target Found] clean the whole inputs")

				connect_client.send(message.encode())
				connect_client.close()

			# There is no direct route
			else:
				for i in UDP_neighb_port:
					s_udp.sendto("request_station".encode(), ('localhost', int(i)))

				
		# UDP socket
		if each_sock is s_udp:
			UDP_connect = True
			udp_data = s_udp.recvfrom(MAX_PACKET)
			print(f"UDP address {udp_data[1]} now has been received")
			data1 = udp_data[0].decode()
			print("Here is the data1------------->", data1)

			from_port = udp_data[1][1]

			print("My current station name ------------->", station_name)

			if(data1.find("sign") != -1):
				targetFound = 1
				print("It goes First")
				print(f"My current UDP_port is {UDP_port}")

				start = data1.find("sign") + len("sign")
				final_length = start - len("sign")

				data_str = data1[0:final_length]

				data_list = []
				print("The data here ------------->", data_str)
				for i in data_str.split(" "):
					data_list.append(i)
				
				body_msg= '''
				<h4>From {Start}, Vehicle {vehicle} at Platform {plf} , Departure Time : {Lv_time}. Arrive Time at {end}: {arv_time}</h4>
				'''.format(Start=station_name, End=data_list[4] ,vehicle=data_list[1], plf=data_list[2], Lv_time=current_time, arv_time=data_list[3], end =data_list[4])

				message = "".join((msg,body_msg) )
				connect_client.send(message.encode())
				connect_client.close()
				inputs.clear()
				print("[Undirect Target Found] clean the whole inputs")
			
			elif(data1.find("nobus") != -1):
				targetFound = 1
				print("There is no bus")

				body_data= '''
					<h4>-------------------------------------------------</h4>
					<h4>Today is not bus available after 10pm.</4>
					<h4>-------------------------------------------------</h4>
					'''
				message = "".join((msg,body_data) )
				connect_client.send(message.encode())
				connect_client.close()
				inputs.clear()
			
			elif(data1.find("request_station") != -1):
				
				s_udp.sendto((station_name+"$").encode(),  udp_data[1])
			
			elif(data1.find("$") != -1):
				data2 = data1[0:len(data1)-1]
				UDP_neighb_name.append(data2)
				# print(f"I found the station name from other neighbour {data2}")

				# print(f"Now UDP neighb name list ------> {UDP_neighb_name}")
				if(len(UDP_neighb_name) == len(UDP_neighb_port)):
					length = 0
					time_table = []
					while(length != len(UDP_neighb_name)):
						for i in routes:
							# Noticed that there is not new line at the end of txt file
							a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
							a =a.split(" ")[1]

							if (a>current_time and UDP_neighb_name[length]==i[4]):
								time_table.append((i))
								break
						length = length + 1

					print(f" Now the time table is------------> {time_table}")
					
					# List of neighbour UDP_portC
					count = 0
					
					print("Now current table is ----------->", time_table)
					for i in UDP_neighb_port:
						arrive_T = time_table[count][3]
						neighb = ('localhost',int(i) )
						
						key_data = str(UDP_port)+"&"+str(destination_name)+"&"+str(arrive_T)+"&"+str(station_name)+"&"+str(targetFound)
						print(f"Now choose which talbe= =========== {arrive_T}")
						print(f" UDP_port: {UDP_port}   destination_name: {destination_name}  arrive_time: {arrive_T}  originalstation: {station_name}")

						s_udp.sendto( key_data.encode(), neighb)
						count = count + 1


			

			else:
				

				# Get info from last neighbour
				data2 = data1.split("&")
				# print("Data 2 ------->", data2)
				original_port = data2[0]
				final_station = data2[1]
				update_levTime = data2[2]
				original_station = data2[3]
				findTarget = data2[4]

				
				routes.clear()
				destination_info2 = []
				destination_info2.clear()
				readfile(station_name)

				# print("The route data----------->", routes)
				print("The final data----------->", final_station)
				print("The arrive time is now----------------------->", update_levTime)
				# Check if the destination is direct( one ride via bus/train)
				for i in routes:
					if final_station==i[4]:
						Direct_flag =  True

				# print("The second route data is -------------------->", routes)
				# print("Final station is ------------------------->", final_station)

				print("If there is Direct Route (Second) ? ---->", Direct_flag)
				print(f"My current UDP_port is {UDP_port}")

				if Direct_flag:
					destination_info2 = []
					now_time = datetime.datetime.now()
					current_time = now_time.strftime("%H:%M")
					def checkDepature(data,time,des):
						for i in data:
							# Noticed that there is not new line at the end of txt file
							a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
							a =a.split(" ")[1]

							if (a>time and des==i[4]):
								destination_info2.append(i)
								today_bus_available = True
								break
							else:
								today_bus_available = False

					checkDepature(routes,update_levTime,final_station)
					print("Now the route data in DIRECT route is-------->", destination_info2)

					print("Check today bus is availbalbe ???????", today_bus_available)

					if(int(targetFound)==0):
						if (today_bus_available):
							a = ' '
							a = a.join(destination_info2[0])
							print("Now a is [Second] destination data --------------------->", a)
							s_udp.sendto((a+"sign").encode(), ('localhost',int(original_port) ) )
						else:
							s_udp.sendto("nobus".encode(), ('localhost',int(original_port) ) )

				else:
					print("don't have direct route")
					now_time = datetime.datetime.now()
					current_time = now_time.strftime("%H:%M")
					def checkDepature(data,time,des):
						for i in data:
							# Noticed that there is not new line at the end of txt file
							a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
							a =a.split(" ")[1]
							if (a>time):
								destination_info2.append(i)
								break
					checkDepature(routes,update_levTime,final_station)
					print("Now the route data in undirect route is-------->", destination_info2)
					new_levTime = destination_info2[0][0]
					print("Now new depature time is -------->", new_levTime)
					# List of neighbour UDP_port
					for i in UDP_neighb_port:
						neighb = ('localhost',int(i) )
						
						key_data = str(original_port)+"&"+str(final_station)+"&"+str(new_levTime+"&"+str(original_station)+"&"+str(targetFound))

						# print("First destination data------------------------>",destination_info)
						if(int(i)!=from_port):
							print(f"will send to the neighb ------->", i)
							s_udp.sendto( key_data.encode(), neighb)
						else:
							print(f"This is the the neighb port we don't wanna send {from_port}")                        


					# inputs.clear()
