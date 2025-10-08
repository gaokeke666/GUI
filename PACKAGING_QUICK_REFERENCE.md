# PyInstaller 打包快速参考

一页纸速查手册，包含最常用的命令和解决方案。

---

## 🚀 快速开始

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 最简单的打包
pyinstaller start.py

# 3. 生成单文件 GUI 应用
pyinstaller -F -w start.py

# 4. 使用本项目的自动化脚本
.\build.bat
```

---

## 📋 常用命令

### 基础命令

```bash
# 单文件模式
pyinstaller -F start.py

# 文件夹模式（更快）
pyinstaller -D start.py

# 无控制台窗口（GUI 应用）
pyinstaller -F -w start.py

# 有控制台窗口（调试用）
pyinstaller -F -c start.py

# 指定输出名称
pyinstaller -F -w -n "MyApp" start.py

# 添加图标
pyinstaller -F -w --icon=app.ico start.py
```

### 依赖处理

```bash
# 添加隐藏导入
pyinstaller -F -w --hidden-import waifu2x_vulkan start.py

# 添加多个隐藏导入
pyinstaller -F -w \
  --hidden-import module1 \
  --hidden-import module2 \
  start.py

# 添加数据文件 (Windows)
pyinstaller -F -w --add-data "conf;conf" start.py

# 添加数据文件 (Linux/macOS)
pyinstaller -F -w --add-data "conf:conf" start.py

# 排除不需要的模块
pyinstaller -F -w --exclude-module tkinter start.py
```

### 使用 .spec 文件

```bash
# 生成 .spec 文件（不打包）
pyi-makespec start.py

# 使用 .spec 文件打包
pyinstaller Waifu2x-GUI.spec

# 清理后重新打包
pyinstaller --clean Waifu2x-GUI.spec
```

---

## 🔧 参数速查表

| 参数 | 说明 | 示例 |
|------|------|------|
| `-F` / `--onefile` | 打包成单个 exe | `pyinstaller -F start.py` |
| `-D` / `--onedir` | 打包成文件夹（默认） | `pyinstaller -D start.py` |
| `-w` / `--windowed` | 无控制台窗口 | `pyinstaller -F -w start.py` |
| `-c` / `--console` | 有控制台窗口（默认） | `pyinstaller -F -c start.py` |
| `-n NAME` | 指定输出名称 | `pyinstaller -F -n "MyApp" start.py` |
| `--icon=FILE` | 设置图标 | `pyinstaller -F --icon=app.ico start.py` |
| `--hidden-import` | 添加隐藏导入 | `pyinstaller -F --hidden-import pkg start.py` |
| `--add-data` | 添加数据文件 | `pyinstaller -F --add-data "src;src" start.py` |
| `--exclude-module` | 排除模块 | `pyinstaller -F --exclude-module tkinter start.py` |
| `--clean` | 清理缓存 | `pyinstaller --clean start.py` |
| `--upx-dir` | UPX 压缩工具路径 | `pyinstaller -F --upx-dir=C:\upx start.py` |
| `--strip` | 去除调试符号 | `pyinstaller -F --strip start.py` |

---

## 🐛 常见错误速查

### 错误 1: ModuleNotFoundError

```
❌ ModuleNotFoundError: No module named 'xxx'

✅ 解决方案:
pyinstaller -F -w --hidden-import xxx start.py
```

### 错误 2: DLL 加载失败

```
❌ ImportError: DLL load failed while importing xxx

✅ 解决方案:
1. 安装 Visual C++ Redistributable
2. 或在 .spec 中添加:
   binaries=[('path/to/xxx.dll', '.')]
```

### 错误 3: Qt 平台插件错误

```
❌ This application failed to start because no Qt platform plugin could be initialized.

✅ 解决方案:
在 start.py 中添加:

import os
import sys
if hasattr(sys, '_MEIPASS'):
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
```

### 错误 4: 资源文件找不到

```
❌ FileNotFoundError: [Errno 2] No such file or directory: 'images/icon.png'

✅ 解决方案 1: 使用 Qt 资源系统
pyside6-rcc resources.qrc -o images_rc.py
import images_rc

✅ 解决方案 2: 动态路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

---

## 📁 .spec 文件模板

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['start.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'waifu2x_vulkan',
        'PySide6',
        'conf',
        'src',
        'ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = 无控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
```

---

## 🎯 本项目打包流程

### 方法 1: 使用自动化脚本（推荐）

```bash
# Windows
.\build.bat

# 输出:
# - waifu2x-demo/start.exe (发布版本)
# - waifu2x-demo/start(debug).exe (调试版本)
# - waifu2x-demo_windows_x64_YYYYMMDD.zip
```

### 方法 2: 手动打包

```bash
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 打包调试版本
pyinstaller -F start.py
move dist\start.exe dist\start_debug.exe

# 3. 打包发布版本
pyinstaller -F -w start.py

# 4. 整理文件
mkdir waifu2x-demo
move dist\*.exe waifu2x-demo\
copy README.md waifu2x-demo\
copy LICENSE waifu2x-demo\
```

### 方法 3: 使用 .spec 文件

```bash
# 1. 复制模板
copy Waifu2x-GUI.spec.template Waifu2x-GUI.spec

# 2. 编辑配置（可选）
# 修改 CONSOLE, ICON_FILE 等参数

# 3. 打包
pyinstaller Waifu2x-GUI.spec
```

---

## 🔍 调试技巧

### 1. 查看详细输出

```bash
# 显示详细信息
pyinstaller -F -w --log-level=DEBUG start.py
```

### 2. 保留构建文件

```bash
# 不清理构建文件，方便调试
pyinstaller -F -w --noconfirm start.py
```

### 3. 生成依赖树

```bash
# 查看所有依赖
pyi-archive_viewer dist\start.exe
```

### 4. 测试打包后的程序

```bash
# 在干净环境中测试
# 1. 复制 exe 到没有 Python 的电脑
# 2. 或在虚拟机中测试
# 3. 或临时重命名 Python 目录
```

---

## 📊 文件大小优化

```bash
# 1. 使用 UPX 压缩
pyinstaller -F -w --upx-dir=C:\upx start.py

# 2. 排除不需要的模块
pyinstaller -F -w \
  --exclude-module tkinter \
  --exclude-module matplotlib \
  start.py

# 3. 使用 --onedir（总大小更小）
pyinstaller -D -w start.py

# 4. 去除调试符号
pyinstaller -F -w --strip start.py
```

---

## 🚦 打包检查清单

### 打包前

- [ ] 程序在开发环境中正常运行
- [ ] 所有依赖已安装 (`pip install -r requirements.txt`)
- [ ] 资源文件已编译（如 `images_rc.py`）
- [ ] 虚拟环境已激活

### 打包后

- [ ] exe 文件生成成功
- [ ] 文件大小合理（通常 20-100 MB）
- [ ] 在当前电脑上能正常运行
- [ ] 调试版本能显示错误信息

### 发布前

- [ ] 在干净环境中测试（无 Python 的电脑）
- [ ] 测试所有功能
- [ ] 检查启动速度
- [ ] 准备好 README 和 LICENSE
- [ ] 版本号正确

---

## 💡 最佳实践

### ✅ 推荐做法

1. **使用虚拟环境打包** - 避免依赖混乱
2. **提供调试版本** - 方便用户反馈问题
3. **使用 .spec 文件** - 配置更灵活
4. **自动化打包** - 使用脚本或 CI/CD
5. **在干净环境测试** - 确保真正独立运行

### ❌ 避免的错误

1. **在全局环境打包** - 可能包含不必要的依赖
2. **只提供无控制台版本** - 难以调试问题
3. **不测试就发布** - 可能在用户电脑上无法运行
4. **硬编码路径** - 打包后路径会改变
5. **忽略错误信息** - 应该认真处理每个警告

---

## 🔗 相关资源

### 官方文档

- PyInstaller 官方文档: https://pyinstaller.org/
- PySide6 文档: https://doc.qt.io/qtforpython/

### 本项目文档

- 详细打包指南: `DEPLOYMENT_GUIDE.md`
- 打包流程详解: `PACKAGING_WORKFLOW.md`
- 自动化脚本: `build.bat`
- .spec 模板: `Waifu2x-GUI.spec.template`

### 工具下载

- PyInstaller: `pip install pyinstaller`
- UPX 压缩: https://upx.github.io/
- 7-Zip: https://www.7-zip.org/

---

## 📞 常见问题 FAQ

### Q1: -F 和 -D 有什么区别？

```
-F (--onefile):
  ✓ 单个 exe 文件，方便分发
  ✗ 启动慢（需要解压）
  ✗ 文件较大

-D (--onedir):
  ✓ 启动快
  ✓ 总大小更小
  ✗ 文件多，不方便分发
```

### Q2: 为什么打包后文件这么大？

```
原因:
- 包含了完整的 Python 解释器（~10 MB）
- PySide6 库很大（~50 MB）
- 所有依赖的 DLL

优化方法:
- 使用 UPX 压缩
- 排除不需要的模块
- 考虑使用 -D 模式
```

### Q3: 如何添加应用图标？

```bash
# 1. 准备 .ico 文件（Windows）
# 2. 使用 --icon 参数
pyinstaller -F -w --icon=app.ico start.py

# 或在 .spec 文件中设置
icon='app.ico'
```

### Q4: 打包后在其他电脑上无法运行？

```
检查清单:
1. 是否缺少 Visual C++ Redistributable
2. 是否缺少 DLL（运行调试版本查看）
3. 是否需要管理员权限
4. 是否被杀毒软件拦截
5. 系统版本是否兼容（Win7/10/11）
```

### Q5: 如何减小启动时间？

```
方法:
1. 使用 -D 而非 -F
2. 减少不必要的导入
3. 延迟导入大型库
4. 使用 SSD 存储
```

---

**快速参考版本**: 1.0  
**适用项目**: Waifu2x-GUI  
**最后更新**: 2024-01-01

---

## 🎓 记住这些核心命令

```bash
# 开发阶段
python start.py                    # 运行程序

# 打包阶段
pyinstaller -F -w start.py         # 打包发布版本
pyinstaller -F start.py            # 打包调试版本

# 使用配置
pyinstaller Waifu2x-GUI.spec       # 使用 .spec 文件

# 自动化
.\build.bat                        # 一键打包（本项目）
```

**记住**: 打包前测试，打包后验证！
