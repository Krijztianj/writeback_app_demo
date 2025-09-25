import pandas as pd
from apps.writeback_app.functions import generate_update_statements, TABLE_NAME

def test_generate_update_statements():
    temp_df = pd.DataFrame({
        "product_id": [1, 2],
        "cost_price": [110, 60],
        "sales_price": [150, 80]
    })

    column = "cost_price"
    statements = generate_update_statements(temp_df, column, TABLE_NAME)

    expected = [
        f"""
            UPDATE {TABLE_NAME}
            SET {column} = 110
            WHERE product_id = 1
        """,
        f"""
            UPDATE {TABLE_NAME}
            SET {column} = 60
            WHERE product_id = 2
        """
    ]

    # Normalize both sides by stripping whitespace and line breaks
    normalized_statements = [" ".join(s.split()) for s in statements]
    normalized_expected = [" ".join(s.split()) for s in expected]

    assert normalized_statements == normalized_expected
