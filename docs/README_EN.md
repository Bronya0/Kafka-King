<div align=center><img src="assets/icon.ico"></div>
<h1 align="center">Kafka King </h1>


<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King)

<strong>A modern, practical Kafka GUI client built using Python flet.</strong>
</div>

# Feature list
- [x] View cluster node list (completed)
- [x] Create topics (support batches), delete topics, and support statistics of the message backlog of each topic based on consumer groups (completed)
- [x] Support viewing detailed information of topic partitions and adding additional partitions to topics (completed)
- [x] Support viewing the message offset of each partition (completed)
- [x] Support simulated producers, send messages in batches, whether to enable gzip compression, acks, batch_size, liner_ms, you can use it for performance testing (completed)
- [x] Supports simulated consumers, consuming specified sizes according to built-in groups (completed)
- [x] Light and dark theme switching (completed)
- [ ] Parameter description comparison table (under evaluation)
- [ ] Monitoring and alarming (under evaluation)
- [ ] Multi-language support (under development)
- [ ] Configuration (under evaluation)
- ……

# download
[Download address](https://github.com/Bronya0/Kafka-King/releases), click Assets and choose your platform

# Function screenshot

## Manipulate topic
Topic list, supports deleting topics

Supports statistics of the message backlog of each topic based on consumer groups

![](snap/p9.png)

Create a theme (supports batch)

![](snap/p4.png)

## View the detailed configuration of the topic
![](snap/p6.png)

## Automatically obtain the cluster broker list
![](snap/p2.png)

## Get broker detailed configuration
![](snap/p3.png)

## Simulate producer-consumer
- Supports simulating producers, sending messages in batches, and whether to enable gzip compression
- Supports simulated consumers, consuming specified sizes according to built-in groups

![](snap/p8.png)
![](docs/snap/p10.png)


## Partition operations
- Supports viewing detailed information of topic partitions
- Support adding additional partitions to themes
-Supports viewing the message offset of each partition

![](snap/p5.png)


# Quick start dev
Select the corresponding version to download under Assets under release on the right.
Or click https://github.com/Bronya0/Kafka-King/releases


# Construct
pip install -r requirements.txt

flet pack main.py -i assets/icon.ico -n kafka-king --add-data=assets/*:assets

# Star
[![Stargazers over time](https://starchart.cc/Bronya0/Kafka-King.svg)](https://starchart.cc/Bronya0/Kafka-King)

# License
Apache-2.0 license

# grateful
- flet-dev: https://github.com/flet-dev/flet
- kafka-python：https://github.com/dpkp/kafka-python