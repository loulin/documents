# GPlus报告完整功能清单

## 📊 完整内容结构（17页）

### ✅ 已实现功能（Enhanced v2.0）

#### Page 1 - 首页摘要
- [x] 患者基本信息表格
- [x] 核心指标卡片（MG, GMI, CV）
- [x] TIR/TAR/TBR百分比
- [x] AGP图谱（百分位数带状图）
- [x] 每日血糖曲线小图（14天网格）

---

### ❌ 待补充功能

#### **Page 2 - 综合分析页**
- [ ] **左侧指标列表**：
  ```
  数据天数: 13.7天
  有效数据比例: 100%
  平均血糖(Mean): 9.57 mmol/L
  GMI: 7.4%
  CV: 24.9%
  标准差(SD): 2.39 mmol/L
  MAGE: 5.17 mmol/L
  日间血糖平均绝对差: 2.44 mmol/L
  ```

- [ ] **TIR/TAR/TBR横向对比条形图**：
  ```
  TBR  ■■  0.6%        参考值: 4%
  TIR  ████████ 59.8%   参考值: 70%
  TAR  ████     39.6%   参考值: 25%
  ```

- [ ] **右侧AGP图谱**（与Page 1相同但更大）

- [ ] **底部14天每日曲线**（更大版本，每天一行）
  - 时间轴：0-24小时
  - 高度：每个约80px
  - 3.9和10.0参考线

- [ ] **底部文字评估**：
  ```
  总体血糖情况：总体血糖水平尚可。餐后血糖波动较大。
  平均血糖为 9.57 mmol/L，目标范围内血糖占比（TIR）为 59.8%。
  建议：注意饮食结构和生活习惯的调整，定期监测餐后血糖。
  ```

---

#### **Page 3 - 详细可视化页**
- [ ] **左侧指标列表**（同Page 2）
- [ ] **右上：TIR圆环图**（可选）
- [ ] **中间：AGP图谱**（同Page 2）
- [ ] **右侧：14天每日曲线**（2列x7行布局）
  - 每天显示完整24小时
  - X轴：0:00, 4:00, 8:00, 12:00, 16:00, 20:00
  - Y轴：0-21 mmol/L
  - 3.9和10.0参考线

---

#### **Page 4 - 详细指标表格**
- [ ] **左侧表格**：
  ```
  项目                    结果      参考范围    单位
  平均血糖(Mean)          9.57      4.9~6.4     mmol/L
  GMI                     7.4%      <7%         %
  CV                      24.9%     19.25%      %
  SD                      2.39      0.6~1.4     mmol/L
  数据天数                13.7                   天
  有效数据比例            100%      >70%        %
  <3mM极低血糖            0.0%      <1.0%       %
  <3.9mM低血糖            0.6%      <4.0%       %
  TIR(3.9-10mM)          59.8%     ≥70.0%      %
  ≥10mM高血糖            39.6%     <25.0%      %
  ≥13.9mM极高血糖        5.2%      <5.0%       %
  AUC(白天)              9.9       4.9~6.7     mmol/L*h
  AUC(夜晚)              8.5       4.7~6.1     mmol/L*h
  AUC(全天)              9.6       4.7~6.3     mmol/L*h
  血糖四分差              3.2       0.7~1.6     mmol/L
  MAGE                   5.17                   mmol/L
  日间血糖平均绝对差      2.44                   mmol/L
  高血糖风险指数          8.19
  低血糖风险指数          2.74
  ```

- [ ] **右侧表格**：
  ```
  项目                          结果        单位
  <3.0mM每日平均时长            0          分钟
  <3.9mM每日平均时长            9          分钟
  ≥7.8mM每日平均时长            1117       分钟
  ≥10mM每日平均时长             561        分钟
  ≥13.9mM每日平均时长           74         分钟
  <3.0mM每日平均发生次数        0          次
  <3.9mM每日平均发生次数        0.1        次
  ≥7.8mM每日平均发生次数        2.6        次
  ≥10mM每日平均发生次数         3          次
  ≥13.9mM每日平均发生次数       1.2        次
  <3.0mM平均持续时间            0          分钟
  <3.9mM平均持续时间            60         分钟
  ≥7.8mM平均持续时间            436        分钟
  ≥10mM平均持续时间             187        分钟
  ≥13.9mM平均持续时间           63         分钟
  ```

---

#### **Page 5 - 按星期布局的曲线图**
- [ ] **7x2网格布局**（按星期几组织）
  ```
  星期一  星期二  星期三  星期四  星期五  星期六  星期日
  [空]    [8.5]   [8.6]   [8.7]   [8.8]   [8.9]   [8.10]

  [8.11]  [8.12]  [8.13]  [8.14]  [8.15]  [8.16]  [8.17]

  [8.18]  [8.19]
  ```

- [ ] **每个小图包含**：
  - 日期标签
  - 完整24小时曲线
  - 3.9和10.0参考线
  - 最高值标注（数值+时间）
  - 最低值标注（数值+时间）
  - X轴时间：0:00, 6:00, 12:00, 18:00

---

#### **Page 6 - TIR趋势面积图**
- [ ] **堆叠面积图**（14-15天）
  ```
  100%  ┌───────────────────────────────────┐
   80%  │       黄色区域(TAR)                │
   60%  │   绿色区域(TIR)                    │
   40%  │                                    │
   20%  │红色(TBR)                           │
    0%  └───────────────────────────────────┘
        D1  D3  D5  D7  D9  D11 D13 D15
  ```

- [ ] **每天TIR百分比标注**（在绿色区域内）
  - 例：100%, 69.8%, 40.6%, 76%, 57.3%...

- [ ] **图例**：
  - 🔴 <3mmol/L
  - 🟠 <3.9mmol/L
  - 🟢 ≥3.9~<10mmol/L
  - 🟡 ≥10mmol/L
  - 🟠 ≥13.9mmol/L

---

#### **Page 7-11 - 逐日详细报告**（每天一页）
- [ ] **表格布局**：3列
  ```
  血糖曲线                用药方案              均值    TIR
  ┌──────────────┐       ┌────────┐        9.0mM   76.0%
  │ 24小时曲线    │       │ (空白)  │
  │ 黄色填充TAR区 │       └────────┘
  │ 灰色背景      │
  └──────────────┘
  ```

- [ ] **血糖曲线特点**：
  - 高于10.0的区域用**黄色填充**
  - Y轴：0-21 mmol/L
  - X轴：0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22
  - 3.9和10.0虚线参考线

- [ ] **用药方案列**：预留给医生填写

- [ ] **均值和TIR列**：
  - 平均值（如：9.0 mM）
  - TIR百分比（如：76.0%）

---

#### **Page 12-13 - 小图版每日报告**
- [ ] **4列x2行布局**（每页8天）
- [ ] **每个小图包含**：
  ```
  血糖曲线              均值/TIR
  ┌──────────┐        均值：5.9
  │ 8月5日    │        TAR: 0.0%
  │ 星期二    │        TIR: 100.0%
  │ [曲线图]  │        TBR: 0.0%
  └──────────┘
  ```

- [ ] **曲线图特点**：
  - 黄色填充TAR区域
  - 灰色背景
  - 3.9和10.0参考线
  - X轴：0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22
  - Y轴：0-21 mmol/L

---

#### **Page 14-16 - 每日详细数据表**
- [ ] **表格：每页6-7天数据**
  ```
  项目                正常参考值     2025-08-05  2025-08-06  ...
  测定次数            -              285         1440        ...
  平均值(MG)         <6.6           5.9         7.59        ...
  标准差(SD)         <1.4           0.43        2.86        ...
  变异系数(CV)       -              7.4%        37.7%       ...
  MAGE               -              /           7.7         ...
  最高值             -              6.6         13.6        ...
  最低值             -              4.9         3.2         ...
  ≥16.7 mmol/L时间   -              0:0 (0%)    0:0 (0%)    ...
  ≥13.9 mmol/L时间   <5%            0:0 (0%)    0:0 (0%)    ...
  ≥10 mmol/L时间     <25%           0:0 (0%)    5:15 (22%)  ...
  <3.9 mmol/L时间    <4%            0:0 (0%)    2:0 (8%)    ...
  <3 mmol/L时间      <1%            0:0 (0%)    0:0 (0%)    ...
  TIR(3.9-10)        ≥70%           4:45 (100%) 16:45 (70%) ...
  ```

---

#### **Page 17 - 总结报告**
- [ ] **CGM总体评估**：
  ```
  CGM提示：共测定19740个，平均值9.57 mmol/L，标准差2.39 mmol/L，
  变异系数24.9%，最高值、最低值分别为16.5 mmol/L、3.2 mmol/L。

  ≥3.9~<10 mmol/L的百分比为60%。≥10 mmol/L、≥13.9 mmol/L及
  ≥16.7 mmol/L的百分比分别为40%，5%及0%；<3.9 mmol/L及<3 mmol/L
  的时间及百分比分别为2小时0分（1%），0小时0分（0%）。
  ```

---

## 🎯 优先级排序

### P0 - 核心缺失（必须实现）
1. **Page 4 - 详细指标表格**
   - MAGE, AUC, 血糖四分差
   - 高/低血糖风险指数
   - 每日平均时长和发生次数

2. **Page 6 - TIR趋势面积堆叠图**
   - 直观展示14天TIR变化
   - 面积图比柱状图更专业

3. **Page 7-11 - 逐日详细报告**
   - 每天独立页面
   - 黄色填充高血糖区域
   - 用药方案栏

### P1 - 重要补充（建议实现）
4. **Page 2 - 综合分析页**
   - TIR/TAR/TBR横向对比条形图
   - 文字评估和建议

5. **Page 14-16 - 每日详细数据表**
   - 完整统计表格
   - 便于数据分析

6. **Page 5 - 按星期布局**
   - 更符合阅读习惯
   - 便于识别周末vs工作日模式

### P2 - 增强功能（可选实现）
7. **Page 12-13 - 小图版每日报告**
   - 提供另一种查看方式
   - 更紧凑的布局

8. **Page 17 - 总结报告**
   - 自动生成文字总结
   - 关键数值汇总

---

## 🔧 实现建议

### 技术方案

#### 1. MAGE计算
```python
def calculate_mage(glucose_values):
    """计算MAGE (Mean Amplitude of Glycemic Excursion)"""
    # 1. 计算标准差
    sd = np.std(glucose_values)

    # 2. 找出所有峰值和谷值
    peaks = find_peaks(glucose_values)[0]
    troughs = find_peaks(-glucose_values)[0]

    # 3. 筛选大于1个标准差的波动
    valid_excursions = []
    for i in range(len(peaks)):
        if abs(glucose_values[peaks[i]] - glucose_values[troughs[i]]) > sd:
            valid_excursions.append(abs(glucose_values[peaks[i]] - glucose_values[troughs[i]]))

    # 4. 计算平均值
    mage = np.mean(valid_excursions) if valid_excursions else 0
    return mage
```

#### 2. 面积堆叠图（TIR趋势）
```python
# 使用matplotlib创建堆叠面积图
fig, ax = plt.subplots()

# 数据准备
days = range(1, 15)
tbr_values = [0.0, 8.3, 0.0, ...]  # 每天TBR
tir_values = [100.0, 69.8, 40.6, ...]  # 每天TIR
tar_values = [0.0, 21.9, 59.4, ...]  # 每天TAR

# 绘制堆叠面积图
ax.fill_between(days, 0, tbr_values, color='#f44336', alpha=0.8, label='TBR')
ax.fill_between(days, tbr_values, [tbr+tir for tbr,tir in zip(tbr_values, tir_values)],
                color='#4caf50', alpha=0.8, label='TIR')
ax.fill_between(days, [tbr+tir for tbr,tir in zip(tbr_values, tir_values)], 100,
                color='#ff9800', alpha=0.8, label='TAR')

# 添加TIR百分比标注
for i, (day, tir) in enumerate(zip(days, tir_values)):
    ax.text(day, tbr_values[i] + tir/2, f'{tir:.1f}%',
            ha='center', va='center', fontsize=9)
```

#### 3. 黄色填充高血糖区域
```javascript
// Chart.js中使用插件实现区域填充
plugins: [{
    afterDatasetsDraw: function(chart) {
        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];
        const yAxis = chart.scales.y;

        // 遍历数据点，找到>10.0的区域
        for (let i = 0; i < dataset.data.length - 1; i++) {
            if (dataset.data[i] > 10.0 || dataset.data[i+1] > 10.0) {
                ctx.fillStyle = 'rgba(255, 235, 59, 0.3)';  // 黄色半透明
                // 绘制填充区域
                ctx.fillRect(x1, y1, x2-x1, y2-y1);
            }
        }
    }
}]
```

#### 4. 自动文字评估生成
```python
def generate_assessment(summary_metrics):
    """生成自动评估文字"""
    mg = summary_metrics['mean_glucose']
    tir = summary_metrics['tir']
    tar = summary_metrics['tar']
    cv = summary_metrics['cv']

    # 血糖水平评估
    if mg < 7.0:
        level_assessment = "总体血糖水平良好"
    elif mg < 9.0:
        level_assessment = "总体血糖水平尚可"
    else:
        level_assessment = "总体血糖水平偏高"

    # 波动评估
    if cv < 30:
        fluctuation = "血糖波动较小"
    elif cv < 36:
        fluctuation = "血糖波动适中"
    else:
        fluctuation = "血糖波动较大，尤其是餐后"

    # TIR评估
    if tir >= 70:
        tir_comment = "目标范围内时间良好"
    elif tir >= 50:
        tir_comment = f"目标范围内血糖占比（TIR）为 {tir:.1f}%，建议提高"
    else:
        tir_comment = f"目标范围内血糖占比（TIR）仅为 {tir:.1f}%，需要改善"

    # 建议
    suggestions = []
    if tar > 25:
        suggestions.append("注意饮食结构调整，控制餐后血糖")
    if cv > 36:
        suggestions.append("规律作息，定时进餐")
    if tir < 70:
        suggestions.append("定期监测餐后血糖")

    assessment = f"""
    总体血糖情况：{level_assessment}。{fluctuation}。
    平均血糖为 {mg:.2f} mmol/L，{tir_comment}。
    建议：{' ; '.join(suggestions)}。
    """

    return assessment.strip()
```

---

## 📝 总结

当前Enhanced v2.0实现了：
- ✅ 约**30%**的GPlus报告功能

还需补充的核心功能：
- ❌ 详细指标表格（MAGE, AUC等）
- ❌ TIR趋势面积图
- ❌ 逐日详细报告页
- ❌ 每日数据统计表
- ❌ 自动文字评估

**建议下一步**：
1. 优先实现P0功能（Page 4和Page 6）
2. 然后补充P1功能（Page 2, 7-11, 14-16）
3. 最后考虑P2增强功能

这样可以达到GPlus报告**90%**以上的功能完整度。
