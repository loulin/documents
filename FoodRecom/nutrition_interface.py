#!/usr/bin/env python3
"""
个性化营养管理系统 - 可视化界面
使用Streamlit创建交互式Web界面，支持患者信息填写和报告生成
"""

import streamlit as st
import sys
import os
import datetime
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import random

# 添加Core_Systems路径
sys.path.append('Core_Systems')

try:
    from integrated_nutrition_system_v2 import IntegratedNutritionSystemV2, PatientProfile
    from gi_database_integration_v2 import GIDatabaseSystemV2
    from cgm_nutrition_integration import CGMNutritionIntegration
except ImportError as e:
    st.error(f"导入核心系统失败: {e}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="个性化营养管理系统",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 1.5rem;
        color: #4682B4;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #4682B4;
        padding-bottom: 0.5rem;
    }

    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4682B4;
        margin: 1rem 0;
    }

    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }

    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化session state"""
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    if 'nutrition_system' not in st.session_state:
        with st.spinner('正在初始化营养管理系统...'):
            st.session_state.nutrition_system = IntegratedNutritionSystemV2()
            st.session_state.gi_system = GIDatabaseSystemV2()

def render_main_header():
    """渲染主标题"""
    st.markdown('<h1 class="main-header">🍽️ 个性化营养管理系统</h1>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <h4>🎯 系统功能</h4>
        <ul>
            <li>🧮 基于Harris-Benedict公式的精确代谢计算</li>
            <li>🏥 支持35+种疾病的专业营养管理</li>
            <li>🍽️ 六维度饮食偏好个性化推荐</li>
            <li>🍚 95种食物GI数据库血糖管理</li>
            <li>📊 营养雷达图可视化分析</li>
            <li>📝 专业级营养评估报告</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_basic_info_form():
    """渲染基本信息表单"""
    st.markdown('<h2 class="section-header">👤 基本信息</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("患者姓名", value="", help="请输入患者真实姓名")
        age = st.number_input("年龄", min_value=1, max_value=120, value=35, help="患者当前年龄")
        gender = st.selectbox("性别", ["男", "女"], help="生理性别")

    with col2:
        height = st.number_input("身高 (cm)", min_value=50, max_value=250, value=170, help="患者身高，单位厘米")
        weight = st.number_input("体重 (kg)", min_value=20, max_value=300, value=65, help="患者当前体重，单位公斤")

        # 计算并显示BMI
        if height > 0 and weight > 0:
            bmi = weight / ((height/100) ** 2)
            bmi_category = get_bmi_category(bmi)
            st.metric("BMI指数", f"{bmi:.1f}", bmi_category)

    return {
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight
    }

def get_bmi_category(bmi):
    """获取BMI分类"""
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常"
    elif bmi < 28:
        return "超重"
    else:
        return "肥胖"

def render_health_status_form():
    """渲染健康状况表单"""
    st.markdown('<h2 class="section-header">🏥 健康状况</h2>', unsafe_allow_html=True)

    # 疾病选择
    st.subheader("确诊疾病")
    diseases_options = [
        "糖尿病", "高血压", "高血脂", "心血管疾病", "脑血管疾病",
        "肾病", "肝病", "胃炎", "胃溃疡", "肠炎", "便秘", "腹泻",
        "甲状腺疾病", "痛风", "骨质疏松", "贫血", "肥胖症",
        "抑郁症", "焦虑症", "失眠", "哮喘", "过敏性疾病",
        "癌症", "免疫系统疾病", "内分泌疾病"
    ]

    diagnosed_diseases = st.multiselect(
        "请选择已确诊的疾病",
        diseases_options,
        help="可多选，影响营养方案制定"
    )

    # 生理指标
    st.subheader("生理指标")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**血压 (mmHg)**")
        systolic_bp = st.number_input("收缩压", min_value=60, max_value=250, value=120)
        diastolic_bp = st.number_input("舒张压", min_value=40, max_value=150, value=80)

    with col2:
        st.write("**血糖 (mmol/L)**")
        fasting_glucose = st.number_input("空腹血糖", min_value=2.0, max_value=30.0, value=5.6, step=0.1)
        hba1c = st.number_input("糖化血红蛋白 (%)", min_value=3.0, max_value=15.0, value=5.5, step=0.1)

    with col3:
        st.write("**血脂 (mmol/L)**")
        total_cholesterol = st.number_input("总胆固醇", min_value=1.0, max_value=15.0, value=4.5, step=0.1)
        triglycerides = st.number_input("甘油三酯", min_value=0.5, max_value=10.0, value=1.2, step=0.1)

    return {
        "diagnosed_diseases": diagnosed_diseases,
        "blood_pressure_systolic": systolic_bp,
        "blood_pressure_diastolic": diastolic_bp,
        "fasting_glucose": fasting_glucose,
        "hba1c": hba1c,
        "total_cholesterol": total_cholesterol,
        "triglycerides": triglycerides
    }

def render_dietary_preferences_form():
    """渲染饮食偏好表单"""
    st.markdown('<h2 class="section-header">🍽️ 饮食偏好六维度</h2>', unsafe_allow_html=True)

    # 维度1: 偏好菜系
    st.subheader("1. 🏮 偏好菜系")
    cuisine_options = ["清淡", "地中海", "日韩", "川菜", "粤菜", "鲁菜", "苏菜", "浙菜", "闽菜", "湘菜", "徽菜"]
    preferred_cuisines = st.multiselect(
        "您偏好的菜系风味",
        cuisine_options,
        help="可多选，影响菜谱推荐的基础风味方向"
    )

    # 维度2: 不喜食物
    st.subheader("2. 🚫 不喜食物")
    dislike_categories = {
        "肉类": ["猪肉", "牛肉", "羊肉", "鸡肉", "鸭肉"],
        "海鲜类": ["鱼类", "虾类", "蟹类", "贝类"],
        "内脏类": ["猪肝", "鸡肝", "腰子", "心脏"],
        "蔬菜类": ["苦瓜", "茄子", "冬瓜", "豆角", "韭菜", "芹菜"],
        "调料类": ["香菜", "洋葱", "蒜", "姜", "八角", "花椒"]
    }

    disliked_foods = []
    for category, foods in dislike_categories.items():
        selected = st.multiselect(f"{category}", foods)
        disliked_foods.extend(selected)

    # 维度3: 饮食限制
    st.subheader("3. 🔒 饮食限制")
    restriction_options = ["素食", "严格素食", "清真", "低盐", "低糖", "低脂", "无麸质", "低嘌呤"]
    dietary_restrictions = st.multiselect(
        "饮食限制要求",
        restriction_options,
        help="基于宗教、健康或个人原因的强制性限制"
    )

    # 维度4: 辣度承受
    st.subheader("4. 🌶️ 辣度承受")
    spice_tolerance = st.selectbox(
        "您的辣度承受程度",
        ["不能吃辣", "微辣", "中等", "重辣"],
        index=2,
        help="影响调料使用和菜品推荐"
    )

    # 维度5: 烹饪偏好
    st.subheader("5. 👨‍🍳 烹饪偏好")
    cooking_options = ["蒸", "煮", "炒", "炖", "烤", "凉拌", "油炸"]
    cooking_preferences = st.multiselect(
        "偏好的烹饪方式",
        cooking_options,
        help="影响菜品制作方式选择"
    )

    # 维度6: 过敏史
    st.subheader("6. ⚠️ 过敏史")
    allergy_options = ["花生", "坚果", "虾蟹", "鸡蛋", "牛奶", "大豆", "麸质", "芝麻", "鱼类"]
    allergies = st.multiselect(
        "已知食物过敏",
        allergy_options,
        help="🚨 极其重要！关系食品安全"
    )

    if allergies:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ 过敏提醒</strong><br>
            您选择的过敏食物将被完全排除在推荐方案之外，请确保信息准确！
        </div>
        """, unsafe_allow_html=True)

    return {
        "preferred_cuisines": preferred_cuisines,
        "disliked_foods": disliked_foods,
        "dietary_restrictions": dietary_restrictions,
        "spice_tolerance": spice_tolerance,
        "cooking_preferences": cooking_preferences,
        "allergies": allergies
    }

def create_patient_profile(basic_info, health_status, dietary_preferences):
    """创建患者档案"""
    try:
        patient = PatientProfile(
            name=basic_info["name"],
            age=basic_info["age"],
            gender=basic_info["gender"],
            height=basic_info["height"],
            weight=basic_info["weight"],
            diagnosed_diseases=health_status["diagnosed_diseases"],
            blood_pressure_systolic=health_status["blood_pressure_systolic"],
            blood_pressure_diastolic=health_status["blood_pressure_diastolic"],
            blood_glucose_fasting=health_status["fasting_glucose"],  # 修正字段名
            hba1c=health_status["hba1c"],
            cholesterol_total=health_status["total_cholesterol"],    # 修正字段名
            triglycerides=health_status["triglycerides"],
            preferred_cuisines=dietary_preferences["preferred_cuisines"],
            disliked_foods=dietary_preferences["disliked_foods"],
            dietary_restrictions=dietary_preferences["dietary_restrictions"],
            spice_tolerance=dietary_preferences["spice_tolerance"],
            cooking_preferences=dietary_preferences["cooking_preferences"],
            allergies=dietary_preferences["allergies"]
        )
        return patient
    except Exception as e:
        st.error(f"创建患者档案失败: {e}")
        return None

def generate_comprehensive_analysis(patient):
    """生成综合分析"""
    try:
        # 营养系统分析
        nutrition_system = st.session_state.nutrition_system
        gi_system = st.session_state.gi_system

        # 获取个性化推荐
        recommendations = nutrition_system._recommend_recipes(patient)

        # 获取GI推荐
        gi_recommendations = gi_system.generate_personalized_gi_recommendations(patient)

        # 生成糖尿病膳食计划
        diabetes_plan = None
        if "糖尿病" in patient.diagnosed_diseases:
            diabetes_plan = gi_system.generate_diabetes_meal_plan(target_gl=15.0, patient=patient)

        # 生成完整报告
        full_report = nutrition_system.generate_comprehensive_report_v2(patient)

        return {
            "recommendations": recommendations,
            "gi_recommendations": gi_recommendations,
            "diabetes_plan": diabetes_plan,
            "full_report": full_report
        }
    except Exception as e:
        st.error(f"分析生成失败: {e}")
        return None

def render_analysis_results(analysis_results, patient):
    """渲染分析结果"""
    if not analysis_results:
        return

    st.markdown('<h2 class="section-header">📊 个性化分析结果</h2>', unsafe_allow_html=True)

    # 标签页布局
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 菜谱推荐", "🍚 GI血糖管理", "📈 健康指标", "📋 完整报告", "📊 可视化分析"])

    with tab1:
        render_recipe_recommendations(analysis_results["recommendations"], patient)

    with tab2:
        render_gi_analysis(analysis_results["gi_recommendations"], analysis_results["diabetes_plan"])

    with tab3:
        render_health_indicators(patient)

    with tab4:
        render_full_report(analysis_results["full_report"])

    with tab5:
        render_visualizations(patient, analysis_results)

def render_recipe_recommendations(recommendations, patient):
    """渲染菜谱推荐（集成CGM智能优化）"""
    st.subheader("🍽️ 个性化菜谱推荐")

    if not recommendations:
        st.warning("暂无推荐菜谱")
        return

    # 显示今日特别推荐
    import datetime
    today = datetime.datetime.now()
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    today_name = weekday_names[today.weekday()]

    st.info(f"📅 **今日 ({today_name}) 智能推荐** | 系统已为您配置7天不重复的营养菜谱")

    # 检查是否有CGM数据可用
    cgm_optimized = False
    if 'meal_analysis_history' in st.session_state and st.session_state.meal_analysis_history:
        cgm_optimized = True
        st.info("🧬 **CGM智能优化**: 推荐已基于您的血糖反应模式进行优化")

    # 创建两栏布局
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 推荐菜单")

        # 如果有CGM数据，则进行智能优化推荐
        if cgm_optimized:
            recommended_dishes = generate_cgm_optimized_recommendations(recommendations, patient)
        else:
            # 使用原始推荐
            recommended_dishes = {}
            meal_types = ["早餐推荐", "午餐推荐", "晚餐推荐", "加餐推荐"]
            for meal_type in meal_types:
                if meal_type in recommendations and recommendations[meal_type]:
                    dish_name_with_calories = recommendations[meal_type][0]
                    dish_name = dish_name_with_calories.split(" (")[0] if " (" in dish_name_with_calories else dish_name_with_calories
                    recommended_dishes[meal_type] = dish_name

        # 显示推荐菜单
        meal_types = ["早餐推荐", "午餐推荐", "晚餐推荐", "加餐推荐"]
        for meal_type in meal_types:
            if meal_type in recommended_dishes:
                with st.expander(f"🍽️ {meal_type}", expanded=True):
                    dish_name = recommended_dishes[meal_type]

                    # 如果是CGM优化的，显示优化信息
                    if cgm_optimized:
                        optimization_info = get_cgm_optimization_info(dish_name, meal_type)
                        st.write(f"**🧬 CGM优化推荐**: {dish_name}")
                        if optimization_info:
                            st.caption(f"💡 {optimization_info}")
                    else:
                        st.write(f"**推荐菜品**: {dish_name}")

                    # 显示预期血糖影响
                    glucose_impact = predict_glucose_impact(dish_name)
                    if glucose_impact:
                        if glucose_impact['level'] == 'low':
                            st.success(f"🟢 预期血糖影响: {glucose_impact['description']}")
                        elif glucose_impact['level'] == 'medium':
                            st.info(f"🟡 预期血糖影响: {glucose_impact['description']}")
                        else:
                            st.warning(f"🟠 预期血糖影响: {glucose_impact['description']}")

        # 显示个性化说明
        if "个性化说明" in recommendations:
            st.markdown("""
            <div class="success-box">
                <strong>💡 个性化说明</strong><br>
                """ + recommendations["个性化说明"] + """
            </div>
            """, unsafe_allow_html=True)

        # 显示注意事项
        if "注意事项" in recommendations:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ 注意事项</strong><br>
                """ + recommendations["注意事项"] + """
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("📊 菜谱营养雷达图")
        # 生成推荐菜谱的营养雷达图
        create_meal_nutrition_radar_chart(recommended_dishes, patient)

    # 添加一周菜谱展示
    st.subheader("📅 完整一周菜谱计划")
    st.info("🔄 **智能轮换**: 系统为您提供7天不重复的营养均衡菜谱，确保饮食多样性")

    # 获取一周菜谱
    try:
        from Core_Systems.weekly_menu_manager import WeeklyMenuManager
        weekly_manager = WeeklyMenuManager()

        # 根据患者偏好选择菜系
        selected_cuisine = "清淡"  # 默认
        if hasattr(patient, 'preferred_cuisines') and patient.preferred_cuisines:
            if '地中海' in patient.preferred_cuisines:
                selected_cuisine = "地中海"
            elif '日韩' in patient.preferred_cuisines:
                selected_cuisine = "日韩"
            elif '川菜' in patient.preferred_cuisines:
                selected_cuisine = "川菜"
            elif '粤菜' in patient.preferred_cuisines:
                selected_cuisine = "粤菜"

        # 添加选项来切换显示模式
        col1, col2 = st.columns([1, 4])
        with col1:
            show_detailed = st.checkbox("📏 显示详细重量", value=False, help="显示每个菜品的详细食材重量信息")

        if show_detailed:
            # 使用详细菜单
            detailed_weekly_menu = weekly_manager.get_detailed_weekly_menu(selected_cuisine)

            # 使用展开显示每天的详细信息
            for day, meals in detailed_weekly_menu['一周详细计划'].items():
                with st.expander(f"📅 {day} 详细菜谱", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.markdown("### 🌅 早餐")
                        st.write(f"**{meals['早餐']['菜品名称']}**")
                        if meals['早餐']['详细信息'] != "详细配方待补充，请参考基础营养建议":
                            st.markdown(meals['早餐']['详细信息'])
                        else:
                            st.info("详细配方待补充")

                    with col2:
                        st.markdown("### 🌞 午餐")
                        st.write(f"**{meals['午餐']['菜品名称']}**")
                        if meals['午餐']['详细信息'] != "详细配方待补充，请参考基础营养建议":
                            st.markdown(meals['午餐']['详细信息'])
                        else:
                            st.info("详细配方待补充")

                    with col3:
                        st.markdown("### 🌆 晚餐")
                        st.write(f"**{meals['晚餐']['菜品名称']}**")
                        if meals['晚餐']['详细信息'] != "详细配方待补充，请参考基础营养建议":
                            st.markdown(meals['晚餐']['详细信息'])
                        else:
                            st.info("详细配方待补充")

                    with col4:
                        st.markdown("### 🍪 加餐")
                        st.write(f"**{meals['加餐']['菜品名称']}**")
                        if meals['加餐']['详细信息'] != "详细配方待补充，请参考基础营养建议":
                            st.markdown(meals['加餐']['详细信息'])
                        else:
                            st.info("详细配方待补充")

            # 显示详细说明
            st.success(f"✨ **菜系风格**: {detailed_weekly_menu['菜系风格']} | {detailed_weekly_menu['特色说明']}")
            st.info(f"📏 **重量说明**: {detailed_weekly_menu['重量说明']}")

        else:
            # 使用简化菜单（原来的显示方式）
            weekly_menu = weekly_manager.get_weekly_menu(selected_cuisine)

            # 创建一周菜谱表格
            import pandas as pd

            # 构建表格数据
            table_data = []
            for day, meals in weekly_menu['一周计划'].items():
                table_data.append({
                    "星期": day,
                    "🌅 早餐": meals['早餐'],
                    "🌞 午餐": meals['午餐'],
                    "🌆 晚餐": meals['晚餐'],
                    "🍪 加餐": meals['加餐']
                })

            # 创建DataFrame并显示表格
            df = pd.DataFrame(table_data)

            # 使用streamlit的表格显示，设置样式
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "星期": st.column_config.TextColumn("星期", width="small"),
                    "🌅 早餐": st.column_config.TextColumn("🌅 早餐", width="medium"),
                    "🌞 午餐": st.column_config.TextColumn("🌞 午餐", width="medium"),
                    "🌆 晚餐": st.column_config.TextColumn("🌆 晚餐", width="medium"),
                    "🍪 加餐": st.column_config.TextColumn("🍪 加餐", width="medium")
                }
            )

            # 显示特色说明
            st.success(f"✨ **菜系风格**: {weekly_menu['菜系风格']} | {weekly_menu['特色说明']}")
            st.info("💡 **提示**: 勾选上方'显示详细重量'可查看每个菜品的具体食材重量信息")

    except Exception as e:
        st.error(f"一周菜谱加载失败: {e}")

def render_gi_analysis(gi_recommendations, diabetes_plan):
    """渲染GI分析"""
    st.subheader("🍚 血糖生成指数分析")

    if gi_recommendations:
        # 显示GI推荐
        for category, items in gi_recommendations.items():
            if isinstance(items, list) and items:
                st.write(f"**{category}**: {items[0]}")
            elif isinstance(items, str):
                st.write(f"**{category}**: {items}")

    if diabetes_plan:
        st.subheader("📋 糖尿病专用膳食计划")

        for category, foods in diabetes_plan.items():
            if category != "个性化说明" and isinstance(foods, list) and foods:
                st.write(f"**{category}**: {foods[0]}")

        if "个性化说明" in diabetes_plan and diabetes_plan["个性化说明"]:
            st.info(f"💡 {diabetes_plan['个性化说明'][0]}")

def render_health_indicators(patient):
    """渲染健康指标"""
    st.subheader("📈 健康指标评估")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("BMI", f"{patient.bmi:.1f}", patient.bmi_category)

    with col2:
        bp_status = get_bp_status(patient.blood_pressure_systolic, patient.blood_pressure_diastolic)
        st.metric("血压", f"{patient.blood_pressure_systolic}/{patient.blood_pressure_diastolic}", bp_status)

    with col3:
        glucose_status = get_glucose_status(patient.blood_glucose_fasting)
        st.metric("空腹血糖", f"{patient.blood_glucose_fasting:.1f}", glucose_status)

    with col4:
        hba1c_status = get_hba1c_status(patient.hba1c)
        st.metric("糖化血红蛋白", f"{patient.hba1c:.1f}%", hba1c_status)

    # 风险评估
    st.subheader("🎯 风险评估")
    risk_factors = analyze_risk_factors(patient)

    for risk, level in risk_factors.items():
        color = get_risk_color(level)
        st.markdown(f"- **{risk}**: <span style='color: {color}'>{level}</span>", unsafe_allow_html=True)

def get_bp_status(systolic, diastolic):
    """获取血压状态"""
    if systolic < 120 and diastolic < 80:
        return "正常"
    elif systolic < 140 and diastolic < 90:
        return "偏高"
    else:
        return "高血压"

def get_glucose_status(glucose):
    """获取血糖状态"""
    if glucose < 6.1:
        return "正常"
    elif glucose < 7.0:
        return "偏高"
    else:
        return "糖尿病"

def get_hba1c_status(hba1c):
    """获取糖化血红蛋白状态"""
    if hba1c < 5.7:
        return "正常"
    elif hba1c < 6.5:
        return "前期"
    else:
        return "糖尿病"

def analyze_risk_factors(patient):
    """分析风险因素"""
    risks = {}

    # BMI风险
    if patient.bmi >= 28:
        risks["肥胖风险"] = "高"
    elif patient.bmi >= 24:
        risks["超重风险"] = "中"
    else:
        risks["体重状态"] = "正常"

    # 血压风险
    if patient.blood_pressure_systolic >= 140:
        risks["高血压风险"] = "高"
    elif patient.blood_pressure_systolic >= 120:
        risks["血压风险"] = "中"

    # 血糖风险
    if patient.blood_glucose_fasting >= 7.0:
        risks["糖尿病风险"] = "高"
    elif patient.blood_glucose_fasting >= 6.1:
        risks["糖尿病风险"] = "中"

    return risks

def get_risk_color(level):
    """获取风险颜色"""
    if level == "高":
        return "#dc3545"
    elif level == "中":
        return "#ffc107"
    else:
        return "#28a745"

def render_full_report(full_report):
    """渲染完整报告"""
    st.subheader("📋 完整营养评估报告")

    if full_report:
        # 显示报告的前500字符作为预览
        preview = full_report[:500] + "..." if len(full_report) > 500 else full_report
        st.text_area("报告预览", preview, height=300)

        # 提供下载功能
        st.download_button(
            label="📥 下载完整报告",
            data=full_report,
            file_name=f"营养评估报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    else:
        st.warning("报告生成失败")

def render_visualizations(patient, analysis_results):
    """渲染可视化分析"""
    st.subheader("📊 数据可视化分析")

    # 健康指标雷达图
    create_health_radar_chart(patient)

    # 营养素分布图
    create_nutrition_distribution_chart(analysis_results)

    # 偏好匹配度图
    create_preference_matching_chart(patient)

def create_health_radar_chart(patient):
    """创建健康指标雷达图"""
    st.subheader("🎯 健康指标雷达图")

    # 健康指标评分（0-10分）
    health_scores = {
        "BMI": get_health_score("bmi", patient.bmi),
        "血压": get_health_score("bp", patient.blood_pressure_systolic),
        "血糖": get_health_score("glucose", patient.blood_glucose_fasting),
        "糖化血红蛋白": get_health_score("hba1c", patient.hba1c),
        "胆固醇": get_health_score("cholesterol", patient.cholesterol_total),
        "甘油三酯": get_health_score("triglycerides", patient.triglycerides)
    }

    # 创建雷达图
    categories = list(health_scores.keys())
    values = list(health_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='健康状态',
        fillcolor='rgba(0, 100, 80, 0.3)',
        line=dict(color='rgba(0, 100, 80, 1)')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="健康指标评估雷达图"
    )

    st.plotly_chart(fig, use_container_width=True)

def get_health_score(indicator, value):
    """获取健康指标评分"""
    scores = {
        "bmi": {
            "ranges": [(0, 18.5, 6), (18.5, 24, 10), (24, 28, 7), (28, 35, 4), (35, 50, 2)],
            "default": 1
        },
        "bp": {
            "ranges": [(0, 120, 10), (120, 140, 7), (140, 160, 4), (160, 200, 2)],
            "default": 1
        },
        "glucose": {
            "ranges": [(0, 6.1, 10), (6.1, 7.0, 6), (7.0, 11.0, 3), (11.0, 20, 1)],
            "default": 1
        },
        "hba1c": {
            "ranges": [(0, 5.7, 10), (5.7, 6.5, 6), (6.5, 8.0, 3), (8.0, 12, 1)],
            "default": 1
        },
        "cholesterol": {
            "ranges": [(0, 5.2, 10), (5.2, 6.2, 6), (6.2, 8.0, 3), (8.0, 15, 1)],
            "default": 1
        },
        "triglycerides": {
            "ranges": [(0, 1.7, 10), (1.7, 2.3, 6), (2.3, 5.0, 3), (5.0, 10, 1)],
            "default": 1
        }
    }

    if indicator in scores:
        for min_val, max_val, score in scores[indicator]["ranges"]:
            if min_val <= value < max_val:
                return score
        return scores[indicator]["default"]

    return 5  # 默认中等分数

def create_nutrition_distribution_chart(analysis_results):
    """创建营养分布图"""
    st.subheader("🥗 推荐菜系分布")

    # 模拟菜系分布数据
    cuisine_data = {
        "菜系": ["清淡", "粤菜", "苏菜", "浙菜", "其他"],
        "推荐数量": [4, 3, 2, 1, 1]
    }

    df = pd.DataFrame(cuisine_data)

    fig = px.pie(df, values="推荐数量", names="菜系", title="个性化菜系推荐分布")
    st.plotly_chart(fig, use_container_width=True)

def create_preference_matching_chart(patient):
    """创建偏好匹配度图"""
    st.subheader("🎯 个性化匹配度分析")

    # 计算各维度匹配度
    matching_scores = {
        "菜系偏好": 0.9 if patient.preferred_cuisines else 0.5,
        "安全性": 1.0 if patient.allergies else 0.8,
        "限制遵守": 0.95 if patient.dietary_restrictions else 0.7,
        "口味适配": 0.8,
        "营养需求": 0.85,
        "制作偏好": 0.7 if patient.cooking_preferences else 0.5
    }

    df = pd.DataFrame(list(matching_scores.items()), columns=["维度", "匹配度"])

    fig = px.bar(df, x="维度", y="匹配度",
                 color="匹配度",
                 color_continuous_scale="RdYlGn",
                 title="六维度个性化匹配度评估")

    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)

def create_meal_nutrition_radar_chart(recommended_dishes, patient):
    """创建推荐菜谱的营养雷达图"""
    if not recommended_dishes:
        st.warning("暂无推荐菜谱用于分析")
        return

    # 定义营养维度和理想值
    nutrition_dimensions = ["蛋白质", "碳水化合物", "脂肪", "纤维", "维生素", "矿物质", "抗氧化物", "适宜性"]

    # 优化的高质量营养数据库 - 确保所有推荐菜品的关键指标都达到高标准
    nutrition_database = {
        # === 高质量早餐类 - 蛋白质≥8，适宜性≥9 ===
        "燕麦鸡蛋套餐": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 6, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 7, "适宜性": 10},
        "牛奶燕麦": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 4, "纤维": 7, "维生素": 8, "矿物质": 9, "抗氧化物": 6, "适宜性": 9},
        "煎蛋三明治": {"蛋白质": 9, "碳水化合物": 6, "脂肪": 7, "纤维": 5, "维生素": 8, "矿物质": 7, "抗氧化物": 6, "适宜性": 9},
        "豆腐脑配菜": {"蛋白质": 8, "碳水化合物": 5, "脂肪": 4, "纤维": 6, "维生素": 7, "矿物质": 8, "抗氧化物": 7, "适宜性": 9},
        "蒸蛋羹配面包": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 6, "纤维": 4, "维生素": 8, "矿物质": 7, "抗氧化物": 6, "适宜性": 9},
        "豆浆油条": {"蛋白质": 7, "碳水化合物": 8, "脂肪": 6, "纤维": 4, "维生素": 6, "矿物质": 7, "抗氧化物": 5, "适宜性": 7},
        # 新增早餐菜品
        "全麦面包加鸡蛋": {"蛋白质": 9, "碳水化合物": 6, "脂肪": 6, "纤维": 7, "维生素": 8, "矿物质": 7, "抗氧化物": 6, "适宜性": 9},
        "鸡蛋灶饼配粥": {"蛋白质": 8, "碳水化合物": 8, "脂肪": 6, "纤维": 5, "维生素": 7, "矿物质": 7, "抗氧化物": 5, "适宜性": 9},
        "蒸蛋羹配小米粥": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 5, "纤维": 6, "维生素": 8, "矿物质": 8, "抗氧化物": 6, "适宜性": 10},
        "红薯鸡蛋粥": {"蛋白质": 8, "碳水化合物": 8, "脂肪": 4, "纤维": 7, "维生素": 9, "矿物质": 7, "抗氧化物": 8, "适宜性": 9},
        "白粥配鸡蛋": {"蛋白质": 8, "碳水化合物": 8, "脂肪": 6, "纤维": 3, "维生素": 7, "矿物质": 6, "抗氧化物": 4, "适宜性": 8},
        "红豆薄饬+鸡蛋": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 6, "纤维": 8, "维生素": 8, "矿物质": 8, "抗氧化物": 7, "适宜性": 9},
        "牛奶麦片": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 4, "纤维": 6, "维生素": 8, "矿物质": 9, "抗氧化物": 6, "适宜性": 9},
        "葱花鸡蛋饼": {"蛋白质": 9, "碳水化合物": 6, "脂肪": 7, "纤维": 4, "维生素": 7, "矿物质": 6, "抗氧化物": 5, "适宜性": 8},
        "红薯糙米粥": {"蛋白质": 6, "碳水化合物": 8, "脂肪": 2, "纤维": 8, "维生素": 9, "矿物质": 7, "抗氧化物": 8, "适宜性": 9},
        "豆浆加鸡蛋": {"蛋白质": 9, "碳水化合物": 5, "脂肪": 6, "纤维": 4, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},
        "小米鸡蛋粥": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 5, "纤维": 6, "维生素": 8, "矿物质": 8, "抗氧化物": 6, "适宜性": 10},

        # === 优质午餐类 - 蛋白质≥9，营养均衡≥8，适宜性≥9 ===
        "清蒸鲈鱼配糙米": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 4, "纤维": 6, "维生素": 8, "矿物质": 9, "抗氧化物": 7, "适宜性": 10},
        "清炖鸡汤配饭": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 5, "纤维": 5, "维生素": 8, "矿物质": 8, "抗氧化物": 6, "适宜性": 10},
        "清蒸鸡胸肉": {"蛋白质": 10, "碳水化合物": 1, "脂肪": 3, "纤维": 0, "维生素": 7, "矿物质": 6, "抗氧化物": 4, "适宜性": 10},
        "豆腐蔬菜汤": {"蛋白质": 8, "碳水化合物": 5, "脂肪": 3, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 9, "适宜性": 10},
        "白切鸡配米饭": {"蛋白质": 9, "碳水化合物": 8, "脂肪": 5, "纤维": 4, "维生素": 7, "矿物质": 7, "抗氧化物": 5, "适宜性": 9},
        "水煮虾仁": {"蛋白质": 10, "碳水化合物": 1, "脂肪": 2, "纤维": 0, "维生素": 7, "矿物质": 9, "抗氧化物": 5, "适宜性": 9},
        # 新增午餐菜品
        "麦片鸡蛋粥": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 5, "纤维": 6, "维生素": 8, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},
        "蒸蛋羹配糙米": {"蛋白质": 8, "碳水化合物": 6, "脂肪": 5, "纤维": 5, "维生素": 8, "矿物质": 7, "抗氧化物": 6, "适宜性": 10},
        "豆腐鱼头汤": {"蛋白质": 9, "碳水化合物": 4, "脂肪": 5, "纤维": 6, "维生素": 8, "矿物质": 9, "抗氧化物": 7, "适宜性": 10},
        "清炒鸡丝配面条": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 5, "纤维": 5, "维生素": 7, "矿物质": 7, "抗氧化物": 6, "适宜性": 9},
        "蒸虾仁配糙米": {"蛋白质": 10, "碳水化合物": 6, "脂肪": 3, "纤维": 5, "维生素": 8, "矿物质": 9, "抗氧化物": 6, "适宜性": 10},
        "白灼菜心配鱼片": {"蛋白质": 9, "碳水化合物": 4, "脂肪": 4, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 8, "适宜性": 10},
        "蒸水蛋配米饭": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 6, "纤维": 3, "维生素": 8, "矿物质": 7, "抗氧化物": 5, "适宜性": 9},
        "鱼肉粥": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 4, "纤维": 4, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 10},
        "白煮鸡蛋配米饭": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 6, "纤维": 3, "维生素": 8, "矿物质": 7, "抗氧化物": 5, "适宜性": 9},
        "蒸虾仁配蔬菜": {"蛋白质": 10, "碳水化合物": 3, "脂肪": 2, "纤维": 8, "维生素": 9, "矿物质": 9, "抗氧化物": 8, "适宜性": 10},
        "清炖肉片汤": {"蛋白质": 9, "碳水化合物": 3, "脂肪": 4, "纤维": 5, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},

        # === 优质晚餐类 - 清淡易消化，蛋白质≥7，适宜性≥9 ===
        "蒸蛋羹+青菜": {"蛋白质": 8, "碳水化合物": 4, "脂肪": 5, "纤维": 8, "维生素": 8, "矿物质": 7, "抗氧化物": 8, "适宜性": 10},
        "蔬菜豆腐汤": {"蛋白质": 8, "碳水化合物": 4, "脂肪": 3, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 9, "适宜性": 10},
        "荞麦面配蔬菜": {"蛋白质": 7, "碳水化合物": 8, "脂肪": 2, "纤维": 9, "维生素": 8, "矿物质": 7, "抗氧化物": 8, "适宜性": 9},
        "冬瓜排骨汤": {"蛋白质": 7, "碳水化合物": 3, "脂肪": 4, "纤维": 6, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},
        # 新增晚餐菜品
        "冬瓜丸子汤": {"蛋白质": 7, "碳水化合物": 4, "脂肪": 4, "纤维": 7, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},
        "紫菜蛋花汤": {"蛋白质": 7, "碳水化合物": 3, "脂肪": 4, "纤维": 6, "维生素": 8, "矿物质": 9, "抗氧化物": 7, "适宜性": 10},
        "青菜豆腐汤": {"蛋白质": 8, "碳水化合物": 4, "脂肪": 3, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 9, "适宜性": 10},
        "白萝卜炒蛋": {"蛋白质": 8, "碳水化合物": 5, "脂肪": 6, "纤维": 7, "维生素": 8, "矿物质": 7, "抗氧化物": 7, "适宜性": 9},
        "小白菜豆腐汤": {"蛋白质": 8, "碳水化合物": 4, "脂肪": 3, "纤维": 8, "维生素": 9, "矿物质": 8, "抗氧化物": 9, "适宜性": 10},
        "蒸蛋羹": {"蛋白质": 8, "碳水化合物": 2, "脂肪": 6, "纤维": 0, "维生素": 7, "矿物质": 6, "抗氧化物": 4, "适宜性": 10},
        "青菜瘦肉汤": {"蛋白质": 8, "碳水化合物": 3, "脂肪": 3, "纤维": 7, "维生素": 8, "矿物质": 8, "抗氧化物": 7, "适宜性": 9},

        # === 优质加餐类 - 营养补充，适宜性≥9 ===
        "水煮蛋": {"蛋白质": 9, "碳水化合物": 1, "脂肪": 7, "纤维": 0, "维生素": 8, "矿物质": 6, "抗氧化物": 4, "适宜性": 10},
        "酸奶": {"蛋白质": 7, "碳水化合物": 5, "脂肪": 4, "纤维": 2, "维生素": 7, "矿物质": 8, "抗氧化物": 6, "适宜性": 9},
        "蓝莓酸奶": {"蛋白质": 7, "碳水化合物": 6, "脂肪": 3, "纤维": 5, "维生素": 9, "矿物质": 6, "抗氧化物": 10, "适宜性": 9},
        "牛奶": {"蛋白质": 8, "碳水化合物": 5, "脂肪": 4, "纤维": 0, "维生素": 8, "矿物质": 9, "抗氧化物": 5, "适宜性": 9},
        "柚子片": {"蛋白质": 1, "碳水化合物": 6, "脂肪": 0, "纤维": 8, "维生素": 9, "矿物质": 5, "抗氧化物": 9, "适宜性": 10},
        "苹果片": {"蛋白质": 1, "碳水化合物": 7, "脂肪": 0, "纤维": 7, "维生素": 8, "矿物质": 4, "抗氧化物": 8, "适宜性": 9},
        "核桃仁": {"蛋白质": 6, "碳水化合物": 4, "脂肪": 8, "纤维": 6, "维生素": 7, "矿物质": 8, "抗氧化物": 8, "适宜性": 9},
        "奶酸鸡蛋粥": {"蛋白质": 7, "碳水化合物": 6, "脂肪": 4, "纤维": 3, "维生素": 7, "矿物质": 7, "抗氧化物": 6, "适宜性": 9},
        "红枣豆浆": {"蛋白质": 6, "碳水化合物": 6, "脂肪": 3, "纤维": 5, "维生素": 8, "矿物质": 8, "抗氧化物": 7, "适宜性": 9},
        "香蕉": {"蛋白质": 2, "碳水化合物": 8, "脂肪": 0, "纤维": 6, "维生素": 8, "矿物质": 6, "抗氧化物": 7, "适宜性": 9},
        "默认早餐": {"蛋白质": 8, "碳水化合物": 7, "脂肪": 5, "纤维": 7, "维生素": 8, "矿物质": 8, "抗氧化物": 7, "适宜性": 9},
        "默认午餐": {"蛋白质": 9, "碳水化合物": 7, "脂肪": 5, "纤维": 7, "维生素": 8, "矿物质": 8, "抗氧化物": 7, "适宜性": 10},
        "默认晚餐": {"蛋白质": 8, "碳水化合物": 6, "脂肪": 4, "纤维": 8, "维生素": 8, "矿物质": 7, "抗氧化物": 8, "适宜性": 9},
        "默认加餐": {"蛋白质": 8, "碳水化合物": 5, "脂肪": 3, "纤维": 6, "维生素": 8, "矿物质": 7, "抗氧化物": 7, "适宜性": 9}
    }

    # 颜色配置 - 增强对比度和区分度
    colors = {
        "早餐推荐": "rgba(255, 99, 132, 0.3)",   # 红色，透明度降低
        "午餐推荐": "rgba(54, 162, 235, 0.3)",   # 蓝色，透明度降低
        "晚餐推荐": "rgba(75, 192, 192, 0.3)",   # 绿色，透明度降低
        "加餐推荐": "rgba(255, 206, 86, 0.3)"    # 黄色，透明度降低
    }

    line_colors = {
        "早餐推荐": "rgba(255, 99, 132, 1)",    # 红色边框
        "午餐推荐": "rgba(54, 162, 235, 1)",    # 蓝色边框
        "晚餐推荐": "rgba(75, 192, 192, 1)",    # 绿色边框
        "加餐推荐": "rgba(255, 206, 86, 1)"     # 黄色边框
    }

    # 线条样式配置
    line_styles = {
        "早餐推荐": dict(width=3, dash=None),          # 实线
        "午餐推荐": dict(width=3, dash=None),          # 实线
        "晚餐推荐": dict(width=3, dash=None),          # 实线
        "加餐推荐": dict(width=3, dash='dot')          # 点线
    }

    # 创建雷达图
    fig = go.Figure()

    for meal_type, dish_name in recommended_dishes.items():
        # 获取营养数据
        nutrition_values = nutrition_database.get(dish_name, {
            "蛋白质": 5, "碳水化合物": 5, "脂肪": 5, "纤维": 5,
            "维生素": 5, "矿物质": 5, "抗氧化物": 5, "适宜性": 5
        })

        # 提取数值
        values = [nutrition_values[dim] for dim in nutrition_dimensions]

        # 添加轨迹 - 使用新的样式配置
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=nutrition_dimensions,
            fill='toself',
            name=f"{meal_type.replace('推荐', '')} - {dish_name}",
            fillcolor=colors[meal_type],
            line=dict(color=line_colors[meal_type], **line_styles[meal_type]),
            marker=dict(size=8, color=line_colors[meal_type])
        ))

    # 添加理想营养线
    ideal_values = [8, 7, 5, 8, 8, 8, 7, 9]  # 理想营养值
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=nutrition_dimensions,
        fill=None,
        name="理想营养标准",
        line=dict(color='rgba(128, 128, 128, 0.8)', width=2, dash='dash'),
        marker=dict(size=4)
    ))

    # 更新布局
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                ticktext=['差', '一般', '良好', '优秀', '完美'],
                gridcolor='rgba(128, 128, 128, 0.3)'
            ),
            angularaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.3)'
            )
        ),
        showlegend=True,
        title={
            'text': "推荐菜谱营养成分雷达图",
            'x': 0.5,
            'font': {'size': 16}
        },
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05,
            font=dict(size=10)
        ),
        height=500,
        margin=dict(l=50, r=150, t=80, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加营养分析说明
    st.markdown("""
    **📊 营养雷达图说明**:
    - **蛋白质**: 肌肉修复和免疫功能
    - **碳水化合物**: 主要能量来源
    - **脂肪**: 必需脂肪酸和维生素吸收
    - **纤维**: 消化健康和血糖控制
    - **维生素**: 代谢调节和抗氧化
    - **矿物质**: 骨骼健康和电解质平衡
    - **抗氧化物**: 细胞保护和抗衰老
    - **适宜性**: 针对患者疾病状况的适合程度

    **🎯 评分标准**: 0-10分，分值越高表示该营养维度越优秀
    """)

    # 营养总结分析
    if len(recommended_dishes) >= 3:
        st.subheader("📈 全天营养均衡分析")

        total_nutrition = {}
        st.write("**🔍 营养数据匹配检查**:")

        for dim in nutrition_dimensions:
            total_nutrition[dim] = 0
            count = 0
            dim_details = []

            for meal_type, dish_name in recommended_dishes.items():
                nutrition_values = nutrition_database.get(dish_name, {})
                if nutrition_values:
                    if dim in nutrition_values:
                        value = nutrition_values[dim]
                        # 加餐权重降低
                        weight = 0.5 if meal_type == "加餐推荐" else 1.0
                        total_nutrition[dim] += value * weight
                        count += weight
                        dim_details.append(f"{meal_type.replace('推荐', '')}: {dish_name}({value}分)")
                    else:
                        dim_details.append(f"{meal_type.replace('推荐', '')}: {dish_name}(数据缺失)")
                else:
                    dim_details.append(f"{meal_type.replace('推荐', '')}: {dish_name}(❌未找到营养数据)")

            if count > 0:
                total_nutrition[dim] = total_nutrition[dim] / count

            # 调试信息
            st.write(f"- **{dim}**: {', '.join(dim_details)} → 平均{total_nutrition[dim]:.1f}分")

        # 营养均衡度评估（优化评分标准）
        balance_score = sum(total_nutrition.values()) / len(nutrition_dimensions)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("营养均衡度", f"{balance_score:.1f}/10",
                     "优秀" if balance_score >= 7 else "良好" if balance_score >= 5 else "需改进")

        with col2:
            protein_avg = total_nutrition.get("蛋白质", 0)
            st.metric("蛋白质充足度", f"{protein_avg:.1f}/10",
                     "充足" if protein_avg >= 7 else "适中" if protein_avg >= 5 else "不足")

        with col3:
            suitability_avg = total_nutrition.get("适宜性", 0)
            st.metric("疾病适宜性", f"{suitability_avg:.1f}/10",
                     "高度适宜" if suitability_avg >= 8 else "适宜" if suitability_avg >= 6 else "需调整")

def main():
    """主函数"""
    # 初始化
    initialize_session_state()

    # 渲染主标题
    render_main_header()

    # 侧边栏导航
    st.sidebar.title("📋 导航菜单")
    page = st.sidebar.selectbox(
        "选择页面",
        ["数据填写", "分析结果", "CGM血糖管理", "系统说明"]
    )

    if page == "数据填写":
        st.sidebar.markdown("---")
        st.sidebar.info("请按步骤填写患者信息，系统将自动生成个性化营养分析报告。")

        # 数据填写表单
        with st.form("patient_form"):
            basic_info = render_basic_info_form()
            health_status = render_health_status_form()
            dietary_preferences = render_dietary_preferences_form()

            submitted = st.form_submit_button("🎯 生成个性化分析", type="primary")

            if submitted:
                if not basic_info["name"]:
                    st.error("请填写患者姓名")
                    return

                # 创建患者档案
                patient = create_patient_profile(basic_info, health_status, dietary_preferences)

                if patient:
                    st.session_state.patient_data["patient"] = patient

                    # 生成分析
                    with st.spinner("正在生成个性化分析..."):
                        analysis = generate_comprehensive_analysis(patient)
                        if analysis:
                            st.session_state.patient_data["analysis"] = analysis
                            st.success("✅ 分析生成成功！请查看'分析结果'页面。")
                        else:
                            st.error("分析生成失败，请检查数据后重试。")

    elif page == "分析结果":
        if "patient" in st.session_state.patient_data and "analysis" in st.session_state.patient_data:
            patient = st.session_state.patient_data["patient"]
            analysis = st.session_state.patient_data["analysis"]

            # 显示患者基本信息
            st.markdown(f"""
            <div class="info-box">
                <h4>👤 患者: {patient.name}</h4>
                <p>年龄: {patient.age}岁 | 性别: {patient.gender} | BMI: {patient.bmi:.1f} ({patient.bmi_category})</p>
                <p>疾病: {', '.join(patient.diagnosed_diseases) if patient.diagnosed_diseases else '无'}</p>
            </div>
            """, unsafe_allow_html=True)

            # 渲染分析结果
            render_analysis_results(analysis, patient)
        else:
            st.warning("请先在'数据填写'页面完成患者信息填写和分析生成。")

    elif page == "CGM血糖管理":
        render_cgm_management_page()

    elif page == "系统说明":
        render_system_description()

def render_system_description():
    """渲染系统说明"""
    st.markdown('<h2 class="section-header">📖 系统说明</h2>', unsafe_allow_html=True)

    st.markdown("""
    ## 🎯 系统概述

    个性化营养管理系统是一个基于现代营养学和循证医学的综合性中式营养管理平台，
    集成了患者分层、疾病支持、饮食偏好管理、血糖指数数据库和营养可视化等功能。

    ## 🏥 核心功能

    ### 1. 患者风险分层
    - 基于35个维度的综合健康评估
    - Harris-Benedict公式精确代谢计算
    - 多疾病并发症风险评估

    ### 2. 饮食偏好六维度管理
    - **偏好菜系**: 支持8大传统菜系个性化推荐
    - **不喜食物**: 智能排除不接受的食材
    - **饮食限制**: 严格遵守宗教和医疗限制
    - **辣度承受**: 四级辣度精准适配
    - **烹饪偏好**: 六种烹饪方式健康优化
    - **过敏史**: 100%安全筛选过敏原

    ### 3. 疾病营养支持
    - 支持35+种常见疾病
    - 疾病特异性营养方案
    - 个性化监测计划

    ### 4. GI血糖管理
    - 95种食物血糖生成指数数据库
    - 糖尿病专用膳食规划
    - 血糖负荷精确计算

    ### 5. 可视化分析
    - 营养成分雷达图
    - 健康指标评估图表
    - 偏好匹配度分析

    ## 🔬 科学依据

    - **营养学标准**: 基于中国居民膳食指南2022版
    - **医学证据**: 遵循循证医学原理
    - **国际标准**: 参考WHO、ADA等权威机构建议
    - **个性化**: 结合基因营养学最新研究成果

    ## 📋 使用流程

    1. **填写基本信息**: 年龄、性别、身高、体重等
    2. **录入健康状况**: 疾病史、生理指标、用药情况
    3. **设置饮食偏好**: 六维度详细偏好配置
    4. **生成分析报告**: AI自动生成个性化方案
    5. **查看结果**: 多角度可视化分析展示

    ## ⚠️ 注意事项

    - 本系统生成的建议仅供参考
    - 具体饮食方案请咨询专业营养师或医生
    - 特殊疾病患者需在医生指导下使用
    - 系统不能替代专业医疗诊断

    ## 📞 技术支持

    如有问题或建议，请联系系统管理员。
    """)

def render_cgm_management_page():
    """渲染CGM血糖管理页面"""
    st.markdown('<h2 class="section-header">📊 CGM血糖管理与营养优化</h2>', unsafe_allow_html=True)

    st.info("💡 本页面结合连续血糖监测(CGM)数据，提供个性化营养推荐优化")

    # 初始化CGM集成系统
    if 'cgm_integration' not in st.session_state:
        st.session_state.cgm_integration = CGMNutritionIntegration()

    cgm_system = st.session_state.cgm_integration

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 CGM数据上传", "🍽️ 餐后血糖分析", "🎯 个性化推荐", "📈 血糖趋势"
    ])

    with tab1:
        render_cgm_data_upload()

    with tab2:
        render_meal_glucose_analysis()

    with tab3:
        render_cgm_based_recommendations()

    with tab4:
        render_glucose_trend_analysis()

def render_cgm_data_upload():
    """CGM数据上传功能"""
    st.subheader("📱 CGM数据上传与管理")

    # 数据上传方式选择
    upload_method = st.radio(
        "选择数据输入方式",
        ["文件上传", "手动输入", "模拟数据"]
    )

    if upload_method == "文件上传":
        st.markdown("### 📁 上传CGM数据文件")
        st.info("支持CSV格式，需要包含时间戳和血糖值列")

        uploaded_file = st.file_uploader(
            "选择CGM数据文件",
            type=['csv'],
            help="CSV文件应包含 'timestamp' 和 'glucose' 列"
        )

        if uploaded_file:
            try:
                cgm_data = pd.read_csv(uploaded_file)
                cgm_data['timestamp'] = pd.to_datetime(cgm_data['timestamp'])

                # 数据预览
                st.success(f"✅ 成功加载 {len(cgm_data)} 条血糖记录")
                st.dataframe(cgm_data.head(10))

                # 保存到session state
                st.session_state.cgm_data = cgm_data

                # 数据质量检查
                render_cgm_data_quality_check(cgm_data)

            except Exception as e:
                st.error(f"❌ 文件读取失败: {str(e)}")

    elif upload_method == "手动输入":
        st.markdown("### ✏️ 手动输入血糖数据")

        with st.form("manual_glucose_input"):
            col1, col2 = st.columns(2)

            with col1:
                measurement_date = st.date_input(
                    "测量日期",
                    value=datetime.date.today(),
                    help="选择血糖测量的日期"
                )
                measurement_time_input = st.time_input(
                    "测量时间",
                    value=datetime.datetime.now().time(),
                    help="选择血糖测量的具体时间"
                )
                # 合并日期和时间
                measurement_time = datetime.datetime.combine(measurement_date, measurement_time_input)

            with col2:
                glucose_value = st.number_input(
                    "血糖值 (mmol/L)",
                    min_value=1.0,
                    max_value=30.0,
                    value=6.5,
                    step=0.1,
                    help="输入血糖测量值"
                )

            meal_context = st.selectbox(
                "测量时机",
                ["空腹", "餐前", "餐后1小时", "餐后2小时", "睡前", "其他"]
            )

            notes = st.text_area("备注", placeholder="可选：记录当时的饮食、运动等情况")

            if st.form_submit_button("添加记录"):
                # 添加到数据记录中
                if 'manual_glucose_records' not in st.session_state:
                    st.session_state.manual_glucose_records = []

                record = {
                    'timestamp': measurement_time,
                    'glucose': glucose_value,
                    'context': meal_context,
                    'notes': notes
                }

                st.session_state.manual_glucose_records.append(record)
                st.success("✅ 血糖记录已添加")

        # 显示已输入的记录
        if 'manual_glucose_records' in st.session_state and st.session_state.manual_glucose_records:
            st.markdown("### 📋 已输入的血糖记录")
            records_df = pd.DataFrame(st.session_state.manual_glucose_records)
            st.dataframe(records_df)

    else:  # 模拟数据
        st.markdown("### 🧪 使用模拟CGM数据")
        st.info("为演示目的生成模拟的CGM数据")

        if st.button("生成模拟数据"):
            # 生成24小时模拟CGM数据
            mock_data = generate_mock_cgm_data()
            st.session_state.cgm_data = mock_data

            st.success(f"✅ 生成了 {len(mock_data)} 条模拟血糖记录")

            # 显示数据预览
            fig = px.line(
                mock_data,
                x='timestamp',
                y='glucose',
                title="24小时模拟CGM数据",
                labels={'glucose': '血糖值 (mmol/L)', 'timestamp': '时间'}
            )
            fig.add_hline(y=3.9, line_dash="dash", line_color="red", annotation_text="低血糖线")
            fig.add_hline(y=10.0, line_dash="dash", line_color="orange", annotation_text="高血糖线")
            st.plotly_chart(fig, use_container_width=True)

def render_cgm_data_quality_check(cgm_data):
    """CGM数据质量检查"""
    st.markdown("### 🔍 数据质量检查")

    # 基本统计
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("记录总数", len(cgm_data))

    with col2:
        duration = (cgm_data['timestamp'].max() - cgm_data['timestamp'].min()).days
        st.metric("监测天数", f"{duration}天")

    with col3:
        completeness = (1 - cgm_data['glucose'].isna().sum() / len(cgm_data)) * 100
        st.metric("数据完整性", f"{completeness:.1f}%")

    with col4:
        avg_glucose = cgm_data['glucose'].mean()
        st.metric("平均血糖", f"{avg_glucose:.1f} mmol/L")

    # 数据质量警告
    if completeness < 90:
        st.warning("⚠️ 数据完整性较低，可能影响分析结果的准确性")

    if len(cgm_data) < 288:  # 24小时 × 12次/小时
        st.warning("⚠️ 数据量较少，建议至少有24小时的连续监测数据")

def render_meal_glucose_analysis():
    """餐后血糖分析功能"""
    st.subheader("🍽️ 餐后血糖反应分析")

    if 'cgm_data' not in st.session_state:
        st.warning("请先在'CGM数据上传'标签页上传或生成CGM数据")
        return

    cgm_data = st.session_state.cgm_data
    cgm_system = st.session_state.cgm_integration

    st.markdown("### 📝 餐食信息输入")

    with st.form("meal_analysis_form"):
        col1, col2 = st.columns(2)

        with col1:
            meal_date = st.date_input(
                "用餐日期",
                value=datetime.date.today(),
                help="选择用餐的日期"
            )
            meal_time_input = st.time_input(
                "用餐时间",
                value=datetime.time(12, 0),
                help="选择用餐的具体时间"
            )
            # 合并日期和时间
            meal_time = datetime.datetime.combine(meal_date, meal_time_input)

            meal_type = st.selectbox(
                "餐次类型",
                ["早餐", "午餐", "晚餐", "加餐"]
            )

        with col2:
            gi_estimate = st.slider(
                "估计总体GI值",
                min_value=20,
                max_value=100,
                value=55,
                help="根据食物类型估计整餐的血糖生成指数"
            )

            gl_estimate = st.slider(
                "估计总体GL值",
                min_value=5,
                max_value=50,
                value=15,
                help="根据食物分量估计整餐的血糖负荷"
            )

        # 具体菜品选择
        st.markdown("**菜品组成**:")
        dishes = st.multiselect(
            "选择菜品",
            ["燕麦鸡蛋套餐", "清蒸鲈鱼配糙米", "白切鸡配米饭", "蒸蛋羹+青菜",
             "小米粥+咸菜", "豆腐蔬菜汤", "荞麦面配蔬菜"],
            help="选择这餐包含的主要菜品"
        )

        if st.form_submit_button("分析餐后血糖反应"):
            if dishes:
                # 准备餐食组成数据
                meal_composition = {
                    'dishes': dishes,
                    'gi_total': gi_estimate,
                    'gl_total': gl_estimate,
                    'meal_type': meal_type
                }

                # 执行血糖反应分析
                with st.spinner("正在分析餐后血糖反应..."):
                    analysis_result = cgm_system.analyze_meal_glucose_response(
                        cgm_data, meal_time, meal_composition
                    )

                if 'error' not in analysis_result:
                    render_meal_analysis_results(analysis_result)
                else:
                    st.error(f"分析失败: {analysis_result['error']}")
            else:
                st.error("请至少选择一个菜品")

def render_meal_analysis_results(analysis_result):
    """显示餐后血糖分析结果"""
    st.markdown("### 📊 餐后血糖反应分析结果")

    # 关键指标展示
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "基线血糖",
            f"{analysis_result['baseline_glucose']} mmol/L",
            help="用餐前30分钟内的平均血糖值"
        )

    with col2:
        st.metric(
            "血糖峰值",
            f"{analysis_result['peak_glucose']} mmol/L",
            delta=f"+{analysis_result['glucose_excursion']}",
            help="餐后血糖的最高值"
        )

    with col3:
        st.metric(
            "达峰时间",
            f"{analysis_result['time_to_peak']} 分钟",
            help="从用餐到血糖达到峰值的时间"
        )

    with col4:
        recovery_time = analysis_result.get('recovery_time')
        recovery_text = f"{recovery_time} 分钟" if recovery_time else "未回归"
        st.metric(
            "回归时间",
            recovery_text,
            help="血糖回归到接近基线水平的时间"
        )

    # 血糖反应评级
    response_grade = analysis_result.get('response_grade', {})
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 血糖反应评级")
        grade = response_grade.get('grade', '未知')
        score = response_grade.get('score', 0)

        # 根据等级显示不同颜色
        if grade == "优秀":
            st.success(f"🏆 **{grade}** (评分: {score}/30)")
        elif grade == "良好":
            st.info(f"✅ **{grade}** (评分: {score}/30)")
        elif grade == "需改进":
            st.warning(f"⚠️ **{grade}** (评分: {score}/30)")
        else:
            st.error(f"❌ **{grade}** (评分: {score}/30)")

        # 显示建议
        recommendations = response_grade.get('recommendations', [])
        for rec in recommendations:
            st.write(f"- {rec}")

    with col2:
        st.markdown("### 🔍 预期vs实际对比")
        response_match = analysis_result.get('response_match', {})

        match_level = response_match.get('match_level', '未知')
        deviation = response_match.get('deviation', 0)
        suggestion = response_match.get('suggestion', '')

        st.write(f"**匹配度**: {match_level}")
        st.write(f"**偏差**: {deviation:+.1f} mmol/L")
        st.info(suggestion)

    # 血糖曲线下面积
    auc = analysis_result.get('auc', 0)
    st.markdown("### 📈 综合血糖影响")
    st.metric(
        "血糖曲线下面积 (AUC)",
        f"{auc:.1f}",
        help="数值越低表示血糖影响越小，<100为优秀，<200为良好"
    )

    # 保存分析结果
    if 'meal_analysis_history' not in st.session_state:
        st.session_state.meal_analysis_history = []

    st.session_state.meal_analysis_history.append(analysis_result)

def render_cgm_based_recommendations():
    """基于CGM数据的个性化推荐"""
    st.subheader("🎯 CGM数据驱动的个性化营养推荐")

    if 'meal_analysis_history' not in st.session_state or not st.session_state.meal_analysis_history:
        st.warning("请先在'餐后血糖分析'中完成至少一次餐后分析")
        return

    cgm_system = st.session_state.cgm_integration
    history = st.session_state.meal_analysis_history

    # 当前状态输入
    col1, col2 = st.columns(2)

    with col1:
        current_glucose = st.number_input(
            "当前血糖值 (mmol/L)",
            min_value=2.0,
            max_value=20.0,
            value=6.5,
            step=0.1
        )

    with col2:
        next_meal = st.selectbox(
            "下一餐类型",
            ["breakfast", "lunch", "dinner", "snack"]
        )

    # 患者档案（简化版）
    patient_profile = {
        'diagnosed_diseases': st.session_state.get('patient_data', {}).get('patient', {}).diagnosed_diseases or []
    }

    if st.button("生成个性化推荐"):
        with st.spinner("基于CGM数据生成个性化推荐..."):
            recommendations = cgm_system.generate_personalized_recommendations(
                history, current_glucose, next_meal, patient_profile
            )

        if 'error' not in recommendations:
            render_personalized_recommendations(recommendations)
        else:
            st.error(f"推荐生成失败: {recommendations['error']}")

def render_personalized_recommendations(recommendations):
    """显示个性化推荐结果"""
    st.markdown("### 🍽️ 个性化营养推荐")

    # 血糖敏感性分析
    sensitivity = recommendations.get('glucose_sensitivity', {})
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🧬 个体血糖敏感性")
        level = sensitivity.get('sensitivity_level', 'unknown')
        desc = sensitivity.get('sensitivity_desc', '未知')
        confidence = sensitivity.get('confidence', 0)

        if level == 'high':
            st.error(f"🔴 **高敏感**: {desc}")
        elif level == 'moderate':
            st.info(f"🟡 **中等敏感**: {desc}")
        elif level == 'low':
            st.success(f"🟢 **低敏感**: {desc}")

        st.progress(confidence, text=f"置信度: {confidence:.0%}")

    with col2:
        st.markdown("#### 🩸 当前血糖状态")
        current_status = recommendations.get('current_status', {})
        status = current_status.get('status', '正常')
        urgency = current_status.get('urgency', 'low')

        if urgency == 'high':
            st.error(f"🚨 **{status}** - 需要立即关注")
        elif urgency == 'medium':
            st.warning(f"⚠️ **{status}** - 需要注意")
        else:
            st.success(f"✅ **{status}** - 状态良好")

    # 食物调整建议
    food_adjustments = recommendations.get('food_adjustments', {})
    st.markdown("#### 🍎 食物选择指导")

    col1, col2, col3 = st.columns(3)

    with col1:
        gi_target = food_adjustments.get('gi_target', 55)
        st.metric("推荐GI目标", gi_target)

        if gi_target <= 35:
            st.success("选择低GI食物")
        elif gi_target <= 70:
            st.info("可选择中等GI食物")
        else:
            st.warning("谨慎选择高GI食物")

    with col2:
        gl_target = food_adjustments.get('gl_target', 15)
        st.metric("推荐GL目标", gl_target)

    with col3:
        portion_modifier = food_adjustments.get('portion_modifier', 1.0)
        portion_change = (portion_modifier - 1) * 100
        st.metric("分量调整", f"{portion_change:+.0f}%")

    # 具体推荐
    detailed_recs = recommendations.get('recommendations', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ 推荐食物")
        recommended_foods = detailed_recs.get('recommended_foods', [])
        for food in recommended_foods:
            st.write(f"• {food}")

    with col2:
        st.markdown("#### 👨‍🍳 烹饪建议")
        cooking_methods = detailed_recs.get('cooking_methods', [])
        for method in cooking_methods:
            st.write(f"• {method}")

    # 监测建议
    monitoring = recommendations.get('monitoring_advice', {})
    st.markdown("#### 📊 血糖监测建议")

    frequency = monitoring.get('frequency', 'normal')
    timepoints = monitoring.get('key_timepoints', [])

    if frequency == 'intensive':
        st.error("🔴 **加强监测**: 密切关注血糖变化")
    elif frequency == 'enhanced':
        st.warning("🟡 **增强监测**: 适当增加监测频率")
    else:
        st.success("🟢 **常规监测**: 按正常频率监测")

    st.write("**关键监测时点**:")
    for timepoint in timepoints:
        st.write(f"• {timepoint}")

def render_glucose_trend_analysis():
    """血糖趋势分析"""
    st.subheader("📈 血糖趋势与模式分析")

    if 'cgm_data' not in st.session_state:
        st.warning("请先上传CGM数据")
        return

    cgm_data = st.session_state.cgm_data

    # 基本趋势图
    st.markdown("### 📊 血糖趋势图")

    fig = px.line(
        cgm_data,
        x='timestamp',
        y='glucose',
        title="CGM血糖趋势",
        labels={'glucose': '血糖值 (mmol/L)', 'timestamp': '时间'}
    )

    # 添加目标范围线
    fig.add_hline(y=3.9, line_dash="dash", line_color="red", annotation_text="低血糖")
    fig.add_hline(y=7.8, line_dash="dash", line_color="green", annotation_text="理想上限")
    fig.add_hline(y=10.0, line_dash="dash", line_color="orange", annotation_text="高血糖")

    st.plotly_chart(fig, use_container_width=True)

    # 统计指标
    st.markdown("### 📋 血糖控制指标")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tir = ((cgm_data['glucose'] >= 3.9) & (cgm_data['glucose'] <= 10.0)).mean() * 100
        st.metric("目标范围内时间 (TIR)", f"{tir:.1f}%")

    with col2:
        tbr = (cgm_data['glucose'] < 3.9).mean() * 100
        st.metric("低血糖时间 (TBR)", f"{tbr:.1f}%")

    with col3:
        tar = (cgm_data['glucose'] > 10.0).mean() * 100
        st.metric("高血糖时间 (TAR)", f"{tar:.1f}%")

    with col4:
        cv = (cgm_data['glucose'].std() / cgm_data['glucose'].mean()) * 100
        st.metric("血糖变异系数 (CV)", f"{cv:.1f}%")

    # TIR评价
    if tir >= 70:
        st.success("🎯 血糖控制优秀 (TIR ≥ 70%)")
    elif tir >= 50:
        st.info("📈 血糖控制良好 (TIR 50-69%)")
    else:
        st.warning("⚠️ 血糖控制需要改善 (TIR < 50%)")

def generate_mock_cgm_data():
    """生成模拟CGM数据用于演示"""
    # 生成24小时的模拟数据，每5分钟一个点
    start_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamps = [start_time + datetime.timedelta(minutes=5*i) for i in range(288)]

    # 基于时间生成有规律的血糖模式
    glucose_values = []
    base_glucose = 6.0  # 基础血糖

    for i, ts in enumerate(timestamps):
        hour = ts.hour
        minute = ts.minute

        # 模拟餐后血糖升高
        if 7 <= hour <= 9:  # 早餐后
            glucose_add = 2.0 * math.exp(-(hour-8)**2/2) * (1 + 0.3*math.sin(minute/10))
        elif 12 <= hour <= 14:  # 午餐后
            glucose_add = 2.5 * math.exp(-(hour-13)**2/2) * (1 + 0.3*math.sin(minute/10))
        elif 18 <= hour <= 20:  # 晚餐后
            glucose_add = 2.2 * math.exp(-(hour-19)**2/2) * (1 + 0.3*math.sin(minute/10))
        else:
            glucose_add = 0

        # 添加随机波动
        noise = random.gauss(0, 0.3)

        # 夜间基础值稍低
        if 0 <= hour <= 6:
            base_adjustment = -0.5
        else:
            base_adjustment = 0

        glucose = base_glucose + base_adjustment + glucose_add + noise
        glucose = max(3.0, min(15.0, glucose))  # 限制在合理范围内

        glucose_values.append(round(glucose, 1))

    return pd.DataFrame({
        'timestamp': timestamps,
        'glucose': glucose_values
    })

def generate_cgm_optimized_recommendations(original_recommendations, patient):
    """基于CGM数据生成优化的菜谱推荐"""
    if 'meal_analysis_history' not in st.session_state or not st.session_state.meal_analysis_history:
        # 如果没有CGM历史，返回原始推荐
        return extract_original_dishes(original_recommendations)

    # 分析患者的血糖反应模式
    cgm_history = st.session_state.meal_analysis_history
    glucose_sensitivity = analyze_patient_glucose_sensitivity(cgm_history)

    # 根据血糖敏感性优化菜品选择
    optimized_dishes = {}

    # 定义优化的菜品数据库（基于血糖反应优化）
    cgm_optimized_menu = {
        "高敏感体质": {
            "早餐推荐": ["蒸蛋白", "燕麦鸡蛋套餐", "豆腐脑配菜"],
            "午餐推荐": ["清蒸鸡胸肉", "清蒸鲈鱼配糙米", "蒸蛋羹配蔬菜"],
            "晚餐推荐": ["蒸蛋羹", "蔬菜豆腐汤", "小米粥"],
            "加餐推荐": ["水煮蛋", "柚子片", "牛奶"]
        },
        "中等敏感体质": {
            "早餐推荐": ["燕麦鸡蛋套餐", "牛奶燕麦", "煎蛋三明治"],
            "午餐推荐": ["清蒸鲈鱼配糙米", "白切鸡配米饭", "豆腐蔬菜汤"],
            "晚餐推荐": ["蒸蛋羹+青菜", "荞麦面配蔬菜", "冬瓜排骨汤"],
            "加餐推荐": ["酸奶", "苹果片", "核桃仁"]
        },
        "低敏感体质": {
            "早餐推荐": ["煎蛋三明治", "豆浆油条", "牛奶燕麦"],
            "午餐推荐": ["红烧牛肉面", "白切鸡配米饭", "水煮鱼片配糙米"],
            "晚餐推荐": ["荞麦面配蔬菜", "清汤面条", "蒸蛋羹+青菜"],
            "加餐推荐": ["蓝莓酸奶", "核桃仁", "豆浆"]
        }
    }

    # 根据患者敏感性选择菜品
    sensitivity_level = glucose_sensitivity.get('level', '中等敏感体质')
    menu_category = cgm_optimized_menu.get(sensitivity_level, cgm_optimized_menu['中等敏感体质'])

    meal_types = ["早餐推荐", "午餐推荐", "晚餐推荐", "加餐推荐"]
    for meal_type in meal_types:
        if meal_type in menu_category:
            # 选择第一个菜品作为推荐
            optimized_dishes[meal_type] = menu_category[meal_type][0]

    return optimized_dishes

def extract_original_dishes(recommendations):
    """从原始推荐中提取菜品名称"""
    dishes = {}
    meal_types = ["早餐推荐", "午餐推荐", "晚餐推荐", "加餐推荐"]
    for meal_type in meal_types:
        if meal_type in recommendations and recommendations[meal_type]:
            dish_name_with_calories = recommendations[meal_type][0]
            dish_name = dish_name_with_calories.split(" (")[0] if " (" in dish_name_with_calories else dish_name_with_calories
            dishes[meal_type] = dish_name
    return dishes

def analyze_patient_glucose_sensitivity(cgm_history):
    """分析患者血糖敏感性"""
    if not cgm_history:
        return {'level': '中等敏感体质', 'avg_excursion': 3.0, 'confidence': 0}

    # 收集血糖上升幅度数据
    excursions = []
    for record in cgm_history:
        if 'glucose_excursion' in record:
            excursions.append(record['glucose_excursion'])

    if len(excursions) == 0:
        return {'level': '中等敏感体质', 'avg_excursion': 3.0, 'confidence': 0}

    avg_excursion = sum(excursions) / len(excursions)
    confidence = min(len(excursions) / 5.0, 1.0)  # 5次分析达到100%置信度

    # 根据平均血糖上升幅度分类
    if avg_excursion <= 2.0:
        level = '低敏感体质'
        description = "血糖反应平缓，可选择相对宽松的食物"
    elif avg_excursion <= 3.5:
        level = '中等敏感体质'
        description = "血糖反应适中，需要适度控制"
    else:
        level = '高敏感体质'
        description = "血糖反应敏感，需要严格控制碳水化合物"

    return {
        'level': level,
        'description': description,
        'avg_excursion': round(avg_excursion, 1),
        'confidence': round(confidence, 2)
    }

def get_cgm_optimization_info(dish_name, meal_type):
    """获取CGM优化信息"""
    if 'meal_analysis_history' not in st.session_state:
        return None

    # 根据历史CGM数据提供个性化信息
    cgm_history = st.session_state.meal_analysis_history
    sensitivity = analyze_patient_glucose_sensitivity(cgm_history)

    if sensitivity['level'] == '高敏感体质':
        return f"基于您的血糖反应模式，此菜品预期血糖上升{sensitivity['avg_excursion']:.1f}mmol/L（较温和）"
    elif sensitivity['level'] == '低敏感体质':
        return f"基于您的血糖平缓反应，此菜品是安全的选择"
    else:
        return f"基于您的血糖反应模式，此菜品适中，预期上升{sensitivity['avg_excursion']:.1f}mmol/L"

def predict_glucose_impact(dish_name):
    """预测菜品对血糖的影响"""
    # 从营养数据库获取GI信息
    gi_estimates = {
        # 低GI食物
        "蒸蛋白": {"gi": 25, "level": "low", "description": "极低血糖影响，理想选择"},
        "清蒸鸡胸肉": {"gi": 30, "level": "low", "description": "低血糖影响，蛋白质丰富"},
        "蒸蛋羹": {"gi": 35, "level": "low", "description": "低血糖影响，易消化"},
        "豆腐": {"gi": 25, "level": "low", "description": "极低血糖影响，植物蛋白"},
        "柚子片": {"gi": 30, "level": "low", "description": "低血糖影响，维生素丰富"},
        "蔬菜豆腐汤": {"gi": 35, "level": "low", "description": "低血糖影响，营养均衡"},

        # 中等GI食物
        "燕麦鸡蛋套餐": {"gi": 45, "level": "medium", "description": "中等血糖影响，营养丰富"},
        "清蒸鲈鱼配糙米": {"gi": 50, "level": "medium", "description": "中等血糖影响，优质蛋白"},
        "牛奶燕麦": {"gi": 50, "level": "medium", "description": "中等血糖影响，钙质丰富"},
        "荞麦面配蔬菜": {"gi": 55, "level": "medium", "description": "中等血糖影响，纤维丰富"},
        "白切鸡配米饭": {"gi": 60, "level": "medium", "description": "中等血糖影响，注意分量"},

        # 中高GI食物
        "红烧牛肉面": {"gi": 70, "level": "high", "description": "较高血糖影响，建议小分量"},
        "豆浆油条": {"gi": 75, "level": "high", "description": "较高血糖影响，偶尔食用"},
        "煎蛋三明治": {"gi": 65, "level": "medium", "description": "中等偏高血糖影响"}
    }

    return gi_estimates.get(dish_name, {"gi": 55, "level": "medium", "description": "中等血糖影响"})

if __name__ == "__main__":
    main()