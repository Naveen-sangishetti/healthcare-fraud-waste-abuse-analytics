#Healthcare Fraud, Waste & Abuse (FWA) Analytics

A healthcare analytics portfolio project focused on identifying potential fraud, waste and abuse (FWA) indicators through provider billing behavior, service utilization, procedure utilization, reimbursement patterns, peer comparison, and provider risk analysis.

Important: This project is a screening/analytical model. A flagged provider or service record is not proof of fraud, waste, or abuse. The source data is provider/service level rather than individual transaction-level claims.

Project Overview

This project analyzes Medicare provider and service data to answer questions such as:

Which providers show unusual service frequency?

Which provider/procedure combinations have unusually high utilization?

How do reimbursement patterns differ across providers and provider types?

How does a provider compare with comparable peers?

Which records contain multiple FWA behavioral indicators?

Which providers or provider/procedure combinations should receive further review?

The project intentionally focuses on FWA behavioral analytics rather than the overpayment, duplicate-claim, and high-value-claim analysis used in the separate Healthcare Claims Payment Integrity project.

Tech Stack

Python — data cleaning, exploratory data analysis, feature engineering and FWA screening

SQL — analytical queries for provider behavior, procedure utilization, reimbursement and FWA investigation

Power BI — interactive three-page analytics dashboard

Pandas / NumPy / Matplotlib — data processing and EDA

Git / GitHub — version control and project delivery

Dataset

The project uses a sampled Medicare Physician Provider & Service dataset downloaded from Kaggle and derived from CMS provider/service data.

The working dataset contains:

292,663 service records

229,615 unique providers

3,458 HCPCS procedure codes

99 provider types

Provider location information

Procedure information

Total beneficiaries

Total services

Submitted charges

Medicare allowed amounts

Medicare payment amounts

Standardized Medicare payment amounts

The dataset is provider/service level and should not be interpreted as an individual claim transaction dataset.

Project Workflow

Raw Dataset
    ↓
Python Data Cleaning
    ↓
Exploratory Data Analysis
    ↓
FWA Behavioral Feature Engineering
    ↓
Peer Comparison
    ↓
FWA Screening Indicators
    ↓
Provider Risk Analysis
    ↓
SQL Analytical Layer
    ↓
Power BI Dashboard
    ↓
Investigation & Reporting

Python Analysis

1. Data Cleaning

python/clean_fwa_data.py

The cleaning stage:

standardizes column names and text fields

cleans provider identifiers and procedure codes

converts numeric fields to appropriate data types

handles optional categorical missing values

checks invalid negative utilization/financial measures

removes exact duplicate records

creates the processed dataset

Output:

data/processed/CMSData_FWA_cleaned.csv

2. Exploratory Data Analysis

python/eda_fwa.py

EDA examines:

provider distribution

provider types

procedure utilization

state distribution

place of service

service utilization

services per beneficiary

reimbursement patterns

payment-to-charge behavior

provider-level variation

EDA outputs are stored under:

images/eda/

3. FWA Indicator Analysis

python/fwa_analysis.py

The screening framework compares providers with peer groups based on:

Provider Type
+
HCPCS Procedure
+
Place of Service

The analysis creates indicators for:

high service frequency versus peers

high services per beneficiary versus peers

extreme utilization percentile

reimbursement deviation versus peers

unusual payment-to-charge patterns

high procedure concentration

These indicators are combined into a transparent screening score and review level.

The final calibrated run produced:

292,663 records analyzed

631 investigation records (0.22%)

4,137 Medium Review records

37 High Review records

21,300 Low Review records

267,189 No Flag records

A flagged record is a potential review signal, not a finding of confirmed fraud.

4. Power BI Data Preparation

python/prepare_powerbi_data.py

Creates dashboard-focused datasets:

data/processed/powerbi/
├── fwa_overview.csv
├── provider_risk.csv
├── fwa_investigation.csv
└── dashboard_summary.csv

SQL Analysis

SQL queries are stored in:

sql/fwa_analysis.sql

The SQL layer covers:

overall FWA landscape

provider billing behavior

procedure utilization

reimbursement patterns by provider type

service frequency versus peers

services per beneficiary versus peers

reimbursement deviation versus peers

FWA investigation queue

FWA indicator frequency

providers requiring review

Power BI Dashboard

The dashboard contains three pages designed for different analytical purposes.

Page 1 — FWA Behavioral Landscape

Focus:

provider population

procedure utilization

overall service activity

reimbursement behavior

FWA review distribution

Visual concepts include:

summary cards

utilization/reimbursement scatter analysis

procedure utilization treemap

FWA review funnel

reimbursement pattern analysis

Page 2 — Provider Risk Analysis

Focus:

selected provider

provider risk score

provider risk level

procedure count

total services

provider service behavior

FWA behavioral indicators

Page 3 — FWA Investigation

Focus:

flagged provider/procedure records

investigation risk score

service utilization versus peers

FWA investigation signals

suspicious provider/procedure investigation queue

The three pages intentionally use different layouts rather than repeating the same KPI/bar/donut template.

Key Analytical Metrics

Examples of metrics used in the project include:

Services per Beneficiary
Payment-to-Charge Ratio
Allowed-to-Charge Ratio
Services vs Peer
Services per Beneficiary vs Peer
Payment vs Peer
Payment-to-Charge vs Peer
Utilization Percentile
Procedure Service Share
FWA Indicator Count
FWA Risk Score
Provider Risk Score
Flag Rate

Business Value

The project demonstrates how analytics can support healthcare payment-abuse and utilization review teams by helping analysts:

identify unusual provider behavior

compare utilization with peer groups

examine reimbursement patterns

prioritize records for further investigation

explain the behavioral signals behind a review flag

The dashboard is intended as an analyst screening and prioritization tool, not an automated fraud determination system.

Repository Structure

healthcare-fraud-waste-abuse-analytics/
│
├── README.md
│
├── data/
│   ├── CMSData_sampled.csv
│   └── processed/
│       ├── CMSData_FWA_cleaned.csv
│       ├── FWA_analysis_dataset.csv
│       ├── provider_risk_summary.csv
│       ├── fwa_flagged_records.csv
│       └── powerbi/
│           ├── fwa_overview.csv
│           ├── provider_risk.csv
│           ├── fwa_investigation.csv
│           └── dashboard_summary.csv
│
├── images/
│   └── eda/
│
├── notebooks/
│
├── powerbi/
│
├── python/
│   ├── clean_fwa_data.py
│   ├── eda_fwa.py
│   ├── fwa_analysis.py
│   └── prepare_powerbi_data.py
│
└── sql/
    └── fwa_analysis.sql

Large raw and processed CSV files are intentionally excluded from GitHub through .gitignore.

How to Run

1. Install Python dependencies

pip install pandas numpy matplotlib

2. Run cleaning

python python/clean_fwa_data.py

3. Run EDA

python python/eda_fwa.py

4. Run FWA analysis

python python/fwa_analysis.py

5. Prepare Power BI datasets

python python/prepare_powerbi_data.py

6. SQL

Run the queries in:

sql/fwa_analysis.sql

using a SQL engine such as DuckDB.

7. Power BI

Import:

data/processed/powerbi/fwa_overview.csv
data/processed/powerbi/provider_risk.csv
data/processed/powerbi/fwa_investigation.csv

Limitations

The source is provider/service level rather than individual transaction-level claims.

There is no claim submission timestamp for temporal sequence analysis.

Peer-based indicators identify unusual behavior but do not establish intent.

Provider type and procedure differences can naturally produce large utilization differences.

FWA signals require analyst review and contextual investigation.

Author

Naveen Kumar

Healthcare Analytics | Python | SQL | Power BI
