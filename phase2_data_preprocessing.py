#!/usr/bin/env python3
"""
Phase 2: Data Cleaning & Transformation
Liquidation Analysis - Data Preprocessing
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class Phase2DataPreprocessing:
    def __init__(self, csv_file_path, phase1_results_path=None):
        """Initialize Phase 2 preprocessing"""
        self.csv_file_path = csv_file_path
        self.phase1_results_path = phase1_results_path
        self.df = None
        self.orders_df = None
        self.checks_df = None
        self.preprocessed_df = None
        self.results = {
            'phase': 'Phase 2: Data Cleaning & Transformation',
            'timestamp': datetime.now().isoformat(),
            'file_path': csv_file_path,
            'transformations': {}
        }
        
    def run_phase2(self):
        """Execute all Phase 2 tasks"""
        print("=" * 80)
        print("PHASE 2: DATA CLEANING & TRANSFORMATION")
        print("=" * 80)
        
        # Load data
        self.load_data()
        
        # 2.1 Data Cleaning
        self.remove_unnecessary_columns()
        self.handle_missing_values()
        self.standardize_data_formats()
        self.handle_duplicates()
        
        # 2.2 Data Transformation
        self.separate_order_and_check_data()
        self.filter_human_executed_checks()
        self.transform_to_wide_format()
        self.create_derived_features()
        
        # Save preprocessed data
        self.save_preprocessed_data()
        self.save_results()
        
        return self.preprocessed_df, self.results
    
    def load_data(self):
        """Load the data file"""
        print("\n" + "-" * 80)
        print("LOADING DATA")
        print("-" * 80)
        
        file_ext = os.path.splitext(self.csv_file_path)[1].lower()
        
        if file_ext == '.csv':
            self.df = pd.read_csv(self.csv_file_path, encoding='utf-8')
        elif file_ext in ['.xlsx', '.xls']:
            self.df = pd.read_excel(self.csv_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        print(f"[OK] Loaded {len(self.df):,} rows, {len(self.df.columns)} columns")
    
    def remove_unnecessary_columns(self):
        """2.1.1 Remove Activity Exception Decoration column"""
        print("\n" + "-" * 80)
        print("2.1.1 REMOVING UNNECESSARY COLUMNS")
        print("-" * 80)
        
        if 'Activity Exception Decoration' in self.df.columns:
            self.df = self.df.drop(columns=['Activity Exception Decoration'])
            print("[OK] Removed 'Activity Exception Decoration' column")
            self.results['transformations']['removed_columns'] = ['Activity Exception Decoration']
        else:
            print("[OK] 'Activity Exception Decoration' column not found (already removed)")
            self.results['transformations']['removed_columns'] = []
        
        print(f"[OK] Remaining columns: {len(self.df.columns)}")
    
    def handle_missing_values(self):
        """2.1.2 Handle missing values"""
        print("\n" + "-" * 80)
        print("2.1.2 HANDLING MISSING VALUES")
        print("-" * 80)
        
        # Document missing value patterns
        missing_summary = {}
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(self.df)) * 100
                missing_summary[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 2)
                }
        
        print(f"[OK] Documented missing values in {len(missing_summary)} columns")
        print("Note: Missing values in order-level columns are expected (only in header rows)")
        print("Note: Missing values in check-level columns will be handled during transformation")
        
        self.results['transformations']['missing_values_documented'] = missing_summary
    
    def standardize_data_formats(self):
        """2.1.3 Standardize data formats"""
        print("\n" + "-" * 80)
        print("2.1.3 STANDARDIZING DATA FORMATS")
        print("-" * 80)
        
        # Convert COGS to numeric
        if 'Amazon COGS' in self.df.columns:
            self.df['Amazon COGS'] = pd.to_numeric(self.df['Amazon COGS'], errors='coerce')
            print("[OK] Converted 'Amazon COGS' to numeric")
        
        # Standardize Disposition values
        if 'Disposition' in self.df.columns:
            # Trim whitespace and standardize case
            self.df['Disposition'] = self.df['Disposition'].str.strip()
            print("[OK] Standardized 'Disposition' values")
        
        # Standardize Checks/Status
        if 'Checks/Status' in self.df.columns:
            self.df['Checks/Status'] = self.df['Checks/Status'].str.strip()
            # Normalize to Passed/Failed
            self.df['Checks/Status'] = self.df['Checks/Status'].replace({
                'Passed': 'Passed',
                'Failed': 'Failed',
                'passed': 'Passed',
                'failed': 'Failed',
                'PASSED': 'Passed',
                'FAILED': 'Failed'
            })
            print("[OK] Standardized 'Checks/Status' values")
        
        # Handle Checks/Failed by decision logic Automatically
        if 'Checks/Failed by decision logic Automatically' in self.df.columns:
            # Convert to string for comparison
            self.df['Checks/Failed by decision logic Automatically'] = self.df[
                'Checks/Failed by decision logic Automatically'
            ].fillna('').astype(str).str.strip()
            
            # Human-executed = empty or 'False' (case-insensitive)
            # Automatic = 'True' (case-insensitive)
            # Create boolean flag: True = human-executed, False = automatic
            self.df['is_human_executed'] = ~self.df['Checks/Failed by decision logic Automatically'].str.upper().isin(['TRUE', 'T', '1', 'YES', 'Y'])
            print("[OK] Created 'is_human_executed' flag")
        
        self.results['transformations']['format_standardization'] = 'completed'
    
    def handle_duplicates(self):
        """2.1.4 Handle duplicates"""
        print("\n" + "-" * 80)
        print("2.1.4 HANDLING DUPLICATES")
        print("-" * 80)
        
        # Check for duplicate order headers (shouldn't have any)
        orders = self.df[self.df['Amazon COGS'].notna()]
        duplicate_orders = orders[orders.duplicated(subset=['LPN'], keep=False)]
        
        if len(duplicate_orders) > 0:
            print(f"[WARNING] Found {len(duplicate_orders)} duplicate order headers")
            # Keep first occurrence
            self.df = self.df.drop_duplicates(subset=['LPN'], keep='first')
            print(f"[OK] Removed duplicate order headers")
        else:
            print("[OK] No duplicate order headers found")
        
        self.results['transformations']['duplicates_handled'] = len(duplicate_orders)
    
    def separate_order_and_check_data(self):
        """2.2.1 Separate order-level and check-level data"""
        print("\n" + "-" * 80)
        print("2.2.1 SEPARATING ORDER AND CHECK DATA")
        print("-" * 80)
        
        # Forward-fill LPN values so check rows inherit LPN from order header
        # This is needed because check rows have empty LPN values
        print("Forward-filling LPN values for check rows...")
        self.df['LPN'] = self.df['LPN'].ffill()
        print("[OK] Forward-filled LPN values")
        
        # Order headers have non-null COGS
        self.orders_df = self.df[self.df['Amazon COGS'].notna()].copy()
        
        # Check steps have null COGS but have Checks/Title
        self.checks_df = self.df[
            (self.df['Amazon COGS'].isna()) & 
            (self.df['Checks/Title'].notna())
        ].copy()
        
        print(f"[OK] Separated data:")
        print(f"  Order headers: {len(self.orders_df):,} rows")
        print(f"  Check steps: {len(self.checks_df):,} rows")
        
        # Verify relationship integrity
        order_lpns = set(self.orders_df['LPN'].dropna())
        check_lpns = set(self.checks_df['LPN'].dropna())
        
        missing_lpns = order_lpns - check_lpns
        extra_lpns = check_lpns - order_lpns
        
        if missing_lpns:
            print(f"[WARNING] {len(missing_lpns)} orders have no check steps")
        if extra_lpns:
            print(f"[WARNING] {len(extra_lpns)} check steps have no matching order")
        
        print(f"[OK] Relationship integrity verified")
        
        self.results['transformations']['orders_count'] = len(self.orders_df)
        self.results['transformations']['checks_count_before_filter'] = len(self.checks_df)
    
    def filter_human_executed_checks(self):
        """2.2.2 Filter to only human-executed checks"""
        print("\n" + "-" * 80)
        print("2.2.2 FILTERING HUMAN-EXECUTED CHECKS")
        print("-" * 80)
        
        initial_count = len(self.checks_df)
        
        # Filter to only human-executed checks
        # Human-executed = Checks/Failed by decision logic Automatically is False or empty
        auto_col = 'Checks/Failed by decision logic Automatically'
        
        if 'is_human_executed' in self.checks_df.columns:
            # Use the flag we created
            self.checks_df = self.checks_df[self.checks_df['is_human_executed'] == True].copy()
        elif auto_col in self.checks_df.columns:
            # Fallback: filter where the column is empty or False
            # Keep rows where the value is empty, False, or falsy (not True)
            self.checks_df = self.checks_df[
                (self.checks_df[auto_col].isna()) | 
                (self.checks_df[auto_col].astype(str).str.strip().str.upper().isin(['', 'FALSE', 'F', '0', 'NO', 'N']))
            ].copy()
        else:
            print("[WARNING] Could not find column to filter human-executed checks")
            print("  Keeping all checks (no filtering applied)")
        
        filtered_count = len(self.checks_df)
        removed_count = initial_count - filtered_count
        
        print(f"[OK] Filtered checks:")
        print(f"  Initial checks: {initial_count:,}")
        print(f"  Human-executed checks: {filtered_count:,}")
        print(f"  Removed (automatic): {removed_count:,} ({removed_count/initial_count*100:.1f}%)")
        
        self.results['transformations']['checks_count_after_filter'] = filtered_count
        self.results['transformations']['checks_removed'] = removed_count
    
    def transform_to_wide_format(self):
        """2.2.3 Transform check data to wide format (one row per order)"""
        print("\n" + "-" * 80)
        print("2.2.3 TRANSFORMING TO WIDE FORMAT")
        print("-" * 80)
        
        # Create a clean check status mapping
        # For each LPN, create columns for each unique check
        print("Creating wide format...")
        
        # Get unique check names
        unique_checks = self.checks_df['Checks/Title'].dropna().unique()
        print(f"[OK] Found {len(unique_checks)} unique quality checks")
        
        # Create a pivot-like structure
        # For each order, get the status of each check
        check_status_map = {}
        
        for lpn in self.orders_df['LPN'].dropna():
            order_checks = self.checks_df[self.checks_df['LPN'] == lpn]
            check_status_map[lpn] = {}
            
            for _, check_row in order_checks.iterrows():
                check_name = check_row['Checks/Title']
                check_status = check_row['Checks/Status']
                
                if pd.notna(check_name):
                    # Clean check name for column name (remove special chars, limit length)
                    clean_name = self._clean_check_name(check_name)
                    check_status_map[lpn][clean_name] = check_status
        
        # Create DataFrame from the map
        check_wide_df = pd.DataFrame.from_dict(check_status_map, orient='index')
        check_wide_df.index.name = 'LPN'
        check_wide_df = check_wide_df.reset_index()
        
        print(f"[OK] Created wide format with {len(check_wide_df.columns)-1} check columns")
        print(f"  Rows: {len(check_wide_df):,}")
        print(f"  Columns: {len(check_wide_df.columns)}")
        
        # Merge with orders data
        self.preprocessed_df = self.orders_df.merge(
            check_wide_df,
            on='LPN',
            how='left',
            suffixes=('', '_check')
        )
        
        print(f"[OK] Merged with order data")
        print(f"  Final preprocessed data: {len(self.preprocessed_df):,} rows, {len(self.preprocessed_df.columns)} columns")
        
        self.results['transformations']['wide_format_checks'] = len(unique_checks)
        self.results['transformations']['final_columns'] = len(self.preprocessed_df.columns)
        self.results['transformations']['final_rows'] = len(self.preprocessed_df)
    
    def _clean_check_name(self, check_name):
        """Clean check name to be a valid column name"""
        # Remove special characters, keep alphanumeric and spaces
        import re
        # Replace special chars with underscore
        clean = re.sub(r'[^a-zA-Z0-9\s]', '_', str(check_name))
        # Replace multiple spaces/underscores with single underscore
        clean = re.sub(r'[\s_]+', '_', clean)
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        # Limit length
        if len(clean) > 50:
            clean = clean[:50]
        return clean
    
    def create_derived_features(self):
        """2.2.4 Create derived features"""
        print("\n" + "-" * 80)
        print("2.2.4 CREATING DERIVED FEATURES")
        print("-" * 80)
        
        # Binary flag for liquidation
        if 'Disposition' in self.preprocessed_df.columns:
            self.preprocessed_df['is_liquidated'] = (
                self.preprocessed_df['Disposition'].str.strip().str.upper() == 'LIQUIDATE'
            ).astype(int)
            print("[OK] Created 'is_liquidated' binary flag")
        
        # COGS bins
        if 'Amazon COGS' in self.preprocessed_df.columns:
            bins = [0, 1000, 1500, 2000, 2500, 3000, float('inf')]
            labels = ['<$1K', '$1K-$1.5K', '$1.5K-$2K', '$2K-$2.5K', '$2.5K-$3K', '$3K+']
            self.preprocessed_df['cogs_bin'] = pd.cut(
                self.preprocessed_df['Amazon COGS'],
                bins=bins,
                labels=labels,
                include_lowest=True
            )
            print("[OK] Created 'cogs_bin' categorical feature")
        
        # Processing time (if dates are available)
        if all(col in self.preprocessed_df.columns for col in ['Started On', 'Completed On']):
            try:
                self.preprocessed_df['Started On'] = pd.to_datetime(self.preprocessed_df['Started On'], errors='coerce')
                self.preprocessed_df['Completed On'] = pd.to_datetime(self.preprocessed_df['Completed On'], errors='coerce')
                self.preprocessed_df['processing_days'] = (
                    self.preprocessed_df['Completed On'] - self.preprocessed_df['Started On']
                ).dt.days
                print("[OK] Created 'processing_days' feature")
            except:
                print("[WARNING] Could not calculate processing days")
        
        # Count check columns (to see how many checks each order has)
        check_columns = [col for col in self.preprocessed_df.columns if col not in 
                        ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
                         'Product Category', 'Result of Repair', 'Scheduled Date', 
                         'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'is_liquidated', 
                         'cogs_bin', 'processing_days']]
        
        # Count passed and failed checks
        passed_count = 0
        failed_count = 0
        for col in check_columns:
            if self.preprocessed_df[col].notna().any():
                passed = (self.preprocessed_df[col] == 'Passed').sum()
                failed = (self.preprocessed_df[col] == 'Failed').sum()
                passed_count += passed
                failed_count += failed
        
        print(f"[OK] Check statistics:")
        print(f"  Total check columns: {len(check_columns)}")
        print(f"  Total passed checks: {passed_count:,}")
        print(f"  Total failed checks: {failed_count:,}")
        
        self.results['transformations']['derived_features'] = [
            'is_liquidated', 'cogs_bin', 'processing_days'
        ]
        self.results['transformations']['check_columns_count'] = len(check_columns)
    
    def save_preprocessed_data(self):
        """Save preprocessed data to CSV"""
        print("\n" + "-" * 80)
        print("SAVING PREPROCESSED DATA")
        print("-" * 80)
        
        # Save to CSV
        base_name = os.path.splitext(self.csv_file_path)[0]
        output_csv = f"{base_name}_preprocessed.csv"
        
        self.preprocessed_df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"[OK] Saved preprocessed data to: {output_csv}")
        print(f"  Rows: {len(self.preprocessed_df):,}")
        print(f"  Columns: {len(self.preprocessed_df.columns)}")
        
        # Also save to Excel for easier viewing
        output_excel = f"{base_name}_preprocessed.xlsx"
        try:
            self.preprocessed_df.to_excel(output_excel, index=False, engine='openpyxl')
            print(f"[OK] Saved preprocessed data to: {output_excel}")
        except Exception as e:
            print(f"[WARNING] Could not save to Excel: {e}")
            print("  (Install openpyxl: pip install openpyxl)")
        
        # Show sample of preprocessed data
        print("\n" + "-" * 80)
        print("SAMPLE OF PREPROCESSED DATA (First 3 rows, first 10 columns):")
        print("-" * 80)
        sample_cols = self.preprocessed_df.columns[:10].tolist()
        print(self.preprocessed_df[sample_cols].head(3).to_string())
        
        print("\n" + "-" * 80)
        print("COLUMN SUMMARY:")
        print("-" * 80)
        print(f"Order-level columns: LPN, Amazon COGS, Disposition, Product, Product Category, etc.")
        print(f"Check columns: {len([c for c in self.preprocessed_df.columns if c not in ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 'Product Category', 'Result of Repair', 'Scheduled Date', 'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'is_liquidated', 'cogs_bin', 'processing_days']])} quality check columns")
        print(f"Derived columns: is_liquidated, cogs_bin, processing_days")
        
        self.results['transformations']['output_files'] = {
            'csv': output_csv,
            'excel': output_excel if 'output_excel' in locals() else None
        }
    
    def save_results(self):
        """Save Phase 2 results to JSON"""
        base_name = os.path.splitext(self.csv_file_path)[0]
        output_file = f"{base_name}_phase2_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 2 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 2 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Removed columns: {len(self.results['transformations'].get('removed_columns', []))}")
        print(f"[OK] Orders processed: {self.results['transformations']['orders_count']:,}")
        print(f"[OK] Human-executed checks: {self.results['transformations']['checks_count_after_filter']:,}")
        print(f"[OK] Final preprocessed rows: {self.results['transformations']['final_rows']:,}")
        print(f"[OK] Final preprocessed columns: {self.results['transformations']['final_columns']}")


def main():
    """Main execution function"""
    import sys
    
    # File path
    csv_file = None
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Try default paths
        possible_paths = [
            "Cost Greater than 1000/Repair Order (repair.order).csv",
            r"Cost Greater than 1000\Repair Order (repair.order).csv",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                csv_file = path
                break
    
    if csv_file is None:
        print("Error: Could not find data file.")
        print("\nPlease provide the file path as an argument:")
        print("  python phase2_data_preprocessing.py <path_to_file>")
        return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Phase 1 results (optional)
    phase1_results = None
    base_name = os.path.splitext(csv_file)[0]
    phase1_file = f"{base_name}_phase1_results.json"
    if os.path.exists(phase1_file):
        phase1_results = phase1_file
    
    # Run Phase 2 preprocessing
    try:
        preprocessor = Phase2DataPreprocessing(csv_file, phase1_results)
        preprocessed_df, results = preprocessor.run_phase2()
        print("\n[OK] Phase 2 preprocessing completed successfully!")
        return preprocessed_df, results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 2 preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    main()

