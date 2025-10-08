@echo off
chcp 65001 >nul
echo ========================================
echo Waifu2x-GUI 自动打包脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境！
    echo 请先创建虚拟环境: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/7] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo.
echo [2/7] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [警告] PyInstaller 未安装，正在安装...
    pip install pyinstaller
)

REM 清理旧文件
echo.
echo [3/7] 清理旧文件...
if exist build (
    echo 删除 build 目录...
    rmdir /s /q build
)
if exist dist (
    echo 删除 dist 目录...
    rmdir /s /q dist
)
if exist waifu2x-demo (
    echo 删除 waifu2x-demo 目录...
    rmdir /s /q waifu2x-demo
)
if exist *.zip (
    echo 删除旧的 zip 文件...
    del /q *.zip
)

REM 打包调试版本
echo.
echo [4/7] 打包调试版本（带控制台）...
echo 命令: pyinstaller -F start.py
pyinstaller -F start.py
if errorlevel 1 (
    echo [错误] 调试版本打包失败！
    pause
    exit /b 1
)
echo 重命名为 start(debug).exe...
move dist\start.exe "dist\start(debug).exe" >nul

REM 打包发布版本
echo.
echo [5/7] 打包发布版本（无控制台）...
echo 命令: pyinstaller -F -w start.py
pyinstaller -F -w start.py
if errorlevel 1 (
    echo [错误] 发布版本打包失败！
    pause
    exit /b 1
)

REM 整理发布文件
echo.
echo [6/7] 整理发布文件...
mkdir waifu2x-demo
echo 复制可执行文件...
move dist\*.exe waifu2x-demo\ >nul
echo 复制文档...
copy README.md waifu2x-demo\ >nul
if exist LICENSE (
    copy LICENSE waifu2x-demo\ >nul
)

REM 生成版本信息
echo.
echo 生成版本信息...
(
    echo Waifu2x-GUI
    echo.
    echo 构建时间: %date% %time%
    echo Python 版本: 
    python --version
    echo.
    echo 文件列表:
    echo - start.exe: 主程序（无控制台窗口）
    echo - start^(debug^).exe: 调试版本（显示控制台，用于查看错误信息）
    echo.
    echo 使用方法:
    echo 1. 双击 start.exe 运行程序
    echo 2. 如遇到问题，运行 start^(debug^).exe 查看错误信息
) > waifu2x-demo\VERSION.txt

REM 压缩发布包
echo.
echo [7/7] 压缩发布包...
set ZIPNAME=waifu2x-demo_windows_x64_%date:~0,4%%date:~5,2%%date:~8,2%.zip
if exist "%ProgramFiles%\7-Zip\7z.exe" (
    "%ProgramFiles%\7-Zip\7z.exe" a -r "%ZIPNAME%" waifu2x-demo\
    echo 压缩完成: %ZIPNAME%
) else (
    echo [警告] 未找到 7-Zip，跳过压缩步骤
    echo 请手动压缩 waifu2x-demo 文件夹
)

REM 显示文件大小
echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 输出目录: waifu2x-demo\
echo.
echo 文件列表:
dir /b waifu2x-demo
echo.
echo 文件大小:
for %%F in (waifu2x-demo\*.exe) do (
    echo %%~nxF: %%~zF 字节
)
echo.
if exist "%ZIPNAME%" (
    echo 压缩包: %ZIPNAME%
    for %%F in ("%ZIPNAME%") do echo 大小: %%~zF 字节
)
echo.
echo ========================================
echo 下一步:
echo 1. 测试 waifu2x-demo\start.exe
echo 2. 如有问题，运行 waifu2x-demo\start^(debug^).exe
echo 3. 确认无误后，分发 %ZIPNAME%
echo ========================================
echo.
pause
