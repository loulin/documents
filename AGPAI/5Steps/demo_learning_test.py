#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示五步法Plus学习机制
"""
import requests
import json
import time

def add_more_learning_data():
    """添加更多学习数据来演示个性化学习"""
    
    base_url = "http://localhost:5001"
    
    # 张医生的修改偏好：喜欢用"优化"而不是"调整"，"管理"而不是"控制"
    zhang_feedback = [
        {
            "patient_id": "demo_001", 
            "doctor_id": "张医生",
            "original_report": "血糖控制需要调整，建议强化治疗方案",
            "modified_report": "血糖管理需要优化，建议强化治疗方案",
            "changes": [{"section": "综合建议", "type": "terminology_preference", "original": "控制需要调整", "modified": "管理需要优化"}]
        },
        {
            "patient_id": "demo_002", 
            "doctor_id": "张医生",
            "original_report": "患者血糖控制不佳，需要调整用药",
            "modified_report": "患者血糖管理不佳，需要优化用药",
            "changes": [{"section": "治疗建议", "type": "terminology_preference", "original": "控制不佳，需要调整", "modified": "管理不佳，需要优化"}]
        }
    ]
    
    # 李医生的修改偏好：喜欢详细的建议，用"改善"而不是"调整"
    li_feedback = [
        {
            "patient_id": "demo_003", 
            "doctor_id": "李医生",
            "original_report": "血糖控制需要调整",
            "modified_report": "血糖控制需要改善，建议从饮食和运动两方面着手",
            "changes": [{"section": "综合建议", "type": "detail_expansion", "original": "需要调整", "modified": "需要改善，建议从饮食和运动两方面着手"}]
        },
        {
            "patient_id": "demo_004", 
            "doctor_id": "李医生", 
            "original_report": "建议调整治疗方案",
            "modified_report": "建议改善治疗方案，具体包括药物剂量调整和生活方式干预",
            "changes": [{"section": "治疗建议", "type": "detail_expansion", "original": "调整治疗方案", "modified": "改善治疗方案，具体包括药物剂量调整和生活方式干预"}]
        }
    ]
    
    all_feedback = zhang_feedback + li_feedback
    
    print("📝 正在添加学习数据...")
    for i, feedback in enumerate(all_feedback, 1):
        try:
            response = requests.post(f"{base_url}/api/save_feedback", json=feedback, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ 已添加反馈 {i}/4: {feedback['doctor_id']} - ID: {result.get('feedback_id')}")
                else:
                    print(f"❌ 反馈 {i} 保存失败: {result.get('error')}")
            else:
                print(f"❌ 反馈 {i} HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 反馈 {i} 异常: {e}")
        
        time.sleep(0.5)  # 避免请求过快

def test_personalized_learning():
    """测试个性化学习效果"""
    
    base_url = "http://localhost:5001"
    
    test_cases = [
        {
            "doctor": "张医生",
            "input": "血糖控制需要调整",
            "expected_changes": ["控制→管理", "调整→优化"]
        },
        {
            "doctor": "李医生", 
            "input": "建议调整治疗方案",
            "expected_changes": ["调整→改善", "增加详细建议"]
        },
        {
            "doctor": "新医生",
            "input": "血糖控制需要调整", 
            "expected_changes": ["使用全局学习模式"]
        }
    ]
    
    print("\n🧠 测试个性化学习效果...")
    print("=" * 60)
    
    for case in test_cases:
        print(f"\n👨‍⚕️ 医生: {case['doctor']}")
        print(f"📝 输入: {case['input']}")
        print(f"🎯 预期: {', '.join(case['expected_changes'])}")
        
        try:
            response = requests.post(
                f"{base_url}/api/generate_adaptive_report",
                json={"base_report": case['input'], "doctor_id": case['doctor']},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    original = result.get("base_report", "")
                    adapted = result.get("adaptive_report", "")
                    applied = result.get("adaptations_applied", False)
                    
                    print(f"🤖 输出: {adapted}")
                    print(f"✨ 个性化: {'✅ 是' if applied else '❌ 否'}")
                    
                    if applied:
                        print(f"🔄 变化: {original} → {adapted}")
                    else:
                        print("💡 说明: 暂未检测到个性化改变（可能需要更多学习数据）")
                else:
                    print(f"❌ API失败: {result.get('error', 'Unknown')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def show_learning_statistics():
    """显示学习统计信息"""
    
    base_url = "http://localhost:5001"
    
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print("\n📊 当前学习统计")
            print("=" * 40)
            print(f"总反馈记录: {data.get('total_records', 0)}")
            print(f"学习引擎状态: {data.get('learning_engine_status', 'unknown')}")
            
            stats = data.get('stats', {})
            print(f"总修改次数: {stats.get('total_modifications', 0)}")
            print("活跃医生排行:")
            
            doctors = stats.get('most_active_doctors', {})
            for doctor, count in sorted(doctors.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {doctor}: {count} 次修改")
            
            enhanced = data.get('enhanced_analysis', {})
            if enhanced:
                print(f"学习状态: {enhanced.get('status', 'unknown')}")
                print(f"改进率: {enhanced.get('improvement_rate', 0):.2%}")
                print(f"建议: {enhanced.get('recommendation', 'N/A')}")
        else:
            print(f"❌ 获取统计失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 统计请求异常: {e}")

def main():
    """主程序"""
    print("🔥 五步法Plus 学习机制演示")
    print("=" * 60)
    
    # 1. 显示当前学习状态
    show_learning_statistics()
    
    # 2. 添加更多学习数据
    add_more_learning_data()
    
    # 3. 重新显示学习状态
    print("\n" + "=" * 60)
    print("📈 添加数据后的学习状态")
    show_learning_statistics()
    
    # 4. 测试个性化学习
    test_personalized_learning()
    
    print("\n" + "=" * 60)
    print("💡 学习机制说明:")
    print("1. 🌐 全局学习: 所有医生的共同模式会被纳入基础知识库")
    print("2. 👨‍⚕️ 个性化学习: 每位医生的独特偏好会形成个人档案")
    print("3. 🎯 自适应生成: 系统根据医生ID自动应用相应的个性化配置")
    print("4. 📊 持续优化: 随着数据增加，学习效果会不断提升")

if __name__ == "__main__":
    main()