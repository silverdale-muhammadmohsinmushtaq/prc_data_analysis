#!/usr/bin/env python3
"""
Phase 6: Answering Specific Questions
Liquidation Analysis - Comprehensive answers to 7 specific questions
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

class Phase6AnswerQuestions:
    def __init__(self, features_csv_path):
        """Initialize Phase 6 question answering"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.check_cols = []
        self.results = {
            'phase': 'Phase 6: Answering Specific Questions',
            'timestamp': datetime.now().isoformat(),
            'file_path': features_csv_path,
            'answers': {}
        }
        self.output_dir = os.path.dirname(features_csv_path)
        self.graphs_dir = os.path.join(self.output_dir, "Phase6_Graphs")
        os.makedirs(self.graphs_dir, exist_ok=True)
        
    def run_phase6(self):
        """Execute all Phase 6 tasks"""
        print("=" * 80)
        print("PHASE 6: ANSWERING SPECIFIC QUESTIONS")
        print("=" * 80)
        
        # Load feature-engineered data
        self.load_data()
        
        # Answer all 7 questions
        self.answer_question1()
        self.answer_question2()
        self.answer_question3()
        self.answer_question4()
        self.answer_question5()
        self.answer_question6()
        self.answer_question7()
        
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
    
    def answer_question1(self):
        """Q1: Which quality checks are causing liquidations?"""
        print("\n" + "=" * 80)
        print("QUESTION 1: Which quality checks are causing liquidations?")
        print("=" * 80)
        
        # Count failed checks in liquidated orders
        check_failure_counts = {}
        check_failure_rates = {}
        
        for col in self.check_cols:
            failed = (self.liquidated[col] == 'Failed').sum()
            total_with_check = self.liquidated[col].notna().sum()
            if total_with_check > 0:
                check_failure_counts[col] = failed
                check_failure_rates[col] = (failed / total_with_check * 100)
        
        # Create DataFrame and rank
        q1_df = pd.DataFrame({
            'check_name': list(check_failure_counts.keys()),
            'failure_count': list(check_failure_counts.values()),
            'failure_rate_pct': list(check_failure_rates.values())
        })
        q1_df = q1_df.sort_values('failure_count', ascending=False)
        
        print("\nTop 15 Quality Checks Causing Liquidations:")
        print(f"{'Rank':<6} {'Check Name':<60} {'Failures':<12} {'Failure Rate %':<15}")
        print("-" * 95)
        for i, (idx, row) in enumerate(q1_df.head(15).iterrows(), 1):
            check_short = row['check_name'][:58] if len(row['check_name']) > 58 else row['check_name']
            print(f"{i:<6} {check_short:<60} {int(row['failure_count']):<12} {row['failure_rate_pct']:<15.1f}")
        
        # Visualize
        fig, ax = plt.subplots(figsize=(16, 10))
        top_15 = q1_df.head(15)
        bars = ax.barh(range(len(top_15)), top_15['failure_count'].values, color='#e74c3c', alpha=0.7)
        ax.set_yticks(range(len(top_15)))
        ax.set_yticklabels([check[:50] for check in top_15['check_name']], fontsize=9)
        ax.set_xlabel('Failure Count in Liquidated Orders', fontsize=12)
        ax.set_title('Top 15 Quality Checks Causing Liquidations', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, row) in enumerate(top_15.iterrows()):
            ax.text(row['failure_count'], i, f" {int(row['failure_count'])} ({row['failure_rate_pct']:.1f}%)", 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q1_Quality_Checks_Causing_Liquidations.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q1_Quality_Checks_Causing_Liquidations.png")
        
        # Store results
        self.results['answers']['question1'] = {
            'top_15_checks': q1_df.head(15).to_dict('records'),
            'summary': {
                'total_checks_analyzed': len(q1_df),
                'top_check': q1_df.iloc[0]['check_name'],
                'top_check_failures': int(q1_df.iloc[0]['failure_count']),
                'top_check_failure_rate': round(q1_df.iloc[0]['failure_rate_pct'], 2)
            }
        }
    
    def answer_question2(self):
        """Q2: Patterns in high COGS items that get liquidated"""
        print("\n" + "=" * 80)
        print("QUESTION 2: Patterns in high COGS items that get liquidated")
        print("=" * 80)
        
        # Compare COGS distributions
        liquidated_cogs = self.liquidated['Amazon COGS']
        sellable_cogs = self.sellable['Amazon COGS']
        
        print("\nCOGS Distribution Comparison:")
        print(f"{'Metric':<25} {'Liquidated':<20} {'Sellable':<20}")
        print("-" * 70)
        print(f"{'Mean':<25} ${liquidated_cogs.mean():<19,.2f} ${sellable_cogs.mean():<19,.2f}")
        print(f"{'Median':<25} ${liquidated_cogs.median():<19,.2f} ${sellable_cogs.median():<19,.2f}")
        print(f"{'Std Dev':<25} ${liquidated_cogs.std():<19,.2f} ${sellable_cogs.std():<19,.2f}")
        print(f"{'Min':<25} ${liquidated_cogs.min():<19,.2f} ${sellable_cogs.min():<19,.2f}")
        print(f"{'Max':<25} ${liquidated_cogs.max():<19,.2f} ${sellable_cogs.max():<19,.2f}")
        
        # Liquidation rate by COGS bins
        print("\nLiquidation Rate by COGS Bins:")
        if 'cogs_bin' in self.df.columns:
            cogs_analysis = self.df.groupby('cogs_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean'],
                'Amazon COGS': ['sum', 'mean']
            })
            cogs_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate', 
                                    'total_value', 'avg_cogs']
            cogs_analysis['liquidation_rate_pct'] = cogs_analysis['liquidation_rate'] * 100
            cogs_analysis['value_lost'] = cogs_analysis['liquidated_count'] * cogs_analysis['avg_cogs']
            
            print(f"{'COGS Bin':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10} {'Value Lost':<15}")
            print("-" * 65)
            for bin_name, row in cogs_analysis.iterrows():
                print(f"{str(bin_name):<15} {int(row['liquidated_count']):<12} {int(row['total_count']):<10} "
                      f"{row['liquidation_rate_pct']:<10.1f} ${row['value_lost']:<14,.2f}")
        
        # High COGS threshold analysis
        thresholds = [1500, 2000, 2500, 3000]
        print("\nLiquidation Rate by COGS Thresholds:")
        print(f"{'Threshold':<15} {'Liquidated':<12} {'Total':<10} {'Rate %':<10} {'Value Lost':<15}")
        print("-" * 65)
        for threshold in thresholds:
            high_cogs = self.df[self.df['Amazon COGS'] >= threshold]
            if len(high_cogs) > 0:
                liquidated = high_cogs['is_liquidated'].sum()
                rate = (liquidated / len(high_cogs)) * 100
                value_lost = high_cogs[high_cogs['is_liquidated'] == 1]['Amazon COGS'].sum()
                print(f"${threshold:,}+{'':<8} {int(liquidated):<12} {len(high_cogs):<10} "
                      f"{rate:<10.1f} ${value_lost:<14,.2f}")
        
        # Visualize
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Histogram comparison
        axes[0, 0].hist([sellable_cogs, liquidated_cogs], bins=30, 
                       label=['Sellable', 'Liquidate'], alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('COGS ($)', fontsize=12)
        axes[0, 0].set_ylabel('Frequency', fontsize=12)
        axes[0, 0].set_title('COGS Distribution: Liquidated vs Sellable', fontsize=14, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Box plot
        bp = axes[0, 1].boxplot([sellable_cogs, liquidated_cogs], tick_labels=['Sellable', 'Liquidate'],
                               patch_artist=True)
        bp['boxes'][0].set_facecolor('#2ecc71')
        bp['boxes'][1].set_facecolor('#e74c3c')
        axes[0, 1].set_ylabel('COGS ($)', fontsize=12)
        axes[0, 1].set_title('COGS Comparison (Box Plot)', fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Liquidation rate by bin
        if 'cogs_bin' in self.df.columns:
            bars = axes[1, 0].bar(cogs_analysis.index.astype(str), cogs_analysis['liquidation_rate_pct'],
                                 color='#e74c3c', alpha=0.7)
            axes[1, 0].set_xlabel('COGS Bin', fontsize=12)
            axes[1, 0].set_ylabel('Liquidation Rate (%)', fontsize=12)
            axes[1, 0].set_title('Liquidation Rate by COGS Bin', fontsize=14, fontweight='bold')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Value lost by bin
        if 'cogs_bin' in self.df.columns:
            bars = axes[1, 1].bar(cogs_analysis.index.astype(str), cogs_analysis['value_lost'],
                                 color='#c0392b', alpha=0.7)
            axes[1, 1].set_xlabel('COGS Bin', fontsize=12)
            axes[1, 1].set_ylabel('Value Lost ($)', fontsize=12)
            axes[1, 1].set_title('Total Value Lost by COGS Bin', fontsize=14, fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q2_High_COGS_Patterns.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q2_High_COGS_Patterns.png")
        
        # Store results
        self.results['answers']['question2'] = {
            'cogs_comparison': {
                'liquidated_mean': round(liquidated_cogs.mean(), 2),
                'sellable_mean': round(sellable_cogs.mean(), 2),
                'difference': round(liquidated_cogs.mean() - sellable_cogs.mean(), 2)
            },
            'liquidation_by_bin': cogs_analysis.to_dict('index') if 'cogs_bin' in self.df.columns else {},
            'total_value_lost': round(self.liquidated['Amazon COGS'].sum(), 2)
        }
    
    def answer_question3(self):
        """Q3: Comparison of passed vs failed checks between Sellable and Liquidate"""
        print("\n" + "=" * 80)
        print("QUESTION 3: Comparison of passed vs failed checks between Sellable and Liquidate")
        print("=" * 80)
        
        comparison_data = []
        
        for col in self.check_cols:
            # Liquidated rates
            liquidated_failed = (self.liquidated[col] == 'Failed').sum()
            liquidated_total = self.liquidated[col].notna().sum()
            liquidated_rate = (liquidated_failed / liquidated_total * 100) if liquidated_total > 0 else 0
            
            # Sellable rates
            sellable_failed = (self.sellable[col] == 'Failed').sum()
            sellable_total = self.sellable[col].notna().sum()
            sellable_rate = (sellable_failed / sellable_total * 100) if sellable_total > 0 else 0
            
            difference = liquidated_rate - sellable_rate
            
            if liquidated_total > 0 or sellable_total > 0:
                comparison_data.append({
                    'check_name': col,
                    'liquidated_failure_rate': round(liquidated_rate, 2),
                    'sellable_failure_rate': round(sellable_rate, 2),
                    'difference': round(difference, 2),
                    'liquidated_count': int(liquidated_failed),
                    'sellable_count': int(sellable_failed)
                })
        
        q3_df = pd.DataFrame(comparison_data)
        q3_df = q3_df.sort_values('difference', ascending=False)
        
        print("\nTop 15 Checks with Biggest Difference (Liquidated vs Sellable):")
        print(f"{'Check Name':<50} {'Liquidated %':<15} {'Sellable %':<15} {'Difference %':<15}")
        print("-" * 95)
        for i, (idx, row) in enumerate(q3_df.head(15).iterrows(), 1):
            check_short = row['check_name'][:48] if len(row['check_name']) > 48 else row['check_name']
            print(f"{check_short:<50} {row['liquidated_failure_rate']:<15.1f} "
                  f"{row['sellable_failure_rate']:<15.1f} {row['difference']:<15.1f}")
        
        # Visualize
        fig, ax = plt.subplots(figsize=(16, 10))
        top_15 = q3_df.head(15)
        x = np.arange(len(top_15))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, top_15['liquidated_failure_rate'], width, 
                       label='Liquidated', color='#e74c3c', alpha=0.7)
        bars2 = ax.barh(x + width/2, top_15['sellable_failure_rate'], width, 
                       label='Sellable', color='#2ecc71', alpha=0.7)
        
        ax.set_yticks(x)
        ax.set_yticklabels([check[:45] for check in top_15['check_name']], fontsize=9)
        ax.set_xlabel('Failure Rate (%)', fontsize=12)
        ax.set_title('Top 15 Checks: Failure Rate Comparison (Liquidated vs Sellable)', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q3_Passed_Failed_Comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q3_Passed_Failed_Comparison.png")
        
        # Store results
        self.results['answers']['question3'] = {
            'top_15_differences': q3_df.head(15).to_dict('records'),
            'summary': {
                'total_checks_compared': len(q3_df),
                'biggest_difference_check': q3_df.iloc[0]['check_name'],
                'biggest_difference_value': round(q3_df.iloc[0]['difference'], 2)
            }
        }
    
    def answer_question4(self):
        """Q4: Product categories most affected"""
        print("\n" + "=" * 80)
        print("QUESTION 4: Product categories most affected")
        print("=" * 80)
        
        category_analysis = self.df.groupby('category_group').agg({
            'is_liquidated': ['sum', 'count', 'mean'],
            'Amazon COGS': ['sum', 'mean']
        })
        category_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate',
                                    'total_cogs', 'avg_cogs']
        category_analysis['liquidation_rate_pct'] = category_analysis['liquidation_rate'] * 100
        category_analysis['value_lost'] = category_analysis['liquidated_count'] * category_analysis['avg_cogs']
        category_analysis = category_analysis.sort_values('liquidated_count', ascending=False)
        
        print("\nTop 15 Categories Most Affected (by Liquidation Count):")
        print(f"{'Category':<50} {'Liquidated':<12} {'Total':<10} {'Rate %':<10} {'Value Lost':<15}")
        print("-" * 100)
        for cat, row in category_analysis.head(15).iterrows():
            cat_short = cat[:48] if len(cat) > 48 else cat
            print(f"{cat_short:<50} {int(row['liquidated_count']):<12} {int(row['total_count']):<10} "
                  f"{row['liquidation_rate_pct']:<10.1f} ${row['value_lost']:<14,.2f}")
        
        # Visualize
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
        
        # By liquidation count
        top_15_count = category_analysis.head(15)
        bars1 = ax1.barh(range(len(top_15_count)), top_15_count['liquidated_count'].values,
                        color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(top_15_count)))
        ax1.set_yticklabels([cat[:40] for cat in top_15_count.index], fontsize=9)
        ax1.set_xlabel('Liquidation Count', fontsize=12)
        ax1.set_title('Top 15 Categories by Liquidation Count', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # By value lost
        top_15_value = category_analysis.sort_values('value_lost', ascending=False).head(15)
        bars2 = ax2.barh(range(len(top_15_value)), top_15_value['value_lost'].values,
                        color='#c0392b', alpha=0.7)
        ax2.set_yticks(range(len(top_15_value)))
        ax2.set_yticklabels([cat[:40] for cat in top_15_value.index], fontsize=9)
        ax2.set_xlabel('Value Lost ($)', fontsize=12)
        ax2.set_title('Top 15 Categories by Value Lost', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q4_Categories_Most_Affected.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q4_Categories_Most_Affected.png")
        
        # Store results
        self.results['answers']['question4'] = {
            'top_15_categories': category_analysis.head(15).to_dict('index'),
            'summary': {
                'total_categories': len(category_analysis),
                'most_affected_category': category_analysis.index[0],
                'most_affected_count': int(category_analysis.iloc[0]['liquidated_count']),
                'total_value_lost': round(category_analysis['value_lost'].sum(), 2)
            }
        }
    
    def answer_question5(self):
        """Q5: Specific liquidation reasons"""
        print("\n" + "=" * 80)
        print("QUESTION 5: Specific liquidation reasons")
        print("=" * 80)
        
        reason_analysis = self.liquidated.groupby('Result of Repair').agg({
            'is_liquidated': 'count',
            'Amazon COGS': ['sum', 'mean']
        })
        reason_analysis.columns = ['count', 'total_value_lost', 'avg_cogs']
        reason_analysis = reason_analysis.sort_values('count', ascending=False)
        reason_analysis['percentage'] = (reason_analysis['count'] / len(self.liquidated) * 100).round(2)
        
        print("\nLiquidation Reasons Breakdown:")
        print(f"{'Reason':<60} {'Count':<10} {'%':<10} {'Avg COGS':<12} {'Total Value Lost':<15}")
        print("-" * 110)
        for reason, row in reason_analysis.iterrows():
            reason_short = reason[:58] if len(reason) > 58 else reason
            print(f"{reason_short:<60} {int(row['count']):<10} {row['percentage']:<10.1f} "
                  f"${row['avg_cogs']:<11,.2f} ${row['total_value_lost']:<14,.2f}")
        
        # Visualize
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Bar chart
        bars = ax1.barh(range(len(reason_analysis)), reason_analysis['count'].values,
                       color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(reason_analysis)))
        ax1.set_yticklabels([reason[:40] for reason in reason_analysis.index], fontsize=9)
        ax1.set_xlabel('Count', fontsize=12)
        ax1.set_title('Liquidation Reasons (Count)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Pie chart
        ax2.pie(reason_analysis['count'], labels=[r[:30] + '...' if len(r) > 30 else r 
                                                   for r in reason_analysis.index],
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
        ax2.set_title('Liquidation Reasons (Percentage)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q5_Liquidation_Reasons.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q5_Liquidation_Reasons.png")
        
        # Store results
        self.results['answers']['question5'] = {
            'liquidation_reasons': reason_analysis.to_dict('index'),
            'summary': {
                'total_reasons': len(reason_analysis),
                'most_common_reason': reason_analysis.index[0],
                'most_common_count': int(reason_analysis.iloc[0]['count']),
                'most_common_percentage': round(reason_analysis.iloc[0]['percentage'], 2)
            }
        }
    
    def answer_question6(self):
        """Q6: Number of liquidations and sellable for each category"""
        print("\n" + "=" * 80)
        print("QUESTION 6: Number of liquidations and sellable for each category")
        print("=" * 80)
        
        # Create pivot table
        pivot = pd.crosstab(self.df['category_group'], self.df['Disposition'], margins=True)
        
        # Calculate liquidation rate
        pivot['Liquidation_Rate_%'] = (pivot['Liquidate'] / pivot['All'] * 100).round(2)
        pivot = pivot.sort_values('Liquidate', ascending=False)
        
        print("\nCategory × Disposition Pivot Table (Top 20):")
        print(f"{'Category':<50} {'Liquidate':<12} {'Sellable':<12} {'Total':<10} {'Rate %':<10}")
        print("-" * 100)
        for cat in pivot.index[:-1]:  # Exclude 'All' row
            if pivot.loc[cat, 'All'] > 0:
                cat_short = cat[:48] if len(cat) > 48 else cat
                print(f"{cat_short:<50} {int(pivot.loc[cat, 'Liquidate']):<12} "
                      f"{int(pivot.loc[cat, 'Sellable']):<12} {int(pivot.loc[cat, 'All']):<10} "
                      f"{pivot.loc[cat, 'Liquidation_Rate_%']:<10.1f}")
        
        # Show totals
        print(f"\n{'TOTAL':<50} {int(pivot.loc['All', 'Liquidate']):<12} "
              f"{int(pivot.loc['All', 'Sellable']):<12} {int(pivot.loc['All', 'All']):<10} "
              f"{pivot.loc['All', 'Liquidation_Rate_%']:<10.1f}")
        
        # Visualize
        fig, ax = plt.subplots(figsize=(16, 10))
        top_20 = pivot.head(20).drop('All', errors='ignore')
        
        x = np.arange(len(top_20))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, top_20['Liquidate'], width, label='Liquidate', 
                      color='#e74c3c', alpha=0.7)
        bars2 = ax.bar(x + width/2, top_20['Sellable'], width, label='Sellable', 
                      color='#2ecc71', alpha=0.7)
        
        ax.set_xlabel('Category', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Liquidation vs Sellable by Category (Top 20)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([cat[:30] for cat in top_20.index], rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q6_Category_Disposition_Pivot.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q6_Category_Disposition_Pivot.png")
        
        # Store results
        pivot_dict = pivot.drop('All', errors='ignore').to_dict('index')
        self.results['answers']['question6'] = {
            'pivot_table': {k: {kk: (int(vv) if isinstance(vv, (int, np.integer)) else float(vv)) 
                               for kk, vv in v.items()} 
                           for k, v in pivot_dict.items()},
            'summary': {
                'total_categories': len(pivot) - 1,
                'total_liquidated': int(pivot.loc['All', 'Liquidate']),
                'total_sellable': int(pivot.loc['All', 'Sellable']),
                'overall_liquidation_rate': round(pivot.loc['All', 'Liquidation_Rate_%'], 2)
            }
        }
    
    def answer_question7(self):
        """Q7: Number of Sellable and Liquidation for each product"""
        print("\n" + "=" * 80)
        print("QUESTION 7: Number of Sellable and Liquidation for each product")
        print("=" * 80)
        
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        product_analysis['liquidation_rate_pct'] = product_analysis['liquidation_rate'] * 100
        product_analysis = product_analysis.sort_values('liquidated_count', ascending=False)
        
        print("\nTop 20 Products by Liquidation Count:")
        print(f"{'Product':<60} {'Liquidated':<12} {'Sellable':<12} {'Total':<10} {'Rate %':<10}")
        print("-" * 105)
        for product, row in product_analysis.head(20).iterrows():
            sellable_count = int(row['total_count'] - row['liquidated_count'])
            product_short = product[:58] if len(product) > 58 else product
            print(f"{product_short:<60} {int(row['liquidated_count']):<12} {sellable_count:<12} "
                  f"{int(row['total_count']):<10} {row['liquidation_rate_pct']:<10.1f}")
        
        # Products with high liquidation rates
        high_liquidation = product_analysis[
            (product_analysis['liquidation_rate_pct'] >= 50) & 
            (product_analysis['total_count'] >= 3)
        ].sort_values('liquidation_rate_pct', ascending=False)
        
        print(f"\nProducts with High Liquidation Rate (>=50%, min 3 orders): {len(high_liquidation)}")
        if len(high_liquidation) > 0:
            print(f"{'Product':<60} {'Liquidation Rate %':<20}")
            print("-" * 80)
            for product, row in high_liquidation.head(15).iterrows():
                product_short = product[:58] if len(product) > 58 else product
                print(f"{product_short:<60} {row['liquidation_rate_pct']:<20.1f}")
        
        # Products with inconsistent outcomes
        inconsistent = product_analysis[
            (product_analysis['liquidated_count'] > 0) & 
            (product_analysis['liquidated_count'] < product_analysis['total_count']) &
            (product_analysis['total_count'] >= 5)
        ].sort_values('total_count', ascending=False)
        
        print(f"\nProducts with Inconsistent Outcomes (some liquidate, some sellable, min 5 orders): {len(inconsistent)}")
        if len(inconsistent) > 0:
            print(f"{'Product':<60} {'Liquidated':<12} {'Sellable':<12} {'Total':<10} {'Rate %':<10}")
            print("-" * 105)
            for product, row in inconsistent.head(15).iterrows():
                sellable_count = int(row['total_count'] - row['liquidated_count'])
                product_short = product[:58] if len(product) > 58 else product
                print(f"{product_short:<60} {int(row['liquidated_count']):<12} {sellable_count:<12} "
                      f"{int(row['total_count']):<10} {row['liquidation_rate_pct']:<10.1f}")
        
        # Visualize
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Top products by liquidation count
        top_20 = product_analysis.head(20)
        bars1 = ax1.barh(range(len(top_20)), top_20['liquidated_count'].values,
                        color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(top_20)))
        ax1.set_yticklabels([prod[:40] for prod in top_20.index], fontsize=8)
        ax1.set_xlabel('Liquidation Count', fontsize=12)
        ax1.set_title('Top 20 Products by Liquidation Count', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # High liquidation rate products
        if len(high_liquidation) > 0:
            top_15_high = high_liquidation.head(15)
            bars2 = ax2.barh(range(len(top_15_high)), top_15_high['liquidation_rate_pct'].values,
                            color='#c0392b', alpha=0.7)
            ax2.set_yticks(range(len(top_15_high)))
            ax2.set_yticklabels([prod[:40] for prod in top_15_high.index], fontsize=8)
            ax2.set_xlabel('Liquidation Rate (%)', fontsize=12)
            ax2.set_title('Products with High Liquidation Rate (>=50%)', fontsize=14, fontweight='bold')
            ax2.set_xlim(0, 105)
            ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'Q7_Product_Analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n[OK] Saved visualization: Q7_Product_Analysis.png")
        
        # Store results
        self.results['answers']['question7'] = {
            'top_20_products': product_analysis.head(20).to_dict('index'),
            'high_liquidation_products': high_liquidation.head(15).to_dict('index') if len(high_liquidation) > 0 else {},
            'inconsistent_products': inconsistent.head(15).to_dict('index') if len(inconsistent) > 0 else {},
            'summary': {
                'total_products': len(product_analysis),
                'products_with_liquidations': int((product_analysis['liquidated_count'] > 0).sum()),
                'high_liquidation_count': len(high_liquidation),
                'inconsistent_count': len(inconsistent)
            }
        }
    
    def save_results(self):
        """Save Phase 6 results to JSON"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        output_file = f"{base_name}_phase6_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 6 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 6 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Answered all 7 specific questions")
        print(f"[OK] Generated visualizations for each question")
        print(f"[OK] All answers saved to JSON")
        print(f"[OK] Graphs saved to: {self.graphs_dir}")


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
            print("Usage: python phase6_answer_questions.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 6 analysis
    try:
        analyzer = Phase6AnswerQuestions(csv_file)
        results = analyzer.run_phase6()
        print("\n[OK] Phase 6 question answering completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 6 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

