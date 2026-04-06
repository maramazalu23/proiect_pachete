import streamlit as st
import plotly.express as px
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from utils.load_data import load_final_dataset

st.set_page_config(page_title="Predicții", page_icon="📉", layout="wide")

st.title("📉 Analiză predictivă")
st.markdown(
    "Această pagină utilizează un model de regresie liniară pentru a analiza relația "
    "dintre traficul total și întârzierile totale la nivel de aeroport."
)

# ==============================
# LOAD DATA
# ==============================
df = load_final_dataset().copy()

# ==============================
# FILTERS
# ==============================
st.sidebar.header("Filtre predicții")

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
# AGGREGATION FOR MODEL
# ==============================
model_df = (
    filtered_df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
    .agg(
        total_traffic=("traffic", "sum"),
        total_delay=("total_delay", "sum")
    )
)

model_df = model_df.dropna(subset=["total_traffic", "total_delay"])

st.subheader("1. Setul de date utilizat pentru model")
st.dataframe(model_df.head(20), width="stretch")

# ==============================
# REGRESSION
# ==============================
X = model_df[["total_traffic"]]
y = model_df["total_delay"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# ==============================
# METRICS
# ==============================
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

st.subheader("2. Metrici ale modelului")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("MAE", f"{mae:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

with col2:
    st.metric("MSE", f"{mse:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

with col3:
    st.metric("R²", f"{r2:.4f}")

st.markdown("""
**Interpretare:**  
Modelul de regresie liniară estimează măsura în care variația traficului total este asociată cu variația întârzierilor totale.  
Valorile indicatorilor de eroare și coeficientul de determinare oferă o imagine asupra calității ajustării modelului.
""")

st.markdown("---")

# ==============================
# SCATTER REAL DATA
# ==============================
st.subheader("3. Relația observată dintre trafic și întârziere")

fig_real = px.scatter(
    model_df,
    x="total_traffic",
    y="total_delay",
    hover_data=["APT_ICAO", "APT_NAME", "STATE_NAME"],
    title="Relația observată dintre traficul total și întârzierea totală",
    labels={
        "total_traffic": "Trafic total",
        "total_delay": "Întârziere totală"
    }
)

st.plotly_chart(fig_real, width="stretch")

st.markdown("---")

# ==============================
# ACTUAL VS PREDICTED
# ==============================
st.subheader("4. Valori reale vs valori estimate")

results_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_pred
})

fig_pred = px.scatter(
    results_df,
    x="actual",
    y="predicted",
    title="Comparație între valorile reale și valorile estimate",
    labels={
        "actual": "Valori reale",
        "predicted": "Valori estimate"
    }
)

st.plotly_chart(fig_pred, width="stretch")

st.dataframe(results_df.head(20), width="stretch")

st.markdown("""
**Interpretare:**  
Cu cât punctele sunt mai apropiate de direcția ideală a egalității dintre valorile reale și cele estimate, cu atât modelul are o performanță mai bună.
""")

st.markdown("---")

# ==============================
# MODEL COEFFICIENT
# ==============================
st.subheader("5. Coeficientul modelului")

coef_df = pd.DataFrame({
    "indicator": ["intercept", "coef_total_traffic"],
    "valoare": [model.intercept_, model.coef_[0]]
})

st.dataframe(coef_df, width="stretch")

st.markdown("""
**Interpretare:**  
Coeficientul asociat traficului total indică direcția și intensitatea relației estimate dintre volum și întârziere.  
Un coeficient pozitiv sugerează că un trafic mai ridicat este asociat, în medie, cu întârzieri mai mari.
""")