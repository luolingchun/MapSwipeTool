# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:58

import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton
from qgis.core import QgsProject
from qgis.gui import QgsMapToolPan

from .map_swipe_tool import MapSwipeTool

plugin_path = os.path.dirname(__file__)


class MapSwipePlugin:

    def __init__(self, iface):
        self.menu = self.title = "卷帘工具"
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.prevTool = self.canvas.mapTool()

        self.widget_action = None
        self.tool = None
        # 图标大小
        self.icon_size = self.iface.iconSize()
        self.height = self.icon_size.height() + 8

        # 图层变化信号
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(self.combobox_add_items)

    def initGui(self):
        self._create_widget()
        self.widget_action = self.iface.addToolBarWidget(self.widget)
        self.tool = MapSwipeTool(plugin_path, self.combobox, self.iface)

    def unload(self):
        if self.prevTool and self.prevTool != self.tool:
            self.canvas.setMapTool(self.prevTool)
        else:
            self.canvas.setMapTool(QgsMapToolPan(self.iface.mapCanvas()))
        self.iface.removeToolBarIcon(self.widget_action)
        del self.widget_action

    def run(self, is_checked):
        if is_checked and self.combobox.isHidden():
            self.prevTool = self.canvas.mapTool()
            self.combobox.show()
            self.combobox_add_items()
            self.canvas.setMapTool(self.tool)
        else:
            self.canvas.setMapTool(self.prevTool)
            self.combobox.hide()

    def _create_widget(self):
        icon = QIcon(os.path.join(plugin_path, 'icon.png'))
        # 新建widget
        self.widget = QWidget(self.iface.mainWindow())
        self.widget.setMinimumHeight(self.height)
        self.hlayout = QHBoxLayout(self.widget)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.pushbutton = QPushButton(icon, '', self.widget)
        self.pushbutton.setToolTip(self.title)
        self.pushbutton.setMinimumSize(self.height, self.height)
        self.pushbutton.setIconSize(self.icon_size)
        self.pushbutton.setCheckable(True)
        self.pushbutton.setFlat(True)
        self.combobox = QComboBox(self.widget)
        self.combobox.setMinimumHeight(self.icon_size.height())
        self.hlayout.addWidget(self.pushbutton)
        self.hlayout.addWidget(self.combobox)

        self.combobox.hide()
        self.combobox_add_items()
        self.pushbutton.clicked.connect(self.run)

    def combobox_add_items(self):
        self.combobox.clear()
        layers = QgsProject.instance().layerTreeRoot().layerOrder()
        self.combobox.addItems([layer.name() for layer in layers])
