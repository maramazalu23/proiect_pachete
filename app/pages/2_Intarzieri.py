import streamlit as st
import plotly.express as px

from utils.load_data import load_final_dataset, get_yearly_delays

st.set_page_config(page_title="Întârzieri ATFM", page_icon="⏱️", layout="wide")

st.title("⏱️ Analiza întârzierilor ATFM")
st.markdown("Această pagină evidențiază evoluția întârzierilor ATFM și relația acestora cu traficul aerian.")

# ==============================
# LOAD DATA
# ==============================
df = load_final_dataset()
yearly_delays = get_yearly_delays()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filtre întârzieri")

countries = sorted(df["STATE_NAME"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Selectează țara/țările",
    options=countries,
    default=[]
)

years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Selectează anul / anii",
    options=years,
    default=years
)

filtered_df = df[df["year"].isin(selected_years)].copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df["STATE_NAME"].isin(selected_countries)]

# ==============================
# KPIs
# ==============================
total_delay = round(filtered_df["total_delay"].sum(), 2)
avg_daily_delay = round(filtered_df["total_delay"].mean(), 2)
num_airports = filtered_df["APT_ICAO"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Întârziere totală", f"{total_delay:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

with col2:
    st.metric("Întârziere medie zilnică", f"{avg_daily_delay:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("Număr aeroporturi", num_airports)

st.markdown("---")

# ==============================
# YEARLY DELAY CHART
# ==============================
delay_by_year = (
    filtered_df.groupby("year", as_index=False)
    .agg(total_delay=("total_delay", "sum"))
    .sort_values("year")
)

fig_year = px.line(
    delay_by_year,
    x="year",
    y="total_delay",
    markers=True,
    title="Evoluția întârzierilor totale pe ani",
    labels={
        "year": "An",
        "total_delay": "Întârziere totală"
    }
)

st.plotly_chart(fig_year, width="stretch")

st.markdown("""
**Interpretare:**  
Evoluția întârzierilor totale permite identificarea anilor în care presiunea operațională a fost mai ridicată.  
Compararea acestora cu nivelul traficului poate evidenția eventuale probleme de capacitate sau congestie.
""")

st.markdown("---")

# ==============================
# MONTHLY DELAY CHART
# ==============================
monthly_delay = (
    filtered_df.groupby(["year", "month"], as_index=False)
    .agg(total_delay=("total_delay", "sum"))
    .sort_values(["year", "month"])
)

fig_month = px.line(
    monthly_delay,
    x="month",
    y="total_delay",
    color="year",
    markers=True,
    title="Întârzierile ATFM lunare, pe ani",
    labels={
        "month": "Luna",
        "total_delay": "Întârziere totală",
        "year": "An"
    }
)

st.plotly_chart(fig_month, width="stretch")

st.markdown("""
**Interpretare:**  
Distribuția lunară a întârzierilor poate evidenția existența unor vârfuri sezoniere,  
în special în perioadele cu trafic aerian intens.
""")

st.markdown("---")

# ==============================
# TOP AIRPORTS BY DELAY
# ==============================
airport_delay = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(total_delay=("total_delay", "sum"))
    .sort_values("total_delay", ascending=False)
)

top_n = st.slider("Selectează numărul de aeroporturi afișate", 5, 20, 10)

top_airports = airport_delay.head(top_n)

fig_airports = px.bar(
    top_airports,
    x="APT_ICAO",
    y="total_delay",
    hover_data=["APT_NAME", "STATE_NAME"],
    title=f"Top {top_n} aeroporturi după întârzierea totală",
    labels={
        "APT_ICAO": "Aeroport",
        "total_delay": "Întârziere totală"
    }
)

st.plotly_chart(fig_airports, width="stretch")

st.markdown("""
**Interpretare:**  
Aeroporturile aflate în partea superioară a clasamentului sunt cele mai afectate de întârzieri operaționale.  
Acestea pot reflecta zone cu cerere ridicată, congestie sau vulnerabilități operaționale.
""")

st.markdown("---")

# ==============================
# TRAFFIC VS DELAY
# ==============================
traffic_delay = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME"], as_index=False)
    .agg(
        total_traffic=("traffic", "sum"),
        total_delay=("total_delay", "sum")
    )
)

fig_scatter = px.scatter(
    traffic_delay,
    x="total_traffic",
    y="total_delay",
    hover_data=["APT_ICAO", "APT_NAME"],
    title="Relația dintre traficul total și întârzierea totală",
    labels={
        "total_traffic": "Trafic total",
        "total_delay": "Întârziere totală"
    }
)

st.plotly_chart(fig_scatter, width="stretch")

st.markdown("""
**Interpretare:**  
Diagrama de dispersie evidențiază relația dintre volumul traficului și nivelul întârzierilor.  
O asociere pozitivă poate sugera că aeroporturile cu trafic intens sunt mai expuse la întârzieri.
""")

st.markdown("---")

# ==============================
# TABLE
# ==============================
st.subheader("Tabel sinteză întârzieri pe aeroport")

table_delay = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(
        total_delay=("total_delay", "sum"),
        avg_daily_delay=("total_delay", "mean")
    )
    .sort_values("total_delay", ascending=False)
)

st.dataframe(table_delay, width="stretch")