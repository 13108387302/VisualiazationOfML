#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件库模块
管理所有可用的机器学习组件
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QPen, QColor


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
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 创建组件分类树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("机器学习组件")
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QTreeWidget.DragOnly)
        
        # 创建组件分类
        self._create_component_categories()
        
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        # 连接拖拽事件
        self.tree.itemPressed.connect(self.on_item_pressed)
        
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
        if component_data:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(component_data))
            drag.setMimeData(mime_data)
            
            # 创建拖拽图标
            pixmap = self._create_drag_pixmap(component_data)
            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())
            
            # 执行拖拽
            drag.exec_(Qt.CopyAction)
            
    def _create_drag_pixmap(self, component_data):
        """创建拖拽图标"""
        pixmap = QPixmap(100, 60)
        pixmap.fill(QColor(200, 200, 200, 180))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        painter.drawRect(0, 0, 99, 59)
        painter.drawText(10, 30, component_data['name'])
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
