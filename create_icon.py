import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import os
from PIL import Image
import numpy as np
from matplotlib.patheffects import withStroke
import matplotlib.patheffects as path_effects

# 设置matplotlib使用Agg后端，避免GUI依赖
matplotlib.use('Agg')

def create_einstein_stokes_icon():
    # 创建一个白色背景的图像，增大尺寸以获得更好的分辨率
    fig = plt.figure(figsize=(8, 8), facecolor='white')
    ax = fig.add_subplot(111)
    
    # 设置坐标轴不可见
    ax.axis('off')
    
    # 设置白色背景
    ax.set_facecolor('none')
    
    # 创建更鲜艳的圆形设计
    # 外圆 - 使用更鲜艳的渐变色填充
    theta = np.linspace(0, 2*np.pi, 100)
    r = 0.45  # 稍微增大半径
    
    # 创建渐变填充的圆 - 使用更鲜艳的蓝色到紫色渐变
    for i in range(40, 0, -1):
        scale = i/40.0
        # 使用更鲜艳的颜色：从亮蓝色(#1E88E5)到紫色(#8E24AA)
        red = int(30 + (142-30) * (1-scale))
        green = int(136 + (36-136) * (1-scale))
        blue = int(229 + (170-229) * (1-scale))
        circle = plt.Circle((0.5, 0.5), r*scale, 
                           color=f'#{red:02x}{green:02x}{blue:02x}', 
                           alpha=0.08, linewidth=0)  # 增加透明度使渐变更明显
        ax.add_patch(circle)
    
    # 添加发光效果的外圆边框
    for i in range(3):
        offset = 3-i
        circle_glow = plt.Circle((0.5, 0.5), r+0.01*offset, fill=False, 
                               color='#3498db', linewidth=1.5, alpha=0.3*(3-i)/3)
        ax.add_patch(circle_glow)
    
    # 添加外圆边框 - 使用更鲜艳的蓝色
    circle_outer = plt.Circle((0.5, 0.5), r, fill=False, 
                             color='#1E88E5', linewidth=4, 
                             path_effects=[path_effects.withSimplePatchShadow(
                                 offset=(2, -2), shadow_rgbFace='#bdc3c7', alpha=0.5)])
    ax.add_patch(circle_outer)
    
    # 添加内圆边框 - 使用更鲜艳的紫蓝色
    circle_inner = plt.Circle((0.5, 0.5), r*0.85, fill=False, 
                             color='#5E35B1', linewidth=2.5)
    ax.add_patch(circle_inner)
    
    # 为方程式添加发光背景，使其更突出
    glow_circle = plt.Circle((0.5, 0.5), r*0.5, color='white', alpha=0.7)
    ax.add_patch(glow_circle)
    
    # 添加爱因斯坦-斯托克斯方程 - 增大字体
    equation = r'$D = \frac{k_B T}{6\pi\eta r}$'
    
    # 在图中添加方程，居中放置，增大字体并添加更明显的阴影效果
    text = ax.text(0.5, 0.5, equation, fontsize=72, ha='center', va='center', 
                  color='#1A237E', fontweight='bold', 
                  path_effects=[
                      path_effects.withStroke(linewidth=2, foreground='white'),
                      path_effects.withSimplePatchShadow(
                          offset=(3, -3), shadow_rgbFace='#bdc3c7', alpha=0.5)
                  ])
    
    # 设置图像边界
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    
    # 保存为PNG文件，增加DPI以获得更高分辨率
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
    plt.savefig(png_path, dpi=600, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close()
    
    # 将PNG转换为ICO文件
    img = Image.open(png_path)
    
    # 创建正方形图像（ICO需要）
    width, height = img.size
    size = max(width, height)
    square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # 将原图粘贴到正方形图像中央
    paste_x = (size - width) // 2
    paste_y = (size - height) // 2
    square_img.paste(img, (paste_x, paste_y))
    
    # 创建不同尺寸的图标
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    
    # 保存为ICO文件
    square_img.save(ico_path, format='ICO', sizes=icon_sizes)
    
    # print(f"图标已创建并保存为: {ico_path}")
    return ico_path

if __name__ == "__main__":
    create_einstein_stokes_icon()