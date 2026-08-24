"""
Healthcare Fraud, Waste & Abuse (FWA) Analytics
Stage 1: Data Cleaning

Purpose:
    - Load the raw CMS sampled CSV
    - Clean and standardize the data
    - Validate identifiers, categorical fields, and numeric measures
    - Remove exact duplicate rows and invalid negative measures
    - Save a new cleaned CSV automatically in data/processed/

This script ONLY performs data cleaning.
No EDA, FWA scoring, risk scoring, or Power BI calculations are created here.
"""

from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. FIND THE RAW CSV
# ---------------------------------------------------------
# The script looks inside data/ and its subfolders.
# It ignores the processed folder so it will not reload
# the cleaned file on a later run.

csv_files = [
    file
    for file in DATA_DIR.rglob("*.csv")
    if PROCESSED_DIR not in file.parents
]

if not csv_files:
    raise FileNotFoundError(
        "No CSV file was found inside the project's data folder.\n"
        "Place CMSData_sampled.csv inside data/ or data/raw/ and run again."
    )

if len(csv_files) > 1:
    file_list = "\n".join(f" - {file}" for file in csv_files)
    raise RuntimeError(
        "More than one raw CSV was found. Keep only the source CSV in data/ "
        "or update the script to select the intended file.\n\n"
        f"Files found:\n{file_list}"
    )

RAW_FILE = csv_files[0]
OUTPUT_FILE = PROCESSED_DIR / "CMSData_FWA_cleaned.csv"

print("=" * 70)
print("HEALTHCARE FWA ANALYTICS - DATA CLEANING")
print("=" * 70)
print(f"Raw file    : {RAW_FILE}")
print(f"Output file : {OUTPUT_FILE}")
print()


# ---------------------------------------------------------
# 3. LOAD DATA
# ---------------------------------------------------------
# Read identifier-like columns as strings where possible.
# This prevents Excel/CSV conversions from damaging codes.

dtype_map = {
    "Rndrng_NPI": "string",
    "Rndrng_Prvdr_State_FIPS": "string",
    "Rndrng_Prvdr_Zip5": "string",
    "HCPCS_Cd": "string",
}

df = pd.read_csv(
    RAW_FILE,
    dtype=dtype_map,
    low_memory=False
)

original_rows = len(df)
original_columns = len(df.columns)

print(f"Original rows    : {original_rows:,}")
print(f"Original columns : {original_columns}")
print()


# ---------------------------------------------------------
# 4. CLEAN COLUMN NAMES
# ---------------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.replace(r"\s+", "_", regex=True)
)


# ---------------------------------------------------------
# 5. CLEAN TEXT COLUMNS
# ---------------------------------------------------------

text_columns = df.select_dtypes(include=["object", "string"]).columns

for column in text_columns:
    df[column] = df[column].astype("string").str.strip()

    # Treat common empty/missing representations as actual missing values.
    df[column] = df[column].replace(
        {
            "": pd.NA,
            "NA": pd.NA,
            "N/A": pd.NA,
            "NULL": pd.NA,
            "null": pd.NA,
            "None": pd.NA,
            "nan": pd.NA,
        }
    )


# ---------------------------------------------------------
# 6. CLEAN PROVIDER IDENTIFIERS
# ---------------------------------------------------------

# NPI is a 10-digit identifier.
df["Rndrng_NPI"] = df["Rndrng_NPI"].map(
    lambda value: f"{int(float(value)):010d}" if pd.notna(value) else pd.NA
).astype("string")


# State FIPS should contain two digits.
df["Rndrng_Prvdr_State_FIPS"] = (
    df["Rndrng_Prvdr_State_FIPS"]
    .astype("string")
    .str.replace(r"\D", "", regex=True)
    .str.zfill(2)
)


# ZIP5 sometimes appears with only four digits because leading zeros
# were removed during CSV/Excel handling. Restore the leading zero.
df["Rndrng_Prvdr_Zip5"] = (
    df["Rndrng_Prvdr_Zip5"]
    .astype("string")
    .str.replace(r"\D", "", regex=True)
    .str.zfill(5)
)


# HCPCS codes are five-character procedure codes.
df["HCPCS_Cd"] = (
    df["HCPCS_Cd"]
    .astype("string")
    .str.upper()
    .str.strip()
)


# ---------------------------------------------------------
# 7. STANDARDIZE CATEGORICAL FIELDS
# ---------------------------------------------------------

uppercase_columns = [
    "Rndrng_Prvdr_Gndr",
    "Rndrng_Prvdr_Ent_Cd",
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_Cntry",
    "Rndrng_Prvdr_Mdcr_Prtcptg_Ind",
    "HCPCS_Drug_Ind",
    "Place_Of_Srvc",
]

for column in uppercase_columns:
    if column in df.columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.upper()
            .str.strip()
        )


# Normalize common credential formatting.
# Example: M.D. -> MD, D.O. -> DO.
if "Rndrng_Prvdr_Crdntls" in df.columns:
    df["Rndrng_Prvdr_Crdntls"] = (
        df["Rndrng_Prvdr_Crdntls"]
        .astype("string")
        .str.upper()
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )


# ---------------------------------------------------------
# 8. NUMERIC DATA TYPES
# ---------------------------------------------------------

numeric_columns = [
    "Rndrng_Prvdr_RUCA",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


# Count fields should contain whole numbers.
count_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
]

for column in count_columns:
    if column in df.columns:
        df[column] = df[column].round().astype("Int64")


# RUCA is a classification code, so store it as an integer code.
if "Rndrng_Prvdr_RUCA" in df.columns:
    df["Rndrng_Prvdr_RUCA"] = df["Rndrng_Prvdr_RUCA"].round().astype("Int64")


# ---------------------------------------------------------
# 9. HANDLE MISSING CATEGORICAL VALUES
# ---------------------------------------------------------
# We do NOT invent numeric values for missing RUCA information.
# Missing numeric information is left as missing.
#
# For categorical provider fields, "Unknown" allows the rows to
# remain available for later analysis instead of unnecessarily
# deleting otherwise useful provider/service records.

categorical_columns = [
    "Rndrng_Prvdr_First_Name",
    "Rndrng_Prvdr_MI",
    "Rndrng_Prvdr_Crdntls",
    "Rndrng_Prvdr_Gndr",
    "Rndrng_Prvdr_St2",
    "Rndrng_Prvdr_RUCA_Desc",
]

for column in categorical_columns:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown")


# ---------------------------------------------------------
# 10. VALIDATE NUMERIC MEASURES
# ---------------------------------------------------------
# Negative utilization or financial values are not valid for
# these fields. Zero payment is retained because it can be a
# legitimate value.

measure_columns = [
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
]

negative_mask = pd.Series(False, index=df.index)

for column in measure_columns:
    if column in df.columns:
        negative_mask |= df[column].lt(0).fillna(False)

negative_rows = int(negative_mask.sum())

if negative_rows > 0:
    df = df.loc[~negative_mask].copy()


# ---------------------------------------------------------
# 11. REMOVE EXACT DUPLICATE ROWS
# ---------------------------------------------------------

duplicate_rows = int(df.duplicated().sum())

if duplicate_rows > 0:
    df = df.drop_duplicates().copy()


# ---------------------------------------------------------
# 12. FINAL COLUMN ORDER
# ---------------------------------------------------------
# Keep the original dataset structure rather than adding
# analytical/FWA features at the cleaning stage.

expected_order = [
    "Rndrng_NPI",
    "Rndrng_Prvdr_Last_Org_Name",
    "Rndrng_Prvdr_First_Name",
    "Rndrng_Prvdr_MI",
    "Rndrng_Prvdr_Crdntls",
    "Rndrng_Prvdr_Gndr",
    "Rndrng_Prvdr_Ent_Cd",
    "Rndrng_Prvdr_St1",
    "Rndrng_Prvdr_St2",
    "Rndrng_Prvdr_City",
    "Rndrng_Prvdr_State_Abrvtn",
    "Rndrng_Prvdr_State_FIPS",
    "Rndrng_Prvdr_Zip5",
    "Rndrng_Prvdr_RUCA",
    "Rndrng_Prvdr_RUCA_Desc",
    "Rndrng_Prvdr_Cntry",
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_Mdcr_Prtcptg_Ind",
    "HCPCS_Cd",
    "HCPCS_Desc",
    "HCPCS_Drug_Ind",
    "Place_Of_Srvc",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Bene_Day_Srvcs",
    "Avg_Sbmtd_Chrg",
    "Avg_Mdcr_Alowd_Amt",
    "Avg_Mdcr_Pymt_Amt",
    "Avg_Mdcr_Stdzd_Amt",
]

existing_order = [column for column in expected_order if column in df.columns]
remaining_columns = [column for column in df.columns if column not in existing_order]

df = df[existing_order + remaining_columns]


# ---------------------------------------------------------
# 13. SAVE CLEANED DATASET
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 14. FINAL REPORT
# ---------------------------------------------------------

print("=" * 70)
print("CLEANING COMPLETED")
print("=" * 70)
print(f"Rows before cleaning : {original_rows:,}")
print(f"Rows after cleaning  : {len(df):,}")
print(f"Columns              : {len(df.columns)}")
print(f"Negative rows removed: {negative_rows:,}")
print(f"Duplicates removed   : {duplicate_rows:,}")
print(f"Output file          : {OUTPUT_FILE}")
print()
print("The cleaned CSV has been created successfully.")
print("This script does not create EDA features or FWA risk scores.")