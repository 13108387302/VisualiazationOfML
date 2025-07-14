#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令管理器模块
实现撤销/重做功能
"""

from PyQt5.QtCore import QObject, pyqtSignal
from typing import List, Any, Dict
import copy
from .memory_manager import MemoryOptimizedList, memory_efficient_decorator


class Command:
    """命令基类"""
    
    def __init__(self, description: str = ""):
        self.description = description
        
    def execute(self):
        """执行命令"""
        raise NotImplementedError
        
    def undo(self):
        """撤销命令"""
        raise NotImplementedError
        
    def redo(self):
        """重做命令（默认等同于执行）"""
        self.execute()


class AddComponentCommand(Command):
    """添加组件命令"""
    
    def __init__(self, canvas, component_type: str, name: str, position, description: str = ""):
        super().__init__(description or f"添加组件: {name}")
        self.canvas = canvas
        self.component_type = component_type
        self.name = name
        self.position = position
        self.component = None
        
    def execute(self):
        """执行添加组件"""
        self.component = self.canvas.add_component(
            self.component_type, self.name, self.position, use_command=False
        )
        return self.component
        
    def undo(self):
        """撤销添加组件"""
        if self.component and self.component in self.canvas.components:
            self.canvas.remove_component(self.component)
            
    def redo(self):
        """重做添加组件"""
        if self.component:
            # 重新添加到场景
            self.canvas.scene.addItem(self.component)
            if self.component not in self.canvas.components:
                self.canvas.components.append(self.component)
        else:
            self.execute()


class RemoveComponentCommand(Command):
    """移除组件命令"""
    
    def __init__(self, canvas, component, description: str = ""):
        super().__init__(description or f"移除组件: {component.name}")
        self.canvas = canvas
        self.component = component
        self.component_data = None
        self.connections_data = []
        
    def execute(self):
        """执行移除组件"""
        # 保存组件数据
        self.component_data = {
            'type': self.component.component_type,
            'name': self.component.name,
            'position': self.component.pos(),
            'properties': self.component.get_properties()
        }
        
        # 保存连接数据
        self.connections_data = []
        for port in self.component.input_ports + self.component.output_ports:
            for connection in port.connections[:]:
                conn_data = {
                    'start_component': connection.start_port.parent_component,
                    'start_port_index': connection.start_port.index,
                    'end_component': connection.end_port.parent_component,
                    'end_port_index': connection.end_port.index,
                    'connection': connection
                }
                self.connections_data.append(conn_data)
        
        # 移除组件
        self.canvas.remove_component(self.component)
        
    def undo(self):
        """撤销移除组件"""
        # 重新创建组件
        self.component = self.canvas.add_component(
            self.component_data['type'],
            self.component_data['name'],
            self.component_data['position']
        )
        
        # 恢复连接
        for conn_data in self.connections_data:
            start_comp = conn_data['start_component']
            end_comp = conn_data['end_component']
            
            if (start_comp in self.canvas.components and 
                end_comp in self.canvas.components):
                
                start_port = start_comp.output_ports[conn_data['start_port_index']]
                end_port = end_comp.input_ports[conn_data['end_port_index']]
                
                # 重新创建连接
                from .components import ConnectionLine
                connection = ConnectionLine(start_port, end_port)
                self.canvas.scene.addItem(connection)
                
                start_port.connections.append(connection)
                end_port.connections.append(connection)
                self.canvas.connections.append(connection)


class MoveComponentCommand(Command):
    """移动组件命令"""
    
    def __init__(self, canvas, component, old_position, new_position, description: str = ""):
        super().__init__(description or f"移动组件: {component.name}")
        self.canvas = canvas
        self.component = component
        self.old_position = old_position
        self.new_position = new_position
        
    def execute(self):
        """执行移动组件"""
        self.component.setPos(self.new_position)
        
    def undo(self):
        """撤销移动组件"""
        self.component.setPos(self.old_position)
        
    def redo(self):
        """重做移动组件"""
        self.component.setPos(self.new_position)


class AddConnectionCommand(Command):
    """添加连接命令"""
    
    def __init__(self, canvas, start_port, end_port, description: str = ""):
        super().__init__(description or "添加连接")
        self.canvas = canvas
        self.start_port = start_port
        self.end_port = end_port
        self.connection = None
        
    def execute(self):
        """执行添加连接"""
        from .components import ConnectionLine
        self.connection = ConnectionLine(self.start_port, self.end_port)
        self.canvas.scene.addItem(self.connection)
        
        self.start_port.connections.append(self.connection)
        self.end_port.connections.append(self.connection)
        self.canvas.connections.append(self.connection)
        
        return self.connection
        
    def undo(self):
        """撤销添加连接"""
        if self.connection:
            self.canvas.remove_connection(self.connection)


class RemoveConnectionCommand(Command):
    """移除连接命令"""
    
    def __init__(self, canvas, connection, description: str = ""):
        super().__init__(description or "移除连接")
        self.canvas = canvas
        self.connection = connection
        self.start_port = connection.start_port
        self.end_port = connection.end_port
        
    def execute(self):
        """执行移除连接"""
        self.canvas.remove_connection(self.connection)
        
    def undo(self):
        """撤销移除连接"""
        # 重新创建连接
        from .components import ConnectionLine
        self.connection = ConnectionLine(self.start_port, self.end_port)
        self.canvas.scene.addItem(self.connection)
        
        self.start_port.connections.append(self.connection)
        self.end_port.connections.append(self.connection)
        self.canvas.connections.append(self.connection)


class ChangePropertyCommand(Command):
    """修改属性命令"""
    
    def __init__(self, component, property_name: str, old_value: Any, new_value: Any, description: str = ""):
        super().__init__(description or f"修改属性: {component.name}.{property_name}")
        self.component = component
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        
    def execute(self):
        """执行修改属性"""
        # 这里需要根据实际的属性设置方法来实现
        setattr(self.component, self.property_name, self.new_value)
        
    def undo(self):
        """撤销修改属性"""
        setattr(self.component, self.property_name, self.old_value)
        
    def redo(self):
        """重做修改属性"""
        setattr(self.component, self.property_name, self.new_value)


class CommandManager(QObject):
    """命令管理器"""
    
    # 信号定义
    can_undo_changed = pyqtSignal(bool)
    can_redo_changed = pyqtSignal(bool)
    command_executed = pyqtSignal(str)  # 命令描述
    
    def __init__(self, max_history: int = 100):
        super().__init__()
        # 使用内存优化的列表管理命令历史
        self.history = MemoryOptimizedList(max_size=max_history, auto_cleanup=True)
        self.current_index = -1
        self.max_history = max_history
        self.is_executing = False
        
    def execute_command(self, command: Command):
        """执行命令并添加到历史记录（优化内存使用）"""
        if self.is_executing:
            return

        self.is_executing = True
        try:
            # 执行命令
            result = command.execute()

            # 清除重做历史（释放内存）
            removed_commands = self.history[self.current_index + 1:]
            self.history = self.history[:self.current_index + 1]

            # 显式删除被移除的命令以释放内存
            for cmd in removed_commands:
                del cmd

            # 添加到历史记录
            self.history.append(command)
            self.current_index += 1

            # 限制历史记录大小，释放旧命令的内存
            if len(self.history) > self.max_history:
                old_command = self.history.pop(0)
                del old_command  # 显式删除以释放内存
                self.current_index -= 1

            # 发射信号
            self.can_undo_changed.emit(True)
            self.can_redo_changed.emit(False)
            self.command_executed.emit(command.description)

            return result

        finally:
            self.is_executing = False
            
    def undo(self):
        """撤销操作"""
        if self.can_undo():
            self.is_executing = True
            try:
                command = self.history[self.current_index]
                command.undo()
                self.current_index -= 1
                
                # 发射信号
                self.can_undo_changed.emit(self.can_undo())
                self.can_redo_changed.emit(True)
                self.command_executed.emit(f"撤销: {command.description}")
                
            finally:
                self.is_executing = False
                
    def redo(self):
        """重做操作"""
        if self.can_redo():
            self.is_executing = True
            try:
                self.current_index += 1
                command = self.history[self.current_index]
                command.redo()
                
                # 发射信号
                self.can_undo_changed.emit(True)
                self.can_redo_changed.emit(self.can_redo())
                self.command_executed.emit(f"重做: {command.description}")
                
            finally:
                self.is_executing = False
                
    def can_undo(self) -> bool:
        """是否可以撤销"""
        return self.current_index >= 0
        
    def can_redo(self) -> bool:
        """是否可以重做"""
        return self.current_index < len(self.history) - 1
        
    def clear_history(self):
        """清空历史记录"""
        self.history.clear()
        self.current_index = -1
        self.can_undo_changed.emit(False)
        self.can_redo_changed.emit(False)
        
    def get_undo_text(self) -> str:
        """获取撤销操作的描述"""
        if self.can_undo():
            return f"撤销 {self.history[self.current_index].description}"
        return "撤销"
        
    def get_redo_text(self) -> str:
        """获取重做操作的描述"""
        if self.can_redo():
            return f"重做 {self.history[self.current_index + 1].description}"
        return "重做"
        
    def get_history_summary(self) -> List[str]:
        """获取历史记录摘要"""
        return [cmd.description for cmd in self.history]
