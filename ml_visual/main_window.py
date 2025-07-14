#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
应用程序的主界面和菜单管理
"""

import json
from typing import Optional, Any
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
                             QToolBar, QMenuBar, QStatusBar, QMessageBox,
                             QFileDialog, QApplication, QLabel, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QCloseEvent

from .canvas import MLCanvas
from .component_library import ComponentLibrary
from .property_panel import PropertyPanel
from .startup_dialog import StartupDialog
from .execution_panel import ExecutionPanel
from .data_preview import DataPreviewPanel
from .backend_adapter import backend_adapter
from .shortcut_manager import ShortcutManager
from .theme_manager import theme_manager
from .config_manager import config_manager, get_ui_config, get_config


class MLVisualizationUI(QMainWindow):
    """主窗口"""

    def __init__(self, project_path=None):
        super().__init__()
        self.current_file = project_path
        self.is_modified = False

        # 快捷键管理器
        self.shortcut_manager = ShortcutManager(self)

        self.init_ui()
        self.connect_signals()
        self.setup_shortcuts()
        # 初始化最近文件管理
        from .utils import FileManager
        self.file_manager = FileManager()
        # 如果有项目路径，则加载项目
        if project_path:
            self.load_project_file(project_path)

    @staticmethod
    def show_startup_dialog() -> Optional['MLVisualizationUI']:
        """显示启动对话框并返回主窗口实例"""
        dialog = StartupDialog()
        # 连接新建项目信号
        def on_new_project():
            dialog.accept()
            dialog.selected_project_path=None

        dialog.new_project_requested.connect(on_new_project)

        if dialog.exec_() == StartupDialog.Accepted:
            project_path = dialog.get_selected_project()
            mlv = MLVisualizationUI(project_path)
            # 不需要保存dialog引用，它会在函数结束时自动清理
            return mlv
        else:
            return None
        
    def init_ui(self) -> None:
        """初始化用户界面"""
        # 从配置获取窗口设置
        ui_config = get_ui_config()
        window_config = ui_config.get('window', {})

        title = window_config.get('title', '机器学习可视化工具')
        default_size = window_config.get('default_size', [1400, 900])
        min_size = window_config.get('minimum_size', [800, 600])
        geometry = window_config.get('geometry', [100, 100])

        self.setWindowTitle(title)
        self.setGeometry(geometry[0], geometry[1], default_size[0], default_size[1])
        self.setMinimumSize(min_size[0], min_size[1])
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主界面
        self.create_main_widget()
        
        # 创建增强状态栏
        self.create_enhanced_status_bar()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 从配置获取菜单文本
        ui_config = get_ui_config()
        menu_config = ui_config.get('menu', {})

        # 文件菜单
        file_menu = menubar.addMenu(menu_config.get('file_text', '文件(&F)'))
        
        new_action = file_menu.addAction('新建(&N)')
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        
        open_action = file_menu.addAction('打开(&O)')
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        
        save_action = file_menu.addAction('保存(&S)')
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        
        save_as_action = file_menu.addAction('另存为(&A)')
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('退出(&X)')
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu(menu_config.get('edit_text', '编辑(&E)'))
        
        self.undo_action = edit_menu.addAction('撤销(&U)')
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = edit_menu.addAction('重做(&R)')
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)

        edit_menu.addSeparator()

        self.copy_action = edit_menu.addAction('复制(&C)')
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.copy)
        self.copy_action.setEnabled(False)

        self.cut_action = edit_menu.addAction('剪切(&X)')
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.triggered.connect(self.cut)
        self.cut_action.setEnabled(False)

        self.paste_action = edit_menu.addAction('粘贴(&V)')
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.paste)
        self.paste_action.setEnabled(False)

        edit_menu.addSeparator()

        self.delete_action = edit_menu.addAction('删除(&D)')
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.delete)
        self.delete_action.setEnabled(False)

        self.select_all_action = edit_menu.addAction('全选(&A)')
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.select_all)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图(&V)')
        
        zoom_in_action = view_menu.addAction('放大(&I)')
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        
        zoom_out_action = view_menu.addAction('缩小(&O)')
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        
        fit_action = view_menu.addAction('适应窗口(&F)')
        fit_action.triggered.connect(self.fit_to_window)

        view_menu.addSeparator()

        # 主题菜单
        theme_menu = view_menu.addMenu('主题(&T)')

        light_theme_action = theme_menu.addAction('浅色主题')
        light_theme_action.triggered.connect(lambda: self.switch_theme('light'))

        dark_theme_action = theme_menu.addAction('深色主题')
        dark_theme_action.triggered.connect(lambda: self.switch_theme('dark'))
        
        # 运行菜单
        run_menu = menubar.addMenu('运行(&R)')
        
        execute_action = run_menu.addAction('执行流程(&E)')
        execute_action.setShortcut('F5')
        execute_action.triggered.connect(lambda: self.execution_panel.start_execution())

        stop_action = run_menu.addAction('停止执行(&S)')
        stop_action.setShortcut('Shift+F5')
        stop_action.triggered.connect(lambda: self.execution_panel.stop_execution())
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = help_menu.addAction('关于(&A)')
        about_action.triggered.connect(self.show_about)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 文件操作
        toolbar.addAction('新建', self.new_project)
        toolbar.addAction('打开', self.open_project)
        toolbar.addAction('保存', self.save_project)
        toolbar.addSeparator()
        
        # 编辑操作
        toolbar.addAction('撤销', self.undo)
        toolbar.addAction('重做', self.redo)
        toolbar.addSeparator()
        
        # 视图操作
        toolbar.addAction('放大', self.zoom_in)
        toolbar.addAction('缩小', self.zoom_out)
        toolbar.addAction('适应', self.fit_to_window)
        toolbar.addSeparator()
        
        # 运行操作
        toolbar.addAction('运行', lambda: self.execution_panel.start_execution())
        toolbar.addAction('停止', lambda: self.execution_panel.stop_execution())
        
    def create_main_widget(self):
        """创建主界面 - 重新设计布局突出主次功能"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 从配置获取布局设置
        ui_config = get_ui_config()
        layout_config = ui_config.get('layout', {})
        main_margins = layout_config.get('main_margins', [5, 5, 5, 5])
        main_spacing = layout_config.get('main_spacing', 5)

        # 主布局 - 垂直布局，分为工作区和底部面板
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(*main_margins)
        main_layout.setSpacing(main_spacing)

        # 创建工作区（主要区域）
        work_area = self.create_work_area()
        main_layout.addWidget(work_area, 4)  # 占主要空间

        # 创建底部面板（次要区域）
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel, 1)  # 占较少空间

    def create_work_area(self):
        """创建工作区 - 包含组件库、画布和属性面板"""
        work_splitter = QSplitter(Qt.Horizontal)

        # 左侧：组件库（可折叠）
        left_panel = self.create_left_panel()
        work_splitter.addWidget(left_panel)

        # 中间：画布区域（主要工作区）
        canvas_area = self.create_canvas_area()
        work_splitter.addWidget(canvas_area)

        # 右侧：属性和预览面板（可折叠）
        right_panel = self.create_right_panel()
        work_splitter.addWidget(right_panel)

        # 从配置获取分割器比例
        ui_config = get_ui_config()
        panels_config = ui_config.get('panels', {})
        splitter_sizes = panels_config.get('splitter_sizes', [300, 900, 300])

        # 设置分割器比例
        work_splitter.setSizes(splitter_sizes)
        work_splitter.setCollapsible(0, True)  # 左侧可折叠
        work_splitter.setCollapsible(2, True)  # 右侧可折叠

        return work_splitter

    def create_left_panel(self):
        """创建左侧面板 - 组件库"""
        from PyQt5.QtWidgets import QFrame

        # 从配置获取面板大小
        ui_config = get_ui_config()
        panels_config = ui_config.get('panels', {})
        left_min_width = panels_config.get('left_min_width', 200)
        left_max_width = panels_config.get('left_max_width', 400)

        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.StyledPanel)
        left_frame.setMinimumWidth(left_min_width)
        left_frame.setMaximumWidth(left_max_width)

        layout = QVBoxLayout(left_frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标题
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtGui import QFont
        title = QLabel("组件库")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(title)

        # 组件库
        self.component_library = ComponentLibrary()
        layout.addWidget(self.component_library)

        return left_frame

    def create_canvas_area(self):
        """创建画布区域 - 主要工作区"""
        from PyQt5.QtWidgets import QFrame

        canvas_frame = QFrame()
        canvas_frame.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(canvas_frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # 画布工具栏
        canvas_toolbar = self.create_canvas_toolbar()
        layout.addWidget(canvas_toolbar)

        # 画布
        self.canvas = MLCanvas()
        self.canvas.setStyleSheet("""
            MLCanvas {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.canvas)

        return canvas_frame

    def create_canvas_toolbar(self):
        """创建画布工具栏"""
        # QSizePolicy和QSpacerItem已在顶部导入

        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 2px;
            }
            QToolButton {
                padding: 4px 8px;
                margin: 1px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #d5dbdb;
            }
        """)

        # 添加常用操作
        toolbar.addAction("▶ 运行", lambda: self.execution_panel.start_execution())
        toolbar.addAction("⏹ 停止", lambda: self.execution_panel.stop_execution())
        toolbar.addSeparator()
        toolbar.addAction("↶ 撤销", self.undo)
        toolbar.addAction("↷ 重做", self.redo)
        toolbar.addSeparator()
        toolbar.addAction("📋 复制", self.copy)
        toolbar.addAction("✂ 剪切", self.cut)
        toolbar.addAction("📄 粘贴", self.paste)
        toolbar.addSeparator()
        toolbar.addAction("🔍+ 放大", self.zoom_in)
        toolbar.addAction("🔍- 缩小", self.zoom_out)
        toolbar.addAction("⬜ 适应", self.fit_to_window)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # 添加状态信息
        self.canvas_status = QLabel("就绪")
        self.canvas_status.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        toolbar.addWidget(self.canvas_status)

        return toolbar

    def create_right_panel(self):
        """创建右侧面板 - 属性和预览"""
        from PyQt5.QtWidgets import QTabWidget, QFrame

        # 从配置获取面板大小
        ui_config = get_ui_config()
        panels_config = ui_config.get('panels', {})
        right_min_width = panels_config.get('right_min_width', 250)
        right_max_width = panels_config.get('right_max_width', 400)

        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_frame.setMinimumWidth(right_min_width)
        right_frame.setMaximumWidth(right_max_width)

        layout = QVBoxLayout(right_frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # 使用标签页组织右侧面板
        right_tabs = QTabWidget()
        right_tabs.setTabPosition(QTabWidget.North)

        # 属性配置标签页
        self.property_panel = PropertyPanel()
        right_tabs.addTab(self.property_panel, "⚙ 属性")

        # 数据预览标签页
        self.data_preview_panel = DataPreviewPanel()
        right_tabs.addTab(self.data_preview_panel, "📊 数据")

        layout.addWidget(right_tabs)

        return right_frame

    def create_bottom_panel(self):
        """创建底部面板 - 执行状态和日志"""
        from PyQt5.QtWidgets import QTabWidget, QFrame

        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.StyledPanel)
        bottom_frame.setMaximumHeight(300)
        bottom_frame.setMinimumHeight(150)

        layout = QVBoxLayout(bottom_frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # 使用标签页组织底部面板
        bottom_tabs = QTabWidget()
        bottom_tabs.setTabPosition(QTabWidget.North)

        # 执行面板标签页
        self.execution_panel = ExecutionPanel()
        bottom_tabs.addTab(self.execution_panel, "🚀 执行")

        # 可以添加更多标签页，如调试信息、帮助等
        # debug_panel = QWidget()
        # bottom_tabs.addTab(debug_panel, "🐛 调试")

        layout.addWidget(bottom_tabs)

        return bottom_frame
        
    def connect_signals(self):
        """连接信号"""
        # 画布信号
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.component_added.connect(self.on_component_added)
        self.canvas.connection_created.connect(self.on_connection_created)
        self.canvas.can_undo_changed.connect(self.on_can_undo_changed)
        self.canvas.can_redo_changed.connect(self.on_can_redo_changed)
        self.canvas.selection_changed.connect(self.on_selection_changed)

        # 属性面板信号
        self.property_panel.property_changed.connect(self.on_property_changed)

        # 执行面板信号
        self.execution_panel.execution_requested.connect(self.on_execution_requested)
        self.execution_panel.stop_requested.connect(self.on_stop_requested)

        # 数据预览面板信号
        self.data_preview_panel.data_requested.connect(self.on_data_requested)
        self.data_preview_panel.statistics_requested.connect(self.on_statistics_requested)
        self.data_preview_panel.chart_requested.connect(self.on_chart_requested)

        # 后端适配器信号
        backend_adapter.execution_started.connect(self.on_execution_started)
        backend_adapter.execution_progress.connect(self.on_execution_progress)
        backend_adapter.execution_completed.connect(self.on_execution_completed)
        backend_adapter.component_completed.connect(self.on_component_completed)
        backend_adapter.data_preview_ready.connect(self.on_data_preview_ready)
        backend_adapter.statistics_ready.connect(self.on_statistics_ready)
        backend_adapter.chart_ready.connect(self.on_chart_ready)
        backend_adapter.error_occurred.connect(self.on_backend_error)
        
    def on_component_selected(self, component):
        """组件选择处理"""
        if component:
            self.statusBar().showMessage(f"已选择组件: {component.name}")
            self.property_panel.show_component_properties(component)
        else:
            self.statusBar().showMessage("就绪")
            self.property_panel.show_empty_state()
            
    def on_component_added(self, component):
        """组件添加处理"""
        self.statusBar().showMessage(f"已添加组件: {component.name}")
        self.set_modified(True)
        
    def on_connection_created(self, connection):
        """连接创建处理"""
        start_name = connection.start_port.parent_component.name
        end_name = connection.end_port.parent_component.name
        self.statusBar().showMessage(f"已连接: {start_name} → {end_name}")
        self.set_modified(True)
        
    def on_property_changed(self, component, prop_name, value):
        """属性改变处理"""
        self.statusBar().showMessage(f"属性已更改: {component.name}.{prop_name} = {value}")
        self.set_modified(True)

    def on_execution_requested(self):
        """执行请求处理"""
        workflow_data = self.canvas.get_workflow_data()
        if not workflow_data['components']:
            QMessageBox.information(self, "提示", "请先添加组件到画布")
            return

        # 通过后端适配器执行工作流程
        execution_id = backend_adapter.execute_workflow(workflow_data)
        self.current_execution_id = execution_id
        self.statusBar().showMessage("正在执行机器学习流程...")

    def on_stop_requested(self):
        """停止请求处理"""
        if hasattr(self, 'current_execution_id'):
            backend_adapter.stop_execution(self.current_execution_id)
            self.statusBar().showMessage("正在停止执行...")

    def on_data_requested(self, data_id):
        """数据请求处理"""
        backend_adapter.get_data_preview(data_id)

    def on_statistics_requested(self, data_id):
        """统计信息请求处理"""
        backend_adapter.get_data_statistics(data_id)

    def on_chart_requested(self, chart_type, data_id, config):
        """图表请求处理"""
        backend_adapter.generate_chart(chart_type, data_id, config)

    def on_execution_started(self, execution_id):
        """执行开始处理"""
        self.execution_panel.add_log_message("工作流程开始执行", "INFO")

    def on_execution_progress(self, execution_id, progress, current_step):
        """执行进度处理"""
        self.execution_panel.update_progress(progress, current_step)
        self.execution_panel.add_log_message(f"正在执行: {current_step}", "INFO")

    def on_execution_completed(self, execution_id, success, results):
        """执行完成处理"""
        self.execution_panel.execution_completed(success, results)
        if success:
            self.statusBar().showMessage("工作流程执行完成")
        else:
            self.statusBar().showMessage("工作流程执行失败")

    def on_component_completed(self, execution_id, component_id, success, result):
        """组件执行完成处理"""
        status = "成功" if success else "失败"
        message = f"组件 {result.get('name', component_id)} 执行{status}"
        level = "SUCCESS" if success else "ERROR"
        self.execution_panel.add_log_message(message, level)

    def on_data_preview_ready(self, data_id, preview_data):
        """数据预览就绪处理"""
        self.data_preview_panel.update_data_preview(preview_data)

    def on_statistics_ready(self, data_id, statistics):
        """统计信息就绪处理"""
        self.data_preview_panel.update_statistics(statistics)

    def on_chart_ready(self, chart_id, chart_data):
        """图表就绪处理"""
        self.data_preview_panel.update_visualization(chart_data)

    def on_backend_error(self, error_code, error_message, details):
        """后端错误处理"""
        self.execution_panel.add_log_message(f"错误: {error_message}", "ERROR")
        QMessageBox.critical(self, "执行错误", f"{error_message}\n\n详情: {details}")
        
    def set_modified(self, modified):
        """设置修改状态"""
        self.is_modified = modified
        title = "机器学习可视化工具"
        if self.current_file:
            title += f" - {self.current_file}"
        if modified:
            title += " *"
        self.setWindowTitle(title)
    
    # 菜单和工具栏事件处理方法
    def new_project(self):
        """新建项目"""
        if self.check_save_changes():
            self.canvas.clear_canvas()
            self.property_panel.show_empty_state()
            self.current_file = None
            self.set_modified(False)
            self.statusBar().showMessage("新建项目")
        
    def open_project(self):
        """打开项目"""
        if self.check_save_changes():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "打开项目", "", "ML Visual项目 (*.mlv);;所有文件 (*)"
            )
            if file_path:
                try:
                    self.load_project_file(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"打开文件失败:\n{str(e)}")
        
    def save_project(self):
        """保存项目"""
        if self.current_file:
            self._save_to_file(self.current_file)
            self.file_manager.add_recent_file(self.current_file)
        else:
            self.save_project_as()
            if self.current_file:
                self.file_manager.add_recent_file(self.current_file)
            
    def save_project_as(self):
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "", "ML Visual项目 (*.mlv);;所有文件 (*)"
        )
        if file_path:
            self._save_to_file(file_path)

    def save_as(self):
        """另存为（快捷键方法）"""
        self.save_project_as()
            
    def _save_to_file(self, file_path):
        """保存到文件"""
        try:
            project_data = self.canvas.get_workflow_data()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.current_file = file_path
            self.set_modified(False)
            self.statusBar().showMessage(f"已保存: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件失败:\n{str(e)}")

    def load_project_file(self, file_path):
        """加载项目文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            self.canvas.load_workflow_data(project_data)
            self.current_file = file_path
            self.set_modified(False)
            self.statusBar().showMessage(f"已打开: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开文件失败:\n{str(e)}")

    def check_save_changes(self):
        """检查是否需要保存更改"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "保存更改", 
                "项目已修改，是否保存更改？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_project()
                return not self.is_modified  # 如果保存失败，返回False
            elif reply == QMessageBox.Cancel:
                return False
        return True
        
    def closeEvent(self, event):
        """关闭事件（增强清理）"""
        if self.check_save_changes():
            self.cleanup_resources()
            event.accept()
        else:
            event.ignore()

    def cleanup_resources(self):
        """清理资源"""
        try:
            # 清理画布资源
            if hasattr(self, 'canvas'):
                self.canvas.scene.clear()
                self.canvas.components.clear()
                self.canvas.connections.clear()

            # 清理命令历史
            if hasattr(self, 'canvas') and hasattr(self.canvas, 'command_manager'):
                if hasattr(self.canvas.command_manager, 'history'):
                    self.canvas.command_manager.history.clear()

            # 强制垃圾回收
            import gc
            gc.collect()

        except Exception as e:
            print(f"清理资源时出错: {e}")

    def create_enhanced_status_bar(self):
        """创建增强状态栏"""
        status_bar = self.statusBar()

        # 主状态标签
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)

        # 添加分隔符
        status_bar.addPermanentWidget(QLabel("|"))

        # 组件计数
        self.component_count_label = QLabel("组件: 0")
        status_bar.addPermanentWidget(self.component_count_label)

        # 添加分隔符
        status_bar.addPermanentWidget(QLabel("|"))

        # 缩放级别
        self.zoom_label = QLabel("缩放: 100%")
        status_bar.addPermanentWidget(self.zoom_label)

        # 添加分隔符
        status_bar.addPermanentWidget(QLabel("|"))

        # 内存使用（如果可用）
        try:
            from .memory_manager import get_memory_usage
            memory_info = get_memory_usage()
            if memory_info and memory_info.get('rss', 0) > 0:
                self.memory_label = QLabel(f"内存: {memory_info['rss']:.0f}MB")
                status_bar.addPermanentWidget(self.memory_label)

                # 定时更新内存信息
                from PyQt5.QtCore import QTimer
                self.memory_timer = QTimer()
                self.memory_timer.timeout.connect(self.update_memory_status)
                self.memory_timer.start(5000)  # 每5秒更新
        except:
            pass

    def update_status(self, message):
        """更新状态消息"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)

    def update_component_count(self):
        """更新组件计数"""
        if hasattr(self, 'component_count_label') and hasattr(self, 'canvas'):
            count = len(self.canvas.components)
            self.component_count_label.setText(f"组件: {count}")

    def update_zoom_level(self):
        """更新缩放级别"""
        if hasattr(self, 'zoom_label') and hasattr(self, 'canvas'):
            scale = self.canvas.transform().m11()
            zoom_percent = int(scale * 100)
            self.zoom_label.setText(f"缩放: {zoom_percent}%")

    def update_memory_status(self):
        """更新内存状态"""
        try:
            from .memory_manager import get_memory_usage
            memory_info = get_memory_usage()
            if memory_info and hasattr(self, 'memory_label'):
                self.memory_label.setText(f"内存: {memory_info['rss']:.0f}MB")
        except:
            pass
        
    def undo(self):
        """撤销"""
        self.canvas.undo()
        self.statusBar().showMessage(f"已执行: {self.canvas.get_undo_text()}")

    def redo(self):
        """重做"""
        self.canvas.redo()
        self.statusBar().showMessage(f"已执行: {self.canvas.get_redo_text()}")

    def on_can_undo_changed(self, can_undo):
        """撤销状态改变"""
        self.undo_action.setEnabled(can_undo)
        if can_undo:
            self.undo_action.setText(self.canvas.get_undo_text())
        else:
            self.undo_action.setText("撤销(&U)")

    def on_can_redo_changed(self, can_redo):
        """重做状态改变"""
        self.redo_action.setEnabled(can_redo)
        if can_redo:
            self.redo_action.setText(self.canvas.get_redo_text())
        else:
            self.redo_action.setText("重做(&R)")

    def copy(self):
        """复制"""
        self.canvas.copy_selected()
        self.statusBar().showMessage("已复制选中的组件")

    def cut(self):
        """剪切"""
        self.canvas.cut_selected()
        self.statusBar().showMessage("已剪切选中的组件")

    def paste(self):
        """粘贴"""
        self.canvas.paste()
        self.statusBar().showMessage("已粘贴组件")

    def delete(self):
        """删除"""
        self.canvas.delete_selected()
        self.statusBar().showMessage("已删除选中的组件")

    def select_all(self):
        """全选"""
        self.canvas.select_all()
        self.statusBar().showMessage("已全选组件")

    def on_selection_changed(self, has_selection):
        """选择状态改变（优化UI更新性能）"""
        # 批量更新UI状态，减少重绘次数
        self.copy_action.setEnabled(has_selection)
        self.cut_action.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)

        # 更新粘贴按钮状态
        from .clipboard_manager import clipboard_manager
        self.paste_action.setEnabled(clipboard_manager.has_content())

        # 更新画布状态显示
        if hasattr(self, 'canvas_status'):
            selected_count = len(self.canvas.get_selected_components())
            if selected_count > 0:
                self.canvas_status.setText(f"已选择 {selected_count} 个组件")
            else:
                self.canvas_status.setText("就绪")

    def setup_shortcuts(self):
        """设置快捷键回调"""
        # 文件操作
        self.shortcut_manager.set_callback('new_project', self.new_project)
        self.shortcut_manager.set_callback('open_project', self.open_project)
        self.shortcut_manager.set_callback('save_project', self.save_project)
        self.shortcut_manager.set_callback('save_as', self.save_as)
        self.shortcut_manager.set_callback('quit', self.close)

        # 编辑操作
        self.shortcut_manager.set_callback('undo', self.undo)
        self.shortcut_manager.set_callback('redo', self.redo)
        self.shortcut_manager.set_callback('copy', self.copy)
        self.shortcut_manager.set_callback('cut', self.cut)
        self.shortcut_manager.set_callback('paste', self.paste)
        self.shortcut_manager.set_callback('delete', self.delete)
        self.shortcut_manager.set_callback('select_all', self.select_all)

        # 视图操作
        self.shortcut_manager.set_callback('zoom_in', self.zoom_in)
        self.shortcut_manager.set_callback('zoom_out', self.zoom_out)
        self.shortcut_manager.set_callback('zoom_fit', self.fit_to_window)

        # 运行操作
        self.shortcut_manager.set_callback('run', lambda: self.execution_panel.start_execution())
        self.shortcut_manager.set_callback('stop', lambda: self.execution_panel.stop_execution())

        # 帮助操作
        self.shortcut_manager.set_callback('about', self.show_about)
        self.shortcut_manager.set_callback('shortcuts', self.show_shortcuts_help)

    def show_shortcuts_help(self):
        """显示快捷键帮助"""
        help_text = self.shortcut_manager.create_shortcuts_help_text()
        QMessageBox.information(self, "快捷键帮助", help_text)

    def switch_theme(self, theme_name: str):
        """切换主题"""
        if theme_manager.apply_theme(theme_name):
            self.statusBar().showMessage(f"已切换到{theme_manager.get_theme_info(theme_name).get('name', theme_name)}主题")
        else:
            self.statusBar().showMessage(f"切换主题失败: {theme_name}")
        

        
    def zoom_in(self):
        """放大"""
        self.canvas.scale(1.2, 1.2)
        
    def zoom_out(self):
        """缩小"""
        self.canvas.scale(0.8, 0.8)
        
    def fit_to_window(self):
        """适应窗口"""
        self.canvas.fit_to_contents()
        

        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于", 
            "机器学习可视化工具 v1.0\n\n"
            "基于PyQt5开发的机器学习流程可视化工具\n"
            "类似Logisim的界面设计，支持拖拽组件构建ML流程\n\n"
            "功能特性：\n"
            "• 可视化组件库\n"
            "• 拖拽式流程构建\n"
            "• 属性配置面板\n"
            "• 项目保存/加载\n"
            "• 后端接口预留"
        )
