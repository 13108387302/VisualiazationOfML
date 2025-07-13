#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动对话框模块
提供项目选择和新建功能
"""

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QFileDialog, QMessageBox, QFrame, QSplitter,
                             QTextEdit, QGroupBox, QGridLayout, QSpacerItem,
                             QSizePolicy, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QIcon


class ProjectItem(QListWidgetItem):
    """项目列表项"""
    
    def __init__(self, project_path, project_info=None):
        super().__init__()
        self.project_path = project_path
        self.project_info = project_info or {}
        
        # 设置显示文本
        project_name = self.project_info.get('name', os.path.basename(project_path))
        self.setText(project_name)
        
        # 设置工具提示
        tooltip = f"路径: {project_path}"
        if 'description' in self.project_info:
            tooltip += f"\n描述: {self.project_info['description']}"
        if 'last_modified' in self.project_info:
            tooltip += f"\n修改时间: {self.project_info['last_modified']}"
        self.setToolTip(tooltip)


class StartupDialog(QDialog):
    """启动对话框"""
    
    project_selected = pyqtSignal(str)  # 项目路径
    new_project_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('MLVisual', 'RecentProjects')
        self.selected_project_path = None
        self.init_ui()
        self.load_recent_projects()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("机器学习可视化工具 - 项目启动")
        self.setFixedSize(1000, 800)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 标题区域
        self.create_header(main_layout)
        
        # 内容区域
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧 - 项目列表
        self.create_project_list(content_splitter)
        
        # 右侧 - 项目详情和操作
        self.create_project_details(content_splitter)
        
        content_splitter.setSizes([400, 400])
        main_layout.addWidget(content_splitter)
        
        # 底部按钮
        self.create_buttons(main_layout)
        
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #cce7ff;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f3ff;
            }
        """)
        
    def create_header(self, layout):
        """创建标题区域"""
        header_frame = QFrame()
        header_frame.setFixedHeight(130)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # 图标（可以后续添加）
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet("background-color: #0078d4; border-radius: 32px;")
        
        # 标题文本
        title_layout = QVBoxLayout()
        
        title_label = QLabel("机器学习可视化工具")
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: #333333;")
        
        subtitle_label = QLabel("选择现有项目或创建新项目开始您的机器学习之旅")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #666666;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
    def create_project_list(self, splitter):
        """创建项目列表"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 最近项目组
        recent_group = QGroupBox("最近项目")
        recent_layout = QVBoxLayout(recent_group)
        
        self.project_list = QListWidget()
        self.project_list.itemSelectionChanged.connect(self.on_project_selection_changed)
        self.project_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        
        recent_layout.addWidget(self.project_list)
        
        # 项目操作按钮
        project_buttons_layout = QHBoxLayout()
        
        self.open_other_btn = QPushButton("浏览其他项目...")
        self.open_other_btn.clicked.connect(self.browse_project)
        
        self.remove_btn = QPushButton("从列表移除")
        self.remove_btn.clicked.connect(self.remove_project)
        self.remove_btn.setEnabled(False)
        
        project_buttons_layout.addWidget(self.open_other_btn)
        project_buttons_layout.addWidget(self.remove_btn)
        project_buttons_layout.addStretch()
        
        recent_layout.addLayout(project_buttons_layout)
        
        left_layout.addWidget(recent_group)
        splitter.addWidget(left_widget)
        
    def create_project_details(self, splitter):
        """创建项目详情区域"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 项目详情组
        details_group = QGroupBox("项目详情")
        details_layout = QVBoxLayout(details_group)
        
        self.project_details = QTextEdit()
        self.project_details.setReadOnly(True)
        self.project_details.setMaximumHeight(200)
        self.project_details.setText("请选择一个项目查看详情")
        
        details_layout.addWidget(self.project_details)
        
        # 快速操作组
        actions_group = QGroupBox("快速操作")
        actions_layout = QGridLayout(actions_group)
        
        # 新建项目按钮
        self.new_project_btn = QPushButton("新建项目")
        self.new_project_btn.setFixedHeight(50)
        self.new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.new_project_btn.clicked.connect(self.new_project)
        
        # 示例项目按钮
        self.demo_project_btn = QPushButton("创建示例项目")
        self.demo_project_btn.setFixedHeight(40)
        self.demo_project_btn.clicked.connect(self.create_demo_project)
        
        # 帮助按钮
        self.help_btn = QPushButton("使用帮助")
        self.help_btn.setFixedHeight(40)
        self.help_btn.clicked.connect(self.show_help)
        
        actions_layout.addWidget(self.new_project_btn, 0, 0, 1, 2)
        actions_layout.addWidget(self.demo_project_btn, 1, 0)
        actions_layout.addWidget(self.help_btn, 1, 1)
        
        right_layout.addWidget(details_group)
        right_layout.addWidget(actions_group)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
    def create_buttons(self, layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        
        # 左侧信息
        info_label = QLabel("提示：双击项目名称可直接打开项目")
        info_label.setStyleSheet("color: #666666; font-size: 20px;")
        
        button_layout.addWidget(info_label)
        button_layout.addStretch()
        
        # 右侧按钮
        self.open_btn = QPushButton("打开项目")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_project)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def load_recent_projects(self):
        """加载最近项目列表"""
        recent_projects = self.settings.value('recent_projects', [])
        
        for project_path in recent_projects:
            if project_path and os.path.exists(project_path):
                project_info = self.load_project_info(project_path)
                item = ProjectItem(project_path, project_info)
                self.project_list.addItem(item)
            else:
                # 移除不存在的项目
                self.remove_from_recent(project_path)
                
    def load_project_info(self, project_path):
        """加载项目信息"""
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 获取文件修改时间
            import time
            mtime = os.path.getmtime(project_path)
            last_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            
            return {
                'name': os.path.splitext(os.path.basename(project_path))[0],
                'description': f"包含 {len(data.get('components', []))} 个组件",
                'last_modified': last_modified,
                'components_count': len(data.get('components', [])),
                'connections_count': len(data.get('connections', []))
            }
        except Exception:
            return {
                'name': os.path.splitext(os.path.basename(project_path))[0],
                'description': "无法读取项目信息"
            }
            
    def on_project_selection_changed(self):
        """项目选择改变处理"""
        current_item = self.project_list.currentItem()
        
        if current_item:
            self.selected_project_path = current_item.project_path
            self.open_btn.setEnabled(True)
            self.remove_btn.setEnabled(True)
            
            # 更新项目详情
            self.update_project_details(current_item)
        else:
            self.selected_project_path = None
            self.open_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            self.project_details.setText("请选择一个项目查看详情")
            
    def update_project_details(self, item):
        """更新项目详情显示"""
        info = item.project_info
        details_text = f"""
<h3>{info.get('name', '未知项目')}</h3>
<p><b>路径:</b> {item.project_path}</p>
<p><b>描述:</b> {info.get('description', '无描述')}</p>
<p><b>最后修改:</b> {info.get('last_modified', '未知')}</p>
<p><b>组件数量:</b> {info.get('components_count', 0)}</p>
<p><b>连接数量:</b> {info.get('connections_count', 0)}</p>
        """
        self.project_details.setHtml(details_text)
        
    def on_project_double_clicked(self, item):
        """项目双击处理"""
        self.selected_project_path = item.project_path
        self.accept()
        
    def browse_project(self):
        """浏览其他项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择项目文件", "", "ML Visual项目 (*.mlv);;所有文件 (*)"
        )
        
        if file_path:
            self.add_to_recent(file_path)
            self.selected_project_path = file_path
            self.accept()
            
    def remove_project(self):
        """从列表移除项目"""
        current_item = self.project_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self, "确认移除", 
                f"确定要从最近项目列表中移除 '{current_item.text()}' 吗？\n\n注意：这不会删除项目文件。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.remove_from_recent(current_item.project_path)
                self.project_list.takeItem(self.project_list.row(current_item))
                
    def new_project(self):
        """新建项目"""
        self.new_project_requested.emit()
        self.accept()
        
    def create_demo_project(self):
        """创建示例项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存示例项目", "示例项目.mlv", "ML Visual项目 (*.mlv)"
        )
        
        if file_path:
            # 创建示例项目数据
            demo_data = self.create_demo_data()
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(demo_data, f, indent=2, ensure_ascii=False)
                    
                self.add_to_recent(file_path)
                self.selected_project_path = file_path
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建示例项目失败:\n{str(e)}")
                
    def create_demo_data(self):
        """创建示例项目数据"""
        return {
            "components": [
                {
                    "id": "data_loader_1",
                    "type": "data",
                    "name": "数据加载",
                    "position": [100, 100],
                    "properties": {
                        "file_path": "data.csv",
                        "separator": ",",
                        "encoding": "utf-8"
                    }
                },
                {
                    "id": "preprocessor_1", 
                    "type": "preprocess",
                    "name": "标准化",
                    "position": [300, 100],
                    "properties": {
                        "method": "Z-score"
                    }
                },
                {
                    "id": "model_1",
                    "type": "model", 
                    "name": "随机森林",
                    "position": [500, 100],
                    "properties": {
                        "n_estimators": 100,
                        "max_depth": 10,
                        "random_state": 42
                    }
                }
            ],
            "connections": [
                {
                    "start_component": "data_loader_1",
                    "start_port": 0,
                    "end_component": "preprocessor_1", 
                    "end_port": 0
                },
                {
                    "start_component": "preprocessor_1",
                    "start_port": 0,
                    "end_component": "model_1",
                    "end_port": 0
                }
            ]
        }
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
<h3>机器学习可视化工具使用帮助</h3>

<h4>项目管理:</h4>
<ul>
<li><b>新建项目:</b> 创建一个空白的机器学习工作流程</li>
<li><b>打开项目:</b> 打开已保存的项目文件(.mlv格式)</li>
<li><b>示例项目:</b> 创建包含基本组件的示例项目</li>
</ul>

<h4>基本操作:</h4>
<ul>
<li><b>添加组件:</b> 从左侧组件库拖拽组件到画布</li>
<li><b>连接组件:</b> 从输出端口拖拽到输入端口建立连接</li>
<li><b>配置属性:</b> 选择组件后在右侧面板配置参数</li>
<li><b>保存项目:</b> 使用Ctrl+S保存项目</li>
</ul>

<h4>快捷键:</h4>
<ul>
<li><b>Ctrl+N:</b> 新建项目</li>
<li><b>Ctrl+O:</b> 打开项目</li>
<li><b>Ctrl+S:</b> 保存项目</li>
<li><b>F5:</b> 执行流程</li>
</ul>
        """
        
        QMessageBox.information(self, "使用帮助", help_text)
        
    def open_project(self):
        """打开选中的项目"""
        if self.selected_project_path:
            self.add_to_recent(self.selected_project_path)
            self.accept()
            
    def add_to_recent(self, project_path):
        """添加到最近项目列表"""
        recent_projects = self.settings.value('recent_projects', [])
        
        # 移除已存在的项目（避免重复）
        if project_path in recent_projects:
            recent_projects.remove(project_path)
            
        # 添加到列表开头
        recent_projects.insert(0, project_path)
        
        # 限制最大数量
        recent_projects = recent_projects[:10]
        
        # 保存设置
        self.settings.setValue('recent_projects', recent_projects)
        
    def remove_from_recent(self, project_path):
        """从最近项目列表移除"""
        recent_projects = self.settings.value('recent_projects', [])
        
        if project_path in recent_projects:
            recent_projects.remove(project_path)
            self.settings.setValue('recent_projects', recent_projects)
            
    def get_selected_project(self):
        """获取选中的项目路径"""
        return self.selected_project_path
