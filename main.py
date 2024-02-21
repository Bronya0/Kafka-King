import traceback
import gc
import flet as ft
from flet_core import TextField

from common import S_Text, prefix, S_Button
from service.kafka_service import kafka_service
from views.init import views_index_map


def init_page(page: ft.Page):
    page.title = "Kafka King"
    page.window_min_width = 800
    page.window_min_height = 600
    theme = page.client_storage.get("theme")
    if theme:
        page.theme_mode = theme


def main(page: ft.Page):
    init_page(page)

    def test_connect(e):
        if kafka_input.value == "":
            msg = "请先填写kafka连接"
            color = "#000000"
        else:
            res = kafka_service.new_client(bootstrap_servers=kafka_input.value.split(','))
            if res:
                msg = f"连接成功"
                color = "#00a0b0"
            else:
                msg = f"连接失败"
                color = "#000000"

        page.snack_bar.content = ft.Text(msg)
        page.snack_bar.bgcolor = color
        page.snack_bar.open = True
        page.update()

    def add_connect(e):
        # 存储连接：{prefix}{连接名} <-> 链接地址
        page.client_storage.set(f"{prefix}{conn_name_input.value}", kafka_input.value)
        refresh_dd_links()
        dlg_modal.open = False
        kafka_input.value = None
        conn_name_input.value = None
        page.update()

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def refresh_dd_links():
        conns = page.client_storage.get_keys(prefix)
        if not conns:
            connect_dd.label = "请添加kafka连接"
        else:
            connect_dd.label = "请选择kafka连接"
            connect_dd.options = []
            for i in conns:
                connect_dd.options.append(ft.dropdown.Option(key=i, text=f'{page.client_storage.get(i)}'))

    def dropdown_changed(e):
        """
        选中下拉后的操作：刷新kafka连接信息
        connect_dd.value实际上就是dropdown.Option里面的key
        """
        # 进度条 loading
        page.controls.append(ft.ProgressBar())
        page.update()

        key = connect_dd.value
        connect_dd.label = key[len(prefix):]
        bootstrap_servers = page.client_storage.get(key)
        print(bootstrap_servers)
        try:
            kafka_service.set_bootstrap_servers(bootstrap_servers)
            refresh_body()
            page.appbar.title = S_Text(key[len(prefix):])
        except Exception as e:
            body.controls = [S_Text(value=f"连接失败：{str(e)}", size=24)]
        page.controls.pop()
        page.update()

    def refresh_body(e=None):
        """
        点左侧导航，刷新右侧内容（controls）
        :param e:
        :return:
        """

        selected_index = Navigation.selected_index
        view = views_index_map.get(selected_index)
        if not view:
            return

        # 先加载框架主体
        try:
            view = view()
            body.controls = view.controls
        except Exception as e:
            body.controls = [S_Text(value=str(e), size=24)]
            page.update()
            return

        # 进度条 loading
        view.controls.append(ft.ProgressBar())
        page.update()

        # 初始化页面数据
        try:
            err = view.init()
            if err:
                body.controls = [S_Text(value=str(err), size=24)]
        except Exception as e:
            traceback.print_exc()
            body.controls = [S_Text(value=str(e), size=24)]
            page.update()
            return

        # 去掉进度条
        view.controls.pop()
        page.update()
        gc.collect()

    def change_theme(e):
        change = {
            ft.ThemeMode.DARK.value: ft.ThemeMode.LIGHT.value,
            ft.ThemeMode.LIGHT.value: ft.ThemeMode.DARK.value,
            ft.ThemeMode.SYSTEM.value: ft.ThemeMode.DARK.value
        }
        new_theme = change[page.theme_mode]
        page.theme_mode = new_theme

        page.client_storage.set("theme", new_theme)
        page.update()

    # 创建输入表单控件
    conn_name_input = TextField(label="连接名", hint_text="例如：本地环境", height=40)
    kafka_input = TextField(label="Kafka地址", hint_text="例如：127.0.0.1:9092", height=40)
    connect_input_column = ft.Column([
        conn_name_input,
        kafka_input,
        ft.Row([
            ft.TextButton("测试连接", on_click=test_connect, on_long_press=True),
            ft.TextButton("是", on_click=add_connect),
            ft.TextButton("否", on_click=close_dlg),
        ])
    ])

    # 添加kafka link
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=S_Text("添加kafka连接"),
        actions=[
            connect_input_column,
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    # 链接下拉
    connect_dd = ft.Dropdown(
        label="连接",
        options=[],
        height=35,
        text_size=16,
        on_change=dropdown_changed,
        alignment=ft.alignment.center_left,
        dense=True,
        content_padding=10,
        focused_bgcolor='#ff0000',
    )

    # 侧边导航栏 NavigationRail
    Navigation = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        # 定义在导航栏中排列的按钮项的外观，该值必须是两个或更多NavigationRailDestination实例的列表。
        destinations=[
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.HIVE_OUTLINED, tooltip="查看集群broker节点和配置"),
                selected_icon_content=ft.Icon(ft.icons.HIVE),
                label="Broker",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.LIBRARY_BOOKS_OUTLINED, tooltip="增删改topic及partition"),
                selected_icon_content=ft.Icon(ft.icons.LIBRARY_BOOKS),
                label="Topic",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.SWITCH_ACCESS_SHORTCUT_ADD_OUTLINED, tooltip="模拟producer及consumer"),
                selected_icon_content=ft.Icon(ft.icons.SWITCH_ACCESS_SHORTCUT_ADD),
                label="Simulate",
            ),

            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.STACKED_BAR_CHART_OUTLINED, tooltip="监控（开发中）"),
                selected_icon_content=ft.Icon(ft.icons.STACKED_BAR_CHART),
                label="Monitor",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.SETTINGS_OUTLINED, tooltip="配置（开发中）"),
                selected_icon_content=ft.Icon(ft.icons.SETTINGS_SUGGEST_OUTLINED),
                label_content=S_Text("Settings"),
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.AUTO_GRAPH_OUTLINED, tooltip="建议我们"),
                selected_icon_content=ft.Icon(ft.icons.AUTO_GRAPH),
                label_content=S_Text("Suggest"),
            ),
        ],
        on_change=refresh_body,
    )

    # 每个页面的主体
    body = ft.Column(
        controls=[],
        expand=True
    )

    # 底部提示
    page.snack_bar = ft.SnackBar(content=ft.Text(""))

    # 顶部导航
    page.appbar = ft.AppBar(
        leading=ft.Image(src="assets/icon.png"),
        leading_width=40,
        title=S_Text("Kafka Client"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            connect_dd,
            ft.IconButton(ft.icons.ADD, on_click=open_dlg_modal, tooltip="添加kafka地址"),  # add link
            ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, on_click=change_theme, tooltip="切换明暗"),  # theme
            # ft.IconButton(ft.icons.TRANSLATE),
            ft.IconButton(ft.icons.TIPS_AND_UPDATES_OUTLINED, tooltip="去github更新或者提出想法",
                          url="https://github.com/Bronya0/Kafka-King"),
            # ft.IconButton(ft.icons.STAR_RATE_OUTLINED),
        ],
    )

    # 初始化加载全部连接
    refresh_dd_links()

    page.add(
        ft.Row(
            [
                Navigation,  # 侧边
                ft.VerticalDivider(width=1),  # 竖线
                body  # 内容
            ],
            expand=True,
        )
    )


ft.app(target=main, assets_dir="assets")
