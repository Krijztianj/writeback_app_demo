import pandas as pd
from apps.writeback_app.app import generate_update_statements, TABLE_NAME

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

    # Strip whitespace for safer comparison
    statements = [s.strip() for s in statements]
    expected = [s.strip() for s in expected]

    assert statements == expected
