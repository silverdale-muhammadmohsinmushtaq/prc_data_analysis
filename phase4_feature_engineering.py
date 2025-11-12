#!/usr/bin/env python3
"""
Phase 4: Feature Engineering
Liquidation Analysis - Create derived features for analysis
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class Phase4FeatureEngineering:
    def __init__(self, preprocessed_csv_path):
        """Initialize Phase 4 feature engineering"""
        self.preprocessed_csv_path = preprocessed_csv_path
        self.df = None
        self.check_cols = []
        self.results = {
            'phase': 'Phase 4: Feature Engineering',
            'timestamp': datetime.now().isoformat(),
            'file_path': preprocessed_csv_path,
            'features_created': {}
        }
        self.output_dir = os.path.dirname(preprocessed_csv_path)
        
    def run_phase4(self):
        """Execute all Phase 4 tasks"""
        print("=" * 80)
        print("PHASE 4: FEATURE ENGINEERING")
        print("=" * 80)
        
        # Load preprocessed data
        self.load_data()
        
        # 4.1 Create Analysis Features
        self.create_order_level_features()
        self.create_check_level_aggregations()
        self.create_specific_check_flags()
        self.create_derived_metrics()
        
        # Save engineered data
        self.save_engineered_data()
        self.save_results()
        
        return self.df, self.results
    
    def load_data(self):
        """Load preprocessed data"""
        print("\n" + "-" * 80)
        print("LOADING PREPROCESSED DATA")
        print("-" * 80)
        
        self.df = pd.read_csv(self.preprocessed_csv_path)
        print(f"[OK] Loaded {len(self.df):,} rows, {len(self.df.columns)} columns")
        
        # Identify check columns
        order_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
                      'Product Category', 'Result of Repair', 'Scheduled Date', 
                      'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'Checks/Title',
                      'Checks/Failed by decision logic Automatically', 'Checks/Status',
                      'is_human_executed', 'is_liquidated', 'cogs_bin', 'processing_days']
        self.check_cols = [c for c in self.df.columns if c not in order_cols]
        print(f"[OK] Identified {len(self.check_cols)} quality check columns")
    
    def create_order_level_features(self):
        """4.1.1 Create order-level features"""
        print("\n" + "-" * 80)
        print("4.1.1 CREATING ORDER-LEVEL FEATURES")
        print("-" * 80)
        
        features_created = []
        
        # is_liquidated (already exists, verify)
        if 'is_liquidated' not in self.df.columns:
            self.df['is_liquidated'] = (self.df['Disposition'].str.strip().str.upper() == 'LIQUIDATE').astype(int)
            features_created.append('is_liquidated')
            print("[OK] Created: is_liquidated")
        else:
            print("[OK] Verified: is_liquidated (already exists)")
        
        # cogs_bin (already exists, verify)
        if 'cogs_bin' not in self.df.columns:
            bins = [0, 1000, 1500, 2000, 2500, 3000, float('inf')]
            labels = ['<$1K', '$1K-$1.5K', '$1.5K-$2K', '$2K-$2.5K', '$2.5K-$3K', '$3K+']
            self.df['cogs_bin'] = pd.cut(
                self.df['Amazon COGS'],
                bins=bins,
                labels=labels,
                include_lowest=True
            )
            features_created.append('cogs_bin')
            print("[OK] Created: cogs_bin")
        else:
            print("[OK] Verified: cogs_bin (already exists)")
        
        # processing_days (already exists, verify)
        if 'processing_days' not in self.df.columns:
            try:
                self.df['Started On'] = pd.to_datetime(self.df['Started On'], errors='coerce')
                self.df['Completed On'] = pd.to_datetime(self.df['Completed On'], errors='coerce')
                self.df['processing_days'] = (
                    self.df['Completed On'] - self.df['Started On']
                ).dt.days
                features_created.append('processing_days')
                print("[OK] Created: processing_days")
            except:
                print("[WARNING] Could not create processing_days")
        else:
            print("[OK] Verified: processing_days (already exists)")
        
        # category_group (simplified category name)
        if 'category_group' not in self.df.columns:
            # Extract the last part of the category path
            self.df['category_group'] = self.df['Product Category'].str.split('/').str[-1].str.strip()
            features_created.append('category_group')
            print("[OK] Created: category_group")
        else:
            print("[OK] Verified: category_group (already exists)")
        
        # high_value_flag (COGS > threshold)
        if 'high_value_flag' not in self.df.columns:
            # Use median + 1.5*IQR as threshold for high value
            q75 = self.df['Amazon COGS'].quantile(0.75)
            q25 = self.df['Amazon COGS'].quantile(0.25)
            iqr = q75 - q25
            threshold = q75 + 1.5 * iqr
            self.df['high_value_flag'] = (self.df['Amazon COGS'] > threshold).astype(int)
            features_created.append('high_value_flag')
            print(f"[OK] Created: high_value_flag (threshold: ${threshold:,.2f})")
        else:
            print("[OK] Verified: high_value_flag (already exists)")
        
        self.results['features_created']['order_level'] = features_created
    
    def create_check_level_aggregations(self):
        """4.1.2 Create check-level aggregations"""
        print("\n" + "-" * 80)
        print("4.1.2 CREATING CHECK-LEVEL AGGREGATIONS")
        print("-" * 80)
        
        features_created = []
        
        # Count checks per order
        if 'total_checks' not in self.df.columns:
            self.df['total_checks'] = 0
            for col in self.check_cols:
                self.df['total_checks'] += self.df[col].notna().astype(int)
            features_created.append('total_checks')
            print(f"[OK] Created: total_checks (mean: {self.df['total_checks'].mean():.2f})")
        else:
            print("[OK] Verified: total_checks (already exists)")
        
        # Count failed checks
        if 'failed_checks_count' not in self.df.columns:
            self.df['failed_checks_count'] = 0
            for col in self.check_cols:
                self.df['failed_checks_count'] += (self.df[col] == 'Failed').astype(int)
            features_created.append('failed_checks_count')
            print(f"[OK] Created: failed_checks_count (mean: {self.df['failed_checks_count'].mean():.2f})")
        else:
            print("[OK] Verified: failed_checks_count (already exists)")
        
        # Count passed checks
        if 'passed_checks_count' not in self.df.columns:
            self.df['passed_checks_count'] = 0
            for col in self.check_cols:
                self.df['passed_checks_count'] += (self.df[col] == 'Passed').astype(int)
            features_created.append('passed_checks_count')
            print(f"[OK] Created: passed_checks_count (mean: {self.df['passed_checks_count'].mean():.2f})")
        else:
            print("[OK] Verified: passed_checks_count (already exists)")
        
        # Failure rate
        if 'failure_rate' not in self.df.columns:
            self.df['failure_rate'] = np.where(
                self.df['total_checks'] > 0,
                self.df['failed_checks_count'] / self.df['total_checks'],
                0
            )
            features_created.append('failure_rate')
            print(f"[OK] Created: failure_rate (mean: {self.df['failure_rate'].mean():.3f})")
        else:
            print("[OK] Verified: failure_rate (already exists)")
        
        self.results['features_created']['check_aggregations'] = features_created
    
    def create_specific_check_flags(self):
        """4.1.3 Create specific check flags"""
        print("\n" + "-" * 80)
        print("4.1.3 CREATING SPECIFIC CHECK FLAGS")
        print("-" * 80)
        
        features_created = []
        
        # Find check columns by searching for keywords
        fraud_checks = [col for col in self.check_cols if 'fraud' in col.lower() or 'Fraud' in col]
        cosmetic_checks = [col for col in self.check_cols if 'scratches' in col.lower() or 'dents' in col.lower() or 'cosmetic' in col.lower()]
        repairable_checks = [col for col in self.check_cols if 'repairable' in col.lower() or 'Repairable' in col]
        works_checks = [col for col in self.check_cols if 'work' in col.lower() and 'does' in col.lower()]
        factory_sealed_checks = [col for col in self.check_cols if 'factory' in col.lower() and 'sealed' in col.lower()]
        
        # Fraud check failed
        if 'fraud_check_failed' not in self.df.columns:
            self.df['fraud_check_failed'] = 0
            for col in fraud_checks:
                self.df['fraud_check_failed'] = self.df['fraud_check_failed'] | (self.df[col] == 'Failed').astype(int)
            self.df['fraud_check_failed'] = self.df['fraud_check_failed'].astype(int)
            features_created.append('fraud_check_failed')
            print(f"[OK] Created: fraud_check_failed (found {len(fraud_checks)} fraud check columns)")
            print(f"      Failed in {self.df['fraud_check_failed'].sum()} orders")
        else:
            print("[OK] Verified: fraud_check_failed (already exists)")
        
        # Cosmetic check failed
        if 'cosmetic_check_failed' not in self.df.columns:
            self.df['cosmetic_check_failed'] = 0
            for col in cosmetic_checks:
                self.df['cosmetic_check_failed'] = self.df['cosmetic_check_failed'] | (self.df[col] == 'Failed').astype(int)
            self.df['cosmetic_check_failed'] = self.df['cosmetic_check_failed'].astype(int)
            features_created.append('cosmetic_check_failed')
            print(f"[OK] Created: cosmetic_check_failed (found {len(cosmetic_checks)} cosmetic check columns)")
            print(f"      Failed in {self.df['cosmetic_check_failed'].sum()} orders")
        else:
            print("[OK] Verified: cosmetic_check_failed (already exists)")
        
        # Repairable check failed
        if 'repairable_check_failed' not in self.df.columns:
            self.df['repairable_check_failed'] = 0
            for col in repairable_checks:
                self.df['repairable_check_failed'] = self.df['repairable_check_failed'] | (self.df[col] == 'Failed').astype(int)
            self.df['repairable_check_failed'] = self.df['repairable_check_failed'].astype(int)
            features_created.append('repairable_check_failed')
            print(f"[OK] Created: repairable_check_failed (found {len(repairable_checks)} repairable check columns)")
            print(f"      Failed in {self.df['repairable_check_failed'].sum()} orders")
        else:
            print("[OK] Verified: repairable_check_failed (already exists)")
        
        # Works check passed
        if 'works_check_passed' not in self.df.columns:
            self.df['works_check_passed'] = 0
            for col in works_checks:
                self.df['works_check_passed'] = self.df['works_check_passed'] | (self.df[col] == 'Passed').astype(int)
            self.df['works_check_passed'] = self.df['works_check_passed'].astype(int)
            features_created.append('works_check_passed')
            print(f"[OK] Created: works_check_passed (found {len(works_checks)} works check columns)")
            print(f"      Passed in {self.df['works_check_passed'].sum()} orders")
        else:
            print("[OK] Verified: works_check_passed (already exists)")
        
        # Factory sealed check passed
        if 'factory_sealed_check_passed' not in self.df.columns:
            self.df['factory_sealed_check_passed'] = 0
            for col in factory_sealed_checks:
                self.df['factory_sealed_check_passed'] = self.df['factory_sealed_check_passed'] | (self.df[col] == 'Passed').astype(int)
            self.df['factory_sealed_check_passed'] = self.df['factory_sealed_check_passed'].astype(int)
            features_created.append('factory_sealed_check_passed')
            print(f"[OK] Created: factory_sealed_check_passed (found {len(factory_sealed_checks)} factory sealed check columns)")
            print(f"      Passed in {self.df['factory_sealed_check_passed'].sum()} orders")
        else:
            print("[OK] Verified: factory_sealed_check_passed (already exists)")
        
        # Store which check columns were used
        self.results['features_created']['check_flags'] = {
            'features': features_created,
            'fraud_checks_found': len(fraud_checks),
            'cosmetic_checks_found': len(cosmetic_checks),
            'repairable_checks_found': len(repairable_checks),
            'works_checks_found': len(works_checks),
            'factory_sealed_checks_found': len(factory_sealed_checks)
        }
    
    def create_derived_metrics(self):
        """4.1.4 Create derived metrics"""
        print("\n" + "-" * 80)
        print("4.1.4 CREATING DERIVED METRICS")
        print("-" * 80)
        
        features_created = []
        
        # Value lost (COGS for liquidated items)
        if 'value_lost' not in self.df.columns:
            self.df['value_lost'] = np.where(
                self.df['is_liquidated'] == 1,
                self.df['Amazon COGS'],
                0
            )
            features_created.append('value_lost')
            total_value_lost = self.df['value_lost'].sum()
            print(f"[OK] Created: value_lost")
            print(f"      Total value lost: ${total_value_lost:,.2f}")
        else:
            print("[OK] Verified: value_lost (already exists)")
        
        # Recovery potential (items that could potentially be recovered)
        # This is a hypothetical metric - items that failed but might be recoverable
        if 'recovery_potential' not in self.df.columns:
            # Items that are liquidated but passed "works" check might have recovery potential
            self.df['recovery_potential'] = np.where(
                (self.df['is_liquidated'] == 1) & (self.df['works_check_passed'] == 1),
                self.df['Amazon COGS'],
                0
            )
            features_created.append('recovery_potential')
            total_recovery = self.df['recovery_potential'].sum()
            print(f"[OK] Created: recovery_potential")
            print(f"      Total recovery potential: ${total_recovery:,.2f}")
            print(f"      Items with recovery potential: {(self.df['recovery_potential'] > 0).sum()}")
        else:
            print("[OK] Verified: recovery_potential (already exists)")
        
        # Additional useful metrics
        # Days to ship
        if 'days_to_ship' not in self.df.columns:
            try:
                self.df['Scheduled Date'] = pd.to_datetime(self.df['Scheduled Date'], errors='coerce')
                self.df['Shipped Date'] = pd.to_datetime(self.df['Shipped Date'], errors='coerce')
                self.df['days_to_ship'] = (self.df['Shipped Date'] - self.df['Scheduled Date']).dt.days
                features_created.append('days_to_ship')
                print(f"[OK] Created: days_to_ship (mean: {self.df['days_to_ship'].mean():.2f} days)")
            except:
                print("[WARNING] Could not create days_to_ship")
        
        # Check efficiency (passed/total ratio)
        if 'check_efficiency' not in self.df.columns:
            self.df['check_efficiency'] = np.where(
                self.df['total_checks'] > 0,
                self.df['passed_checks_count'] / self.df['total_checks'],
                0
            )
            features_created.append('check_efficiency')
            print(f"[OK] Created: check_efficiency (mean: {self.df['check_efficiency'].mean():.3f})")
        
        self.results['features_created']['derived_metrics'] = features_created
    
    def save_engineered_data(self):
        """Save feature-engineered data"""
        print("\n" + "-" * 80)
        print("SAVING FEATURE-ENGINEERED DATA")
        print("-" * 80)
        
        base_name = os.path.splitext(self.preprocessed_csv_path)[0]
        output_csv = f"{base_name}_features.csv"
        
        # Save to CSV
        self.df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"[OK] Saved feature-engineered data to: {output_csv}")
        print(f"  Rows: {len(self.df):,}")
        print(f"  Columns: {len(self.df.columns)}")
        
        # Show summary of new features
        print("\n" + "-" * 80)
        print("FEATURE SUMMARY:")
        print("-" * 80)
        
        # List all feature columns (non-check, non-original order columns)
        original_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
                       'Product Category', 'Result of Repair', 'Scheduled Date', 
                       'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'Checks/Title',
                       'Checks/Failed by decision logic Automatically', 'Checks/Status',
                       'is_human_executed']
        
        feature_cols = [col for col in self.df.columns if col not in original_cols and col not in self.check_cols]
        
        print(f"\nEngineered Features ({len(feature_cols)}):")
        for i, col in enumerate(feature_cols, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\nOriginal Order Columns: {len(original_cols)}")
        print(f"Quality Check Columns: {len(self.check_cols)}")
        print(f"Total Columns: {len(self.df.columns)}")
        
        self.results['output_file'] = output_csv
        self.results['total_features'] = len(feature_cols)
        self.results['feature_columns'] = feature_cols
    
    def save_results(self):
        """Save Phase 4 results to JSON"""
        base_name = os.path.splitext(self.preprocessed_csv_path)[0]
        output_file = f"{base_name}_phase4_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 4 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 4 SUMMARY:")
        print("-" * 80)
        total_features = sum(len(v) if isinstance(v, list) else 1 for v in self.results['features_created'].values())
        print(f"[OK] Total features created/verified: {total_features}")
        print(f"[OK] Feature-engineered data saved")
        print(f"[OK] Ready for analysis and modeling")


def main():
    """Main execution function"""
    import sys
    
    # File path
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Try default path
        default_path = r"Cost Greater than 1000\Repair Order (repair.order)_preprocessed.csv"
        if os.path.exists(default_path):
            csv_file = default_path
        else:
            print("Error: Please provide the preprocessed CSV file path")
            print("Usage: python phase4_feature_engineering.py <preprocessed_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 4 feature engineering
    try:
        engineer = Phase4FeatureEngineering(csv_file)
        df, results = engineer.run_phase4()
        print("\n[OK] Phase 4 feature engineering completed successfully!")
        return df, results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 4 feature engineering: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    main()

