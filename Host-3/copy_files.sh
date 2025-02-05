docker cp files/ue_video_1080p.pcap rfsim5g-oai-ext-dn:/
docker cp files/enc_video_1080p.pcap rfsim5g-oai-ext-dn:/
docker cp files/2_UE_video_1080p.pcap rfsim5g-hcs-source:/

docker cp files/tcpreplay-4.4.2 rfsim5g-oai-ext-dn:/
docker cp files/tcpreplay-4.4.2 rfsim5g-hcs-source:/

docker cp files/Pure_SBC_encoder.py rfsim5g-hcs-encoder:/
docker cp files/Pure_SW_encoder.py rfsim5g-hcs-encoder:/
docker cp files/FlexNC_encoder.py rfsim5g-hcs-encoder:/
docker cp files/Forwarder_at_Enc.py rfsim5g-hcs-encoder:/

docker cp files/Pure_SBC_decoder.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/Pure_SW_decoder.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/FlexNC_decoder.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/receiver.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/Relay_UE_forwarder.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue

docker cp files/Src_UE_forwarder.py rfsim5g-oai-nr-ue2:/opt/oai-nr-ue
docker cp files/Src_UE_encoder.py rfsim5g-oai-nr-ue2:/opt/oai-nr-ue

docker cp files/Decoder_SBC.py rfsim5g-hcs-decoder:/
docker cp files/Received_at_decoder.py rfsim5g-hcs-decoder:/

echo "FINISHED!!!"
