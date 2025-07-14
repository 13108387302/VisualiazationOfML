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
from .command_manager import (CommandManager, AddComponentCommand, RemoveComponentCommand,
                             MoveComponentCommand, AddConnectionCommand, RemoveConnectionCommand)
from .clipboard_manager import clipboard_manager
from .error_handler import handle_errors, ErrorReporter, ComponentError
from .config_manager import get_config, get_canvas_config


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

        # 命令管理器
        self.command_manager = CommandManager()
        self.command_manager.can_undo_changed.connect(self.can_undo_changed)
        self.command_manager.can_redo_changed.connect(self.can_redo_changed)

        # 组件移动相关
        self.moving_component = None
        self.move_start_position = None

        # 性能优化相关
        self._visible_components = set()  # 可见组件缓存
        self._update_timer = None  # 延迟更新定时器
        self._pending_updates = set()  # 待更新的组件

        self.init_ui()
        self._setup_performance_optimization()

    # 新增信号
    can_undo_changed = pyqtSignal(bool)
    can_redo_changed = pyqtSignal(bool)
    selection_changed = pyqtSignal(bool)  # 是否有选中项
        
    def init_ui(self):
        """初始化用户界面"""
        # 优化渲染设置
        from PyQt5.QtGui import QPainter
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)  # 性能优化
        self.setCacheMode(QGraphicsView.CacheBackground)  # 缓存背景
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)  # 性能优化

        # 设置交互模式
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)  # 启用鼠标跟踪以获得更好的交互

        # 设置滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 性能优化：减少不必要的重绘
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setInteractive(True)

        # 从配置获取场景设置
        canvas_config = get_canvas_config()
        scene_config = canvas_config.get('scene', {})
        scene_rect = scene_config.get('rect', [-2000, -2000, 4000, 4000])
        bg_color = scene_config.get('background_color', '#f5f5f5')

        # 设置场景大小
        self.scene.setSceneRect(*scene_rect)

        # 设置背景
        self.setBackgroundBrush(QBrush(QColor(bg_color)))

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
                component_text = event.mimeData().text()

                # 转换坐标
                scene_pos = self.mapToScene(event.pos())

                # 处理组件名称（移除emoji）
                import re
                clean_text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', component_text).strip()
                if not clean_text:
                    clean_text = "组件"

                # 创建组件
                self.add_component(
                    clean_text,
                    f"新{clean_text}",
                    scene_pos
                )
                
                event.acceptProposedAction()
            except Exception as e:
                print(f"拖拽放下错误: {e}")
                # 显示用户友好的错误提示
                error_pos = scene_pos if 'scene_pos' in locals() else QPointF(0, 0)
                self.show_error_feedback(error_pos, "组件创建失败，请重试")

    def show_error_feedback(self, pos, message):
        """显示错误反馈（临时提示）"""
        # 创建临时的错误提示文本
        from PyQt5.QtWidgets import QGraphicsTextItem
        from PyQt5.QtCore import QTimer

        # 从配置获取反馈设置
        canvas_config = get_canvas_config()
        feedback_config = canvas_config.get('feedback', {})
        error_color = feedback_config.get('error_color', '#dc3545')
        error_duration = feedback_config.get('error_duration', 3000)

        error_text = QGraphicsTextItem(message)
        error_text.setPos(pos)
        error_text.setDefaultTextColor(QColor(error_color))
        self.scene.addItem(error_text)

        # 自动移除
        QTimer.singleShot(error_duration, lambda: self.scene.removeItem(error_text))
                
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

    def keyPressEvent(self, event):
        """键盘事件处理"""
        key = event.key()
        modifiers = event.modifiers()

        # Delete键删除选中组件
        if key == Qt.Key_Delete:
            self.delete_selected_components()
            return

        # 方向键移动选中组件
        if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            self.move_selected_components(key, modifiers)
            return

        # Escape键取消当前操作
        if key == Qt.Key_Escape:
            self.cancel_current_operation()
            return

        super().keyPressEvent(event)

    def delete_selected_components(self):
        """删除选中的组件"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, MLComponent):
                self.remove_component(item)

    def move_selected_components(self, key, modifiers):
        """移动选中的组件"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return

        # 从配置获取移动步长
        canvas_config = get_canvas_config()
        interaction_config = canvas_config.get('interaction', {})
        step = interaction_config.get('keyboard_move_fast_step', 10) if modifiers & Qt.ShiftModifier else interaction_config.get('keyboard_move_step', 1)

        dx, dy = 0, 0
        if key == Qt.Key_Left:
            dx = -step
        elif key == Qt.Key_Right:
            dx = step
        elif key == Qt.Key_Up:
            dy = -step
        elif key == Qt.Key_Down:
            dy = step

        # 移动组件
        for item in selected_items:
            if isinstance(item, MLComponent):
                new_pos = item.pos() + QPointF(dx, dy)
                item.setPos(new_pos)

    def cancel_current_operation(self):
        """取消当前操作"""
        if self.connecting_mode and self.current_connection:
            self.scene.removeItem(self.current_connection)
            self.current_connection = None
            self.connecting_mode = False
        
    def start_connection(self, start_port):
        """开始连接"""
        if not start_port or start_port.is_input:
            return  # 只能从输出端口开始连接

        # 取消当前连接（如果有）
        if self.connecting_mode:
            self.cancel_connection()

        self.connecting_mode = True
        self.current_connection = ConnectionLine(start_port)
        self.scene.addItem(self.current_connection)
        
    def finish_connection(self, end_port):
        """完成连接"""
        if not self.current_connection or not end_port:
            self.cancel_connection()
            return

        # 验证连接有效性
        if (end_port.is_input and
            end_port.parent_component != self.current_connection.start_port.parent_component):

            # 检查端口是否已有连接（输入端口只能有一个连接）
            if end_port.connections:
                self.show_error_feedback(end_port.scenePos(), "输入端口已有连接")
                self.cancel_connection()
                return

            # 检查是否会形成循环
            if self._would_create_cycle(self.current_connection.start_port.parent_component,
                                       end_port.parent_component):
                self.show_error_feedback(end_port.scenePos(), "连接会形成循环")
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

    def _would_create_cycle(self, start_component, end_component):
        """检查连接是否会创建循环"""
        def has_path(from_comp, to_comp, visited=None):
            if visited is None:
                visited = set()

            if from_comp == to_comp:
                return True

            if from_comp in visited:
                return False

            visited.add(from_comp)

            # 检查所有输出连接
            for port in from_comp.output_ports:
                for connection in port.connections:
                    if connection.end_port:
                        next_comp = connection.end_port.parent_component
                        if has_path(next_comp, to_comp, visited.copy()):
                            return True

            return False

        return has_path(end_component, start_component)

    def show_error_feedback(self, position, message):
        """显示错误反馈"""
        try:
            from .ui_utils import NotificationWidget
            from PyQt5.QtCore import QTimer

            # 创建临时错误提示
            error_widget = NotificationWidget(message, "error")
            error_widget.setParent(self)
            error_widget.move(self.mapFromScene(position).toPoint())
            error_widget.show()

            # 3秒后自动移除
            QTimer.singleShot(3000, error_widget.deleteLater)
        except Exception:
            # 回退到简单的状态栏消息
            if hasattr(self, 'parent') and hasattr(self.parent(), 'statusBar'):
                self.parent().statusBar().showMessage(f"错误: {message}", 3000)
        
    def on_selection_changed(self):
        """选择改变时的处理"""
        selected_items = self.scene.selectedItems()
        if selected_items and isinstance(selected_items[0], MLComponent):
            self.component_selected.emit(selected_items[0])
        else:
            self.component_selected.emit(None)

        # 发射选择变化信号
        has_selection = len(selected_items) > 0
        self.selection_changed.emit(has_selection)
            
    @handle_errors("添加组件失败")
    def add_component(self, component_type, name, pos=None, use_command=True):
        """添加组件到画布（增强错误处理）"""
        try:
            # 验证输入参数
            if not component_type or not name:
                raise ComponentError("组件类型和名称不能为空")

            if pos is None:
                pos = QPointF(0, 0)
            elif not isinstance(pos, QPointF):
                raise ComponentError("位置参数必须是QPointF类型")

            if use_command:
                # 使用命令模式
                command = AddComponentCommand(self, component_type, name, pos)
                return self.command_manager.execute_command(command)
            else:
                # 直接添加（用于命令执行）
                component = MLComponent(component_type, name)
                component.setPos(pos)
                self.scene.addItem(component)
                self.components.append(component)

                # 发射组件添加信号
                self.component_added.emit(component)

                return component

        except Exception as e:
            ErrorReporter.report_component_error(name, "添加", e)
            return None
        
    def remove_component(self, component):
        """移除组件（增强清理）"""
        if component in self.components:
            try:
                # 移除相关连接
                self.remove_component_connections(component)

                # 从可见组件缓存中移除
                if hasattr(self, '_visible_components') and component in self._visible_components:
                    self._visible_components.remove(component)

                # 从待更新列表中移除
                if hasattr(self, '_pending_updates') and component in self._pending_updates:
                    self._pending_updates.remove(component)

                # 从场景和列表中移除
                self.scene.removeItem(component)
                self.components.remove(component)

                # 发射组件移除信号
                if hasattr(self, 'component_removed'):
                    self.component_removed.emit(component)

            except Exception as e:
                print(f"移除组件时出错: {e}")
                # 确保至少从列表中移除
                if component in self.components:
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
            # 确保组件有唯一ID
            if not hasattr(component, 'unique_id'):
                import uuid
                component.unique_id = str(uuid.uuid4())

            workflow['components'].append({
                'id': component.unique_id,
                'type': component.component_type,
                'name': component.name,
                'position': (component.pos().x(), component.pos().y()),
                'properties': component.get_properties()
            })

        # 收集连接数据
        for connection in self.connections:
            if connection.start_port and connection.end_port:
                # 确保组件有唯一ID
                start_comp = connection.start_port.parent_component
                end_comp = connection.end_port.parent_component

                if not hasattr(start_comp, 'unique_id'):
                    import uuid
                    start_comp.unique_id = str(uuid.uuid4())
                if not hasattr(end_comp, 'unique_id'):
                    import uuid
                    end_comp.unique_id = str(uuid.uuid4())

                workflow['connections'].append({
                    'start_component': start_comp.unique_id,
                    'start_port': connection.start_port.index,
                    'end_component': end_comp.unique_id,
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
                try:
                    # 安全地获取端口
                    start_port_index = conn_data['start_port']
                    end_port_index = conn_data['end_port']

                    if (start_port_index < len(start_comp.output_ports) and
                        end_port_index < len(end_comp.input_ports)):

                        start_port = start_comp.output_ports[start_port_index]
                        end_port = end_comp.input_ports[end_port_index]

                        # 创建连接
                        connection = ConnectionLine(start_port, end_port)
                        self.scene.addItem(connection)
                        self.connections.append(connection)
                    else:
                        print(f"端口索引超出范围: start_port={start_port_index}, end_port={end_port_index}")
                except Exception as e:
                    print(f"创建连接失败: {e}")
                
                # 添加到端口连接列表
                start_port.connections.append(connection)
                end_port.connections.append(connection)
                self.connections.append(connection)
        
    def wheelEvent(self, event):
        """鼠标滚轮缩放（性能优化版本）"""
        # 限制缩放频率，避免过度重绘
        if not hasattr(self, '_last_wheel_time'):
            self._last_wheel_time = 0

        import time
        current_time = time.time()
        if current_time - self._last_wheel_time < 0.016:  # 限制60FPS
            return

        self._last_wheel_time = current_time

        # 从配置获取缩放设置
        canvas_config = get_canvas_config()
        zoom_config = canvas_config.get('zoom', {})
        factor = zoom_config.get('factor', 1.15)
        min_scale = zoom_config.get('min_scale', 0.1)
        max_scale = zoom_config.get('max_scale', 5.0)

        # 缩放逻辑
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        # 限制缩放范围
        current_scale = self.transform().m11()
        if (factor > 1 and current_scale > max_scale) or (factor < 1 and current_scale < min_scale):
            return

        self.scale(factor, factor)
        
    def fit_to_contents(self):
        """适应内容大小"""
        if self.components:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        else:
            self.resetTransform()

    def undo(self):
        """撤销操作"""
        self.command_manager.undo()

    def redo(self):
        """重做操作"""
        self.command_manager.redo()

    def can_undo(self):
        """是否可以撤销"""
        return self.command_manager.can_undo()

    def can_redo(self):
        """是否可以重做"""
        return self.command_manager.can_redo()

    def get_undo_text(self):
        """获取撤销文本"""
        return self.command_manager.get_undo_text()

    def get_redo_text(self):
        """获取重做文本"""
        return self.command_manager.get_redo_text()

    def clear_history(self):
        """清空历史记录"""
        self.command_manager.clear_history()

    def copy_selected(self):
        """复制选中的组件"""
        selected_items = self.scene.selectedItems()
        selected_components = [item for item in selected_items if isinstance(item, MLComponent)]

        if selected_components:
            clipboard_manager.copy_components(selected_components, self.connections)

    def cut_selected(self):
        """剪切选中的组件"""
        selected_items = self.scene.selectedItems()
        selected_components = [item for item in selected_items if isinstance(item, MLComponent)]

        if selected_components:
            clipboard_manager.cut_components(selected_components, self.connections)
            # 删除选中的组件
            for component in selected_components:
                command = RemoveComponentCommand(self, component)
                self.command_manager.execute_command(command)

    def paste(self):
        """粘贴组件"""
        if clipboard_manager.has_content():
            # 计算粘贴位置（鼠标位置或视图中心）
            view_center = self.mapToScene(self.viewport().rect().center())
            # 从配置获取粘贴偏移量
            canvas_config = get_canvas_config()
            interaction_config = canvas_config.get('interaction', {})
            paste_offset = interaction_config.get('paste_offset', [20, 20])
            offset = QPointF(paste_offset[0], paste_offset[1])

            new_components = clipboard_manager.paste_components(self, offset)

            # 选中新粘贴的组件
            self.scene.clearSelection()
            for component in new_components:
                component.setSelected(True)

    def delete_selected(self):
        """删除选中的组件"""
        selected_items = self.scene.selectedItems()
        selected_components = [item for item in selected_items if isinstance(item, MLComponent)]

        for component in selected_components:
            command = RemoveComponentCommand(self, component)
            self.command_manager.execute_command(command)

    def select_all(self):
        """全选组件"""
        for component in self.components:
            component.setSelected(True)

    def has_selection(self):
        """是否有选中的组件"""
        selected_items = self.scene.selectedItems()
        return any(isinstance(item, MLComponent) for item in selected_items)

    def get_selected_components(self):
        """获取选中的组件"""
        selected_items = self.scene.selectedItems()
        return [item for item in selected_items if isinstance(item, MLComponent)]



    def _setup_performance_optimization(self):
        """设置性能优化"""
        try:
            # 视口变化时更新可见组件
            self.horizontalScrollBar().valueChanged.connect(self._update_visible_components)
            self.verticalScrollBar().valueChanged.connect(self._update_visible_components)

            # 初始化更新定时器
            from PyQt5.QtCore import QTimer
            self._update_timer = QTimer(self)  # 指定父对象
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._process_pending_updates)

        except Exception as e:
            print(f"设置性能优化时出错: {e}")
            # 创建空的定时器以避免后续错误
            self._update_timer = None

    def _update_visible_components(self):
        """更新可见组件列表（视口裁剪优化）"""
        try:
            visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
            new_visible = set()

            # 创建组件列表的副本，避免在迭代时修改
            components_copy = list(self.components)

            for component in components_copy:
                try:
                    # 检查组件是否仍然有效
                    if component.scene() is None:
                        # 组件已被删除，从列表中移除
                        if component in self.components:
                            self.components.remove(component)
                        continue

                    if component.sceneBoundingRect().intersects(visible_rect):
                        new_visible.add(component)
                        # 确保可见组件启用更新
                        if not component.isVisible():
                            component.setVisible(True)
                    else:
                        # 不可见组件可以暂停某些更新
                        if component.isVisible():
                            component.setVisible(True)  # 保持可见，但可以优化渲染

                except RuntimeError:
                    # 组件已被删除，从列表中移除
                    if component in self.components:
                        self.components.remove(component)
                    continue

            self._visible_components = new_visible

        except Exception as e:
            print(f"更新可见组件时出错: {e}")

    def schedule_component_update(self, component):
        """调度组件更新（批量处理）"""
        try:
            self._pending_updates.add(component)
            if self._update_timer and not self._update_timer.isActive():
                self._update_timer.start(16)  # 约60FPS
        except Exception as e:
            print(f"调度组件更新时出错: {e}")
            # 回退到立即更新
            if hasattr(component, 'update'):
                component.update()

    def _process_pending_updates(self):
        """处理待更新的组件（优化版本）"""
        # 使用集合交集操作，比逐个检查更高效
        visible_pending = self._pending_updates & self._visible_components
        for component in visible_pending:
            try:
                component.update()
            except Exception as e:
                print(f"更新组件时出错: {e}")
        self._pending_updates.clear()
