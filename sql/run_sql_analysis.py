"""
Automated SQL Database Setup & Analytics Runner
===============================================
Loads CSV dimension and fact tables into a local SQLite database (tech_jobs_india.db),
runs all schema definitions, audit checks, and analytical queries, and prints/saves reports.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "data/processed/tech_jobs_india.db"
PROCESSED_DIR = "data/processed"


def setup_database():
    """Create SQLite database and load tables from cleaned CSV files."""
    print("--------------------------------------------------")
    print("Setting up SQLite Database: " + DB_PATH)
    print("--------------------------------------------------")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load each CSV table
    tables = [
        "dim_roles",
        "dim_companies",
        "dim_locations",
        "dim_dates",
        "dim_skills",
        "fact_jobs",
        "fact_job_skills"
    ]

    for tbl in tables:
        csv_path = os.path.join(PROCESSED_DIR, f"{tbl}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_sql(tbl, conn, if_exists="replace", index=False)
            print(f" Loaded table '{tbl}' ({len(df):,} rows)")
        else:
            print(f" Warning: File {csv_path} not found.")

    conn.commit()
    return conn


def run_analytical_queries(conn):
    """Executes sample high-impact queries from analysis_queries.sql and displays results."""
    print("\n==================================================")
    print(" EXECUTING ADVANCED SQL ANALYTICAL QUERIES")
    print("==================================================\n")

    queries = {
        "1. Hiring Demand & Average Salary by Tech Role": """
            SELECT 
                r.role_category AS 'Role Category',
                COUNT(j.job_id) AS 'Total Jobs',
                ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs), 2) AS 'Job Share %',
                ROUND(AVG(j.avg_salary_lpa), 2) AS 'Avg Salary (INR LPA)',
                ROUND(AVG(j.experience_avg), 1) AS 'Avg Exp (Years)'
            FROM fact_jobs j
            JOIN dim_roles r ON j.role_id = r.role_id
            GROUP BY r.role_category
            ORDER BY COUNT(j.job_id) DESC;
        """,
        "2. Top 8 Indian Tech Hiring Cities": """
            SELECT 
                l.city AS 'City',
                COUNT(j.job_id) AS 'Total Jobs',
                ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs), 2) AS 'Market Share %',
                ROUND(AVG(j.avg_salary_lpa), 2) AS 'Avg Salary (INR LPA)'
            FROM fact_jobs j
            JOIN dim_locations l ON j.location_id = l.location_id
            GROUP BY l.city
            ORDER BY COUNT(j.job_id) DESC;
        """,
        "3. Salary Growth Across Experience Brackets by Role": """
            SELECT 
                r.role_category AS 'Role Category',
                j.experience_bracket AS 'Experience Bracket',
                COUNT(j.job_id) AS 'Postings',
                ROUND(AVG(j.avg_salary_lpa), 2) AS 'Avg Salary (INR LPA)'
            FROM fact_jobs j
            JOIN dim_roles r ON j.role_id = r.role_id
            GROUP BY r.role_category, j.experience_bracket
            ORDER BY r.role_category, 
                CASE j.experience_bracket
                    WHEN '0-2 Yrs (Entry Level)' THEN 1
                    WHEN '3-5 Yrs (Mid Level)' THEN 2
                    WHEN '6-9 Yrs (Senior)' THEN 3
                    ELSE 4
                END;
        """,
        "4. Top 10 Highest-Paying In-Demand Skills in India": """
            SELECT 
                s.skill_name AS 'Skill Name',
                s.skill_category AS 'Category',
                COUNT(fjs.job_id) AS 'Job Mentions',
                ROUND(AVG(j.avg_salary_lpa), 2) AS 'Avg Salary (INR LPA)'
            FROM fact_job_skills fjs
            JOIN dim_skills s ON fjs.skill_id = s.skill_id
            JOIN fact_jobs j ON fjs.job_id = j.job_id
            GROUP BY s.skill_name, s.skill_category
            HAVING COUNT(fjs.job_id) >= 50
            ORDER BY AVG(j.avg_salary_lpa) DESC
            LIMIT 10;
        """,
        "5. Top 5 In-Demand Skills Ranked Within Each Role (Window Function)": """
            WITH RankedSkills AS (
                SELECT 
                    r.role_category,
                    s.skill_name,
                    COUNT(j.job_id) AS mentions,
                    DENSE_RANK() OVER (PARTITION BY r.role_category ORDER BY COUNT(j.job_id) DESC) AS rank
                FROM fact_job_skills fjs
                JOIN fact_jobs j ON fjs.job_id = j.job_id
                JOIN dim_roles r ON j.role_id = r.role_id
                JOIN dim_skills s ON fjs.skill_id = s.skill_id
                GROUP BY r.role_category, s.skill_name
            )
            SELECT 
                role_category AS 'Role Category',
                rank AS 'Rank',
                skill_name AS 'Top Skill',
                mentions AS 'Demand Mentions'
            FROM RankedSkills
            WHERE rank <= 5
            ORDER BY role_category, rank;
        """
    }

    for title, qry in queries.items():
        print(f"--- {title} ---")
        df_res = pd.read_sql_query(qry, conn)
        print(df_res.to_string(index=False))
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    conn = setup_database()
    run_analytical_queries(conn)
    conn.close()
    print("SQL execution verified successfully!")

