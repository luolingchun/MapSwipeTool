# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QComboBox, QAction, QToolBar
from qgis.core import QgsProject
from qgis.gui import QgisInterface

from .mapTool import SwipeMapTool

here = os.path.dirname(__file__)
project = QgsProject.instance()


class Swipe:

    def __init__(self, iface):
        self.iface: QgisInterface = iface
        self.mapCanvas = self.iface.mapCanvas()

        self.toolBar: QToolBar = self.iface.addToolBar('Swipe Toolbar')
        self.toolBar.setToolTip("Swipe Toolbar")
        self.swipeAction = QAction(QIcon(os.path.join(here, 'icon.png')), 'Swipe Tool', self.toolBar)
        self.swipeAction.setCheckable(True)
        self.swipeAction.triggered.connect(self.swipeActionTriggered)
        self.layerCombobox = QComboBox()
        self.layerCombobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.layerCombobox.setFixedHeight(self.iface.iconSize().height())

        self.swipeTool = SwipeMapTool(self.layerCombobox, self.mapCanvas)

        # 图层变化信号
        project.layerTreeRoot().layerOrderChanged.connect(self.updateCombobox)
        project.layerTreeRoot().visibilityChanged.connect(self.updateCombobox)
        project.layerTreeRoot().nameChanged.connect(self.updateCombobox)
        # 地图工具变化
        self.mapCanvas.mapToolSet.connect(self.mapCanvasMapToolSet)
        # 初始化图层
        self.updateCombobox()

    def initGui(self):
        self.toolBar.addAction(self.swipeAction)
        self.toolBar.addWidget(self.layerCombobox)

    def unload(self):
        project.layerTreeRoot().layerOrderChanged.disconnect(self.updateCombobox)
        project.layerTreeRoot().visibilityChanged.disconnect(self.updateCombobox)
        project.layerTreeRoot().nameChanged.disconnect(self.updateCombobox)
        self.mapCanvas.mapToolSet.disconnect(self.mapCanvasMapToolSet)
        self.mapCanvas.unsetMapTool(self.swipeTool)

        del self.toolBar

    def swipeActionTriggered(self):
        if self.layerCombobox.count() < 2:
            self.swipeAction.setChecked(False)
            self.iface.messageBar().pushMessage("At least two layers are required.")
            return
        self.swipeAction.setChecked(True)
        if self.mapCanvas.mapTool() != self.swipeTool:
            self.mapCanvas.setMapTool(self.swipeTool)

    def updateCombobox(self):
        self.layerCombobox.clear()
        layers = project.layerTreeRoot().checkedLayers()
        for layer in layers:
            self.layerCombobox.addItem(layer.name(), layer.id())
        if self.layerCombobox.count() < 2:
            self.swipeAction.setChecked(False)
            self.mapCanvas.unsetMapTool(self.swipeTool)

    def mapCanvasMapToolSet(self, newTool, _):
        if newTool.__class__.__name__ != 'SwipeMapTool':
            self.swipeAction.setChecked(False)
