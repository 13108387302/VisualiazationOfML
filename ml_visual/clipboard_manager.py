#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪贴板管理器模块
实现复制/粘贴功能
"""

import json
import copy
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QPointF


class ClipboardManager(QObject):
    """剪贴板管理器"""
    
    # 信号定义
    clipboard_changed = pyqtSignal(bool)  # 是否有内容
    
    def __init__(self):
        super().__init__()
        self.clipboard_data = None
        self.clipboard_type = None
        
    def copy_components(self, components: List, connections: List = None):
        """复制组件"""
        if not components:
            return
            
        # 收集组件数据
        components_data = []
        component_ids = set()
        
        for component in components:
            # 确保组件有唯一ID
            if not hasattr(component, 'unique_id'):
                import uuid
                component.unique_id = str(uuid.uuid4())

            component_data = {
                'id': component.unique_id,
                'type': component.component_type,
                'name': component.name,
                'position': [component.pos().x(), component.pos().y()],
                'properties': component.get_properties()
            }
            components_data.append(component_data)
            component_ids.add(component.unique_id)
            
        # 收集相关连接
        connections_data = []
        if connections:
            for connection in connections:
                start_comp = connection.start_port.parent_component
                end_comp = connection.end_port.parent_component

                # 确保组件有唯一ID
                if not hasattr(start_comp, 'unique_id'):
                    import uuid
                    start_comp.unique_id = str(uuid.uuid4())
                if not hasattr(end_comp, 'unique_id'):
                    import uuid
                    end_comp.unique_id = str(uuid.uuid4())

                start_comp_id = start_comp.unique_id
                end_comp_id = end_comp.unique_id

                # 只复制两端都在选中组件中的连接
                if start_comp_id in component_ids and end_comp_id in component_ids:
                    connection_data = {
                        'start_component': start_comp_id,
                        'start_port': connection.start_port.index,
                        'end_component': end_comp_id,
                        'end_port': connection.end_port.index
                    }
                    connections_data.append(connection_data)
        
        # 保存到剪贴板
        self.clipboard_data = {
            'components': components_data,
            'connections': connections_data
        }
        self.clipboard_type = 'components'
        
        # 发射信号
        self.clipboard_changed.emit(True)
        
    def paste_components(self, canvas, offset: QPointF = None) -> List:
        """粘贴组件"""
        if not self.has_content() or self.clipboard_type != 'components':
            return []
            
        if offset is None:
            offset = QPointF(20, 20)  # 默认偏移
            
        # 创建ID映射
        old_to_new_id = {}
        new_components = []
        
        # 粘贴组件
        for comp_data in self.clipboard_data['components']:
            # 计算新位置
            old_pos = QPointF(comp_data['position'][0], comp_data['position'][1])
            new_pos = old_pos + offset
            
            # 创建新组件
            new_component = canvas.add_component(
                comp_data['type'],
                comp_data['name'],
                new_pos
            )
            
            # 设置属性
            if comp_data.get('properties'):
                new_component.set_properties(comp_data['properties'])
            
            # 记录ID映射
            old_to_new_id[comp_data['id']] = new_component
            new_components.append(new_component)
            
        # 粘贴连接
        for conn_data in self.clipboard_data['connections']:
            start_comp = old_to_new_id.get(conn_data['start_component'])
            end_comp = old_to_new_id.get(conn_data['end_component'])
            
            if start_comp and end_comp:
                start_port = start_comp.output_ports[conn_data['start_port']]
                end_port = end_comp.input_ports[conn_data['end_port']]
                
                # 创建连接
                from .components import ConnectionLine
                connection = ConnectionLine(start_port, end_port)
                canvas.scene.addItem(connection)
                
                start_port.connections.append(connection)
                end_port.connections.append(connection)
                canvas.connections.append(connection)
                
        return new_components
        
    def cut_components(self, components: List, connections: List = None):
        """剪切组件"""
        # 先复制
        self.copy_components(components, connections)
        
        # 标记为剪切
        self.clipboard_type = 'cut_components'
        
    def has_content(self) -> bool:
        """是否有剪贴板内容"""
        return self.clipboard_data is not None
        
    def get_content_type(self) -> Optional[str]:
        """获取剪贴板内容类型"""
        return self.clipboard_type
        
    def clear(self):
        """清空剪贴板"""
        self.clipboard_data = None
        self.clipboard_type = None
        self.clipboard_changed.emit(False)
        
    def get_content_summary(self) -> str:
        """获取内容摘要"""
        if not self.has_content():
            return "剪贴板为空"
            
        if self.clipboard_type in ['components', 'cut_components']:
            comp_count = len(self.clipboard_data.get('components', []))
            conn_count = len(self.clipboard_data.get('connections', []))
            action = "剪切" if self.clipboard_type == 'cut_components' else "复制"
            return f"{action}了 {comp_count} 个组件和 {conn_count} 个连接"
            
        return "未知内容"
        
    def export_to_json(self) -> str:
        """导出为JSON字符串"""
        if not self.has_content():
            return ""
            
        return json.dumps(self.clipboard_data, indent=2, ensure_ascii=False)
        
    def import_from_json(self, json_str: str) -> bool:
        """从JSON字符串导入"""
        try:
            data = json.loads(json_str)
            
            # 验证数据格式
            if 'components' in data and isinstance(data['components'], list):
                self.clipboard_data = data
                self.clipboard_type = 'components'
                self.clipboard_changed.emit(True)
                return True
                
        except (json.JSONDecodeError, KeyError):
            pass
            
        return False


# 全局剪贴板管理器实例
clipboard_manager = ClipboardManager()
