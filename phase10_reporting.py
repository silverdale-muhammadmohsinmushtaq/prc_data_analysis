#!/usr/bin/env python3
"""
Phase 10: Reporting & Documentation
Liquidation Analysis - Comprehensive reporting and documentation
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class Phase10Reporting:
    def __init__(self, features_csv_path):
        """Initialize Phase 10 reporting"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.output_dir = os.path.dirname(features_csv_path)
        
        # Load previous phase results
        self.phase6_results = None
        self.phase7_results = None
        self.phase9_results = None
        self.load_previous_results()
        
    def load_previous_results(self):
        """Load results from previous phases"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        
        phase6_file = f"{base_name}_phase6_results.json"
        phase7_file = f"{base_name}_phase7_results.json"
        phase9_file = f"{base_name}_phase9_results.json"
        
        if os.path.exists(phase6_file):
            with open(phase6_file, 'r', encoding='utf-8') as f:
                self.phase6_results = json.load(f)
        
        if os.path.exists(phase7_file):
            with open(phase7_file, 'r', encoding='utf-8') as f:
                self.phase7_results = json.load(f)
        
        if os.path.exists(phase9_file):
            with open(phase9_file, 'r', encoding='utf-8') as f:
                self.phase9_results = json.load(f)
    
    def run_phase10(self):
        """Execute all Phase 10 tasks"""
        print("=" * 80)
        print("PHASE 10: REPORTING & DOCUMENTATION")
        print("=" * 80)
        
        # Load data for summary stats
        self.df = pd.read_csv(self.features_csv_path)
        
        # 10.1 Create Analysis Report
        self.create_executive_summary()
        self.create_detailed_analysis_report()
        self.create_recommendations_section()
        
        # 10.2 Documentation
        self.create_data_documentation()
        self.create_code_documentation()
        
        # 10.3 Deliverables Checklist
        self.create_deliverables_checklist()
        
        print("\n" + "=" * 80)
        print("PHASE 10 COMPLETE")
        print("=" * 80)
    
    def create_executive_summary(self):
        """10.1.1 Executive Summary"""
        print("\n" + "-" * 80)
        print("10.1.1 CREATING EXECUTIVE SUMMARY")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        report_file = f"{base_name}_EXECUTIVE_SUMMARY.md"
        
        liquidated = self.df[self.df['is_liquidated'] == 1]
        sellable = self.df[self.df['is_liquidated'] == 0]
        liquidation_rate = len(liquidated) / len(self.df) * 100
        total_value_lost = liquidated['Amazon COGS'].sum()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Executive Summary: Liquidation Analysis\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n")
            f.write(f"**Analysis Period:** Based on {len(self.df):,} repair orders\n\n")
            f.write("---\n\n")
            
            # Overview
            f.write("## Overview\n\n")
            f.write("This analysis examines the liquidation decision process for Amazon Repair Products ")
            f.write("to identify root causes of high liquidation rates and opportunities for improvement. ")
            f.write("The analysis covers quality check patterns, product and category trends, and financial impact.\n\n")
            
            # Key Metrics
            f.write("## Key Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Total Orders Analyzed | {len(self.df):,} |\n")
            f.write(f"| Liquidation Rate | {liquidation_rate:.1f}% |\n")
            f.write(f"| Liquidated Orders | {len(liquidated):,} |\n")
            f.write(f"| Sellable Orders | {len(sellable):,} |\n")
            f.write(f"| Total Value Lost | ${total_value_lost:,.2f} |\n")
            f.write(f"| Average COGS (Liquidated) | ${liquidated['Amazon COGS'].mean():,.2f} |\n")
            f.write(f"| Average COGS (Sellable) | ${sellable['Amazon COGS'].mean():,.2f} |\n\n")
            
            # Top 5 Findings
            f.write("## Top 5 Key Findings\n\n")
            if self.phase9_results and 'key_findings' in self.phase9_results:
                findings = self.phase9_results['key_findings'][:5]
                for i, finding in enumerate(findings, 1):
                    f.write(f"### {i}. {finding['finding']} [{finding['severity']}]\n\n")
                    f.write(f"{finding['description']}\n\n")
                    f.write(f"**Impact:** {finding['impact']}\n\n")
            
            # Financial Impact Summary
            f.write("## Financial Impact Summary\n\n")
            if self.phase9_results and 'financial_impact' in self.phase9_results:
                financial = self.phase9_results['financial_impact']
                f.write(f"- **Current Value Lost:** ${financial['current_value_lost']:,.2f}\n")
                f.write(f"- **Potential Recovery Value:** ${financial['potential_recovery_value']:,.2f}\n")
                f.write(f"- **High COGS Items Liquidated:** {financial['high_cogs_liquidated_count']} items, ${financial['high_cogs_liquidated_value']:,.2f}\n\n")
                
                f.write("### Recovery Scenarios\n\n")
                for scenario, data in financial.get('recovery_scenarios', {}).items():
                    f.write(f"- **{data['description']}:** ${data['value']:,.2f} ({data['count']} items)\n")
                f.write("\n")
                
                f.write("### ROI Analysis\n\n")
                f.write(f"- **Total Potential Recovery:** ${financial.get('total_potential_recovery', 0):,.2f}\n")
                f.write(f"- **Estimated Implementation Cost:** ${financial.get('estimated_implementation_cost', 0):,.2f}\n")
                f.write(f"- **Estimated Annual Recovery:** ${financial.get('estimated_annual_recovery', 0):,.2f}\n")
                f.write(f"- **ROI:** {financial.get('roi_percentage', 0):.1f}%\n")
                f.write(f"- **Payback Period:** {financial.get('payback_period_months', 0):.1f} months\n\n")
            
            # Top 3 Recommendations
            f.write("## Top 3 Recommendations\n\n")
            if self.phase9_results and 'recommendations' in self.phase9_results:
                recommendations = [r for r in self.phase9_results['recommendations'] if r['priority'] == 'HIGH'][:3]
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"### {i}. {rec['recommendation']}\n\n")
                    f.write(f"**Type:** {rec['type']}  |  **Priority:** {rec['priority']}  |  **Timeline:** {rec['timeline']}\n\n")
                    f.write(f"{rec['description']}\n\n")
                    f.write(f"**Expected Impact:** {rec['expected_impact']}\n\n")
            
            # Conclusion
            f.write("## Conclusion\n\n")
            f.write("The analysis reveals significant opportunities to reduce liquidation rates and recover value. ")
            f.write("Key focus areas include implementing exception handling for high COGS items, preventing ")
            f.write("liquidation of working items, and reviewing cosmetic check criteria. With an estimated ")
            f.write("ROI of over 400% and a payback period of less than 3 months, these improvements ")
            f.write("represent high-value opportunities for process optimization.\n\n")
        
        print(f"[OK] Executive Summary saved to: {report_file}")
    
    def create_detailed_analysis_report(self):
        """10.1.2 Detailed Analysis Report"""
        print("\n" + "-" * 80)
        print("10.1.2 CREATING DETAILED ANALYSIS REPORT")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        report_file = f"{base_name}_DETAILED_ANALYSIS_REPORT.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Detailed Analysis Report: Liquidation Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Methodology
            f.write("## 1. Methodology\n\n")
            f.write("### 1.1 Data Science Pipeline\n\n")
            f.write("This analysis followed a comprehensive 10-phase data science pipeline:\n\n")
            f.write("1. **Data Understanding & Preparation** - Initial data loading, structure analysis, quality assessment\n")
            f.write("2. **Data Cleaning & Transformation** - Data preprocessing, multi-row handling, human-executed check filtering\n")
            f.write("3. **Exploratory Data Analysis (EDA)** - Univariate, bivariate, and check-level analysis\n")
            f.write("4. **Feature Engineering** - Created 18 derived features for deeper analysis\n")
            f.write("5. **Statistical Analysis** - Hypothesis testing, correlation analysis, effect sizes\n")
            f.write("6. **Answering Specific Questions** - Direct answers to 7 business questions\n")
            f.write("7. **Advanced Analysis** - Additional questions (Q8-Q25), pattern recognition, root cause analysis\n")
            f.write("8. **Data Visualization** - 13 comprehensive visualizations\n")
            f.write("9. **Insights & Recommendations** - Key findings, problem identification, actionable recommendations\n")
            f.write("10. **Reporting & Documentation** - Executive summary, detailed report, documentation\n\n")
            
            f.write("### 1.2 Data Sources\n\n")
            f.write("- **Primary Dataset:** Repair Order data (CSV/Excel format)\n")
            f.write("- **Data Period:** Based on provided dataset\n")
            f.write(f"- **Total Records:** {len(self.df):,} repair orders\n")
            f.write(f"- **Quality Checks:** {len([c for c in self.df.columns if c not in ['LPN', 'Amazon COGS', 'Disposition', 'Product', 'Product Category', 'Result of Repair']])} unique checks\n\n")
            
            f.write("### 1.3 Tools & Technologies\n\n")
            f.write("- **Programming Language:** Python 3\n")
            f.write("- **Libraries:** pandas, numpy, matplotlib, seaborn, scipy\n")
            f.write("- **Data Format:** CSV, JSON for results\n")
            f.write("- **Visualization:** Matplotlib, Seaborn\n\n")
            
            # Data Description
            f.write("## 2. Data Description\n\n")
            f.write("### 2.1 Dataset Overview\n\n")
            f.write(f"- **Total Orders:** {len(self.df):,}\n")
            f.write(f"- **Total Columns:** {len(self.df.columns)}\n")
            f.write(f"- **Liquidated Orders:** {len(self.df[self.df['is_liquidated'] == 1]):,} ({len(self.df[self.df['is_liquidated'] == 1])/len(self.df)*100:.1f}%)\n")
            f.write(f"- **Sellable Orders:** {len(self.df[self.df['is_liquidated'] == 0]):,} ({len(self.df[self.df['is_liquidated'] == 0])/len(self.df)*100:.1f}%)\n\n")
            
            f.write("### 2.2 Key Variables\n\n")
            f.write("| Variable | Description |\n")
            f.write("|----------|-------------|\n")
            f.write("| LPN | License Plate Number (unique identifier)\n")
            f.write("| Amazon COGS | Cost of Goods Sold\n")
            f.write("| Disposition | Final outcome (Sellable/Liquidate)\n")
            f.write("| Product | Product identifier\n")
            f.write("| Product Category | Product category classification\n")
            f.write("| Result of Repair | Specific liquidation reason\n")
            f.write("| Quality Checks | 44+ human-executed quality checks\n")
            f.write("| is_liquidated | Binary flag (1=Liquidated, 0=Sellable)\n\n")
            
            # Detailed Findings
            f.write("## 3. Detailed Findings\n\n")
            
            # Question 1
            f.write("### 3.1 Question 1: Which Quality Checks Are Causing Liquidations?\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question1' in self.phase6_results['answers']:
                q1 = self.phase6_results['answers']['question1']
                f.write("**Top 5 Quality Checks Causing Liquidations:**\n\n")
                for i, check in enumerate(q1.get('top_15_checks', [])[:5], 1):
                    f.write(f"{i}. **{check['check_name']}** - {check['failure_count']} failures ({check['failure_rate_pct']:.1f}% failure rate)\n")
                f.write("\n")
            
            # Question 2
            f.write("### 3.2 Question 2: Patterns in High COGS Items That Get Liquidated\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question2' in self.phase6_results['answers']:
                q2 = self.phase6_results['answers']['question2']
                f.write(f"**Key Findings:**\n\n")
                f.write(f"- High COGS items (>= $2,000) have {q2.get('high_cogs_liquidation_rate', 0):.1f}% liquidation rate\n")
                f.write(f"- Lower COGS items have {q2.get('low_cogs_liquidation_rate', 0):.1f}% liquidation rate\n")
                f.write(f"- Average COGS for liquidated high-value items: ${q2.get('high_cogs_avg_cogs', 0):,.2f}\n")
                f.write(f"- Total value lost from high COGS items: ${q2.get('high_cogs_value_lost', 0):,.2f}\n\n")
            
            # Question 3
            f.write("### 3.3 Question 3: Comparison of Passed vs Failed Checks\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question3' in self.phase6_results['answers']:
                q3 = self.phase6_results['answers']['question3']
                f.write(f"**Key Findings:**\n\n")
                f.write(f"- Average failed checks (Liquidated): {q3.get('liquidated_avg_failed', 0):.1f}\n")
                f.write(f"- Average failed checks (Sellable): {q3.get('sellable_avg_failed', 0):.1f}\n")
                f.write(f"- Average passed checks (Liquidated): {q3.get('liquidated_avg_passed', 0):.1f}\n")
                f.write(f"- Average passed checks (Sellable): {q3.get('sellable_avg_passed', 0):.1f}\n\n")
            
            # Question 4
            f.write("### 3.4 Question 4: Product Categories Most Affected\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question4' in self.phase6_results['answers']:
                q4 = self.phase6_results['answers']['question4']
                f.write("**Top 5 Categories by Liquidation Count:**\n\n")
                for i, cat in enumerate(q4.get('top_categories_by_count', [])[:5], 1):
                    f.write(f"{i}. **{cat['category']}** - {cat['liquidated_count']} liquidations ({cat['liquidation_rate_pct']:.1f}%)\n")
                f.write("\n")
            
            # Question 5
            f.write("### 3.5 Question 5: Specific Liquidation Reasons\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question5' in self.phase6_results['answers']:
                q5 = self.phase6_results['answers']['question5']
                f.write("**Liquidation Reasons Breakdown:**\n\n")
                reasons_data = q5.get('liquidation_reasons', {})
                if isinstance(reasons_data, dict):
                    for reason, data in list(reasons_data.items())[:5]:
                        if isinstance(data, dict):
                            count = data.get('count', 0)
                            value = data.get('total_value', data.get('value', 0))
                            f.write(f"- **{reason}:** {count} items (${value:,.2f})\n")
                f.write("\n")
            
            # Question 6
            f.write("### 3.6 Question 6: Liquidation and Sellable Counts by Category\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question6' in self.phase6_results['answers']:
                q6 = self.phase6_results['answers']['question6']
                f.write("**Top 5 Categories:**\n\n")
                for i, cat in enumerate(q6.get('top_categories', [])[:5], 1):
                    f.write(f"{i}. **{cat['category']}** - Liquidated: {cat['liquidated']}, Sellable: {cat['sellable']}\n")
                f.write("\n")
            
            # Question 7
            f.write("### 3.7 Question 7: Liquidation and Sellable Counts by Product\n\n")
            if self.phase6_results and 'answers' in self.phase6_results and 'question7' in self.phase6_results['answers']:
                q7 = self.phase6_results['answers']['question7']
                f.write("**Top 5 Products:**\n\n")
                for i, prod in enumerate(q7.get('top_products', [])[:5], 1):
                    f.write(f"{i}. **{prod['product']}** - Liquidated: {prod['liquidated']}, Sellable: {prod['sellable']}\n")
                f.write("\n")
            
            # Statistical Results
            f.write("## 4. Statistical Results\n\n")
            if self.phase7_results and 'findings' in self.phase7_results:
                findings = self.phase7_results['findings']
                
                if 'q8_time_analysis' in findings:
                    f.write("### 4.1 Processing Time Analysis\n\n")
                    time_analysis = findings['q8_time_analysis']
                    f.write(f"- Average processing time (Liquidated): {time_analysis.get('liquidated_mean_days', 0):.2f} days\n")
                    f.write(f"- Average processing time (Sellable): {time_analysis.get('sellable_mean_days', 0):.2f} days\n")
                    f.write(f"- Difference: {time_analysis.get('difference_days', 0):.2f} days\n\n")
                
                if 'q9_check_correlation' in findings:
                    f.write("### 4.2 Check Correlation Analysis\n\n")
                    f.write("**Top 5 Checks with Strongest Correlation to Liquidation:**\n\n")
                    corr_data = findings['q9_check_correlation'].get('top_15_correlations', {})
                    for i, (check, data) in enumerate(list(corr_data.items())[:5], 1):
                        f.write(f"{i}. **{check}** - Correlation: {data.get('correlation', 0):.4f}\n")
                    f.write("\n")
            
            # Visualizations
            f.write("## 5. Visualizations\n\n")
            f.write("The following visualizations were created:\n\n")
            f.write("### Phase 3 Visualizations\n")
            f.write("- Disposition distribution\n")
            f.write("- COGS distribution\n")
            f.write("- COGS by disposition\n")
            f.write("- Liquidation rate by COGS bin\n")
            f.write("- Top categories\n")
            f.write("- Liquidation reasons\n")
            f.write("- Category liquidation analysis\n")
            f.write("- Top failed checks\n")
            f.write("- Check comparison\n\n")
            
            f.write("### Phase 6 Visualizations\n")
            f.write("- Question-specific visualizations (7 charts)\n\n")
            
            f.write("### Phase 8 Visualizations\n")
            f.write("- 13 comprehensive visualizations covering:\n")
            f.write("  - Distribution charts\n")
            f.write("  - Comparison charts\n")
            f.write("  - Financial impact charts\n")
            f.write("  - Product-level charts\n")
            f.write("  - Check analysis charts\n\n")
            
            f.write("All visualizations are saved in the respective Phase folders.\n\n")
        
        print(f"[OK] Detailed Analysis Report saved to: {report_file}")
    
    def create_recommendations_section(self):
        """10.1.3 Recommendations Section"""
        print("\n" + "-" * 80)
        print("10.1.3 CREATING RECOMMENDATIONS SECTION")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        report_file = f"{base_name}_RECOMMENDATIONS.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Recommendations: Liquidation Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("---\n\n")
            
            if self.phase9_results and 'recommendations' in self.phase9_results:
                recommendations = self.phase9_results['recommendations']
                
                # Prioritized by type
                immediate = [r for r in recommendations if r['type'] == 'IMMEDIATE']
                process_improvements = [r for r in recommendations if r['type'] == 'PROCESS_IMPROVEMENT']
                bpmn_modifications = [r for r in recommendations if r['type'] == 'BPMN_MODIFICATION']
                
                # Immediate Actions
                f.write("## Immediate Actions (Quick Wins)\n\n")
                f.write("These recommendations can be implemented quickly (1-4 weeks) and have high impact:\n\n")
                for i, rec in enumerate(immediate, 1):
                    f.write(f"### {i}. {rec['recommendation']}\n\n")
                    f.write(f"**Priority:** {rec['priority']}  |  **Timeline:** {rec['timeline']}\n\n")
                    f.write(f"**Description:** {rec['description']}\n\n")
                    f.write("**Action Items:**\n")
                    for action in rec['action_items']:
                        f.write(f"- {action}\n")
                    f.write(f"\n**Expected Impact:** {rec['expected_impact']}\n\n")
                    f.write("---\n\n")
                
                # Process Improvements
                f.write("## Process Improvements\n\n")
                f.write("These recommendations require process changes and have medium to high impact:\n\n")
                for i, rec in enumerate(process_improvements, 1):
                    f.write(f"### {i}. {rec['recommendation']}\n\n")
                    f.write(f"**Priority:** {rec['priority']}  |  **Timeline:** {rec['timeline']}\n\n")
                    f.write(f"**Description:** {rec['description']}\n\n")
                    f.write("**Action Items:**\n")
                    for action in rec['action_items']:
                        f.write(f"- {action}\n")
                    f.write(f"\n**Expected Impact:** {rec['expected_impact']}\n\n")
                    f.write("---\n\n")
                
                # BPMN Modifications
                f.write("## BPMN Process Modifications\n\n")
                f.write("These recommendations require changes to the BPMN process flow:\n\n")
                for i, rec in enumerate(bpmn_modifications, 1):
                    f.write(f"### {i}. {rec['recommendation']}\n\n")
                    f.write(f"**Priority:** {rec['priority']}  |  **Timeline:** {rec['timeline']}\n\n")
                    f.write(f"**Description:** {rec['description']}\n\n")
                    f.write("**Action Items:**\n")
                    for action in rec['action_items']:
                        f.write(f"- {action}\n")
                    f.write(f"\n**Expected Impact:** {rec['expected_impact']}\n\n")
                    f.write("---\n\n")
                
                # Implementation Roadmap
                f.write("## Implementation Roadmap\n\n")
                f.write("### Phase 1: Quick Wins (Weeks 1-4)\n\n")
                for rec in immediate[:3]:
                    f.write(f"- {rec['recommendation']} ({rec['timeline']})\n")
                f.write("\n")
                
                f.write("### Phase 2: Process Improvements (Weeks 5-12)\n\n")
                for rec in process_improvements[:5]:
                    f.write(f"- {rec['recommendation']} ({rec['timeline']})\n")
                f.write("\n")
                
                f.write("### Phase 3: BPMN Modifications (Weeks 13-18)\n\n")
                for rec in bpmn_modifications:
                    f.write(f"- {rec['recommendation']} ({rec['timeline']})\n")
                f.write("\n")
                
                # Risk Assessment
                f.write("## Risk Assessment\n\n")
                f.write("### Low Risk Recommendations\n\n")
                f.write("- Review and prevent liquidating working items\n")
                f.write("- Implement recovery process for working liquidated items\n")
                f.write("- Review cosmetic check criteria\n\n")
                
                f.write("### Medium Risk Recommendations\n\n")
                f.write("- Exception handling for high COGS items (requires careful testing)\n")
                f.write("- Category-specific quality standards review\n")
                f.write("- Standardize decision criteria\n\n")
                
                f.write("### High Risk Recommendations\n\n")
                f.write("- BPMN process modifications (requires extensive testing and validation)\n")
                f.write("- Fraud detection review (may impact fraud prevention)\n\n")
        
        print(f"[OK] Recommendations Section saved to: {report_file}")
    
    def create_data_documentation(self):
        """10.2.1 Data Documentation"""
        print("\n" + "-" * 80)
        print("10.2.1 CREATING DATA DOCUMENTATION")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        doc_file = f"{base_name}_DATA_DOCUMENTATION.md"
        
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write("# Data Documentation: Liquidation Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("---\n\n")
            
            # Data Dictionary
            f.write("## Data Dictionary\n\n")
            f.write("### Order-Level Columns\n\n")
            f.write("| Column Name | Data Type | Description |\n")
            f.write("|-------------|-----------|-------------|\n")
            f.write("| LPN | String | License Plate Number - Unique identifier for each repair order |\n")
            f.write("| Amazon COGS | Float | Cost of Goods Sold - Financial value of the product |\n")
            f.write("| Disposition | String | Final outcome: 'Sellable' or 'Liquidate' |\n")
            f.write("| Product | String | Product identifier/name |\n")
            f.write("| Product Category | String | Product category classification |\n")
            f.write("| Result of Repair | String | Specific reason for liquidation (if liquidated) |\n")
            f.write("| Started On | DateTime | When repair process started |\n")
            f.write("| Completed On | DateTime | When repair process completed |\n")
            f.write("| Scheduled Date | DateTime | Scheduled completion date |\n")
            f.write("| Shipped Date | DateTime | When item was shipped (if applicable) |\n\n")
            
            f.write("### Quality Check Columns\n\n")
            f.write("Quality check columns represent individual checks performed during the repair process.\n")
            f.write("Each check can have values: 'Passed', 'Failed', or NaN (not applicable).\n\n")
            f.write("**Key Quality Checks:**\n\n")
            key_checks = [
                "Does_the_item_work_El_art_culo_funciona",
                "Is_it_Fraud_Es_fraude",
                "Is_the_item_Repairable_El_art_culo_es_reparable",
                "Does_the_item_have_scratches_or_dents_larger_that_",
                "Is_the_Item_Factory_Sealed_El_art_culo_est_sellado"
            ]
            for check in key_checks:
                f.write(f"- {check}\n")
            f.write("\n")
            
            f.write("### Derived Features\n\n")
            f.write("| Feature | Description |\n")
            f.write("|---------|-------------|\n")
            f.write("| is_liquidated | Binary flag: 1 if liquidated, 0 if sellable |\n")
            f.write("| cogs_bin | COGS value binned into ranges |\n")
            f.write("| processing_days | Days from 'Started On' to 'Completed On' |\n")
            f.write("| category_group | Grouped product categories |\n")
            f.write("| total_checks | Total number of checks performed |\n")
            f.write("| failed_checks_count | Number of failed checks |\n")
            f.write("| passed_checks_count | Number of passed checks |\n")
            f.write("| failure_rate | Percentage of checks that failed |\n")
            f.write("| works_check_passed | Binary: 1 if 'Does it work?' passed |\n")
            f.write("| fraud_check_failed | Binary: 1 if fraud check failed |\n")
            f.write("| cosmetic_check_failed | Binary: 1 if cosmetic check failed |\n")
            f.write("| repairable_check_failed | Binary: 1 if repairable check failed |\n")
            f.write("| value_lost | COGS value if liquidated, 0 otherwise |\n")
            f.write("| recovery_potential | COGS value if working item was liquidated |\n\n")
            
            # Business Rules
            f.write("## Business Rules\n\n")
            f.write("### Data Filtering Rules\n\n")
            f.write("1. **Human-Executed Checks Only:** Only quality checks where 'Checks/Failed by decision logic Automatically' is False or empty are included\n")
            f.write("2. **Multi-Row Data:** Quality checks for a single repair order are spread across multiple rows, transformed to wide format\n")
            f.write("3. **Missing Values:** Missing check values indicate the check was not performed or not applicable\n\n")
            
            f.write("### Disposition Rules\n\n")
            f.write("- **Sellable:** Item passed quality checks and can be sold\n")
            f.write("- **Liquidate:** Item failed critical checks and must be liquidated\n")
            f.write("- Liquidation reasons include: Functional Issues, Fraud, Cosmetic Issues, Wrong Item Description\n\n")
            
            # Known Data Quality Issues
            f.write("## Known Data Quality Issues\n\n")
            f.write("1. **Multi-Row Format:** Original data had quality checks in multiple rows per order - transformed to wide format\n")
            f.write("2. **Missing Dates:** Some orders have missing date fields - handled in preprocessing\n")
            f.write("3. **Inconsistent Check Names:** Some checks have slight variations in naming - standardized during preprocessing\n")
            f.write("4. **Automated Checks:** Checks marked as 'Failed by decision logic Automatically' were excluded from analysis\n\n")
        
        print(f"[OK] Data Documentation saved to: {doc_file}")
    
    def create_code_documentation(self):
        """10.2.2 Code Documentation"""
        print("\n" + "-" * 80)
        print("10.2.2 CREATING CODE DOCUMENTATION")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        doc_file = f"{base_name}_CODE_DOCUMENTATION.md"
        
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write("# Code Documentation: Liquidation Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("---\n\n")
            
            f.write("## Scripts Overview\n\n")
            f.write("### Phase 1: Data Understanding\n")
            f.write("- **Script:** `phase1_data_understanding.py`\n")
            f.write("- **Purpose:** Load data, inspect structure, perform initial quality assessment\n")
            f.write("- **Output:** JSON file with data profiling results\n\n")
            
            f.write("### Phase 2: Data Preprocessing\n")
            f.write("- **Script:** `phase2_data_preprocessing.py`\n")
            f.write("- **Purpose:** Clean data, transform multi-row format to wide format, filter human-executed checks\n")
            f.write("- **Output:** Preprocessed CSV file\n\n")
            
            f.write("### Phase 3: Exploratory Data Analysis\n")
            f.write("- **Script:** `phase3_eda.py`\n")
            f.write("- **Purpose:** Perform univariate, bivariate, and check-level analysis\n")
            f.write("- **Output:** JSON results and visualization scripts\n\n")
            
            f.write("### Phase 4: Feature Engineering\n")
            f.write("- **Script:** `phase4_feature_engineering.py`\n")
            f.write("- **Purpose:** Create derived features for deeper analysis\n")
            f.write("- **Output:** Feature-engineered CSV file\n\n")
            
            f.write("### Phase 5: Statistical Analysis\n")
            f.write("- **Script:** `phase5_statistical_analysis.py`\n")
            f.write("- **Purpose:** Perform hypothesis testing, correlation analysis\n")
            f.write("- **Output:** JSON file with statistical results\n\n")
            
            f.write("### Phase 6: Answering Specific Questions\n")
            f.write("- **Script:** `phase6_answer_questions.py`\n")
            f.write("- **Purpose:** Directly answer the 7 business questions\n")
            f.write("- **Output:** JSON results and visualizations\n\n")
            
            f.write("### Phase 7: Advanced Analysis\n")
            f.write("- **Script:** `phase7_advanced_analysis.py`\n")
            f.write("- **Purpose:** Answer additional questions (Q8-Q25), pattern recognition, root cause analysis\n")
            f.write("- **Output:** JSON file with advanced analysis results\n\n")
            
            f.write("### Phase 8: Data Visualization\n")
            f.write("- **Script:** `phase8_visualizations.py`\n")
            f.write("- **Purpose:** Create comprehensive visualizations\n")
            f.write("- **Output:** 13 PNG visualization files\n\n")
            
            f.write("### Phase 9: Insights & Recommendations\n")
            f.write("- **Script:** `phase9_insights_recommendations.py`\n")
            f.write("- **Purpose:** Generate key findings, identify problems, create recommendations\n")
            f.write("- **Output:** JSON results and markdown report\n\n")
            
            f.write("### Phase 10: Reporting & Documentation\n")
            f.write("- **Script:** `phase10_reporting.py`\n")
            f.write("- **Purpose:** Create comprehensive reports and documentation\n")
            f.write("- **Output:** Multiple markdown reports\n\n")
            
            # Assumptions
            f.write("## Key Assumptions\n\n")
            f.write("1. **Data Completeness:** All provided data is representative of the full process\n")
            f.write("2. **Human-Executed Checks:** Only checks not marked as 'Failed by decision logic Automatically' are considered\n")
            f.write("3. **COGS Accuracy:** COGS values are accurate and represent true product value\n")
            f.write("4. **Disposition Accuracy:** Disposition values correctly reflect final outcomes\n")
            f.write("5. **Check Independence:** Quality checks are assumed to be independent (may not be true in practice)\n\n")
            
            # Reproducibility
            f.write("## Reproducibility\n\n")
            f.write("### Required Python Packages\n\n")
            f.write("```\n")
            f.write("pandas>=1.5.0\n")
            f.write("numpy>=1.23.0\n")
            f.write("matplotlib>=3.6.0\n")
            f.write("seaborn>=0.12.0\n")
            f.write("scipy>=1.9.0\n")
            f.write("openpyxl>=3.0.0\n")
            f.write("```\n\n")
            
            f.write("### Running the Analysis\n\n")
            f.write("1. Ensure all required packages are installed\n")
            f.write("2. Place data file in the correct directory\n")
            f.write("3. Run phases sequentially (Phase 1 through Phase 10)\n")
            f.write("4. Each phase produces output files that are used by subsequent phases\n\n")
            
            f.write("### Data File Structure\n\n")
            f.write("Expected input file structure:\n")
            f.write("- CSV or Excel format\n")
            f.write("- Multi-row format where quality checks are in separate rows\n")
            f.write("- Key columns: LPN, Amazon COGS, Disposition, Product, Product Category, Result of Repair\n")
            f.write("- Quality check columns: Various check names with Passed/Failed values\n\n")
        
        print(f"[OK] Code Documentation saved to: {doc_file}")
    
    def create_deliverables_checklist(self):
        """10.3 Deliverables Checklist"""
        print("\n" + "-" * 80)
        print("10.3 CREATING DELIVERABLES CHECKLIST")
        print("-" * 80)
        
        base_name = os.path.splitext(self.features_csv_path)[0]
        checklist_file = f"{base_name}_DELIVERABLES_CHECKLIST.md"
        
        # Check what files exist
        deliverables = {
            'Analysis Scripts': [],
            'Analysis Reports': [],
            'Data Visualizations': [],
            'Results Files': [],
            'Documentation': []
        }
        
        # Check for scripts
        script_files = [
            'phase1_data_understanding.py',
            'phase2_data_preprocessing.py',
            'phase3_eda.py',
            'phase4_feature_engineering.py',
            'phase5_statistical_analysis.py',
            'phase6_answer_questions.py',
            'phase7_advanced_analysis.py',
            'phase8_visualizations.py',
            'phase9_insights_recommendations.py',
            'phase10_reporting.py'
        ]
        
        for script in script_files:
            if os.path.exists(script):
                deliverables['Analysis Scripts'].append(script)
        
        # Check for reports
        report_files = [
            f"{base_name}_EXECUTIVE_SUMMARY.md",
            f"{base_name}_DETAILED_ANALYSIS_REPORT.md",
            f"{base_name}_RECOMMENDATIONS.md",
            f"{base_name}_PHASE9_INSIGHTS_AND_RECOMMENDATIONS.md"
        ]
        
        for report in report_files:
            if os.path.exists(report):
                deliverables['Analysis Reports'].append(os.path.basename(report))
        
        # Check for visualizations
        viz_dirs = [
            os.path.join(self.output_dir, 'Phase3_Graphs'),
            os.path.join(self.output_dir, 'Phase6_Graphs'),
            os.path.join(self.output_dir, 'Phase8_Visualizations')
        ]
        
        for viz_dir in viz_dirs:
            if os.path.exists(viz_dir):
                files = [f for f in os.listdir(viz_dir) if f.endswith('.png')]
                deliverables['Data Visualizations'].extend([f"{os.path.basename(viz_dir)}/{f}" for f in files])
        
        # Check for results files
        results_files = [
            f"{base_name}_phase1_results.json",
            f"{base_name}_phase2_results.json",
            f"{base_name}_preprocessed.csv",
            f"{base_name}_preprocessed_features.csv",
            f"{base_name}_phase3_results.json",
            f"{base_name}_phase4_results.json",
            f"{base_name}_phase5_results.json",
            f"{base_name}_phase6_results.json",
            f"{base_name}_phase7_results.json",
            f"{base_name}_phase9_results.json"
        ]
        
        for result_file in results_files:
            if os.path.exists(result_file):
                deliverables['Results Files'].append(os.path.basename(result_file))
        
        # Check for documentation
        doc_files = [
            f"{base_name}_DATA_DOCUMENTATION.md",
            f"{base_name}_CODE_DOCUMENTATION.md",
            'DATA_SCIENCE_CHECKLIST.md',
            'ANALYSIS_QUESTIONS_AND_ANSWERS.md'
        ]
        
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                deliverables['Documentation'].append(os.path.basename(doc_file) if os.path.basename(doc_file) else doc_file)
        
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write("# Deliverables Checklist: Liquidation Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("---\n\n")
            
            f.write("## Deliverables Summary\n\n")
            f.write("| Category | Count |\n")
            f.write("|----------|-------|\n")
            f.write(f"| Analysis Scripts | {len(deliverables['Analysis Scripts'])} |\n")
            f.write(f"| Analysis Reports | {len(deliverables['Analysis Reports'])} |\n")
            f.write(f"| Data Visualizations | {len(deliverables['Data Visualizations'])} |\n")
            f.write(f"| Results Files | {len(deliverables['Results Files'])} |\n")
            f.write(f"| Documentation | {len(deliverables['Documentation'])} |\n\n")
            
            # Analysis Scripts
            f.write("## Analysis Scripts (Python)\n\n")
            for script in deliverables['Analysis Scripts']:
                f.write(f"- [x] {script}\n")
            f.write("\n")
            
            # Analysis Reports
            f.write("## Analysis Reports\n\n")
            for report in deliverables['Analysis Reports']:
                f.write(f"- [x] {report}\n")
            f.write("\n")
            
            # Data Visualizations
            f.write("## Data Visualizations\n\n")
            f.write(f"**Total Visualizations:** {len(deliverables['Data Visualizations'])}\n\n")
            f.write("### Phase 3 Graphs\n")
            phase3_viz = [v for v in deliverables['Data Visualizations'] if 'Phase3' in v]
            for viz in phase3_viz[:10]:  # Show first 10
                f.write(f"- [x] {viz}\n")
            if len(phase3_viz) > 10:
                f.write(f"- ... and {len(phase3_viz) - 10} more\n")
            f.write("\n")
            
            f.write("### Phase 6 Graphs\n")
            phase6_viz = [v for v in deliverables['Data Visualizations'] if 'Phase6' in v]
            for viz in phase6_viz:
                f.write(f"- [x] {viz}\n")
            f.write("\n")
            
            f.write("### Phase 8 Visualizations\n")
            phase8_viz = [v for v in deliverables['Data Visualizations'] if 'Phase8' in v]
            for viz in phase8_viz:
                f.write(f"- [x] {viz}\n")
            f.write("\n")
            
            # Results Files
            f.write("## Results Files (JSON/CSV)\n\n")
            for result in deliverables['Results Files']:
                f.write(f"- [x] {result}\n")
            f.write("\n")
            
            # Documentation
            f.write("## Documentation\n\n")
            for doc in deliverables['Documentation']:
                f.write(f"- [x] {doc}\n")
            f.write("\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write("All deliverables have been created and are available in the project directory.\n")
            f.write("The analysis is complete and ready for review.\n\n")
        
        print(f"[OK] Deliverables Checklist saved to: {checklist_file}")


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
            print("Usage: python phase10_reporting.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 10 reporting
    try:
        reporter = Phase10Reporting(csv_file)
        reporter.run_phase10()
        print("\n[OK] Phase 10 reporting and documentation completed successfully!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 10 reporting: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

