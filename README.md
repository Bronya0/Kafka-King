<div align=center><img src="assets/icon.ico"></div>
<h1 align="center">Kafka King </h1>
<h4 align="center"><strong>简体中文</strong> | <a href="https://github.com/Bronya0/Kafka-King/blob/main/docs/README_EN.md">English</a></h4>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King)

<strong>一个现代、实用的kafka GUI客户端，使用python flet构建。</strong>
</div>

> 项目完全由python开发，开源免费、简单易懂，右上角点个 **star**，和作者一起学习 python gui开发🥰

# 功能清单
- [x] 查看集群节点列表（完成）
- [x] 创建主题（支持批量）、删除主题、支持根据消费者组统计每个topic的消息积压量（完成）
- [x] 支持查看topic的分区的详细信息，并为主题添加额外的分区（完成）
- [x] 支持查看每个分区的消息offset（完成）
- [x] 支持模拟生产者，批量发送消息，是否开启gzip压缩、acks、batch_size、liner_ms，你可以用来做性能测试（完成）
- [x] 支持模拟消费者，按照内置的组进行指定size的消费（完成）
- [x] 光暗主题切换（完成）
- [ ] 参数说明对照表（评估中）
- [ ] 监控、告警（评估中）
- [ ] 多语言支持（开发中）
- [ ] 配置化（评估中）
- ……

# 下载
[下载地址](https://github.com/Bronya0/Kafka-King/releases)，点击Assets，选择自己的平台

# 功能截图

## 操作topic
主题列表，支持删除主题

支持根据消费者组统计每个topic的消息积压量

![](docs/snap/p9.png)

创建主题（支持批量）

![](docs/snap/p4.png)

## 查看topic的详细配置
![](docs/snap/p6.png)

## 自动获取集群broker列表
![](docs/snap/p2.png)

## 获取broker详细配置
![](docs/snap/p3.png)

## 模拟生产者消费者
- 支持模拟生产者，批量发送消息，是否开启gzip压缩
- 支持模拟消费者，按照内置的组进行指定size的消费

![](docs/snap/p8.png)



## 分区操作
- 支持查看topic的分区的详细信息
- 支持为主题添加额外的分区
- 支持查看每个分区的消息offset

![](docs/snap/p5.png)


# 快速开始
在右侧release下的Assets选择对应版本下载即可。
或者点击 https://github.com/Bronya0/Kafka-King/releases

# 构建

pip install -r requirements.txt

flet pack main.py -i assets/icon.ico  -n kafka-king --add-data=assets/*:assets

# Star星星
[![Stargazers over time](https://starchart.cc/Bronya0/Kafka-King.svg)](https://starchart.cc/Bronya0/Kafka-King)


# License
Apache-2.0 license

# 感谢
- flet-dev：https://github.com/flet-dev/flet
- kafka-python：https://github.com/dpkp/kafka-python