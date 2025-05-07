import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.gridspec as gridspec
# 导入自定义的文本处理函数
from utils.text_utils import format_special_chars, superscript_alpha

class ReportGenerator:
    def __init__(self):
        pass
        
    def generate_report(self, output_path, trajectories, dimension, msd_results, 
                       fitting_results, scaling_results, settings):
        """
        生成分析报告
        
        参数:
        output_path: 输出PDF文件路径
        trajectories: 轨迹数据
        dimension: 维度
        msd_results: MSD计算结果
        fitting_results: 拟合结果
        scaling_results: 标度律分析结果
        settings: 分析设置
        
        返回:
        output_path: 生成的报告文件路径
        """
        with PdfPages(output_path) as pdf:
            # 生成报告封面
            self._create_cover_page(pdf, settings)
            
            # 生成轨迹图和MSD曲线图（一页两图）
            self._create_dual_page(pdf, 
                              self._plot_trajectory, [trajectories, dimension, settings],
                              self._plot_msd, [msd_results, settings],
                              "颗粒运动轨迹", "均方位移 (MSD) 曲线")
            
            # 生成统计量图和RDC图（一页两图）
            self._create_dual_page(pdf,
                              self._plot_statistics, [msd_results, settings],
                              self._plot_rdc, [msd_results, dimension, settings],
                              "每个时间点的颗粒统计数量", "动态扩散系数曲线(RDC)")
            
            # 生成拟合结果图和标度律分析图（一页两图）
            self._create_dual_page(pdf,
                              self._plot_fitting, [msd_results, fitting_results, dimension, settings],
                              self._plot_scaling, [msd_results, scaling_results, settings],
                              "平均MSD拟合结果", "双对数坐标下的MSD曲线与标度律分析")
            
            # 生成数据表格
            self._create_data_table_page(pdf, msd_results, fitting_results, scaling_results, settings)
            
        return output_path
        
    def _create_cover_page(self, pdf, settings):
        """创建报告封面"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4尺寸
        
        plt.axis('off')
        
        # 添加标题
        plt.text(0.5, 0.8, "《颗粒运动MSD分析报告》", fontsize=24, ha='center', weight='bold')
        
        # 添加设置信息
        settings_text = f"【分析设置】:\n"
        settings_text += f"时间单位: {settings['time_unit']}\n"
        settings_text += f"空间单位: {settings['space_unit']}\n"
        
        # 更新：使用模型类型替换重力设置
        model_type_map = {
            'brownian': '简单扩散(纯布朗运动)',
            'drift': '定向扩散(漂移速度恒定)',
            'confined': '受限扩散(圆内或球内)'
        }
        model_name = model_type_map.get(settings['model_type'], settings['model_type'])
        settings_text += f"扩散模型: {model_name}\n"
        
        settings_text += f"拟合模式: {'自动拟合' if settings['auto_fit'] else '手动拟合'}\n"
        if settings['auto_fit']:
            settings_text += f"拟合优度阈值：{settings['r_squared_threshold']}\n"
        settings_text += f"起始时间: {settings['start_time']} {settings['time_unit']}\n"
        if not settings['auto_fit']:
            settings_text += f"终止时间: {settings['end_time']} {settings['time_unit']}\n"
        
        plt.text(0.5, 0.5, settings_text, fontsize=12, ha='center', va='center')
        
        # 添加页脚
        plt.text(0.5, 0.15, "分析工具: MSD Analyzer V1.1", fontsize=14, ha='center')

        # 添加作者
        plt.text(0.5, 0.01, "程序作者: Lucien\n联系方式: lucien-6@qq.com", fontsize=10, ha='center')

        # 添加日期
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
        plt.text(0.5, 0.1, f"生成时间: {date_str}", fontsize=14, ha='center')
        
        pdf.savefig(fig)
        plt.close(fig)
        
    def _create_dual_page(self, pdf, plot_func1, args1, plot_func2, args2, title1, title2):
        """创建包含两个图表的页面"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4尺寸
        
        # 创建两个子图
        ax1 = fig.add_subplot(211)  # 上半部分
        ax2 = fig.add_subplot(212)  # 下半部分
        
        # 绘制第一个图表
        plot_func1(ax1, *args1)
        ax1.set_title(title1)
        
        # 绘制第二个图表
        plot_func2(ax2, *args2)
        ax2.set_title(title2)
        
        plt.tight_layout(pad=3.0)  # 增加间距，避免图表重叠
        pdf.savefig(fig)
        plt.close(fig)
        
    def _plot_trajectory(self, ax, trajectories, dimension, settings):
        """在给定的轴上绘制轨迹图"""
        if dimension == 2:
            ax.set_xlabel(f"X ({settings['space_unit']})")
            ax.set_ylabel(f"Y ({settings['space_unit']})")
            
            # 使用不同颜色绘制每个颗粒的轨迹
            colors = plt.cm.tab20.colors  # 使用tab20色彩方案
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]  # 循环使用颜色
                x = data['x'].values
                y = data['y'].values
                
                # 绘制轨迹线
                line, = ax.plot(x, y, '-', alpha=0.7, linewidth=1.5, color=color, label=particle_id)
                
                # 标记起点和终点
                ax.plot(x[0], y[0], '+', color=color, markersize=10)
                ax.plot(x[-1], y[-1], 'o', color=color, markersize=6)
                
        elif dimension == 3:
            # 移除2D轴并创建3D轴
            parent_fig = ax.figure
            parent_fig.delaxes(ax)
            ax = parent_fig.add_subplot(211, projection='3d')
            
            ax.set_xlabel(f"X ({settings['space_unit']})")
            ax.set_ylabel(f"Y ({settings['space_unit']})")
            ax.set_zlabel(f"Z ({settings['space_unit']})")
            
            # 使用不同颜色绘制每个颗粒的轨迹
            colors = plt.cm.tab10.colors  # 使用tab10色彩方案
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]  # 循环使用颜色
                x = data['x'].values
                y = data['y'].values
                z = data['z'].values
                
                # 绘制轨迹线
                line, = ax.plot(x, y, z, '-', alpha=0.7, linewidth=1.5, color=color, label=particle_id)
                
                # 标记起点和终点
                ax.plot([x[0]], [y[0]], [z[0]], '+', color=color, markersize=10)
                ax.plot([x[-1]], [y[-1]], [z[-1]], 'o', color=color, markersize=6)
                
        # 添加图例（如果颗粒数量不多）
        if len(trajectories) <= 10:
            ax.legend(loc='best', fontsize='small')
            
    def _plot_msd(self, ax, msd_results, settings):
        """在给定的轴上绘制MSD曲线"""
        # 绘制每个颗粒的MSD
        for particle_id, msd_data in msd_results['individual'].items():
            ax.plot(msd_data['lag_time'], msd_data['msd'], '-', alpha=0.3, linewidth=1)
            
        # 绘制平均MSD
        avg_msd = msd_results['average']
        ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'r-', linewidth=2, label='平均MSD')
        
        ax.set_xlabel(f"时间延迟 ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.set_title("均方位移 (MSD) 曲线")  # 添加标题
        ax.legend(loc='best')  # 调整图例位置
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_statistics(self, ax, msd_results, settings):
        """在给定的轴上绘制统计量图"""
        stats_data = msd_results['stats']
        ax.bar(stats_data['lag_time'], stats_data['count'], 
              width=stats_data['lag_time'][1]-stats_data['lag_time'][0] if len(stats_data['lag_time']) > 1 else 1)
        
        ax.set_xlabel(f"时间延迟 ({settings['time_unit']})")
        ax.set_ylabel("颗粒数量")
        ax.set_title("每个时间点的颗粒统计数量")  # 添加标题
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_rdc(self, ax, msd_results, dimension, settings):
        """在给定的轴上绘制RDC曲线"""
        rdc_data = msd_results['rdc']
        ax.plot(rdc_data['lag_time'], rdc_data['rdc'], 'b-', linewidth=2)
        
        ax.set_xlabel(f"时间延迟 ({settings['time_unit']})")
        ylabel = f"RDC ({settings['space_unit']}²/{settings['time_unit']})"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.set_title("动态扩散系数曲线(RDC)")  # 添加标题
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_fitting(self, ax, msd_results, fitting_results, dimension, settings):
        """在给定的轴上绘制拟合结果图"""
        # 绘制原始平均MSD数据
        avg_msd = msd_results['average']
        ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'bo', alpha=0.5, label='实验数据')
        
        # 绘制拟合曲线
        fit_times = fitting_results['fit_times']
        fit_msd = fitting_results['fit_msd']
        ax.plot(fit_times, fit_msd, 'r-', linewidth=2, label='拟合曲线')
        
        # 标记拟合区间 - 修复索引错误
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
        # 更新：根据模型类型显示不同的拟合方程和参数
        model_type = settings.get('model_type', 'brownian')
        
        if model_type == 'drift':
            # 定速漂移模型
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            V_conf = fitting_results.get('V_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"V = {fitting_results.get('V', 0):.4e} [{V_conf[0]:.4e}, {V_conf[1]:.4e}] {settings['space_unit']}/{settings['time_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = f"MSD(t) = {2*dimension}Dt + V²t²"
        elif model_type == 'confined':
            # 受限扩散模型
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            L_conf = fitting_results.get('L_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"L = {fitting_results.get('L', 0):.4e} [{L_conf[0]:.4e}, {L_conf[1]:.4e}] {settings['space_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = "MSD(t) = L² (1 - exp(-4Dt/L²))"
        else:
            # 自由扩散模型
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = f"MSD(t) = {2*dimension}Dt"
        
        # 使用format_special_chars处理特殊字符
        fit_text = format_special_chars(fit_text)
        equation = format_special_chars(equation)
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.75, f"拟合方程: {equation}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(f"时间延迟 ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_scaling(self, ax, msd_results, scaling_results, settings):
        """在给定的轴上绘制标度律分析图"""
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
        
        # 添加拟合参数文本
        alpha_conf = scaling_results.get('alpha_conf_interval', [0, 0])
        K_conf = scaling_results.get('K_conf_interval', [0, 0])
        
        fit_text = f"α = {scaling_results['alpha']:.4f} [{alpha_conf[0]:.4f}, {alpha_conf[1]:.4f}]\n"
        fit_text += f"K = {scaling_results['K']:.4e} [{K_conf[0]:.4e}, {K_conf[1]:.4e}]\n"
        fit_text += f"R² = {scaling_results['r_squared']:.4f}"
    
        # 使用format_special_chars处理特殊字符
        fit_text = format_special_chars(fit_text)
        equation = superscript_alpha("MSD(t) = Kt^α")
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.75, f"拟合方程: {equation}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 添加标度律解释
        if scaling_results['alpha'] < 0.9:
            motion_type = "亚扩散 (α < 0.9)"
        elif scaling_results['alpha'] > 1.1:
            motion_type = "超扩散 (α > 1.1)"
        else:
            motion_type = "正常扩散 (α ≈ 1)"
            
        ax.text(0.05, 0.6, f"运动类型: {motion_type}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(f"时间延迟 ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _create_data_table_page(self, pdf, msd_results, fitting_results, scaling_results, settings):
        """创建数据表格页面"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4尺寸
        
        # 关闭坐标轴
        plt.axis('off')
        
        # 重新调整网格布局，使用更合理的高度比例和间距
        gs = gridspec.GridSpec(3, 1, height_ratios=[2.2, 1.0, 0.8], hspace=0.1, 
                              top=0.9, bottom=0.02, left=0.1, right=0.9)
        
        # 添加总标题
        plt.suptitle("数据分析结果汇总", fontsize=16, y=0.98, weight='bold')
        
        # 创建MSD数据表格
        ax1 = plt.subplot(gs[0])
        ax1.axis('off')
        # 调整标题位置，使其更靠近表格
        ax1.text(0.5, 1.05, "平均MSD数据(均匀抽样20行)", fontsize=12, ha='center', weight='bold')
        
        # 准备MSD表格数据
        avg_msd = msd_results['average']
        msd_table_data = []
        
        # 限制显示的数据点数量
        max_rows = 20
        step = max(1, len(avg_msd['lag_time']) // max_rows)
        
        # 创建表头
        msd_table_data.append([f"时间延迟 ({settings['time_unit']})", 
                              f"MSD ({settings['space_unit']}²)", 
                              f"RDC ({settings['space_unit']}²/{settings['time_unit']})"])
        
        # 添加数据行
        rdc_data = msd_results['rdc']
        for i in range(0, len(avg_msd['lag_time']), step):
            if i < len(avg_msd['lag_time']):
                lag_time = avg_msd['lag_time'][i]
                msd_val = avg_msd['msd'][i]
                rdc_val = rdc_data['rdc'][i] if i < len(rdc_data['rdc']) else np.nan
                msd_table_data.append([f"{lag_time:.4f}", f"{msd_val:.6e}", f"{rdc_val:.6e}"])
        
        # 创建表格并优化大小
        msd_table = ax1.table(cellText=msd_table_data, loc='center', cellLoc='center')
        msd_table.auto_set_font_size(False)
        msd_table.set_fontsize(9)
        # 固定表格高度，确保不会过大或过小
        msd_table.scale(1, 1.5)
        
        # 设置表头样式
        for i in range(3):
            msd_table[(0, i)].set_facecolor('#D7E4F5')
            msd_table[(0, i)].set_text_props(weight='bold')

        # 调整MSD表格列宽
        msd_table.auto_set_column_width([0, 1, 2])
        # 设置列宽比例 (第一列窄一些，后两列宽一些)
        col_widths = [0.2, 0.4, 0.4]
        for i, width in enumerate(col_widths):
            for row in range(len(msd_table_data)):
                msd_table[(row, i)].set_width(width)
        
        # 创建拟合结果表格
        ax2 = plt.subplot(gs[1])
        ax2.axis('off')
        # 调整标题位置，使其更靠近表格
        ax2.text(0.5, 0.85, "平均MSD拟合结果", fontsize=12, ha='center', weight='bold')
        
        # 准备拟合结果表格数据
        fit_table_data = []
        
        # 创建表头
        fit_table_data.append(["参数", "值", "95%置信区间", "单位"])
        
        # 添加数据行 - 根据模型类型显示不同参数
        model_type = settings.get('model_type', 'brownian')
        
        # 基本参数（所有模型都有）
        D_conf = fitting_results.get('D_conf_interval', [0, 0])
        D_conf_str = f"[{D_conf[0]:.6e}, {D_conf[1]:.6e}]" if D_conf[0] > 0 else "N/A"
        fit_table_data.append(["扩散系数 (D)", f"{fitting_results['D']:.6e}", D_conf_str, f"{settings['space_unit']}²/{settings['time_unit']}"])
        
        # 根据模型类型添加特定参数
        if model_type == 'drift':
            # 定速漂移模型
            V_conf = fitting_results.get('V_conf_interval', [0, 0])
            V_conf_str = f"[{V_conf[0]:.6e}, {V_conf[1]:.6e}]" if V_conf[0] > 0 else "N/A"
            fit_table_data.append(["漂移速度 (V)", f"{fitting_results.get('V', 0):.6e}", V_conf_str, f"{settings['space_unit']}/{settings['time_unit']}"])
        elif model_type == 'confined':
            # 受限扩散模型
            L_conf = fitting_results.get('L_conf_interval', [0, 0])
            L_conf_str = f"[{L_conf[0]:.6e}, {L_conf[1]:.6e}]" if L_conf[0] > 0 else "N/A"
            fit_table_data.append(["限制范围 (L)", f"{fitting_results.get('L', 0):.6e}", L_conf_str, f"{settings['space_unit']}"])
        else:
            #自由扩散模型
            pass
        
        # 通用参数
        fit_table_data.append(["拟合优度 (R²)", f"{fitting_results['r_squared']:.6f}", "N/A", ""])
        fit_table_data.append(["拟合区间", f"{fitting_results['start_time']:.2f} - {fitting_results['end_time']:.2f}", "N/A", settings['time_unit']])
        
        # 创建表格并优化大小
        fit_table = ax2.table(cellText=fit_table_data, loc='center', cellLoc='center')
        fit_table.auto_set_font_size(False)
        fit_table.set_fontsize(10)
        # 固定表格高度
        fit_table.scale(1, 1.8)
        
        # 设置表头样式
        for i in range(4):
            fit_table[(0, i)].set_facecolor('#D7E4F5')
            fit_table[(0, i)].set_text_props(weight='bold')

        # 调整拟合结果表格列宽
        fit_table.auto_set_column_width([0, 1, 2, 3])
        # 设置列宽比例 (参数列窄一些，置信区间列宽一些)
        fit_col_widths = [0.2, 0.25, 0.35, 0.2]
        for i, width in enumerate(fit_col_widths):
            for row in range(len(fit_table_data)):
                fit_table[(row, i)].set_width(width)
        
        # 创建标度律分析表格
        ax3 = plt.subplot(gs[2])
        ax3.axis('off')
        # 调整标题位置，使其更靠近表格
        ax3.text(0.5, 1.00, "标度律分析结果", fontsize=12, ha='center', weight='bold')
        
        # 准备标度律分析表格数据
        scaling_table_data = []
        
        # 创建表头
        scaling_table_data.append(["参数", "值", "95%置信区间", "单位/说明"])

        # 添加数据行
        alpha_conf = scaling_results.get('alpha_conf_interval', [0, 0])
        alpha_conf_str = f"[{alpha_conf[0]:.4f}, {alpha_conf[1]:.4f}]" if 'alpha_conf_interval' in scaling_results else "N/A"

        K_conf = scaling_results.get('K_conf_interval', [0, 0])
        K_conf_str = f"[{K_conf[0]:.4e}, {K_conf[1]:.4e}]" if 'K_conf_interval' in scaling_results else "N/A"

        scaling_table_data.append(["标度指数 (α)", f"{scaling_results['alpha']:.6f}", alpha_conf_str, ""])
        scaling_table_data.append(["比例系数 (K)", f"{scaling_results['K']:.6e}", K_conf_str, f"{settings['space_unit']}²/{settings['time_unit']}^α"])
        scaling_table_data.append(["拟合优度 (R²)", f"{scaling_results['r_squared']:.6f}", "N/A", ""])

        # 添加运动类型解释
        if scaling_results['alpha'] < 0.9:
            motion_type = "亚扩散 (α < 0.9)"
        elif scaling_results['alpha'] > 1.1:
            motion_type = "超扩散 (α > 1.1)"
        else:
            motion_type = "正常扩散 (α ≈ 1)"
        scaling_table_data.append(["运动类型", motion_type, "N/A", ""])

        # 创建表格并优化大小
        scaling_table = ax3.table(cellText=scaling_table_data, loc='center', cellLoc='center')
        scaling_table.auto_set_font_size(False)
        scaling_table.set_fontsize(10)
        # 固定表格高度
        scaling_table.scale(1, 1.8)

        # 设置表头样式
        for i in range(4):
            scaling_table[(0, i)].set_facecolor('#D7E4F5')
            scaling_table[(0, i)].set_text_props(weight='bold')
        
        # 调整标度律分析表格列宽
        scaling_table.auto_set_column_width([0, 1, 2, 3])
        # 设置列宽比例 (与拟合结果表格保持一致)
        scaling_col_widths = [0.2, 0.25, 0.35, 0.2]
        for i, width in enumerate(scaling_col_widths):
            for row in range(len(scaling_table_data)):
                scaling_table[(row, i)].set_width(width)
        
        pdf.savefig(fig)
        plt.close(fig)