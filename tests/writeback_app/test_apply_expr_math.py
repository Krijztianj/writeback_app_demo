import pytest
from decimal import Decimal
from apps.writeback_app.functions import apply_expr

def test_apply_expr_with_column_value():
    display_column = "Cost Price"

    test_cases = [
        (Decimal("100"), "Cost Price * 2", Decimal("200")),
        (Decimal("50"), "Cost Price + 25", Decimal("75")),
        (Decimal("80"), "Cost Price - 30", Decimal("50")),
    ]

    for old_value, expr, expected in test_cases:
        result = apply_expr(old_value, expr, display_column)
        assert result == expected
