#!/usr/bin/env python3
"""
Phase 3: Data Visualization
Generate graphs and charts from Phase 3 EDA results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from pathlib import Path

# Set style for better-looking plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")

class Phase3Visualizations:
    def __init__(self, preprocessed_csv_path):
        """Initialize visualization generator"""
        self.preprocessed_csv_path = preprocessed_csv_path
        self.df = None
        self.output_dir = os.path.dirname(preprocessed_csv_path)
        self.check_cols = []
        
    def run_visualizations(self):
        """Generate all visualizations"""
        print("=" * 80)
        print("PHASE 3: DATA VISUALIZATION")
        print("=" * 80)
        
        # Load data
        self.load_data()
        
        # Create output directory for graphs
        graphs_dir = os.path.join(self.output_dir, "Phase3_Graphs")
        os.makedirs(graphs_dir, exist_ok=True)
        self.graphs_dir = graphs_dir
        
        print(f"\n[OK] Output directory: {graphs_dir}")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        
        # 1. Target variable visualizations
        self.plot_disposition_distribution()
        
        # 2. COGS visualizations
        self.plot_cogs_distribution()
        self.plot_cogs_by_disposition()
        self.plot_liquidation_rate_by_cogs_bin()
        
        # 3. Categorical variable visualizations
        self.plot_top_categories()
        self.plot_liquidation_reasons()
        
        # 4. Category analysis
        self.plot_category_liquidation_analysis()
        
        # 5. Check analysis
        self.plot_top_failed_checks()
        self.plot_check_comparison()
        
        print("\n" + "=" * 80)
        print(f"ALL VISUALIZATIONS SAVED TO: {graphs_dir}")
        print("=" * 80)
        
    def load_data(self):
        """Load preprocessed data"""
        self.df = pd.read_csv(self.preprocessed_csv_path)
        
        # Identify check columns
        order_cols = ['LPN', 'Amazon COGS', 'Completed On', 'Disposition', 'Product', 
                      'Product Category', 'Result of Repair', 'Scheduled Date', 
                      'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'Checks/Title',
                      'Checks/Failed by decision logic Automatically', 'Checks/Status',
                      'is_human_executed', 'is_liquidated', 'cogs_bin', 'processing_days']
        self.check_cols = [c for c in self.df.columns if c not in order_cols]
    
    def plot_disposition_distribution(self):
        """Plot disposition distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Bar chart
        disposition_counts = self.df['Disposition'].value_counts()
        colors = ['#2ecc71', '#e74c3c']  # Green for Sellable, Red for Liquidate
        bars = ax1.bar(disposition_counts.index, disposition_counts.values, color=colors)
        ax1.set_title('Disposition Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_xlabel('Disposition', fontsize=12)
        
        # Add value labels on bars
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
        plt.savefig(os.path.join(self.graphs_dir, '01_Disposition_Distribution.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 01_Disposition_Distribution.png")
    
    def plot_cogs_distribution(self):
        """Plot COGS distribution"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        cogs = self.df['Amazon COGS']
        
        # Histogram
        axes[0, 0].hist(cogs, bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(cogs.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${cogs.mean():,.2f}')
        axes[0, 0].axvline(cogs.median(), color='green', linestyle='--', linewidth=2, label=f'Median: ${cogs.median():,.2f}')
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
        liquidated_cogs = self.df[self.df['is_liquidated'] == 1]['Amazon COGS']
        sellable_cogs = self.df[self.df['is_liquidated'] == 0]['Amazon COGS']
        
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
        plt.savefig(os.path.join(self.graphs_dir, '02_COGS_Distribution.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 02_COGS_Distribution.png")
    
    def plot_cogs_by_disposition(self):
        """Plot COGS statistics by disposition"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        cogs_stats = self.df.groupby('Disposition')['Amazon COGS'].agg(['mean', 'median'])
        
        x = np.arange(len(cogs_stats.index))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, cogs_stats['mean'], width, label='Mean', alpha=0.8)
        bars2 = ax.bar(x + width/2, cogs_stats['median'], width, label='Median', alpha=0.8)
        
        ax.set_xlabel('Disposition', fontsize=12)
        ax.set_ylabel('COGS ($)', fontsize=12)
        ax.set_title('COGS Statistics by Disposition', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cogs_stats.index)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '03_COGS_by_Disposition.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 03_COGS_by_Disposition.png")
    
    def plot_liquidation_rate_by_cogs_bin(self):
        """Plot liquidation rate by COGS bins"""
        if 'cogs_bin' not in self.df.columns:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bin_analysis = self.df.groupby('cogs_bin').agg({
            'is_liquidated': ['sum', 'count', 'mean']
        })
        bin_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate']
        bin_analysis['liquidation_rate_pct'] = bin_analysis['liquidation_rate'] * 100
        
        # Sort by bin order
        bin_order = ['<$1K', '$1K-$1.5K', '$1.5K-$2K', '$2K-$2.5K', '$2.5K-$3K', '$3K+']
        bin_analysis = bin_analysis.reindex([b for b in bin_order if b in bin_analysis.index])
        
        bars = ax.bar(bin_analysis.index, bin_analysis['liquidation_rate_pct'], 
                     color='#e74c3c', alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('COGS Bin', fontsize=12)
        ax.set_ylabel('Liquidation Rate (%)', fontsize=12)
        ax.set_title('Liquidation Rate by COGS Bin', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (bin_name, row) in enumerate(bin_analysis.iterrows()):
            height = row['liquidation_rate_pct']
            total = row['total_count']
            liquidated = row['liquidated_count']
            ax.text(i, height,
                   f'{height:.1f}%\n({int(liquidated)}/{int(total)})',
                   ha='center', va='bottom', fontsize=10)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '04_Liquidation_Rate_by_COGS_Bin.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 04_Liquidation_Rate_by_COGS_Bin.png")
    
    def plot_top_categories(self):
        """Plot top categories"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        category_counts = self.df['Product Category'].value_counts().head(10)
        
        # Top categories by count
        bars1 = ax1.barh(range(len(category_counts)), category_counts.values, 
                        color='steelblue', alpha=0.7)
        ax1.set_yticks(range(len(category_counts)))
        ax1.set_yticklabels([cat.split('/')[-1][:40] for cat in category_counts.index], fontsize=9)
        ax1.set_xlabel('Count', fontsize=12)
        ax1.set_title('Top 10 Product Categories (by Count)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, val) in enumerate(category_counts.items()):
            ax1.text(val, i, f' {int(val)}', va='center', fontsize=10)
        
        # Top categories by liquidation
        category_analysis = self.df.groupby('Product Category').agg({
            'is_liquidated': 'sum'
        }).sort_values('is_liquidated', ascending=False).head(10)
        
        bars2 = ax2.barh(range(len(category_analysis)), category_analysis['is_liquidated'].values,
                        color='#e74c3c', alpha=0.7)
        ax2.set_yticks(range(len(category_analysis)))
        ax2.set_yticklabels([cat.split('/')[-1][:40] for cat in category_analysis.index], fontsize=9)
        ax2.set_xlabel('Liquidation Count', fontsize=12)
        ax2.set_title('Top 10 Categories by Liquidation Count', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, val) in enumerate(category_analysis.iterrows()):
            ax2.text(val['is_liquidated'], i, f' {int(val["is_liquidated"])}', 
                    va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '05_Top_Categories.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 05_Top_Categories.png")
    
    def plot_liquidation_reasons(self):
        """Plot liquidation reasons"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        liquidated = self.df[self.df['is_liquidated'] == 1]
        repair_result_counts = liquidated['Result of Repair'].value_counts()
        
        # Bar chart
        bars = ax1.barh(range(len(repair_result_counts)), repair_result_counts.values,
                       color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(repair_result_counts)))
        ax1.set_yticklabels([reason[:50] for reason in repair_result_counts.index], fontsize=9)
        ax1.set_xlabel('Count', fontsize=12)
        ax1.set_title('Liquidation Reasons (Count)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, val) in enumerate(repair_result_counts.items()):
            pct = val / len(liquidated) * 100
            ax1.text(val, i, f' {int(val)} ({pct:.1f}%)', va='center', fontsize=9)
        
        # Pie chart
        ax2.pie(repair_result_counts.values, 
               labels=[reason[:30] + '...' if len(reason) > 30 else reason 
                      for reason in repair_result_counts.index],
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
        ax2.set_title('Liquidation Reasons (Percentage)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '06_Liquidation_Reasons.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 06_Liquidation_Reasons.png")
    
    def plot_category_liquidation_analysis(self):
        """Plot category liquidation analysis"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        category_analysis = self.df.groupby('Product Category').agg({
            'is_liquidated': ['sum', 'count', 'mean'],
            'Amazon COGS': 'mean'
        })
        category_analysis.columns = ['liquidated_count', 'total_count', 'liquidation_rate', 'avg_cogs']
        category_analysis['liquidation_rate_pct'] = category_analysis['liquidation_rate'] * 100
        category_analysis = category_analysis.sort_values('liquidated_count', ascending=False).head(15)
        
        # Create horizontal bar chart
        y_pos = np.arange(len(category_analysis))
        bars = ax.barh(y_pos, category_analysis['liquidation_rate_pct'], 
                      color='#e74c3c', alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([cat.split('/')[-1][:50] for cat in category_analysis.index], fontsize=9)
        ax.set_xlabel('Liquidation Rate (%)', fontsize=12)
        ax.set_title('Top 15 Categories: Liquidation Rate', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, row) in enumerate(category_analysis.iterrows()):
            ax.text(row['liquidation_rate_pct'], i,
                   f" {row['liquidation_rate_pct']:.1f}% ({int(row['liquidated_count'])}/{int(row['total_count'])})",
                   va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '07_Category_Liquidation_Analysis.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 07_Category_Liquidation_Analysis.png")
    
    def plot_top_failed_checks(self):
        """Plot top failed checks"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Overall failed checks
        check_failure_counts = {}
        for col in self.check_cols:
            failed = (self.df[col] == 'Failed').sum()
            if failed > 0:
                check_failure_counts[col] = failed
        
        check_failure_df = pd.DataFrame.from_dict(check_failure_counts, orient='index', 
                                                 columns=['failure_count'])
        check_failure_df = check_failure_df.sort_values('failure_count', ascending=False).head(15)
        
        bars1 = ax1.barh(range(len(check_failure_df)), check_failure_df['failure_count'].values,
                        color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(check_failure_df)))
        ax1.set_yticklabels([check[:50] for check in check_failure_df.index], fontsize=9)
        ax1.set_xlabel('Failure Count', fontsize=12)
        ax1.set_title('Top 15 Most Frequently Failed Checks (Overall)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, val) in enumerate(check_failure_df.iterrows()):
            ax1.text(val['failure_count'], i, f" {int(val['failure_count'])}", 
                    va='center', fontsize=9)
        
        # Failed checks in liquidated orders
        liquidated = self.df[self.df['is_liquidated'] == 1]
        check_failure_liquidated = {}
        for col in self.check_cols:
            failed = (liquidated[col] == 'Failed').sum()
            if failed > 0:
                check_failure_liquidated[col] = failed
        
        check_failure_liquidated_df = pd.DataFrame.from_dict(check_failure_liquidated, orient='index',
                                                             columns=['failure_count'])
        check_failure_liquidated_df = check_failure_liquidated_df.sort_values('failure_count', 
                                                                             ascending=False).head(15)
        
        bars2 = ax2.barh(range(len(check_failure_liquidated_df)), 
                        check_failure_liquidated_df['failure_count'].values,
                        color='#c0392b', alpha=0.7)
        ax2.set_yticks(range(len(check_failure_liquidated_df)))
        ax2.set_yticklabels([check[:50] for check in check_failure_liquidated_df.index], fontsize=9)
        ax2.set_xlabel('Failure Count (Liquidated Orders)', fontsize=12)
        ax2.set_title('Top 15 Most Frequently Failed Checks (Liquidated Orders)', 
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        for i, (idx, val) in enumerate(check_failure_liquidated_df.iterrows()):
            ax2.text(val['failure_count'], i, f" {int(val['failure_count'])}", 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graphs_dir, '08_Top_Failed_Checks.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 08_Top_Failed_Checks.png")
    
    def plot_check_comparison(self):
        """Plot check comparison between liquidated and sellable"""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        liquidated = self.df[self.df['is_liquidated'] == 1]
        sellable = self.df[self.df['is_liquidated'] == 0]
        
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
        plt.savefig(os.path.join(self.graphs_dir, '09_Check_Comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Saved: 09_Check_Comparison.png")


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
            print("Usage: python phase3_visualizations.py <preprocessed_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Check if matplotlib is available
    try:
        import matplotlib
    except ImportError:
        print("\n[ERROR] matplotlib is not installed.")
        print("Please install it using: pip install matplotlib seaborn")
        return
    
    # Run visualizations
    try:
        viz = Phase3Visualizations(csv_file)
        viz.run_visualizations()
        print("\n[OK] All visualizations generated successfully!")
    except Exception as e:
        print(f"\n[ERROR] Error during visualization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

