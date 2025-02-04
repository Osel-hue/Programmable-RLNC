import socket
import sys

# TODO: Import your RLNC module here and replace the placeholder for proprietary RLNC library
import rlnc_library

# TODO: Initialize your SBC encoder object here and replace the following placeholder
enc = rlnc_library.Enc("Define RLNC SBC parameters for Encoder")

# Encoder IP address and port where packets will arrive
enc_ip = "192.168.72.145"
enc_port = 9050
enc_ip_port = (enc_ip, enc_port)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(enc_ip_port)

# UE IP address and port to where encoded packets will be send
ue_ip = "12.1.1.2"
ue_port= 9000
ue_ip_port_map = (ue_ip, ue_port)
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

BUFSIZE = 2048

# Function performing RLNC Encoding with proprietary functions hidden
def encode_pkts():
     pkt_data, net_info = receiver.recvfrom(BUFSIZE)
     # TODO: Implement RLNC Encoding functionality and replace the placeholder lines 
     "enc.Source_Data_Processing(pkt_data)"
     while "enc.Enc_Processing_Condition()":
        data = "enc.Retrieve_Encoded_Data()"
        fwd.sendto(data,ue_ip_port_map)

while True:
    encode_pkts()
