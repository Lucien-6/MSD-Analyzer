"""
MSD Analyzer Report Generator Module

Generates publication-quality PDF reports with analysis results,
figures, and data tables.

Author: Lucien
Email: lucien-6@qq.com
"""
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.gridspec as gridspec
# Import custom text processing functions
from utils.text_utils import format_special_chars, superscript_alpha


class ReportGenerator:
    """
    Generate comprehensive PDF reports for MSD analysis results.
    
    Creates publication-quality figures and data tables with
    proper formatting and English labels.
    """
    
    def __init__(self):
        pass
        
    def generate_report(self, output_path, trajectories, dimension, msd_results, 
                       fitting_results, scaling_results, settings):
        """
        Generate analysis report.
        
        Parameters
        ----------
        output_path : str
            Output PDF file path
        trajectories : dict
            Trajectory data
        dimension : int
            Trajectory dimension
        msd_results : dict
            MSD calculation results
        fitting_results : dict
            Fitting results
        scaling_results : dict
            Scaling analysis results
        settings : dict
            Analysis settings
        
        Returns
        -------
        str
            Generated report file path
        """
        with PdfPages(output_path) as pdf:
            # Generate cover page
            self._create_cover_page(pdf, settings)
            
            # Generate trajectory and MSD plots (two per page)
            self._create_dual_page(pdf, 
                              self._plot_trajectory, [trajectories, dimension, settings],
                              self._plot_msd, [msd_results, settings],
                              "Particle Trajectories", "Mean Squared Displacement (MSD)")
            
            # Generate statistics and RDC plots
            self._create_dual_page(pdf,
                              self._plot_statistics, [msd_results, settings],
                              self._plot_rdc, [msd_results, dimension, settings],
                              "Particle Count per Lag Time", "Running Diffusion Coefficient (RDC)")
            
            # Generate fitting and scaling plots
            self._create_dual_page(pdf,
                              self._plot_fitting, [msd_results, fitting_results, dimension, settings],
                              self._plot_scaling, [msd_results, scaling_results, settings],
                              "MSD Fitting Results", "Log-Log MSD Curve and Scaling Analysis")
            
            # Generate data tables
            self._create_data_table_page(pdf, msd_results, fitting_results, scaling_results, settings)
            
        return output_path
        
    def _create_cover_page(self, pdf, settings):
        """Create report cover page"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
        
        plt.axis('off')
        
        # Add title
        plt.text(0.5, 0.8, "MSD Analysis Report", fontsize=24, ha='center', weight='bold')
        
        # Add settings information
        settings_text = "Analysis Settings:\n\n"
        settings_text += f"Time Unit: {settings['time_unit']}\n"
        settings_text += f"Space Unit: {settings['space_unit']}\n"
        
        # Model type mapping
        model_type_map = {
            'brownian': 'Brownian Motion',
            'drift': 'Drift Diffusion',
            'confined': 'Confined Diffusion'
        }
        model_name = model_type_map.get(settings['model_type'], settings['model_type'])
        settings_text += f"Diffusion Model: {model_name}\n"
        
        settings_text += f"Fitting Mode: {'Auto Fitting' if settings['auto_fit'] else 'Manual Fitting'}\n"
        if settings['auto_fit']:
            settings_text += f"R² Threshold: {settings['r_squared_threshold']}\n"
        settings_text += f"Start Time: {settings['start_time']} {settings['time_unit']}\n"
        if not settings['auto_fit']:
            settings_text += f"End Time: {settings['end_time']} {settings['time_unit']}\n"
        
        plt.text(0.5, 0.5, settings_text, fontsize=12, ha='center', va='center')
        
        # Add footer
        plt.text(0.5, 0.15, "Analysis Tool: MSD Analyzer V1.3", fontsize=14, ha='center')

        # Add author
        plt.text(0.5, 0.01, "Author: Lucien\nContact: lucien-6@qq.com", fontsize=10, ha='center')

        # Add date
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        plt.text(0.5, 0.1, f"Generated: {date_str}", fontsize=14, ha='center')
        
        pdf.savefig(fig)
        plt.close(fig)
        
    def _create_dual_page(self, pdf, plot_func1, args1, plot_func2, args2, title1, title2):
        """Create page with two plots"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
        
        # Create two subplots
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        
        # Plot first figure
        plot_func1(ax1, *args1)
        ax1.set_title(title1, fontweight='bold')
        
        # Plot second figure
        plot_func2(ax2, *args2)
        ax2.set_title(title2, fontweight='bold')
        
        plt.tight_layout(pad=3.0)
        pdf.savefig(fig)
        plt.close(fig)
        
    def _plot_trajectory(self, ax, trajectories, dimension, settings):
        """Plot trajectories on given axes"""
        if dimension == 2:
            ax.set_xlabel(f"X ({settings['space_unit']})")
            ax.set_ylabel(f"Y ({settings['space_unit']})")
            # Set equal aspect ratio for 1:1 scale
            ax.set_aspect('equal', adjustable='datalim')
            
            colors = plt.cm.tab20.colors
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                
                # Plot trajectory line
                line, = ax.plot(x, y, '-', alpha=0.7, linewidth=1.5, color=color, label=particle_id)
                
                # Mark start and end points
                ax.plot(x[0], y[0], '^', color=color, markersize=10)
                ax.plot(x[-1], y[-1], 'o', color=color, markersize=6)
                
        elif dimension == 3:
            # Remove 2D axes and create 3D axes
            parent_fig = ax.figure
            parent_fig.delaxes(ax)
            ax = parent_fig.add_subplot(211, projection='3d')
            
            ax.set_xlabel(f"X ({settings['space_unit']})")
            ax.set_ylabel(f"Y ({settings['space_unit']})")
            ax.set_zlabel(f"Z ({settings['space_unit']})")
            # Set equal aspect ratio for 3D plot
            ax.set_box_aspect([1, 1, 1])
            
            colors = plt.cm.tab10.colors
            
            for i, (particle_id, data) in enumerate(trajectories.items()):
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                z = data['z'].values
                
                # Plot trajectory line
                line, = ax.plot(x, y, z, '-', alpha=0.7, linewidth=1.5, color=color, label=particle_id)
                
                # Mark start and end points
                ax.plot([x[0]], [y[0]], [z[0]], '^', color=color, markersize=10)
                ax.plot([x[-1]], [y[-1]], [z[-1]], 'o', color=color, markersize=6)
                
        # Add legend if particle count is small
        if len(trajectories) <= 10:
            ax.legend(loc='best', fontsize='small', title='Particle ID')
            
    def _plot_msd(self, ax, msd_results, settings):
        """Plot MSD curves on given axes"""
        # Plot individual MSD curves
        for particle_id, msd_data in msd_results['individual'].items():
            ax.plot(msd_data['lag_time'], msd_data['msd'], '-', alpha=0.3, linewidth=1)
            
        # Plot average MSD
        avg_msd = msd_results['average']
        ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'r-', linewidth=2, label='Average MSD')
        
        ax.set_xlabel(f"Lag Time ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_statistics(self, ax, msd_results, settings):
        """Plot statistics on given axes"""
        stats_data = msd_results['stats']
        width = stats_data['lag_time'][1] - stats_data['lag_time'][0] if len(stats_data['lag_time']) > 1 else 1
        ax.bar(stats_data['lag_time'], stats_data['count'], width=width)
        
        ax.set_xlabel(f"Lag Time ({settings['time_unit']})")
        ax.set_ylabel("Particle Count")
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_rdc(self, ax, msd_results, dimension, settings):
        """Plot RDC curve on given axes"""
        rdc_data = msd_results['rdc']
        ax.plot(rdc_data['lag_time'], rdc_data['rdc'], 'b-', linewidth=2)
        
        ax.set_xlabel(f"Lag Time ({settings['time_unit']})")
        ylabel = f"RDC ({settings['space_unit']}²/{settings['time_unit']})"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_fitting(self, ax, msd_results, fitting_results, dimension, settings):
        """Plot fitting results on given axes"""
        # Plot experimental data as line with std deviation shading
        avg_msd = msd_results['average']
        lag_time = avg_msd['lag_time']
        msd = avg_msd['msd']
        std = avg_msd.get('std', np.zeros_like(msd))
        
        # Plot mean MSD as line
        ax.plot(lag_time, msd, 'b-', linewidth=1.5, label='Experimental Data')
        # Add standard deviation shading
        ax.fill_between(lag_time, msd - std, msd + std, color='blue', alpha=0.2, label='±STD')
        
        # Plot fitted curve
        fit_times = fitting_results['fit_times']
        fit_msd = fitting_results['fit_msd']
        ax.plot(fit_times, fit_msd, 'r-', linewidth=2, label='Fitted Curve')
        
        # Mark fitting range
        start_idx_array = np.where(lag_time >= fitting_results['start_time'])[0]
        start_idx = start_idx_array[0] if len(start_idx_array) > 0 else 0
        
        if fitting_results['end_time'] < lag_time[-1]:
            end_idx_array = np.where(lag_time >= fitting_results['end_time'])[0]
            end_idx = end_idx_array[0] if len(end_idx_array) > 0 else len(lag_time)-1
        else:
            end_idx = len(lag_time)-1
        
        ax.axvspan(lag_time[start_idx], lag_time[end_idx], 
                  alpha=0.2, color='green', label='Fitting Range')
        
        # Add fitting parameters text
        model_type = settings.get('model_type', 'brownian')
        
        if model_type == 'drift':
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            V_conf = fitting_results.get('V_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"V = {fitting_results.get('V', 0):.4e} [{V_conf[0]:.4e}, {V_conf[1]:.4e}] {settings['space_unit']}/{settings['time_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = f"MSD(t) = {2*dimension}Dt + V²t²"
        elif model_type == 'confined':
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            L_conf = fitting_results.get('L_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"L = {fitting_results.get('L', 0):.4e} [{L_conf[0]:.4e}, {L_conf[1]:.4e}] {settings['space_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = "MSD(t) = L²(1 - exp(-4Dt/L²))"
        else:
            D_conf = fitting_results.get('D_conf_interval', [0, 0])
            
            fit_text = f"D = {fitting_results['D']:.4e} [{D_conf[0]:.4e}, {D_conf[1]:.4e}] {settings['space_unit']}²/{settings['time_unit']}\n"
            fit_text += f"R² = {fitting_results['r_squared']:.4f}"
            equation = f"MSD(t) = {2*dimension}Dt"
        
        fit_text = format_special_chars(fit_text)
        equation = format_special_chars(equation)
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.75, f"Equation: {equation}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(f"Lag Time ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _plot_scaling(self, ax, msd_results, scaling_results, settings):
        """Plot scaling analysis on given axes"""
        # Get average MSD data
        avg_msd = msd_results['average']
        lag_time = avg_msd['lag_time']
        msd = avg_msd['msd']
        std = avg_msd.get('std', np.zeros_like(msd))
        
        # Plot log-log MSD data as line
        ax.loglog(lag_time, msd, 'b-', linewidth=1.5, label='Experimental Data')
        # Add standard deviation shading (ensure positive values for log scale)
        msd_lower = np.maximum(msd - std, msd * 0.01)  # Avoid zero/negative values
        msd_upper = msd + std
        ax.fill_between(lag_time, msd_lower, msd_upper, color='blue', alpha=0.2, label='±STD')
        
        # Plot fitted curve
        fit_times = scaling_results['fit_times']
        fit_msd = scaling_results['fit_msd']
        ax.loglog(fit_times, fit_msd, 'r-', linewidth=2, label='Fitted Curve')
        
        # Add fitting parameters text
        alpha_conf = scaling_results.get('alpha_conf_interval', [0, 0])
        K_conf = scaling_results.get('K_conf_interval', [0, 0])
        
        fit_text = f"α = {scaling_results['alpha']:.4f} [{alpha_conf[0]:.4f}, {alpha_conf[1]:.4f}]\n"
        fit_text += f"K = {scaling_results['K']:.4e} [{K_conf[0]:.4e}, {K_conf[1]:.4e}]\n"
        fit_text += f"R² = {scaling_results['r_squared']:.4f}"
    
        fit_text = format_special_chars(fit_text)
        equation = superscript_alpha("MSD(t) = Kt^α")
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.75, f"Equation: {equation}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add motion type interpretation
        if scaling_results['alpha'] < 0.9:
            motion_type = "Sub-diffusion (α < 0.9)"
        elif scaling_results['alpha'] > 1.1:
            motion_type = "Super-diffusion (α > 1.1)"
        else:
            motion_type = "Normal Diffusion (α ≈ 1)"
            
        ax.text(0.05, 0.6, f"Motion Type: {motion_type}", transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(f"Lag Time ({settings['time_unit']})")
        ylabel = f"MSD ({settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
    def _create_data_table_page(self, pdf, msd_results, fitting_results, scaling_results, settings):
        """Create data table page"""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
        
        plt.axis('off')
        
        # Adjust grid layout
        gs = gridspec.GridSpec(3, 1, height_ratios=[2.2, 1.0, 0.8], hspace=0.1, 
                              top=0.9, bottom=0.02, left=0.1, right=0.9)
        
        # Add main title
        plt.suptitle("Data Analysis Summary", fontsize=16, y=0.98, weight='bold')
        
        # Create MSD data table
        ax1 = plt.subplot(gs[0])
        ax1.axis('off')
        ax1.text(0.5, 1.05, "Average MSD Data (20 samples)", fontsize=12, ha='center', weight='bold')
        
        # Prepare MSD table data
        avg_msd = msd_results['average']
        msd_table_data = []
        
        max_rows = 20
        step = max(1, len(avg_msd['lag_time']) // max_rows)
        
        # Create header
        msd_table_data.append([f"Lag Time ({settings['time_unit']})", 
                              f"MSD ({settings['space_unit']}²)", 
                              f"RDC ({settings['space_unit']}²/{settings['time_unit']})"])
        
        # Add data rows
        rdc_data = msd_results['rdc']
        for i in range(0, len(avg_msd['lag_time']), step):
            if i < len(avg_msd['lag_time']):
                lag_time = avg_msd['lag_time'][i]
                msd_val = avg_msd['msd'][i]
                rdc_val = rdc_data['rdc'][i] if i < len(rdc_data['rdc']) else np.nan
                msd_table_data.append([f"{lag_time:.4f}", f"{msd_val:.6e}", f"{rdc_val:.6e}"])
        
        # Create table
        msd_table = ax1.table(cellText=msd_table_data, loc='center', cellLoc='center')
        msd_table.auto_set_font_size(False)
        msd_table.set_fontsize(9)
        msd_table.scale(1, 1.5)
        
        # Set header style
        for i in range(3):
            msd_table[(0, i)].set_facecolor('#D7E4F5')
            msd_table[(0, i)].set_text_props(weight='bold')

        # Adjust column widths
        msd_table.auto_set_column_width([0, 1, 2])
        col_widths = [0.2, 0.4, 0.4]
        for i, width in enumerate(col_widths):
            for row in range(len(msd_table_data)):
                msd_table[(row, i)].set_width(width)
        
        # Create fitting results table
        ax2 = plt.subplot(gs[1])
        ax2.axis('off')
        ax2.text(0.5, 0.85, "MSD Fitting Results", fontsize=12, ha='center', weight='bold')
        
        # Prepare fitting table data
        fit_table_data = []
        
        # Create header
        fit_table_data.append(["Parameter", "Value", "95% CI", "Unit"])
        
        # Add data rows based on model type
        model_type = settings.get('model_type', 'brownian')
        
        # Basic parameters
        D_conf = fitting_results.get('D_conf_interval', [0, 0])
        D_conf_str = f"[{D_conf[0]:.6e}, {D_conf[1]:.6e}]" if D_conf[0] > 0 else "N/A"
        fit_table_data.append(["Diffusion Coefficient (D)", f"{fitting_results['D']:.6e}", 
                              D_conf_str, f"{settings['space_unit']}²/{settings['time_unit']}"])
        
        # Model-specific parameters
        if model_type == 'drift':
            V_conf = fitting_results.get('V_conf_interval', [0, 0])
            V_conf_str = f"[{V_conf[0]:.6e}, {V_conf[1]:.6e}]" if V_conf[0] > 0 else "N/A"
            fit_table_data.append(["Drift Velocity (V)", f"{fitting_results.get('V', 0):.6e}", 
                                  V_conf_str, f"{settings['space_unit']}/{settings['time_unit']}"])
        elif model_type == 'confined':
            L_conf = fitting_results.get('L_conf_interval', [0, 0])
            L_conf_str = f"[{L_conf[0]:.6e}, {L_conf[1]:.6e}]" if L_conf[0] > 0 else "N/A"
            fit_table_data.append(["Confinement Length (L)", f"{fitting_results.get('L', 0):.6e}", 
                                  L_conf_str, f"{settings['space_unit']}"])
        
        # Common parameters
        fit_table_data.append(["Goodness of Fit (R²)", f"{fitting_results['r_squared']:.6f}", "N/A", ""])
        fit_table_data.append(["Fitting Range", 
                              f"{fitting_results['start_time']:.2f} - {fitting_results['end_time']:.2f}", 
                              "N/A", settings['time_unit']])
        
        # Create table
        fit_table = ax2.table(cellText=fit_table_data, loc='center', cellLoc='center')
        fit_table.auto_set_font_size(False)
        fit_table.set_fontsize(10)
        fit_table.scale(1, 1.8)
        
        # Set header style
        for i in range(4):
            fit_table[(0, i)].set_facecolor('#D7E4F5')
            fit_table[(0, i)].set_text_props(weight='bold')

        # Adjust column widths
        fit_table.auto_set_column_width([0, 1, 2, 3])
        fit_col_widths = [0.2, 0.25, 0.35, 0.2]
        for i, width in enumerate(fit_col_widths):
            for row in range(len(fit_table_data)):
                fit_table[(row, i)].set_width(width)
        
        # Create scaling analysis table
        ax3 = plt.subplot(gs[2])
        ax3.axis('off')
        ax3.text(0.5, 1.00, "Scaling Analysis Results", fontsize=12, ha='center', weight='bold')
        
        # Prepare scaling table data
        scaling_table_data = []
        
        # Create header
        scaling_table_data.append(["Parameter", "Value", "95% CI", "Unit/Note"])

        # Add data rows
        alpha_conf = scaling_results.get('alpha_conf_interval', [0, 0])
        alpha_conf_str = f"[{alpha_conf[0]:.4f}, {alpha_conf[1]:.4f}]" if 'alpha_conf_interval' in scaling_results else "N/A"

        K_conf = scaling_results.get('K_conf_interval', [0, 0])
        K_conf_str = f"[{K_conf[0]:.4e}, {K_conf[1]:.4e}]" if 'K_conf_interval' in scaling_results else "N/A"

        scaling_table_data.append(["Scaling Exponent (α)", f"{scaling_results['alpha']:.6f}", alpha_conf_str, ""])
        scaling_table_data.append(["Prefactor (K)", f"{scaling_results['K']:.6e}", K_conf_str, 
                                  f"{settings['space_unit']}²/{settings['time_unit']}^α"])
        scaling_table_data.append(["Goodness of Fit (R²)", f"{scaling_results['r_squared']:.6f}", "N/A", ""])

        # Add motion type interpretation
        if scaling_results['alpha'] < 0.9:
            motion_type = "Sub-diffusion (α < 0.9)"
        elif scaling_results['alpha'] > 1.1:
            motion_type = "Super-diffusion (α > 1.1)"
        else:
            motion_type = "Normal Diffusion (α ≈ 1)"
        scaling_table_data.append(["Motion Type", motion_type, "N/A", ""])

        # Create table
        scaling_table = ax3.table(cellText=scaling_table_data, loc='center', cellLoc='center')
        scaling_table.auto_set_font_size(False)
        scaling_table.set_fontsize(10)
        scaling_table.scale(1, 1.8)

        # Set header style
        for i in range(4):
            scaling_table[(0, i)].set_facecolor('#D7E4F5')
            scaling_table[(0, i)].set_text_props(weight='bold')
        
        # Adjust column widths
        scaling_table.auto_set_column_width([0, 1, 2, 3])
        scaling_col_widths = [0.2, 0.25, 0.35, 0.2]
        for i, width in enumerate(scaling_col_widths):
            for row in range(len(scaling_table_data)):
                scaling_table[(row, i)].set_width(width)
        
        pdf.savefig(fig)
        plt.close(fig)
