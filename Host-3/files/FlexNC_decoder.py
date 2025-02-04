import socket
import struct
import sys
import time
import csv

# TODO: Import your RLNC module here and replace the placeholder for proprietary RLNC library
import rlnc_library

Audio =  [26425, 480]
Video = [11942, 1328]
Haptic = [635000, 82]

owd_result = list() # list of oneway delays
data_buffer = list() #list storing received data and its timestamp
owd_result.clear()
data_buffer.clear()

OUTPUT_FILE = sys.argv[1]
nc_protocol = sys.argv[2]

BUFSIZE = 4084

send_idx = 0
index = []
send_idx_buf = []

# UE IP address and port where packets will arrive
ue_ip = "12.1.1.2" 
ue_port = 9000
ue_ip_port = (ue_ip, ue_port)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(ue_ip_port)

if nc_protocol == "sw":
    # TODO: Initialize your SW encoder object for different traffic types and replace the following placeholders
    dec1 = rlnc_library.Dec("Define RLNC SW parameters for Decoder specific to Video")
    dec2 = rlnc_library.Dec("Define RLNC SW parameters for Decoder specific to Haptic")
    dec3 = rlnc_library.Dec("Define RLNC SW parameters for Decoder specific to Audio")
elif nc_protocol == "sbc":
    # TODO: Initialize your SW encoder object for different traffic types and replace the following placeholders
    dec1 = rlnc_library.Dec("Define RLNC SBC parameters for Decoder specific to Video")
    dec2 = rlnc_library.Dec("Define RLNC SBC parameters for Decoder specific to Haptic")
    dec3 = rlnc_library.Dec("Define RLNC SBC parameters for Decoder specific to Audio")


flag_dec = False 
packet_count = 0
send_time_buf = [] 

def decoding(packet, dec, count, tot_pkt):
     flag = False
     # TODO: Implement RLNC Decoding functionality and replace the placeholder lines 
     "dec.Put_Packet_Dec_Buffer(packet)"
     while "dec.Dec_Buffer_Not_Empty()":      
        origin_data = "dec.Retrieve_Original_Data()"
        recv_time = time.time() * 1e6
        if count == 0:        
            bw_mon_st = recv_time        
        sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12])
        send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7] 
        send_time =int.from_bytes(send_time_bytes, 'little')
        send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
        send_idx=int.from_bytes(send_idx_bytes, 'little') 
        print(send_time, send_idx)
        if send_idx == 123456789: 
            flag = True
            break
        data_buffer.append((origin_data, recv_time))                 
        if send_idx == tot_pkt: 
            flag = True
            break
     return flag

timeout = 5
receiver.settimeout(timeout)

while True:
     try:
        pkt_data = receiver.recv(BUFSIZE)
     except socket.timeout:
        break
     enc_pkt_length = int(len(bytes(pkt_data)))-4
     nc_type = struct.unpack('!I',pkt_data[enc_pkt_length:enc_pkt_length+4])[0] 
     # If data is haptic 
     if nc_type == 1 :
        flag_dec = decoding(pkt_data[0:enc_pkt_length], dec1, packet_count, int(Video[0]))         
     elif nc_type == 2 :
        flag_dec = decoding(pkt_data[0:enc_pkt_length], dec2, packet_count, int(Haptic[0])) 
     elif nc_type == 3 :
        flag_dec = decoding(pkt_data[0:enc_pkt_length], dec3, packet_count, int(Audio[0]))  
     elif nc_type == 41 or nc_type == 42 or nc_type == 43 or nc_type == 0:
        origin_data = pkt_data[0:enc_pkt_length]
        recv_time = time.time() * 1e6
        if packet_count == 0:        
           bw_mon_st = recv_time        
        sender_infobits = struct.unpack("!cccccccccccc", origin_data[0:12])
        send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7]
        send_time =int.from_bytes(send_time_bytes, 'little')
        send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
        send_idx=int.from_bytes(send_idx_bytes, 'little')
        print(send_time, send_idx)
        if send_idx == 123456789: 
           flag = True
           break
        data_buffer.append((origin_data, recv_time))
        if (nc_type == 41 and send_idx == Video[0]) or (nc_type == 42 and send_idx == Haptic[0]) or (nc_type == 43 and send_idx == Audio[0]): 
           flag_dec = True
           break
     packet_count = packet_count+1
     if flag_dec:
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

#Mbits/s
bw = (total_size/(bw_mon_end - bw_mon_st))*8  
print(f'Bandwidth: {bw}Mbits/s')

if nc_type == 41 or nc_type == 1:
    pkt_loss = ((Video[0] - (recv_idx + 1))*100)/(Video[0])
elif nc_type == 42 or nc_type == 2:
    pkt_loss = ((Haptic[0] - (recv_idx + 1))*100)/(Haptic[0])
elif nc_type == 43 or nc_type == 3:
    pkt_loss = ((Audio[0] - (recv_idx + 1))*100)/(Audio[0])
    
print('Packet loss% :', pkt_loss)                
with open(OUTPUT_FILE, 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(zip(send_idx_buf, owd_result, send_time_buf)) 
    writer.writerow([recv_idx + 1, bw])

 
receiver.close()             
        
        
        
