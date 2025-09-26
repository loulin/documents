-- 糖尿病知识图谱数据库设计
-- 支持PostgreSQL和Neo4j两种存储方案

-- ==============================================
-- PostgreSQL 关系数据库方案
-- ==============================================

-- 1. 实体表
CREATE TABLE entities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    properties JSONB, -- 存储特定属性
    metadata JSONB,   -- 存储元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_category ON entities(category);
CREATE INDEX idx_entities_properties ON entities USING GIN(properties);

-- 2. 关系表
CREATE TABLE relationships (
    id VARCHAR(50) PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL REFERENCES entities(id),
    target_id VARCHAR(50) NOT NULL REFERENCES entities(id),
    relation_type VARCHAR(100) NOT NULL,
    strength VARCHAR(20),
    evidence_level VARCHAR(20),
    properties JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);
CREATE INDEX idx_relationships_type ON relationships(relation_type);

-- 3. 知识推理规则表
CREATE TABLE inference_rules (
    id VARCHAR(50) PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    conditions JSONB NOT NULL, -- 规则条件
    conclusions JSONB NOT NULL, -- 规则结论
    confidence DECIMAL(3,2), -- 置信度 0.00-1.00
    rule_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 用户查询历史表
CREATE TABLE query_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),
    entities_mentioned JSONB, -- 查询中提及的实体
    response_entities JSONB,  -- 响应中涉及的实体
    satisfaction_score INTEGER, -- 1-5评分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 知识来源表
CREATE TABLE knowledge_sources (
    id VARCHAR(50) PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50), -- guideline, textbook, paper, clinical_data
    authority_level VARCHAR(20), -- high, medium, low
    publication_date DATE,
    last_verified DATE,
    url TEXT,
    metadata JSONB
);

-- 6. 实体-来源关联表
CREATE TABLE entity_sources (
    entity_id VARCHAR(50) REFERENCES entities(id),
    source_id VARCHAR(50) REFERENCES knowledge_sources(id),
    confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, source_id)
);

-- ==============================================
-- 示例数据插入
-- ==============================================

-- 插入生理实体
INSERT INTO entities (id, name, name_en, type, category, description, properties) VALUES
('PHYS_001', '胰岛素', 'Insulin', 'physiological_entity', 'hormone', 
 '由胰岛β细胞分泌的蛋白质激素，调节血糖水平', 
 '{"normal_range": {"fasting": "5-25 mIU/L"}, "location": "胰腺胰岛β细胞", "molecular_weight": "5808 Da"}'),

('PHYS_002', '血糖', 'Blood Glucose', 'physiological_entity', 'metabolite',
 '血液中的葡萄糖浓度，是糖尿病诊断的关键指标',
 '{"normal_range": {"fasting": "3.9-6.1 mmol/L", "random": "<11.1 mmol/L"}, "unit": "mmol/L"}'),

('PHYS_003', '胰岛β细胞', 'Pancreatic Beta Cell', 'physiological_entity', 'cell',
 '胰腺胰岛中负责分泌胰岛素的细胞',
 '{"location": "胰腺胰岛", "function": ["胰岛素分泌", "血糖感知"]}');

-- 插入病理实体
INSERT INTO entities (id, name, name_en, type, category, description, properties) VALUES
('PATH_001', '2型糖尿病', 'Type 2 Diabetes Mellitus', 'pathological_entity', 'disease',
 '以胰岛素抵抗和胰岛β细胞功能缺陷为特征的代谢性疾病',
 '{"icd10_code": "E11", "prevalence": {"global": "9.3%", "china": "11.2%"}, "risk_factors": ["肥胖", "年龄", "家族史"]}'),

('PATH_002', '糖尿病肾病', 'Diabetic Nephropathy', 'pathological_entity', 'complication',
 '糖尿病最常见的微血管并发症之一',
 '{"icd10_code": "E11.2", "stages": ["1期", "2期", "3期", "4期", "5期"], "progression_time": "5-25年"}');

-- 插入临床实体  
INSERT INTO entities (id, name, name_en, type, category, description, properties) VALUES
('CLIN_001', '糖化血红蛋白', 'HbA1c', 'clinical_entity', 'diagnostic_test',
 '反映2-3个月平均血糖水平的指标',
 '{"normal_range": "<5.7%", "diabetes_threshold": "≥6.5%", "target": "<7.0%"}'),

('CLIN_002', '二甲双胍', 'Metformin', 'clinical_entity', 'medication',
 '2型糖尿病一线治疗药物',
 '{"mechanism": "减少肝糖输出，改善胰岛素敏感性", "dosage": "500-2000mg/日", "contraindications": ["严重肾功能不全"]}');

-- 插入关系
INSERT INTO relationships (id, source_id, target_id, relation_type, strength, evidence_level, properties) VALUES
('REL_001', 'PHYS_003', 'PHYS_001', 'produces', 'strong', 'high',
 '{"mechanism": "胰岛β细胞感知血糖升高后分泌胰岛素", "regulation": "葡萄糖依赖性"}'),

('REL_002', 'PHYS_001', 'PHYS_002', 'regulates', 'strong', 'high', 
 '{"mechanism": "促进组织摄取葡萄糖，抑制肝糖输出", "time_course": "分钟级"}'),

('REL_003', 'PATH_001', 'PATH_002', 'causes', 'strong', 'high',
 '{"progression_rate": "20-40%患者发展为肾病", "time_frame": "5-25年", "risk_factors": ["血糖控制不佳", "高血压"]}');

-- ==============================================
-- Neo4j Cypher 查询示例
-- ==============================================

/*
// 创建实体节点
CREATE (:PhysiologicalEntity {
  id: 'PHYS_001', 
  name: '胰岛素',
  name_en: 'Insulin',
  type: 'hormone',
  description: '由胰岛β细胞分泌的蛋白质激素，调节血糖水平',
  normal_range: '5-25 mIU/L'
})

// 创建关系
MATCH (a:PhysiologicalEntity {id: 'PHYS_003'}), (b:PhysiologicalEntity {id: 'PHYS_001'})
CREATE (a)-[:PRODUCES {strength: 'strong', evidence_level: 'high'}]->(b)

// 查询糖尿病的所有并发症
MATCH (d:PathologicalEntity {name: '2型糖尿病'})-[:CAUSES]->(c:PathologicalEntity)
WHERE c.category = 'complication'
RETURN c.name, c.description

// 查询影响血糖的所有因素
MATCH (x)-[r:AFFECTS]->(bg:PhysiologicalEntity {name: '血糖'})
RETURN x.name, r.relation_type, r.strength
ORDER BY r.strength DESC
*/

-- ==============================================
-- 查询函数示例
-- ==============================================

-- 查找实体的所有关系
CREATE OR REPLACE FUNCTION get_entity_relationships(entity_id VARCHAR)
RETURNS TABLE (
    related_entity_id VARCHAR,
    related_entity_name VARCHAR,
    relation_type VARCHAR,
    direction VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.target_id as related_entity_id,
        e.name as related_entity_name,
        r.relation_type,
        'outgoing' as direction
    FROM relationships r
    JOIN entities e ON r.target_id = e.id
    WHERE r.source_id = entity_id
    
    UNION ALL
    
    SELECT 
        r.source_id as related_entity_id,
        e.name as related_entity_name,
        r.relation_type,
        'incoming' as direction
    FROM relationships r  
    JOIN entities e ON r.source_id = e.id
    WHERE r.target_id = entity_id;
END;
$$ LANGUAGE plpgsql;

-- 查找疾病的治疗方案
CREATE OR REPLACE FUNCTION get_treatment_options(disease_id VARCHAR)
RETURNS TABLE (
    treatment_name VARCHAR,
    treatment_type VARCHAR,
    evidence_level VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.name as treatment_name,
        e.type as treatment_type,
        r.evidence_level
    FROM relationships r
    JOIN entities e ON r.source_id = e.id
    WHERE r.target_id = disease_id 
    AND r.relation_type IN ('treats', 'alleviates', 'prevents')
    AND e.type = 'clinical_entity'
    ORDER BY 
        CASE r.evidence_level 
            WHEN 'high' THEN 1
            WHEN 'moderate' THEN 2
            WHEN 'low' THEN 3
        END;
END;
$$ LANGUAGE plpgsql;