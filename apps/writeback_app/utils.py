from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
WAREHOUSE_HTTP_PATH = "/sql/1.0/warehouses/5eced0d6af754723"
TABLE_NAME = "workspace.writeback.products"

schema_ddl = f"""CREATE SCHEMA IF NOT EXISTS workspace.writeback"""
table_ddl = f"""
CREATE TABLE IF NOT EXISTS workspace.writeback.products AS 

with product as (
select distinct product 

from samples.bakehouse.sales_transactions
),
cost_price as (
select 
product as product_name 
, CAST(FLOOR(rand() * 10) + 1 AS DECIMAL(10,2)) as cost_price
from product )

select 
row_number() OVER(partition by 1 order by 1) AS product_id
, product_name
, cost_price
, cost_price*2 as sales_price
from cost_price
"""

def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=WAREHOUSE_HTTP_PATH,
        credentials_provider=lambda: cfg.authenticate
    )

def table_exists(conn, table_name: str) -> bool:
    cursor = conn.cursor()
    table_name = table_name.split(".")[-1]
    cursor.execute(
        "SELECT table_name FROM system.information_schema.tables WHERE table_name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None

def init_products_table(conn):
    """Create products table if it does not exist."""
    with conn.cursor() as cursor:
        cursor.execute(schema_ddl)
        cursor.execute(table_ddl)


def read_table(conn):
    query = f"""
    SELECT * FROM {TABLE_NAME}
    ORDER BY 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        df = cursor.fetchall_arrow().to_pandas()
    return df

def execute_statements(conn, statements):
    """Execute a list of SQL statements using the given connection."""
    with conn.cursor() as cursor:
        for stmt in statements:
            cursor.execute(stmt)
