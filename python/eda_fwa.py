"""
Healthcare Fraud, Waste & Abuse (FWA) Analytics
Stage 2: Exploratory Data Analysis (EDA)

Why are we doing EDA?
EDA helps us understand the cleaned healthcare data before we
build FWA indicators and the Power BI dashboard.

This script:
- Loads the cleaned dataset
- Checks shape, data types, missing values and duplicates
- Studies provider, procedure and service patterns
- Studies reimbursement and charge patterns
- Creates temporary EDA metrics
- Creates charts and summary CSV files
- Prints important observations

Important:
This script does NOT create final FWA risk scores.
It does NOT label providers as fraudulent.
It does NOT modify the cleaned dataset.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLEANED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "CMSData_FWA_cleaned.csv"
)

IMAGES_DIR = PROJECT_ROOT / "images"
EDA_DIR = IMAGES_DIR / "eda"

EDA_DIR.mkdir(parents=True, exist_ok=True)

if not CLEANED_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned dataset not found:\n{CLEANED_FILE}\n\n"
        "Run clean_fwa_data.py first."
    )


# ============================================================
# 2. LOAD CLEANED DATA
# ============================================================

print("=" * 70)
print("HEALTHCARE FWA ANALYTICS - EDA")
print("=" * 70)
print(f"Loading: {CLEANED_FILE}")
print()

df = pd.read_csv(
    CLEANED_FILE,
    low_memory=False
)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")
print()


# ============================================================
# 3. BASIC DATASET INFORMATION
# ============================================================

print("=" * 70)
print("1. BASIC DATASET INFORMATION")
print("=" * 70)

print("\nColumn names:")
for column in df.columns:
    print(f" - {column}")

print("\nData types:")
print(df.dtypes)

print("\nMemory usage:")
print(f"{df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB")


# Save data types.
dtype_summary = pd.DataFrame({
    "column": df.columns,
    "dtype": df.dtypes.astype(str).values
})

dtype_summary.to_csv(
    EDA_DIR / "column_data_types.csv",
    index=False
)


# ============================================================
# 4. MISSING VALUE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("2. MISSING VALUE ANALYSIS")
print("=" * 70)

missing_summary = pd.DataFrame({
    "column": df.columns,
    "missing_count": df.isna().sum().values
})

missing_summary["missing_percentage"] = (
    missing_summary["missing_count"] / len(df) * 100
).round(2)

missing_summary = missing_summary.sort_values(
    "missing_count",
    ascending=False
)

print(missing_summary.to_string(index=False))

missing_summary.to_csv(
    EDA_DIR / "missing_values_summary.csv",
    index=False
)


# ============================================================
# 5. DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 70)
print("3. DUPLICATE CHECK")
print("=" * 70)

duplicate_count = int(df.duplicated().sum())

print(f"Exact duplicate rows: {duplicate_count:,}")


# ============================================================
# 6. UNIQUE VALUE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. UNIQUE VALUE ANALYSIS")
print("=" * 70)

unique_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_State_Abrvtn",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
]

unique_summary_rows = []

for column in unique_columns:
    unique_count = df[column].nunique(dropna=True)

    unique_summary_rows.append({
        "column": column,
        "unique_values": unique_count
    })

    print(f"{column}: {unique_count:,}")

unique_summary = pd.DataFrame(unique_summary_rows)

unique_summary.to_csv(
    EDA_DIR / "unique_values_summary.csv",
    index=False
)


# ============================================================
# 7. TEMPORARY EDA METRICS
# ============================================================
# These are created only for exploration.
# They are NOT saved back into the cleaned dataset.

df_eda = df.copy()

df_eda["Services_Per_Beneficiary"] = np.where(
    df_eda["Tot_Benes"] > 0,
    df_eda["Tot_Srvcs"] / df_eda["Tot_Benes"],
    np.nan
)

df_eda["Payment_to_Charge_Ratio"] = np.where(
    df_eda["Avg_Sbmtd_Chrg"] > 0,
    df_eda["Avg_Mdcr_Pymt_Amt"] / df_eda["Avg_Sbmtd_Chrg"],
    np.nan
)


# ============================================================
# 8. NUMERIC SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("5. NUMERIC SUMMARY")
print("=" * 70)

numeric_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
    "Services_Per_Beneficiary",
    "Payment_to_Charge_Ratio",
]

numeric_summary = (
    df_eda[numeric_columns]
    .describe()
    .T
)

print(numeric_summary)

numeric_summary.to_csv(
    EDA_DIR / "numeric_summary.csv"
)


# ============================================================
# 9. PROVIDER TYPE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("6. PROVIDER TYPE ANALYSIS")
print("=" * 70)

provider_type_summary = (
    df.groupby("Rndrng_Prvdr_Type")
    .agg(
        Provider_Count=("Rndrng_NPI", "nunique"),
        Service_Records=("HCPCS_Cd", "size"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Total_Services=("Tot_Srvcs", "sum"),
        Avg_Services_Per_Record=("Tot_Srvcs", "mean"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
    )
    .sort_values("Total_Services", ascending=False)
)

print(provider_type_summary.head(15).to_string())

provider_type_summary.to_csv(
    EDA_DIR / "provider_type_summary.csv"
)


# ============================================================
# 10. PROCEDURE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("7. PROCEDURE ANALYSIS")
print("=" * 70)

procedure_summary = (
    df.groupby(["HCPCS_Cd", "HCPCS_Desc"], dropna=False)
    .agg(
        Provider_Count=("Rndrng_NPI", "nunique"),
        Service_Records=("HCPCS_Cd", "size"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Total_Services=("Tot_Srvcs", "sum"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
        Avg_Allowed_Amount=("Avg_Mdcr_Alowd_Amt", "mean"),
    )
    .sort_values("Total_Services", ascending=False)
)

print(procedure_summary.head(15).to_string())

procedure_summary.to_csv(
    EDA_DIR / "procedure_summary.csv"
)


# ============================================================
# 11. STATE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("8. STATE ANALYSIS")
print("=" * 70)

state_summary = (
    df.groupby("Rndrng_Prvdr_State_Abrvtn", dropna=False)
    .agg(
        Provider_Count=("Rndrng_NPI", "nunique"),
        Total_Services=("Tot_Srvcs", "sum"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
    )
    .sort_values("Total_Services", ascending=False)
)

print(state_summary.head(15).to_string())

state_summary.to_csv(
    EDA_DIR / "state_summary.csv"
)


# ============================================================
# 12. PLACE OF SERVICE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("9. PLACE OF SERVICE ANALYSIS")
print("=" * 70)

place_summary = (
    df.groupby("Place_Of_Srvc", dropna=False)
    .agg(
        Service_Records=("Place_Of_Srvc", "size"),
        Total_Services=("Tot_Srvcs", "sum"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
    )
    .sort_values("Total_Services", ascending=False)
)

print(place_summary.to_string())

place_summary.to_csv(
    EDA_DIR / "place_of_service_summary.csv"
)


# ============================================================
# 13. TOP PROVIDERS BY SERVICE VOLUME
# ============================================================

print("\n" + "=" * 70)
print("10. TOP PROVIDERS BY SERVICE VOLUME")
print("=" * 70)

top_providers = (
    df.groupby(
        ["Rndrng_NPI", "Rndrng_Prvdr_Last_Org_Name", "Rndrng_Prvdr_Type"],
        dropna=False
    )
    .agg(
        Service_Records=("HCPCS_Cd", "size"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Total_Services=("Tot_Srvcs", "sum"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
    )
    .sort_values("Total_Services", ascending=False)
    .head(25)
)

print(top_providers.to_string())

top_providers.to_csv(
    EDA_DIR / "top_25_providers_by_service_volume.csv"
)


# ============================================================
# 14. TEMPORARY METRIC EXTREMES
# ============================================================

print("\n" + "=" * 70)
print("11. TEMPORARY METRIC EXTREMES")
print("=" * 70)

# Remove infinite values before calculating percentiles.
df_eda["Services_Per_Beneficiary"] = (
    df_eda["Services_Per_Beneficiary"]
    .replace([np.inf, -np.inf], np.nan)
)

df_eda["Payment_to_Charge_Ratio"] = (
    df_eda["Payment_to_Charge_Ratio"]
    .replace([np.inf, -np.inf], np.nan)
)

print("\nServices per beneficiary:")
print(
    df_eda["Services_Per_Beneficiary"]
    .describe(percentiles=[0.50, 0.75, 0.90, 0.95, 0.99])
)

print("\nPayment-to-charge ratio:")
print(
    df_eda["Payment_to_Charge_Ratio"]
    .describe(percentiles=[0.50, 0.75, 0.90, 0.95, 0.99])
)


# ============================================================
# 15. CHART 1 - SERVICE VOLUME BY PROVIDER TYPE
# ============================================================

chart_data = provider_type_summary.head(10).sort_values(
    "Total_Services"
)

plt.figure(figsize=(11, 7))
plt.barh(
    chart_data.index.astype(str),
    chart_data["Total_Services"]
)
plt.xlabel("Total Services")
plt.ylabel("Provider Type")
plt.title("Top Provider Types by Total Service Volume")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "01_provider_type_service_volume.png",
    dpi=150
)
plt.close()


# ============================================================
# 16. CHART 2 - TOP PROCEDURES
# ============================================================

chart_data = procedure_summary.head(10).sort_values(
    "Total_Services"
)

labels = chart_data.index.get_level_values("HCPCS_Cd").astype(str)

plt.figure(figsize=(10, 6))
plt.barh(
    labels,
    chart_data["Total_Services"]
)
plt.xlabel("Total Services")
plt.ylabel("HCPCS Code")
plt.title("Top Procedures by Service Volume")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "02_top_procedures_by_service_volume.png",
    dpi=150
)
plt.close()


# ============================================================
# 17. CHART 3 - STATE SERVICE VOLUME
# ============================================================

chart_data = state_summary.head(15).sort_values(
    "Total_Services"
)

plt.figure(figsize=(11, 7))
plt.barh(
    chart_data.index.astype(str),
    chart_data["Total_Services"]
)
plt.xlabel("Total Services")
plt.ylabel("State")
plt.title("Top States by Total Service Volume")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "03_state_service_volume.png",
    dpi=150
)
plt.close()


# ============================================================
# 18. CHART 4 - SERVICES PER BENEFICIARY DISTRIBUTION
# ============================================================

plot_data = df_eda["Services_Per_Beneficiary"].dropna()

# Limit the display to the 99th percentile so extreme outliers
# do not make the distribution unreadable.
upper_limit = plot_data.quantile(0.99)

plot_data = plot_data[plot_data <= upper_limit]

plt.figure(figsize=(10, 6))
plt.hist(
    plot_data,
    bins=50
)
plt.xlabel("Services per Beneficiary")
plt.ylabel("Number of Records")
plt.title("Distribution of Services per Beneficiary")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "04_services_per_beneficiary_distribution.png",
    dpi=150
)
plt.close()


# ============================================================
# 19. CHART 5 - PAYMENT TO CHARGE RATIO
# ============================================================

plot_data = df_eda["Payment_to_Charge_Ratio"].dropna()

upper_limit = plot_data.quantile(0.99)

plot_data = plot_data[
    (plot_data >= 0) &
    (plot_data <= upper_limit)
]

plt.figure(figsize=(10, 6))
plt.hist(
    plot_data,
    bins=50
)
plt.xlabel("Medicare Payment / Submitted Charge")
plt.ylabel("Number of Records")
plt.title("Distribution of Payment-to-Charge Ratio")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "05_payment_to_charge_ratio_distribution.png",
    dpi=150
)
plt.close()


# ============================================================
# 20. CHART 6 - PAYMENT VS SUBMITTED CHARGE
# ============================================================

plot_data = df_eda[
    [
        "Avg_Sbmtd_Chrg",
        "Avg_Mdcr_Pymt_Amt"
    ]
].dropna()

# Remove extreme values only for visualization.
charge_limit = plot_data["Avg_Sbmtd_Chrg"].quantile(0.99)
payment_limit = plot_data["Avg_Mdcr_Pymt_Amt"].quantile(0.99)

plot_data = plot_data[
    (plot_data["Avg_Sbmtd_Chrg"] <= charge_limit) &
    (plot_data["Avg_Mdcr_Pymt_Amt"] <= payment_limit)
]

plt.figure(figsize=(9, 7))
plt.scatter(
    plot_data["Avg_Sbmtd_Chrg"],
    plot_data["Avg_Mdcr_Pymt_Amt"],
    alpha=0.25,
    s=10
)
plt.xlabel("Average Submitted Charge")
plt.ylabel("Average Medicare Payment")
plt.title("Submitted Charges vs Medicare Payments")
plt.tight_layout()
plt.savefig(
    EDA_DIR / "06_submitted_charge_vs_medicare_payment.png",
    dpi=150
)
plt.close()


# ============================================================
# 21. EDA COMPLETION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 70)

print(f"EDA files saved in:")
print(EDA_DIR)

print("\nCreated summary files:")
summary_files = sorted(EDA_DIR.glob("*.csv"))

for file in summary_files:
    print(f" - {file.name}")

print("\nCreated charts:")
chart_files = sorted(EDA_DIR.glob("*.png"))

for file in chart_files:
    print(f" - {file.name}")

print("\nIMPORTANT:")
print("The EDA only helps us understand the dataset.")
print("No provider has been labeled as fraudulent.")
print("No final FWA risk score has been created.")
print("The cleaned CSV was not modified.")

print("=" * 70)