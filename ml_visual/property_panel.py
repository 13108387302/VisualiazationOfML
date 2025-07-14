#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
属性面板模块
管理组件属性的显示和配置
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QGroupBox, QFormLayout, QLineEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QSpacerItem,
                             QSizePolicy, QHBoxLayout, QSlider, QPushButton,
                             QFileDialog, QTextEdit, QListWidget, QTableWidget,
                             QTableWidgetItem, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class PropertyPanel(QWidget):
    """属性配置面板"""
    
    property_changed = pyqtSignal(object, str, object)  # 组件, 属性名, 新值
    
    def __init__(self):
        super().__init__()
        self.current_component = None
        self.property_widgets = {}
        self.update_timer = None  # 延迟更新定时器
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("组件属性")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # 滚动区域
        scroll = QScrollArea()
        self.property_widget = QWidget()
        self.property_layout = QVBoxLayout(self.property_widget)
        
        scroll.setWidget(self.property_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        # 默认显示空状态
        self.show_empty_state()
        
    def show_empty_state(self):
        """显示空状态"""
        self.clear_properties()
        empty_label = QLabel("请选择一个组件")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("color: gray; font-style: italic;")
        self.property_layout.addWidget(empty_label)
        
    def clear_properties(self):
        """清空属性面板"""
        while self.property_layout.count():
            child = self.property_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.property_widgets.clear()
                
    def show_component_properties(self, component):
        """显示组件属性（使用延迟更新优化性能）"""
        # 使用定时器延迟更新，避免频繁更新
        if self.update_timer:
            self.update_timer.stop()

        from PyQt5.QtCore import QTimer
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(lambda: self._do_show_properties(component))
        self.update_timer.start(50)  # 50ms延迟

    def _do_show_properties(self, component):
        """实际执行属性显示（优化版本）"""
        # 如果是同一个组件，不需要重新构建界面
        if self.current_component == component:
            return

        self.clear_properties()
        self.current_component = component
        
        # 组件名称
        name_label = QLabel(f"组件: {component.name}")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        self.property_layout.addWidget(name_label)
        
        # 组件类型
        type_label = QLabel(f"类型: {component.component_type}")
        type_label.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        self.property_layout.addWidget(type_label)
        
        # 根据组件类型显示不同的属性
        if component.component_type == 'data':
            self.add_data_properties(component)
        elif component.component_type == 'preprocess':
            self.add_preprocess_properties(component)
        elif component.component_type == 'model':
            self.add_model_properties(component)
        elif component.component_type == 'evaluate':
            self.add_evaluate_properties(component)
        elif component.component_type == 'output':
            self.add_output_properties(component)
            
        # 添加弹性空间
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.property_layout.addItem(spacer)
        
    def add_data_properties(self, component):
        """添加数据组件属性"""
        if "加载" in component.name:
            self.add_property_group("数据源配置", [
                ("文件路径", "LineEdit", "data.csv"),
                ("分隔符", "ComboBox", [",", ";", "\t"]),
                ("编码格式", "ComboBox", ["utf-8", "gbk", "ascii"])
            ])
        elif "清洗" in component.name:
            self.add_property_group("清洗选项", [
                ("删除缺失值", "CheckBox", True),
                ("填充方式", "ComboBox", ["均值", "中位数", "众数"]),
                ("异常值处理", "CheckBox", False)
            ])
        elif "特征选择" in component.name:
            self.add_property_group("特征选择", [
                ("选择方法", "ComboBox", ["方差选择", "卡方检验", "互信息"]),
                ("特征数量", "SpinBox", 10),
                ("阈值", "DoubleSpinBox", 0.1)
            ])
        elif "分割" in component.name:
            self.add_property_group("数据分割", [
                ("测试集比例", "DoubleSpinBox", 0.2),
                ("随机状态", "SpinBox", 42),
                ("分层采样", "CheckBox", True)
            ])
            
    def add_preprocess_properties(self, component):
        """添加预处理组件属性"""
        if "标准化" in component.name:
            self.add_property_group("标准化参数", [
                ("方法", "ComboBox", ["Z-score", "Min-Max", "Robust"]),
                ("特征范围", "LineEdit", "0,1")
            ])
        elif "归一化" in component.name:
            self.add_property_group("归一化参数", [
                ("范围最小值", "DoubleSpinBox", 0.0),
                ("范围最大值", "DoubleSpinBox", 1.0)
            ])
        elif "编码" in component.name:
            self.add_property_group("编码参数", [
                ("编码方式", "ComboBox", ["独热编码", "标签编码", "目标编码"]),
                ("处理未知值", "CheckBox", True)
            ])
        elif "降维" in component.name:
            self.add_property_group("降维参数", [
                ("方法", "ComboBox", ["PCA", "LDA", "t-SNE"]),
                ("目标维度", "SpinBox", 2),
                ("方差保留比例", "DoubleSpinBox", 0.95)
            ])
            
    def add_model_properties(self, component):
        """添加模型组件属性"""
        if "随机森林" in component.name:
            self.add_property_group("模型参数", [
                ("树的数量", "SpinBox", 100),
                ("最大深度", "SpinBox", 10),
                ("最小分割样本", "SpinBox", 2),
                ("随机状态", "SpinBox", 42)
            ])
        elif "线性回归" in component.name:
            self.add_property_group("回归参数", [
                ("正则化", "ComboBox", ["None", "L1", "L2"]),
                ("正则化强度", "DoubleSpinBox", 1.0),
                ("拟合截距", "CheckBox", True)
            ])
        elif "决策树" in component.name:
            self.add_property_group("决策树参数", [
                ("最大深度", "SpinBox", 5),
                ("分割标准", "ComboBox", ["gini", "entropy"]),
                ("最小分割样本", "SpinBox", 2)
            ])
        elif "SVM" in component.name:
            self.add_property_group("SVM参数", [
                ("核函数", "ComboBox", ["rbf", "linear", "poly"]),
                ("C参数", "DoubleSpinBox", 1.0),
                ("gamma", "ComboBox", ["scale", "auto"])
            ])
        elif "神经网络" in component.name:
            self.add_property_group("神经网络参数", [
                ("隐藏层大小", "LineEdit", "100,50"),
                ("激活函数", "ComboBox", ["relu", "tanh", "logistic"]),
                ("学习率", "DoubleSpinBox", 0.001),
                ("最大迭代次数", "SpinBox", 200)
            ])
            
    def add_evaluate_properties(self, component):
        """添加评估组件属性"""
        self.add_property_group("评估设置", [
            ("交叉验证", "CheckBox", True),
            ("折数", "SpinBox", 5),
            ("评估指标", "ComboBox", ["准确率", "精确率", "召回率", "F1分数"]),
            ("显示详细结果", "CheckBox", True)
        ])
        
    def add_output_properties(self, component):
        """添加输出组件属性"""
        if "保存" in component.name:
            self.add_property_group("保存设置", [
                ("保存路径", "LineEdit", "output/"),
                ("文件格式", "ComboBox", ["CSV", "JSON", "Excel"]),
                ("包含索引", "CheckBox", False)
            ])
        elif "可视化" in component.name:
            self.add_property_group("可视化设置", [
                ("图表类型", "ComboBox", ["散点图", "柱状图", "热力图"]),
                ("图片格式", "ComboBox", ["PNG", "SVG", "PDF"]),
                ("图片大小", "LineEdit", "800x600")
            ])
        elif "报告" in component.name:
            self.add_property_group("报告设置", [
                ("报告格式", "ComboBox", ["HTML", "PDF", "Word"]),
                ("包含图表", "CheckBox", True),
                ("详细程度", "ComboBox", ["简要", "详细", "完整"])
            ])
        
    def add_property_group(self, title, properties):
        """添加属性组"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        form_layout = QFormLayout()
        
        for prop_name, prop_type, default_value in properties:
            widget = self._create_property_widget(prop_type, default_value)
            if widget:
                # 连接信号
                self._connect_property_signal(widget, prop_name)
                # 存储widget引用
                self.property_widgets[prop_name] = widget
                form_layout.addRow(prop_name + ":", widget)
                
        group.setLayout(form_layout)
        self.property_layout.addWidget(group)
        
    def _create_property_widget(self, prop_type, default_value):
        """创建属性控件"""
        if prop_type == "LineEdit":
            widget = QLineEdit(str(default_value))
            return widget
        elif prop_type == "ComboBox":
            widget = QComboBox()
            if isinstance(default_value, list):
                widget.addItems(default_value)
            else:
                widget.addItem(str(default_value))
            return widget
        elif prop_type == "SpinBox":
            widget = QSpinBox()
            widget.setRange(1, 10000)
            widget.setValue(default_value)
            return widget
        elif prop_type == "DoubleSpinBox":
            widget = QDoubleSpinBox()
            widget.setRange(0.0, 1000.0)
            widget.setDecimals(3)
            widget.setValue(default_value)
            return widget
        elif prop_type == "CheckBox":
            widget = QCheckBox()
            widget.setChecked(default_value)
            return widget
        else:
            return None
            
    def _connect_property_signal(self, widget, prop_name):
        """连接属性控件信号"""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(
                lambda value: self._on_property_changed(prop_name, value)
            )
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(
                lambda value: self._on_property_changed(prop_name, value)
            )
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(
                lambda value: self._on_property_changed(prop_name, value)
            )
        elif isinstance(widget, QCheckBox):
            widget.toggled.connect(
                lambda value: self._on_property_changed(prop_name, value)
            )
            
    def _on_property_changed(self, prop_name, value):
        """属性值改变处理"""
        if self.current_component:
            # 保存属性到组件
            if not hasattr(self.current_component, 'custom_properties'):
                self.current_component.custom_properties = {}
            self.current_component.custom_properties[prop_name] = value

            self.property_changed.emit(self.current_component, prop_name, value)
            
    def get_component_properties(self):
        """获取当前组件的所有属性值"""
        if not self.current_component:
            return {}
            
        properties = {}
        for prop_name, widget in self.property_widgets.items():
            if isinstance(widget, QLineEdit):
                properties[prop_name] = widget.text()
            elif isinstance(widget, QComboBox):
                properties[prop_name] = widget.currentText()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                properties[prop_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                properties[prop_name] = widget.isChecked()
                
        return properties
        
    def set_component_properties(self, properties):
        """设置组件属性值"""
        for prop_name, value in properties.items():
            if prop_name in self.property_widgets:
                widget = self.property_widgets[prop_name]
                try:
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                        widget.setValue(value)
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
                except Exception as e:
                    print(f"设置属性 {prop_name} 失败: {e}")

    def create_slider_widget(self, prop_name, prop_config):
        """创建滑块控件"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(prop_config.get('min', 0))
        slider.setMaximum(prop_config.get('max', 100))
        slider.setValue(prop_config.get('default', 50))

        value_label = QLabel(str(slider.value()))

        def on_value_changed(value):
            value_label.setText(str(value))
            self.property_changed.emit(self.current_component, prop_name, value)

        slider.valueChanged.connect(on_value_changed)

        layout.addWidget(slider)
        layout.addWidget(value_label)

        return container

    def create_file_widget(self, prop_name, prop_config):
        """创建文件选择控件"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        line_edit = QLineEdit()
        line_edit.setText(prop_config.get('default', ''))
        line_edit.setPlaceholderText(prop_config.get('placeholder', '选择文件...'))

        browse_btn = QPushButton("浏览...")
        browse_btn.setMaximumWidth(60)

        def browse_file():
            file_filter = prop_config.get('filter', 'All Files (*)')
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", file_filter)
            if file_path:
                line_edit.setText(file_path)
                self.property_changed.emit(self.current_component, prop_name, file_path)

        browse_btn.clicked.connect(browse_file)

        def on_text_changed():
            self.property_changed.emit(self.current_component, prop_name, line_edit.text())

        line_edit.textChanged.connect(on_text_changed)

        layout.addWidget(line_edit)
        layout.addWidget(browse_btn)

        return container
