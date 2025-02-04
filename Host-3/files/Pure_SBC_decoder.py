import socket
import struct
import sys
import time
import csv

# TODO: Import your RLNC module here and replace the placeholder for proprietary RLNC library
import rlnc_library


owd_result = list() # list of one-way-delays
data_buffer = list() #list storing received data and its timestamp
owd_result.clear()
data_buffer.clear()

OUTPUT_FILE = sys.argv[1]

# Total number of packets 
tot_pkt = int(sys.argv[2])

BUFSIZE = 4084
recv_idx = 0

send_idx = 0
index = []
send_idx_buf = []

# UE IP address and port where packets will arrive
ue_ip = "12.1.1.2"
ue_port = 9000
ue_ip_port = (ue_ip, ue_port)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
receiver.bind(ue_ip_port)

# TODO: Initialize your SBC decoder object here and replace the following placeholder
dec = rlnc_library.Dec("Define RLNC SBC parameters for Decoder")

flag = False 
send_time_buf = [] 

while True:     
     pkt_data = receiver.recv(BUFSIZE)   
     # TODO: Implement RLNC Decoding functionality and replace the placeholder lines 
     "dec.Put_Packet_Dec_Buffer(pkt_data)"
     while "dec.Dec_Buffer_Not_Empty()":      
        origin_data = "dec.Retrieve_Original_Data()"
        recv_time = time.time() * 1e6
        if recv_idx == 0:        
            bw_mon_st = recv_time        
        sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12]) #unpack sender's info in b' form
        send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7] 
        send_time =int.from_bytes(send_time_bytes, 'little')
        send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
        send_idx=int.from_bytes(send_idx_bytes, 'little') 
        print(send_time, send_idx)
        if send_idx == 123456789: 
            flag = True
            break
        data_buffer.append((origin_data, recv_time))
        recv_idx = recv_idx+1          
        if send_idx == tot_pkt: 
            flag = True
            break
     if flag:
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


bw = (total_size/(bw_mon_end - bw_mon_st))*8  
print(f'Bandwidth: {bw}Mbits/s')
pkt_loss = ((tot_pkt - (recv_idx + 1))*100)/(tot_pkt)
print('Packet loss% :', pkt_loss)                
with open(OUTPUT_FILE, 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(zip(send_idx_buf, owd_result, send_time_buf)) 
    writer.writerow([recv_idx + 1, bw])

receiver.close()        
        
        
        
        
