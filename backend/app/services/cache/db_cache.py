"""
Database/analytics query caching utilities.
"""
from functools import wraps
from typing import Any, Callable
from cachetools import TTLCache
import hashlib
import json
import logging

logger = logging.getLogger("cache.db")

# Analytics cache: 5 minutes TTL (frequent queries that change occasionally)
ANALYTICS_CACHE_TTL = 300  # 5 minutes
ANALYTICS_CACHE_MAXSIZE = 128

# Create cache instance
analytics_cache = TTLCache(maxsize=ANALYTICS_CACHE_MAXSIZE, ttl=ANALYTICS_CACHE_TTL)


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    # Convert args and kwargs to a stable string representation
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items()) if kwargs else {}
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_analytics(func: Callable) -> Callable:
    """
    Decorator to cache analytics query results.
    Caches based on function arguments with TTL.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}:{_generate_cache_key(*args, **kwargs)}"
        
        # Check cache
        if cache_key in analytics_cache:
            logger.debug(f"Cache HIT for analytics: {func.__name__}")
            return analytics_cache[cache_key]
        
        # Cache miss - execute function
        logger.debug(f"Cache MISS for analytics: {func.__name__}")
        result = func(*args, **kwargs)
        analytics_cache[cache_key] = result
        return result
    
    return wrapper


def clear_analytics_cache():
    """Clear all analytics cache entries."""
    analytics_cache.clear()
    logger.info("Analytics cache cleared")

