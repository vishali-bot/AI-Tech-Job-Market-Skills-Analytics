# Power BI Dashboard Guide

File to create: `Power BI/AI_Tech_Job_Market.pbix` (Power BI Desktop is free).

## 1. Load data
Home > Get Data > Text/CSV, load both files from `Data/cleaned/`:
- `dataset1_final.csv` (table **jobs**)
- `job_skills.csv` (table **job_skills**)

In Power Query check types: Job_ID whole number, Salary_* decimal, Salary_Disclosed True/False, Days_Ago whole number.

## 2. Model
Model view: relationship `jobs[Job_ID]` 1 -> * `job_skills[Job_ID]`, single direction (jobs filters job_skills).

## 3. DAX measures (create a table called `_Measures`)
```DAX
Total Jobs = DISTINCTCOUNT(jobs[Job_ID])

Total Companies = DISTINCTCOUNT(jobs[Company_Name])

Jobs With Salary = CALCULATE([Total Jobs], jobs[Salary_Disclosed] = TRUE())

% Salary Disclosed = DIVIDE([Jobs With Salary], [Total Jobs])

Median Salary LPA = MEDIAN(jobs[Salary_Mid_LPA])

Avg Salary LPA = AVERAGE(jobs[Salary_Mid_LPA])

Skill Job Count = DISTINCTCOUNT(job_skills[Job_ID])

% Of Jobs With Skill =
DIVIDE(
    CALCULATE(DISTINCTCOUNT(job_skills[Job_ID])),
    CALCULATE([Total Jobs], ALL(jobs))
)

Fresher Jobs = CALCULATE([Total Jobs], jobs[Experience_Min] <= 1)

% Fresher Jobs = DIVIDE([Fresher Jobs], [Total Jobs])

Python And SQL Jobs =
VAR py = CALCULATETABLE(VALUES(job_skills[Job_ID]), job_skills[Skill] = "Python")
VAR sq = CALCULATETABLE(VALUES(job_skills[Job_ID]), job_skills[Skill] = "SQL")
RETURN COUNTROWS(INTERSECT(py, sq))
```

Calculated column for experience bands (in `jobs`):
```DAX
Experience Band =
SWITCH(TRUE(),
    ISBLANK(jobs[Experience_Min]), "Not stated",
    jobs[Experience_Min] <= 1, "0-1 yrs",
    jobs[Experience_Min] <= 3, "2-3 yrs",
    jobs[Experience_Min] <= 5, "4-5 yrs",
    jobs[Experience_Min] <= 8, "6-8 yrs",
    "9+ yrs")
```

Technical-skill flag (in `job_skills`) so you can hide buzzwords:
```DAX
Is Technical =
IF(job_skills[Skill] IN {"Analytics","Research","Agile","Automation","Communication",
   "Project Management","Stakeholder Management","Cloud","Data Analysis",
   "Artificial Intelligence","Business Intelligence"}, FALSE(), TRUE())
```

## 4. Pages

### Page 1 - Market Overview
- 4 KPI cards: Total Jobs, Total Companies, Median Salary LPA, % Salary Disclosed
- Donut: jobs by `Role_Category`
- Bar: top 10 `City` by Total Jobs
- Column: `Experience Band` by Total Jobs
- Slicers: City, Role_Category, Seniority

### Page 2 - Skills Demand
- Bar: top 15 `job_skills[Skill]` by Skill Job Count, filter `Is Technical = TRUE`
- Matrix: rows = Skill, columns = jobs[Role_Category], values = Skill Job Count (conditional-format background colour)
- Cards: Python And SQL Jobs, jobs requesting Power BI, Tableau
- Slicers: Role_Category, Experience Band

### Page 3 - Salary Insights
- Add a visual-level filter `Salary_Disclosed = True` on every visual here
- Bar: Median Salary LPA by Role_Category
- Bar: Median Salary LPA by City (filter to cities with 30+ salaried postings)
- Column: Median Salary LPA by Experience Band
- Histogram-style column chart: Salary bins (use Group on Salary_Mid_LPA, bin size 5)
- Text box: "Only 8.2% of postings disclose salary"

### Page 4 - Companies and Trends (optional)
- Table: top 15 Company_Name by Total Jobs
- Column: Total Jobs by Days_Ago bins

## 5. Design tips
- One theme: dark blue (#2F5D8C) and orange (#E08A2E), same as the charts in `Reports/figures/`.
- Page title on every page, slicers aligned on the left, sync slicers across pages (View > Sync slicers).
- Take a screenshot of each page and save in `Reports/figures/powerbi_page1.png` etc. for the report and PPT.

## 6. Review checklist before taking screenshots
1. Skills chart: filter `Skill` to Top 15 by Skill Job Count; matrix: Top 10.
2. Remove `Is Technical` from the chart Legend and matrix Rows (keep it only as a filter).
3. Skills page: the combined slicer should contain only `Experience Band`.
4. Add column `Experience Band Order` (0-1 yrs=1 ... 9+ yrs=5, Not stated=6) and use Sort by column on `Experience Band`.
5. Salary page: filter the city chart to cities with at least 30 salary postings.
6. Remove the quotation marks from the salary text note.
7. Add a title text box at the top of every page and align the visuals.
8. Check Model view: jobs[Job_ID] 1:* job_skills[Job_ID]. With no slicer: Total Jobs 12,140; Python And SQL 527; Power BI 769.
