import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
# 导入自定义的文本处理函数
from utils.text_utils import format_special_chars, superscript_alpha

class PlotWidget(QWidget):
    def __init__(self, title="", interactive=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.interactive = interactive
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        
        # 添加工具栏
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # 如果是交互式图形，设置鼠标事件
        if self.interactive:
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            # 添加鼠标点击事件处理
            self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
            # 添加pick事件处理
            self.canvas.mpl_connect('pick_event', self.on_pick)
            
        # 存储数据
        self.trajectories = None
        self.dimension = None
        self.particle_lines = {}
        self.particle_visibility = {}
        self.start_markers = {}  # 添加起点标记字典
        self.end_markers = {}    # 添加终点标记字典
        self.annotation = None
        # 添加初始状态标记
        self.all_visible = True

    def clear(self):
        """清除图形"""
        self.figure.clear()
        self.canvas.draw()
        self.particle_lines = {}
        self.particle_visibility = {}
        self.start_markers = {}  # 清除起点标记字典
        self.end_markers = {}    # 清除终点标记字典
        
    def plot_trajectories(self, trajectories, dimension, space_unit):
        """绘制颗粒运动轨迹图"""
        self.trajectories = trajectories
        self.dimension = dimension
        self.figure.clear()
        
        # 创建颜色循环
        colors = list(mcolors.TABLEAU_COLORS.values())
        
        # 存储起点和终点标记
        self.start_markers = {}
        self.end_markers = {}
        
        # 获取颗粒数量
        particle_count = len(trajectories)
        # 设置图例最大显示数量
        max_legend_items = 20
        
        if dimension == 2:
            ax = self.figure.add_subplot(111)
            ax.set_title("颗粒运动轨迹")
            ax.set_xlabel(f"X ({space_unit})")
            ax.set_ylabel(f"Y ({space_unit})")
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                
                # 绘制轨迹线
                line, = ax.plot(x, y, '-', color=color, label=particle_id, 
                            picker=5, alpha=0.7)
                
                # 标记起点和终点 - 使用相同颜色
                start_marker, = ax.plot(x[0], y[0], '^', color=color, markersize=10)
                end_marker, = ax.plot(x[-1], y[-1], 'o', color=color, markersize=6)
                
                # 存储线对象和标记对象
                self.particle_lines[particle_id] = line
                self.start_markers[particle_id] = start_marker
                self.end_markers[particle_id] = end_marker
                self.particle_visibility[particle_id] = True
                
        elif dimension == 3:
            ax = self.figure.add_subplot(111, projection='3d')
            ax.set_title("颗粒运动轨迹")
            ax.set_xlabel(f"X ({space_unit}))")
            ax.set_ylabel(f"Y ({space_unit})")
            ax.set_zlabel(f"Z ({space_unit}))")
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                z = data['z'].values
                
                # 绘制轨迹线
                line, = ax.plot(x, y, z, '-', color=color, label=particle_id, 
                            picker=5, alpha=0.7)
                
                # 标记起点和终点 - 使用相同颜色
                start_marker, = ax.plot([x[0]], [y[0]], [z[0]], '^', color=color, markersize=10)
                end_marker, = ax.plot([x[-1]], [y[-1]], [z[-1]], 'o', color=color, markersize=6)
                
                # 存储线对象和标记对象
                self.particle_lines[particle_id] = line
                self.start_markers[particle_id] = start_marker
                self.end_markers[particle_id] = end_marker
                self.particle_visibility[particle_id] = True
        
        # 创建图例 - 修改位置设置和边界框参数
        handles = [mpatches.Patch(color=colors[i % len(colors)], label=pid) 
                for i, pid in enumerate(trajectories.keys())]
        
        # 处理图例 - 当颗粒数量过多时采用替代方案
        if particle_count <= max_legend_items:
            # 正常显示所有颗粒ID的图例
            legend = ax.legend(handles=handles, loc='upper right', 
                            bbox_to_anchor=(1.15, 1), title="颗粒ID")
            
            # 设置图例文本属性
            particle_ids = list(trajectories.keys())
            for i, text in enumerate(legend.get_texts()):
                if i < len(particle_ids):  # 防止索引越界
                    text.particle_id = particle_ids[i]  # 设置颗粒ID属性
        else:
            # 颗粒数量过多时，只显示部分颗粒ID
            selected_handles = handles[:max_legend_items-1]  # 留一个位置给"更多..."
            selected_ids = list(trajectories.keys())[:max_legend_items-1]
            
            # 添加"更多..."项
            more_patch = mpatches.Patch(color='gray', label=f'更多... (共{particle_count}个)')
            selected_handles.append(more_patch)
            selected_ids.append("more")
            
            # 创建有限的图例
            legend = ax.legend(handles=selected_handles, loc='upper right', 
                            bbox_to_anchor=(1.15, 1), title=f"颗粒ID (显示前{max_legend_items-1}个)")
            
            # 设置图例文本属性
            for i, text in enumerate(legend.get_texts()):
                if i < len(selected_ids):  # 防止索引越界
                    if selected_ids[i] != "more":
                        text.particle_id = selected_ids[i]  # 设置颗粒ID属性
        
        # 调整图形布局，确保图例完全可见
        self.figure.tight_layout()
        self.figure.subplots_adjust(right=0.88)  # 为图例留出足够的空间
        
        # 创建注释对象用于显示颗粒ID
        self.annotation = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                    textcoords="offset points",
                                    bbox=dict(boxstyle="round", fc="w"),
                                    arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)
        
        # 重置状态
        self.all_visible = True
        
        self.canvas.draw()

    def on_mouse_click(self, event):
        """处理鼠标点击事件"""
        if not self.interactive or not hasattr(self, 'particle_lines') or not self.particle_lines:
            return
            
        # 双击左键恢复所有轨迹显示
        if event.dblclick and event.button == 1:
            # 检查是否点击在空白处（没有拾取到任何对象）
            if not event.inaxes or not hasattr(event, 'artist'):
                self._reset_all_visibility()
                return

    def on_pick(self, event):
        """处理鼠标拾取事件"""
        # 获取被点击的对象
        artist = event.artist
        
        # 如果是线条对象（轨迹线）
        if isinstance(artist, Line2D):
            # 获取线条标签（通常是颗粒ID）
            particle_id = artist.get_label()
            
            # 获取鼠标事件
            mouse_event = event.mouseevent
            
            # 左键点击：只显示当前轨迹
            if mouse_event.button == 1:
                self._show_only_particle(particle_id)
                
            # 右键点击：隐藏当前轨迹
            elif mouse_event.button == 3:
                self._hide_particle(particle_id)

    def _show_only_particle(self, particle_id):
        """只显示指定颗粒的轨迹，隐藏其他轨迹"""
        if particle_id not in self.particle_lines:
            return
            
        # 遍历所有轨迹
        for pid, line in self.particle_lines.items():
            # 设置可见性
            visible = (pid == particle_id)
            line.set_visible(visible)
            
            # 同时设置起点和终点标记的可见性
            if pid in self.start_markers:
                self.start_markers[pid].set_visible(visible)
            if pid in self.end_markers:
                self.end_markers[pid].set_visible(visible)
                
            self.particle_visibility[pid] = visible
            
            # 更新图例
            for text in line.axes.get_legend().get_texts():
                if hasattr(text, 'particle_id') and text.particle_id == pid:
                    if visible:
                        text.set_alpha(1.0)
                    else:
                        text.set_alpha(0.3)
        
        self.all_visible = False
        self.canvas.draw_idle()

    def _hide_particle(self, particle_id):
        """隐藏指定颗粒的轨迹"""
        if particle_id not in self.particle_lines:
            return
            
        # 获取轨迹线对象
        line = self.particle_lines[particle_id]
        
        # 设置为不可见
        line.set_visible(False)
        
        # 同时隐藏起点和终点标记
        if particle_id in self.start_markers:
            self.start_markers[particle_id].set_visible(False)
        if particle_id in self.end_markers:
            self.end_markers[particle_id].set_visible(False)
            
        self.particle_visibility[particle_id] = False
        
        # 更新图例
        for text in line.axes.get_legend().get_texts():
            if hasattr(text, 'particle_id') and text.particle_id == particle_id:
                text.set_alpha(0.3)
        
        self.all_visible = False
        self.canvas.draw_idle()

    def _reset_all_visibility(self):
        """重置所有轨迹为可见状态"""
        # 遍历所有轨迹
        for pid, line in self.particle_lines.items():
            # 设置为可见
            line.set_visible(True)
            
            # 同时显示起点和终点标记
            if pid in self.start_markers:
                self.start_markers[pid].set_visible(True)
            if pid in self.end_markers:
                self.end_markers[pid].set_visible(True)
                
            self.particle_visibility[pid] = True
            
            # 更新图例
            for text in line.axes.get_legend().get_texts():
                if hasattr(text, 'particle_id') and text.particle_id == pid:
                    text.set_alpha(1.0)
        
        self.all_visible = True
        self.canvas.draw_idle()

    def plot_msd(self, msd_results, time_unit, space_unit):
        """绘制MSD图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 创建颜色循环
        colors = list(mcolors.TABLEAU_COLORS.values())
        
        # 存储颗粒线条对象和标签，用于单独创建图例
        particle_lines = []
        particle_labels = []
        
        # 获取颗粒数量
        particle_count = len(msd_results['individual'])
        # 设置图例最大显示数量
        max_legend_items = 20
        
        # 绘制每个颗粒的MSD
        for i, (particle_id, msd_data) in enumerate(msd_results['individual'].items()):
            color = colors[i % len(colors)]
            line, = ax.plot(msd_data['lag_time'], msd_data['msd'], '-', 
                   color=color, alpha=0.5, linewidth=1)
            particle_lines.append(line)
            particle_labels.append(f'{particle_id}')
            
        # 绘制平均MSD
        avg_msd = msd_results['average']
        avg_line, = ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'r-', linewidth=2, label='平均MSD')
        
        # 处理图例 - 当颗粒数量过多时采用替代方案
        if particle_count <= max_legend_items:
            # 创建颗粒ID的图例，放在右侧
            particle_legend = ax.legend(handles=particle_lines, labels=particle_labels, 
                                      loc='upper right', bbox_to_anchor=(1.15, 1), 
                                      title="颗粒ID", fontsize='small')
        else:
            # 颗粒数量过多时，只显示部分颗粒ID
            selected_lines = particle_lines[:max_legend_items-1]  # 留一个位置给"更多..."
            selected_labels = particle_labels[:max_legend_items-1]
            
            # 创建一个"更多..."的线条
            more_line, = ax.plot([], [], '-', color='gray', alpha=0.5)
            selected_lines.append(more_line)
            selected_labels.append(f'更多... (共{particle_count}个)')
            
            # 创建有限的图例
            particle_legend = ax.legend(handles=selected_lines, labels=selected_labels, 
                                      loc='upper right', bbox_to_anchor=(1.15, 1), 
                                      title=f"颗粒ID (显示前{max_legend_items-1}个)", fontsize='small')         
        
        # 添加第一个图例回图表中
        ax.add_artist(particle_legend)

        # 创建平均MSD的图例，放在左上角
        ax.legend(handles=[avg_line], loc='upper left')
        
        ax.set_title("均方位移 (MSD) 曲线")
        ax.set_xlabel(f"时间延迟 ({time_unit})")
        # 使用format_special_chars处理特殊字符
        ylabel = f"MSD ({space_unit}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        
        # 调整图形布局，确保图例完全可见
        self.figure.tight_layout()
        self.figure.subplots_adjust(right=0.88)  # 为图例留出足够的空间
        
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_statistics(self, stats_data, time_unit):
        """绘制统计量图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.bar(stats_data['lag_time'], stats_data['count'], width=stats_data['lag_time'][1]-stats_data['lag_time'][0] if len(stats_data['lag_time']) > 1 else 1)
        
        ax.set_title("每个时间点的颗粒统计数量")
        ax.set_xlabel(f"时间延迟 ({time_unit})")
        ax.set_ylabel("颗粒数量")
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_rdc(self, rdc_data, dimension, time_unit, space_unit):
        """绘制RDC图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(rdc_data['lag_time'], rdc_data['rdc'], 'b-', linewidth=2)
        
        ax.set_title("动态扩散系数曲线(RDC) ")
        ax.set_xlabel(f"时间延迟 ({time_unit})")
        # 使用format_special_chars处理特殊字符
        ylabel = f"RDC ({space_unit}²/{time_unit})"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_fitted_msd(self, msd_results, fitting_results, dimension, fit_settings):
        """绘制MSD拟合结果"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 绘制原始平均MSD数据
        avg_msd = msd_results['average']
        ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'bo', alpha=0.5, label='实验数据')
        
        # 绘制拟合曲线
        fit_times = fitting_results['fit_times']
        fit_msd = fitting_results['fit_msd']
        ax.plot(fit_times, fit_msd, 'r-', linewidth=2, label='拟合曲线')
        
        # 标记拟合区间
        start_idx_array = np.where(avg_msd['lag_time'] >= fitting_results['start_time'])[0]
        start_idx = start_idx_array[0] if len(start_idx_array) > 0 else 0
        
        if fitting_results['end_time'] < avg_msd['lag_time'][-1]:
            end_idx_array = np.where(avg_msd['lag_time'] >= fitting_results['end_time'])[0]
            end_idx = end_idx_array[0] if len(end_idx_array) > 0 else len(avg_msd['lag_time'])-1
        else:
            end_idx = len(avg_msd['lag_time'])-1
        
        ax.axvspan(avg_msd['lag_time'][start_idx], avg_msd['lag_time'][end_idx], 
                  alpha=0.2, color='green', label='拟合区间')
        
        # 添加拟合参数文本
        model_type = fitting_results.get('model', 'brownian')
        
        if model_type == 'confined':
            D = fitting_results['D']
            D_err = fitting_results['D_err']
            L = fitting_results['L']
            L_err = fitting_results['L_err']
            r_squared = fitting_results['r_squared']
            fit_text = f"D = {D:.4e} ± {D_err:.4e} {fit_settings['space_unit']}²/{fit_settings['time_unit']}\n"
            fit_text += f"L = {L:.4f} ± {L_err:.4e} {fit_settings['space_unit']}\n"
            fit_text += f"R² = {r_squared:.4f}"
            equation = format_special_chars(f"MSD(t) = L²(1-e^(-{2*dimension}Dt/L²))")
        elif model_type == 'drift':
            D = fitting_results['D']
            D_err = fitting_results['D_err']
            V = fitting_results['V']
            V_err = fitting_results['V_err']
            r_squared = fitting_results['r_squared']
            fit_text = f"D = {D:.4e} ± {D_err:.4e} {fit_settings['space_unit']}²/{fit_settings['time_unit']}\n"
            fit_text += f"V = {V:.4e} ± {V_err:.4e} {fit_settings['space_unit']}/{fit_settings['time_unit']}\n"
            fit_text += f"R² = {r_squared:.4f}"
            equation = format_special_chars(f"MSD(t) = {2*dimension}Dt + V²t²")
        else:  # brownian
            D = fitting_results['D']
            D_err = fitting_results['D_err']
            r_squared = fitting_results['r_squared']
            fit_text = f"D = {D:.4e} ± {D_err:.4e} {fit_settings['space_unit']}²/{fit_settings['time_unit']}\n"
            fit_text += f"R² = {r_squared:.4f}"
            equation = format_special_chars(f"MSD(t) = {2*dimension}Dt")

        # 使用format_special_chars处理特殊字符
        fit_text = format_special_chars(fit_text)
        fit_text = superscript_alpha(fit_text)
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.85, f"拟合方程: {equation}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title("MSD拟合结果")
        ax.set_xlabel(f"时间延迟 ({fit_settings['time_unit']})")
        # 使用format_special_chars处理特殊字符
        ylabel = f"MSD ({fit_settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_log_log_msd(self, msd_results, scaling_results, fit_settings):
        """绘制双对数坐标下的MSD图和标度律分析"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 获取平均MSD数据
        avg_msd = msd_results['average']
        lag_time = avg_msd['lag_time']
        msd = avg_msd['msd']
        
        # 绘制双对数坐标下的MSD数据
        ax.loglog(lag_time, msd, 'bo', alpha=0.5, label='实验数据')
        
        # 绘制拟合曲线
        fit_times = scaling_results['fit_times']
        fit_msd = scaling_results['fit_msd']
        ax.loglog(fit_times, fit_msd, 'r-', linewidth=2, label='拟合曲线')
        
        # 标记拟合区间
        start_idx_array = np.where(lag_time >= fit_settings['start_time'])[0]
        start_idx = start_idx_array[0] if len(start_idx_array) > 0 else 0
        
        if fit_settings['end_time'] < lag_time[-1]:
            end_idx_array = np.where(lag_time >= fit_settings['end_time'])[0]
            end_idx = end_idx_array[0] if len(end_idx_array) > 0 else len(lag_time)-1
        else:
            end_idx = len(lag_time)-1
            
        ax.axvspan(lag_time[start_idx], lag_time[end_idx], 
                  alpha=0.2, color='green', label='拟合区间')
        
        # 添加拟合参数文本
        alpha_err = scaling_results['alpha_err']
        K_err = scaling_results['K_err']
        # 使用format_special_chars处理特殊字符
        fit_text = f"α = {scaling_results['alpha']:.4f} ± {alpha_err:.4f}\n"
        fit_text += f"K = {scaling_results['K']:.4e} ± {K_err:.4e}\n"
        fit_text += f"R² = {scaling_results['r_squared']:.4f}"
        
        # 使用format_special_chars处理特殊字符
        fit_text = format_special_chars(fit_text)
        equation = superscript_alpha("MSD(t) = Kt^α")
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.85, f"拟合方程: {equation}", transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 添加标度律解释
        alpha = scaling_results['alpha']
        interpretation = ""
        if alpha < 0.9:
            interpretation = "次扩散 (Sub-diffusion)"
        elif 0.9 <= alpha <= 1.1:
            interpretation = "正常扩散 (Normal diffusion)"
        else:
            interpretation = "超扩散 (Super-diffusion)"
            
        ax.text(0.05, 0.80, f"扩散类型: {interpretation}", transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title("双对数坐标下的MSD曲线与标度律分析")
        ax.set_xlabel(f"时间延迟 ({fit_settings['time_unit']})")
        # 使用format_special_chars处理特殊字符
        ylabel = f"MSD ({fit_settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if not self.interactive or not hasattr(self, 'annotation') or not self.annotation:
            return
            
        if event.inaxes:
            # 获取当前坐标轴的数据范围
            xmin, xmax = event.inaxes.get_xlim()
            ymin, ymax = event.inaxes.get_ylim()
            
            # 根据数据范围动态调整阈值
            threshold = min(abs(xmax - xmin), abs(ymax - ymin)) * 0.01
            
            # 找到最近的轨迹线
            closest_line = None
            closest_dist = float('inf')
            closest_id = None
            
            for particle_id, line in self.particle_lines.items():
                if not self.particle_visibility[particle_id]:
                    continue
                    
                # 获取线的数据
                if self.dimension == 2:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    
                    # 计算鼠标位置到线的最小距离
                    for i in range(len(xdata)-1):
                        x1, y1 = xdata[i], ydata[i]
                        x2, y2 = xdata[i+1], ydata[i+1]
                        
                        # 计算点到线段的距离
                        dist = self._point_to_segment_dist(event.xdata, event.ydata, x1, y1, x2, y2)
                        
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_line = line
                            closest_id = particle_id
                
                elif self.dimension == 3:
                    # 3D情况下距离计算较复杂，这里简化处理
                    # 仅检查鼠标是否在线的投影附近
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    
                    for i in range(len(xdata)):
                        dist = np.sqrt((event.xdata - xdata[i])**2 + (event.ydata - ydata[i])**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_line = line
                            closest_id = particle_id
            
            # 使用动态阈值判断是否显示注释
            if closest_line and closest_dist < threshold:
                self.annotation.xy = (event.xdata, event.ydata)
                self.annotation.set_text(f"颗粒ID: {closest_id}")
                self.annotation.set_visible(True)
                self.canvas.draw_idle()
            else:
                if self.annotation.get_visible():
                    self.annotation.set_visible(False)
                    self.canvas.draw_idle()
    
    def _toggle_particle_visibility(self, particle_id):
        """切换颗粒轨迹的可见性"""
        if particle_id in self.particle_lines:
            line = self.particle_lines[particle_id]
            visible = not line.get_visible()
            line.set_visible(visible)
            self.particle_visibility[particle_id] = visible
            
            # 更新图例
            for text in line.axes.get_legend().get_texts():
                if hasattr(text, 'particle_id') and text.particle_id == particle_id:
                    if visible:
                        text.set_alpha(1.0)
                    else:
                        text.set_alpha(0.3)
            
            self.canvas.draw_idle()
    
    def _point_to_segment_dist(self, px, py, x1, y1, x2, y2):
        """计算点到线段的距离"""
        # 线段长度的平方
        l2 = (x2 - x1)**2 + (y2 - y1)**2
        
        if l2 == 0:  # 线段退化为点
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        # 计算投影点的参数 t
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
        
        # 投影点坐标
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # 点到投影点的距离
        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def save_figure(self, filename):
        """保存图形到文件"""
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')
        return filename
        