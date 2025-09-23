#!/bin/bash

# AGPAI虚拟环境设置脚本

echo "🚀 AGPAI虚拟环境设置"
echo "===================="

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 检测到虚拟环境: $VIRTUAL_ENV"
else
    echo "❌ 未检测到虚拟环境"
    echo "请先激活虚拟环境："
    echo "source /Users/williamsun/Documents/gplus/.venv/bin/activate"
    exit 1
fi

# 升级pip
echo "📦 升级pip..."
python -m pip install --upgrade pip

# 安装依赖包
echo "📦 安装AGPAI依赖包..."
pip install pandas>=2.0.0
pip install numpy>=1.20.0
pip install scipy>=1.7.0
pip install matplotlib>=3.5.0
pip install seaborn>=0.11.0
pip install scikit-learn>=1.0.0

# 验证安装
echo "🔍 验证安装..."
python -c "
import pandas as pd
import numpy as np
import scipy
import matplotlib
import seaborn as sns
import sklearn

print('✅ pandas版本:', pd.__version__)
print('✅ numpy版本:', np.__version__)
print('✅ scipy版本:', scipy.__version__)
print('✅ matplotlib版本:', matplotlib.__version__)
print('✅ seaborn版本:', sns.__version__)
print('✅ scikit-learn版本:', sklearn.__version__)
print('\n🎉 所有依赖包安装成功！')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 安装完成！现在您可以运行："
    echo "python CGM_AGP_Analyzer_Agent.py"
    echo "python Full_AGP_Demo.py"
else
    echo "❌ 安装过程中出现错误"
fi