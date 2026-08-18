# Analysis of European Air Traffic Performance and ATFM Delays (2019–2023)

Project developed as part of the **Software Packages** course — Faculty of CSIE, Year III.

---

## Description

The project analyzes the performance of European air traffic during the 2019–2023 period, using official data provided by **EUROCONTROL** through the [Aviation Intelligence Portal](https://ansperformance.eu/data/).

The analyzed period covers a relevant economic context: pre-pandemic traffic (2019), the drastic decline during the COVID-19 period (2020), the gradual recovery (2021–2022), and the return to a level close to normality (2023).

The analysis aims to identify the relationship between air traffic volume and operational delays (ATFM), as well as to evaluate airport efficiency under different economic contexts.

The project is structured into two main components:

* **Python** — interactive application developed in Streamlit for data exploration, statistical analysis, predictive modeling, and interactive visualization
* **SAS** — statistical processing, descriptive procedures, reporting, and graph generation

---

## Data used

Data source: [EUROCONTROL Aviation Intelligence Portal](https://ansperformance.eu/data/) — official, freely available data covering monitored European airports.

| File                       | Description                                                 | Period    |
| -------------------------- | ----------------------------------------------------------- | --------- |
| `airport_traffic_YYYY.csv` | Daily IFR flights (arrivals + departures) per airport       | 2019–2023 |
| `apt_dly_YYYY.csv`         | Arrival ATFM delays per airport and cause category          | 2019–2023 |

**Data size:**

* Airport Traffic: ~562,000 records, 333 airports, 42 countries
* ATFM Delays: ~493,000 records, 15 cause categories

---

## Methodology

The analysis was performed by integrating two datasets at the airport and day level, using the airport code and calendar date as common keys.

The main data processing stages were:

* cleaning and standardizing formats (dates, airport codes)
* handling missing values
* aggregating data at monthly and annual levels
* calculating relevant statistical indicators (averages, variations)
* analyzing relationships between variables through statistical methods, clustering, linear regression, and multiple regression

---

## Project structure

```text
proiect_pachete/
├── README.md
├── app/
│   ├── 0_Acasa.py                        # Main Streamlit page
│   ├── data/
│   │   ├── raw/                          # Original CSV files downloaded from EUROCONTROL
│   │   │   ├── airport_traffic_2019.csv
│   │   │   ├── airport_traffic_2020.csv
│   │   │   ├── airport_traffic_2021.csv
│   │   │   ├── airport_traffic_2022.csv
│   │   │   ├── airport_traffic_2023.csv
│   │   │   ├── apt_dly_2019.csv
│   │   │   ├── apt_dly_2020.csv
│   │   │   ├── apt_dly_2021.csv
│   │   │   ├── apt_dly_2022.csv
│   │   │   └── apt_dly_2023.csv
│   │   └── processed/                    # Processed data generated after processing
│   ├── pages/
│   │   ├── 1_Trafic.py                   # Evolution of air traffic 2019–2023
│   │   ├── 2_Intarzieri.py               # Analysis of ATFM delays by cause
│   │   ├── 3_Analiza.py                  # Statistics, grouping, and clustering
│   │   ├── 4_Predictii.py                # Predictive analysis through linear regression
│   │   └── 5_Covid.py                    # Impact of COVID-19 and recovery rate
│   ├── utils/                            # Reusable functions (loading, cleaning, preprocessing)
│   │   ├── export_data.py
│   │   └── load_data.py
│   └── requirements.txt
└── sas/
    ├── 01_import_raw.sas                         # Importing raw CSV files into SAS
    ├── 01_import_raw-results.html                # Results of running the import script
    ├── 02_build_final_dataset.sas                # Building the final dataset
    ├── 02_build_final_dataset-results.html       # Results of building the final dataset
    ├── 03_formats_subsets_reports.sas            # Formats, subsets, and reporting
    ├── 03_formats_subsets_reports-results.html   # Reporting-related results
    ├── 04_statistical_procedures.sas             # Descriptive statistical procedures
    ├── 04_statistical_procedures-results.html    # Results of statistical procedures
    ├── 05_graphs.sas                             # Graph generation in SAS
    └── 05_graphs-results.html                    # Generated graphs and results
```

---

## Implemented features

### Python (Streamlit)

| #  | Feature                                       | Description                                                                  |
|----|-----------------------------------------------|------------------------------------------------------------------------------|
| 1  | Multi-page structure                          | Organizing the application across multiple pages                             |
| 2  | Interactive filtering                         | Using widgets for data and chart selection                                   |
| 3  | CSV data import                               | Loading and combining CSV files using `pandas`                               |
| 4  | Handling missing values                       | Identifying and filling missing values during the preprocessing stage        |
| 5  | Encoding and scaling                          | Encoding categorical variables and scaling numerical variables               |
| 6  | Aggregation and grouping                      | Statistical processing through `groupby`, aggregations, and summary tables   |
| 7  | Accessing data with `loc` and `iloc`          | Selecting observations by position and logical conditions                    |
| 8  | Dynamic visualization                        | Interactive charts created with `plotly`                                     |
| 9  | Machine Learning with scikit-learn            | K-Means clustering and linear regression                                     |
| 10 | Multiple regression with statsmodels          | Estimating an OLS model for explaining total delays                          |
| 11 | Displaying metrics                            | Using `st.metric` for key indicators and model metrics                       |

---

### SAS

| # | Feature                | Description                                           |
| - | ---------------------- | ----------------------------------------------------- |
| 1 | Data import            | Creating SAS datasets from external files             |
| 2 | Custom formats         | Defining and using formats                            |
| 3 | Conditional processing | Iterative data processing                             |
| 4 | Subsets                | Creating relevant subsets                             |
| 5 | Data combination       | Merging datasets using PROC SQL                       |
| 6 | Statistical analysis   | Calculating indicators and generating graphs          |

---

## Installation and running (Python)

### Requirements

* Python 3.9+
* CSV files placed in the `app/data/raw/` directory

### Steps

```bash
# Clone repository
git clone https://github.com/username/proiect_pachete.git
cd proiect_pachete

# Create virtual environment
python -m venv .venv
# Activate virtual environment (Windows)
.venv\Scripts\activate
# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Run application
python -m streamlit run app/0_Acasa.py
```

---

## Authors

| Name             | Contribution                                                     |
| ---------------- | ---------------------------------------------------------------- |
| Mazâlu Mara      | Python application development (Streamlit) and exploratory analysis |
| Mitu Ana-Maria-Antonia | Statistical analysis and data processing in SAS             |

CSIE, Group 1091, Series D
