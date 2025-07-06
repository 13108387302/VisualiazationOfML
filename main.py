#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习可视化工具 - 主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_visual import MLVisualizationUI


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("机器学习可视化工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ML Visual Team")
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 启用高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # 显示启动对话框
        window= MLVisualizationUI.show_startup_dialog()

        if window:
            window.show()
            # 运行应用程序
            sys.exit(app.exec_())
        else:
            # 用户取消了启动对话框
            sys.exit(0)

    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
