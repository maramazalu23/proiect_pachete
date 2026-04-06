import streamlit as st
import plotly.express as px
import pandas as pd

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans

from utils.load_data import load_final_dataset

st.set_page_config(page_title="Analiză statistică", page_icon="📊", layout="wide")

st.title("📊 Analiză statistică și clustering")
st.markdown(
    "Această pagină evidențiază prelucrarea statistică a datelor și gruparea aeroporturilor "
    "în funcție de trafic și întârzieri."
)

# ==============================
# LOAD DATA
# ==============================
df = load_final_dataset().copy()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filtre analiză")

years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Selectează anul / anii",
    options=years,
    default=years
)

countries = sorted(df["STATE_NAME"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Selectează țara/țările",
    options=countries,
    default=[]
)

filtered_df = df[df["year"].isin(selected_years)].copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df["STATE_NAME"].isin(selected_countries)]

# ==============================
# MISSING VALUES
# ==============================
st.subheader("1. Verificarea valorilor lipsă")

missing_df = filtered_df.isna().sum().reset_index()
missing_df.columns = ["coloana", "numar_valori_lipsa"]
missing_df["procent_valori_lipsa"] = (
    missing_df["numar_valori_lipsa"] / len(filtered_df) * 100
).round(2)

st.dataframe(missing_df, width="stretch")

st.markdown("""
**Interpretare:**  
Identificarea valorilor lipsă reprezintă o etapă esențială în preprocesarea datelor.  
În cadrul aplicației, valorile lipsă sunt tratate înainte de analiza statistică și predictivă.
""")

st.markdown("---")

# ==============================
# BASIC AGGREGATION
# ==============================
st.subheader("2. Agregare date la nivel de aeroport")

airport_stats = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(
        total_traffic=("traffic", "sum"),
        avg_daily_traffic=("traffic", "mean"),
        total_delay=("total_delay", "sum"),
        avg_daily_delay=("total_delay", "mean")
    )
    .sort_values("total_traffic", ascending=False)
)

st.dataframe(airport_stats.head(20), width="stretch")

st.markdown("""
**Interpretare:**  
Agregarea datelor la nivel de aeroport permite evidențierea principalelor noduri de trafic și a nivelului mediu al întârzierilor operaționale.
""")

st.markdown("---")

# ==============================
# ENCODING
# ==============================
st.subheader("3. Codificarea variabilelor categoriale")

encoded_df = airport_stats.copy()

label_encoder = LabelEncoder()
encoded_df["state_encoded"] = label_encoder.fit_transform(encoded_df["STATE_NAME"])

encoding_preview = encoded_df[["STATE_NAME", "state_encoded"]].drop_duplicates().sort_values("STATE_NAME")
st.dataframe(encoding_preview.head(20), width="stretch")

st.markdown("""
**Interpretare:**  
Pentru utilizarea unor algoritmi de învățare automată, variabilele categoriale trebuie transformate în valori numerice.
""")

st.markdown("---")

# ==============================
# SCALING
# ==============================
st.subheader("4. Scalarea variabilelor numerice")

features_for_scaling = encoded_df[[
    "total_traffic",
    "avg_daily_traffic",
    "total_delay",
    "avg_daily_delay",
    "state_encoded"
]].copy()

scaler = StandardScaler()
scaled_array = scaler.fit_transform(features_for_scaling)

scaled_df = pd.DataFrame(
    scaled_array,
    columns=[
        "total_traffic_scaled",
        "avg_daily_traffic_scaled",
        "total_delay_scaled",
        "avg_daily_delay_scaled",
        "state_encoded_scaled"
    ]
)

st.dataframe(scaled_df.head(10), width="stretch")

st.markdown("""
**Interpretare:**  
Scalarea variabilelor este necesară pentru a elimina efectul diferențelor de ordin de mărime dintre indicatori și pentru a asigura funcționarea corectă a algoritmilor de grupare.
""")

st.markdown("---")

# ==============================
# CLUSTERING
# ==============================
st.subheader("5. Gruparea aeroporturilor prin K-Means")

n_clusters = st.slider("Selectează numărul de clustere", min_value=2, max_value=6, value=3)

kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
clusters = kmeans.fit_predict(scaled_array)

clustered_df = encoded_df.copy()
clustered_df["cluster"] = clusters.astype(str)

fig_cluster = px.scatter(
    clustered_df,
    x="total_traffic",
    y="total_delay",
    color="cluster",
    hover_data=["APT_ICAO", "APT_NAME", "STATE_NAME"],
    title="Clustering al aeroporturilor în funcție de trafic și întârzieri",
    labels={
        "total_traffic": "Trafic total",
        "total_delay": "Întârziere totală",
        "cluster": "Cluster"
    }
)

st.plotly_chart(fig_cluster, width="stretch")

st.markdown("""
**Interpretare:**  
Clusteringul permite identificarea unor grupuri de aeroporturi cu profil operațional similar.  
De exemplu, unele aeroporturi pot avea trafic ridicat și întârzieri ridicate, în timp ce altele pot combina trafic ridicat cu eficiență mai bună.
""")

st.markdown("---")

# ==============================
# CLUSTER SUMMARY
# ==============================
st.subheader("6. Sinteză pe clustere")

cluster_summary = (
    clustered_df.groupby("cluster", as_index=False)
    .agg(
        num_airports=("APT_ICAO", "count"),
        avg_total_traffic=("total_traffic", "mean"),
        avg_total_delay=("total_delay", "mean")
    )
    .sort_values("cluster")
)

st.dataframe(cluster_summary, width="stretch")

st.markdown("""
**Interpretare:**  
Tabelul de sinteză pe clustere ajută la caracterizarea fiecărui grup rezultat și la formularea unor concluzii comparative între aeroporturi.
""")