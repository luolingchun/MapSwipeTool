# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:59

from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPen, QColor
from qgis.gui import QgsMapCanvasItem


class SwipeMap(QgsMapCanvasItem):
    def __init__(self, canvas):
        super(SwipeMap, self).__init__(canvas)
        self.copy_image = None
        self.length = 0
        self.isVertical = True
        self.layers = []
        self.is_paint = False

        self.direction = 0
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.x = self.y = 0

    def setContent(self, image, rect):
        self.copy_image = image
        self.setRect(rect)

    def clear(self):
        del self.layers[:]
        self.is_paint = False

    def setLayersId(self, layers):
        del self.layers[:]
        for item in layers:
            self.layers.append(item)

    def set_direction(self, direction):
        # 0:'⬇', 1:'⬆', 2:'➡', 3:'⬅'
        if direction == 0:
            self.direction = 0
        elif direction == 1:
            self.direction = 1
        elif direction == 2:
            self.direction = 2
        else:
            self.direction = 3
        self.start_x, self.start_y, self.end_x, self.end_y = 0, 0, self.boundingRect().width(), self.boundingRect().height()

    def set_img_extent(self, x, y):
        self.x = x
        self.y = y
        if self.direction == 0:  # 0:'⬇'
            self.end_y = y
        elif self.direction == 1:  # 1:'⬆'
            self.start_y = y
        elif self.direction == 2:  # 2:'➡'
            self.end_x = x
        else:  # 3:'⬅'
            self.start_x = x
        self.is_paint = True
        self.update()

    def paint(self, painter, *args):
        if len(self.layers) == 0 or self.is_paint is False:
            return

        w = self.boundingRect().width()
        h = self.boundingRect().height()

        pen = QPen(Qt.DashDotDotLine)
        pen.setColor(QColor(18, 150, 219))
        pen.setWidth(4)

        if self.isVertical:
            painter.setPen(pen)
            painter.drawLine(QPointF(self.x, 0), QPointF(self.x, h))
        else:
            painter.setPen(pen)
            painter.drawLine(QPointF(0, self.y), QPointF(w, self.y))

        image = self.copy_image.copy(self.start_x, self.start_y, self.end_x, self.end_y)
        painter.drawImage(QRectF(self.start_x, self.start_y, self.end_x, self.end_y), image)
