# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QCursor, QPixmap
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob
from qgis.gui import QgsMapTool

from .mapItem import SwipeMapItem

here = os.path.dirname(__file__)
project = QgsProject.instance()


class SwipeMapTool(QgsMapTool):
    def __init__(self, layerCombobox, mapCanvas):
        super(SwipeMapTool, self).__init__(mapCanvas)
        self.layerCombobox = layerCombobox
        self.mapCanvas = mapCanvas
        self.mapItem = SwipeMapItem(self.mapCanvas)
        self.startSwipe = False
        self.controlDown = False
        self.layers = []

        self.cursorSV = QCursor(QPixmap(os.path.join(here, 'images/split_v.png')))
        self.cursorSH = QCursor(QPixmap(os.path.join(here, 'images/split_h.png')))
        self.cursorUp = QCursor(QPixmap(os.path.join(here, 'images/up.png')))
        self.cursorDown = QCursor(QPixmap(os.path.join(here, 'images/down.png')))
        self.cursorLeft = QCursor(QPixmap(os.path.join(here, 'images/left.png')))
        self.cursorRight = QCursor(QPixmap(os.path.join(here, 'images/right.png')))
        self.cursorBox = QCursor(QPixmap(os.path.join(here, 'images/box.png')))

    def activate(self):
        self.connect()
        self.startSwipe = False
        self.setLayersSwipe()

    def connect(self, is_connect=True):
        if is_connect:
            self.mapCanvas.mapCanvasRefreshed.connect(self.setMapLayers)
            self.layerCombobox.currentIndexChanged.connect(self.setLayersSwipe)
        else:
            self.mapCanvas.mapCanvasRefreshed.disconnect(self.setMapLayers)
            self.layerCombobox.currentIndexChanged.disconnect(self.setLayersSwipe)

    def setLayersSwipe(self, ):
        self.layers = project.layerTreeRoot().checkedLayers()
        currentLayer = project.mapLayer(self.layerCombobox.currentData())
        if currentLayer in self.layers:
            self.layers.remove(currentLayer)
        self.setMapLayers()

    def setMapLayers(self):
        def finished():
            self.mapItem.image = job.renderedImage()
            self.mapItem.setRect(self.mapCanvas.extent())

        if len(self.layers) == 0:
            return

        settings = QgsMapSettings(self.mapCanvas.mapSettings())
        settings.setLayers(self.layers)

        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.finished.connect(finished)
        job.waitForFinished()

    def keyPressEvent(self, e):
        if e.modifiers() == Qt.ControlModifier:
            self.mapCanvas.setCursor(self.cursorBox)
            self.controlDown = True

    def keyReleaseEvent(self, e) -> None:
        if not e.isAutoRepeat():
            self.controlDown = False
            pos = self.cursorBox.pos()
            # 触发鼠标移动事件
            self.cursorBox.setPos(pos.x() + 1, pos.y() + 1)

    def canvasPressEvent(self, e):
        self.startSwipe = True
        w, h = self.mapCanvas.width(), self.mapCanvas.height()
        if not self.controlDown:
            if 0.25 * w < e.x() < 0.75 * w and e.y() < 0.5 * h:
                self.mapItem.direction = 0  # '⬇'
                self.mapCanvas.setCursor(self.cursorSH)
            elif 0.25 * w < e.x() < 0.75 * w and e.y() > 0.5 * h:
                self.mapItem.direction = 1  # '⬆'
                self.mapCanvas.setCursor(self.cursorSH)
            elif e.x() < 0.25 * w:
                self.mapItem.direction = 2  # '➡'
                self.mapCanvas.setCursor(self.cursorSV)
            else:  # elif e.x() > 0.75 * w:
                self.mapItem.direction = 3  # '⬅'
                self.mapCanvas.setCursor(self.cursorSV)
            self.mapItem.updateImageRect(e.x(), e.y())
        else:
            self.mapItem.direction = -1  # all
            self.mapItem.updateImageRect(w, h)

    def canvasMoveEvent(self, e):
        if self.controlDown:
            return
        if self.startSwipe:
            self.mapItem.updateImageRect(e.x(), e.y())
        else:
            # 设置当前cursor
            w, h = self.mapCanvas.width(), self.mapCanvas.height()
            if e.x() < 0.25 * w:
                self.mapCanvas.setCursor(self.cursorRight)
            if e.x() > 0.75 * w:
                self.mapCanvas.setCursor(self.cursorLeft)
            if 0.25 * w < e.x() < 0.75 * w and e.y() < 0.5 * h:
                self.mapCanvas.setCursor(self.cursorDown)
            if 0.25 * w < e.x() < 0.75 * w and e.y() > 0.5 * h:
                self.mapCanvas.setCursor(self.cursorUp)

    def canvasReleaseEvent(self, e):
        self.startSwipe = False
        self.canvasMoveEvent(e)
        # 鼠标释放后重新绘制
        self.mapItem.startPaint = False
        self.mapItem.update()

    def deactivate(self):
        self.connect(False)
        self.deactivated.emit()
