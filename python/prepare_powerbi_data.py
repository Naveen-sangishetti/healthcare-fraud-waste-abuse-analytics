"""
Healthcare Fraud, Waste & Abuse (FWA) Analytics
Stage 4: Prepare Power BI datasets
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POWERBI_DIR = PROCESSED_DIR / "powerbi"
POWERBI_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_FILE = PROCESSED_DIR / "FWA_analysis_dataset.csv"
PROVIDER_FILE = PROCESSED_DIR / "provider_risk_summary.csv"
FLAGGED_FILE = PROCESSED_DIR / "fwa_flagged_records.csv"

for file in [ANALYSIS_FILE, PROVIDER_FILE, FLAGGED_FILE]:
    if not file.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{file}\n"
            "Run python/fwa_analysis.py first."
        )

print("=" * 75)
print("PREPARING POWER BI DATASETS")
print("=" * 75)

analysis = pd.read_csv(ANALYSIS_FILE, low_memory=False)
provider = pd.read_csv(PROVIDER_FILE, low_memory=False)
flagged = pd.read_csv(FLAGGED_FILE, low_memory=False)

print(f"Full analysis rows : {len(analysis):,}")
print(f"Provider rows      : {len(provider):,}")
print(f"Flagged rows       : {len(flagged):,}")
print()

# ------------------------------------------------------------
# 1. FWA OVERVIEW TABLE
# ------------------------------------------------------------

overview_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_State_Abrvtn",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
    "Services_Per_Beneficiary",
    "Payment_to_Charge_Ratio",
    "Allowed_to_Charge_Ratio",
    "FWA_Indicator_Count",
    "FWA_Risk_Score",
    "FWA_Risk_Level",
    "Investigation_Reason",
]

overview_columns = [c for c in overview_columns if c in analysis.columns]
fwa_overview = analysis[overview_columns].copy()

fwa_overview.to_csv(
    POWERBI_DIR / "fwa_overview.csv",
    index=False
)

# ------------------------------------------------------------
# 2. PROVIDER RISK TABLE
# ------------------------------------------------------------

provider_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_State_Abrvtn",
    "Service_Records",
    "Procedure_Count",
    "Total_Beneficiaries",
    "Total_Services",
    "Avg_Medicare_Payment",
    "Avg_Submitted_Charge",
    "Avg_Services_Per_Beneficiary",
    "Avg_Payment_to_Charge",
    "Max_FWA_Indicator_Count",
    "Flagged_Service_Records",
    "High_Risk_Service_Records",
    "Average_FWA_Risk_Score",
    "Flag_Rate",
    "Provider_Risk_Score",
    "Provider_Risk_Level",
]

provider_columns = [c for c in provider_columns if c in provider.columns]
provider_risk = provider[provider_columns].copy()

provider_risk.to_csv(
    POWERBI_DIR / "provider_risk.csv",
    index=False
)

# ------------------------------------------------------------
# 3. INVESTIGATION TABLE
# ------------------------------------------------------------

investigation_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_State_Abrvtn",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "Place_Of_Srvc",
    "Tot_Benes",
    "Tot_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
    "Services_Per_Beneficiary",
    "Payment_to_Charge_Ratio",
    "Peer_Provider_Count",
    "Peer_Avg_Services",
    "Peer_Avg_Services_Per_Beneficiary",
    "Peer_Avg_Payment",
    "Peer_Avg_Payment_to_Charge",
    "Services_vs_Peer",
    "Services_Per_Beneficiary_vs_Peer",
    "Payment_vs_Peer",
    "Payment_to_Charge_vs_Peer",
    "Utilization_Percentile",
    "Procedure_Service_Share",
    "Indicator_High_Service_Frequency",
    "Indicator_High_Utilization_Per_Beneficiary",
    "Indicator_High_Utilization_Percentile",
    "Indicator_Reimbursement_Deviation",
    "Indicator_Payment_Pattern_Deviation",
    "Indicator_High_Procedure_Concentration",
    "FWA_Indicator_Count",
    "FWA_Risk_Score",
    "FWA_Risk_Level",
    "Investigation_Reason",
]

investigation_columns = [c for c in investigation_columns if c in flagged.columns]
fwa_investigation = flagged[investigation_columns].copy()

fwa_investigation.to_csv(
    POWERBI_DIR / "fwa_investigation.csv",
    index=False
)

# ------------------------------------------------------------
# 4. DASHBOARD SUMMARY
# ------------------------------------------------------------

summary = pd.DataFrame({
    "Metric": [
        "Total service records",
        "Unique providers",
        "Unique procedures",
        "Total services",
        "Flagged investigation records",
        "High review records",
        "Medium review records",
        "Low review records",
        "No flag records",
    ],
    "Value": [
        len(analysis),
        analysis["Rndrng_NPI"].nunique(),
        analysis["HCPCS_Cd"].nunique(),
        analysis["Tot_Srvcs"].sum(),
        len(flagged),
        int((analysis["FWA_Risk_Level"] == "High Review").sum()),
        int((analysis["FWA_Risk_Level"] == "Medium Review").sum()),
        int((analysis["FWA_Risk_Level"] == "Low Review").sum()),
        int((analysis["FWA_Risk_Level"] == "No Flag").sum()),
    ],
})

summary.to_csv(
    POWERBI_DIR / "dashboard_summary.csv",
    index=False
)

print("=" * 75)
print("POWER BI DATA PREPARATION COMPLETED")
print("=" * 75)
print(f"Output folder: {POWERBI_DIR}")
print()
print("Created:")
print(" - fwa_overview.csv")
print(" - provider_risk.csv")
print(" - fwa_investigation.csv")
print(" - dashboard_summary.csv")
print()
print(f"FWA overview rows  : {len(fwa_overview):,}")
print(f"Provider rows      : {len(provider_risk):,}")
print(f"Investigation rows : {len(fwa_investigation):,}")
print()
print("Power BI datasets are ready.")
print("=" * 75)