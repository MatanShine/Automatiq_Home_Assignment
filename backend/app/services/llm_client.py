"""
LLM client module - main entry point for LLM functionality.

This module maintains backward compatibility by re-exporting the main query functions.
The implementation has been split into logical modules:
- llm_config.py: Configuration constants
- llm_client_setup.py: OpenAI client initialization
- llm_responses.py: Response utilities
- llm_formatters.py: Data formatting functions
- llm_tool_handlers.py: Tool handler functions
- llm_queries.py: Main query execution functions
"""

# Re-export main query functions for backward compatibility
from app.services.llm_queries import (
    authenticate_employee,
    regular_employee_query,
    ciso_query
)

# Re-export types and utilities if needed elsewhere
from app.services.llm_responses import QueryResponse

__all__ = [
    "authenticate_employee",
    "regular_employee_query",
    "ciso_query",
    "QueryResponse",
]
