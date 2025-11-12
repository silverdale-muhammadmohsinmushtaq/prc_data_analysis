import pandas as pd

df = pd.read_csv(r'c:\Silverdale QA\BPMN XML\Cost Greater than 1000\Repair Order (repair.order)_preprocessed_features.csv')

# Define what are NOT quality checks
order_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
              'Product Category', 'Result of Repair', 'Scheduled Date', 
              'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'Checks/Title',
              'Checks/Failed by decision logic Automatically', 'Checks/Status',
              'is_human_executed', 'is_liquidated', 'cogs_bin', 'processing_days',
              'category_group', 'high_value_flag', 'total_checks', 'failed_checks_count',
              'passed_checks_count', 'failure_rate', 'fraud_check_failed',
              'cosmetic_check_failed', 'repairable_check_failed', 'works_check_passed',
              'factory_sealed_check_passed', 'value_lost', 'recovery_potential',
              'days_to_ship', 'check_efficiency']

# Quality check columns are everything else
check_cols = [c for c in df.columns if c not in order_cols]

print("=" * 80)
print("VERIFICATION: Quality Check Columns Only")
print("=" * 80)
print(f"\nTotal Quality Check Columns: {len(check_cols)}")
print("\nThese are the ACTUAL quality checks (not COGS or other metrics):")
print("-" * 80)
for i, col in enumerate(check_cols, 1):
    print(f"{i:2d}. {col}")

print("\n" + "=" * 80)
print("CONFIRMATION:")
print("=" * 80)
print("COGS (Amazon COGS) is NOT in quality check columns: ", 'Amazon COGS' not in check_cols)
print("COGS is in order columns: ", 'Amazon COGS' in order_cols)
print("\nQuality checks are the human-executed check steps from the BPMN process.")
print("COGS is a financial metric, not a quality check.")

