"""
India Tech Job Market Dataset Engine & Scaled Pipeline
======================================================
Synthesizes a statistically rigorous, realistic dataset of 6,500+ Indian Tech Job Postings
across SDE, Data Analyst, Data Scientist, and AI/ML Engineer roles.
Reflects genuine Indian salary structures (in INR LPA), tech hubs (Bengaluru, Hyderabad, Pune, NCR, Mumbai, Chennai),
company tiers (Indian Startups/Unicorns, GCCs, Analytics consultancies, IT giants), and skill distributions.
"""

import argparse
import os
import random
import re
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Fix seed for reproducibility
np.random.seed(42)
random.seed(42)

TARGET_ROLES = [
    "Software Development Engineer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer"
]

COMPANIES_BY_TIER = {
    "Product_Unicorn": [
        "Flipkart", "Swiggy", "Zomato", "PhonePe", "Razorpay", "CRED", "Meesho",
        "Zepto", "Paytm", "Ola", "Groww", "Urban Company", "InMobi", "Postman",
        "Dream11", "BrowserStack", "Chargebee", "Licious", "Zerodha"
    ],
    "Global_GCC": [
        "Amazon India", "Microsoft India", "Google India", "Walmart Global Tech",
        "Adobe India", "Uber India", "Salesforce India", "JPMorgan Chase India",
        "Morgan Stanley India", "Goldman Sachs India", "Cisco India", "Target India",
        "Intuit India", "Oracle India", "PayPal India", "Visa India", "Qualcomm India"
    ],
    "Analytics_Specialist": [
        "Fractal Analytics", "Tiger Analytics", "Mu Sigma", "LatentView Analytics",
        "Quantiphi", "TheMathCompany", "Tredence", "Course5 Intelligence",
        "Absolutdata (Infogain)", "ZS Associates India", "EXL Analytics"
    ],
    "IT_Consulting_Enterprise": [
        "TCS", "Infosys", "Wipro", "HCLTech", "Tech Mahindra", "LTIMindtree",
        "Accenture India", "Cognizant India", "Capgemini India", "Deloitte India",
        "PwC India", "EY India", "KPMG India"
    ]
}

LOCATIONS_INDIA = [
    {"city": "Bengaluru", "state": "Karnataka", "weight": 0.38, "mult": 1.16, "raw_variants": ["Bengaluru", "Bangalore", "Bengaluru / Bangalore", "Bangalore Rural, Karnataka"]},
    {"city": "Hyderabad", "state": "Telangana", "weight": 0.20, "mult": 1.04, "raw_variants": ["Hyderabad", "Hyderabad / Secunderabad", "HITEC City, Hyderabad"]},
    {"city": "Pune", "state": "Maharashtra", "weight": 0.13, "mult": 0.96, "raw_variants": ["Pune", "Hinjawadi, Pune", "Pune / Pimpri-Chinchwad"]},
    {"city": "Delhi NCR", "state": "Haryana/UP", "weight": 0.14, "mult": 1.10, "raw_variants": ["Gurugram", "Gurgaon", "Noida", "Delhi / NCR", "Cyber City, Gurugram"]},
    {"city": "Mumbai", "state": "Maharashtra", "weight": 0.06, "mult": 1.08, "raw_variants": ["Mumbai", "Navi Mumbai", "Bandra-Kurla Complex, Mumbai"]},
    {"city": "Chennai", "state": "Tamil Nadu", "weight": 0.05, "mult": 0.93, "raw_variants": ["Chennai", "OMR, Chennai", "Chennai South"]},
    {"city": "Remote", "state": "India", "weight": 0.04, "mult": 1.07, "raw_variants": ["Remote (India)", "Work From Home - India", "Remote / Any Location"]}
]

ROLE_CONFIGS = {
    "Software Development Engineer": {
        "title_templates": [
            "Software Development Engineer I (SDE-1)", "Software Development Engineer II (SDE-2)",
            "Senior SDE (SDE-3)", "Full Stack Developer", "Backend Software Engineer",
            "Frontend Engineer (React/TypeScript)", "Java Backend Developer",
            "Lead Software Engineer", "Staff Software Engineer", "Python/Go Developer"
        ],
        "core_skills": ["Python", "Java", "C++", "Go", "Spring Boot", "Node.js", "React", "Docker", "Kubernetes", "AWS", "SQL", "Redis", "Microservices", "Kafka", "System Design", "Git", "CI/CD", "REST APIs", "GraphQL", "PostgreSQL"],
        "sal_base": {"0-2": (6.5, 14.0), "3-5": (14.0, 28.0), "6-9": (28.0, 48.0), "10+": (45.0, 75.0)},
        "desc_snippets": [
            "Architecting resilient microservices using Java/Go and Spring Boot deployed on AWS EKS.",
            "Building high-throughput real-time streaming pipelines with Apache Kafka, Redis, and PostgreSQL.",
            "Designing scalable frontend applications in React, Next.js, and TypeScript with state-of-the-art UX.",
            "Mentoring junior engineers, conducting rigorous code reviews, and upholding solid system design principles."
        ]
    },
    "Data Analyst": {
        "title_templates": [
            "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst",
            "Lead BI Analyst", "Marketing Data Analyst", "Product Data Analyst",
            "Operations Analytics Specialist", "Data Analytics Consultant", "SQL & Power BI Developer"
        ],
        "core_skills": ["SQL", "Power BI", "Tableau", "Excel", "Python", "DAX", "Pandas", "Statistics", "Data Modeling", "ETL", "Snowflake", "BigQuery", "Looker", "Business Analysis", "Data Storytelling", "A/B Testing", "MySQL", "Alteryx"],
        "sal_base": {"0-2": (4.5, 8.5), "3-5": (8.5, 17.5), "6-9": (17.0, 30.0), "10+": (28.0, 45.0)},
        "desc_snippets": [
            "Developing interactive Power BI & Tableau dashboards with complex DAX measures for executive leadership.",
            "Authoring optimized SQL queries, CTEs, and window functions to extract insights from multi-terabyte data warehouses.",
            "Partnering with product and operations teams to define core KPIs, track user retention, and run cohort analyses.",
            "Automating repetitive data reporting pipelines using Python (Pandas/NumPy) and scheduled cron jobs."
        ]
    },
    "Data Scientist": {
        "title_templates": [
            "Data Scientist", "Senior Data Scientist", "Lead Data Scientist",
            "Applied Data Scientist", "Staff Data Scientist", "Data Science Consultant",
            "Quantitative Data Scientist", "Principal Data Scientist"
        ],
        "core_skills": ["Python", "R", "SQL", "Machine Learning", "Scikit-Learn", "Pandas", "NumPy", "Statistics", "A/B Testing", "XGBoost", "Deep Learning", "NLP", "PyTorch", "Feature Engineering", "Spark", "MLflow", "BigQuery", "Hypothesis Testing", "Data Visualization"],
        "sal_base": {"0-2": (7.0, 14.5), "3-5": (14.5, 27.0), "6-9": (26.0, 50.0), "10+": (45.0, 68.0)},
        "desc_snippets": [
            "Building predictive ML models (LightGBM, XGBoost, Random Forest) for customer churn, LTV, and pricing optimization.",
            "Designing statistical experimentation frameworks, hypothesis testing, and power analysis for A/B product rollouts.",
            "Deploying ML inference pipelines to production using FastAPI, Docker, and MLflow tracking.",
            "Extracting actionable business intelligence from complex unstructured and semi-structured datasets."
        ]
    },
    "AI/ML Engineer": {
        "title_templates": [
            "AI/ML Engineer", "Machine Learning Engineer", "Senior ML Engineer",
            "Generative AI Engineer", "LLM Application Engineer", "Lead AI Engineer",
            "Computer Vision Engineer", "NLP / AI Research Engineer", "MLOps Engineer"
        ],
        "core_skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Docker", "Kubernetes", "LangChain", "Transformers", "LLMs", "NLP", "Computer Vision", "AWS SageMaker", "MLflow", "ONNX", "Vector Databases", "FastAPI", "C++", "Fine-Tuning", "RAG Systems"],
        "sal_base": {"0-2": (8.5, 17.0), "3-5": (17.0, 35.0), "6-9": (32.0, 58.0), "10+": (52.0, 85.0)},
        "desc_snippets": [
            "Developing Generative AI & RAG pipelines leveraging LangChain, LlamaIndex, Vector DBs (Milvus/Pinecone), and OpenAI/Open-Source LLMs.",
            "Architecting end-to-end MLOps platforms for automated model training, quantization, validation, and containerized deployment.",
            "Fine-tuning transformer-based LLMs and diffusion models with PyTorch, DeepSpeed, and LoRA on GPU clusters.",
            "Building ultra-low latency inference microservices using C++, ONNX Runtime, TensorRT, and FastAPI."
        ]
    }
}

INDUSTRIES = [
    "E-Commerce & Quick Commerce",
    "FinTech & Digital Banking",
    "SaaS & Enterprise Software",
    "Information Technology & Services",
    "Healthcare & HealthTech",
    "EdTech & Consumer Internet",
    "Logistics, Mobility & Supply Chain",
    "Analytics & Consulting Services"
]

EDUCATIONS = [
    "B.Tech / B.E. in Computer Science, IT or related engineering disciplines",
    "B.Tech / M.Tech / MCA in Computer Science, Data Science, or Mathematics",
    "Bachelor's / Master's degree in Statistics, Mathematics, Economics, or Analytics",
    "B.Sc / BCA / MCA / M.Sc in Computing or Information Systems",
    "Master's / Ph.D. in Computer Science, AI, or Quantitative Sciences"
]

SOURCES = [
    "Foundit India", "TimesJobs", "Instahyre", "Hirist",
    "Arbeitnow Feed", "RemoteOK Feed", "Naukri Public Feed", "Hasjob"
]


def generate_raw_dataset(num_records: int = 6500, output_dir: str = "data/raw") -> pd.DataFrame:
    """
    Generates a high-fidelity Indian tech job market raw dataset with realistic anomalies.
    
    Parameters:
        num_records (int): Total number of job postings to generate. Default 6500.
        output_dir (str): Directory where CSV and JSON raw files are saved.
    
    Returns:
        pd.DataFrame: Generated raw dataset.
    """
    os.makedirs(output_dir, exist_ok=True)
    records = []

    start_date = datetime(2025, 9, 1)
    end_date = datetime(2026, 9, 20)
    total_days = (end_date - start_date).days

    # Role distribution weights: SDE (35%), Data Analyst (28%), Data Scientist (20%), AI/ML (17%)
    role_choices = [
        ("Software Development Engineer", 0.35),
        ("Data Analyst", 0.28),
        ("Data Scientist", 0.20),
        ("AI/ML Engineer", 0.17)
    ]
    roles, role_probs = zip(*role_choices)

    # Location distribution
    loc_cities = [loc["city"] for loc in LOCATIONS_INDIA]
    loc_weights = [loc["weight"] for loc in LOCATIONS_INDIA]
    loc_map = {loc["city"]: loc for loc in LOCATIONS_INDIA}

    # Company tiers distribution: IT Consulting (34%), Product Unicorns (29%), Global GCCs (22%), Analytics (15%)
    tier_choices = [
        ("IT_Consulting_Enterprise", 0.34),
        ("Product_Unicorn", 0.29),
        ("Global_GCC", 0.22),
        ("Analytics_Specialist", 0.15)
    ]
    tiers, tier_probs = zip(*tier_choices)
    tier_multipliers = {
        "Product_Unicorn": 1.22,
        "Global_GCC": 1.30,
        "Analytics_Specialist": 1.00,
        "IT_Consulting_Enterprise": 0.82
    }

    # Experience level distribution: 0-2 (24%), 3-5 (38%), 6-9 (26%), 10+ (12%)
    exp_brackets = ["0-2", "3-5", "6-9", "10+"]
    exp_probs = [0.24, 0.38, 0.26, 0.12]

    for idx in range(1, num_records + 1):
        role_category = random.choices(roles, weights=role_probs)[0]
        config = ROLE_CONFIGS[role_category]

        # Select location
        selected_city_name = random.choices(loc_cities, weights=loc_weights)[0]
        loc_info = loc_map[selected_city_name]
        raw_location = random.choice(loc_info["raw_variants"])

        # Select company tier & company
        tier = random.choices(tiers, weights=tier_probs)[0]
        company = random.choice(COMPANIES_BY_TIER[tier])

        # Experience
        exp_bracket = random.choices(exp_brackets, weights=exp_probs)[0]
        if exp_bracket == "0-2":
            min_exp = random.randint(0, 1)
            max_exp = min_exp + random.randint(1, 2)
        elif exp_bracket == "3-5":
            min_exp = random.randint(3, 4)
            max_exp = min_exp + random.randint(1, 2)
        elif exp_bracket == "6-9":
            min_exp = random.randint(6, 7)
            max_exp = min_exp + random.randint(2, 3)
        else:
            min_exp = random.randint(10, 12)
            max_exp = min_exp + random.randint(3, 5)

        # Experience raw formats
        exp_style = random.choice(["range_yrs", "to_years", "min_only", "plus_yrs", "clean"])
        if exp_style == "range_yrs":
            raw_experience = f"{min_exp} - {max_exp} Yrs"
        elif exp_style == "to_years":
            raw_experience = f"{min_exp} to {max_exp} Years"
        elif exp_style == "min_only":
            raw_experience = f"Min {min_exp}+ yrs"
        elif exp_style == "plus_yrs":
            raw_experience = f"{min_exp}+ Years"
        else:
            raw_experience = f"{min_exp}-{max_exp} yrs"

        # Base Salary Calculation in INR LPA
        base_low, base_high = config["sal_base"][exp_bracket]
        loc_mult = loc_info["mult"]
        tier_mult = tier_multipliers[tier]

        # Add random variation
        jitter = np.random.normal(1.0, 0.08)
        calculated_min_lpa = round(max(2.8, base_low * loc_mult * tier_mult * jitter), 2)
        spread = np.random.uniform(1.3, 1.8)
        calculated_max_lpa = round(max(calculated_min_lpa + 1.5, base_high * loc_mult * tier_mult * jitter * spread * 0.7), 2)
        avg_lpa = round((calculated_min_lpa + calculated_max_lpa) / 2, 2)

        # Realistic salary anomalies / missingness (~16% missing salary like real portals)
        salary_is_disclosed = random.random() > 0.16
        if salary_is_disclosed:
            sal_format = random.choice(["lpa_range", "inr_full", "inr_pa", "single_lpa", "usd_remote"])
            if sal_format == "lpa_range":
                raw_salary = f"{calculated_min_lpa} - {calculated_max_lpa} LPA"
            elif sal_format == "inr_full":
                raw_salary = f"₹{int(calculated_min_lpa * 100000):,} - ₹{int(calculated_max_lpa * 100000):,} P.A."
            elif sal_format == "inr_pa":
                raw_salary = f"₹ {calculated_min_lpa:.1f} Lakhs - {calculated_max_lpa:.1f} Lakhs"
            elif sal_format == "single_lpa":
                raw_salary = f"₹ {avg_lpa:.1f} LPA"
            else:
                # 3% USD remote contracts
                usd_min = int(calculated_min_lpa * 1200)
                usd_max = int(calculated_max_lpa * 1200)
                raw_salary = f"${usd_min:,} - ${usd_max:,} / year"
        else:
            raw_salary = random.choice(["Not Disclosed", "Competitive", "Best in Industry", None, "Confidential"])
            calculated_min_lpa = None
            calculated_max_lpa = None

        # Title
        job_title = random.choice(config["title_templates"])
        # Add tech qualifiers sometimes
        if role_category == "Software Development Engineer" and random.random() > 0.6:
            job_title = f"{random.choice(['Senior', 'Lead', 'Principal', 'Staff'])} {job_title}"

        # Skills (sample 4 to 8 skills with high probability of core skills)
        num_skills = random.randint(4, 8)
        sampled_skills = random.sample(config["core_skills"], min(num_skills, len(config["core_skills"])))
        # Add 1 common crossover skill sometimes
        crossover_skills = ["Python", "SQL", "Git", "Docker", "AWS", "Communication", "Problem Solving"]
        sampled_skills.append(random.choice(crossover_skills))
        sampled_skills = list(set(sampled_skills))
        raw_skills = ", ".join(sampled_skills) if random.random() > 0.1 else " | ".join(sampled_skills)

        # Job Description construction
        snippets = random.sample(config["desc_snippets"], 2)
        desc_text = (
            f"We are seeking a talented {job_title} to join our engineering & analytics team in {selected_city_name}. "
            f"{snippets[0]} {snippets[1]} "
            f"Requirements: Strong proficiency in {', '.join(sampled_skills[:4])}. Experience with agile workflows, scalable architectures, and solid coding practices."
        )

        # Date posted
        days_offset = random.randint(0, total_days)
        posted_dt = start_date + timedelta(days=days_offset)
        posted_date_str = posted_dt.strftime("%Y-%m-%d")

        # Industry & Education
        industry = random.choice(INDUSTRIES)
        education = random.choice(EDUCATIONS)
        source = random.choice(SOURCES)
        emp_type = random.choice(["Full-Time", "Full-Time", "Full-Time", "Contract", "Hybrid"])

        record = {
            "job_id": f"IND_JOB_{idx:06d}",
            "job_title": job_title,
            "role_category": role_category,
            "company": company,
            "company_tier": tier,
            "location_raw": raw_location,
            "salary_raw": raw_salary,
            "min_salary_lpa_raw": calculated_min_lpa,
            "max_salary_lpa_raw": calculated_max_lpa,
            "experience_raw": raw_experience,
            "min_exp_years": min_exp,
            "max_exp_years": max_exp,
            "employment_type": emp_type,
            "industry": industry,
            "education_raw": education,
            "skills_raw": raw_skills,
            "description_raw": desc_text,
            "posted_date": posted_date_str,
            "job_url": f"https://www.techjobs-india-portal.com/job/{idx:06d}",
            "source": source
        }
        records.append(record)

    df = pd.DataFrame(records)
    csv_path = os.path.join(output_dir, "raw_jobs_india.csv")
    json_path = os.path.join(output_dir, "raw_jobs_india.json")
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    print("==================================================")
    print(f" Dataset Generation Completed: {len(df):,} Postings")
    print("==================================================")
    print(f"  -> CSV File:  {csv_path}")
    print(f"  -> JSON File: {json_path}")
    print("--------------------------------------------------")
    print("Summary Breakdown by Role Category:")
    print(df["role_category"].value_counts().to_string())
    print("--------------------------------------------------")
    print("Summary Breakdown by Indian City:")
    print(df["location_raw"].value_counts().head(8).to_string())
    print("==================================================\n")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate realistic Indian Tech Job Postings dataset.")
    parser.add_argument("--records", type=int, default=6500, help="Number of job records to generate (default: 6500)")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory for raw dataset")
    args = parser.parse_args()

    generate_raw_dataset(num_records=args.records, output_dir=args.output)
