import pandas as pd
import numpy as np

# Load preprocessed data
df = pd.read_csv(r'c:\Silverdale QA\BPMN XML\Cost Greater than 1000\Repair Order (repair.order)_preprocessed.csv')

print("=" * 80)
print("PREPROCESSED DATA REVIEW")
print("=" * 80)

# 1. Basic Structure Check
print("\n1. BASIC STRUCTURE:")
print(f"   Total Rows: {len(df):,}")
print(f"   Total Columns: {len(df.columns)}")
print(f"   Unique LPNs: {df['LPN'].nunique():,}")
print(f"   Expected: 954 orders")
print(f"   Status: {'[OK]' if len(df) == 954 and df['LPN'].nunique() == 954 else '[ISSUE]'}")

# 2. Check if Activity Exception Decoration was removed
print("\n2. COLUMN REMOVAL CHECK:")
has_activity_col = 'Activity Exception Decoration' in df.columns
print(f"   Activity Exception Decoration present: {has_activity_col}")
print(f"   Status: {'[OK]' if not has_activity_col else '[ISSUE] - Should be removed'}")

# 3. Check for leftover columns that shouldn't be there
print("\n3. UNNECESSARY COLUMNS CHECK:")
unnecessary_cols = ['Checks/Title', 'Checks/Failed by decision logic Automatically', 'Checks/Status', 'is_human_executed']
found_unnecessary = [col for col in unnecessary_cols if col in df.columns]
if found_unnecessary:
    print(f"   Found columns that should be removed: {found_unnecessary}")
    print(f"   Status: [ISSUE] - These should be removed (they're intermediate columns)")
else:
    print(f"   Status: [OK] - No unnecessary columns found")

# 4. Check Disposition values
print("\n4. DISPOSITION VALUES:")
print(df['Disposition'].value_counts())
print(f"   Status: [OK]")

# 5. Check is_liquidated derived feature
print("\n5. DERIVED FEATURES CHECK:")
if 'is_liquidated' in df.columns:
    liquidated_count = df['is_liquidated'].sum()
    sellable_count = (df['is_liquidated'] == 0).sum()
    print(f"   is_liquidated: {liquidated_count} liquidated, {sellable_count} sellable")
    
    # Verify it matches Disposition
    actual_liquidate = (df['Disposition'].str.strip().str.upper() == 'LIQUIDATE').sum()
    if liquidated_count == actual_liquidate:
        print(f"   Status: [OK] - Matches Disposition column")
    else:
        print(f"   Status: [ISSUE] - Mismatch with Disposition")
else:
    print(f"   Status: [ISSUE] - is_liquidated column missing")

# 6. Check COGS bin
if 'cogs_bin' in df.columns:
    print(f"   cogs_bin: {df['cogs_bin'].value_counts().to_dict()}")
    print(f"   Status: [OK]")

# 7. Check quality check columns
print("\n6. QUALITY CHECK COLUMNS:")
order_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
              'Product Category', 'Result of Repair', 'Scheduled Date', 
              'Shipped Date', 'Started On', 'LPN/Amazon COGS']
derived_cols = ['is_liquidated', 'cogs_bin', 'processing_days']
unnecessary_cols_list = ['Checks/Title', 'Checks/Failed by decision logic Automatically', 
                          'Checks/Status', 'is_human_executed']

check_cols = [c for c in df.columns if c not in order_cols + derived_cols + unnecessary_cols_list]
print(f"   Number of check columns: {len(check_cols)}")
print(f"   Sample check columns (first 5):")
for i, col in enumerate(check_cols[:5], 1):
    print(f"     {i}. {col}")

# 8. Check check column values
print("\n7. CHECK COLUMN VALUES:")
if check_cols:
    sample_check = check_cols[0]
    unique_vals = df[sample_check].value_counts(dropna=False)
    print(f"   Sample check '{sample_check}':")
    print(f"     Unique values: {dict(unique_vals)}")
    print(f"     Non-null: {df[sample_check].notna().sum()}")
    print(f"     Null: {df[sample_check].isna().sum()}")
    
    # Check if values are only Passed/Failed/NaN
    all_check_values = set()
    for col in check_cols:
        all_check_values.update(df[col].dropna().unique())
    
    print(f"   All unique values across all checks: {sorted(all_check_values)}")
    expected_values = {'Passed', 'Failed'}
    unexpected = all_check_values - expected_values
    if unexpected:
        print(f"   Status: [ISSUE] - Unexpected values found: {unexpected}")
    else:
        print(f"   Status: [OK] - Only Passed/Failed/NaN values")

# 9. Check for duplicate LPNs
print("\n8. DUPLICATE CHECK:")
duplicate_lpns = df[df.duplicated(subset=['LPN'], keep=False)]
if len(duplicate_lpns) > 0:
    print(f"   Status: [ISSUE] - Found {len(duplicate_lpns)} duplicate LPNs")
else:
    print(f"   Status: [OK] - No duplicate LPNs")

# 10. Check data completeness
print("\n9. DATA COMPLETENESS:")
missing_cogs = df['Amazon COGS'].isna().sum()
missing_disposition = df['Disposition'].isna().sum()
missing_lpn = df['LPN'].isna().sum()
print(f"   Missing COGS: {missing_cogs}")
print(f"   Missing Disposition: {missing_disposition}")
print(f"   Missing LPN: {missing_lpn}")
if missing_cogs == 0 and missing_disposition == 0 and missing_lpn == 0:
    print(f"   Status: [OK]")
else:
    print(f"   Status: [ISSUE] - Missing critical values")

# 11. Check if check columns have proper structure
print("\n10. CHECK COLUMNS STRUCTURE:")
# Count how many orders have at least one check value
orders_with_checks = 0
for idx, row in df.iterrows():
    has_check = False
    for col in check_cols:
        if pd.notna(row[col]):
            has_check = True
            break
    if has_check:
        orders_with_checks += 1

print(f"   Orders with at least one check: {orders_with_checks} / {len(df)}")
if orders_with_checks == len(df):
    print(f"   Status: [OK] - All orders have check data")
else:
    print(f"   Status: [WARNING] - {len(df) - orders_with_checks} orders have no check data")

# 12. Summary
print("\n" + "=" * 80)
print("REVIEW SUMMARY")
print("=" * 80)
issues = []
if has_activity_col:
    issues.append("Activity Exception Decoration column still present")
if found_unnecessary:
    issues.append(f"Unnecessary columns present: {found_unnecessary}")
if len(df) != 954:
    issues.append(f"Row count mismatch: {len(df)} != 954")
if df['LPN'].nunique() != 954:
    issues.append(f"LPN count mismatch: {df['LPN'].nunique()} != 954")
if len(duplicate_lpns) > 0:
    issues.append(f"Duplicate LPNs found: {len(duplicate_lpns)}")

# 11. Check for redundant columns
print("\n11. REDUNDANT COLUMNS CHECK:")
if 'LPN/Amazon COGS' in df.columns and 'Amazon COGS' in df.columns:
    if (df['LPN/Amazon COGS'] == df['Amazon COGS']).all():
        print(f"   LPN/Amazon COGS is identical to Amazon COGS (redundant)")
        issues.append("LPN/Amazon COGS column is redundant (identical to Amazon COGS)")
    else:
        print(f"   LPN/Amazon COGS differs from Amazon COGS")
        print(f"   Status: [OK] - Column may have different purpose")

# 12. Check for empty check columns
print("\n12. EMPTY CHECK COLUMNS:")
empty_check_cols = [col for col in check_cols if df[col].isna().all()]
if empty_check_cols:
    print(f"   Found {len(empty_check_cols)} check columns with all NaN values")
    print(f"   Sample: {empty_check_cols[:3]}")
    print(f"   Status: [WARNING] - These columns can be removed (no data)")
    issues.append(f"{len(empty_check_cols)} empty check columns found")
else:
    print(f"   Status: [OK] - No completely empty check columns")

# 13. Check check column data types
print("\n13. CHECK COLUMN DATA TYPES:")
if check_cols:
    sample_col = check_cols[0]
    dtype = df[sample_col].dtype
    print(f"   Sample column '{sample_col}' type: {dtype}")
    if dtype == 'object':
        print(f"   Status: [OK] - String type (Passed/Failed)")
    else:
        print(f"   Status: [WARNING] - Unexpected type: {dtype}")

if issues:
    print("\n" + "=" * 80)
    print("[ISSUES FOUND]:")
    print("=" * 80)
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    print("\nRecommendation: Fix these issues before proceeding to Phase 3")
else:
    print("\n" + "=" * 80)
    print("[OK] Data structure looks good!")
    print("=" * 80)
    print("Recommendation: Ready for Phase 3 analysis")

