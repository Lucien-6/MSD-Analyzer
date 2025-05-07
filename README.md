# MSD Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

MSD Analyzer 是一款用于分析均方位移 (Mean Squared Displacement, MSD) 数据的桌面应用程序。它提供了友好的图形用户界面，帮助用户导入、处理、可视化 MSD 数据，并可能包含相关的物理模型拟合与参数提取功能。

## 📜 目录

- [MSD Analyzer](#msd-analyzer)
  - [📜 目录](#-目录)
  - [🚀 主要功能](#-主要功能)
  - [✨ 截图](#-截图)
  - [🛠️ 技术栈](#️-技术栈)
  - [⚙️ 安装](#️-安装)
  - [▶️ 运行](#️-运行)
  - [📖 使用方法](#-使用方法)
  - [🚀 发布与打包](#-发布与打包)
  - [🤝 如何贡献](#-如何贡献)
  - [📄 许可证](#-许可证)

## 🚀 主要功能

- **数据导入**: 支持从常见数据格式（如 .csv, .xlsx）导入 MSD 数据。
- **数据处理**: 提供数据清洗、筛选和预处理选项。
- **可视化**: 使用 `matplotlib` 生成 MSD 曲线图，支持自定义绘图参数。
- **分析与拟合**: (推测) 可能包含对 MSD 曲线进行线性或非线性拟合，提取扩散系数等物理参数。
- **报告生成**: (推测基于 `reportlab`) 可能支持将分析结果导出为 PDF 报告。
- **Excel 导出**: (推测基于 `xlsxwriter` 和 `openpyxl`) 支持将处理后的数据或结果导出到 Excel 文件。
- **用户友好的 GUI**: 基于 `PyQt5` 构建，操作直观。

## 🛠️ 技术栈

- **Python 3.10+**
- **GUI**: `PyQt5`
- **数据处理与分析**: `numpy`, `pandas`, `scipy`
- **绘图**: `matplotlib`
- **Excel 操作**: `openpyxl`, `xlsxwriter`
- **PDF 报告**: `reportlab`

## ⚙️ 安装

1.  **克隆仓库**

    ```bash
    git clone <your-repository-url>
    cd MSD-Analyzer
    ```

    _(请将 `<your-repository-url>` 替换为您的实际仓库 URL，并将 `MSD-Analyzer` 替换为您的项目文件夹名称，如果不同)_

2.  **创建并激活虚拟环境 (推荐)**

    **首选方式：使用 Conda**

    ```bash
    # 创建新的 conda 环境 (例如，命名为 msd_env，使用 Python 3.10)
    conda create -n msd_env python=3.10
    # 激活环境
    conda activate msd_env
    ```

    **备选方式：使用 venv**

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ 运行

安装完依赖后，通过以下命令运行应用程序：

```bash
python main.py
```

应用程序启动后，会显示欢迎信息。根据提示，您可以 "双击'单位设置'查看使用指南" 以获取更详细的操作说明。

## 📖 使用方法

详细的使用指南请参见应用内的 "单位设置" 部分或相关帮助文档（如果提供）。

基本流程通常包括：

1.  启动应用程序。
2.  通过菜单栏或工具栏导入您的 MSD 数据文件。
3.  根据需要进行数据单位设置或预处理。
4.  查看生成的 MSD 曲线图。
5.  使用分析工具（如拟合功能）提取参数。
6.  导出结果或报告。

## 🚀 发布与打包

### 推荐：从 Releases 下载

为了方便使用，建议直接从本项目的 GitHub Releases 页面下载最新版本的预编译可执行文件。

➡️ **[前往 Releases 页面](<your-repository-url>/releases)**

_(请将 `<your-repository-url>` 替换为您的实际仓库 URL)_

下载后解压（如果需要），即可直接运行，无需安装 Python 或其他依赖。

### 从源码打包 (可选)

如果您希望自行从源代码构建可执行文件，可以按照以下步骤操作：

1.  确保您已经按照 [⚙️ 安装](#️-安装) 部分的说明设置好了开发环境并安装了所有依赖。
2.  确保您的系统中安装了 `PyInstaller`。如果未安装，可以通过 `pip install pyinstaller` 安装。
3.  在项目根目录下运行打包脚本：

    ```bash
    python build_exe.py
    ```

4.  打包成功后，可执行文件将位于项目根目录下的 `dist` 文件夹内 (通常是 `dist/MSD Analyzer/MSD Analyzer.exe` 或类似路径)。

## 🤝 如何贡献

本项目采用 [MIT 许可证](LICENSE)授权。
