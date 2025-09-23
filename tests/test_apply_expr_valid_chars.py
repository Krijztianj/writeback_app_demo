import pytest
from app import apply_expr

def test_apply_expr_invalid_characters():
    global expr, display_column
    display_column = "Cost Price"
    
    unsafe_expressions = [
        "os.system('rm -rf /')",
        "__import__('os').system('ls')",
        "DROP TABLE products",
        "100; import sys"
    ]
    
    for e in unsafe_expressions:
        expr = e
        with pytest.raises(ValueError):
            apply_expr(100)
