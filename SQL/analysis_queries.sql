-- =====================================================================
-- AI & Tech Job Market Analysis  |  SQL analysis on jobs.db (SQLite)
-- Tables: jobs(Job_ID, Job_Title, Role_Category, Seniority, Company_Name,
--              Experience_Min/Max, Salary_Min/Max/Mid_LPA, Salary_Disclosed,
--              City, Skills, Skill_Count, Days_Ago, ...)
--         job_skills(Job_ID, Skill)
-- Run:  sqlite3 Data/cleaned/jobs.db < SQL/analysis_queries.sql
-- =====================================================================

-- Q01. Dataset overview
SELECT COUNT(*) AS total_jobs,
       COUNT(DISTINCT Company_Name) AS companies,
       COUNT(DISTINCT City) AS cities,
       SUM(Salary_Disclosed) AS jobs_with_salary,
       ROUND(100.0*SUM(Salary_Disclosed)/COUNT(*),1) AS pct_salary_disclosed
FROM jobs;

-- Q02. Jobs by role category
SELECT Role_Category, COUNT(*) AS jobs,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM jobs),1) AS pct
FROM jobs GROUP BY Role_Category ORDER BY jobs DESC;

-- Q03. Top 15 cities by number of openings
SELECT City, COUNT(*) AS jobs,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM jobs),1) AS pct
FROM jobs WHERE City IS NOT NULL
GROUP BY City ORDER BY jobs DESC LIMIT 15;

-- Q04. Top 20 skills overall (technical + generic)
SELECT Skill, COUNT(*) AS jobs,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM jobs),1) AS pct_of_jobs
FROM job_skills GROUP BY Skill ORDER BY jobs DESC LIMIT 20;

-- Q05. Top 15 TECHNICAL skills (generic buzzwords excluded)
SELECT Skill, COUNT(*) AS jobs,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM jobs),1) AS pct_of_jobs
FROM job_skills
WHERE Skill NOT IN ('Analytics','Research','Agile','Automation','Communication',
                    'Project Management','Stakeholder Management','Cloud',
                    'Data Analysis','Artificial Intelligence','Business Intelligence')
GROUP BY Skill ORDER BY jobs DESC LIMIT 15;

-- Q06. Top 5 skills inside each role category (window function)
WITH s AS (
  SELECT j.Role_Category, k.Skill, COUNT(*) AS jobs,
         ROW_NUMBER() OVER (PARTITION BY j.Role_Category ORDER BY COUNT(*) DESC) AS rn
  FROM jobs j JOIN job_skills k USING (Job_ID)
  WHERE j.Role_Category IN ('Data Scientist','Data Analyst / BI',
        'Machine Learning / AI Engineer','Data Engineer')
    AND k.Skill NOT IN ('Analytics','Research','Agile','Automation','Communication',
                        'Data Analysis','Artificial Intelligence','Project Management')
  GROUP BY j.Role_Category, k.Skill)
SELECT Role_Category, Skill, jobs FROM s WHERE rn <= 5 ORDER BY Role_Category, jobs DESC;

-- Q07. Salary by role category (only jobs that disclose salary, min 15 jobs)
SELECT Role_Category, COUNT(*) AS jobs_with_salary,
       ROUND(AVG(Salary_Mid_LPA),1) AS avg_lpa,
       ROUND(MIN(Salary_Mid_LPA),1) AS min_lpa,
       ROUND(MAX(Salary_Mid_LPA),1) AS max_lpa
FROM jobs WHERE Salary_Disclosed = 1
GROUP BY Role_Category HAVING COUNT(*) >= 15 ORDER BY avg_lpa DESC;

-- Q08. Average salary by city (min 20 salary-disclosed jobs)
SELECT City, COUNT(*) AS jobs_with_salary, ROUND(AVG(Salary_Mid_LPA),1) AS avg_lpa
FROM jobs WHERE Salary_Disclosed = 1
GROUP BY City HAVING COUNT(*) >= 20 ORDER BY avg_lpa DESC;

-- Q09. Which skills are linked to higher pay? (skills in >= 30 salaried jobs)
SELECT k.Skill, COUNT(*) AS jobs_with_salary, ROUND(AVG(j.Salary_Mid_LPA),1) AS avg_lpa
FROM job_skills k JOIN jobs j USING (Job_ID)
WHERE j.Salary_Disclosed = 1
GROUP BY k.Skill HAVING COUNT(*) >= 30 ORDER BY avg_lpa DESC LIMIT 15;

-- Q10. Experience band vs demand and salary
SELECT CASE WHEN Experience_Min <= 1 THEN '0-1 yrs (Fresher)'
            WHEN Experience_Min <= 3 THEN '2-3 yrs'
            WHEN Experience_Min <= 5 THEN '4-5 yrs'
            WHEN Experience_Min <= 8 THEN '6-8 yrs'
            ELSE '9+ yrs' END AS experience_band,
       COUNT(*) AS jobs, ROUND(AVG(Salary_Mid_LPA),1) AS avg_lpa
FROM jobs WHERE Experience_Min IS NOT NULL
GROUP BY experience_band ORDER BY MIN(Experience_Min);

-- Q11. Seniority distribution
SELECT Seniority, COUNT(*) AS jobs, ROUND(AVG(Salary_Mid_LPA),1) AS avg_lpa
FROM jobs GROUP BY Seniority ORDER BY jobs DESC;

-- Q12. Top 15 hiring companies
SELECT Company_Name, COUNT(*) AS openings
FROM jobs GROUP BY Company_Name ORDER BY openings DESC LIMIT 15;

-- Q13. Most frequent skill PAIRS (self join)
SELECT a.Skill AS skill_1, b.Skill AS skill_2, COUNT(*) AS together
FROM job_skills a JOIN job_skills b ON a.Job_ID = b.Job_ID AND a.Skill < b.Skill
WHERE a.Skill NOT IN ('Analytics','Research','Agile','Automation','Communication')
  AND b.Skill NOT IN ('Analytics','Research','Agile','Automation','Communication')
GROUP BY a.Skill, b.Skill ORDER BY together DESC LIMIT 15;

-- Q14. Python vs SQL vs Both vs Neither
SELECT CASE WHEN py=1 AND sq=1 THEN 'Python + SQL'
            WHEN py=1 THEN 'Python only'
            WHEN sq=1 THEN 'SQL only' ELSE 'Neither' END AS combo,
       COUNT(*) AS jobs
FROM (SELECT j.Job_ID,
        MAX(CASE WHEN k.Skill='Python' THEN 1 ELSE 0 END) AS py,
        MAX(CASE WHEN k.Skill='SQL' THEN 1 ELSE 0 END) AS sq
      FROM jobs j LEFT JOIN job_skills k USING (Job_ID) GROUP BY j.Job_ID)
GROUP BY combo ORDER BY jobs DESC;

-- Q15. BI tool demand (Power BI vs Tableau vs Excel)
SELECT Skill, COUNT(*) AS jobs FROM job_skills
WHERE Skill IN ('Power BI','Tableau','Excel') GROUP BY Skill ORDER BY jobs DESC;

-- Q16. Cloud platform demand
SELECT Skill, COUNT(*) AS jobs FROM job_skills
WHERE Skill IN ('AWS','Azure','GCP') GROUP BY Skill ORDER BY jobs DESC;

-- Q17. Posting freshness: jobs by days since posting
SELECT CASE WHEN Days_Ago <= 3 THEN '0-3 days'
            WHEN Days_Ago <= 7 THEN '4-7 days'
            WHEN Days_Ago <= 14 THEN '8-14 days'
            WHEN Days_Ago <= 30 THEN '15-30 days'
            ELSE '30+ days' END AS freshness, COUNT(*) AS jobs
FROM jobs WHERE Days_Ago IS NOT NULL GROUP BY freshness ORDER BY MIN(Days_Ago);

-- Q18. Average number of skills asked per role category
SELECT Role_Category, ROUND(AVG(Skill_Count),1) AS avg_skills_per_job
FROM jobs GROUP BY Role_Category ORDER BY avg_skills_per_job DESC;
