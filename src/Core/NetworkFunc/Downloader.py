# -*- coding: utf-8 -*-
# 标准库导入
from pathlib import Path

# 第三方库导入
import httpx
from creart import it
from loguru import logger
from PySide6.QtCore import QUrl, Signal, QThread

# 项目内模块导入
from src.Ui.UnitPage.status import ButtonStatus, ProgressRingStatus
from src.Core.Utils.PathFunc import PathFunc


class NapCatDownloader(QThread):
    """
    ## 执行下载 NapCat 的任务
    """
    # 按钮模式切换
    buttonToggle = Signal(ButtonStatus)
    # 进度条模式切换
    progressRingToggle = Signal(ProgressRingStatus)
    # 状态标签
    statusLabel = Signal(str)
    # 下载进度
    downloadProgress = Signal(int)
    # 下载完成
    downloadFinish = Signal()
    # 引发错误导致结束
    errorFinsh = Signal()

    def __init__(self, url: QUrl) -> None:
        """
        ## 初始化下载器
            - url 下载连接
            - path 下载路径
        """
        super().__init__()
        self.url: QUrl = url
        self.path: Path = it(PathFunc).tmp_path

    def run(self) -> None:
        """
        ## 运行下载 NapCat 的任务
            - 自动检查是否需要使用代理
            - 尽可能下载成功
        """
        # 显示进度环为不确定进度环
        self.progressRingToggle.emit(ProgressRingStatus.INDETERMINATE)

        # 检查网络环境
        if not self.checkNetwork():
            # 如果网络环境不好, 则调整下载链接
            self.url = QUrl(f"https://gh.ddlc.top/{self.url.url()}")
            logger.info(f"访问 GITHUB 速度偏慢,切换下载链接为: https://gh.ddlc.top/{self.url.url()}")
            self.statusLabel.emit(self.tr("网络环境较差"))

        # 开始下载
        try:
            logger.info(f"{'-' * 10} 开始下载 NapCat ~ {'-' * 10}")
            self.statusLabel.emit(self.tr(" 开始下载 NapCat ~ "))
            with httpx.stream("GET", self.url.url(), follow_redirects=True) as response:

                if (total_size := int(response.headers.get("content-length", 0))) == 0:
                    # 尝试获取文件大小
                    logger.error("无法获取文件大小, Content-Length为空或无法连接到下载链接")
                    self.statusLabel.emit(self.tr("无法获取文件大小"))
                    self.errorFinsh.emit()
                    return

                # 设置进度条为 进度模式
                self.progressRingToggle.emit(ProgressRingStatus.DETERMINATE)

                with open(f"{self.path / self.url.fileName()}", "wb") as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)  # 写入字节
                        self.statusLabel.emit(self.tr("正在下载 NapCat ~ "))
                        self.downloadProgress.emit(int((file.tell() / total_size) * 100))  # 设置进度条

            # 下载完成
            self.downloadFinish.emit()  # 发送下载完成信号
            self.statusLabel.emit(self.tr("下载完成"))
            logger.info(f"{'-' * 10} 下载 NapCat 结束 ~ {'-' * 10}")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"发送下载 NapCat 请求时引发 HTTPStatusError, "
                f"响应码: {e.response.status_code}, 响应内容: {e.response.content}"
            )
            self.statusLabel.emit(self.tr("下载失败"))
            self.errorFinsh.emit()
        except (httpx.RequestError, FileNotFoundError, PermissionError, Exception) as e:
            logger.error(f"下载 NapCat 时引发 {type(e).__name__}: {e}")
            self.statusLabel.emit(self.tr("下载失败"))
            self.errorFinsh.emit()

        finally:
            # 无论是否出错,都会重置
            self.progressRingToggle.emit(ProgressRingStatus.INDETERMINATE)

    def checkNetwork(self) -> bool:
        """
        ## 检查网络能否正常访问 Github
        """
        try:
            logger.info(f"{'-' * 10} 检查网络环境 {'-' * 10}")
            self.statusLabel.emit(self.tr("检查网络环境"))
            # 如果 5 秒内能访问到 Github 表示网络环境非常奈斯
            response = httpx.head(r"https://github.com", timeout=5)
            logger.info("网络环境非常奈斯")
            self.statusLabel.emit(self.tr("网络环境良好"))
            return response.status_code == 200
        except httpx.RequestError:
            # 引发错误返回 False
            return False

    def setUrl(self, url: QUrl) -> None:
        self.url = url

    def setPath(self, path: Path) -> None:
        self.path = path


class QQDownloader(QThread):
    """
    ## 执行下载 QQ 的任务
    """

    # 进度条模式切换 (进度模式: 0 \ 未知进度模式: 1 \ 文字模式: 2)
    progressBarToggle = Signal(int)
    # 下载进度
    downloadProgress = Signal(int)
    # 下载完成
    downloadFinish = Signal()
    # 引发错误导致结束
    errorFinsh = Signal()

    def __init__(self, url: QUrl, path: Path) -> None:
        """
        ## 初始化下载器
        """
        super().__init__()
        self.url: QUrl = url if url else None
        self.path: Path = Path(path) if path else None

    def run(self) -> None:
        """
        ## 运行下载 QQ 的任务
            - 自动下载 QQ
        """
        # 调整按钮样式为禁用
        self.progressBarToggle.emit(3)

        # 开始下载 QQ
        try:
            logger.info(f"{'-' * 10} 开始下载 QQ ~ {'-' * 10}")
            with httpx.stream("GET", self.url.url(), follow_redirects=True) as response:

                if (total_size := int(response.headers.get("content-length", 0))) == 0:
                    # 尝试获取文件大小
                    logger.error("无法获取文件大小, Content-Length为空或无法连接到下载链接")
                    self.progressBarToggle.emit(2)
                    self.errorFinsh.emit()
                    return

                self.progressBarToggle.emit(0)  # 设置进度条为 进度模式
                with open(f"{self.path / self.url.fileName()}", "wb") as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)  # 写入字节
                        self.downloadProgress.emit(int((file.tell() / total_size) * 100))  # 设置进度条

            # 下载完成
            self.downloadFinish.emit()  # 发生下载完成信号
            logger.info(f"{'-' * 10} 下载 QQ 结束 ~ {'-' * 10}")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"发送下载 QQ 请求时引发 HTTPStatusError, "
                f"响应码: {e.response.status_code}, 响应内容: {e.response.content}"
            )
            self.errorFinsh.emit()
        except (httpx.RequestError, FileNotFoundError, PermissionError, Exception) as e:
            logger.error(f"下载 QQ 时引发 {type(e).__name__}: {e}")
            self.errorFinsh.emit()

        finally:
            # 无论是否出错,都会重置
            self.downloadProgress.emit(0)  # 重置进度条进度
            self.progressBarToggle.emit(2)  # 设置进度条为 文字模式
            self.progressBarToggle.emit(4)  # 解除禁用

    def setUrl(self, url: QUrl) -> None:
        self.url = url

    def setPath(self, path: Path) -> None:
        self.path = path
