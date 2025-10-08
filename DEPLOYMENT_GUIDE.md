# 打包与部署详细指南 (Deployment Guide)

本文档详细说明了如何将 Waifu2x-GUI 这个 PySide6 桌面应用打包成独立的可执行文件并部署给最终用户。

---

## 目录

1. [打包概述](#打包概述)
2. [环境准备](#环境准备)
3. [PyInstaller 打包详解](#pyinstaller-打包详解)
4. [依赖处理与问题解决](#依赖处理与问题解决)
5. [自动化打包流程](#自动化打包流程)
6. [发布与分发](#发布与分发)

---

## 打包概述

### 什么是打包？

打包是将 Python 源代码和所有运行时依赖（包括 Python 解释器、第三方库、资源文件等）整合成一个独立的可执行文件或文件夹的过程。这样用户无需安装 Python 环境即可直接运行应用程序。

### 本项目的打包目标

- **输入**: Python 源代码 + PySide6 GUI + waifu2x-vulkan 引擎 + 图片资源
- **输出**: 独立的 `.exe` 可执行文件（Windows）或对应平台的可执行程序
- **用户体验**: 双击即可运行，无需任何配置

---

## 环境准备

### 1. 安装依赖

首先确保所有项目依赖已安装：

```bash
# 激活虚拟环境（推荐）
.\venv\Scripts\activate

# 安装项目依赖
pip install -r requirements.txt
```

**requirements.txt 内容**:
```
PySide6==6.1.3
pillow==8.3.2
waifu2x-vulkan==1.1.1
```

### 2. 安装 PyInstaller

```bash
pip install pyinstaller
```

PyInstaller 是 Python 最流行的打包工具，支持 Windows、macOS、Linux 多平台。

---

## PyInstaller 打包详解

### 基础打包命令

#### 最简单的打包方式

```bash
pyinstaller start.py
```

这会生成：
- `build/` 文件夹：临时构建文件
- `dist/` 文件夹：包含可执行文件的目录
- `start.spec` 文件：打包配置文件

#### 常用打包选项

```bash
# -F: 打包成单个 exe 文件
# -w: 无控制台窗口（GUI 应用）
# -n: 指定输出文件名
pyinstaller -F -w -n "Waifu2x-GUI" start.py
```

**参数说明**:

| 参数 | 说明 | 适用场景 |
|------|------|----------|
| `-F` / `--onefile` | 打包成单个 exe 文件 | 方便分发，但启动稍慢 |
| `-D` / `--onedir` | 打包成文件夹（默认） | 启动快，文件多 |
| `-w` / `--windowed` | 不显示控制台窗口 | GUI 应用 |
| `-c` / `--console` | 显示控制台窗口（默认） | 调试用，可看到错误信息 |
| `-n NAME` | 指定输出文件名 | 自定义应用名称 |
| `--icon=icon.ico` | 设置应用图标 | 美化应用 |

### 本项目的打包策略

#### Windows 打包（生产环境）

```bash
# 第一步：生成带控制台的调试版本
pyinstaller -F start.py
mv dist/start.exe "dist/start(debug).exe"

# 第二步：生成无控制台的发布版本
pyinstaller -F -w start.py
```

**为什么要两个版本？**
- **调试版本** (`start(debug).exe`): 显示控制台，用户遇到问题时可以看到错误信息
- **发布版本** (`start.exe`): 无控制台，用户体验更好

#### macOS 打包

```bash
pyinstaller --clean --onedir --name Waifu2x-demo \
    --hidden-import waifu2x_vulkan \
    --hidden-import PySide6 \
    --hidden-import conf \
    --hidden-import src \
    --hidden-import src.qt \
    --hidden-import src.qt.com \
    --hidden-import src.qt.menu \
    --hidden-import src.qt.util\
    --hidden-import src.util \
    --hidden-import ui \
    --strip --windowed \
    start.py
```

**macOS 特殊处理**:
- 使用 `--onedir` 而非 `-F`，因为 macOS 应用通常是 `.app` 包
- 需要明确指定所有隐藏导入的模块
- 使用 `--strip` 减小文件大小

---

## 依赖处理与问题解决

### 1. 隐藏导入 (Hidden Imports)

#### 问题描述

PyInstaller 通过静态分析代码来查找依赖，但某些动态导入的模块无法被检测到，导致打包后运行时报错：

```python
ModuleNotFoundError: No module named 'xxx'
```

#### 解决方案

使用 `--hidden-import` 参数明确指定：

```bash
pyinstaller -F -w \
    --hidden-import waifu2x_vulkan \
    --hidden-import PySide6 \
    --hidden-import conf \
    --hidden-import src \
    start.py
```

**本项目需要的隐藏导入**:
- `waifu2x_vulkan`: 图像处理引擎
- `PySide6`: Qt GUI 框架
- `conf`: 配置模块
- `src.*`: 所有业务逻辑模块
- `ui`: UI 定义文件

### 2. 资源文件处理

#### 问题描述

图片、图标、配置文件等资源需要被打包进 exe 中。

#### 解决方案 1: 使用 Qt 资源系统

本项目使用了 Qt 的资源编译系统：

```python
# images_rc.py 是通过 pyside6-rcc 编译生成的
import images_rc
```

**生成资源文件**:
```bash
# 从 .qrc 文件生成 Python 模块
pyside6-rcc resources.qrc -o images_rc.py
```

这样图片资源会被编译进 Python 代码，PyInstaller 会自动打包。

#### 解决方案 2: 使用 --add-data

对于其他资源文件：

```bash
# Windows
pyinstaller -F -w --add-data "conf;conf" --add-data "images;images" start.py

# Linux/macOS
pyinstaller -F -w --add-data "conf:conf" --add-data "images:images" start.py
```

### 3. DLL 依赖问题

#### 问题描述

某些库（如 waifu2x-vulkan）依赖 C++ 动态链接库，PyInstaller 可能无法自动找到。

#### 解决方案: 使用 .spec 文件

创建或修改 `Waifu2x-GUI.spec` 文件：

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start.py'],
    pathex=[],
    binaries=[
        # 手动添加 DLL 文件
        ('path/to/waifu2x.dll', '.'),
        ('path/to/vulkan-1.dll', '.'),
    ],
    datas=[
        # 添加数据文件
        ('conf', 'conf'),
        ('images_rc.py', '.'),
    ],
    hiddenimports=[
        'waifu2x_vulkan',
        'PySide6',
        'conf',
        'src',
        'src.qt',
        'src.qt.com',
        'src.qt.menu',
        'src.qt.util',
        'src.util',
        'ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='start',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 应用图标
)
```

**使用 .spec 文件打包**:
```bash
pyinstaller Waifu2x-GUI.spec
```

### 4. 常见错误与解决

#### 错误 1: 找不到 PySide6 插件

```
This application failed to start because no Qt platform plugin could be initialized.
```

**解决方案**:
```python
# 在 start.py 中添加
import os
import sys
from PySide6 import QtWidgets

if hasattr(sys, '_MEIPASS'):
    # PyInstaller 打包后的临时目录
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
```

#### 错误 2: 图片资源加载失败

**解决方案**: 确保导入了资源模块
```python
import images_rc  # 必须导入
```

#### 错误 3: waifu2x_vulkan 初始化失败

**解决方案**: 检查 Vulkan 驱动和 GPU 支持
```python
try:
    from waifu2x_vulkan import waifu2x_vulkan
    config.CanWaifu2x = True
except Exception as es:
    config.CanWaifu2x = False
    config.ErrorMsg = str(es)
```

---

## 自动化打包流程

### GitHub Actions CI/CD

本项目使用 GitHub Actions 实现自动化打包和发布。

#### 工作流配置 (`.github/workflows/release.yml`)

```yaml
name: release
on:
  push:
    tags:
      - '*'  # 当推送 tag 时触发

jobs:
  windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python 3.7
      uses: actions/setup-python@v2
      with:
        python-version: 3.7
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        pip install -r requirements.txt
    
    - name: Build
      run: |
        # 生成调试版本
        pyinstaller -F start.py
        mv dist/start.exe "dist/start(debug).exe"
        
        # 生成发布版本
        pyinstaller -F -w start.py
        
        # 整理发布文件
        mv dist waifu2x-demo
        cp LICENSE waifu2x-demo\
        cp README.md waifu2x-demo\
        
        # 压缩
        7z a -r "waifu2x-demo_windows_x64.zip" "waifu2x-demo"
    
    - name: Upload Release
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ needs.release.outputs.Up_Url }}
        asset_path: waifu2x-demo_windows_x64.zip
        asset_name: waifu2x-demo_windows_x64.zip
        asset_content_type: application/zip
```

#### 触发自动打包

```bash
# 创建并推送 tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions 会自动：
# 1. 在 Windows/macOS/Linux 环境中打包
# 2. 创建 GitHub Release
# 3. 上传打包文件
```

### 本地打包脚本

创建 `build.bat` (Windows):

```batch
@echo off
echo ========================================
echo Waifu2x-GUI 打包脚本
echo ========================================

echo.
echo [1/4] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo [2/4] 打包调试版本（带控制台）...
pyinstaller -F start.py
if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)
move dist\start.exe dist\start_debug.exe

echo.
echo [3/4] 打包发布版本（无控制台）...
pyinstaller -F -w start.py
if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo [4/4] 整理发布文件...
mkdir waifu2x-demo
move dist\*.exe waifu2x-demo\
copy README.md waifu2x-demo\
copy LICENSE waifu2x-demo\

echo.
echo ========================================
echo 打包完成！
echo 输出目录: waifu2x-demo\
echo ========================================
pause
```

---

## 发布与分发

### 1. 准备发布包

发布包应包含：

```
waifu2x-demo/
├── start.exe           # 主程序（无控制台）
├── start(debug).exe    # 调试版本（带控制台）
├── README.md           # 使用说明
└── LICENSE             # 许可证
```

### 2. 编写用户文档

在 `README.md` 中说明：

```markdown
# Waifu2x-GUI

基于 Waifu2x-ncnn 的图像超分辨率桌面应用

## 功能特性

- 图像超分辨率处理（放大）
- 图像降噪
- 批量处理
- 支持多种图片格式

## 使用方法

### Windows

1. 下载最新版本的 zip 文件
2. 解压到任意目录
3. 双击 `start.exe` 运行

### 系统要求

- Windows 10 或更高版本
- 支持 Vulkan 的 GPU（推荐）
- 4GB 以上内存

### 常见问题

**Q: 程序无法启动？**
A: 请运行 `start(debug).exe` 查看错误信息

**Q: 提示缺少 DLL？**
A: 请安装 Visual C++ Redistributable

**Q: GPU 加速不可用？**
A: 请更新显卡驱动，确保支持 Vulkan
```

### 3. 压缩与分发

```bash
# Windows
7z a -r waifu2x-demo_v1.0.0_windows_x64.zip waifu2x-demo/

# Linux/macOS
tar -zcvf waifu2x-demo_v1.0.0_linux_x64.tar.gz waifu2x-demo/
```

### 4. 发布渠道

#### GitHub Releases

1. 在 GitHub 仓库创建 Release
2. 上传压缩包
3. 编写 Release Notes

#### 其他平台

- 百度网盘 / 阿里云盘
- 软件下载站
- 官方网站

---

## 打包流程总结

### 完整打包步骤

```bash
# 1. 准备环境
.\venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

# 2. 测试程序
python start.py

# 3. 打包调试版本
pyinstaller -F start.py

# 4. 测试调试版本
.\dist\start.exe

# 5. 打包发布版本
pyinstaller -F -w start.py

# 6. 整理文件
mkdir release
copy dist\start.exe release\
copy README.md release\
copy LICENSE release\

# 7. 压缩发布
7z a waifu2x-demo.zip release\
```

### 关键技术点

1. **PyInstaller 参数选择**: `-F` 单文件 vs `-D` 目录，`-w` 无控制台 vs `-c` 有控制台
2. **隐藏导入处理**: 使用 `--hidden-import` 解决动态导入问题
3. **资源文件打包**: Qt 资源系统 (`images_rc.py`) 或 `--add-data`
4. **DLL 依赖管理**: 通过 `.spec` 文件手动添加
5. **多平台支持**: Windows/macOS/Linux 的不同打包策略
6. **自动化 CI/CD**: GitHub Actions 实现自动打包发布

### 常见陷阱

- ❌ 忘记导入资源模块 (`import images_rc`)
- ❌ 动态导入的模块未添加到 `hiddenimports`
- ❌ 相对路径在打包后失效（使用 `sys._MEIPASS`）
- ❌ 第三方库的 DLL 未被包含
- ❌ 在虚拟环境外打包，导致依赖混乱

---

## 进阶优化

### 1. 减小文件大小

```bash
# 使用 UPX 压缩
pyinstaller -F -w --upx-dir=/path/to/upx start.py

# 排除不需要的模块
pyinstaller -F -w --exclude-module tkinter start.py
```

### 2. 加快启动速度

```bash
# 使用 --onedir 而非 -F
pyinstaller -D -w start.py
```

### 3. 添加应用图标

```bash
pyinstaller -F -w --icon=app.ico start.py
```

### 4. 代码签名（Windows）

```bash
# 使用 signtool 签名
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\start.exe
```

---

## 总结

通过 PyInstaller 打包 PySide6 应用的核心流程：

1. **环境准备**: 安装依赖和 PyInstaller
2. **基础打包**: 使用 `-F -w` 参数生成单文件 GUI 应用
3. **依赖处理**: 解决隐藏导入、资源文件、DLL 等问题
4. **测试验证**: 在干净环境中测试打包后的程序
5. **自动化**: 使用 CI/CD 实现多平台自动打包
6. **发布分发**: 整理文件、编写文档、压缩发布

本项目通过完善的打包流程，成功将复杂的 Python GUI 应用交付给最终用户，实现了"开箱即用"的用户体验。
