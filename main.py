import ast
import gc
import traceback

import flet as ft
from flet_core import TextField, ControlEvent

from service.check import version_check, ping
from service.common import S_Text, prefix, GITHUB_URL, TITLE, open_snack_bar, close_dlg, PAGE_WIDTH, PAGE_HEIGHT, \
    WINDOW_TOP, WINDOW_LEFT, view_instance_map, Navigation, body, progress_bar, CONFIG_KEY, PAGE_MIN_WIDTH, \
    PAGE_MIN_HEIGHT, common_page
from service.font import get_default_font, get_os_platform
from service.kafka_service import kafka_service
from service.translate import lang, i18n
from views.all_views import get_view_instance


class Main:

    def __init__(self, page: ft.Page):
        self.page: ft.Page = page

        # self.page.window.on_event = self.on_win_event

        self.page_width = PAGE_WIDTH
        self.page_height = PAGE_HEIGHT
        self.window_top = WINDOW_TOP
        self.window_left = WINDOW_LEFT

        # 存储当前实例化的页面，用于左侧点击切换

        self.delete_modal = ft.AlertDialog(
            modal=False,
            title=S_Text("删除kafka连接？"),
            actions=[
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),

        )

        # 添加连接
        self.conn_name_input = TextField(tooltip="连接名", label="连接名，任意取名，保证唯一", hint_text="例如：本地环境",
                                         height=40, content_padding=5)
        self.bootstrap_servers = TextField(
            tooltip="Kafka地址，使用域名:port而不是ip:port，必须在本地添加域名ip映射，多个地址用逗号分隔，通常写一个就行",
            label="bootstrap_servers", hint_text="域名:9092，必须在本地电脑添加域名ip映射", height=40, content_padding=5)
        self.api_version = TextField(
            tooltip="指定要使用的 Kafka API 版本。如果不设置，则将尝试通过探测各种 API 来推断代理版本。示例：(2, 5, 0)",
            label="api_version", hint_text="例如：(2, 5, 0)", height=40, content_padding=5)

        self.ssl_cafile = TextField(tooltip="证书验证的CA文件的文件路径", hint_text=r"例如：C:\ssl\ca.pem",
                                    label="ssl_cafile", height=40, content_padding=5)
        self.ssl_certfile = TextField(
            tooltip="证书PEM文件的文件路径，其中包含客户端证书以及建立证书真实性所需的任何 CA 证书",
            hint_text=r"例如：C:\ca.pem or .keytab", label="ssl_certfile", height=40, content_padding=5)
        self.ssl_keyfile = TextField(tooltip="包含客户端私钥的可选文件路径", hint_text=r"例如：C:\ssl\client.key",
                                     label="ssl_keyfile", height=40, content_padding=5)
        self.ssl_password = TextField(tooltip="加载证书链时使用的可选密码,如果你的key文件有密码的话",
                                      label="ssl_password", height=40, content_padding=5)
        self.ssl_crlfile = TextField(
            tooltip="包含用于检查证书过期的CRL文件路径。默认情况下，不执行 CRL 检查。提供文件时，将仅根据此 CRL 检查叶证书。",
            hint_text=r"例如：C:\ssl\ca.pem", label="ssl_crlfile", height=40, content_padding=5)

        self.security_protocol = ft.Dropdown(
            tooltip="可选：与代理通信的协议。有效值为：PLAINTEXT、SSL、SASL_PLAINTEXT、SASL_SSL。默认值：PLAINTEXT。",
            options=[
                ft.dropdown.Option("PLAINTEXT"),
                ft.dropdown.Option("SSL"),
                ft.dropdown.Option("SASL_PLAINTEXT"),
                ft.dropdown.Option("SASL_SSL"),
            ],
            value="PLAINTEXT", label="代理通信协议", dense=True, height=40, text_size=14, content_padding=7
        )
        self.sasl_mechanism = ft.Dropdown(
            tooltip="可选：为 SASL_PLAINTEXT 或 SASL_SSL 配置代理通信协议时的身份验证机制。有效值为：PLAIN、GSSAPI、OAUTHBEARER、SCRAM-SHA-256、SCRAM-SHA-512。",
            options=[
                ft.dropdown.Option("PLAIN"),
                ft.dropdown.Option("GSSAPI"),
                ft.dropdown.Option("OAUTHBEARER"),
                ft.dropdown.Option("SCRAM-SHA-256"),
                ft.dropdown.Option("SCRAM-SHA-512"),
            ],
            label="sasl身份验证机制", dense=True, height=40, text_size=14, content_padding=7
        )
        self.sasl_plain_username = TextField(
            tooltip="可选：用于 sasl PLAIN 和 SCRAM 身份验证的用户名。如果 身份验证机制 是 PLAIN 或 SCRAM 机制之一，则为必需。",
            label="sasl/SCRAM 用户名", hint_text="", height=40, content_padding=5)
        self.sasl_plain_password = TextField(
            tooltip="可选：用于 sasl PLAIN 和 SCRAM 身份验证的密码。如果 身份验证机制 是 PLAIN 或 SCRAM 机制之一，则为必需。",
            label="sasl/SCRAM 密码", hint_text="", height=40, content_padding=5)
        # self.sasl_kerberos_service_name = TextField(
        #     tooltip="可选：要包含在 GSSAPI sasl 机制握手中的服务名称。默认值：'kafka'", label="sasl Kerberos GSSAPI服务名",
        #     hint_text="", height=40, content_padding=5)
        # self.sasl_kerberos_domain_name = TextField(
        #     tooltip="可选：用于 GSSAPI SASL 机制握手的 Kerberos 域名。默认值：引导服务器之一", label="sasl Kerberos域名",
        #     hint_text="", height=40, content_padding=5)
        # # https://www.cnblogs.com/zjqv/p/16810181.html
        # self.krb5_conf = TextField(
        #     tooltip="可选：Kerberos krb5conf文件位置", label="Kerberos krb5.conf",
        #     hint_text="Kerberos krb5.conf文件位置", height=40, content_padding=5)

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
            width=250,
        )

        # 侧边导航栏 NavigationRail
        self.Navigation = Navigation
        self.Navigation.on_change = self.refresh_view

        self.color_menu_item = [
            ft.MenuItemButton(
                data="primary",
                content=ft.Text("default"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="red",
                content=ft.Text("red"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="orange",
                content=ft.Text("orange"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="pink",
                content=ft.Text("pink"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="yellow",
                content=ft.Text("yellow"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="green",
                content=ft.Text("green"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="blue",
                content=ft.Text("blue"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="purple",
                content=ft.Text("purple"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="grey",
                content=ft.Text("grey"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="white",
                content=ft.Text("white"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="black",
                content=ft.Text("black"),
                on_click=self.change_color,
            ),

        ]
        self.color_menu = ft.Dropdown(
            options=self.color_menu_item,
            label="  配色",
            height=35,
            alignment=ft.alignment.center_left,
            content_padding=5,
            width=100,
        )
        # 工具按钮
        self.tools = [
            ft.TextButton("添加kafka连接", on_click=self.add_dlg_modal, icon=ft.icons.ADD_BOX_OUTLINED,
                          tooltip="添加kafka地址",
                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("编辑/删除当前kafka连接", on_click=self.edit_link_modal, icon=ft.icons.EDIT,
                          tooltip="编辑kafka地址",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("切换主题", on_click=self.change_theme, icon=ft.icons.WB_SUNNY_OUTLINED, tooltip="切换明暗",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("更新", on_click=self.change_theme, icon=ft.icons.UPGRADE_OUTLINED,
                          tooltip="去github更新或者提出想法",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8)),
                          url=GITHUB_URL),
        ]
        # 每个页面的主体
        self.body = body
        self.body.controls = self.tools

        # 底部提示
        self.page.overlay.append(ft.SnackBar(content=ft.Text("")))

        # 顶部导航
        # 如果 AppBar.adaptive=True 且应用程序在 iOS 或 macOS 设备上打开，则仅使用此列表的第一个元素!!!!!!
        self.page.appbar = ft.AppBar(
            leading=ft.Image(src="icon.png"),
            leading_width=40,
            title=S_Text(TITLE),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                self.connect_dd,
                ft.TextButton("添加", on_click=self.add_dlg_modal, icon=ft.icons.ADD_BOX_OUTLINED,
                              tooltip="添加kafka地址", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                ft.IconButton(on_click=self.edit_link_modal, icon=ft.icons.EDIT, tooltip="编辑kafka地址",
                              style=ft.ButtonStyle(color=ft.colors.SECONDARY,
                                                   shape=ft.RoundedRectangleBorder(radius=8))),
                ft.IconButton(on_click=self.change_theme, icon=ft.icons.WB_SUNNY_OUTLINED, tooltip="切换明暗", ),
                ft.IconButton(on_click=self.change_theme, icon=ft.icons.UPGRADE_OUTLINED,
                              tooltip="去github更新或者提出想法", url=GITHUB_URL),
                self.color_menu,
                ft.Text("   ")
                # ft.IconButton(on_click=self.window_min, icon=ft.icons.HORIZONTAL_RULE_OUTLINED, tooltip="最小化", ),
                # ft.IconButton(on_click=self.window_max, icon=ft.icons.CROP_SQUARE_OUTLINED, tooltip="最大化", ),
                # ft.IconButton(on_click=self.window_close, icon=ft.icons.CLOSE_ROUNDED, tooltip="关闭", ),
            ],
        )

        self.pr = progress_bar
        # 初始化加载全部连接
        self.refresh_dd_links()

        # 页面主体框架
        self.page.add(
            ft.Row(
                [
                    self.Navigation,  # 侧边
                    ft.VerticalDivider(width=1),  # 竖线
                    self.body,  # 内容
                ],
                expand=True
            ),
            ft.Column(
                [
                    self.pr
                ],
                height=8
            )

        )

    def test_connect(self, e: ControlEvent):
        """
        连接测试
        """
        e.control.text = "连接中……"
        e.page.update()
        conn_name = self.conn_name_input.value
        print("连接测试：", conn_name)

        color = "green"
        err = None
        if None in [conn_name, self.bootstrap_servers.value] or "" in [conn_name, self.bootstrap_servers.value]:
            msg = "请先填写kafka连接"
        else:
            conn = self.get_conn()
            res, err = kafka_service.new_client(conn_name, conn)
            if res:
                msg = f"连接成功"
                color = "green"
            else:
                msg = f"连接失败: {err}"
                color = "red"

        e.control.text = msg
        e.control.tooltip = err
        e.control.style = ft.ButtonStyle(color=color)
        self.page.update()

    def add_connect(self, e):
        """
        存储连接信息，会覆盖，唯一key是连接名。{prefix: {"name1": [bootstraps, sasl name, sasl pwd]}}
        """
        connect_name = self.conn_name_input.value
        print("添加连接：", e.control.data)

        connects = self.page.client_storage.get(prefix)
        connects = {} if connects is None else connects
        connects.pop(connect_name, None)

        connects[connect_name] = self.get_conn()
        print("保存：", connects)

        self.page.client_storage.set(prefix, connects)

        # 添加连接后，回到首页
        self.Navigation.selected_index = 0
        self.refresh_dd_links()
        close_dlg(e)

        # 清空输入框
        self.clear_conn()
        open_snack_bar(e.page, "操作成功", True)

    def add_dlg_modal(self, e):
        """
        添加kafka连接 弹框
        """

        # 创建输入表单控件

        def cancel(event):
            close_dlg(event)
            self.clear_conn()

        dlg_modal = ft.AlertDialog(
            modal=True,
            open=True,
            title=S_Text("添加kafka连接"),
            actions=[
                ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("必填：连接信息"),
                            self.conn_name_input,
                            self.bootstrap_servers,
                            ft.Text("选填：kafka API版本信息"),
                            self.api_version,
                        ]),
                        ft.Column([
                            ft.Text("选填：ssl配置"),
                            self.ssl_cafile,
                            self.ssl_certfile,
                            self.ssl_keyfile,
                            self.ssl_password,
                        ]),
                        ft.Column([
                            ft.Text("选填：sasl配置"),
                            self.security_protocol,
                            self.sasl_mechanism,
                            self.sasl_plain_username,
                            self.sasl_plain_password,
                            # self.sasl_kerberos_service_name,
                            # self.sasl_kerberos_domain_name,
                        ]),
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Text("提示：请先将kafka节点的域名ip映射添加到本地hosts文件中，否则无法连接", color="red"),
                    ft.Row([
                        ft.TextButton("连接测试", on_click=self.test_connect,
                                      style=ft.ButtonStyle(color=ft.colors.RED),
                                      ),
                        ft.TextButton("添加", on_click=self.add_connect,
                                      data=self.conn_name_input.value
                                      ),
                        ft.TextButton("取消", on_click=cancel),
                    ])
                ],
                    width=960
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=2)

        )
        e.page.dialog = dlg_modal
        e.page.update()

    def delete_connect(self, e):
        key = e.control.data
        connects = e.page.client_storage.get(prefix)
        print("删除：", key, connects)
        connects.pop(key, None)
        e.page.client_storage.set(prefix, connects)
        self.refresh_dd_links()
        close_dlg(e)
        self.clear_conn()
        open_snack_bar(e.page, "删除成功", True)

    def edit_link_modal(self, e: ControlEvent):
        """
        编辑、删除连接
        """

        def cancel(event):
            close_dlg(event)
            self.clear_conn()

        connect_name = self.connect_dd.value
        if not connect_name:
            open_snack_bar(e.page, "请先打开kafka连接", False)
            return
        conn: dict = self.page.client_storage.get(prefix).get(connect_name, {})

        self.conn_name_input.value = connect_name
        self.bootstrap_servers.value = conn.get("bootstrap_servers")
        self.api_version.value = conn.get("api_version")
        self.ssl_cafile.value = conn.get("ssl_cafile")
        self.ssl_certfile.value = conn.get("ssl_certfile")
        self.ssl_keyfile.value = conn.get("ssl_keyfile")
        self.ssl_password.value = conn.get("ssl_password")
        self.security_protocol.value = conn.get("security_protocol")
        self.sasl_mechanism.value = conn.get("sasl_mechanism")
        self.sasl_plain_username.value = conn.get("sasl_plain_username")
        self.sasl_plain_password.value = conn.get("sasl_plain_password")
        # self.sasl_kerberos_service_name.value = conn.get("sasl_kerberos_service_name")
        # self.sasl_kerberos_domain_name.value = conn.get("sasl_kerberos_domain_name")

        e.page.dialog = ft.AlertDialog(
            modal=True,
            open=True,
            title=S_Text("编辑连接"),
            actions=[
                ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("必填：连接信息"),
                            self.conn_name_input,
                            self.bootstrap_servers,
                            ft.Text("选填：kafka API版本信息"),
                            self.api_version,
                        ]),
                        ft.Column([
                            ft.Text("选填：ssl配置"),
                            self.ssl_cafile,
                            self.ssl_certfile,
                            self.ssl_keyfile,
                            self.ssl_password,
                        ]),
                        ft.Column([
                            ft.Text("选填：sasl配置"),
                            self.security_protocol,
                            self.sasl_mechanism,
                            self.sasl_plain_username,
                            self.sasl_plain_password,
                            # self.sasl_kerberos_service_name,
                            # self.sasl_kerberos_domain_name,
                        ]),
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Text("提示：请先将kafka节点的域名ip映射添加到本地hosts文件中，否则无法连接", color="red"),
                    ft.Row([
                        ft.TextButton("连接测试", on_click=self.test_connect,
                                      style=ft.ButtonStyle(color=ft.colors.RED),
                                      data=conn
                                      ),
                        ft.TextButton("删除", on_click=self.delete_connect,
                                      style=ft.ButtonStyle(color=ft.colors.RED),
                                      data=self.conn_name_input.value),

                        ft.TextButton("保存", on_click=self.add_connect,
                                      data=(self.conn_name_input.value, conn)
                                      ),
                        ft.TextButton("取消", on_click=cancel),
                    ])
                ],
                    width=960
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=2)

        )

        self.refresh_dd_links()
        e.page.update()

    def refresh_dd_links(self):
        """
        更新连接下拉菜单
        conns = {"name1": [bootstraps, sasl name, sasl pwd]}
        """
        conns: dict = self.page.client_storage.get(prefix)
        options = []
        print("当前全部连接存储：", conns)

        # 清理历史的格式不对的存储
        new_conns = {}
        need_write = False
        for k, v in conns.items():
            if isinstance(v, dict):
                new_conns[k] = v
            else:
                need_write = True
        if need_write:
            self.page.client_storage.set(prefix, new_conns)

        if not new_conns:
            self.connect_dd.label = i18n("请添加kafka连接")
        else:
            self.connect_dd.label = i18n("请选择连接")
            for name, coon in new_conns.items():
                op = ft.dropdown.Option(key=name, text=f"『{name}』 {coon.get('bootstrap_servers')}")
                options.append(op)
        self.connect_dd.options = options

    def dropdown_changed(self, e):
        """
        选中下拉后的操作：刷新kafka连接信息
        connect_dd.value实际上就是dropdown.Option里面的key
        """
        # 进度条 loading
        self.pr.visible = True
        self.page.update()

        conn_name = self.connect_dd.value
        self.connect_dd.label = conn_name

        conns: dict = self.page.client_storage.get(prefix)

        conn = conns.get(conn_name)
        print(conn_name)
        self.page.appbar.title = S_Text(f"{TITLE} | 当前连接: {conn_name}")
        self.Navigation.selected_index = 0
        print("切换连接时，清空页面缓存")
        view_instance_map.clear()
        self.body.controls = []
        self.page.update()

        try:
            kafka_service.set_connect(conn_name, conn)
            self.refresh_body()
        except Exception as e:
            self.body.controls = [S_Text(value=f"连接失败：{str(e)}", size=24)] + self.tools
        self.pr.visible = False
        self.page.update()

    def refresh_view(self, e):
        """
        点左侧导航，获取右侧内容（controls）
        """
        selected_index = self.Navigation.selected_index
        view = view_instance_map.get(selected_index)
        self.refresh_body(view=view)

    def refresh_body(self, view=None):
        """
        重新实例化页面
        """
        self.pr.visible = True
        self.pr.update()

        selected_index = self.Navigation.selected_index
        if view:
            print(f"读取缓存view: {selected_index}，执行init函数")
        else:
            view = get_view_instance(selected_index)()
            print(f"无缓存，初始化view：{selected_index}，并执行init函数")

        # 先加载框架主体
        try:
            self.body.controls = view.controls
        except Exception as e:
            traceback.print_exc()
            self.body.controls = [S_Text(value=str(e), size=24)] + self.tools
            self.page.update()
            return

        self.body.update()

        # 初始化页面数据
        try:
            # 每个页面的init函数会在每次点击后重复执行
            err = view.init(page=self.page)
            if err:
                self.body.controls = [S_Text(value=str(err), size=24)]
        except Exception as e:
            traceback.print_exc()
            self.body.controls = [S_Text(value=str(e), size=24)] + self.tools
            self.pr.visible = False
            self.page.update()
            return

        # 进度条 loading
        self.pr.visible = False
        self.body.update()
        self.pr.update()

        # 缓存页面。
        view_instance_map[selected_index] = view
        gc.collect()

    def get_conn(self):
        api_version = None
        if self.api_version.value:
            try:
                api_version = ast.literal_eval(self.api_version.value)
            except:
                open_snack_bar(self.page, i18n("api_version格式不正确，请检查"))

        conn = {
            "bootstrap_servers": self.bootstrap_servers.value,
            "api_version": api_version,
            "ssl_cafile": self.ssl_cafile.value,
            "ssl_certfile": self.ssl_certfile.value,
            "ssl_keyfile": self.ssl_keyfile.value,
            "ssl_password": self.ssl_password.value,
            "ssl_crlfile": self.ssl_crlfile.value,
            "security_protocol": self.security_protocol.value,
            "sasl_mechanism": self.sasl_mechanism.value,
            "sasl_plain_username": self.sasl_plain_username.value,
            "sasl_plain_password": self.sasl_plain_password.value,
            # "sasl_kerberos_service_name": self.sasl_kerberos_service_name.value,
            # "sasl_kerberos_domain_name": self.sasl_kerberos_domain_name.value,
        }
        conn = {key: value for key, value in conn.items() if value is not None and value != ""}
        return conn

    def clear_conn(self):
        for i in (self.conn_name_input, self.bootstrap_servers, self.api_version,
                  self.ssl_cafile, self.ssl_certfile, self.ssl_keyfile, self.ssl_password, self.ssl_crlfile,
                  self.security_protocol, self.sasl_mechanism, self.sasl_plain_username, self.sasl_plain_password,
                  # self.sasl_kerberos_service_name, self.sasl_kerberos_domain_name
                  ):
            i.value = None

    def change_color(self, e):
        """
        切换主题颜色
        """
        try:
            self.page.theme.color_scheme_seed = e.control.data
            self.page.update()
            self.page.client_storage.set("color", e.control.data)
            print("切换主题颜色：", e.control.data)
        except Exception as e:
            traceback.print_exc()
            self.page.update()

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

    def window_max(self, e):
        if self.page.window.maximized:
            self.page.window.maximized = False
        else:
            self.page.window.maximized = True
        self.page.update()

    def window_min(self, e):
        if self.page.window.minimized:
            self.page.window.minimized = False
        else:
            self.page.window.minimized = True
        self.page.update()

    def window_close(self, e):
        self.page.window.close()


def init_config(page):
    config = page.client_storage.get(CONFIG_KEY)

    if not config:
        config = {
            "language": "简体中文",
            "default_width": PAGE_WIDTH,
            "default_height": PAGE_HEIGHT,
        }
        page.client_storage.set(CONFIG_KEY, config)
    return config


def init(page: ft.Page):
    page.title = TITLE
    common_page.set_page(page)
    # page.window.frameless = True

    # 主题
    theme = page.client_storage.get("theme")
    if theme is not None:
        page.theme_mode = theme

    config = init_config(page)

    language = config.get('language')
    if language is not None:
        lang.language = language

    # 主题
    font_family = get_default_font(get_os_platform())
    color = page.client_storage.get("color")
    page.theme = ft.Theme(font_family=font_family, color_scheme_seed=color)

    # 窗口大小
    page.window.width = config['default_width'] if 'default_width' in config else PAGE_WIDTH
    page.window.height = config['default_height'] if 'default_height' in config else PAGE_HEIGHT
    page.window.min_width = PAGE_MIN_WIDTH
    page.window.min_height = PAGE_MIN_HEIGHT

    Main(page)

    # 版本检查, 务必要包异常，内网无法连接会报错
    try:
        version_check(page)
        ping()
    except:
        traceback.print_exc()


if __name__ == '__main__':
    ft.app(target=init, assets_dir="assets")
