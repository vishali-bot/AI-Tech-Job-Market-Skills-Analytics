"""
Rebuilds a properly cleaned Dataset 1 from Dataset1_SQL_Ready.csv.

Outputs (same folder as this script by default):
  dataset1_final.csv   one row per job posting, parsed columns
  job_skills.csv       one row per (job_id, skill)  -> use this for skill analysis
  jobs.db              SQLite database with tables jobs and job_skills
"""
import re
import sqlite3
import pandas as pd

SRC = "Dataset1_SQL_Ready.csv"
COLS = ["Job_Title", "Company_Name", "Experience_Required", "Package_Details",
        "Location", "Skills", "Job_URL", "Post_Time"]

# ---------- 1. Load (header was saved as a data row, so skip it) ----------
df = pd.read_csv(SRC, header=None, skiprows=1, names=COLS)
n_raw = len(df)

# ---------- 2. Remove duplicates ----------
df = df.drop_duplicates()
n_full = len(df)
# same URL scraped on different days -> keep the first record
has_url = df["Job_URL"].notna()
df = pd.concat([df[has_url].drop_duplicates(subset="Job_URL"), df[~has_url]])
df = df.reset_index(drop=True)

# ---------- 3. Text columns ----------
for c in ["Job_Title", "Company_Name", "Location", "Skills"]:
    df[c] = df[c].astype("string").str.strip()
df["Job_Title"] = df["Job_Title"].replace({"None": pd.NA, "NONE": pd.NA})

# ---------- 4. Experience ----------
exp = df["Experience_Required"].str.extract(r"(\d+)\s*-\s*(\d+)")
df["Experience_Min"] = pd.to_numeric(exp[0]).astype("Int64")
df["Experience_Max"] = pd.to_numeric(exp[1]).astype("Int64")

# ---------- 5. Salary (only "x-y Lacs PA" is convertible to LPA) ----------
sal = df["Package_Details"].str.extract(r"([\d.]+)\s*-\s*([\d.]+)\s*Lacs PA")
df["Salary_Min_LPA"] = pd.to_numeric(sal[0])
df["Salary_Max_LPA"] = pd.to_numeric(sal[1])
df["Salary_Mid_LPA"] = (df["Salary_Min_LPA"] + df["Salary_Max_LPA"]) / 2
df["Salary_Disclosed"] = df["Salary_Mid_LPA"].notna()

# ---------- 6. Post time -> days ago ----------
def days_ago(s):
    if pd.isna(s):
        return pd.NA
    s = s.lower()
    if "just now" in s or "today" in s or "hour" in s:
        return 0
    m = re.match(r"(\d+)\+?\s*day", s)
    return int(m.group(1)) if m else pd.NA

df["Days_Ago"] = df["Post_Time"].map(days_ago).astype("Int64")

# ---------- 7. Location -> primary city ----------
CITY_FIX = {"gurgaon": "Gurugram", "gurugram": "Gurugram", "bangalore": "Bengaluru",
            "bengaluru": "Bengaluru", "hyderabad": "Hyderabad", "secunderabad": "Hyderabad",
            "bombay": "Mumbai", "mumbai": "Mumbai", "new delhi": "Delhi", "delhi": "Delhi",
            "noida": "Noida", "pune": "Pune", "chennai": "Chennai", "kolkata": "Kolkata"}

def primary_city(s):
    if pd.isna(s):
        return pd.NA
    first = re.split(r"[,/]", s)[0].strip()
    return CITY_FIX.get(first.lower(), first.title())

df["City"] = df["Location"].map(primary_city)
df["Multi_Location"] = df["Location"].fillna("").str.count(",") >= 3

# ---------- 8. Role category from title ----------
ROLE_RULES = [
    ("Machine Learning / AI Engineer", r"machine learning|\bml\b|\bai\b|artificial|deep learning|nlp|llm|gen ?ai"),
    ("Data Engineer",                  r"data engineer|etl|big data|pipeline"),
    ("Data Scientist",                 r"data scien"),
    ("Data Analyst / BI",              r"analyst|analytics|business intelligence|\bbi\b|reporting"),
    ("Software / Other Tech",          r"developer|software|engineer|architect"),
]
def role(t):
    if pd.isna(t):
        return "Unknown"
    t = t.lower()
    for name, pat in ROLE_RULES:
        if re.search(pat, t):
            return name
    return "Other"

df["Role_Category"] = df["Job_Title"].map(role)

def seniority(t):
    if pd.isna(t):
        return "Unknown"
    t = t.lower()
    if re.search(r"head|director|vp|vice president|principal|chief", t): return "Leadership"
    if re.search(r"manager|lead|architect", t):                         return "Manager / Lead"
    if re.search(r"senior|sr\.?\b", t):                                 return "Senior"
    if re.search(r"intern|trainee|junior|jr\.?\b|fresher|associate", t): return "Junior"
    return "Mid / Unspecified"

df["Seniority"] = df["Job_Title"].map(seniority)

# ---------- 9. Skills: the scraped text has no separators, so match a vocabulary ----------
# (case-insensitive unless noted; short tokens are matched case-sensitively to avoid false hits)
SKILLS = {
    "Python": r"python", "SQL": r"sql", "R": None, "Machine Learning": r"machine learning",
    "Deep Learning": r"deep learning", "NLP": r"nlp|natural language", "Computer Vision": r"computer vision",
    "Generative AI": r"generative ai|genai|gen ai|llm|large language", "TensorFlow": r"tensorflow",
    "PyTorch": r"pytorch", "Scikit-learn": r"scikit", "Keras": r"keras", "Pandas": r"pandas",
    "NumPy": r"numpy", "Statistics": r"statistic", "Data Analysis": r"data analy",
    "Data Visualization": r"data visuali[sz]ation|visuali[sz]ation", "Data Mining": r"data mining",
    "Data Modeling": r"data modell?ing", "Predictive Modeling": r"predictive model",
    "Power BI": r"power ?bi", "Tableau": r"tableau", "Excel": r"excel", "SAS": None,
    "Spark": r"spark", "Hadoop": r"hadoop", "Hive": r"hive", "Kafka": r"kafka",
    "AWS": r"aws|amazon web", "Azure": r"azure", "GCP": r"gcp|google cloud", "Cloud": r"cloud",
    "Docker": r"docker", "Kubernetes": r"kubernetes", "Git": r"\bgit\b|github", "Linux": r"linux",
    "Java": r"java(?!script)", "JavaScript": r"javascript", "Scala": r"scala", "C++": r"c\+\+",
    "MATLAB": r"matlab", "Big Data": r"big data", "ETL": r"\betl\b", "Data Warehousing": r"data warehous",
    "MongoDB": r"mongo", "NoSQL": r"nosql", "Snowflake": r"snowflake", "Databricks": r"databricks",
    "MLOps": r"mlops", "Time Series": r"time series", "Forecasting": r"forecast",
    "Artificial Intelligence": r"artificial intelligence", "Analytics": r"analytic",
    "Business Intelligence": r"business intelligence", "Project Management": r"project management",
    "Communication": r"communication", "Stakeholder Management": r"stakeholder",
    "Agile": r"agile", "Automation": r"automation", "Research": r"research",
}
CASE_SENSITIVE = {"R": r"(?<![A-Za-z])R(?![a-z])", "SAS": r"SAS(?![a-z])"}

def extract_skills(s):
    if pd.isna(s):
        return []
    found = []
    for name, pat in SKILLS.items():
        if name in CASE_SENSITIVE:
            hit = re.search(CASE_SENSITIVE[name], s)
        else:
            hit = re.search(pat, s, flags=re.I)
        if hit:
            found.append(name)
    return found

df["Job_ID"] = range(1, len(df) + 1)
df["Skill_List"] = df["Skills"].map(extract_skills)
df["Skill_Count"] = df["Skill_List"].str.len()

skills_long = (df[["Job_ID", "Skill_List"]].explode("Skill_List")
               .dropna().rename(columns={"Skill_List": "Skill"}))

# ---------- 10. Save ----------
final_cols = ["Job_ID", "Job_Title", "Role_Category", "Seniority", "Company_Name",
              "Experience_Required", "Experience_Min", "Experience_Max",
              "Package_Details", "Salary_Min_LPA", "Salary_Max_LPA", "Salary_Mid_LPA",
              "Salary_Disclosed", "Location", "City", "Multi_Location",
              "Skills", "Skill_Count", "Post_Time", "Days_Ago", "Job_URL"]
out = df[final_cols]
out.to_csv("dataset1_final.csv", index=False)
skills_long.to_csv("job_skills.csv", index=False)

with sqlite3.connect("jobs.db") as conn:
    out.to_sql("jobs", conn, if_exists="replace", index=False)
    skills_long.to_sql("job_skills", conn, if_exists="replace", index=False)

print(f"raw rows: {n_raw:,} | after full-row dedup: {n_full:,} | after URL dedup: {len(df):,}")
print(f"salary disclosed: {out['Salary_Disclosed'].sum():,} | skill rows: {len(skills_long):,}")
print(f"jobs with >=1 skill extracted: {(out['Skill_Count'] > 0).mean():.0%}")
