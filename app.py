import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config


# Constants
WAREHOUSE_HTTP_PATH = "/sql/1.0/warehouses/341b0ab16cc13ff6"
TABLE_NAME = "krjo_demo.dais_debrief.products"

cfg = Config()

@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=WAREHOUSE_HTTP_PATH,
        credentials_provider=lambda: cfg.authenticate
    )

def read_table(conn):
    query = f"""
    SELECT 
        *
    FROM {TABLE_NAME}
    ORDER BY 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        # Fetch as Arrow and convert to Pandas
        df = cursor.fetchall_arrow().to_pandas()
    return df

# Replace column name in expression with current value
def apply_expr(old):
    safe_expr = expr.replace(display_column, str(old))
    import re
    if not re.fullmatch(r"[0-9+\-*/(). ]+", safe_expr):
        raise ValueError("Expression contains invalid characters")
    return eval(safe_expr)

if "prices_updated" not in st.session_state:
    st.session_state.prices_updated = False

st.title("Update Product Pricing")

# Show confirmation if prices were updated
if st.session_state.prices_updated:
    st.success("Prices have been successfully updated!")
    # Reset the flag so the message only shows once
    st.session_state.prices_updated = False

conn = get_connection()
df = read_table(conn)
st.subheader("Current Price Overview")

df_display = df[["product_id", "product_name", "cost_price", "sales_price"]].rename(
    columns={
        "product_name": "Product",
        "cost_price": "Cost Price",
        "sales_price": "Sales Price"
    }
)
st.dataframe(df_display, hide_index=True)

# Initialize session state
if "new_df" not in st.session_state:
    st.session_state.new_df = df_display.copy()
if "profit_impact_pct" not in st.session_state:
    st.session_state.profit_impact_pct = None

# Column selector - display only price columns
price_columns = [col for col in df_display.columns if "price" in col.lower()]

cleaned_choice = st.selectbox("Choose Price to modify", list(price_columns))
display_column = cleaned_choice
column = 'cost_price' if display_column == 'Cost Price' else 'sales_price'


# Prefill expression with the selected column
default_expr = f"{display_column}"
expr = st.text_input("Enter calculation to apply (e.g. Cost Price +2 or Sales Price / 1.5)", value=default_expr)

# Create a container for outputs
output_container = st.container()

# Buttons in a row
col1, col2, col3 = st.columns(3)
with col1:
    apply_pressed = st.button("Show new price structure")
with col2:
    profit_pressed = st.button("Show profit impact")
with col3:
    update_pressed = st.button("Apply Price Update")

# Apply transformation
if apply_pressed:
    try:
        st.session_state.new_df = df_display.copy()
        st.session_state.new_df[display_column] = st.session_state.new_df[display_column].apply(apply_expr)
        with output_container:
            st.subheader("New Price Structure (Preview)")
            st.dataframe(st.session_state.new_df, hide_index=True)
    except Exception as e:
        with output_container:
            st.error(f"Error: {e}")

# Apply new prices
elif update_pressed:
    try:
        temp_df = df_display.copy()
        temp_df[display_column] = temp_df[display_column].apply(apply_expr)
        temp_df = temp_df.rename(columns={
            "Cost Price": "cost_price",
            "Sales Price": "sales_price"
        })

        with conn.cursor() as cursor:
            for row in temp_df.itertuples(index=False):
                sql = f"""
                    UPDATE {TABLE_NAME}
                    SET {column} = {row._asdict()[column]}
                    WHERE product_id = {row.product_id}
                """
                cursor.execute(sql)
        with output_container:
            st.success("Table updated successfully")

        #Refresh the table at the top to show new prices 
        st.session_state.prices_updated = True
        st.rerun() 

    except Exception as e:
        with output_container:
            st.error(f"Error updating table: {e}")

# Show profit impact
elif profit_pressed:
    try:
        # Original profit
        old_profit = (
            df_display["Sales Price"].astype(float)
            - df_display["Cost Price"].astype(float)
        ).sum()

        # New profit based on current expr
        temp_df = df_display.copy()
        temp_df[display_column] = temp_df[display_column].apply(apply_expr)
        new_profit = (
            temp_df["Sales Price"].astype(float)
            - temp_df["Cost Price"].astype(float)
        ).sum()

        # Profit impact as %
        profit_impact_pct = ((new_profit - old_profit) / old_profit) * 100

        with output_container:
            st.subheader("Profit Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Old Profit", value=f"{old_profit:.2f}%")
            col2.metric(label="New Profit", value=f"{new_profit:.2f}%")
            col3.metric(label="Profit Impact (%)", value=f"{profit_impact_pct:.2f}%")

    except Exception as e:
        with output_container:
            st.error(f"Error calculating profit impact: {e}")


