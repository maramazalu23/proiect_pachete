# Analiza performanței traficului aerian european și a întârzierilor ATFM (2019–2023)

Proiect realizat în cadrul disciplinei **Pachete Software** — Facultatea CSIE, anul III.

---

## Descriere

Proiectul analizează performanța traficului aerian european în perioada 2019–2023, utilizând date oficiale furnizate de **EUROCONTROL** prin intermediul portalului [Aviation Intelligence Portal](https://ansperformance.eu/data/).

Perioada analizată acoperă un context economic relevant: traficul pre-pandemic (2019), scăderea drastică din perioada COVID-19 (2020), redresarea treptată (2021–2022) și revenirea la un nivel apropiat de normalitate (2023).

Analiza urmărește identificarea relației dintre volumul traficului aerian și întârzierile operaționale (ATFM), precum și evaluarea eficienței aeroporturilor în diferite contexte economice.

Proiectul este structurat în două componente principale:

* **Python** — aplicație interactivă dezvoltată în Streamlit pentru explorarea și analiza datelor
* **SAS** — prelucrări statistice, raportare și generare de grafice

---

## Date utilizate

Sursa datelor: [EUROCONTROL Aviation Intelligence Portal](https://ansperformance.eu/data/) — date oficiale, gratuite, care acoperă aeroporturile europene monitorizate.

| Fișier                     | Descriere                                                    | Perioadă  |
| -------------------------- | ------------------------------------------------------------ | --------- |
| `airport_traffic_YYYY.csv` | Zboruri IFR zilnice (sosiri + plecări) per aeroport          | 2019–2023 |
| `apt_dly_YYYY.csv`         | Întârzieri ATFM la sosire per aeroport și categorie de cauză | 2019–2023 |

**Dimensiunea datelor:**

* Airport Traffic: ~562.000 înregistrări, 333 aeroporturi, 42 țări
* ATFM Delays: ~493.000 înregistrări, 15 categorii de cauze

---

## Metodologie

Analiza a fost realizată prin integrarea a două seturi de date la nivel de aeroport și zi, utilizând drept chei comune codul aeroportului și data calendaristică.

Etapele principale ale prelucrării datelor au fost:

* curățarea și standardizarea formatelor (date, coduri aeroport)
* tratarea valorilor lipsă
* agregarea datelor la nivel lunar și anual
* calculul indicatorilor statistici relevanți (medii, variații)
* analiza relațiilor dintre variabile prin metode statistice și modele predictive

---

## Structura proiectului

```
proiect-aviation/
├── README.md
├── data/
│   ├── raw/                          # Fișierele CSV originale descărcate de pe EUROCONTROL
│   │   ├── airport_traffic_2019.csv
│   │   ├── airport_traffic_2020.csv
│   │   ├── airport_traffic_2021.csv
│   │   ├── airport_traffic_2022.csv
│   │   ├── airport_traffic_2023.csv
│   │   ├── apt_dly_2019.csv
│   │   ├── apt_dly_2020.csv
│   │   ├── apt_dly_2021.csv
│   │   ├── apt_dly_2022.csv
│   │   └── apt_dly_2023.csv
│   └── processed/                    # Date procesate generate în urma prelucrării
├── app/
│   ├── app.py                        # Pagina principală Streamlit
│   ├── pages/
│   │   ├── 1_Trafic.py               # Evoluția traficului aerian 2019–2023
│   │   ├── 2_Intarzieri.py           # Analiza întârzierilor ATFM pe cauze
│   │   ├── 3_Analiza.py              # Statistici, grupări și clustering
│   │   └── 4_Predictii.py            # Modele de regresie și clasificare
│   ├── utils/                        # Funcții reutilizabile (încărcare, curățare, preprocesare)
│   └── requirements.txt
└── sas/
    ├── 01_import_date.sas            # Creare seturi de date SAS din CSV
    ├── 02_formate_si_curatare.sas    # Formate definite de utilizator + curățare
    ├── 03_procesare.sas              # Procesare iterativă și condițională
    ├── 04_subseturi.sas              # Creare subseturi de date
    ├── 05_combinare_sql.sas          # Îmbinare seturi de date (PROC SQL)
    ├── 06_raportare_statistici.sas   # Statistici descriptive și grafice
    └── output/                       # Rapoarte și grafice generate de SAS
```

---

## Facilități implementate

### Python (Streamlit)

| # | Facilitate               | Descriere                                           |
| - | ------------------------ | --------------------------------------------------- |
| 1 | Structură multi-pagină   | Organizarea aplicației pe mai multe pagini          |
| 2 | Filtrare interactivă     | Utilizarea widget-urilor pentru selecția datelor    |
| 3 | Import date CSV          | Încărcarea și combinarea fișierelor folosind pandas |
| 4 | Tratarea valorilor lipsă | Curățarea și completarea datelor                    |
| 5 | Preprocesare date        | Codificarea variabilelor categoriale și scalare     |
| 6 | Agregare și grupare      | Analiza datelor prin `groupby`                      |
| 7 | Vizualizare date         | Grafice interactive realizate cu Plotly             |
| 8 | Machine Learning         | Modele de regresie și clustering (scikit-learn)     |

---

### SAS

| # | Facilitate             | Descriere                                         |
| - | ---------------------- | ------------------------------------------------- |
| 1 | Import date            | Crearea seturilor de date SAS din fișiere externe |
| 2 | Formate personalizate  | Definirea și utilizarea formatelor                |
| 3 | Procesare condițională | Prelucrarea iterativă a datelor                   |
| 4 | Subseturi              | Crearea de subseturi relevante                    |
| 5 | Combinare date         | Îmbinarea seturilor de date folosind PROC SQL     |
| 6 | Analiză statistică     | Calcul indicatori și generare grafice             |

---

## Instalare și rulare (Python)

### Cerințe

* Python 3.9+
* Fișierele CSV plasate în directorul `data/raw/`

### Pași

```bash
# Clonare repository
git clone https://github.com/username/proiect-aviation.git
cd proiect-aviation

# Creare mediu virtual
python -m venv .venv
# Activare mediu virtual (Windows)
.venv\Scripts\activate
# Activare mediu virtual (Linux/Mac)
source .venv/bin/activate

# Instalare dependențe
pip install -r app/requirements.txt

# Rulare aplicație
streamlit run app/app.py
```

---

## Autori

| Nume             | Contribuție                                                     |
| ---------------- | --------------------------------------------------------------- |
| Mazâlu Mara     | Dezvoltare aplicație Python (Streamlit) și analiză exploratorie |
| Mitu Ana-Maria-Antonia | Analiză statistică și prelucrare date în SAS                    |

Facultatea CSIE — Pachete Software, Anul III, 2024–2025
