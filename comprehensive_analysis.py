#!/usr/bin/env python3
"""
Comprehensive Liquidation Analysis
Answers specific questions about high COGS items and suggests additional insights
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json
from pathlib import Path

class ComprehensiveLiquidationAnalyzer:
    def __init__(self, csv_file):
        """Initialize analyzer with CSV file"""
        self.csv_file = csv_file
        self.df = None
        self.orders_df = None
        self.checks_df = None
        
    def load_data(self):
        """Load and structure the data"""
        print("Loading data...")
        self.df = pd.read_csv(self.csv_file)
        
        # Separate order headers from check steps
        # Order headers have non-null COGS
        self.orders_df = self.df[self.df['Amazon COGS'].notna()].copy()
        self.orders_df['Amazon COGS'] = pd.to_numeric(self.orders_df['Amazon COGS'], errors='coerce')
        
        # Check steps have null COGS but have Checks/Title
        self.checks_df = self.df[self.df['Amazon COGS'].isna() & self.df['Checks/Title'].notna()].copy()
        
        print(f"Loaded {len(self.orders_df)} repair orders")
        print(f"Loaded {len(self.checks_df)} quality check steps")
        
    def answer_question_1(self):
        """1. Which quality checks are causing liquidations"""
        print("\n" + "="*80)
        print("QUESTION 1: Which quality checks are causing liquidations?")
        print("="*80)
        
        # Get liquidated orders
        liquidated_orders = self.orders_df[self.orders_df['Disposition'] == 'Liquidate']
        liquidated_lpns = set(liquidated_orders['LPN'].dropna())
        
        # Get checks for liquidated orders
        liquidated_checks = self.checks_df[self.checks_df['LPN'].isin(liquidated_lpns)]
        
        # Count failed checks by check name
        failed_checks = liquidated_checks[liquidated_checks['Checks/Status'] == 'Failed']
        check_failures = failed_checks['Checks/Title'].value_counts()
        
        print(f"\nTop Quality Checks Causing Liquidations:")
        print("-" * 80)
        for check, count in check_failures.head(15).items():
            percentage = (count / len(liquidated_orders)) * 100
            print(f"{check}: {count} failures ({percentage:.1f}% of liquidated orders)")
        
        return check_failures.to_dict()
    
    def answer_question_2(self):
        """2. Patterns in high COGS items that get liquidated"""
        print("\n" + "="*80)
        print("QUESTION 2: Patterns in high COGS items that get liquidated")
        print("="*80)
        
        liquidated = self.orders_df[self.orders_df['Disposition'] == 'Liquidate']
        sellable = self.orders_df[self.orders_df['Disposition'] == 'Sellable']
        
        print(f"\nCOGS Statistics:")
        print("-" * 80)
        print(f"Liquidated Items:")
        print(f"  Count: {len(liquidated)}")
        print(f"  Average COGS: ${liquidated['Amazon COGS'].mean():.2f}")
        print(f"  Median COGS: ${liquidated['Amazon COGS'].median():.2f}")
        print(f"  Min COGS: ${liquidated['Amazon COGS'].min():.2f}")
        print(f"  Max COGS: ${liquidated['Amazon COGS'].max():.2f}")
        print(f"  Total Value Lost: ${liquidated['Amazon COGS'].sum():,.2f}")
        
        print(f"\nSellable Items:")
        print(f"  Count: {len(sellable)}")
        print(f"  Average COGS: ${sellable['Amazon COGS'].mean():.2f}")
        print(f"  Median COGS: ${sellable['Amazon COGS'].median():.2f}")
        
        # COGS distribution analysis
        print(f"\nCOGS Distribution Analysis:")
        print("-" * 80)
        bins = [1000, 1500, 2000, 2500, 3000, float('inf')]
        labels = ['$1K-$1.5K', '$1.5K-$2K', '$2K-$2.5K', '$2.5K-$3K', '$3K+']
        
        liquidated['COGS_Bin'] = pd.cut(liquidated['Amazon COGS'], bins=bins, labels=labels)
        sellable['COGS_Bin'] = pd.cut(sellable['Amazon COGS'], bins=bins, labels=labels)
        
        print("\nLiquidation Rate by COGS Range:")
        for label in labels:
            liquidated_count = len(liquidated[liquidated['COGS_Bin'] == label])
            sellable_count = len(sellable[sellable['COGS_Bin'] == label])
            total = liquidated_count + sellable_count
            if total > 0:
                rate = (liquidated_count / total) * 100
                print(f"  {label}: {liquidated_count}/{total} ({rate:.1f}%)")
        
        return {
            'liquidated_stats': liquidated['Amazon COGS'].describe().to_dict(),
            'sellable_stats': sellable['Amazon COGS'].describe().to_dict(),
            'total_value_lost': float(liquidated['Amazon COGS'].sum())
        }
    
    def answer_question_3(self):
        """3. Comparison of passed vs failed checks between Sellable and Liquidate"""
        print("\n" + "="*80)
        print("QUESTION 3: Comparison of passed vs failed checks")
        print("="*80)
        
        liquidated_lpns = set(self.orders_df[self.orders_df['Disposition'] == 'Liquidate']['LPN'].dropna())
        sellable_lpns = set(self.orders_df[self.orders_df['Disposition'] == 'Sellable']['LPN'].dropna())
        
        liquidated_checks = self.checks_df[self.checks_df['LPN'].isin(liquidated_lpns)]
        sellable_checks = self.checks_df[self.checks_df['LPN'].isin(sellable_lpns)]
        
        # Get unique check names
        all_checks = set(liquidated_checks['Checks/Title'].dropna()) | set(sellable_checks['Checks/Title'].dropna())
        
        comparison = []
        
        print(f"\nCheck-by-Check Comparison:")
        print("-" * 80)
        print(f"{'Check Name':<60} {'Liquidate Failed':<20} {'Sellable Failed':<20} {'Difference':<15}")
        print("-" * 115)
        
        for check in sorted(all_checks):
            if pd.isna(check):
                continue
                
            liq_failed = len(liquidated_checks[(liquidated_checks['Checks/Title'] == check) & 
                                               (liquidated_checks['Checks/Status'] == 'Failed')])
            sell_failed = len(sellable_checks[(sellable_checks['Checks/Title'] == check) & 
                                             (sellable_checks['Checks/Status'] == 'Failed')])
            
            liq_total = len(liquidated_checks[liquidated_checks['Checks/Title'] == check])
            sell_total = len(sellable_checks[sellable_checks['Checks/Title'] == check])
            
            if liq_total > 0 and sell_total > 0:
                liq_rate = (liq_failed / liq_total) * 100
                sell_rate = (sell_failed / sell_total) * 100
                diff = liq_rate - sell_rate
                
                if abs(diff) > 5 or liq_failed > 10:  # Show significant differences
                    print(f"{check[:58]:<60} {liq_failed:>5} ({liq_rate:>5.1f}%){'':<10} {sell_failed:>5} ({sell_rate:>5.1f}%){'':<10} {diff:>+6.1f}%")
                    comparison.append({
                        'check': check,
                        'liquidate_failed': liq_failed,
                        'liquidate_rate': liq_rate,
                        'sellable_failed': sell_failed,
                        'sellable_rate': sell_rate,
                        'difference': diff
                    })
        
        return comparison
    
    def answer_question_4(self):
        """4. Product categories most affected"""
        print("\n" + "="*80)
        print("QUESTION 4: Product categories most affected")
        print("="*80)
        
        category_analysis = self.orders_df.groupby(['Product Category', 'Disposition']).agg({
            'LPN': 'count',
            'Amazon COGS': ['sum', 'mean']
        }).reset_index()
        
        category_analysis.columns = ['Category', 'Disposition', 'Count', 'Total_COGS', 'Avg_COGS']
        
        print(f"\nCategory Analysis:")
        print("-" * 80)
        
        categories = self.orders_df['Product Category'].value_counts()
        
        for category in categories.head(10).index:
            cat_data = self.orders_df[self.orders_df['Product Category'] == category]
            liquidated = cat_data[cat_data['Disposition'] == 'Liquidate']
            sellable = cat_data[cat_data['Disposition'] == 'Sellable']
            
            total = len(cat_data)
            liq_count = len(liquidated)
            sell_count = len(sellable)
            liq_rate = (liq_count / total) * 100 if total > 0 else 0
            
            print(f"\n{category}:")
            print(f"  Total: {total} orders")
            print(f"  Liquidated: {liq_count} ({liq_rate:.1f}%)")
            print(f"  Sellable: {sell_count} ({100-liq_rate:.1f}%)")
            if len(liquidated) > 0:
                print(f"  Avg COGS Liquidated: ${liquidated['Amazon COGS'].mean():.2f}")
                print(f"  Total Value Lost: ${liquidated['Amazon COGS'].sum():,.2f}")
        
        return category_analysis.to_dict('records')
    
    def answer_question_5(self):
        """5. Specific liquidation reasons"""
        print("\n" + "="*80)
        print("QUESTION 5: Specific liquidation reasons")
        print("="*80)
        
        liquidated = self.orders_df[self.orders_df['Disposition'] == 'Liquidate']
        
        reasons = liquidated['Result of Repair'].value_counts()
        
        print(f"\nLiquidation Reasons Breakdown:")
        print("-" * 80)
        
        for reason, count in reasons.items():
            percentage = (count / len(liquidated)) * 100
            reason_data = liquidated[liquidated['Result of Repair'] == reason]
            avg_cogs = reason_data['Amazon COGS'].mean()
            total_value = reason_data['Amazon COGS'].sum()
            
            print(f"\n{reason}:")
            print(f"  Count: {count} ({percentage:.1f}%)")
            print(f"  Average COGS: ${avg_cogs:.2f}")
            print(f"  Total Value: ${total_value:,.2f}")
        
        return reasons.to_dict()
    
    def answer_question_6(self):
        """6. Number of liquidations and sellable for each category"""
        print("\n" + "="*80)
        print("QUESTION 6: Liquidation vs Sellable by Category")
        print("="*80)
        
        category_summary = self.orders_df.groupby(['Product Category', 'Disposition']).size().unstack(fill_value=0)
        
        if 'Liquidate' not in category_summary.columns:
            category_summary['Liquidate'] = 0
        if 'Sellable' not in category_summary.columns:
            category_summary['Sellable'] = 0
        
        category_summary['Total'] = category_summary['Liquidate'] + category_summary['Sellable']
        category_summary['Liquidation_Rate'] = (category_summary['Liquidate'] / category_summary['Total'] * 100).round(1)
        category_summary = category_summary.sort_values('Total', ascending=False)
        
        print(f"\n{'Category':<60} {'Liquidate':<12} {'Sellable':<12} {'Total':<10} {'Liq Rate':<12}")
        print("-" * 106)
        
        for category, row in category_summary.iterrows():
            print(f"{category[:58]:<60} {int(row['Liquidate']):<12} {int(row['Sellable']):<12} {int(row['Total']):<10} {row['Liquidation_Rate']:<12.1f}%")
        
        return category_summary.to_dict('index')
    
    def answer_question_7(self):
        """7. Number of Sellable and Liquidation for each product"""
        print("\n" + "="*80)
        print("QUESTION 7: Liquidation vs Sellable by Product")
        print("="*80)
        
        product_summary = self.orders_df.groupby(['Product', 'Disposition']).size().unstack(fill_value=0)
        
        if 'Liquidate' not in product_summary.columns:
            product_summary['Liquidate'] = 0
        if 'Sellable' not in product_summary.columns:
            product_summary['Sellable'] = 0
        
        product_summary['Total'] = product_summary['Liquidate'] + product_summary['Sellable']
        product_summary['Liquidation_Rate'] = (product_summary['Liquidate'] / product_summary['Total'] * 100).round(1)
        product_summary = product_summary.sort_values('Total', ascending=False)
        
        print(f"\nTop 20 Products:")
        print(f"{'Product':<50} {'Liquidate':<12} {'Sellable':<12} {'Total':<10} {'Liq Rate':<12}")
        print("-" * 96)
        
        for product, row in product_summary.head(20).iterrows():
            product_name = str(product)[:48] if pd.notna(product) else "Unknown"
            print(f"{product_name:<50} {int(row['Liquidate']):<12} {int(row['Sellable']):<12} {int(row['Total']):<10} {row['Liquidation_Rate']:<12.1f}%")
        
        # Products with high liquidation rates
        high_liq_products = product_summary[product_summary['Total'] >= 3]
        high_liq_products = high_liq_products[high_liq_products['Liquidation_Rate'] >= 50]
        
        if len(high_liq_products) > 0:
            print(f"\n\nProducts with High Liquidation Rate (≥50%, min 3 orders):")
            print(f"{'Product':<50} {'Liquidate':<12} {'Sellable':<12} {'Total':<10} {'Liq Rate':<12}")
            print("-" * 96)
            for product, row in high_liq_products.sort_values('Liquidation_Rate', ascending=False).iterrows():
                product_name = str(product)[:48] if pd.notna(product) else "Unknown"
                print(f"{product_name:<50} {int(row['Liquidate']):<12} {int(row['Sellable']):<12} {int(row['Total']):<10} {row['Liquidation_Rate']:<12.1f}%")
        
        return product_summary.to_dict('index')
    
    def suggest_additional_questions(self):
        """Suggest additional valuable questions"""
        print("\n" + "="*80)
        print("ADDITIONAL QUESTIONS TO CONSIDER")
        print("="*80)
        
        questions = [
            "8. What is the average time from 'Started On' to 'Completed On' for liquidated vs sellable items?",
            "9. Which specific check failures correlate most strongly with liquidation?",
            "10. Are there products that always liquidate regardless of checks passed?",
            "11. What percentage of high COGS items (>$2000) are being liquidated vs lower COGS items?",
            "12. Which liquidation reasons (Cosmetic, Fraud, Functional) have the highest average COGS?",
            "13. Are there patterns in the sequence of failed checks that lead to liquidation?",
            "14. What is the success rate of items that pass 'Does the item work?' check?",
            "15. How many items marked as 'Fraud' actually have high COGS that could be recovered?",
            "16. Which product categories have the highest total value lost to liquidation?",
            "17. Are there specific products that should be exempted from certain quality checks due to high COGS?",
            "18. What is the correlation between 'Scheduled Date' to 'Completed On' duration and liquidation rate?",
            "19. Which checks have the highest false positive rate (items that fail but could be sellable)?",
            "20. Are there geographic or time-based patterns in liquidations?",
            "21. What percentage of liquidated items had 'Is it Fraud?' check failed?",
            "22. How many liquidated items passed 'Does the item work?' but still got liquidated?",
            "23. What is the average number of failed checks for liquidated vs sellable items?",
            "24. Which products have inconsistent outcomes (some liquidate, some sellable) and why?",
            "25. What would be the potential recovery value if we relaxed criteria for high COGS items?"
        ]
        
        for i, question in enumerate(questions, 8):
            print(f"\n{question}")
        
        return questions
    
    def run_full_analysis(self):
        """Run complete analysis"""
        self.load_data()
        
        results = {
            'question_1': self.answer_question_1(),
            'question_2': self.answer_question_2(),
            'question_3': self.answer_question_3(),
            'question_4': self.answer_question_4(),
            'question_5': self.answer_question_5(),
            'question_6': self.answer_question_6(),
            'question_7': self.answer_question_7(),
            'additional_questions': self.suggest_additional_questions()
        }
        
        # Save results
        output_file = self.csv_file.replace('.csv', '_analysis_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n\nAnalysis complete! Results saved to: {output_file}")
        
        return results


def main():
    import sys
    
    csv_file = "Cost Greater than 1000/Repair Order (repair.order).csv"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if not Path(csv_file).exists():
        print(f"Error: File '{csv_file}' not found")
        return
    
    analyzer = ComprehensiveLiquidationAnalyzer(csv_file)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()

