# -*- coding: utf-8 -*-

"""
构建主窗体
"""
from abc import ABC
from typing import Optional

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QSystemTrayIcon
from creart import it, add_creator, exists_module
from creart.creator import AbstractCreator, CreateTargetInfo
from loguru import logger
from qfluentwidgets import InfoBar, InfoBarPosition, NavigationBarPushButton, Theme
from qfluentwidgets.common import FluentIcon
from qfluentwidgets.components import NavigationItemPosition
from qfluentwidgets.window import MSFluentWindow, SplashScreen

from src.Core.Config import cfg
from src.Ui.AddPage import AddWidget
from src.Ui.BotListPage import BotListWidget
from src.Ui.HomePage import HomeWidget
from src.Ui.Icon import NapCatDesktopIcon
from src.Ui.MainWindow.SystemTryIcon import SystemTrayIcon
from src.Ui.MainWindow.TitleBar import CustomTitleBar
from src.Ui.SetupPage import SetupWidget
from src.Ui.UpdatePage import UpdateWidget


class MainWindow(MSFluentWindow):
    """
    ## 程序的主窗体
    """

    def __init__(self) -> None:
        super().__init__()

        self.update_widget: Optional[UpdateWidget] = None
        self.splashScreen: Optional[SplashScreen] = None
        self.setup_widget: Optional[SetupWidget] = None
        self.add_widget: Optional[AddWidget] = None
        self.bot_list_widget: Optional[BotListWidget] = None
        self.home_widget: Optional[HomeWidget] = None

        self.update_widget_button: Optional[NavigationBarPushButton] = None
        self.home_widget_button: Optional[NavigationBarPushButton] = None
        self.add_widget_button: Optional[NavigationBarPushButton] = None
        self.bot_list_widget_button: Optional[NavigationBarPushButton] = None
        self.setup_widget_button: Optional[NavigationBarPushButton] = None

        self.trayIcon: Optional[SystemTrayIcon] = None

    def initialize(self) -> None:
        """
        ## 初始化程序, 并显示窗体
        """
        self.setWindow()
        self.setItem()
        self.setPage()
        self.setTrayIcon()
        # 组件加载完成结束 SplashScreen
        self.splashScreen.finish()
        logger.success("窗体构建完成")

        # 检查 EULA
        self.showEULA()

    def setWindow(self) -> None:
        """
        设置窗体
        """
        # 标题栏部分
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon(NapCatDesktopIcon.LOGO.path(Theme.LIGHT)))
        # 窗体大小以及设置打开时居中
        self.setMinimumSize(930, 630)
        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)
        # 创建 Splash Screen
        self.splashScreen = SplashScreen(":Global/logo.png", self, True)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.raise_()
        # 显示窗体
        self.show()
        # 挂起
        QApplication.processEvents()
        logger.success("窗体设置完成")

    def setItem(self) -> None:
        """
        设置侧边栏
        """
        self.setup_widget = it(SetupWidget).initialize(self)
        self.add_widget = it(AddWidget).initialize(self)
        self.bot_list_widget = it(BotListWidget).initialize(self)
        self.update_widget = it(UpdateWidget).initialize(self)
        self.home_widget = it(HomeWidget).initialize(self)

        # 添加子页面
        self.home_widget_button = self.addSubInterface(
            interface=self.home_widget,
            icon=FluentIcon.HOME,
            text=self.tr("Home"),
            position=NavigationItemPosition.TOP
        )

        self.add_widget_button = self.addSubInterface(
            interface=self.add_widget,
            icon=FluentIcon.ADD_TO,
            text=self.tr("Add Bot"),
            position=NavigationItemPosition.TOP
        )
        self.bot_list_widget_button = self.addSubInterface(
            interface=self.bot_list_widget,
            icon=FluentIcon.MENU,
            text=self.tr("Bot List"),
            position=NavigationItemPosition.TOP
        )
        self.update_widget_button = self.addSubInterface(
            interface=self.update_widget,
            icon=FluentIcon.UPDATE,
            text=self.tr("Update"),
            position=NavigationItemPosition.TOP
        )
        widget1 = QWidget()
        widget1.setObjectName("fix")
        self.fix_widget_button = self.addSubInterface(
            interface=widget1,
            icon=FluentIcon.DEVELOPER_TOOLS,
            text=self.tr("Fix"),
            position=NavigationItemPosition.TOP
        )
        self.setup_widget_button = self.addSubInterface(
            interface=self.setup_widget,
            icon=FluentIcon.SETTING,
            text=self.tr("Setup"),
            position=NavigationItemPosition.BOTTOM
        )

        logger.success("侧边栏构建完成")

    def setPage(self) -> None:
        """
        ## 窗口创建完成进行一些处理
        """
        self.bot_list_widget.botList.updateList()

    def setTrayIcon(self):
        """
        ## 设置托盘图标
        """
        self.trayIcon = SystemTrayIcon(self)
        self.trayIcon.activated.connect(self.trayIconAction)
        self.trayIcon.show()

    def showEULA(self):
        """
        ## 检测用户是否同意EULA
        """
        if cfg.get(cfg.EULA):
            return
        from src.Core.EULA import EULAMessageBox
        self.home_widget_button.setEnabled(False)
        self.add_widget_button.setEnabled(False)
        self.bot_list_widget_button.setEnabled(False)
        self.setup_widget_button.setEnabled(False)
        if EULAMessageBox(self.home_widget).exec():
            self.home_widget_button.setEnabled(True)
            self.add_widget_button.setEnabled(True)
            self.bot_list_widget_button.setEnabled(True)
            self.setup_widget_button.setEnabled(True)
            cfg.set(cfg.EULA, True, True)
        else:
            self.close()

    @Slot(QSystemTrayIcon)
    def trayIconAction(self, reason: QSystemTrayIcon):
        """
        ## 托盘图标被点击事件
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal() if self.isMinimized() else None
            self.show() if self.isHidden() else None

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    @staticmethod
    def showInfo(title: str, content: str, showcasePage: QWidget) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        InfoBar.info(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,
            duration=5000,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=showcasePage
        )

    @staticmethod
    def showError(title: str, content: str, showcasePage: QWidget) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,
            duration=50000,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=showcasePage
        )

    @staticmethod
    def showWarning(title: str, content: str, showcasePage: QWidget) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,
            duration=10000,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=showcasePage
        )

    @staticmethod
    def showSuccess(title: str, content: str, showcasePage: QWidget) -> None:
        """
        # 配置 InfoBar 的一些配置, 简化内部使用 InfoBar 的步骤
        """
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,
            duration=5000,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=showcasePage
        )


class MainWindowClassCreator(AbstractCreator, ABC):
    # 定义类方法targets，该方法返回一个元组，元组中包含了一个CreateTargetInfo对象，
    # 该对象描述了创建目标的相关信息，包括应用程序名称和类名。
    targets = (CreateTargetInfo("src.Ui.MainWindow.Window", "MainWindow"),)

    # 静态方法available()，用于检查模块"MainWindow"是否存在，返回值为布尔型。
    @staticmethod
    def available() -> bool:
        return exists_module("src.Ui.MainWindow.Window")

    # 静态方法create()，用于创建MainWindow类的实例，返回值为MainWindow对象。
    @staticmethod
    def create(create_type: [MainWindow]) -> MainWindow:
        return MainWindow()


add_creator(MainWindowClassCreator)
