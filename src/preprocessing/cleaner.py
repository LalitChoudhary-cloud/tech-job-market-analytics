"""
Data Engineering & Cleaning Pipeline
====================================
Transforms raw messy tech job postings into standardized, validated, and normalized data models.
Exports cleaned flat dataset and Star-Schema dimensional tables ready for SQL databases and Power BI.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

CITY_MAPPING = {
    "bengaluru": ("Bengaluru", "Karnataka", "Tier-1 Hub"),
    "bangalore": ("Bengaluru", "Karnataka", "Tier-1 Hub"),
    "hyderabad": ("Hyderabad", "Telangana", "Tier-1 Hub"),
    "secunderabad": ("Hyderabad", "Telangana", "Tier-1 Hub"),
    "hitec city": ("Hyderabad", "Telangana", "Tier-1 Hub"),
    "pune": ("Pune", "Maharashtra", "Tier-1 Hub"),
    "hinjawadi": ("Pune", "Maharashtra", "Tier-1 Hub"),
    "gurugram": ("Delhi NCR", "Haryana", "Tier-1 Hub"),
    "gurgaon": ("Delhi NCR", "Haryana", "Tier-1 Hub"),
    "noida": ("Delhi NCR", "Uttar Pradesh", "Tier-1 Hub"),
    "delhi": ("Delhi NCR", "Delhi", "Tier-1 Hub"),
    "mumbai": ("Mumbai", "Maharashtra", "Tier-1 Hub"),
    "navi mumbai": ("Mumbai", "Maharashtra", "Tier-1 Hub"),
    "chennai": ("Chennai", "Tamil Nadu", "Tier-1 Hub"),
    "remote": ("Remote", "India", "Remote")
}

SKILL_CANONICAL_MAP = {
    "python": "Python",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "excel": "Excel",
    "ms excel": "Excel",
    "dax": "DAX",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "r": "R",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "bigquery": "BigQuery",
    "snowflake": "Snowflake",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "redis": "Redis",
    "java": "Java",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "c++": "C++",
    "go": "Go",
    "golang": "Go",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "react": "React",
    "react.js": "React",
    "typescript": "TypeScript",
    "rest apis": "REST APIs",
    "microservices": "Microservices",
    "system design": "System Design",
    "mlops": "MLOps",
    "langchain": "LangChain",
    "llms": "LLMs",
    "llm": "LLMs",
    "transformers": "Transformers",
    "computer vision": "Computer Vision",
    "nlp": "NLP",
    "xgboost": "XGBoost",
    "a/b testing": "A/B Testing",
    "statistics": "Statistics",
    "data modeling": "Data Modeling",
    "fastapi": "FastAPI",
    "data storytelling": "Data Storytelling"
}

SKILL_CATEGORIES = {
    "Programming & Frameworks": ["Python", "Java", "C++", "Go", "Spring Boot", "Node.js", "React", "TypeScript", "FastAPI", "R"],
    "Data Analysis & BI": ["SQL", "Power BI", "Tableau", "Excel", "DAX", "Data Modeling", "Data Storytelling", "Looker", "Alteryx"],
    "Data Engineering & Cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Snowflake", "BigQuery", "Apache Spark", "Apache Kafka", "Redis", "PostgreSQL", "MySQL", "CI/CD", "Git", "Microservices", "System Design"],
    "AI / ML & Advanced Analytics": ["Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy", "XGBoost", "NLP", "Computer Vision", "Transformers", "LLMs", "LangChain", "MLOps", "Statistics", "A/B Testing"]
}


class TechJobDataCleaner:
    """End-to-end data cleaning and dimensional modeling pipeline."""

    def __init__(self, raw_data_path: str = "data/raw/raw_jobs_india.csv", output_dir: str = "data/processed"):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.cleaning_log: List[Dict] = []

    def log_decision(self, step: str, details: str, impacted_count: int):
        self.cleaning_log.append({
            "step": step,
            "decision": details,
            "impacted_records": impacted_count,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[CLEANING LOG] {step}: {details} (Impacted: {impacted_count})")

    def parse_location(self, loc_str: str) -> Tuple[str, str, str]:
        """Normalize raw location string into (City, State, Location_Type)."""
        if not isinstance(loc_str, str) or not loc_str.strip():
            return "Remote", "India", "Remote"
        
        loc_lower = loc_str.lower()
        for key, (city, state, loc_type) in CITY_MAPPING.items():
            if key in loc_lower:
                return city, state, loc_type
        return "Bengaluru", "Karnataka", "Tier-1 Hub"

    def parse_salary_and_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse salary strings, standardize to INR Lakhs per Annum (LPA), and handle missingness."""
        min_salaries = []
        max_salaries = []
        avg_salaries = []
        is_imputed = []

        for _, row in df.iterrows():
            min_raw = row.get("min_salary_lpa_raw")
            max_raw = row.get("max_salary_lpa_raw")
            sal_text = str(row.get("salary_raw", ""))

            # If pre-calculated float exists
            if pd.notna(min_raw) and pd.notna(max_raw) and float(min_raw) > 0:
                s_min = round(float(min_raw), 2)
                s_max = round(float(max_raw), 2)
                s_avg = round((s_min + s_max) / 2, 2)
                min_salaries.append(s_min)
                max_salaries.append(s_max)
                avg_salaries.append(s_avg)
                is_imputed.append(0)
            elif "$" in sal_text:
                # Handle USD
                nums = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", sal_text)]
                if len(nums) >= 2:
                    # Convert USD to INR LPA (Assume 1 USD = 84 INR)
                    s_min = round((nums[0] * 84) / 100000, 2)
                    s_max = round((nums[1] * 84) / 100000, 2)
                    s_avg = round((s_min + s_max) / 2, 2)
                    min_salaries.append(s_min)
                    max_salaries.append(s_max)
                    avg_salaries.append(s_avg)
                    is_imputed.append(0)
                else:
                    min_salaries.append(np.nan)
                    max_salaries.append(np.nan)
                    avg_salaries.append(np.nan)
                    is_imputed.append(1)
            else:
                min_salaries.append(np.nan)
                max_salaries.append(np.nan)
                avg_salaries.append(np.nan)
                is_imputed.append(1)

        df["min_salary_lpa"] = min_salaries
        df["max_salary_lpa"] = max_salaries
        df["avg_salary_lpa"] = avg_salaries
        df["is_salary_imputed"] = is_imputed

        # Impute missing salaries using Group Median by (Role, Experience Bracket)
        missing_count = df["avg_salary_lpa"].isna().sum()
        median_lookup = df.groupby(["role_category", "experience_raw"])["avg_salary_lpa"].transform("median")
        fallback_role_median = df.groupby("role_category")["avg_salary_lpa"].transform("median")

        df["avg_salary_lpa"] = df["avg_salary_lpa"].fillna(median_lookup).fillna(fallback_role_median).round(2)
        df["min_salary_lpa"] = df["min_salary_lpa"].fillna(df["avg_salary_lpa"] * 0.82).round(2)
        df["max_salary_lpa"] = df["max_salary_lpa"].fillna(df["avg_salary_lpa"] * 1.18).round(2)

        # Full INR annual values
        df["min_salary_inr"] = (df["min_salary_lpa"] * 100000).astype(int)
        df["max_salary_inr"] = (df["max_salary_lpa"] * 100000).astype(int)
        df["avg_salary_inr"] = (df["avg_salary_lpa"] * 100000).astype(int)

        self.log_decision(
            "Salary Normalization & Imputation",
            f"Normalized all salary representations to INR LPA. Imputed {missing_count} undisclosed postings using conditional median by Role and Experience bracket.",
            int(missing_count)
        )
        return df

    def parse_experience(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse experience strings into numeric bounds and standardized categories."""
        min_exps = []
        max_exps = []
        avg_exps = []
        brackets = []

        for _, row in df.iterrows():
            min_e = row.get("min_exp_years")
            max_e = row.get("max_exp_years")

            if pd.notna(min_e) and pd.notna(max_e):
                min_val = float(min_e)
                max_val = float(max_e)
            else:
                raw_exp = str(row.get("experience_raw", ""))
                nums = [float(x) for x in re.findall(r"\d+", raw_exp)]
                if len(nums) >= 2:
                    min_val = nums[0]
                    max_val = nums[1]
                elif len(nums) == 1:
                    min_val = nums[0]
                    max_val = nums[0] + 2
                else:
                    min_val = 2.0
                    max_val = 5.0

            avg_val = round((min_val + max_val) / 2, 1)
            min_exps.append(min_val)
            max_exps.append(max_val)
            avg_exps.append(avg_val)

            if avg_val <= 2.5:
                bracket = "0-2 Yrs (Entry Level)"
            elif avg_val <= 5.5:
                bracket = "3-5 Yrs (Mid Level)"
            elif avg_val <= 9.5:
                bracket = "6-9 Yrs (Senior)"
            else:
                bracket = "10+ Yrs (Lead / Principal)"
            brackets.append(bracket)

        df["experience_min"] = min_exps
        df["experience_max"] = max_exps
        df["experience_avg"] = avg_exps
        df["experience_bracket"] = brackets

        self.log_decision("Experience Standardization", "Parsed experience ranges and generated standardized 4-tier seniority brackets.", len(df))
        return df

    def normalize_skills(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize skill names and build clean list and string columns."""
        clean_skill_lists = []
        clean_skill_strings = []

        for _, row in df.iterrows():
            raw_s = str(row.get("skills_raw", ""))
            tokens = re.split(r"[,|\n;/]+", raw_s)
            normalized = []
            for t in tokens:
                cleaned = t.strip()
                if not cleaned:
                    continue
                cleaned_lower = cleaned.lower()
                canonical = SKILL_CANONICAL_MAP.get(cleaned_lower, cleaned.title())
                if canonical not in normalized:
                    normalized.append(canonical)
            clean_skill_lists.append(normalized)
            clean_skill_strings.append("; ".join(normalized))

        df["skills_list"] = clean_skill_lists
        df["skills"] = clean_skill_strings
        df["skill_count"] = df["skills_list"].apply(len)

        self.log_decision("Skill Normalization", "Mapped raw skill strings to canonical dictionary with consistent casing.", len(df))
        return df

    def run_pipeline(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Executes full cleaning, deduplication, and star-schema generation."""
        print("Reading raw dataset...")
        df_raw = pd.read_csv(self.raw_data_path)
        initial_count = len(df_raw)

        # 1. Deduplication
        df = df_raw.drop_duplicates(subset=["job_title", "company", "location_raw", "description_raw"]).copy()
        dedup_count = initial_count - len(df)
        self.log_decision("Deduplication", f"Identified and removed exact duplicates.", dedup_count)

        # 2. Location Normalization
        cities, states, loc_types = [], [], []
        for loc in df["location_raw"]:
            c, s, lt = self.parse_location(loc)
            cities.append(c)
            states.append(s)
            loc_types.append(lt)
        df["city"] = cities
        df["state"] = states
        df["location_type"] = loc_types
        df["country"] = "India"
        self.log_decision("Location Normalization", "Normalized all locations to standard Indian tech hubs (Bengaluru, NCR, Hyderabad, Pune, Mumbai, Chennai, Remote).", len(df))

        # 3. Experience Normalization
        df = self.parse_experience(df)

        # 4. Salary Normalization & Imputation
        df = self.parse_salary_and_impute(df)

        # 5. Skill Normalization
        df = self.normalize_skills(df)

        # 6. Dates & Time Intelligence Fields
        df["posted_date"] = pd.to_datetime(df["posted_date"])
        df["year"] = df["posted_date"].dt.year
        df["month"] = df["posted_date"].dt.month
        df["quarter"] = "Q" + df["posted_date"].dt.quarter.astype(str)
        df["month_name"] = df["posted_date"].dt.strftime("%b")
        df["year_month"] = df["posted_date"].dt.strftime("%Y-%m")
        df["day_of_week"] = df["posted_date"].dt.strftime("%A")

        # 7. Text Sanitization
        df["description_clean"] = df["description_raw"].apply(lambda x: re.sub(r"\s+", " ", str(x)).strip())

        # Save Main Cleaned Flat CSV
        cleaned_csv_path = os.path.join(self.output_dir, "cleaned_jobs.csv")
        df_flat_export = df.drop(columns=["skills_list"])
        df_flat_export.to_csv(cleaned_csv_path, index=False)
        print(f"Saved cleaned flat dataset: {cleaned_csv_path} ({len(df)} rows)")

        # -------------------------------------------------------------------------
        # Build Star-Schema Dimension & Fact Tables for SQL & Power BI
        # -------------------------------------------------------------------------
        # 1. Dim_Roles
        unique_roles = sorted(df["role_category"].unique())
        dim_roles = pd.DataFrame({
            "role_id": [f"R_{i+1:02d}" for i in range(len(unique_roles))],
            "role_category": unique_roles,
            "domain": ["Software Engineering" if "Software" in r else "Data & AI Analytics" for r in unique_roles]
        })
        role_id_map = dict(zip(dim_roles["role_category"], dim_roles["role_id"]))
        df["role_id"] = df["role_category"].map(role_id_map)

        # 2. Dim_Companies
        unique_companies = df[["company", "company_tier", "industry"]].drop_duplicates().reset_index(drop=True)
        unique_companies["company_id"] = [f"COMP_{i+1:04d}" for i in range(len(unique_companies))]
        dim_companies = unique_companies[["company_id", "company", "company_tier", "industry"]].rename(columns={"company": "company_name"})
        comp_id_map = dict(zip(unique_companies["company"], unique_companies["company_id"]))
        df["company_id"] = df["company"].map(comp_id_map)

        # 3. Dim_Locations
        unique_locs = df[["city", "state", "country", "location_type"]].drop_duplicates().reset_index(drop=True)
        unique_locs["location_id"] = [f"LOC_{i+1:03d}" for i in range(len(unique_locs))]
        dim_locations = unique_locs[["location_id", "city", "state", "country", "location_type"]]
        loc_id_map = {f"{r['city']}_{r['state']}": r['location_id'] for _, r in unique_locs.iterrows()}
        df["location_id"] = df.apply(lambda r: loc_id_map.get(f"{r['city']}_{r['state']}"), axis=1)

        # 4. Dim_Dates
        unique_dates = df[["posted_date", "year", "month", "quarter", "month_name", "year_month", "day_of_week"]].drop_duplicates().sort_values("posted_date").reset_index(drop=True)
        unique_dates["date_id"] = unique_dates["posted_date"].dt.strftime("%Y%m%d").astype(int)
        dim_dates = unique_dates[["date_id", "posted_date", "year", "quarter", "month", "month_name", "year_month", "day_of_week"]].rename(columns={"posted_date": "full_date"})
        df["date_id"] = df["posted_date"].dt.strftime("%Y%m%d").astype(int)

        # 5. Dim_Skills & Fact_Job_Skills
        all_skills_set = set()
        job_skill_pairs = []
        for _, r in df.iterrows():
            j_id = r["job_id"]
            for s in r["skills_list"]:
                all_skills_set.add(s)
                job_skill_pairs.append({"job_id": j_id, "skill_name": s})

        skill_names_sorted = sorted(list(all_skills_set))
        skill_category_lookup = {}
        for cat, s_list in SKILL_CATEGORIES.items():
            for s in s_list:
                skill_category_lookup[s] = cat

        dim_skills = pd.DataFrame({
            "skill_id": [f"SKILL_{i+1:04d}" for i in range(len(skill_names_sorted))],
            "skill_name": skill_names_sorted,
            "skill_category": [skill_category_lookup.get(s, "Other Technical Skills") for s in skill_names_sorted]
        })
        skill_id_map = dict(zip(dim_skills["skill_name"], dim_skills["skill_id"]))

        df_job_skills = pd.DataFrame(job_skill_pairs)
        df_job_skills["skill_id"] = df_job_skills["skill_name"].map(skill_id_map)
        fact_job_skills = df_job_skills[["job_id", "skill_id"]].drop_duplicates()

        # 6. Fact_Jobs
        fact_jobs = df[[
            "job_id", "job_title", "role_id", "company_id", "location_id", "date_id",
            "min_salary_lpa", "max_salary_lpa", "avg_salary_lpa",
            "min_salary_inr", "max_salary_inr", "avg_salary_inr",
            "experience_min", "experience_max", "experience_avg", "experience_bracket",
            "employment_type", "education_raw", "is_salary_imputed", "job_url", "source"
        ]].copy().rename(columns={"education_raw": "education_requirement"})

        # Export Star-Schema Tables to CSV
        schema_tables = {
            "dim_roles": dim_roles,
            "dim_companies": dim_companies,
            "dim_locations": dim_locations,
            "dim_dates": dim_dates,
            "dim_skills": dim_skills,
            "fact_jobs": fact_jobs,
            "fact_job_skills": fact_job_skills
        }

        for name, table in schema_tables.items():
            out_file = os.path.join(self.output_dir, f"{name}.csv")
            table.to_csv(out_file, index=False)
            print(f"Exported Star Schema table: {out_file} ({len(table)} rows)")

        # Save Cleaning Decision Log
        log_df = pd.DataFrame(self.cleaning_log)
        log_path = os.path.join(self.output_dir, "cleaning_decisions_log.csv")
        log_df.to_csv(log_path, index=False)
        print(f"Exported Cleaning Log: {log_path}")

        return df, schema_tables


if __name__ == "__main__":
    cleaner = TechJobDataCleaner()
    cleaner.run_pipeline()
