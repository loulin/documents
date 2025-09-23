# 甲状腺疾病知识图谱部署指南

## 环境准备

### 1. Neo4j 数据库安装

#### Ubuntu/Debian 系统
```bash
# 添加 Neo4j 官方源
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 4.x' | sudo tee -a /etc/apt/sources.list.d/neo4j.list

# 安装 Neo4j
sudo apt update
sudo apt install neo4j

# 启动服务
sudo systemctl enable neo4j
sudo systemctl start neo4j
```

#### macOS 系统
```bash
# 使用 Homebrew 安装
brew install neo4j

# 启动 Neo4j
neo4j start
```

#### Docker 部署
```bash
# 拉取 Neo4j 镜像
docker pull neo4j:4.4

# 运行 Neo4j 容器
docker run \
    --name thyroid-kg-neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/thyroid123 \
    neo4j:4.4
```

### 2. Python 环境配置

```bash
# 创建虚拟环境
python -m venv thyroid_kg_env
source thyroid_kg_env/bin/activate  # Linux/macOS
# 或
thyroid_kg_env\Scripts\activate     # Windows

# 安装依赖
pip install neo4j python-dotenv pandas numpy scikit-learn matplotlib seaborn
```

### 3. 环境变量配置

创建 `.env` 文件：
```bash
# Neo4j 连接配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=thyroid123

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=thyroid_kg.log

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
```

## 系统部署

### 1. 初始化知识图谱

```python
from thyroid_kg_implementation import ThyroidKnowledgeGraph
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 连接数据库并初始化
with ThyroidKnowledgeGraph(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
) as kg:
    # 初始化知识库
    kg.initialize_knowledge_base()
    print("知识图谱初始化完成！")
```

### 2. 验证部署

```python
# 验证脚本
def verify_deployment():
    with ThyroidKnowledgeGraph(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    ) as kg:
        
        # 检查节点数量
        node_counts = kg.run_query("""
        MATCH (n) 
        RETURN labels(n)[0] as node_type, count(n) as count
        ORDER BY count DESC
        """)
        
        print("节点统计:")
        for result in node_counts:
            print(f"- {result['node_type']}: {result['count']} 个")
        
        # 检查关系数量
        rel_counts = kg.run_query("""
        MATCH ()-[r]->() 
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        """)
        
        print("\n关系统计:")
        for result in rel_counts:
            print(f"- {result['rel_type']}: {result['count']} 个")

verify_deployment()
```

### 3. Web API 接口

创建 `api_server.py`：

```python
from flask import Flask, request, jsonify
from thyroid_kg_implementation import *
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 全局知识图谱连接
kg = ThyroidKnowledgeGraph(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)

diagnostic_engine = ThyroidDiagnosticEngine(kg)
treatment_engine = ThyroidTreatmentEngine(kg)

@app.route('/diagnose', methods=['POST'])
def diagnose_patient():
    """患者诊断接口"""
    try:
        data = request.json
        
        # 构建患者数据
        patient = PatientData(
            patient_id=data.get('patient_id', 'unknown'),
            age=data.get('age', 0),
            gender=data.get('gender', ''),
            symptoms=data.get('symptoms', []),
            lab_results=data.get('lab_results', {}),
            medical_history=data.get('medical_history', []),
            current_medications=data.get('current_medications', []),
            allergies=data.get('allergies', []),
            pregnancy_status=data.get('pregnancy_status', False),
            comorbidities=data.get('comorbidities', [])
        )
        
        # 执行诊断
        result = diagnostic_engine.diagnose(patient)
        
        return jsonify({
            'success': True,
            'diagnosis': {
                'disease': result.disease,
                'confidence': result.confidence,
                'supporting_evidence': result.supporting_evidence,
                'differential_diagnosis': result.differential_diagnosis,
                'recommended_tests': result.recommended_tests
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/treatment', methods=['POST'])
def recommend_treatment():
    """治疗推荐接口"""
    try:
        data = request.json
        diagnosis = data.get('diagnosis')
        
        # 构建患者数据
        patient = PatientData(
            patient_id=data.get('patient_id', 'unknown'),
            age=data.get('age', 0),
            gender=data.get('gender', ''),
            symptoms=data.get('symptoms', []),
            lab_results=data.get('lab_results', {}),
            medical_history=data.get('medical_history', []),
            current_medications=data.get('current_medications', []),
            allergies=data.get('allergies', []),
            pregnancy_status=data.get('pregnancy_status', False),
            comorbidities=data.get('comorbidities', [])
        )
        
        # 获取治疗建议
        recommendations = treatment_engine.recommend_treatment(diagnosis, patient)
        
        treatment_list = []
        for rec in recommendations:
            treatment_list.append({
                'treatment_name': rec.treatment_name,
                'medication': rec.medication,
                'dosage': rec.dosage,
                'duration': rec.duration,
                'monitoring_plan': rec.monitoring_plan,
                'contraindications': rec.contraindications,
                'success_probability': rec.success_probability
            })
        
        return jsonify({
            'success': True,
            'recommendations': treatment_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        result = kg.run_query("RETURN 1 as test")
        if result:
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 8000)),
        debug=os.getenv('API_DEBUG', 'True').lower() == 'true'
    )
```

### 4. 启动服务

```bash
# 启动 API 服务
python api_server.py

# 或使用 gunicorn (生产环境)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
```

## 使用示例

### 1. 命令行使用

```python
from thyroid_kg_implementation import *

# 创建患者数据
patient = PatientData(
    patient_id="P001",
    age=35,
    gender="女",
    symptoms=["心悸", "体重下降", "怕热多汗"],
    lab_results={
        "TSH": 0.05,
        "FT4": 35.0,
        "TRAb": 8.5
    },
    medical_history=[],
    current_medications=[],
    allergies=[],
    pregnancy_status=False,
    comorbidities=[]
)

# 连接知识图谱并诊断
with ThyroidKnowledgeGraph("bolt://localhost:7687", "neo4j", "thyroid123") as kg:
    diagnostic_engine = ThyroidDiagnosticEngine(kg)
    treatment_engine = ThyroidTreatmentEngine(kg)
    
    # 执行诊断
    diagnosis = diagnostic_engine.diagnose(patient)
    print(f"诊断: {diagnosis.disease} (置信度: {diagnosis.confidence:.2f})")
    
    # 获取治疗建议
    treatments = treatment_engine.recommend_treatment(diagnosis.disease, patient)
    for treatment in treatments:
        print(f"治疗: {treatment.treatment_name}")
        print(f"药物: {treatment.medication}")
        print(f"剂量: {treatment.dosage}")
```

### 2. HTTP API 调用

#### 诊断接口调用
```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "age": 35,
    "gender": "女",
    "symptoms": ["心悸", "体重下降", "怕热多汗"],
    "lab_results": {
      "TSH": 0.05,
      "FT4": 35.0,
      "TRAb": 8.5
    },
    "pregnancy_status": false
  }'
```

#### 治疗推荐接口调用
```bash
curl -X POST http://localhost:8000/treatment \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "diagnosis": "Graves病",
    "age": 35,
    "gender": "女",
    "pregnancy_status": false,
    "comorbidities": []
  }'
```

### 3. Python 客户端示例

```python
import requests
import json

class ThyroidKGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def diagnose(self, patient_data):
        """患者诊断"""
        response = requests.post(
            f"{self.base_url}/diagnose",
            json=patient_data
        )
        return response.json()
    
    def get_treatment(self, diagnosis, patient_data):
        """获取治疗建议"""
        data = patient_data.copy()
        data['diagnosis'] = diagnosis
        
        response = requests.post(
            f"{self.base_url}/treatment",
            json=data
        )
        return response.json()

# 使用客户端
client = ThyroidKGClient()

patient_data = {
    "patient_id": "P001",
    "age": 35,
    "gender": "女",
    "symptoms": ["心悸", "体重下降", "怕热多汗"],
    "lab_results": {
        "TSH": 0.05,
        "FT4": 35.0,
        "TRAb": 8.5
    },
    "pregnancy_status": False
}

# 诊断
diagnosis_result = client.diagnose(patient_data)
print("诊断结果:", diagnosis_result)

# 治疗建议
if diagnosis_result['success']:
    diagnosis = diagnosis_result['diagnosis']['disease']
    treatment_result = client.get_treatment(diagnosis, patient_data)
    print("治疗建议:", treatment_result)
```

## 性能优化

### 1. 数据库索引优化

```cypher
// 创建复合索引
CREATE INDEX disease_category_idx IF NOT EXISTS 
FOR (d:Disease) ON (d.category, d.name);

CREATE INDEX symptom_category_idx IF NOT EXISTS 
FOR (s:Symptom) ON (s.category, s.name);

CREATE INDEX medication_class_idx IF NOT EXISTS 
FOR (m:Medication) ON (m.drug_class, m.name);

// 查看索引状态
SHOW INDEXES;
```

### 2. 查询优化

```cypher
// 使用 PROFILE 分析查询性能
PROFILE 
MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
WHERE s.name IN ['心悸', '体重下降']
RETURN d.name, avg(r.probability)
ORDER BY avg(r.probability) DESC;

// 使用 EXPLAIN 查看执行计划
EXPLAIN 
MATCH (d:Disease {name: 'Graves病'})-[r:TREATED_BY]->(t:Treatment)
RETURN t.name, r.effectiveness;
```

### 3. 连接池配置

```python
from neo4j import GraphDatabase

# 配置连接池
config = {
    'max_connection_lifetime': 1000,
    'max_connection_pool_size': 50,
    'connection_acquisition_timeout': 60,
    'connection_timeout': 60,
    'max_retry_time': 15,
    'resolver': None,
    'trust': 'TRUST_ALL_CERTIFICATES',
    'encrypted': False
}

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password"),
    **config
)
```

## 监控和维护

### 1. 系统监控

```python
import psutil
import time

def monitor_system():
    """系统性能监控"""
    while True:
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%")
        
        # 检查 Neo4j 连接
        try:
            with ThyroidKnowledgeGraph("bolt://localhost:7687", "neo4j", "password") as kg:
                result = kg.run_query("RETURN 1")
                db_status = "OK" if result else "ERROR"
        except:
            db_status = "DISCONNECTED"
        
        print(f"Database: {db_status}")
        print("-" * 50)
        
        time.sleep(60)  # 每分钟检查一次

# 启动监控
monitor_system()
```

### 2. 数据备份

```bash
#!/bin/bash
# 备份脚本 backup_kg.sh

BACKUP_DIR="/opt/thyroid_kg_backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="thyroid_kg_backup_${DATE}"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 停止 Neo4j 服务
sudo systemctl stop neo4j

# 复制数据文件
cp -r /var/lib/neo4j/data ${BACKUP_DIR}/${BACKUP_FILE}

# 压缩备份
tar -czf ${BACKUP_DIR}/${BACKUP_FILE}.tar.gz -C ${BACKUP_DIR} ${BACKUP_FILE}

# 删除未压缩的备份
rm -rf ${BACKUP_DIR}/${BACKUP_FILE}

# 启动 Neo4j 服务
sudo systemctl start neo4j

# 保留最近30天的备份
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: ${BACKUP_DIR}/${BACKUP_FILE}.tar.gz"
```

### 3. 日志分析

```python
import re
from collections import defaultdict
from datetime import datetime

def analyze_logs(log_file):
    """分析系统日志"""
    error_patterns = defaultdict(int)
    request_counts = defaultdict(int)
    response_times = []
    
    with open(log_file, 'r') as f:
        for line in f:
            # 错误模式分析
            if 'ERROR' in line:
                error_match = re.search(r'ERROR.*?:(.*)', line)
                if error_match:
                    error_patterns[error_match.group(1).strip()] += 1
            
            # 请求统计
            if 'POST' in line or 'GET' in line:
                endpoint_match = re.search(r'(POST|GET)\s+(\S+)', line)
                if endpoint_match:
                    request_counts[endpoint_match.group(2)] += 1
            
            # 响应时间分析
            time_match = re.search(r'response_time:(\d+\.?\d*)ms', line)
            if time_match:
                response_times.append(float(time_match.group(1)))
    
    # 输出分析结果
    print("错误统计:")
    for error, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {error}: {count} 次")
    
    print("\n请求统计:")
    for endpoint, count in sorted(request_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {endpoint}: {count} 次")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        print(f"\n响应时间: 平均 {avg_time:.2f}ms, 最大 {max_time:.2f}ms, 最小 {min_time:.2f}ms")

# 分析日志
analyze_logs("thyroid_kg.log")
```

## 故障排除

### 常见问题及解决方案

1. **Neo4j 连接失败**
   ```bash
   # 检查服务状态
   sudo systemctl status neo4j
   
   # 查看日志
   sudo journalctl -u neo4j -f
   
   # 重启服务
   sudo systemctl restart neo4j
   ```

2. **内存不足**
   ```bash
   # 增加 Neo4j 内存配置
   sudo nano /etc/neo4j/neo4j.conf
   
   # 添加或修改以下配置
   dbms.memory.heap.initial_size=2g
   dbms.memory.heap.max_size=4g
   dbms.memory.pagecache.size=2g
   ```

3. **查询性能慢**
   ```cypher
   // 查看慢查询
   CALL dbms.listQueries() YIELD query, elapsedTimeMillis
   WHERE elapsedTimeMillis > 1000
   RETURN query, elapsedTimeMillis;
   
   // 杀死慢查询
   CALL dbms.killQuery('query-id');
   ```

这个部署指南提供了完整的系统搭建、配置、使用和维护方案，确保甲状腺疾病知识图谱能够稳定高效地运行。