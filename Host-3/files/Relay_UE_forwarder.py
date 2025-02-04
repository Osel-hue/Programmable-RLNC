import socket

BUFSIZE = 2048

# Relay OAI UE network configuration
relay_ue_ip = "12.1.1.2" 
relay_ue_port = 9000
relay_ue_info = (relay_ue_ip, int(relay_ue_port))
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(relay_ue_info)

# Recoder network configurations
rec_ip = "172.19.0.66" 
rec_port = 9010
rec_info = (rec_ip, int(rec_port))
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

while True:
    data = receiver.recv(BUFSIZE)
    fwd.sendto(data,rec_info)

receiver.close
