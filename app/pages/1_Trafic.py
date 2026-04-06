import streamlit as st
import plotly.express as px

from utils.load_data import load_final_dataset, get_yearly_traffic, get_airport_summary

st.set_page_config(page_title="Trafic aerian", page_icon="📈", layout="wide")

st.title("📈 Analiza traficului aerian")
st.markdown("Această pagină evidențiază evoluția traficului aerian european în perioada 2019–2023.")

# ==============================
# LOAD DATA
# ==============================
df = load_final_dataset()
yearly_traffic = get_yearly_traffic()
airport_summary = get_airport_summary()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filtre trafic")

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

# Filtrare dataset principal
filtered_df = df[df["year"].isin(selected_years)].copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df["STATE_NAME"].isin(selected_countries)]

# ==============================
# KPIs
# ==============================
total_traffic = int(filtered_df["traffic"].sum())
avg_daily_traffic = round(filtered_df["traffic"].mean(), 2)
num_airports = filtered_df["APT_ICAO"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Trafic total", f"{total_traffic:,}".replace(",", "."))

with col2:
    st.metric("Trafic mediu zilnic", f"{avg_daily_traffic:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("Număr aeroporturi", num_airports)

st.markdown("---")

# ==============================
# YEARLY TRAFFIC CHART
# ==============================
traffic_by_year = (
    filtered_df.groupby("year", as_index=False)
    .agg(total_traffic=("traffic", "sum"))
    .sort_values("year")
)

fig_year = px.line(
    traffic_by_year,
    x="year",
    y="total_traffic",
    markers=True,
    title="Evoluția traficului aerian total pe ani",
    labels={
        "year": "An",
        "total_traffic": "Trafic total"
    }
)

st.plotly_chart(fig_year, width="stretch")

st.markdown("""
**Interpretare:**  
Graficul evidențiază dinamica traficului aerian european pe intervalul analizat. 
Diferențele dintre ani permit observarea impactului contextului economic și sanitar asupra volumului de zboruri.
""")

st.markdown("---")

# ==============================
# MONTHLY TRAFFIC CHART
# ==============================
monthly_traffic = (
    filtered_df.groupby(["year", "month"], as_index=False)
    .agg(total_traffic=("traffic", "sum"))
    .sort_values(["year", "month"])
)

fig_month = px.line(
    monthly_traffic,
    x="month",
    y="total_traffic",
    color="year",
    markers=True,
    title="Traficul aerian lunar, pe ani",
    labels={
        "month": "Luna",
        "total_traffic": "Trafic total",
        "year": "An"
    }
)

st.plotly_chart(fig_month, width="stretch")

st.markdown("""
**Interpretare:**  
Distribuția lunară a traficului permite identificarea eventualelor modele sezoniere, 
precum perioadele de vârf asociate vacanțelor și sezonului turistic.
""")

st.markdown("---")

# ==============================
# TOP AIRPORTS
# ==============================
airport_filtered = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(total_traffic=("traffic", "sum"))
    .sort_values("total_traffic", ascending=False)
)

top_n = st.slider("Selectează numărul de aeroporturi afișate în clasament", 5, 20, 10)

top_airports = airport_filtered.head(top_n)

fig_airports = px.bar(
    top_airports,
    x="APT_ICAO",
    y="total_traffic",
    hover_data=["APT_NAME", "STATE_NAME"],
    title=f"Top {top_n} aeroporturi după traficul total",
    labels={
        "APT_ICAO": "Aeroport",
        "total_traffic": "Trafic total"
    }
)

st.plotly_chart(fig_airports, width="stretch")

st.markdown("""
**Interpretare:**  
Clasamentul aeroporturilor evidențiază principalele noduri de trafic aerian din Europa. 
Aeroporturile cu valori ridicate ale traficului pot fi considerate centre operaționale majore.
""")

st.markdown("---")

# ==============================
# TABLE
# ==============================
st.subheader("Tabel sinteză aeroporturi")

table_summary = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(
        total_traffic=("traffic", "sum"),
        avg_daily_traffic=("traffic", "mean")
    )
    .sort_values("total_traffic", ascending=False)
)

st.dataframe(table_summary, width="stretch")