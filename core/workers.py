"""
MSD Analyzer 后台工作线程模块

提供异步计算功能，避免阻塞 GUI。

Author: Lucien
Email: lucien-6@qq.com
Date: 2025-12-03
"""
import logging
from PyQt5.QtCore import QThread, pyqtSignal

# 获取模块级日志记录器
logger = logging.getLogger(__name__)


class MSDCalculationWorker(QThread):
    """
    MSD 计算工作线程
    
    在后台线程中执行 MSD 计算，避免阻塞主 GUI 线程。
    
    Signals
    -------
    progress : pyqtSignal(int, str)
        进度信号，参数为进度百分比和状态消息
    finished : pyqtSignal(dict)
        计算完成信号，参数为计算结果
    error : pyqtSignal(str)
        错误信号，参数为错误消息
    """
    # 信号定义
    progress = pyqtSignal(int, str)   # 进度百分比, 消息
    finished = pyqtSignal(dict)        # 计算结果
    error = pyqtSignal(str)            # 错误消息
    
    def __init__(self, calculator, trajectories, dimension, excluded_particles=None):
        """
        初始化工作线程
        
        Parameters
        ----------
        calculator : MSDCalculator
            MSD 计算器实例
        trajectories : dict
            轨迹数据字典
        dimension : int
            轨迹维度（2或3）
        excluded_particles : list, optional
            要排除的粒子ID列表
        """
        super().__init__()
        self.calculator = calculator
        self.trajectories = trajectories
        self.dimension = dimension
        self.excluded_particles = excluded_particles or []
        self._is_cancelled = False
    
    def run(self):
        """执行MSD计算"""
        try:
            self.progress.emit(0, "正在准备计算...")
            
            result = self.calculator.calculate(
                self.trajectories,
                self.dimension,
                self.excluded_particles,
                progress_callback=self._report_progress
            )
            
            if not self._is_cancelled and result is not None:
                self.progress.emit(100, "计算完成")
                self.finished.emit(result)
            elif self._is_cancelled:
                logger.info("MSD计算已取消")
                
        except Exception as e:
            logger.error(f"MSD计算出错: {str(e)}")
            self.error.emit(str(e))
    
    def _report_progress(self, percent, message):
        """
        报告计算进度
        
        Parameters
        ----------
        percent : int
            进度百分比 (0-100)
        message : str
            状态消息
        """
        if not self._is_cancelled:
            self.progress.emit(percent, message)
    
    def cancel(self):
        """取消计算"""
        self._is_cancelled = True
        logger.info("请求取消MSD计算")


class FittingWorker(QThread):
    """
    拟合分析工作线程
    
    在后台线程中执行拟合分析。
    
    Signals
    -------
    finished : pyqtSignal(dict)
        拟合完成信号，参数为拟合结果
    error : pyqtSignal(str)
        错误信号，参数为错误消息
    """
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, analyzer, msd_results, dimension, fit_settings):
        """
        初始化工作线程
        
        Parameters
        ----------
        analyzer : FittingAnalyzer
            拟合分析器实例
        msd_results : dict
            MSD计算结果
        dimension : int
            轨迹维度
        fit_settings : dict
            拟合设置
        """
        super().__init__()
        self.analyzer = analyzer
        self.msd_results = msd_results
        self.dimension = dimension
        self.fit_settings = fit_settings
    
    def run(self):
        """执行拟合分析"""
        try:
            result = self.analyzer.fit_msd(
                self.msd_results,
                self.dimension,
                self.fit_settings
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"拟合分析出错: {str(e)}")
            self.error.emit(str(e))


class ScalingAnalysisWorker(QThread):
    """
    标度律分析工作线程
    
    Signals
    -------
    finished : pyqtSignal(dict)
        分析完成信号，参数为分析结果
    error : pyqtSignal(str)
        错误信号，参数为错误消息
    """
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, analyzer, msd_results, fit_settings, fitting_results=None):
        """
        初始化工作线程
        
        Parameters
        ----------
        analyzer : FittingAnalyzer
            拟合分析器实例
        msd_results : dict
            MSD计算结果
        fit_settings : dict
            拟合设置
        fitting_results : dict, optional
            已有的拟合结果，用于确定终止时间
        """
        super().__init__()
        self.analyzer = analyzer
        self.msd_results = msd_results
        self.fit_settings = fit_settings
        self.fitting_results = fitting_results
    
    def run(self):
        """执行标度律分析"""
        try:
            result = self.analyzer.analyze_scaling(
                self.msd_results,
                self.fit_settings,
                self.fitting_results
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"标度律分析出错: {str(e)}")
            self.error.emit(str(e))

