#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端接口适配器
连接前端UI和后端ML执行引擎
"""

import json
import uuid
import os
import sys
import importlib.util
from typing import Dict, Any, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer


class BackendAdapter(QObject):
    """后端接口适配器"""
    
    # 信号定义
    execution_started = pyqtSignal(str)  # execution_id
    execution_progress = pyqtSignal(str, float, str)  # execution_id, progress, current_step
    execution_completed = pyqtSignal(str, bool, dict)  # execution_id, success, results
    component_completed = pyqtSignal(str, str, bool, dict)  # execution_id, component_id, success, result
    
    data_preview_ready = pyqtSignal(str, dict)  # data_id, preview_data
    statistics_ready = pyqtSignal(str, dict)  # data_id, statistics
    chart_ready = pyqtSignal(str, dict)  # chart_id, chart_data
    
    error_occurred = pyqtSignal(str, str, str)  # error_code, error_message, details
    
    def __init__(self):
        super().__init__()
        self.backend_implementation = None
        self.current_executions = {}
        self.data_cache = {}

        # 尝试加载后端实现
        self._load_backend_implementation()

    def set_backend_implementation(self, backend_impl):
        """设置后端实现"""
        self.backend_implementation = backend_impl

    def _load_backend_implementation(self):
        """加载后端实现"""
        try:
            # 尝试从backend_implementation.py加载
            import importlib.util
            backend_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend_implementation.py')

            if os.path.exists(backend_file):
                spec = importlib.util.spec_from_file_location("backend_implementation", backend_file)
                backend_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(backend_module)

                # 查找BackendImplementation类
                if hasattr(backend_module, 'BackendImplementation'):
                    self.backend_implementation = backend_module.BackendImplementation()
                    print("✅ 后端实现加载成功")
                else:
                    print("⚠️ 后端文件中未找到BackendImplementation类")
            else:
                print("ℹ️ 未找到backend_implementation.py，使用模拟后端")

        except Exception as e:
            print(f"⚠️ 加载后端实现失败: {e}")
            print("ℹ️ 将使用模拟后端进行开发和测试")
        
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """
        执行工作流程
        
        Args:
            workflow_data: 工作流程配置数据
            
        Returns:
            execution_id: 执行ID
        """
        execution_id = str(uuid.uuid4())

        if not self.backend_implementation:
            # 使用模拟后端
            self._simulate_execution(execution_id, workflow_data)
        else:
            # 调用实际后端实现
            try:
                result = self.backend_implementation.execute_workflow(workflow_data)
                if result.get('success'):
                    backend_execution_id = result.get('execution_id', execution_id)
                    self.current_executions[execution_id] = backend_execution_id
                    self.execution_started.emit(execution_id)
                    self._monitor_execution(execution_id, backend_execution_id)
                else:
                    self.error_occurred.emit(
                        "EXECUTION_ERROR",
                        result.get('message', '执行失败'),
                        result.get('error_details', '')
                    )
            except Exception as e:
                self.error_occurred.emit(
                    "BACKEND_ERROR",
                    f"后端调用失败: {str(e)}",
                    str(e)
                )
                
        return execution_id
        
    def stop_execution(self, execution_id: str):
        """停止执行"""
        if execution_id in self.current_executions:
            if self.backend_implementation:
                try:
                    backend_execution_id = self.current_executions[execution_id]
                    result = self.backend_implementation.stop_execution(backend_execution_id)
                    if not result.get('success'):
                        self.error_occurred.emit("STOP_ERROR", result.get('message', '停止失败'), "")
                except Exception as e:
                    self.error_occurred.emit(
                        "BACKEND_ERROR",
                        f"停止执行失败: {str(e)}",
                        str(e)
                    )

            del self.current_executions[execution_id]
            
    def get_data_preview(self, data_id: str, rows: int = 10):
        """获取数据预览"""
        if not self.backend_implementation:
            # 模拟数据预览
            self._simulate_data_preview(data_id, rows)
        else:
            try:
                result = self.backend_implementation.get_data_preview(data_id, rows)
                if result.get('success'):
                    self.data_preview_ready.emit(data_id, result)
                else:
                    self.error_occurred.emit(
                        "DATA_PREVIEW_ERROR",
                        result.get('message', '数据预览失败'),
                        result.get('error_details', '')
                    )
            except Exception as e:
                self.error_occurred.emit(
                    "BACKEND_ERROR",
                    f"获取数据预览失败: {str(e)}",
                    str(e)
                )
                
    def get_data_statistics(self, data_id: str):
        """获取数据统计信息"""
        if not self.backend_module:
            # 模拟统计信息
            self._simulate_statistics(data_id)
        else:
            try:
                result = self.backend_module.get_data_statistics(data_id)
                if result.get('success'):
                    self.statistics_ready.emit(data_id, result)
                else:
                    self.error_occurred.emit(
                        "STATISTICS_ERROR",
                        result.get('message', '统计信息获取失败'),
                        result.get('error_details', '')
                    )
            except Exception as e:
                self.error_occurred.emit(
                    "BACKEND_ERROR",
                    f"获取统计信息失败: {str(e)}",
                    str(e)
                )
                
    def generate_chart(self, chart_type: str, data_id: str, config: Dict[str, Any]):
        """生成图表"""
        chart_id = str(uuid.uuid4())
        
        if not self.backend_module:
            # 模拟图表生成
            self._simulate_chart_generation(chart_id, chart_type, data_id, config)
        else:
            try:
                result = self.backend_module.generate_plot(chart_type, data_id, config)
                if result.get('success'):
                    self.chart_ready.emit(chart_id, result)
                else:
                    self.error_occurred.emit(
                        "CHART_ERROR",
                        result.get('message', '图表生成失败'),
                        result.get('error_details', '')
                    )
            except Exception as e:
                self.error_occurred.emit(
                    "BACKEND_ERROR",
                    f"图表生成失败: {str(e)}",
                    str(e)
                )
                
        return chart_id
        
    def _simulate_execution(self, execution_id: str, workflow_data: Dict[str, Any]):
        """模拟工作流程执行"""
        self.execution_started.emit(execution_id)
        
        components = workflow_data.get('components', [])
        total_components = len(components)
        
        # 使用定时器模拟执行过程
        self.simulation_timer = QTimer()
        self.simulation_step = 0
        self.simulation_execution_id = execution_id
        self.simulation_components = components
        
        def simulate_step():
            if self.simulation_step < total_components:
                component = self.simulation_components[self.simulation_step]
                progress = (self.simulation_step + 1) / total_components
                
                # 发射进度信号
                self.execution_progress.emit(
                    execution_id, 
                    progress, 
                    f"正在执行: {component['name']}"
                )
                
                # 模拟组件执行结果
                component_result = {
                    'success': True,
                    'name': component['name'],
                    'execution_time': 1.5,
                    'summary': f"{component['name']} 执行完成",
                    'output_shape': [100, 5] if component['type'] == 'data' else None
                }
                
                self.component_completed.emit(
                    execution_id,
                    str(component.get('id', f'component_{self.simulation_step}')),
                    True,
                    component_result
                )
                
                self.simulation_step += 1
            else:
                # 执行完成
                self.simulation_timer.stop()
                
                # 模拟最终结果
                results = {}
                for comp in self.simulation_components:
                    results[comp['id']] = {
                        'success': True,
                        'name': comp['name'],
                        'execution_time': 1.5,
                        'summary': f"{comp['name']} 执行完成"
                    }
                
                self.execution_completed.emit(execution_id, True, results)
                
        self.simulation_timer.timeout.connect(simulate_step)
        self.simulation_timer.start(2000)  # 每2秒执行一个组件
        
    def _simulate_data_preview(self, data_id: str, rows: int):
        """模拟数据预览"""
        # 模拟数据
        preview_data = {
            'success': True,
            'preview_data': [
                ['Alice', 25, 'Engineer', 75000],
                ['Bob', 30, 'Manager', 85000],
                ['Charlie', 35, 'Director', 95000],
                ['Diana', 28, 'Analyst', 65000],
                ['Eve', 32, 'Designer', 70000]
            ][:rows],
            'columns': ['Name', 'Age', 'Position', 'Salary'],
            'shape': [1000, 4],
            'dtypes': {
                'Name': 'object',
                'Age': 'int64',
                'Position': 'object', 
                'Salary': 'int64'
            },
            'memory_usage': '32.5 KB'
        }
        
        # 延迟发射信号模拟网络请求
        QTimer.singleShot(500, lambda: self.data_preview_ready.emit(data_id, preview_data))
        
    def _simulate_statistics(self, data_id: str):
        """模拟统计信息"""
        stats_data = {
            'success': True,
            'shape': [1000, 4],
            'n_columns': 4,
            'n_numeric': 2,
            'n_categorical': 2,
            'total_missing': 15,
            'duplicates': 3,
            'numeric_stats': {
                'Age': {
                    'mean': 30.5,
                    'std': 5.2,
                    'min': 22,
                    '25%': 27,
                    '50%': 30,
                    '75%': 34,
                    'max': 45,
                    'missing': 2
                },
                'Salary': {
                    'mean': 75000,
                    'std': 12000,
                    'min': 45000,
                    '25%': 65000,
                    '50%': 75000,
                    '75%': 85000,
                    'max': 120000,
                    'missing': 5
                }
            },
            'categorical_stats': {
                'Position': {
                    'unique': 5,
                    'top': 'Engineer',
                    'freq': 350,
                    'missing': 3
                },
                'Name': {
                    'unique': 995,
                    'top': 'John',
                    'freq': 2,
                    'missing': 5
                }
            }
        }
        
        QTimer.singleShot(800, lambda: self.statistics_ready.emit(data_id, stats_data))
        
    def _simulate_chart_generation(self, chart_id: str, chart_type: str, data_id: str, config: Dict[str, Any]):
        """模拟图表生成"""
        chart_data = {
            'success': True,
            'chart_type': chart_type,
            'image_base64': '',  # 这里应该是实际的base64图片数据
            'chart_config': config
        }
        
        QTimer.singleShot(1200, lambda: self.chart_ready.emit(chart_id, chart_data))
        
    def _monitor_execution(self, execution_id: str):
        """监控执行状态"""
        if not self.backend_module:
            return
            
        def check_status():
            try:
                backend_execution_id = self.current_executions.get(execution_id)
                if not backend_execution_id:
                    return
                    
                status = self.backend_module.get_execution_status(backend_execution_id)
                
                if status.get('status') == 'running':
                    self.execution_progress.emit(
                        execution_id,
                        status.get('progress', 0),
                        status.get('current_step', '')
                    )
                elif status.get('status') in ['completed', 'failed']:
                    # 执行完成
                    success = status.get('status') == 'completed'
                    results = status.get('results', {})
                    
                    self.execution_completed.emit(execution_id, success, results)
                    
                    if execution_id in self.current_executions:
                        del self.current_executions[execution_id]
                        
            except Exception as e:
                self.error_occurred.emit(
                    "MONITOR_ERROR",
                    f"监控执行状态失败: {str(e)}",
                    str(e)
                )
                
        # 创建监控定时器
        monitor_timer = QTimer()
        monitor_timer.timeout.connect(check_status)
        monitor_timer.start(1000)  # 每秒检查一次
        
        # 保存定时器引用
        self.current_executions[f"{execution_id}_timer"] = monitor_timer


# 全局后端适配器实例
backend_adapter = BackendAdapter()
