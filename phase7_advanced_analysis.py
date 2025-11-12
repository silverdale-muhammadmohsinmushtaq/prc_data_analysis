#!/usr/bin/env python3
"""
Phase 7: Advanced Analysis
Liquidation Analysis - Advanced questions, pattern recognition, and root cause analysis
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")

class Phase7AdvancedAnalysis:
    def __init__(self, features_csv_path):
        """Initialize Phase 7 advanced analysis"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.check_cols = []
        self.results = {
            'phase': 'Phase 7: Advanced Analysis',
            'timestamp': datetime.now().isoformat(),
            'file_path': features_csv_path,
            'findings': {}
        }
        self.output_dir = os.path.dirname(features_csv_path)
        self.graphs_dir = os.path.join(self.output_dir, "Phase7_Graphs")
        os.makedirs(self.graphs_dir, exist_ok=True)
        
    def run_phase7(self):
        """Execute all Phase 7 tasks"""
        print("=" * 80)
        print("PHASE 7: ADVANCED ANALYSIS")
        print("=" * 80)
        
        # Load feature-engineered data
        self.load_data()
        
        # 7.1 Additional Questions Analysis (Q8-Q25)
        self.analyze_additional_questions()
        
        # 7.2 Pattern Recognition
        self.pattern_recognition()
        
        # 7.3 Root Cause Analysis
        self.root_cause_analysis()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def load_data(self):
        """Load feature-engineered data"""
        print("\n" + "-" * 80)
        print("LOADING FEATURE-ENGINEERED DATA")
        print("-" * 80)
        
        self.df = pd.read_csv(self.features_csv_path)
        print(f"[OK] Loaded {len(self.df):,} rows, {len(self.df.columns)} columns")
        
        # Identify check columns
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
        self.check_cols = [c for c in self.df.columns if c not in order_cols]
        print(f"[OK] Identified {len(self.check_cols)} quality check columns")
        
        # Separate liquidated and sellable
        self.liquidated = self.df[self.df['is_liquidated'] == 1]
        self.sellable = self.df[self.df['is_liquidated'] == 0]
    
    def analyze_additional_questions(self):
        """7.1 Additional Questions Analysis (Q8-Q25)"""
        print("\n" + "=" * 80)
        print("7.1 ADDITIONAL QUESTIONS ANALYSIS (Q8-Q25)")
        print("=" * 80)
        
        # Q8: Time Analysis
        self.q8_time_analysis()
        
        # Q9: Check Correlation
        self.q9_check_correlation()
        
        # Q10: Product Consistency
        self.q10_product_consistency()
        
        # Q11: COGS Threshold Analysis
        self.q11_cogs_threshold_analysis()
        
        # Q12: Reason by COGS
        self.q12_reason_by_cogs()
        
        # Q14: "Does it Work?" Success Rate
        self.q14_works_check_success_rate()
        
        # Q15: Fraud Recovery Potential
        self.q15_fraud_recovery_potential()
        
        # Q16: Category Value Impact
        self.q16_category_value_impact()
        
        # Q17: Exception Candidates
        self.q17_exception_candidates()
        
        # Q18: Processing Time Impact
        self.q18_processing_time_impact()
        
        # Q19: False Positive Rate
        self.q19_false_positive_rate()
        
        # Q21: Fraud Check Impact
        self.q21_fraud_check_impact()
        
        # Q22: Working Items Liquidated
        self.q22_working_items_liquidated()
        
        # Q23: Failure Count Analysis
        self.q23_failure_count_analysis()
        
        # Q24: Inconsistent Products
        self.q24_inconsistent_products()
        
        # Q25: Recovery Potential
        self.q25_recovery_potential()
    
    def q8_time_analysis(self):
        """Q8: Time Analysis - Processing duration"""
        print("\n" + "-" * 80)
        print("Q8: Time Analysis - Processing Duration")
        print("-" * 80)
        
        if 'processing_days' in self.df.columns:
            liquidated_time = self.liquidated['processing_days'].dropna()
            sellable_time = self.sellable['processing_days'].dropna()
            
            print("\nProcessing Time (Started On to Completed On):")
            print(f"{'Metric':<25} {'Liquidated':<20} {'Sellable':<20}")
            print("-" * 70)
            print(f"{'Mean (days)':<25} {liquidated_time.mean():<20.2f} {sellable_time.mean():<20.2f}")
            print(f"{'Median (days)':<25} {liquidated_time.median():<20.2f} {sellable_time.median():<20.2f}")
            print(f"{'Std Dev (days)':<25} {liquidated_time.std():<20.2f} {sellable_time.std():<20.2f}")
            print(f"{'Min (days)':<25} {liquidated_time.min():<20.2f} {sellable_time.min():<20.2f}")
            print(f"{'Max (days)':<25} {liquidated_time.max():<20.2f} {sellable_time.max():<20.2f}")
            
            self.results['findings']['q8_time_analysis'] = {
                'liquidated_mean_days': round(liquidated_time.mean(), 2),
                'sellable_mean_days': round(sellable_time.mean(), 2),
                'difference_days': round(liquidated_time.mean() - sellable_time.mean(), 2)
            }
    
    def q9_check_correlation(self):
        """Q9: Check Correlation - Which checks correlate most with liquidation"""
        print("\n" + "-" * 80)
        print("Q9: Check Correlation - Strongest Predictors")
        print("-" * 80)
        
        check_correlations = {}
        
        for col in self.check_cols:
            # Create binary: 1 if failed, 0 otherwise
            failed = (self.df[col] == 'Failed').astype(int)
            if failed.sum() > 0:  # Only if there are failures
                correlation = self.df['is_liquidated'].corr(failed)
                if not np.isnan(correlation):
                    check_correlations[col] = correlation
        
        # Sort by absolute correlation
        corr_df = pd.DataFrame.from_dict(check_correlations, orient='index', columns=['correlation'])
        corr_df['abs_correlation'] = corr_df['correlation'].abs()
        corr_df = corr_df.sort_values('abs_correlation', ascending=False)
        
        print("\nTop 15 Checks with Strongest Correlation to Liquidation:")
        print(f"{'Check Name':<50} {'Correlation':<15} {'Interpretation':<30}")
        print("-" * 95)
        for check, row in corr_df.head(15).iterrows():
            check_short = check[:48] if len(check) > 48 else check
            corr = row['correlation']
            if abs(corr) < 0.1:
                interpretation = "negligible"
            elif abs(corr) < 0.3:
                interpretation = "weak"
            elif abs(corr) < 0.5:
                interpretation = "moderate"
            elif abs(corr) < 0.7:
                interpretation = "strong"
            else:
                interpretation = "very strong"
            
            direction = "positive" if corr > 0 else "negative"
            print(f"{check_short:<50} {corr:>14.4f}  {direction} {interpretation}")
        
        self.results['findings']['q9_check_correlation'] = {
            'top_15_correlations': corr_df.head(15).to_dict('index')
        }
    
    def q10_product_consistency(self):
        """Q10: Product Consistency - Products that always liquidate"""
        print("\n" + "-" * 80)
        print("Q10: Product Consistency - Always Liquidate Products")
        print("-" * 80)
        
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        
        # Products that always liquidate (100% rate, min 2 orders)
        always_liquidate = product_analysis[
            (product_analysis['liquidation_rate'] == 1.0) & 
            (product_analysis['total_count'] >= 2)
        ].sort_values('total_count', ascending=False)
        
        print(f"\nProducts that ALWAYS Liquidate (100% rate, min 2 orders): {len(always_liquidate)}")
        if len(always_liquidate) > 0:
            print(f"{'Product':<60} {'Orders':<10} {'Avg COGS':<15}")
            print("-" * 85)
            for product, row in always_liquidate.iterrows():
                product_short = product[:58] if len(product) > 58 else product
                avg_cogs = self.df[self.df['Product'] == product]['Amazon COGS'].mean()
                print(f"{product_short:<60} {int(row['total_count']):<10} ${avg_cogs:<14,.2f}")
        
        self.results['findings']['q10_product_consistency'] = {
            'always_liquidate_products': always_liquidate.to_dict('index') if len(always_liquidate) > 0 else {},
            'always_liquidate_count': len(always_liquidate)
        }
    
    def q11_cogs_threshold_analysis(self):
        """Q11: COGS Threshold Analysis"""
        print("\n" + "-" * 80)
        print("Q11: COGS Threshold Analysis")
        print("-" * 80)
        
        thresholds = [1500, 2000, 2500, 3000]
        
        print("\nLiquidation Rate by COGS Threshold:")
        print(f"{'Threshold':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10} {'Value Lost':<15}")
        print("-" * 65)
        
        threshold_analysis = []
        for threshold in thresholds:
            high_cogs = self.df[self.df['Amazon COGS'] >= threshold]
            low_cogs = self.df[self.df['Amazon COGS'] < threshold]
            
            if len(high_cogs) > 0 and len(low_cogs) > 0:
                high_liquidated = high_cogs['is_liquidated'].sum()
                high_rate = (high_liquidated / len(high_cogs)) * 100
                high_value = high_cogs[high_cogs['is_liquidated'] == 1]['Amazon COGS'].sum()
                
                low_liquidated = low_cogs['is_liquidated'].sum()
                low_rate = (low_liquidated / len(low_cogs)) * 100
                
                print(f"${threshold:,}+{'':<8} {int(high_liquidated):<12} {len(high_cogs):<10} "
                      f"{high_rate:<10.1f} ${high_value:<14,.2f}")
                print(f"${threshold:,}-{'':<8} {int(low_liquidated):<12} {len(low_cogs):<10} "
                      f"{low_rate:<10.1f}")
                print()
                
                threshold_analysis.append({
                    'threshold': threshold,
                    'high_cogs_liquidation_rate': round(high_rate, 2),
                    'low_cogs_liquidation_rate': round(low_rate, 2),
                    'difference': round(high_rate - low_rate, 2)
                })
        
        self.results['findings']['q11_cogs_threshold'] = threshold_analysis
    
    def q12_reason_by_cogs(self):
        """Q12: Reason by COGS - Which reasons have highest COGS"""
        print("\n" + "-" * 80)
        print("Q12: Liquidation Reason by COGS")
        print("-" * 80)
        
        reason_cogs = self.liquidated.groupby('Result of Repair')['Amazon COGS'].agg(['mean', 'sum', 'count'])
        reason_cogs = reason_cogs.sort_values('mean', ascending=False)
        
        print("\nLiquidation Reasons by Average COGS:")
        print(f"{'Reason':<60} {'Count':<10} {'Avg COGS':<15} {'Total Value':<15}")
        print("-" * 100)
        for reason, row in reason_cogs.iterrows():
            reason_short = reason[:58] if len(reason) > 58 else reason
            print(f"{reason_short:<60} {int(row['count']):<10} ${row['mean']:<14,.2f} ${row['sum']:<14,.2f}")
        
        self.results['findings']['q12_reason_by_cogs'] = reason_cogs.to_dict('index')
    
    def q14_works_check_success_rate(self):
        """Q14: 'Does it Work?' Success Rate"""
        print("\n" + "-" * 80)
        print("Q14: 'Does it Work?' Check Success Rate")
        print("-" * 80)
        
        # Find works check column
        works_checks = [col for col in self.check_cols if 'work' in col.lower() and 'does' in col.lower()]
        
        if works_checks:
            works_col = works_checks[0]
            
            # Items that passed "Does it work?"
            passed_works = self.df[self.df[works_col] == 'Passed']
            passed_works_sellable = (passed_works['is_liquidated'] == 0).sum()
            passed_works_total = len(passed_works)
            success_rate = (passed_works_sellable / passed_works_total * 100) if passed_works_total > 0 else 0
            
            print(f"\nItems that PASSED 'Does it work?' check:")
            print(f"  Total items: {passed_works_total}")
            print(f"  Sellable: {passed_works_sellable} ({success_rate:.1f}%)")
            print(f"  Liquidated: {passed_works_total - passed_works_sellable} ({100-success_rate:.1f}%)")
            
            # Items that failed "Does it work?"
            failed_works = self.df[self.df[works_col] == 'Failed']
            failed_works_liquidated = (failed_works['is_liquidated'] == 1).sum()
            failed_works_total = len(failed_works)
            liquidation_rate = (failed_works_liquidated / failed_works_total * 100) if failed_works_total > 0 else 0
            
            print(f"\nItems that FAILED 'Does it work?' check:")
            print(f"  Total items: {failed_works_total}")
            print(f"  Liquidated: {failed_works_liquidated} ({liquidation_rate:.1f}%)")
            print(f"  Sellable: {failed_works_total - failed_works_liquidated} ({100-liquidation_rate:.1f}%)")
            
            self.results['findings']['q14_works_check_success'] = {
                'passed_works_sellable_rate': round(success_rate, 2),
                'failed_works_liquidation_rate': round(liquidation_rate, 2),
                'total_passed_works': int(passed_works_total),
                'total_failed_works': int(failed_works_total)
            }
    
    def q15_fraud_recovery_potential(self):
        """Q15: Fraud Recovery Potential"""
        print("\n" + "-" * 80)
        print("Q15: Fraud Recovery Potential")
        print("-" * 80)
        
        # Items marked as fraud
        fraud_liquidated = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Fraud', case=False, na=False)
        ]
        
        print(f"\nItems Liquidated due to Fraud:")
        print(f"  Total fraud liquidations: {len(fraud_liquidated)}")
        print(f"  Total value: ${fraud_liquidated['Amazon COGS'].sum():,.2f}")
        print(f"  Average COGS: ${fraud_liquidated['Amazon COGS'].mean():,.2f}")
        
        # High COGS fraud items (potential recovery)
        high_cogs_fraud = fraud_liquidated[fraud_liquidated['Amazon COGS'] >= 2000]
        
        print(f"\nHigh COGS Fraud Items (>= $2,000) - Potential Recovery:")
        print(f"  Count: {len(high_cogs_fraud)}")
        print(f"  Total value: ${high_cogs_fraud['Amazon COGS'].sum():,.2f}")
        print(f"  Average COGS: ${high_cogs_fraud['Amazon COGS'].mean():,.2f}")
        
        # Fraud items that passed "works" check
        if 'works_check_passed' in self.df.columns:
            fraud_works = fraud_liquidated[fraud_liquidated['works_check_passed'] == 1]
            print(f"\nFraud Items that PASSED 'Does it work?' - High Recovery Potential:")
            print(f"  Count: {len(fraud_works)}")
            print(f"  Total value: ${fraud_works['Amazon COGS'].sum():,.2f}")
        
        self.results['findings']['q15_fraud_recovery'] = {
            'total_fraud_liquidations': len(fraud_liquidated),
            'fraud_total_value': round(fraud_liquidated['Amazon COGS'].sum(), 2),
            'high_cogs_fraud_count': len(high_cogs_fraud),
            'high_cogs_fraud_value': round(high_cogs_fraud['Amazon COGS'].sum(), 2) if len(high_cogs_fraud) > 0 else 0
        }
    
    def q16_category_value_impact(self):
        """Q16: Category Value Impact"""
        print("\n" + "-" * 80)
        print("Q16: Category Value Impact")
        print("-" * 80)
        
        category_value = self.liquidated.groupby('category_group').agg({
            'Amazon COGS': ['sum', 'mean', 'count']
        })
        category_value.columns = ['total_value_lost', 'avg_cogs', 'count']
        category_value = category_value.sort_values('total_value_lost', ascending=False)
        
        print("\nTop 15 Categories by Total Value Lost:")
        print(f"{'Category':<50} {'Count':<10} {'Total Value Lost':<20} {'Avg COGS':<15}")
        print("-" * 100)
        for cat, row in category_value.head(15).iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {int(row['count']):<10} ${row['total_value_lost']:<19,.2f} ${row['avg_cogs']:<14,.2f}")
        
        self.results['findings']['q16_category_value_impact'] = {
            'top_15_by_value': category_value.head(15).to_dict('index'),
            'total_value_lost_all_categories': round(category_value['total_value_lost'].sum(), 2)
        }
    
    def q17_exception_candidates(self):
        """Q17: Exception Candidates - High COGS items that might need exceptions"""
        print("\n" + "-" * 80)
        print("Q17: Exception Candidates - High COGS Items")
        print("-" * 80)
        
        # High COGS items that were liquidated
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        
        print(f"\nHigh COGS Items (>= $2,000) that were Liquidated: {len(high_cogs_liquidated)}")
        print(f"  Total value: ${high_cogs_liquidated['Amazon COGS'].sum():,.2f}")
        
        # High COGS items that passed "works" check
        if 'works_check_passed' in self.df.columns:
            high_cogs_works = high_cogs_liquidated[high_cogs_liquidated['works_check_passed'] == 1]
            print(f"\nHigh COGS Items that PASSED 'Does it work?' but were Liquidated:")
            print(f"  Count: {len(high_cogs_works)}")
            print(f"  Total value: ${high_cogs_works['Amazon COGS'].sum():,.2f}")
            print(f"  Average COGS: ${high_cogs_works['Amazon COGS'].mean():,.2f}")
            
            if len(high_cogs_works) > 0:
                print(f"\n  Top 10 Exception Candidates:")
                print(f"  {'Product':<60} {'COGS':<15} {'Reason':<40}")
                print("  " + "-" * 115)
                for idx, row in high_cogs_works.nlargest(10, 'Amazon COGS').iterrows():
                    product_short = str(row['Product'])[:58] if len(str(row['Product'])) > 58 else str(row['Product'])
                    reason_short = str(row['Result of Repair'])[:38] if len(str(row['Result of Repair'])) > 38 else str(row['Result of Repair'])
                    print(f"  {product_short:<60} ${row['Amazon COGS']:<14,.2f} {reason_short:<40}")
        
        self.results['findings']['q17_exception_candidates'] = {
            'high_cogs_liquidated_count': len(high_cogs_liquidated),
            'high_cogs_liquidated_value': round(high_cogs_liquidated['Amazon COGS'].sum(), 2),
            'high_cogs_works_passed_count': len(high_cogs_works) if 'works_check_passed' in self.df.columns else 0,
            'high_cogs_works_passed_value': round(high_cogs_works['Amazon COGS'].sum(), 2) if 'works_check_passed' in self.df.columns and len(high_cogs_works) > 0 else 0
        }
    
    def q18_processing_time_impact(self):
        """Q18: Processing Time Impact"""
        print("\n" + "-" * 80)
        print("Q18: Processing Time Impact")
        print("-" * 80)
        
        if 'processing_days' in self.df.columns and 'days_to_ship' in self.df.columns:
            # Correlation between processing time and liquidation
            processing_corr = self.df['processing_days'].corr(self.df['is_liquidated'])
            shipping_corr = self.df['days_to_ship'].corr(self.df['is_liquidated'])
            
            print(f"\nCorrelation Analysis:")
            print(f"  Processing Days vs Liquidation: {processing_corr:.4f}")
            print(f"  Days to Ship vs Liquidation: {shipping_corr:.4f}")
            
            # Time bins analysis
            self.df['processing_time_bin'] = pd.cut(
                self.df['processing_days'].fillna(0),
                bins=[-1, 0, 1, 3, 7, 30, float('inf')],
                labels=['0 days', '1 day', '2-3 days', '4-7 days', '8-30 days', '30+ days']
            )
            
            time_analysis = self.df.groupby('processing_time_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean']
            })
            time_analysis.columns = ['liquidated', 'total', 'rate']
            time_analysis['rate_pct'] = time_analysis['rate'] * 100
            
            print(f"\nLiquidation Rate by Processing Time:")
            print(f"{'Time Bin':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10}")
            print("-" * 50)
            for time_bin, row in time_analysis.iterrows():
                print(f"{str(time_bin):<15} {int(row['liquidated']):<12} {int(row['total']):<10} {row['rate_pct']:<10.1f}")
            
            self.results['findings']['q18_processing_time'] = {
                'processing_days_correlation': round(processing_corr, 4),
                'days_to_ship_correlation': round(shipping_corr, 4),
                'liquidation_by_time_bin': time_analysis.to_dict('index')
            }
    
    def q19_false_positive_rate(self):
        """Q19: False Positive Rate - Checks that are too strict"""
        print("\n" + "-" * 80)
        print("Q19: False Positive Rate - Checks Too Strict")
        print("-" * 80)
        
        false_positive_analysis = []
        
        for col in self.check_cols:
            # Items that failed this check but were sellable (false positive)
            failed_check = self.df[self.df[col] == 'Failed']
            if len(failed_check) > 0:
                false_positives = failed_check[failed_check['is_liquidated'] == 0]
                false_positive_rate = (len(false_positives) / len(failed_check)) * 100 if len(failed_check) > 0 else 0
                
                if len(failed_check) >= 10:  # Only checks with significant failures
                    false_positive_analysis.append({
                        'check_name': col,
                        'total_failures': len(failed_check),
                        'false_positives': len(false_positives),
                        'false_positive_rate': false_positive_rate
                    })
        
        fp_df = pd.DataFrame(false_positive_analysis)
        fp_df = fp_df.sort_values('false_positive_rate', ascending=False)
        
        print("\nTop 15 Checks with Highest False Positive Rate (Failed but Sellable):")
        print(f"{'Check Name':<50} {'Failures':<12} {'False Positives':<15} {'False Pos Rate %':<15}")
        print("-" * 95)
        for idx, row in fp_df.head(15).iterrows():
            check_short = row['check_name'][:48] if len(row['check_name']) > 48 else row['check_name']
            print(f"{check_short:<50} {int(row['total_failures']):<12} {int(row['false_positives']):<15} {row['false_positive_rate']:<15.1f}")
        
        self.results['findings']['q19_false_positive'] = {
            'top_15_false_positive_checks': fp_df.head(15).to_dict('records')
        }
    
    def q21_fraud_check_impact(self):
        """Q21: Fraud Check Impact"""
        print("\n" + "-" * 80)
        print("Q21: Fraud Check Impact")
        print("-" * 80)
        
        if 'fraud_check_failed' in self.df.columns:
            fraud_failed = self.liquidated[self.liquidated['fraud_check_failed'] == 1]
            
            print(f"\nLiquidated Items with Fraud Check Failed:")
            print(f"  Count: {len(fraud_failed)} ({len(fraud_failed)/len(self.liquidated)*100:.1f}% of liquidations)")
            print(f"  Total value: ${fraud_failed['Amazon COGS'].sum():,.2f}")
            print(f"  Average COGS: ${fraud_failed['Amazon COGS'].mean():,.2f}")
            
            # Fraud check failure rate in liquidated vs sellable
            liquidated_fraud_rate = (self.liquidated['fraud_check_failed'] == 1).sum() / len(self.liquidated) * 100
            sellable_fraud_rate = (self.sellable['fraud_check_failed'] == 1).sum() / len(self.sellable) * 100 if len(self.sellable) > 0 else 0
            
            print(f"\nFraud Check Failure Rate:")
            print(f"  Liquidated orders: {liquidated_fraud_rate:.1f}%")
            print(f"  Sellable orders: {sellable_fraud_rate:.1f}%")
            print(f"  Difference: {liquidated_fraud_rate - sellable_fraud_rate:.1f} percentage points")
            
            self.results['findings']['q21_fraud_check_impact'] = {
                'fraud_failed_in_liquidated': len(fraud_failed),
                'fraud_failed_percentage': round(len(fraud_failed)/len(self.liquidated)*100, 2),
                'fraud_failed_value': round(fraud_failed['Amazon COGS'].sum(), 2),
                'liquidated_fraud_rate': round(liquidated_fraud_rate, 2),
                'sellable_fraud_rate': round(sellable_fraud_rate, 2)
            }
    
    def q22_working_items_liquidated(self):
        """Q22: Working Items Liquidated"""
        print("\n" + "-" * 80)
        print("Q22: Working Items Liquidated (Recovery Opportunity)")
        print("-" * 80)
        
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            
            print(f"\nItems that PASSED 'Does it work?' but were LIQUIDATED:")
            print(f"  Count: {len(working_liquidated)} ({len(working_liquidated)/len(self.liquidated)*100:.1f}% of liquidations)")
            print(f"  Total value: ${working_liquidated['Amazon COGS'].sum():,.2f}")
            print(f"  Average COGS: ${working_liquidated['Amazon COGS'].mean():,.2f}")
            
            # Reasons for liquidating working items
            if len(working_liquidated) > 0:
                print(f"\n  Reasons for Liquidating Working Items:")
                reason_counts = working_liquidated['Result of Repair'].value_counts()
                for reason, count in reason_counts.items():
                    pct = count / len(working_liquidated) * 100
                    value = working_liquidated[working_liquidated['Result of Repair'] == reason]['Amazon COGS'].sum()
                    print(f"    {reason}: {count} ({pct:.1f}%) - ${value:,.2f}")
            
            # High COGS working items liquidated
            high_cogs_working = working_liquidated[working_liquidated['Amazon COGS'] >= 2000]
            if len(high_cogs_working) > 0:
                print(f"\n  High COGS Working Items Liquidated (>= $2,000):")
                print(f"    Count: {len(high_cogs_working)}")
                print(f"    Total value: ${high_cogs_working['Amazon COGS'].sum():,.2f}")
            
            self.results['findings']['q22_working_items_liquidated'] = {
                'count': len(working_liquidated),
                'percentage_of_liquidations': round(len(working_liquidated)/len(self.liquidated)*100, 2),
                'total_value': round(working_liquidated['Amazon COGS'].sum(), 2),
                'avg_cogs': round(working_liquidated['Amazon COGS'].mean(), 2),
                'high_cogs_count': len(high_cogs_working) if len(working_liquidated) > 0 else 0,
                'high_cogs_value': round(high_cogs_working['Amazon COGS'].sum(), 2) if len(high_cogs_working) > 0 else 0
            }
    
    def q23_failure_count_analysis(self):
        """Q23: Failure Count Analysis"""
        print("\n" + "-" * 80)
        print("Q23: Failure Count Analysis")
        print("-" * 80)
        
        if 'failed_checks_count' in self.df.columns:
            liquidated_failures = self.liquidated['failed_checks_count']
            sellable_failures = self.sellable['failed_checks_count']
            
            print("\nFailed Checks Count Comparison:")
            print(f"{'Metric':<25} {'Liquidated':<20} {'Sellable':<20}")
            print("-" * 70)
            print(f"{'Mean':<25} {liquidated_failures.mean():<20.2f} {sellable_failures.mean():<20.2f}")
            print(f"{'Median':<25} {liquidated_failures.median():<20.2f} {sellable_failures.median():<20.2f}")
            print(f"{'Std Dev':<25} {liquidated_failures.std():<20.2f} {sellable_failures.std():<20.2f}")
            print(f"{'Min':<25} {liquidated_failures.min():<20.0f} {sellable_failures.min():<20.0f}")
            print(f"{'Max':<25} {liquidated_failures.max():<20.0f} {sellable_failures.max():<20.0f}")
            
            # Distribution by failure count ranges
            self.df['failure_count_bin'] = pd.cut(
                self.df['failed_checks_count'],
                bins=[0, 5, 10, 15, 20, 30, float('inf')],
                labels=['0-5', '6-10', '11-15', '16-20', '21-30', '30+']
            )
            
            failure_bin_analysis = self.df.groupby('failure_count_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean']
            })
            failure_bin_analysis.columns = ['liquidated', 'total', 'rate']
            failure_bin_analysis['rate_pct'] = failure_bin_analysis['rate'] * 100
            
            print(f"\nLiquidation Rate by Failure Count Range:")
            print(f"{'Failure Range':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10}")
            print("-" * 50)
            for bin_name, row in failure_bin_analysis.iterrows():
                print(f"{str(bin_name):<15} {int(row['liquidated']):<12} {int(row['total']):<10} {row['rate_pct']:<10.1f}")
            
            self.results['findings']['q23_failure_count'] = {
                'liquidated_mean_failures': round(liquidated_failures.mean(), 2),
                'sellable_mean_failures': round(sellable_failures.mean(), 2),
                'liquidation_by_failure_range': failure_bin_analysis.to_dict('index')
            }
    
    def q24_inconsistent_products(self):
        """Q24: Inconsistent Products"""
        print("\n" + "-" * 80)
        print("Q24: Inconsistent Products Analysis")
        print("-" * 80)
        
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean'],
            'Amazon COGS': 'mean'
        })
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate', 'avg_cogs']
        
        # Products with inconsistent outcomes (some liquidate, some sellable, min 5 orders)
        inconsistent = product_analysis[
            (product_analysis['liquidated_count'] > 0) & 
            (product_analysis['liquidated_count'] < product_analysis['total_count']) &
            (product_analysis['total_count'] >= 5)
        ].sort_values('total_count', ascending=False)
        
        print(f"\nProducts with Inconsistent Outcomes (min 5 orders): {len(inconsistent)}")
        if len(inconsistent) > 0:
            print(f"{'Product':<60} {'Liquidated':<12} {'Sellable':<12} {'Total':<10} {'Rate %':<10} {'Avg COGS':<15}")
            print("-" * 110)
            for product, row in inconsistent.head(20).iterrows():
                sellable_count = int(row['total_count'] - row['liquidated_count'])
                product_short = product[:58] if len(product) > 58 else product
                print(f"{product_short:<60} {int(row['liquidated_count']):<12} {sellable_count:<12} "
                      f"{int(row['total_count']):<10} {row['liquidation_rate']*100:<10.1f} ${row['avg_cogs']:<14,.2f}")
        
        self.results['findings']['q24_inconsistent_products'] = {
            'inconsistent_products_count': len(inconsistent),
            'top_20_inconsistent': inconsistent.head(20).to_dict('index') if len(inconsistent) > 0 else {}
        }
    
    def q25_recovery_potential(self):
        """Q25: Recovery Potential"""
        print("\n" + "-" * 80)
        print("Q25: Recovery Potential Analysis")
        print("-" * 80)
        
        # Already calculated in Phase 4
        if 'recovery_potential' in self.df.columns:
            total_recovery = self.df['recovery_potential'].sum()
            recovery_items = (self.df['recovery_potential'] > 0).sum()
            
            print(f"\nCurrent Recovery Potential (Items that work but were liquidated):")
            print(f"  Items: {recovery_items}")
            print(f"  Total value: ${total_recovery:,.2f}")
            
            # High COGS recovery potential
            high_cogs_recovery = self.df[
                (self.df['recovery_potential'] > 0) & 
                (self.df['Amazon COGS'] >= 2000)
            ]
            
            if len(high_cogs_recovery) > 0:
                print(f"\n  High COGS Recovery Potential (>= $2,000):")
                print(f"    Items: {len(high_cogs_recovery)}")
                print(f"    Total value: ${high_cogs_recovery['Amazon COGS'].sum():,.2f}")
            
            # Potential if we relaxed criteria for high COGS items
            high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
            potential_relaxed = high_cogs_liquidated['Amazon COGS'].sum()
            
            print(f"\nPotential Recovery if Relaxing Criteria for High COGS Items (>= $2,000):")
            print(f"  Items: {len(high_cogs_liquidated)}")
            print(f"  Total value: ${potential_relaxed:,.2f}")
            
            self.results['findings']['q25_recovery_potential'] = {
                'current_recovery_potential_items': int(recovery_items),
                'current_recovery_potential_value': round(total_recovery, 2),
                'high_cogs_recovery_items': len(high_cogs_recovery),
                'high_cogs_recovery_value': round(high_cogs_recovery['Amazon COGS'].sum(), 2) if len(high_cogs_recovery) > 0 else 0,
                'relaxed_criteria_potential_items': len(high_cogs_liquidated),
                'relaxed_criteria_potential_value': round(potential_relaxed, 2)
            }
    
    def pattern_recognition(self):
        """7.2 Pattern Recognition"""
        print("\n" + "=" * 80)
        print("7.2 PATTERN RECOGNITION")
        print("=" * 80)
        
        # 7.2.1 Common check failure combinations
        self.identify_check_combinations()
        
        # 7.2.2 Products that always liquidate
        self.identify_always_liquidate_products()
        
        # 7.2.3 Categories with consistent patterns
        self.identify_category_patterns()
    
    def identify_check_combinations(self):
        """7.2.1 Common check failure combinations"""
        print("\n" + "-" * 80)
        print("7.2.1 Common Check Failure Combinations")
        print("-" * 80)
        
        # Analyze top checks that fail together in liquidated orders
        top_checks = ['Does_the_item_work_El_art_culo_funciona', 
                     'Is_it_Fraud_Es_fraude',
                     'Does_the_item_have_scratches_or_dents_larger_that_',
                     'Is_the_item_Repairable_El_art_culo_es_reparable']
        
        # Filter to checks that exist
        top_checks = [c for c in top_checks if c in self.check_cols]
        
        print("\nCommon Failure Combinations in Liquidated Orders:")
        print(f"{'Check 1':<40} {'Check 2':<40} {'Both Failed':<15} {'% of Liquidated':<15}")
        print("-" * 110)
        
        combinations = []
        for i, check1 in enumerate(top_checks):
            for check2 in top_checks[i+1:]:
                both_failed = self.liquidated[
                    (self.liquidated[check1] == 'Failed') & 
                    (self.liquidated[check2] == 'Failed')
                ]
                if len(both_failed) > 0:
                    pct = len(both_failed) / len(self.liquidated) * 100
                    check1_short = check1[:38] if len(check1) > 38 else check1
                    check2_short = check2[:38] if len(check2) > 38 else check2
                    print(f"{check1_short:<40} {check2_short:<40} {len(both_failed):<15} {pct:<15.1f}")
                    combinations.append({
                        'check1': check1,
                        'check2': check2,
                        'both_failed_count': len(both_failed),
                        'percentage': round(pct, 2)
                    })
        
        self.results['findings']['check_combinations'] = combinations
    
    def identify_always_liquidate_products(self):
        """7.2.2 Products that always liquidate"""
        print("\n" + "-" * 80)
        print("7.2.2 Products that Always Liquidate")
        print("-" * 80)
        
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        
        always_liquidate = product_analysis[
            (product_analysis['liquidation_rate'] == 1.0) & 
            (product_analysis['total_count'] >= 2)
        ].sort_values('total_count', ascending=False)
        
        print(f"\nProducts that ALWAYS Liquidate (100% rate, min 2 orders): {len(always_liquidate)}")
        if len(always_liquidate) > 0:
            print(f"{'Product':<60} {'Orders':<10} {'Total Value Lost':<20}")
            print("-" * 90)
            for product, row in always_liquidate.iterrows():
                product_short = product[:58] if len(product) > 58 else product
                value = self.df[self.df['Product'] == product]['Amazon COGS'].sum()
                print(f"{product_short:<60} {int(row['total_count']):<10} ${value:<19,.2f}")
        
        self.results['findings']['always_liquidate_products'] = {
            'count': len(always_liquidate),
            'products': always_liquidate.to_dict('index') if len(always_liquidate) > 0 else {}
        }
    
    def identify_category_patterns(self):
        """7.2.3 Categories with consistent patterns"""
        print("\n" + "-" * 80)
        print("7.2.3 Categories with Consistent Patterns")
        print("-" * 80)
        
        category_analysis = self.df.groupby('category_group').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        category_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        category_analysis['liquidation_rate_pct'] = category_analysis['liquidation_rate'] * 100
        
        # Categories with very high liquidation rates (>=80%)
        high_liquidation_cats = category_analysis[
            (category_analysis['liquidation_rate_pct'] >= 80) & 
            (category_analysis['total_count'] >= 5)
        ].sort_values('liquidation_rate_pct', ascending=False)
        
        # Categories with very low liquidation rates (<=10%)
        low_liquidation_cats = category_analysis[
            (category_analysis['liquidation_rate_pct'] <= 10) & 
            (category_analysis['total_count'] >= 10)
        ].sort_values('liquidation_rate_pct', ascending=True)
        
        print("\nCategories with Very High Liquidation Rate (>=80%, min 5 orders):")
        print(f"{'Category':<50} {'Liquidation Rate %':<20} {'Total Orders':<15}")
        print("-" * 85)
        for cat, row in high_liquidation_cats.iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {row['liquidation_rate_pct']:<20.1f} {int(row['total_count']):<15}")
        
        print("\nCategories with Very Low Liquidation Rate (<=10%, min 10 orders):")
        print(f"{'Category':<50} {'Liquidation Rate %':<20} {'Total Orders':<15}")
        print("-" * 85)
        for cat, row in low_liquidation_cats.iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {row['liquidation_rate_pct']:<20.1f} {int(row['total_count']):<15}")
        
        self.results['findings']['category_patterns'] = {
            'high_liquidation_categories': high_liquidation_cats.to_dict('index') if len(high_liquidation_cats) > 0 else {},
            'low_liquidation_categories': low_liquidation_cats.to_dict('index') if len(low_liquidation_cats) > 0 else {}
        }
    
    def root_cause_analysis(self):
        """7.3 Root Cause Analysis"""
        print("\n" + "=" * 80)
        print("7.3 ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        # 7.3.1 Primary drivers
        self.identify_primary_drivers()
        
        # 7.3.2 Secondary contributing factors
        self.identify_secondary_factors()
        
        # 7.3.3 Systemic issues
        self.identify_systemic_issues()
        
        # 7.3.4 Process inefficiencies
        self.identify_process_inefficiencies()
    
    def identify_primary_drivers(self):
        """7.3.1 Primary drivers of liquidation"""
        print("\n" + "-" * 80)
        print("7.3.1 PRIMARY DRIVERS OF LIQUIDATION")
        print("-" * 80)
        
        print("\nTop 5 Primary Drivers:")
        
        # 1. Functional issues (from Result of Repair)
        functional_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Functional', case=False, na=False)
        ]
        print(f"\n1. Functional Issues:")
        print(f"   Count: {len(functional_issues)} ({len(functional_issues)/len(self.liquidated)*100:.1f}% of liquidations)")
        print(f"   Value: ${functional_issues['Amazon COGS'].sum():,.2f}")
        
        # 2. "Does it work?" check failure
        if 'works_check_passed' in self.df.columns:
            works_failed = self.liquidated[self.liquidated['works_check_passed'] == 0]
            print(f"\n2. 'Does it work?' Check Failed:")
            print(f"   Count: {len(works_failed)} ({len(works_failed)/len(self.liquidated)*100:.1f}% of liquidations)")
            print(f"   Value: ${works_failed['Amazon COGS'].sum():,.2f}")
        
        # 3. Fraud detection
        fraud_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Fraud', case=False, na=False)
        ]
        print(f"\n3. Fraud Detection:")
        print(f"   Count: {len(fraud_issues)} ({len(fraud_issues)/len(self.liquidated)*100:.1f}% of liquidations)")
        print(f"   Value: ${fraud_issues['Amazon COGS'].sum():,.2f}")
        
        # 4. Cosmetic issues
        cosmetic_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Cosmetic', case=False, na=False)
        ]
        print(f"\n4. Cosmetic Issues:")
        print(f"   Count: {len(cosmetic_issues)} ({len(cosmetic_issues)/len(self.liquidated)*100:.1f}% of liquidations)")
        print(f"   Value: ${cosmetic_issues['Amazon COGS'].sum():,.2f}")
        
        # 5. Repairability
        if 'repairable_check_failed' in self.df.columns:
            repairable_failed = self.liquidated[self.liquidated['repairable_check_failed'] == 1]
            print(f"\n5. Repairability Check Failed:")
            print(f"   Count: {len(repairable_failed)} ({len(repairable_failed)/len(self.liquidated)*100:.1f}% of liquidations)")
            print(f"   Value: ${repairable_failed['Amazon COGS'].sum():,.2f}")
        
        self.results['findings']['primary_drivers'] = {
            'functional_issues': {
                'count': len(functional_issues),
                'percentage': round(len(functional_issues)/len(self.liquidated)*100, 2),
                'value': round(functional_issues['Amazon COGS'].sum(), 2)
            },
            'works_check_failed': {
                'count': len(works_failed) if 'works_check_passed' in self.df.columns else 0,
                'percentage': round(len(works_failed)/len(self.liquidated)*100, 2) if 'works_check_passed' in self.df.columns else 0,
                'value': round(works_failed['Amazon COGS'].sum(), 2) if 'works_check_passed' in self.df.columns else 0
            },
            'fraud_issues': {
                'count': len(fraud_issues),
                'percentage': round(len(fraud_issues)/len(self.liquidated)*100, 2),
                'value': round(fraud_issues['Amazon COGS'].sum(), 2)
            }
        }
    
    def identify_secondary_factors(self):
        """7.3.2 Secondary contributing factors"""
        print("\n" + "-" * 80)
        print("7.3.2 SECONDARY CONTRIBUTING FACTORS")
        print("-" * 80)
        
        print("\nSecondary Factors:")
        
        # Category-specific issues
        high_rate_cats = self.df.groupby('category_group')['is_liquidated'].mean()
        high_rate_cats = high_rate_cats[high_rate_cats >= 0.8].sort_values(ascending=False)
        
        if len(high_rate_cats) > 0:
            print(f"\n1. Category-Specific Issues:")
            print(f"   {len(high_rate_cats)} categories with >=80% liquidation rate")
            for cat, rate in high_rate_cats.head(5).items():
                print(f"     - {cat}: {rate*100:.1f}%")
        
        # Product-specific issues
        product_rates = self.df.groupby('Product')['is_liquidated'].mean()
        always_liquidate = product_rates[product_rates == 1.0]
        
        if len(always_liquidate) > 0:
            print(f"\n2. Product-Specific Issues:")
            print(f"   {len(always_liquidate)} products always liquidate (100% rate)")
        
        # Cosmetic check failures
        if 'cosmetic_check_failed' in self.df.columns:
            cosmetic_failed = (self.liquidated['cosmetic_check_failed'] == 1).sum()
            print(f"\n3. Cosmetic Check Failures:")
            print(f"   {cosmetic_failed} liquidated items failed cosmetic checks ({cosmetic_failed/len(self.liquidated)*100:.1f}%)")
        
        self.results['findings']['secondary_factors'] = {
            'high_liquidation_categories_count': len(high_rate_cats),
            'always_liquidate_products_count': len(always_liquidate)
        }
    
    def identify_systemic_issues(self):
        """7.3.3 Systemic issues"""
        print("\n" + "-" * 80)
        print("7.3.3 SYSTEMIC ISSUES")
        print("-" * 80)
        
        systemic_issues = []
        
        # Issue 1: Working items being liquidated
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            if len(working_liquidated) > 0:
                print(f"\n1. Working Items Being Liquidated:")
                print(f"   {len(working_liquidated)} items ({len(working_liquidated)/len(self.liquidated)*100:.1f}%)")
                print(f"   Value: ${working_liquidated['Amazon COGS'].sum():,.2f}")
                systemic_issues.append({
                    'issue': 'Working items liquidated',
                    'count': len(working_liquidated),
                    'value': round(working_liquidated['Amazon COGS'].sum(), 2)
                })
        
        # Issue 2: High COGS items liquidated
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        if len(high_cogs_liquidated) > 0:
            print(f"\n2. High COGS Items Liquidated (>= $2,000):")
            print(f"   {len(high_cogs_liquidated)} items ({len(high_cogs_liquidated)/len(self.liquidated)*100:.1f}%)")
            print(f"   Value: ${high_cogs_liquidated['Amazon COGS'].sum():,.2f}")
            systemic_issues.append({
                'issue': 'High COGS items liquidated',
                'count': len(high_cogs_liquidated),
                'value': round(high_cogs_liquidated['Amazon COGS'].sum(), 2)
            })
        
        # Issue 3: Categories with very high rates
        category_rates = self.df.groupby('category_group')['is_liquidated'].mean()
        very_high_rate = category_rates[category_rates >= 0.9]
        if len(very_high_rate) > 0:
            print(f"\n3. Categories with Very High Liquidation Rates (>=90%):")
            print(f"   {len(very_high_rate)} categories")
            for cat, rate in very_high_rate.head(5).items():
                print(f"     - {cat}: {rate*100:.1f}%")
        
        self.results['findings']['systemic_issues'] = systemic_issues
    
    def identify_process_inefficiencies(self):
        """7.3.4 Process inefficiencies"""
        print("\n" + "-" * 80)
        print("7.3.4 PROCESS INEFFICIENCIES")
        print("-" * 80)
        
        inefficiencies = []
        
        # Inefficiency 1: Too many checks for simple decisions
        if 'total_checks' in self.df.columns:
            avg_checks = self.df['total_checks'].mean()
            print(f"\n1. Check Volume:")
            print(f"   Average checks per order: {avg_checks:.1f}")
            if avg_checks > 20:
                print(f"   [INEFFICIENCY] High number of checks may slow down processing")
                inefficiencies.append('High check volume per order')
        
        # Inefficiency 2: Inconsistent outcomes for same product
        product_consistency = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'std', 'count'])
        inconsistent = product_consistency[
            (product_consistency['mean'] > 0) & 
            (product_consistency['mean'] < 1) & 
            (product_consistency['count'] >= 5)
        ]
        if len(inconsistent) > 0:
            print(f"\n2. Inconsistent Product Outcomes:")
            print(f"   {len(inconsistent)} products have inconsistent outcomes")
            print(f"   [INEFFICIENCY] Same product sometimes liquidates, sometimes sells")
            inefficiencies.append('Inconsistent outcomes for same products')
        
        # Inefficiency 3: High false positive rate
        if 'works_check_passed' in self.df.columns:
            works_failed_sellable = self.sellable[self.sellable['works_check_passed'] == 0]
            if len(works_failed_sellable) > 0:
                print(f"\n3. False Positives in 'Does it work?' Check:")
                print(f"   {len(works_failed_sellable)} sellable items failed 'works' check")
                print(f"   [INEFFICIENCY] Check may be too strict or inconsistently applied")
                inefficiencies.append('False positives in works check')
        
        self.results['findings']['process_inefficiencies'] = inefficiencies
    
    def save_results(self):
        """Save Phase 7 results to JSON"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        output_file = f"{base_name}_phase7_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 7 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 7 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Analyzed additional questions (Q8-Q25)")
        print(f"[OK] Identified patterns in data")
        print(f"[OK] Performed root cause analysis")
        print(f"[OK] All findings saved to JSON")


def main():
    """Main execution function"""
    import sys
    
    # File path
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Try default path
        default_path = r"Cost Greater than 1000\Repair Order (repair.order)_preprocessed_features.csv"
        if os.path.exists(default_path):
            csv_file = default_path
        else:
            print("Error: Please provide the features CSV file path")
            print("Usage: python phase7_advanced_analysis.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 7 analysis
    try:
        analyzer = Phase7AdvancedAnalysis(csv_file)
        results = analyzer.run_phase7()
        print("\n[OK] Phase 7 advanced analysis completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 7 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

