
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Pakistan E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. PROFESSIONAL DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #14213D;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #14213D !important;
}

[data-testid="stSidebar"] input {
    color: #14213D !important;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #14213D;
    margin-bottom: 0px;
}

.sub-title {
    font-size: 15px;
    color: #64748B;
    margin-bottom: 25px;
}

.section-title {
    color: #14213D;
    font-size: 22px;
    font-weight: 700;
    margin-top: 12px;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 20px 18px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

[data-testid="stMetricLabel"] {
    color: #64748B;
    font-size: 14px;
}

[data-testid="stMetricValue"] {
    color: #14213D;
    font-size: 25px;
    font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 10px;
}

.footer {
    text-align: center;
    color: #64748B;
    padding: 20px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    data = pd.read_csv("pakistan_ecommerce_cleaned.csv.gz", compression="gzip")


    data["created_at"] = pd.to_datetime(
        data["created_at"], errors="coerce"
    )

    data["price"] = pd.to_numeric(
        data["price"], errors="coerce"
    )

    data["qty_ordered"] = pd.to_numeric(
        data["qty_ordered"], errors="coerce"
    )

    data["discount_amount"] = pd.to_numeric(
        data["discount_amount"], errors="coerce"
    )

    data["item_total_value"] = (
        data["price"] * data["qty_ordered"]
    )

    return data


df = load_data()


# ==========================================
# 4. HELPER FUNCTION
# ==========================================

def format_value(value):

    if value >= 1_000_000_000:
        return f"Rs. {value / 1_000_000_000:.2f}B"

    elif value >= 1_000_000:
        return f"Rs. {value / 1_000_000:.2f}M"

    elif value >= 1_000:
        return f"Rs. {value / 1_000:.2f}K"

    return f"Rs. {value:,.0f}"


# ==========================================
# 5. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("📊 E-Commerce Analytics")
st.sidebar.caption("Business Intelligence Dashboard")

st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

valid_dates = df["created_at"].dropna()

if valid_dates.empty:
    st.error("No valid dates found in dataset.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = sorted(
    df["category_name_1"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "Product Categories",
    categories,
    default=categories
)

payments = sorted(
    df["payment_method"].dropna().unique()
)

selected_payments = st.sidebar.multiselect(
    "Payment Methods",
    payments,
    default=payments
)

st.sidebar.divider()

if st.sidebar.button("Reset All Filters", use_container_width=True):
    st.rerun()


# ==========================================
# 6. FILTER DATA
# ==========================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["created_at"].dt.date >= start_date) &
        (filtered_df["created_at"].dt.date <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["category_name_1"].isin(selected_categories)
]

filtered_df = filtered_df[
    filtered_df["payment_method"].isin(selected_payments)
]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()


# ==========================================
# 7. HEADER
# ==========================================

st.markdown(
    '<p class="main-title">Pakistan E-Commerce Analytics</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Business Intelligence | Sales Performance | Customer Insights</p>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 8. BUSINESS KPIs
# ==========================================

total_orders = filtered_df["increment_id"].nunique()

total_customers = filtered_df["Customer ID"].nunique()

total_records = len(filtered_df)

total_quantity = filtered_df["qty_ordered"].sum()

total_value = filtered_df["item_total_value"].sum()

average_order_value = (
    total_value / total_orders if total_orders > 0 else 0
)

st.markdown(
    '<p class="section-title">Business Overview</p>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Customers", f"{total_customers:,}")
col3.metric("Total Records", f"{total_records:,}")

col4, col5, col6 = st.columns(3)

col4.metric("Products Quantity", f"{total_quantity:,.0f}")
col5.metric("Recorded Product Value", format_value(total_value))
col6.metric("Average Value / Order", format_value(average_order_value))

st.caption(
    "Note: Recorded Product Value = Price × Quantity. "
    "It is not verified collected revenue or profit."
)

st.divider()


# ==========================================
# 9. PREPARE CHART DATA
# ==========================================

monthly_data = filtered_df.copy()

monthly_data["Month"] = (
    monthly_data["created_at"]
    .dt.to_period("M")
    .astype(str)
)

monthly_data = (
    monthly_data.groupby("Month")["item_total_value"]
    .sum()
    .reset_index()
)

category_data = (
    filtered_df.groupby("category_name_1")["item_total_value"]
    .sum()
    .reset_index()
    .sort_values("item_total_value", ascending=True)
)

product_data = (
    filtered_df[
        ~filtered_df["sku"].isin(["Unknown", r"\N"])
    ]
    .groupby("sku")
    .agg(
        Total_Quantity=("qty_ordered", "sum"),
        Recorded_Value=("item_total_value", "sum")
    )
    .reset_index()
    .sort_values("Total_Quantity", ascending=False)
    .head(10)
)

payment_data = (
    filtered_df.groupby("payment_method")["increment_id"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
    .head(10)
)

status_data = (
    filtered_df.groupby("status")["increment_id"]
    .nunique()
    .reset_index(name="Unique Orders")
    .sort_values("Unique Orders", ascending=False)
)


# ==========================================
# 10. DASHBOARD TABS
# ==========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📦 Products",
    "💳 Orders & Payments",
    "📋 Data Explorer"
])


# ==========================================
# TAB 1: OVERVIEW
# ==========================================

with tab1:

    st.markdown(
        '<p class="section-title">Monthly Performance Trend</p>',
        unsafe_allow_html=True
    )

    fig_monthly = px.area(
        monthly_data,
        x="Month",
        y="item_total_value",
        markers=True,
        template="plotly_white",
        color_discrete_sequence=["#2563EB"],
        labels={
            "Month": "Month",
            "item_total_value": "Recorded Product Value (PKR)"
        }
    )

    fig_monthly.update_traces(
        line=dict(width=3),
        fillcolor="rgba(37, 99, 235, 0.12)"
    )

    fig_monthly.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=25, b=20),
        hovermode="x unified",
        showlegend=False
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

    st.markdown(
        '<p class="section-title">Category Performance</p>',
        unsafe_allow_html=True
    )

    fig_category = px.bar(
        category_data,
        x="item_total_value",
        y="category_name_1",
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#2563EB"],
        labels={
            "category_name_1": "Category",
            "item_total_value": "Recorded Product Value (PKR)"
        }
    )

    fig_category.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=25, b=20),
        showlegend=False
    )

    st.plotly_chart(fig_category, use_container_width=True)



    # ==========================================
    # EXECUTIVE BUSINESS INSIGHTS
    # ==========================================

    st.divider()

    st.markdown(
        '<p class="section-title">Executive Business Insights</p>',
        unsafe_allow_html=True
    )

    # Highest performing category
    best_category = category_data.sort_values(
        "item_total_value", ascending=False
    ).iloc[0]

    # Highest recorded value month
    peak_month = monthly_data.loc[
        monthly_data["item_total_value"].idxmax()
    ]

    # Most used payment method
    popular_payment = payment_data.iloc[0]

    # Most common order status
    common_status = status_data.sort_values(
        "Unique Orders", ascending=False
    ).iloc[0]

    insight1, insight2 = st.columns(2)

    with insight1:
        st.info(
            f"**Top Category**\n\n"
            f"{best_category['category_name_1']} has the highest "
            f"recorded product value of "
            f"{format_value(best_category['item_total_value'])}."
        )

        st.info(
            f"**Peak Month**\n\n"
            f"{peak_month['Month']} recorded the highest "
            f"product value of "
            f"{format_value(peak_month['item_total_value'])}."
        )

    with insight2:
        st.info(
            f"**Popular Payment Method**\n\n"
            f"{popular_payment['payment_method']} has the highest "
            f"number of unique orders "
            f"({popular_payment['Total Orders']:,})."
        )

        st.info(
            f"**Most Common Order Status**\n\n"
            f"{common_status['status']} is the most frequent "
            f"status, with {common_status['Unique Orders']:,} "
            f"unique orders."
        )

    st.caption(
        "Insights are dynamically calculated from the currently selected filters. "
        "Product value represents price × quantity, not verified revenue."
    )



# ==========================================
# TAB 2: PRODUCTS
# ==========================================

with tab2:

    st.markdown(
        '<p class="section-title">Top 10 Products by Quantity</p>',
        unsafe_allow_html=True
    )

    product_chart = product_data.sort_values("Total_Quantity")

    fig_products = px.bar(
        product_chart,
        x="Total_Quantity",
        y="sku",
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#0F766E"],
        labels={
            "sku": "Product SKU",
            "Total_Quantity": "Quantity Ordered"
        }
    )

    fig_products.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=25, b=20)
    )

    st.plotly_chart(fig_products, use_container_width=True)

    st.markdown(
        '<p class="section-title">Category Value Distribution</p>',
        unsafe_allow_html=True
    )

    fig_pie = px.pie(
        category_data,
        names="category_name_1",
        values="item_total_value",
        hole=0.55,
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_pie.update_layout(height=450)

    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### Product Performance Details")

    st.dataframe(
        product_data,
        use_container_width=True,
        hide_index=True
    )



# ==========================================
# TAB 3: ORDERS & PAYMENTS
# ==========================================

with tab3:

    st.markdown("### Order Status Analysis")

    # Focus on major business statuses
    important_statuses = [
        "complete",
        "canceled",
        "received",
        "order_refunded",
        "refund"
    ]

    important_status_data = status_data[
        status_data["status"].isin(important_statuses)
    ].sort_values("Unique Orders", ascending=True)

    left, right = st.columns(2)

    with left:

        fig_status = px.bar(
            important_status_data,
            x="Unique Orders",
            y="status",
            orientation="h",
            text="Unique Orders",
            title="Major Order Statuses",
            template="plotly_white",
            color_discrete_sequence=["#2563EB"]
        )

        fig_status.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig_status.update_layout(
            height=430,
            showlegend=False,
            margin=dict(l=15, r=60, t=55, b=20)
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )

    with right:

        fig_payment = px.bar(
            payment_data.sort_values("Total Orders"),
            x="Total Orders",
            y="payment_method",
            orientation="h",
            text="Total Orders",
            title="Top 10 Payment Methods",
            template="plotly_white",
            color_discrete_sequence=["#0F766E"]
        )

        fig_payment.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig_payment.update_layout(
            height=430,
            showlegend=False,
            margin=dict(l=15, r=60, t=55, b=20)
        )

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )

    st.markdown("### Complete Order Status Details")

    st.dataframe(
        status_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Payment Method Details")

    st.dataframe(
        payment_data,
        use_container_width=True,
        hide_index=True
    )



# ==========================================
# TAB 4: DATA EXPLORER
# ==========================================

with tab4:

    st.markdown("### Explore E-Commerce Records")

    search_text = st.text_input(
        "Search by Product SKU",
        placeholder="Enter product SKU..."
    )

    table_df = filtered_df.copy()

    if search_text:

        table_df = table_df[
            table_df["sku"].astype(str).str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    st.write(f"Showing {len(table_df):,} records")

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = table_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Filtered Dataset",
        data=csv_data,
        file_name="pakistan_ecommerce_filtered.csv",
        mime="text/csv"
    )


# ==========================================
# 11. FOOTER
# ==========================================

st.divider()

st.markdown("""
<div class="footer">
    Pakistan E-Commerce Analytics Dashboard<br>
    Developed using Python | Pandas | Plotly | Streamlit
</div>
""", unsafe_allow_html=True)
