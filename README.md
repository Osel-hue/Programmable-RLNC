# Overview

This repository contains files and codes to implement FlexNC and RecNet in the cloud-native 5G System.  We use OpenAirInterface (OAI) to perform the `basic` deployment of a 5G Core Network and use the `OAI RF simulator` as a RAN Emulator. We integrate Random Linear Network Coding (RLNC) nodes in the 5G System. Each RLNC and 5G node is deployed on a Docker container. We use Docker Compose as an automation tool to streamline the deployment procedure.

If you want to know more about the work, you can find more details in the paper: Measurement Study of Programmable Network Coding in Cloud-native 5G and Beyond Networks. DOI: 
https://doi.org/10.48550/arXiv.2408.06115.

# 1. Testbed Specification #

We used four hosts in our RLNC-enabled 5G testbed, each having the following specifications:

- **CPU:** Intel Core i7-6700 (3.40GHz)
- **RAM:** 32 GB
- **Network Interface Cards (NICs):** Two Intel x550
- **Operating System:** Ubuntu 18.04 (Kernel 4.15.0)
- **Docker Version:** 24.0.1
- **Docker Compose Version:** 2.18.1

These computers are connected using an Aruba 2930F switch having Gigabit ports. To implement RecNet, we use a Cisco Catalyst 9500 switch (`INC Switch`) having a 4-core x86, 2. GHz CPU, 16 GBDDR4 memory, and 16 GB internal storage.

We used Docker Swarm, a container orchestration tool built into Docker, to deploy and manage OAI 5G Core, OAI 5G RAN, and RLNC node containers across these different hosts. The Docker containers are interconnected through three Docker networks: 

- **Control Network:** Enables signalling traffic between the 5G components. Established using Docker Swarm overlay network
- **Data Network:** Manages user traffic to and from UE container. Established using Docker Swarm overlay network
- **Relay Network:** Facilitate communication between  the hosts and the RLNC `Recoder` container. Established using the Docker MacVLAN driver


# 2. Prerequisites for Testbed Implementation #

We deploy OAI 5G nodes using Docker and highly recommend using the OAI Docker images (as `.tar` files) given here in the `images` folder to prevent compatibility issues. Here we provide the steps to run Docker images from a `.tar` file, build Docker networks, and start containers. We use KODO RLNC libraries from Steiwerf which require a license and cannot be open-sourced. Therefore, in all programs where this library is used, we have replaced the actual code lines (using the KODO library) with placeholders. Any user must replace these lines with their own RLNC implementation. The RLNC `Encoder`, the RLNC `Recoder`, and the RLNC `Decoder` containers are built based on Ubuntu 20.04 wherein we install the KODO library. Additionally, we modify the default OAI `UE` Docker image by installing the RLNC library which was used in the `docker-compose.yaml` file. Thus, in the `docker-compose.yaml` file in `Host-3`, make sure to replace our Docker image name with that of your Docker image to run containers.

Copy all the files given in the directory `Host-1`, `Host-2`, `Host-3`, and `Host-4` to your respective hosts.

Below, we mention which containers are deployed on which hosts and switch:

- **Host-1:** `NRF`, `AMF`, `SMF`, and `MySql` 
- **Host-2:** `UPF`
- **Host-3:** `gNB`
- **Host-4:** `ext-DN`, `UE`, `Encoder`, and `Decoder`
- **INC Switch:** `Recoder`

## 2.1. Retrieving the images on Docker-Hub ##

Retrieve the Docker images from OAI.

You may need to log on [docker-hub](https://hub.docker.com/):

```bash
$ docker login
Login with your Docker ID to push and pull images from Docker Hub. If you don't have a Docker ID, head over to https://hub.docker.com to create one.
Username:
Password:
```

Now pull images in the respective host as stated in the previous point.

```bash
$ docker pull mysql:8.0
$ docker pull oaisoftwarealliance/oai-amf:v1.5.0
$ docker pull oaisoftwarealliance/oai-nrf:v1.5.0
$ docker pull oaisoftwarealliance/oai-smf:v1.5.0
$ docker pull oaisoftwarealliance/oai-spgwu-tiny:v1.5.0
$ docker pull oaisoftwarealliance/trf-gen-cn5g:focal

$ docker pull oaisoftwarealliance/oai-gnb:develop
$ docker pull oaisoftwarealliance/oai-nr-ue:develop
```

```bash
$ docker logout
```


## 2.2. Verify Docker Image ##

Check if the image is available in your hosts by using:

```bash
$ docker images
```


## 2.3. Docker Swarm Configurations ##

After we have loaded all the docker images in their respective host, we can now focus on their connection with each other. If all Docker containers (5G and RLNC nodes) are running on one host then Docker Swarm is not needed. However, since our containers are deployed across four hosts, we need to enable Docker Swarm on each host to connect the containers. Following are the necessary steps to 

### 2.3.1. Start Docker Swarm ###

Run the following command to initialize Docker Swarm in `Host-1`:

```bash
$ sudo docker swarm init
```

After this command completes execution, it will display the join instructions for other hosts.


### 2.3.2. Join Docker Swarm ###

On all other hosts (`Host-2`, `Host-3`, and `Host-4`), we need to join the Docker Swarm using the instructions displayed after the execution of the Step 1 command.

### 2.3.3. Create Overlay Network ###

Run the following command in `Host-1`:

```bash
$ sudo bash ./files/create_overlay_networks.sh
```

## 2.4. Recoder on Cisco Switch ##

To deploy the RLNC `Recoder` Docker container on the INC switch we set up the Macvlan network on the `Host-1`.

### 2.4.1. Create Macvlan Network ###

Run the following command in `Host-1`:

```bash
$ docker network create -d macvlan --subnet=172.19.0.0/24  -o parent=enp4s0 ext-destination-net
```

You can create a test container and attach it to the MacVLAN network, to check if the Macvlan Network is created successfully:

```bash
$ docker run -d  -it --network ext-destination-net --ip 172.19.0.50 --name sender fwd_img bash
```

### 2.4.2. Create Macvlan Network ###

Login to the INC Cisco switch. Then create a new application on the Cisco switch and assign the application IP and resources using the following commands:

```
swneu3# conf t
swneu3(config)# app-hosting appid 5g_nc_recoder
swneu3(config-app-hosting)# app-vnic management guest-interface 0
swneu3(config-app-hosting-mgmt-gateway)# guest-ipaddress 172.19.0.66 netmask 255.255.255.0
swneu3(config-app-hosting-mgmt-gateway)# exit
swneu3(config-app-hosting)# app-resource profile custom
swneu3(config-app-resource-profile-custom)# cpu 1024
swneu3(config-app-resource-profile-custom)# memory 1024
swneu3(config-app-resource-profile-custom)# persist-disk 1000
swneu3(config-app-resource-profile-custom)# end
```

Run the following command to deploy your RLNC `Recoder` Docker `.tar` file on the Cisco switch:

```
swneu3# app-hosting install appid 5g_nc_recoder package flash:rlnc.tar
```

Run the container using the following commands:

```
swneu3# app-hosting activate appid 5g_nc_recoder
swneu3# app-hosting start appid 5g_nc_recoder
```

Use the following commands to manage the RLNC `Recoder` Docker container :
```
//stop the container
app-hosting stop appid 5g_nc_recoder

//deactivate 
app-hosting deactivate appid 5g_nc_recoder

//uninstall
app-hosting uninstall appid 5g_nc_recoder
```


# 3. Testbed Implementation #

After ensuring that Docker images are in their respective hosts we can use `docker-compose` to deploy every OAI 5G node and RLNC node as a Docker container.

## 3.1. Deploy OAI 5G CN ##

We first start with deploying and running 5G CN containers. 5G Core has a Control Plane (CP) and a User Plane (UP). We deploy the Network Functions (NFs) of 5G Core CP and UP separately on different hosts (`Host-1` and `Host-2` respectively).

### 3.1.1. Deploy OAI 5G Core CP ###

In your `Host-1`, go to the directory containing `docker-compose.yaml` file. Deploy `NRF`, `AMF`, `SMF`, and `MySql` Docker containers using the following command:

```bash
$ docker-compose up -d
```

Wait for a bit and ensure the containers are healthy:

```bash
$ docker-compose ps -a
       Name                     Command                  State                  Ports            
-------------------------------------------------------------------------------------------------
rfsim5g-mysql        docker-entrypoint.sh mysqld      Up (healthy)   3306/tcp, 33060/tcp         
rfsim5g-oai-amf      /bin/bash /openair-amf/bin ...   Up (healthy)   38412/sctp, 80/tcp, 9090/tcp                              
rfsim5g-oai-nrf      /bin/bash /openair-nrf/bin ...   Up (healthy)   80/tcp, 9090/tcp            
rfsim5g-oai-smf      /bin/bash -c /openair-smf/ ...   Up (healthy)   80/tcp, 8805/udp, 9090/tcp      
```

### 3.1.2. Deploy OAI 5G Core UP ###

In your `Host-2`, go to the directory containing the `docker-compose.yaml` file. Deploy the `UPF` Docker container using the following command:

```bash
$ docker-compose up -d
```

Wait for a bit and ensure the container is healthy:

```bash
$ docker-compose ps -a
       Name                     Command                  State                  Ports            
-------------------------------------------------------------------------------------------------
rfsim5g-oai-spgwu    /openair-spgwu-tiny/bin/en ...   Up (healthy)   2152/udp, 8805/udp          
```

## 3.2. Deploy OAI gNB in RF simulator mode and in Standalone Mode ##

**CAUTION: To execute this 2nd step, the whole `CN5G` SHALL be in a `healthy` state (especially the `mysql` container).**

We deploy a monolithic gNB. In your `Host-4`, go to the directory containing the `docker-compose.yaml` file.

```bash
$ docker-compose up -d 
```

Wait for a bit and check:

```bash
$ docker-compose ps -a
       Name                     Command                  State                  Ports            
-------------------------------------------------------------------------------------------------                              
rfsim5g-oai-gnb      /opt/oai-gnb/bin/entrypoin ...   Up (healthy)               
```

You can verify that the `gNB` is connected with the `AMF`:

```bash
$ docker logs rfsim5g-oai-amf
```

## 3.3. Deploy OAI UE, ext-DN, and RLNC nodes ##

We run the `Decoder` Python script in the `UE` Docker container for FlexNC and have a separate `Decoder` container for RecNet. In your `Host-4`, go to the directory containing the `docker-compose.yaml` file. Then we deploy the `ext-DN`, the `Encoder`, the `Decoder`, the  `Source`, and two `UE` Docker containers using: 

```bash
$ docker-compose up -d 
```

Wait for a bit and check if the containers are running:

```bash
$ docker-compose ps -a        
```


# 4. Evaluation with FlexNC #

We can use the same testbed for both FlexNC and RecNet. Here we start the evaluation with FlexNC.

## 4.1. Copy files from hosts to containers ##

To run the FlexNC algorithm we copy the Python scripts from hosts to the respective Docker container. We use `tcpreplay` to replay pcap files. We have altered `tcpreplay` code to insert timestamps when the packet is sent. This is used for computing One-Way-Delay (OWD). We extract `tcpreplay-4.4.2.zip` in `./files/Host-3`. Then we copy it and other files from `Host-3` to their respective Docker container using the following command in  `Host-3`:

```bash
$ sudo bash ./Host-3/copy_files.sh   
```

## 4.2. Setting Random Packet losses ##

We use Linux NetEm Server (tc-netem) to simulate packet losses in our 5G System. First, we configure our 5G System to experience a uniform random packet loss probability of 10% by running the following command inside the `UPF` container in `Host-2`:

```bash
tc qdisc add dev tun0 root handle 1: prio
tc qdisc add dev tun0 parent 1:3 handle 30: netem loss 10%
tc filter add dev tun0 protocol ip parent 1:0 prio 3 u32 match ip dst 12.1.1.2 flowid 1:3  
```
In our case, the UE IP address is `12.1.1.2`. However, it can be modified to match any desired UE address as needed. After which we can start with the FlexNC evaluation.


## 4.3. Running code and copying files into container ##

As an example, we provide our video pcap file that will be copied into the `ext-DN` container from where we send packets using the previous command. We use `tcpreplay` to replay this video pcap file but must first compile it inside the containers where it will be used (`ext-DN` and `Source`):

```bash
 cd tcpreplay-4.4.2/
make
make install
```
 
Additionally, we provide some bash scripts that will automatically run each test 50 times (for video traffic) and collect OWD in a CSV file. One can change these scripts depending on their container names, number of runs etc. Please run the following command to start the script in `Host-3`, ensuring all containers are running and the necessary files have been copied from their respective hosts to the appropriate containers:

```bash
$ sudo bash ./Host-3/Pure_RLNC_script.sh   
```


## 4.4. Setting Bursty Packet losses ##

We also configure our 5G System to experience bursty packet loss probability using tc-netem. But "First, we need to remove the priority queuing discipline to reset the traffic control settings and ensure that we can apply our bursty packet loss without any conflicting settings (our previous setting with random packet loss) running in parallel. Thus, please run the following command inside the `UPF` container in `Host-2`:

```bash
tc qdisc del dev tun0 root handle 1: prio 
```

Now run the following command inside the `UPF` container in `Host-2` to set bursty packet losses:

```bash
tc qdisc add dev tun0 root handle 1: prio
tc qdisc add dev tun0 parent 1:3 handle 30: netem loss gemodel 2% 10% 75% 0.1%
tc filter add dev tun0 protocol ip parent 1:0 prio 3 u32 match ip dst 12.1.1.2 flowid 1:3
```
After this step, repeat **Step 4.3** to evaluate the FlexNC algorithm in bursty packet losses.


# 5. Evaluation with RecNet #

We use the same testbed but we involve additional container containers like RLNC the `Recoder`. We implement RecNet over two topologies in the 5G System. First, we copy the relevant files into the `Recoder` container.


## 5.1. One-UE topology ##

Please follow the steps below:

### 5.1.1. Copy files to Recoder  ###

To copy relevant files into the `Recoder` container in the Cisco switch:
1. Ensure the `files` is in your `Host-1`.
2. ssh inside the `Recoder` container in the switch and scp the following files from your `Host-1`:

```
scp Host-1@IP-Address:/files/Forwarder_at_Cisco.py .
scp Host-1@IP-Address:/files/Recoder_at_Cisco.py .
```

### 5.1.2. Run the code ###

We now begin the actual evaluation by executing the codes. We implement RecNet for remote users in 5G System. Thus, in our OAI-based testbed, we use the OAI `UE` container as the relay or forwarder and the `Decoder` container as the remote user which is in the same network as the Cisco switch where we deploy the `Recoder` container. We consider three measurement scenarios for our evaluations which are covered below.

#### 5.1.2.1. No RLNC ####

The first measurement scenario is without any RLNC, i.e., it is the default 5G System in UM mode of RLC layer. Since we focus on downlink communication, the receiver is the remote user and the sender is the `ext-DN`. We start by running the Python script in the remote user, referred to as the `Decoder` container, to maintain consistency, even though no RLNC decoding takes place in this scenario. Thus, go inside the `Decoder` container (deployed in `Host-3`) and execute the command:
```bash
$ python3 Received_at_decoder.py output_file_No_RLNC.csv 11942
```
The two arguments of `Received_at_decoder.py` are the output CSV file and the total number of packets sent. After the code is executed, we obtain a CSV file `output_file_No_RLNC.csv` from which we use OWD values and the number of packets received. 

We forward packets through the OAI `UE` container (deployed in `Host-3`) by running the command inside the OAI `UE` container:
```bash
$ python3 Relay_UE_forwarder.py
```

Since no RLNC occurs we also forward packets through the `Encoder` container (deployed in `Host-3`) by running the command inside the `Encoder` container:
```bash
$ python3 Forwarder_at_Enc.py
```

Similarly, since there is no RLNC recoding, packets are forwarded through the `Recoder` container (in the Cisco Switch) by running the command inside the `Recoder` container: 
```bash
$ python3 Forwarder_at_Cisco.py
```

Now we send packets from the `ext-DN` container (deployed in `Host-3`) by running the command inside the `ext-DN` container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano enc_video_1080p.pcap
```

#### 5.1.2.2. Pure SBC ####

The next measurement scenario is Pure SBC without RLNC recoding. Thus, packets are forwarded through the `Recoder` container. 

Inside the `Decoder` container execute the command to enable RLNC decoding:
```bash
$ python3 Decoder_SBC.py output_file_Pure_SBC.csv 11942
```

We forward packets through the OAI `UE` container by running the command inside the OAI `UE` container:
```bash
$ python3 Relay_UE_forwarder.py
```

Packets are RLNC encoded in the `Encoder` container by running the command inside the `Encoder` container:
```bash
$ python3 Pure_SBC_encoder.py
```

As there is no RLNC recoding in this scenario, packets are forwarded through the `Recoder` container by running the command inside the `Recoder` container: 
```bash
$ python3 Forwarder_at_Cisco.py
```

Now we send packets from the `ext-DN` container by running the command inside the `ext-DN` container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano enc_video_1080p.pcap
```


#### 5.1.2.3. RecNet ####

The final measurement scenario is ReNet. Thus, packets are RLNC recoded in the `Recoder` container. 

Similar to the previous scenario, in the `Decoder` container execute the command to enable RLNC decoding:
```bash
$ python3 Decoder_SBC.py output_file_Pure_SBC.csv 11942
```

We forward packets through the OAI `UE` container by running the command inside the OAI `UE` container:
```bash
$ python3 Relay_UE_forwarder.py
```

Packets are RLNC encoded in the `Encoder` container by running the command inside the `Encoder` container:
```bash
$ python3 Pure_SBC_encoder.py
```

In this case, we RLNC recode in the `Recoder` container by running the command inside the `Recoder` container: 
```bash
$ python3 Recoder_at_Cisco.py
```

Now we send packets from the `ext-DN` container by running the command inside the `ext-DN` container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano enc_video_1080p.pcap
```

## 5.2. Two-UE topology ##

Since we already copied files in the  **Step 5.1.1**, we can directly start running the codes:

### 5.2.1. Run the code ###

We evaluate ReNet in the two-UE system wherein the sender and the receiver are both `UEs`. Since we use `tcpreplay` we can't directly run it in the OAI `UE` container so we build a Docker image based on Ubuntu 20.04 and run it as the `Source` container. The `Source` container sends packets to the OAI `UE` container which has the RLNC library and can thus perform RLNC encoding. This OAI  `UE` container will forward or encode packets (depending on the measurement scenario) and send them to the second  OAI  `UE` container which will forward them to the `Recoder` container (in the Cisco switch). From the `Recoder` container, the packets are received at the `Decoder` container.

#### 5.2.1.1. No RLNC ####

The first measurement scenario is without any RLNC. We start by running the Python code inside the `Decoder` container (deployed in `Host-3`) using the command:
```bash
$ python3 Received_at_decoder.py output_file_No_RLNC.csv 11942
```

We forward packets through the relay OAI `UE` container (deployed in `Host-3`) by running the command inside the OAI `UE` container:
```bash
$ python3 Relay_UE_forwarder.py
```

Since no RLNC occurs we also forward packets through the source OAI `UE` container (deployed in `Host-3`) by running the command inside the container:
```bash
$ python3 Src_UE_forwarder.py
```

Similarly, since there is no RLNC recoding, packets are forwarded through the `Recoder` container (in the Cisco Switch) by running the command inside the `Recoder` container: 
```bash
$ python3 Forwarder_at_Cisco.py
```

Finally, we send packets from the `Source` container (deployed in `Host-3`) by running the command inside the `Source` container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano 2_UE_video_1080p.pcap
```

#### 5.1.2.2. Pure SBC ####

Next measurement scenario is Pure SBC without RLNC recoding. 

Inside the `Decoder` container execute the command to enable RLNC decoding:
```bash
$ python3 Decoder_SBC.py output_file_Pure_SBC.csv 11942
```

We forward packets through the relay OAI `UE` container by running the command inside the OAI `UE` container:
```bash
$ python3 Relay_UE_forwarder.py
```

Packets are RLNC encoded in the source OAI `UE` container by running the command inside the container:
```bash
$ python3 Src_UE_encoder.py
```

As there is no RLNC recoding in this scenario, packets are forwarded through the `Recoder` container by running the command inside the `Recoder` container: 
```bash
$ python3 Forwarder_at_Cisco.py
```

Now we send packets from the `Source` container by running the command inside this container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano 2_UE_video_1080p.pcap
```


#### 5.1.2.3. RecNet ####

The final measurement scenario is ReNet. Thus, packets are RLNC recoded in the `Recoder` container. 

Similar to the previous scenario, in the `Decoder` container execute the command to enable RLNC decoding:
```bash
$ python3 Decoder_SBC.py output_file_Pure_SBC.csv 11942
```

Forward packets through the relay OAI `UE` container by running the command inside it:
```bash
$ python3 Relay_UE_forwarder.py
```

Packets are RLNC encoded in the source OAI `UE` container by executing the following command inside the container:
```bash
$ python3 Src_UE_encoder.py
```

In this case, we RLNC recode in the `Recoder` container by running the command inside the `Recoder` container: 
```bash
$ python3 Recoder_at_Cisco.py
```

We send packets from the `Source` container by running the command inside this container where the pcap file is located: 
```bash
$ tcpreplay -i eth0 --timer=nano 2_UE_video_1080p.pcap
```


### Bug fix:
If the Python script cannot capture the traffic sent by `tcpreplay`, run the following commands in the respective container that runs the Python script for example the `Encoder` container.

```
apt update
apt-get install -y nftables
nft add table input_table
nft 'add chain input_table input {type filter hook input priority -300;}'
nft 'add rule input_table input ip protocol udp udp checksum set 0'
```
