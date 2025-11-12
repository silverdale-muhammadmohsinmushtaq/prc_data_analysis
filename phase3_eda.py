#!/usr/bin/env python3
"""
Phase 3: Exploratory Data Analysis (EDA)
Liquidation Analysis - Comprehensive Data Exploration
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class Phase3EDA:
    def __init__(self, preprocessed_csv_path):
        """Initialize Phase 3 EDA"""
        self.preprocessed_csv_path = preprocessed_csv_path
        self.df = None
        self.results = {
            'phase': 'Phase 3: Exploratory Data Analysis',
            'timestamp': datetime.now().isoformat(),
            'file_path': preprocessed_csv_path,
            'findings': {}
        }
        self.output_dir = os.path.dirname(preprocessed_csv_path)
        
    def run_phase3(self):
        """Execute all Phase 3 tasks"""
        print("=" * 80)
        print("PHASE 3: EXPLORATORY DATA ANALYSIS (EDA)")
        print("=" * 80)
        
        # Load preprocessed data
        self.load_data()
        
        # 3.1 Univariate Analysis
        self.univariate_analysis()
        
        # 3.2 Bivariate Analysis
        self.bivariate_analysis()
        
        # 3.3 Check-Level Analysis
        self.check_level_analysis()
        
        # Save results
        self.save_results()
        
        return self.results
    
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
    
    def univariate_analysis(self):
        """3.1 Univariate Analysis"""
        print("\n" + "=" * 80)
        print("3.1 UNIVARIATE ANALYSIS")
        print("=" * 80)
        
        # 3.1.1 Target variable analysis
        self.analyze_target_variable()
        
        # 3.1.2 COGS analysis
        self.analyze_cogs()
        
        # 3.1.3 Categorical variables
        self.analyze_categorical_variables()
        
        # 3.1.4 Temporal analysis
        self.analyze_temporal_data()
    
    def analyze_target_variable(self):
        """3.1.1 Target variable analysis"""
        print("\n" + "-" * 80)
        print("3.1.1 TARGET VARIABLE ANALYSIS")
        print("-" * 80)
        
        # Distribution of Disposition
        disposition_counts = self.df['Disposition'].value_counts()
        disposition_pct = self.df['Disposition'].value_counts(normalize=True) * 100
        
        print("\nDisposition Distribution:")
        for disp in disposition_counts.index:
            print(f"  {disp}: {disposition_counts[disp]:,} ({disposition_pct[disp]:.1f}%)")
        
        # Liquidation rate
        liquidation_rate = (self.df['is_liquidated'] == 1).sum() / len(self.df) * 100
        print(f"\nOverall Liquidation Rate: {liquidation_rate:.2f}%")
        print(f"  Liquidated: {(self.df['is_liquidated'] == 1).sum():,}")
        print(f"  Sellable: {(self.df['is_liquidated'] == 0).sum():,}")
        
        # Store results
        self.results['findings']['target_variable'] = {
            'disposition_distribution': disposition_counts.to_dict(),
            'disposition_percentages': disposition_pct.to_dict(),
            'liquidation_rate': round(liquidation_rate, 2),
            'liquidated_count': int((self.df['is_liquidated'] == 1).sum()),
            'sellable_count': int((self.df['is_liquidated'] == 0).sum())
        }
    
    def analyze_cogs(self):
        """3.1.2 COGS analysis"""
        print("\n" + "-" * 80)
        print("3.1.2 COGS ANALYSIS")
        print("-" * 80)
        
        cogs = self.df['Amazon COGS']
        
        # Distribution statistics
        stats = {
            'mean': cogs.mean(),
            'median': cogs.median(),
            'std': cogs.std(),
            'min': cogs.min(),
            'max': cogs.max(),
            'q25': cogs.quantile(0.25),
            'q75': cogs.quantile(0.75)
        }
        
        print("\nCOGS Distribution Statistics:")
        print(f"  Mean: ${stats['mean']:,.2f}")
        print(f"  Median: ${stats['median']:,.2f}")
        print(f"  Std Dev: ${stats['std']:,.2f}")
        print(f"  Min: ${stats['min']:,.2f}")
        print(f"  Max: ${stats['max']:,.2f}")
        print(f"  25th Percentile: ${stats['q25']:,.2f}")
        print(f"  75th Percentile: ${stats['q75']:,.2f}")
        
        # Outliers (using IQR method)
        iqr = stats['q75'] - stats['q25']
        lower_bound = stats['q25'] - 1.5 * iqr
        upper_bound = stats['q75'] + 1.5 * iqr
        outliers = cogs[(cogs < lower_bound) | (cogs > upper_bound)]
        
        print(f"\nCOGS Outliers (IQR method):")
        print(f"  Lower bound: ${lower_bound:,.2f}")
        print(f"  Upper bound: ${upper_bound:,.2f}")
        print(f"  Outliers found: {len(outliers)} ({len(outliers)/len(cogs)*100:.1f}%)")
        if len(outliers) > 0:
            print(f"  Outlier range: ${outliers.min():,.2f} - ${outliers.max():,.2f}")
        
        # COGS by Disposition
        print(f"\nCOGS by Disposition:")
        cogs_by_disp = self.df.groupby('Disposition')['Amazon COGS'].agg(['mean', 'median', 'std', 'min', 'max'])
        for disp in cogs_by_disp.index:
            print(f"  {disp}:")
            print(f"    Mean: ${cogs_by_disp.loc[disp, 'mean']:,.2f}")
            print(f"    Median: ${cogs_by_disp.loc[disp, 'median']:,.2f}")
            print(f"    Std Dev: ${cogs_by_disp.loc[disp, 'std']:,.2f}")
        
        # Store results
        self.results['findings']['cogs_analysis'] = {
            'statistics': {k: round(v, 2) for k, v in stats.items()},
            'outliers_count': int(len(outliers)),
            'outliers_percentage': round(len(outliers)/len(cogs)*100, 2),
            'by_disposition': cogs_by_disp.to_dict()
        }
    
    def analyze_categorical_variables(self):
        """3.1.3 Categorical variables"""
        print("\n" + "-" * 80)
        print("3.1.3 CATEGORICAL VARIABLES ANALYSIS")
        print("-" * 80)
        
        # Product Category
        print("\nProduct Category Distribution:")
        category_counts = self.df['Product Category'].value_counts()
        print(f"  Total categories: {len(category_counts)}")
        print(f"  Top 10 categories:")
        for i, (cat, count) in enumerate(category_counts.head(10).items(), 1):
            pct = count / len(self.df) * 100
            print(f"    {i:2d}. {cat}: {count:,} ({pct:.1f}%)")
        
        # Result of Repair
        print("\nResult of Repair Distribution:")
        repair_result_counts = self.df['Result of Repair'].value_counts()
        print(f"  Total unique results: {len(repair_result_counts)}")
        print(f"  Top 10 results:")
        for i, (result, count) in enumerate(repair_result_counts.head(10).items(), 1):
            pct = count / len(self.df) * 100
            print(f"    {i:2d}. {result}: {count:,} ({pct:.1f}%)")
        
        # Product
        print("\nProduct Distribution:")
        product_counts = self.df['Product'].value_counts()
        print(f"  Total unique products: {len(product_counts)}")
        print(f"  Top 10 products:")
        for i, (product, count) in enumerate(product_counts.head(10).items(), 1):
            pct = count / len(self.df) * 100
            print(f"    {i:2d}. {product[:60]}...: {count:,} ({pct:.1f}%)")
        
        # Store results
        self.results['findings']['categorical_analysis'] = {
            'product_category': {
                'total_categories': int(len(category_counts)),
                'top_10': category_counts.head(10).to_dict()
            },
            'result_of_repair': {
                'total_unique': int(len(repair_result_counts)),
                'top_10': repair_result_counts.head(10).to_dict()
            },
            'product': {
                'total_unique': int(len(product_counts)),
                'top_10': product_counts.head(10).to_dict()
            }
        }
    
    def analyze_temporal_data(self):
        """3.1.4 Temporal analysis"""
        print("\n" + "-" * 80)
        print("3.1.4 TEMPORAL ANALYSIS")
        print("-" * 80)
        
        # Convert date columns
        date_cols = ['Scheduled Date', 'Started On', 'Completed On', 'Shipped Date']
        date_data = {}
        
        for col in date_cols:
            if col in self.df.columns:
                try:
                    dates = pd.to_datetime(self.df[col], errors='coerce')
                    non_null = dates.notna().sum()
                    if non_null > 0:
                        date_data[col] = {
                            'non_null_count': int(non_null),
                            'date_range': {
                                'min': str(dates.min()),
                                'max': str(dates.max())
                            }
                        }
                        print(f"\n{col}:")
                        print(f"  Non-null values: {non_null:,} / {len(self.df):,}")
                        print(f"  Date range: {dates.min()} to {dates.max()}")
                except:
                    print(f"\n{col}: Could not parse dates")
        
        # Processing days analysis
        if 'processing_days' in self.df.columns:
            proc_days = self.df['processing_days'].dropna()
            if len(proc_days) > 0:
                print(f"\nProcessing Days (Completed - Started):")
                print(f"  Mean: {proc_days.mean():.1f} days")
                print(f"  Median: {proc_days.median():.1f} days")
                print(f"  Min: {proc_days.min():.1f} days")
                print(f"  Max: {proc_days.max():.1f} days")
                date_data['processing_days'] = {
                    'mean': round(proc_days.mean(), 2),
                    'median': round(proc_days.median(), 2),
                    'min': round(proc_days.min(), 2),
                    'max': round(proc_days.max(), 2)
                }
        
        self.results['findings']['temporal_analysis'] = date_data
    
    def bivariate_analysis(self):
        """3.2 Bivariate Analysis"""
        print("\n" + "=" * 80)
        print("3.2 BIVARIATE ANALYSIS")
        print("=" * 80)
        
        # 3.2.1 Disposition vs COGS
        self.analyze_disposition_vs_cogs()
        
        # 3.2.2 Disposition vs Product Category
        self.analyze_disposition_vs_category()
        
        # 3.2.3 Disposition vs Result of Repair
        self.analyze_disposition_vs_repair_result()
        
        # 3.2.4 Disposition vs Product
        self.analyze_disposition_vs_product()
    
    def analyze_disposition_vs_cogs(self):
        """3.2.1 Disposition vs COGS"""
        print("\n" + "-" * 80)
        print("3.2.1 DISPOSITION VS COGS")
        print("-" * 80)
        
        # Average and median COGS by Disposition
        cogs_by_disp = self.df.groupby('Disposition')['Amazon COGS'].agg(['mean', 'median', 'std'])
        print("\nCOGS Statistics by Disposition:")
        for disp in cogs_by_disp.index:
            print(f"  {disp}:")
            print(f"    Mean: ${cogs_by_disp.loc[disp, 'mean']:,.2f}")
            print(f"    Median: ${cogs_by_disp.loc[disp, 'median']:,.2f}")
            print(f"    Std Dev: ${cogs_by_disp.loc[disp, 'std']:,.2f}")
        
        # Liquidation rate by COGS bins
        print("\nLiquidation Rate by COGS Bins:")
        if 'cogs_bin' in self.df.columns:
            bin_analysis = self.df.groupby('cogs_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean']
            }).round(4)
            bin_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
            bin_analysis['liquidation_rate_pct'] = bin_analysis['liquidation_rate'] * 100
            
            for bin_name in bin_analysis.index:
                row = bin_analysis.loc[bin_name]
                print(f"  {bin_name}:")
                print(f"    Liquidated: {int(row['liquidated_count'])} / {int(row['total_count'])} ({row['liquidation_rate_pct']:.1f}%)")
        
        # Store results
        self.results['findings']['disposition_vs_cogs'] = {
            'cogs_by_disposition': cogs_by_disp.to_dict(),
            'liquidation_rate_by_bin': bin_analysis.to_dict() if 'cogs_bin' in self.df.columns else {}
        }
    
    def analyze_disposition_vs_category(self):
        """3.2.2 Disposition vs Product Category"""
        print("\n" + "-" * 80)
        print("3.2.2 DISPOSITION VS PRODUCT CATEGORY")
        print("-" * 80)
        
        category_analysis = self.df.groupby('Product Category').agg({
            'is_liquidated': ['sum', 'count', 'mean'],
            'Amazon COGS': ['mean', 'sum']
        }).round(2)
        category_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate', 'avg_cogs', 'total_cogs']
        category_analysis['liquidation_rate_pct'] = category_analysis['liquidation_rate'] * 100
        category_analysis['value_lost'] = category_analysis['liquidated_count'] * category_analysis['avg_cogs']
        category_analysis = category_analysis.sort_values('liquidated_count', ascending=False)
        
        print("\nTop 15 Categories by Liquidation Count:")
        print(f"{'Category':<50} {'Liquidated':<12} {'Total':<10} {'Rate %':<10} {'Avg COGS':<12} {'Value Lost':<15}")
        print("-" * 110)
        for cat, row in category_analysis.head(15).iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {int(row['liquidated_count']):<12} {int(row['total_count']):<10} "
                  f"{row['liquidation_rate_pct']:<10.1f} ${row['avg_cogs']:<11,.2f} ${row['value_lost']:<14,.2f}")
        
        # Store results
        self.results['findings']['disposition_vs_category'] = {
            'top_categories_by_liquidation': category_analysis.head(15).to_dict('index')
        }
    
    def analyze_disposition_vs_repair_result(self):
        """3.2.3 Disposition vs Result of Repair"""
        print("\n" + "-" * 80)
        print("3.2.3 DISPOSITION VS RESULT OF REPAIR")
        print("-" * 80)
        
        # Focus on liquidated items
        liquidated = self.df[self.df['is_liquidated'] == 1]
        repair_result_analysis = liquidated.groupby('Result of Repair').agg({
            'is_liquidated': 'count',
            'Amazon COGS': ['mean', 'sum']
        }).round(2)
        repair_result_analysis.columns = ['count', 'avg_cogs', 'total_value_lost']
        repair_result_analysis = repair_result_analysis.sort_values('count', ascending=False)
        repair_result_analysis['percentage'] = (repair_result_analysis['count'] / len(liquidated) * 100).round(2)
        
        print("\nLiquidation Reasons (Result of Repair):")
        print(f"{'Reason':<60} {'Count':<10} {'%':<10} {'Avg COGS':<12} {'Total Value Lost':<15}")
        print("-" * 110)
        for reason, row in repair_result_analysis.iterrows():
            reason_short = reason[:58] if len(reason) > 58 else reason
            print(f"{reason_short:<60} {int(row['count']):<10} {row['percentage']:<10.1f} "
                  f"${row['avg_cogs']:<11,.2f} ${row['total_value_lost']:<14,.2f}")
        
        # Store results
        self.results['findings']['disposition_vs_repair_result'] = {
            'liquidation_reasons': repair_result_analysis.to_dict('index')
        }
    
    def analyze_disposition_vs_product(self):
        """3.2.4 Disposition vs Product"""
        print("\n" + "-" * 80)
        print("3.2.4 DISPOSITION VS PRODUCT")
        print("-" * 80)
        
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        }).round(4)
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        product_analysis['liquidation_rate_pct'] = product_analysis['liquidation_rate'] * 100
        product_analysis = product_analysis.sort_values('liquidated_count', ascending=False)
        
        print("\nTop 15 Products by Liquidation Count:")
        print(f"{'Product':<60} {'Liquidated':<12} {'Total':<10} {'Rate %':<10}")
        print("-" * 95)
        for product, row in product_analysis.head(15).iterrows():
            product_short = product[:58] if len(product) > 58 else product
            print(f"{product_short:<60} {int(row['liquidated_count']):<12} {int(row['total_count']):<10} "
                  f"{row['liquidation_rate_pct']:<10.1f}")
        
        # Products with high liquidation rates (>=50% and at least 3 orders)
        high_liquidation = product_analysis[
            (product_analysis['liquidation_rate_pct'] >= 50) & 
            (product_analysis['total_count'] >= 3)
        ].sort_values('liquidation_rate_pct', ascending=False)
        
        print(f"\nProducts with High Liquidation Rate (>=50%, min 3 orders): {len(high_liquidation)}")
        if len(high_liquidation) > 0:
            print(f"{'Product':<60} {'Liquidation Rate %':<20}")
            print("-" * 80)
            for product, row in high_liquidation.head(10).iterrows():
                product_short = product[:58] if len(product) > 58 else product
                print(f"{product_short:<60} {row['liquidation_rate_pct']:<20.1f}")
        
        # Store results
        self.results['findings']['disposition_vs_product'] = {
            'top_products_by_liquidation': product_analysis.head(15).to_dict('index'),
            'high_liquidation_products': high_liquidation.head(10).to_dict('index') if len(high_liquidation) > 0 else {}
        }
    
    def check_level_analysis(self):
        """3.3 Check-Level Analysis"""
        print("\n" + "=" * 80)
        print("3.3 CHECK-LEVEL ANALYSIS")
        print("=" * 80)
        
        # 3.3.1 Check failure analysis
        self.analyze_check_failures()
        
        # 3.3.2 Check-by-check comparison
        self.compare_checks_by_disposition()
    
    def analyze_check_failures(self):
        """3.3.1 Check failure analysis"""
        print("\n" + "-" * 80)
        print("3.3.1 CHECK FAILURE ANALYSIS")
        print("-" * 80)
        
        # Count failed checks per order
        failed_counts = []
        for idx, row in self.df.iterrows():
            failed = sum(1 for col in self.check_cols if pd.notna(row[col]) and row[col] == 'Failed')
            failed_counts.append(failed)
        
        self.df['failed_checks_count'] = failed_counts
        
        print("\nFailed Checks per Order:")
        failed_stats = self.df['failed_checks_count'].describe()
        print(f"  Mean: {failed_stats['mean']:.2f}")
        print(f"  Median: {failed_stats['50%']:.2f}")
        print(f"  Min: {failed_stats['min']:.0f}")
        print(f"  Max: {failed_stats['max']:.0f}")
        
        # Average failed checks by Disposition
        failed_by_disp = self.df.groupby('Disposition')['failed_checks_count'].agg(['mean', 'median'])
        print("\nAverage Failed Checks by Disposition:")
        for disp in failed_by_disp.index:
            print(f"  {disp}:")
            print(f"    Mean: {failed_by_disp.loc[disp, 'mean']:.2f}")
            print(f"    Median: {failed_by_disp.loc[disp, 'median']:.2f}")
        
        # Most frequently failed checks overall
        check_failure_counts = {}
        for col in self.check_cols:
            failed = (self.df[col] == 'Failed').sum()
            if failed > 0:
                check_failure_counts[col] = failed
        
        check_failure_df = pd.DataFrame.from_dict(check_failure_counts, orient='index', columns=['failure_count'])
        check_failure_df = check_failure_df.sort_values('failure_count', ascending=False)
        check_failure_df['failure_rate'] = (check_failure_df['failure_count'] / len(self.df) * 100).round(2)
        
        print("\nTop 15 Most Frequently Failed Checks (Overall):")
        print(f"{'Check Name':<60} {'Failures':<12} {'Failure Rate %':<15}")
        print("-" * 90)
        for check, row in check_failure_df.head(15).iterrows():
            check_short = check[:58] if len(check) > 58 else check
            print(f"{check_short:<60} {int(row['failure_count']):<12} {row['failure_rate']:<15.1f}")
        
        # Most frequently failed checks in liquidated orders
        liquidated = self.df[self.df['is_liquidated'] == 1]
        check_failure_liquidated = {}
        for col in self.check_cols:
            failed = (liquidated[col] == 'Failed').sum()
            if failed > 0:
                check_failure_liquidated[col] = failed
        
        check_failure_liquidated_df = pd.DataFrame.from_dict(check_failure_liquidated, orient='index', columns=['failure_count'])
        check_failure_liquidated_df = check_failure_liquidated_df.sort_values('failure_count', ascending=False)
        check_failure_liquidated_df['failure_rate'] = (check_failure_liquidated_df['failure_count'] / len(liquidated) * 100).round(2)
        
        print("\nTop 15 Most Frequently Failed Checks (Liquidated Orders Only):")
        print(f"{'Check Name':<60} {'Failures':<12} {'Failure Rate %':<15}")
        print("-" * 90)
        for check, row in check_failure_liquidated_df.head(15).iterrows():
            check_short = check[:58] if len(check) > 58 else check
            print(f"{check_short:<60} {int(row['failure_count']):<12} {row['failure_rate']:<15.1f}")
        
        # Store results
        self.results['findings']['check_failure_analysis'] = {
            'failed_checks_per_order': {
                'mean': round(failed_stats['mean'], 2),
                'median': round(failed_stats['50%'], 2),
                'min': int(failed_stats['min']),
                'max': int(failed_stats['max'])
            },
            'failed_checks_by_disposition': failed_by_disp.to_dict(),
            'top_failed_checks_overall': check_failure_df.head(15).to_dict('index'),
            'top_failed_checks_liquidated': check_failure_liquidated_df.head(15).to_dict('index')
        }
    
    def compare_checks_by_disposition(self):
        """3.3.2 Check-by-check comparison"""
        print("\n" + "-" * 80)
        print("3.3.2 CHECK-BY-CHECK COMPARISON")
        print("-" * 80)
        
        liquidated = self.df[self.df['is_liquidated'] == 1]
        sellable = self.df[self.df['is_liquidated'] == 0]
        
        check_comparison = []
        
        for col in self.check_cols:
            # Calculate failure rates
            liquidated_failed = (liquidated[col] == 'Failed').sum()
            liquidated_total = liquidated[col].notna().sum()
            liquidated_rate = (liquidated_failed / liquidated_total * 100) if liquidated_total > 0 else 0
            
            sellable_failed = (sellable[col] == 'Failed').sum()
            sellable_total = sellable[col].notna().sum()
            sellable_rate = (sellable_failed / sellable_total * 100) if sellable_total > 0 else 0
            
            difference = liquidated_rate - sellable_rate
            
            if liquidated_total > 0 or sellable_total > 0:
                check_comparison.append({
                    'check_name': col,
                    'liquidated_failure_rate': round(liquidated_rate, 2),
                    'sellable_failure_rate': round(sellable_rate, 2),
                    'difference': round(difference, 2),
                    'liquidated_count': int(liquidated_failed),
                    'sellable_count': int(sellable_failed)
                })
        
        comparison_df = pd.DataFrame(check_comparison)
        comparison_df = comparison_df.sort_values('difference', ascending=False)
        
        print("\nTop 15 Checks with Biggest Difference (Liquidated vs Sellable):")
        print(f"{'Check Name':<50} {'Liquidated %':<15} {'Sellable %':<15} {'Difference %':<15}")
        print("-" * 95)
        for _, row in comparison_df.head(15).iterrows():
            check_short = row['check_name'][:48] if len(row['check_name']) > 48 else row['check_name']
            print(f"{check_short:<50} {row['liquidated_failure_rate']:<15.1f} "
                  f"{row['sellable_failure_rate']:<15.1f} {row['difference']:<15.1f}")
        
        # Store results
        self.results['findings']['check_comparison'] = {
            'top_differences': comparison_df.head(15).to_dict('records')
        }
    
    def save_results(self):
        """Save Phase 3 results to JSON"""
        base_name = os.path.splitext(self.preprocessed_csv_path)[0]
        output_file = f"{base_name}_phase3_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 3 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 3 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Univariate analysis completed")
        print(f"[OK] Bivariate analysis completed")
        print(f"[OK] Check-level analysis completed")
        print(f"[OK] All findings saved to JSON")


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
            print("Usage: python phase3_eda.py <preprocessed_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 3 analysis
    try:
        analyzer = Phase3EDA(csv_file)
        results = analyzer.run_phase3()
        print("\n[OK] Phase 3 EDA completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 3 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

