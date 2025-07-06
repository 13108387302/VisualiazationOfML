import sys
import json
import uuid
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns

# ======================
# 核心组件系统
# ======================
class MLComponent:
    """机器学习组件基类"""
    def __init__(self, name, category="未分类", icon="🔵"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.category = category
        self.icon = icon
        self.input_ports = []
        self.output_ports = []
        self.params = {}
        self.position = (0, 0)
        self.size = (120, 80)
        self.color = QColor(70, 130, 180)  # 钢蓝色
        
    def add_input_port(self, name, data_type="any"):
        self.input_ports.append({"name": name, "data_type": data_type, "connections": []})
        
    def add_output_port(self, name, data_type="any"):
        self.output_ports.append({"name": name, "data_type": data_type, "connections": []})
        
    def set_param(self, name, value):
        self.params[name] = value
        
    def execute(self, inputs):
        """执行组件逻辑，返回输出字典"""
        raise NotImplementedError("子类必须实现execute方法")
    
    def to_dict(self):
        """序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "icon": self.icon,
            "params": self.params,
            "position": self.position,
            "input_ports": self.input_ports,
            "output_ports": self.output_ports
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        component = cls(data["name"], data.get("category", "未分类"), data.get("icon", "🔵"))
        component.id = data["id"]
        component.params = data["params"]
        component.position = data["position"]
        component.input_ports = data["input_ports"]
        component.output_ports = data["output_ports"]
        return component

# 具体组件实现
class DataLoader(MLComponent):
    """数据加载组件"""
    def __init__(self):
        super().__init__("数据加载", "数据", "📊")
        self.add_output_port("数据集", "pd.DataFrame")
        self.set_param("dataset", "iris")
        self.color = QColor(46, 139, 87)  # 海洋绿
        
    def execute(self, inputs):
        if self.params["dataset"] == "iris":
            iris = load_iris()
            df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
            df['target'] = iris.target
            return {"数据集": df}
        elif self.params["dataset"] == "titanic":
            # 实际项目中可加载真实数据
            return {"数据集": pd.DataFrame()}
        else:
            # 自定义数据加载
            return {"数据集": pd.DataFrame()}

class DataSplitter(MLComponent):
    """数据拆分组件"""
    def __init__(self):
        super().__init__("数据拆分", "数据", "✂️")
        self.add_input_port("数据集", "pd.DataFrame")
        self.add_output_port("训练集", "pd.DataFrame")
        self.add_output_port("测试集", "pd.DataFrame")
        self.set_param("test_size", 0.2)
        self.set_param("random_state", 42)
        self.color = QColor(210, 105, 30)  # 巧克力色
        
    def execute(self, inputs):
        df = inputs["数据集"]
        train, test = train_test_split(
            df, 
            test_size=float(self.params["test_size"]), 
            random_state=int(self.params["random_state"])
        )
        return {"训练集": train, "测试集": test}

class StandardScalerComponent(MLComponent):
    """标准化组件"""
    def __init__(self):
        super().__init__("特征标准化", "预处理", "📏")
        self.add_input_port("数据集", "pd.DataFrame")
        self.add_output_port("标准化数据", "pd.DataFrame")
        self.color = QColor(218, 165, 32)  # 金色
        
    def execute(self, inputs):
        df = inputs["数据集"]
        scaler = StandardScaler()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        return {"标准化数据": df}

class RandomForestClassifierComponent(MLComponent):
    """随机森林分类器"""
    def __init__(self):
        super().__init__("随机森林", "模型", "🌲")
        self.add_input_port("训练集", "pd.DataFrame")
        self.add_output_port("模型", "sklearn.Model")
        self.set_param("n_estimators", 100)
        self.set_param("max_depth", 5)
        self.color = QColor(50, 205, 50)  # 酸橙绿
        
    def execute(self, inputs):
        train = inputs["训练集"]
        X = train.drop('target', axis=1)
        y = train['target']
        
        model = RandomForestClassifier(
            n_estimators=int(self.params["n_estimators"]),
            max_depth=int(self.params["max_depth"])
        )
        model.fit(X, y)
        return {"模型": model}

class ModelEvaluator(MLComponent):
    """模型评估器"""
    def __init__(self):
        super().__init__("模型评估", "评估", "📈")
        self.add_input_port("模型", "sklearn.Model")
        self.add_input_port("测试集", "pd.DataFrame")
        self.add_output_port("准确率", "float")
        self.add_output_port("混淆矩阵", "plt.Figure")
        self.color = QColor(138, 43, 226)  # 紫罗兰色
        
    def execute(self, inputs):
        model = inputs["模型"]
        test = inputs["测试集"]
        
        X_test = test.drop('target', axis=1)
        y_test = test['target']
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 创建混淆矩阵图
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(pd.crosstab(y_test, y_pred), 
                   annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title('混淆矩阵')
        
        return {"准确率": accuracy, "混淆矩阵": fig}

# ======================
# 工作流引擎
# ======================
class WorkflowEngine:
    """工作流执行引擎"""
    def __init__(self):
        self.components = {}  # id -> component
        self.connections = []  # (from_id, from_port, to_id, to_port)
        self.execution_order = []
        self.results = {}  # component_id -> output
        
    def add_component(self, component):
        self.components[component.id] = component
        
    def remove_component(self, component_id):
        # 删除组件及相关的连接
        self.components.pop(component_id, None)
        self.connections = [c for c in self.connections 
                           if c[0] != component_id and c[2] != component_id]
        
    def connect_ports(self, from_id, from_port, to_id, to_port):
        # 检查连接是否有效
        from_comp = self.components[from_id]
        to_comp = self.components[to_id]
        
        # 找到对应的输出端口和输入端口
        out_port = next((p for p in from_comp.output_ports if p["name"] == from_port), None)
        in_port = next((p for p in to_comp.input_ports if p["name"] == to_port), None)
        
        if not out_port or not in_port:
            return False
            
        # 检查数据类型是否兼容
        if out_port["data_type"] != "any" and in_port["data_type"] != "any" and \
           out_port["data_type"] != in_port["data_type"]:
            return False
            
        # 添加连接
        self.connections.append((from_id, from_port, to_id, to_port))
        return True
        
    def disconnect_ports(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
        
    def validate_workflow(self):
        """验证工作流是否有效"""
        # 1. 检查是否有环
        # 2. 检查所有输入是否都有连接
        # 这里简化实现，实际项目中需要完整实现
        return True
        
    def topological_sort(self):
        """对组件进行拓扑排序"""
        # 构建依赖图
        graph = {comp_id: [] for comp_id in self.components}
        in_degree = {comp_id: 0 for comp_id in self.components}
        
        for conn in self.connections:
            from_id, _, to_id, _ = conn
            graph[from_id].append(to_id)
            in_degree[to_id] += 1
            
        # 拓扑排序
        queue = [comp_id for comp_id in self.components if in_degree[comp_id] == 0]
        order = []
        
        while queue:
            node = queue.pop(0)
            order.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(order) != len(self.components):
            raise RuntimeError("工作流中存在循环依赖")
            
        self.execution_order = order
        return order
        
    def execute_workflow(self):
        """执行整个工作流"""
        if not self.validate_workflow():
            return False
            
        self.topological_sort()
        self.results = {}
        
        for comp_id in self.execution_order:
            comp = self.components[comp_id]
            
            # 收集输入数据
            inputs = {}
            for conn in self.connections:
                if conn[2] == comp_id:  # 目标组件是当前组件
                    from_id, from_port, _, to_port = conn
                    
                    # 确保源组件已执行
                    if from_id not in self.results:
                        raise RuntimeError(f"依赖组件 {from_id} 未执行")
                        
                    # 获取数据
                    from_outputs = self.results[from_id]
                    if from_port in from_outputs:
                        inputs[to_port] = from_outputs[from_port]
            
            # 执行组件
            try:
                outputs = comp.execute(inputs)
                self.results[comp_id] = outputs
            except Exception as e:
                print(f"执行组件 {comp.name} 时出错: {str(e)}")
                self.results[comp_id] = {"error": str(e)}
                return False
                
        return True

# ======================
# GUI 界面
# ======================
class PortWidget(QWidget):
    """端口显示控件"""
    def __init__(self, port, is_input, parent=None):
        super().__init__(parent)
        self.port = port
        self.is_input = is_input
        
        layout = QHBoxLayout()
        if is_input:
            layout.addWidget(QLabel("◀"))
        else:
            layout.addWidget(QLabel("▶"))
            
        layout.addWidget(QLabel(port["name"]))
        self.setLayout(layout)
        
        self.setFixedHeight(20)
        
    def mousePressEvent(self, event):
        """处理端口点击事件"""
        if event.button() == Qt.LeftButton:
            self.parent().port_clicked(self, self.is_input)

class ComponentWidget(QGraphicsItem):
    """组件图形项"""
    def __init__(self, component, engine):
        super().__init__()
        self.component = component
        self.engine = engine
        self.setPos(*component.position)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # 创建端口控件
        self.port_widgets = []
        
    def boundingRect(self):
        return QRectF(0, 0, self.component.size[0], self.component.size[1])
        
    def paint(self, painter, option, widget):
        # 绘制组件背景
        color = self.component.color
        if self.isSelected():
            color = color.darker(120)
            
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black, 1.5))
        painter.drawRoundedRect(0, 0, self.component.size[0], self.component.size[1], 5, 5)
        
        # 绘制标题栏
        painter.setBrush(QBrush(color.darker(130)))
        painter.drawRect(0, 0, self.component.size[0], 25)
        
        # 绘制标题
        painter.setPen(Qt.white)
        painter.drawText(QRectF(5, 0, self.component.size[0]-10, 25), 
                        Qt.AlignLeft | Qt.AlignVCenter, 
                        f"{self.component.icon} {self.component.name}")
        
        # 绘制端口
        input_y = 30
        for port in self.component.input_ports:
            painter.drawText(QRectF(5, input_y, 100, 20), 
                           Qt.AlignLeft | Qt.AlignVCenter, 
                           f"◀ {port['name']}")
            input_y += 20
            
        output_y = 30
        for port in self.component.output_ports:
            painter.drawText(QRectF(self.component.size[0]-105, output_y, 100, 20), 
                           Qt.AlignRight | Qt.AlignVCenter, 
                           f"{port['name']} ▶")
            output_y += 20
            
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # 更新组件位置
        self.component.position = (self.x(), self.y())
        
    def contextMenuEvent(self, event):
        menu = QMenu()
        
        # 添加删除操作
        delete_action = QAction("删除组件", menu)
        delete_action.triggered.connect(lambda: self.engine.remove_component(self.component.id))
        menu.addAction(delete_action)
        
        # 添加配置操作
        config_action = QAction("配置参数", menu)
        config_action.triggered.connect(self.show_config_dialog)
        menu.addAction(config_action)
        
        menu.exec_(event.screenPos())
        
    def show_config_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle(f"配置 {self.component.name}")
        layout = QFormLayout()
        
        # 为每个参数创建输入控件
        self.param_edits = {}
        for param, value in self.component.params.items():
            if isinstance(value, bool):
                edit = QCheckBox()
                edit.setChecked(value)
            elif isinstance(value, int):
                edit = QSpinBox()
                edit.setRange(0, 10000)
                edit.setValue(value)
            elif isinstance(value, float):
                edit = QDoubleSpinBox()
                edit.setRange(0.0, 1.0)
                edit.setValue(value)
                edit.setSingleStep(0.01)
            else:
                edit = QLineEdit(str(value))
                
            layout.addRow(QLabel(param), edit)
            self.param_edits[param] = edit
            
        # 添加确定/取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # 更新参数值
            for param, edit in self.param_edits.items():
                if isinstance(edit, QCheckBox):
                    self.component.set_param(param, edit.isChecked())
                elif isinstance(edit, QSpinBox):
                    self.component.set_param(param, edit.value())
                elif isinstance(edit, QDoubleSpinBox):
                    self.component.set_param(param, edit.value())
                else:
                    self.component.set_param(param, edit.text())

class ConnectionItem(QGraphicsPathItem):
    """连接线图形项"""
    def __init__(self, start_item, start_port, end_item, end_port):
        super().__init__()
        self.start_item = start_item
        self.start_port = start_port
        self.end_item = end_item
        self.end_port = end_port
        self.setPen(QPen(Qt.black, 2))
        self.setZValue(-1)  # 确保在组件下方
        self.update_path()
        
    def update_path(self):
        """更新连接线路径"""
        # 计算起点位置（输出端口）
        start_rect = self.start_item.boundingRect()
        start_x = self.start_item.x() + start_rect.width()
        start_y = self.start_item.y() + 40  # 简化处理
        
        # 计算终点位置（输入端口）
        end_rect = self.end_item.boundingRect()
        end_x = self.end_item.x()
        end_y = self.end_item.y() + 40  # 简化处理
        
        # 创建贝塞尔曲线路径
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        
        # 控制点使曲线更平滑
        ctrl1_x = start_x + (end_x - start_x) * 0.5
        ctrl1_y = start_y
        ctrl2_x = start_x + (end_x - start_x) * 0.5
        ctrl2_y = end_y
        
        path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
        self.setPath(path)

class Canvas(QGraphicsView):
    """主画布"""
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)
        
        self.temp_connection = None
        self.connection_source = None
        
    def add_component(self, component):
        """添加组件到画布"""
        comp_widget = ComponentWidget(component, self.engine)
        self.scene.addItem(comp_widget)
        self.engine.add_component(component)
        return comp_widget
        
    def port_clicked(self, port_widget, is_input):
        """处理端口点击事件"""
        if is_input:
            # 如果是输入端口，完成连接
            if self.connection_source:
                source_item = self.connection_source["item"]
                source_port = self.connection_source["port"]
                target_item = port_widget.parent()
                target_port = port_widget.port["name"]
                
                # 添加到引擎
                if self.engine.connect_ports(
                    source_item.component.id, source_port,
                    target_item.component.id, target_port
                ):
                    # 创建连接图形
                    connection = ConnectionItem(
                        source_item, source_port,
                        target_item, target_port
                    )
                    self.scene.addItem(connection)
                
                # 清理临时连接
                if self.temp_connection:
                    self.scene.removeItem(self.temp_connection)
                    self.temp_connection = None
                self.connection_source = None
        else:
            # 如果是输出端口，开始新连接
            self.connection_source = {
                "item": port_widget.parent(),
                "port": port_widget.port["name"]
            }
            
            # 创建临时连接
            if self.temp_connection:
                self.scene.removeItem(self.temp_connection)
                
            start_pos = port_widget.parent().mapToScene(
                port_widget.parent().boundingRect().topRight()
            )
            self.temp_connection = QGraphicsLineItem(
                start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y()
            )
            self.temp_connection.setPen(QPen(Qt.gray, 2, Qt.DashLine))
            self.scene.addItem(self.temp_connection)
            
    def mouseMoveEvent(self, event):
        """更新临时连接位置"""
        super().mouseMoveEvent(event)
        if self.temp_connection and self.connection_source:
            mouse_pos = self.mapToScene(event.pos())
            start_pos = self.mapFromScene(
                self.connection_source["item"].mapToScene(
                    self.connection_source["item"].boundingRect().topRight()
                )
            )
            self.temp_connection.setLine(
                start_pos.x(), start_pos.y() + 40,  # 简化处理
                mouse_pos.x(), mouse_pos.y()
            )

class ComponentLibrary(QListWidget):
    """组件库面板"""
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setDragEnabled(True)
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(60, 60))
        self.setSpacing(10)
        self.setAcceptDrops(False)
        self.setMaximumWidth(150)
        
        self.load_components()
        
    def load_components(self):
        """加载可用组件"""
        categories = {
            "数据": [DataLoader(), DataSplitter()],
            "预处理": [StandardScalerComponent()],
            "模型": [RandomForestClassifierComponent()],
            "评估": [ModelEvaluator()]
        }
        
        for category, components in categories.items():
            # 添加分类标题
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.NoItemFlags)
            category_item.setBackground(QColor(220, 220, 220))
            self.addItem(category_item)
            
            # 添加组件
            for comp in components:
                item = QListWidgetItem(comp.icon + " " + comp.name)
                item.setData(Qt.UserRole, comp)
                self.addItem(item)
                
    def startDrag(self, supportedActions):
        """开始拖拽组件"""
        item = self.currentItem()
        if item and item.data(Qt.UserRole):
            comp = item.data(Qt.UserRole)
            
            # 创建拖拽
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(comp.name)
            drag.setMimeData(mime)
            
            # 执行拖拽
            drag.exec_(Qt.CopyAction)

class ResultViewer(QTabWidget):
    """结果查看器"""
    def __init__(self):
        super().__init__()
        self.setTabPosition(QTabWidget.South)
        
        # 添加标签页
        self.addTab(QLabel("执行结果将显示在这里"), "结果")
        self.addTab(QTextEdit(), "日志")
        
        # 存储结果控件
        self.result_widgets = {}
        
    def show_results(self, component_id, outputs):
        """显示组件输出结果"""
        # 清除旧结果
        if component_id in self.result_widgets:
            self.removeTab(self.indexOf(self.result_widgets[component_id]))
            
        # 创建新的结果容器
        container = QScrollArea()
        container.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # 添加每个输出
        for name, value in outputs.items():
            if name == "error":
                # 错误信息
                error_label = QLabel(f"<font color='red'>错误: {value}</font>")
                layout.addWidget(error_label)
            elif isinstance(value, float):
                # 数值结果
                layout.addWidget(QLabel(f"{name}: {value:.4f}"))
            elif isinstance(value, plt.Figure):
                # 图形结果
                canvas = FigureCanvas(value)
                layout.addWidget(canvas)
            elif isinstance(value, pd.DataFrame):
                # 数据表格
                table = QTableWidget()
                table.setRowCount(value.shape[0])
                table.setColumnCount(value.shape[1])
                table.setHorizontalHeaderLabels(value.columns)
                
                for i in range(value.shape[0]):
                    for j in range(value.shape[1]):
                        table.setItem(i, j, QTableWidgetItem(str(value.iloc[i, j])))
                
                layout.addWidget(table)
        
        container.setWidget(content)
        self.addTab(container, f"结果: {component_id[:8]}")
        self.setCurrentIndex(self.count()-1)
        self.result_widgets[component_id] = container

class MLWorkflowApp(QMainWindow):
    """主应用程序窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMLFlow - 交互式机器学习工作流")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建工作流引擎
        self.engine = WorkflowEngine()
        
        # 创建主界面
        self.create_ui()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_ui(self):
        """创建用户界面"""
        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧组件库
        self.canvas = Canvas(self.engine)
        self.library = ComponentLibrary(self.canvas)
        
        # 右侧面板
        right_panel = QSplitter(Qt.Vertical)
        
        # 属性编辑器
        self.property_editor = QTextEdit()
        self.property_editor.setPlaceholderText("选择组件查看和编辑属性")
        
        # 结果查看器
        self.result_viewer = ResultViewer()
        
        right_panel.addWidget(self.property_editor)
        right_panel.addWidget(self.result_viewer)
        right_panel.setSizes([300, 500])
        
        # 添加组件到主布局
        main_layout.addWidget(self.library, 1)
        main_layout.addWidget(self.canvas, 4)
        main_layout.addWidget(right_panel, 2)
        
        self.setCentralWidget(main_widget)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 连接信号
        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("操作")
        
        # 运行按钮
        run_action = QAction("▶ 运行工作流", self)
        run_action.triggered.connect(self.run_workflow)
        toolbar.addAction(run_action)
        
        # 保存按钮
        save_action = QAction("💾 保存", self)
        save_action.triggered.connect(self.save_workflow)
        toolbar.addAction(save_action)
        
        # 加载按钮
        load_action = QAction("📂 加载", self)
        load_action.triggered.connect(self.load_workflow)
        toolbar.addAction(load_action)
        
    def on_selection_changed(self):
        """当选择改变时更新属性编辑器"""
        items = self.canvas.scene.selectedItems()
        if items:
            comp_widget = items[0]
            comp = comp_widget.component
            
            # 显示组件属性
            prop_text = f"<h2>{comp.name}</h2>"
            prop_text += f"<p><b>ID:</b> {comp.id}</p>"
            prop_text += "<h3>参数</h3><ul>"
            
            for param, value in comp.params.items():
                prop_text += f"<li><b>{param}:</b> {value}</li>"
                
            prop_text += "</ul>"
            
            self.property_editor.setHtml(prop_text)
            
    def run_workflow(self):
        """执行工作流"""
        self.statusBar().showMessage("正在执行工作流...")
        QApplication.processEvents()  # 更新UI
        
        success = self.engine.execute_workflow()
        
        if success:
            self.statusBar().showMessage("工作流执行成功!")
            # 显示所有组件结果
            for comp_id, outputs in self.engine.results.items():
                if "error" not in outputs:  # 跳过错误结果
                    self.result_viewer.show_results(comp_id, outputs)
        else:
            self.statusBar().showMessage("工作流执行失败!")
            
    def save_workflow(self):
        """保存工作流到文件"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存工作流", "", "JSON Files (*.json)"
        )
        if filename:
            workflow_data = {
                "components": [comp.to_dict() for comp in self.engine.components.values()],
                "connections": self.engine.connections
            }
            with open(filename, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            self.statusBar().showMessage(f"工作流已保存到 {filename}")
            
    def load_workflow(self):
        """从文件加载工作流"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载工作流", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    workflow_data = json.load(f)
                
                # 清除当前工作流
                self.canvas.scene.clear()
                self.engine = WorkflowEngine()
                
                # 加载组件
                component_map = {}
                for comp_data in workflow_data["components"]:
                    # 根据类型创建具体组件
                    comp_classes = {
                        "数据加载": DataLoader,
                        "数据拆分": DataSplitter,
                        "特征标准化": StandardScalerComponent,
                        "随机森林": RandomForestClassifierComponent,
                        "模型评估": ModelEvaluator
                    }
                    
                    comp_class = comp_classes.get(comp_data["name"], MLComponent)
                    comp = comp_class.from_dict(comp_data)
                    comp_widget = self.canvas.add_component(comp)
                    comp_widget.setPos(*comp.position)
                    component_map[comp.id] = comp
                
                # 加载连接
                self.engine.connections = workflow_data["connections"]
                
                # 创建连接图形
                for conn in self.engine.connections:
                    from_id, from_port, to_id, to_port = conn
                    from_comp = component_map[from_id]
                    to_comp = component_map[to_id]
                    
                    # 找到对应的图形项
                    from_item = next(item for item in self.canvas.scene.items() 
                                    if isinstance(item, ComponentWidget) and item.component.id == from_id)
                    to_item = next(item for item in self.canvas.scene.items() 
                                 if isinstance(item, ComponentWidget) and item.component.id == to_id)
                    
                    connection = ConnectionItem(from_item, from_port, to_item, to_port)
                    self.canvas.scene.addItem(connection)
                
                self.statusBar().showMessage(f"工作流已从 {filename} 加载")
            except Exception as e:
                QMessageBox.critical(self, "加载错误", f"加载工作流失败: {str(e)}")
                self.statusBar().showMessage("加载失败!")

# ======================
# 运行应用程序
# ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用样式
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MLWorkflowApp()
    window.show()
    sys.exit(app.exec_())
