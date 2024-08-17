# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:59

from qgis.PyQt.QtCore import QRectF, Qt, QLineF
from qgis.PyQt.QtGui import QPen, QColor
from qgis.gui import QgsMapCanvasItem
import ctypes


def get_windows_scaling_factor():
    try:
        # 调用 Windows API 函数获取缩放比例
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        scaling_factor = user32.GetDpiForSystem()

        # 计算缩放比例
        return scaling_factor / 96.0

    except Exception as e:
        print("获取缩放比例时出错:", e)
        return None


# 调用函数获取 Windows 桌面的缩放比例
scaling_factor = get_windows_scaling_factor()
if scaling_factor is not None:
    print("Windows 桌面的缩放比例:", scaling_factor)
else:
    scaling_factor = 1


class SwipeMapItem(QgsMapCanvasItem):
    def __init__(self, mapCanvas):
        super(SwipeMapItem, self).__init__(mapCanvas)
        self.image = None
        self.line = None
        self.startPaint = False

        self.direction = -1
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def updateImageRect(self, x, y):
        w = self.boundingRect().width()*scaling_factor
        h = self.boundingRect().height()*scaling_factor
        if self.direction == -1:  # all
            self.x = 0
            self.y = 0
            self.w = w
            self.h = h
        elif self.direction == 0:  # 0:'⬇'
            self.x = 0
            self.y = 0
            self.w = w
            self.h = y*scaling_factor
            self.line = QLineF(0, y, w, y)
        elif self.direction == 1:  # 1:'⬆'
            self.x = 0
            self.y = y
            self.w = w
            self.h = h - y
            self.line = QLineF(0, y, w, y)
        elif self.direction == 2:  # 2:'➡'
            self.x = 0
            self.y = 0
            self.w = x*scaling_factor
            self.h = h
            self.line = QLineF(x, 0, x, h)
        else:  # 3:'⬅'
            self.x = x
            self.y = 0
            self.w = w - x
            self.h = h
            self.line = QLineF(x, 0, x, h)
        self.startPaint = True
        self.update()

    def paint(self, painter, *args):
        if self.startPaint is False:
            return

        pen = QPen(Qt.DashDotDotLine)
        pen.setColor(QColor(18, 150, 219))
        pen.setWidth(4)
        painter.setPen(pen)
        if self.line:
            painter.drawLine(self.line)

        image = self.image.copy(int(self.x*scaling_factor), int(
            self.y*scaling_factor), int(self.w), int(self.h))
        painter.drawImage(QRectF(self.x,
                          self.y, self.w/scaling_factor, self.h/scaling_factor), image)
