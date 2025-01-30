docker network create -d overlay --subnet=192.168.71.128/26 --attachable rfsim5g-oai-public-net
docker network create -d overlay --subnet=192.168.72.128/26  --attachable rfsim5g-oai-traffic-net
