import socket

# Placeholder for proprietary RLNC library
import rlnc_library


# TODO: Initialize your SBC encoder object here and replace the following placeholder
enc = rlnc_library.Enc("Define RLNC SBC parameters for Encoder")

BUFSIZE = 2048

# Source OAI UE network configurations
src_ue_ip = "192.168.74.151"
src_ue_port = 9050
src_ue_info = (src_ue_ip, src_ue_port)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp
receiver.bind(src_ue_info)

# Relay OAI UE network configuration
relay_ue_ip = "12.1.1.2" 
relay_ue_port = 9000
relay_ue_info = (relay_ue_ip, int(relay_ue_port))
fwd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


def encode_pkts():
     pkt_data, net_info = receiver.recvfrom(BUFSIZE)
     # TODO: Implement RLNC Encoding functionality and replace the placeholder lines 
     "enc.Source_Data_Processing(pkt_data)"
     while "enc.Enc_Processing_Condition()":
        data = "enc.Retrieve_Encoded_Data()"
        fwd.sendto(data,relay_ue_info)

while True:
    encode_pkts()
