# Quick Start Data Analysis Pipeline - Liquidation Analysis

## Essential Steps (Do These First)

### Step 1: Load & Understand Data (30 min)
```python
# Load data
df = pd.read_csv('Repair Order (repair.order).csv')

# Separate orders from checks
orders_df = df[df['Amazon COGS'].notna()].copy()
checks_df = df[df['Amazon COGS'].isna() & df['Checks/Title'].notna()].copy()

# Basic stats
print(f"Orders: {len(orders_df)}")
print(f"Checks: {len(checks_df)}")
print(f"Disposition: {orders_df['Disposition'].value_counts()}")
```

### Step 2: Clean Data (1 hour)
- [ ] Convert COGS to numeric
- [ ] Standardize Disposition values
- [ ] Fix date formats
- [ ] Handle missing values
- [ ] Remove duplicates

### Step 3: Answer Core Questions (2-3 hours)
- [ ] Q1: Top failed checks in liquidated orders
- [ ] Q2: COGS patterns (liquidated vs sellable)
- [ ] Q3: Check failure rate comparison
- [ ] Q4: Category analysis
- [ ] Q5: Liquidation reasons breakdown
- [ ] Q6: Category pivot table
- [ ] Q7: Product-level analysis

### Step 4: Create Visualizations (1 hour)
- [ ] Disposition distribution
- [ ] COGS comparison charts
- [ ] Top checks causing liquidations
- [ ] Category liquidation rates
- [ ] Value lost charts

### Step 5: Generate Insights (1 hour)
- [ ] Identify top 3 problems
- [ ] Calculate financial impact
- [ ] Create recommendations
- [ ] Prioritize actions

### Step 6: Document & Report (1 hour)
- [ ] Write findings summary
- [ ] Create recommendations list
- [ ] Save visualizations
- [ ] Export results

---

## Total Time Estimate: 6-8 hours

## Priority Order:
1. **Must Do**: Steps 1-3 (Core analysis)
2. **Should Do**: Step 4 (Visualizations)
3. **Nice to Have**: Steps 5-6 (Advanced insights)

