#!/usr/bin/env python
# -*-coding:utf-8 -*-
from typing import Optional, Dict

import flet as ft
from flet_core import ControlEvent
from kafka import KafkaAdminClient
from kafka.admin import NewTopic

from common import S_Text, open_snack_bar, S_Button, dd_common_configs
from service.kafka_service import kafka_service


class Topic(object):
    """
    topic页的组件
    """

    def __init__(self):
        # _lag_label: when select consumer groups, use it, that is 'loading...'
        self.table_topics = []
        self._lag_label = None
        self.topic_offset = None
        self.topic_lag = None
        self.topic_op_content = None
        self.describe_topics_map: Optional[Dict] = None
        self.partition_table = None
        self.describe_topics = None
        self.topic_table = None

        if not kafka_service.kac:
            raise Exception("请先选择一个可用的kafka连接！")

        # 创建topic输入框
        self.create_topics_multi_text_input = ft.TextField(
            hint_text="such as: \ntopic1,1,1\ntopic2,1,1\ntopic3,1,1",
            multiline=True,
            dense=False,
            keyboard_type=ft.KeyboardType.MULTILINE,
            max_length=1000,
            max_lines=10,
            min_lines=2,
            helper_text="分区数后续可以增加但是不能减少; 0 < 副本因子 <= broker数（必须）；"
        )
        self.create_topic_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("批量创建topic\n每行填写：topic名称,分区数,副本因子，用英文逗号隔开"),
            actions=[
                ft.Column([
                    self.create_topics_multi_text_input,
                    ft.Row([
                        ft.TextButton("确认", on_click=self.create_topic),
                        ft.TextButton("取消", on_click=self.close_create_topic_dlg),
                    ])
                ]),
            ],
            adaptive=True,
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # 创建分区
        self.create_partition_text_input = ft.TextField(
            label='extra partition nums'
        )
        self.create_partition_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("新增分区"),
            actions=[
                ft.Column([
                    self.create_partition_text_input,
                    ft.Row([
                        ft.TextButton("确认", on_click=self.create_partitions),
                        ft.TextButton("取消", on_click=self.close_create_partition_dlg),
                    ])
                ]),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # refresh button
        self.refresh_button = ft.IconButton(icon=ft.icons.REFRESH_OUTLINED, on_click=self.topic_page_refresh)

        # consumer groups Dropdown
        self.topic_groups_dd = ft.Dropdown(
            label="consumer groups",
            on_change=self.groups_dd_onchange,
            **dd_common_configs
        )

        # partition tab's topic Dropdown
        self.partition_topic_dd = ft.Dropdown(
            label="topic",
            on_change=self.click_partition_topic_dd_onchange,
            **dd_common_configs
        )

        # search datatable
        self.search_text = ft.TextField(label='search', on_submit=self.search_table, width=200,
                                        height=30, text_size=14, content_padding=10)

        # topic list tap
        self.topic_tab = ft.Tab(
            icon=ft.icons.LIST_ALT_OUTLINED, text="List", content=ft.Container()
        )

        # partition list tap
        self.partition_tab = ft.Tab(
            icon=ft.icons.WAVES_OUTLINED, text="Partition", content=ft.Container()
        )

        # config tap
        self.config_tab = ft.Tab(
            text='Topic配置', content=ft.Container()
        )

        # all in one
        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.topic_tab,
                self.partition_tab,
                self.config_tab,
            ],
            expand=1,
        )

        self.controls = [
            self.tab,
        ]

    def init(self):
        if not kafka_service.kac:
            return "请先选择一个可用的kafka连接！"
        self.describe_topics = kafka_service.get_topics()
        self.describe_topics_map = {i['topic']: i for i in self.describe_topics}

        # init topic table data
        rows = []
        self.topic_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("ID")),
                ft.DataColumn(S_Text("Topic")),
                ft.DataColumn(S_Text("分区数")),
                ft.DataColumn(S_Text("积压量(先选择组)")),
                ft.DataColumn(S_Text("查看配置")),
                ft.DataColumn(S_Text("删除")),
            ],
            rows=rows,
        )
        _topics = []
        for i, topic in enumerate(self.describe_topics):
            topic_name_ = topic.get('topic')

            # search filter
            search_text_value = self.search_text.value
            if search_text_value is not None and search_text_value not in topic_name_:
                continue

            lag = self.topic_lag.get(topic_name_) if self.topic_lag else self._lag_label
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(i)),
                        ft.DataCell(S_Button(
                            text=topic_name_,
                            bgcolor="#F7E7E6",
                            color="#DA3A66",
                            on_click=self.click_topic_button,
                        )),
                        ft.DataCell(S_Text(len(topic.get('partitions')))),
                        ft.DataCell(S_Text(lag, color='#315EFB')),
                        ft.DataCell(
                            ft.IconButton(icon=ft.icons.CONSTRUCTION, data=topic_name_, on_click=self.show_config_tab)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.icons.DELETE_FOREVER_OUTLINED,
                                on_click=self.open_delete_dialog,
                                data=topic_name_,
                                icon_color="#DA3A66",
                                tooltip=f"删除{topic_name_}",
                            )
                        ) if not topic.get('is_internal') else ft.DataCell(ft.Text("禁止"))  # not allowed
                    ],
                )
            )
            _topics.append(topic_name_)
        self.table_topics = _topics

        # 消费组初始化
        self.topic_groups_dd.options = [ft.dropdown.Option(text=i) for i in kafka_service.get_groups()]

        # init topic tab
        self.topic_tab.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.topic_groups_dd,
                    self.search_text,
                    S_Button(text="Create Topic", on_click=self.open_create_topic_dlg_modal,
                             tooltip="批量输入要创建的topic及参数，一行一个", ),
                    self.refresh_button
                ]),
                self.topic_table,
            ],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            alignment=ft.alignment.top_left,
            padding=10,

        )

        # init partition tab
        self.partition_topic_dd.options = [ft.dropdown.Option(text=i) for i in self.describe_topics_map.keys()]

    def _create_partition_table(self, topic_name_):
        rows = []
        self.partition_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("分区编号")),
                ft.DataColumn(S_Text("Leader分布")),
                ft.DataColumn(S_Text("Replicas分布")),
                ft.DataColumn(S_Text("ISR分布")),
                ft.DataColumn(S_Text("失联副本")),
                ft.DataColumn(S_Text("last_committed")),
                ft.DataColumn(S_Text("end_offset")),
                ft.DataColumn(S_Text("lag")),
            ],
            rows=rows,
        )
        partitions = self.describe_topics_map[topic_name_]['partitions']
        partitions = sorted(partitions, key=lambda d: d['partition'])
        for i, partitions in enumerate(partitions):
            p_id = partitions.get('partition')

            # topic_offset[topic][partition] = [last_committed, end_offsets, _lag]
            last_committed, end_offsets, _lag = None, None, None
            if self.topic_offset:
                last_committed, end_offsets, _lag = self.topic_offset[topic_name_][p_id]

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(p_id)),
                        ft.DataCell(S_Text(partitions.get('leader'))),
                        ft.DataCell(S_Text(partitions.get('replicas'))),
                        ft.DataCell(S_Text(partitions.get('isr'))),
                        ft.DataCell(S_Text(partitions.get('offline_replicas'))),
                        ft.DataCell(S_Text(last_committed)),
                        ft.DataCell(S_Text(end_offsets)),
                        ft.DataCell(S_Text(_lag)),
                    ],
                )
            )

        # 初始化 partition_tab 页面
        self.partition_tab.content = ft.Container(
            ft.Column(
                [
                    ft.Row([
                        self.partition_topic_dd,
                        S_Button(text="Create Partitions", on_click=self.open_create_partition_dlg_modal,
                                 tooltip="为当前topic增加额外的分区数", ),
                    ]),
                    self.partition_table
                ], scroll=ft.ScrollMode.ALWAYS
            ),
            padding=10,
        )

    def click_topic_button(self, e: ControlEvent):
        """
        点击topic，跳转到分区tab
        :return:
        """
        topic_name_ = e.control.text
        self.tab.selected_index = 1
        # 切换的时候，把topic带过来，赋给分区页的下拉
        self.partition_topic_dd.value = topic_name_
        self._create_partition_table(topic_name_=topic_name_)
        e.page.update()

    def click_partition_topic_dd_onchange(self, e: ControlEvent):
        """
        点击topic，则刷新分区tab数据
        :param e:
        :return:
        """
        topic_name_ = e.control.value
        self._create_partition_table(topic_name_=topic_name_)
        e.page.update()

    def open_create_topic_dlg_modal(self, e):
        e.page.dialog = self.create_topic_modal
        self.create_topic_modal.open = True
        e.page.update()

    def close_create_topic_dlg(self, e):
        self.create_topic_modal.open = False
        self.create_topics_multi_text_input.value = None
        e.page.update()

    def open_create_partition_dlg_modal(self, e):
        e.page.dialog = self.create_partition_modal
        self.create_partition_modal.open = True
        e.page.update()

    def close_create_partition_dlg(self, e):
        self.create_partition_modal.open = False
        self.create_partition_text_input.value = None
        e.page.update()

    def create_topic(self, e: ControlEvent):
        """
        创建多个topic
        name、副本因子、分区数
        在集群中创建新主题。

         参数：
        topics_configs：
        [
            {
                "name":,
                "num_partitions":,
                "replication_factor":,
            }
        ...
        ]

        api参数
        new_topics – NewTopic 对象的列表。
        timeout_ms – 代理返回之前等待创建新主题的毫秒数。
        validate_only – 如果为 True，则实际上不创建新主题。并非所有版本都支持。默认值：假
         返回：
        CreateTopicResponse 类的适当版本。
        """
        # check
        list_ = []
        names = []
        try:
            _topics_configs = self.create_topics_multi_text_input.value
            lines = _topics_configs.split('\n')
            if len(lines) > 100:
                raise Exception("不能一次创建的数目超过100个")
            for _config in lines:
                config = _config.split(',')
                name, num_partitions, replication_factor = str(config[0]), int(config[1]), int(config[2])
                if not (len(name) < 100 and num_partitions > 0 and replication_factor > 0):
                    raise Exception("格式验证不正确，请确保分区和副本因子大于0，主题名不可过长。一次最多输入100个topic")
                if name not in names:
                    names.append(name)
                else:
                    raise Exception(f"不可创填写重复的topic: {name}")

                new_topic = NewTopic(name=name, num_partitions=num_partitions, replication_factor=replication_factor)
                list_.append(new_topic)
        except Exception as e_:
            msg = str(e_)
        else:
            try:
                res = kafka_service.kac.create_topics(new_topics=list_, validate_only=False, timeout_ms=60 * 1000)
                msg = f"{len(lines)}个主题创建成功"
                self.create_topics_multi_text_input.value = None
            except Exception as _e:
                msg = f"创建失败： {str(_e)}"
        self.create_topic_modal.open = False
        self.init()
        open_snack_bar(e.page, e.page.snack_bar, msg)

    def create_partitions(self, e: ControlEvent):
        """
        为topic创建额外分区
        """
        extra_num = self.create_partition_text_input.value
        extra_num = int(extra_num)
        topic = self.partition_topic_dd.value
        old_partition_num = len(self.describe_topics_map[topic]['partitions'])
        res = kafka_service.create_partitions(topic, old_partition_num, extra_num)
        msg = f"Topic：{topic} 成功创建 {extra_num} 个分区，当前总共 {old_partition_num + extra_num} 个"
        if not res:
            msg = "分区创建失败，请尝试减小分区数量"
        self.create_partition_modal.open = False
        self.init()
        self._create_partition_table(topic_name_=topic)
        open_snack_bar(e.page, e.page.snack_bar, msg)

    def open_delete_dialog(self, e):
        topic_name = e.control.data
        print(topic_name)
        page = e.page

        def cancel(e_):
            dlg_modal.open = False
            page.update()

        def ensure(e_):
            dlg_modal.open = False
            page.update()
            msg = self.delete_topic(topic_name)
            open_snack_bar(page, page.snack_bar, msg)
            self.init()
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("请确认"),
            content=ft.Text(f"您真的要删除topic: {topic_name}吗？"),
            actions=[
                ft.TextButton("删除", on_click=ensure),
                ft.TextButton("取消", on_click=cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def delete_topic(self, topic_name):

        try:
            kac: KafkaAdminClient = kafka_service.kac
            res = kac.delete_topics([topic_name])
            print(res)
            msg = f"topic：{topic_name}删除成功"
        except Exception as e_:
            msg = f"{topic_name}删除失败： {str(e_)}"
        return msg

    def groups_dd_onchange(self, e: ControlEvent):
        """
        给topic表格添加
        :param e:
        :return:
        """
        group_id = self.topic_groups_dd.value

        self._lag_label = 'reading...'
        self.topic_offset, self.topic_lag = None, None
        self.init()
        e.page.update()

        topics = self.table_topics
        print(topics)
        # topic_offset[topic][partition] = [last_committed, end_offsets, _lag]
        # topic_lag[topic] = _lag
        self.topic_offset, self.topic_lag, = kafka_service.get_topic_offsets(topics, group_id)
        self.init()
        e.page.update()

    def search_table(self, e: ControlEvent):
        """
        search table
        :param e:
        :return:
        """
        self.init()
        e.page.update()

    def topic_page_refresh(self, e):
        self.init()
        self.groups_dd_onchange(e)
        e.page.update()

    def show_config_tab(self, e: ControlEvent):
        """
        打开侧边栏
        """
        e.control.disabled = True
        topic = e.control.data
        configs = kafka_service.get_configs(res_type='topic', name=topic)

        md_text = """
        | 配置名 | 配置值 |\n|-|-|\n"""
        for config in configs:
            config_names = f"**{config['config_names']}**"
            config_value = f"{config['config_value']}" if config['config_value'] is not None else ""
            md_text += f"| {config_names} | {config_value} |\n"
        self.config_tab.content = ft.Container(
            ft.Column(
                [
                    ft.Markdown(
                        value=f"""{md_text}""",
                        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
                        selectable=True
                    ),
                ],
                scroll=ft.ScrollMode.ALWAYS
            ),
            padding=10
        )

        self.tab.selected_index = 2
        e.control.disabled = False
        e.page.update()
