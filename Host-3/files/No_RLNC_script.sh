#!/bin/bash

first=1
runs=50

echo "Start No NC python code in containers for video traffic..."
for ((i=first; i<=runs; i++));
do
  echo "Start receiver $i..."
  docker exec -d rfsim5g-oai-nr-ue  bash -c "python3 receiver.py vid_$i.csv 11942"
  echo "Start DN $i..."
  docker exec -d rfsim5g-oai-ext-dn  bash -c "tcpreplay -i eth0 --timer=nano ue_video_1080p.pcap"
  sleep 35
done


sleep 5

echo "Copy CSV files from UE container to host3"
for ((i=first; i<=runs; i++));
do
  docker cp rfsim5g-oai-nr-ue:/opt/oai-nr-ue/vid_$i.csv ./
done


echo "Run bash script for with Single Network Coding:"
/bin/bash ./Pure_RLNC_script.sh

exit
