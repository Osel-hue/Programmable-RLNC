docker cp files/ue_video_1080p.pcap rfsim5g-oai-ext-dn:/
docker cp files/enc_video_1080p.pcap rfsim5g-oai-ext-dn:/
docker cp files/tcpreplay-4.4.2 rfsim5g-oai-ext-dn:/

docker cp files/single_encoder.py rfsim5g-hcs-encoder:/
docker cp files/sampling.py rfsim5g-hcs-encoder:/

docker cp files/single_decoder.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/decoder_sampling.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue
docker cp files/receiver.py rfsim5g-oai-nr-ue:/opt/oai-nr-ue

echo "FINISHED!!!"
