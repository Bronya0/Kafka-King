import gc
import os
import threading
import time
import traceback

import flet as ft
import requests
from flet_core import TextField

from common import S_Text, prefix, GITHUB_URL, TITLE, UPDATE_URL, open_snack_bar, close_dlg
from language.translate import lang, i18n
from service.kafka_service import kafka_service
from views.init import views_index_map


class Main:

    def __init__(self, page):
        self.page = page

        # 创建输入表单控件
        self.conn_name_input = TextField(label="连接名", hint_text="例如：本地环境", height=48)
        self.kafka_input = TextField(label="Kafka地址", hint_text="例如：127.0.0.1:9092", height=48)
        self.connect_input_column = ft.Column([
            self.conn_name_input,
            self.kafka_input,
            ft.Row([
                ft.TextButton("连接测试", on_click=self.test_connect, on_long_press=True,
                              style=ft.ButtonStyle(color=ft.colors.RED)),
                ft.TextButton("确认", on_click=self.add_connect),
                ft.TextButton("取消", on_click=close_dlg),
            ])
        ],
            width=360
        )

        # 添加kafka link
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("添加kafka连接"),
            actions=[
                self.connect_input_column,
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8)

        )

        self.delete_modal = ft.AlertDialog(
            modal=True,
            title=S_Text("删除kafka连接？"),
            actions=[
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),

        )

        # 链接下拉
        self.connect_dd = ft.Dropdown(
            label="连接",
            options=[],
            height=35,
            text_size=16,
            on_change=self.dropdown_changed,
            alignment=ft.alignment.center_left,
            dense=True,
            content_padding=5,
            focused_bgcolor='#ff0000',
        )

        # 侧边导航栏 NavigationRail
        self.Navigation = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            # 定义在导航栏中排列的按钮项的外观，该值必须是两个或更多NavigationRailDestination实例的列表。
            destinations=[
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.HIVE_OUTLINED, tooltip="查看集群broker节点和配置"),
                    selected_icon_content=ft.Icon(ft.icons.HIVE),
                    label=i18n("集群"),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.LIBRARY_BOOKS_OUTLINED, tooltip="增删改topic及partition"),
                    selected_icon_content=ft.Icon(ft.icons.LIBRARY_BOOKS),
                    label=i18n("主题"),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.SWITCH_ACCESS_SHORTCUT_ADD_OUTLINED,
                                         tooltip="模拟producer及consumer"),
                    selected_icon_content=ft.Icon(ft.icons.SWITCH_ACCESS_SHORTCUT_ADD),
                    label=i18n("模拟"),
                ),

                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.STACKED_BAR_CHART_ROUNDED, tooltip="监控（开发中）"),
                    selected_icon_content=ft.Icon(ft.icons.STACKED_BAR_CHART),
                    label=i18n("监控"),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.SETTINGS_OUTLINED, tooltip="配置（开发中）"),
                    selected_icon_content=ft.Icon(ft.icons.SETTINGS_SUGGEST_OUTLINED),
                    label_content=S_Text(i18n("设置")),
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.AUTO_GRAPH_OUTLINED, tooltip="建议我们"),
                    selected_icon_content=ft.Icon(ft.icons.AUTO_GRAPH),
                    label_content=S_Text(i18n("建议")),
                ),
            ],
            on_change=self.refresh_body,
        )

        # 每个页面的主体
        self.body = ft.Column(
            controls=[],
            expand=True
        )

        # 底部提示
        self.page.snack_bar = ft.SnackBar(content=ft.Text(""))

        # 顶部导航
        self.page.appbar = ft.AppBar(
            leading=ft.Image(src="icon.png"),
            leading_width=40,
            title=S_Text(TITLE),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                self.connect_dd,
                ft.IconButton(ft.icons.ADD_BOX_OUTLINED, on_click=self.open_dlg_modal, tooltip="添加kafka地址"),  # add link
                ft.IconButton(ft.icons.DELETE_OUTLINE, on_click=self.open_delete_link_modal, tooltip="删除kafka地址"),
                # add link
                ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, on_click=self.change_theme, tooltip="切换明暗"),  # theme
                ft.IconButton(ft.icons.TIPS_AND_UPDATES_OUTLINED, tooltip="去github更新或者提出想法",
                              url=GITHUB_URL),
            ],
        )

        self.pr = ft.ProgressBar(visible=False)

        # 初始化加载全部连接
        self.refresh_dd_links()

        self.page.add(
            ft.Row(
                [
                    self.Navigation,  # 侧边
                    ft.VerticalDivider(width=1),  # 竖线
                    self.body,  # 内容
                ],
                expand=True,
            ),

            self.pr
        )

    def test_connect(self, e):
        if self.kafka_input.value == "":
            msg = "请先填写kafka连接"
            color = "#000000"
        else:
            res = kafka_service.new_client(bootstrap_servers=self.kafka_input.value.split(','))
            if res:
                msg = f"连接成功"
                color = "#00a0b0"
            else:
                msg = f"连接失败"
                color = "#000000"

        self.page.snack_bar.content = ft.Text(msg)
        self.page.snack_bar.bgcolor = color
        self.page.snack_bar.open = True
        self.page.update()

    def add_connect(self, e):
        # 存储连接：{prefix}{连接名} <-> 链接地址
        self.page.client_storage.set(f"{prefix}{self.conn_name_input.value}", self.kafka_input.value)
        self.refresh_dd_links()
        self.dlg_modal.open = False
        self.kafka_input.value = None
        self.conn_name_input.value = None
        self.page.update()

    def open_dlg_modal(self, e):
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()

    def delete_connect(self, e):
        self.page.client_storage.remove(self.connect_dd.value)
        self.page.dialog.open = False
        self.refresh_dd_links()
        self.page.update()

    def open_delete_link_modal(self, e):
        key = self.connect_dd.value
        if key is None:
            open_snack_bar(self.page, "请先选择一个链接")
            return

        self.delete_modal.actions = [
            ft.Column(
                controls=[
                    ft.Row([S_Text(f"连接名：{key[len(prefix):]}")]),
                    ft.Row([S_Text(f"地址：{self.page.client_storage.get(key)}")]),
                    ft.Row([
                        ft.TextButton(text="删除", on_click=self.delete_connect,
                                      style=ft.ButtonStyle(color=ft.colors.RED)),
                        ft.TextButton(text="取消", on_click=close_dlg),
                    ])
                ]
            )
        ]
        self.page.dialog = self.delete_modal
        self.delete_modal.open = True
        self.page.update()

    def refresh_dd_links(self):
        conns = self.page.client_storage.get_keys(prefix)
        self.connect_dd.options = []

        if not conns:
            self.connect_dd.label = i18n("请在右侧添加kafka连接")
        else:
            self.connect_dd.label = i18n("请下拉选择")
            for i in conns:
                text = f'{self.page.client_storage.get(i)}'
                op = ft.dropdown.Option(key=i, text=text)
                self.connect_dd.options.append(op)

    def dropdown_changed(self, e):
        """
        选中下拉后的操作：刷新kafka连接信息
        connect_dd.value实际上就是dropdown.Option里面的key
        """
        # 进度条 loading
        self.pr.visible = True
        self.page.update()

        key = self.connect_dd.value
        self.connect_dd.label = key[len(prefix):]
        bootstrap_servers = self.page.client_storage.get(key)
        print(bootstrap_servers)
        self.page.appbar.title = S_Text(f"{TITLE} | 当前连接: {key[len(prefix):]}")
        self.page.update()

        try:
            kafka_service.set_bootstrap_servers(bootstrap_servers)
            self.refresh_body()
        except Exception as e:
            self.body.controls = [S_Text(value=f"连接失败：{str(e)}", size=24)]
        self.pr.visible = False
        self.page.update()

    def refresh_body(self, e=None):
        """
        点左侧导航，刷新右侧内容（controls）
        :param e:
        :return:
        """
        self.pr.visible = True
        self.page.update()

        selected_index = self.Navigation.selected_index
        view = views_index_map.get(selected_index)
        if not view:
            return

        # 先加载框架主体
        try:
            self.body.controls = view.controls
        except Exception as e:
            self.body.controls = [S_Text(value=str(e), size=24)]
            self.page.update()
            return

        # 进度条 loading
        self.pr.visible = False
        self.page.update()

        # 初始化页面数据
        try:
            err = view.init()
            if err:
                self.body.controls = [S_Text(value=str(err), size=24)]
        except Exception as e:
            traceback.print_exc()
            self.body.controls = [S_Text(value=str(e), size=24)]
            self.pr.visible = False
            self.page.update()
            return

        # 去掉进度条
        self.page.update()
        gc.collect()

    def change_theme(self, e):

        change = {
            ft.ThemeMode.DARK.value: ft.ThemeMode.LIGHT.value,
            ft.ThemeMode.LIGHT.value: ft.ThemeMode.DARK.value,
            ft.ThemeMode.SYSTEM.value: ft.ThemeMode.DARK.value
        }
        try:
            new_theme = change[self.page.theme_mode]
            self.page.theme_mode = new_theme
            self.page.update()
            self.page.client_storage.set("theme", new_theme)
        except Exception as e:
            traceback.print_exc()
            self.page.theme_mode = ft.ThemeMode.DARK.value
            self.page.update()
            self.page.client_storage.set("theme", ft.ThemeMode.DARK.value)


def check(page: ft.Page):
    print("开始检查版本……", UPDATE_URL)

    res = requests.get(UPDATE_URL)
    if res.status_code != 200:
        res = requests.get(UPDATE_URL)
        if res.status_code != 200:
            res = requests.get(UPDATE_URL)
            if res.status_code != 200:
                return
    latest_version = res.json()['tag_name']
    body = res.json()['body']
    # 先获取当前运行时临时目录路径
    basedir = os.path.dirname(__file__)
    print(basedir)
    version = open(f'{basedir}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
    if version != latest_version:
        print("需要更新 {} -> {}".format(version, latest_version))

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🎉🎉发现新版本: {}".format(latest_version)),
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(f"当前版本：{version}"),
                                ft.Text(body),
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                            height=160,
                        ),
                        ft.Row(
                            [
                                ft.TextButton(text="前往下载", url=GITHUB_URL),
                                ft.TextButton(text="下次再说", on_click=close_dlg, style=ft.ButtonStyle(color=ft.colors.GREY)),
                            ]
                        )
                    ],
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),
            open=True,
        )

        page.update()


def init(page: ft.Page):
    page.title = TITLE
    page.window_min_width = 800
    page.window_min_height = 600
    theme = page.client_storage.get("theme")
    if theme is not None:
        page.theme_mode = theme
    language = page.client_storage.get("language")
    if language is not None:
        lang.language = language

    page.theme = ft.Theme(font_family="Microsoft YaHei")

    Main(page)
    t = threading.Thread(target=check, args=(page,))
    t.start()


ft.app(target=init, assets_dir="assets")
