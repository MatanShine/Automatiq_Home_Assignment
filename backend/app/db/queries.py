"""
Backward compatibility module.

This module re-exports functions from the separated modules:
- verifiers: Verification functions
- authorization: Authorization functions  
- regular_employee: Regular employee functions
- ciso: CISO-specific functions

New code should import directly from the specific modules.
"""

# Re-export for backward compatibility
from app.db.verifiers import employee_exists_in_database, is_ciso
from app.db.regular_employee import (
    fetch_employee_data,
    fetch_employee_training_status,
    calculate_employee_time_to_finish_training
)
from app.db.ciso import (
    fetch_all_employees_with_this_training_status,
    get_statistic_summary,
    calculate_time_to_finish_training
)
from app.db.common import calculate_time_diff

__all__ = [
    "employee_exists_in_database",
    "is_ciso",
    "fetch_employee_data",
    "fetch_employee_training_status",
    "calculate_employee_time_to_finish_training",
    "fetch_all_employees_with_this_training_status",
    "get_statistic_summary",
    "calculate_time_to_finish_training",
    "calculate_time_diff",
]
