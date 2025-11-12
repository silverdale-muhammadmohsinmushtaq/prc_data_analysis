# Liquidation Analysis Guide

## Problem Statement

You're facing two critical issues:
1. **Too many items** are going to Liquidation Palletizer
2. **High COGS items** (≥$1000) are being liquidated when they shouldn't be

## Solution: Data-Driven Analysis

This analysis tool will help you:
- Identify which quality checks are causing the most liquidations
- Understand why high COGS items are being liquidated
- Find patterns in the decision tree that lead to unnecessary liquidations
- Generate actionable recommendations

---

## Step 1: Prepare Your Data

You need a CSV or Excel file with quality check data. The file should contain:

### Required Columns:
- **product_id**: Unique identifier for each product
- **cogs**: Cost of Goods Sold (numeric value)
- **destination**: Either "Liquidation Palletizer" or "Sellable Palletizer"

### Quality Check Columns (QCP Codes):
Include columns for each quality check question with answers "Yes" or "No":

- **QCP00024**: Is it IOG?
- **QCP00025**: Is there something in the box?
- **QCP00026**: Is it the Expected Item?
- **QCP00028**: Is it Fraud?
- **QCP00029**: Is the Item Factory Sealed?
- **QCP00030**: Does the item Need to be Destroyed?
- **QCP00031**: Does the item have scratches and dents larger than a badge?
- **QCP00032**: Did you do a Factory Reset?
- **QCP00033**: Is the Item Repairable?
- **QCP00037**: Does the Item Work?
- **QCP00045**: Does the Item Work?
- **QCP00046**: Is the Item Repairable?

### Example Data Format:

```csv
product_id,cogs,destination,QCP00024,QCP00025,QCP00026,QCP00028,QCP00029,QCP00030,QCP00031,QCP00032,QCP00033,QCP00037,QCP00045,QCP00046
PROD001,1500,Liquidation Palletizer,No,Yes,Yes,No,No,No,Yes,No,No,No,No,No
PROD002,500,Sellable Palletizer,No,Yes,Yes,No,Yes,No,No,Yes,Yes,Yes,Yes,Yes
PROD003,1200,Liquidation Palletizer,No,No,Yes,Yes,No,No,No,No,No,No,No,No
```

---

## Step 2: Run the Analysis

### Install Required Libraries:
```bash
pip install pandas numpy openpyxl
```

### Run the Analyzer:
```bash
python liquidation_analyzer.py your_data.csv
```

Or for Excel files:
```bash
python liquidation_analyzer.py your_data.xlsx
```

---

## Step 3: Understand the Results

The analysis will provide:

### 1. Overall Statistics
- Total items processed
- Percentage going to Liquidation vs Sellable
- Liquidation rate

### 2. High COGS Analysis
- How many high COGS items (≥$1000) are being liquidated
- Total value lost due to liquidation
- Average COGS of liquidated high-value items

### 3. Liquidation Reason Analysis
- Top reasons items are being liquidated
- Breakdown by decision point (QCP code)
- Comparison between all items vs high COGS items

### 4. Decision Point Analysis
- Which quality checks are causing the most liquidations
- How "Yes" vs "No" answers affect routing
- Impact of each decision point

### 5. Recommendations
- Specific actions to reduce liquidation rate
- High COGS item handling strategies
- Decision points to review or modify

---

## Step 4: Create Sample Data Template

If you don't have your data ready yet, create a template:

```bash
python liquidation_analyzer.py
```

This will create `sample_quality_data.csv` with example structure.

---

## Expected Output

The analysis will generate:

1. **Console Report**: Detailed analysis printed to console
2. **JSON File**: `your_data_analysis.json` with structured results

---

## Key Questions the Analysis Answers

1. **Which quality check is causing the most liquidations?**
   - Identifies the primary decision point leading to liquidation

2. **Why are high COGS items being liquidated?**
   - Shows specific quality checks failing for high-value items
   - Calculates total value lost

3. **Are there patterns in the decision tree?**
   - Maps which paths through the BPMN lead to liquidation
   - Identifies if certain combinations of answers cause issues

4. **What should we change?**
   - Provides specific recommendations based on data
   - Suggests which decision points need review

---

## Next Steps After Analysis

Based on the results, you can:

1. **Modify Decision Criteria**: Adjust thresholds for specific QCP codes
2. **Add Exception Handling**: Create special rules for high COGS items
3. **Implement Manual Review**: Route high-value items for human review before liquidation
4. **Update BPMN**: Modify the decision tree based on findings
5. **A/B Testing**: Test relaxed criteria for problematic decision points

---

## Example Analysis Workflow

```bash
# 1. Create sample template (if needed)
python liquidation_analyzer.py

# 2. Prepare your data file with quality check results
# (Export from your system or database)

# 3. Run analysis
python liquidation_analyzer.py quality_checks_2024.csv

# 4. Review results
# - Check console output for summary
# - Open quality_checks_2024_analysis.json for detailed data

# 5. Take action based on recommendations
```

---

## Troubleshooting

### Error: "File not found"
- Make sure your data file is in the same directory
- Check file name spelling

### Error: "Column not found"
- Ensure your CSV has required columns: product_id, cogs, destination
- QCP columns are optional but recommended for full analysis

### Error: "Invalid data format"
- Check that COGS column contains numeric values
- Ensure destination column contains exactly "Liquidation Palletizer" or "Sellable Palletizer"
- QCP columns should contain "Yes" or "No" (case-insensitive)

---

## Support

For questions or issues:
1. Check that your data matches the expected format
2. Review the sample template for reference
3. Ensure all required Python libraries are installed


