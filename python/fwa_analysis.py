"""
Healthcare Fraud, Waste & Abuse (FWA) Analytics
Stage 3: FWA Indicator Analysis

Purpose:
    Convert the cleaned CMS provider/service data into an analytical
    dataset containing provider behavior metrics, peer comparisons,
    FWA indicators, and a transparent provider risk score.

Important:
    - This is an analytical screening model, not proof of fraud.
    - "Flagged" means the record is unusual relative to defined peers.
    - Peer groups are based on Provider Type + HCPCS Code + Place of Service.
    - No individual claim-level fraud is inferred because this dataset
      is provider/service level rather than transaction-level claims.

Outputs:
    data/processed/FWA_analysis_dataset.csv
    data/processed/provider_risk_summary.csv
    data/processed/fwa_flagged_records.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "CMSData_FWA_cleaned.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_FILE = OUTPUT_DIR / "FWA_analysis_dataset.csv"
PROVIDER_FILE = OUTPUT_DIR / "provider_risk_summary.csv"
FLAGGED_FILE = OUTPUT_DIR / "fwa_flagged_records.csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned dataset not found:\n{INPUT_FILE}\n\n"
        "Run clean_fwa_data.py first."
    )

print("=" * 75)
print("HEALTHCARE FWA ANALYTICS - FWA INDICATOR ANALYSIS")
print("=" * 75)
print(f"Loading: {INPUT_FILE}")
print()

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print()


# ============================================================
# 3. STANDARDIZE REQUIRED FIELDS
# ============================================================

required_columns = [
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
]

missing_required = [
    column for column in required_columns
    if column not in df.columns
]

if missing_required:
    raise ValueError(
        "Required columns are missing:\n"
        + "\n".join(f" - {column}" for column in missing_required)
    )


# Numeric conversion for safety.
numeric_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 4. CREATE BASE BEHAVIOR METRICS
# ============================================================

# How many services were performed per beneficiary for this
# provider/procedure record?
df["Services_Per_Beneficiary"] = np.where(
    df["Tot_Benes"] > 0,
    df["Tot_Srvcs"] / df["Tot_Benes"],
    np.nan
)

# Average payment as a share of submitted charge.
# This describes reimbursement behavior; it is not an overpayment
# calculation and is therefore distinct from the previous project.
df["Payment_to_Charge_Ratio"] = np.where(
    df["Avg_Sbmtd_Chrg"] > 0,
    df["Avg_Mdcr_Pymt_Amt"] / df["Avg_Sbmtd_Chrg"],
    np.nan
)

# Allowed-to-charge relationship.
df["Allowed_to_Charge_Ratio"] = np.where(
    df["Avg_Sbmtd_Chrg"] > 0,
    df["Avg_Mdcr_Alowd_Amt"] / df["Avg_Sbmtd_Chrg"],
    np.nan
)


# ============================================================
# 5. DEFINE PEER GROUPS
# ============================================================
# A provider is compared primarily with other providers billing
# the same procedure in the same place-of-service and provider type.
#
# This reduces false comparisons such as comparing an ambulance
# provider with a primary-care physician.

peer_columns = [
    "Rndrng_Prvdr_Type",
    "HCPCS_Cd",
    "Place_Of_Srvc",
]

# Minimum peer-group support.
MIN_PEER_ROWS = 10


# ============================================================
# 6. PEER BASELINES
# ============================================================

peer = (
    df.groupby(peer_columns, dropna=False)
    .agg(
        Peer_Record_Count=("Rndrng_NPI", "size"),
        Peer_Avg_Services=("Tot_Srvcs", "mean"),
        Peer_Avg_Services_Per_Beneficiary=(
            "Services_Per_Beneficiary",
            "mean"
        ),
        Peer_Median_Services_Per_Beneficiary=(
            "Services_Per_Beneficiary",
            "median"
        ),
        Peer_Avg_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Peer_Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
        Peer_Avg_Payment_to_Charge=("Payment_to_Charge_Ratio", "mean"),
    )
    .reset_index()
)

df = df.merge(
    peer,
    on=peer_columns,
    how="left"
)


# ============================================================
# 7. PROVIDER-LEVEL SUMMARY
# ============================================================
# These metrics describe the provider's overall behavior across
# all procedures in the dataset.

provider_summary = (
    df.groupby(
        [
            "Rndrng_NPI",
            "Rndrng_Prvdr_Last_Org_Name",
            "Rndrng_Prvdr_Type",
            "Rndrng_Prvdr_State_Abrvtn",
        ],
        dropna=False
    )
    .agg(
        Provider_Service_Records=("HCPCS_Cd", "size"),
        Provider_Procedure_Count=("HCPCS_Cd", "nunique"),
        Provider_Total_Beneficiaries=("Tot_Benes", "sum"),
        Provider_Total_Services=("Tot_Srvcs", "sum"),
        Provider_Avg_Services_Per_Record=("Tot_Srvcs", "mean"),
        Provider_Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Provider_Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
        Provider_Avg_Payment_to_Charge=(
            "Payment_to_Charge_Ratio",
            "mean"
        ),
    )
    .reset_index()
)


# Provider-wide services per beneficiary.
provider_summary["Provider_Services_Per_Beneficiary"] = np.where(
    provider_summary["Provider_Total_Beneficiaries"] > 0,
    provider_summary["Provider_Total_Services"]
    / provider_summary["Provider_Total_Beneficiaries"],
    np.nan
)

df = df.merge(
    provider_summary[
        [
            "Rndrng_NPI",
            "Provider_Service_Records",
            "Provider_Procedure_Count",
            "Provider_Total_Beneficiaries",
            "Provider_Total_Services",
            "Provider_Avg_Services_Per_Record",
            "Provider_Avg_Medicare_Payment",
            "Provider_Avg_Submitted_Charge",
            "Provider_Avg_Payment_to_Charge",
            "Provider_Services_Per_Beneficiary",
        ]
    ],
    on="Rndrng_NPI",
    how="left"
)


# ============================================================
# 8. PEER DEVIATION METRICS
# ============================================================

# Require at least MIN_PEER_ROWS in a peer group before using
# peer comparisons.

valid_peer = df["Peer_Record_Count"] >= MIN_PEER_ROWS


df["Services_vs_Peer"] = np.where(
    valid_peer & (df["Peer_Avg_Services"] > 0),
    df["Tot_Srvcs"] / df["Peer_Avg_Services"],
    np.nan
)

df["Services_Per_Beneficiary_vs_Peer"] = np.where(
    valid_peer & (df["Peer_Avg_Services_Per_Beneficiary"] > 0),
    df["Services_Per_Beneficiary"]
    / df["Peer_Avg_Services_Per_Beneficiary"],
    np.nan
)

df["Payment_vs_Peer"] = np.where(
    valid_peer & (df["Peer_Avg_Payment"] > 0),
    df["Avg_Mdcr_Pymt_Amt"] / df["Peer_Avg_Payment"],
    np.nan
)

df["Payment_to_Charge_vs_Peer"] = np.where(
    valid_peer & (df["Peer_Avg_Payment_to_Charge"] > 0),
    df["Payment_to_Charge_Ratio"]
    / df["Peer_Avg_Payment_to_Charge"],
    np.nan
)


# ============================================================
# 9. PROCEDURE UTILIZATION PERCENTILE
# ============================================================
# Percentile within the same Provider Type + HCPCS + Place of
# Service peer group.

def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(
        method="average",
        pct=True
    )

df["Utilization_Percentile"] = np.nan

valid_peer_indices = df.index[valid_peer]

if len(valid_peer_indices) > 0:
    df.loc[valid_peer_indices, "Utilization_Percentile"] = (
        df.loc[valid_peer_indices]
        .groupby(peer_columns, dropna=False)["Tot_Srvcs"]
        .transform(percentile_rank)
    )


# ============================================================
# 10. DEFINE FWA INDICATORS
# ============================================================
# Thresholds are deliberately conservative and transparent.
#
# These indicators identify unusual behavior for further review.
# They do not prove fraud, waste, or abuse.

# Indicator A:
# Service frequency is at least 3x the peer average.
df["Indicator_High_Service_Frequency"] = (
    valid_peer
    & (df["Services_vs_Peer"] >= 4)
)


# Indicator B:
# Services per beneficiary is at least 2x the peer average.
df["Indicator_High_Utilization_Per_Beneficiary"] = (
    valid_peer
    & (df["Services_Per_Beneficiary_vs_Peer"] >= 3)
)


# Indicator C:
# Provider/procedure service volume is in the top 95% of the
# peer distribution.
df["Indicator_High_Utilization_Percentile"] = (
    valid_peer
    & (df["Utilization_Percentile"] >= 0.99)
)


# Indicator D:
# Payment amount is substantially above the peer average.
# This is reimbursement-pattern analysis, NOT overpayment detection.
df["Indicator_Reimbursement_Deviation"] = (
    valid_peer
    & (df["Payment_vs_Peer"] >= 3)
)


# Indicator E:
# Provider's payment-to-charge ratio is substantially different
# from the peer baseline.
df["Indicator_Payment_Pattern_Deviation"] = (
    valid_peer
    & (
        (df["Payment_to_Charge_vs_Peer"] >= 2.5)
        | (df["Payment_to_Charge_vs_Peer"] <= 0.40)
    )
)


# ============================================================
# 11. PROCEDURE CONCENTRATION
# ============================================================
# Calculate what share of a provider's service volume is represented
# by the current procedure.

provider_service_totals = (
    df.groupby("Rndrng_NPI", dropna=False)["Tot_Srvcs"]
    .sum()
    .rename("Provider_Total_Services_For_Concentration")
)

df = df.join(
    provider_service_totals,
    on="Rndrng_NPI"
)

df["Procedure_Service_Share"] = np.where(
    df["Provider_Total_Services_For_Concentration"] > 0,
    df["Tot_Srvcs"]
    / df["Provider_Total_Services_For_Concentration"],
    np.nan
)

# High concentration means this procedure contributes at least
# 50% of the provider's service volume.
df["Indicator_High_Procedure_Concentration"] = (
    (df["Provider_Service_Records"] >= 3)
    & (df["Procedure_Service_Share"] >= 0.75)
)


# ============================================================
# 12. FWA INDICATOR COUNT
# ============================================================

indicator_columns = [
    "Indicator_High_Service_Frequency",
    "Indicator_High_Utilization_Per_Beneficiary",
    "Indicator_High_Utilization_Percentile",
    "Indicator_Reimbursement_Deviation",
    "Indicator_Payment_Pattern_Deviation",
    "Indicator_High_Procedure_Concentration",
]

df["FWA_Indicator_Count"] = (
    df[indicator_columns]
    .astype(int)
    .sum(axis=1)
)


# ============================================================
# 13. TRANSPARENT RISK SCORE
# ============================================================
# Each indicator contributes equally.
# Six indicators -> maximum score 100.

df["FWA_Risk_Score"] = (
    df["FWA_Indicator_Count"] / len(indicator_columns) * 100
).round(1)


def assign_risk_level(indicator_count: int) -> str:
    if indicator_count >= 5:
        return "Critical Review"
    if indicator_count >= 4:
        return "High Review"
    if indicator_count >= 2:
        return "Medium Review"
    if indicator_count == 1:
        return "Low Review"
    return "No Flag"


df["FWA_Risk_Level"] = df["FWA_Indicator_Count"].apply(
    assign_risk_level
)


# ============================================================
# 14. INVESTIGATION REASON
# ============================================================

def build_reason(row: pd.Series) -> str:
    reasons = []

    if row["Indicator_High_Service_Frequency"]:
        reasons.append("High service frequency vs peers")

    if row["Indicator_High_Utilization_Per_Beneficiary"]:
        reasons.append("High services per beneficiary vs peers")

    if row["Indicator_High_Utilization_Percentile"]:
        reasons.append("High utilization percentile")

    if row["Indicator_Reimbursement_Deviation"]:
        reasons.append("High reimbursement vs peers")

    if row["Indicator_Payment_Pattern_Deviation"]:
        reasons.append("Unusual payment-to-charge pattern")

    if row["Indicator_High_Procedure_Concentration"]:
        reasons.append("High procedure concentration")

    if not reasons:
        return "No FWA indicator triggered"

    return "; ".join(reasons)


df["Investigation_Reason"] = df.apply(
    build_reason,
    axis=1
)


# ============================================================
# 15. PROVIDER RISK SUMMARY
# ============================================================
# Roll the service-level signals up to the provider level.

provider_risk = (
    df.groupby(
        [
            "Rndrng_NPI",
            "Rndrng_Prvdr_Last_Org_Name",
            "Rndrng_Prvdr_Type",
            "Rndrng_Prvdr_State_Abrvtn",
        ],
        dropna=False
    )
    .agg(
        Service_Records=("HCPCS_Cd", "size"),
        Procedure_Count=("HCPCS_Cd", "nunique"),
        Total_Beneficiaries=("Tot_Benes", "sum"),
        Total_Services=("Tot_Srvcs", "sum"),
        Avg_Medicare_Payment=("Avg_Mdcr_Pymt_Amt", "mean"),
        Avg_Submitted_Charge=("Avg_Sbmtd_Chrg", "mean"),
        Avg_Services_Per_Beneficiary=(
            "Services_Per_Beneficiary",
            "mean"
        ),
        Avg_Payment_to_Charge=(
            "Payment_to_Charge_Ratio",
            "mean"
        ),
        Max_FWA_Indicator_Count=(
            "FWA_Indicator_Count",
            "max"
        ),
        Flagged_Service_Records=(
            "FWA_Indicator_Count",
            lambda x: int((x > 0).sum())
        ),
        High_Risk_Service_Records=(
            "FWA_Indicator_Count",
            lambda x: int((x >= 4).sum())
        ),
        Average_FWA_Risk_Score=(
            "FWA_Risk_Score",
            "mean"
        ),
    )
    .reset_index()
)


provider_risk["Flag_Rate"] = np.where(
    provider_risk["Service_Records"] >= 3,
    provider_risk["Flagged_Service_Records"]
    / provider_risk["Service_Records"],
    0
)

provider_risk["Flag_Rate"] = (
    provider_risk["Flag_Rate"] * 100
).round(2)


# Provider score:
# emphasize both intensity of risk and percentage of service records
# that triggered an indicator, while keeping the score transparent.

provider_risk["Provider_Risk_Score"] = (
    (
        provider_risk["Average_FWA_Risk_Score"] * 0.70
    )
    +
    (
        provider_risk["Flag_Rate"].clip(upper=100) * 0.30
    )
).round(1)


def provider_risk_level(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    if score > 0:
        return "Low"
    return "No Flag"


provider_risk["Provider_Risk_Level"] = (
    provider_risk["Provider_Risk_Score"]
    .apply(provider_risk_level)
)


provider_risk = provider_risk.sort_values(
    [
        "Provider_Risk_Score",
        "Flagged_Service_Records",
        "Total_Services",
    ],
    ascending=False
)


# ============================================================
# 16. FLAGGED RECORDS FOR INVESTIGATION
# ============================================================

flagged = df[
    df["FWA_Indicator_Count"] > 2
].copy()

flagged = flagged.sort_values(
    [
        "FWA_Risk_Score",
        "FWA_Indicator_Count",
        "Tot_Srvcs",
    ],
    ascending=False
)


# ============================================================
# 17. SAVE OUTPUTS
# ============================================================

# Keep the full analytical dataset for Power BI / SQL preparation.
df.to_csv(
    ANALYSIS_FILE,
    index=False
)

provider_risk.to_csv(
    PROVIDER_FILE,
    index=False
)

flagged.to_csv(
    FLAGGED_FILE,
    index=False
)


# ============================================================
# 18. REPORT
# ============================================================

print("=" * 75)
print("FWA ANALYSIS COMPLETED")
print("=" * 75)

print(f"Analysis dataset : {ANALYSIS_FILE}")
print(f"Provider summary : {PROVIDER_FILE}")
print(f"Flagged records  : {FLAGGED_FILE}")
print()

print(f"Total records analyzed : {len(df):,}")
print(
    f"Flagged service records: "
    f"{len(flagged):,} "
    f"({len(flagged) / len(df) * 100:.2f}%)"
)

print()
print("Risk-level distribution:")

risk_distribution = (
    df["FWA_Risk_Level"]
    .value_counts()
)

for level, count in risk_distribution.items():
    print(f" - {level}: {count:,}")

print()
print("Top 10 providers by provider risk score:")

display_columns = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_Type",
    "Provider_Risk_Score",
    "Provider_Risk_Level",
    "Flagged_Service_Records",
    "Flag_Rate",
    "Total_Services",
]

print(
    provider_risk[display_columns]
    .head(10)
    .to_string(index=False)
)

print()
print("IMPORTANT:")
print("These are screening indicators for further review.")
print("They do NOT prove fraud, waste, or abuse.")
print("The source dataset is provider/service level, not individual claim level.")
print("=" * 75)