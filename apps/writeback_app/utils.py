from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
WAREHOUSE_HTTP_PATH = "/sql/1.0/warehouses/5eced0d6af754723"
TABLE_NAME = "app_demos.writeback.products"

products_ddl = f"""
CREATE CATALOG IF NOT EXISTS app_demos;
CREATE SCHEMA IF NOT EXISTS app_demos.writeback;

CREATE TABLE IF NOT EXISTS app_demos.writeback.products AS 

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

def init_products_table(conn):
    """Create products table if it does not exist."""
    with conn.cursor() as cursor:
        cursor.execute(products_ddl)

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
