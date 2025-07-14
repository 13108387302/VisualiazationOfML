#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理器模块
管理应用程序的主题和样式
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from typing import Dict, Any
import json
import os


class ThemeManager(QObject):
    """主题管理器"""
    
    # 信号定义
    theme_changed = pyqtSignal(str)  # 主题名称
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.themes = self.load_default_themes()
        self.custom_styles = {}
        
    def load_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """加载默认主题"""
        return {
            "light": {
                "name": "浅色主题",
                "description": "经典的浅色主题",
                "colors": {
                    "background": "#ffffff",
                    "surface": "#f5f5f5",
                    "primary": "#0078d4",
                    "secondary": "#6c757d",
                    "accent": "#17a2b8",
                    "text": "#212529",
                    "text_secondary": "#6c757d",
                    "border": "#dee2e6",
                    "hover": "#e9ecef",
                    "selected": "#cce7ff",
                    "error": "#dc3545",
                    "warning": "#ffc107",
                    "success": "#28a745",
                    "info": "#17a2b8"
                },
                "styles": {
                    "window": """
                        QMainWindow {
                            background-color: #ffffff;
                            color: #212529;
                        }
                    """,
                    "menu": """
                        QMenuBar {
                            background-color: #f8f9fa;
                            border-bottom: 1px solid #dee2e6;
                        }
                        QMenuBar::item {
                            padding: 4px 8px;
                            background-color: transparent;
                        }
                        QMenuBar::item:selected {
                            background-color: #e9ecef;
                        }
                        QMenu {
                            background-color: #ffffff;
                            border: 1px solid #dee2e6;
                        }
                        QMenu::item {
                            padding: 4px 20px;
                        }
                        QMenu::item:selected {
                            background-color: #e9ecef;
                        }
                    """,
                    "toolbar": """
                        QToolBar {
                            background-color: #f8f9fa;
                            border: 1px solid #dee2e6;
                            spacing: 2px;
                        }
                        QToolButton {
                            padding: 4px;
                            border: none;
                            border-radius: 3px;
                        }
                        QToolButton:hover {
                            background-color: #e9ecef;
                        }
                        QToolButton:pressed {
                            background-color: #dee2e6;
                        }
                    """,
                    "button": """
                        QPushButton {
                            background-color: #0078d4;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #106ebe;
                        }
                        QPushButton:pressed {
                            background-color: #005a9e;
                        }
                        QPushButton:disabled {
                            background-color: #6c757d;
                        }
                    """,
                    "input": """
                        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                            background-color: #ffffff;
                            border: 1px solid #ced4da;
                            border-radius: 4px;
                            padding: 4px 8px;
                        }
                        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                            border-color: #0078d4;
                            outline: none;
                        }
                    """,
                    "list": """
                        QListWidget, QTreeWidget, QTableWidget {
                            background-color: #ffffff;
                            border: 1px solid #dee2e6;
                            alternate-background-color: #f8f9fa;
                        }
                        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
                            background-color: #cce7ff;
                        }
                    """
                }
            },
            "dark": {
                "name": "深色主题",
                "description": "现代的深色主题",
                "colors": {
                    "background": "#2b2b2b",
                    "surface": "#3c3c3c",
                    "primary": "#0078d4",
                    "secondary": "#6c757d",
                    "accent": "#17a2b8",
                    "text": "#ffffff",
                    "text_secondary": "#adb5bd",
                    "border": "#495057",
                    "hover": "#495057",
                    "selected": "#0078d4",
                    "error": "#dc3545",
                    "warning": "#ffc107",
                    "success": "#28a745",
                    "info": "#17a2b8"
                },
                "styles": {
                    "window": """
                        QMainWindow {
                            background-color: #2b2b2b;
                            color: #ffffff;
                        }
                    """,
                    "menu": """
                        QMenuBar {
                            background-color: #3c3c3c;
                            border-bottom: 1px solid #495057;
                            color: #ffffff;
                        }
                        QMenuBar::item {
                            padding: 4px 8px;
                            background-color: transparent;
                        }
                        QMenuBar::item:selected {
                            background-color: #495057;
                        }
                        QMenu {
                            background-color: #3c3c3c;
                            border: 1px solid #495057;
                            color: #ffffff;
                        }
                        QMenu::item {
                            padding: 4px 20px;
                        }
                        QMenu::item:selected {
                            background-color: #495057;
                        }
                    """,
                    "toolbar": """
                        QToolBar {
                            background-color: #3c3c3c;
                            border: 1px solid #495057;
                            spacing: 2px;
                        }
                        QToolButton {
                            padding: 4px;
                            border: none;
                            border-radius: 3px;
                            color: #ffffff;
                        }
                        QToolButton:hover {
                            background-color: #495057;
                        }
                        QToolButton:pressed {
                            background-color: #6c757d;
                        }
                    """,
                    "button": """
                        QPushButton {
                            background-color: #0078d4;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #106ebe;
                        }
                        QPushButton:pressed {
                            background-color: #005a9e;
                        }
                        QPushButton:disabled {
                            background-color: #6c757d;
                        }
                    """,
                    "input": """
                        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                            background-color: #495057;
                            border: 1px solid #6c757d;
                            border-radius: 4px;
                            padding: 4px 8px;
                            color: #ffffff;
                        }
                        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                            border-color: #0078d4;
                            outline: none;
                        }
                    """,
                    "list": """
                        QListWidget, QTreeWidget, QTableWidget {
                            background-color: #3c3c3c;
                            border: 1px solid #495057;
                            alternate-background-color: #495057;
                            color: #ffffff;
                        }
                        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
                            background-color: #0078d4;
                        }
                    """
                }
            }
        }
        
    def apply_theme(self, theme_name: str):
        """应用主题（优化性能）"""
        if theme_name not in self.themes:
            print(f"主题 '{theme_name}' 不存在")
            return False

        # 如果是当前主题，无需重复应用
        if theme_name == self.current_theme:
            return True

        theme = self.themes[theme_name]
        app = QApplication.instance()

        if not app:
            print("没有找到QApplication实例")
            return False

        # 缓存样式表以避免重复构建
        cache_key = f"stylesheet_{theme_name}"
        if not hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache = {}

        if cache_key not in self._stylesheet_cache:
            # 构建完整样式表
            stylesheet = ""
            for style_type, style_content in theme["styles"].items():
                stylesheet += style_content + "\n"
            self._stylesheet_cache[cache_key] = stylesheet

        # 应用缓存的样式表
        app.setStyleSheet(self._stylesheet_cache[cache_key])

        # 更新当前主题
        self.current_theme = theme_name

        # 发射信号
        self.theme_changed.emit(theme_name)

        return True
        
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self.current_theme
        
    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """获取主题信息"""
        return self.themes.get(theme_name, {})
        
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {name: theme.get("name", name) for name, theme in self.themes.items()}
        
    def get_theme_color(self, color_name: str, theme_name: str = None) -> str:
        """获取主题颜色"""
        if theme_name is None:
            theme_name = self.current_theme
            
        theme = self.themes.get(theme_name, {})
        colors = theme.get("colors", {})
        return colors.get(color_name, "#000000")
        
    def add_custom_theme(self, theme_name: str, theme_data: Dict[str, Any]):
        """添加自定义主题"""
        self.themes[theme_name] = theme_data
        
    def remove_theme(self, theme_name: str) -> bool:
        """移除主题"""
        if theme_name in ["light", "dark"]:
            print("不能移除默认主题")
            return False
            
        if theme_name in self.themes:
            del self.themes[theme_name]
            if self.current_theme == theme_name:
                self.apply_theme("light")
            return True
            
        return False
        
    def export_theme(self, theme_name: str) -> str:
        """导出主题为JSON"""
        if theme_name not in self.themes:
            return ""
            
        return json.dumps(self.themes[theme_name], indent=2, ensure_ascii=False)
        
    def import_theme(self, theme_name: str, theme_json: str) -> bool:
        """从JSON导入主题"""
        try:
            theme_data = json.loads(theme_json)
            self.add_custom_theme(theme_name, theme_data)
            return True
        except json.JSONDecodeError:
            return False
            
    def save_themes_to_file(self, file_path: str):
        """保存主题到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存主题失败: {e}")
            
    def load_themes_from_file(self, file_path: str):
        """从文件加载主题"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    themes = json.load(f)
                    self.themes.update(themes)
        except Exception as e:
            print(f"加载主题失败: {e}")


# 全局主题管理器实例
theme_manager = ThemeManager()
