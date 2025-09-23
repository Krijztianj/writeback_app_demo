import pandas as pd
from apps.writeback_app.app import apply_expr

def test_new_price_structure_preview():
    df = pd.DataFrame({
        "Cost Price": [100, 50],
        "Sales Price": [150, 80]
    })
    
    global expr, display_column
    display_column = "Cost Price"
    expr = "Cost Price + 10"
    
    df_copy = df.copy()
    df_copy[display_column] = df_copy[display_column].apply(apply_expr)
    
    expected = pd.DataFrame({
        "Cost Price": [110, 60],
        "Sales Price": [150, 80]
    })
    
    pd.testing.assert_frame_equal(df_copy, expected)
