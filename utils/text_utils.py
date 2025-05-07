def format_special_chars(text):
    """
    处理特殊字符，将其转换为matplotlib可以正确显示的格式
    
    Args:
        text: 包含特殊字符的文本
        
    Returns:
        处理后的文本
    """
    # 替换常见的特殊字符为数学表达式
    replacements = {
        '²': '$^2$',
        '³': '$^3$',
        'α': r'$\alpha$',
        'β': r'$\beta$',
        'γ': r'$\gamma$',
        'μ': r'$\mu$',
        'σ': r'$\sigma$',
        '±': r'$\pm$',
        '°': r'$^\circ$'
    }
    
    # 先处理特殊单位组合
    unit_replacements = {
        'μm': r'$\mu$m',  # 使μ和m在同一数学环境中但保持m为正常字体
    }
    
    for unit, replacement in unit_replacements.items():
        text = text.replace(unit, replacement)
    
    # 再处理单个特殊字符
    for char, replacement in replacements.items():
        # 避免重复替换已经处理过的单位中的字符
        if char == 'μ' and 'μm' in text:
            continue
        text = text.replace(char, replacement)
    
    return text

def superscript_alpha(text):
    """
    将文本中的 ^α 转换为上标α
    
    Args:
        text: 包含 ^α 的文本
        
    Returns:
        处理后的文本，^α 被转换为上标α
    """
    return text.replace('^α', r'$^{\alpha}$')