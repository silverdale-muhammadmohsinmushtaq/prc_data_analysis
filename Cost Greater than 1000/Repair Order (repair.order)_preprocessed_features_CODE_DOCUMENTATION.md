# Code Documentation: Liquidation Analysis

**Generated:** November 12, 2025

---

## Scripts Overview

### Phase 1: Data Understanding
- **Script:** `phase1_data_understanding.py`
- **Purpose:** Load data, inspect structure, perform initial quality assessment
- **Output:** JSON file with data profiling results

### Phase 2: Data Preprocessing
- **Script:** `phase2_data_preprocessing.py`
- **Purpose:** Clean data, transform multi-row format to wide format, filter human-executed checks
- **Output:** Preprocessed CSV file

### Phase 3: Exploratory Data Analysis
- **Script:** `phase3_eda.py`
- **Purpose:** Perform univariate, bivariate, and check-level analysis
- **Output:** JSON results and visualization scripts

### Phase 4: Feature Engineering
- **Script:** `phase4_feature_engineering.py`
- **Purpose:** Create derived features for deeper analysis
- **Output:** Feature-engineered CSV file

### Phase 5: Statistical Analysis
- **Script:** `phase5_statistical_analysis.py`
- **Purpose:** Perform hypothesis testing, correlation analysis
- **Output:** JSON file with statistical results

### Phase 6: Answering Specific Questions
- **Script:** `phase6_answer_questions.py`
- **Purpose:** Directly answer the 7 business questions
- **Output:** JSON results and visualizations

### Phase 7: Advanced Analysis
- **Script:** `phase7_advanced_analysis.py`
- **Purpose:** Answer additional questions (Q8-Q25), pattern recognition, root cause analysis
- **Output:** JSON file with advanced analysis results

### Phase 8: Data Visualization
- **Script:** `phase8_visualizations.py`
- **Purpose:** Create comprehensive visualizations
- **Output:** 13 PNG visualization files

### Phase 9: Insights & Recommendations
- **Script:** `phase9_insights_recommendations.py`
- **Purpose:** Generate key findings, identify problems, create recommendations
- **Output:** JSON results and markdown report

### Phase 10: Reporting & Documentation
- **Script:** `phase10_reporting.py`
- **Purpose:** Create comprehensive reports and documentation
- **Output:** Multiple markdown reports

## Key Assumptions

1. **Data Completeness:** All provided data is representative of the full process
2. **Human-Executed Checks:** Only checks not marked as 'Failed by decision logic Automatically' are considered
3. **COGS Accuracy:** COGS values are accurate and represent true product value
4. **Disposition Accuracy:** Disposition values correctly reflect final outcomes
5. **Check Independence:** Quality checks are assumed to be independent (may not be true in practice)

## Reproducibility

### Required Python Packages

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
scipy>=1.9.0
openpyxl>=3.0.0
```

### Running the Analysis

1. Ensure all required packages are installed
2. Place data file in the correct directory
3. Run phases sequentially (Phase 1 through Phase 10)
4. Each phase produces output files that are used by subsequent phases

### Data File Structure

Expected input file structure:
- CSV or Excel format
- Multi-row format where quality checks are in separate rows
- Key columns: LPN, Amazon COGS, Disposition, Product, Product Category, Result of Repair
- Quality check columns: Various check names with Passed/Failed values

