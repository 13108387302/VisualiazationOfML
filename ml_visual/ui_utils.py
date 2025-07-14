"""
UI工具类模块
提供通用的UI组件和工具函数，减少重复代码
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette, QFont, QPainter, QBrush, QPen


class UIUtils:
    """UI工具类 - 提供通用的UI创建和样式方法"""
    
    @staticmethod
    def create_card_frame(title=None, content_widget=None):
        """创建卡片式框架"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
            layout.addWidget(title_label)
            
        if content_widget:
            layout.addWidget(content_widget)
            
        return frame, layout
    
    @staticmethod
    def create_primary_button(text, icon=None):
        """创建主要按钮"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 2px solid #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
                border: 2px solid #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        
        if icon:
            button.setIcon(icon)
            
        return button
    
    @staticmethod
    def create_secondary_button(text, icon=None):
        """创建次要按钮"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
            QPushButton:pressed {
                background-color: #3d4142;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
        """)
        
        if icon:
            button.setIcon(icon)
            
        return button
    
    @staticmethod
    def create_icon_button(icon, tooltip=None, size=32):
        """创建图标按钮"""
        button = QPushButton()
        button.setIcon(icon)
        button.setFixedSize(size, size)
        button.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: {size//2}px;
                background-color: transparent;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 123, 255, 0.1);
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 123, 255, 0.2);
            }}
        """)
        
        if tooltip:
            button.setToolTip(tooltip)
            
        return button
    
    @staticmethod
    def create_separator(orientation=Qt.Horizontal):
        """创建分隔线"""
        separator = QFrame()
        if orientation == Qt.Horizontal:
            separator.setFrameShape(QFrame.HLine)
        else:
            separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        return separator
    
    @staticmethod
    def create_status_label(text="就绪", status_type="info"):
        """创建状态标签"""
        label = QLabel(text)
        
        colors = {
            "info": "#17a2b8",
            "success": "#28a745", 
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        
        color = colors.get(status_type, colors["info"])
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: rgba({color[1:3]}, {color[3:5]}, {color[5:7]}, 0.1);
            }}
        """)
        
        return label


class AnimatedWidget(QWidget):
    """带动画效果的Widget基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        
    def fade_in(self, duration=300):
        """淡入动画"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
        
    def fade_out(self, duration=300):
        """淡出动画"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
        
    def slide_in(self, direction="left", duration=300):
        """滑入动画"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        current_rect = self.geometry()
        if direction == "left":
            start_rect = QRect(-current_rect.width(), current_rect.y(), 
                             current_rect.width(), current_rect.height())
        elif direction == "right":
            start_rect = QRect(current_rect.width(), current_rect.y(),
                             current_rect.width(), current_rect.height())
        elif direction == "top":
            start_rect = QRect(current_rect.x(), -current_rect.height(),
                             current_rect.width(), current_rect.height())
        else:  # bottom
            start_rect = QRect(current_rect.x(), current_rect.height(),
                             current_rect.width(), current_rect.height())
            
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(current_rect)
        self.animation.start()


class NotificationManager(QWidget):
    """通知管理器 - 显示临时通知"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
    def show_notification(self, message, notification_type="info", duration=3000):
        """显示通知"""
        notification = NotificationWidget(message, notification_type)
        self.layout.addWidget(notification)
        self.notifications.append(notification)
        
        # 动画显示
        notification.fade_in()
        
        # 自动移除
        QTimer.singleShot(duration, lambda: self.remove_notification(notification))
        
    def remove_notification(self, notification):
        """移除通知"""
        if notification in self.notifications:
            notification.fade_out()
            QTimer.singleShot(300, lambda: self._remove_widget(notification))
            
    def _remove_widget(self, notification):
        """实际移除widget"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.layout.removeWidget(notification)
            notification.deleteLater()


class NotificationWidget(AnimatedWidget):
    """单个通知组件"""
    
    def __init__(self, message, notification_type="info"):
        super().__init__()
        self.setup_ui(message, notification_type)
        
    def setup_ui(self, message, notification_type):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 消息文本
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # 设置样式
        colors = {
            "info": "#d1ecf1",
            "success": "#d4edda",
            "warning": "#fff3cd", 
            "error": "#f8d7da"
        }
        
        bg_color = colors.get(notification_type, colors["info"])
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: {bg_color};
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 6px;
                margin: 2px;
            }}
        """)


class BaseDialog(QWidget):
    """对话框基类"""

    def __init__(self, title="对话框", parent=None, modal=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        if modal:
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
            self.setWindowModality(Qt.ApplicationModal)
        self.setup_base_ui()

    def setup_base_ui(self):
        """设置基础UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 子类可以重写此方法来添加内容
        self.setup_content()

        # 添加按钮区域
        self.setup_buttons()

    def setup_content(self):
        """设置内容区域 - 子类重写"""
        pass

    def setup_buttons(self):
        """设置按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = UIUtils.create_primary_button("确定")
        self.cancel_button = UIUtils.create_secondary_button("取消")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout)

    def accept(self):
        """接受对话框"""
        self.close()

    def reject(self):
        """拒绝对话框"""
        self.close()


class ProgressDialog(BaseDialog):
    """进度对话框"""

    def __init__(self, title="处理中...", parent=None):
        super().__init__(title, parent, modal=True)
        self.setFixedSize(350, 150)

    def setup_content(self):
        """设置内容"""
        self.label = QLabel("正在处理，请稍候...")
        self.main_layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.main_layout.addWidget(self.progress_bar)

    def setup_buttons(self):
        """进度对话框不需要按钮"""
        pass

    def set_message(self, message):
        """设置消息"""
        self.label.setText(message)

    def set_progress(self, value, maximum=100):
        """设置进度"""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
