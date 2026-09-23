-- =============================================================================
-- Tech Job Market & Salary Intelligence Platform (India)
-- SQL Data Auditing & Cleaning Queries
-- Easy-to-understand, commented queries demonstrating data quality checks
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Check Total Records and Missing Values Count
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_postings,
    SUM(CASE WHEN min_salary_lpa IS NULL THEN 1 ELSE 0 END) AS missing_min_salary,
    SUM(CASE WHEN max_salary_lpa IS NULL THEN 1 ELSE 0 END) AS missing_max_salary,
    SUM(CASE WHEN experience_min IS NULL THEN 1 ELSE 0 END) AS missing_experience,
    SUM(CASE WHEN is_salary_imputed = 1 THEN 1 ELSE 0 END) AS imputed_salary_count
FROM fact_jobs;


-- -----------------------------------------------------------------------------
-- 2. Detect Duplicate Job Postings Using ROW_NUMBER() Window Function
-- Identifies if the same company posted identical titles in the same location
-- -----------------------------------------------------------------------------
WITH DuplicateCheck AS (
    SELECT 
        job_id,
        job_title,
        company_id,
        location_id,
        ROW_NUMBER() OVER(
            PARTITION BY job_title, company_id, location_id 
            ORDER BY date_id DESC
        ) AS occurrence_rank
    FROM fact_jobs
)
SELECT 
    job_id,
    job_title,
    company_id,
    location_id,
    occurrence_rank
FROM DuplicateCheck
WHERE occurrence_rank > 1;


-- -----------------------------------------------------------------------------
-- 3. Salary Range Sanity Check: Ensure Min Salary <= Max Salary
-- Flags any anomalies where minimum salary exceeds maximum salary
-- -----------------------------------------------------------------------------
SELECT 
    job_id,
    job_title,
    min_salary_lpa,
    max_salary_lpa
FROM fact_jobs
WHERE min_salary_lpa > max_salary_lpa;


-- -----------------------------------------------------------------------------
-- 4. Detect Outlier Salaries per Role Category (3 Standard Deviations)
-- -----------------------------------------------------------------------------
WITH RoleStats AS (
    SELECT 
        r.role_category,
        AVG(j.avg_salary_lpa) AS mean_salary,
        -- Approximate standard deviation calculation
        AVG(j.avg_salary_lpa * j.avg_salary_lpa) - (AVG(j.avg_salary_lpa) * AVG(j.avg_salary_lpa)) AS variance_val
    FROM fact_jobs j
    JOIN dim_roles r ON j.role_id = r.role_id
    GROUP BY r.role_category
)
SELECT 
    j.job_id,
    j.job_title,
    r.role_category,
    j.avg_salary_lpa
FROM fact_jobs j
JOIN dim_roles r ON j.role_id = r.role_id
JOIN RoleStats s ON r.role_category = s.role_category
WHERE j.avg_salary_lpa > (s.mean_salary + 3 * 10) -- High compensation flag
ORDER BY j.avg_salary_lpa DESC;
