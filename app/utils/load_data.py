import glob
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = BASE_DIR / "data" / "raw"


@st.cache_data
def load_traffic_data(path_pattern=None):
    if path_pattern is None:
        path_pattern = str(DATA_RAW_DIR / "airport_traffic_*.csv")

    files = sorted(glob.glob(path_pattern))

    if not files:
        raise FileNotFoundError(
            f"Nu au fost gasite fisierele airport_traffic_*.csv in folderul {DATA_RAW_DIR}"
        )

    traffic = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    expected_cols = ["FLT_DATE", "APT_ICAO", "APT_NAME", "STATE_NAME", "FLT_TOT_1"]
    missing_cols = [col for col in expected_cols if col not in traffic.columns]
    if missing_cols:
        raise ValueError(f"Lipsesc coloanele necesare din fisierele de trafic: {missing_cols}")

    traffic = traffic[expected_cols].copy()
    traffic["FLT_DATE"] = pd.to_datetime(traffic["FLT_DATE"], errors="coerce")
    traffic["FLT_TOT_1"] = pd.to_numeric(traffic["FLT_TOT_1"], errors="coerce")
    traffic = traffic.dropna(subset=["FLT_DATE", "APT_ICAO"])
    traffic = traffic.rename(columns={"FLT_TOT_1": "traffic"})

    return traffic


@st.cache_data
def load_traffic_raw():
    """Returneaza datele de trafic INAINTE de tratarea valorilor lipsa - pentru cerinta 4."""
    path_pattern = str(DATA_RAW_DIR / "airport_traffic_*.csv")
    files = sorted(glob.glob(path_pattern))
    traffic = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    traffic["FLT_DATE"] = pd.to_datetime(traffic["FLT_DATE"], errors="coerce")
    return traffic


@st.cache_data
def load_delay_data(path_pattern=None):
    if path_pattern is None:
        path_pattern = str(DATA_RAW_DIR / "apt_dly_*.csv")

    files = sorted(glob.glob(path_pattern))

    if not files:
        raise FileNotFoundError(
            f"Nu au fost gasite fisierele apt_dly_*.csv in folderul {DATA_RAW_DIR}"
        )

    delays = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    expected_base_cols = ["FLT_DATE", "APT_ICAO"]
    missing_base = [col for col in expected_base_cols if col not in delays.columns]
    if missing_base:
        raise ValueError(f"Lipsesc coloanele necesare din fisierele de intarzieri: {missing_base}")

    delays["FLT_DATE"] = pd.to_datetime(delays["FLT_DATE"], errors="coerce", utc=True)
    delays["FLT_DATE"] = delays["FLT_DATE"].dt.tz_convert(None)

    delay_cols = [col for col in delays.columns if col.startswith("DLY_APT_ARR_")]

    if not delay_cols:
        raise ValueError("Nu au fost identificate coloane de intarziere care incep cu DLY_APT_ARR_.")

    for col in delay_cols:
        delays[col] = pd.to_numeric(delays[col], errors="coerce").fillna(0)

    delays["total_delay"] = delays[delay_cols].sum(axis=1)
    delays = delays[["FLT_DATE", "APT_ICAO", "total_delay"]].copy()
    delays = delays.dropna(subset=["FLT_DATE", "APT_ICAO"])

    return delays


@st.cache_data
def load_delay_by_cause():
    """Returneaza intarzierile detaliate pe categorii de cauze."""
    path_pattern = str(DATA_RAW_DIR / "apt_dly_*.csv")
    files = sorted(glob.glob(path_pattern))
    delays = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    delays["FLT_DATE"] = pd.to_datetime(delays["FLT_DATE"], errors="coerce", utc=True)
    delays["FLT_DATE"] = delays["FLT_DATE"].dt.tz_convert(None)

    delay_cols = [c for c in delays.columns if c.startswith("DLY_APT_ARR_") and c != "DLY_APT_ARR_1"]
    for col in delay_cols:
        delays[col] = pd.to_numeric(delays[col], errors="coerce").fillna(0)

    cause_map = {
        "DLY_APT_ARR_A_1": "Accident / incident",
        "DLY_APT_ARR_C_1": "Capacitate ATC",
        "DLY_APT_ARR_D_1": "Deficiente de date",
        "DLY_APT_ARR_E_1": "Echipament (tehnic)",
        "DLY_APT_ARR_G_1": "ATC general",
        "DLY_APT_ARR_I_1": "Infrastructura aeroport",
        "DLY_APT_ARR_M_1": "Evenimente militare",
        "DLY_APT_ARR_N_1": "Personal ATC",
        "DLY_APT_ARR_O_1": "Alte cauze",
        "DLY_APT_ARR_P_1": "Personal aeroport",
        "DLY_APT_ARR_R_1": "Rutare",
        "DLY_APT_ARR_S_1": "Spatiu aerian restrictiv",
        "DLY_APT_ARR_T_1": "Trafic / congestie",
        "DLY_APT_ARR_V_1": "Conditii meteo en-route",
        "DLY_APT_ARR_W_1": "Vreme / meteo aeroport",
        "DLY_APT_ARR_NA_1": "Necategorizat",
    }

    keep_cols = ["FLT_DATE", "APT_ICAO", "APT_NAME", "STATE_NAME"] + delay_cols
    keep_cols = [c for c in keep_cols if c in delays.columns]
    delays = delays[keep_cols].copy()
    delays = delays.rename(columns=cause_map)
    delays["year"] = delays["FLT_DATE"].dt.year

    return delays


@st.cache_data
def load_covid_impact():
    """Returneaza impactul COVID si rata de recuperare per tara si aeroport."""
    path_pattern = str(DATA_RAW_DIR / "airport_traffic_*.csv")
    files = sorted(glob.glob(path_pattern))
    traffic = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    traffic["FLT_DATE"] = pd.to_datetime(traffic["FLT_DATE"], errors="coerce")
    traffic["year"] = traffic["FLT_DATE"].dt.year
    traffic["FLT_TOT_1"] = pd.to_numeric(traffic["FLT_TOT_1"], errors="coerce")

    country_year = (
        traffic.groupby(["STATE_NAME", "year"], as_index=False)
        .agg(total_traffic=("FLT_TOT_1", "sum"))
    )
    pivot_country = country_year.pivot_table(
        index="STATE_NAME", columns="year", values="total_traffic"
    ).reset_index()
    pivot_country.columns.name = None
    pivot_country.columns = [str(c) for c in pivot_country.columns]

    if "2019" in pivot_country.columns and "2020" in pivot_country.columns:
        pivot_country["drop_pct"] = (
            (pivot_country["2020"] - pivot_country["2019"]) / pivot_country["2019"] * 100
        ).round(1)
    if "2019" in pivot_country.columns and "2023" in pivot_country.columns:
        pivot_country["recovery_pct"] = (
            pivot_country["2023"] / pivot_country["2019"] * 100
        ).round(1)

    apt_year = (
        traffic.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME", "year"], as_index=False)
        .agg(total_traffic=("FLT_TOT_1", "sum"))
    )
    pivot_apt = apt_year.pivot_table(
        index=["APT_ICAO", "APT_NAME", "STATE_NAME"], columns="year", values="total_traffic"
    ).reset_index()
    pivot_apt.columns.name = None
    pivot_apt.columns = [str(c) for c in pivot_apt.columns]

    if "2019" in pivot_apt.columns and "2023" in pivot_apt.columns:
        pivot_apt["recovery_pct"] = (
            pivot_apt["2023"] / pivot_apt["2019"] * 100
        ).round(1)

    return pivot_country, pivot_apt


@st.cache_data
def load_final_dataset():
    traffic = load_traffic_data()
    delays = load_delay_data()

    df = pd.merge(traffic, delays, on=["FLT_DATE", "APT_ICAO"], how="left")
    df["total_delay"] = df["total_delay"].fillna(0)
    df["year"] = df["FLT_DATE"].dt.year
    df["month"] = df["FLT_DATE"].dt.month
    df["month_name"] = df["FLT_DATE"].dt.month_name()

    return df


@st.cache_data
def get_airport_summary():
    df = load_final_dataset()
    return (
        df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
        .agg(
            total_traffic=("traffic", "sum"),
            avg_daily_traffic=("traffic", "mean"),
            total_delay=("total_delay", "sum"),
            avg_daily_delay=("total_delay", "mean"),
        )
        .sort_values("total_traffic", ascending=False)
    )


@st.cache_data
def get_yearly_traffic():
    df = load_final_dataset()
    return (
        df.groupby("year", as_index=False)
        .agg(total_traffic=("traffic", "sum"))
        .sort_values("year")
    )


@st.cache_data
def get_yearly_delays():
    df = load_final_dataset()
    return (
        df.groupby("year", as_index=False)
        .agg(total_delay=("total_delay", "sum"))
        .sort_values("year")
    )