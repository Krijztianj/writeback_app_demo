import pytest
from apps.writeback_app.functions import apply_expr

def test_apply_expr_invalid_characters():
    display_column = "Cost Price"
    
    unsafe_expressions = [
        "os.system('rm -rf /')",
        "__import__('os').system('ls')",
        "DROP TABLE products",
        "100; import sys"
    ]
    
    for expr in unsafe_expressions:
        with pytest.raises(ValueError):
            apply_expr(100, expr, display_column)