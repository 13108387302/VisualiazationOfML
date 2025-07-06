#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习组件模块
包含组件、端口、连接线等基础图形元素
"""

from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont


class ConnectionPort(QGraphicsEllipseItem):
    """连接端口"""
    
    def __init__(self, parent_component, port_type, index, is_input=True):
        super().__init__(-5, -5, 10, 10)
        self.parent_component = parent_component
        self.port_type = port_type  # 数据类型
        self.index = index
        self.is_input = is_input
        self.connections = []
        
        # 设置端口样式
        self.setBrush(QBrush(QColor(50, 50, 50)))
        self.setPen(QPen(QColor(0, 0, 0), 1))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        # 设置父组件
        self.setParentItem(parent_component)
        
        # 计算端口位置
        self.update_position()
        
    def update_position(self):
        """更新端口位置"""
        rect = self.parent_component.rect()
        if self.is_input:
            # 输入端口在左侧
            x = 0
            y = rect.height() * (self.index + 1) / (len(self.parent_component.input_ports) + 1)
        else:
            # 输出端口在右侧
            x = rect.width()
            y = rect.height() * (self.index + 1) / (len(self.parent_component.output_ports) + 1)
        
        self.setPos(x, y)


class ConnectionLine(QGraphicsLineItem):
    """连接线"""
    
    def __init__(self, start_port, end_port=None):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.temp_end_pos = None
        
        # 设置线条样式
        self.setPen(QPen(QColor(50, 50, 50), 2))
        
        # 更新线条
        self.update_line()
        
    def update_line(self):
        """更新连接线"""
        if self.start_port:
            start_pos = self.start_port.scenePos()
            
            if self.end_port:
                end_pos = self.end_port.scenePos()
            elif self.temp_end_pos:
                end_pos = self.temp_end_pos
            else:
                return
                
            self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
            
    def set_temp_end_pos(self, pos):
        """设置临时结束位置（用于拖拽时）"""
        self.temp_end_pos = pos
        self.update_line()


class MLComponent(QGraphicsRectItem):
    """机器学习组件基类"""
    
    def __init__(self, component_type, name, width=120, height=80):
        super().__init__(0, 0, width, height)
        self.component_type = component_type
        self.name = name
        self.input_ports = []
        self.output_ports = []
        self.connections = []
        
        # 设置组件样式
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # 创建文本标签
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(10, 30)
        self.text_item.setFont(QFont("Arial", 10))
        
        # 设置颜色
        self.setup_appearance()
        
        # 创建端口
        self.create_ports()
        
    def setup_appearance(self):
        """设置组件外观"""
        colors = {
            'data': QColor(100, 150, 255),      # 蓝色 - 数据相关
            'preprocess': QColor(255, 200, 100), # 橙色 - 预处理
            'model': QColor(150, 255, 150),     # 绿色 - 模型
            'evaluate': QColor(255, 150, 150),  # 红色 - 评估
            'output': QColor(200, 200, 200)     # 灰色 - 输出
        }
        
        color = colors.get(self.component_type, QColor(200, 200, 200))
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(50, 50, 50), 2))
        
    def create_ports(self):
        """创建输入输出端口"""
        # 根据组件类型创建不同的端口
        port_config = {
            'data': {'inputs': 0, 'outputs': 1},
            'preprocess': {'inputs': 1, 'outputs': 1},
            'model': {'inputs': 1, 'outputs': 1},
            'evaluate': {'inputs': 2, 'outputs': 1},
            'output': {'inputs': 1, 'outputs': 0}
        }
        
        config = port_config.get(self.component_type, {'inputs': 1, 'outputs': 1})
        
        # 创建输入端口
        for i in range(config['inputs']):
            port = ConnectionPort(self, 'data', i, is_input=True)
            self.input_ports.append(port)
            
        # 创建输出端口
        for i in range(config['outputs']):
            port = ConnectionPort(self, 'data', i, is_input=False)
            self.output_ports.append(port)
            
    def itemChange(self, change, value):
        """组件位置改变时更新连接线"""
        if change == QGraphicsItem.ItemPositionChange:
            # 更新所有连接的线条
            for port in self.input_ports + self.output_ports:
                for connection in port.connections:
                    connection.update_line()
        return super().itemChange(change, value)
        
    def get_properties(self):
        """获取组件属性（供后端使用）"""
        return {
            'type': self.component_type,
            'name': self.name,
            'position': (self.pos().x(), self.pos().y()),
            'parameters': {}  # 具体参数由子类实现
        }
        
    def set_properties(self, properties):
        """设置组件属性（供后端使用）"""
        if 'position' in properties:
            x, y = properties['position']
            self.setPos(QPointF(x, y))
        # 其他属性设置由子类实现
