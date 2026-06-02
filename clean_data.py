import pandas as pd
import numpy as np
import os

# ── Load raw data ─────────────────────────────────────────────────────────────
raw_path = os.path.join("data", "WA_Fn-UseC_-HR-Employee-Attrition.csv")
df = pd.read_csv(raw_path)

print(f"Raw data loaded: {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}\n")

# ── Drop useless columns (same value for all rows) ───────────────────────────
df = df.drop(columns=["EmployeeCount", "Over18", "StandardHours"])

# ── Binary encode Attrition ───────────────────────────────────────────────────
df["AttritionBinary"] = (df["Attrition"] == "Yes").astype(int)

# ── Tenure bands ─────────────────────────────────────────────────────────────
df["TenureBand"] = pd.cut(
    df["YearsAtCompany"],
    bins=[-1, 2, 5, 10, 20, 100],
    labels=["0-2 yrs", "3-5 yrs", "6-10 yrs", "11-20 yrs", "20+ yrs"]
)

# ── Seniority band from JobLevel ──────────────────────────────────────────────
df["SeniorityBand"] = df["JobLevel"].map({
    1: "Junior",
    2: "Mid-Level",
    3: "Senior",
    4: "Lead",
    5: "Director"
})

# ── Salary range bands ────────────────────────────────────────────────────────
df["SalaryBand"] = pd.cut(
    df["MonthlyIncome"],
    bins=[0, 3000, 6000, 10000, 20000],
    labels=["Low (<3K)", "Medium (3-6K)", "High (6-10K)", "Very High (10K+)"]
)

# ── Age bands ─────────────────────────────────────────────────────────────────
df["AgeBand"] = pd.cut(
    df["Age"],
    bins=[17, 25, 35, 45, 55, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "55+"]
)

# ── Distance band ─────────────────────────────────────────────────────────────
df["DistanceBand"] = pd.cut(
    df["DistanceFromHome"],
    bins=[0, 5, 15, 29],
    labels=["Near (1-5)", "Medium (6-15)", "Far (16+)"]
)

# ── Satisfaction labels ───────────────────────────────────────────────────────
satisfaction_map = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
df["JobSatisfactionLabel"]         = df["JobSatisfaction"].map(satisfaction_map)
df["EnvironmentSatisfactionLabel"] = df["EnvironmentSatisfaction"].map(satisfaction_map)
df["WorkLifeBalanceLabel"]         = df["WorkLifeBalance"].map({
    1: "Bad", 2: "Good", 3: "Better", 4: "Best"
})

# ── Performance label ─────────────────────────────────────────────────────────
df["PerformanceLabel"] = df["PerformanceRating"].map({
    1: "Low", 2: "Good", 3: "Excellent", 4: "Outstanding"
})

# ── Overtime flag ─────────────────────────────────────────────────────────────
df["OvertimeBinary"] = (df["OverTime"] == "Yes").astype(int)

# ── Years since last promotion band ──────────────────────────────────────────
df["PromotionRecency"] = pd.cut(
    df["YearsSinceLastPromotion"],
    bins=[-1, 0, 2, 5, 100],
    labels=["Just Promoted", "1-2 yrs", "3-5 yrs", "5+ yrs"]
)

# ── Attrition risk score (simple weighted formula) ────────────────────────────
# Higher = more at risk. Used for the What-If model.
df["AttritionRiskScore"] = (
    (5 - df["JobSatisfaction"]) * 0.25 +
    (5 - df["EnvironmentSatisfaction"]) * 0.20 +
    (5 - df["WorkLifeBalance"]) * 0.15 +
    df["OvertimeBinary"] * 0.20 +
    (df["YearsSinceLastPromotion"] / df["YearsSinceLastPromotion"].max()) * 0.10 +
    (df["DistanceFromHome"] / df["DistanceFromHome"].max()) * 0.10
).round(3)

# ── Monthly income in thousands (cleaner for charts) ─────────────────────────
df["MonthlyIncomeK"] = (df["MonthlyIncome"] / 1000).round(2)

# ── Total compensation estimate (monthly * 12) ───────────────────────────────
df["AnnualIncome"] = df["MonthlyIncome"] * 12

# ── Reorder columns for readability ──────────────────────────────────────────
key_cols = [
    "EmployeeNumber", "Age", "AgeBand", "Gender", "MaritalStatus",
    "Department", "JobRole", "JobLevel", "SeniorityBand",
    "MonthlyIncome", "MonthlyIncomeK", "AnnualIncome", "SalaryBand",
    "Attrition", "AttritionBinary", "AttritionRiskScore",
    "YearsAtCompany", "TenureBand", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "PromotionRecency",
    "YearsWithCurrManager", "NumCompaniesWorked",
    "TotalWorkingYears", "TrainingTimesLastYear",
    "JobSatisfaction", "JobSatisfactionLabel",
    "EnvironmentSatisfaction", "EnvironmentSatisfactionLabel",
    "WorkLifeBalance", "WorkLifeBalanceLabel",
    "PerformanceRating", "PerformanceLabel",
    "OverTime", "OvertimeBinary",
    "BusinessTravel", "DistanceFromHome", "DistanceBand",
    "Education", "EducationField",
    "StockOptionLevel", "PercentSalaryHike",
    "RelationshipSatisfaction", "JobInvolvement"
]

df = df[key_cols]

# ── Save cleaned file ─────────────────────────────────────────────────────────
out_path = os.path.join("data", "hr_cleaned.csv")
df.to_csv(out_path, index=False)

print(f"✅  Cleaned data saved to: {out_path}")
print(f"    Rows: {len(df)} | Columns: {len(df.columns)}")
print(f"\nAttrition breakdown:")
print(df["Attrition"].value_counts())
print(f"\nAttrition rate: {df['AttritionBinary'].mean()*100:.1f}%")
print(f"\nDepartment breakdown:")
print(df["Department"].value_counts())
print(f"\nSalary bands:")
print(df["SalaryBand"].value_counts())
print(f"\nTenure bands:")
print(df["TenureBand"].value_counts())
print("\n✅  Data preparation complete. Ready to load into Power BI.")