import pytest
from apps.writeback_app.functions import apply_expr

def test_apply_expr_with_column_value():
    display_column = "Cost Price"

    test_cases = [
        (100, "Cost Price * 2", 200),
        (50, "Cost Price + 25", 75),
        (80, "Cost Price - 30", 50)
    ]

    for old_value, expr, expected in test_cases:
        result = apply_expr(old_value, expr, display_column)
        assert result == expected
