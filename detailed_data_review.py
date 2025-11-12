import pandas as pd
import numpy as np

# Load preprocessed data
df = pd.read_csv(r'c:\Silverdale QA\BPMN XML\Cost Greater than 1000\Repair Order (repair.order)_preprocessed.csv')

print("=" * 80)
print("DETAILED DATA REVIEW - NO CHANGES MADE")
print("=" * 80)

# 1. List all columns
print("\n1. ALL COLUMNS IN THE DATASET:")
print(f"   Total: {len(df.columns)} columns\n")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. {col}")

# 2. Identify column categories
print("\n" + "=" * 80)
print("2. COLUMN CATEGORIZATION:")
print("=" * 80)

order_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
              'Product Category', 'Result of Repair', 'Scheduled Date', 
              'Shipped Date', 'Started On']
derived_cols = ['is_liquidated', 'cogs_bin', 'processing_days']
intermediate_cols = ['Checks/Title', 'Checks/Failed by decision logic Automatically', 
                     'Checks/Status', 'is_human_executed']
other_cols = ['LPN/Amazon COGS']

check_cols = [c for c in df.columns if c not in order_cols + derived_cols + intermediate_cols + other_cols]

print(f"\n   Order-level columns ({len(order_cols)}):")
for col in order_cols:
    if col in df.columns:
        print(f"     - {col}")

print(f"\n   Derived feature columns ({len(derived_cols)}):")
for col in derived_cols:
    if col in df.columns:
        print(f"     - {col}")

print(f"\n   Intermediate/processing columns ({len(intermediate_cols)}):")
for col in intermediate_cols:
    if col in df.columns:
        print(f"     - {col}")

print(f"\n   Other columns ({len(other_cols)}):")
for col in other_cols:
    if col in df.columns:
        print(f"     - {col}")

print(f"\n   Quality check columns ({len(check_cols)}):")
print(f"     (These are the transformed check columns)")

# 3. Analyze intermediate columns
print("\n" + "=" * 80)
print("3. INTERMEDIATE COLUMNS ANALYSIS:")
print("=" * 80)

for col in intermediate_cols:
    if col in df.columns:
        print(f"\n   {col}:")
        print(f"     Unique values: {df[col].nunique()}")
        print(f"     Non-null: {df[col].notna().sum()}, Null: {df[col].isna().sum()}")
        if df[col].notna().any():
            print(f"     Sample values:")
            sample_vals = df[col].value_counts().head(3)
            for val, count in sample_vals.items():
                print(f"       '{val}': {count}")

# 4. Check LPN/Amazon COGS vs Amazon COGS
print("\n" + "=" * 80)
print("4. REDUNDANCY CHECK:")
print("=" * 80)

if 'LPN/Amazon COGS' in df.columns and 'Amazon COGS' in df.columns:
    matches = (df['LPN/Amazon COGS'] == df['Amazon COGS']).sum()
    print(f"\n   LPN/Amazon COGS vs Amazon COGS:")
    print(f"     Identical values: {matches} / {len(df)} ({matches/len(df)*100:.1f}%)")
    print(f"     Different values: {(df['LPN/Amazon COGS'] != df['Amazon COGS']).sum()}")
    if matches == len(df):
        print(f"     Status: [REDUNDANT] - Completely identical to Amazon COGS")

# 5. Check check columns
print("\n" + "=" * 80)
print("5. QUALITY CHECK COLUMNS ANALYSIS:")
print("=" * 80)

print(f"\n   Total check columns: {len(check_cols)}")
print(f"\n   Sample check columns (first 10):")
for i, col in enumerate(check_cols[:10], 1):
    non_null = df[col].notna().sum()
    null = df[col].isna().sum()
    unique_vals = df[col].dropna().unique() if non_null > 0 else []
    print(f"     {i:2d}. {col}")
    print(f"         Non-null: {non_null}, Null: {null}")
    if len(unique_vals) > 0:
        print(f"         Values: {sorted(unique_vals)}")

# Check for empty check columns
empty_check_cols = [col for col in check_cols if df[col].isna().all()]
print(f"\n   Empty check columns (all NaN): {len(empty_check_cols)}")
if empty_check_cols:
    print(f"     Sample: {empty_check_cols[:5]}")

# Check columns with data
cols_with_data = [col for col in check_cols if df[col].notna().any()]
print(f"\n   Check columns with data: {len(cols_with_data)}")

# 6. Check data consistency
print("\n" + "=" * 80)
print("6. DATA CONSISTENCY CHECKS:")
print("=" * 80)

# is_liquidated vs Disposition
if 'is_liquidated' in df.columns and 'Disposition' in df.columns:
    liquidated_from_flag = df['is_liquidated'].sum()
    liquidated_from_disp = (df['Disposition'].str.strip().str.upper() == 'LIQUIDATE').sum()
    print(f"\n   is_liquidated vs Disposition:")
    print(f"     From is_liquidated flag: {liquidated_from_flag}")
    print(f"     From Disposition column: {liquidated_from_disp}")
    print(f"     Match: {'[OK]' if liquidated_from_flag == liquidated_from_disp else '[MISMATCH]'}")

# 7. Sample row analysis
print("\n" + "=" * 80)
print("7. SAMPLE ROW ANALYSIS:")
print("=" * 80)

print("\n   First row (LPNPMBF9981266):")
first_row = df.iloc[0]
print(f"     LPN: {first_row['LPN']}")
print(f"     Disposition: {first_row['Disposition']}")
print(f"     is_liquidated: {first_row['is_liquidated']}")
print(f"     COGS: ${first_row['Amazon COGS']:,.2f}")
print(f"     cogs_bin: {first_row['cogs_bin']}")
print(f"     processing_days: {first_row['processing_days']}")

# Count checks with values for this row
checks_with_values = [(col, first_row[col]) for col in check_cols if pd.notna(first_row[col])]
print(f"\n     Quality checks with values: {len(checks_with_values)}")
print(f"     Sample checks (first 10):")
for col, val in checks_with_values[:10]:
    print(f"       {col}: {val}")

# 8. Summary of findings
print("\n" + "=" * 80)
print("8. REVIEW SUMMARY:")
print("=" * 80)

print("\n   Data Structure:")
print(f"     - Total rows: {len(df)} (one per repair order)")
print(f"     - Total columns: {len(df.columns)}")
print(f"     - Unique LPNs: {df['LPN'].nunique()}")
print(f"     - Order-level columns: {len([c for c in order_cols if c in df.columns])}")
print(f"     - Quality check columns: {len(check_cols)}")
print(f"     - Derived feature columns: {len([c for c in derived_cols if c in df.columns])}")
print(f"     - Intermediate/processing columns: {len([c for c in intermediate_cols if c in df.columns])}")

print("\n   Data Quality:")
print(f"     - Missing COGS: {df['Amazon COGS'].isna().sum()}")
print(f"     - Missing Disposition: {df['Disposition'].isna().sum()}")
print(f"     - Missing LPN: {df['LPN'].isna().sum()}")
print(f"     - Duplicate LPNs: {df.duplicated(subset=['LPN']).sum()}")

print("\n   Observations:")
observations = []
if len([c for c in intermediate_cols if c in df.columns]) > 0:
    observations.append(f"- {len([c for c in intermediate_cols if c in df.columns])} intermediate columns present (used during processing)")
if 'LPN/Amazon COGS' in df.columns:
    if (df['LPN/Amazon COGS'] == df['Amazon COGS']).all():
        observations.append("- LPN/Amazon COGS column is identical to Amazon COGS (redundant)")
if len(empty_check_cols) > 0:
    observations.append(f"- {len(empty_check_cols)} check columns are completely empty")
if len(checks_with_values) > 0:
    observations.append(f"- Each order has quality check data (sample row has {len(checks_with_values)} checks)")

for obs in observations:
    print(f"     {obs}")

print("\n" + "=" * 80)
print("REVIEW COMPLETE - NO CHANGES MADE")
print("=" * 80)

