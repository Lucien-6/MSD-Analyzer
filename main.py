import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
import matplotlib.pyplot as plt
from utils.font_config import configure_fonts
import create_icon

try:
    # 配置字体系统
    available_fonts = configure_fonts()
    
    # 确保matplotlib使用Qt5后端
    plt.switch_backend('Qt5Agg')
    
    if __name__ == "__main__":
        print('From Lucien: 欢迎使用MSD Analyzer！\n软件正在启动，请稍候片刻...\n此窗口作为软件的日志输出窗口，请勿关闭。')

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
except Exception as e:
    error_msg = f"程序启动时发生错误:\n{str(e)}\n\n{traceback.format_exc()}"
    app = QApplication(sys.argv) if not 'app' in locals() else app
    QMessageBox.critical(None, "启动错误", error_msg)
    sys.exit(1)