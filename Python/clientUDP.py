import socket

udp_port = 9991
Message = "North Terminus to South Busport"


# Create socket
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# The server adress to connect to
server_address = ('localhost', udp_port)

# Send a Message
c.sendto(Message.encode(), server_address)

