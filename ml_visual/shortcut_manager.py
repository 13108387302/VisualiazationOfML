#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷键管理器模块
管理应用程序的键盘快捷键
"""

from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence
from typing import Dict, Callable, Optional
from .config_manager import get_shortcuts_config


class ShortcutManager(QObject):
    """快捷键管理器"""
    
    # 信号定义
    shortcut_activated = pyqtSignal(str)  # 快捷键名称
    
    def __init__(self, parent_widget: QWidget):
        super().__init__()
        self.parent_widget = parent_widget
        self.shortcuts: Dict[str, QShortcut] = {}
        self.callbacks: Dict[str, Callable] = {}
        
        # 注册默认快捷键
        self.register_default_shortcuts()
        
    def register_shortcut(self, name: str, key_sequence: str, callback: Callable, 
                         description: str = "", context: Qt.ShortcutContext = Qt.WindowShortcut):
        """注册快捷键"""
        if name in self.shortcuts:
            # 移除已存在的快捷键
            self.unregister_shortcut(name)
            
        # 创建快捷键
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent_widget)
        shortcut.setContext(context)
        
        # 连接回调
        shortcut.activated.connect(lambda: self.on_shortcut_activated(name, callback))
        
        # 保存
        self.shortcuts[name] = shortcut
        self.callbacks[name] = callback
        
        # 设置描述
        if description:
            shortcut.setWhatsThis(description)
            
    def unregister_shortcut(self, name: str):
        """注销快捷键"""
        if name in self.shortcuts:
            shortcut = self.shortcuts[name]
            shortcut.setParent(None)
            del self.shortcuts[name]
            del self.callbacks[name]
            
    def on_shortcut_activated(self, name: str, callback: Callable):
        """快捷键激活处理"""
        try:
            callback()
            self.shortcut_activated.emit(name)
        except Exception as e:
            print(f"快捷键 {name} 执行失败: {e}")
            
    def register_default_shortcuts(self):
        """注册默认快捷键"""
        # 这些快捷键将在主窗口中设置具体的回调
        default_shortcuts = {
            # 文件操作
            'new_project': ('Ctrl+N', '新建项目'),
            'open_project': ('Ctrl+O', '打开项目'),
            'save_project': ('Ctrl+S', '保存项目'),
            'save_as': ('Ctrl+Shift+S', '另存为'),
            'close_project': ('Ctrl+W', '关闭项目'),
            'quit': ('Ctrl+Q', '退出应用'),
            
            # 编辑操作
            'undo': ('Ctrl+Z', '撤销'),
            'redo': ('Ctrl+Y', '重做'),
            'copy': ('Ctrl+C', '复制'),
            'cut': ('Ctrl+X', '剪切'),
            'paste': ('Ctrl+V', '粘贴'),
            'delete': ('Delete', '删除'),
            'select_all': ('Ctrl+A', '全选'),
            
            # 视图操作
            'zoom_in': ('Ctrl+=', '放大'),
            'zoom_out': ('Ctrl+-', '缩小'),
            'zoom_fit': ('Ctrl+0', '适应窗口'),
            'zoom_reset': ('Ctrl+1', '重置缩放'),
            
            # 运行操作
            'run': ('F5', '运行'),
            'stop': ('Shift+F5', '停止'),
            'debug': ('F9', '调试'),
            
            # 导航操作
            'find': ('Ctrl+F', '查找'),
            'goto': ('Ctrl+G', '跳转'),
            'next': ('F3', '下一个'),
            'previous': ('Shift+F3', '上一个'),
            
            # 窗口操作
            'toggle_fullscreen': ('F11', '切换全屏'),
            'toggle_component_library': ('Ctrl+1', '切换组件库'),
            'toggle_property_panel': ('Ctrl+2', '切换属性面板'),
            'toggle_execution_panel': ('Ctrl+3', '切换执行面板'),
            'toggle_data_preview': ('Ctrl+4', '切换数据预览'),
            
            # 组件操作
            'add_data_component': ('Ctrl+Shift+D', '添加数据组件'),
            'add_model_component': ('Ctrl+Shift+M', '添加模型组件'),
            'add_preprocess_component': ('Ctrl+Shift+P', '添加预处理组件'),
            'add_evaluate_component': ('Ctrl+Shift+E', '添加评估组件'),
            
            # 快速操作
            'quick_save': ('Ctrl+S', '快速保存'),
            'quick_run': ('Ctrl+R', '快速运行'),
            'quick_export': ('Ctrl+E', '快速导出'),
            
            # 帮助操作
            'help': ('F1', '帮助'),
            'about': ('Ctrl+Shift+A', '关于'),
            'shortcuts': ('Ctrl+Shift+K', '快捷键列表'),
        }
        
        # 注册占位符回调（将在主窗口中替换）
        for name, (key_sequence, description) in default_shortcuts.items():
            self.register_shortcut(name, key_sequence, lambda: None, description)
            
    def set_callback(self, name: str, callback: Callable):
        """设置快捷键回调"""
        if name in self.shortcuts:
            self.callbacks[name] = callback
            # 重新连接信号
            shortcut = self.shortcuts[name]
            shortcut.activated.disconnect()
            shortcut.activated.connect(lambda: self.on_shortcut_activated(name, callback))
            
    def get_shortcut_text(self, name: str) -> str:
        """获取快捷键文本"""
        if name in self.shortcuts:
            return self.shortcuts[name].key().toString()
        return ""
        
    def get_shortcut_description(self, name: str) -> str:
        """获取快捷键描述"""
        if name in self.shortcuts:
            return self.shortcuts[name].whatsThis()
        return ""
        
    def is_enabled(self, name: str) -> bool:
        """检查快捷键是否启用"""
        if name in self.shortcuts:
            return self.shortcuts[name].isEnabled()
        return False
        
    def set_enabled(self, name: str, enabled: bool):
        """设置快捷键启用状态"""
        if name in self.shortcuts:
            self.shortcuts[name].setEnabled(enabled)
            
    def get_all_shortcuts(self) -> Dict[str, tuple]:
        """获取所有快捷键信息"""
        result = {}
        for name, shortcut in self.shortcuts.items():
            result[name] = (
                shortcut.key().toString(),
                shortcut.whatsThis(),
                shortcut.isEnabled()
            )
        return result
        
    def export_shortcuts(self) -> str:
        """导出快捷键配置"""
        shortcuts_data = {}
        for name, shortcut in self.shortcuts.items():
            shortcuts_data[name] = {
                'key': shortcut.key().toString(),
                'description': shortcut.whatsThis(),
                'enabled': shortcut.isEnabled()
            }
        
        import json
        return json.dumps(shortcuts_data, indent=2, ensure_ascii=False)
        
    def import_shortcuts(self, shortcuts_json: str) -> bool:
        """导入快捷键配置"""
        try:
            import json
            shortcuts_data = json.loads(shortcuts_json)
            
            for name, config in shortcuts_data.items():
                if name in self.shortcuts:
                    # 更新现有快捷键
                    shortcut = self.shortcuts[name]
                    shortcut.setKey(QKeySequence(config['key']))
                    shortcut.setWhatsThis(config.get('description', ''))
                    shortcut.setEnabled(config.get('enabled', True))
                    
            return True
        except Exception as e:
            print(f"导入快捷键配置失败: {e}")
            return False
            
    def reset_to_defaults(self):
        """重置为默认快捷键"""
        # 清除所有快捷键
        for name in list(self.shortcuts.keys()):
            self.unregister_shortcut(name)
            
        # 重新注册默认快捷键
        self.register_default_shortcuts()
        
    def create_shortcuts_help_text(self) -> str:
        """创建快捷键帮助文本"""
        help_text = "快捷键列表:\n\n"
        
        categories = {
            '文件操作': ['new_project', 'open_project', 'save_project', 'save_as', 'close_project', 'quit'],
            '编辑操作': ['undo', 'redo', 'copy', 'cut', 'paste', 'delete', 'select_all'],
            '视图操作': ['zoom_in', 'zoom_out', 'zoom_fit', 'zoom_reset'],
            '运行操作': ['run', 'stop', 'debug'],
            '导航操作': ['find', 'goto', 'next', 'previous'],
            '窗口操作': ['toggle_fullscreen', 'toggle_component_library', 'toggle_property_panel', 
                       'toggle_execution_panel', 'toggle_data_preview'],
            '组件操作': ['add_data_component', 'add_model_component', 'add_preprocess_component', 
                       'add_evaluate_component'],
            '快速操作': ['quick_save', 'quick_run', 'quick_export'],
            '帮助操作': ['help', 'about', 'shortcuts']
        }
        
        for category, shortcut_names in categories.items():
            help_text += f"{category}:\n"
            for name in shortcut_names:
                if name in self.shortcuts:
                    key_text = self.get_shortcut_text(name)
                    description = self.get_shortcut_description(name)
                    help_text += f"  {key_text:<20} {description}\n"
            help_text += "\n"
            
        return help_text
        
    def find_conflicts(self) -> Dict[str, list]:
        """查找快捷键冲突"""
        conflicts = {}
        key_to_names = {}
        
        for name, shortcut in self.shortcuts.items():
            key_text = shortcut.key().toString()
            if key_text:
                if key_text not in key_to_names:
                    key_to_names[key_text] = []
                key_to_names[key_text].append(name)
                
        # 找出冲突
        for key_text, names in key_to_names.items():
            if len(names) > 1:
                conflicts[key_text] = names
                
        return conflicts
