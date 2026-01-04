"""
MSD Analyzer 主窗口模块

Author: Lucien
Email: lucien-6@qq.com
"""
import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QPushButton, QFileDialog, QMessageBox,
                            QLabel, QComboBox, QDoubleSpinBox, QCheckBox, 
                            QGroupBox, QFormLayout, QListWidget, QSplitter,
                            QTextBrowser, QDialog, QProgressBar)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from gui.plot_widget import PlotWidget
from gui.settings_panel import SettingsPanel
from core.data_loader import DataLoader
from core.msd_calculator import MSDCalculator
from core.fitting import FittingAnalyzer
from core.report_generator import ReportGenerator
from core.app_state import AppState
from core.workers import MSDCalculationWorker, FittingWorker, ScalingAnalysisWorker
from utils.helpers import export_results_to_excel
from utils.help_content import get_help_content

# 获取模块级日志记录器
logger = logging.getLogger(__name__)


class HelpDialog(QDialog):
    """帮助对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MSD Analyzer 使用指南")
        self.resize(1200, 800)

        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        
        # 创建文本浏览器
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setMarkdown(get_help_content())
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.text_browser.setFont(font)
        
        layout.addWidget(self.text_browser)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(close_button)


class MainWindow(QMainWindow):
    """MSD Analyzer 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSD Analyzer V1.6 - by Lucien")
        self.resize(1600, 1200)

        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 初始化应用状态
        self.state = AppState()
        
        # 初始化数据处理组件
        self.data_loader = DataLoader()
        self.msd_calculator = MSDCalculator()
        self.fitting_analyzer = FittingAnalyzer()
        self.report_generator = ReportGenerator()
        
        # 工作线程引用
        self._msd_worker = None
        self._fitting_worker = None
        self._scaling_worker = None
        
        # 初始化UI
        self.setup_ui()
        
        # 安装事件过滤器以捕获双击标题栏事件
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获双击标题栏事件"""
        if obj == self and event.type() == event.MouseButtonDblClick:
            pos = event.pos()
            if pos.y() < self.frameGeometry().height() - self.geometry().height():
                self.show_help()
                return True
        return super().eventFilter(obj, event)
        
    def show_help(self):
        """显示帮助对话框"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧设置面板
        self.settings_panel = SettingsPanel(self)
        
        # 创建右侧绘图区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 创建绘图标签页
        self.plot_tabs = QTabWidget()
        self.trajectory_plot = PlotWidget("轨迹图", interactive=True)
        self.msd_plot = PlotWidget("MSD图")
        self.stats_plot = PlotWidget("统计量图")
        self.rdc_plot = PlotWidget("RDC图")
        self.fitted_msd_plot = PlotWidget("平均MSD拟合图")
        self.log_log_plot = PlotWidget("双对数MSD图")
        
        self.plot_tabs.addTab(self.trajectory_plot, "轨迹图")
        self.plot_tabs.addTab(self.msd_plot, "MSD图")
        self.plot_tabs.addTab(self.stats_plot, "统计量图")
        self.plot_tabs.addTab(self.rdc_plot, "RDC图")
        self.plot_tabs.addTab(self.fitted_msd_plot, "平均MSD拟合图")
        self.plot_tabs.addTab(self.log_log_plot, "双对数MSD图")
        
        right_layout.addWidget(self.plot_tabs)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("加载数据")
        self.calculate_btn = QPushButton("计算MSD")
        self.fit_btn = QPushButton("拟合MSD")
        self.scaling_btn = QPushButton("标度律分析")
        self.save_btn = QPushButton("完成并保存")
        
        self.calculate_btn.setEnabled(False)
        self.fit_btn.setEnabled(False)
        self.scaling_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.fit_btn)
        button_layout.addWidget(self.scaling_btn)
        button_layout.addWidget(self.save_btn)
        
        right_layout.addLayout(button_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.settings_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 1500])
        
        main_layout.addWidget(splitter)
        
        # 连接信号和槽
        self.load_btn.clicked.connect(self.load_data)
        self.calculate_btn.clicked.connect(self.calculate_msd)
        self.fit_btn.clicked.connect(self.fit_msd)
        self.scaling_btn.clicked.connect(self.analyze_scaling)
        self.save_btn.clicked.connect(self.save_results)
        
        # 连接设置面板的排除颗粒变化信号
        self.settings_panel.excluded_particles_changed.connect(self.on_excluded_particles_changed)
        
        # 设置状态栏
        self.statusBar().showMessage("就绪")
        
        # 创建进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def _show_progress(self, message="处理中..."):
        """
        显示进度条
        
        Parameters
        ----------
        message : str
            状态栏显示的消息
        """
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage(message)
    
    def _hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
    
    def _update_progress(self, percent, message):
        """
        更新进度条
        
        Parameters
        ----------
        percent : int
            进度百分比 (0-100)
        message : str
            状态消息
        """
        self.progress_bar.setValue(percent)
        self.statusBar().showMessage(message)
        
    def load_data(self):
        """加载Excel或CSV数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", 
            "数据文件 (*.xlsx *.xls *.csv);;Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            self.statusBar().showMessage("正在加载数据...")
            QApplication.processEvents()
            
            # 加载数据
            self.state.trajectories, self.state.dimension = self.data_loader.load_data(file_path)
            self.state.current_file_path = file_path
            
            # 重置计算结果
            self.state.reset_results()
            
            # 更新设置面板中的颗粒列表
            self.settings_panel.update_particle_list(list(self.state.trajectories.keys()))

            # 获取单位设置
            space_unit = self.settings_panel.get_space_unit()
            
            # 绘制轨迹图
            self.trajectory_plot.clear()
            self.trajectory_plot.plot_trajectories(
                self.state.trajectories, 
                self.state.dimension, 
                space_unit
            )
            self.plot_tabs.setCurrentIndex(0)
            
            # 更新UI状态
            self.calculate_btn.setEnabled(True)
            self.fit_btn.setEnabled(False)
            self.scaling_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            
            self.statusBar().showMessage(
                f"已加载{len(self.state.trajectories)}个颗粒的轨迹数据，维度: {self.state.dimension}D"
            )
            
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")
            self.statusBar().showMessage("加载数据失败")
    
    def calculate_msd(self):
        """计算MSD（使用后台线程）"""
        if not self.state.has_trajectories():
            return
        
        # 如果已有计算在进行中，忽略
        if self._msd_worker is not None and self._msd_worker.isRunning():
            return
            
        try:
            # 禁用按钮
            self._set_buttons_enabled(False)
            self._show_progress("正在计算MSD...")
            
            # 获取排除的颗粒
            self.state.excluded_particles = self.settings_panel.get_excluded_particles()
            
            # 创建工作线程
            self._msd_worker = MSDCalculationWorker(
                self.msd_calculator,
                self.state.trajectories,
                self.state.dimension,
                self.state.excluded_particles
            )
            
            # 连接信号
            self._msd_worker.progress.connect(self._update_progress)
            self._msd_worker.finished.connect(self._on_msd_calculation_finished)
            self._msd_worker.error.connect(self._on_msd_calculation_error)
            
            # 启动计算
            self._msd_worker.start()
            
        except Exception as e:
            logger.error(f"启动MSD计算失败: {str(e)}")
            self._hide_progress()
            self._set_buttons_enabled(True, has_trajectories=True)
            QMessageBox.critical(self, "错误", f"计算MSD失败: {str(e)}")
    
    def _on_msd_calculation_finished(self, result):
        """MSD计算完成的处理函数"""
        self._hide_progress()
        
        if result is None:
            QMessageBox.warning(self, "警告", "MSD计算被中断或失败，请重试")
            self._set_buttons_enabled(True, has_trajectories=True)
            return
        
        # 保存结果
        self.state.msd_results = result
        
        # 获取单位设置
        time_unit = self.settings_panel.get_time_unit()
        space_unit = self.settings_panel.get_space_unit()
        
        # 绘制MSD图
        self.msd_plot.clear()
        self.msd_plot.plot_msd(self.state.msd_results, time_unit, space_unit)
        
        # 绘制统计量图
        self.stats_plot.clear()
        self.stats_plot.plot_statistics(self.state.msd_results['stats'], time_unit)
        
        # 绘制RDC图
        self.rdc_plot.clear()
        self.rdc_plot.plot_rdc(
            self.state.msd_results['rdc'], 
            self.state.dimension, 
            time_unit, 
            space_unit
        )
        
        # 切换到MSD图
        self.plot_tabs.setCurrentIndex(1)
        
        # 更新UI状态
        self._set_buttons_enabled(True, has_trajectories=True, has_msd=True)
        self.statusBar().showMessage("MSD计算完成")
    
    def _on_msd_calculation_error(self, error_msg):
        """MSD计算错误的处理函数"""
        self._hide_progress()
        self._set_buttons_enabled(True, has_trajectories=True)
        logger.error(f"MSD计算错误: {error_msg}")
        QMessageBox.critical(self, "错误", f"计算MSD失败: {error_msg}")
        self.statusBar().showMessage("计算MSD失败")
            
    def fit_msd(self):
        """拟合MSD曲线"""
        if not self.state.has_msd_results():
            return
            
        try:
            # 验证设置
            valid, message = self.settings_panel.validate_settings()
            if not valid:
                QMessageBox.warning(self, "参数错误", message)
                return
                
            self.statusBar().showMessage("正在拟合MSD...")
            QApplication.processEvents()
            
            # 获取拟合设置
            fit_settings = self.settings_panel.get_fit_settings()
            
            # 执行拟合
            self.state.fitting_results = self.fitting_analyzer.fit_msd(
                self.state.msd_results,
                self.state.dimension,
                fit_settings
            )
            
            # 绘制拟合结果
            self.fitted_msd_plot.clear()
            self.fitted_msd_plot.plot_fitted_msd(
                self.state.msd_results, 
                self.state.fitting_results,
                self.state.dimension,
                fit_settings
            )
            
            # 切换到拟合图
            self.plot_tabs.setCurrentIndex(4)
            
            # 更新UI状态
            self.scaling_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.statusBar().showMessage("MSD拟合完成")
            
        except Exception as e:
            logger.error(f"拟合MSD失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"拟合MSD失败: {str(e)}")
            self.statusBar().showMessage("拟合MSD失败")
            
    def analyze_scaling(self):
        """进行标度律分析"""
        if not self.state.has_msd_results():
            return
            
        try:
            self.statusBar().showMessage("正在进行标度律分析...")
            QApplication.processEvents()
            
            # 获取拟合设置
            fit_settings = self.settings_panel.get_fit_settings()
            
            # 执行标度律分析
            self.state.scaling_results = self.fitting_analyzer.analyze_scaling(
                self.state.msd_results,
                fit_settings,
                self.state.fitting_results
            )
            
            # 绘制双对数图
            self.log_log_plot.clear()
            self.log_log_plot.plot_log_log_msd(
                self.state.msd_results,
                self.state.scaling_results,
                fit_settings
            )
            
            # 切换到双对数图
            self.plot_tabs.setCurrentIndex(5)
            
            self.statusBar().showMessage("标度律分析完成")
            
        except Exception as e:
            logger.error(f"标度律分析失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"标度律分析失败: {str(e)}")
            self.statusBar().showMessage("标度律分析失败")

    def save_results(self):
        """保存结果和生成报告"""
        if not self.state.has_msd_results() or not self.state.has_fitting_results():
            return
            
        try:
            # 选择保存目录
            save_dir = QFileDialog.getExistingDirectory(self, "选择保存目录")
            if not save_dir:
                return
                
            self.statusBar().showMessage("正在保存结果和生成报告...")
            QApplication.processEvents()
            
            # 获取所有设置
            fit_settings = self.settings_panel.get_fit_settings()
            settings = {
                'time_unit': fit_settings['time_unit'],
                'space_unit': fit_settings['space_unit'],
                'model_type': fit_settings['model_type'],
                'auto_fit': fit_settings['auto_fit'],
                'start_time': fit_settings['start_time'],
                'end_time': fit_settings['end_time'],
                'r_squared_threshold': fit_settings['r_squared_threshold'],
                'excluded_particles': self.state.excluded_particles,
                'dimension': self.state.dimension
            }
            
            # 保存图像
            self.trajectory_plot.save_figure(os.path.join(save_dir, "trajectory_plot.png"))
            self.msd_plot.save_figure(os.path.join(save_dir, "msd_plot.png"))
            self.stats_plot.save_figure(os.path.join(save_dir, "stats_plot.png"))
            self.rdc_plot.save_figure(os.path.join(save_dir, "rdc_plot.png"))
            self.fitted_msd_plot.save_figure(os.path.join(save_dir, "fitted_msd_plot.png"))
            self.log_log_plot.save_figure(os.path.join(save_dir, "log_log_plot.png"))
            
            # 导出Excel数据
            excel_path = os.path.join(save_dir, "msd_analysis_results.xlsx")
            export_results_to_excel(
                excel_path,
                self.state.msd_results,
                self.state.fitting_results,
                self.state.scaling_results,
                settings
            )
            
            # 生成报告
            self.report_generator.generate_report(
                os.path.join(save_dir, "report.pdf"),
                self.state.trajectories,
                self.state.dimension,
                self.state.msd_results,
                self.state.fitting_results,
                self.state.scaling_results,
                settings
            )
            
            self.statusBar().showMessage(f"结果已保存至 {save_dir}")
            QMessageBox.information(self, "保存成功", f"分析结果和报告已保存至:\n{save_dir}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"保存结果失败: {str(e)}")
            self.statusBar().showMessage("保存结果失败")
    
    def _set_buttons_enabled(self, enabled, has_trajectories=False, has_msd=False, has_fitting=False):
        """
        设置按钮的启用状态
        
        Parameters
        ----------
        enabled : bool
            基础启用状态
        has_trajectories : bool
            是否有轨迹数据
        has_msd : bool
            是否有MSD结果
        has_fitting : bool
            是否有拟合结果
        """
        self.load_btn.setEnabled(enabled)
        self.calculate_btn.setEnabled(enabled and has_trajectories)
        self.fit_btn.setEnabled(enabled and has_msd)
        self.scaling_btn.setEnabled(enabled and has_msd)
        self.save_btn.setEnabled(enabled and has_fitting)
    
    def on_excluded_particles_changed(self, excluded_ids):
        """
        当排除颗粒列表变化时的处理函数
        
        Parameters
        ----------
        excluded_ids : list
            被排除的颗粒ID列表
        """
        # 更新状态
        self.state.excluded_particles = excluded_ids
        
        # 更新轨迹图的可见性
        self.trajectory_plot.update_particle_visibility(excluded_ids)
        
        # 更新状态栏提示
        if excluded_ids:
            display_ids = ', '.join(excluded_ids[:3])
            suffix = '...' if len(excluded_ids) > 3 else ''
            self.statusBar().showMessage(f"已排除 {len(excluded_ids)} 个颗粒: {display_ids}{suffix}")
        else:
            self.statusBar().showMessage("未排除任何颗粒")
