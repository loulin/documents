# CGMEHR系统流程图

## 整体系统架构流程图

```mermaid
flowchart TD
    A[数据输入层] --> B[数据整合与预处理]
    B --> C[IGRS 3.0 核心评分模型]
    C --> D{特殊人群判断}
    
    D -->|妊娠患者| E1[母胎血糖风险模型]
    D -->|胰腺术后| E2[胰腺术后血糖模型]
    D -->|TPN+静脉胰岛素| E3[TPN滴定模型]
    D -->|透析患者| E4[透析周期依赖模型]
    D -->|一般患者| F[基础风险评分]
    
    E1 --> G[风险分数整合]
    E2 --> G
    E3 --> G
    E4 --> G
    F --> G
    
    G --> H{绝对高危规则}
    H -->|DKA/HHS/严重低血糖| I1[紧急级别]
    H -->|否| J[风险等级映射]
    
    J --> I1[紧急 >60分]
    J --> I2[高危 40-59分]
    J --> I3[关注 20-39分]
    J --> I4[稳定 <20分]
    
    I1 --> K[临床行动指令]
    I2 --> K
    I3 --> K
    I4 --> K
    
    K --> L[临床仪表盘展示]
    L --> M[医护人员决策]
    M --> N[患者管理与干预]
    
    style A fill:#e1f5fe
    style L fill:#f3e5f5
    style I1 fill:#ffebee
    style I2 fill:#fff3e0
    style I3 fill:#fff8e1
    style I4 fill:#e8f5e8
```

## 数据输入详细流程

```mermaid
flowchart LR
    A1[CGM数据] --> B1[血糖值序列]
    A1 --> B2[趋势数据]
    A1 --> B3[变异性指标]
    
    A2[EHR数据] --> C1[基本信息]
    A2 --> C2[实验室检验]
    A2 --> C3[用药记录]
    A2 --> C4[医嘱治疗]
    A2 --> C5[临床事件]
    
    B1 --> D[特征工程]
    B2 --> D
    B3 --> D
    C1 --> D
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    
    D --> E[结构化特征矩阵]
    
    style A1 fill:#e3f2fd
    style A2 fill:#e8f5e8
    style E fill:#fff3e0
```

## 精确分层算法框架

```mermaid
flowchart TD
    A[原始数据] --> B[特征提取算法]
    
    B --> B1[时序特征算法<br/>CV, MAGE, TIR, TAR, TBR]
    B --> B2[统计特征算法<br/>均值, 标准差, 偏度, 峰度]
    B --> B3[动态特征算法<br/>变化率, 加速度, 趋势持续时间]
    
    B1 --> C[风险分层算法]
    B2 --> C
    B3 --> C
    
    C --> C1[一级分层: 临床规则]
    C --> C2[二级分层: 机器学习]
    
    C1 --> D1[血糖阈值判定]
    C1 --> D2[变异性阈值判定]
    C1 --> D3[低血糖频次统计]
    
    C2 --> E1[随机森林<br/>非线性特征关系]
    C2 --> E2[XGBoost<br/>梯度提升精度]
    C2 --> E3[LSTM神经网络<br/>时序依赖关系]
    
    D1 --> F[风险评分整合]
    D2 --> F
    D3 --> F
    E1 --> F
    E2 --> F
    E3 --> F
    
    F --> G[预测算法]
    G --> G1[ARIMA模型<br/>短期血糖预测]
    G --> G2[Cox回归<br/>并发症风险评估]
    G --> G3[聚类算法<br/>患者群体识别]
    
    G1 --> H[决策支持算法]
    G2 --> H
    G3 --> H
    
    H --> H1[多属性决策分析]
    H --> H2[贝叶斯网络]
    H --> H3[规则引擎]
    
    H1 --> I[个性化干预方案]
    H2 --> I
    H3 --> I
    
    style B fill:#e1f5fe
    style C fill:#f3e5f5
    style G fill:#e8f5e8
    style H fill:#fff8e1
    style I fill:#ffebee
```

## 风险等级与行动指令流程

```mermaid
flowchart TD
    A[风险分数计算完成] --> B{绝对高危判断}
    
    B -->|是| C1[紧急级别<br/>立即响应]
    B -->|否| D{分数范围判断}
    
    D -->|>60分| C1
    D -->|40-59分| C2[高危级别<br/>重点关注]
    D -->|20-39分| C3[关注级别<br/>定期评估]
    D -->|<20分| C4[稳定级别<br/>常规管理]
    
    C1 --> E1[30分钟内床边响应<br/>高优先级警报]
    C2 --> E2[2-4小时内评估<br/>考虑内分泌会诊]
    C3 --> E3[查房时审查方案<br/>黄色高亮显示]
    C4 --> E4[常规方案管理<br/>每日报告]
    
    E1 --> F[仪表盘显示与记录]
    E2 --> F
    E3 --> F
    E4 --> F
    
    F --> G[医护人员查看]
    G --> H[临床决策执行]
    H --> I[患者状态监测]
    I --> J[结果评估与反馈]
    J --> A
    
    style C1 fill:#ffcdd2
    style C2 fill:#ffe0b2
    style C3 fill:#fff9c4
    style C4 fill:#c8e6c9
    style F fill:#e1f5fe
```

## 数据质量与CGM性能监控

```mermaid
flowchart TD
    A[CGM数据输入] --> B[数据质量评估]
    
    B --> C1[生理干扰检测]
    B --> C2[药物干扰检测]
    B --> C3[传感器性能评估]
    
    C1 --> D1[红细胞压积异常<br/>低氧血症<br/>酸中毒]
    C2 --> D2[维生素C<br/>对乙酰氨基酚<br/>羟基脲等]
    C3 --> D3[频繁校准请求<br/>信号丢失<br/>BGM-CGM差异]
    
    D1 --> E{CGM品牌识别}
    D2 --> E
    D3 --> E
    
    E --> F1[Dexcom G6/G7<br/>品牌特异性处理]
    E --> F2[Medtronic Guardian<br/>品牌特异性处理]
    E --> F3[FreeStyle Libre<br/>品牌特异性处理]
    
    F1 --> G[CGM数据置信度评分]
    F2 --> G
    F3 --> G
    
    G --> H{置信度等级}
    H -->|高| I1[正常权重使用CGM数据]
    H -->|中| I2[适度调整权重<br/>增加BGM验证]
    H -->|低| I3[显著降低权重<br/>频繁BGM监测]
    
    I1 --> J[风险评分计算]
    I2 --> J
    I3 --> J
    
    style E fill:#e3f2fd
    style G fill:#fff3e0
    style I3 fill:#ffcdd2
```

## 使用说明

### 生成图片方法：
1. 将上述Mermaid代码复制到 [Mermaid Live Editor](https://mermaid.live/)
2. 在线生成PNG或SVG格式图片
3. 或使用支持Mermaid的工具如Typora、VS Code等

### 展示建议：
1. **整体架构流程图** - 用于系统总体介绍
2. **精确分层算法框架** - 用于技术细节展示
3. **风险等级与行动指令流程** - 用于临床应用说明
4. **数据质量监控流程** - 用于质量保证说明

每个流程图都可以单独使用，也可以组合展示，根据受众需求选择合适的详细程度。