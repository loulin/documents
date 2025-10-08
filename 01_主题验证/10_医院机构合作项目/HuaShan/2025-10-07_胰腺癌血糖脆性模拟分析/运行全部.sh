#!/bin/bash
# 胰腺癌血糖脆性分析 - 一键运行脚本

echo "=========================================="
echo "胰腺癌血糖脆性分析 - 完整流程"
echo "=========================================="
echo ""

# 检查Python环境
echo "[1/4] 检查Python环境..."
python --version
if [ $? -ne 0 ]; then
    echo "错误: Python未安装"
    exit 1
fi

# 检查依赖包
echo ""
echo "[2/4] 检查依赖包..."
python -c "import pandas, numpy, sklearn, matplotlib, seaborn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖包..."
    pip install pandas numpy scikit-learn matplotlib seaborn -q
fi

# 步骤1: 生成数据
echo ""
echo "[3/4] 步骤1: 生成虚拟患者数据..."
python 01_模拟患者数据生成.py
if [ $? -ne 0 ]; then
    echo "错误: 数据生成失败"
    exit 1
fi

# 步骤2: 分析
echo ""
echo "[3/4] 步骤2: 运行血糖脆性分析..."
python 02_血糖脆性分析.py
if [ $? -ne 0 ]; then
    echo "错误: 分析失败"
    exit 1
fi

# 步骤3: 可视化
echo ""
echo "[4/4] 步骤3: 生成可视化和报告..."
python 03_可视化与报告.py
if [ $? -ne 0 ]; then
    echo "错误: 可视化生成失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 全部完成！"
echo "=========================================="
echo ""
echo "生成的文件:"
echo "  - 虚拟患者数据_术前术中术后.csv"
echo "  - 血糖脆性分析报告.txt"
echo "  - 可视化结果/ (包含6张图表和患者报告)"
echo ""
