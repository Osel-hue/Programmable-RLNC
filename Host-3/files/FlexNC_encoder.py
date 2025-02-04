import socket
import random
import sys
import struct
import itertools
from collections import deque
import numpy as np

# TODO: Import your RLNC module here and replace the placeholder for proprietary RLNC library
import rlnc_library

Audio =  [26425, 480]
Video = [11942, 1328]
Haptic = [635000, 82]

rlnc_protocol = sys.argv[1]

# Check which RLNC protocol the user has applied
if rlnc_protocol == "sw":    
    # TODO: Initialize your SW encoder object for different traffic types and replace the following placeholders
    enc1 = rlnc_library.Enc("Define RLNC SW parameters for Encoder specific to Video")
    enc2 = rlnc_library.Enc("Define RLNC SW parameters for Encoder specific to Haptic")
    enc3 = rlnc_library.Enc("Define RLNC SW parameters for Encoder specific to Audio")

elif rlnc_protocol == "sbc":
    # TODO: Initialize your SBC encoder object for different traffic types and replace the following placeholders
    enc1 = rlnc_library.Enc("Define RLNC SBC parameters for Encoder specific to Video")
    enc2 = rlnc_library.Enc("Define RLNC SBC parameters for Encoder specific to Haptic")
    enc3 = rlnc_library.Enc("Define RLNC SBC parameters for Encoder specific to Audio")


BUFSIZE = 2048

# Encoder network configuration
enc_ip = "192.168.72.145"
enc_port = 9050
enc_ip_port = (enc_ip, enc_port)
# Create receiver's UDP socket
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
receiver.bind(enc_ip_port)

# UE network configuration and UDP socket
ue_ip = "12.1.1.2"
ue_port= 9000
ue_ip_port_map = (ue_ip, ue_port)
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# Number of packets to select every N packets received
# Every (SAMPLE_RATIO) packets, the program will select (SAMPLE_SIZE) random packets from the buffer.
SAMPLE_RATIO = 64*4
SAMPLE_SIZE = 16*4

# Initialize the packet buffer
packet_buffer = deque(maxlen=SAMPLE_RATIO) # packet classificate more up to date if the buffer size is equivalent of sample ratio

packet_count = 0

# Function to select a random sample from the buffer, the sample size is SAMPLE_SIZE
def select_random_packets(buf): 
    select_index = random.randint(0, len(buf)) 
    if select_index - SAMPLE_SIZE < 0:
        selected_packets = list(itertools.islice(buf, select_index, select_index+SAMPLE_SIZE))
    else:
        selected_packets = list(itertools.islice(buf, select_index-SAMPLE_SIZE, select_index)) 
    return selected_packets

def classify_traffic(buf, packets):
    send_time_list = []
    send_idx_list = []
    IPD = []
    pkt_size = []
    
    for packet in packets:
        sender_infobits = struct.unpack("!cccccccccccc", packet[0:12]) # Unpack sender's info in b' form
        send_time_bytes = sender_infobits[0] + sender_infobits[1] + sender_infobits[2] + sender_infobits[3] + sender_infobits[4] + sender_infobits[5] + sender_infobits[6] + sender_infobits[7]
        send_time =int.from_bytes(send_time_bytes, 'little')
        send_idx_bytes = sender_infobits[8] + sender_infobits[9] + sender_infobits[10] + sender_infobits[11]
        send_idx=int.from_bytes(send_idx_bytes, 'little')
        send_time_list.append((send_idx, send_time, int(len(packet))))
        send_idx_list.append(send_idx)
    
    for i, metadata in enumerate(send_time_list[:SAMPLE_SIZE-1]):
        IPD.append((send_time_list[i+1][1] - send_time_list[i][1])/1000)
        pkt_size.append(metadata[2])
    
    IPD_mean = sum(IPD) / len(IPD)     
    payload_mean = np.mean(pkt_size)   
    payload_std_dev = np.std(pkt_size)   
      
    if (payload_mean > 800 and payload_mean <= 1500) and payload_std_dev < 700 and max(pkt_size)>= 1300 and min(pkt_size)>10 and IPD_mean < 20:
        return 1
    elif (payload_mean < pkt_size[-1]+100 and payload_mean > pkt_size[-1]-100) and payload_std_dev < 50 and pkt_size[-1]<350:    
        return 2 
    elif (payload_mean < pkt_size[-1]+2 and payload_mean > pkt_size[-1]-2) and payload_std_dev < 0.4 and max(pkt_size)< pkt_size[-1]+2 and min(pkt_size)>pkt_size[-1]-2:
        return 3 
    else:
        return 0

ENCODING_RATIO = {
  "video" : 0.25*Video[0],     
  "haptic": 0.1*Haptic[0],      
  "audio" : 0.2*Audio[0]       
}

# Function performing RLNC Encoding with proprietary functions hidden
def encoding(enc, packet, size, packet_class):
    # TODO: Implement RLNC Encoding functionality and replace the placeholder lines
    "enc.Source_Data_Processing(packet)"
    while "enc.Enc_Processing_Condition()":
        enc_data = "enc.Retrieve_Encoded_Data()" 
        enc_pkt_length = int(len(bytes(enc_data)))
        enc_data[enc_pkt_length:enc_pkt_length+4] = struct.pack("!I", packet_class)
        fwd.sendto(enc_data,ue_ip_port_map)  
        
traffic_class = 0 # simple forwarding    
 
while True:
    data, addr = receiver.recvfrom(BUFSIZE)
    packet_count += 1

    # Store the received packet in the buffer
    packet_buffer.append(data)

    # Select SAMPLE_SIZE random packets from the buffer every SAMPLE_RATIO packets received
    if packet_count % SAMPLE_RATIO == 0:
        selected_packets = select_random_packets(packet_buffer)
        traffic_class=classify_traffic(packet_buffer, selected_packets)
        
    #Choose the right NC encoder based on the traffic_class 
    if traffic_class == 1:
        if packet_count > int(ENCODING_RATIO["video"]):
            encoding(enc1, data, Video[1], traffic_class)
        else:
            data = bytearray(data + struct.pack("!I", 41))
            fwd.sendto(data,ue_ip_port_map) 
    elif traffic_class == 2:
        if packet_count > int(ENCODING_RATIO["haptic"]):
            encoding(enc2, data, Haptic[1],traffic_class)       
        else:
            data = bytearray(data + struct.pack("!I", 42))
            fwd.sendto(data,ue_ip_port_map) 
    elif traffic_class == 3: 
        if packet_count > int(ENCODING_RATIO["audio"]):
            encoding(enc3, data, Audio[1], traffic_class)       
        else:
            data = bytearray(data + struct.pack("!I", 43))
            fwd.sendto(data,ue_ip_port_map) 
    else:
        data = bytearray(data + struct.pack("!I", 0))
        fwd.sendto(data,ue_ip_port_map) 
        
        
# Close the socket (not reached in this example)
receiver.close()
