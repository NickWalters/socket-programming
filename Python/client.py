import socket


tcp_port = 4444
udp_port = 9991


# Create TCP/IP socket
c = socket.socket()

# The server adress to connect to
server_address = ('localhost', tcp_port)

# connect to the server adress
c.connect(server_address)


#get information/feedback from the server, and print it
print(c.recv(1024).decode())

