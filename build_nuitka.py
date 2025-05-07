import os
import shutil
import subprocess
import sys

def build_executable():
    print("开始使用Nuitka打包MSD Analyzer...")
    
    # 确保当前目录是项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 删除之前的构建文件夹
    if os.path.exists('nuitka_build'):
        print("删除旧的nuitka_build文件夹...")
        shutil.rmtree('nuitka_build')
    
    # 使用Nuitka打包
    print("使用Nuitka打包应用...")
    
    # 构建命令
    cmd = [
        'python', '-m', 'nuitka',
        '--standalone',                  
        '--follow-imports',              
        '--include-package=core',        
        '--include-package=gui',         
        '--include-package=utils',       
        '--include-package=PyQt5',       
        '--include-package=numpy',       
        '--include-package=pandas',      
        '--include-package=scipy',       
        '--include-package=matplotlib',  
        '--mingw64',                     
        '--output-dir=nuitka_build',     
        '--show-progress',               
        '--enable-plugin=pyqt5',         
        '--nofollow-import-to=tkinter',  
        '--windows-icon-from-ico=icon.ico',  # 修改后的参数名称  
        'main.py'                        
    ]
    
    result = subprocess.run(cmd, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    if result.returncode != 0:
        print("打包失败！错误信息:")
        print(result.stderr)
        return False
    
    print("打包完成！可执行文件位于 nuitka_build 文件夹中")
    print("现在您可以将 main.exe 移动到任何位置运行")
    
    # 重命名可执行文件为更友好的名称
    try:
        os.rename(
            os.path.join('nuitka_build', 'main.exe'),
            os.path.join('nuitka_build', 'MSD Analyzer.exe')
        )
        print("已将可执行文件重命名为 'MSD Analyzer.exe'")
    except Exception as e:
        print(f"重命名可执行文件失败: {e}")
    
    return True

# ... existing code ...

if __name__ == "__main__":
    # 检查并安装必要的依赖
    print("检查并安装必要的依赖...")
    dependencies = [
        'nuitka',
        'ordered-set',  # Nuitka的依赖
        'zstandard',    # Nuitka的依赖
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
    
    # 检查Nuitka版本
    try:
        result = subprocess.run(['python', '-m', 'nuitka', '--version'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
        if result.returncode == 0:
            print(f"检测到Nuitka版本: {result.stdout.strip()}")
        else:
            raise ImportError("无法获取Nuitka版本")
    except (ImportError, subprocess.SubprocessError):
        print("Nuitka安装可能有问题，请检查安装状态")
        sys.exit(1)
    
    success = build_executable()
    if success:
        print("\n您可以通过运行 nuitka_build/MSD Analyzer.exe 来启动应用")
    sys.exit(0 if success else 1)