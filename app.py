# ================================
# Streamlit Production Dashboard
# ================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# -------------------------
# Safe autorefresh import
# -------------------------
try:
    from streamlit_autorefresh import st_autorefresh
    AUTO_REFRESH_AVAILABLE = True
except ImportError:
    AUTO_REFRESH_AVAILABLE = False

# -------------------------
# Page Config (MUST BE FIRST)
# -------------------------
st.set_page_config(
    page_title="COB Production Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Constants
# -------------------------
SUB_CATEGORY = {
    "Die Bond": ["IC Bonding", "Pd/VC Bonding"],
    "Machine Only": ["Wire Bonding", "Wire Checking", "Lens Bonding", "Lens CCD  Position Check"],
    "Dispensing": ["Module Dispensing", "UV Curing dispense", "U Lens", "Bake/Oven", "Dispensing Reverse"],
    "Function": ["Incoming Check", "Upload Program", "Divide Board", "Labeling", "BERT Test"],
    "Packing": ["Check Connector", "Packing"]
}

CUSTOM_ORDER = [
    "Incoming Check", "Module Dispensing", "UV Curing dispense",
    "IC Bonding", "Pd/VC Bonding", "Wire Bonding", "Wire Checking",
    "Lens Bonding", "Lens CCD  Position Check", "U Lens", "Bake/Oven",
    "Upload Program", "Divide Board", "Labeling", "BERT Test",
    "Dispensing Reverse", "Check Connector", "Packing"
]

CUSTOM_ORDER_TIME = [
    "10:00", "12:00", "15:00", "17:00",
    "20:00", "22:00", "0:00", "3:00", "5:00", "8:00"
]

# -------------------------
# Auto Refresh
# -------------------------
if AUTO_REFRESH_AVAILABLE:
    st_autorefresh(interval=30000, key="refresh")

# -------------------------
# Load Google Sheet
# -------------------------
SHEET_ID = "1oOJu04mdSgeGALFv9orv9LnvTf_HRBOlnLJVv4I07xc"
GID = "190517020"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# -------------------------
# Data Cleaning
# -------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Time"] = df["Time"].astype(str)
df["Batch"] = df["Batch"].astype(str).str.lower().str.replace(" ", "")
df["DateTime"] = pd.to_datetime(
    df["Date"].dt.date.astype(str) + " " + df["Time"],
    errors="coerce"
)

# -------------------------
# Header
# -------------------------
st.markdown("""
<div style="
    background:#0078FF;
    padding:16px;
    border-radius:10px;
    text-align:center;
    color:white;
    font-size:30px;
    font-weight:bold;">
    🏭 COB Line Real-Time Production Dashboard
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Filters
# -------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    type_filter = st.selectbox("Type", ["All"] + sorted(df["TYPE"].dropna().unique()))

with col2:
    start_date = st.date_input("Start Date", date.today())

with col3:
    end_date = st.date_input("End Date", date.today())

with col4:
    batch_filter = st.selectbox("Batch", ["All"] + sorted(df["Batch"].unique()))

filtered_df = df.copy()

if type_filter != "All":
    filtered_df = filtered_df[filtered_df["TYPE"] == type_filter]

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if batch_filter != "All":
    filtered_df = filtered_df[filtered_df["Batch"] == batch_filter]

# -------------------------
# Pivot Table
# -------------------------
st.subheader("📋 Station Record Summary")

pivot = filtered_df.pivot_table(
    index="Time",
    columns="Station",
    values="OK",
    aggfunc="sum",
    fill_value=0
)

pivot = pivot[[c for c in CUSTOM_ORDER if c in pivot.columns]]
pivot["Total"] = pivot.sum(axis=1)

st.dataframe(pivot, use_container_width=True)

st.markdown("---")

# -------------------------
# Bar Chart
# -------------------------
st.subheader("🧰 Production Output")

fig = px.bar(
    filtered_df,
    x="DateTime",
    y="OK",
    color="Station",
    barmode="group",
    category_orders={"Station": CUSTOM_ORDER}
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# -------------------------
# NG Analysis
# -------------------------
st.subheader("📈 Top 5 NG Station")

ng_df = (
    filtered_df
    .groupby(["TYPE", "Station"], as_index=False)["NG"]
    .sum()
    .nlargest(5, "NG")
)

fig_ng = px.scatter(
    ng_df,
    x="Station",
    y="NG",
    color="Station",
    size="NG",
    symbol="TYPE",
    title="🚨 Top 5 NG Line"
)

st.plotly_chart(fig_ng, use_container_width=True)

st.markdown("---")

# -------------------------
# Pie Chart
# -------------------------
st.subheader("🔄 Batch Analyze Flow")

pie_df = filtered_df.melt(
    value_vars=["OK", "NG"],
    var_name="Result",
    value_name="Count"
).groupby("Result", as_index=False)["Count"].sum()

fig_pie = px.pie(
    pie_df,
    names="Result",
    values="Count",
    hole=0.6,
    color="Result",
    color_discrete_map={"OK": "#2E8B57", "NG": "#D9534F"}
)

st.plotly_chart(fig_pie, use_container_width=True)
