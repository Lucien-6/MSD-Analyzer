"""
MSD Analyzer 日志配置模块

Author: Lucien
Email: lucien-6@qq.com
Date: 2025-12-03
"""
import logging
import os
from datetime import datetime


class QMessageBoxHandler(logging.Handler):
    """
    自定义日志处理器，将 WARNING 及以上级别的日志通过 QMessageBox 弹窗显示
    
    Attributes
    ----------
    parent : QWidget, optional
        弹窗的父窗口
    """
    
    def __init__(self, parent=None):
        """
        初始化处理器
        
        Parameters
        ----------
        parent : QWidget, optional
            弹窗的父窗口
        """
        super().__init__()
        self.parent = parent
        self.setLevel(logging.WARNING)  # 仅处理 WARNING 及以上级别
    
    def emit(self, record):
        """
        处理日志记录，显示弹窗
        
        Parameters
        ----------
        record : logging.LogRecord
            日志记录对象
        """
        try:
            # 延迟导入，避免循环依赖
            from PyQt5.QtWidgets import QMessageBox, QApplication
            
            # 确保有 QApplication 实例
            app = QApplication.instance()
            if app is None:
                return
            
            msg = self.format(record)
            
            if record.levelno >= logging.ERROR:
                QMessageBox.critical(self.parent, "错误", msg)
            elif record.levelno >= logging.WARNING:
                QMessageBox.warning(self.parent, "警告", msg)
                
        except Exception:
            # 如果弹窗失败，静默处理
            pass


def setup_logger(log_dir=None, log_level=logging.INFO, enable_gui_handler=True):
    """
    配置全局日志系统
    
    Parameters
    ----------
    log_dir : str, optional
        日志文件保存目录，默认为 None（不保存到文件）
    log_level : int, optional
        日志级别，默认为 INFO
    enable_gui_handler : bool, optional
        是否启用 GUI 弹窗处理器，默认为 True
        
    Returns
    -------
    logging.Logger
        配置好的根日志记录器
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除已有的处理器（避免重复添加）
    root_logger.handlers.clear()
    
    # 日志格式：时间戳 | 级别 | 模块名:行号 | 消息
    log_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 简洁的弹窗消息格式（不包含时间戳和模块信息）
    gui_format = logging.Formatter(fmt='%(message)s')
    
    # 文件处理器（可选）
    if log_dir:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = f"msd_analyzer_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = os.path.join(log_dir, log_filename)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)
    
    # GUI 弹窗处理器（仅处理 WARNING 及以上级别）
    if enable_gui_handler:
        gui_handler = QMessageBoxHandler()
        gui_handler.setLevel(logging.WARNING)
        gui_handler.setFormatter(gui_format)
        root_logger.addHandler(gui_handler)
    
    return root_logger


def get_logger(name):
    """
    获取指定名称的日志记录器
    
    Parameters
    ----------
    name : str
        日志记录器名称，通常使用 __name__
        
    Returns
    -------
    logging.Logger
        日志记录器实例
    """
    return logging.getLogger(name)
