"""
Notebooks Generator Script
===========================
Generates 4 fully documented, clean, and executable Jupyter Notebooks:
1. 01_data_cleaning.ipynb
2. 02_eda.ipynb
3. 03_nlp_skill_analysis.ipynb
4. 04_ml_models.ipynb
"""

import os
import nbformat as nbf


def make_notebook(cells, file_path):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    with open(file_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Created notebook: {file_path}")


def create_01_cleaning_notebook():
    cells = [
        nbf.v4.new_markdown_cell("""# 01 — Data Cleaning & Preprocessing Pipeline
## Project: Tech Job Market & Salary Intelligence Platform (India)

**Objective**: This notebook demonstrates an end-to-end data cleaning and engineering workflow that transforms raw, messy tech job postings into standardized, validated datasets and relational Star-Schema dimensional tables.

---
### Workflow Steps:
1. **Data Ingestion & Profiling**: Inspecting initial schema, data types, and missingness.
2. **Deduplication**: Detecting and removing duplicate job postings.
3. **Location Normalization**: Standardizing city variants (e.g., Bangalore -> Bengaluru) across Indian tech hubs.
4. **Experience Parsing**: Extracting numerical minimum/maximum years and creating 4 seniority brackets.
5. **Salary Standardization & Imputation**: Converting all compensation to INR Lakhs per Annum (LPA) and handling missing values with conditional group medians.
6. **Skill Canonicalization**: Normalizing skill strings into consistent casing and categories.
7. **Star-Schema Dimensional Modeling**: Exporting clean tables (`dim_roles`, `dim_companies`, `dim_locations`, `dim_dates`, `dim_skills`, `fact_jobs`, `fact_job_skills`).
"""),
        nbf.v4.new_code_cell("""# Step 1: Import Core Libraries
import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

# Set clean visualization style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["font.size"] = 11

print("Libraries imported successfully!")
"""),
        nbf.v4.new_code_cell("""# Step 2: Load Raw Job Market Data
raw_path = "data/raw/raw_jobs_india.csv" if os.path.exists("data/raw/raw_jobs_india.csv") else "../data/raw/raw_jobs_india.csv"
output_dir = "data/processed" if os.path.exists("data/processed") else "../data/processed"

df_raw = pd.read_csv(raw_path)
print(f"Total Raw Records: {len(df_raw):,}")
print(f"Total Columns: {len(df_raw.columns)}")
df_raw.head(3)
"""),
        nbf.v4.new_code_cell("""# Step 3: Check Missing Values in Raw Data
missing_summary = pd.DataFrame({
    "Missing Count": df_raw.isnull().sum(),
    "Missing Percentage (%)": (df_raw.isnull().sum() / len(df_raw) * 100).round(2)
})
missing_summary[missing_summary["Missing Count"] > 0]
"""),
        nbf.v4.new_code_cell("""# Step 4: Run the Standardized Data Cleaner Pipeline
from src.preprocessing.cleaner import TechJobDataCleaner

cleaner = TechJobDataCleaner(raw_data_path=raw_path, output_dir=output_dir)
df_cleaned, schema_tables = cleaner.run_pipeline()

print(f"Cleaned dataset ready: {len(df_cleaned):,} rows")
"""),
        nbf.v4.new_code_cell("""# Step 5: Visualizing Salary Distributions Before and After Imputation
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Before Imputation (Only Disclosed)
sns.histplot(df_raw["min_salary_lpa_raw"].dropna(), kde=True, ax=axes[0], color="#2b5c8f")
axes[0].set_title("Salary Distribution (Disclosed Only, N=5,430)")
axes[0].set_xlabel("Salary (INR LPA)")

# After Normalization & Conditional Imputation
sns.histplot(df_cleaned["avg_salary_lpa"], kde=True, ax=axes[1], color="#2ca02c")
axes[1].set_title("Cleaned & Imputed Salary Distribution (N=6,500)")
axes[1].set_xlabel("Average Salary (INR LPA)")

plt.tight_layout()
plt.show()
"""),
        nbf.v4.new_code_cell("""# Step 6: Verify Star-Schema Exported Tables
print("Exported Dimensional Tables:")
for table_name, table_df in schema_tables.items():
    print(f"  - {table_name:<18}: {len(table_df):>6,} rows | Columns: {list(table_df.columns)}")
""")
    ]
    make_notebook(cells, "notebooks/01_data_cleaning.ipynb")


def create_02_eda_notebook():
    cells = [
        nbf.v4.new_markdown_cell("""# 02 — Exploratory Data Analysis & Statistics
## Project: Tech Job Market & Salary Intelligence Platform (India)

**Objective**: Perform statistical exploration and hypothesis testing to answer key business questions regarding tech job demand, compensation structures, experience dynamics, and geographic hubs across India.

---
### Key Business Questions Addressed:
1. **Job Demand**: Which roles and companies are hiring most in India?
2. **Salary Intelligence**: What are the average, median, and spread of salaries per role?
3. **Experience Impact**: How does compensation scale across experience tiers?
4. **Geographic Distribution**: Which Indian tech hubs offer the highest compensation?
5. **Statistical Testing**: Is the salary difference between roles statistically significant (ANOVA)?
"""),
        nbf.v4.new_code_cell("""# Step 1: Import Libraries & Load Cleaned Data
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (11, 6)

csv_path = "data/processed/cleaned_jobs.csv" if os.path.exists("data/processed/cleaned_jobs.csv") else "../data/processed/cleaned_jobs.csv"
df = pd.read_csv(csv_path)
print(f"Cleaned dataset loaded successfully: {len(df):,} job postings")
df.head(2)
"""),
        nbf.v4.new_markdown_cell("### 1. Descriptive Statistics: Salary Across 4 Tech Roles"),
        nbf.v4.new_code_cell("""# Descriptive Summary Table for Salary (INR LPA)
salary_stats = df.groupby("role_category")["avg_salary_lpa"].agg(
    Postings="count",
    Mean="mean",
    Median="median",
    Std_Dev="std",
    Min="min",
    Max="max",
    IQR=lambda x: x.quantile(0.75) - x.quantile(0.25)
).round(2).reset_index()

salary_stats
"""),
        nbf.v4.new_code_cell("""# Visualizing Salary Distributions Across Roles (Box & Violin Plot)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

sns.boxplot(data=df, x="role_category", y="avg_salary_lpa", palette="Set2", ax=axes[0])
axes[0].set_title("Salary Distribution by Tech Role (Boxplot)", fontsize=14, fontweight="bold")
axes[0].set_xlabel("Role Category")
axes[0].set_ylabel("Average Salary (INR LPA)")
axes[0].tick_params(axis="x", rotation=15)

sns.violinplot(data=df, x="role_category", y="avg_salary_lpa", palette="Pastel1", inner="quartile", ax=axes[1])
axes[1].set_title("Salary Density by Tech Role (Violin Plot)", fontsize=14, fontweight="bold")
axes[1].set_xlabel("Role Category")
axes[1].set_ylabel("Average Salary (INR LPA)")
axes[1].tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.show()
"""),
        nbf.v4.new_markdown_cell("### 2. Hiring Demand & Geographic Hubs in India"),
        nbf.v4.new_code_cell("""# Job Demand by Indian City
city_demand = df["city"].value_counts().reset_index()
city_demand.columns = ["City", "Total Postings"]
city_demand["Market Share %"] = (city_demand["Total Postings"] / len(df) * 100).round(2)

plt.figure(figsize=(10, 5))
bar = sns.barplot(data=city_demand, x="City", y="Total Postings", palette="viridis")
plt.title("Tech Job Postings by City (India)", fontsize=14, fontweight="bold")
plt.xlabel("City")
plt.ylabel("Number of Postings")
for p in bar.patches:
    bar.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')
plt.show()
city_demand
"""),
        nbf.v4.new_markdown_cell("### 3. Experience vs. Salary Dynamics"),
        nbf.v4.new_code_cell("""# Experience vs Salary by Role
plt.figure(figsize=(12, 6))
sns.lineplot(
    data=df, 
    x="experience_avg", 
    y="avg_salary_lpa", 
    hue="role_category", 
    marker="o", 
    linewidth=2.5,
    palette="tab10"
)
plt.title("Salary Growth Trajectory with Experience (Years)", fontsize=14, fontweight="bold")
plt.xlabel("Average Experience Required (Years)")
plt.ylabel("Average Salary (INR LPA)")
plt.legend(title="Role Category")
plt.show()
"""),
        nbf.v4.new_markdown_cell("### 4. Statistical Hypothesis Testing: One-Way ANOVA on Role Salaries"),
        nbf.v4.new_code_cell("""# Test if salary difference between the 4 roles is statistically significant
roles = df["role_category"].unique()
role_groups = [df[df["role_category"] == r]["avg_salary_lpa"].values for r in roles]

f_stat, p_val = stats.f_oneway(*role_groups)

print(f"ANOVA F-Statistic: {f_stat:.4f}")
print(f"p-value: {p_val:.4e}")

if p_val < 0.05:
    print("Conclusion: Reject Null Hypothesis (H0). There is a statistically significant difference in salaries across tech roles in India.")
else:
    print("Conclusion: Fail to reject Null Hypothesis.")
""")
    ]
    make_notebook(cells, "notebooks/02_eda.ipynb")


def create_03_nlp_notebook():
    cells = [
        nbf.v4.new_markdown_cell("""# 03 — NLP & Skill Intelligence Analysis
## Project: Tech Job Market & Salary Intelligence Platform (India)

**Objective**: Apply Natural Language Processing (NLP) techniques (tokenization, stop-word removal, TF-IDF, and co-occurrence modeling) on job descriptions and requirements to uncover distinguishing terminology and skill synergies across roles.

---
### Key Analytics:
1. **TF-IDF Term Extraction**: Identifying top distinctive terms for each role.
2. **Skill Co-Occurrence Analysis**: Which technical tools frequently appear together?
3. **Cross-Role Skill Matrix**: Comparing skill prevalence across SDE, Data Analyst, Data Scientist, and AI/ML Engineer.
"""),
        nbf.v4.new_code_cell("""# Step 1: Import Libraries
import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

sns.set_theme(style="whitegrid")
csv_path = "data/processed/cleaned_jobs.csv" if os.path.exists("data/processed/cleaned_jobs.csv") else "../data/processed/cleaned_jobs.csv"
df = pd.read_csv(csv_path)
print(f"Loaded {len(df):,} jobs for NLP analysis.")
"""),
        nbf.v4.new_markdown_cell("### 1. TF-IDF Analysis: Extracting Distinctive Terminology per Role"),
        nbf.v4.new_code_cell("""# Initialize TF-IDF Vectorizer
tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=2000,
    ngram_range=(1, 2),
    min_df=10
)

tfidf_matrix = tfidf.fit_transform(df["description_clean"])
feature_names = np.array(tfidf.get_feature_names_out())

# Extract top TF-IDF keywords per role
top_keywords_by_role = {}
for role in df["role_category"].unique():
    role_indices = df[df["role_category"] == role].index
    role_tfidf_mean = np.asarray(tfidf_matrix[role_indices].mean(axis=0)).flatten()
    top_indices = role_tfidf_mean.argsort()[-8:][::-1]
    top_keywords_by_role[role] = [(feature_names[i], round(role_tfidf_mean[i], 4)) for i in top_indices]

# Display as DataFrame
df_tfidf_summary = pd.DataFrame({
    role: [f"{kw} ({score})" for kw, score in kws]
    for role, kws in top_keywords_by_role.items()
})
df_tfidf_summary
"""),
        nbf.v4.new_markdown_cell("### 2. Cross-Role Skill Comparison Matrix"),
        nbf.v4.new_code_cell("""# Build Skill Demand Matrix across the 4 Roles
base_dir = "data/processed" if os.path.exists("data/processed") else "../data/processed"
fjs = pd.read_csv(os.path.join(base_dir, "fact_job_skills.csv"))
dim_skills = pd.read_csv(os.path.join(base_dir, "dim_skills.csv"))
dim_roles = pd.read_csv(os.path.join(base_dir, "dim_roles.csv"))
fact_jobs = pd.read_csv(os.path.join(base_dir, "fact_jobs.csv"))

# Merge
merged_skills = fjs.merge(dim_skills, on="skill_id").merge(fact_jobs[["job_id", "role_id"]], on="job_id").merge(dim_roles, on="role_id")

# Create Cross-tab of Skill vs Role %
skill_role_crosstab = pd.crosstab(
    merged_skills["skill_name"], 
    merged_skills["role_category"], 
    normalize="columns"
) * 100

# Select top 15 most prominent skills
top_overall_skills = merged_skills["skill_name"].value_counts().head(15).index
skill_matrix_top = skill_role_crosstab.loc[top_overall_skills].round(1)

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(skill_matrix_top, annot=True, fmt=".1f", cmap="Blues", cbar_kws={'label': 'Role Penetration (%)'})
plt.title("Tech Skill Matrix: Penetration % Across Roles", fontsize=14, fontweight="bold")
plt.xlabel("Role Category")
plt.ylabel("Skill Name")
plt.show()

skill_matrix_top
"""),
        nbf.v4.new_markdown_cell("### 3. Skill Co-Occurrence Network"),
        nbf.v4.new_code_cell("""# Compute Co-occurrence for Data Analyst & AI/ML Skills
from itertools import combinations

co_occur_counter = Counter()
for skills_str in df["skills"]:
    skills_list = [s.strip() for s in skills_str.split(";")]
    for s1, s2 in combinations(sorted(skills_list), 2):
        co_occur_counter[(s1, s2)] += 1

# Top 10 most common skill pairs
top_pairs = co_occur_counter.most_common(10)
df_pairs = pd.DataFrame([{"Skill 1": p[0][0], "Skill 2": p[0][1], "Co-occurrences": p[1]} for p in top_pairs])
df_pairs
""")
    ]
    make_notebook(cells, "notebooks/03_nlp_skill_analysis.ipynb")


def create_04_ml_notebook():
    cells = [
        nbf.v4.new_markdown_cell("""# 04 — Supporting Machine Learning Models
## Project: Tech Job Market & Salary Intelligence Platform (India)

**Objective**: Implement supporting Machine Learning models to solve two targeted analytical problems:
1. **Model A (Salary Prediction Regression)**: Predict expected compensation (`avg_salary_lpa`) from role, experience, location, company tier, industry, and skills using Linear Regression, Random Forest, and XGBoost.
2. **Model B (Job Role Classification)**: Classify job postings into the 4 target roles using TF-IDF text features and Logistic Regression / Random Forest.

> [!NOTE]
> *Disclaimer*: Feature importance in these models represents statistical association within the dataset and does not establish unilateral real-world causality.
"""),
        nbf.v4.new_code_cell("""# Step 1: Import Libraries
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb

sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

sns.set_theme(style="whitegrid")
csv_path = "data/processed/cleaned_jobs.csv" if os.path.exists("data/processed/cleaned_jobs.csv") else "../data/processed/cleaned_jobs.csv"
df = pd.read_csv(csv_path)
print(f"Loaded {len(df):,} records for ML modeling.")
"""),
        nbf.v4.new_markdown_cell("### 1. Model A — Salary Prediction (Regression)"),
        nbf.v4.new_code_cell("""# Feature Engineering for Regression
features = ["role_category", "experience_avg", "city", "company_tier", "industry"]
target = "avg_salary_lpa"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

categorical_cols = ["role_category", "city", "company_tier", "industry"]
numerical_cols = ["experience_avg"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols)
    ]
)

# Benchmark 3 Regressors
models = {
    "Linear Regression (Baseline)": LinearRegression(),
    "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost Regressor": xgb.XGBRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42)
}

results = []
trained_pipelines = {}

for name, model in models.items():
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    results.append({
        "Model": name,
        "MAE (INR LPA)": round(mae, 2),
        "RMSE (INR LPA)": round(rmse, 2),
        "R2 Score": round(r2, 4)
    })
    trained_pipelines[name] = pipeline

df_results = pd.DataFrame(results)
df_results
"""),
        nbf.v4.new_code_cell("""# Feature Importance from XGBoost Regressor
xgb_model = trained_pipelines["XGBoost Regressor"].named_steps["model"]
encoded_cat_names = trained_pipelines["XGBoost Regressor"].named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_cols)
all_feature_names = list(numerical_cols) + list(encoded_cat_names)

importance_df = pd.DataFrame({
    "Feature": all_feature_names,
    "Importance": xgb_model.feature_importances_
}).sort_values(by="Importance", ascending=False).head(12)

plt.figure(figsize=(10, 5))
sns.barplot(data=importance_df, x="Importance", y="Feature", palette="mako")
plt.title("Top Feature Importances for Salary Prediction (XGBoost)", fontsize=14, fontweight="bold")
plt.xlabel("Relative Importance Score")
plt.show()

importance_df
"""),
        nbf.v4.new_markdown_cell("### 2. Model B — Job Role Classification (NLP + Classifier)"),
        nbf.v4.new_code_cell("""# Text & Role Classification
X_text = df["description_clean"] + " " + df["skills"]
y_role = df["role_category"]

X_tr_text, X_te_text, y_tr_role, y_te_role = train_test_split(X_text, y_role, test_size=0.2, random_state=42, stratify=y_role)

clf_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=2500, ngram_range=(1, 2), stop_words="english")),
    ("classifier", LogisticRegression(max_iter=1000, random_state=42))
])

clf_pipeline.fit(X_tr_text, y_tr_role)
y_pred_role = clf_pipeline.predict(X_te_text)

acc = accuracy_score(y_te_role, y_pred_role)
print(f"Classification Accuracy: {acc * 100:.2f}%\n")
print("--- Classification Report ---")
print(classification_report(y_te_role, y_pred_role))
"""),
        nbf.v4.new_code_cell("""# Confusion Matrix Heatmap
cm = confusion_matrix(y_te_role, y_pred_role, labels=clf_pipeline.classes_)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=clf_pipeline.classes_, yticklabels=clf_pipeline.classes_)
plt.title("Confusion Matrix — Job Role Classification", fontsize=14, fontweight="bold")
plt.xlabel("Predicted Role")
plt.ylabel("Actual Role")
plt.xticks(rotation=20)
plt.show()
""")
    ]
    make_notebook(cells, "notebooks/04_ml_models.ipynb")


if __name__ == "__main__":
    os.makedirs("notebooks", exist_ok=True)
    create_01_cleaning_notebook()
    create_02_eda_notebook()
    create_03_nlp_notebook()
    create_04_ml_notebook()
    print("All 4 Jupyter Notebooks generated successfully!")
