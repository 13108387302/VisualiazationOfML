#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件库模块
管理所有可用的机器学习组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QLabel, QLineEdit, QScrollArea)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QPen, QColor, QFont


class ComponentLibrary(QWidget):
    """组件库面板"""
    
    def __init__(self):
        super().__init__()
        self.component_types = self._init_component_types()
        self.init_ui()
        
    def _init_component_types(self):
        """初始化组件类型映射"""
        return {
            "数据加载": "data",
            "数据清洗": "data", 
            "特征选择": "data",
            "数据分割": "data",
            "标准化": "preprocess",
            "归一化": "preprocess",
            "编码": "preprocess",
            "降维": "preprocess",
            "线性回归": "model",
            "决策树": "model",
            "随机森林": "model",
            "SVM": "model",
            "神经网络": "model",
            "准确率": "evaluate",
            "混淆矩阵": "evaluate",
            "ROC曲线": "evaluate",
            "特征重要性": "evaluate",
            "结果保存": "output",
            "可视化": "output",
            "报告生成": "output"
        }
        
    def init_ui(self):
        """初始化用户界面 - 现代化设计"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # 搜索框
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(8, 8, 8, 8)

        search_label = QLabel("🔍 搜索组件")
        search_label.setFont(QFont("Arial", 9, QFont.Bold))
        search_label.setStyleSheet("color: #495057; background: transparent;")
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入组件名称...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        self.search_box.textChanged.connect(self.filter_components)
        search_layout.addWidget(self.search_box)

        layout.addWidget(search_container)

        # 创建组件分类树 - 改进样式
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("机器学习组件")
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QTreeWidget.DragOnly)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTreeWidget::item:hover {
                background-color: #f8f9fa;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)

        # 创建组件分类
        self._create_modern_component_categories()

        layout.addWidget(self.tree)
        self.setLayout(layout)

        # 连接拖拽事件
        self.tree.itemPressed.connect(self.on_item_pressed)

    def filter_components(self, text):
        """过滤组件（优化搜索性能）"""
        # 使用定时器延迟搜索，避免频繁过滤
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()

        from PyQt5.QtCore import QTimer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(lambda: self._do_filter_components(text))
        self.search_timer.start(300)  # 300ms延迟，等待用户停止输入

    def _do_filter_components(self, text):
        """实际执行组件过滤"""
        text_lower = text.lower()  # 预先转换为小写，避免重复转换

        for i in range(self.tree.topLevelItemCount()):
            category_item = self.tree.topLevelItem(i)
            category_visible = False

            for j in range(category_item.childCount()):
                child_item = category_item.child(j)
                # 优化字符串匹配
                if not text or text_lower in child_item.text(0).lower():
                    child_item.setHidden(False)
                    category_visible = True
                else:
                    child_item.setHidden(True)

            category_item.setHidden(not category_visible and bool(text))

    def _create_modern_component_categories(self):
        """创建现代化组件分类"""
        # 数据处理组件
        data_item = self.create_category_item("📊 数据处理", "#e3f2fd")
        data_item.addChild(self.create_component_item("📁 数据加载", "从文件或数据库加载数据"))
        data_item.addChild(self.create_component_item("🧹 数据清洗", "处理缺失值和异常值"))
        data_item.addChild(self.create_component_item("🎯 特征选择", "选择重要特征"))
        data_item.addChild(self.create_component_item("✂️ 数据分割", "分割训练和测试集"))

        # 预处理组件
        preprocess_item = self.create_category_item("🔧 预处理", "#f3e5f5")
        preprocess_item.addChild(self.create_component_item("📏 标准化", "标准化数据分布"))
        preprocess_item.addChild(self.create_component_item("📐 归一化", "归一化数据范围"))
        preprocess_item.addChild(self.create_component_item("🔤 编码", "编码分类变量"))
        preprocess_item.addChild(self.create_component_item("📉 降维", "降低数据维度"))

        # 机器学习模型
        model_item = self.create_category_item("🤖 机器学习", "#e8f5e8")
        model_item.addChild(self.create_component_item("📈 线性回归", "线性回归模型"))
        model_item.addChild(self.create_component_item("🌳 决策树", "决策树模型"))
        model_item.addChild(self.create_component_item("🌲 随机森林", "随机森林模型"))
        model_item.addChild(self.create_component_item("🎯 SVM", "支持向量机"))
        model_item.addChild(self.create_component_item("🧠 神经网络", "深度学习模型"))

        # 模型评估
        eval_item = self.create_category_item("📈 模型评估", "#fff3e0")
        eval_item.addChild(self.create_component_item("✅ 准确率", "计算模型准确率"))
        eval_item.addChild(self.create_component_item("📊 混淆矩阵", "生成混淆矩阵"))
        eval_item.addChild(self.create_component_item("📈 ROC曲线", "绘制ROC曲线"))
        eval_item.addChild(self.create_component_item("⭐ 特征重要性", "分析特征重要性"))

        # 输出导出
        output_item = self.create_category_item("📤 输出导出", "#fce4ec")
        output_item.addChild(self.create_component_item("💾 结果保存", "保存模型结果"))
        output_item.addChild(self.create_component_item("📊 可视化", "生成图表"))
        output_item.addChild(self.create_component_item("📄 报告生成", "生成分析报告"))

        # 添加到树中
        self.tree.addTopLevelItem(data_item)
        self.tree.addTopLevelItem(preprocess_item)
        self.tree.addTopLevelItem(model_item)
        self.tree.addTopLevelItem(eval_item)
        self.tree.addTopLevelItem(output_item)

        # 默认展开所有分类
        self.tree.expandAll()

    def create_category_item(self, name, color):
        """创建分类项"""
        item = QTreeWidgetItem([name])
        item.setFont(0, QFont("Arial", 10, QFont.Bold))
        # 设置分类项的背景色
        item.setData(0, Qt.UserRole, "category")
        return item

    def create_component_item(self, name, description):
        """创建组件项"""
        item = QTreeWidgetItem([name])
        item.setToolTip(0, description)
        item.setData(0, Qt.UserRole, "component")
        return item

    def _create_component_categories(self):
        """创建组件分类"""
        # 数据组件
        data_item = QTreeWidgetItem(["数据处理"])
        data_item.addChild(self.create_draggable_item("数据加载"))
        data_item.addChild(self.create_draggable_item("数据清洗"))
        data_item.addChild(self.create_draggable_item("特征选择"))
        data_item.addChild(self.create_draggable_item("数据分割"))
        
        # 预处理组件
        preprocess_item = QTreeWidgetItem(["预处理"])
        preprocess_item.addChild(self.create_draggable_item("标准化"))
        preprocess_item.addChild(self.create_draggable_item("归一化"))
        preprocess_item.addChild(self.create_draggable_item("编码"))
        preprocess_item.addChild(self.create_draggable_item("降维"))
        
        # 模型组件
        model_item = QTreeWidgetItem(["机器学习模型"])
        model_item.addChild(self.create_draggable_item("线性回归"))
        model_item.addChild(self.create_draggable_item("决策树"))
        model_item.addChild(self.create_draggable_item("随机森林"))
        model_item.addChild(self.create_draggable_item("SVM"))
        model_item.addChild(self.create_draggable_item("神经网络"))
        
        # 评估组件
        eval_item = QTreeWidgetItem(["模型评估"])
        eval_item.addChild(self.create_draggable_item("准确率"))
        eval_item.addChild(self.create_draggable_item("混淆矩阵"))
        eval_item.addChild(self.create_draggable_item("ROC曲线"))
        eval_item.addChild(self.create_draggable_item("特征重要性"))
        
        # 输出组件
        output_item = QTreeWidgetItem(["输出"])
        output_item.addChild(self.create_draggable_item("结果保存"))
        output_item.addChild(self.create_draggable_item("可视化"))
        output_item.addChild(self.create_draggable_item("报告生成"))
        
        # 添加到树中
        self.tree.addTopLevelItem(data_item)
        self.tree.addTopLevelItem(preprocess_item)
        self.tree.addTopLevelItem(model_item)
        self.tree.addTopLevelItem(eval_item)
        self.tree.addTopLevelItem(output_item)
        
        # 展开所有项目
        self.tree.expandAll()
        
    def create_draggable_item(self, name):
        """创建可拖拽的组件项"""
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, {
            'name': name,
            'type': self.component_types.get(name, 'unknown')
        })
        return item
        
    def on_item_pressed(self, item, column):
        """处理项目按下事件"""
        _ = column  # 忽略column参数
        if item.parent() is not None:  # 只有子项目可以拖拽
            self.start_drag(item)
            
    def start_drag(self, item):
        """开始拖拽"""
        component_data = item.data(0, Qt.UserRole)
        if component_data == "component":  # 检查是否是组件项
            component_name = item.text(0)
            drag = QDrag(self)
            mime_data = QMimeData()
            # 只传递组件名称，简化数据传输
            mime_data.setText(component_name)
            drag.setMimeData(mime_data)

            # 创建拖拽图标
            pixmap = self._create_drag_pixmap(component_name)
            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())

            # 执行拖拽
            drag.exec_(Qt.CopyAction)
            
    def _create_drag_pixmap(self, component_name):
        """创建拖拽图标"""
        pixmap = QPixmap(100, 60)
        pixmap.fill(QColor(200, 200, 200, 180))

        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        painter.drawRect(0, 0, 99, 59)
        # 简化文本显示，只显示组件名称
        painter.drawText(10, 30, str(component_name))
        painter.end()

        return pixmap
        
    def get_component_info(self, component_name):
        """获取组件信息"""
        return {
            'name': component_name,
            'type': self.component_types.get(component_name, 'unknown'),
            'description': self._get_component_description(component_name)
        }
        
    def _get_component_description(self, component_name):
        """获取组件描述"""
        descriptions = {
            "数据加载": "从文件或数据库加载数据",
            "数据清洗": "处理缺失值、异常值等数据质量问题",
            "特征选择": "选择对模型最有用的特征",
            "数据分割": "将数据分为训练集和测试集",
            "标准化": "将特征缩放到标准正态分布",
            "归一化": "将特征缩放到指定范围",
            "编码": "对分类变量进行编码",
            "降维": "减少特征维度",
            "线性回归": "线性回归模型",
            "决策树": "决策树分类/回归模型",
            "随机森林": "随机森林集成模型",
            "SVM": "支持向量机模型",
            "神经网络": "多层感知机神经网络",
            "准确率": "计算模型预测准确率",
            "混淆矩阵": "生成混淆矩阵",
            "ROC曲线": "绘制ROC曲线",
            "特征重要性": "分析特征重要性",
            "结果保存": "保存模型结果到文件",
            "可视化": "生成结果可视化图表",
            "报告生成": "生成分析报告"
        }
        return descriptions.get(component_name, "暂无描述")
        
    def add_custom_component(self, category, name, component_type, description=""):
        """添加自定义组件"""
        self.component_types[name] = component_type
        
        # 找到对应的分类并添加组件
        for i in range(self.tree.topLevelItemCount()):
            category_item = self.tree.topLevelItem(i)
            if category_item.text(0) == category:
                category_item.addChild(self.create_draggable_item(name))
                break
