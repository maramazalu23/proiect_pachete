import streamlit as st
import plotly.express as px
import pandas as pd

from utils.load_data import load_covid_impact, load_final_dataset

st.set_page_config(page_title="Impact COVID-19", page_icon="🦠", layout="wide")

st.title("🦠 Impactul COVID-19 asupra aviației europene")
st.markdown("""
Pandemia COVID-19 a reprezentat cel mai sever șoc din istoria aviației civile.  
Această pagină analizează amploarea colapsului din 2020 și viteza de recuperare  
a fiecărei țări și aeroport până în 2023, pe baza datelor oficiale EUROCONTROL.
""")

# ==============================
# LOAD DATA
# ==============================
pivot_country, pivot_apt = load_covid_impact()
df = load_final_dataset()

st.markdown("---")

# ==============================
# KPI COVID
# ==============================
total_2019 = df[df["year"] == 2019]["traffic"].sum()
total_2020 = df[df["year"] == 2020]["traffic"].sum()
total_2023 = df[df["year"] == 2023]["traffic"].sum()

drop_pct = round((total_2020 - total_2019) / total_2019 * 100, 1)
recovery_pct = round(total_2023 / total_2019 * 100, 1)
recovered_apts = int((pivot_apt["recovery_pct"] >= 100).sum()) if "recovery_pct" in pivot_apt.columns else 0
total_apts = len(pivot_apt)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Scădere trafic 2019→2020", f"{drop_pct}%", delta=f"{drop_pct}%", delta_color="inverse")
with col2:
    st.metric("Recuperare 2023 vs 2019", f"{recovery_pct}%")
with col3:
    st.metric("Aeroporturi complet recuperate", f"{recovered_apts} / {total_apts}")
with col4:
    st.metric("Zboruri pierdute în 2020", f"{(total_2019 - total_2020):,}".replace(",", "."))

st.markdown("---")

# ==============================
# IMPACT COVID PE TARI
# ==============================
st.subheader("1. Impactul COVID-19 pe țări (scădere trafic 2019 → 2020)")

if "drop_pct" in pivot_country.columns:
    drop_df = pivot_country[["STATE_NAME", "drop_pct"]].dropna().sort_values("drop_pct")

    fig_drop = px.bar(
        drop_df,
        x="drop_pct",
        y="STATE_NAME",
        orientation="h",
        title="Scăderea procentuală a traficului în 2020 față de 2019, pe țări",
        labels={
            "drop_pct": "Variație trafic (%)",
            "STATE_NAME": "Țară"
        },
        color="drop_pct",
        color_continuous_scale="RdYlGn",
        range_color=[-75, 10]
    )
    fig_drop.update_layout(
        height=800,
        coloraxis_showscale=False,
        yaxis={"tickfont": {"size": 11}}
    )
    st.plotly_chart(fig_drop, width="stretch")

    st.markdown("""
    **Interpretare:**  
    Toate țările europene au înregistrat scăderi semnificative ale traficului în 2020.  
    Țările cu dependență ridicată de turismul internațional și rutele intercontinentale  
    (Georgia, Israel, Maroc) au fost cele mai afectate, cu scăderi de peste 65%.  
    Țările cu trafic intern consistent sau rute de tranzit esențiale au rezistat relativ mai bine.
    """)

st.markdown("---")

# ==============================
# RATA DE RECUPERARE PE TARI
# ==============================
st.subheader("2. Rata de recuperare a traficului în 2023 față de 2019, pe țări")

if "recovery_pct" in pivot_country.columns:
    rec_df = pivot_country[["STATE_NAME", "recovery_pct"]].dropna().sort_values(
        "recovery_pct", ascending=False
    )

    fig_rec = px.bar(
        rec_df,
        x="recovery_pct",
        y="STATE_NAME",
        orientation="h",
        title="Recuperare trafic 2023 vs 2019 (100% = revenire completă)",
        labels={
            "recovery_pct": "Rata recuperare (%)",
            "STATE_NAME": "Țară"
        },
        color="recovery_pct",
        color_continuous_scale="RdYlGn",
        range_color=[50, 150]
    )
    fig_rec.add_vline(
        x=100,
        line_dash="dash",
        line_color="gray",
        annotation_text="Nivel 2019",
        annotation_position="top"
    )
    fig_rec.update_layout(
        height=800,
        coloraxis_showscale=False,
        yaxis={"tickfont": {"size": 11}}
    )
    st.plotly_chart(fig_rec, width="stretch")

    st.markdown("""
    **Interpretare:**  
    Linia verticală marcează nivelul de referință din 2019. Țările cu bare verzi care depășesc  
    această linie și-au depășit traficul pre-pandemic până în 2023. Țările cu bare roșii  
    continuă să se recupereze. Această diferență reflectă atât viteza de redeschidere a  
    frontierelor, cât și dinamica economică și turistică a fiecărei regiuni.
    """)

st.markdown("---")

# ==============================
# EVOLUTIE ANUALA TRAFIC
# ==============================
st.subheader("3. Evoluția traficului total european 2019–2023")

yearly = (
    df.groupby("year", as_index=False)
    .agg(total_traffic=("traffic", "sum"))
)
yearly["pct_vs_2019"] = (yearly["total_traffic"] / yearly.loc[yearly["year"] == 2019, "total_traffic"].values[0] * 100).round(1)

fig_evo = px.bar(
    yearly,
    x="year",
    y="total_traffic",
    text="pct_vs_2019",
    title="Trafic total european pe ani (% față de 2019)",
    labels={"year": "An", "total_traffic": "Trafic total"},
    color="total_traffic",
    color_continuous_scale="Blues"
)
fig_evo.update_traces(texttemplate="%{text}%", textposition="outside")
fig_evo.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_evo, width="stretch")

st.markdown("""
**Interpretare:**  
Graficul ilustrează cei cinci ani analizați ca procent față de nivelul de referință din 2019.  
Prăbușirea la ~43% din traficul normal în 2020 a fost urmată de o revenire treptată:  
54% în 2021, 84% în 2022 și 92% în 2023 — un ritm de recuperare remarcabil pentru un sector  
atât de puternic afectat.
""")

st.markdown("---")

# ==============================
# TOP AEROPORTURI RECUPERATE / NERECUPERATE
# ==============================
st.subheader("4. Aeroporturi — status recuperare în 2023")

if "recovery_pct" in pivot_apt.columns:
    apt_rec = pivot_apt[["APT_ICAO", "APT_NAME", "STATE_NAME", "recovery_pct"]].dropna()
    apt_rec = apt_rec[apt_rec["recovery_pct"] > 0]

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Top 15 aeroporturi cu cea mai rapidă recuperare**")
        top_rec = apt_rec.sort_values("recovery_pct", ascending=False).head(15)
        fig_top = px.bar(
            top_rec,
            x="recovery_pct",
            y="APT_ICAO",
            orientation="h",
            hover_data=["APT_NAME", "STATE_NAME"],
            labels={"recovery_pct": "Recuperare (%)", "APT_ICAO": "Aeroport"},
            color="recovery_pct",
            color_continuous_scale="Greens"
        )
        fig_top.add_vline(x=100, line_dash="dash", line_color="gray")
        fig_top.update_layout(coloraxis_showscale=False, height=450)
        st.plotly_chart(fig_top, width="stretch")

    with col_b:
        st.markdown("**Top 15 aeroporturi cu cea mai lentă recuperare**")
        bot_rec = apt_rec.sort_values("recovery_pct").head(15)
        fig_bot = px.bar(
            bot_rec,
            x="recovery_pct",
            y="APT_ICAO",
            orientation="h",
            hover_data=["APT_NAME", "STATE_NAME"],
            labels={"recovery_pct": "Recuperare (%)", "APT_ICAO": "Aeroport"},
            color="recovery_pct",
            color_continuous_scale="Reds"
        )
        fig_bot.add_vline(x=100, line_dash="dash", line_color="gray")
        fig_bot.update_layout(coloraxis_showscale=False, height=450)
        st.plotly_chart(fig_bot, width="stretch")

    st.markdown("""
    **Interpretare:**  
    Aeroporturile care au depășit nivelul de trafic din 2019 sunt în general hub-uri  
    regionale sau aeroporturi din țări cu turism în creștere. Aeroporturile cu recuperare  
    lentă reflectă efecte persistente ale pandemiei — rute intercontinentale nerestabilite  
    sau restructurări ale companiilor aeriene care le deserveau.
    """)