# 机器学习可视化界面 - API文档

## 📋 目录
1. [核心模块API](#核心模块api)
2. [组件系统API](#组件系统api)
3. [事件系统API](#事件系统api)
4. [数据管理API](#数据管理api)
5. [工具函数API](#工具函数api)
6. [后端接口API](#后端接口api)

## 🏗️ 核心模块API

### MLVisualizationUI (主窗口)

#### 类定义
```python
class MLVisualizationUI(QMainWindow):
    """主窗口类，管理整个应用程序的界面和交互"""
```

#### 主要方法

##### 文件操作
```python
def new_project(self) -> None:
    """创建新项目"""
    
def open_project(self) -> None:
    """打开项目文件"""
    
def save_project(self) -> None:
    """保存当前项目"""
    
def save_project_as(self) -> None:
    """另存为项目文件"""
    
def _save_to_file(self, file_path: str) -> None:
    """保存项目到指定文件
    
    Args:
        file_path: 文件路径
    """
```

##### 事件处理
```python
def on_component_selected(self, component: MLComponent) -> None:
    """处理组件选择事件
    
    Args:
        component: 被选择的组件，None表示取消选择
    """
    
def on_component_added(self, component: MLComponent) -> None:
    """处理组件添加事件
    
    Args:
        component: 新添加的组件
    """
    
def on_connection_created(self, connection: ConnectionLine) -> None:
    """处理连接创建事件
    
    Args:
        connection: 新创建的连接
    """
    
def on_property_changed(self, component: MLComponent, prop_name: str, value: Any) -> None:
    """处理属性改变事件
    
    Args:
        component: 属性被修改的组件
        prop_name: 属性名称
        value: 新的属性值
    """
```

##### 界面操作
```python
def zoom_in(self) -> None:
    """放大画布"""
    
def zoom_out(self) -> None:
    """缩小画布"""
    
def fit_to_window(self) -> None:
    """适应窗口大小"""
    
def run_pipeline(self) -> None:
    """执行机器学习流程"""
    
def stop_pipeline(self) -> None:
    """停止流程执行"""
```

### MLCanvas (画布)

#### 类定义
```python
class MLCanvas(QGraphicsView):
    """画布类，负责组件的显示、交互和连接管理"""
    
    # 信号定义
    component_selected = pyqtSignal(object)
    component_added = pyqtSignal(object)
    connection_created = pyqtSignal(object)
```

#### 主要方法

##### 组件管理
```python
def add_component(self, component_type: str, name: str, pos: QPointF = None) -> MLComponent:
    """添加组件到画布
    
    Args:
        component_type: 组件类型 ('data', 'preprocess', 'model', 'evaluate', 'output')
        name: 组件名称
        pos: 组件位置，默认为(0,0)
        
    Returns:
        创建的组件实例
    """
    
def remove_component(self, component: MLComponent) -> None:
    """从画布移除组件
    
    Args:
        component: 要移除的组件
    """
    
def clear_canvas(self) -> None:
    """清空画布上的所有组件和连接"""
```

##### 连接管理
```python
def start_connection(self, start_port: ConnectionPort) -> None:
    """开始创建连接
    
    Args:
        start_port: 起始端口
    """
    
def finish_connection(self, end_port: ConnectionPort) -> None:
    """完成连接创建
    
    Args:
        end_port: 结束端口
    """
    
def cancel_connection(self) -> None:
    """取消当前连接创建"""
    
def remove_connection(self, connection: ConnectionLine) -> None:
    """移除连接
    
    Args:
        connection: 要移除的连接
    """
```

##### 数据管理
```python
def get_workflow_data(self) -> Dict[str, Any]:
    """获取工作流程数据
    
    Returns:
        包含组件和连接信息的字典
    """
    
def load_workflow_data(self, workflow_data: Dict[str, Any]) -> None:
    """加载工作流程数据
    
    Args:
        workflow_data: 工作流程数据字典
    """
```

##### 视图操作
```python
def fit_to_contents(self) -> None:
    """适应内容大小"""
    
def wheelEvent(self, event: QWheelEvent) -> None:
    """处理鼠标滚轮事件（缩放）
    
    Args:
        event: 滚轮事件
    """
```

## 🧩 组件系统API

### MLComponent (ML组件)

#### 类定义
```python
class MLComponent(QGraphicsRectItem):
    """机器学习组件基类"""
```

#### 构造函数
```python
def __init__(self, component_type: str, name: str, width: int = 120, height: int = 80):
    """初始化ML组件
    
    Args:
        component_type: 组件类型
        name: 组件名称
        width: 组件宽度
        height: 组件高度
    """
```

#### 主要方法
```python
def setup_appearance(self) -> None:
    """设置组件外观（颜色、样式）"""
    
def create_ports(self) -> None:
    """创建输入输出端口"""
    
def get_properties(self) -> Dict[str, Any]:
    """获取组件属性
    
    Returns:
        组件属性字典
    """
    
def set_properties(self, properties: Dict[str, Any]) -> None:
    """设置组件属性
    
    Args:
        properties: 属性字典
    """
```

#### 属性
```python
component_type: str          # 组件类型
name: str                   # 组件名称
input_ports: List[ConnectionPort]   # 输入端口列表
output_ports: List[ConnectionPort]  # 输出端口列表
connections: List[ConnectionLine]   # 连接列表
```

### ConnectionPort (连接端口)

#### 类定义
```python
class ConnectionPort(QGraphicsEllipseItem):
    """连接端口类"""
```

#### 构造函数
```python
def __init__(self, parent_component: MLComponent, port_type: str, index: int, is_input: bool = True):
    """初始化连接端口
    
    Args:
        parent_component: 父组件
        port_type: 端口类型
        index: 端口索引
        is_input: 是否为输入端口
    """
```

#### 主要方法
```python
def update_position(self) -> None:
    """更新端口位置"""
```

#### 属性
```python
parent_component: MLComponent  # 父组件
port_type: str                # 端口类型
index: int                    # 端口索引
is_input: bool               # 是否为输入端口
connections: List[ConnectionLine]  # 连接到此端口的连接列表
```

### ConnectionLine (连接线)

#### 类定义
```python
class ConnectionLine(QGraphicsLineItem):
    """连接线类"""
```

#### 构造函数
```python
def __init__(self, start_port: ConnectionPort, end_port: ConnectionPort = None):
    """初始化连接线
    
    Args:
        start_port: 起始端口
        end_port: 结束端口，可选
    """
```

#### 主要方法
```python
def update_line(self) -> None:
    """更新连接线位置"""
    
def set_temp_end_pos(self, pos: QPointF) -> None:
    """设置临时结束位置（拖拽时使用）
    
    Args:
        pos: 临时结束位置
    """
```

#### 属性
```python
start_port: ConnectionPort    # 起始端口
end_port: ConnectionPort     # 结束端口
temp_end_pos: QPointF       # 临时结束位置
```

## 📡 事件系统API

### 信号定义

#### MLCanvas信号
```python
component_selected = pyqtSignal(object)  # 组件选择信号
component_added = pyqtSignal(object)     # 组件添加信号
connection_created = pyqtSignal(object)  # 连接创建信号
```

#### PropertyPanel信号
```python
property_changed = pyqtSignal(object, str, object)  # 属性改变信号
# 参数: (组件, 属性名, 新值)
```

### 事件处理模式

#### 连接信号槽
```python
# 在主窗口中连接信号
def connect_signals(self):
    self.canvas.component_selected.connect(self.on_component_selected)
    self.canvas.component_added.connect(self.on_component_added)
    self.canvas.connection_created.connect(self.on_connection_created)
    self.property_panel.property_changed.connect(self.on_property_changed)
```

#### 自定义事件处理
```python
def on_custom_event(self, *args):
    """自定义事件处理函数
    
    Args:
        *args: 事件参数
    """
    # 处理逻辑
    pass
```

## 💾 数据管理API

### WorkflowManager (工作流程管理器)

#### 类定义
```python
class WorkflowManager:
    """工作流程管理器，负责组件和连接的数据管理"""
```

#### 主要方法
```python
def add_component(self, component_config: ComponentConfig) -> None:
    """添加组件配置
    
    Args:
        component_config: 组件配置对象
    """
    
def add_connection(self, connection_config: ConnectionConfig) -> None:
    """添加连接配置
    
    Args:
        connection_config: 连接配置对象
    """
    
def remove_component(self, component_id: str) -> None:
    """移除组件
    
    Args:
        component_id: 组件ID
    """
    
def get_execution_order(self) -> List[str]:
    """获取组件执行顺序（拓扑排序）
    
    Returns:
        组件ID的执行顺序列表
        
    Raises:
        ValueError: 检测到循环依赖时
    """
    
def validate_workflow(self) -> List[str]:
    """验证工作流程
    
    Returns:
        错误信息列表，空列表表示验证通过
    """
    
def export_to_dict(self) -> Dict[str, Any]:
    """导出为字典格式
    
    Returns:
        工作流程数据字典
    """
    
def import_from_dict(self, data: Dict[str, Any]) -> None:
    """从字典导入数据
    
    Args:
        data: 工作流程数据字典
    """
```

### 数据类定义

#### ComponentConfig
```python
@dataclass
class ComponentConfig:
    """组件配置数据类"""
    component_id: str      # 组件唯一ID
    component_type: str    # 组件类型
    name: str             # 组件名称
    position: tuple       # 组件位置 (x, y)
    properties: dict      # 组件属性字典
```

#### ConnectionConfig
```python
@dataclass
class ConnectionConfig:
    """连接配置数据类"""
    start_component: str  # 起始组件ID
    start_port: int      # 起始端口索引
    end_component: str   # 结束组件ID
    end_port: int       # 结束端口索引
```

## 🔧 工具函数API

### FileManager (文件管理器)

#### 静态方法
```python
@staticmethod
def save_project(file_path: str, workflow_data: Dict[str, Any]) -> bool:
    """保存项目文件

    Args:
        file_path: 文件路径
        workflow_data: 工作流程数据

    Returns:
        保存是否成功
    """

@staticmethod
def load_project(file_path: str) -> Optional[Dict[str, Any]]:
    """加载项目文件

    Args:
        file_path: 文件路径

    Returns:
        工作流程数据，失败时返回None
    """

@staticmethod
def get_recent_files(max_count: int = 10) -> List[str]:
    """获取最近打开的文件列表

    Args:
        max_count: 最大文件数量

    Returns:
        最近文件路径列表
    """

@staticmethod
def add_recent_file(file_path: str) -> None:
    """添加到最近文件列表

    Args:
        file_path: 文件路径
    """
```

### ComponentValidator (组件验证器)

#### 静态方法
```python
@staticmethod
def validate_data_component(properties: Dict[str, Any]) -> List[str]:
    """验证数据组件

    Args:
        properties: 组件属性字典

    Returns:
        错误信息列表
    """

@staticmethod
def validate_model_component(properties: Dict[str, Any]) -> List[str]:
    """验证模型组件

    Args:
        properties: 组件属性字典

    Returns:
        错误信息列表
    """

@staticmethod
def validate_component(component_type: str, properties: Dict[str, Any]) -> List[str]:
    """验证组件

    Args:
        component_type: 组件类型
        properties: 组件属性字典

    Returns:
        错误信息列表
    """
```

## 🚀 后端接口API

### ExecutionEngine (执行引擎)

#### 类定义
```python
class ExecutionEngine:
    """执行引擎，负责工作流程的执行"""
```

#### 主要方法
```python
def execute_workflow(self, workflow_manager: WorkflowManager) -> bool:
    """执行工作流程

    Args:
        workflow_manager: 工作流程管理器

    Returns:
        执行是否成功
    """

def stop_execution(self) -> None:
    """停止执行"""

def get_progress(self) -> tuple:
    """获取执行进度

    Returns:
        (当前步骤, 总步骤数)
    """
```

#### 组件执行方法
```python
def _execute_component(self, component: ComponentConfig) -> bool:
    """执行单个组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """

def _execute_data_component(self, component: ComponentConfig) -> bool:
    """执行数据组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """

def _execute_preprocess_component(self, component: ComponentConfig) -> bool:
    """执行预处理组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """

def _execute_model_component(self, component: ComponentConfig) -> bool:
    """执行模型组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """

def _execute_evaluate_component(self, component: ComponentConfig) -> bool:
    """执行评估组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """

def _execute_output_component(self, component: ComponentConfig) -> bool:
    """执行输出组件

    Args:
        component: 组件配置

    Returns:
        执行是否成功
    """
```

#### 属性
```python
is_running: bool        # 是否正在执行
current_step: int      # 当前执行步骤
total_steps: int       # 总步骤数
```

## 📊 组件库API

### ComponentLibrary (组件库)

#### 类定义
```python
class ComponentLibrary(QWidget):
    """组件库面板，管理所有可用的ML组件"""
```

#### 主要方法
```python
def get_component_info(self, component_name: str) -> Dict[str, Any]:
    """获取组件信息

    Args:
        component_name: 组件名称

    Returns:
        组件信息字典，包含name、type、description
    """

def add_custom_component(self, category: str, name: str, component_type: str, description: str = "") -> None:
    """添加自定义组件

    Args:
        category: 组件分类
        name: 组件名称
        component_type: 组件类型
        description: 组件描述
    """

def create_draggable_item(self, name: str) -> QTreeWidgetItem:
    """创建可拖拽的组件项

    Args:
        name: 组件名称

    Returns:
        树形控件项
    """
```

#### 组件类型映射
```python
component_types: Dict[str, str]  # 组件名称到类型的映射
```

### PropertyPanel (属性面板)

#### 类定义
```python
class PropertyPanel(QWidget):
    """属性配置面板，动态显示和配置组件属性"""

    # 信号定义
    property_changed = pyqtSignal(object, str, object)
```

#### 主要方法
```python
def show_component_properties(self, component: MLComponent) -> None:
    """显示组件属性

    Args:
        component: 要显示属性的组件
    """

def show_empty_state(self) -> None:
    """显示空状态（无组件选择）"""

def clear_properties(self) -> None:
    """清空属性面板"""

def add_property_group(self, title: str, properties: List[Tuple[str, str, Any]]) -> None:
    """添加属性组

    Args:
        title: 属性组标题
        properties: 属性列表，每个属性为(名称, 类型, 默认值)的元组
    """

def get_component_properties(self) -> Dict[str, Any]:
    """获取当前组件的所有属性值

    Returns:
        属性字典
    """

def set_component_properties(self, properties: Dict[str, Any]) -> None:
    """设置组件属性值

    Args:
        properties: 属性字典
    """
```

#### 属性控件类型
```python
支持的控件类型:
- "LineEdit"      # 文本输入框
- "ComboBox"      # 下拉选择框
- "SpinBox"       # 整数输入框
- "DoubleSpinBox" # 浮点数输入框
- "CheckBox"      # 复选框
```

## 🔍 使用示例

### 创建和配置组件
```python
# 创建画布
canvas = MLCanvas()

# 添加组件
data_loader = canvas.add_component('data', '数据加载', QPointF(100, 100))
model = canvas.add_component('model', '随机森林', QPointF(300, 100))

# 获取组件属性
properties = data_loader.get_properties()

# 设置组件属性
data_loader.set_properties({
    'file_path': 'data.csv',
    'separator': ',',
    'encoding': 'utf-8'
})
```

### 创建连接
```python
# 获取端口
output_port = data_loader.output_ports[0]
input_port = model.input_ports[0]

# 创建连接
connection = ConnectionLine(output_port, input_port)
canvas.scene.addItem(connection)

# 添加到端口连接列表
output_port.connections.append(connection)
input_port.connections.append(connection)
```

### 工作流程管理
```python
# 创建工作流程管理器
wm = WorkflowManager()

# 添加组件配置
comp_config = ComponentConfig(
    component_id="data_loader_1",
    component_type="data",
    name="数据加载",
    position=(100, 100),
    properties={'file_path': 'data.csv'}
)
wm.add_component(comp_config)

# 验证工作流程
errors = wm.validate_workflow()
if not errors:
    print("工作流程验证通过")

# 获取执行顺序
execution_order = wm.get_execution_order()
print(f"执行顺序: {execution_order}")
```

### 执行工作流程
```python
# 创建执行引擎
engine = ExecutionEngine()

# 执行工作流程
success = engine.execute_workflow(wm)
if success:
    print("工作流程执行成功")
else:
    print("工作流程执行失败")
```

## 📝 注意事项

### 线程安全
- GUI操作必须在主线程中进行
- 长时间运行的任务应使用QThread
- 使用信号槽进行线程间通信

### 内存管理
- 及时清理不再使用的组件和连接
- 避免循环引用
- 大数据处理时注意内存使用

### 错误处理
- 所有公共方法都应包含适当的错误处理
- 使用异常处理机制
- 提供有意义的错误信息

### 性能考虑
- 大量组件时考虑视口裁剪
- 使用缓存减少重复计算
- 避免频繁的界面更新

---

这份API文档提供了所有主要类和方法的详细说明，可以作为开发时的参考手册。
