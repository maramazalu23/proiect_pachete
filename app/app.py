import streamlit as st
from utils.load_data import load_final_dataset

st.set_page_config(
    page_title="Trafic aerian european",
    page_icon="✈️",
    layout="wide"
)

df = load_final_dataset()

st.title("✈️ Analiza performanței traficului aerian european și a întârzierilor ATFM")
st.subheader("Perioada analizată: 2019–2023")

st.markdown("""
Această aplicație interactivă a fost realizată în cadrul proiectului de la disciplina **Pachete Software**  
și analizează relația dintre traficul aeroportuar și întârzierile ATFM în aeroporturile europene,  
pe baza datelor oficiale furnizate de **EUROCONTROL**.
""")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Număr observații", f"{len(df):,}".replace(",", "."))

with col2:
    st.metric("Număr aeroporturi", df["APT_ICAO"].nunique())

with col3:
    st.metric("Număr țări", df["STATE_NAME"].nunique())

with col4:
    st.metric("Perioadă", "2019–2023")

st.markdown("---")

st.markdown("""
## Obiectivele aplicației

- analiza evoluției traficului aerian european;
- analiza întârzierilor ATFM la nivel de aeroport;
- evidențierea relației dintre trafic și întârzieri;
- aplicarea unor metode statistice și predictive pentru interpretarea datelor.
""")

st.markdown("""
## Structura aplicației

Aplicația este organizată în patru pagini principale:

- **Trafic** — evoluția traficului aerian și clasamentul aeroporturilor;
- **Întârzieri** — analiza întârzierilor ATFM și relația acestora cu traficul;
- **Analiză** — prelucrare statistică, valori lipsă, codificare, scalare și clustering;
- **Predicții** — model de regresie liniară pentru estimarea întârzierilor.
""")

st.info(
    "Navigarea între secțiuni se face din meniul lateral al aplicației."
)

st.markdown("---")

st.markdown("""
## Sursa datelor

Datele utilizate provin din portalul **EUROCONTROL Aviation Intelligence Portal**  
și includ informații despre:
- traficul aeroportuar zilnic;
- întârzierile ATFM la sosire;
- aeroporturi europene monitorizate în perioada 2019–2023.
""")