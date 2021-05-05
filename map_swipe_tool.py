# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QCursor, QPixmap
from qgis.gui import QgsMapTool
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob
from .swipe_map import SwipeMap

here = os.path.dirname(__file__)
project = QgsProject.instance()


class MapSwipeTool(QgsMapTool):
    def __init__(self, height, layer_combobox, map_canvas):
        super(MapSwipeTool, self).__init__(map_canvas)
        self.layer_combobox = layer_combobox
        self.map_canvas = map_canvas
        self.swipe = SwipeMap(self.map_canvas)
        self.hasSwipe = False
        self.start_point = QPoint()

        self.cursorSV = QCursor(QPixmap(os.path.join(here, 'images/split_v.png')).scaledToHeight(height))
        self.cursorSH = QCursor(QPixmap(os.path.join(here, 'images/split_h.png')).scaledToHeight(height))
        self.cursorUP = QCursor(QPixmap(os.path.join(here, 'images/up.png')).scaledToHeight(height))
        self.cursorDOWN = QCursor(QPixmap(os.path.join(here, 'images/down.png')).scaledToHeight(height))
        self.cursorLEFT = QCursor(QPixmap(os.path.join(here, 'images/left.png')).scaledToHeight(height))
        self.cursorRIGHT = QCursor(QPixmap(os.path.join(here, 'images/right.png')).scaledToHeight(height))

    def activate(self):
        self.map_canvas.setCursor(QCursor(Qt.CrossCursor))
        self._connect()
        self.hasSwipe = False
        self.setLayersSwipe()

    def canvasPressEvent(self, e):
        self.hasSwipe = True
        direction = None
        w, h = self.map_canvas.width(), self.map_canvas.height()
        if 0.25 * w < e.x() < 0.75 * w and e.y() < 0.5 * h:
            direction = 0  # '⬇'
            self.swipe.isVertical = False
        if 0.25 * w < e.x() < 0.75 * w and e.y() > 0.5 * h:
            direction = 1  # '⬆'
            self.swipe.isVertical = False
        if e.x() < 0.25 * w:
            direction = 2  # '➡'
            self.swipe.isVertical = True
        if e.x() > 0.75 * w:
            direction = 3  # '⬅'
            self.swipe.isVertical = True

        self.swipe.set_direction(direction)
        self.map_canvas.setCursor(self.cursorSV if self.swipe.isVertical else self.cursorSH)
        self.swipe.set_img_extent(e.x(), e.y())

    def canvasReleaseEvent(self, e):
        self.hasSwipe = False
        self.canvasMoveEvent(e)
        # 鼠标释放后，移除绘制的线
        self.swipe.set_img_extent(-9999, -9999)

    def canvasMoveEvent(self, e):
        if self.hasSwipe:
            self.swipe.set_img_extent(e.x(), e.y())
        else:
            # 设置当前cursor
            w, h = self.map_canvas.width(), self.map_canvas.height()
            if e.x() < 0.25 * w:
                self.canvas().setCursor(self.cursorRIGHT)
            if e.x() > 0.75 * w:
                self.canvas().setCursor(self.cursorLEFT)
            if 0.25 * w < e.x() < 0.75 * w and e.y() < 0.5 * h:
                self.canvas().setCursor(self.cursorDOWN)
            if 0.25 * w < e.x() < 0.75 * w and e.y() > 0.5 * h:
                self.canvas().setCursor(self.cursorUP)

    def _connect(self, is_connect=True):
        signal_slot = (
            {'signal': self.map_canvas.mapCanvasRefreshed, 'slot': self.setMap},
            {'signal': self.layer_combobox.currentIndexChanged, 'slot': self.setLayersSwipe},
            {'signal': project.removeAll, 'slot': self.disable}
        )
        if is_connect:
            for item in signal_slot:
                item['signal'].connect(item['slot'])
        else:
            for item in signal_slot:
                item['signal'].disconnect(item['slot'])

    def setLayersSwipe(self, ):
        current_layer = project.mapLayersByName(self.layer_combobox.currentText())
        if len(current_layer) == 0:
            return
        layers = project.layerTreeRoot().checkedLayers()
        layer_list = []
        for layer in layers:
            if layer.id() == current_layer[0].id():
                continue
            layer_list.append(layer)
        self.swipe.clear()
        self.swipe.setLayersId(layer_list)
        self.setMap()

    def disable(self):
        self.swipe.clear()
        self.hasSwipe = False

    def deactivate(self):
        self.deactivated.emit()
        self.swipe.clear()
        self._connect(False)

    def setMap(self):
        def finished():
            self.swipe.setContent(job.renderedImage(), self.map_canvas.extent())

        if len(self.swipe.layers) == 0:
            return

        settings = QgsMapSettings(self.map_canvas.mapSettings())
        settings.setLayers(self.swipe.layers)

        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.finished.connect(finished)
        job.waitForFinished()
