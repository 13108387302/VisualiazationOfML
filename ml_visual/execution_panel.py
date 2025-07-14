#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行面板模块
显示工作流程执行状态和结果
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QGroupBox,
                             QScrollArea, QSplitter, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette


class ExecutionStatusWidget(QWidget):
    """执行状态显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 状态标题
        self.status_label = QLabel("执行状态: 就绪")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 当前步骤
        self.current_step_label = QLabel("")
        self.current_step_label.setVisible(False)
        layout.addWidget(self.current_step_label)
        
        # 执行时间
        self.time_label = QLabel("")
        self.time_label.setVisible(False)
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
        
    def set_status(self, status, message=""):
        """设置执行状态"""
        status_colors = {
            "ready": "#666666",
            "running": "#ff8c00", 
            "completed": "#008000",
            "failed": "#dc143c",
            "stopped": "#8b4513"
        }
        
        color = status_colors.get(status, "#666666")
        self.status_label.setText(f"执行状态: {message}")
        self.status_label.setStyleSheet(f"color: {color};")
        
        if status == "running":
            self.progress_bar.setVisible(True)
            self.current_step_label.setVisible(True)
            self.time_label.setVisible(True)
        elif status in ["completed", "failed", "stopped"]:
            self.progress_bar.setVisible(False)
            self.current_step_label.setVisible(False)
            
    def set_progress(self, progress, current_step="", estimated_time=""):
        """设置执行进度"""
        self.progress_bar.setValue(int(progress * 100))
        
        if current_step:
            self.current_step_label.setText(f"当前步骤: {current_step}")
            
        if estimated_time:
            self.time_label.setText(f"预计剩余时间: {estimated_time}")


class ExecutionLogWidget(QWidget):
    """执行日志显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 日志标题和控制按钮
        header_layout = QHBoxLayout()
        
        log_label = QLabel("执行日志")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(log_label)
        
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        
    def add_log(self, message, level="INFO"):
        """添加日志消息（优化性能）"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        level_colors = {
            "INFO": "#000000",
            "WARNING": "#ff8c00",
            "ERROR": "#dc143c",
            "SUCCESS": "#008000"
        }

        color = level_colors.get(level, "#000000")
        formatted_message = f'<span style="color: gray;">[{timestamp}]</span> <span style="color: {color};">[{level}]</span> {message}'

        # 限制日志条数，避免内存过度使用
        if self.log_text.document().blockCount() > 1000:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 100)  # 删除前100行
            cursor.removeSelectedText()

        self.log_text.append(formatted_message)

        # 批量滚动，减少UI更新频率
        if not hasattr(self, '_scroll_timer'):
            from PyQt5.QtCore import QTimer
            self._scroll_timer = QTimer()
            self._scroll_timer.setSingleShot(True)
            self._scroll_timer.timeout.connect(self._scroll_to_bottom)

        self._scroll_timer.start(100)  # 100ms后滚动

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()


class ResultsDisplayWidget(QWidget):
    """结果显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 结果标签页
        self.tab_widget = QTabWidget()
        
        # 组件结果标签页
        self.component_results_tab = QWidget()
        self.init_component_results_tab()
        self.tab_widget.addTab(self.component_results_tab, "组件结果")
        
        # 模型评估标签页
        self.evaluation_tab = QWidget()
        self.init_evaluation_tab()
        self.tab_widget.addTab(self.evaluation_tab, "模型评估")
        
        # 可视化标签页
        self.visualization_tab = QWidget()
        self.init_visualization_tab()
        self.tab_widget.addTab(self.visualization_tab, "可视化")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def init_component_results_tab(self):
        """初始化组件结果标签页"""
        layout = QVBoxLayout()
        
        # 组件结果表格
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["组件名称", "状态", "执行时间", "输出摘要"])
        
        layout.addWidget(self.results_table)
        self.component_results_tab.setLayout(layout)
        
    def init_evaluation_tab(self):
        """初始化评估标签页"""
        layout = QVBoxLayout()
        
        # 评估指标显示
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(150)
        
        layout.addWidget(QLabel("模型评估指标:"))
        layout.addWidget(self.metrics_text)
        
        # 混淆矩阵等详细结果
        self.detailed_results = QTextEdit()
        self.detailed_results.setReadOnly(True)
        
        layout.addWidget(QLabel("详细评估结果:"))
        layout.addWidget(self.detailed_results)
        
        self.evaluation_tab.setLayout(layout)
        
    def init_visualization_tab(self):
        """初始化可视化标签页"""
        layout = QVBoxLayout()
        
        # 图表显示区域
        self.chart_label = QLabel("暂无可视化结果")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setMinimumHeight(300)
        self.chart_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f9f9f9;")
        
        layout.addWidget(self.chart_label)
        self.visualization_tab.setLayout(layout)
        
    def update_component_results(self, results):
        """更新组件结果"""
        self.results_table.setRowCount(len(results))
        
        for i, (comp_id, result) in enumerate(results.items()):
            self.results_table.setItem(i, 0, QTableWidgetItem(result.get("name", comp_id)))
            
            status = "成功" if result.get("success", False) else "失败"
            status_item = QTableWidgetItem(status)
            if result.get("success", False):
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            self.results_table.setItem(i, 1, status_item)
            
            exec_time = result.get("execution_time", 0)
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{exec_time:.2f}s"))
            
            summary = result.get("summary", "无输出")
            self.results_table.setItem(i, 3, QTableWidgetItem(summary))
            
        self.results_table.resizeColumnsToContents()
        
    def update_evaluation_results(self, metrics, detailed_results):
        """更新评估结果"""
        # 格式化指标显示
        metrics_text = ""
        for metric, value in metrics.items():
            if isinstance(value, float):
                metrics_text += f"{metric}: {value:.4f}\n"
            else:
                metrics_text += f"{metric}: {value}\n"
                
        self.metrics_text.setText(metrics_text)
        self.detailed_results.setText(detailed_results)
        
    def update_visualization(self, chart_data):
        """更新可视化结果"""
        # 这里可以集成matplotlib或其他图表库
        # 暂时显示占位文本
        self.chart_label.setText("可视化图表将在此显示")


class ExecutionPanel(QWidget):
    """执行面板主组件"""
    
    # 信号定义
    execution_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.execution_timer = QTimer()
        self.execution_timer.timeout.connect(self.update_execution_status)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 执行控制区域
        control_group = QGroupBox("执行控制")
        control_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("执行工作流程")
        self.execute_btn.clicked.connect(self.start_execution)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.stop_btn = QPushButton("停止执行")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc143c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b91c3c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        control_layout.addWidget(self.execute_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 状态显示区域
        self.status_widget = ExecutionStatusWidget()
        layout.addWidget(self.status_widget)
        
        # 分割器：日志和结果
        splitter = QSplitter(Qt.Vertical)
        
        # 执行日志
        self.log_widget = ExecutionLogWidget()
        splitter.addWidget(self.log_widget)
        
        # 结果显示
        self.results_widget = ResultsDisplayWidget()
        splitter.addWidget(self.results_widget)
        
        splitter.setSizes([200, 400])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def start_execution(self):
        """开始执行"""
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.status_widget.set_status("running", "正在执行...")
        self.log_widget.add_log("开始执行工作流程", "INFO")
        
        # 发射执行请求信号
        self.execution_requested.emit()
        
        # 开始状态更新定时器
        self.execution_timer.start(1000)  # 每秒更新一次
        
    def stop_execution(self):
        """停止执行"""
        self.stop_btn.setEnabled(False)
        self.status_widget.set_status("stopped", "正在停止...")
        self.log_widget.add_log("用户请求停止执行", "WARNING")
        
        # 发射停止请求信号
        self.stop_requested.emit()
        
    def execution_completed(self, success, results=None):
        """执行完成"""
        self.execution_timer.stop()
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            self.status_widget.set_status("completed", "执行完成")
            self.log_widget.add_log("工作流程执行完成", "SUCCESS")
            
            if results:
                self.results_widget.update_component_results(results)
        else:
            self.status_widget.set_status("failed", "执行失败")
            self.log_widget.add_log("工作流程执行失败", "ERROR")
            
    def update_execution_status(self):
        """更新执行状态（定时调用）"""
        # 这个方法由定时器调用，用于更新执行状态
        # 实际的状态更新通过信号机制处理，这里可以做一些UI状态检查
        try:
            # 检查按钮状态是否一致
            if not self.execute_btn.isEnabled() and not self.stop_btn.isEnabled():
                # 如果两个按钮都被禁用，可能是异常状态，重置为可执行状态
                self.execute_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.execution_timer.stop()
        except Exception as e:
            print(f"更新执行状态时出错: {e}")
        
    def add_log_message(self, message, level="INFO"):
        """添加日志消息"""
        self.log_widget.add_log(message, level)
        
    def update_progress(self, progress, current_step=""):
        """更新执行进度"""
        self.status_widget.set_progress(progress, current_step)
