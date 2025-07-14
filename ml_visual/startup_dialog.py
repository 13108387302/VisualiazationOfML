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
from .ui_utils import UIUtils, NotificationManager
from .config_manager import get_config


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

        # 用户体验增强
        self.notification_manager = None  # 延迟初始化

        # 从配置获取对话框大小
        self.startup_config = get_config('startup', {})
        dialog_size = self.startup_config.get('dialog_size', [900, 600])
        self.setFixedSize(dialog_size[0], dialog_size[1])

        self.init_ui()
        # 在UI初始化后加载最近项目
        self.load_recent_projects_with_feedback()
        
    def init_ui(self):
        """初始化用户界面 - 现代化设计"""
        # 从配置获取文本
        texts = self.startup_config.get('texts', {})
        title = f"{texts.get('title', 'ML Visual')} - {texts.get('subtitle', '机器学习可视化工具')}"

        self.setWindowTitle(title)
        self.setModal(True)

        # 从配置获取样式
        styles = self.startup_config.get('styles', {})
        fonts = self.startup_config.get('fonts', {})

        # 设置现代化样式
        self.setStyleSheet(f"""
            QDialog {{
                background: {styles.get('dialog_bg_gradient', 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef)')};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox {{
                font-weight: bold;
                border: {styles.get('card_border', '2px solid #dee2e6')};
                border-radius: {styles.get('card_border_radius', '8px')};
                margin-top: 10px;
                padding-top: 10px;
                background-color: {styles.get('card_bg', 'rgba(255, 255, 255, 0.8)')};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
            }}
            QPushButton {{
                background-color: {styles.get('button_bg', '#007bff')};
                color: white;
                border: none;
                padding: {styles.get('button_padding', '10px 20px')};
                border-radius: {styles.get('button_border_radius', '6px')};
                font-weight: bold;
                font-size: {fonts.get('button_size', '14px')};
            }}
            QPushButton:hover {{
                background-color: {styles.get('button_hover', '#0056b3')};
            }}
            QPushButton:pressed {{
                background-color: {styles.get('button_pressed', '#004085')};
            }}
            QPushButton#primaryButton {{
                background-color: {styles.get('primary_button_bg', '#28a745')};
                font-size: {fonts.get('primary_button_size', '16px')};
                padding: {styles.get('primary_button_padding', '12px 24px')};
            }}
            QPushButton#primaryButton:hover {{
                background-color: {styles.get('primary_button_hover', '#218838')};
            }}
            QPushButton#secondaryButton {{
                background-color: {styles.get('secondary_button_bg', '#6c757d')};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {styles.get('secondary_button_hover', '#545b62')};
            }}
        """)

        # 从配置获取布局设置
        layout_config = self.startup_config.get('layout', {})
        main_margins = layout_config.get('main_margins', [20, 20, 20, 20])
        main_spacing = layout_config.get('main_spacing', 20)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*main_margins)
        main_layout.setSpacing(main_spacing)

        # 标题区域
        self.create_modern_header(main_layout)

        # 内容区域 - 使用卡片式设计
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # 左侧 - 快速开始卡片
        quick_start_card = self.create_quick_start_card()
        content_layout.addWidget(quick_start_card, 1)

        # 右侧 - 最近项目卡片
        recent_projects_card = self.create_recent_projects_card()
        content_layout.addWidget(recent_projects_card, 1)

        main_layout.addLayout(content_layout)

        # 底部操作区域
        self.create_modern_footer(main_layout)

        self.setLayout(main_layout)
        

        

        

        

        

        
    def load_recent_projects(self):
        """加载最近项目列表（优化加载性能）"""
        if not hasattr(self, 'recent_list'):
            return  # UI还未初始化

        recent_projects = self.settings.value('recent_projects', [])

        # 批量处理，减少UI更新次数
        valid_projects = []
        invalid_projects = []

        for project_path in recent_projects:
            if project_path and os.path.exists(project_path):
                valid_projects.append(project_path)
            else:
                invalid_projects.append(project_path)

        # 批量添加有效项目
        for project_path in valid_projects:
            try:
                project_info = self.load_project_info(project_path)
                item_text = f"{project_info['name']} - {project_info['description']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, project_path)
                self.recent_list.addItem(item)
            except Exception:
                # 如果加载失败，添加到无效列表
                invalid_projects.append(project_path)

        # 批量移除无效项目
        for project_path in invalid_projects:
            self.remove_from_recent(project_path)

    def load_recent_projects_with_feedback(self):
        """带用户反馈的加载最近项目"""
        try:
            # 延迟初始化通知管理器，确保UI已完全初始化
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, self._init_notification_and_load)

        except Exception as e:
            print(f"加载项目时出错: {e}")
            # 回退到直接加载
            self.load_recent_projects()

    def _init_notification_and_load(self):
        """初始化通知管理器并加载项目"""
        try:
            # 初始化通知管理器
            if not self.notification_manager:
                self.notification_manager = NotificationManager(self)
                self.notification_manager.move(self.width() - 320, 20)
                self.notification_manager.show()

            # 显示加载提示
            self.notification_manager.show_notification("正在加载最近项目...", "info", 1000)

            # 执行加载
            self.load_recent_projects()

        except Exception as e:
            print(f"初始化通知管理器时出错: {e}")
            # 回退到直接加载
            self.load_recent_projects()
                
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
        
    def on_project_double_clicked(self, item=None):
        """项目双击处理"""
        if item is None:
            item = self.recent_list.currentItem()

        if item:
            # 从item的UserRole数据中获取项目路径
            self.selected_project_path = item.data(Qt.UserRole)
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
        """新建项目（增强用户反馈）"""
        try:
            if self.notification_manager:
                self.notification_manager.show_notification("正在创建新项目...", "info", 1500)

            # 延迟发射信号，让用户看到反馈
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, lambda: (
                self.new_project_requested.emit(),
                self.accept()
            ))
        except Exception as e:
            print(f"创建新项目时出错: {e}")
            if self.notification_manager:
                self.notification_manager.show_notification("创建项目失败", "error")
        
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
        """打开项目文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目文件", "", "ML Visual项目 (*.mlv);;所有文件 (*)"
        )

        if file_path:
            # 验证文件是否存在且可读
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # 验证JSON格式

                self.add_to_recent(file_path)
                self.selected_project_path = file_path
                self.accept()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开项目文件:\n{str(e)}")
            
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

    def create_modern_header(self, layout):
        """创建现代化标题区域"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                margin-bottom: 10px;
            }
        """)
        header_widget.setFixedHeight(120)

        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)

        # 主标题
        title = QLabel("ML Visual")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("机器学习可视化工具 - 让AI开发更简单")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                background: transparent;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_widget)

    def create_quick_start_card(self):
        """创建快速开始卡片（重构版本）"""
        # 使用通用卡片创建方法
        card, layout = UIUtils.create_card_frame("🚀 快速开始")

        # 新建项目按钮 - 使用主要按钮样式
        new_project_btn = UIUtils.create_primary_button("📝 创建新项目")
        new_project_btn.clicked.connect(self.new_project)
        layout.addWidget(new_project_btn)

        # 打开项目按钮 - 使用次要按钮样式
        open_project_btn = UIUtils.create_secondary_button("📂 打开现有项目")
        open_project_btn.clicked.connect(self.open_project)
        layout.addWidget(open_project_btn)

        # 示例项目按钮 - 使用次要按钮样式
        example_btn = UIUtils.create_secondary_button("🎯 浏览示例项目")
        example_btn.clicked.connect(self.browse_examples)
        layout.addWidget(example_btn)

        # 添加说明文本
        layout.addSpacing(20)
        info_label = QLabel("""
        <div style='color: #6c757d; font-size: 14px; line-height: 1.5;'>
        <b>新手指南：</b><br>
        • 创建新项目开始您的ML之旅<br>
        • 拖拽组件构建机器学习流程<br>
        • 可视化查看数据和结果<br>
        • 支持多种算法和数据格式
        </div>
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()
        return card

    def create_recent_projects_card(self):
        """创建最近项目卡片"""
        card = QGroupBox("📋 最近项目")
        card.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                color: #2c3e50;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # 项目列表
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        layout.addWidget(self.recent_list)

        # 项目操作按钮
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("打开")
        open_btn.clicked.connect(self.on_project_double_clicked)
        btn_layout.addWidget(open_btn)

        remove_btn = QPushButton("移除")
        remove_btn.setObjectName("secondaryButton")
        remove_btn.clicked.connect(self.remove_project)
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("清空列表")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self.clear_recent_list)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        return card

    def create_modern_footer(self, layout):
        """创建现代化底部区域"""
        footer_layout = QHBoxLayout()

        # 左侧：版本信息
        version_label = QLabel("版本 1.0.0 | © 2024 ML Visual")
        version_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        footer_layout.addWidget(version_label)

        footer_layout.addStretch()

        # 右侧：主要操作按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)

        continue_btn = QPushButton("继续")
        continue_btn.setObjectName("primaryButton")
        continue_btn.clicked.connect(self.accept_selection)
        footer_layout.addWidget(continue_btn)

        layout.addLayout(footer_layout)

    def accept_selection(self):
        """接受选择"""
        if self.recent_list.currentItem():
            self.on_project_double_clicked()
        else:
            self.new_project()

    def browse_examples(self):
        """浏览示例项目"""
        try:
            # 创建示例项目选择对话框
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel

            dialog = QDialog(self)
            dialog.setWindowTitle("选择示例项目")
            dialog.setFixedSize(500, 400)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("选择一个示例项目开始学习：")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
            layout.addWidget(title_label)

            # 示例项目列表
            examples_list = QListWidget()

            # 添加示例项目
            examples = [
                ("基础分类流程", "使用鸢尾花数据集进行分类的完整流程"),
                ("回归分析示例", "房价预测的线性回归分析"),
                ("数据预处理流程", "数据清洗和特征工程的完整示例"),
                ("模型比较分析", "多种算法的性能对比分析")
            ]

            for name, description in examples:
                item = QListWidgetItem(f"{name}\n{description}")
                item.setData(Qt.UserRole, name)
                examples_list.addItem(item)

            layout.addWidget(examples_list)

            # 按钮区域
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)

            create_btn = QPushButton("创建示例")
            create_btn.clicked.connect(lambda: self._create_selected_example(dialog, examples_list))
            btn_layout.addWidget(create_btn)

            layout.addLayout(btn_layout)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开示例项目失败:\n{str(e)}")

    def _create_selected_example(self, dialog, examples_list):
        """创建选中的示例项目"""
        current_item = examples_list.currentItem()
        if not current_item:
            QMessageBox.warning(dialog, "提示", "请选择一个示例项目")
            return

        example_name = current_item.data(Qt.UserRole)

        # 让用户选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            dialog, f"保存示例项目: {example_name}",
            f"{example_name}.mlv", "ML Visual项目 (*.mlv)"
        )

        if file_path:
            try:
                # 根据示例名称创建不同的示例数据
                demo_data = self._create_example_data(example_name)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(demo_data, f, indent=2, ensure_ascii=False)

                self.add_to_recent(file_path)
                self.selected_project_path = file_path
                dialog.accept()
                self.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "错误", f"创建示例项目失败:\n{str(e)}")

    def _create_example_data(self, example_name):
        """根据示例名称创建示例数据"""
        base_data = {
            "version": "1.0",
            "name": example_name,
            "description": f"{example_name}的示例项目",
            "created": "2024-01-01",
            "components": [],
            "connections": []
        }

        if example_name == "基础分类流程":
            base_data["components"] = [
                {
                    "id": "data_loader_1",
                    "type": "data",
                    "name": "数据加载",
                    "position": [100, 100],
                    "properties": {"file_path": "iris.csv", "separator": ","}
                },
                {
                    "id": "preprocessor_1",
                    "type": "preprocess",
                    "name": "标准化",
                    "position": [300, 100],
                    "properties": {"method": "Z-score"}
                },
                {
                    "id": "model_1",
                    "type": "model",
                    "name": "随机森林",
                    "position": [500, 100],
                    "properties": {"n_estimators": 100, "max_depth": 10}
                },
                {
                    "id": "evaluator_1",
                    "type": "evaluate",
                    "name": "准确率",
                    "position": [700, 100],
                    "properties": {"metric": "accuracy"}
                }
            ]
            base_data["connections"] = [
                {"start_component": "data_loader_1", "start_port": 0, "end_component": "preprocessor_1", "end_port": 0},
                {"start_component": "preprocessor_1", "start_port": 0, "end_component": "model_1", "end_port": 0},
                {"start_component": "model_1", "start_port": 0, "end_component": "evaluator_1", "end_port": 0}
            ]
        elif example_name == "回归分析示例":
            base_data["components"] = [
                {
                    "id": "data_loader_1",
                    "type": "data",
                    "name": "数据加载",
                    "position": [100, 100],
                    "properties": {"file_path": "housing.csv", "separator": ","}
                },
                {
                    "id": "model_1",
                    "type": "model",
                    "name": "线性回归",
                    "position": [300, 100],
                    "properties": {"regularization": "L2", "alpha": 0.1}
                }
            ]
            base_data["connections"] = [
                {"start_component": "data_loader_1", "start_port": 0, "end_component": "model_1", "end_port": 0}
            ]

        return base_data

    def clear_recent_list(self):
        """清空最近项目列表"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空最近项目列表吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.recent_list.clear()
            self.settings.setValue('recent_projects', [])
