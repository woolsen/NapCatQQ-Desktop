# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget


class HomePage(QWidget):
    """主页"""

    def __init__(self, parent=None) -> None:
        """构造函数"""
        super().__init__(parent)

        # 设置属性
        self.setObjectName("HomePage")


__all__ = ["HomePage"]
