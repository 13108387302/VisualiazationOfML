#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画布模块
处理组件的拖拽、连接和交互
"""

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QBrush, QColor

from .components import MLComponent, ConnectionPort, ConnectionLine


class MLCanvas(QGraphicsView):
    """机器学习流程图画布"""
    
    component_selected = pyqtSignal(object)
    component_added = pyqtSignal(object)
    connection_created = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.current_connection = None
        self.connecting_mode = False
        self.components = []
        self.connections = []
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置画布属性
        self.setDragMode(QGraphicsView.RubberBandDrag)
        from PyQt5.QtGui import QPainter
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAcceptDrops(True)
        
        # 设置场景大小
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        # 设置背景
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # 连接信号
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """拖拽放下事件"""
        if event.mimeData().hasText():
            try:
                # 获取组件信息
                component_data = eval(event.mimeData().text())
                
                # 转换坐标
                scene_pos = self.mapToScene(event.pos())
                
                # 创建组件
                self.add_component(
                    component_data['type'], 
                    component_data['name'], 
                    scene_pos
                )
                
                event.acceptProposedAction()
            except Exception as e:
                print(f"拖拽放下错误: {e}")
                
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            
            # 检查是否点击了端口
            if isinstance(item, ConnectionPort):
                self.start_connection(item)
                return
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.connecting_mode and self.current_connection:
            # 更新连接线的临时结束位置
            scene_pos = self.mapToScene(event.pos())
            self.current_connection.set_temp_end_pos(scene_pos)
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.connecting_mode and event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            
            if isinstance(item, ConnectionPort):
                self.finish_connection(item)
            else:
                self.cancel_connection()
                
        super().mouseReleaseEvent(event)
        
    def start_connection(self, start_port):
        """开始连接"""
        if start_port.is_input:
            return  # 只能从输出端口开始连接
            
        self.connecting_mode = True
        self.current_connection = ConnectionLine(start_port)
        self.scene.addItem(self.current_connection)
        
    def finish_connection(self, end_port):
        """完成连接"""
        if (self.current_connection and 
            end_port.is_input and 
            end_port.parent_component != self.current_connection.start_port.parent_component):
            
            # 检查端口是否已有连接（输入端口只能有一个连接）
            if end_port.connections:
                self.cancel_connection()
                return
            
            # 设置连接的结束端口
            self.current_connection.end_port = end_port
            self.current_connection.temp_end_pos = None
            self.current_connection.update_line()
            
            # 添加到端口的连接列表
            self.current_connection.start_port.connections.append(self.current_connection)
            end_port.connections.append(self.current_connection)
            
            # 添加到画布连接列表
            self.connections.append(self.current_connection)
            
            # 发射连接创建信号
            self.connection_created.emit(self.current_connection)
            
        else:
            self.cancel_connection()
            
        self.connecting_mode = False
        self.current_connection = None
        
    def cancel_connection(self):
        """取消连接"""
        if self.current_connection:
            self.scene.removeItem(self.current_connection)
            
        self.connecting_mode = False
        self.current_connection = None
        
    def on_selection_changed(self):
        """选择改变时的处理"""
        selected_items = self.scene.selectedItems()
        if selected_items and isinstance(selected_items[0], MLComponent):
            self.component_selected.emit(selected_items[0])
        else:
            self.component_selected.emit(None)
            
    def add_component(self, component_type, name, pos=None):
        """添加组件到画布"""
        if pos is None:
            pos = QPointF(0, 0)
            
        component = MLComponent(component_type, name)
        component.setPos(pos)
        self.scene.addItem(component)
        self.components.append(component)
        
        # 发射组件添加信号
        self.component_added.emit(component)
        
        return component
        
    def remove_component(self, component):
        """移除组件"""
        if component in self.components:
            # 移除相关连接
            self.remove_component_connections(component)
            
            # 从场景和列表中移除
            self.scene.removeItem(component)
            self.components.remove(component)
            
    def remove_component_connections(self, component):
        """移除组件的所有连接"""
        connections_to_remove = []
        
        # 收集需要移除的连接
        for port in component.input_ports + component.output_ports:
            connections_to_remove.extend(port.connections)
            
        # 移除连接
        for connection in connections_to_remove:
            self.remove_connection(connection)
            
    def remove_connection(self, connection):
        """移除连接"""
        if connection in self.connections:
            # 从端口连接列表中移除
            if connection.start_port:
                connection.start_port.connections.remove(connection)
            if connection.end_port:
                connection.end_port.connections.remove(connection)
                
            # 从场景和列表中移除
            self.scene.removeItem(connection)
            self.connections.remove(connection)
            
    def clear_canvas(self):
        """清空画布"""
        self.scene.clear()
        self.components.clear()
        self.connections.clear()
        
    def get_workflow_data(self):
        """获取工作流程数据"""
        workflow = {
            'components': [],
            'connections': []
        }
        
        # 收集组件数据
        for component in self.components:
            workflow['components'].append({
                'id': id(component),
                'type': component.component_type,
                'name': component.name,
                'position': (component.pos().x(), component.pos().y()),
                'properties': component.get_properties()
            })
            
        # 收集连接数据
        for connection in self.connections:
            workflow['connections'].append({
                'start_component': id(connection.start_port.parent_component),
                'start_port': connection.start_port.index,
                'end_component': id(connection.end_port.parent_component),
                'end_port': connection.end_port.index
            })
            
        return workflow
        
    def load_workflow_data(self, workflow_data):
        """加载工作流程数据"""
        self.clear_canvas()
        
        # 组件ID映射
        component_map = {}
        
        # 创建组件
        for comp_data in workflow_data.get('components', []):
            component = self.add_component(
                comp_data['type'],
                comp_data['name'],
                QPointF(comp_data['position'][0], comp_data['position'][1])
            )
            component_map[comp_data['id']] = component
            
        # 创建连接
        for conn_data in workflow_data.get('connections', []):
            start_comp = component_map.get(conn_data['start_component'])
            end_comp = component_map.get(conn_data['end_component'])
            
            if start_comp and end_comp:
                start_port = start_comp.output_ports[conn_data['start_port']]
                end_port = end_comp.input_ports[conn_data['end_port']]
                
                # 创建连接
                connection = ConnectionLine(start_port, end_port)
                self.scene.addItem(connection)
                
                # 添加到端口连接列表
                start_port.connections.append(connection)
                end_port.connections.append(connection)
                self.connections.append(connection)
        
    def wheelEvent(self, event):
        """鼠标滚轮缩放"""
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
            
        self.scale(factor, factor)
        
    def fit_to_contents(self):
        """适应内容大小"""
        if self.components:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        else:
            self.resetTransform()
