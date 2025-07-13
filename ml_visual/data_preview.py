#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据预览模块
显示数据集的预览、统计信息和可视化
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QTabWidget, QTextEdit, QGroupBox, QSplitter,
                             QScrollArea, QFrame, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap


class DataTableWidget(QWidget):
    """数据表格显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("显示行数:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(5, 1000)
        self.rows_spinbox.setValue(10)
        self.rows_spinbox.valueChanged.connect(self.update_display)
        control_layout.addWidget(self.rows_spinbox)
        
        control_layout.addStretch()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_data)
        control_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(control_layout)
        
        # 数据表格
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # 信息栏
        self.info_label = QLabel("暂无数据")
        self.info_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
    def update_data(self, data_info):
        """更新数据显示"""
        if not data_info:
            self.table.clear()
            self.info_label.setText("暂无数据")
            return
            
        # 更新表格
        rows = data_info.get('preview_data', [])
        columns = data_info.get('columns', [])
        
        if rows and columns:
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(i, j, item)
                    
            self.table.resizeColumnsToContents()
            
        # 更新信息
        shape = data_info.get('shape', [0, 0])
        dtypes = data_info.get('dtypes', {})
        memory_usage = data_info.get('memory_usage', '0 MB')
        
        info_text = f"形状: {shape[0]} 行 × {shape[1]} 列 | 内存使用: {memory_usage}"
        self.info_label.setText(info_text)
        
    def update_display(self):
        """更新显示行数"""
        # 这里应该重新请求数据
        pass
        
    def refresh_data(self):
        """刷新数据"""
        # 这里应该重新加载数据
        pass


class DataStatisticsWidget(QWidget):
    """数据统计信息组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 基本统计信息
        basic_group = QGroupBox("基本信息")
        self.basic_info_text = QTextEdit()
        self.basic_info_text.setReadOnly(True)
        self.basic_info_text.setMaximumHeight(150)
        
        basic_layout = QVBoxLayout()
        basic_layout.addWidget(self.basic_info_text)
        basic_group.setLayout(basic_layout)
        
        layout.addWidget(basic_group)
        
        # 数值型变量统计
        numeric_group = QGroupBox("数值型变量统计")
        self.numeric_stats_table = QTableWidget()
        
        numeric_layout = QVBoxLayout()
        numeric_layout.addWidget(self.numeric_stats_table)
        numeric_group.setLayout(numeric_layout)
        
        layout.addWidget(numeric_group)
        
        # 分类型变量统计
        categorical_group = QGroupBox("分类型变量统计")
        self.categorical_stats_table = QTableWidget()
        
        categorical_layout = QVBoxLayout()
        categorical_layout.addWidget(self.categorical_stats_table)
        categorical_group.setLayout(categorical_layout)
        
        layout.addWidget(categorical_group)
        
        self.setLayout(layout)
        
    def update_statistics(self, stats_info):
        """更新统计信息"""
        if not stats_info:
            return
            
        # 更新基本信息
        basic_info = f"""
数据集形状: {stats_info.get('shape', 'N/A')}
列数: {stats_info.get('n_columns', 'N/A')}
数值型列: {stats_info.get('n_numeric', 'N/A')}
分类型列: {stats_info.get('n_categorical', 'N/A')}
缺失值总数: {stats_info.get('total_missing', 'N/A')}
重复行数: {stats_info.get('duplicates', 'N/A')}
        """
        self.basic_info_text.setText(basic_info.strip())
        
        # 更新数值型统计
        numeric_stats = stats_info.get('numeric_stats', {})
        if numeric_stats:
            columns = ['变量名', '均值', '标准差', '最小值', '25%', '50%', '75%', '最大值', '缺失值']
            self.numeric_stats_table.setColumnCount(len(columns))
            self.numeric_stats_table.setHorizontalHeaderLabels(columns)
            self.numeric_stats_table.setRowCount(len(numeric_stats))
            
            for i, (var_name, stats) in enumerate(numeric_stats.items()):
                self.numeric_stats_table.setItem(i, 0, QTableWidgetItem(var_name))
                self.numeric_stats_table.setItem(i, 1, QTableWidgetItem(f"{stats.get('mean', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 2, QTableWidgetItem(f"{stats.get('std', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 3, QTableWidgetItem(f"{stats.get('min', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 4, QTableWidgetItem(f"{stats.get('25%', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 5, QTableWidgetItem(f"{stats.get('50%', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 6, QTableWidgetItem(f"{stats.get('75%', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 7, QTableWidgetItem(f"{stats.get('max', 0):.3f}"))
                self.numeric_stats_table.setItem(i, 8, QTableWidgetItem(str(stats.get('missing', 0))))
                
            self.numeric_stats_table.resizeColumnsToContents()
            
        # 更新分类型统计
        categorical_stats = stats_info.get('categorical_stats', {})
        if categorical_stats:
            columns = ['变量名', '唯一值数', '最频繁值', '频次', '缺失值']
            self.categorical_stats_table.setColumnCount(len(columns))
            self.categorical_stats_table.setHorizontalHeaderLabels(columns)
            self.categorical_stats_table.setRowCount(len(categorical_stats))
            
            for i, (var_name, stats) in enumerate(categorical_stats.items()):
                self.categorical_stats_table.setItem(i, 0, QTableWidgetItem(var_name))
                self.categorical_stats_table.setItem(i, 1, QTableWidgetItem(str(stats.get('unique', 0))))
                self.categorical_stats_table.setItem(i, 2, QTableWidgetItem(str(stats.get('top', 'N/A'))))
                self.categorical_stats_table.setItem(i, 3, QTableWidgetItem(str(stats.get('freq', 0))))
                self.categorical_stats_table.setItem(i, 4, QTableWidgetItem(str(stats.get('missing', 0))))
                
            self.categorical_stats_table.resizeColumnsToContents()


class DataVisualizationWidget(QWidget):
    """数据可视化组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 可视化控制
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("图表类型:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["直方图", "散点图", "相关性热图", "箱线图", "分布图"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        control_layout.addWidget(self.chart_type_combo)
        
        control_layout.addWidget(QLabel("变量:"))
        self.variable_combo = QComboBox()
        self.variable_combo.currentTextChanged.connect(self.update_chart)
        control_layout.addWidget(self.variable_combo)
        
        control_layout.addStretch()
        
        self.generate_btn = QPushButton("生成图表")
        self.generate_btn.clicked.connect(self.generate_chart)
        control_layout.addWidget(self.generate_btn)
        
        layout.addLayout(control_layout)
        
        # 图表显示区域
        self.chart_label = QLabel("选择图表类型和变量后点击生成图表")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setMinimumHeight(400)
        self.chart_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                background-color: #f9f9f9;
                color: #666666;
                font-size: 14px;
            }
        """)
        
        layout.addWidget(self.chart_label)
        
        self.setLayout(layout)
        
    def update_variables(self, columns):
        """更新可用变量列表"""
        self.variable_combo.clear()
        self.variable_combo.addItems(columns)
        
    def update_chart(self):
        """更新图表显示"""
        chart_type = self.chart_type_combo.currentText()
        variable = self.variable_combo.currentText()
        
        if chart_type and variable:
            self.chart_label.setText(f"将显示 {variable} 的{chart_type}")
        else:
            self.chart_label.setText("选择图表类型和变量后点击生成图表")
            
    def generate_chart(self):
        """生成图表"""
        chart_type = self.chart_type_combo.currentText()
        variable = self.variable_combo.currentText()
        
        if not chart_type or not variable:
            return
            
        # 这里应该调用后端接口生成图表
        self.chart_label.setText(f"正在生成 {variable} 的{chart_type}...")
        
    def display_chart(self, chart_data):
        """显示图表"""
        if 'image_base64' in chart_data:
            # 显示base64编码的图片
            import base64
            image_data = base64.b64decode(chart_data['image_base64'])
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.chart_label.setPixmap(pixmap.scaled(
                self.chart_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.chart_label.setText("图表生成失败")


class DataPreviewPanel(QWidget):
    """数据预览面板主组件"""
    
    # 信号定义
    data_requested = pyqtSignal(str)  # 请求数据预览
    statistics_requested = pyqtSignal(str)  # 请求统计信息
    chart_requested = pyqtSignal(str, str, str)  # 请求图表生成
    
    def __init__(self):
        super().__init__()
        self.current_data_id = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel("数据预览")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.data_source_label = QLabel("数据源: 未选择")
        self.data_source_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(self.data_source_label)
        
        layout.addLayout(header_layout)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 数据表格标签页
        self.table_widget = DataTableWidget()
        self.tab_widget.addTab(self.table_widget, "数据表格")
        
        # 统计信息标签页
        self.statistics_widget = DataStatisticsWidget()
        self.tab_widget.addTab(self.statistics_widget, "统计信息")
        
        # 可视化标签页
        self.visualization_widget = DataVisualizationWidget()
        self.tab_widget.addTab(self.visualization_widget, "数据可视化")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        
        # 连接信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def set_data_source(self, data_id, source_name):
        """设置数据源"""
        self.current_data_id = data_id
        self.data_source_label.setText(f"数据源: {source_name}")
        
        # 请求数据预览
        self.data_requested.emit(data_id)
        
    def update_data_preview(self, data_info):
        """更新数据预览"""
        self.table_widget.update_data(data_info)
        
        # 更新可视化组件的变量列表
        columns = data_info.get('columns', [])
        self.visualization_widget.update_variables(columns)
        
    def update_statistics(self, stats_info):
        """更新统计信息"""
        self.statistics_widget.update_statistics(stats_info)
        
    def update_visualization(self, chart_data):
        """更新可视化"""
        self.visualization_widget.display_chart(chart_data)
        
    def on_tab_changed(self, index):
        """标签页切换处理"""
        if not self.current_data_id:
            return
            
        if index == 1:  # 统计信息标签页
            self.statistics_requested.emit(self.current_data_id)
        elif index == 2:  # 可视化标签页
            pass  # 可视化按需生成
            
    def clear_preview(self):
        """清空预览"""
        self.current_data_id = None
        self.data_source_label.setText("数据源: 未选择")
        self.table_widget.update_data(None)
        self.statistics_widget.update_statistics(None)
