"""
Caching utilities for analytics queries and LLM responses.
"""
from functools import wraps
from typing import Any, Callable, Optional
from cachetools import TTLCache
import hashlib
import json
import logging

logger = logging.getLogger("cache")

# Analytics cache: 5 minutes TTL (frequent queries that change occasionally)
ANALYTICS_CACHE_TTL = 300  # 5 minutes
ANALYTICS_CACHE_MAXSIZE = 128

# LLM cache: 1 hour TTL (LLM responses are expensive, cache longer)
LLM_CACHE_TTL = 3600  # 1 hour
LLM_CACHE_MAXSIZE = 512

# Create cache instances
analytics_cache = TTLCache(maxsize=ANALYTICS_CACHE_MAXSIZE, ttl=ANALYTICS_CACHE_TTL)
llm_cache = TTLCache(maxsize=LLM_CACHE_MAXSIZE, ttl=LLM_CACHE_TTL)


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    # Convert args and kwargs to a stable string representation
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items()) if kwargs else {}
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def _generate_llm_cache_key(
    user_message: str,
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None,
    history: Optional[list] = None,
    query_type: Optional[str] = None
) -> str:
    """Generate a cache key for LLM queries based on user, message, and context."""
    # Create a stable representation of the query
    cache_data = {
        "message": user_message,
        "employee_id": employee_id,
        "employee_name": employee_name,
        "query_type": query_type,
        # Include history length and last few messages for context
        "history_length": len(history) if history else 0,
        "history_tail": history[-3:] if history and len(history) > 0 else []
    }
    key_str = json.dumps(cache_data, sort_keys=True, default=str)
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


def cache_llm(func: Callable) -> Callable:
    """
    Decorator to cache LLM query results based on user, message, and context.
    Works with async functions.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Extract parameters from function call
        # Function signatures vary:
        # - authenticate_employee(user_message, history=None)
        # - regular_employee_query(user_message, history=None, employee_id=None, employee_name=None)
        # - ciso_query(user_message, history=None, employee_id=None, employee_name=None)
        
        # Get user_message (first positional arg or from kwargs)
        msg = kwargs.get('user_message', args[0] if args else None)
        
        # Get history (second positional arg or from kwargs)
        hist = kwargs.get('history', args[1] if len(args) > 1 else None)
        
        # Get employee_id and employee_name (from kwargs or later positional args)
        emp_id = kwargs.get('employee_id', args[2] if len(args) > 2 else None)
        emp_name = kwargs.get('employee_name', args[3] if len(args) > 3 else None)
        
        qtype = func.__name__
        
        cache_key = f"llm:{qtype}:{_generate_llm_cache_key(msg, emp_id, emp_name, hist, qtype)}"
        
        # Check cache
        if cache_key in llm_cache:
            logger.info(f"Cache HIT for LLM: {qtype} (user: {emp_id})")
            return llm_cache[cache_key]
        
        # Cache miss - execute function
        logger.info(f"Cache MISS for LLM: {qtype} (user: {emp_id})")
        result = await func(*args, **kwargs)
        llm_cache[cache_key] = result
        return result
    
    return async_wrapper


def clear_analytics_cache():
    """Clear all analytics cache entries."""
    analytics_cache.clear()
    logger.info("Analytics cache cleared")


def clear_llm_cache():
    """Clear all LLM cache entries."""
    llm_cache.clear()
    logger.info("LLM cache cleared")


def clear_all_caches():
    """Clear all caches."""
    clear_analytics_cache()
    clear_llm_cache()
    logger.info("All caches cleared")

