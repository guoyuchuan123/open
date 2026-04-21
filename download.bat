@echo off
chcp 65001 >nul
title GitHub 快速下载工具

echo ==================================================
echo GitHub 快速下载工具
echo ==================================================
echo.

set /p url="请输入 GitHub 链接或镜像链接: "

if "%url%"=="" (
    echo 错误: 链接不能为空！
    pause
    exit /b 1
)

echo.
echo 正在下载...
echo.

python "%~dp0github_downloader.py" "%url%"

if %errorlevel% equ 0 (
    echo.
    echo 下载完成！文件保存在 D:\downupload 目录下
) else (
    echo.
    echo 下载失败，请检查链接是否正确
)

echo.
pause
