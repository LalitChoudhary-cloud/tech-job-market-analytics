-- =============================================================================
-- Tech Job Market & Salary Intelligence Platform (India)
-- Relational Star Schema Database DDL (PostgreSQL / MySQL / SQLite Compatible)
-- =============================================================================

-- Drop tables if exists in reverse dependency order
DROP TABLE IF EXISTS fact_job_skills;
DROP TABLE IF EXISTS fact_jobs;
DROP TABLE IF EXISTS dim_skills;
DROP TABLE IF EXISTS dim_dates;
DROP TABLE IF EXISTS dim_locations;
DROP TABLE IF EXISTS dim_companies;
DROP TABLE IF EXISTS dim_roles;

-- 1. Dim_Roles: Core tech role categories
CREATE TABLE dim_roles (
    role_id VARCHAR(10) PRIMARY KEY,
    role_category VARCHAR(100) NOT NULL UNIQUE,
    domain VARCHAR(100) NOT NULL
);

-- 2. Dim_Companies: Organizations hiring tech talent
CREATE TABLE dim_companies (
    company_id VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    company_tier VARCHAR(50) NOT NULL,
    industry VARCHAR(100) NOT NULL
);

-- 3. Dim_Locations: Indian tech hubs & geographic tiers
CREATE TABLE dim_locations (
    location_id VARCHAR(10) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'India',
    location_type VARCHAR(50) NOT NULL
);

-- 4. Dim_Dates: Calendar dimension for time-intelligence analysis
CREATE TABLE dim_dates (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter VARCHAR(5) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    day_of_week VARCHAR(15) NOT NULL
);

-- 5. Dim_Skills: Normalized technical and analytical skills
CREATE TABLE dim_skills (
    skill_id VARCHAR(20) PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(100) NOT NULL
);

-- 6. Fact_Jobs: Central fact table containing job postings, metrics, and compensation
CREATE TABLE fact_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    job_title VARCHAR(200) NOT NULL,
    role_id VARCHAR(10) NOT NULL,
    company_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(10) NOT NULL,
    date_id INTEGER NOT NULL,
    min_salary_lpa NUMERIC(6, 2),
    max_salary_lpa NUMERIC(6, 2),
    avg_salary_lpa NUMERIC(6, 2) NOT NULL,
    min_salary_inr BIGINT,
    max_salary_inr BIGINT,
    avg_salary_inr BIGINT NOT NULL,
    experience_min NUMERIC(4, 1),
    experience_max NUMERIC(4, 1),
    experience_avg NUMERIC(4, 1) NOT NULL,
    experience_bracket VARCHAR(50) NOT NULL,
    employment_type VARCHAR(50),
    education_requirement VARCHAR(255),
    is_salary_imputed INTEGER DEFAULT 0,
    job_url VARCHAR(255),
    source VARCHAR(100),
    FOREIGN KEY (role_id) REFERENCES dim_roles(role_id),
    FOREIGN KEY (company_id) REFERENCES dim_companies(company_id),
    FOREIGN KEY (location_id) REFERENCES dim_locations(location_id),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)
);

-- 7. Fact_Job_Skills: Bridge / associative fact table modeling Many-to-Many job skills
CREATE TABLE fact_job_skills (
    job_id VARCHAR(50) NOT NULL,
    skill_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES fact_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES dim_skills(skill_id) ON DELETE CASCADE
);

-- Indexes for high-performance analytical queries
CREATE INDEX idx_jobs_role_id ON fact_jobs(role_id);
CREATE INDEX idx_jobs_company_id ON fact_jobs(company_id);
CREATE INDEX idx_jobs_location_id ON fact_jobs(location_id);
CREATE INDEX idx_jobs_date_id ON fact_jobs(date_id);
CREATE INDEX idx_jobs_avg_salary ON fact_jobs(avg_salary_lpa);
CREATE INDEX idx_jobs_exp_bracket ON fact_jobs(experience_bracket);
CREATE INDEX idx_job_skills_skill_id ON fact_job_skills(skill_id);
