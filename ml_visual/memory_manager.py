"""
内存管理模块
提供内存监控、对象生命周期管理和内存优化功能
"""

import gc
import weakref
import os
from typing import Dict, List, Any, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication

# 可选依赖：psutil用于内存监控
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("警告: psutil未安装，内存监控功能将被禁用")


class MemoryMonitor(QObject):
    """内存监控器"""
    
    memory_warning = pyqtSignal(float)  # 内存使用率警告
    memory_critical = pyqtSignal(float)  # 内存使用率严重警告
    
    def __init__(self, warning_threshold=None, critical_threshold=None):
        super().__init__()

        # 从配置获取阈值
        from .config_manager import get_config
        memory_config = get_config('memory', {})
        self.warning_threshold = warning_threshold or memory_config.get('warning_threshold', 80.0)
        self.critical_threshold = critical_threshold or memory_config.get('critical_threshold', 90.0)
        monitor_interval = memory_config.get('monitor_interval', 5000)

        self.process = None

        if HAS_PSUTIL:
            try:
                self.process = psutil.Process(os.getpid())
                # 监控定时器
                self.monitor_timer = QTimer()
                self.monitor_timer.timeout.connect(self.check_memory)
                self.monitor_timer.start(monitor_interval)  # 使用配置的间隔
            except Exception as e:
                print(f"初始化内存监控失败: {e}")
                self.process = None
        
    def get_memory_usage(self):
        """获取当前内存使用情况"""
        if not HAS_PSUTIL or not self.process:
            return {
                'rss': 0,
                'vms': 0,
                'percent': 0,
                'available': 1024  # 假设有1GB可用
            }

        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()

            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': memory_percent,
                'available': psutil.virtual_memory().available / 1024 / 1024  # MB
            }
        except Exception as e:
            print(f"获取内存信息失败: {e}")
            return None
            
    def check_memory(self):
        """检查内存使用情况"""
        usage = self.get_memory_usage()
        if not usage:
            return
            
        if usage['percent'] >= self.critical_threshold:
            self.memory_critical.emit(usage['percent'])
        elif usage['percent'] >= self.warning_threshold:
            self.memory_warning.emit(usage['percent'])
            
    def force_garbage_collection(self):
        """强制垃圾回收"""
        collected = gc.collect()
        print(f"垃圾回收完成，回收了 {collected} 个对象")
        return collected


class ObjectTracker:
    """对象跟踪器 - 跟踪对象的创建和销毁"""
    
    def __init__(self):
        self.tracked_objects: Dict[str, List[weakref.ref]] = {}
        self.creation_count: Dict[str, int] = {}
        self.destruction_count: Dict[str, int] = {}
        
    def track_object(self, obj: Any, category: str = None):
        """跟踪对象"""
        if category is None:
            category = obj.__class__.__name__
            
        # 创建弱引用
        weak_ref = weakref.ref(obj, lambda ref: self._on_object_destroyed(category))
        
        # 添加到跟踪列表
        if category not in self.tracked_objects:
            self.tracked_objects[category] = []
            self.creation_count[category] = 0
            self.destruction_count[category] = 0
            
        self.tracked_objects[category].append(weak_ref)
        self.creation_count[category] += 1
        
    def _on_object_destroyed(self, category: str):
        """对象被销毁时的回调"""
        self.destruction_count[category] += 1
        
    def get_statistics(self):
        """获取对象统计信息"""
        stats = {}
        for category in self.tracked_objects:
            # 清理已销毁的弱引用
            alive_refs = [ref for ref in self.tracked_objects[category] if ref() is not None]
            self.tracked_objects[category] = alive_refs
            
            stats[category] = {
                'alive': len(alive_refs),
                'created': self.creation_count[category],
                'destroyed': self.destruction_count[category]
            }
            
        return stats
        
    def cleanup_category(self, category: str):
        """清理指定类别的对象"""
        if category in self.tracked_objects:
            # 强制删除所有引用
            for ref in self.tracked_objects[category]:
                obj = ref()
                if obj is not None:
                    del obj
            self.tracked_objects[category].clear()


class MemoryPool:
    """内存池 - 重用对象以减少内存分配"""
    
    def __init__(self, max_size: int = 100):
        self.pools: Dict[str, List[Any]] = {}
        self.max_size = max_size
        
    def get_object(self, object_type: str, factory_func):
        """从池中获取对象"""
        if object_type not in self.pools:
            self.pools[object_type] = []
            
        pool = self.pools[object_type]
        if pool:
            return pool.pop()
        else:
            return factory_func()
            
    def return_object(self, object_type: str, obj: Any):
        """将对象返回到池中"""
        if object_type not in self.pools:
            self.pools[object_type] = []
            
        pool = self.pools[object_type]
        if len(pool) < self.max_size:
            # 重置对象状态
            if hasattr(obj, 'reset'):
                obj.reset()
            pool.append(obj)
        else:
            # 池已满，直接删除对象
            del obj
            
    def clear_pool(self, object_type: str = None):
        """清空池"""
        if object_type:
            if object_type in self.pools:
                self.pools[object_type].clear()
        else:
            for pool in self.pools.values():
                pool.clear()

    def get_pool_stats(self):
        """获取内存池统计信息"""
        stats = {}
        for object_type, pool in self.pools.items():
            stats[object_type] = {
                'size': len(pool),
                'max_size': self.max_size,
                'usage_percent': (len(pool) / self.max_size) * 100
            }
        return stats


class MemoryManager:
    """内存管理器 - 统一管理内存相关功能"""
    
    def __init__(self):
        self.monitor = MemoryMonitor()
        self.tracker = ObjectTracker()
        self.pool = MemoryPool()
        
        # 连接信号
        self.monitor.memory_warning.connect(self.on_memory_warning)
        self.monitor.memory_critical.connect(self.on_memory_critical)
        
    def on_memory_warning(self, usage_percent):
        """内存警告处理"""
        print(f"内存使用警告: {usage_percent:.1f}%")
        # 执行轻量级清理
        self.light_cleanup()
        
    def on_memory_critical(self, usage_percent):
        """内存严重警告处理"""
        print(f"内存使用严重警告: {usage_percent:.1f}%")
        # 执行深度清理
        self.deep_cleanup()
        
    def light_cleanup(self):
        """轻量级内存清理"""
        # 清理内存池
        self.pool.clear_pool()
        
        # 强制垃圾回收
        self.monitor.force_garbage_collection()
        
    def deep_cleanup(self):
        """深度内存清理"""
        # 执行轻量级清理
        self.light_cleanup()
        
        # 清理Qt对象缓存
        app = QApplication.instance()
        if app:
            app.processEvents()
            
        # 多次垃圾回收
        for _ in range(3):
            self.monitor.force_garbage_collection()
            
    def get_memory_report(self):
        """获取内存报告"""
        memory_usage = self.monitor.get_memory_usage()
        object_stats = self.tracker.get_statistics()
        
        return {
            'memory_usage': memory_usage,
            'object_statistics': object_stats,
            'pool_status': {name: len(pool) for name, pool in self.pool.pools.items()}
        }
        
    def track_component(self, component):
        """跟踪组件对象"""
        self.tracker.track_object(component, 'MLComponent')
        
    def track_connection(self, connection):
        """跟踪连接对象"""
        self.tracker.track_object(connection, 'ConnectionLine')
        
    def get_pooled_object(self, object_type: str, factory_func):
        """获取池化对象"""
        return self.pool.get_object(object_type, factory_func)
        
    def return_pooled_object(self, object_type: str, obj):
        """返回池化对象"""
        self.pool.return_object(object_type, obj)


# 全局内存管理器实例
memory_manager = MemoryManager()


def track_object(obj, category=None):
    """跟踪对象的便捷函数"""
    memory_manager.tracker.track_object(obj, category)


def get_memory_usage():
    """获取内存使用情况的便捷函数"""
    return memory_manager.monitor.get_memory_usage()


def force_cleanup():
    """强制清理内存的便捷函数"""
    memory_manager.deep_cleanup()


class MemoryOptimizedList:
    """内存优化的列表 - 自动清理不再使用的对象"""
    
    def __init__(self, max_size=1000, auto_cleanup=True):
        self._items = []
        self.max_size = max_size
        self.auto_cleanup = auto_cleanup
        
    def append(self, item):
        """添加项目"""
        self._items.append(item)
        if self.auto_cleanup and len(self._items) > self.max_size:
            self._cleanup_old_items()
            
    def _cleanup_old_items(self):
        """清理旧项目"""
        # 保留最新的一半项目
        keep_count = self.max_size // 2
        removed_items = self._items[:-keep_count]
        self._items = self._items[-keep_count:]
        
        # 显式删除旧项目
        for item in removed_items:
            del item
            
    def clear(self):
        """清空列表"""
        for item in self._items:
            del item
        self._items.clear()
        
    def __len__(self):
        return len(self._items)
        
    def __getitem__(self, index):
        return self._items[index]
        
    def __iter__(self):
        return iter(self._items)


def memory_efficient_decorator(func):
    """内存效率装饰器 - 在函数执行后清理临时对象"""
    def wrapper(*args, **kwargs):
        # 记录执行前的内存使用
        initial_usage = get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 执行后清理
            gc.collect()
            
            # 检查内存增长
            final_usage = get_memory_usage()
            if initial_usage and final_usage:
                growth = final_usage['rss'] - initial_usage['rss']
                if growth > 50:  # 增长超过50MB
                    print(f"函数 {func.__name__} 内存增长: {growth:.1f}MB")
                    
    return wrapper


class SmartCleaner:
    """智能内存清理器"""

    def __init__(self):
        self.cleanup_threshold = 0.8  # 80%内存使用率时触发清理
        self.last_cleanup_time = 0
        self.cleanup_interval = 30  # 最小清理间隔30秒

    def should_cleanup(self):
        """判断是否应该进行清理"""
        import time
        current_time = time.time()

        # 检查时间间隔
        if current_time - self.last_cleanup_time < self.cleanup_interval:
            return False

        # 检查内存使用率
        usage = get_memory_usage()
        if usage and usage.get('percent', 0) > self.cleanup_threshold * 100:
            return True

        return False

    def smart_cleanup(self):
        """智能清理"""
        if not self.should_cleanup():
            return

        import time
        self.last_cleanup_time = time.time()

        print("开始智能内存清理...")

        # 清理步骤
        steps = [
            self._cleanup_qt_cache,
            self._cleanup_python_cache,
            self._force_garbage_collection,
            self._cleanup_temporary_objects
        ]

        for step in steps:
            try:
                step()
            except Exception as e:
                print(f"清理步骤失败: {e}")

        print("智能内存清理完成")

    def _cleanup_qt_cache(self):
        """清理Qt缓存"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.processEvents()

    def _cleanup_python_cache(self):
        """清理Python缓存"""
        import sys
        # 清理模块缓存中的__pycache__
        for module_name in list(sys.modules.keys()):
            if '__pycache__' in module_name:
                del sys.modules[module_name]

    def _force_garbage_collection(self):
        """强制垃圾回收"""
        import gc
        for _ in range(3):
            collected = gc.collect()
            if collected == 0:
                break

    def _cleanup_temporary_objects(self):
        """清理临时对象"""
        # 这里可以添加应用程序特定的临时对象清理逻辑
        pass


# 全局智能清理器
smart_cleaner = SmartCleaner()


def smart_cleanup():
    """智能清理的便捷函数"""
    smart_cleaner.smart_cleanup()
