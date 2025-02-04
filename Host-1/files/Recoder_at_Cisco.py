import socket

# TODO: Import your RLNC module here and replace the placeholder for proprietary RLNC library
import rlnc_library


# TODO: Initialize your SBC recoder object here and replace the following placeholder
rec = rlnc_library.Rec("Define RLNC SBC parameters for Recoder")

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


# TODO: Implement RLNC Recoding functionality and replace the placeholder lines 
def collect_rec():
     while "rec.Rec_Processing_Condition()":
        rec_data = "rec.Retrieve_Recoded_Data()" 
        fwd.sendto(rec_data,dec_info)


while True:
     try:
        pkt_data, net_info = receiver.recvfrom(BUFSIZE)
        rcv_idx = rcv_idx + 1
     except socket.timeout:
        break
     # TODO: Implement RLNC Recoding functionality and replace the placeholder lines
     "rec.Trigger_When_Ready(collect_rec)" 
     "rec.Put_Packet_Rec_Buffer(pkt_data)"


print('Total packets recevied from Encoder: ', rcv_idx)

