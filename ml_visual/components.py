#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习组件模块
包含组件、端口、连接线等基础图形元素
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsEllipseItem,
                             QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont
from .memory_manager import memory_manager
from .config_manager import get_component_config


class ConnectionPort(QGraphicsEllipseItem):
    """连接端口"""
    
    def __init__(self, parent_component, port_type: str, index: int, is_input: bool = True) -> None:
        """
        初始化连接端口

        Args:
            parent_component: 父组件
            port_type: 端口数据类型
            index: 端口索引
            is_input: 是否为输入端口
        """
        # 参数验证
        if parent_component is None:
            raise ValueError("父组件不能为None")
        if not isinstance(port_type, str) or not port_type.strip():
            raise ValueError("端口类型必须是非空字符串")
        if not isinstance(index, int) or index < 0:
            raise ValueError("端口索引必须是非负整数")
        if not isinstance(is_input, bool):
            raise ValueError("is_input必须是布尔值")

        super().__init__(-5, -5, 10, 10)
        self.parent_component = parent_component
        self.port_type = port_type.strip()  # 数据类型
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

        # 性能优化设置
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption, True)

        # 更新线条
        self.update_line()

        # 内存管理 - 跟踪连接对象
        memory_manager.track_connection(self)
        
    def update_line(self):
        """更新连接线（优化版本）"""
        if not self.start_port:
            return

        try:
            start_pos = self.start_port.scenePos()

            if self.end_port:
                end_pos = self.end_port.scenePos()
            elif self.temp_end_pos:
                end_pos = self.temp_end_pos
            else:
                return

            # 只有位置真正改变时才更新
            current_line = self.line()
            new_line = (start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

            # 增加阈值以减少微小移动的更新
            threshold = 1.0
            if (abs(current_line.x1() - new_line[0]) > threshold or
                abs(current_line.y1() - new_line[1]) > threshold or
                abs(current_line.x2() - new_line[2]) > threshold or
                abs(current_line.y2() - new_line[3]) > threshold):
                self.setLine(*new_line)

        except RuntimeError:
            # 端口已被删除
            pass
            
    def set_temp_end_pos(self, pos):
        """设置临时结束位置（用于拖拽时）"""
        self.temp_end_pos = pos
        self.update_line()


class MLComponent(QGraphicsRectItem):
    """机器学习组件基类"""
    
    def __init__(self, component_type: str, name: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
        """
        初始化机器学习组件

        Args:
            component_type: 组件类型 (data, preprocess, model, evaluate, output)
            name: 组件名称
            width: 组件宽度，默认从配置获取
            height: 组件高度，默认从配置获取
        """
        # 从配置获取默认大小
        if width is None or height is None:
            component_config = get_component_config()
            default_size = component_config.get('default_size', [120, 80])
            width = width or default_size[0]
            height = height or default_size[1]

        super().__init__(0, 0, width, height)

        # 生成唯一ID
        import uuid
        self.unique_id = str(uuid.uuid4())

        self.component_type = component_type
        self.name = name
        self.input_ports = []
        self.output_ports = []
        self.connections = []
        
        # 设置组件样式
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # 性能优化设置
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)  # 缓存渲染结果
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption, True)  # 优化样式选项
        
        # 创建文本标签
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(10, 30)
        self.text_item.setFont(QFont("Arial", 10))
        
        # 设置颜色
        self.setup_appearance()
        
        # 创建端口
        self.create_ports()

        # 内存管理 - 跟踪组件对象
        memory_manager.track_component(self)
        
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
            
    def paint(self, painter, option, widget):
        """自定义绘制方法（性能优化）"""
        # 检查细节级别（LOD优化）
        lod = option.levelOfDetailFromTransform(painter.worldTransform())

        # 低细节级别时简化绘制
        if lod < 0.3:
            # 极简绘制 - 只绘制填充矩形
            painter.fillRect(self.rect(), QColor(200, 200, 200))
            return
        elif lod < 0.7:
            # 简化绘制 - 基本形状
            painter.fillRect(self.rect(), self.brush().color())
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawRect(self.rect())
            return

        # 完整绘制（正常缩放级别）
        super().paint(painter, option, widget)

        # 只在高细节级别绘制文本
        if lod > 0.8 and hasattr(self, 'text_item'):
            # 文本已经由text_item处理，这里不需要额外绘制
            pass

    def itemChange(self, change, value):
        """组件位置改变时更新连接线（优化版本）"""
        if change == QGraphicsItem.ItemPositionChange:
            # 批量更新连接线，减少重绘次数
            connections_to_update = set()
            for port in self.input_ports + self.output_ports:
                for connection in port.connections:
                    connections_to_update.add(connection)

            # 延迟更新连接线
            if hasattr(self.scene(), 'views') and self.scene().views():
                canvas = self.scene().views()[0]
                if hasattr(canvas, 'schedule_component_update'):
                    for connection in connections_to_update:
                        canvas.schedule_component_update(connection)
                else:
                    # 回退到立即更新
                    for connection in connections_to_update:
                        connection.update_line()
            else:
                for connection in connections_to_update:
                    connection.update_line()

        return super().itemChange(change, value)
        
    def get_properties(self):
        """获取组件属性（供后端使用）"""
        properties = {
            'type': self.component_type,
            'name': self.name,
            'position': (self.pos().x(), self.pos().y()),
            'parameters': {}  # 具体参数由子类实现
        }

        # 添加组件特定属性
        if hasattr(self, 'custom_properties'):
            properties['parameters'].update(self.custom_properties)

        return properties

    def set_properties(self, properties):
        """设置组件属性（供后端使用）"""
        if 'name' in properties:
            self.name = properties['name']
            self.update_display()

        if 'position' in properties:
            x, y = properties['position']
            self.setPos(QPointF(x, y))

        if 'parameters' in properties:
            if not hasattr(self, 'custom_properties'):
                self.custom_properties = {}
            self.custom_properties.update(properties['parameters'])

    def get_property(self, key, default=None):
        """获取单个属性"""
        if not hasattr(self, 'custom_properties'):
            self.custom_properties = {}
        return self.custom_properties.get(key, default)

    def set_property(self, key, value):
        """设置单个属性"""
        if not hasattr(self, 'custom_properties'):
            self.custom_properties = {}
        self.custom_properties[key] = value

    def update_display(self):
        """更新显示（重新绘制组件）"""
        self.update()
