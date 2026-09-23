# 5-Page Power BI Dashboard Specification

## Design Theme & Palette
* **Background**: `#0F172A` (Slate Dark) / `#F8FAFC` (Clean Light Mode)
* **Primary Accent**: `#3B82F6` (Electric Blue)
* **Secondary Accent**: `#10B981` (Emerald Green)
* **Highlight / Warning**: `#F59E0B` (Amber Gold)
* **Typography**: Segoe UI / Inter, bold KPI values, clean muted axis labels.

---

## Page 1: Executive Overview
### Top KPI Cards:
* `[Total Jobs]` -> **6,500**
* `[Total Companies]` -> **480**
* `[Total Locations]` -> **8 Tech Hubs**
* `[Average Salary LPA]` -> **₹ 30.68 LPA**
* `[Median Salary LPA]` -> **₹ 27.50 LPA**
* `Most Demanded Role` -> **Software Development Engineer (35.5%)**

### Visuals:
1. **Donut Chart**: Postings by Role Category (`dim_roles[role_category]`, `[Total Jobs]`).
2. **Clustered Bar Chart**: Average Salary by Role Category (`[Average Salary LPA]`).
3. **Stacked Bar Chart**: Top 10 Hiring Companies by Openings (`dim_companies[company_name]`, `[Total Jobs]`).
4. **Line Chart**: Monthly Hiring Trend (`dim_dates[year_month]`, `[Total Jobs]`).
5. **Horizontal Bar Chart**: Jobs by Location (`dim_locations[city]`, `[Total Jobs]`).

---

## Page 2: Role Comparison
### Global Slicers:
* Role Category (`dim_roles[role_category]`)
* Experience Tier (`fact_jobs[experience_bracket]`)
* Indian City (`dim_locations[city]`)
* Industry (`dim_companies[industry]`)

### Visuals:
1. **Multi-Row Card**: Head-to-Head Comparison (SDE vs Data Analyst vs Data Scientist vs AI/ML).
2. **Grouped Bar Chart**: Average vs Median Salary by Role.
3. **100% Stacked Column Chart**: Experience Level Distribution within each role.
4. **Clustered Column Chart**: Top 5 In-Demand Skills for selected roles.
5. **Treemap Visual**: Industry Distribution across tech roles.

---

## Page 3: Skills Intelligence & Skill Matrix
### Visuals:
1. **Interactive Skill Matrix (Matrix Visual)**:
   * Rows: `dim_skills[skill_name]`
   * Columns: `dim_roles[role_category]`
   * Values: `[Skill Demand %]` (Heatmap color formatting with blue gradient).
2. **Top 15 Most Demanded Skills (Horizontal Bar Chart)**: Total mentions across India.
3. **Universal vs Role-Specific Skills (Venn/Table Visual)**: Cross-role versatility analysis.
4. **Top Co-Occurring Skill Pairs Table**: Highlighting common tool pairings (e.g., Python + SQL, Power BI + DAX).

---

## Page 4: Salary Intelligence
### Visuals:
1. **Box & Whisker Plot**: Salary spread, IQR, and outliers per role category.
2. **Scatter Plot**: Experience (X-axis) vs Average Salary in ₹ LPA (Y-axis) colored by Role.
3. **Top 15 Highest-Paying Skills (Bar Chart)**: Filtered for min 50 postings.
4. **Salary by Company Tier (Column Chart)**: Product Unicorns vs GCCs vs Analytics Consultancies vs IT Services.
5. **Salary Distribution Histogram**: Overall frequency of salary brackets.

---

## Page 5: Geographic & Hiring Trends
### Visuals:
1. **Map / Filled Map Visual**: Job volume and average salary across Indian tech cities.
2. **City-Wise Role Breakdown (Stacked Bar)**: Role proportion in Bengaluru vs Hyderabad vs Pune vs NCR vs Mumbai vs Chennai.
3. **Salary Premium by City (Bar Chart)**: Regional cost-of-talent index.
4. **Quarterly Hiring Seasonality (Area Chart)**: Q1 vs Q2 vs Q3 vs Q4 recruitment patterns.
5. **Remote vs Onsite Hiring Share (Donut Chart)**: In-office vs Hybrid/Remote percentages.
