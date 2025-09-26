@echo off
chcp 65001 > nul

REM 个性化营养管理系统v3.0启动脚本 (Windows版本)

echo 🍽️ 启动个性化营养管理系统v3.0界面...
echo ========================================

REM 检查Python版本
echo 📋 检查Python环境...
python --version

REM 检查是否已安装streamlit
streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 未找到streamlit，正在安装依赖包...
    pip install -r requirements.txt
) else (
    echo ✅ Streamlit已安装
)

REM 检查核心系统文件
echo 📋 检查核心系统文件...
if not exist "Core_Systems\integrated_nutrition_system_v2.py" (
    echo ❌ 缺少核心文件: integrated_nutrition_system_v2.py
    pause
    exit /b 1
)

if not exist "Core_Systems\gi_database_integration_v2.py" (
    echo ❌ 缺少核心文件: gi_database_integration_v2.py
    pause
    exit /b 1
)

if not exist "Core_Systems\weekly_menu_manager.py" (
    echo ❌ 缺少核心文件: weekly_menu_manager.py
    pause
    exit /b 1
)

if not exist "Core_Systems\cgm_nutrition_integration.py" (
    echo ❌ 缺少核心文件: cgm_nutrition_integration.py
    pause
    exit /b 1
)

echo ✅ 核心系统文件检查完成 (v3.0)

REM 创建必要目录
echo 📁 创建必要目录...
if not exist "Charts" mkdir Charts
if not exist "Reports" mkdir Reports

echo 🚀 启动Web界面...
echo 📱 界面地址: http://localhost:8501
echo 🛑 停止服务: 按 Ctrl+C
echo ========================================

REM 启动streamlit应用
streamlit run nutrition_interface.py --server.port=8501

pause