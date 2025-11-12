#!/usr/bin/env python3
"""
Phase 8: Data Visualization
Liquidation Analysis - Comprehensive visualizations and dashboard
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import json

# Set style for plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")

class Phase8Visualizations:
    def __init__(self, features_csv_path):
        """Initialize Phase 8 visualizations"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.check_cols = []
        self.results = {
            'phase': 'Phase 8: Data Visualization',
            'timestamp': datetime.now().isoformat(),
            'file_path': features_csv_path,
            'visualizations_created': []
        }
        self.output_dir = os.path.dirname(features_csv_path)
        self.graphs_dir = os.path.join(self.output_dir, "Phase8_Visualizations")
        os.makedirs(self.graphs_dir, exist_ok=True)
        
    def run_phase8(self):
        """Execute all Phase 8 tasks"""
        print("=" * 80)
        print("PHASE 8: DATA VISUALIZATION")
        print("=" * 80)
        
        # Load feature-engineered data
        self.load_data()
        
        # 8.1 Key Visualizations
        self.create_distribution_charts()
        self.create_comparison_charts()
        self.create_financial_impact_charts()
        self.create_product_level_charts()
        self.create_check_analysis_charts()
        
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
        print(f"[OK] Output directory: {self.graphs_dir}")
    
    def create_distribution_charts(self):
        """8.1.1 Distribution charts"""
        print("\n" + "-" * 80)
        print("8.1.1 CREATING DISTRIBUTION CHARTS")
        print("-" * 80)
        
        # Chart 1: Disposition distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        disposition_counts = self.df['Disposition'].value_counts()
        colors = ['#2ecc71', '#e74c3c']
        
        # Bar chart
        bars = ax1.bar(disposition_counts.index, disposition_counts.values, color=colors)
        ax1.set_title('Disposition Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_xlabel('Disposition', fontsize=12)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}\n({height/len(self.df)*100:.1f}%)',
                    ha='center', va='bottom', fontsize=11)
        
        # Pie chart
        ax2.pie(disposition_counts.values, labels=disposition_counts.index, 
                autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Disposition Distribution (Pie Chart)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V01_Disposition_Distribution.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V01_Disposition_Distribution.png")
        self.results['visualizations_created'].append('V01_Disposition_Distribution.png')
        
        # Chart 2: COGS distribution
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        cogs = self.df['Amazon COGS']
        liquidated_cogs = self.liquidated['Amazon COGS']
        sellable_cogs = self.sellable['Amazon COGS']
        
        # Histogram
        axes[0, 0].hist(cogs, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
        axes[0, 0].axvline(cogs.mean(), color='red', linestyle='--', linewidth=2, 
                           label=f'Mean: ${cogs.mean():,.2f}')
        axes[0, 0].axvline(cogs.median(), color='green', linestyle='--', linewidth=2, 
                           label=f'Median: ${cogs.median():,.2f}')
        axes[0, 0].set_title('COGS Distribution (Histogram)', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('COGS ($)', fontsize=12)
        axes[0, 0].set_ylabel('Frequency', fontsize=12)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Box plot
        bp = axes[0, 1].boxplot([cogs], vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        axes[0, 1].set_title('COGS Distribution (Box Plot)', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('COGS ($)', fontsize=12)
        axes[0, 1].grid(True, alpha=0.3)
        
        # COGS by Disposition - Histogram overlay
        axes[1, 0].hist([sellable_cogs, liquidated_cogs], bins=30, 
                       label=['Sellable', 'Liquidate'], alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('COGS Distribution by Disposition', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('COGS ($)', fontsize=12)
        axes[1, 0].set_ylabel('Frequency', fontsize=12)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # COGS by Disposition - Box plot
        data_to_plot = [sellable_cogs, liquidated_cogs]
        bp = axes[1, 1].boxplot(data_to_plot, tick_labels=['Sellable', 'Liquidate'], 
                                patch_artist=True)
        bp['boxes'][0].set_facecolor('#2ecc71')
        bp['boxes'][1].set_facecolor('#e74c3c')
        axes[1, 1].set_title('COGS by Disposition (Box Plot)', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('COGS ($)', fontsize=12)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V02_COGS_Distribution.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V02_COGS_Distribution.png")
        self.results['visualizations_created'].append('V02_COGS_Distribution.png')
    
    def create_comparison_charts(self):
        """8.1.2 Comparison charts"""
        print("\n" + "-" * 80)
        print("8.1.2 CREATING COMPARISON CHARTS")
        print("-" * 80)
        
        # Chart 1: Liquidation rate by category
        category_rates = self.df.groupby('category_group').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        category_rates.columns = ['liquidated', 'total', 'rate']
        category_rates['rate_pct'] = category_rates['rate'] * 100
        category_rates = category_rates.sort_values('liquidated', ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        bars = ax.barh(range(len(category_rates)), category_rates['rate_pct'].values,
                      color='#e74c3c', alpha=0.7)
        ax.set_yticks(range(len(category_rates)))
        ax.set_yticklabels([cat[:50] for cat in category_rates.index], fontsize=9)
        ax.set_xlabel('Liquidation Rate (%)', fontsize=12)
        ax.set_title('Top 15 Categories: Liquidation Rate', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, row) in enumerate(category_rates.iterrows()):
            ax.text(row['rate_pct'], i,
                   f" {row['rate_pct']:.1f}% ({int(row['liquidated'])}/{int(row['total'])})",
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V03_Liquidation_Rate_by_Category.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V03_Liquidation_Rate_by_Category.png")
        self.results['visualizations_created'].append('V03_Liquidation_Rate_by_Category.png')
        
        # Chart 2: Liquidation rate by COGS bin
        if 'cogs_bin' in self.df.columns:
            cogs_rates = self.df.groupby('cogs_bin').agg({
                'is_liquidated': ['sum', 'count', 'mean']
            })
            cogs_rates.columns = ['liquidated', 'total', 'rate']
            cogs_rates['rate_pct'] = cogs_rates['rate'] * 100
            
            # Sort by bin order
            bin_order = ['<$1K', '$1K-$1.5K', '$1.5K-$2K', '$2K-$2.5K', '$2.5K-$3K', '$3K+']
            cogs_rates = cogs_rates.reindex([b for b in bin_order if b in cogs_rates.index])
            
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(cogs_rates.index.astype(str), cogs_rates['rate_pct'].values,
                         color='#e74c3c', alpha=0.7, edgecolor='black')
            ax.set_xlabel('COGS Bin', fontsize=12)
            ax.set_ylabel('Liquidation Rate (%)', fontsize=12)
            ax.set_title('Liquidation Rate by COGS Bin', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 105)
            ax.grid(True, alpha=0.3, axis='y')
            
            for i, (bin_name, row) in enumerate(cogs_rates.iterrows()):
                ax.text(i, row['rate_pct'],
                       f'{row["rate_pct"]:.1f}%\n({int(row["liquidated"])}/{int(row["total"])})',
                       ha='center', va='bottom', fontsize=9)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.graphs_dir, 'V04_Liquidation_Rate_by_COGS_Bin.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()
            print("[OK] Saved: V04_Liquidation_Rate_by_COGS_Bin.png")
            self.results['visualizations_created'].append('V04_Liquidation_Rate_by_COGS_Bin.png')
        
        # Chart 3: Check failure rates comparison
        liquidated = self.liquidated
        sellable = self.sellable
        
        check_comparison = []
        for col in self.check_cols:
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
                    'liquidated_rate': liquidated_rate,
                    'sellable_rate': sellable_rate,
                    'difference': difference
                })
        
        comparison_df = pd.DataFrame(check_comparison)
        comparison_df = comparison_df.sort_values('difference', ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        x = np.arange(len(comparison_df))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, comparison_df['liquidated_rate'], width, 
                       label='Liquidated', color='#e74c3c', alpha=0.7)
        bars2 = ax.barh(x + width/2, comparison_df['sellable_rate'], width, 
                       label='Sellable', color='#2ecc71', alpha=0.7)
        
        ax.set_yticks(x)
        ax.set_yticklabels([check[:50] for check in comparison_df['check_name']], fontsize=9)
        ax.set_xlabel('Failure Rate (%)', fontsize=12)
        ax.set_title('Top 15 Checks: Failure Rate Comparison (Liquidated vs Sellable)', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V05_Check_Failure_Rates_Comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V05_Check_Failure_Rates_Comparison.png")
        self.results['visualizations_created'].append('V05_Check_Failure_Rates_Comparison.png')
        
        # Chart 4: Liquidation reasons breakdown
        liquidated = self.liquidated
        reason_counts = liquidated['Result of Repair'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Bar chart
        bars = ax1.barh(range(len(reason_counts)), reason_counts.values,
                       color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(reason_counts)))
        ax1.set_yticklabels([reason[:50] for reason in reason_counts.index], fontsize=9)
        ax1.set_xlabel('Count', fontsize=12)
        ax1.set_title('Liquidation Reasons (Count)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, val) in enumerate(reason_counts.items()):
            pct = val / len(liquidated) * 100
            ax1.text(val, i, f' {int(val)} ({pct:.1f}%)', va='center', fontsize=9)
        
        # Pie chart
        ax2.pie(reason_counts.values, 
               labels=[reason[:30] + '...' if len(reason) > 30 else reason 
                      for reason in reason_counts.index],
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
        ax2.set_title('Liquidation Reasons (Percentage)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V06_Liquidation_Reasons_Breakdown.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V06_Liquidation_Reasons_Breakdown.png")
        self.results['visualizations_created'].append('V06_Liquidation_Reasons_Breakdown.png')
    
    def create_financial_impact_charts(self):
        """8.1.3 Financial impact charts"""
        print("\n" + "-" * 80)
        print("8.1.3 CREATING FINANCIAL IMPACT CHARTS")
        print("-" * 80)
        
        # Chart 1: Total value lost by category
        category_value = self.liquidated.groupby('category_group').agg({
            'Amazon COGS': 'sum'
        }).sort_values('Amazon COGS', ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        bars = ax.barh(range(len(category_value)), category_value['Amazon COGS'].values,
                      color='#c0392b', alpha=0.7)
        ax.set_yticks(range(len(category_value)))
        ax.set_yticklabels([cat[:50] for cat in category_value.index], fontsize=9)
        ax.set_xlabel('Value Lost ($)', fontsize=12)
        ax.set_title('Top 15 Categories: Total Value Lost to Liquidation', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, val) in enumerate(category_value.iterrows()):
            ax.text(val['Amazon COGS'], i, f" ${val['Amazon COGS']:,.0f}", 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V07_Value_Lost_by_Category.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V07_Value_Lost_by_Category.png")
        self.results['visualizations_created'].append('V07_Value_Lost_by_Category.png')
        
        # Chart 2: Total value lost by reason
        reason_value = self.liquidated.groupby('Result of Repair')['Amazon COGS'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        bars = ax.barh(range(len(reason_value)), reason_value.values,
                      color='#c0392b', alpha=0.7)
        ax.set_yticks(range(len(reason_value)))
        ax.set_yticklabels([reason[:50] for reason in reason_value.index], fontsize=9)
        ax.set_xlabel('Value Lost ($)', fontsize=12)
        ax.set_title('Total Value Lost by Liquidation Reason', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, val) in enumerate(reason_value.items()):
            ax.text(val, i, f" ${val:,.0f}", va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V08_Value_Lost_by_Reason.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V08_Value_Lost_by_Reason.png")
        self.results['visualizations_created'].append('V08_Value_Lost_by_Reason.png')
        
        # Chart 3: Average COGS liquidated vs sellable
        cogs_stats = self.df.groupby('Disposition')['Amazon COGS'].agg(['mean', 'median'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(cogs_stats.index))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, cogs_stats['mean'], width, label='Mean', alpha=0.8, color='#e74c3c')
        bars2 = ax.bar(x + width/2, cogs_stats['median'], width, label='Median', alpha=0.8, color='#c0392b')
        
        ax.set_xlabel('Disposition', fontsize=12)
        ax.set_ylabel('COGS ($)', fontsize=12)
        ax.set_title('Average COGS: Liquidated vs Sellable', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cogs_stats.index)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V09_Avg_COGS_Comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V09_Avg_COGS_Comparison.png")
        self.results['visualizations_created'].append('V09_Avg_COGS_Comparison.png')
    
    def create_product_level_charts(self):
        """8.1.4 Product-level charts"""
        print("\n" + "-" * 80)
        print("8.1.4 CREATING PRODUCT-LEVEL CHARTS")
        print("-" * 80)
        
        # Chart 1: Top products by liquidation count
        product_analysis = self.df.groupby('Product').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        product_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        product_analysis = product_analysis.sort_values('liquidated_count', ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        bars = ax.barh(range(len(product_analysis)), product_analysis['liquidated_count'].values,
                      color='#e74c3c', alpha=0.7)
        ax.set_yticks(range(len(product_analysis)))
        ax.set_yticklabels([prod[:50] for prod in product_analysis.index], fontsize=9)
        ax.set_xlabel('Liquidation Count', fontsize=12)
        ax.set_title('Top 15 Products by Liquidation Count', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, row) in enumerate(product_analysis.iterrows()):
            ax.text(row['liquidated_count'], i, f" {int(row['liquidated_count'])}", 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V10_Top_Products_by_Liquidation.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V10_Top_Products_by_Liquidation.png")
        self.results['visualizations_created'].append('V10_Top_Products_by_Liquidation.png')
        
        # Chart 2: Products with high liquidation rates
        high_liquidation = product_analysis[
            (product_analysis['liquidation_rate'] >= 0.5) & 
            (product_analysis['total_count'] >= 3)
        ].sort_values('liquidation_rate', ascending=False).head(15)
        
        if len(high_liquidation) > 0:
            fig, ax = plt.subplots(figsize=(16, 10))
            bars = ax.barh(range(len(high_liquidation)), 
                          high_liquidation['liquidation_rate'].values * 100,
                          color='#c0392b', alpha=0.7)
            ax.set_yticks(range(len(high_liquidation)))
            ax.set_yticklabels([prod[:50] for prod in high_liquidation.index], fontsize=9)
            ax.set_xlabel('Liquidation Rate (%)', fontsize=12)
            ax.set_title('Products with High Liquidation Rate (>=50%)', 
                        fontsize=14, fontweight='bold')
            ax.set_xlim(0, 105)
            ax.grid(True, alpha=0.3, axis='x')
            
            for i, (idx, row) in enumerate(high_liquidation.iterrows()):
                ax.text(row['liquidation_rate'] * 100, i, 
                       f" {row['liquidation_rate']*100:.1f}%", 
                       va='center', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.graphs_dir, 'V11_High_Liquidation_Rate_Products.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()
            print("[OK] Saved: V11_High_Liquidation_Rate_Products.png")
            self.results['visualizations_created'].append('V11_High_Liquidation_Rate_Products.png')
    
    def create_check_analysis_charts(self):
        """8.1.5 Check analysis charts"""
        print("\n" + "-" * 80)
        print("8.1.5 CREATING CHECK ANALYSIS CHARTS")
        print("-" * 80)
        
        # Chart 1: Top checks causing liquidations
        check_failure_counts = {}
        for col in self.check_cols:
            failed = (self.liquidated[col] == 'Failed').sum()
            if failed > 0:
                check_failure_counts[col] = failed
        
        check_failure_df = pd.DataFrame.from_dict(check_failure_counts, orient='index', 
                                                 columns=['failure_count'])
        check_failure_df = check_failure_df.sort_values('failure_count', ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        bars = ax.barh(range(len(check_failure_df)), check_failure_df['failure_count'].values,
                      color='#e74c3c', alpha=0.7)
        ax.set_yticks(range(len(check_failure_df)))
        ax.set_yticklabels([check[:50] for check in check_failure_df.index], fontsize=9)
        ax.set_xlabel('Failure Count in Liquidated Orders', fontsize=12)
        ax.set_title('Top 15 Quality Checks Causing Liquidations', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, row) in enumerate(check_failure_df.iterrows()):
            ax.text(row['failure_count'], i, f" {int(row['failure_count'])}", 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V12_Top_Checks_Causing_Liquidations.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V12_Top_Checks_Causing_Liquidations.png")
        self.results['visualizations_created'].append('V12_Top_Checks_Causing_Liquidations.png')
        
        # Chart 2: Check failure rate comparison (heatmap)
        # Select top 15 checks for heatmap
        top_checks = check_failure_df.head(15).index.tolist()
        
        # Create comparison matrix
        comparison_data = []
        for check in top_checks:
            liquidated_failed = (self.liquidated[check] == 'Failed').sum()
            liquidated_total = self.liquidated[check].notna().sum()
            liquidated_rate = (liquidated_failed / liquidated_total * 100) if liquidated_total > 0 else 0
            
            sellable_failed = (self.sellable[check] == 'Failed').sum()
            sellable_total = self.sellable[check].notna().sum()
            sellable_rate = (sellable_failed / sellable_total * 100) if sellable_total > 0 else 0
            
            comparison_data.append({
                'check': check[:40],
                'liquidated_rate': liquidated_rate,
                'sellable_rate': sellable_rate
            })
        
        comp_df = pd.DataFrame(comparison_data)
        comp_df = comp_df.set_index('check')
        
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(comp_df, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Failure Rate (%)'}, ax=ax)
        ax.set_title('Check Failure Rate Comparison Heatmap\n(Liquidated vs Sellable)', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Disposition', fontsize=12)
        ax.set_ylabel('Quality Check', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, 'V13_Check_Failure_Rate_Heatmap.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: V13_Check_Failure_Rate_Heatmap.png")
        self.results['visualizations_created'].append('V13_Check_Failure_Rate_Heatmap.png')
    
    def save_results(self):
        """Save Phase 8 results to JSON"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        output_file = f"{base_name}_phase8_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 8 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nPHASE 8 SUMMARY:")
        print("-" * 80)
        print(f"[OK] Created {len(self.results['visualizations_created'])} visualizations")
        print(f"[OK] All graphs saved to: {self.graphs_dir}")
        print("\nVisualizations Created:")
        for i, viz in enumerate(self.results['visualizations_created'], 1):
            print(f"  {i:2d}. {viz}")


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
            print("Usage: python phase8_visualizations.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 8 visualizations
    try:
        viz = Phase8Visualizations(csv_file)
        results = viz.run_phase8()
        print("\n[OK] Phase 8 visualizations completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 8 visualizations: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

