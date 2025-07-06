#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习可视化工具包
"""

__version__ = "1.0.0"
__author__ = "ML Visual Team"
__description__ = "基于PyQt5的机器学习可视化界面工具"

from .main_window import MLVisualizationUI
from .components import MLComponent, ConnectionPort, ConnectionLine
from .canvas import MLCanvas
from .component_library import ComponentLibrary
from .property_panel import PropertyPanel
from .startup_dialog import StartupDialog

__all__ = [
    'MLVisualizationUI',
    'MLComponent',
    'ConnectionPort',
    'ConnectionLine',
    'MLCanvas',
    'ComponentLibrary',
    'PropertyPanel',
    'StartupDialog'
]
