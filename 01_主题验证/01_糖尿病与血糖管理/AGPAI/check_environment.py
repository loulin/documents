#!/usr/bin/env python3
"""
检查Python环境和依赖包
"""

import sys
import subprocess

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境检查")
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")
    print()
    
    # 检查必需的包
    required_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'), 
        ('scipy', 'scipy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('scikit-learn', 'sklearn')  # 包名和导入名不同
    ]
    
    print("📦 依赖包检查:")
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name} - 已安装")
        except ImportError:
            print(f"  ❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下包: {', '.join(missing_packages)}")
        print("\n📥 安装命令:")
        print(f"python3 -m pip install --user {' '.join(missing_packages)}")
        print("\n或者一次性安装所有依赖:")
        print(f"python3 -m pip install --user {' '.join(required_packages)}")
    else:
        print("\n🎉 所有依赖包都已正确安装!")
        
    return len(missing_packages) == 0

def test_agp_import():
    """测试AGP智能体导入"""
    print("\n🤖 AGPAI智能体导入测试:")
    
    try:
        # 测试完整版智能体
        from CGM_AGP_Analyzer_Agent import CGMDataReader, AGPVisualAnalyzer, AGPIntelligentReporter
        print("  ✅ 完整版智能体 - 导入成功")
        
        # 创建实例测试
        reader = CGMDataReader()
        analyzer = AGPVisualAnalyzer()
        reporter = AGPIntelligentReporter()
        print("  ✅ 智能体实例化 - 成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 完整版智能体 - 导入失败: {e}")
        
        # 尝试简化版
        try:
            from Simple_CGM_AGP_Analyzer import SimpleCGMDataReader, SimpleAGPAnalyzer
            print("  ✅ 简化版智能体 - 导入成功")
            print("  💡 建议: 如果只需要基础功能，可以使用简化版智能体")
            return False
        except Exception as e2:
            print(f"  ❌ 简化版智能体 - 导入也失败: {e2}")
            return False

def main():
    """主函数"""
    print("=== AGPAI环境检查工具 ===\n")
    
    # 检查Python环境
    packages_ok = check_python_environment()
    
    # 测试智能体导入
    import_ok = test_agp_import()
    
    print("\n" + "="*50)
    
    if packages_ok and import_ok:
        print("🎯 环境检查完成 - 一切正常!")
        print("您可以运行: python3 Full_AGP_Demo.py")
    elif packages_ok and not import_ok:
        print("⚠️ 依赖包正常，但智能体导入失败")
        print("建议检查文件路径和模块结构")
    elif not packages_ok:
        print("❌ 缺少必需的依赖包")
        print("请先安装缺失的包，然后重新运行此脚本")
    
    print("\n📝 如果问题持续存在，请尝试:")
    print("  1. 使用完整路径: /usr/bin/python3 或 /usr/local/bin/python3")
    print("  2. 检查是否有多个Python版本")  
    print("  3. 使用虚拟环境: python3 -m venv agpai_env && source agpai_env/bin/activate")
    print("  4. 使用简化版: python3 Simple_CGM_AGP_Analyzer.py")

if __name__ == "__main__":
    main()