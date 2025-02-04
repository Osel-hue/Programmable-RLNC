import socket

BUFSIZE = 2048

# Recoder network configurations
rec_ip = "172.19.0.66" 
rec_port = 9010
rec_info = (rec_ip, int(rec_port))
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(rec_info)

# Decoder network configurations
dec_ip = "172.19.0.67" 
dec_port = 9020
dec_info = (dec_ip, int(dec_port))
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

rcv_idx = 0

timeout = 10
receiver.settimeout(timeout)
while True:
     try:
        pkt_data, net_info = receiver.recvfrom(BUFSIZE)
     except socket.timeout:
        break
     fwd.sendto(pkt_data,dec_info)  
     rcv_idx = rcv_idx +1

print('From Encoder: ', rcv_idx)
