"""
MSD Analyzer Font Configuration Module

Configures matplotlib fonts for publication-quality figures.
Uses Arial as the primary font with proper size hierarchy.

Author: Lucien
Email: lucien-6@qq.com
"""
import matplotlib
import matplotlib.font_manager as fm
import platform
import warnings

# Ignore font-related warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


def configure_fonts():
    """
    Configure matplotlib font system for publication-quality figures.
    
    Font hierarchy (following top-tier journal standards):
    - Title: 14pt, Bold
    - Axis labels: 12pt, Normal
    - Tick labels: 10pt, Normal
    - Legend: 10pt, Normal
    - Legend title: 11pt, Normal
    
    Returns
    -------
    list
        List of available fonts in priority order
    """
    system = platform.system()
    
    # Font priority list - Arial first for publication quality
    font_list = []
    
    if system == 'Windows':
        font_list = [
            'Arial',            # Primary font for publications
            'Helvetica',        # Alternative sans-serif
            'DejaVu Sans',      # Good math symbol support
            'Segoe UI',         # Windows system font
            'Microsoft YaHei',  # Chinese support fallback
            'SimSun',           # Chinese support fallback
        ]
    elif system == 'Darwin':  # macOS
        font_list = [
            'Arial',
            'Helvetica',
            'Helvetica Neue',
            'DejaVu Sans',
            'PingFang SC',      # Chinese support fallback
        ]
    else:  # Linux and other systems
        font_list = [
            'Arial',
            'DejaVu Sans',
            'Liberation Sans',
            'FreeSans',
            'Noto Sans',
            'Noto Sans CJK SC',  # Chinese support fallback
        ]
    
    # Add universal fallback fonts
    font_list.extend(['DejaVu Sans', 'STIXGeneral', 'FreeSans'])
    
    # Filter to fonts actually available on the system
    available_fonts = []
    system_fonts = set([f.name for f in fm.fontManager.ttflist])
    
    for font in font_list:
        if font in system_fonts:
            available_fonts.append(font)
            
    if not available_fonts:
        available_fonts = ['sans-serif']
    
    # ==========================================
    # Font Family Configuration
    # ==========================================
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = available_fonts
    
    # ==========================================
    # Font Size Hierarchy (Top-tier Journal Standards, +50% for GUI display)
    # ==========================================
    # Title: 21pt (14 * 1.5), Bold
    matplotlib.rcParams['axes.titlesize'] = 21
    matplotlib.rcParams['axes.titleweight'] = 'bold'
    matplotlib.rcParams['figure.titlesize'] = 24
    matplotlib.rcParams['figure.titleweight'] = 'bold'
    
    # Axis labels: 18pt (12 * 1.5)
    matplotlib.rcParams['axes.labelsize'] = 18
    matplotlib.rcParams['axes.labelweight'] = 'normal'
    
    # Tick labels: 15pt (10 * 1.5)
    matplotlib.rcParams['xtick.labelsize'] = 15
    matplotlib.rcParams['ytick.labelsize'] = 15
    
    # Legend: 15pt (10 * 1.5), title 17pt (11 * 1.5)
    matplotlib.rcParams['legend.fontsize'] = 15
    matplotlib.rcParams['legend.title_fontsize'] = 17
    
    # ==========================================
    # Line and Axis Style (Publication Quality)
    # ==========================================
    matplotlib.rcParams['lines.linewidth'] = 1.5
    matplotlib.rcParams['axes.linewidth'] = 1.2
    matplotlib.rcParams['xtick.major.width'] = 1.0
    matplotlib.rcParams['ytick.major.width'] = 1.0
    matplotlib.rcParams['xtick.minor.width'] = 0.8
    matplotlib.rcParams['ytick.minor.width'] = 0.8
    matplotlib.rcParams['xtick.major.size'] = 5
    matplotlib.rcParams['ytick.major.size'] = 5
    matplotlib.rcParams['xtick.minor.size'] = 3
    matplotlib.rcParams['ytick.minor.size'] = 3
    matplotlib.rcParams['xtick.direction'] = 'in'
    matplotlib.rcParams['ytick.direction'] = 'in'
    
    # ==========================================
    # Grid Style
    # ==========================================
    matplotlib.rcParams['grid.linewidth'] = 0.8
    matplotlib.rcParams['grid.alpha'] = 0.5
    
    # ==========================================
    # Figure and Subplot
    # ==========================================
    matplotlib.rcParams['figure.dpi'] = 100
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['savefig.bbox'] = 'tight'
    matplotlib.rcParams['savefig.pad_inches'] = 0.1
    
    # ==========================================
    # Math Text Configuration
    # ==========================================
    matplotlib.rcParams['axes.unicode_minus'] = True
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['mathtext.default'] = 'regular'
    matplotlib.rcParams['text.usetex'] = False
    
    return available_fonts
