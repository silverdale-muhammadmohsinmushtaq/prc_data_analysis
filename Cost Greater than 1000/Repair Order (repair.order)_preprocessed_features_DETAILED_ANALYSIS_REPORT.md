# Detailed Analysis Report: Liquidation Analysis

**Generated:** November 12, 2025 at 02:01:12

---

## 1. Methodology

### 1.1 Data Science Pipeline

This analysis followed a comprehensive 10-phase data science pipeline:

1. **Data Understanding & Preparation** - Initial data loading, structure analysis, quality assessment
2. **Data Cleaning & Transformation** - Data preprocessing, multi-row handling, human-executed check filtering
3. **Exploratory Data Analysis (EDA)** - Univariate, bivariate, and check-level analysis
4. **Feature Engineering** - Created 18 derived features for deeper analysis
5. **Statistical Analysis** - Hypothesis testing, correlation analysis, effect sizes
6. **Answering Specific Questions** - Direct answers to 7 business questions
7. **Advanced Analysis** - Additional questions (Q8-Q25), pattern recognition, root cause analysis
8. **Data Visualization** - 13 comprehensive visualizations
9. **Insights & Recommendations** - Key findings, problem identification, actionable recommendations
10. **Reporting & Documentation** - Executive summary, detailed report, documentation

### 1.2 Data Sources

- **Primary Dataset:** Repair Order data (CSV/Excel format)
- **Data Period:** Based on provided dataset
- **Total Records:** 954 repair orders
- **Quality Checks:** 71 unique checks

### 1.3 Tools & Technologies

- **Programming Language:** Python 3
- **Libraries:** pandas, numpy, matplotlib, seaborn, scipy
- **Data Format:** CSV, JSON for results
- **Visualization:** Matplotlib, Seaborn

## 2. Data Description

### 2.1 Dataset Overview

- **Total Orders:** 954
- **Total Columns:** 77
- **Liquidated Orders:** 285 (29.9%)
- **Sellable Orders:** 669 (70.1%)

### 2.2 Key Variables

| Variable | Description |
|----------|-------------|
| LPN | License Plate Number (unique identifier)
| Amazon COGS | Cost of Goods Sold
| Disposition | Final outcome (Sellable/Liquidate)
| Product | Product identifier
| Product Category | Product category classification
| Result of Repair | Specific liquidation reason
| Quality Checks | 44+ human-executed quality checks
| is_liquidated | Binary flag (1=Liquidated, 0=Sellable)

## 3. Detailed Findings

### 3.1 Question 1: Which Quality Checks Are Causing Liquidations?

**Top 5 Quality Checks Causing Liquidations:**

1. **Is_it_IOG_Es_IOG** - 285 failures (100.0% failure rate)
2. **Is_the_Item_Factory_Sealed_El_art_culo_est_sellado** - 194 failures (100.0% failure rate)
3. **Does_the_item_need_to_be_Destroyed_El_art_culo_nec** - 191 failures (99.0% failure rate)
4. **Does_the_item_work_El_art_culo_funciona** - 162 failures (95.9% failure rate)
5. **Is_the_item_Repairable_El_art_culo_es_reparable** - 142 failures (87.7% failure rate)

### 3.2 Question 2: Patterns in High COGS Items That Get Liquidated

**Key Findings:**

- High COGS items (>= $2,000) have 0.0% liquidation rate
- Lower COGS items have 0.0% liquidation rate
- Average COGS for liquidated high-value items: $0.00
- Total value lost from high COGS items: $0.00

### 3.3 Question 3: Comparison of Passed vs Failed Checks

**Key Findings:**

- Average failed checks (Liquidated): 0.0
- Average failed checks (Sellable): 0.0
- Average passed checks (Liquidated): 0.0
- Average passed checks (Sellable): 0.0

### 3.4 Question 4: Product Categories Most Affected

**Top 5 Categories by Liquidation Count:**


### 3.5 Question 5: Specific Liquidation Reasons

**Liquidation Reasons Breakdown:**

- **Liquidate - Functional Issues - NRF:** 135 items ($0.00)
- **Liquidate - Advanced Fraud - Fake - Not Authentic - NRD:** 86 items ($0.00)
- **Liquidate - Cosmetic - NRC:** 43 items ($0.00)
- **Wrong Item Description - NRM:** 18 items ($0.00)
- **Destroy - NRS:** 2 items ($0.00)

### 3.6 Question 6: Liquidation and Sellable Counts by Category

**Top 5 Categories:**


### 3.7 Question 7: Liquidation and Sellable Counts by Product

**Top 5 Products:**


## 4. Statistical Results

### 4.1 Processing Time Analysis

- Average processing time (Liquidated): 4.01 days
- Average processing time (Sellable): 3.04 days
- Difference: 0.97 days

### 4.2 Check Correlation Analysis

**Top 5 Checks with Strongest Correlation to Liquidation:**

1. **Is_it_the_expected_item_Es_el_art_culo_esperado** - Correlation: 0.5125
2. **DONE** - Correlation: 0.4988
3. **Does_the_item_need_to_be_Destroyed_El_art_culo_nec** - Correlation: -0.4973
4. **Is_the_Item_Factory_Sealed_El_art_culo_est_sellado** - Correlation: -0.4835
5. **Is_the_item_factory_Sealed_El_art_culo_est_sellado** - Correlation: -0.4622

## 5. Visualizations

The following visualizations were created:

### Phase 3 Visualizations
- Disposition distribution
- COGS distribution
- COGS by disposition
- Liquidation rate by COGS bin
- Top categories
- Liquidation reasons
- Category liquidation analysis
- Top failed checks
- Check comparison

### Phase 6 Visualizations
- Question-specific visualizations (7 charts)

### Phase 8 Visualizations
- 13 comprehensive visualizations covering:
  - Distribution charts
  - Comparison charts
  - Financial impact charts
  - Product-level charts
  - Check analysis charts

All visualizations are saved in the respective Phase folders.

