from encodings import utf_8
import socket
import struct
import sys
import time
import csv
from scapy.all import *

Audio =  [26425, 1328]
Video = [11942, 1328] 
Haptic = [635000, 82]

owd_result = list() # list of oneway delays
data_buffer = list() #list storing received data and its timestamp
owd_result.clear()
data_buffer.clear()

OUTPUT_FILE = sys.argv[1]

# Change it to audio, video or haptic depending on traffic under test
tot_pkt = int(sys.argv[2])

ue_ip = "12.1.1.2" 
ue_port = 9000 
ue_info = (ue_ip, int(ue_port))
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
server.bind(ue_info)

BUFSIZE = 4084

recv_idx = 0
send_idx = 0
index = []
send_idx_buf = []
send_time_buf = [] 
while True:
    origin_data = server.recv(BUFSIZE)
    recv_time = time.time() * 1e6
    if recv_idx == 0:        
        bw_mon_st = recv_time
    sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12])
    send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7] 
    send_time =int.from_bytes(send_time_bytes, 'little')
    send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
    send_idx=int.from_bytes(send_idx_bytes, 'little') 
    print(send_time, send_idx)
    if send_idx == 123456789 :
        print('Ending packet received, i.e., last pkt lost')
        break
    data_buffer.append((origin_data, recv_time))
    recv_idx = recv_idx+1
    if send_idx == tot_pkt :
        break

bw_mon_end = time.time() * 1e6
total_size = 0

for recv_idx, (origin_data, recv_time) in enumerate(data_buffer):
    sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12]) 
    send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7] 
    send_time =int.from_bytes(send_time_bytes, 'little')
    send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
    send_idx=int.from_bytes(send_idx_bytes, 'little') 
    owd = recv_time - send_time
    owd_result.append(owd)
    send_idx_buf.append(send_idx)
    send_time_buf.append(send_time)
    total_size = total_size + len(origin_data)

print('Received packet', recv_idx)    
# Mbit/s
bw = (total_size /(bw_mon_end - bw_mon_st))*8
print(f'Bandwidth: {bw}Mbits/s')
pkt_loss = ((tot_pkt - (recv_idx + 1))*100)/(tot_pkt)
print('Packet loss% :', pkt_loss)

with open(OUTPUT_FILE, 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(zip(send_idx_buf, owd_result, send_time_buf)) 
    writer.writerow([recv_idx + 1, bw])

server.close

