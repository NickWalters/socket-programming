#!/usr/bin/env python3
import socket
import sys
import datetime
from select import select 
#Initialise
HEADERSIZE = 10
MAX_PACKET = 32768
route_data = []
str_data = ""
destination_data = []
back_port = []
udp_data = ""
finish_flag =0
today_bus_available = True
Direct_flag = False
TCP_connect = False
UDP_connect = False
host = "localhost"
destination_name = ""
station_count = 0

TCP_port = 0
UDP_port = 0
UDP_neighb_port = 0

station_name = sys.argv[1]
TCP_port = int(sys.argv[2])
UDP_port = int(sys.argv[3])
UDP_neighb_port = sys.argv[4:]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, TCP_port))
s.listen(5)

# Read Station data
def readfile(station):
    f = open("tt-"+station+".txt", "r")
    for i in f:
        route_data.append(i.rstrip('\n').split(','))
    route_data.remove(route_data[0])
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
            <div class="img_center"><img src = "data:image/png;base64,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">
            <hr>
            <h1>Welcome to TransPerth!</h1>
            <hr>
            </div>
            <h2>The Route of the journey shows below:</h2>

            </body>
            </html>'''

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
            print("My route data is --------------->", route_data)
            print("My destination name is ----------->", destination_name)

            for i in route_data:
                if destination_name==i[4]:
                    Direct_flag = True

            
            print("The first Direct flag is ----------->", Direct_flag)

            destination_data.clear()


            # Check nearest depature time, if it's direct must have direct neighbour. If not, choose data and send to neighbour
            if(Direct_flag):
                for i in route_data:
                    # Noticed that there is not new line at the end of txt file
                    a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
                    a =a.split(" ")[1]

                    if (a>current_time and destination_name==i[4]):
                        destination_data.append(i)
            else:
                for i in route_data:
                    # Noticed that there is not new line at the end of txt file
                    a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
                    a =a.split(" ")[1]
                    if (a>current_time):
                        destination_data.append(i)

            print("Now the destination data is -------------->", destination_data)

            # Today don't have no more bus
            if(len(destination_data)==0 ):
                for i in route_data:
                    if(destination_name==i[4]):
                        print("True the destination data is empty")
                        today_bus_available = False
                        destination_data.append(i)
                        break
                    else:
                        destination_data.append(route_data[0])

            # If there are direct destination

            if Direct_flag:
                leave_time = destination_data[0][0]
                vehicle_number = destination_data[0][1]
                platform = destination_data[0][2]
                arrive_time = destination_data[0][3]
            else:
                leave_time = " "
                vehicle_number = " "
                platform = " "
                arrive_time = destination_data[0][3]

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
                # List of neighbour UDP_port
                for i in UDP_neighb_port:
                    neighb = ('localhost',int(i) )
                    
                    key_data = str(UDP_port)+"&"+str(destination_name)+"&"+str(arrive_time+"&"+str(station_name)+"&"+str(station_count))

                    # print("First destination data------------------------>",destination_data)

                    # print("data------------------------>", str_data)
                    s_udp.sendto( key_data.encode(), neighb)
                    station_count = station_count + 1

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

            else:
                # Get info from last neighbour
                data2 = data1.split("&")
                # print("Data 2 ------->", data2)
                original_port = data2[0]
                final_station = data2[1]
                update_levTime = data2[2]
                original_station = data2[3]
                current_count = data2[4]
                
                route_data.clear()
                destination_data2 = []
                destination_data2.clear()
                readfile(station_name)

                # print("The route data----------->", route_data)
                print("The final data----------->", final_station)
                print("The current count --------------------->", current_count)
                print("The arrive time is now----------------------->", update_levTime)
                # Check if the destination is direct( one ride via bus/train)
                for i in route_data:
                    if final_station==i[4]:
                        Direct_flag =  True

                # print("The second route data is -------------------->", route_data)
                # print("Final station is ------------------------->", final_station)

                print("If there is Direct Route (Second) ? ---->", Direct_flag)
                print(f"My current UDP_port is {UDP_port}")

                if Direct_flag:
                    destination_data2 = []
                    now_time = datetime.datetime.now()
                    current_time = now_time.strftime("%H:%M")
                    def checkDepature(data,time,des):
                        for i in data:
                            # Noticed that there is not new line at the end of txt file
                            a= str(now_time.replace(hour=int(i[0][0:2]),minute=int(i[0][3:5]),second=0, microsecond=0 ))
                            a =a.split(" ")[1]

                            if (a>time and des==i[4]):
                                destination_data2.append(i)
                                today_bus_available = True
                                break
                            else:
                                today_bus_available = False

                    checkDepature(route_data,update_levTime,final_station)
                    print("Now the route data in DIRECT route is-------->", destination_data2)

                    print("Check today bus is availbalbe ???????", today_bus_available)
                    if (today_bus_available):
                        a = ' '
                        a = a.join(destination_data2[0])
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
                                destination_data2.append(i)
                                break
                    checkDepature(route_data,update_levTime,final_station)
                    print("Now the route data in undirect route is-------->", destination_data2)
                    new_levTime = destination_data2[0][0]
                    print("Now new depature time is -------->", new_levTime)
                    # List of neighbour UDP_port
                    for i in UDP_neighb_port:
                        neighb = ('localhost',int(i) )
                        
                        key_data = str(original_port)+"&"+str(final_station)+"&"+str(new_levTime+"&"+str(original_station)+"&"+str(current_count))

                        # print("First destination data------------------------>",destination_data)
                        if(int(i)!=from_port):
                            print(f"will send to the neighb ------->", i)
                            s_udp.sendto( key_data.encode(), neighb)
                        else:
                            print(f"This is the the neighb port we don't wanna send {from_port}")                        


                    # inputs.clear()

        

        

    




    



