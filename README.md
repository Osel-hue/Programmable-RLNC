# Overview

This repository contains files and codes needed to implement FlexNC and RecNet in cloud-native 5G System. We use OpenAirInterface (OAI) to perform `basic` deployment of of 5G Core Network and use `OAI RF simulator` as RAN Emulator. We integrate in Random Linear Network Coding (RLNC) nodes in 5G System. Each RLNC and 5G node is deployed on a Docker container. We use Docker Compose as an automation tool to streamline the deployment procesdure.

# 1. Testbed Specification #

We used four hosts in our RLNC-enabled 5G testbed, each having the following specifications:

- **CPU:** Intel Core i7-6700 (3.40GHz)
- **RAM:** 32 GB
- **Network Interface Cards (NICs):** Two Intel x550
- **Operating System:** Ubuntu 18.04 (Kernel 4.15.0)
- **Docker Version:** 24.0.1
- **Docker Compose Version:** 2.18.1

These computers are connected using a Aruba 2930F switch having Gigabit ports. To implement RecNet, we use a Cisco Catalyst 9500 switch (`INC Switch`) having a 4-core x86, 2. GHz CPU, 16 GBDDR4 memory, and 16 GB internal storage.

We used Docker Swarm, a container orchestration tool built into Docker, to deploy and manage OAI 5G Core and OAI 5G RAN containers across these different hosts. The Docker container are interconnected through three Docker networks: 

- **Control Network:** Enables signaling traffic between the 5G components. Established using Docker Swarm overlay network
- **Data Network:** Manages user traffic to and from UE container. Established using Docker Swarm overlay network
- **Relay Network:** Facilitate communication the hosts and RLNC `Recoder` container. Established using the Docker MacVLAN driver


# 2. Prerequisites for Testbed Implementation #

We deploy OAI 5G nodes using Docker and highly recommend using the OAI Docker images (as `.tar` files) given here at `images` folder to prevent compatibility issues. Here we provide the steps to run Docker images from a `.tar` file, build Docker network, and start containers. We build a container based on Ubuntu 20.04, where we install the necessary coding libraries. This container can be used as a RLNC node (`Encoder`, `Recoder`, and `Decoder`). We use KODO RLNC libraries from Steiwerf which require license and cannot be open-sources. Therefore, in all programs where this library is used, we must mask the corresponding code lines. Copy all the files given in the directory `Host-1`, `Host-2`, `Host-3`, and `Host-4` to your respective hosts.

Below, we mention which containers are deployed on which hosts and switch:

- **Host-1:** `NRF`, `AMF`, `SMF`, and `MySql` 
- **Host-2:** `UPF`
- **Host-3:** `gNB`
- **Host-4:** `ext-DN`, `UE`, and `Encoder`
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

After we have all the loaded all the docker image in their respective host, we can now focus on their connection between each other. If all Docker containers (5G and RLNC nodes) are ran on one host then Docker Swarm is not needed. However, since our containers are deployed across four hosts, we need to enable Docker Swarm on each host to connect the containers. Following are the necessary steps to 

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

To deploy RLNC `Recoder` Docker container on INC switch we set up Macvlan network on the `Host-1`.

### 2.4.1. Create Macvlan Network ###

Run the following command in `Host-1`:

```bash
$ docker network create -d macvlan --subnet=172.19.0.0/24  -o parent=enp4s0 ext-destination-net
```

You can create a test container and attach it to the MacVLAN network, to check if Macvlan Network is created successfully:

```bash
$ docker run -d  -it --network ext-destination-net --ip 172.19.0.50 --name sender fwd_img bash
```

### 2.4.2. Create Macvlan Network ###

Login to the INC Cisco switch. Then create a new application on Cisco switch and assign the application IP and resources using the following commands:

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


### Bug fix:
In case the python script cannot capture the traffic sent by tcpreplay, you need to run the following command in the container that runs the python script e.g. the encoder container.

```
apt update
apt-get install -y nftables
nft add table input_table
nft 'add chain input_table input {type filter hook input priority -300;}'
nft 'add rule input_table input ip protocol udp udp checksum set 0'
```

# 3. Testbed Implementation #

After ensuring that Docker images are in their respective hosts we can use `docker-compose` to deploy every OAI 5G node and RLNC node as Docker container.

## 3.1. Deploy OAI 5G CN ##

We first start with deploying and running 5G CN containers. 5G Core has a Control Plane (CP) and User Plane (UP). We deploy the Network Functions (NFs) of 5G Core CP and UP separately on different hosts (`Host-1` and `Host-2` respectively).

### 3.1.1. Deploy OAI 5G Core CP ###

In your `Host-1`, go to the directory containing `docker-compose.yaml` file. Deploy `NRF`, `AMF`, `SMF`, and `MySql` Docker container using the following command

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

In your `Host-2`, go to the directory containing `docker-compose.yaml` file. Deploy `UPF` Docker container using the following command:

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

**CAUTION: To execute this 2nd step, the whole `CN5G` SHALL be in `healthy` state (especially the `mysql` container).**

We deploy a monolithic gNB. In your `Host-4`, go to the directory containing `docker-compose.yaml` file.

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

## 3.2. Deploy OAI UE, ext-DN, and RLNC nodes ##

We run `Decoder` Python program in the `UE` Docker container. In your `Host-4`, go to the directory containing `docker-compose.yaml` file. Then we deploy `ext-DN`, `Encoder`, and `UE` Docker container using: 

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

To run FlexNC algorithm we have to copy the Python files from hosts to the respective Docker container. We use `tcpreplay` to replay pcap files. We have altered `tcpreplay` code to insert timestamps when the packet is sent. This is used for computing One-Way-Delay (OWD). We extract `tcpreplay-4.4.2.zip` in `./files/Host-3`. Then we copy it and other files from `Host-3` to their respective Docker container using the following command in  `Host-3`:

```bash
$ sudo bash ./Host-3/copy_files.sh   
```
























