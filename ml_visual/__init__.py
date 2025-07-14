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
from .execution_panel import ExecutionPanel
from .data_preview import DataPreviewPanel
from .backend_adapter import BackendAdapter, backend_adapter
from .command_manager import CommandManager
from .clipboard_manager import ClipboardManager, clipboard_manager
from .shortcut_manager import ShortcutManager
from .theme_manager import ThemeManager, theme_manager

__all__ = [
    'MLVisualizationUI',
    'MLComponent',
    'ConnectionPort',
    'ConnectionLine',
    'MLCanvas',
    'ComponentLibrary',
    'PropertyPanel',
    'StartupDialog',
    'ExecutionPanel',
    'DataPreviewPanel',
    'BackendAdapter',
    'backend_adapter',
    'CommandManager',
    'ClipboardManager',
    'clipboard_manager',
    'ShortcutManager',
    'ThemeManager',
    'theme_manager'
]
