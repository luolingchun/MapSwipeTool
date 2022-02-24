# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:59

from qgis.PyQt.QtCore import QRectF, Qt, QLineF
from qgis.PyQt.QtGui import QPen, QColor
from qgis.gui import QgsMapCanvasItem


class SwipeMapItem(QgsMapCanvasItem):
    def __init__(self, mapCanvas):
        super(SwipeMapItem, self).__init__(mapCanvas)
        self.image = None
        self.line = None
        self.startPaint = False

        self.direction = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def updateImageRect(self, x, y):
        w = self.boundingRect().width()
        h = self.boundingRect().height()
        if self.direction == 0:  # 0:'⬇'
            self.x = 0
            self.y = 0
            self.w = w
            self.h = y
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
            self.w = x
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
        painter.drawLine(self.line)

        image = self.image.copy(self.x, self.y, self.w, self.h)
        painter.drawImage(QRectF(self.x, self.y, self.w, self.h), image)
