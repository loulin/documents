"""
缓存模块
提供本地缓存功能，支持内存缓存和Redis缓存
"""

import json
import time
import asyncio
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import aioredis

@dataclass
class CacheConfig:
    """缓存配置"""
    type: str = "memory"  # "memory" or "redis"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    expire: int = 3600  # 默认1小时过期
    max_size: int = 1000  # 内存缓存最大条目数

class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, config: CacheConfig):
        """初始化内存缓存
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self._cache: Dict[str, Dict] = {}
        self._expire_times: Dict[str, float] = {}
        
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值
        """
        if key not in self._cache:
            return None
            
        # 检查是否过期
        if key in self._expire_times:
            if time.time() > self._expire_times[key]:
                await self.delete(key)
                return None
                
        return self._cache[key]
        
    async def set(self, 
                  key: str, 
                  value: Any, 
                  expire: Optional[int] = None) -> bool:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
            
        Returns:
            bool: 是否成功
        """
        # 检查缓存大小
        if len(self._cache) >= self.config.max_size:
            # 移除最早过期的项
            await self._remove_oldest()
            
        self._cache[key] = value
        
        # 设置过期时间
        if expire is not None:
            self._expire_times[key] = time.time() + expire
        elif self.config.expire > 0:
            self._expire_times[key] = time.time() + self.config.expire
            
        return True
        
    async def delete(self, key: str) -> bool:
        """删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功
        """
        self._cache.pop(key, None)
        self._expire_times.pop(key, None)
        return True
        
    async def clear(self) -> bool:
        """清空缓存
        
        Returns:
            bool: 是否成功
        """
        self._cache.clear()
        self._expire_times.clear()
        return True
        
    async def _remove_oldest(self):
        """移除最早过期的缓存项"""
        if not self._expire_times:
            # 如果没有过期时间，删除任意一项
            if self._cache:
                key = next(iter(self._cache))
                await self.delete(key)
            return
            
        # 找到最早过期的项
        oldest_key = min(
            self._expire_times.items(),
            key=lambda x: x[1]
        )[0]
        await self.delete(oldest_key)

class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config: CacheConfig):
        """初始化Redis缓存
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self._redis = None
        
    async def _ensure_connection(self):
        """确保Redis连接存在"""
        if self._redis is None:
            self._redis = await aioredis.create_redis_pool(
                f'redis://{self.config.host}:{self.config.port}',
                db=self.config.db,
                password=self.config.password,
                encoding='utf-8'
            )
            
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值
        """
        await self._ensure_connection()
        value = await self._redis.get(key)
        if value is None:
            return None
        return json.loads(value)
        
    async def set(self, 
                  key: str, 
                  value: Any, 
                  expire: Optional[int] = None) -> bool:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
            
        Returns:
            bool: 是否成功
        """
        await self._ensure_connection()
        
        # 序列化值
        value_str = json.dumps(value)
        
        # 设置过期时间
        if expire is not None:
            await self._redis.setex(key, expire, value_str)
        elif self.config.expire > 0:
            await self._redis.setex(key, self.config.expire, value_str)
        else:
            await self._redis.set(key, value_str)
            
        return True
        
    async def delete(self, key: str) -> bool:
        """删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否成功
        """
        await self._ensure_connection()
        await self._redis.delete(key)
        return True
        
    async def clear(self) -> bool:
        """清空缓存
        
        Returns:
            bool: 是否成功
        """
        await self._ensure_connection()
        await self._redis.flushdb()
        return True
        
    async def close(self):
        """关闭Redis连接"""
        if self._redis is not None:
            self._redis.close()
            await self._redis.wait_closed()
            self._redis = None

class Cache:
    """缓存统一接口"""
    
    def __init__(self, config: Dict = None):
        """初始化缓存
        
        Args:
            config: 缓存配置
        """
        # 合并默认配置
        config = config or {}
        self.config = CacheConfig(**config)
        
        # 根据配置类型创建具体实现
        if self.config.type == "redis":
            self._impl = RedisCache(self.config)
        else:
            self._impl = MemoryCache(self.config)
            
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return await self._impl.get(key)
        
    async def set(self, 
                  key: str, 
                  value: Any, 
                  expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        return await self._impl.set(key, value, expire)
        
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        return await self._impl.delete(key)
        
    async def clear(self) -> bool:
        """清空缓存"""
        return await self._impl.clear()
        
    async def close(self):
        """关闭缓存"""
        if hasattr(self._impl, 'close'):
            await self._impl.close()
            
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        """异步上下文管理器退出"""
        await self.close()
