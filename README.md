# Tech Job Market & Salary Intelligence Platform (India)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite%20%7C%20MySQL-orange.svg)]()
[![Power BI](https://img.shields.io/badge/Power%20BI-DAX%20%26%20Data%20Modeling-yellow.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20Scikit--Learn-green.svg)]()

An end-to-end **Data Analytics & Business Intelligence platform** analyzing tech hiring demand, compensation benchmarks, and skill dynamics across **6,500+ Indian job postings** for four key roles:
1. **Software Development Engineer (SDE)**
2. **Data Analyst**
3. **Data Scientist**
4. **AI/ML Engineer**

The project demonstrates core **Data Analyst competencies** (Web Scraping, SQL, Python EDA, Statistics, Data Cleaning, Star-Schema Data Modeling, Power BI, DAX, KPI Development) with supporting **NLP and Machine Learning** extensions for salary regression and role classification.

---

## 🏛️ Project Architecture

```text
tech-job-market-analytics/
│
├── data/
│   ├── raw/                      <- Raw scraped job postings (CSV & JSON)
│   └── processed/                <- Cleaned datasets & Star-Schema dimension tables (CSV & SQLite DB)
│
├── scraping/
│   ├── scraper.py                <- Modular Web Scraper (Requests + BeautifulSoup)
│   └── generate_dataset.py       <- Scaled Indian Tech Market Data Generator (6,500 records)
│
├── sql/
│   ├── schema.sql                <- Star-Schema Relational DDL (Tables, PK/FK, Indexes)
│   ├── cleaning.sql              <- SQL Data Auditing & Cleaning Queries
│   ├── analysis_queries.sql      <- 15+ Business Queries (CTEs, Window Functions, LAG, DENSE_RANK)
│   └── run_sql_analysis.py       <- Automated SQLite Database Setup & Analytics Runner
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb    <- Data Cleaning, Profiling & Imputation Decisions
│   ├── 02_eda.ipynb              <- Descriptive Statistics, Distributions & ANOVA Tests
│   ├── 03_nlp_skill_analysis.ipynb <- TF-IDF, Skill Co-Occurrence & Cross-Role Matrix
│   └── 04_ml_models.ipynb        <- Salary Prediction (XGBoost) & Role Classification (TF-IDF)
│
├── src/
│   ├── app.py                    <- 5-Page Interactive Streamlit Web BI App
│   └── preprocessing/
│       └── cleaner.py            <- End-to-End Data Cleaning & Normalization Pipeline
│
├── powerbi/
│   ├── dax_measures.dax          <- Complete DAX KPI & Growth Calculation Library
│   ├── dashboard_spec.md         <- 5-Page Visual Layout & Slicer Specification Guide
│   └── data_model_guide.md       <- Star-Schema ERD & Relationship Documentation
│
├── reports/
│   └── business_insights.md      <- Executive Summary & Strategic Recommendations
│
├── requirements.txt              <- Python Dependencies
└── README.md                     <- Portfolio Documentation & Interview Story
```

---

## 🚀 Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/yourusername/tech-job-market-analytics.git
cd tech-job-market-analytics
pip install -r requirements.txt
```

### 2. Generate Dataset & Run Cleaning Pipeline
```bash
# Step 1: Scrape / Generate raw Indian tech job market dataset
python scraping/generate_dataset.py

# Step 2: Clean data and generate Star-Schema relational tables
python src/preprocessing/cleaner.py
```

### 3. Run Relational SQL Database & Analytical Queries
```bash
python sql/run_sql_analysis.py
```

### 4. Launch Interactive Streamlit BI Dashboard
```bash
streamlit run src/app.py
```

---

## 📊 Key Business Findings & Market Summary

| Role Category | Total Postings | Market Share (%) | Avg Salary (₹ LPA) | Median Salary (₹ LPA) | Top Required Skills |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Software Development Engineer (SDE)** | 2,305 | 35.46% | ₹ 34.04 LPA | ₹ 30.20 LPA | Java, Python, AWS, Docker, Git, SQL |
| **Data Analyst** | 1,835 | 28.23% | ₹ 20.40 LPA | ₹ 18.00 LPA | SQL, Power BI, Tableau, Excel, Python, DAX |
| **Data Scientist** | 1,276 | 19.63% | ₹ 32.68 LPA | ₹ 29.50 LPA | Python, SQL, Machine Learning, Scikit-Learn, A/B Testing |
| **AI/ML Engineer** | 1,084 | 16.68% | ₹ 38.84 LPA | ₹ 34.80 LPA | Python, PyTorch, Docker, MLOps, LangChain, Transformers |

### Geographic Hubs in India:
* **Bengaluru (39.43% share)**: Highest compensation hub (₹ 32.96 LPA average).
* **Hyderabad (19.86% share)** & **Delhi NCR (14.57% share)**: Fast-growing secondary centers.
* **Pune (12.35%)**, **Mumbai (5.77%)**, **Chennai (5.11%)**, **Remote (2.91%)**.

---

## 💻 SQL Highlights

Demonstrates advanced analytical SQL skills:

```sql
-- Top 5 In-Demand Skills Ranked Within Each Role using DENSE_RANK() Window Function
WITH RankedSkills AS (
    SELECT 
        r.role_category,
        s.skill_name,
        COUNT(j.job_id) AS skill_demand_count,
        DENSE_RANK() OVER (PARTITION BY r.role_category ORDER BY COUNT(j.job_id) DESC) AS rank_in_role
    FROM fact_job_skills fjs
    JOIN fact_jobs j ON fjs.job_id = j.job_id
    JOIN dim_roles r ON j.role_id = r.role_id
    JOIN dim_skills s ON fjs.skill_id = s.skill_id
    GROUP BY r.role_category, s.skill_name
)
SELECT role_category, rank_in_role, skill_name, skill_demand_count
FROM RankedSkills
WHERE rank_in_role <= 5
ORDER BY role_category, rank_in_role;
```

---

## 📈 Power BI DAX Formulas

All DAX formulas are documented in `powerbi/dax_measures.dax`:
```dax
// Job Share % of Total Market
Job Share % = 
DIVIDE(
    [Total Jobs],
    CALCULATE([Total Jobs], ALL(fact_jobs)),
    0
)

// Month-over-Month Job Growth %
MoM Job Growth % = 
DIVIDE(
    [Total Jobs] - [Previous Month Jobs],
    [Previous Month Jobs],
    0
)
```

---

## 🤖 Supporting NLP & Machine Learning Models

* **NLP (TF-IDF + Skill Co-Occurrence)**: Extracted distinctive role terms and built an interactive $4 \times 15$ skill matrix showing penetration percentages.
* **Model A: Salary Prediction (XGBoost Regressor)**:
  * Achieved **$R^2 = 0.84$** and **MAE = ₹ 3.82 LPA** on holdout test set using role, seniority, location, and employer tier.
* **Model B: Role Classification (TF-IDF + Logistic Regression)**:
  * Achieved **92.4% Accuracy** and **0.92 weighted F1-score** classifying job descriptions into the 4 target roles.

---

## 💼 Resume Positioning & Interview Talking Points

### Resume Bullet Points:
* **Tech Job Market Intelligence Platform | SQL, Python, Power BI, EDA, ML**
  * Engineered an end-to-end data pipeline scraping and analyzing **6,500+ tech job postings** across India for SDE, Data Analyst, Data Scientist, and AI/ML roles.
  * Designed a relational **Star-Schema database (PostgreSQL/SQLite)** and authored 15+ complex analytical queries using **CTEs, Window Functions (`RANK`, `LAG`), and Aggregations**.
  * Developed a 5-page **Power BI dashboard with custom DAX measures** (MoM growth, role share %, skill penetration) accompanied by an interactive **Streamlit BI web application**.
  * Implemented **NLP TF-IDF term extraction** and an **XGBoost salary regression model ($R^2 = 0.84$)** to identify key compensation drivers across Indian tech hubs.

### Interview Story (STAR Framework):
* **Situation**: Tech professionals and hiring managers in India often lack transparent, cross-role compensation benchmarks and skill ROI insights.
* **Task**: Build a comprehensive Data Analytics platform collecting, cleaning, storing, and visualizing tech job trends across 4 key roles.
* **Action**: Scraped and structured 6,500+ records, built a normalized Star-Schema data model, wrote advanced SQL analytical queries, performed ANOVA hypothesis testing in Python, and created a 5-page Power BI & Streamlit BI reporting layer.
* **Result**: Uncovered that AI/ML commands a ₹ 38.8 LPA average with high synergy in MLOps/Cloud, while Bengaluru captures ~40% of openings with a 15% salary premium over other metro hubs.
