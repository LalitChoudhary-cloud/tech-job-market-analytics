# Power BI Star Schema Data Model Architecture

This document describes the relational Star-Schema design used in the **Tech Job Market & Salary Intelligence Platform (India)**.

---

## 1. Schema Overview & Architecture Diagram

```text
              +-------------------+
              |     dim_dates     |
              |-------------------|
              | date_id (PK)      |
              | full_date         |
              | year, quarter     |
              | month_name        |
              +---------+---------+
                        | (1)
                        |
                        | (*)
+-------------------+   |   +---------------------+   +---------------------+
|     dim_roles     |   |   |      fact_jobs      |   |    dim_locations    |
|-------------------|   |   |---------------------|   |---------------------|
| role_id (PK)      |<--+-->| job_id (PK)         |<--+-- location_id (PK)  |
| role_category     | (1)(*)| role_id (FK)        |(*)| city, state         |
| domain            |       | company_id (FK)     |   | location_type       |
+-------------------+       | location_id (FK)    |   +---------------------+
                            | date_id (FK)        |
+-------------------+       | min_salary_lpa      |   +---------------------+
|   dim_companies   |       | max_salary_lpa      |   |  fact_job_skills    |
|-------------------|       | avg_salary_lpa      |   |---------------------|
| company_id (PK)   |<------+ experience_min      |<--+-- job_id (FK)       |
| company_name      | (1)(*)| experience_max      |(*)|   skill_id (FK)     |
| company_tier      |       | experience_bracket  |   +----------+----------+
| industry          |       +---------------------+              | (*)
+-------------------+                                            |
                                                                 | (1)
                                                      +----------v----------+
                                                      |     dim_skills      |
                                                      |---------------------|
                                                      | skill_id (PK)       |
                                                      | skill_name          |
                                                      | skill_category      |
                                                      +---------------------+
```

---

## 2. Table Relationships & Cardinality Configuration

| From Table (Dimension) | Primary Key (PK) | To Table (Fact) | Foreign Key (FK) | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`dim_roles`** | `role_id` | `fact_jobs` | `role_id` | 1 to Many (1:*) | Single |
| **`dim_companies`** | `company_id` | `fact_jobs` | `company_id` | 1 to Many (1:*) | Single |
| **`dim_locations`** | `location_id` | `fact_jobs` | `location_id` | 1 to Many (1:*) | Single |
| **`dim_dates`** | `date_id` | `fact_jobs` | `date_id` | 1 to Many (1:*) | Single |
| **`fact_jobs`** | `job_id` | `fact_job_skills` | `job_id` | 1 to Many (1:*) | Both (Bi-directional) |
| **`dim_skills`** | `skill_id` | `fact_job_skills` | `skill_id` | 1 to Many (1:*) | Single |

---

## 3. Power BI 1-Click Import Instructions
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Folder** (or **Text/CSV**) and point to the `data/processed/` directory.
3. Select `dim_roles.csv`, `dim_companies.csv`, `dim_locations.csv`, `dim_dates.csv`, `dim_skills.csv`, `fact_jobs.csv`, `fact_job_skills.csv`.
4. Go to **Model View** and verify the 1-to-many relationships matching the table above.
5. In **Report View**, paste the DAX measures from `powerbi/dax_measures.dax` into a dedicated `_Measures` table.
