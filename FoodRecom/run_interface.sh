#!/bin/bash

# 个性化营养管理系统v3.0启动脚本
# 使用方法: chmod +x run_interface.sh && ./run_interface.sh

echo "🍽️ 启动个性化营养管理系统v3.0界面..."
echo "========================================"

# 检查Python版本
echo "📋 检查Python环境..."
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查是否已安装streamlit
if ! command -v streamlit &> /dev/null; then
    echo "⚠️ 未找到streamlit，正在安装依赖包..."
    pip3 install -r requirements.txt
else
    echo "✅ Streamlit已安装"
fi

# 检查核心系统文件
echo "📋 检查核心系统文件..."
if [ ! -f "Core_Systems/integrated_nutrition_system_v2.py" ]; then
    echo "❌ 缺少核心文件: integrated_nutrition_system_v2.py"
    exit 1
fi

if [ ! -f "Core_Systems/gi_database_integration_v2.py" ]; then
    echo "❌ 缺少核心文件: gi_database_integration_v2.py"
    exit 1
fi

if [ ! -f "Core_Systems/weekly_menu_manager.py" ]; then
    echo "❌ 缺少核心文件: weekly_menu_manager.py"
    exit 1
fi

if [ ! -f "Core_Systems/cgm_nutrition_integration.py" ]; then
    echo "❌ 缺少核心文件: cgm_nutrition_integration.py"
    exit 1
fi

echo "✅ 核心系统文件检查完成 (v3.0)"

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p Charts
mkdir -p Reports

echo "🚀 启动Web界面..."
echo "📱 界面地址: http://localhost:8501"
echo "🛑 停止服务: 按 Ctrl+C"
echo "========================================"

# 启动streamlit应用
streamlit run nutrition_interface.py --server.port=8501