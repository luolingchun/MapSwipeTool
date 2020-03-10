# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:54

from .map_swipe_plugin import MapSwipePlugin


def classFactory(iface):
    return MapSwipePlugin(iface)
