#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五步法Plus启动脚本 - 一键启动智能学习CGM分析系统
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask',
        'flask-cors', 
        'pandas',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"   • {pkg}")
        
        print("\n🔧 安装缺少的依赖包:")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        print(f"   {install_cmd}")
        
        response = input("\n是否现在安装? (y/n): ")
        if response.lower() == 'y':
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
                print("✅ 依赖包安装完成!")
            except subprocess.CalledProcessError:
                print("❌ 依赖包安装失败，请手动安装")
                return False
        else:
            return False
    else:
        print("✅ 所有依赖包已就绪!")
    
    return True

def check_files():
    """检查必要文件"""
    current_dir = Path(__file__).parent
    
    required_files = [
        'five_steps_plus_interactive.html',
        'five_steps_plus_server.py',
        'learning_analyzer.py',
        'run_report_layered_assessment.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"   • {file}")
        return False
    else:
        print("✅ 所有必要文件已就绪!")
    
    return True

def create_sample_config():
    """创建示例配置文件"""
    config_path = Path(__file__).parent / "5Steps.json"
    
    if not config_path.exists():
        sample_config = {
            "strict": {
                "tir_excellent": 90,
                "tir_good": 80,
                "tir_acceptable": 70,
                "tbr_safe": 1,
                "tbr_acceptable": 4
            },
            "lenient": {
                "tir_good": 70,
                "tir_acceptable": 50,
                "tbr_safe": 4,
                "tbr_acceptable": 10
            },
            "assessment_rules": {
                "hypoglycemia_priority": True,
                "safety_first": True,
                "age_adjustment": False
            }
        }
        
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
        
        print("✅ 已创建默认配置文件: 5Steps.json")

def start_server():
    """启动服务器"""
    print("\n🚀 启动五步法Plus服务器...")
    
    server_script = Path(__file__).parent / "five_steps_plus_server.py"
    
    try:
        # 启动Flask服务器
        process = subprocess.Popen([
            sys.executable, str(server_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否启动成功
        if process.poll() is None:  # 进程还在运行
            print("✅ 服务器启动成功!")
            print("📝 服务器地址: http://localhost:5001")
            
            # 自动打开浏览器
            try:
                webbrowser.open('http://localhost:5001')
                print("🌐 已自动打开浏览器")
            except:
                print("⚠️ 无法自动打开浏览器，请手动访问 http://localhost:5001")
            
            print("\n" + "="*60)
            print("🎉 五步法Plus系统已启动!")
            print("="*60)
            print("📋 使用说明:")
            print("1. 在浏览器中访问 http://localhost:5001")
            print("2. 上传CGM数据文件或使用示例数据")
            print("3. AI将生成初始分析报告")
            print("4. 在富文本编辑器中修改建议")
            print("5. 保存最终报告，系统将记录修改用于学习")
            print("="*60)
            print("⌨️ 按 Ctrl+C 停止服务器")
            print("="*60)
            
            # 保持服务器运行
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务器...")
                process.terminate()
                process.wait()
                print("✅ 服务器已停止")
        
        else:
            # 进程已终止，打印错误信息
            stdout, stderr = process.communicate()
            print("❌ 服务器启动失败!")
            if stderr:
                print("错误信息:")
                print(stderr)
            
    except FileNotFoundError:
        print("❌ 无法找到服务器脚本")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def show_help():
    """显示帮助信息"""
    print("""
🔧 五步法Plus 启动脚本

用法:
    python start_five_steps_plus.py [选项]

选项:
    --check-only    : 只检查依赖和文件，不启动服务器
    --install-deps  : 强制安装/更新依赖包
    --help         : 显示此帮助信息

功能说明:
    • 自动检查并安装依赖包
    • 验证必要文件存在性
    • 创建默认配置文件
    • 启动Web服务器
    • 自动打开浏览器

系统要求:
    • Python 3.7+
    • 网络连接(用于安装依赖包)
    • 现代浏览器(Chrome/Firefox/Edge)
    """)

def main():
    """主函数"""
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    print("🔥 五步法Plus - 智能学习CGM分析系统")
    print("="*50)
    
    # 检查依赖
    print("📦 检查依赖包...")
    if not check_dependencies():
        print("❌ 依赖检查失败，退出启动")
        return
    
    # 检查文件
    print("\n📁 检查系统文件...")
    if not check_files():
        print("❌ 文件检查失败，退出启动")
        return
    
    # 创建配置文件
    print("\n⚙️ 准备配置文件...")
    create_sample_config()
    
    if '--check-only' in args:
        print("\n✅ 系统检查完成，所有准备就绪!")
        return
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()