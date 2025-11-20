"""
Cache utilities package.
"""
from app.services.cache.db_cache import (
    cache_analytics,
    clear_analytics_cache
)
from app.services.cache.llm_cache import (
    cache_llm,
    clear_llm_cache
)


def clear_all_caches():
    """Clear all caches (both DB and LLM)."""
    clear_analytics_cache()
    clear_llm_cache()


__all__ = [
    "cache_analytics",
    "cache_llm",
    "clear_analytics_cache",
    "clear_llm_cache",
    "clear_all_caches",
]

