#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康顾问API服务示例
基于FastAPI的RESTful接口实现
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from health_advisor_integration import HealthAdvisorSystem

# 数据模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    user_id: str = "default"
    user_profile: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    status: str
    response: str
    type: str
    knowledge_used: Optional[list] = None
    rules_applied: Optional[int] = None
    processing_steps: Optional[list] = None

class UserProfileRequest(BaseModel):
    """用户档案请求模型"""
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    disease_ids: Optional[list] = None
    medication_ids: Optional[list] = None

# 创建FastAPI应用
app = FastAPI(
    title="健康顾问API",
    description="基于知识库的智能健康咨询系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局健康顾问系统实例
advisor_system = HealthAdvisorSystem()

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 健康顾问API服务启动成功!")
    print("📚 知识库加载完成")
    print("🔗 接口地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "健康顾问API服务",
        "status": "running",
        "docs": "/docs"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    健康咨询聊天接口
    
    Args:
        request: 聊天请求
        
    Returns:
        ChatResponse: 聊天响应
    """
    try:
        # 处理用户输入
        result = advisor_system.process_user_input(
            message=request.message,
            user_id=request.user_id,
            user_profile=request.user_profile
        )
        
        return ChatResponse(
            status="success",
            response=result["response"],
            type=result["type"],
            knowledge_used=result.get("knowledge_used"),
            rules_applied=result.get("rules_applied"),
            processing_steps=result.get("processing_steps")
        )
        
    except Exception as e:
        print(f"❌ 处理聊天请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/profile")
async def update_user_profile(request: UserProfileRequest):
    """
    更新用户档案接口
    
    Args:
        request: 用户档案请求
        
    Returns:
        dict: 更新结果
    """
    try:
        # 这里应该连接数据库存储用户档案
        # 目前只是示例实现
        user_profile = {
            "user_id": request.user_id,
            "age": request.age,
            "gender": request.gender,
            "disease_ids": request.disease_ids or [],
            "medication_ids": request.medication_ids or [],
            "updated_at": "2025-09-05T10:00:00Z"
        }
        
        # 存储到系统中（实际应该存储到数据库）
        advisor_system.user_profiles[request.user_id] = user_profile
        
        return {
            "status": "success",
            "message": "用户档案更新成功",
            "user_profile": user_profile
        }
        
    except Exception as e:
        print(f"❌ 更新用户档案时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    获取用户档案接口
    
    Args:
        user_id: 用户ID
        
    Returns:
        dict: 用户档案
    """
    try:
        profile = advisor_system.user_profiles.get(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="用户档案未找到")
            
        return {
            "status": "success",
            "user_profile": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取用户档案时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """
    获取知识库统计信息
    
    Returns:
        dict: 知识库统计
    """
    try:
        stats = {}
        for kb_name, kb_data in advisor_system.knowledge_bases.items():
            if isinstance(kb_data, list):
                stats[kb_name] = {"type": "list", "count": len(kb_data)}
            elif isinstance(kb_data, dict):
                stats[kb_name] = {"type": "dict", "keys": len(kb_data)}
            else:
                stats[kb_name] = {"type": type(kb_data).__name__, "loaded": bool(kb_data)}
                
        return {
            "status": "success",
            "knowledge_bases": stats,
            "core_prompt_loaded": bool(advisor_system.core_prompt)
        }
        
    except Exception as e:
        print(f"❌ 获取知识库统计时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": "2025-09-05T10:00:00Z",
        "version": "1.0.0"
    }

# 用于本地开发的启动函数
def start_server():
    """启动开发服务器"""
    uvicorn.run(
        "api_server_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()