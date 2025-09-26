#!/usr/bin/env python3
"""
糖尿病知识图谱API服务器
基于FastAPI构建的RESTful API服务
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uvicorn
import json
from diabetes_kg_inference_engine import DiabetesQASystem, QueryResult, QueryType, EntityType

# Pydantic模型定义
class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户问题", min_length=1, max_length=500)
    user_id: Optional[str] = Field(None, description="用户ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class QuestionResponse(BaseModel):
    question: str
    query_type: str
    answer: str
    confidence: float
    entities_found: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    sources: List[str]
    response_time: float
    timestamp: datetime


class EntityInfo(BaseModel):
    id: str
    name: str
    name_en: str
    type: str
    category: str
    description: str
    properties: Dict[str, Any]


class HealthStatus(BaseModel):
    service: str = "diabetes-kg-api"
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
    entities_count: int
    relationships_count: int


class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    entity_types: Optional[List[str]] = Field(None, description="限定实体类型")
    limit: Optional[int] = Field(10, description="返回结果数量限制")


# 初始化应用
app = FastAPI(
    title="糖尿病知识图谱API",
    description="基于第一性原理构建的糖尿病知识问答系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
qa_system = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global qa_system
    qa_system = DiabetesQASystem()
    print("糖尿病知识图谱系统初始化完成")


def get_qa_system():
    """获取问答系统实例"""
    if qa_system is None:
        raise HTTPException(status_code=503, detail="系统初始化中，请稍后重试")
    return qa_system


# API路由定义
@app.get("/", response_class=HTMLResponse)
async def root():
    """首页 - 简单的演示界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>糖尿病知识图谱问答系统</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: #2c3e50; }
            .question-box { margin: 20px 0; }
            .question-input { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #3498db; border-radius: 8px; }
            .ask-button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            .answer-box { margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 8px; }
            .loading { color: #7f8c8d; }
            .examples { margin: 20px 0; }
            .example-btn { margin: 5px; padding: 8px 15px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1 class="header">🩺 糖尿病知识图谱问答系统</h1>
        
        <div class="question-box">
            <input type="text" id="questionInput" class="question-input" placeholder="请输入您的问题，例如：糖尿病如何诊断？" />
            <button onclick="askQuestion()" class="ask-button">询问</button>
        </div>
        
        <div class="examples">
            <h3>示例问题：</h3>
            <button class="example-btn" onclick="setQuestion('糖尿病如何诊断？')">糖尿病如何诊断？</button>
            <button class="example-btn" onclick="setQuestion('2型糖尿病怎么治疗？')">2型糖尿病怎么治疗？</button>
            <button class="example-btn" onclick="setQuestion('如何预防糖尿病？')">如何预防糖尿病？</button>
            <button class="example-btn" onclick="setQuestion('血糖高了怎么办？')">血糖高了怎么办？</button>
        </div>
        
        <div id="answerBox" class="answer-box" style="display: none;">
            <h3>答案：</h3>
            <div id="answerContent"></div>
            <div id="metadata" style="margin-top: 15px; font-size: 12px; color: #7f8c8d;"></div>
        </div>

        <script>
            function setQuestion(question) {
                document.getElementById('questionInput').value = question;
            }
            
            async function askQuestion() {
                const question = document.getElementById('questionInput').value;
                if (!question.trim()) {
                    alert('请输入问题');
                    return;
                }
                
                const answerBox = document.getElementById('answerBox');
                const answerContent = document.getElementById('answerContent');
                const metadata = document.getElementById('metadata');
                
                answerBox.style.display = 'block';
                answerContent.innerHTML = '<div class="loading">正在思考中...</div>';
                metadata.innerHTML = '';
                
                try {
                    const response = await fetch('/api/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question }),
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        answerContent.innerHTML = result.answer.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                        metadata.innerHTML = `
                            查询类型: ${result.query_type} | 
                            置信度: ${(result.confidence * 100).toFixed(1)}% | 
                            响应时间: ${result.response_time.toFixed(2)}秒
                        `;
                    } else {
                        answerContent.innerHTML = '<div style="color: red;">错误: ' + result.detail + '</div>';
                    }
                } catch (error) {
                    answerContent.innerHTML = '<div style="color: red;">网络错误，请重试</div>';
                }
            }
            
            // 支持回车键提交
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askQuestion();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/health", response_model=HealthStatus)
async def health_check(system: DiabetesQASystem = Depends(get_qa_system)):
    """健康检查接口"""
    return HealthStatus(
        timestamp=datetime.now(),
        entities_count=len(system.kg.entities),
        relationships_count=len(system.kg.relationships)
    )


@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    system: DiabetesQASystem = Depends(get_qa_system)
):
    """问答接口 - 核心功能"""
    start_time = datetime.now()
    
    try:
        # 调用问答系统
        result = system.answer_question(request.question)
        
        # 计算响应时间
        response_time = (datetime.now() - start_time).total_seconds()
        
        # 转换实体信息
        entities_info = []
        for entity in result.entities_found:
            entities_info.append({
                "id": entity.id,
                "name": entity.name,
                "name_en": entity.name_en,
                "type": entity.type.value,
                "category": entity.category,
                "description": entity.description,
                "properties": entity.properties
            })
        
        # 转换关系信息
        relationships_info = []
        for rel in result.relationships:
            relationships_info.append({
                "id": rel.id,
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "relation_type": rel.relation_type.value,
                "strength": rel.strength,
                "evidence_level": rel.evidence_level,
                "properties": rel.properties
            })
        
        return QuestionResponse(
            question=result.query_text,
            query_type=result.query_type.value,
            answer=result.answer,
            confidence=result.confidence,
            entities_found=entities_info,
            relationships=relationships_info,
            sources=result.sources,
            response_time=response_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")


@app.get("/api/entities", response_model=List[EntityInfo])
async def get_entities(
    entity_type: Optional[str] = Query(None, description="过滤实体类型"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=200),
    system: DiabetesQASystem = Depends(get_qa_system)
):
    """获取实体列表"""
    entities = []
    count = 0
    
    for entity in system.kg.entities.values():
        if entity_type and entity.type.value != entity_type:
            continue
            
        entities.append(EntityInfo(
            id=entity.id,
            name=entity.name,
            name_en=entity.name_en,
            type=entity.type.value,
            category=entity.category,
            description=entity.description,
            properties=entity.properties
        ))
        
        count += 1
        if count >= limit:
            break
    
    return entities


@app.get("/api/entities/{entity_id}", response_model=EntityInfo)
async def get_entity_by_id(
    entity_id: str,
    system: DiabetesQASystem = Depends(get_qa_system)
):
    """根据ID获取特定实体"""
    if entity_id not in system.kg.entities:
        raise HTTPException(status_code=404, detail="实体不存在")
    
    entity = system.kg.entities[entity_id]
    return EntityInfo(
        id=entity.id,
        name=entity.name,
        name_en=entity.name_en,
        type=entity.type.value,
        category=entity.category,
        description=entity.description,
        properties=entity.properties
    )


@app.post("/api/search")
async def search_entities(
    request: SearchRequest,
    system: DiabetesQASystem = Depends(get_qa_system)
):
    """搜索实体"""
    results = []
    query_lower = request.query.lower()
    
    for entity in system.kg.entities.values():
        # 检查实体类型过滤
        if request.entity_types and entity.type.value not in request.entity_types:
            continue
        
        # 简单的文本匹配搜索
        if (query_lower in entity.name.lower() or 
            query_lower in entity.name_en.lower() or
            query_lower in entity.description.lower()):
            
            results.append({
                "id": entity.id,
                "name": entity.name,
                "name_en": entity.name_en,
                "type": entity.type.value,
                "category": entity.category,
                "description": entity.description
            })
            
            if len(results) >= request.limit:
                break
    
    return {
        "query": request.query,
        "total_found": len(results),
        "results": results
    }


@app.get("/api/stats")
async def get_statistics(system: DiabetesQASystem = Depends(get_qa_system)):
    """获取系统统计信息"""
    entity_stats = {}
    for entity in system.kg.entities.values():
        entity_type = entity.type.value
        if entity_type not in entity_stats:
            entity_stats[entity_type] = 0
        entity_stats[entity_type] += 1
    
    relation_stats = {}
    for rel in system.kg.relationships:
        rel_type = rel.relation_type.value
        if rel_type not in relation_stats:
            relation_stats[rel_type] = 0
        relation_stats[rel_type] += 1
    
    return {
        "total_entities": len(system.kg.entities),
        "total_relationships": len(system.kg.relationships),
        "entity_distribution": entity_stats,
        "relationship_distribution": relation_stats,
        "inference_rules": len(system.inference_engine.inference_rules)
    }


# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "资源不存在", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "服务器内部错误", "detail": str(exc)}


if __name__ == "__main__":
    uvicorn.run(
        "diabetes_kg_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )