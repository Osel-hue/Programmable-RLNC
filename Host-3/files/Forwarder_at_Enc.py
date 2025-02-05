import socket

BUFSIZE = 2048

# Encoder network configurations
enc_ip = "192.168.72.145"
enc_port = 9050
enc_info = (enc_ip, enc_port)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
receiver.bind(enc_info)

# UE network configurations
ue_ip = "12.1.1.2" 
ue_port = 9000
ue_info = (ue_ip, int(ue_port))
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


def forward():
     pkt_data, net_info = receiver.recvfrom(BUFSIZE)
     fwd.sendto(pkt_data,ue_info)

while True:
    forward()
