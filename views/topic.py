#!/usr/bin/env python
# -*-coding:utf-8 -*-
from typing import Optional, Dict

import flet as ft
from flet_core import ControlEvent
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import for_code

from service.common import S_Text, open_snack_bar, S_Button, dd_common_configs, close_dlg, SIMULATE, view_instance_map, \
    Navigation, body, progress_bar, common_page, build_tab_container
from service.kafka_service import kafka_service
from views.simulate import Simulate


class Topic(object):
    """
    topic页的组件
    """

    def __init__(self):
        # _lag_label: when select consumer groups, use it, that is 'loading...'
        self.page = None
        self.pr = progress_bar
        self.table_topics = []
        self._lag_label = None
        self.topic_offset = None
        self.topic_lag = None
        self.topic_op_content = None
        self.describe_topics_map: Optional[Dict] = None
        self.partition_table = None
        self.describe_topics = None
        self.describe_topics_tmp = []
        self.topic_table = None
        self.page_num = 1
        self.page_size = 8

        # 创建topic输入框
        self.create_topics_multi_text_input = ft.TextField(
            hint_text="例如: \ntopic1,1,2\ntopic2,2,2\ntopic3,3,2",
            multiline=True,
            dense=False,
            keyboard_type=ft.KeyboardType.MULTILINE,
            max_length=1000,
            max_lines=10,
            min_lines=2,
            helper_text="分区数后续可以增加但是不能减少; 分布式下副本因子建议至少为2；"
        )
        self.create_topic_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("批量创建主题\n每行填写：主题名称,分区数,副本因子(集群建议为2)（英文逗号隔开）"),
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
            label='额外的分区数量'
        )
        self.create_partition_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("新增额外分区数量"),
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
            label="请选择消费组",
            **dd_common_configs
        )

        # partition tab's topic Dropdown
        self.partition_topic_dd = ft.Dropdown(
            label="当前主题",
            on_change=self.click_partition_topic_dd_onchange,
            **dd_common_configs
        )

        # search datatable
        self.search_text = ft.TextField(label='检索', on_submit=self.search_table, width=200,
                                        height=38, text_size=14, content_padding=5)

        # topic list tap
        self.topic_tab = ft.Tab(
            icon=ft.icons.LIST_ALT_OUTLINED, text="列表", content=ft.Row()
        )

        # partition list tap
        self.partition_tab = ft.Tab(
            icon=ft.icons.WAVES_OUTLINED, text="分区",
            content=ft.Container(content=ft.Text("请从主题列表的分区列点击进入", size=20))
        )

        # config tap
        self.config_tab = ft.Tab(
            text='主题配置', content=ft.Container(content=ft.Text("请从主题的配置按钮进入", size=20)),
            icon=ft.icons.CONSTRUCTION_OUTLINED
        )

        # all in one
        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.topic_tab,
                self.partition_tab,
                self.config_tab,
            ],
            expand=True,
        )

        self.controls = [
            self.tab,
        ]

    def init(self, page=None):
        if not kafka_service.kac:
            return "请先选择一个可用的kafka连接！\nPlease select an available kafka connection first!"
        # 数据初始化
        self.describe_topics = kafka_service.get_topics()
        self.describe_topics_map = {i['topic']: i for i in self.describe_topics}
        self.search_table_handle(self.describe_topics)

        # 消费组初始化
        groups = kafka_service.get_groups()
        if groups:
            self.topic_groups_dd.options = [ft.dropdown.Option(text=i) for i in groups]
        else:
            self.topic_groups_dd.label = "无消费组"

        self.init_table()

    def init_table(self):

        # init topic table data
        rows = []
        self.topic_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("编号")),
                ft.DataColumn(S_Text("健康")),
                ft.DataColumn(S_Text("主题")),
                ft.DataColumn(S_Text("副本数")),
                ft.DataColumn(S_Text("分区")),
                ft.DataColumn(S_Text("消息总量(组)")),
                ft.DataColumn(S_Text("提交总量(组)")),
                ft.DataColumn(S_Text("积压量(组)")),
                ft.DataColumn(S_Text("操作"))
            ],
            rows=rows,
            column_spacing=20,
            expand=True
        )
        _topics = []
        # 根据self.describe_topics、self.page_num、self.page_size实现分页
        offset = (self.page_num - 1) * self.page_size
        for i, topic in enumerate(self.describe_topics_tmp):
            topic_name_ = topic.get('topic')

            lag = self.topic_lag.get(topic_name_) if self.topic_lag else self._lag_label
            end_offset = lag[0] if isinstance(lag, list) and lag else self._lag_label
            commit_offset = lag[1] if isinstance(lag, list) and lag else self._lag_label
            _lag = self._lag_label
            if isinstance(lag, list) and end_offset is not None and commit_offset is not None:
                _lag = end_offset - commit_offset
            refactor = len(topic['partitions'][0]['replicas']) if topic['partitions'] else "无分区"
            disabled = False if not topic.get('is_internal') else True

            err_color = 'green'
            err_desc = None
            for _p in topic['partitions']:
                if _p['error_code'] != 0:
                    err_color = 'red'
                    err_desc = for_code(_p['error_code']).description
                    break

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(offset + i + 1)),
                        ft.DataCell(ft.Icon(ft.icons.CIRCLE, color=err_color, size=16, tooltip=err_desc)),
                        ft.DataCell(S_Text(topic_name_, size=13)),
                        ft.DataCell(S_Text(refactor)),
                        ft.DataCell(ft.TextButton(
                            text=str(len(topic.get('partitions'))),
                            style=ft.ButtonStyle(color=err_color),
                            on_click=self.click_topic_button,
                            data=topic_name_,
                        )),
                        ft.DataCell(S_Text(end_offset, size=13)),
                        ft.DataCell(S_Text(commit_offset, size=13)),
                        ft.DataCell(S_Text(_lag, color='red' if isinstance(lag, list) and int(_lag) > 10000 else None,
                                           size=13)),
                        ft.DataCell(
                            ft.MenuBar(
                                style=ft.MenuStyle(
                                    alignment=ft.alignment.top_left,
                                ),
                                controls=[
                                    ft.SubmenuButton(
                                        content=ft.Text("操作"),
                                        height=40,
                                        leading=ft.Icon(ft.icons.MORE_VERT),
                                        controls=[
                                            ft.MenuItemButton(
                                                data=topic_name_,
                                                content=ft.Text("生产"),
                                                on_click=self.show_produce_page,
                                                disabled=disabled,
                                            ),
                                            ft.MenuItemButton(
                                                data=topic_name_,
                                                content=ft.Text("消费"),
                                                on_click=self.show_consumer_page,
                                                disabled=disabled,

                                            ),
                                            ft.MenuItemButton(
                                                data=topic_name_,
                                                content=ft.Text("配置", color="brown"),
                                                on_click=self.show_config_tab,
                                                disabled=disabled,

                                            ),
                                            ft.MenuItemButton(
                                                data=topic_name_,
                                                content=ft.Text("删除", color="red"),
                                                on_click=self.open_delete_dialog,
                                                disabled=disabled,

                                            ),

                                        ]
                                    ),
                                ]
                            )

                        ),

                    ],
                )
            )
            _topics.append(topic_name_)
        self.table_topics = _topics

        # init topic tab
        self.topic_tab.content = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    self.topic_groups_dd,
                                    self.search_text,
                                    S_Button(text="创建主题", on_click=self.open_create_topic_dlg_modal,
                                             tooltip="批量输入要创建的主题及参数，一行一个", ),
                                    S_Button(text="刷新offset", on_click=self.groups_dd_onchange),
                                    self.refresh_button
                                ]),

                            ft.Row([self.topic_table]),
                            ft.Row(
                                [
                                    # 翻页图标和当前页显示
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK,
                                        icon_size=20,
                                        on_click=self.page_prev,
                                        tooltip="上一页",
                                    ),
                                    ft.Text(f"{self.page_num}/{int(len(self.describe_topics) / self.page_size) + 1}"),
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_FORWARD,
                                        icon_size=20,
                                        on_click=self.page_next,
                                        tooltip="下一页",
                                    ),
                                    ft.Text(f"每页{self.page_size}条"),
                                    ft.Slider(min=5, max=55, divisions=10, round=1, value=self.page_size,
                                              label="{value}", on_change_end=self.page_size_change),
                                ]
                            )
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ), alignment=ft.alignment.top_left, padding=10)
            ],
        )

        # init partition tab
        self.partition_topic_dd.options = [ft.dropdown.Option(text=i) for i in self.describe_topics_map.keys()]

    def page_prev(self, e):
        if self.page_num == 1:
            return
        self.page_num -= 1

        offset = (self.page_num - 1) * self.page_size
        self.describe_topics_tmp = self.describe_topics[offset:offset + self.page_size]

        self.init_table()
        e.page.update()

    def page_next(self, e):
        # 最后一页则return
        if self.page_num * self.page_size >= len(self.describe_topics):
            return
        self.page_num += 1
        offset = (self.page_num - 1) * self.page_size
        self.describe_topics_tmp = self.describe_topics[offset:offset + self.page_size]

        self.init_table()
        e.page.update()

    def page_size_change(self, e):
        # page
        self.page_size = int(e.control.value)
        self.describe_topics_tmp = self.describe_topics[:self.page_size]

        self.init_table()
        e.page.update()

    def _create_partition_table(self, topic_name_):
        rows = []
        self.partition_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("编号")),
                ft.DataColumn(S_Text("健康")),
                ft.DataColumn(S_Text("Leader分布")),
                ft.DataColumn(S_Text("Replicas分布")),
                ft.DataColumn(S_Text("ISR分布")),
                ft.DataColumn(S_Text("失联副本分布")),
                ft.DataColumn(S_Text("上次提交")),
                ft.DataColumn(S_Text("最末偏移量")),
                ft.DataColumn(S_Text("积压量")),
            ],
            rows=rows,
            expand=True

        )
        partitions = self.describe_topics_map[topic_name_]['partitions']
        partitions = sorted(partitions, key=lambda d: d['partition'])
        for i, partition in enumerate(partitions):
            p_id = partition.get('partition')

            # topic_offset[topic][partition] = [last_committed, end_offsets, _lag]
            last_committed, end_offsets, _lag = None, None, None
            if self.topic_offset:
                last_committed, end_offsets, _lag = self.topic_offset.get(topic_name_, {}).get(p_id, (None, None, None))

            err_desc = for_code(partition.get('error_code')).description
            err_color = 'green' if partition.get('error_code') == 0 else 'red'

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(p_id)),
                        ft.DataCell(ft.Icon(ft.icons.CIRCLE, color=err_color, size=16, tooltip=err_desc)),
                        ft.DataCell(S_Text(partition.get('leader'))),
                        ft.DataCell(S_Text(partition.get('replicas'))),
                        ft.DataCell(S_Text(partition.get('isr'))),
                        ft.DataCell(S_Text(partition.get('offline_replicas'))),
                        ft.DataCell(S_Text(last_committed)),
                        ft.DataCell(S_Text(end_offsets)),
                        ft.DataCell(S_Text(_lag)),

                    ],
                )
            )

        # 初始化 partition_tab 页面
        self.partition_tab.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.partition_topic_dd,
                    S_Button(text="为主题添加额外的分区", on_click=self.open_create_partition_dlg_modal,
                             # Create Partitions
                             tooltip="为当前topic增加额外的分区数", ),
                ]),
                ft.Row([
                    self.partition_table
                ]),

            ]
        )

    def click_topic_button(self, e: ControlEvent):
        """
        点击topic，跳转到分区tab
        :return:
        """
        topic_name_ = e.control.data
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
        success = False
        ori = e.control.text
        e.control.text = "创建中……"
        e.control.update()

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
                msg = "{}个主题创建成功".format(len(lines))
                self.create_topics_multi_text_input.value = None
                success = True
            except Exception as _e:
                msg = f"创建失败： {str(_e)}"
        self.create_topic_modal.open = False
        self.init()
        open_snack_bar(e.page, msg, success)
        e.control.text = ori
        e.control.update()

    def create_partitions(self, e: ControlEvent):
        """
        为topic创建额外分区
        """
        ori = e.control.text
        e.control.text = "创建中……"
        e.control.update()

        extra_num = self.create_partition_text_input.value
        extra_num = int(extra_num)
        if extra_num < 1:
            e.control.text = ori
            open_snack_bar(e.page, "额外分区数必须大于1", success=False)
            return

        topic = self.partition_topic_dd.value
        old_partition_num = len(self.describe_topics_map[topic]['partitions'])
        print("为topic创建额外分区", topic, old_partition_num, extra_num)

        res, err = kafka_service.create_partitions(topic, old_partition_num, extra_num)
        if not res:
            msg = f"分区创建失败: {err}"
        else:
            msg = "Topic：{} 成功创建 {} 个分区，当前总共 {} 个".format(topic, extra_num, old_partition_num + extra_num)
        self.create_partition_modal.open = False
        self.init()
        self._create_partition_table(topic_name_=topic)
        open_snack_bar(e.page, msg, success=True)
        e.control.text = ori
        e.control.update()

    def open_delete_dialog(self, e):
        topic_name = e.control.data
        page = e.page

        def ensure(e_):
            dlg_modal.open = False
            page.update()
            msg, success = self.delete_topic(topic_name)
            open_snack_bar(page, msg, success)
            self.init()
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("请确认"),
            content=ft.Text("您真的要删除topic: {}吗？".format(topic_name)),
            actions=[
                ft.TextButton("删除", on_click=ensure),
                ft.TextButton("取消", on_click=close_dlg),
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
            msg = "topic：{}删除成功".format(topic_name)
            return msg, True
        except Exception as e_:
            msg = "{}删除失败： {}".format(topic_name, str(e_))
            return msg, False

    def groups_dd_onchange(self, e: ControlEvent):
        """
        给topic表格添加
        :param e:
        :return:
        """
        group_id = self.topic_groups_dd.value
        topics = self.table_topics
        if group_id is None:
            open_snack_bar(e.page, "请先选择消费组", success=False)
            return

        self.pr.visible = True
        self.pr.update()

        open_snack_bar(e.page, "正在获取消费组offset信息，请稍后……", success=True)

        self.topic_offset, self.topic_lag = None, None
        self.get_offset_handle(topics, group_id)
        self.init_table()
        self.pr.visible = False
        e.page.update()

    def get_offset_handle(self, topics, group_id):
        self.topic_offset, self.topic_lag, = kafka_service.get_topic_offsets(topics, group_id)

    def search_table(self, e: ControlEvent):
        """
        搜索，配合分页
        :param e:
        :return:
        """
        all_topics = kafka_service.get_topics()
        self.search_table_handle(all_topics)
        e.page.update()

    def search_table_handle(self, all_topics):
        search_text_value = self.search_text.value
        _lst = []
        if search_text_value is not None:
            for i in all_topics:
                topic_name_ = i.get('topic')
                if str(search_text_value) in topic_name_:
                    _lst.append(i)
        else:
            _lst = all_topics
        self.page_num = 1
        self.describe_topics = _lst
        self.describe_topics_tmp = _lst[:self.page_size]
        self.init_table()

    def topic_page_refresh(self, e):
        self.init()
        self.groups_dd_onchange(e)
        e.page.update()

    def show_produce_page(self, e: ControlEvent):
        """
        打开模拟生产者页面
        """
        Navigation.selected_index = SIMULATE
        view: Simulate = view_instance_map.get(SIMULATE)
        if not view:
            view = Simulate()
            view_instance_map[SIMULATE] = view
        view.tab.selected_index = 0
        view.producer_topic_dd.value = e.control.data
        body.controls = view.controls
        err = view.init()
        if err:
            body.controls = [S_Text(value=str(err), size=24)]
        e.page.update()

    def show_consumer_page(self, e: ControlEvent):
        """
        打开模拟消费者页面
        """
        Navigation.selected_index = SIMULATE
        view: Simulate = view_instance_map.get(SIMULATE)
        if not view:
            view = Simulate()
            view_instance_map[SIMULATE] = view
        view.consumer_topic_dd.value = e.control.data
        view.tab.selected_index = 1
        body.controls = view.controls
        err = view.init()
        if err:
            body.controls = [S_Text(value=str(err), size=24)]
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
