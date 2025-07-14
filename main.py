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
    # 启用高DPI支持（必须在创建QApplication之前设置）
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("机器学习可视化工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ML Visual Team")

    # 设置应用样式
    app.setStyle('Fusion')
    
    try:
        # 设置全局异常处理
        from ml_visual.error_handler import setup_global_error_handler, log_info
        setup_global_error_handler()

        # 记录应用程序启动
        log_info("=== VML 应用程序启动 ===")
        log_info(f"Python版本: {sys.version}")
        log_info(f"PyQt5版本: {QApplication.instance().applicationVersion()}")

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

        # 显示用户友好的错误对话框
        try:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("启动错误")
            msg.setText("应用程序启动失败")
            msg.setDetailedText(str(e))
            msg.exec_()
        except:
            pass  # 如果连错误对话框都无法显示，就静默失败

        sys.exit(1)


if __name__ == '__main__':
    main()
