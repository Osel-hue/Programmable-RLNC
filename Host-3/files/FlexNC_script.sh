#!/bin/bash

first=1
runs=50

echo "Start sliding window python code in containers for video traffic..."
for ((i=first; i<=runs; i++));
do
  echo "Start encoder $i..."
  docker exec -d rfsim5g-hcs-encoder  bash -c "timeout 35s python3 FlexNC_encoder.py sw"
  echo "Start decoder $i..."
  docker exec -d rfsim5g-oai-nr-ue  bash -c "python3 FlexNC_decoder.py vid_flexnc_sw_$i.csv sw"
  echo "Start DN $i..."
  docker exec -d rfsim5g-oai-ext-dn  bash -c "tcpreplay -i eth0 --timer=nano enc_video_1080p.pcap"
  sleep 35
done


sleep 10



echo "Start systematic block coding (sbc) python code in containers for video traffic..."
for ((i=first; i<=runs; i++));
do
  echo "Start encoder $i..."
  docker exec -d rfsim5g-hcs-encoder  bash -c "timeout 35s python3 FlexNC_encoder.py sbc"
  echo "Start decoder $i..."
  docker exec -d rfsim5g-oai-nr-ue  bash -c "python3 FlexNC_decoder.py vid_flexnc_sbc_$i.csv sbc"
  echo "Start DN $i..."
  docker exec -d rfsim5g-oai-ext-dn  bash -c "tcpreplay -i eth0 --timer=nano enc_video_1080p.pcap"
  sleep 35
done

sleep 5


echo "Copy CSV files from UE container to host3"
for ((i=first; i<=runs; i++));
do
  docker cp rfsim5g-oai-nr-ue:/opt/oai-nr-ue/vid_flexnc_sw_$i.csv ./
  docker cp rfsim5g-oai-nr-ue:/opt/oai-nr-ue/vid_flexnc_sbc_$i.csv ./
done

sleep 15

echo "Run bash script for when No Network Coding:"
/bin/bash ./No_RLNC_script.sh


exit
