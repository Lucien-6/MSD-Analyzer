"""
MSD Analyzer Plot Widget Module

Provides interactive matplotlib-based plotting widgets for trajectory
and MSD visualization with publication-quality styling.

Author: Lucien
Email: lucien-6@qq.com
"""
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
from mpl_toolkits.mplot3d import Axes3D
# Import custom text processing functions
from utils.text_utils import format_special_chars, superscript_alpha
from utils.helpers import natural_sort_key


class PlotWidget(QWidget):
    """
    Interactive matplotlib plotting widget for MSD analysis visualization.
    
    Supports trajectory plots, MSD curves, RDC plots, and fitting results
    with publication-quality styling using Arial font.
    """
    
    def __init__(self, title="", interactive=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.interactive = interactive
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        
        # Add toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Set up mouse events for interactive plots
        if self.interactive:
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
            self.canvas.mpl_connect('pick_event', self.on_pick)
            
        # Store data
        self.trajectories = None
        self.dimension = None
        self.particle_lines = {}
        self.particle_visibility = {}
        self.start_markers = {}
        self.end_markers = {}
        self.annotation = None
        self.all_visible = True

    def clear(self):
        """Clear the figure"""
        self.figure.clear()
        self.canvas.draw()
        self.particle_lines = {}
        self.particle_visibility = {}
        self.start_markers = {}
        self.end_markers = {}
        
    def plot_trajectories(self, trajectories, dimension, space_unit):
        """
        Plot particle trajectories.
        
        Parameters
        ----------
        trajectories : dict
            Dictionary of trajectory data, keyed by particle ID
        dimension : int
            Trajectory dimension (2 or 3)
        space_unit : str
            Spatial unit for axis labels
        """
        self.trajectories = trajectories
        self.dimension = dimension
        self.figure.clear()
        
        # Create color cycle
        colors = list(mcolors.TABLEAU_COLORS.values())
        
        # Store start and end markers
        self.start_markers = {}
        self.end_markers = {}
        
        # Sort particle IDs naturally
        sorted_particle_ids = sorted(trajectories.keys(), key=natural_sort_key)
        
        if dimension == 2:
            ax = self.figure.add_subplot(111)
            ax.set_title("Particle Trajectories")
            ax.set_xlabel(f"X ({space_unit})")
            ax.set_ylabel(f"Y ({space_unit})")
            # Set equal aspect ratio for 1:1 scale
            ax.set_aspect('equal', adjustable='datalim')
            
            for i, particle_id in enumerate(sorted_particle_ids):
                data = trajectories[particle_id]
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                
                # Plot trajectory line
                line, = ax.plot(x, y, '-', color=color, label=particle_id, 
                            picker=5, alpha=0.7)
                
                # Mark start and end points
                start_marker, = ax.plot(x[0], y[0], '^', color=color, markersize=10)
                end_marker, = ax.plot(x[-1], y[-1], 'o', color=color, markersize=6)
                
                # Store line and marker objects
                self.particle_lines[particle_id] = line
                self.start_markers[particle_id] = start_marker
                self.end_markers[particle_id] = end_marker
                self.particle_visibility[particle_id] = True
                
        elif dimension == 3:
            ax = self.figure.add_subplot(111, projection='3d')
            ax.set_title("Particle Trajectories")
            ax.set_xlabel(f"X ({space_unit})")
            ax.set_ylabel(f"Y ({space_unit})")
            ax.set_zlabel(f"Z ({space_unit})")
            # Set equal aspect ratio for 3D plot
            ax.set_box_aspect([1, 1, 1])
            
            for i, particle_id in enumerate(sorted_particle_ids):
                data = trajectories[particle_id]
                color = colors[i % len(colors)]
                x = data['x'].values
                y = data['y'].values
                z = data['z'].values
                
                # Plot trajectory line
                line, = ax.plot(x, y, z, '-', color=color, label=particle_id, 
                            picker=5, alpha=0.7)
                
                # Mark start and end points
                start_marker, = ax.plot([x[0]], [y[0]], [z[0]], '^', color=color, markersize=10)
                end_marker, = ax.plot([x[-1]], [y[-1]], [z[-1]], 'o', color=color, markersize=6)
                
                # Store line and marker objects
                self.particle_lines[particle_id] = line
                self.start_markers[particle_id] = start_marker
                self.end_markers[particle_id] = end_marker
                self.particle_visibility[particle_id] = True
        
        # Adjust layout (no legend for cleaner appearance)
        self.figure.tight_layout()
        
        # Create annotation for hover display
        self.annotation = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                    textcoords="offset points",
                                    bbox=dict(boxstyle="round", fc="w"),
                                    arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)
        
        self.all_visible = True
        self.canvas.draw()

    def on_mouse_click(self, event):
        """Handle mouse click events"""
        if not self.interactive or not hasattr(self, 'particle_lines') or not self.particle_lines:
            return
            
        # Double left click to restore all trajectories
        if event.dblclick and event.button == 1:
            if not event.inaxes or not hasattr(event, 'artist'):
                self._reset_all_visibility()
                return

    def on_pick(self, event):
        """Handle pick events"""
        artist = event.artist
        
        if isinstance(artist, Line2D):
            particle_id = artist.get_label()
            mouse_event = event.mouseevent
            
            # Left click: show only this trajectory
            if mouse_event.button == 1:
                self._show_only_particle(particle_id)
                
            # Right click: hide this trajectory
            elif mouse_event.button == 3:
                self._hide_particle(particle_id)

    def _show_only_particle(self, particle_id):
        """Show only the specified particle trajectory"""
        if particle_id not in self.particle_lines:
            return
            
        for pid, line in self.particle_lines.items():
            visible = (pid == particle_id)
            line.set_visible(visible)
            
            if pid in self.start_markers:
                self.start_markers[pid].set_visible(visible)
            if pid in self.end_markers:
                self.end_markers[pid].set_visible(visible)
                
            self.particle_visibility[pid] = visible
        
        self.all_visible = False
        self.canvas.draw_idle()

    def _hide_particle(self, particle_id):
        """Hide the specified particle trajectory"""
        if particle_id not in self.particle_lines:
            return
            
        line = self.particle_lines[particle_id]
        line.set_visible(False)
        
        if particle_id in self.start_markers:
            self.start_markers[particle_id].set_visible(False)
        if particle_id in self.end_markers:
            self.end_markers[particle_id].set_visible(False)
            
        self.particle_visibility[particle_id] = False
        
        self.all_visible = False
        self.canvas.draw_idle()

    def _reset_all_visibility(self):
        """Reset all trajectories to visible"""
        for pid, line in self.particle_lines.items():
            line.set_visible(True)
            
            if pid in self.start_markers:
                self.start_markers[pid].set_visible(True)
            if pid in self.end_markers:
                self.end_markers[pid].set_visible(True)
                
            self.particle_visibility[pid] = True
        
        self.all_visible = True
        self.canvas.draw_idle()

    def update_particle_visibility(self, excluded_particle_ids):
        """
        Update trajectory visibility based on exclusion list.
        
        Parameters
        ----------
        excluded_particle_ids : list
            List of particle IDs to exclude (hide)
        """
        if not hasattr(self, 'particle_lines') or not self.particle_lines:
            return
        
        for particle_id, line in self.particle_lines.items():
            should_hide = particle_id in excluded_particle_ids
            
            line.set_visible(not should_hide)
            
            if particle_id in self.start_markers:
                self.start_markers[particle_id].set_visible(not should_hide)
            if particle_id in self.end_markers:
                self.end_markers[particle_id].set_visible(not should_hide)
            
            self.particle_visibility[particle_id] = not should_hide
        
        self.canvas.draw_idle()

    def plot_msd(self, msd_results, time_unit, space_unit):
        """
        Plot MSD curves.
        
        Parameters
        ----------
        msd_results : dict
            MSD calculation results
        time_unit : str
            Time unit for axis labels
        space_unit : str
            Spatial unit for axis labels
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        colors = list(mcolors.TABLEAU_COLORS.values())
        sorted_particle_ids = sorted(msd_results['individual'].keys(), key=natural_sort_key)
        
        # Plot individual MSD curves
        for i, particle_id in enumerate(sorted_particle_ids):
            msd_data = msd_results['individual'][particle_id]
            color = colors[i % len(colors)]
            ax.plot(msd_data['lag_time'], msd_data['msd'], '-', 
                   color=color, alpha=0.5, linewidth=1)
            
        # Plot average MSD
        avg_msd = msd_results['average']
        avg_line, = ax.plot(avg_msd['lag_time'], avg_msd['msd'], 'r-', 
                           linewidth=2, label='Average MSD')
        
        ax.set_title("Mean Squared Displacement (MSD)")
        ax.set_xlabel(f"Lag Time ({time_unit})")
        ylabel = f"MSD ({space_unit}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        
        # No legend for cleaner appearance
        self.figure.tight_layout()
        
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_statistics(self, stats_data, time_unit):
        """
        Plot particle count statistics.
        
        Parameters
        ----------
        stats_data : dict
            Statistics data containing lag_time and count
        time_unit : str
            Time unit for axis labels
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        width = stats_data['lag_time'][1] - stats_data['lag_time'][0] if len(stats_data['lag_time']) > 1 else 1
        ax.bar(stats_data['lag_time'], stats_data['count'], width=width)
        
        ax.set_title("Particle Count per Lag Time")
        ax.set_xlabel(f"Lag Time ({time_unit})")
        ax.set_ylabel("Particle Count")
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_rdc(self, rdc_data, dimension, time_unit, space_unit):
        """
        Plot Running Diffusion Coefficient (RDC) curve.
        
        Parameters
        ----------
        rdc_data : dict
            RDC data containing lag_time and rdc values
        dimension : int
            Trajectory dimension
        time_unit : str
            Time unit for axis labels
        space_unit : str
            Spatial unit for axis labels
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(rdc_data['lag_time'], rdc_data['rdc'], 'b-', linewidth=2)
        
        ax.set_title("Running Diffusion Coefficient (RDC)")
        ax.set_xlabel(f"Lag Time ({time_unit})")
        ylabel = f"RDC ({space_unit}²/{time_unit})"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_fitted_msd(self, msd_results, fitting_results, dimension, fit_settings):
        """
        Plot MSD fitting results.
        
        Parameters
        ----------
        msd_results : dict
            MSD calculation results
        fitting_results : dict
            Fitting results including parameters and curves
        dimension : int
            Trajectory dimension
        fit_settings : dict
            Fitting settings including units
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
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

        fit_text = format_special_chars(fit_text)
        fit_text = superscript_alpha(fit_text)
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=15,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.80, f"Equation: {equation}", transform=ax.transAxes, fontsize=15,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title("MSD Fitting Results")
        ax.set_xlabel(f"Lag Time ({fit_settings['time_unit']})")
        ylabel = f"MSD ({fit_settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def plot_log_log_msd(self, msd_results, scaling_results, fit_settings):
        """
        Plot log-log MSD curve with scaling analysis.
        
        Parameters
        ----------
        msd_results : dict
            MSD calculation results
        scaling_results : dict
            Scaling analysis results
        fit_settings : dict
            Fitting settings including units
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
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
        
        # Mark fitting range
        start_idx_array = np.where(lag_time >= fit_settings['start_time'])[0]
        start_idx = start_idx_array[0] if len(start_idx_array) > 0 else 0
        
        if fit_settings['end_time'] < lag_time[-1]:
            end_idx_array = np.where(lag_time >= fit_settings['end_time'])[0]
            end_idx = end_idx_array[0] if len(end_idx_array) > 0 else len(lag_time)-1
        else:
            end_idx = len(lag_time)-1
            
        ax.axvspan(lag_time[start_idx], lag_time[end_idx], 
                  alpha=0.2, color='green', label='Fitting Range')
        
        # Add fitting parameters text
        alpha_err = scaling_results['alpha_err']
        K_err = scaling_results['K_err']
        fit_text = f"α = {scaling_results['alpha']:.4f} ± {alpha_err:.4f}\n"
        fit_text += f"K = {scaling_results['K']:.4e} ± {K_err:.4e}\n"
        fit_text += f"R² = {scaling_results['r_squared']:.4f}"
        
        fit_text = format_special_chars(fit_text)
        equation = superscript_alpha("MSD(t) = Kt^α")
            
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=15,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.05, 0.80, f"Equation: {equation}", transform=ax.transAxes, fontsize=15,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add diffusion type interpretation
        alpha = scaling_results['alpha']
        if alpha < 0.9:
            interpretation = "Sub-diffusion"
        elif 0.9 <= alpha <= 1.1:
            interpretation = "Normal Diffusion"
        else:
            interpretation = "Super-diffusion"
            
        ax.text(0.05, 0.72, f"Diffusion Type: {interpretation}", transform=ax.transAxes, fontsize=15,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title("Log-Log MSD Curve and Scaling Analysis")
        ax.set_xlabel(f"Lag Time ({fit_settings['time_unit']})")
        ylabel = f"MSD ({fit_settings['space_unit']}²)"
        ax.set_ylabel(format_special_chars(ylabel))
        
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas.draw()
        
    def on_mouse_move(self, event):
        """Handle mouse move events for hover display"""
        if not self.interactive or not hasattr(self, 'annotation') or not self.annotation:
            return
            
        if event.inaxes:
            xmin, xmax = event.inaxes.get_xlim()
            ymin, ymax = event.inaxes.get_ylim()
            
            threshold = min(abs(xmax - xmin), abs(ymax - ymin)) * 0.01
            
            closest_line = None
            closest_dist = float('inf')
            closest_id = None
            
            for particle_id, line in self.particle_lines.items():
                if not self.particle_visibility[particle_id]:
                    continue
                    
                if self.dimension == 2:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    
                    for i in range(len(xdata)-1):
                        x1, y1 = xdata[i], ydata[i]
                        x2, y2 = xdata[i+1], ydata[i+1]
                        
                        dist = self._point_to_segment_dist(event.xdata, event.ydata, x1, y1, x2, y2)
                        
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_line = line
                            closest_id = particle_id
                
                elif self.dimension == 3:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    
                    for i in range(len(xdata)):
                        dist = np.sqrt((event.xdata - xdata[i])**2 + (event.ydata - ydata[i])**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_line = line
                            closest_id = particle_id
            
            if closest_line and closest_dist < threshold:
                self.annotation.xy = (event.xdata, event.ydata)
                self.annotation.set_text(f"Particle ID: {closest_id}")
                self.annotation.set_visible(True)
                self.canvas.draw_idle()
            else:
                if self.annotation.get_visible():
                    self.annotation.set_visible(False)
                    self.canvas.draw_idle()
    
    def _toggle_particle_visibility(self, particle_id):
        """Toggle particle trajectory visibility"""
        if particle_id in self.particle_lines:
            line = self.particle_lines[particle_id]
            visible = not line.get_visible()
            line.set_visible(visible)
            self.particle_visibility[particle_id] = visible
            
            for text in line.axes.get_legend().get_texts():
                if hasattr(text, 'particle_id') and text.particle_id == particle_id:
                    if visible:
                        text.set_alpha(1.0)
                    else:
                        text.set_alpha(0.3)
            
            self.canvas.draw_idle()
    
    def _point_to_segment_dist(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        l2 = (x2 - x1)**2 + (y2 - y1)**2
        
        if l2 == 0:
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)
    
    def save_figure(self, filename):
        """Save figure to file"""
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')
        return filename
