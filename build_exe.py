import os
import shutil
import subprocess
import sys

def build_executable():
    print("开始打包MSD Analyzer...")
    
    # 确保当前目录是项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 删除之前的构建文件夹
    if os.path.exists('build'):
        print("删除旧的build文件夹...")
        shutil.rmtree('build')
    if os.path.exists('dist'):
        print("删除旧的dist文件夹...")
        shutil.rmtree('dist')
    
    # 使用PyInstaller打包
    print("使用PyInstaller打包应用...")
    result = subprocess.run(['pyinstaller', 'msd_analyzer.spec'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    if result.returncode != 0:
        print("打包失败！错误信息:")
        print(result.stderr)
        return False
    
    print("打包完成！可执行文件位于 dist 文件夹中")
    print("现在您可以将 MSD Analyzer.exe 移动到任何位置运行")
    return True

if __name__ == "__main__":
    success = build_executable()
    if success:
        print("\n您可以通过运行 dist/MSD Analyzer.exe 来启动应用")
    sys.exit(0 if success else 1)