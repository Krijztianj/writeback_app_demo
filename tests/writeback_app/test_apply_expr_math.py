import pytest
from apps.writeback_app.functions import apply_expr

def test_apply_expr_with_column_value():
    global expr, display_column
    display_column = "Cost Price"
    
    test_cases = [
        (100, "Cost Price * 2", 200),
        (50, "Cost Price + 25", 75),
        (80, "Cost Price - 30", 50)
    ]
    
    for old_value, e, expected in test_cases:
        expr = e
        result = apply_expr(old_value)
        assert result == expected
