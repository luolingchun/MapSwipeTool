# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QComboBox, QAction, QToolBar
from qgis.core import QgsProject
from qgis.gui import QgsMapToolPan, QgisInterface

from .map_swipe_tool import MapSwipeTool

here = os.path.dirname(__file__)
project = QgsProject.instance()


class MapSwipePlugin:

    def __init__(self, iface):
        self.iface: QgisInterface = iface
        self.map_canvas = self.iface.mapCanvas()
        self.prevTool = self.map_canvas.mapTool()

        self.tool_bar: QToolBar = self.iface.addToolBar('Swipe Toolbar')
        self.tool_bar.setToolTip("Swipe Toolbar")
        self.swipe_action = QAction(QIcon(os.path.join(here, 'icon.png')), 'swipe tool', self.tool_bar)
        self.swipe_action.setCheckable(True)
        self.swipe_action.triggered.connect(self.run)
        self.layer_combobox = QComboBox(self.tool_bar)
        self.layer_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.tool_bar.setContentsMargins(0, 0, 0, 0)
        height = self.iface.iconSize().height() + 8
        self.layer_combobox.setFixedHeight(height)

        self.swipe_tool = MapSwipeTool(height, self.layer_combobox, self.map_canvas)

        # 图层变化信号
        project.layerTreeRoot().layerOrderChanged.connect(lambda: self.combobox_add_items())
        project.layerTreeRoot().visibilityChanged.connect(self.combobox_add_items)
        project.layerTreeRoot().nameChanged.connect(self.combobox_add_items)

        # 初始化图层
        self.combobox_add_items()

    def initGui(self):
        self.tool_bar.addAction(self.swipe_action)
        self.tool_bar.addWidget(self.layer_combobox)

    def unload(self):
        if self.prevTool and self.prevTool != self.swipe_tool:
            self.map_canvas.setMapTool(self.prevTool)
        else:
            self.map_canvas.setMapTool(QgsMapToolPan(self.iface.mapCanvas()))

        del self.tool_bar

    def run(self, is_checked):
        if is_checked:
            self.prevTool = self.map_canvas.mapTool()
            self.map_canvas.setMapTool(self.swipe_tool)
        else:
            self.map_canvas.setMapTool(self.prevTool)

    def combobox_add_items(self):
        self.layer_combobox.clear()
        layers = project.layerTreeRoot().checkedLayers()
        names = [layer.name() for layer in layers]
        self.layer_combobox.addItems(names)
