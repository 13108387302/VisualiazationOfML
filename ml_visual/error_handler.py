"""
错误处理模块
提供统一的错误处理和用户友好的错误提示
"""

import sys
import os
import traceback
import logging
from datetime import datetime
from functools import wraps
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QObject, pyqtSignal


class ErrorHandler(QObject):
    """统一错误处理器"""
    
    error_occurred = pyqtSignal(str, str)  # 错误类型, 错误消息
    
    def __init__(self):
        super().__init__()
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志记录"""
        # 在当前项目目录创建logs文件夹
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(current_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log")

        # 创建文件处理器，指定UTF-8编码
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # 改为INFO级别以记录更多信息

        # 创建控制台处理器，设置UTF-8编码
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # 设置格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 获取根日志记录器并配置
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)  # 改为INFO级别以记录更多信息

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 添加新处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.logger = logging.getLogger(__name__)
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        try:
            self.logger.error(f"未捕获的异常: {error_msg}")
        except UnicodeEncodeError:
            # 如果编码失败，使用ASCII安全的方式记录
            safe_msg = error_msg.encode('ascii', 'replace').decode('ascii')
            self.logger.error(f"Uncaught exception: {safe_msg}")
        
        # 发射错误信号
        self.error_occurred.emit("系统错误", str(exc_value))
        
        # 显示用户友好的错误对话框
        self.show_error_dialog("系统错误", 
                              f"程序遇到了一个意外错误:\n{str(exc_value)}\n\n"
                              f"错误详情已记录到日志文件中。")
        
    def show_error_dialog(self, title, message, error_type="error"):
        """显示错误对话框"""
        app = QApplication.instance()
        if not app:
            return
            
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if error_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif error_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
            
        msg_box.exec_()
        
    def log_error(self, error_msg, context=""):
        """记录错误日志"""
        full_msg = f"{context}: {error_msg}" if context else error_msg
        self.logger.error(full_msg)


# 全局错误处理器实例
error_handler = ErrorHandler()


def handle_errors(error_message="操作失败", show_dialog=True):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(str(e), func.__name__)
                
                if show_dialog:
                    error_handler.show_error_dialog(
                        "操作错误",
                        f"{error_message}\n\n错误详情: {str(e)}"
                    )
                else:
                    print(f"错误: {error_message} - {str(e)}")
                    
                return None
        return wrapper
    return decorator


def safe_execute(func, *args, **kwargs):
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.log_error(str(e), func.__name__)
        return None


class ValidationError(Exception):
    """验证错误"""
    pass


class FileOperationError(Exception):
    """文件操作错误"""
    pass


class ComponentError(Exception):
    """组件相关错误"""
    pass


def validate_file_path(file_path):
    """验证文件路径"""
    import os
    if not file_path:
        raise ValidationError("文件路径不能为空")
    if not os.path.exists(file_path):
        raise FileOperationError(f"文件不存在: {file_path}")
    if not os.path.isfile(file_path):
        raise FileOperationError(f"路径不是文件: {file_path}")


def validate_project_data(project_data):
    """验证项目数据"""
    if not isinstance(project_data, dict):
        raise ValidationError("项目数据必须是字典格式")
    
    required_fields = ['name', 'version', 'components']
    for field in required_fields:
        if field not in project_data:
            raise ValidationError(f"项目数据缺少必需字段: {field}")


def validate_component_data(component_data):
    """验证组件数据"""
    if not isinstance(component_data, dict):
        raise ValidationError("组件数据必须是字典格式")
    
    required_fields = ['type', 'name']
    for field in required_fields:
        if field not in component_data:
            raise ValidationError(f"组件数据缺少必需字段: {field}")


class ErrorReporter:
    """错误报告器"""
    
    @staticmethod
    def report_file_error(operation, file_path, error):
        """报告文件操作错误"""
        message = f"文件{operation}失败\n文件: {file_path}\n错误: {str(error)}"
        error_handler.show_error_dialog("文件操作错误", message)
        
    @staticmethod
    def report_component_error(component_name, operation, error):
        """报告组件操作错误"""
        message = f"组件 '{component_name}' {operation}失败\n错误: {str(error)}"
        error_handler.show_error_dialog("组件操作错误", message)
        
    @staticmethod
    def report_network_error(operation, error):
        """报告网络错误"""
        message = f"网络{operation}失败\n错误: {str(error)}\n请检查网络连接"
        error_handler.show_error_dialog("网络错误", message)
        
    @staticmethod
    def report_validation_error(field, value, expected):
        """报告验证错误"""
        message = f"数据验证失败\n字段: {field}\n当前值: {value}\n期望: {expected}"
        error_handler.show_error_dialog("数据验证错误", message)


class ProgressErrorHandler:
    """进度操作错误处理器"""
    
    def __init__(self, progress_dialog=None):
        self.progress_dialog = progress_dialog
        self.errors = []
        
    def add_error(self, error_msg):
        """添加错误"""
        self.errors.append(error_msg)
        
    def has_errors(self):
        """是否有错误"""
        return len(self.errors) > 0
        
    def show_error_summary(self):
        """显示错误摘要"""
        if not self.has_errors():
            return
            
        if len(self.errors) == 1:
            error_handler.show_error_dialog("操作错误", self.errors[0])
        else:
            error_list = "\n".join([f"• {error}" for error in self.errors])
            error_handler.show_error_dialog(
                "多个错误",
                f"操作过程中发生了 {len(self.errors)} 个错误:\n\n{error_list}"
            )
            
    def clear_errors(self):
        """清除错误"""
        self.errors.clear()


def setup_global_error_handler():
    """设置全局错误处理"""
    sys.excepthook = error_handler.handle_exception


# 常用的错误处理函数
def handle_file_operation(operation_name):
    """文件操作错误处理装饰器"""
    return handle_errors(f"文件{operation_name}失败", show_dialog=True)


def handle_component_operation(operation_name):
    """组件操作错误处理装饰器"""
    return handle_errors(f"组件{operation_name}失败", show_dialog=True)


def handle_ui_operation(operation_name):
    """UI操作错误处理装饰器"""
    return handle_errors(f"界面{operation_name}失败", show_dialog=False)


# 初始化全局错误处理
setup_global_error_handler()


class RecoveryManager:
    """错误恢复管理器"""

    def __init__(self):
        self.recovery_actions = {}
        self.auto_save_enabled = True

    def register_recovery_action(self, error_type, action_func):
        """注册错误恢复动作"""
        self.recovery_actions[error_type] = action_func

    def attempt_recovery(self, error_type, context=None):
        """尝试错误恢复"""
        if error_type in self.recovery_actions:
            try:
                return self.recovery_actions[error_type](context)
            except Exception as e:
                print(f"恢复操作失败: {e}")
                return False
        return False

    def auto_save_project(self, project_data):
        """自动保存项目"""
        if not self.auto_save_enabled:
            return

        try:
            import tempfile
            import json
            import datetime

            # 创建临时文件
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix=f'_autosave_{timestamp}.mlv',
                delete=False
            )

            json.dump(project_data, temp_file, indent=2)
            temp_file.close()

            print(f"项目已自动保存到: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            print(f"自动保存失败: {e}")
            return None


# 全局恢复管理器
recovery_manager = RecoveryManager()


def register_recovery_action(error_type, action_func):
    """注册恢复动作的便捷函数"""
    recovery_manager.register_recovery_action(error_type, action_func)


def attempt_recovery(error_type, context=None):
    """尝试恢复的便捷函数"""
    return recovery_manager.attempt_recovery(error_type, context)


# 便捷的日志记录函数
def log_info(message):
    """记录信息日志"""
    try:
        error_handler.logger.info(message)
    except Exception:
        print(f"INFO: {message}")


def log_warning(message):
    """记录警告日志"""
    try:
        error_handler.logger.warning(message)
    except Exception:
        print(f"WARNING: {message}")


def log_error(message):
    """记录错误日志"""
    try:
        error_handler.logger.error(message)
    except Exception:
        print(f"ERROR: {message}")


def log_debug(message):
    """记录调试日志"""
    try:
        error_handler.logger.debug(message)
    except Exception:
        print(f"DEBUG: {message}")


def safe_execute(func, default_return=None, error_message="操作失败"):
    """
    安全执行函数，统一异常处理

    Args:
        func: 要执行的函数
        default_return: 异常时的默认返回值
        error_message: 错误消息前缀

    Returns:
        函数执行结果或默认返回值
    """
    try:
        return func()
    except Exception as e:
        log_error(f"{error_message}: {str(e)}")
        return default_return


def safe_call(obj, method_name, *args, default_return=None, **kwargs):
    """
    安全调用对象方法

    Args:
        obj: 目标对象
        method_name: 方法名称
        *args: 位置参数
        default_return: 异常时的默认返回值
        **kwargs: 关键字参数

    Returns:
        方法执行结果或默认返回值
    """
    try:
        if hasattr(obj, method_name):
            method = getattr(obj, method_name)
            return method(*args, **kwargs)
        else:
            log_warning(f"对象 {type(obj).__name__} 没有方法 {method_name}")
            return default_return
    except Exception as e:
        log_error(f"调用 {type(obj).__name__}.{method_name} 失败: {str(e)}")
        return default_return
