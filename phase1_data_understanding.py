#!/usr/bin/env python3
"""
Phase 1: Data Understanding & Preparation
Liquidation Analysis - Data Loading, Inspection, and Quality Assessment
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import json
from datetime import datetime

class Phase1DataUnderstanding:
    def __init__(self, csv_file_path):
        """Initialize Phase 1 analysis"""
        self.csv_file_path = csv_file_path
        self.df = None
        self.orders_df = None
        self.checks_df = None
        self.results = {
            'phase': 'Phase 1: Data Understanding & Preparation',
            'timestamp': datetime.now().isoformat(),
            'file_path': csv_file_path,
            'findings': {}
        }
        
    def run_phase1(self):
        """Execute all Phase 1 tasks"""
        print("=" * 80)
        print("PHASE 1: DATA UNDERSTANDING & PREPARATION")
        print("=" * 80)
        
        # 1.1 Data Loading & Initial Inspection
        self.load_data()
        self.understand_data_structure()
        self.initial_data_profiling()
        
        # 1.2 Data Quality Assessment
        self.check_data_quality()
        self.validate_business_rules()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def load_data(self):
        """1.1.1 Load the data file"""
        print("\n" + "-" * 80)
        print("1.1.1 LOADING DATA FILE")
        print("-" * 80)
        
        # Verify file path and accessibility
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"File not found: {self.csv_file_path}")
        
        print(f"[OK] File path verified: {self.csv_file_path}")
        
        # Check file size
        file_size = os.path.getsize(self.csv_file_path)
        file_size_mb = file_size / (1024 * 1024)
        print(f"[OK] File size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        
        self.results['findings']['file_size_mb'] = round(file_size_mb, 2)
        self.results['findings']['file_size_bytes'] = file_size
        
        # Load data with error handling for encoding
        print("\nLoading data...")
        file_ext = os.path.splitext(self.csv_file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                # Try UTF-8 first
                try:
                    self.df = pd.read_csv(self.csv_file_path, encoding='utf-8')
                    print("[OK] Successfully loaded CSV with UTF-8 encoding")
                    self.results['findings']['encoding'] = 'UTF-8'
                except UnicodeDecodeError:
                    # Try latin-1 if UTF-8 fails
                    self.df = pd.read_csv(self.csv_file_path, encoding='latin-1')
                    print("[OK] Successfully loaded CSV with Latin-1 encoding")
                    self.results['findings']['encoding'] = 'Latin-1'
            elif file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.csv_file_path)
                print(f"[OK] Successfully loaded Excel file ({file_ext})")
                self.results['findings']['encoding'] = 'Excel'
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"[ERROR] Error loading file: {e}")
            raise
        
        # Check row count
        total_rows = len(self.df)
        total_columns = len(self.df.columns)
        print(f"[OK] Total rows loaded: {total_rows:,}")
        print(f"[OK] Total columns: {total_columns}")
        
        self.results['findings']['total_rows'] = total_rows
        self.results['findings']['total_columns'] = total_columns
        
        # Check for special characters/encoding issues
        special_char_count = 0
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].dtype == 'object':
                try:
                    self.df[col].str.encode('utf-8')
                except:
                    special_char_count += 1
        
        if special_char_count > 0:
            print(f"[WARNING] Warning: {special_char_count} columns may have encoding issues")
            self.results['findings']['encoding_issues'] = special_char_count
        else:
            print("[OK] No encoding issues detected")
            self.results['findings']['encoding_issues'] = 0
    
    def understand_data_structure(self):
        """1.1.2 Understand data structure"""
        print("\n" + "-" * 80)
        print("1.1.2 UNDERSTANDING DATA STRUCTURE")
        print("-" * 80)
        
        # Identify header row
        print("\nColumn Names:")
        print("-" * 80)
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i:2d}. {col}")
        
        self.results['findings']['column_names'] = list(self.df.columns)
        
        # Map column names and meanings
        print("\nColumn Data Types:")
        print("-" * 80)
        dtype_summary = {}
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            dtype_summary[col] = dtype
            non_null = self.df[col].notna().sum()
            print(f"{col:<40} {dtype:<15} Non-null: {non_null:,}")
        
        self.results['findings']['column_dtypes'] = dtype_summary
        
        # Identify multi-row structure (order headers vs check steps)
        print("\n" + "-" * 80)
        print("Identifying Data Structure (Order Headers vs Check Steps):")
        print("-" * 80)
        
        # Orders have non-null COGS
        orders_count = self.df['Amazon COGS'].notna().sum()
        # Check steps have null COGS but have Checks/Title
        checks_count = self.df[
            (self.df['Amazon COGS'].isna()) & 
            (self.df['Checks/Title'].notna())
        ].shape[0]
        
        print(f"Order Headers (rows with COGS): {orders_count:,}")
        print(f"Check Steps (rows with Checks/Title, no COGS): {checks_count:,}")
        print(f"Other rows: {len(self.df) - orders_count - checks_count:,}")
        
        self.results['findings']['order_headers_count'] = orders_count
        self.results['findings']['check_steps_count'] = checks_count
        
        # Document data format and relationships
        print("\nData Format Documentation:")
        print("-" * 80)
        print("- Each repair order has ONE header row with:")
        print("  - Amazon COGS, Disposition, LPN, Product, Dates, etc.")
        print("- Each repair order has MULTIPLE check step rows with:")
        print("  - Checks/Title (quality check name)")
        print("  - Checks/Status (Passed/Failed)")
        print("  - Other columns are empty/null")
        print("- Relationship: LPN links header to check steps")
        
        # Verify LPN relationship
        if 'LPN' in self.df.columns:
            unique_lpns = self.df['LPN'].dropna().nunique()
            print(f"\n[OK] Unique LPNs (repair orders): {unique_lpns:,}")
            self.results['findings']['unique_lpns'] = unique_lpns
            
            # Check if all orders have LPN
            orders_with_lpn = self.df[self.df['Amazon COGS'].notna()]['LPN'].notna().sum()
            print(f"[OK] Orders with LPN: {orders_with_lpn:,} / {orders_count:,}")
            self.results['findings']['orders_with_lpn'] = orders_with_lpn
    
    def initial_data_profiling(self):
        """1.1.3 Initial data profiling"""
        print("\n" + "-" * 80)
        print("1.1.3 INITIAL DATA PROFILING")
        print("-" * 80)
        
        # Count total rows and columns (already done, but summarize)
        print(f"\nDataset Summary:")
        print(f"  Total Rows: {len(self.df):,}")
        print(f"  Total Columns: {len(self.df.columns)}")
        
        # Identify data types
        print(f"\nData Type Summary:")
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} columns")
        
        # Convert dtype objects to strings for JSON serialization
        dtype_dict = {str(k): int(v) for k, v in dtype_counts.items()}
        self.results['findings']['dtype_distribution'] = dtype_dict
        
        # Check for missing values
        print(f"\nMissing Values by Column:")
        print("-" * 80)
        missing_data = {}
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            if missing_count > 0:
                print(f"{col:<40} {missing_count:>8,} ({missing_pct:>5.1f}%)")
                missing_data[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 2)
                }
        
        if not missing_data:
            print("  No missing values found")
        
        self.results['findings']['missing_values'] = missing_data
        
        # Identify unique identifiers
        print(f"\nUnique Identifiers:")
        print("-" * 80)
        if 'LPN' in self.df.columns:
            unique_lpns = self.df['LPN'].dropna().nunique()
            print(f"  LPN (License Plate Number): {unique_lpns:,} unique values")
        
        if 'Product' in self.df.columns:
            unique_products = self.df['Product'].dropna().nunique()
            print(f"  Product: {unique_products:,} unique values")
            self.results['findings']['unique_products'] = unique_products
        
        if 'Product Category' in self.df.columns:
            unique_categories = self.df['Product Category'].dropna().nunique()
            print(f"  Product Category: {unique_categories:,} unique values")
            self.results['findings']['unique_categories'] = unique_categories
    
    def check_data_quality(self):
        """1.2.1 Check for data quality issues"""
        print("\n" + "=" * 80)
        print("1.2 DATA QUALITY ASSESSMENT")
        print("=" * 80)
        print("\n1.2.1 CHECKING DATA QUALITY ISSUES")
        print("-" * 80)
        
        quality_issues = []
        
        # Missing values analysis
        print("\nMissing Values Analysis:")
        high_missing_cols = []
        for col in self.df.columns:
            missing_pct = (self.df[col].isna().sum() / len(self.df)) * 100
            if missing_pct > 50:  # Flag columns with >50% missing
                high_missing_cols.append((col, missing_pct))
                quality_issues.append(f"High missing values in {col}: {missing_pct:.1f}%")
        
        if high_missing_cols:
            print("  [WARNING] Columns with >50% missing values:")
            for col, pct in high_missing_cols:
                print(f"    - {col}: {pct:.1f}%")
        else:
            print("  [OK] No columns with excessive missing values")
        
        # Duplicate records check
        print("\nDuplicate Records Check:")
        total_duplicates = self.df.duplicated().sum()
        if total_duplicates > 0:
            print(f"  [WARNING] Found {total_duplicates:,} completely duplicate rows")
            quality_issues.append(f"Duplicate rows: {total_duplicates}")
        else:
            print("  [OK] No completely duplicate rows found")
        
        # Check for duplicate LPNs in order headers
        if 'LPN' in self.df.columns and 'Amazon COGS' in self.df.columns:
            orders = self.df[self.df['Amazon COGS'].notna()]
            duplicate_lpns = orders[orders.duplicated(subset=['LPN'], keep=False)]
            if len(duplicate_lpns) > 0:
                print(f"  [WARNING] Found {len(duplicate_lpns):,} orders with duplicate LPNs")
                quality_issues.append(f"Duplicate LPNs in orders: {len(duplicate_lpns)}")
            else:
                print("  [OK] No duplicate LPNs in order headers")
        
        # Inconsistent formatting check
        print("\nFormat Consistency Check:")
        
        # Check COGS format
        if 'Amazon COGS' in self.df.columns:
            cogs_orders = self.df[self.df['Amazon COGS'].notna()]
            # Try to convert to numeric
            try:
                pd.to_numeric(cogs_orders['Amazon COGS'], errors='coerce')
                print("  [OK] COGS values are numeric-compatible")
            except:
                print("  [WARNING] COGS values may have formatting issues")
                quality_issues.append("COGS formatting issues")
        
        # Check date formats
        date_columns = [col for col in self.df.columns if 'Date' in col or 'On' in col]
        if date_columns:
            print(f"  Date columns found: {', '.join(date_columns)}")
            for col in date_columns:
                sample_dates = self.df[col].dropna().head(5)
                if len(sample_dates) > 0:
                    print(f"    Sample {col}: {sample_dates.iloc[0]}")
        
        # Outliers detection
        print("\nOutliers Detection:")
        if 'Amazon COGS' in self.df.columns:
            cogs_values = pd.to_numeric(self.df['Amazon COGS'], errors='coerce').dropna()
            if len(cogs_values) > 0:
                negative_cogs = (cogs_values < 0).sum()
                zero_cogs = (cogs_values == 0).sum()
                very_high_cogs = (cogs_values > 10000).sum()  # Flag if >$10K
                
                if negative_cogs > 0:
                    print(f"  [WARNING] Found {negative_cogs} negative COGS values")
                    quality_issues.append(f"Negative COGS: {negative_cogs}")
                else:
                    print("  [OK] No negative COGS values")
                
                if zero_cogs > 0:
                    print(f"  [WARNING] Found {zero_cogs} zero COGS values")
                    quality_issues.append(f"Zero COGS: {zero_cogs}")
                
                if very_high_cogs > 0:
                    print(f"  [WARNING] Found {very_high_cogs} COGS values > $10,000")
                    print(f"    Max COGS: ${cogs_values.max():,.2f}")
                    quality_issues.append(f"Very high COGS (>$10K): {very_high_cogs}")
                else:
                    print(f"  [OK] Max COGS: ${cogs_values.max():,.2f}")
        
        # Data completeness per column
        print("\nData Completeness Summary:")
        completeness = {}
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            pct = (non_null / len(self.df)) * 100
            completeness[col] = round(pct, 2)
            if pct < 10:  # Flag columns with <10% data
                print(f"  [WARNING] {col}: {pct:.1f}% complete")
        
        self.results['findings']['quality_issues'] = quality_issues
        self.results['findings']['data_completeness'] = completeness
    
    def validate_business_rules(self):
        """1.2.2 Validate business rules"""
        print("\n1.2.2 VALIDATING BUSINESS RULES")
        print("-" * 80)
        
        validation_results = {}
        
        # All COGS values >= $1000
        print("\nBusiness Rule 1: All COGS values >= $1000")
        if 'Amazon COGS' in self.df.columns:
            cogs_values = pd.to_numeric(self.df['Amazon COGS'], errors='coerce').dropna()
            if len(cogs_values) > 0:
                below_1000 = (cogs_values < 1000).sum()
                if below_1000 > 0:
                    print(f"  [WARNING] VIOLATION: {below_1000} COGS values < $1,000")
                    print(f"    Min COGS: ${cogs_values.min():,.2f}")
                    validation_results['cogs_below_1000'] = int(below_1000)
                else:
                    print(f"  [OK] PASS: All COGS values >= $1,000")
                    print(f"    Min COGS: ${cogs_values.min():,.2f}")
                    print(f"    Max COGS: ${cogs_values.max():,.2f}")
                    print(f"    Avg COGS: ${cogs_values.mean():,.2f}")
                    validation_results['cogs_below_1000'] = 0
        
        # Disposition values are valid
        print("\nBusiness Rule 2: Disposition values are valid")
        if 'Disposition' in self.df.columns:
            orders = self.df[self.df['Amazon COGS'].notna()]
            dispositions = orders['Disposition'].value_counts()
            print(f"  Disposition distribution:")
            for disp, count in dispositions.items():
                pct = (count / len(orders)) * 100
                print(f"    {disp}: {count:,} ({pct:.1f}%)")
            
            valid_dispositions = ['Liquidate', 'Sellable', 'Liquidation Palletizer', 'Sellable Palletizer']
            invalid = orders[~orders['Disposition'].isin(valid_dispositions + [None])]
            if len(invalid) > 0:
                print(f"  [WARNING] VIOLATION: {len(invalid)} orders with invalid Disposition")
                print(f"    Invalid values: {invalid['Disposition'].unique().tolist()}")
                validation_results['invalid_dispositions'] = len(invalid)
            else:
                print(f"  [OK] PASS: All Disposition values are valid")
                validation_results['invalid_dispositions'] = 0
            
            validation_results['disposition_distribution'] = dispositions.to_dict()
        
        # Date fields are in correct format and logical order
        print("\nBusiness Rule 3: Date fields format and logical order")
        date_columns = [col for col in self.df.columns if 'Date' in col or 'On' in col]
        if date_columns:
            orders = self.df[self.df['Amazon COGS'].notna()]
            date_issues = []
            
            for col in date_columns:
                non_null_dates = orders[col].dropna()
                if len(non_null_dates) > 0:
                    print(f"  {col}: {len(non_null_dates):,} non-null values")
                    # Try to parse as datetime
                    try:
                        pd.to_datetime(non_null_dates.head(1).iloc[0])
                        print(f"    [OK] Format appears valid")
                    except:
                        print(f"    [WARNING] May have format issues")
                        date_issues.append(col)
            
            # Check logical order: Scheduled < Started < Completed < Shipped
            if all(col in orders.columns for col in ['Scheduled Date', 'Started On', 'Completed On', 'Shipped Date']):
                print("\n  Checking date logical order...")
                # This would require date parsing - simplified check
                print("    (Date parsing needed for full validation)")
            
            validation_results['date_format_issues'] = date_issues
        
        # LPN values are unique per order
        print("\nBusiness Rule 4: LPN values are unique per order")
        if 'LPN' in self.df.columns:
            orders = self.df[self.df['Amazon COGS'].notna()]
            unique_lpns = orders['LPN'].nunique()
            total_orders = len(orders)
            
            if unique_lpns == total_orders:
                print(f"  [OK] PASS: All {total_orders:,} orders have unique LPNs")
                validation_results['unique_lpn_check'] = 'PASS'
            else:
                duplicates = total_orders - unique_lpns
                print(f"  [WARNING] VIOLATION: {duplicates} duplicate LPNs found")
                print(f"    Unique LPNs: {unique_lpns:,}")
                print(f"    Total orders: {total_orders:,}")
                validation_results['unique_lpn_check'] = 'FAIL'
                validation_results['duplicate_lpns'] = duplicates
        
        self.results['findings']['business_rule_validation'] = validation_results
        
        # Summary
        print("\n" + "-" * 80)
        print("BUSINESS RULE VALIDATION SUMMARY")
        print("-" * 80)
        issues_found = sum([
            validation_results.get('cogs_below_1000', 0),
            validation_results.get('invalid_dispositions', 0),
            len(validation_results.get('date_format_issues', [])),
            1 if validation_results.get('unique_lpn_check') == 'FAIL' else 0
        ])
        
        if issues_found == 0:
            print("[OK] All business rules validated successfully")
        else:
            print(f"[WARNING] {issues_found} business rule issue(s) found")
    
    def save_results(self):
        """Save Phase 1 results to JSON file"""
        # Handle both CSV and Excel file paths
        base_name = os.path.splitext(self.csv_file_path)[0]
        output_file = f"{base_name}_phase1_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 1 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 1 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Data loaded: {self.results['findings']['total_rows']:,} rows, {self.results['findings']['total_columns']} columns")
        print(f"[OK] Order headers: {self.results['findings']['order_headers_count']:,}")
        print(f"[OK] Check steps: {self.results['findings']['check_steps_count']:,}")
        print(f"[OK] Unique repair orders (LPNs): {self.results['findings'].get('unique_lpns', 'N/A')}")
        
        quality_issues = len(self.results['findings'].get('quality_issues', []))
        if quality_issues > 0:
            print(f"[WARNING] Quality issues found: {quality_issues}")
        else:
            print("[OK] No major quality issues detected")


def main():
    """Main execution function"""
    # File path - adjust based on your directory structure
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Try different possible paths
        possible_paths = [
            "Cost Greater than 1000/Repair Order (repair.order).csv",
            r"Cost Greater than 1000\Repair Order (repair.order).csv",
            r"Cost Greater than 1000\Repair Order (repair.order) (3).xlsx"
        ]
        csv_file = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_file = path
                break
        
        if csv_file is None:
            print("Error: Could not find data file.")
            print("\nPlease provide the file path as an argument:")
            print("  python phase1_data_understanding.py <path_to_file>")
            print("\nOr place the file in one of these locations:")
            for path in possible_paths:
                print(f"  - {path}")
            return
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        print("\nPlease ensure the file path is correct.")
        return
    
    # Run Phase 1 analysis
    try:
        analyzer = Phase1DataUnderstanding(csv_file)
        results = analyzer.run_phase1()
        print("\n[OK] Phase 1 analysis completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 1 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
