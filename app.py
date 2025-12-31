import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import date 

SUB_CATEGORY = {
    "Die Bond": ["IC Bonding", "Pd/VC Bonding"],
    "Machine Only": ["Wire Bonding", "Wire Checking", "Lens Bonding", "Lens CCD  Position Check"],
    "Dispensing": ["Module Dispensing", "UV Curing dispense", "U Lens","Bake/Oven","Dispensing Reverse"],
    "Function": ["Incoming Check", "Upload Program", "Divide Board", "Labeling", "BERT Test"],
    "Packing": ["Check Connector", "Packing"] 
}

CUSTOM_ORDER = [
    "Incoming Check",
    "Module Dispensing",
    "UV Curing dispense",
    "IC Bonding",
    "Pd/VC Bonding",
    "Wire Bonding",
    "Wire Checking",
    "Lens Bonding",
    "Lens CCD  Position Check",
    "U Lens",
    "Bake/Oven",
    "Upload Program",
    "Divide Board",
    "Labeling",
    "BERT Test",
    "Dispensing Reverse",
    "Check Connector",
    "Packing"
]

CUSTOM_ORDER_TIME = [
    '10:00', '12:00', '15:00', '17:00',
    '20:00', '22:00', '0:00', '3:00', '5:00','8:00'
]

def bar_plot (df, x_axis, y_axis, color, title, CUSTOM_ORDER=None):
    if CUSTOM_ORDER and color in df.columns:
        df[color] = pd.Categorical(df[color], categories=CUSTOM_ORDER, ordered=True)
        df = df.sort_values(by=color)
        

    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        color=color,
        barmode="group",
        text_auto=True,
        title=title,
        custom_data=[df[color]],
    )
    
    fig.update_traces(
    hovertemplate=(
            "<b>Station:</b> %{customdata[0]}"
            "<br><b>Time:</b> %{x}"
            "<br><b>OK:</b> %{y}"
            "<extra></extra>"
        ),
    marker_line_width=1.2,
    marker_line_color="white",
    )



    fig.update_layout(
        legend=dict(
            title="Station",
            font=dict(size=25),
            itemsizing="trace",  
            itemwidth=60,
        ),
        title_font=dict(size=18),
        xaxis_title_font=dict(size=16),
        yaxis_title_font=dict(size=16),
        
     
    )


    return fig

def scatter_plot(df, x_axis, y_axis, color, symbol, title):
    fig = px.scatter(
    df,
    x=x_axis,
    y=y_axis,
    color=color,
    symbol=symbol,
    size=y_axis,
    text=y_axis,
    title=title,

    symbol_map={
            "RX": "circle",
            "TX": "diamond"
        },
        category_orders={
            symbol: ["RX", "TX"]
        }
    
    )

    for trace in fig.data:
        trace_symbol = trace.name.split(",")[-1].strip() 
        trace.customdata = [[trace_symbol]] * len(trace.x)  

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=14, color="#333", family="Arial Black"),
        marker=dict(line=dict(width=2, color="white"), opacity=0.9),
        hovertemplate="<b>Station:</b> %{x}<br><b>Type:</b> %{customdata[0]}<br><b>NG Count:</b> %{y}<extra></extra>"
    )

    fig.update_yaxes(range=[0, df[y_axis].max() * 1.3])

    

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title=dict(x=0.5),
        font=dict(family="Arial", size=13),
        legend_title=f"{color} / {symbol}"
    )


    return fig

st.set_page_config(
    page_title="Real-time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def make_card(title, value, subtitle, color="#27AE60"):
    st.markdown(f"""
    <div style="
        background-color: #ffffff;
        border-left: 8px solid {color};
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    ">
        <h4 style="color:#2C3E50;">{title}</h4>
        <h2 style="color:{color}; margin:0;">{value}</h2>
        <p style="color:gray;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)



# ------------------------------
# Auto-refresh every 30 seconds
st_autorefresh(interval=30000, limit=None, key="refresh")

# ------------------------------
# Google Sheets CSV URL (must be CSV export)
# region Reading add google sheet verificarion
SHEET_ID = "1oOJu04mdSgeGALFv9orv9LnvTf_HRBOlnLJVv4I07xc"
GID = "190517020"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)  # cache for 60 seconds
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

df = load_data()
df["DateTime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str), errors="coerce")

# endregion

st.markdown("""
    <div style="
        background-color:#0078FF;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 30px;
        font-weight: bold;
        letter-spacing: 1px;
    ">
        🏭 COB Line Real-Time Production Dashboard
    </div>
""", unsafe_allow_html=True
)

# ------------------------------
# Filter by TYPE
# region filterring data
st.markdown("---")  # horizontal line separator

df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
unique_dates = sorted({d.isoformat() for d in df['Date'].dropna()})  # set -> unique
categories_dates = ["All"] + unique_dates
today_iso = pd.Timestamp.today().date().isoformat()

default_index = 0
try:
    default_index = categories_dates.index(today_iso)
except ValueError:
    # today not present, default stays 0
    default_index = 0


df['Time'] = pd.Categorical(df['Time'], categories=CUSTOM_ORDER_TIME, ordered=True)
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Batch'] = df['Batch'].astype(str).str.strip()
df['Batch'] = df['Batch'].str.strip().str.lower().str.replace(' ', '')
batchs_available = ["All"] + df['Batch'].unique().tolist()

# # --- Debugging output (remove when working)
# st.write("DEBUG: today_iso =", today_iso)
# st.write("DEBUG: first 10 categories_dates =", categories_dates)
# st.write("DEBUG: default_index computed =", default_index)
filtered_df = df.copy()

col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 0.5])

with col1:
    st.markdown(
        "<h4 style='color:#2C3E50; margin-top:24px;'>🔍 Select Category:</h4>",
        unsafe_allow_html=True
    )

with col2:
    categories_1 = ["All"] + sorted(df['TYPE'].dropna().unique().tolist())
    selected_category_1 = st.selectbox(
        "Type Module",
        options=categories_1,
        index=0,
        key="category_filter_1"
    )

    if selected_category_1 != "All":
        filtered_df = filtered_df[filtered_df['TYPE'] == selected_category_1]

with col3:
    selected_category_2 = st.date_input(
        "Start Date",
        value=date.today(),
        key="category_filter_2"
    )

with col4:
    selected_category_3 = st.date_input(
        "End Date",
        value=date.today(),
        key="category_filter_3"
    )

    # ✅ Apply date filtering (no "All" string check)
    start_date = pd.to_datetime(selected_category_2)
    end_date = pd.to_datetime(selected_category_3)
    filtered_df = filtered_df[
        (filtered_df['Date'] >= start_date) &
        (filtered_df['Date'] <= end_date)
    ]

with col5:
    batchs_available_data = ["All"] + filtered_df['Batch'].dropna().unique().tolist()
    selected_category_4 = st.selectbox(
        "Batch",
        options=batchs_available_data,
        index=0,
        key="category_filter_4"
    )

    if selected_category_4 != "All":
        filtered_df = filtered_df[filtered_df['Batch'] == selected_category_4]

with col6:
    st.markdown(
        f"""
        <div style='
            background-color:#eef6ff;
            border-left:5px solid #0078ff;
            padding:8px 14px;
            border-radius:8px;
            font-size:15px;
            color:#2C3E50;
            margin-top:28px;
        '>
            📦 Showing: <b>{selected_category_1}</b><br>
            📅 From <b>{selected_category_2}</b> to <b>{selected_category_3}</b>
        </div>
        """,
        unsafe_allow_html=True
    )



# endregion

# ------------------------------
# Create pivot table
pivot_1 = filtered_df.pivot_table(
    index='Time',
    columns='Station',
    values='OK',
    aggfunc='sum',
    fill_value=0, 
)
pivot_1 = pivot_1[[col for col in CUSTOM_ORDER if col in pivot_1.columns]]
pivot_1['Total per Time'] = pivot_1.sum(axis=1)
pivot_1.loc['Grand Total'] = pivot_1.sum(numeric_only=True)
pivot_1 = pivot_1.applymap(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)



# ------------------------------
# Display DataFrame
st.subheader("📋 Station Record Summary")
st.dataframe(
    pivot_1,
    use_container_width=True,
    hide_index=False
)

st.markdown("---")

# ------------------------------
# Plotly bar chart
st.subheader("🧰 Production Station Pcs")
options = ["Die Bond", "Machine Only", "Dispensing", "Function","Packing", "All"]

plot_df = filtered_df.copy()
if hasattr(st, "pills"):
    selection = st.pills("Station Categories", options, selection_mode="multi")
else:
    selection = st.multiselect("Station Categories", options, default=["All"])
if "All" not in selection:
    selected_subcats = []
    for category in selection:
        selected_subcats.extend(SUB_CATEGORY.get(category, []))
    plot_df = plot_df[plot_df['Station'].isin(selected_subcats)]



# st.markdown(f"Your selected options: {selection}.")
st.plotly_chart(bar_plot(plot_df,"DateTime","OK","Station","Output Production Daily",  CUSTOM_ORDER))

st.markdown("---")

# ------------------------------
# Top NG Line
st.subheader(" 📈 Production Performance Matrix")
col1, col2 = st.columns(2)
# ==========================
#  SELECT BATCH (LEFT)
# ==========================
with col1:
    # Header with padding
    st.markdown(
        """
        <h3 style="
            padding-left: 20px;
            padding-top: 20px;
            padding-bottom: 45px;
            color: #2C3E50;
            font-weight: 600;
        ">
            🧩 Select Batch
        </h3>
        """,
        unsafe_allow_html=True
    )

    # Batch selector
    selected_batch = st.selectbox(
        "",
        index = len(batchs_available) - 1,
        options=batchs_available,
        key="batch_select",
        label_visibility="collapsed"
    )

    # Top 5 NG Chart
    df_NG = df.copy()

    if selected_batch != "All":
        df_NG = df_NG[df_NG["Batch"] == selected_batch]

    group_1 = df_NG.groupby(['TYPE', 'Station'], as_index=False)['NG'].sum()
    top5_NG = group_1.nlargest(5, 'NG')
    st.plotly_chart(
        scatter_plot(top5_NG, "Station", "NG", "Station","TYPE", "🚨 Top 5 NG Line"),
        use_container_width=True
    )
   

# ==========================
# SELECT WEEK (RIGHT)
# ==========================
with col2:
    # Ensure datetime conversion
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['ISO_Year'] = df['Date'].dt.isocalendar().year
    df['ISO_Week'] = df['Date'].dt.isocalendar().week

    today = pd.Timestamp.today()
    current_week = today.isocalendar().week
    current_year = today.year

    # Week header
    st.markdown(
        """
        <h3 style="
            padding-left: 20px;
            padding-top: 20px;
            color: #2C3E50;
            font-weight: 600;
        ">
            📆 Select Week
        </h3>
        """,
        unsafe_allow_html=True
    )

    # Week selector
    df['ISO_Week'] = df['ISO_Week'].astype('Int64')
    weeks_available = sorted(df['ISO_Week'].dropna().astype(int).unique().tolist())

    if current_week in weeks_available:
        default_index = weeks_available.index(current_week)
    else:
        default_index = len(weeks_available) - 1  # fallback to last week

    selected_week = st.selectbox(
        "",
        options=weeks_available,
        index=default_index,
        key="week_select"
    )

    # Filter & plot
    filteredout_df = df[
        (df['ISO_Week'] == selected_week) &
        (df['ISO_Year'] == current_year)
    ].copy()

    station_df = filteredout_df[filteredout_df['Station'] == 'Packing']
    group_out = station_df.groupby('Date', as_index=False)['OK'].sum()

    fig = px.bar(
        group_out,
        x="OK",
        y="Date",
        orientation='h',
        text="OK",
        title=f"📦 Packing Output — Week {selected_week}",
        color="OK",
         color_continuous_scale=[
        (0, "black"),  
        (0.25, "red"),       
        (0.75, "yellow"), 
        (1, "green")     
    ],
    range_color=[0, 1500]
        
    )
    fig.update_yaxes(
    tickformat="%Y-%m-%d"
    )

    fig.add_vline(
        x=1500,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text="Target minimum = 1500",
        annotation_position="top right"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Total OK Units",
        yaxis_title="Date",
        showlegend=False,
        bargap=0.3
    )

    st.plotly_chart(fig, use_container_width=True)


# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     make_card("📦 Output", "12,480", "Units Today", "#27AE60")
# with col2:
#     make_card("🎯 Target", "1200", "Date", "#D1CE1E")
# with col3:
#     make_card("⚙️ Material Processing", "98.5%", "This Shift", "#2980B9")
# with col4:
#     make_card("❌ NG Rate", "1.2%", "Target < 2%", "#E74C3C")

# st.markdown("---")

st.subheader("🔄 Batch Analyze Flow ")

col1, col2 = st.columns([1,2])

with col1:

    # Batch selector
    batchs_available_process = ["All"] + df['Batch'].unique().tolist()

    col11, col12 = st.columns(2)

    with col11:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        selected_batch_process = st.selectbox(
            "",
            index = len(batchs_available_process) - 1,
            options=batchs_available_process,
            key="batch_select_process",
            label_visibility="collapsed"
        )

    with col12:
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        model_type = st.radio(
            "",
            options=["TX","RX"],
            horizontal=True,
            label_visibility="collapsed"
        )
    

    
    
    batch_df = df.copy()

    if selected_batch_process != "All":
        batch_df = batch_df[batch_df["Batch"] == selected_batch_process]

    else:
        batch_df = batch_df

    batch_df = batch_df[batch_df['TYPE'] == model_type]
    
    pie_df = batch_df.melt(
    id_vars=["Batch"],
    value_vars=["OK", "NG"],
    var_name="Category",
    value_name="Value"
    )

    pie_df = pie_df.groupby("Category", as_index=False)["Value"].sum()
    pie_df["Category"] = pie_df["Category"].str.strip().str.upper()


    fig = px.pie(
    pie_df,
    names="Category",
    values="Value",
    color="Category",
    color_discrete_map={"OK": "#2E8B57", "NG": "#D9534F"},
    hole=0.6
)

    # --- Add selected batch name in the center ---
    fig.add_annotation(
        text=selected_batch_process,
        x=0.5, y=0.5,
        font=dict(size=30, color="#333", family="Arial Black"),
        showarrow=False
    )

    # --- Display in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)


with col2:
    filtered_2_df = batch_df.copy()
    filtered_2_df[["OK", "NG"]] = filtered_2_df[["OK", "NG"]].fillna(0)

    df_group_1 = (
        filtered_2_df
        .groupby("Station")[["OK", "NG"]]
        .sum()
        .reset_index() 
    )
    
    df_melted = df_group_1.melt(id_vars="Station", value_vars=["OK", "NG"], var_name="Status", value_name="Count")

# Plot stacked bar chart
    fig = px.bar(
    df_melted,
    x="Station",
    y="Count",
    color="Status",
    text="Count",
    title="📊 Production Result by Station",
    color_discrete_map={
        "OK": "#2E8B57",   # sea green
        "NG": "#D9534F"    # soft red
    },
    category_orders={"Station": CUSTOM_ORDER}
    )
    fig.update_yaxes(range=[0, df_melted["Count"].max() * 1.4])

# Make bars stacked
    fig.update_layout(barmode="stack")

# Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)




