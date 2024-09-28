# -*- coding: utf-8 -*-
# 标准库导入
import winreg
from abc import ABC
from pathlib import Path

# 第三方库导入
from creart import add_creator, exists_module
from loguru import logger
from creart.creator import AbstractCreator, CreateTargetInfo


class PathFunc:

    def __init__(self):
        """
        ## 初始化
        """
        self.qq_path = None
        self.base_path = Path.cwd()
        self.config_dir_path = self.base_path / "config"
        self.config_path = self.config_dir_path / "config.json"
        self.bot_config_path = self.config_dir_path / "bot.json"
        self.tmp_path = self.base_path / "tmp"
        self.napcat_path = self.base_path / "NapCat"

        self.pathValidator()

    def pathValidator(self) -> None:
        """
        ## 验证一系列路径
        """
        logger.info(f"{'-' * 10}开始验证路径{'-' * 10}")

        if not self.config_dir_path.exists():
            self.config_dir_path.mkdir(parents=True, exist_ok=True)
            logger.info("Config Path 路径不存在, 已创建")
        elif not self.config_dir_path.is_dir():
            self.config_dir_path.mkdir(parents=True, exist_ok=True)
            logger.warning("存在一个名为 config 的文件, 请检查")
        logger.info("Config Path 验证完成")

        if not self.tmp_path.exists():
            self.tmp_path.mkdir(parents=True, exist_ok=True)
            logger.info("Tmp Path 路径不存在, 已创建")
        elif not self.tmp_path.is_dir():
            self.tmp_path.mkdir(parents=True, exist_ok=True)
            logger.warning("存在一个名为 tmp 的文件, 请检查")
        logger.info("Tmp Path 验证完成")

        if not self.napcat_path.exists():
            self.napcat_path.mkdir(parents=True, exist_ok=True)
            logger.info("NapCat Path 路径不存在, 已创建")
        elif not self.napcat_path.is_dir():
            self.napcat_path.mkdir(parents=True, exist_ok=True)
            logger.warning("存在一个名为 NapCat 的文件, 请检查")
        logger.info("NapCat Path 验证完成")

        logger.info(f"{'-' * 10}路径验证完成{'-' * 10}")

    @staticmethod
    def getQQPath() -> Path | None:
        """
        获取QQ路径
        """
        try:
            key = winreg.OpenKey(
                key=winreg.HKEY_LOCAL_MACHINE,
                sub_key=r"SOFTWARE\WOW6432Node\Tencent\QQNT",
            )
            return Path(winreg.QueryValueEx(key, "Install")[0])
        except FileNotFoundError:
            return None

    def getNapCatPath(self) -> Path:
        """
        ## 获取 NapCat 路径
        """
        return self.napcat_path


class PathFuncClassCreator(AbstractCreator, ABC):
    # 定义类方法targets，该方法返回一个元组，元组中包含了一个CreateTargetInfo对象，
    # 该对象描述了创建目标的相关信息，包括应用程序名称和类名。
    targets = (CreateTargetInfo("src.Core.Utils.PathFunc", "PathFunc"),)

    # 静态方法available()，用于检查模块"PathFunc"是否存在，返回值为布尔型。
    @staticmethod
    def available() -> bool:
        return exists_module("src.Core.Utils.PathFunc")

    # 静态方法create()，用于创建PathFunc类的实例，返回值为PathFunc对象。
    @staticmethod
    def create(create_type: list[PathFunc]) -> PathFunc:
        return PathFunc()


add_creator(PathFuncClassCreator)
