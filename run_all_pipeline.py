"""
Master Pipeline Orchestration Script
====================================
Runs the entire Tech Job Market & Salary Intelligence pipeline in one command:
  1. Data Generation / Scraping (6,500 records)
  2. Data Engineering & Cleaning (Star-Schema generation)
  3. SQL Database Setup & Analytical Query Execution
  4. Jupyter Notebooks Generation & Verification
"""

import subprocess
import sys


def run_step(step_name, command):
    print("\n" + "=" * 60)
    print(f"  RUNNING STEP: {step_name}")
    print("=" * 60)
    res = subprocess.run(command, shell=True)
    if res.returncode != 0:
        print(f" Error in step: {step_name}")
        sys.exit(res.returncode)
    print(f" Step completed successfully: {step_name}\n")


def main():
    print("""
    ============================================================
      Tech Job Market & Salary Intelligence Platform (India)
      End-to-End Execution Pipeline
    ============================================================
    """)
    
    # Step 1: Scrape & Generate Raw Dataset
    run_step("1. Data Generation / Scraping", "python scraping/generate_dataset.py --records 6500")

    # Step 2: Clean Data & Build Star Schema
    run_step("2. Data Preprocessing & Star Schema Modeling", "python src/preprocessing/cleaner.py")

    # Step 3: Setup SQLite Database & Run Advanced SQL Queries
    run_step("3. SQL Database Loader & Analytical Queries", "python sql/run_sql_analysis.py")

    # Step 4: Generate All 4 Jupyter Notebooks
    run_step("4. Jupyter Notebooks Generation", "python notebooks/generate_notebooks.py")

    # Step 5: Execute and Populate Notebook Outputs
    run_step("5. Execute & Populate Notebook Outputs", "python notebooks/execute_and_populate_notebooks.py")

    print("""
    ============================================================
       ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!
    ============================================================
    Next Actions:
      1. Launch the interactive BI Web Companion:
         streamlit run src/app.py
         
      2. Open Jupyter Notebooks:
         jupyter notebook notebooks/
         
      3. View Executive Insights:
         reports/business_insights.md
    ============================================================
    """)


if __name__ == "__main__":
    main()
