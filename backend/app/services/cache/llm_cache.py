"""
LLM response caching utilities.
"""
from functools import wraps
from typing import Any, Callable, Optional
from cachetools import TTLCache
import hashlib
import json
import logging

logger = logging.getLogger("cache.llm")

# LLM cache: 1 hour TTL (LLM responses are expensive, cache longer)
LLM_CACHE_TTL = 3600  # 1 hour
LLM_CACHE_MAXSIZE = 512

# Create cache instance
llm_cache = TTLCache(maxsize=LLM_CACHE_MAXSIZE, ttl=LLM_CACHE_TTL)


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


def clear_llm_cache():
    """Clear all LLM cache entries."""
    llm_cache.clear()
    logger.info("LLM cache cleared")

