# 🛡️ Healthcare Fraud, Waste & Abuse (FWA) Analytics

> **Python | SQL | Power BI**

Healthcare analytics project focused on identifying **potential Fraud, Waste & Abuse (FWA) indicators** through provider billing behavior, service utilization, procedure patterns, reimbursement behavior, and peer comparison.

---

## 🎯 Project Objective

Identify unusual healthcare provider/service patterns that may require **further investigation**.

### 🔍 What This Project Analyzes

- 👨‍⚕️ **Provider Billing Behavior**
- 💳 **Reimbursement Patterns**
- 📊 **Service Frequency & Utilization**
- 🧾 **Procedure Utilization**
- ⚖️ **Peer Comparison**
- 🚩 **FWA Indicators**
- 🛡️ **Provider Risk Analysis**
- 🔎 **Suspicious Provider–Procedure Investigation**

> ⚠️ A flagged record is a **screening signal**, not proof of fraud, waste, or abuse.

---

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Cleaning, EDA & FWA analysis |
| 🗄️ SQL | Analytical queries & investigation |
| 📊 Power BI | Interactive dashboard |
| 🐼 Pandas | Data processing |
| 🔢 NumPy | Feature calculations |
| 📈 Matplotlib | EDA visualization |
| 🔧 Git & GitHub | Version control |

---

## 📂 Dataset

The project uses a sampled Medicare Provider & Service dataset.

**Dataset size:**
- 📌 292,663 service records
- 👥 229,615 providers
- 🧾 3,458 HCPCS procedures
- 🏥 99 provider types

The dataset is **provider/service level**, not individual transaction-level claims.

---

## 🔄 Project Workflow

```text
Raw Dataset
    ↓
🧹 Python Data Cleaning
    ↓
📊 Exploratory Data Analysis
    ↓
⚙️ FWA Feature Engineering
    ↓
⚖️ Peer Comparison
    ↓
🚩 FWA Screening Indicators
    ↓
🛡️ Provider Risk Analysis
    ↓
🗄️ SQL Analysis
    ↓
📊 Power BI Dashboard
    ↓
🔎 Investigation
```

---

## 🚩 FWA Indicators

The screening framework evaluates:

```text
• High Service Frequency vs Peers
• High Services per Beneficiary
• Extreme Utilization Percentile
• Reimbursement Deviation
• Payment-to-Charge Pattern Deviation
• High Procedure Concentration
```

These indicators are combined into a transparent **FWA Risk Score** for review prioritization.

---

## 📊 Power BI Dashboard

### 1️⃣ FWA Behavioral Landscape
Explores:

- Service utilization
- Procedure utilization
- Reimbursement behavior
- FWA review distribution

### 2️⃣ Provider Risk Analysis
Analyzes:

- Provider risk score
- Provider risk level
- Service behavior
- Procedure utilization
- FWA indicators

### 3️⃣ FWA Investigation
Supports:

- Suspicious provider–procedure review
- Peer deviation analysis
- Investigation signals
- Review prioritization

---

## 🗄️ SQL Analysis

SQL is used for:

- Provider billing behavior
- Procedure utilization
- Reimbursement patterns
- Peer comparison
- FWA investigation
- Provider review prioritization

SQL file:

```text
sql/fwa_analysis.sql
```

---

## 📁 Project Structure

```text
healthcare-fraud-waste-abuse-analytics/
│
├── 📄 README.md
├── 🚫 .gitignore
├── 🐍 python/
│   ├── clean_fwa_data.py
│   ├── eda_fwa.py
│   ├── fwa_analysis.py
│   └── prepare_powerbi_data.py
│
├── 🗄️ sql/
│   └── fwa_analysis.sql
│
├── 📊 powerbi/
│   └── fwa.pbix
│
├── 🖼️ images/
│   └── eda/
│
└── 📓 notebooks/
```

---

## 📌 Key Outcome

The project creates a **risk-based analytical screening workflow** that helps prioritize unusual provider/service patterns for further review.

### ✅ Skills Demonstrated

**Python • SQL • Power BI • EDA • Data Cleaning • Feature Engineering • Healthcare Analytics • Risk Analysis • Data Visualization**

---

## 👨‍💻 Author

**Naveen Kumar**

🎓 B.Tech Computer Science  
🐍 Python | 🗄️ SQL | 📊 Power BI  
🔗 GitHub: [Naveen-sangishetti](https://github.com/Naveen-sangishetti)

---
