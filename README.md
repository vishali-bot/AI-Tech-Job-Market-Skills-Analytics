# AI & Tech Job Market Analysis

MCA mini project by Sribala N. Analyses 12,140 data / AI / tech job postings from the Indian market to find the most demanded skills, the best cities and the salary patterns.

**Stack:** Python (pandas, matplotlib) | SQLite + SQL | Power BI | HTML/CSS/JavaScript website

## Headline findings
- Machine Learning (28.1%), SQL (24.6%) and Python (13.1%) are the most requested technical skills
- Bengaluru has 22.3% of all openings; Gurugram has the highest median salary (20.2 LPA)
- Median disclosed salary is 12.5 LPA (only 8.2% of postings disclose pay)
- Power BI is requested about twice as often as Tableau

Full list: [`Reports/insights.md`](Reports/insights.md)

## Folder structure
```
AI-Tech-Job-Market-Skills-Analytics/
├── Data/
│   ├── raw/                  Dataset1.xlsx, Dataset2.xlsx (original scraped files)
│   └── cleaned/              dataset1_final.csv, job_skills.csv, jobs.db, Dataset1_SQL_Ready.csv
├── python/
│   ├── clean_dataset1.py     Cleans Dataset 1 -> csv + SQLite
│   ├── analysis.py           EDA + 12 charts
│   ├── Dataset1_cleaned.ipynb
│   └── Dataset2_cleaned.ipynb
├── SQL/
│   ├── analysis_queries.sql  18 analysis queries
│   └── query_results/        Q01.csv ... Q18.csv
├── Power BI/
│   └── Dashboard_Guide.md    Steps, DAX measures, page layouts (put the .pbix here)
├── Website/
│   └── index.html            Career Finder site: login, skill tests, jobs, internships, companies
├── Reports/
│   ├── insights.md           Findings and recommendations
│   ├── key_findings.txt
│   └── figures/              12 PNG charts
├── Documentation/
│   ├── Project_Report.md
│   └── Data_Dictionary.md
├── requirements.txt
└── README.md
```

## Career Finder website
`Website/index.html` is a single self-contained file (data embedded). Open it in a browser or host it free with GitHub Pages (Settings > Pages > branch > `/Website` folder, or rename the folder to `docs`).
- **Careers:** booming careers for new users; skills, pay, experience and cities for each field
- **Skill tests:** SQL, Python, Statistics, Machine Learning, Power BI & Excel, each giving a Beginner / Intermediate / Advanced level
- **Jobs and Internships:** openings ranked by how well they match your skills, with Naukri apply links from the dataset
- **Companies:** the skills each company asks for and your match with it
- **Login:** a demo login; accounts are stored only in the browser (not secure authentication)

## How to run
```bash
pip install -r requirements.txt

# 1. Clean Dataset 1 (run inside the python/ folder; Dataset1_SQL_Ready.csv is in this folder; outputs are written here, so copy them to Data/cleaned/)
cd python
python clean_dataset1.py
cd ..

# 2. SQL analysis
sqlite3 Data/cleaned/jobs.db < SQL/analysis_queries.sql

# 3. Charts and key findings (run from project root)
python python/analysis.py
```
Then follow `Power BI/Dashboard_Guide.md` to build the dashboard from the two CSV files.

## Data model
`jobs` (one row per posting) 1 --- * `job_skills` (one row per posting and skill), joined on `Job_ID`. See `Documentation/Data_Dictionary.md`.
