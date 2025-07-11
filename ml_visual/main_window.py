#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
应用程序的主界面和菜单管理
"""

import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                             QToolBar, QMenuBar, QStatusBar, QMessageBox,
                             QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

from .canvas import MLCanvas
from .component_library import ComponentLibrary
from .property_panel import PropertyPanel
from .startup_dialog import StartupDialog


class MLVisualizationUI(QMainWindow):
    """主窗口"""

    def __init__(self, project_path=None):
        super().__init__()
        self.current_file = project_path
        self.is_modified = False
        self.init_ui()
        self.connect_signals()
        self.dia=None
        # 如果有项目路径，则加载项目
        if project_path:
            self.load_project_file(project_path)

    @staticmethod
    def show_startup_dialog():
        """显示启动对话框并返回主窗口实例"""
        dialog = StartupDialog()
        # 连接新建项目信号
        def on_new_project():
            dialog.accept()

        dialog.new_project_requested.connect(on_new_project)

        if dialog.exec_() == StartupDialog.Accepted:
            project_path = dialog.get_selected_project()
            mlv=MLVisualizationUI(project_path)
            mlv.dia=dialog
            return mlv
        else:
            return None
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("机器学习可视化工具")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主界面
        self.create_main_widget()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
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
        edit_menu = menubar.addMenu('编辑(&E)')
        
        undo_action = edit_menu.addAction('撤销(&U)')
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        
        redo_action = edit_menu.addAction('重做(&R)')
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        
        edit_menu.addSeparator()
        
        copy_action = edit_menu.addAction('复制(&C)')
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        
        paste_action = edit_menu.addAction('粘贴(&P)')
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        
        delete_action = edit_menu.addAction('删除(&D)')
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected)
        
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
        
        # 运行菜单
        run_menu = menubar.addMenu('运行(&R)')
        
        execute_action = run_menu.addAction('执行流程(&E)')
        execute_action.setShortcut('F5')
        execute_action.triggered.connect(self.run_pipeline)
        
        stop_action = run_menu.addAction('停止执行(&S)')
        stop_action.setShortcut('Shift+F5')
        stop_action.triggered.connect(self.stop_pipeline)
        
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
        toolbar.addAction('运行', self.run_pipeline)
        toolbar.addAction('停止', self.stop_pipeline)
        
    def create_main_widget(self):
        """创建主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板 - 组件库
        self.component_library = ComponentLibrary()
        self.component_library.setMaximumWidth(250)
        self.component_library.setMinimumWidth(200)
        
        # 中间 - 画布
        self.canvas = MLCanvas()
        
        # 右侧面板 - 属性配置
        self.property_panel = PropertyPanel()
        self.property_panel.setMaximumWidth(300)
        self.property_panel.setMinimumWidth(250)
        
        # 添加到分割器
        splitter.addWidget(self.component_library)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.property_panel)
        
        # 设置分割器比例
        splitter.setSizes([250, 850, 300])
        
        main_layout.addWidget(splitter)
        
    def connect_signals(self):
        """连接信号"""
        # 画布信号
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.component_added.connect(self.on_component_added)
        self.canvas.connection_created.connect(self.on_connection_created)
        
        # 属性面板信号
        self.property_panel.property_changed.connect(self.on_property_changed)
        
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
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    
                    self.canvas.load_workflow_data(project_data)
                    self.current_file = file_path
                    self.set_modified(False)
                    self.statusBar().showMessage(f"已打开: {file_path}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"打开文件失败:\n{str(e)}")
        
    def save_project(self):
        """保存项目"""
        if self.current_file:
            self._save_to_file(self.current_file)
            paths=self.dia.settings.value('recent_projects', [])
            if self.current_file in paths:
                paths.remove(self.current_file)
            paths.insert(0, self.current_file)
            paths=paths[:10]
            self.dia.settings.setValue('recent_projects', paths)
        else:
            self.save_project_as()
            
    def save_project_as(self):
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "", "ML Visual项目 (*.mlv);;所有文件 (*)"
        )
        if file_path:
            self._save_to_file(file_path)
            
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
        """关闭事件"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
        
    def undo(self):
        """撤销"""
        self.statusBar().showMessage("撤销功能待实现")
        
    def redo(self):
        """重做"""
        self.statusBar().showMessage("重做功能待实现")
        
    def copy(self):
        """复制"""
        self.statusBar().showMessage("复制功能待实现")
        
    def paste(self):
        """粘贴"""
        self.statusBar().showMessage("粘贴功能待实现")
        
    def delete_selected(self):
        """删除选中项"""
        selected_items = self.canvas.scene.selectedItems()
        for item in selected_items:
            if hasattr(item, 'parent_component'):  # 是组件
                self.canvas.remove_component(item)
        self.statusBar().showMessage("已删除选中项")
        
    def zoom_in(self):
        """放大"""
        self.canvas.scale(1.2, 1.2)
        
    def zoom_out(self):
        """缩小"""
        self.canvas.scale(0.8, 0.8)
        
    def fit_to_window(self):
        """适应窗口"""
        self.canvas.fit_to_contents()
        
    def run_pipeline(self):
        """执行流程"""
        workflow_data = self.canvas.get_workflow_data()
        if not workflow_data['components']:
            QMessageBox.information(self, "提示", "请先添加组件到画布")
            return
            
        self.statusBar().showMessage("执行机器学习流程...")
        # 这里可以调用后端执行引擎
        QTimer.singleShot(2000, lambda: self.statusBar().showMessage("流程执行完成"))
        
    def stop_pipeline(self):
        """停止执行"""
        self.statusBar().showMessage("停止执行")
        
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
