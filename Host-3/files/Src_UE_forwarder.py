import socket

BUFSIZE = 2048

# Source OAI UE network configurations
src_ue_ip = "192.168.74.151" 
src_ue_port = 9050
src_ue_info = (src_ue_ip, int(src_ue_port))
receiver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
receiver.bind(src_ue_info)

# Relay OAI UE network configuration
relay_ue_ip = "12.1.1.2" 
relay_ue_port = 9000
relay_ue_info = (relay_ue_ip, int(relay_ue_port))
fwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  

while True:
    data = receiver.recv(BUFSIZE)
    fwd.sendto(data, relay_ue_info)    

receiver.close
