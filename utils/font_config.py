import matplotlib
import matplotlib.font_manager as fm
import platform
import os
import warnings

# 忽略字体相关警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def configure_fonts():
    """配置matplotlib字体系统，确保中文和特殊字符正确显示"""
    system = platform.system()
    
    # 创建字体列表，优先使用支持数学符号和中文的字体
    font_list = []
    
    if system == 'Windows':
        # Windows系统字体优先级
        font_list = [
            'Microsoft YaHei',  # 微软雅黑，支持中文
            'SimSun',           # 宋体
            'Arial Unicode MS', # 支持广泛的Unicode字符
            'DejaVu Sans',      # 良好支持数学符号
            'Segoe UI Symbol',  # Windows符号字体
            'Arial',
            'Helvetica'
        ]
    elif system == 'Darwin':  # macOS
        font_list = [
            'PingFang SC',      # 苹方，macOS上的中文字体
            'Heiti SC',         # 黑体-简
            'Apple SD Gothic Neo',
            'Hiragino Sans GB',
            'Arial Unicode MS',
            'Helvetica'
        ]
    else:  # Linux和其他系统
        font_list = [
            'Noto Sans CJK SC', # Google Noto字体，支持中文
            'WenQuanYi Micro Hei',
            'DejaVu Sans',
            'Liberation Sans',
            'FreeSans',
            'Ubuntu'
        ]
    
    # 添加通用备选字体
    font_list.extend(['DejaVu Sans', 'STIXGeneral', 'STIX', 'XITS', 'FreeSans'])
    
    # 过滤出系统中实际存在的字体
    available_fonts = []
    system_fonts = set([f.name for f in fm.fontManager.ttflist])
    
    for font in font_list:
        if font in system_fonts:
            available_fonts.append(font)
            
    if not available_fonts:
        # 如果没有找到任何指定字体，使用系统默认字体
        available_fonts = ['sans-serif']
    
    # 配置matplotlib字体
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = available_fonts
    
    # 启用Unicode负号
    matplotlib.rcParams['axes.unicode_minus'] = True
    
    # 配置数学文本
    matplotlib.rcParams['mathtext.fontset'] = 'stix'  # 使用STIX字体集，更好地支持数学符号
    # 设置数学字体为正体，解决μm中μ与m字体不一致的问题
    matplotlib.rcParams['mathtext.default'] = 'regular'
    
    # 使用数学文本渲染特殊字符
    matplotlib.rcParams['text.usetex'] = False  # 不使用LaTeX，避免依赖问题
    
    # print(f"当前字体配置: {available_fonts}，建议安装DejaVu Sans字体，以支持数学符号和中文。")
    
    # 返回可用字体列表，以便其他地方使用
    return available_fonts