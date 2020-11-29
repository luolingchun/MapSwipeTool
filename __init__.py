# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/3/10 14:54


def classFactory(iface):
    from .map_swipe_plugin import MapSwipePlugin
    return MapSwipePlugin(iface)
