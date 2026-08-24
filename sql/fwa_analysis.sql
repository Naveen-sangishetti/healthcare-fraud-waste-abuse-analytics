-- Healthcare Fraud, Waste & Abuse (FWA) Analytics
-- SQL Analysis Layer
-- Recommended engine: DuckDB

-- 1. Overall FWA landscape
SELECT
    COUNT(*) AS service_records,
    COUNT(DISTINCT Rndrng_NPI) AS unique_providers,
    COUNT(DISTINCT HCPCS_Cd) AS unique_procedures,
    SUM(Tot_Srvcs) AS total_services,
    AVG(Avg_Mdcr_Pymt_Amt) AS avg_medicare_payment,
    AVG(Services_Per_Beneficiary) AS avg_services_per_beneficiary,
    AVG(Payment_to_Charge_Ratio) AS avg_payment_to_charge_ratio
FROM read_csv_auto('data/processed/powerbi/fwa_overview.csv');

-- 2. Provider billing behavior
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    Rndrng_Prvdr_State_Abrvtn,
    COUNT(*) AS service_records,
    SUM(Tot_Srvcs) AS total_services,
    SUM(Tot_Benes) AS total_beneficiaries,
    AVG(Services_Per_Beneficiary) AS avg_services_per_beneficiary,
    AVG(Avg_Mdcr_Pymt_Amt) AS avg_medicare_payment,
    AVG(Payment_to_Charge_Ratio) AS avg_payment_to_charge_ratio,
    AVG(FWA_Risk_Score) AS avg_fwa_risk_score
FROM read_csv_auto('data/processed/powerbi/fwa_overview.csv')
GROUP BY
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    Rndrng_Prvdr_State_Abrvtn
ORDER BY total_services DESC
LIMIT 25;

-- 3. Procedure utilization
SELECT
    HCPCS_Cd,
    ANY_VALUE(HCPCS_Desc) AS HCPCS_Desc,
    COUNT(DISTINCT Rndrng_NPI) AS provider_count,
    SUM(Tot_Srvcs) AS total_services,
    SUM(Tot_Benes) AS total_beneficiaries,
    AVG(Avg_Mdcr_Pymt_Amt) AS avg_medicare_payment,
    AVG(Services_Per_Beneficiary) AS avg_services_per_beneficiary
FROM read_csv_auto('data/processed/powerbi/fwa_overview.csv')
GROUP BY HCPCS_Cd
ORDER BY total_services DESC
LIMIT 25;

-- 4. Reimbursement patterns by provider type
SELECT
    Rndrng_Prvdr_Type,
    COUNT(DISTINCT Rndrng_NPI) AS provider_count,
    SUM(Tot_Srvcs) AS total_services,
    AVG(Avg_Sbmtd_Chrg) AS avg_submitted_charge,
    AVG(Avg_Mdcr_Alowd_Amt) AS avg_allowed_amount,
    AVG(Avg_Mdcr_Pymt_Amt) AS avg_medicare_payment,
    AVG(Payment_to_Charge_Ratio) AS avg_payment_to_charge_ratio
FROM read_csv_auto('data/processed/powerbi/fwa_overview.csv')
GROUP BY Rndrng_Prvdr_Type
ORDER BY total_services DESC;

-- 5. High service frequency vs peers
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    HCPCS_Cd,
    HCPCS_Desc,
    Tot_Srvcs,
    Peer_Avg_Services,
    Services_vs_Peer,
    FWA_Risk_Score,
    FWA_Risk_Level
FROM read_csv_auto('data/processed/FWA_analysis_dataset.csv')
WHERE Services_vs_Peer >= 4
ORDER BY Services_vs_Peer DESC
LIMIT 100;

-- 6. High utilization per beneficiary vs peers
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    HCPCS_Cd,
    HCPCS_Desc,
    Services_Per_Beneficiary,
    Peer_Avg_Services_Per_Beneficiary,
    Services_Per_Beneficiary_vs_Peer,
    FWA_Risk_Score,
    FWA_Risk_Level
FROM read_csv_auto('data/processed/FWA_analysis_dataset.csv')
WHERE Services_Per_Beneficiary_vs_Peer >= 3
ORDER BY Services_Per_Beneficiary_vs_Peer DESC
LIMIT 100;

-- 7. Reimbursement deviation vs peers
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    HCPCS_Cd,
    HCPCS_Desc,
    Avg_Mdcr_Pymt_Amt,
    Peer_Avg_Payment,
    Payment_vs_Peer,
    Payment_to_Charge_Ratio,
    FWA_Risk_Score,
    FWA_Risk_Level
FROM read_csv_auto('data/processed/FWA_analysis_dataset.csv')
WHERE Payment_vs_Peer >= 3
ORDER BY Payment_vs_Peer DESC
LIMIT 100;

-- 8. FWA investigation queue
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    HCPCS_Cd,
    HCPCS_Desc,
    Tot_Benes,
    Tot_Srvcs,
    FWA_Indicator_Count,
    FWA_Risk_Score,
    FWA_Risk_Level,
    Investigation_Reason
FROM read_csv_auto('data/processed/powerbi/fwa_investigation.csv')
ORDER BY FWA_Risk_Score DESC, FWA_Indicator_Count DESC, Tot_Srvcs DESC;

-- 9. FWA indicator frequency
SELECT
    SUM(CASE WHEN Indicator_High_Service_Frequency THEN 1 ELSE 0 END) AS high_service_frequency_flags,
    SUM(CASE WHEN Indicator_High_Utilization_Per_Beneficiary THEN 1 ELSE 0 END) AS high_utilization_per_beneficiary_flags,
    SUM(CASE WHEN Indicator_High_Utilization_Percentile THEN 1 ELSE 0 END) AS high_utilization_percentile_flags,
    SUM(CASE WHEN Indicator_Reimbursement_Deviation THEN 1 ELSE 0 END) AS reimbursement_deviation_flags,
    SUM(CASE WHEN Indicator_Payment_Pattern_Deviation THEN 1 ELSE 0 END) AS payment_pattern_deviation_flags,
    SUM(CASE WHEN Indicator_High_Procedure_Concentration THEN 1 ELSE 0 END) AS high_procedure_concentration_flags
FROM read_csv_auto('data/processed/FWA_analysis_dataset.csv');

-- 10. Providers requiring review
SELECT
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_Type,
    Provider_Risk_Score,
    Provider_Risk_Level,
    Flagged_Service_Records,
    Flag_Rate,
    Total_Services
FROM read_csv_auto('data/processed/powerbi/provider_risk.csv')
WHERE Provider_Risk_Level IN ('High', 'Medium')
ORDER BY Provider_Risk_Score DESC, Flagged_Service_Records DESC, Total_Services DESC
LIMIT 50;