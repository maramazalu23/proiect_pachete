import glob
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]   # .../app
DATA_RAW_DIR = BASE_DIR / "data" / "raw"


@st.cache_data
def load_traffic_data(path_pattern=None):
    if path_pattern is None:
        path_pattern = str(DATA_RAW_DIR / "airport_traffic_*.csv")

    files = sorted(glob.glob(path_pattern))

    if not files:
        raise FileNotFoundError(
            f"Nu au fost găsite fișierele airport_traffic_*.csv în folderul {DATA_RAW_DIR}"
        )

    df_list = []
    for file in files:
        df = pd.read_csv(file)
        df_list.append(df)

    traffic = pd.concat(df_list, ignore_index=True)

    expected_cols = ["FLT_DATE", "APT_ICAO", "APT_NAME", "STATE_NAME", "FLT_TOT_1"]
    missing_cols = [col for col in expected_cols if col not in traffic.columns]
    if missing_cols:
        raise ValueError(
            f"Lipsesc coloanele necesare din fișierele de trafic: {missing_cols}"
        )

    traffic = traffic[expected_cols].copy()

    traffic["FLT_DATE"] = pd.to_datetime(traffic["FLT_DATE"], errors="coerce")
    traffic["FLT_TOT_1"] = pd.to_numeric(traffic["FLT_TOT_1"], errors="coerce")

    traffic = traffic.dropna(subset=["FLT_DATE", "APT_ICAO"])
    traffic = traffic.rename(columns={"FLT_TOT_1": "traffic"})

    return traffic


@st.cache_data
def load_delay_data(path_pattern=None):
    if path_pattern is None:
        path_pattern = str(DATA_RAW_DIR / "apt_dly_*.csv")

    files = sorted(glob.glob(path_pattern))

    if not files:
        raise FileNotFoundError(
            f"Nu au fost găsite fișierele apt_dly_*.csv în folderul {DATA_RAW_DIR}"
        )

    df_list = []
    for file in files:
        df = pd.read_csv(file)
        df_list.append(df)

    delays = pd.concat(df_list, ignore_index=True)

    expected_base_cols = ["FLT_DATE", "APT_ICAO"]
    missing_base = [col for col in expected_base_cols if col not in delays.columns]
    if missing_base:
        raise ValueError(
            f"Lipsesc coloanele necesare din fișierele de întârzieri: {missing_base}"
        )

    delays["FLT_DATE"] = pd.to_datetime(delays["FLT_DATE"], errors="coerce", utc=True)
    delays["FLT_DATE"] = delays["FLT_DATE"].dt.tz_localize(None)

    delay_cols = [col for col in delays.columns if col.startswith("DLY_APT_ARR_")]

    if not delay_cols:
        raise ValueError(
            "Nu au fost identificate coloane de întârziere care încep cu 'DLY_APT_ARR_'."
        )

    for col in delay_cols:
        delays[col] = pd.to_numeric(delays[col], errors="coerce").fillna(0)

    delays["total_delay"] = delays[delay_cols].sum(axis=1)

    delays = delays[["FLT_DATE", "APT_ICAO", "total_delay"]].copy()
    delays = delays.dropna(subset=["FLT_DATE", "APT_ICAO"])

    return delays


@st.cache_data
def load_final_dataset():
    traffic = load_traffic_data()
    delays = load_delay_data()

    df = pd.merge(
        traffic,
        delays,
        on=["FLT_DATE", "APT_ICAO"],
        how="left"
    )

    df["total_delay"] = df["total_delay"].fillna(0)

    df["year"] = df["FLT_DATE"].dt.year
    df["month"] = df["FLT_DATE"].dt.month
    df["month_name"] = df["FLT_DATE"].dt.month_name()

    return df


@st.cache_data
def get_airport_summary():
    df = load_final_dataset()

    summary = (
        df.groupby(["APT_ICAO", "APT_NAME", "STATE_NAME"], as_index=False)
        .agg(
            total_traffic=("traffic", "sum"),
            avg_daily_traffic=("traffic", "mean"),
            total_delay=("total_delay", "sum"),
            avg_daily_delay=("total_delay", "mean"),
        )
        .sort_values("total_traffic", ascending=False)
    )

    return summary


@st.cache_data
def get_yearly_traffic():
    df = load_final_dataset()

    yearly = (
        df.groupby("year", as_index=False)
        .agg(total_traffic=("traffic", "sum"))
        .sort_values("year")
    )

    return yearly


@st.cache_data
def get_yearly_delays():
    df = load_final_dataset()

    yearly = (
        df.groupby("year", as_index=False)
        .agg(total_delay=("total_delay", "sum"))
        .sort_values("year")
    )

    return yearly