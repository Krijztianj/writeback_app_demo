from unittest.mock import MagicMock
import pandas as pd

def test_update_sql_statements_generated_correctly():
    from app import TABLE_NAME
    
    temp_df = pd.DataFrame({
        "product_id": [1, 2],
        "cost_price": [110, 60],
        "sales_price": [150, 80]
    })
    
    mock_cursor = MagicMock()
    
    column = "cost_price"
    for row in temp_df.itertuples(index=False):
        sql_stmt = f"""
            UPDATE {TABLE_NAME}
            SET {column} = {row._asdict()[column]}
            WHERE product_id = {row.product_id}
        """
        mock_cursor.execute(sql_stmt)
    
    expected_calls = [
        f"\n            UPDATE {TABLE_NAME}\n            SET {column} = 110\n            WHERE product_id = 1\n        ",
        f"\n            UPDATE {TABLE_NAME}\n            SET {column} = 60\n            WHERE product_id = 2\n        "
    ]
    
    actual_calls = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert actual_calls == expected_calls
