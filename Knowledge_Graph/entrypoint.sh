#!/bin/bash

# 综合内分泌疾病知识图谱 API 启动脚本

set -e

echo "=== 综合内分泌疾病知识图谱 API 启动中... ==="

# 等待数据库服务启动
echo "等待数据库服务启动..."

# 检查Neo4j连接
until nc -z neo4j 7687; do
    echo "等待 Neo4j 启动..."
    sleep 5
done
echo "Neo4j 已就绪"

# 检查Redis连接  
until nc -z redis 6379; do
    echo "等待 Redis 启动..."
    sleep 5
done
echo "Redis 已就绪"

# 检查MongoDB连接
until nc -z mongodb 27017; do
    echo "等待 MongoDB 启动..."
    sleep 5
done
echo "MongoDB 已就绪"

# 初始化知识图谱数据（如果需要）
if [ "$INIT_KNOWLEDGE_GRAPH" = "true" ]; then
    echo "初始化知识图谱数据..."
    python -c "
import json
from neo4j import GraphDatabase

# 连接Neo4j
driver = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'endocrine123'))

with driver.session() as session:
    # 创建索引
    session.run('CREATE INDEX disease_id IF NOT EXISTS FOR (d:Disease) ON (d.id)')
    session.run('CREATE INDEX symptom_name IF NOT EXISTS FOR (s:Symptom) ON (s.name)')
    session.run('CREATE INDEX test_name IF NOT EXISTS FOR (t:Test) ON (t.name)')
    session.run('CREATE INDEX autoantibody_name IF NOT EXISTS FOR (a:Autoantibody) ON (a.name)')
    session.run('CREATE INDEX hla_type IF NOT EXISTS FOR (h:HLA) ON (h.type)')
    session.run('CREATE INDEX relationship_type IF NOT EXISTS FOR ()-[r]-() ON (type(r))')
    
    print('知识图谱索引创建完成')
    
    # 加载风湿免疫疾病相关数据
    print('加载风湿免疫疾病数据...')
    with open('/app/comprehensive_endocrine_knowledge_graph.json', 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    # 统计风湿免疫疾病实体
    rheumatic_diseases = []
    for key, value in kg_data.items():
        if isinstance(value, dict) and key.startswith('RHEUM_'):
            rheumatic_diseases.append(value)
    
    print(f'已加载 {len(rheumatic_diseases)} 个风湿免疫疾病实体')
    
    # 验证关联关系数据
    if 'rheumatic_endocrine_relationships' in kg_data:
        relationships = kg_data['rheumatic_endocrine_relationships']
        matrix_size = len(relationships.get('disease_relationship_matrix', {}))
        print(f'已加载 {matrix_size} 个疾病关联矩阵')
    
    print('风湿免疫疾病知识图谱初始化完成')

driver.close()
"
fi

# 创建日志目录
mkdir -p /app/logs

# 设置环境变量默认值
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-8000}
export LOG_LEVEL=${LOG_LEVEL:-info}
export WORKERS=${WORKERS:-4}

echo "API服务配置:"
echo "  - Host: $API_HOST"  
echo "  - Port: $API_PORT"
echo "  - Workers: $WORKERS"
echo "  - Log Level: $LOG_LEVEL"

# 启动API服务
echo "启动 FastAPI 服务器..."
exec "$@"