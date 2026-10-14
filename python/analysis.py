"""
EDA + charts for the AI & Tech Job Market Analysis project.
Reads  : Data/cleaned/jobs.db
Writes : Reports/figures/*.png  and  Reports/key_findings.txt
Run from the project root:  python python/analysis.py
"""
import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB = os.path.join("Data", "cleaned", "jobs.db")
OUT = os.path.join("Reports", "figures")
os.makedirs(OUT, exist_ok=True)

GENERIC = ["Analytics", "Research", "Agile", "Automation", "Communication",
           "Project Management", "Stakeholder Management", "Cloud",
           "Data Analysis", "Artificial Intelligence", "Business Intelligence"]

plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10})
BLUE, ORANGE = "#2F5D8C", "#E08A2E"

conn = sqlite3.connect(DB)
jobs = pd.read_sql("SELECT * FROM jobs", conn)
skills = pd.read_sql("SELECT * FROM job_skills", conn)
n_jobs = len(jobs)


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close()


def hbar(series, title, xlabel, name, color=BLUE, fmt="{:,.0f}"):
    series = series.sort_values()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(series.index, series.values, color=color)
    for i, v in enumerate(series.values):
        ax.text(v, i, " " + fmt.format(v), va="center", fontsize=8)
    ax.set_title(title, fontweight="bold", loc="left")
    ax.set_xlabel(xlabel)
    save(name)


# 1. Role category
hbar(jobs["Role_Category"].value_counts(), "Job openings by role category",
     "Number of job postings", "01_role_category.png")

# 2. Top cities
hbar(jobs["City"].value_counts().head(10), "Top 10 cities by openings",
     "Number of job postings", "02_top_cities.png", ORANGE)

# 3. Top technical skills (% of jobs)
tech = skills[~skills["Skill"].isin(GENERIC)]["Skill"].value_counts().head(15)
hbar(tech / n_jobs * 100, "Top 15 technical skills (% of job postings)",
     "% of postings mentioning the skill", "03_top_technical_skills.png",
     BLUE, "{:.1f}%")

# 4. Python / SQL overlap
has = skills.assign(v=1).pivot_table(index="Job_ID", columns="Skill", values="v", aggfunc="max").fillna(0)
py = has.reindex(jobs["Job_ID"]).fillna(0)["Python"]
sq = has.reindex(jobs["Job_ID"]).fillna(0)["SQL"]
combo = pd.Series({"Neither": ((py == 0) & (sq == 0)).sum(),
                   "SQL only": ((py == 0) & (sq == 1)).sum(),
                   "Python only": ((py == 1) & (sq == 0)).sum(),
                   "Python + SQL": ((py == 1) & (sq == 1)).sum()})
hbar(combo, "Python vs SQL in job postings", "Number of postings", "04_python_sql.png", ORANGE)

# 5. BI tools and cloud
tools = skills[skills["Skill"].isin(["Power BI", "Tableau", "Excel", "AWS", "Azure", "GCP"])]["Skill"].value_counts()
hbar(tools, "BI tool and cloud platform demand", "Number of postings", "05_bi_cloud.png")

# 6. Experience bands
bins = [-1, 1, 3, 5, 8, 100]
labels = ["0-1 yrs", "2-3 yrs", "4-5 yrs", "6-8 yrs", "9+ yrs"]
jobs["Exp_Band"] = pd.cut(jobs["Experience_Min"], bins=bins, labels=labels)
exp = jobs["Exp_Band"].value_counts().reindex(labels)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(exp.index.astype(str), exp.values, color=BLUE)
for i, v in enumerate(exp.values):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=8)
ax.set_title("Demand by minimum experience required", fontweight="bold", loc="left")
ax.set_ylabel("Number of postings")
save("06_experience_demand.png")

# 7. Salary distribution + by role
sal = jobs[jobs["Salary_Disclosed"] == 1]
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(sal["Salary_Mid_LPA"].clip(upper=60), bins=30, color=ORANGE, edgecolor="white")
ax.axvline(sal["Salary_Mid_LPA"].median(), color="black", ls="--", lw=1)
ax.text(sal["Salary_Mid_LPA"].median() + 0.5, ax.get_ylim()[1] * 0.9,
        f"median {sal['Salary_Mid_LPA'].median():.1f} LPA", fontsize=8)
ax.set_title(f"Salary distribution (n={len(sal):,} postings that disclose pay)", fontweight="bold", loc="left")
ax.set_xlabel("Mid-point salary (LPA, capped at 60)")
ax.set_ylabel("Postings")
save("07_salary_distribution.png")

role_sal = sal.groupby("Role_Category")["Salary_Mid_LPA"].agg(["count", "median"])
role_sal = role_sal[role_sal["count"] >= 30]["median"]
hbar(role_sal, "Median salary by role (LPA, salary-disclosed postings)", "Median LPA",
     "08_salary_by_role.png", BLUE, "{:.1f}")

# 9. Salary by city
city_sal = sal.groupby("City")["Salary_Mid_LPA"].agg(["count", "median"])
city_sal = city_sal[city_sal["count"] >= 30]["median"]
hbar(city_sal, "Median salary by city (LPA, cities with 30+ salary postings)",
     "Median LPA", "09_salary_by_city.png", ORANGE, "{:.1f}")

# 10. Skills linked to pay (technical only, 30+ salaried postings)
sk = skills.merge(sal[["Job_ID", "Salary_Mid_LPA"]], on="Job_ID")
sk = sk[~sk["Skill"].isin(GENERIC)]
g = sk.groupby("Skill")["Salary_Mid_LPA"].agg(["count", "median"])
g = g[g["count"] >= 30]["median"].sort_values(ascending=False).head(12)
hbar(g, "Median salary of postings by skill (LPA, technical skills)", "Median LPA",
     "10_salary_by_skill.png", BLUE, "{:.1f}")

# 11. Heatmap: top technical skills by role
roles = ["Data Scientist", "Data Analyst / BI", "Machine Learning / AI Engineer", "Data Engineer"]
top = list(tech.index[:10])
m = skills.merge(jobs[["Job_ID", "Role_Category"]], on="Job_ID")
m = m[m["Role_Category"].isin(roles) & m["Skill"].isin(top)]
ct = pd.crosstab(m["Skill"], m["Role_Category"]).reindex(top)[roles]
share = ct / jobs[jobs["Role_Category"].isin(roles)]["Role_Category"].value_counts().reindex(roles) * 100
fig, ax = plt.subplots(figsize=(7.5, 4.8))
im = ax.imshow(share.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(roles)))
ax.set_xticklabels(["Data\nScientist", "Data Analyst\n/ BI", "ML / AI\nEngineer", "Data\nEngineer"])
ax.set_yticks(range(len(top)))
ax.set_yticklabels(top)
for i in range(share.shape[0]):
    for j in range(share.shape[1]):
        ax.text(j, i, f"{share.values[i, j]:.0f}%", ha="center", va="center",
                fontsize=8, color="white" if share.values[i, j] > 30 else "black")
ax.set_title("% of postings in each role that ask for the skill", fontweight="bold", loc="left")
save("11_skill_role_heatmap.png")

# 12. Hiring companies
hbar(jobs["Company_Name"].value_counts().head(10), "Top 10 hiring companies (openings)",
     "Number of postings", "12_top_companies.png", ORANGE)

# ---------- key findings text ----------
lines = [
    f"Total postings: {n_jobs:,} | companies: {jobs['Company_Name'].nunique():,} | cities: {jobs['City'].nunique()}",
    f"Salary disclosed: {len(sal):,} ({len(sal)/n_jobs:.1%}); median {sal['Salary_Mid_LPA'].median():.1f} LPA, mean {sal['Salary_Mid_LPA'].mean():.1f} LPA",
    f"Top city: {jobs['City'].value_counts().index[0]} ({jobs['City'].value_counts().iloc[0]/n_jobs:.1%})",
    "Top technical skills (% of postings): " + ", ".join(f"{k} {v/n_jobs*100:.1f}%" for k, v in tech.head(6).items()),
    f"Python+SQL together: {combo['Python + SQL']:,} | SQL only: {combo['SQL only']:,} | Python only: {combo['Python only']:,}",
]
with open(os.path.join("Reports", "key_findings.txt"), "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print("Charts saved to", OUT)
