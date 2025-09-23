#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF数据挖掘Agent依赖包安装脚本
"""

import subprocess
import sys

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """安装所有依赖包"""
    
    # 核心依赖包 (必需)
    core_packages = [
        "pandas>=1.3.0",
        "numpy>=1.20.0"
    ]
    
    # 统计分析包 (推荐)
    statistics_packages = [
        "scipy>=1.7.0"
    ]
    
    # 机器学习包 (可选)
    ml_packages = [
        "scikit-learn>=1.0.0"
    ]
    
    # 可视化包 (可选)
    visualization_packages = [
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0"
    ]
    
    # 网络分析包 (可选)
    network_packages = [
        "networkx>=2.6.0"
    ]
    
    print("🚀 开始安装CRF数据挖掘Agent依赖包...")
    print("=" * 60)
    
    # 安装核心包
    print("📦 正在安装核心依赖包...")
    for package in core_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
        else:
            print(f"❌ {package} 安装失败")
            return
    
    # 安装统计包
    print("\n📊 正在安装统计分析包...")
    for package in statistics_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
        else:
            print(f"⚠️ {package} 安装失败，部分统计功能将不可用")
    
    # 安装机器学习包
    print("\n🤖 正在安装机器学习包...")
    for package in ml_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
        else:
            print(f"⚠️ {package} 安装失败，机器学习功能将不可用")
    
    # 安装可视化包
    print("\n📈 正在安装可视化包...")
    for package in visualization_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
        else:
            print(f"⚠️ {package} 安装失败，可视化功能将不可用")
    
    # 安装网络分析包
    print("\n🕸️ 正在安装网络分析包...")
    for package in network_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
        else:
            print(f"⚠️ {package} 安装失败，网络分析功能将不可用")
    
    print("\n" + "=" * 60)
    print("✅ 依赖包安装完成!")
    print("🎯 现在可以运行CRF数据挖掘Agent了")
    print("\n使用方法:")
    print("python3 example_analysis.py")
    
if __name__ == "__main__":
    main()