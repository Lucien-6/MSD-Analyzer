import os
import sys
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
import matplotlib.pyplot as plt
from utils.font_config import configure_fonts
from utils.logger_config import setup_logger
import create_icon

# 获取模块级日志记录器
logger = logging.getLogger(__name__)


def main():
    """
    MSD Analyzer 程序主入口函数
    
    Author: Lucien
    Email: lucien-6@qq.com
    """
    try:
        # 初始化日志系统
        setup_logger(log_level=logging.INFO)
        
        # 配置字体系统
        available_fonts = configure_fonts()
        
        # 确保matplotlib使用Qt5后端
        plt.switch_backend('Qt5Agg')

        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion风格，更现代化

        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        
        # 如果图标不存在，则创建它
        if not os.path.exists(icon_path):
            icon_path = create_icon.create_einstein_stokes_icon()
        
        # 设置应用程序图标
        app.setWindowIcon(QIcon(icon_path))
        
        # 创建主窗口
        window = MainWindow()
        # 显示主窗口
        window.show()

        # 显示启动提示
        QMessageBox.information(window, "Welcome", 
                               "Lucien: Hallo ~\n"
                               "欢迎使用MSD Analyzer!\n"
                               "双击'单位设置'查看使用指南。")
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        error_msg = f"依赖库导入失败:\n{str(e)}\n请检查是否安装了所有依赖库"
        logger.error(error_msg)
        sys.exit(1)
    except Exception as e:
        error_msg = f"程序启动时发生错误:\n{str(e)}\n\n{traceback.format_exc()}"
        try:
            logger.error(error_msg)
            app = QApplication(sys.argv) if 'app' not in locals() else app
            QMessageBox.critical(None, "启动错误", error_msg)
        except:
            logger.error(error_msg)  # 如果GUI创建失败，至少记录错误
        sys.exit(1)


if __name__ == "__main__":
    main()
