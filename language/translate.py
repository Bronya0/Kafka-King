#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json


class Lang(object):
    def __init__(self, language):
        self.language = language

    def i18n(self, default_str: str):
        if self.language is None:
            return default_str
        res = lang_dict.get(default_str, {}).get(self.language, default_str)
        return res


lang = Lang(language=None)
i18n = lang.i18n


lang_dict = {
    "请先选择一个可用的kafka连接！": {
        "en": ""
    },
    "请在右侧添加kafka连接": {
        "en": "Please add kafka connection"
    },
    "请选择kafka连接": {
        "en": "Please select kafka connection"
    },
    "基础信息": {
        "en": ""
    },
    "集群": {
        "en": "Broker"
    },
    "主题": {
        "en": "Topic"
    },
    "监控": {
        "en": "Simulate"
    },
    "设置": {
        "en": "Settings"
    },
    "建议": {
        "en": "Suggest"
    },
    "模拟": {
        "en": "Simulate"
    },
    "集群节点列表": {
        "en": ""
    },
    "机架感知": {
        "en": ""
    },
    "查看配置": {
        "en": ""
    },
    "分区数后续可以增加但是不能减少; 0 < 副本因子 <= broker数（必须）；": {
        "en": ""
    },
    "批量创建topic\\n每行填写：topic名称,分区数,副本因子，用英文逗号隔开": {
        "en": ""
    },
    "确认": {
        "en": ""
    },
    "取消": {
        "en": ""
    },
    "额外的分区数量": {
        "en": ""
    },
    "新增分区": {
        "en": ""
    },
    "请选择消费组": {
        "en": ""
    },
    "Topic配置": {
        "en": ""
    },
    "分区数": {
        "en": ""
    },
    "积压量(先选择组)": {
        "en": ""
    },
    "删除": {
        "en": ""
    },
    "禁止": {
        "en": ""
    },
    "批量输入要创建的topic及参数，一行一个": {
        "en": ""
    },
    "分区编号": {
        "en": ""
    },
    "Leader分布": {
        "en": ""
    },
    "Replicas分布": {
        "en": ""
    },
    "ISR分布": {
        "en": ""
    },
    "失联副本": {
        "en": ""
    },
    "为当前topic增加额外的分区数": {
        "en": ""
    },
    "不能一次创建的数目超过100个": {
        "en": ""
    },
    "格式验证不正确，请确保分区和副本因子大于0，主题名不可过长。一次最多输入100个topic": {
        "en": ""
    },
    "不可创填写重复的topic": {
        "en": ""
    },
    "{}个主题创建成功": {
        "en": ""
    },
    "创建失败": {
        "en": ""
    },
    "Topic：{} 成功创建 {} 个分区，当前总共 {} 个": {
        "en": ""
    },
    "分区创建失败，请尝试减小分区数量": {
        "en": ""
    },
    "请确认": {
        "en": ""
    },
    "您真的要删除topic: {}吗？": {
        "en": ""
    },
    "{}删除失败： {}": {
        "en": ""
    },
    "配置名": {
        "en": ""
    },
    "配置值": {
        "en": ""
    },
    "敬请期待": {
        "en": ""
    },
    "支持字符串，可以输入String、Json等消息。": {
        "en": ""
    },
    "开启gzip压缩：": {
        "en": ""
    },
    "输入单条消息内容": {
        "en": ""
    },
    "消息发送倍数：默认*1": {
        "en": ""
    },
    "参数填写不正确": {
        "en": ""
    },
    "发送成功": {
        "en": ""
    },
    "发送失败：": {
        "en": ""
    },
    "发送耗时": {
        "en": ""
    },
    "请选择topic": {
        "en": ""
    },
    "size需要大于0": {
        "en": ""
    },
    "size不能大于10000": {
        "en": ""
    },
    "请输入正确的size，整数类型": {
        "en": ""
    },
    "拉取成功": {
        "en": ""
    },
    "拉取失败": {
        "en": ""
    },
    "语言：": {
        "en": ""
    }
}