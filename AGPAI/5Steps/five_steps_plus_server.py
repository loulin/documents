#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五步法Plus服务端 - 提供API接口和修改记录功能
"""
import json
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd

# 导入现有的五步法分析模块和增强学习引擎
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from run_report_layered_assessment import (
        calculate_layered_metrics, 
        generate_layered_report, 
        load_data
    )
    from enhanced_learning_engine import EnhancedLearningEngine
    ENHANCED_LEARNING_AVAILABLE = True
except ImportError:
    print("警告: 无法导入分析模块或增强学习引擎，将使用基础功能")
    ENHANCED_LEARNING_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# 配置文件路径
FEEDBACK_DB_PATH = "feedback_database.json"
CONFIG_PATH = "5Steps.json"

class FeedbackCollector:
    """修改反馈收集器"""
    
    def __init__(self, db_path=FEEDBACK_DB_PATH):
        self.db_path = db_path
        self.feedback_data = self.load_feedback_db()
    
    def load_feedback_db(self):
        """加载反馈数据库"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"feedback_records": [], "learning_stats": {}}
        return {"feedback_records": [], "learning_stats": {}}
    
    def save_feedback_db(self):
        """保存反馈数据库"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
    
    def record_feedback(self, patient_id, doctor_id, original_report, modified_report, changes):
        """记录医生修改反馈"""
        feedback_record = {
            "id": len(self.feedback_data["feedback_records"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "original_report": original_report,
            "modified_report": modified_report,
            "changes": changes,
            "change_summary": self.analyze_changes(original_report, modified_report)
        }
        
        self.feedback_data["feedback_records"].append(feedback_record)
        self.update_learning_stats()
        self.save_feedback_db()
        
        return feedback_record["id"]
    
    def analyze_changes(self, original, modified):
        """分析修改类型和模式"""
        changes = {
            "text_length_change": len(modified) - len(original),
            "modification_type": "content_edit",
            "estimated_sections_modified": 0
        }
        
        # 简单的修改分析
        if abs(changes["text_length_change"]) > 100:
            changes["modification_type"] = "major_revision"
        elif abs(changes["text_length_change"]) > 20:
            changes["modification_type"] = "moderate_edit"
        else:
            changes["modification_type"] = "minor_edit"
        
        # 估算修改段落数
        original_lines = original.count('\n')
        modified_lines = modified.count('\n')
        changes["estimated_sections_modified"] = abs(modified_lines - original_lines)
        
        return changes
    
    def update_learning_stats(self):
        """更新学习统计信息"""
        records = self.feedback_data["feedback_records"]
        if not records:
            return
        
        stats = {
            "total_modifications": len(records),
            "modification_types": {},
            "most_active_doctors": {},
            "average_changes_per_report": 0,
            "last_update": datetime.now().isoformat()
        }
        
        # 统计修改类型
        for record in records:
            mod_type = record["change_summary"]["modification_type"]
            stats["modification_types"][mod_type] = stats["modification_types"].get(mod_type, 0) + 1
            
            doctor = record.get("doctor_id", "unknown")
            stats["most_active_doctors"][doctor] = stats["most_active_doctors"].get(doctor, 0) + 1
        
        self.feedback_data["learning_stats"] = stats

feedback_collector = FeedbackCollector()

# 初始化增强学习引擎
if ENHANCED_LEARNING_AVAILABLE:
    learning_engine = EnhancedLearningEngine()
    print("✅ 增强学习引擎已加载")
else:
    learning_engine = None
    print("⚠️ 使用基础学习功能")

@app.route('/')
def index():
    """主页面"""
    try:
        with open('five_steps_plus_interactive.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>五步法Plus系统</h1>
        <p>请确保 five_steps_plus_interactive.html 文件在同一目录下</p>
        <p>API endpoints:</p>
        <ul>
            <li>POST /api/analyze - 分析CGM数据</li>
            <li>POST /api/save_feedback - 保存修改反馈</li>
            <li>GET /api/stats - 获取学习统计</li>
        </ul>
        """

@app.route('/api/analyze', methods=['POST'])
def analyze_cgm_data():
    """分析CGM数据API"""
    try:
        # 检查是否有文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # 保存临时文件
                temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                file.save(temp_path)
                
                try:
                    # 使用真实的五步法分析
                    raw_df = load_data(temp_path)
                    patient_metrics = calculate_layered_metrics(raw_df)
                    
                    # 加载配置
                    if os.path.exists(CONFIG_PATH):
                        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                            agp_rules = json.load(f)
                    else:
                        # 默认配置
                        agp_rules = {"strict": {}, "lenient": {}}
                    
                    # 生成报告
                    report_lines = generate_layered_report(patient_metrics, agp_rules, raw_df)
                    
                    # 清理临时文件
                    os.remove(temp_path)
                    
                    # 转换为HTML格式
                    html_report = convert_report_to_html(report_lines)
                    
                    return jsonify({
                        "success": True,
                        "patient_data": patient_metrics,
                        "report_html": html_report,
                        "report_text": "\n".join(report_lines)
                    })
                    
                except Exception as e:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise e
        
        # 使用示例数据
        elif request.json and request.json.get('use_sample_data'):
            return get_sample_analysis()
        
        else:
            return jsonify({"success": False, "error": "没有提供文件或示例数据请求"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/save_feedback', methods=['POST'])
def save_feedback():
    """保存修改反馈API"""
    try:
        data = request.json
        
        # 提取数据
        patient_id = data.get('patient_id', 'unknown')
        doctor_id = data.get('doctor_id', 'default_doctor')
        original_report = data.get('original_report', '')
        modified_report = data.get('modified_report', '')
        changes = data.get('changes', [])
        
        # 记录反馈
        feedback_id = feedback_collector.record_feedback(
            patient_id, doctor_id, original_report, modified_report, changes
        )
        
        return jsonify({
            "success": True,
            "feedback_id": feedback_id,
            "message": "修改反馈已记录，用于系统学习优化"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stats', methods=['GET'])
def get_learning_stats():
    """获取学习统计信息API"""
    basic_stats = {
        "success": True,
        "stats": feedback_collector.feedback_data.get("learning_stats", {}),
        "total_records": len(feedback_collector.feedback_data.get("feedback_records", []))
    }
    
    # 如果有增强学习引擎，添加详细分析
    if learning_engine:
        try:
            effectiveness = learning_engine.evaluate_learning_effectiveness()
            basic_stats["enhanced_analysis"] = effectiveness
            basic_stats["learning_engine_status"] = "active"
        except Exception as e:
            basic_stats["enhanced_analysis"] = {"error": str(e)}
            basic_stats["learning_engine_status"] = "error"
    else:
        basic_stats["learning_engine_status"] = "unavailable"
    
    return jsonify(basic_stats)

@app.route('/api/generate_adaptive_report', methods=['POST'])
def generate_adaptive_report():
    """生成自适应报告API"""
    try:
        data = request.json
        base_report = data.get('base_report', '')
        doctor_id = data.get('doctor_id', None)
        
        if not learning_engine:
            return jsonify({
                "success": False, 
                "error": "增强学习引擎不可用",
                "adaptive_report": base_report
            })
        
        # 使用学习引擎生成自适应报告
        adaptive_report = learning_engine.generate_adaptive_suggestions(base_report, doctor_id)
        
        return jsonify({
            "success": True,
            "adaptive_report": adaptive_report,
            "base_report": base_report,
            "doctor_id": doctor_id,
            "adaptations_applied": adaptive_report != base_report
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/export_learning_model', methods=['GET'])
def export_learning_model():
    """导出学习模型API"""
    try:
        if not learning_engine:
            return jsonify({"success": False, "error": "增强学习引擎不可用"})
        
        model_path = learning_engine.export_learning_model("exported_model.json")
        
        return jsonify({
            "success": True,
            "model_path": model_path,
            "message": "学习模型已导出"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def convert_report_to_html(report_lines):
    """将报告文本转换为HTML格式"""
    html_lines = []
    
    for line in report_lines:
        line = line.strip()
        if not line or line == "---" or line.startswith("="):
            continue
            
        # 主标题
        if line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        # 三级标题
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        # 四级标题
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:]}</h4>")
        # 分隔线
        elif line == "---":
            html_lines.append("<hr>")
        # 列表项或普通内容
        else:
            # 处理粗体标记
            line = line.replace("**", "<strong>").replace("**", "</strong>")
            if line.startswith("- "):
                html_lines.append(f"<p>{line[2:]}</p>")
            else:
                html_lines.append(f"<p>{line}</p>")
    
    return "\n".join(html_lines)

def get_sample_analysis():
    """获取示例分析数据"""
    sample_data = {
        "patient_id": "吕广仁-92098",
        "cgm_wear_days": 14.0,
        "cgm_valid_data_percentage": 99.6,
        "standard_tir": 88.6,
        "strict_tir": 58.5,
        "lenient_tir": 97.9,
        "mean_glucose": 7.96,
        "tbr_percentage": 0.1,
        "cv": 26.6,
        "strict_tar": 41.4
    }
    
    # 生成示例报告HTML
    html_report = f"""
    <h2>AGP 报告分层评估解读: v3.0</h2>
    <hr>
    <p><strong>患者ID:</strong> {sample_data['patient_id']}<br>
    <strong>分析时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    <strong>血糖管理等级:</strong> 血糖控制亚优，需要调整<br>
    <strong>评估类型:</strong> 严格评估<br>
    <strong>主要建议:</strong> 需要强化生活方式管理<br>
    <strong>随访频率:</strong> 月度监测</p>
    <hr>

    <h3>一. 数据质量评估</h3>
    <p>1. 佩戴天数: <strong>{sample_data['cgm_wear_days']} 天</strong> (标准: ≥14天)<br>
    2. 有效数据: <strong>{sample_data['cgm_valid_data_percentage']}%</strong> (标准: ≥70%)<br>
    3. 评估结论: <strong>数据充分可信</strong></p>

    <h3>二. 分层血糖达标评估</h3>
    <h4>三层目标范围TIR对比</h4>
    <p>1. <strong>标准TIR (3.9-10.0 mmol/L): {sample_data['standard_tir']}%</strong> (糖尿病目标: >70%)<br>
    2. <strong>严格TIR (3.9-7.8 mmol/L): {sample_data['strict_tir']}%</strong> (代谢健康目标: >80%)<br>
    3. <strong>宽松TIR (3.9-13.9 mmol/L): {sample_data['lenient_tir']}%</strong> (基础安全目标: >50%)<br>
    4. <strong>平均葡萄糖: {sample_data['mean_glucose']} mmol/L</strong></p>

    <h4>分层评估结果</h4>
    <p>1. <strong>评估路径:</strong> 标准TIR ≥ 70%，启动严格评估<br>
    2. <strong>严格评估等级:</strong> 血糖控制亚优，需要调整<br>
    3. <strong>临床意义:</strong> 血糖控制良好，按代谢健康人群标准评估</p>

    <h3>三. 低血糖风险评估</h3>
    <p>1. <strong>TBR (&lt;3.9 mmol/L): {sample_data['tbr_percentage']}%</strong> (安全目标: &lt;4%)<br>
    2. <strong>低血糖风险:</strong> 较低，低血糖风险较低</p>

    <h3>四. 血糖稳定性评估</h3>
    <p>1. <strong>血糖变异系数 (CV): {sample_data['cv']}%</strong> (理想目标: ≤36%)<br>
    2. <strong>稳定性:</strong> 尚可，血糖波动在临床可接受范围内</p>

    <h3>五. 高血糖负担评估 (严格标准)</h3>
    <p>1. <strong>TAR (>7.8 mmol/L): {sample_data['strict_tar']}%</strong> (代谢健康目标: <20%)<br>
    2. <strong>高血糖负担:</strong> 偏高，建议调整生活方式</p>

    <h3>综合评估与建议</h3>
    <p>1. <strong>最终评级:</strong> 血糖控制亚优，需要调整<br>
    2. <strong>主要建议:</strong> 需要强化生活方式管理<br>
    3. <strong>随访计划:</strong> 月度监测<br>
    4. <strong>下次CGM:</strong> 建议4周后</p>

    <hr>
    <p><strong>分层评估报告生成完毕</strong><br>
    <strong>免责声明:</strong> 本报告仅供临床参考，具体治疗方案请遵医嘱</p>
    """
    
    return jsonify({
        "success": True,
        "patient_data": sample_data,
        "report_html": html_report.strip(),
        "report_text": "示例分析文本报告"
    })

if __name__ == '__main__':
    print("五步法Plus服务器启动中...")
    print("访问地址: http://localhost:5000")
    print("API文档: http://localhost:5000")
    
    # 创建必要的目录
    os.makedirs('temp', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5001)