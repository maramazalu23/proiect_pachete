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

- analiza evoluției traficului aerian european în perioada 2019–2023;
- analiza întârzierilor ATFM la nivel de aeroport și pe categorii de cauze;
- evidențierea impactului COVID-19 și a ratei de recuperare per țară;
- aplicarea unor metode statistice și predictive pentru interpretarea datelor.
""")

st.markdown("""
## Structura aplicației

Aplicația este organizată în cinci pagini principale:

- **Trafic** — evoluția traficului aerian, sezonalitate și clasamentul aeroporturilor;
- **Întârzieri** — analiza întârzierilor ATFM pe cauze și eficiența operațională;
- **Analiză** — prelucrare statistică, valori lipsă, codificare, scalare și clustering;
- **Predicții** — analiză predictivă a relației dintre trafic și întârzieri prin regresie liniară;
- **COVID** — analiza colapsului din 2020 și rata de recuperare per țară și aeroport.
            
Prin această structură, aplicația permite atât explorarea interactivă a datelor, cât și formularea unor concluzii economice relevante privind performanța traficului aerian european.
""")

st.info("Navigarea între secțiuni se face din meniul lateral al aplicației.")

st.markdown("---")

st.markdown("""
## Sursa datelor

Datele utilizate provin din portalul **EUROCONTROL Aviation Intelligence Portal**  
și includ informații despre:
- traficul aeroportuar zilnic (IFR flights) — 562.436 înregistrări;
- întârzierile ATFM la sosire pe 15 categorii de cauze — 493.221 înregistrări;
- aeroporturi europene monitorizate: 333 aeroporturi din 42 de țări.
""")