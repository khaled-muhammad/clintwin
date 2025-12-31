"""
Caching Utility
===============
Simple in-memory LRU cache with TTL support.
"""
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from collections import OrderedDict
import time
import asyncio
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LRUCache:
    """
    Thread-safe LRU cache with TTL support.
    
    For production, replace with Redis.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl  # seconds
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: dict = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None
            
            # Check TTL
            if self._is_expired(key):
                self._remove(key)
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL."""
        async with self._lock:
            # Remove oldest if at capacity
            while len(self._cache) >= self.max_size:
                oldest = next(iter(self._cache))
                self._remove(oldest)
            
            self._cache[key] = value
            self._timestamps[key] = (time.time(), ttl or self.default_ttl)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        async with self._lock:
            self._remove(key)
    
    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key not in self._timestamps:
            return True
        created_at, ttl = self._timestamps[key]
        return time.time() - created_at > ttl
    
    def _remove(self, key: str):
        """Remove key from cache (not thread-safe, use within lock)."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    async def cleanup(self):
        """Remove expired entries."""
        async with self._lock:
            expired_keys = [k for k in self._cache if self._is_expired(k)]
            for key in expired_keys:
                self._remove(key)
            if expired_keys:
                logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries")


# Global cache instance
_cache: Optional[LRUCache] = None


def get_cache() -> LRUCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = LRUCache(max_size=1000, default_ttl=300)
    return _cache


def _make_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching async function results.
    
    Usage:
        @cached(ttl=60, key_prefix="medicines")
        async def get_medicines():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cache = get_cache()
            
            # Generate cache key
            key = f"{key_prefix}:{func.__name__}:{_make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl)
            logger.debug(f"Cache miss, stored: {key}")
            
            return result
        return wrapper
    return decorator


def cached_sync(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching sync function results.
    
    For synchronous functions that don't need async.
    """
    _sync_cache: dict = {}
    _sync_timestamps: dict = {}
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            key = f"{key_prefix}:{func.__name__}:{_make_cache_key(*args, **kwargs)}"
            
            # Check cache
            if key in _sync_cache:
                created_at, cached_ttl = _sync_timestamps.get(key, (0, 0))
                if time.time() - created_at <= cached_ttl:
                    return _sync_cache[key]
            
            # Call function
            result = func(*args, **kwargs)
            _sync_cache[key] = result
            _sync_timestamps[key] = (time.time(), ttl)
            
            return result
        return wrapper
    return decorator
