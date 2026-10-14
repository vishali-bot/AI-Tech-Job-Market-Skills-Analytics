# Key Insights - AI & Tech Job Market Analysis

Source: 12,140 de-duplicated job postings (Dataset 1, Indian market), 3,197 companies, 222 locations.
All numbers come from `SQL/analysis_queries.sql` (results in `SQL/query_results/`) and `python/analysis.py`.

## 1. Demand
- **Data Scientist titles lead the market (46%)**, followed by Data Analyst / BI (29%). ML / AI Engineer titles are 6.8% and Data Engineer titles 1.5%.
- **Bengaluru has the most openings (22.3%)**, then Hyderabad (11.9%), Gurugram (10.0%), Mumbai (9.2%) and Pune (6.6%). Remote roles make up 6.4%.
- Demand is concentrated at **2-5 years of experience** (about 60% of postings with a stated range). Fresher-level (0-1 yrs) roles are 1,927 postings (about 16%).

## 2. Skills
- Most requested technical skills (share of all postings): **Machine Learning 28.1%, SQL 24.6%, Python 13.1%**, Data Mining 9.6%, Excel 7.7%, Statistics 7.4%, Power BI 6.3%.
- **SQL appears in almost twice as many postings as Python** (2,984 vs 1,589). Only 527 postings list both.
- **Power BI (769) is requested about twice as often as Tableau (392)**; Excel (930) is still the most requested BI tool.
- Among cloud platforms, **GCP (504) leads Azure (246) and AWS (202)** in this dataset.
- Strongest skill pairs: Machine Learning + SQL (1,284), Machine Learning + Python (575), Python + SQL (527).
- SQL is the top skill for Data Analyst / BI and Data Engineer titles; Machine Learning is the top skill for Data Scientist titles (39% of those postings).

## 3. Salary (only 992 postings = 8.2% disclose pay)
- **Median 12.5 LPA, mean 14.6 LPA.**
- Median by role: Data Scientist 15.0, Software / Other Tech 14.5, Data Analyst / BI 12.0, ML / AI Engineer 11.2, Data Engineer 10.5 LPA.
- **Gurugram pays the most (median 20.2 LPA)**, then Chennai (14.0) and Pune (13.2). Bengaluru and Mumbai have the lowest medians (8.0 LPA each) despite high demand.
- Postings that mention Deep Learning, Automation, Project Management and SAS have the highest average pay (about 16.5-17.3 LPA), compared with 14.6 LPA overall.
- Senior and leadership titles average 15.4-15.7 LPA versus 12.8 LPA for junior titles.

## 4. Recommendations for job seekers
1. Learn **SQL first, then Python**; the SQL-only postings outnumber Python-only by 2.3x.
2. Add **Machine Learning fundamentals + Statistics** for Data Scientist roles.
3. Pick **Power BI** over Tableau for the Indian market; keep Excel strong.
4. Learn one cloud platform (GCP / Azure) and basic automation to move into higher-paying postings.
5. Target Bengaluru, Hyderabad and Gurugram for volume; Gurugram for pay.

## 5. Limitations
- Only 8.2% of postings disclose salary, so salary findings are indicative, not representative.
- Skills were extracted by keyword matching from a short scraped text; Python (13%) is probably under-counted.
- A few employers post many near-identical roles (for example one company has about 500 postings with the same title), which inflates company and city counts.
- A snapshot, not a time series: 69% of postings are 15-30 days old, so no trend analysis is possible.
