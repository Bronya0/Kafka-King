<p align="center">
  <img src="app/build/appicon.png" width="200" alt="图片标题">
</p>
<h1 align="center">Kafka King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/Kafka-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/Kafka-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/Kafka-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/Kafka-King.svg?style=flat-square)

<h3 align="center">一个现代、实用的kafka GUI客户端 </h3>

</div>
<h4 align="center">
<a href="readme.md">English</a> | 简体中文 | <a href="docs/readme/readme-ja.md">日本語</a> | <a href="docs/readme/readme-ru.md">рускі</a> | <a href="docs/readme/readme-ko.md">한국인</a> | <a href="docs/readme/readme-es.md">Español</a> | <a href="docs/readme/readme-fr.md">Français</a> | <a href="docs/readme/readme-de.md">Deutsch</a> | <a href="docs/readme/readme-pt.md">Português</a> | <a href="docs/readme/readme-it.md">Italiano</a> | <a href="docs/readme/readme-vi.md">Tiếng Việt</a> | <a href="docs/readme/readme-id.md">Bahasa Indonesia</a>  
</h4>

让kafka更好用，make kafka great again!

本项目是一个kafka GUI客户端，适配各个桌面系统（除了win7），支持kafka 0.8.0 到 3.8+，基于 [Wails](https://github.com/wailsapp/wails) and [franz-go](https://github.com/twmb/franz-go) 构建。点个star支持作者辛苦开源吧 谢谢❤❤
加群和作者一起交流： <a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz">研发技术交流群：964440643</a>

> - 同款好用elasticsearch客户端 `ES-King`，可以一起收藏下：https://github.com/Bronya0/ES-King
> - **作者另一款开源编码 AI Agent**：[ally-agent](https://github.com/Bronya0/ally-agent)
> - HDFS客户端：https://github.com/Bronya0/HDFS-King

**文档（AI）**：[https://zread.ai/Bronya0/Kafka-King](https://zread.ai/Bronya0/Kafka-King)

# Kafka-King功能清单
- [x] 查看集群节点列表，支持动态配置broker、topic的配置项
- [x] 支持消费者客户端，按照指定的group进行指定topic、size、timeout的消费，以表格的形式展示消息的各个维度信息
- [x] 支持PLAIN、SSL、SASL、kerberos、sasl_plaintext等等
- [x] 支持消息gzip、lz4、snappy、zstd压缩和解压缩
- [x] 创建主题（支持批量）、删除主题，指定副本、分区
- [x] 支持根据消费者组统计每个topic的消息总量、提交总量、积压量
- [x] 支持查看topic的分区的详细信息（offset），并支持添加额外的分区
- [x] 支持模拟生产者，批量发送消息，指定headers、分区
- [x] topic、分区健康检查（完成）
- [x] 支持查看消费者组、消费者
- [x] offset巡检报表

# 下载
- 方法1：右侧下载，或者点[下载地址](https://github.com/Bronya0/Kafka-King/releases)，展开【Assets】，选择自己的平台下载，支持windows、macos、linux（一般用不到）。
- 方法2：【qq群高速下载】：964440643

对于macos，“M1”、“M2”通常是ARM64架构，“Intel”是AMD64架构

**macOS 用户如果遇到“已损坏”无法打开，终端执行 `xattr -dr com.apple.quarantine /Applications/Kafka-King.app` 即可（原因是 app 未签名被 Gatekeeper 拦截）。**

`必看 注意事项：`

> 1、**使用前请检查kafka集群配置的`advertised.listeners`，如果未配置，或配置的是域名，那么在King中填写连接地址时，请提前在本机电脑的hosts文件中添加对应域名解析，否则会因为无法解析域名而无法连接，哪怕你在king输入框里填的是ip也一样**
> 
> 2、**如果你的连接需要SSL，那么勾选TLS并勾选忽略验证（有证书的话就下下来，开启tls验证，填入证书路径）。**
> 
> 3、**对于SASL机制用户需要勾选开启SASL，并选择SASL协议（通常是plain），并填入用户名密码。**
>
> 4、**如果遇到webview2运行时错误，从微软官网下载重装运行时即可：https://developer.microsoft.com/zh-cn/microsoft-edge/webview2**


# 功能截图
offset巡检，v0.33版本上线，最直观的方式查看消息积压情况
![](../snap/img_5.png)
topic列表，各种操作
![](../snap/img.png)
查看消息
![](../snap/img_3.png)


# 捐赠
有条件可以请作者喝杯咖啡，支持项目发展，感谢💕

![image](https://github.com/user-attachments/assets/da6d46da-4e24-41e3-843d-495c6cd32065)

# 参与开发
安装golang、node.js、npm，运行 go install github.com/wailsapp/wails/v2/cmd/wails@latest 安装 Wails CLI。
```
cd app
wails dev
```
## QQ交流群
<a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz">KingTool研发技术交流群：964440643</a>

![](assets/qq.jpg)


# License
Apache-2.0 license

# 感谢
- wails：https://wails.io/docs/gettingstarted/installation
- naive ui：https://www.naiveui.com/
- franz-go：https://github.com/twmb/franz-go/
- xicons：https://xicons.org/#/

# 翻译
支持中文、日语、英语、韩语、俄语等多种语言

修复或添加新语言：https://github.com/Bronya0/Kafka-King/issues/51

# Star

[![Stargazers over time](https://starchart.cc/Bronya0/Kafka-King.svg?variant=adaptive)](https://starchart.cc/Bronya0/Kafka-King)

## MY Project 我的项目 

| 项目名称 | 描述 | Star & Download |
| --- | --- | --- |
| [**Kafka-King**](https://github.com/Bronya0/Kafka-King) | 一个现代且实用的Kafka GUI客户端 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/Kafka-King.svg?style=flat-square)](https://github.com/Bronya0/Kafka-King) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/Kafka-King/total.svg?style=flat-square)](https://github.com/Bronya0/Kafka-King/releases) |
| [**ES-King**](https://github.com/Bronya0/ES-King) | 一个现代、实用的Elasticsearch本地客户端 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/ES-King.svg?style=flat-square)](https://github.com/Bronya0/ES-King) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/ES-King/total.svg?style=flat-square)](https://github.com/Bronya0/ES-King/releases) |
| [**Tab-King**](https://github.com/Bronya0/Tab-King) | 功能强大的浏览器自定义新标签页扩展 | [edge商店](https://microsoftedge.microsoft.com/addons/detail/tab-king/gjfaiiokimilnlmifafjhhcmjeakmmdf) | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/Tab-King.svg?style=flat-square)](https://github.com/Bronya0/Tab-King) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/Tab-King/total.svg?style=flat-square)](https://github.com/Bronya0/Tab-King/releases)
| [**epub-merge**](https://github.com/Bronya0/epub-merge) | epub合并工具 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/epub-merge.svg?style=flat-square)](https://github.com/Bronya0/epub-merge) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/epub-merge/total.svg?style=flat-square)](https://github.com/Bronya0/epub-merge/releases) |
| [**typora-theme-bronya**](https://github.com/Bronya0/typora-theme-bronya) | 一个名为bronya的Typora主题 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/typora-theme-bronya.svg?style=flat-square)](https://github.com/Bronya0/typora-theme-bronya) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/typora-theme-bronya/total.svg?style=flat-square)](https://github.com/Bronya0/typora-theme-bronya/releases) |
| [**webp-to-jpg**](https://github.com/Bronya0/webp-to-jpg) | 将webp图片转换为jpeg格式 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/webp-to-jpg.svg?style=flat-square)](https://github.com/Bronya0/webp-to-jpg) [![GitHub Downloads](https://img.shields.io/github/downloads/Bronya0/webp-to-jpg/total.svg?style=flat-square)](https://github.com/Bronya0/webp-to-jpg/releases) |
| [**web-starter**](https://github.com/Bronya0/web-starter) | Golang Web项目脚手架 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/web-starter.svg?style=flat-square)](https://github.com/Bronya0/web-starter) |
| [**go-utils**](https://github.com/Bronya0/go-utils) | 提供Golang中安全、高效的操作函数 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/go-utils.svg?style=flat-square)](https://github.com/Bronya0/go-utils) |
| [**django-onii**](https://github.com/Bronya0/django-onii) | 基于Python Django+DRF的脚手架 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/django-onii.svg?style=flat-square)](https://github.com/Bronya0/django-onii) |
| [**Jetbrains-Darcula-Zed-Theme**](https://github.com/Bronya0/Jetbrains-Darcula-Zed-Theme) | 仿Jetbrains Zed的Darcula主题 | [![GitHub Stars](https://img.shields.io/github/stars/Bronya0/Jetbrains-Darcula-Zed-Theme.svg?style=flat-square)](https://github.com/Bronya0/Jetbrains-Darcula-Zed-Theme) |
