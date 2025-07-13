#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端接口实现示例
展示如何实现机器学习后端接口
"""

import pandas as pd
import numpy as np
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io


class MLBackend:
    """机器学习后端实现"""
    
    def __init__(self):
        self.data_cache = {}
        self.model_cache = {}
        self.execution_status = {}
        
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流程
        
        Args:
            workflow_data: 工作流程配置数据
            
        Returns:
            执行结果
        """
        try:
            execution_id = str(uuid.uuid4())
            
            # 初始化执行状态
            self.execution_status[execution_id] = {
                'status': 'running',
                'progress': 0.0,
                'current_step': '',
                'results': {},
                'start_time': time.time()
            }
            
            # 解析工作流程
            components = workflow_data.get('components', [])
            connections = workflow_data.get('connections', [])
            
            # 构建执行图
            execution_order = self._get_execution_order(components, connections)
            
            # 执行组件
            for i, component_id in enumerate(execution_order):
                component = next(c for c in components if c['id'] == component_id)
                
                # 更新状态
                self.execution_status[execution_id]['progress'] = i / len(execution_order)
                self.execution_status[execution_id]['current_step'] = component['name']
                
                # 执行组件
                result = self._execute_component(component, execution_id)
                self.execution_status[execution_id]['results'][component_id] = result
                
                if not result.get('success', False):
                    self.execution_status[execution_id]['status'] = 'failed'
                    return {
                        'success': False,
                        'execution_id': execution_id,
                        'message': f"组件 {component['name']} 执行失败",
                        'error_details': result.get('error', '')
                    }
            
            # 执行完成
            self.execution_status[execution_id]['status'] = 'completed'
            self.execution_status[execution_id]['progress'] = 1.0
            
            return {
                'success': True,
                'execution_id': execution_id,
                'message': '工作流程执行完成',
                'results': self.execution_status[execution_id]['results']
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'工作流程执行失败: {str(e)}',
                'error_details': str(e)
            }
    
    def _get_execution_order(self, components: List[Dict], connections: List[Dict]) -> List[str]:
        """获取组件执行顺序（拓扑排序）"""
        # 构建依赖图
        dependencies = {comp['id']: set() for comp in components}
        
        for conn in connections:
            dependencies[conn['end_component']].add(conn['start_component'])
        
        # 拓扑排序
        result = []
        visited = set()
        temp_visited = set()
        
        def dfs(node):
            if node in temp_visited:
                raise ValueError("检测到循环依赖")
            if node in visited:
                return
                
            temp_visited.add(node)
            for dep in dependencies[node]:
                dfs(dep)
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
            
        for comp in components:
            if comp['id'] not in visited:
                dfs(comp['id'])
                
        return result
    
    def _execute_component(self, component: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """执行单个组件"""
        component_type = component['type']
        component_name = component['name']
        properties = component.get('properties', {})
        
        try:
            if component_type == 'data':
                return self._execute_data_component(component, properties)
            elif component_type == 'preprocess':
                return self._execute_preprocess_component(component, properties, execution_id)
            elif component_type == 'model':
                return self._execute_model_component(component, properties, execution_id)
            elif component_type == 'evaluate':
                return self._execute_evaluate_component(component, properties, execution_id)
            elif component_type == 'output':
                return self._execute_output_component(component, properties, execution_id)
            else:
                return {
                    'success': False,
                    'error': f'未知组件类型: {component_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'组件执行失败: {str(e)}'
            }
    
    def _execute_data_component(self, component: Dict, properties: Dict) -> Dict[str, Any]:
        """执行数据组件"""
        if '加载' in component['name']:
            return self.execute_data_loader(properties)
        elif '清洗' in component['name']:
            # 需要输入数据，这里简化处理
            return {'success': True, 'message': '数据清洗完成'}
        else:
            return {'success': True, 'message': '数据处理完成'}
    
    def execute_data_loader(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据加载组件"""
        try:
            file_path = config.get('file_path', 'data.csv')
            separator = config.get('separator', ',')
            encoding = config.get('encoding', 'utf-8')
            
            # 如果文件不存在，创建示例数据
            if not os.path.exists(file_path):
                data = self._create_sample_data()
            else:
                data = pd.read_csv(file_path, sep=separator, encoding=encoding)
            
            # 缓存数据
            data_id = str(uuid.uuid4())
            self.data_cache[data_id] = data
            
            return {
                'success': True,
                'data_id': data_id,
                'shape': list(data.shape),
                'columns': list(data.columns),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024:.1f} KB",
                'message': f'成功加载数据: {data.shape[0]} 行 × {data.shape[1]} 列'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'数据加载失败: {str(e)}'
            }
    
    def _create_sample_data(self) -> pd.DataFrame:
        """创建示例数据"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'income': np.random.normal(50000, 15000, n_samples),
            'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
            'experience': np.random.randint(0, 40, n_samples),
            'target': np.random.choice([0, 1], n_samples)
        }
        
        return pd.DataFrame(data)
    
    def get_data_preview(self, data_id: str, rows: int = 10) -> Dict[str, Any]:
        """获取数据预览"""
        try:
            if data_id not in self.data_cache:
                return {
                    'success': False,
                    'error': '数据不存在'
                }
            
            data = self.data_cache[data_id]
            preview_data = data.head(rows).values.tolist()
            
            return {
                'success': True,
                'preview_data': preview_data,
                'columns': list(data.columns),
                'shape': list(data.shape),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024:.1f} KB"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取数据预览失败: {str(e)}'
            }
    
    def get_data_statistics(self, data_id: str) -> Dict[str, Any]:
        """获取数据统计信息"""
        try:
            if data_id not in self.data_cache:
                return {
                    'success': False,
                    'error': '数据不存在'
                }
            
            data = self.data_cache[data_id]
            
            # 基本信息
            basic_info = {
                'shape': list(data.shape),
                'n_columns': len(data.columns),
                'n_numeric': len(data.select_dtypes(include=[np.number]).columns),
                'n_categorical': len(data.select_dtypes(include=['object']).columns),
                'total_missing': data.isnull().sum().sum(),
                'duplicates': data.duplicated().sum()
            }
            
            # 数值型变量统计
            numeric_stats = {}
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                stats = data[col].describe()
                numeric_stats[col] = {
                    'mean': stats['mean'],
                    'std': stats['std'],
                    'min': stats['min'],
                    '25%': stats['25%'],
                    '50%': stats['50%'],
                    '75%': stats['75%'],
                    'max': stats['max'],
                    'missing': data[col].isnull().sum()
                }
            
            # 分类型变量统计
            categorical_stats = {}
            categorical_cols = data.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                value_counts = data[col].value_counts()
                categorical_stats[col] = {
                    'unique': data[col].nunique(),
                    'top': value_counts.index[0] if len(value_counts) > 0 else None,
                    'freq': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    'missing': data[col].isnull().sum()
                }
            
            return {
                'success': True,
                **basic_info,
                'numeric_stats': numeric_stats,
                'categorical_stats': categorical_stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取统计信息失败: {str(e)}'
            }
    
    def generate_plot(self, plot_type: str, data_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成图表"""
        try:
            if data_id not in self.data_cache:
                return {
                    'success': False,
                    'error': '数据不存在'
                }
            
            data = self.data_cache[data_id]
            variable = config.get('variable')
            
            plt.figure(figsize=(10, 6))
            
            if plot_type == '直方图' and variable:
                plt.hist(data[variable], bins=30, alpha=0.7)
                plt.title(f'{variable} 分布直方图')
                plt.xlabel(variable)
                plt.ylabel('频次')
            elif plot_type == '散点图':
                x_var = config.get('x_variable')
                y_var = config.get('y_variable')
                if x_var and y_var:
                    plt.scatter(data[x_var], data[y_var], alpha=0.6)
                    plt.xlabel(x_var)
                    plt.ylabel(y_var)
                    plt.title(f'{x_var} vs {y_var}')
            elif plot_type == '相关性热图':
                numeric_data = data.select_dtypes(include=[np.number])
                correlation = numeric_data.corr()
                sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
                plt.title('特征相关性热图')
            else:
                plt.text(0.5, 0.5, f'暂不支持 {plot_type}', 
                        ha='center', va='center', transform=plt.gca().transAxes)
                plt.title('图表类型不支持')
            
            # 保存图片为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'success': True,
                'image_base64': image_base64,
                'plot_type': plot_type,
                'config': config
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'图表生成失败: {str(e)}'
            }
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """获取执行状态"""
        if execution_id not in self.execution_status:
            return {
                'success': False,
                'error': '执行ID不存在'
            }
        
        status = self.execution_status[execution_id]
        return {
            'success': True,
            'status': status['status'],
            'progress': status['progress'],
            'current_step': status['current_step'],
            'results': status['results']
        }
    
    def stop_execution(self, execution_id: str) -> Dict[str, Any]:
        """停止执行"""
        if execution_id in self.execution_status:
            self.execution_status[execution_id]['status'] = 'stopped'
            return {
                'success': True,
                'message': '执行已停止'
            }
        else:
            return {
                'success': False,
                'error': '执行ID不存在'
            }


# 使用示例
if __name__ == '__main__':
    # 创建后端实例
    backend = MLBackend()
    
    # 示例工作流程
    workflow = {
        'components': [
            {
                'id': 'data_loader_1',
                'type': 'data',
                'name': '数据加载',
                'properties': {
                    'file_path': 'sample_data.csv',
                    'separator': ',',
                    'encoding': 'utf-8'
                }
            }
        ],
        'connections': []
    }
    
    # 执行工作流程
    result = backend.execute_workflow(workflow)
    print("执行结果:", result)
    
    if result['success']:
        execution_id = result['execution_id']
        
        # 获取执行状态
        status = backend.get_execution_status(execution_id)
        print("执行状态:", status)
        
        # 获取数据预览
        if 'data_loader_1' in status['results']:
            data_result = status['results']['data_loader_1']
            if 'data_id' in data_result:
                preview = backend.get_data_preview(data_result['data_id'])
                print("数据预览:", preview)
