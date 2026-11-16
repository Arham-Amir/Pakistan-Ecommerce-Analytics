
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

REQUIRED_COLUMNS = [
    "created_at", "status", "sku", "increment_id", "category_name_1",
    "payment_method", "Customer ID", "qty_ordered", "item_total_value"
]


def _norm(name):
    return str(name).strip().lower().replace(" ", "_")


@st.cache_data(show_spinner="Loading dataset...")
def load_data():

    data = pd.read_csv(
        "pakistan_ecommerce_cleaned.csv.gz",
        compression="gzip",
        low_memory=False
    )

    # Column names ke aage peeche ke spaces hata do (e.g. " MV " -> "MV")
    data.columns = data.columns.astype(str).str.strip()

    # Naam ka chota-bara farq / space ka farq khud theek karo
    existing = {_norm(c): c for c in data.columns}
    rename_map = {}
    for required in REQUIRED_COLUMNS:
        if required not in data.columns and _norm(required) in existing:
            rename_map[existing[_norm(required)]] = required
    data = data.rename(columns=rename_map)

    # Mixed-type (object) columns ko string bana do taake Arrow error na aaye
    for column in data.columns:
        if data[column].dtype == "object":
            data[column] = data[column].astype("string")

    # Date column
    if "created_at" in data.columns:
        data["created_at"] = pd.to_datetime(
            data["created_at"],
            errors="coerce"
        )

    # Numeric columns
    for column in ["qty_ordered", "item_total_value"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    # Memory bachane ke liye low-cardinality columns ko category bana do
    for column in ["status", "category_name_1", "payment_method"]:
        if column in data.columns:
            data[column] = data[column].astype("category")

    return data


df = load_data()

missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing_columns:
    st.error(f"Dataset mein ye columns nahi mile: {missing_columns}")
    st.write("Dataset ke asal columns:", list(df.columns))
    st.stop()


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def format_value(value):

    if pd.isna(value):
        return "Rs. 0"

    if value >= 1_000_000_000:
        return f"Rs. {value / 1_000_000_000:.2f}B"

    elif value >= 1_000_000:
        return f"Rs. {value / 1_000_000:.2f}M"

    elif value >= 1_000:
        return f"Rs. {value / 1_000:.2f}K"

    return f"Rs. {value:,.0f}"


@st.cache_data(show_spinner=False)
def to_csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8")


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

categories = sorted(df["category_name_1"].dropna().astype(str).unique())
payments = sorted(df["payment_method"].dropna().astype(str).unique())

# Default values session_state mein set karo (reset button isi se kaam karega)
if "date_range" not in st.session_state:
    st.session_state["date_range"] = (min_date, max_date)

if "selected_categories" not in st.session_state:
    st.session_state["selected_categories"] = categories

if "selected_payments" not in st.session_state:
    st.session_state["selected_payments"] = payments


def reset_filters():
    st.session_state["date_range"] = (min_date, max_date)
    st.session_state["selected_categories"] = categories
    st.session_state["selected_payments"] = payments


date_range = st.sidebar.date_input(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    key="date_range"
)

selected_categories = st.sidebar.multiselect(
    "Product Categories",
    categories,
    key="selected_categories"
)

selected_payments = st.sidebar.multiselect(
    "Payment Methods",
    payments,
    key="selected_payments"
)

st.sidebar.divider()

st.sidebar.button(
    "Reset All Filters",
    width="stretch",
    on_click=reset_filters
)


# ==========================================
# 6. FILTER DATA
# ==========================================

mask = (
    df["category_name_1"].isin(selected_categories) &
    df["payment_method"].isin(selected_payments)
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date, end_date = date_range

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)

    mask &= (df["created_at"] >= start_ts) & (df["created_at"] < end_ts)

filtered_df = df[mask]

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

monthly_data = (
    filtered_df.dropna(subset=["created_at"])
    .assign(Month=lambda d: d["created_at"].dt.to_period("M").astype(str))
    .groupby("Month")["item_total_value"]
    .sum()
    .reset_index()
    .sort_values("Month")
)

category_data = (
    filtered_df.groupby("category_name_1", observed=True)["item_total_value"]
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
    filtered_df.groupby("payment_method", observed=True)["increment_id"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
    .head(10)
)

status_data = (
    filtered_df.groupby("status", observed=True)["increment_id"]
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

    st.plotly_chart(fig_monthly, width="stretch")

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

    st.plotly_chart(fig_category, width="stretch")

    # ==========================================
    # EXECUTIVE BUSINESS INSIGHTS
    # ==========================================

    st.divider()

    st.markdown(
        '<p class="section-title">Executive Business Insights</p>',
        unsafe_allow_html=True
    )

    if monthly_data.empty or category_data.empty \
            or payment_data.empty or status_data.empty:

        st.info("Not enough data to calculate insights for the selected filters.")

    else:

        best_category = category_data.sort_values(
            "item_total_value", ascending=False
        ).iloc[0]

        peak_month = monthly_data.loc[
            monthly_data["item_total_value"].idxmax()
        ]

        popular_payment = payment_data.iloc[0]

        common_status = status_data.iloc[0]

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

    st.plotly_chart(fig_products, width="stretch")

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

    st.plotly_chart(fig_pie, width="stretch")

    st.markdown("### Product Performance Details")

    st.dataframe(
        product_data,
        width="stretch",
        hide_index=True
    )


# ==========================================
# TAB 3: ORDERS & PAYMENTS
# ==========================================

with tab3:

    st.markdown("### Order Status Analysis")

    important_statuses = [
        "complete",
        "canceled",
        "received",
        "order_refunded",
        "refund"
    ]

    important_status_data = status_data[
        status_data["status"].astype(str).str.lower().isin(important_statuses)
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

        st.plotly_chart(fig_status, width="stretch")

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

        st.plotly_chart(fig_payment, width="stretch")

    st.markdown("### Complete Order Status Details")

    st.dataframe(
        status_data,
        width="stretch",
        hide_index=True
    )

    st.markdown("### Payment Method Details")

    st.dataframe(
        payment_data,
        width="stretch",
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

    table_df = filtered_df

    if search_text:

        table_df = table_df[
            table_df["sku"].astype(str).str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        ]

    MAX_ROWS = 1000

    st.write(
        f"Total {len(table_df):,} records found "
        f"(showing first {min(MAX_ROWS, len(table_df)):,})"
    )

    # Poora table browser mein bhejna bohat heavy hota hai, is liye sirf top rows
    st.dataframe(
        table_df.head(MAX_ROWS),
        width="stretch",
        hide_index=True
    )

    # CSV sirf tab banao jab user chahe (memory bachane ke liye)
    if st.checkbox("Prepare full filtered dataset for download"):

        st.download_button(
            "📥 Download Filtered Dataset",
            data=to_csv_bytes(table_df),
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