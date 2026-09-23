-- =============================================================================
-- Tech Job Market & Salary Intelligence Platform (India)
-- Business Analysis SQL Queries
-- Comprehensive, modular queries written with easy-to-follow comments,
-- CTEs (Common Table Expressions), Window Functions, and Aggregations.
-- =============================================================================

-- =============================================================================
-- SECTION 1: JOB MARKET OVERVIEW
-- =============================================================================

-- Query 1.1: Total Job Postings and Share % by Role Category
-- Purpose: Discover which tech role has the highest hiring demand in India.
SELECT 
    r.role_category,
    COUNT(j.job_id) AS total_jobs,
    ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs), 2) AS job_share_pct,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa,
    ROUND(AVG(j.experience_avg), 1) AS avg_experience_years
FROM fact_jobs j
JOIN dim_roles r ON j.role_id = r.role_id
GROUP BY r.role_category
ORDER BY total_jobs DESC;


-- Query 1.2: Top 10 Hiring Companies Across India
-- Purpose: Identify which enterprises and startups are actively recruiting tech talent.
SELECT 
    c.company_name,
    c.company_tier,
    c.industry,
    COUNT(j.job_id) AS total_openings,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_offered_salary_lpa
FROM fact_jobs j
JOIN dim_companies c ON j.company_id = c.company_id
GROUP BY c.company_name, c.company_tier, c.industry
ORDER BY total_openings DESC
LIMIT 10;


-- Query 1.3: Geographic Job Demand: Jobs by Indian Tech City
-- Purpose: Understand which Indian tech hubs dominate tech hiring.
SELECT 
    l.city,
    l.state,
    COUNT(j.job_id) AS total_jobs,
    ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs), 2) AS market_share_pct,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa
FROM fact_jobs j
JOIN dim_locations l ON j.location_id = l.location_id
GROUP BY l.city, l.state
ORDER BY total_jobs DESC;


-- Query 1.4: Monthly Hiring Trend and Month-over-Month (MoM) Growth using LAG() Window Function
-- Purpose: Track how job posting volumes fluctuate over time.
WITH MonthlyHiring AS (
    SELECT 
        d.year_month,
        COUNT(j.job_id) AS monthly_job_count
    FROM fact_jobs j
    JOIN dim_dates d ON j.date_id = d.date_id
    GROUP BY d.year_month
)
SELECT 
    year_month,
    monthly_job_count,
    LAG(monthly_job_count, 1) OVER (ORDER BY year_month) AS previous_month_jobs,
    ROUND(
        (monthly_job_count - LAG(monthly_job_count, 1) OVER (ORDER BY year_month)) * 100.0 
        / LAG(monthly_job_count, 1) OVER (ORDER BY year_month), 
        2
    ) AS mom_growth_pct
FROM MonthlyHiring
ORDER BY year_month;


-- =============================================================================
-- SECTION 2: SALARY INTELLIGENCE
-- =============================================================================

-- Query 2.1: Salary Summary (Min, Max, Avg, Range) by Role
-- Purpose: Compare earning potential across SDE, Data Analyst, Data Scientist, and AI/ML.
SELECT 
    r.role_category,
    COUNT(j.job_id) AS sample_size,
    ROUND(MIN(j.min_salary_lpa), 2) AS lowest_min_lpa,
    ROUND(AVG(j.avg_salary_lpa), 2) AS average_salary_lpa,
    ROUND(MAX(j.max_salary_lpa), 2) AS highest_max_lpa,
    ROUND(MAX(j.avg_salary_lpa) - MIN(j.avg_salary_lpa), 2) AS salary_spread_lpa
FROM fact_jobs j
JOIN dim_roles r ON j.role_id = r.role_id
GROUP BY r.role_category
ORDER BY average_salary_lpa DESC;


-- Query 2.2: Salary Progression Across Experience Brackets
-- Purpose: Analyze how compensation scales with career progression in India.
SELECT 
    r.role_category,
    j.experience_bracket,
    COUNT(j.job_id) AS job_count,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa,
    ROUND(MIN(j.avg_salary_lpa), 2) AS min_avg_lpa,
    ROUND(MAX(j.avg_salary_lpa), 2) AS max_avg_lpa
FROM fact_jobs j
JOIN dim_roles r ON j.role_id = r.role_id
GROUP BY r.role_category, j.experience_bracket
ORDER BY r.role_category, 
    CASE j.experience_bracket
        WHEN '0-2 Yrs (Entry Level)' THEN 1
        WHEN '3-5 Yrs (Mid Level)' THEN 2
        WHEN '6-9 Yrs (Senior)' THEN 3
        WHEN '10+ Yrs (Lead / Principal)' THEN 4
        ELSE 5
    END;


-- Query 2.3: Salary Comparison by Location and Role
-- Purpose: Discover which cities offer the highest pay for each role.
SELECT 
    l.city,
    r.role_category,
    COUNT(j.job_id) AS job_count,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa,
    RANK() OVER (PARTITION BY r.role_category ORDER BY AVG(j.avg_salary_lpa) DESC) AS city_rank_for_role
FROM fact_jobs j
JOIN dim_locations l ON j.location_id = l.location_id
JOIN dim_roles r ON j.role_id = r.role_id
GROUP BY l.city, r.role_category
ORDER BY r.role_category, avg_salary_lpa DESC;


-- Query 2.4: Top 15 Highest Paying Skills in India
-- Purpose: Find high-value skills that correlate with top salary tiers.
SELECT 
    s.skill_name,
    s.skill_category,
    COUNT(fjs.job_id) AS job_mentions,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa,
    ROUND(MIN(j.avg_salary_lpa), 2) AS min_salary_lpa,
    ROUND(MAX(j.avg_salary_lpa), 2) AS max_salary_lpa
FROM fact_job_skills fjs
JOIN dim_skills s ON fjs.skill_id = s.skill_id
JOIN fact_jobs j ON fjs.job_id = j.job_id
GROUP BY s.skill_name, s.skill_category
HAVING COUNT(fjs.job_id) >= 50 -- Filter for skills with meaningful market presence
ORDER BY avg_salary_lpa DESC
LIMIT 15;


-- =============================================================================
-- SECTION 3: SKILLS INTELLIGENCE
-- =============================================================================

-- Query 3.1: Top 5 In-Demand Skills for Each Tech Role using DENSE_RANK()
-- Purpose: Determine what specific skills job seekers must master for each role.
WITH RankedRoleSkills AS (
    SELECT 
        r.role_category,
        s.skill_name,
        COUNT(j.job_id) AS skill_demand_count,
        ROUND(COUNT(j.job_id) * 100.0 / (SELECT COUNT(*) FROM fact_jobs fj WHERE fj.role_id = r.role_id), 1) AS role_penetration_pct,
        DENSE_RANK() OVER (PARTITION BY r.role_category ORDER BY COUNT(j.job_id) DESC) AS rank_in_role
    FROM fact_job_skills fjs
    JOIN fact_jobs j ON fjs.job_id = j.job_id
    JOIN dim_roles r ON j.role_id = r.role_id
    JOIN dim_skills s ON fjs.skill_id = s.skill_id
    GROUP BY r.role_category, r.role_id, s.skill_name
)
SELECT 
    role_category,
    rank_in_role,
    skill_name,
    skill_demand_count,
    role_penetration_pct
FROM RankedRoleSkills
WHERE rank_in_role <= 5
ORDER BY role_category, rank_in_role;


-- Query 3.2: Universal Skills (Common Across All 4 Roles)
-- Purpose: Find transversal skills that are valued everywhere in tech.
SELECT 
    s.skill_name,
    COUNT(DISTINCT j.role_id) AS roles_present_in,
    COUNT(j.job_id) AS total_mentions,
    ROUND(AVG(j.avg_salary_lpa), 2) AS overall_avg_salary_lpa
FROM fact_job_skills fjs
JOIN fact_jobs j ON fjs.job_id = j.job_id
JOIN dim_skills s ON fjs.skill_id = s.skill_id
GROUP BY s.skill_name
HAVING COUNT(DISTINCT j.role_id) = 4 -- Present in all 4 roles
ORDER BY total_mentions DESC;


-- Query 3.3: Skill Demand by Seniority Bracket
-- Purpose: Reveal how technical expectations evolve from Junior to Lead roles.
SELECT 
    j.experience_bracket,
    s.skill_name,
    COUNT(j.job_id) AS demand_count,
    ROW_NUMBER() OVER (PARTITION BY j.experience_bracket ORDER BY COUNT(j.job_id) DESC) AS skill_rank_in_bracket
FROM fact_job_skills fjs
JOIN fact_jobs j ON fjs.job_id = j.job_id
JOIN dim_skills s ON fjs.skill_id = s.skill_id
GROUP BY j.experience_bracket, s.skill_name
ORDER BY j.experience_bracket, demand_count DESC;


-- =============================================================================
-- SECTION 4: EXPERIENCE INTELLIGENCE
-- =============================================================================

-- Query 4.1: Experience Distribution Across Roles
-- Purpose: Assess which career stages have the most openings per role.
SELECT 
    r.role_category,
    j.experience_bracket,
    COUNT(j.job_id) AS total_jobs,
    ROUND(COUNT(j.job_id) * 100.0 / SUM(COUNT(j.job_id)) OVER(PARTITION BY r.role_category), 2) AS pct_within_role
FROM fact_jobs j
JOIN dim_roles r ON j.role_id = r.role_id
GROUP BY r.role_category, j.experience_bracket
ORDER BY r.role_category, total_jobs DESC;


-- Query 4.2: Correlation Analysis Prep: Experience vs Salary by Industry Tier
-- Purpose: Understand how salary accelerates with experience in Product Startups vs IT Services.
SELECT 
    c.company_tier,
    j.experience_bracket,
    COUNT(j.job_id) AS total_openings,
    ROUND(AVG(j.avg_salary_lpa), 2) AS avg_salary_lpa,
    ROUND(AVG(j.experience_avg), 1) AS avg_experience_years
FROM fact_jobs j
JOIN dim_companies c ON j.company_id = c.company_id
GROUP BY c.company_tier, j.experience_bracket
ORDER BY c.company_tier, avg_experience_years;
