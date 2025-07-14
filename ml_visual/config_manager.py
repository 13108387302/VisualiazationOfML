"""
配置管理模块
统一管理应用程序的配置和设置
"""

import json
import os
from PyQt5.QtCore import QSettings, QStandardPaths
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器 - 统一管理应用程序配置"""
    
    def __init__(self):
        self.settings = QSettings('MLVisual', 'Application')
        self.config_dir = self._get_config_dir()
        self.ensure_config_dir()

        # 加载配置文件
        self.config_data = self.load_config_file()

        # 合并用户设置
        self.merge_user_settings()

        # 性能优化：缓存常用配置节
        self._section_cache = {}
        self._cache_common_sections()

    def _cache_common_sections(self):
        """缓存常用的配置节以提高性能"""
        common_sections = ['ui', 'canvas', 'components', 'performance']
        for section in common_sections:
            if section in self.config_data:
                self._section_cache[section] = self.config_data[section]
        
    def _get_config_dir(self):
        """获取配置目录"""
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return os.path.join(app_data, 'MLVisual')
        
    def ensure_config_dir(self):
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)

    def load_config_file(self):
        """加载配置文件"""
        # 首先尝试加载项目目录下的配置文件
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")

        # 如果加载失败，返回空配置
        return {}

    def merge_user_settings(self):
        """合并用户设置"""
        # 用户设置覆盖默认配置
        for key in self.settings.allKeys():
            self.set_nested_value(self.config_data, key, self.settings.value(key))

    def set_nested_value(self, data, key, value):
        """设置嵌套值"""
        keys = key.split('.')
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 支持点号分隔的嵌套键
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
        
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.settings.setValue(key, value)
        
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return {
            'theme': self.get('ui.theme'),
            'language': self.get('ui.language'),
            'window_size': self.get('ui.window_size'),
            'window_maximized': self.get('ui.window_maximized'),
            'panel_sizes': self.get('ui.panel_sizes')
        }
        
    def set_ui_config(self, config: Dict[str, Any]):
        """设置UI配置"""
        for key, value in config.items():
            self.set(f'ui.{key}', value)
            
    def get_canvas_config(self) -> Dict[str, Any]:
        """获取画布配置"""
        return {
            'grid_enabled': self.get('canvas.grid_enabled'),
            'grid_size': self.get('canvas.grid_size'),
            'snap_to_grid': self.get('canvas.snap_to_grid'),
            'auto_save_interval': self.get('canvas.auto_save_interval'),
            'max_undo_steps': self.get('canvas.max_undo_steps')
        }
        
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return {
            'enable_lod': self.get('performance.enable_lod'),
            'enable_caching': self.get('performance.enable_caching'),
            'max_components': self.get('performance.max_components'),
            'update_interval': self.get('performance.update_interval')
        }
        
    def get_recent_projects(self) -> list:
        """获取最近项目列表"""
        return self.settings.value('recent_projects', [])
        
    def add_recent_project(self, project_path: str):
        """添加最近项目"""
        recent = self.get_recent_projects()
        
        # 移除重复项
        if project_path in recent:
            recent.remove(project_path)
            
        # 添加到开头
        recent.insert(0, project_path)
        
        # 限制数量
        max_count = self.get('recent_projects.max_count')
        recent = recent[:max_count]
        
        self.settings.setValue('recent_projects', recent)
        
    def remove_recent_project(self, project_path: str):
        """移除最近项目"""
        recent = self.get_recent_projects()
        if project_path in recent:
            recent.remove(project_path)
            self.settings.setValue('recent_projects', recent)
            
    def clear_recent_projects(self):
        """清空最近项目"""
        self.settings.setValue('recent_projects', [])
        
    def export_config(self, file_path: str):
        """导出配置到文件"""
        config = {}
        for key in self.settings.allKeys():
            config[key] = self.settings.value(key)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
    def import_config(self, file_path: str):
        """从文件导入配置"""
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for key, value in config.items():
                self.settings.setValue(key, value)
                
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
            
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.settings.clear()
        
    def get_config_file_path(self, filename: str) -> str:
        """获取配置文件路径"""
        return os.path.join(self.config_dir, filename)
        
    def save_window_state(self, window):
        """保存窗口状态"""
        self.set('ui.window_size', (window.width(), window.height()))
        self.set('ui.window_maximized', window.isMaximized())
        if hasattr(window, 'saveGeometry'):
            geometry = window.saveGeometry()
            self.settings.setValue('window_geometry', geometry)
            
    def restore_window_state(self, window):
        """恢复窗口状态"""
        # 恢复几何状态
        geometry = self.settings.value('window_geometry')
        if geometry:
            window.restoreGeometry(geometry)
        else:
            # 使用默认大小
            size = self.get('ui.window_size')
            window.resize(*size)
            
        # 恢复最大化状态
        if self.get('ui.window_maximized'):
            window.showMaximized()


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """获取配置的便捷函数"""
    return config_manager.get(key, default)


def set_config(key: str, value: Any):
    """设置配置的便捷函数"""
    config_manager.set(key, value)


def get_ui_config() -> Dict[str, Any]:
    """获取UI配置的便捷函数"""
    return config_manager.get_ui_config()


def get_canvas_config() -> Dict[str, Any]:
    """获取画布配置的便捷函数"""
    return config_manager.get_canvas_config()


def get_performance_config() -> Dict[str, Any]:
    """获取性能配置的便捷函数"""
    return config_manager.get_performance_config()


def get_component_config() -> Dict[str, Any]:
    """获取组件配置的便捷函数"""
    return config_manager.get('components', {})





def get_shortcuts_config() -> Dict[str, Any]:
    """获取快捷键配置的便捷函数"""
    return config_manager.get('shortcuts', {})


def get_colors() -> Dict[str, str]:
    """获取颜色配置的便捷函数"""
    return config_manager.get('ui.colors', {})
