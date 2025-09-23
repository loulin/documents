# 使用官方Python 3.11基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 下载spaCy模型
RUN python -m spacy download en_core_web_sm \
    && python -m spacy download zh_core_web_sm

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 设置权限
RUN chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动脚本
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认命令
CMD ["uvicorn", "endocrine_knowledge_graph_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]