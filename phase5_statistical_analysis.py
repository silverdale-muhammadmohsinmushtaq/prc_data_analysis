#!/usr/bin/env python3
"""
Phase 5: Statistical Analysis
Liquidation Analysis - Statistical tests and correlation analysis
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from scipy import stats
from scipy.stats import chi2_contingency

class Phase5StatisticalAnalysis:
    def __init__(self, features_csv_path):
        """Initialize Phase 5 statistical analysis"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.results = {
            'phase': 'Phase 5: Statistical Analysis',
            'timestamp': datetime.now().isoformat(),
            'file_path': features_csv_path,
            'findings': {}
        }
        self.output_dir = os.path.dirname(features_csv_path)
        
    def run_phase5(self):
        """Execute all Phase 5 tasks"""
        print("=" * 80)
        print("PHASE 5: STATISTICAL ANALYSIS")
        print("=" * 80)
        
        # Load feature-engineered data
        self.load_data()
        
        # 5.1 Descriptive Statistics
        self.descriptive_statistics()
        
        # 5.2 Hypothesis Testing
        self.hypothesis_testing()
        
        # 5.3 Correlation Analysis
        self.correlation_analysis()
        
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
        
        # Separate liquidated and sellable
        self.liquidated = self.df[self.df['is_liquidated'] == 1]
        self.sellable = self.df[self.df['is_liquidated'] == 0]
        print(f"[OK] Liquidated: {len(self.liquidated):,}, Sellable: {len(self.sellable):,}")
    
    def descriptive_statistics(self):
        """5.1 Descriptive Statistics"""
        print("\n" + "=" * 80)
        print("5.1 DESCRIPTIVE STATISTICS")
        print("=" * 80)
        
        # 5.1.1 Summary statistics
        self.summary_statistics()
        
        # 5.1.2 Financial impact
        self.financial_impact()
    
    def summary_statistics(self):
        """5.1.1 Summary statistics"""
        print("\n" + "-" * 80)
        print("5.1.1 SUMMARY STATISTICS")
        print("-" * 80)
        
        # Overall liquidation rate
        overall_rate = self.df['is_liquidated'].mean() * 100
        print(f"\nOverall Liquidation Rate: {overall_rate:.2f}%")
        print(f"  Liquidated: {len(self.liquidated):,} ({overall_rate:.1f}%)")
        print(f"  Sellable: {len(self.sellable):,} ({100-overall_rate:.1f}%)")
        
        # Liquidation rate by category
        print("\nLiquidation Rate by Category (Top 10):")
        category_rates = self.df.groupby('category_group').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        category_rates.columns = ['liquidated', 'total', 'rate']
        category_rates['rate_pct'] = category_rates['rate'] * 100
        category_rates = category_rates.sort_values('liquidated', ascending=False).head(10)
        
        print(f"{'Category':<50} {'Liquidated':<12} {'Total':<10} {'Rate %':<10}")
        print("-" * 85)
        for cat, row in category_rates.iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {int(row['liquidated']):<12} {int(row['total']):<10} {row['rate_pct']:<10.1f}")
        
        # Liquidation rate by COGS range
        print("\nLiquidation Rate by COGS Range:")
        if 'cogs_bin' in self.df.columns:
            cogs_rates = self.df.groupby('cogs_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean']
            })
            cogs_rates.columns = ['liquidated', 'total', 'rate']
            cogs_rates['rate_pct'] = cogs_rates['rate'] * 100
            
            print(f"{'COGS Bin':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10}")
            print("-" * 50)
            for bin_name, row in cogs_rates.iterrows():
                print(f"{str(bin_name):<15} {int(row['liquidated']):<12} {int(row['total']):<10} {row['rate_pct']:<10.1f}")
        
        # Average COGS liquidated vs sellable
        print("\nAverage COGS Comparison:")
        liquidated_cogs_mean = self.liquidated['Amazon COGS'].mean()
        sellable_cogs_mean = self.sellable['Amazon COGS'].mean()
        difference = liquidated_cogs_mean - sellable_cogs_mean
        
        print(f"  Liquidated: ${liquidated_cogs_mean:,.2f}")
        print(f"  Sellable: ${sellable_cogs_mean:,.2f}")
        print(f"  Difference: ${difference:,.2f} ({difference/sellable_cogs_mean*100:+.2f}%)")
        
        # Store results
        self.results['findings']['summary_statistics'] = {
            'overall_liquidation_rate': round(overall_rate, 2),
            'liquidation_rate_by_category': category_rates.to_dict('index'),
            'liquidation_rate_by_cogs': cogs_rates.to_dict('index') if 'cogs_bin' in self.df.columns else {},
            'avg_cogs_liquidated': round(liquidated_cogs_mean, 2),
            'avg_cogs_sellable': round(sellable_cogs_mean, 2),
            'cogs_difference': round(difference, 2),
            'cogs_difference_pct': round(difference/sellable_cogs_mean*100, 2)
        }
    
    def financial_impact(self):
        """5.1.2 Financial impact"""
        print("\n" + "-" * 80)
        print("5.1.2 FINANCIAL IMPACT")
        print("-" * 80)
        
        # Total value lost
        total_value_lost = self.liquidated['Amazon COGS'].sum()
        print(f"\nTotal Value Lost to Liquidation: ${total_value_lost:,.2f}")
        
        # Average value lost per liquidated item
        avg_value_lost = self.liquidated['Amazon COGS'].mean()
        print(f"Average Value Lost per Liquidated Item: ${avg_value_lost:,.2f}")
        
        # Value lost by category
        print("\nValue Lost by Category (Top 10):")
        category_value = self.liquidated.groupby('category_group').agg({
            'Amazon COGS': ['sum', 'count', 'mean']
        })
        category_value.columns = ['total_value_lost', 'count', 'avg_value']
        category_value = category_value.sort_values('total_value_lost', ascending=False).head(10)
        
        print(f"{'Category':<50} {'Count':<10} {'Total Value Lost':<20} {'Avg Value':<15}")
        print("-" * 100)
        for cat, row in category_value.iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {int(row['count']):<10} ${row['total_value_lost']:<19,.2f} ${row['avg_value']:<14,.2f}")
        
        # Value lost by liquidation reason
        print("\nValue Lost by Liquidation Reason:")
        reason_value = self.liquidated.groupby('Result of Repair').agg({
            'Amazon COGS': ['sum', 'count', 'mean']
        })
        reason_value.columns = ['total_value_lost', 'count', 'avg_value']
        reason_value = reason_value.sort_values('total_value_lost', ascending=False)
        
        print(f"{'Reason':<60} {'Count':<10} {'Total Value Lost':<20} {'Avg Value':<15}")
        print("-" * 110)
        for reason, row in reason_value.iterrows():
            reason_short = reason[:58] if len(reason) > 58 else reason
            print(f"{reason_short:<60} {int(row['count']):<10} ${row['total_value_lost']:<19,.2f} ${row['avg_value']:<14,.2f}")
        
        # Store results
        self.results['findings']['financial_impact'] = {
            'total_value_lost': round(total_value_lost, 2),
            'avg_value_lost_per_item': round(avg_value_lost, 2),
            'value_lost_by_category': category_value.to_dict('index'),
            'value_lost_by_reason': reason_value.to_dict('index')
        }
    
    def hypothesis_testing(self):
        """5.2 Hypothesis Testing"""
        print("\n" + "=" * 80)
        print("5.2 HYPOTHESIS TESTING")
        print("=" * 80)
        
        # 5.2.1 COGS difference: Liquidated vs Sellable (t-test)
        self.test_cogs_difference()
        
        # 5.2.2 Liquidation rate difference: High vs Low COGS (chi-square)
        self.test_liquidation_rate_by_cogs()
        
        # 5.2.3 Check failure rate differences (proportion tests)
        self.test_check_failure_rates()
    
    def test_cogs_difference(self):
        """5.2.1 Test COGS difference between Liquidated and Sellable"""
        print("\n" + "-" * 80)
        print("5.2.1 COGS DIFFERENCE TEST (t-test)")
        print("-" * 80)
        
        liquidated_cogs = self.liquidated['Amazon COGS'].dropna()
        sellable_cogs = self.sellable['Amazon COGS'].dropna()
        
        # Perform independent t-test
        t_stat, p_value = stats.ttest_ind(liquidated_cogs, sellable_cogs)
        
        print(f"\nNull Hypothesis: Mean COGS is the same for Liquidated and Sellable")
        print(f"Alternative Hypothesis: Mean COGS differs between Liquidated and Sellable")
        print(f"\nTest Results:")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Significance level (alpha): 0.05")
        
        if p_value < 0.05:
            print(f"  Result: REJECT null hypothesis (p < 0.05)")
            print(f"  Conclusion: There IS a statistically significant difference in COGS")
        else:
            print(f"  Result: FAIL TO REJECT null hypothesis (p >= 0.05)")
            print(f"  Conclusion: No statistically significant difference in COGS")
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(liquidated_cogs) - 1) * liquidated_cogs.std()**2 + 
                             (len(sellable_cogs) - 1) * sellable_cogs.std()**2) / 
                            (len(liquidated_cogs) + len(sellable_cogs) - 2))
        cohens_d = (liquidated_cogs.mean() - sellable_cogs.mean()) / pooled_std
        
        print(f"\nEffect Size (Cohen's d): {cohens_d:.4f}")
        if abs(cohens_d) < 0.2:
            effect_size = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size = "small"
        elif abs(cohens_d) < 0.8:
            effect_size = "medium"
        else:
            effect_size = "large"
        print(f"  Effect size interpretation: {effect_size}")
        
        # Store results
        self.results['findings']['hypothesis_tests'] = {
            'cogs_difference_test': {
                't_statistic': round(t_stat, 4),
                'p_value': round(p_value, 4),
                'significant': p_value < 0.05,
                'cohens_d': round(cohens_d, 4),
                'effect_size': effect_size
            }
        }
    
    def test_liquidation_rate_by_cogs(self):
        """5.2.2 Test liquidation rate difference by COGS (chi-square)"""
        print("\n" + "-" * 80)
        print("5.2.2 LIQUIDATION RATE BY COGS TEST (chi-square)")
        print("-" * 80)
        
        if 'cogs_bin' not in self.df.columns:
            print("[SKIP] cogs_bin column not available")
            return
        
        # Create contingency table
        contingency = pd.crosstab(self.df['cogs_bin'], self.df['is_liquidated'])
        
        print("\nContingency Table:")
        print(contingency)
        
        # Perform chi-square test
        chi2, p_value, dof, expected = chi2_contingency(contingency)
        
        print(f"\nNull Hypothesis: Liquidation rate is independent of COGS bin")
        print(f"Alternative Hypothesis: Liquidation rate depends on COGS bin")
        print(f"\nTest Results:")
        print(f"  Chi-square statistic: {chi2:.4f}")
        print(f"  Degrees of freedom: {dof}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Significance level (alpha): 0.05")
        
        if p_value < 0.05:
            print(f"  Result: REJECT null hypothesis (p < 0.05)")
            print(f"  Conclusion: Liquidation rate IS dependent on COGS bin")
        else:
            print(f"  Result: FAIL TO REJECT null hypothesis (p >= 0.05)")
            print(f"  Conclusion: Liquidation rate is independent of COGS bin")
        
        # Cramér's V (effect size for chi-square)
        n = contingency.sum().sum()
        cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
        print(f"\nEffect Size (Cramér's V): {cramers_v:.4f}")
        if cramers_v < 0.1:
            effect_size = "negligible"
        elif cramers_v < 0.3:
            effect_size = "small"
        elif cramers_v < 0.5:
            effect_size = "medium"
        else:
            effect_size = "large"
        print(f"  Effect size interpretation: {effect_size}")
        
        # Store results
        if 'hypothesis_tests' not in self.results['findings']:
            self.results['findings']['hypothesis_tests'] = {}
        self.results['findings']['hypothesis_tests']['liquidation_by_cogs_test'] = {
            'chi2_statistic': round(chi2, 4),
            'p_value': round(p_value, 4),
            'degrees_of_freedom': int(dof),
            'significant': p_value < 0.05,
            'cramers_v': round(cramers_v, 4),
            'effect_size': effect_size
        }
    
    def test_check_failure_rates(self):
        """5.2.3 Test check failure rate differences"""
        print("\n" + "-" * 80)
        print("5.2.3 CHECK FAILURE RATE DIFFERENCES (proportion tests)")
        print("-" * 80)
        
        # Test failure_rate difference
        liquidated_failure_rate = self.liquidated['failure_rate'].mean()
        sellable_failure_rate = self.sellable['failure_rate'].mean()
        
        # Two-proportion z-test
        n1 = len(self.liquidated)
        n2 = len(self.sellable)
        p1 = liquidated_failure_rate
        p2 = sellable_failure_rate
        
        # Pooled proportion
        p_pool = (self.liquidated['failed_checks_count'].sum() + 
                 self.sellable['failed_checks_count'].sum()) / \
                (self.liquidated['total_checks'].sum() + 
                 self.sellable['total_checks'].sum())
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        # Z-statistic
        z_stat = (p1 - p2) / se
        
        # p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        print(f"\nNull Hypothesis: Failure rates are the same for Liquidated and Sellable")
        print(f"Alternative Hypothesis: Failure rates differ between Liquidated and Sellable")
        print(f"\nTest Results:")
        print(f"  Liquidated failure rate: {liquidated_failure_rate:.4f} ({liquidated_failure_rate*100:.2f}%)")
        print(f"  Sellable failure rate: {sellable_failure_rate:.4f} ({sellable_failure_rate*100:.2f}%)")
        print(f"  Difference: {liquidated_failure_rate - sellable_failure_rate:.4f}")
        print(f"  Z-statistic: {z_stat:.4f}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Significance level (alpha): 0.05")
        
        if p_value < 0.05:
            print(f"  Result: REJECT null hypothesis (p < 0.05)")
            print(f"  Conclusion: There IS a statistically significant difference in failure rates")
        else:
            print(f"  Result: FAIL TO REJECT null hypothesis (p >= 0.05)")
            print(f"  Conclusion: No statistically significant difference in failure rates")
        
        # Store results
        if 'hypothesis_tests' not in self.results['findings']:
            self.results['findings']['hypothesis_tests'] = {}
        self.results['findings']['hypothesis_tests']['failure_rate_test'] = {
            'liquidated_rate': round(liquidated_failure_rate, 4),
            'sellable_rate': round(sellable_failure_rate, 4),
            'difference': round(liquidated_failure_rate - sellable_failure_rate, 4),
            'z_statistic': round(z_stat, 4),
            'p_value': round(p_value, 4),
            'significant': p_value < 0.05
        }
    
    def correlation_analysis(self):
        """5.3 Correlation Analysis"""
        print("\n" + "=" * 80)
        print("5.3 CORRELATION ANALYSIS")
        print("=" * 80)
        
        # Select numeric columns for correlation
        numeric_cols = ['Amazon COGS', 'is_liquidated', 'total_checks', 
                       'failed_checks_count', 'passed_checks_count', 'failure_rate',
                       'fraud_check_failed', 'cosmetic_check_failed', 
                       'repairable_check_failed', 'works_check_passed',
                       'factory_sealed_check_passed', 'value_lost', 
                       'processing_days', 'days_to_ship', 'check_efficiency',
                       'high_value_flag']
        
        # Filter to columns that exist
        numeric_cols = [col for col in numeric_cols if col in self.df.columns]
        
        # Calculate correlation matrix
        corr_matrix = self.df[numeric_cols].corr()
        
        # Correlation with liquidation
        print("\n" + "-" * 80)
        print("5.3.1 CORRELATION WITH LIQUIDATION")
        print("-" * 80)
        
        liquidation_corr = corr_matrix['is_liquidated'].sort_values(ascending=False)
        
        print(f"\nCorrelation with Liquidation (is_liquidated):")
        print(f"{'Variable':<40} {'Correlation':<15} {'Interpretation':<30}")
        print("-" * 85)
        for var, corr in liquidation_corr.items():
            if var == 'is_liquidated':
                continue
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
            print(f"{var:<40} {corr:>14.4f}  {direction} {interpretation}")
        
        # Correlation between COGS and liquidation
        cogs_liquidation_corr = corr_matrix.loc['Amazon COGS', 'is_liquidated']
        print(f"\nCorrelation between COGS and Liquidation: {cogs_liquidation_corr:.4f}")
        
        # Correlation between check failures and liquidation
        failure_liquidation_corr = corr_matrix.loc['failure_rate', 'is_liquidated']
        print(f"Correlation between Failure Rate and Liquidation: {failure_liquidation_corr:.4f}")
        
        # Correlation matrix of key variables
        print("\n" + "-" * 80)
        print("5.3.2 CORRELATION MATRIX (Key Variables)")
        print("-" * 80)
        
        key_vars = ['is_liquidated', 'Amazon COGS', 'failure_rate', 
                   'fraud_check_failed', 'cosmetic_check_failed',
                   'works_check_passed', 'total_checks']
        key_vars = [v for v in key_vars if v in numeric_cols]
        
        key_corr = self.df[key_vars].corr()
        
        print("\nCorrelation Matrix:")
        print(key_corr.round(4))
        
        # Identify multicollinearity
        print("\n" + "-" * 80)
        print("5.3.3 MULTICOLLINEARITY CHECK")
        print("-" * 80)
        
        # Check for high correlations (|r| > 0.7) between predictor variables
        high_corr_pairs = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                var1 = numeric_cols[i]
                var2 = numeric_cols[j]
                if var1 == 'is_liquidated' or var2 == 'is_liquidated':
                    continue
                corr_val = corr_matrix.loc[var1, var2]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append((var1, var2, corr_val))
        
        if high_corr_pairs:
            print(f"\nHigh Correlations Found (|r| > 0.7): {len(high_corr_pairs)} pairs")
            print(f"{'Variable 1':<40} {'Variable 2':<40} {'Correlation':<15}")
            print("-" * 100)
            for var1, var2, corr in high_corr_pairs:
                print(f"{var1:<40} {var2:<40} {corr:>14.4f}")
            print("\n[WARNING] Multicollinearity detected - these variables are highly correlated")
        else:
            print("\n[OK] No high correlations found (|r| <= 0.7) - no multicollinearity issues")
        
        # Store results
        self.results['findings']['correlation_analysis'] = {
            'correlation_with_liquidation': liquidation_corr.to_dict(),
            'cogs_liquidation_correlation': round(cogs_liquidation_corr, 4),
            'failure_rate_liquidation_correlation': round(failure_liquidation_corr, 4),
            'key_variables_correlation_matrix': key_corr.to_dict(),
            'multicollinearity_pairs': [{'var1': v1, 'var2': v2, 'correlation': round(c, 4)} 
                                      for v1, v2, c in high_corr_pairs]
        }
    
    def save_results(self):
        """Save Phase 5 results to JSON"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        output_file = f"{base_name}_phase5_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 5 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 5 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Descriptive statistics completed")
        print(f"[OK] Hypothesis testing completed")
        print(f"[OK] Correlation analysis completed")
        print(f"[OK] All statistical results saved to JSON")


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
            print("Usage: python phase5_statistical_analysis.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Check if scipy is available
    try:
        from scipy import stats
    except ImportError:
        print("\n[ERROR] scipy is not installed.")
        print("Please install it using: pip install scipy")
        return
    
    # Run Phase 5 analysis
    try:
        analyzer = Phase5StatisticalAnalysis(csv_file)
        results = analyzer.run_phase5()
        print("\n[OK] Phase 5 statistical analysis completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 5 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

