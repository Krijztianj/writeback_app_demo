import streamlit as st
from .utils import get_connection, read_table, execute_statements, TABLE_NAME
from .functions import apply_expr, calculate_profit_impact, generate_update_statements

if "prices_updated" not in st.session_state:
    st.session_state.prices_updated = False

st.title("Update Product Pricing")

if st.session_state.prices_updated:
    st.success("Prices have been successfully updated!")
    st.session_state.prices_updated = False

conn = get_connection()
df = read_table(conn)

df_display = df[["product_id", "product_name", "cost_price", "sales_price"]].rename(
    columns={
        "product_name": "Product",
        "cost_price": "Cost Price",
        "sales_price": "Sales Price"
    }
)
st.subheader("Current Price Overview")
st.dataframe(df_display, hide_index=True)

if "new_df" not in st.session_state:
    st.session_state.new_df = df_display.copy()
if "profit_impact_pct" not in st.session_state:
    st.session_state.profit_impact_pct = None

price_columns = [col for col in df_display.columns if "price" in col.lower()]
display_column = st.selectbox("Choose Price to modify", list(price_columns))
column = 'cost_price' if display_column == 'Cost Price' else 'sales_price'

default_expr = f"{display_column}"
expr = st.text_input(
    "Enter calculation to apply (e.g. Cost Price + 2 or Sales Price / 1.5)",
    value=default_expr
)

output_container = st.container()
col1, col2, col3 = st.columns(3)
apply_pressed = col1.button("Show new price structure")
profit_pressed = col2.button("Show profit impact")
update_pressed = col3.button("Apply Price Update")

if apply_pressed:
    try:
        st.session_state.new_df = df_display.copy()
        st.session_state.new_df[display_column] = st.session_state.new_df[display_column].apply(
            lambda val: apply_expr(val, expr, display_column)
        )
        with output_container:
            st.subheader("New Price Structure (Preview)")
            st.dataframe(st.session_state.new_df, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")

elif update_pressed:
    try:
        temp_df = df_display.copy()
        temp_df[display_column] = temp_df[display_column].apply(
            lambda val: apply_expr(val, expr, display_column)
        )
        temp_df = temp_df.rename(columns={"Cost Price": "cost_price", "Sales Price": "sales_price"})
        statements = generate_update_statements(temp_df, column, TABLE_NAME)
        execute_statements(conn, statements)
        st.success("Table updated successfully")
        st.session_state.prices_updated = True
        st.rerun()
    except Exception as e:
        st.error(f"Error updating table: {e}")

elif profit_pressed:
    try:
        profit_impact_pct = calculate_profit_impact(df_display, expr, display_column)
        with output_container:
            st.subheader("Profit Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Old Profit", f"{(df_display['Sales Price'] - df_display['Cost Price']).sum():.2f}")
            col2.metric("New Profit", f"{(st.session_state.new_df['Sales Price'] - st.session_state.new_df['Cost Price']).sum():.2f}")
            col3.metric("Profit Impact (%)", f"{profit_impact_pct:.2f}%")
    except Exception as e:
        st.error(f"Error calculating profit impact: {e}")
