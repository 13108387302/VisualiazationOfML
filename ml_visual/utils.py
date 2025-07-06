#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块
提供通用工具函数和后端接口
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ComponentConfig:
    """组件配置数据类"""
    component_id: str
    component_type: str
    name: str
    position: tuple
    properties: dict
    

@dataclass
class ConnectionConfig:
    """连接配置数据类"""
    start_component: str
    start_port: int
    end_component: str
    end_port: int


class WorkflowManager:
    """工作流程管理器"""
    
    def __init__(self):
        self.components = {}
        self.connections = []
        
    def add_component(self, component_config: ComponentConfig):
        """添加组件"""
        self.components[component_config.component_id] = component_config
        
    def add_connection(self, connection_config: ConnectionConfig):
        """添加连接"""
        self.connections.append(connection_config)
        
    def remove_component(self, component_id: str):
        """移除组件"""
        if component_id in self.components:
            del self.components[component_id]
            # 移除相关连接
            self.connections = [
                conn for conn in self.connections
                if conn.start_component != component_id and conn.end_component != component_id
            ]
            
    def get_execution_order(self) -> List[str]:
        """获取执行顺序（拓扑排序）"""
        # 构建依赖图
        dependencies = {comp_id: set() for comp_id in self.components.keys()}
        
        for conn in self.connections:
            dependencies[conn.end_component].add(conn.start_component)
            
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
            
        for comp_id in self.components.keys():
            if comp_id not in visited:
                dfs(comp_id)
                
        return result
        
    def validate_workflow(self) -> List[str]:
        """验证工作流程"""
        errors = []
        
        # 检查是否有组件
        if not self.components:
            errors.append("工作流程中没有组件")
            return errors
            
        # 检查连接有效性
        for conn in self.connections:
            if conn.start_component not in self.components:
                errors.append(f"连接中的起始组件不存在: {conn.start_component}")
            if conn.end_component not in self.components:
                errors.append(f"连接中的结束组件不存在: {conn.end_component}")
                
        # 检查循环依赖
        try:
            self.get_execution_order()
        except ValueError as e:
            errors.append(str(e))
            
        return errors
        
    def export_to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            'components': [
                {
                    'id': comp_id,
                    'type': comp.component_type,
                    'name': comp.name,
                    'position': comp.position,
                    'properties': comp.properties
                }
                for comp_id, comp in self.components.items()
            ],
            'connections': [
                {
                    'start_component': conn.start_component,
                    'start_port': conn.start_port,
                    'end_component': conn.end_component,
                    'end_port': conn.end_port
                }
                for conn in self.connections
            ]
        }
        
    def import_from_dict(self, data: Dict[str, Any]):
        """从字典导入"""
        self.components.clear()
        self.connections.clear()
        
        # 导入组件
        for comp_data in data.get('components', []):
            config = ComponentConfig(
                component_id=comp_data['id'],
                component_type=comp_data['type'],
                name=comp_data['name'],
                position=tuple(comp_data['position']),
                properties=comp_data['properties']
            )
            self.add_component(config)
            
        # 导入连接
        for conn_data in data.get('connections', []):
            config = ConnectionConfig(
                start_component=conn_data['start_component'],
                start_port=conn_data['start_port'],
                end_component=conn_data['end_component'],
                end_port=conn_data['end_port']
            )
            self.add_connection(config)


class FileManager:
    """文件管理器"""
    
    @staticmethod
    def save_project(file_path: str, workflow_data: Dict[str, Any]) -> bool:
        """保存项目文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
            
    @staticmethod
    def load_project(file_path: str) -> Optional[Dict[str, Any]]:
        """加载项目文件"""
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文件失败: {e}")
            return None
            
    @staticmethod
    def get_recent_files(max_count: int = 10) -> List[str]:
        """获取最近打开的文件列表"""
        # 这里可以实现最近文件的管理
        # 暂时返回空列表
        return []
        
    @staticmethod
    def add_recent_file(file_path: str):
        """添加到最近文件列表"""
        # 这里可以实现最近文件的管理
        pass


class ComponentValidator:
    """组件验证器"""
    
    @staticmethod
    def validate_data_component(properties: Dict[str, Any]) -> List[str]:
        """验证数据组件"""
        errors = []
        
        if 'file_path' in properties:
            file_path = properties['file_path']
            if not file_path:
                errors.append("文件路径不能为空")
            elif not os.path.exists(file_path):
                errors.append(f"文件不存在: {file_path}")
                
        return errors
        
    @staticmethod
    def validate_model_component(properties: Dict[str, Any]) -> List[str]:
        """验证模型组件"""
        errors = []
        
        # 检查必要参数
        if 'n_estimators' in properties:
            n_estimators = properties['n_estimators']
            if not isinstance(n_estimators, int) or n_estimators <= 0:
                errors.append("树的数量必须是正整数")
                
        if 'max_depth' in properties:
            max_depth = properties['max_depth']
            if max_depth is not None and (not isinstance(max_depth, int) or max_depth <= 0):
                errors.append("最大深度必须是正整数或None")
                
        return errors
        
    @staticmethod
    def validate_component(component_type: str, properties: Dict[str, Any]) -> List[str]:
        """验证组件"""
        if component_type == 'data':
            return ComponentValidator.validate_data_component(properties)
        elif component_type == 'model':
            return ComponentValidator.validate_model_component(properties)
        else:
            return []  # 其他类型暂不验证


class ExecutionEngine:
    """执行引擎接口（预留给后端实现）"""
    
    def __init__(self):
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        
    def execute_workflow(self, workflow_manager: WorkflowManager) -> bool:
        """执行工作流程"""
        # 验证工作流程
        errors = workflow_manager.validate_workflow()
        if errors:
            print("工作流程验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        # 获取执行顺序
        try:
            execution_order = workflow_manager.get_execution_order()
        except ValueError as e:
            print(f"获取执行顺序失败: {e}")
            return False
            
        print("执行顺序:", execution_order)
        
        # 这里是执行的主要逻辑
        # 实际实现时，这里会调用具体的机器学习库
        self.is_running = True
        self.total_steps = len(execution_order)
        
        for i, component_id in enumerate(execution_order):
            self.current_step = i + 1
            component = workflow_manager.components[component_id]
            
            print(f"执行步骤 {self.current_step}/{self.total_steps}: {component.name}")
            
            # 这里调用具体的组件执行逻辑
            success = self._execute_component(component)
            if not success:
                print(f"组件执行失败: {component.name}")
                self.is_running = False
                return False
                
        self.is_running = False
        print("工作流程执行完成")
        return True
        
    def _execute_component(self, component: ComponentConfig) -> bool:
        """执行单个组件（预留接口）"""
        # 这里是具体的组件执行逻辑
        # 根据组件类型调用不同的处理函数
        
        if component.component_type == 'data':
            return self._execute_data_component(component)
        elif component.component_type == 'preprocess':
            return self._execute_preprocess_component(component)
        elif component.component_type == 'model':
            return self._execute_model_component(component)
        elif component.component_type == 'evaluate':
            return self._execute_evaluate_component(component)
        elif component.component_type == 'output':
            return self._execute_output_component(component)
        else:
            print(f"未知组件类型: {component.component_type}")
            return False
            
    def _execute_data_component(self, component: ComponentConfig) -> bool:
        """执行数据组件"""
        print(f"  处理数据组件: {component.name}")
        # 这里实现数据加载、清洗等逻辑
        return True
        
    def _execute_preprocess_component(self, component: ComponentConfig) -> bool:
        """执行预处理组件"""
        print(f"  处理预处理组件: {component.name}")
        # 这里实现数据预处理逻辑
        return True
        
    def _execute_model_component(self, component: ComponentConfig) -> bool:
        """执行模型组件"""
        print(f"  处理模型组件: {component.name}")
        # 这里实现模型训练逻辑
        return True
        
    def _execute_evaluate_component(self, component: ComponentConfig) -> bool:
        """执行评估组件"""
        print(f"  处理评估组件: {component.name}")
        # 这里实现模型评估逻辑
        return True
        
    def _execute_output_component(self, component: ComponentConfig) -> bool:
        """执行输出组件"""
        print(f"  处理输出组件: {component.name}")
        # 这里实现结果输出逻辑
        return True
        
    def stop_execution(self):
        """停止执行"""
        self.is_running = False
        print("执行已停止")
        
    def get_progress(self) -> tuple:
        """获取执行进度"""
        return (self.current_step, self.total_steps)
