import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QPushButton, QFileDialog, QMessageBox,
                            QLabel, QComboBox, QDoubleSpinBox, QCheckBox, 
                            QGroupBox, QFormLayout, QListWidget, QSplitter,
                            QTextBrowser, QDialog)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from gui.plot_widget import PlotWidget
from gui.settings_panel import SettingsPanel
from core.data_loader import DataLoader
from core.msd_calculator import MSDCalculator
from core.fitting import FittingAnalyzer
from core.report_generator import ReportGenerator
from utils.helpers import export_results_to_excel
from utils.help_content import get_help_content

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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSD Analyzer V1.2 - by Lucien")
        self.resize(2000, 1500)

        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 初始化数据处理组件
        self.data_loader = DataLoader()
        self.msd_calculator = MSDCalculator()
        self.fitting_analyzer = FittingAnalyzer()
        self.report_generator = ReportGenerator()
        
        # 初始化UI
        self.setup_ui()
        
        # 状态变量
        self.trajectories = None
        self.msd_results = None
        self.fitting_results = None
        self.scaling_results = None
        self.dimension = None
        self.excluded_particles = []
        
        # 安装事件过滤器以捕获双击标题栏事件
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获双击标题栏事件"""
        if obj == self and event.type() == event.MouseButtonDblClick:
            # 获取鼠标位置
            pos = event.pos()
            # 检查是否在标题栏区域
            if pos.y() < self.frameGeometry().height() - self.geometry().height():
                self.show_help()
                return True
        return super().eventFilter(obj, event)
        
    def show_help(self):
        """显示帮助对话框"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()
        
    def setup_ui(self):
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
        splitter.setSizes([500, 1500])  # 设置初始分割比例
        
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
        
    def load_data(self):
        """加载Excel或CSV数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", "数据文件 (*.xlsx *.xls *.csv);;Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            self.statusBar().showMessage("正在加载数据...")
            QApplication.processEvents()
            self.trajectories, self.dimension = self.data_loader.load_data(file_path)
            
            # 更新设置面板中的颗粒列表
            self.settings_panel.update_particle_list(list(self.trajectories.keys()))

            # 获取单位设置
            space_unit = self.settings_panel.get_space_unit()
            
            # 绘制轨迹图
            self.trajectory_plot.clear()
            self.trajectory_plot.plot_trajectories(self.trajectories, self.dimension, space_unit)
            self.plot_tabs.setCurrentIndex(0)  # 切换到轨迹图
            
            # 更新UI状态
            self.calculate_btn.setEnabled(True)
            self.statusBar().showMessage(f"已加载{len(self.trajectories)}个颗粒的轨迹数据，维度: {self.dimension}D")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")
            self.statusBar().showMessage("加载数据失败")
    
    def calculate_msd(self):
        """计算MSD"""
        if not self.trajectories:
            return
            
        try:
            # 禁用计算按钮，防止重复点击
            self.calculate_btn.setEnabled(False)
            self.statusBar().showMessage("正在计算MSD...")
            QApplication.processEvents()
            
            # 获取排除的颗粒
            self.excluded_particles = self.settings_panel.get_excluded_particles()
            
            # 获取单位设置
            time_unit = self.settings_panel.get_time_unit()
            space_unit = self.settings_panel.get_space_unit()
            
            # 计算MSD - 传入主窗口引用，确保多线程计算不会创建新窗口
            self.msd_results = self.msd_calculator.calculate(
                self.trajectories, 
                self.dimension,
                excluded_particles=self.excluded_particles,
                parent_window=self  # 传入主窗口引用
            )
            
            # 检查MSD计算是否成功
            if self.msd_results is None:
                QMessageBox.warning(self, "警告", "MSD计算被中断或失败，请重试")
                return
            
            # 绘制MSD图
            self.msd_plot.clear()
            self.msd_plot.plot_msd(self.msd_results, time_unit, space_unit)
            
            # 绘制统计量图
            self.stats_plot.clear()
            self.stats_plot.plot_statistics(self.msd_results['stats'], time_unit)
            
            # 绘制RDC图
            self.rdc_plot.clear()
            self.rdc_plot.plot_rdc(self.msd_results['rdc'], self.dimension, time_unit, space_unit)
            
            # 切换到MSD图
            self.plot_tabs.setCurrentIndex(1)
            
            # 更新UI状态
            self.fit_btn.setEnabled(True)
            self.scaling_btn.setEnabled(True)
            self.statusBar().showMessage("MSD计算完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"计算MSD失败: {str(e)}")
            self.statusBar().showMessage("计算MSD失败")
        finally:
            # 重新启用计算按钮
            self.calculate_btn.setEnabled(True)
            
    def fit_msd(self):
        """拟合MSD曲线"""
        if not self.msd_results:
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
            self.fitting_results = self.fitting_analyzer.fit_msd(
                self.msd_results,
                self.dimension,
                fit_settings
            )
            
            # 绘制拟合结果
            self.fitted_msd_plot.clear()
            self.fitted_msd_plot.plot_fitted_msd(
                self.msd_results, 
                self.fitting_results,
                self.dimension,
                fit_settings
            )
            
            # 切换到拟合图
            self.plot_tabs.setCurrentIndex(4)
            
            # 更新UI状态
            self.scaling_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.statusBar().showMessage("MSD拟合完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"拟合MSD失败: {str(e)}")
            self.statusBar().showMessage("拟合MSD失败")
            
    def analyze_scaling(self):
        """进行标度律分析"""
        if not self.msd_results:
            return
            
        try:
            self.statusBar().showMessage("正在进行标度律分析...")
            QApplication.processEvents()
            
            # 获取拟合设置
            fit_settings = self.settings_panel.get_fit_settings()
            
            # 执行标度律分析，传入fitting_results以使用相同的终止时间
            scaling_results = self.fitting_analyzer.analyze_scaling(
                self.msd_results,
                fit_settings,
                self.fitting_results  # 传入已有的拟合结果
            )
            
            # 绘制双对数图
            self.log_log_plot.clear()
            self.log_log_plot.plot_log_log_msd(
                self.msd_results,
                scaling_results,
                fit_settings
            )
            
            # 切换到双对数图
            self.plot_tabs.setCurrentIndex(5)
            
            # 更新结果
            self.scaling_results = scaling_results
            self.statusBar().showMessage("标度律分析完成") 
        except Exception as e:
            QMessageBox.critical(self, "错误", f"标度律分析失败: {str(e)}")
            self.statusBar().showMessage("标度律分析失败")

    def save_results(self):
        """保存结果和生成报告"""
        if not self.msd_results or not self.fitting_results:
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
                'model_type': fit_settings['model_type'],  # 替换原有的gravity相关设置
                'auto_fit': fit_settings['auto_fit'],
                'start_time': fit_settings['start_time'],
                'end_time': fit_settings['end_time'],
                'r_squared_threshold': fit_settings['r_squared_threshold'],
                'excluded_particles': self.excluded_particles,
                'dimension': self.dimension
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
                self.msd_results,
                self.fitting_results,
                self.scaling_results,
                settings
            )
            
            # 生成报告
            report_path = self.report_generator.generate_report(
                os.path.join(save_dir, "report.pdf"),  # 输出PDF文件路径
                self.trajectories,
                self.dimension,
                self.msd_results,
                self.fitting_results,
                self.scaling_results,  # 使用修复后的变量
                settings
            )
            
            self.statusBar().showMessage(f"结果已保存至 {save_dir}")
            QMessageBox.information(self, "保存成功", f"分析结果和报告已保存至:\n{save_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存结果失败: {str(e)}")
            self.statusBar().showMessage("保存结果失败")
    
    def on_excluded_particles_changed(self, excluded_ids):
        """
        当排除颗粒列表变化时的处理函数
        
        参数:
        excluded_ids: 被排除的颗粒ID列表
        """
        # 更新轨迹图的可见性
        self.trajectory_plot.update_particle_visibility(excluded_ids)
        
        # 更新状态栏提示
        if excluded_ids:
            self.statusBar().showMessage(f"已排除 {len(excluded_ids)} 个颗粒: {', '.join(excluded_ids[:3])}{'...' if len(excluded_ids) > 3 else ''}")
        else:
            self.statusBar().showMessage("未排除任何颗粒")