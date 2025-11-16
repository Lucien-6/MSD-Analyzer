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
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        return False
    
    print("打包完成！可执行文件位于 dist 文件夹中")
    print("现在您可以将 MSD Analyzer.exe 移动到任何位置运行")
    return True

if __name__ == "__main__":
    # 检查并安装必要的依赖
    print("检查并安装必要的依赖...")
    dependencies = [
        'pyinstaller',
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', dep],
                         check=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
            print(f"已安装/更新 {dep}")
        except subprocess.CalledProcessError as e:
            print(f"安装 {dep} 失败: {e}")
            sys.exit(1)
    
    # 检查PyInstaller版本
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
        if result.returncode == 0:
            print(f"检测到PyInstaller版本: {result.stdout.strip()}")
        else:
            raise ImportError("无法获取PyInstaller版本")
    except (ImportError, subprocess.SubprocessError):
        print("PyInstaller安装可能有问题，请检查安装状态")
        sys.exit(1)
    
    success = build_executable()
    if success:
        print("\n您可以通过运行 dist/MSD Analyzer.exe 来启动应用")
    sys.exit(0 if success else 1)