from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
WAREHOUSE_HTTP_PATH = "/sql/1.0/warehouses/5eced0d6af754723"
TABLE_NAME = "app_demos.writeback.products"

def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=WAREHOUSE_HTTP_PATH,
        credentials_provider=lambda: cfg.authenticate
    )

def init_products_table(conn):
    """Create products table if it does not exist."""
    with open("resources/products.sql", "r") as f:
        sql_script = f.read()
    with conn.cursor() as cursor:
        cursor.execute(sql_script)

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