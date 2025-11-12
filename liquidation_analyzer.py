#!/usr/bin/env python3
"""
BPMN Liquidation Analysis Tool
Analyzes quality check data to identify why items are being routed to Liquidation Palletizer
Focuses on high COGS items and identifies problematic decision points
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json
from pathlib import Path

class LiquidationAnalyzer:
    def __init__(self, bpmn_xml_file="bpmn.xml"):
        """Initialize analyzer with BPMN structure"""
        self.bpmn_file = bpmn_xml_file
        self.liquidation_paths = self._identify_liquidation_paths()
        self.decision_points = self._map_decision_points()
        
    def _identify_liquidation_paths(self):
        """Identify all paths that lead to Liquidation Palletizer"""
        # Based on BPMN analysis, these are the key paths to liquidation
        liquidation_paths = {
            'Empty Box': {
                'decision': 'Is there something in the box? QCP00025',
                'answer': 'No',
                'path': ['Print LPN label', 'Is it IOG?', 'Is there something in the box?', 'Send to Liquidation Palletizer']
            },
            'Non-Repairable (Path 1)': {
                'decision': 'Is the Item Repairable? QCP00033',
                'answer': 'No',
                'path': ['Does the Item Work', 'Is the Item Repairable?', 'Complete TREX Liquidation QCP00044']
            },
            'Fraud - Yes': {
                'decision': 'Is it Fraud? QCP00028',
                'answer': 'Yes',
                'path': ['Is it the Expected Item?', 'Is it Fraud?', 'Complete TREX Liquidation QCP00042']
            },
            'Fraud - No': {
                'decision': 'Is it Fraud? QCP00028',
                'answer': 'No',
                'path': ['Is it the Expected Item?', 'Is it Fraud?', 'Complete TREX Liquidation QCP00040']
            },
            'Needs Destruction': {
                'decision': 'Does the item Need to be Destroyed QCP00030',
                'answer': 'Yes',
                'path': ['Is the Item Factory Sealed?', 'Does the item Need to be Destroyed', 'Complete TREX Liquidation QCP00058']
            },
            'Scratches/Dents': {
                'decision': 'Does the item have scratches and dents larger than a badge? QCP00031',
                'answer': 'Yes',
                'path': ['Does the item Need to be Destroyed', 'Does the item have scratches and dents', 'Complete TREX Liquidation QCP00043']
            },
            'Non-Repairable (Path 2)': {
                'decision': 'Is the Item Repairable QCP00046',
                'answer': 'No',
                'path': ['Does the Item Work QCP00045', 'Is the Item Repairable', 'Complete TREX Liquidation QCP00049']
            }
        }
        return liquidation_paths
    
    def _map_decision_points(self):
        """Map decision points to their QCP codes"""
        decision_map = {
            'QCP00025': 'Is there something in the box?',
            'QCP00033': 'Is the Item Repairable?',
            'QCP00028': 'Is it Fraud?',
            'QCP00030': 'Does the item Need to be Destroyed',
            'QCP00031': 'Does the item have scratches and dents larger than a badge?',
            'QCP00046': 'Is the Item Repairable',
            'QCP00037': 'Does the Item Work',
            'QCP00026': 'Is it the Expected Item?',
            'QCP00029': 'Is the Item Factory Sealed?',
            'QCP00032': 'Did you do a Factory Reset?',
            'QCP00045': 'Does the Item Work',
            'QCP00024': 'Is it IOG?',
            'QCP00027': 'Are you using Harvested Parts?',
            'QCP00034': 'Does it need Parts?',
            'QCP00035': 'Does it Need a Manual?',
            'QCP00036': 'Does it need Manual?',
            'QCP00038': 'Do you have the parts?',
            'QCP00039': 'Does it need Sanitization',
            'QCP00051': 'Does it need Sanitization?',
            'QCP00056': 'Does it need Sanitization?',
            'QCP00070': 'Does it need a Manual?',
            'QCP00071': 'Does it Need a Manual?',
            'QCP00072': 'Does it Need a Manual?',
        }
        return decision_map
    
    def analyze_liquidation_reasons(self, data_file):
        """
        Analyze quality check data to identify liquidation reasons
        
        Expected data format (CSV or Excel):
        - product_id: Unique product identifier
        - cogs: Cost of goods sold
        - destination: 'Liquidation Palletizer' or 'Sellable Palletizer'
        - QCP00025: Answer to 'Is there something in the box?' (Yes/No)
        - QCP00033: Answer to 'Is the Item Repairable?' (Yes/No)
        - QCP00028: Answer to 'Is it Fraud?' (Yes/No)
        - QCP00030: Answer to 'Does the item Need to be Destroyed' (Yes/No)
        - QCP00031: Answer to 'Does the item have scratches and dents' (Yes/No)
        - QCP00046: Answer to 'Is the Item Repairable' (Yes/No)
        - ... (other QCP columns)
        """
        # Load data
        if data_file.endswith('.csv'):
            df = pd.read_csv(data_file)
        elif data_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data_file)
        else:
            raise ValueError("Data file must be CSV or Excel format")
        
        print("=" * 80)
        print("LIQUIDATION ANALYSIS REPORT")
        print("=" * 80)
        
        # Basic statistics
        total_items = len(df)
        liquidation_items = df[df['destination'] == 'Liquidation Palletizer']
        sellable_items = df[df['destination'] == 'Sellable Palletizer']
        
        print(f"\n1. OVERALL STATISTICS")
        print("-" * 80)
        print(f"Total Items: {total_items:,}")
        print(f"Liquidation Palletizer: {len(liquidation_items):,} ({len(liquidation_items)/total_items*100:.2f}%)")
        print(f"Sellable Palletizer: {len(sellable_items):,} ({len(sellable_items)/total_items*100:.2f}%)")
        
        # High COGS analysis
        high_cogs_threshold = 1000
        high_cogs_items = df[df['cogs'] >= high_cogs_threshold]
        high_cogs_liquidation = high_cogs_items[high_cogs_items['destination'] == 'Liquidation Palletizer']
        
        print(f"\n2. HIGH COGS ANALYSIS (COGS >= ${high_cogs_threshold})")
        print("-" * 80)
        print(f"High COGS Items: {len(high_cogs_items):,}")
        print(f"High COGS → Liquidation: {len(high_cogs_liquidation):,} ({len(high_cogs_liquidation)/len(high_cogs_items)*100:.2f}%)")
        print(f"High COGS → Sellable: {len(high_cogs_items) - len(high_cogs_liquidation):,}")
        
        if len(high_cogs_liquidation) > 0:
            print(f"\nAverage COGS of Liquidated High-Value Items: ${high_cogs_liquidation['cogs'].mean():.2f}")
            print(f"Total Value Lost: ${high_cogs_liquidation['cogs'].sum():,.2f}")
        
        # Analyze liquidation reasons
        print(f"\n3. LIQUIDATION REASON ANALYSIS")
        print("-" * 80)
        
        liquidation_reasons = self._identify_liquidation_reasons(liquidation_items)
        
        print("\nTop Reasons for Liquidation (All Items):")
        for reason, count in liquidation_reasons.items():
            percentage = (count / len(liquidation_items)) * 100
            print(f"  {reason}: {count:,} items ({percentage:.2f}%)")
        
        # High COGS liquidation reasons
        if len(high_cogs_liquidation) > 0:
            high_cogs_reasons = self._identify_liquidation_reasons(high_cogs_liquidation)
            print("\nTop Reasons for Liquidation (High COGS Items Only):")
            for reason, count in high_cogs_reasons.items():
                percentage = (count / len(high_cogs_liquidation)) * 100
                print(f"  {reason}: {count:,} items ({percentage:.2f}%)")
        
        # Decision point analysis
        print(f"\n4. DECISION POINT ANALYSIS")
        print("-" * 80)
        
        decision_analysis = self._analyze_decision_points(df, liquidation_items)
        
        print("\nDecision Points Contributing to Liquidation:")
        for qcp_code, stats in decision_analysis.items():
            print(f"\n  {qcp_code} - {self.decision_points.get(qcp_code, 'Unknown')}")
            print(f"    Liquidation when 'No': {stats['no_to_liquidation']:,} items")
            print(f"    Liquidation when 'Yes': {stats['yes_to_liquidation']:,} items")
            print(f"    Total impact: {stats['total_impact']:,} items")
        
        # Recommendations
        print(f"\n5. RECOMMENDATIONS")
        print("-" * 80)
        self._generate_recommendations(liquidation_reasons, high_cogs_reasons if len(high_cogs_liquidation) > 0 else {}, decision_analysis)
        
        return {
            'liquidation_reasons': liquidation_reasons,
            'high_cogs_reasons': high_cogs_reasons if len(high_cogs_liquidation) > 0 else {},
            'decision_analysis': decision_analysis,
            'summary': {
                'total_items': total_items,
                'liquidation_count': len(liquidation_items),
                'liquidation_percentage': len(liquidation_items)/total_items*100,
                'high_cogs_liquidation_count': len(high_cogs_liquidation),
                'high_cogs_liquidation_percentage': len(high_cogs_liquidation)/len(high_cogs_items)*100 if len(high_cogs_items) > 0 else 0,
                'total_value_lost': high_cogs_liquidation['cogs'].sum() if len(high_cogs_liquidation) > 0 else 0
            }
        }
    
    def _identify_liquidation_reasons(self, liquidation_df):
        """Identify primary reasons for liquidation based on QCP answers"""
        reasons = Counter()
        
        # Check each liquidation path
        if 'QCP00025' in liquidation_df.columns:
            empty_box = liquidation_df[liquidation_df['QCP00025'].str.upper() == 'NO']
            reasons['Empty Box (QCP00025)'] = len(empty_box)
        
        if 'QCP00033' in liquidation_df.columns:
            non_repairable_1 = liquidation_df[liquidation_df['QCP00033'].str.upper() == 'NO']
            reasons['Non-Repairable (QCP00033)'] = len(non_repairable_1)
        
        if 'QCP00028' in liquidation_df.columns:
            fraud_yes = liquidation_df[liquidation_df['QCP00028'].str.upper() == 'YES']
            fraud_no = liquidation_df[liquidation_df['QCP00028'].str.upper() == 'NO']
            reasons['Fraud - Yes (QCP00028)'] = len(fraud_yes)
            reasons['Fraud - No (QCP00028)'] = len(fraud_no)
        
        if 'QCP00030' in liquidation_df.columns:
            needs_destruction = liquidation_df[liquidation_df['QCP00030'].str.upper() == 'YES']
            reasons['Needs Destruction (QCP00030)'] = len(needs_destruction)
        
        if 'QCP00031' in liquidation_df.columns:
            scratches_dents = liquidation_df[liquidation_df['QCP00031'].str.upper() == 'YES']
            reasons['Scratches/Dents (QCP00031)'] = len(scratches_dents)
        
        if 'QCP00046' in liquidation_df.columns:
            non_repairable_2 = liquidation_df[liquidation_df['QCP00046'].str.upper() == 'NO']
            reasons['Non-Repairable (QCP00046)'] = len(non_repairable_2)
        
        return reasons
    
    def _analyze_decision_points(self, full_df, liquidation_df):
        """Analyze how each decision point affects liquidation"""
        decision_analysis = {}
        
        qcp_codes = ['QCP00025', 'QCP00033', 'QCP00028', 'QCP00030', 'QCP00031', 'QCP00046', 
                     'QCP00037', 'QCP00026', 'QCP00029', 'QCP00032', 'QCP00045']
        
        for qcp in qcp_codes:
            if qcp not in full_df.columns:
                continue
            
            # Count how many "No" answers lead to liquidation
            no_answers = full_df[full_df[qcp].str.upper() == 'NO']
            no_to_liquidation = len(no_answers[no_answers['destination'] == 'Liquidation Palletizer'])
            
            # Count how many "Yes" answers lead to liquidation
            yes_answers = full_df[full_df[qcp].str.upper() == 'YES']
            yes_to_liquidation = len(yes_answers[yes_answers['destination'] == 'Liquidation Palletizer'])
            
            decision_analysis[qcp] = {
                'no_to_liquidation': no_to_liquidation,
                'yes_to_liquidation': yes_to_liquidation,
                'total_impact': no_to_liquidation + yes_to_liquidation
            }
        
        return decision_analysis
    
    def _generate_recommendations(self, liquidation_reasons, high_cogs_reasons, decision_analysis):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for high liquidation rate
        if len(liquidation_reasons) > 0:
            top_reason = max(liquidation_reasons.items(), key=lambda x: x[1])
            recommendations.append(f"1. PRIMARY ISSUE: '{top_reason[0]}' is causing {top_reason[1]:,} liquidations")
            recommendations.append(f"   → Review quality check criteria for this decision point")
            recommendations.append(f"   → Consider if thresholds are too strict")
        
        # High COGS specific recommendations
        if len(high_cogs_reasons) > 0:
            top_high_cogs_reason = max(high_cogs_reasons.items(), key=lambda x: x[1])
            recommendations.append(f"\n2. HIGH COGS ISSUE: '{top_high_cogs_reason[0]}' is liquidating high-value items")
            recommendations.append(f"   → Implement exception handling for high COGS items")
            recommendations.append(f"   → Consider manual review for items above $1000 COGS")
            recommendations.append(f"   → Review if quality standards should be relaxed for high-value items")
        
        # Decision point recommendations
        if decision_analysis:
            high_impact_decisions = sorted(decision_analysis.items(), 
                                         key=lambda x: x[1]['total_impact'], 
                                         reverse=True)[:3]
            
            recommendations.append(f"\n3. TOP DECISION POINTS TO REVIEW:")
            for qcp, stats in high_impact_decisions:
                decision_name = self.decision_points.get(qcp, 'Unknown')
                recommendations.append(f"   → {qcp} ({decision_name}): {stats['total_impact']:,} liquidations")
                recommendations.append(f"     - 'No' → Liquidation: {stats['no_to_liquidation']:,}")
                recommendations.append(f"     - 'Yes' → Liquidation: {stats['yes_to_liquidation']:,}")
        
        recommendations.append(f"\n4. GENERAL RECOMMENDATIONS:")
        recommendations.append(f"   → Implement COGS-based routing rules (e.g., manual review for COGS > $1000)")
        recommendations.append(f"   → Add 'Exception Review' path for high-value items before liquidation")
        recommendations.append(f"   → Track and analyze false positives (items that could be sellable)")
        recommendations.append(f"   → Consider A/B testing with relaxed criteria for specific decision points")
        
        for rec in recommendations:
            print(rec)
    
    def create_sample_data_template(self, output_file="sample_quality_data.csv"):
        """Create a sample data template for analysis"""
        sample_data = {
            'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD004', 'PROD005'],
            'cogs': [1500, 500, 1200, 300, 2000],
            'destination': ['Liquidation Palletizer', 'Sellable Palletizer', 'Liquidation Palletizer', 'Sellable Palletizer', 'Liquidation Palletizer'],
            'QCP00024': ['No', 'No', 'No', 'No', 'No'],  # Is it IOG?
            'QCP00025': ['Yes', 'Yes', 'No', 'Yes', 'Yes'],  # Is there something in the box?
            'QCP00026': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],  # Is it the Expected Item?
            'QCP00028': ['No', 'No', 'Yes', 'No', 'No'],  # Is it Fraud?
            'QCP00029': ['No', 'Yes', 'No', 'Yes', 'No'],  # Is the Item Factory Sealed?
            'QCP00030': ['No', 'No', 'No', 'No', 'Yes'],  # Does the item Need to be Destroyed
            'QCP00031': ['Yes', 'No', 'No', 'No', 'No'],  # Scratches and dents
            'QCP00032': ['No', 'Yes', 'No', 'Yes', 'No'],  # Did you do a Factory Reset?
            'QCP00033': ['No', 'Yes', 'No', 'Yes', 'No'],  # Is the Item Repairable?
            'QCP00037': ['No', 'Yes', 'No', 'Yes', 'No'],  # Does the Item Work
            'QCP00045': ['No', 'Yes', 'No', 'Yes', 'No'],  # Does the Item Work
            'QCP00046': ['No', 'Yes', 'No', 'Yes', 'No'],  # Is the Item Repairable
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_file, index=False)
        print(f"Sample data template created: {output_file}")
        print("\nExpected columns:")
        print("  - product_id: Unique product identifier")
        print("  - cogs: Cost of goods sold")
        print("  - destination: 'Liquidation Palletizer' or 'Sellable Palletizer'")
        print("  - QCP00024 through QCP00046: Quality check answers (Yes/No)")
        return output_file


def main():
    import sys
    
    analyzer = LiquidationAnalyzer()
    
    if len(sys.argv) < 2:
        print("Usage: python liquidation_analyzer.py <data_file.csv>")
        print("\nCreating sample data template...")
        analyzer.create_sample_data_template()
        print("\nPlease provide your quality check data file (CSV or Excel)")
        print("The file should contain columns: product_id, cogs, destination, and QCP codes")
        return
    
    data_file = sys.argv[1]
    
    if not Path(data_file).exists():
        print(f"Error: File '{data_file}' not found")
        print("\nCreating sample data template...")
        analyzer.create_sample_data_template()
        return
    
    try:
        results = analyzer.analyze_liquidation_reasons(data_file)
        
        # Save results to JSON
        output_file = data_file.replace('.csv', '_analysis.json').replace('.xlsx', '_analysis.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n\nAnalysis results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


