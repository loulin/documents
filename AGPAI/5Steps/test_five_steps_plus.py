#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五步法Plus 完整测试套件
"""
import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

class FiveStepsPlusTestSuite:
    """五步法Plus测试套件"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    def log_test(self, test_name, success, message="", details=None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results["tests"].append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        return success
    
    def test_file_integrity(self):
        """测试文件完整性"""
        print("\n📁 测试文件完整性...")
        
        required_files = [
            "five_steps_plus_server.py",
            "five_steps_plus_interactive.html", 
            "enhanced_learning_engine.py",
            "learning_analyzer.py",
            "run_report_layered_assessment.py",
            "start_five_steps_plus.py",
            "feedback_database.json",
            "5Steps.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            return self.log_test(
                "文件完整性检查", 
                False, 
                f"缺少文件: {', '.join(missing_files)}"
            )
        else:
            return self.log_test("文件完整性检查", True, "所有必要文件存在")
    
    def test_dependencies(self):
        """测试依赖包"""
        print("\n📦 测试依赖包...")
        
        required_packages = ['flask', 'flask_cors', 'pandas', 'numpy', 'openpyxl']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return self.log_test(
                "依赖包检查", 
                False, 
                f"缺少依赖: {', '.join(missing_packages)}"
            )
        else:
            return self.log_test("依赖包检查", True, "所有依赖包已安装")
    
    def test_basic_learning_engine(self):
        """测试基础学习引擎"""
        print("\n🧠 测试基础学习引擎...")
        
        try:
            from learning_analyzer import LearningAnalyzer
            analyzer = LearningAnalyzer()
            insights = analyzer.analyze_all_feedback()
            
            if insights and "summary" in insights:
                total_records = insights["summary"].get("total_records_analyzed", 0)
                return self.log_test(
                    "基础学习引擎", 
                    True, 
                    f"成功分析了{total_records}条记录",
                    {"insights_keys": list(insights.keys())}
                )
            else:
                return self.log_test("基础学习引擎", False, "分析结果格式异常")
                
        except Exception as e:
            return self.log_test("基础学习引擎", False, f"导入或运行失败: {str(e)}")
    
    def test_enhanced_learning_engine(self):
        """测试增强学习引擎"""
        print("\n🚀 测试增强学习引擎...")
        
        try:
            from enhanced_learning_engine import EnhancedLearningEngine
            engine = EnhancedLearningEngine()
            
            # 测试学习效果评估
            effectiveness = engine.evaluate_learning_effectiveness()
            
            if effectiveness and "status" in effectiveness:
                return self.log_test(
                    "增强学习引擎",
                    True,
                    f"状态: {effectiveness['status']}",
                    {"effectiveness": effectiveness}
                )
            else:
                return self.log_test("增强学习引擎", False, "评估结果异常")
                
        except Exception as e:
            return self.log_test("增强学习引擎", False, f"导入或运行失败: {str(e)}")
    
    def test_five_steps_algorithm(self):
        """测试五步法分析算法"""
        print("\n⚗️ 测试五步法分析算法...")
        
        try:
            from run_report_layered_assessment import calculate_layered_metrics, load_data
            
            # 检查示例数据文件
            sample_file = "/Users/williamsun/Documents/gplus/docs/HuaShan/DemoData/吕广仁-92098-1MH00UPRRF4.xlsx"
            
            if os.path.exists(sample_file):
                df = load_data(sample_file)
                metrics = calculate_layered_metrics(df)
                
                required_metrics = ["standard_tir", "strict_tir", "mean_glucose", "tbr_percentage", "cv"]
                missing_metrics = [m for m in required_metrics if m not in metrics]
                
                if missing_metrics:
                    return self.log_test(
                        "五步法算法", 
                        False, 
                        f"缺少指标: {', '.join(missing_metrics)}"
                    )
                else:
                    return self.log_test(
                        "五步法算法", 
                        True, 
                        f"成功计算{len(metrics)}个指标",
                        {"sample_metrics": {k: v for k, v in list(metrics.items())[:5]}}
                    )
            else:
                return self.log_test("五步法算法", False, "示例数据文件不存在，跳过实际数据测试")
                
        except Exception as e:
            return self.log_test("五步法算法", False, f"算法测试失败: {str(e)}")
    
    def test_server_startup(self):
        """测试服务器启动"""
        print("\n🚀 测试服务器启动...")
        
        try:
            # 检查服务器是否已经在运行
            response = requests.get(f"{self.base_url}", timeout=2)
            if response.status_code == 200:
                return self.log_test("服务器启动", True, "服务器已在运行")
            else:
                return self.log_test("服务器启动", False, f"服务器响应异常: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            return self.log_test("服务器启动", False, "无法连接到服务器，请先启动服务器")
        except Exception as e:
            return self.log_test("服务器启动", False, f"连接测试失败: {str(e)}")
    
    def test_api_endpoints(self):
        """测试API端点"""
        print("\n🔌 测试API端点...")
        
        # 测试统计API
        try:
            response = requests.get(f"{self.base_url}/api/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                if stats.get("success"):
                    self.log_test("API-stats", True, "统计API正常", {"stats_keys": list(stats.keys())})
                else:
                    self.log_test("API-stats", False, "统计API返回失败")
            else:
                self.log_test("API-stats", False, f"统计API响应码: {response.status_code}")
        except Exception as e:
            self.log_test("API-stats", False, f"统计API测试失败: {str(e)}")
        
        # 测试自适应报告生成API
        try:
            test_data = {
                "base_report": "血糖控制需要调整，建议强化生活方式管理",
                "doctor_id": "测试医生"
            }
            response = requests.post(
                f"{self.base_url}/api/generate_adaptive_report", 
                json=test_data, 
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") is not False:  # 可能为False但有adaptive_report
                    self.log_test("API-adaptive", True, "自适应报告API正常")
                else:
                    self.log_test("API-adaptive", False, f"自适应API返回: {result.get('error', 'Unknown')}")
            else:
                self.log_test("API-adaptive", False, f"自适应API响应码: {response.status_code}")
        except Exception as e:
            self.log_test("API-adaptive", False, f"自适应API测试失败: {str(e)}")
        
        # 测试学习模型导出API
        try:
            response = requests.get(f"{self.base_url}/api/export_learning_model", timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") is not False:
                    self.log_test("API-export", True, "模型导出API正常")
                else:
                    self.log_test("API-export", False, f"导出API返回: {result.get('error', 'Unknown')}")
            else:
                self.log_test("API-export", False, f"导出API响应码: {response.status_code}")
        except Exception as e:
            self.log_test("API-export", False, f"导出API测试失败: {str(e)}")
    
    def test_feedback_system(self):
        """测试反馈系统"""
        print("\n📝 测试反馈系统...")
        
        try:
            # 模拟反馈数据
            feedback_data = {
                "patient_id": "test_patient_001", 
                "doctor_id": "test_doctor",
                "original_report": "血糖控制需要调整",
                "modified_report": "血糖管理需要优化",
                "changes": [
                    {
                        "section": "综合建议",
                        "type": "terminology_change", 
                        "original": "调整",
                        "modified": "优化"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/save_feedback",
                json=feedback_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    feedback_id = result.get("feedback_id")
                    return self.log_test(
                        "反馈系统", 
                        True, 
                        f"成功记录反馈 ID: {feedback_id}",
                        {"feedback_data": feedback_data}
                    )
                else:
                    return self.log_test("反馈系统", False, f"反馈保存失败: {result.get('error')}")
            else:
                return self.log_test("反馈系统", False, f"反馈API响应码: {response.status_code}")
                
        except Exception as e:
            return self.log_test("反馈系统", False, f"反馈系统测试失败: {str(e)}")
    
    def test_html_interface(self):
        """测试HTML界面"""
        print("\n🌐 测试HTML界面...")
        
        try:
            response = requests.get(f"{self.base_url}", timeout=5)
            
            if response.status_code == 200:
                html_content = response.text
                
                # 检查关键元素
                required_elements = [
                    "五步法Plus",
                    "富文本编辑器", 
                    "使用示例数据",
                    "开始AI分析",
                    "保存最终报告"
                ]
                
                missing_elements = [elem for elem in required_elements if elem not in html_content]
                
                if missing_elements:
                    return self.log_test(
                        "HTML界面",
                        False,
                        f"缺少界面元素: {', '.join(missing_elements)}"
                    )
                else:
                    return self.log_test(
                        "HTML界面", 
                        True, 
                        "界面加载完整",
                        {"html_size": len(html_content)}
                    )
            else:
                return self.log_test("HTML界面", False, f"界面响应码: {response.status_code}")
                
        except Exception as e:
            return self.log_test("HTML界面", False, f"界面测试失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🔥 五步法Plus 系统完整测试")
        print("=" * 50)
        
        tests = [
            self.test_file_integrity,
            self.test_dependencies,
            self.test_basic_learning_engine,
            self.test_enhanced_learning_engine,
            self.test_five_steps_algorithm,
            self.test_server_startup,
            self.test_html_interface,
            self.test_api_endpoints,
            self.test_feedback_system
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # 生成总结
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["summary"] = {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "pass_rate": f"{(passed/total)*100:.1f}%",
            "overall_status": "PASS" if passed == total else "FAIL"
        }
        
        print("\n" + "=" * 50)
        print("📊 测试结果总结")
        print("=" * 50)
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"通过率: {self.test_results['summary']['pass_rate']}")
        
        overall_status = self.test_results['summary']['overall_status']
        status_icon = "✅" if overall_status == "PASS" else "❌"
        print(f"总体状态: {status_icon} {overall_status}")
        
        # 导出测试报告
        report_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 详细测试报告已导出: {report_path}")
        
        return overall_status == "PASS"

def main():
    """主程序"""
    if len(sys.argv) > 1 and sys.argv[1] == "--url":
        base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5001"
    else:
        base_url = "http://localhost:5001"
    
    tester = FiveStepsPlusTestSuite(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()