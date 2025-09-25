import re
import pandas as pd
from decimal import Decimal

TABLE_NAME = "workspace.writeback.products"

def apply_expr(value, expr, display_column):
    """Safely evaluate math expression with given column substituted."""
    # Replace column reference with 'val' so eval can use Decimal directly
    safe_expr = expr.replace(display_column, "val")
    if not re.fullmatch(r"[0-9+\-*/(). val]+", safe_expr):
        raise ValueError("Expression contains invalid characters")
    return eval(safe_expr, {"val": Decimal(value), "Decimal": Decimal})

def calculate_profit_impact(df: pd.DataFrame, expr: str, display_column: str) -> float:
    """Calculate profit impact (%) from applying expression to a column."""
    old_profit = (df["Sales Price"].astype(float) - df["Cost Price"].astype(float)).sum()
    temp_df = df.copy()
    temp_df[display_column] = temp_df[display_column].apply(
        lambda val: apply_expr(val, expr, display_column)
    )
    new_profit = (temp_df["Sales Price"].astype(float) - temp_df["Cost Price"].astype(float)).sum()
    return ((new_profit - old_profit) / old_profit) * 100

def generate_update_statements(df: pd.DataFrame, column: str, table_name: str):
    """Generate SQL UPDATE statements for the given column and DataFrame."""
    statements = []
    for row in df.itertuples(index=False):
        stmt = f"""
            UPDATE {table_name}
            SET {column} = {row._asdict()[column]}
            WHERE product_id = {row.product_id}
        """
        statements.append(stmt)
    return statements
