import socket
import struct
import sys
import time
import csv

OUTPUT_FILE = sys.argv[1]

# Total number of packets 
tot_pkt = int(sys.argv[2]) 

owd_result = list() # list of one-way-delays
data_buffer = list() #list storing received data and its timestamp
owd_result.clear()
data_buffer.clear()


BUFSIZE = 4084

# Decoder network configurations
dec_ip = "172.19.0.67" 
dec_port = 9020
dec_info = (dec_ip, int(dec_port))
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(dec_info)

recv_idx = 0
send_idx = 0
send_idx_buf = []
flag = False 
in_rec = 0
send_time_buf = [] 

timeout = 10
receiver.settimeout(timeout)

while True:
     try:
        origin_data = receiver.recv(BUFSIZE)
     except socket.timeout:
        break
     recv_time = time.time() * 1e6
     in_rec = in_rec +1
     if recv_idx == 0:
        bw_mon_st = recv_time
     sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12]) #unpack sender's info in b' form
     send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7]
     send_time =int.from_bytes(send_time_bytes, 'little')
     send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
     send_idx=int.from_bytes(send_idx_bytes, 'little')
     print(send_time, send_idx)
     if send_idx == 123456789:
        break
     data_buffer.append((origin_data, recv_time))
     recv_idx = recv_idx+1
     if send_idx == tot_pkt:
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

print('Received packet', in_rec)
print('## Recovered packet', recv_idx+1)   
#Mbits/s
bw = (total_size/(bw_mon_end - bw_mon_st))*8  
print(f'Bandwidth: {bw}Mbits/s')
pkt_loss = ((tot_pkt - (recv_idx + 1))*100)/(tot_pkt)
print('Packet loss% :', pkt_loss)                
with open(OUTPUT_FILE, 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(zip(send_idx_buf, owd_result, send_time_buf)) 
    writer.writerow([recv_idx + 1, bw, in_rec])

receiver.close()        
        
        
        
        
