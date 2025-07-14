#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VML 后端实现接口定义

这个文件定义了VML前端与后端之间的标准接口。
后端开发者需要实现这些接口来提供机器学习功能。

接口设计原则：
1. 异步执行 - 所有长时间运行的操作都是异步的
2. 状态反馈 - 提供详细的执行状态和进度信息
3. 错误处理 - 统一的错误码和错误信息格式
4. 数据标准化 - 标准化的数据格式和结构
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import uuid


class BackendInterface(ABC):
    """
    VML后端接口基类
    
    所有后端实现都必须继承这个类并实现所有抽象方法。
    """
    
    @abstractmethod
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行机器学习工作流程
        
        Args:
            workflow_data: 工作流程配置数据
            {
                'components': [
                    {
                        'id': 'component_uuid',
                        'type': 'data|preprocess|model|evaluate|output',
                        'name': '组件名称',
                        'position': (x, y),
                        'properties': {
                            # 组件特定的配置参数
                        }
                    }
                ],
                'connections': [
                    {
                        'start_component': 'start_component_id',
                        'start_port': 0,
                        'end_component': 'end_component_id', 
                        'end_port': 0
                    }
                ]
            }
            
        Returns:
            {
                'success': bool,
                'execution_id': str,  # 执行ID，用于后续状态查询
                'message': str,       # 成功或失败消息
                'error_details': str  # 错误详情（如果失败）
            }
        """
        pass
    
    @abstractmethod
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            {
                'success': bool,
                'status': 'running|completed|failed|stopped',
                'progress': float,        # 0.0-1.0
                'current_step': str,      # 当前执行步骤描述
                'estimated_time': int,    # 预计剩余时间（秒）
                'results': dict,          # 执行结果（如果完成）
                'error_message': str      # 错误信息（如果失败）
            }
        """
        pass
    
    @abstractmethod
    def stop_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        停止执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            {
                'success': bool,
                'message': str
            }
        """
        pass
    
    @abstractmethod
    def get_data_preview(self, data_id: str, rows: int = 10) -> Dict[str, Any]:
        """
        获取数据预览
        
        Args:
            data_id: 数据ID
            rows: 预览行数
            
        Returns:
            {
                'success': bool,
                'data': {
                    'columns': ['col1', 'col2', ...],
                    'rows': [
                        ['val1', 'val2', ...],
                        ...
                    ],
                    'total_rows': int,
                    'total_columns': int
                },
                'message': str,
                'error_details': str
            }
        """
        pass
    
    @abstractmethod
    def get_data_statistics(self, data_id: str) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Args:
            data_id: 数据ID
            
        Returns:
            {
                'success': bool,
                'statistics': {
                    'numeric_columns': {
                        'column_name': {
                            'count': int,
                            'mean': float,
                            'std': float,
                            'min': float,
                            'max': float,
                            'quartiles': [q1, q2, q3]
                        }
                    },
                    'categorical_columns': {
                        'column_name': {
                            'count': int,
                            'unique': int,
                            'top': str,
                            'freq': int,
                            'value_counts': {'value': count, ...}
                        }
                    },
                    'missing_values': {'column_name': count, ...},
                    'data_types': {'column_name': 'type', ...}
                },
                'message': str,
                'error_details': str
            }
        """
        pass
    
    @abstractmethod
    def generate_plot(self, chart_type: str, data_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成图表
        
        Args:
            chart_type: 图表类型 ('histogram', 'scatter', 'line', 'bar', 'box', 'heatmap', etc.)
            data_id: 数据ID
            config: 图表配置
            {
                'x_column': str,      # X轴列名
                'y_column': str,      # Y轴列名（可选）
                'color_column': str,  # 颜色分组列名（可选）
                'title': str,         # 图表标题
                'width': int,         # 图表宽度
                'height': int,        # 图表高度
                'style': str,         # 图表样式
                # 其他图表特定配置
            }
            
        Returns:
            {
                'success': bool,
                'chart_data': {
                    'type': str,          # 图表类型
                    'image_path': str,    # 图表图片路径（可选）
                    'image_base64': str,  # 图表图片base64编码（可选）
                    'html': str,          # 交互式图表HTML（可选）
                    'data': dict,         # 图表数据（用于前端渲染）
                    'config': dict        # 图表配置
                },
                'message': str,
                'error_details': str
            }
        """
        pass
    
    @abstractmethod
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工作流程配置
        
        Args:
            workflow_data: 工作流程配置数据
            
        Returns:
            {
                'success': bool,
                'valid': bool,
                'errors': [
                    {
                        'component_id': str,
                        'error_type': str,
                        'message': str
                    }
                ],
                'warnings': [
                    {
                        'component_id': str,
                        'warning_type': str,
                        'message': str
                    }
                ]
            }
        """
        pass
    
    @abstractmethod
    def get_component_info(self, component_type: str) -> Dict[str, Any]:
        """
        获取组件信息
        
        Args:
            component_type: 组件类型
            
        Returns:
            {
                'success': bool,
                'info': {
                    'name': str,
                    'description': str,
                    'category': str,
                    'input_ports': [
                        {
                            'name': str,
                            'type': str,
                            'required': bool,
                            'description': str
                        }
                    ],
                    'output_ports': [
                        {
                            'name': str,
                            'type': str,
                            'description': str
                        }
                    ],
                    'parameters': [
                        {
                            'name': str,
                            'type': str,
                            'default': Any,
                            'required': bool,
                            'description': str,
                            'options': List[Any]  # 可选值列表（如果适用）
                        }
                    ]
                },
                'message': str,
                'error_details': str
            }
        """
        pass
    
    @abstractmethod
    def get_supported_components(self) -> Dict[str, Any]:
        """
        获取支持的组件列表
        
        Returns:
            {
                'success': bool,
                'components': {
                    'data': ['data_loader', 'data_cleaner', ...],
                    'preprocess': ['scaler', 'encoder', ...],
                    'model': ['linear_regression', 'random_forest', ...],
                    'evaluate': ['accuracy', 'confusion_matrix', ...],
                    'output': ['save_model', 'export_results', ...]
                },
                'message': str
            }
        """
        pass


# 错误码定义
class ErrorCodes:
    """标准错误码定义"""
    
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    
    # 工作流程错误
    WORKFLOW_VALIDATION_ERROR = "WORKFLOW_VALIDATION_ERROR"
    COMPONENT_NOT_FOUND = "COMPONENT_NOT_FOUND"
    INVALID_CONNECTION = "INVALID_CONNECTION"
    CIRCULAR_DEPENDENCY = "CIRCULAR_DEPENDENCY"
    
    # 执行错误
    EXECUTION_ERROR = "EXECUTION_ERROR"
    EXECUTION_NOT_FOUND = "EXECUTION_NOT_FOUND"
    EXECUTION_ALREADY_STOPPED = "EXECUTION_ALREADY_STOPPED"
    
    # 数据错误
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    DATA_FORMAT_ERROR = "DATA_FORMAT_ERROR"
    DATA_ACCESS_ERROR = "DATA_ACCESS_ERROR"
    
    # 模型错误
    MODEL_TRAINING_ERROR = "MODEL_TRAINING_ERROR"
    MODEL_PREDICTION_ERROR = "MODEL_PREDICTION_ERROR"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    
    # 图表错误
    CHART_GENERATION_ERROR = "CHART_GENERATION_ERROR"
    UNSUPPORTED_CHART_TYPE = "UNSUPPORTED_CHART_TYPE"


# 数据类型定义
class DataTypes:
    """数据类型定义"""
    
    DATAFRAME = "dataframe"      # pandas DataFrame
    ARRAY = "array"              # numpy array
    MODEL = "model"              # 训练好的模型
    METRICS = "metrics"          # 评估指标
    PLOT = "plot"                # 图表
    TEXT = "text"                # 文本数据
    IMAGE = "image"              # 图像数据
    ANY = "any"                  # 任意类型


# 组件类型定义
class ComponentTypes:
    """组件类型定义"""
    
    DATA = "data"                # 数据处理组件
    PREPROCESS = "preprocess"    # 预处理组件
    MODEL = "model"              # 模型组件
    EVALUATE = "evaluate"        # 评估组件
    OUTPUT = "output"            # 输出组件


# 示例实现（仅用于参考）
class ExampleBackend(BackendInterface):
    """
    示例后端实现
    
    这是一个简单的示例实现，展示了如何实现后端接口。
    实际的后端实现应该根据具体需求来实现这些方法。
    """
    
    def __init__(self):
        self.executions = {}
    
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        execution_id = str(uuid.uuid4())
        # 这里应该实现实际的工作流程执行逻辑
        return {
            'success': True,
            'execution_id': execution_id,
            'message': '工作流程开始执行'
        }
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        # 这里应该实现实际的状态查询逻辑
        return {
            'success': True,
            'status': 'running',
            'progress': 0.5,
            'current_step': '正在训练模型...',
            'estimated_time': 120
        }
    
    def stop_execution(self, execution_id: str) -> Dict[str, Any]:
        # 这里应该实现实际的停止逻辑
        return {
            'success': True,
            'message': '执行已停止'
        }
    
    def get_data_preview(self, data_id: str, rows: int = 10) -> Dict[str, Any]:
        # 这里应该实现实际的数据预览逻辑
        return {
            'success': True,
            'data': {
                'columns': ['feature1', 'feature2', 'target'],
                'rows': [
                    [1.0, 2.0, 'A'],
                    [1.5, 2.5, 'B']
                ],
                'total_rows': 1000,
                'total_columns': 3
            },
            'message': '数据预览获取成功'
        }
    
    def get_data_statistics(self, data_id: str) -> Dict[str, Any]:
        # 这里应该实现实际的统计信息计算逻辑
        return {
            'success': True,
            'statistics': {
                'numeric_columns': {
                    'feature1': {
                        'count': 1000,
                        'mean': 1.25,
                        'std': 0.5,
                        'min': 0.0,
                        'max': 2.0,
                        'quartiles': [1.0, 1.25, 1.5]
                    }
                },
                'categorical_columns': {
                    'target': {
                        'count': 1000,
                        'unique': 2,
                        'top': 'A',
                        'freq': 600,
                        'value_counts': {'A': 600, 'B': 400}
                    }
                },
                'missing_values': {},
                'data_types': {'feature1': 'float64', 'feature2': 'float64', 'target': 'object'}
            },
            'message': '统计信息获取成功'
        }
    
    def generate_plot(self, chart_type: str, data_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        # 这里应该实现实际的图表生成逻辑
        return {
            'success': True,
            'chart_data': {
                'type': chart_type,
                'image_base64': 'base64_encoded_image_data',
                'data': {'x': [1, 2, 3], 'y': [1, 4, 9]},
                'config': config
            },
            'message': '图表生成成功'
        }
    
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        # 这里应该实现实际的工作流程验证逻辑
        return {
            'success': True,
            'valid': True,
            'errors': [],
            'warnings': []
        }
    
    def get_component_info(self, component_type: str) -> Dict[str, Any]:
        # 这里应该实现实际的组件信息查询逻辑
        return {
            'success': True,
            'info': {
                'name': '线性回归',
                'description': '线性回归模型',
                'category': 'model',
                'input_ports': [
                    {
                        'name': 'training_data',
                        'type': 'dataframe',
                        'required': True,
                        'description': '训练数据'
                    }
                ],
                'output_ports': [
                    {
                        'name': 'model',
                        'type': 'model',
                        'description': '训练好的模型'
                    }
                ],
                'parameters': [
                    {
                        'name': 'fit_intercept',
                        'type': 'bool',
                        'default': True,
                        'required': False,
                        'description': '是否拟合截距',
                        'options': [True, False]
                    }
                ]
            },
            'message': '组件信息获取成功'
        }
    
    def get_supported_components(self) -> Dict[str, Any]:
        # 这里应该实现实际的支持组件查询逻辑
        return {
            'success': True,
            'components': {
                'data': ['csv_loader', 'excel_loader'],
                'preprocess': ['standard_scaler', 'min_max_scaler'],
                'model': ['linear_regression', 'random_forest'],
                'evaluate': ['accuracy_score', 'confusion_matrix'],
                'output': ['save_model', 'export_csv']
            },
            'message': '支持的组件列表获取成功'
        }
