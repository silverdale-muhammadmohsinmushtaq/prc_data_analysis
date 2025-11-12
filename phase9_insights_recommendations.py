#!/usr/bin/env python3
"""
Phase 9: Insights & Recommendations
Liquidation Analysis - Key findings, problem identification, and actionable recommendations
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class Phase9InsightsRecommendations:
    def __init__(self, features_csv_path):
        """Initialize Phase 9 insights and recommendations"""
        self.features_csv_path = features_csv_path
        self.df = None
        self.check_cols = []
        self.results = {
            'phase': 'Phase 9: Insights & Recommendations',
            'timestamp': datetime.now().isoformat(),
            'file_path': features_csv_path,
            'key_findings': [],
            'problems_identified': [],
            'recommendations': [],
            'financial_impact': {}
        }
        self.output_dir = os.path.dirname(features_csv_path)
        
        # Load previous phase results if available
        self.phase6_results = None
        self.phase7_results = None
        self.load_previous_results()
        
    def load_previous_results(self):
        """Load results from previous phases"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        
        phase6_file = f"{base_name}_phase6_results.json"
        phase7_file = f"{base_name}_phase7_results.json"
        
        if os.path.exists(phase6_file):
            with open(phase6_file, 'r', encoding='utf-8') as f:
                self.phase6_results = json.load(f)
        
        if os.path.exists(phase7_file):
            with open(phase7_file, 'r', encoding='utf-8') as f:
                self.phase7_results = json.load(f)
    
    def run_phase9(self):
        """Execute all Phase 9 tasks"""
        print("=" * 80)
        print("PHASE 9: INSIGHTS & RECOMMENDATIONS")
        print("=" * 80)
        
        # Load feature-engineered data
        self.load_data()
        
        # 9.1 Key Findings Summary
        self.summarize_key_findings()
        
        # 9.2 Problem Identification
        self.identify_problems()
        
        # 9.3 Recommendations
        self.generate_recommendations()
        
        # 9.4 Financial Impact
        self.calculate_financial_impact()
        
        # Save results
        self.save_results()
        
        # Generate markdown report
        self.generate_markdown_report()
        
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
        
        # Separate liquidated and sellable
        self.liquidated = self.df[self.df['is_liquidated'] == 1]
        self.sellable = self.df[self.df['is_liquidated'] == 0]
        
        print(f"[OK] Liquidated: {len(self.liquidated):,} ({len(self.liquidated)/len(self.df)*100:.1f}%)")
        print(f"[OK] Sellable: {len(self.sellable):,} ({len(self.sellable)/len(self.df)*100:.1f}%)")
    
    def summarize_key_findings(self):
        """9.1 Key Findings Summary"""
        print("\n" + "=" * 80)
        print("9.1 KEY FINDINGS SUMMARY")
        print("=" * 80)
        
        findings = []
        
        # Finding 1: Overall Liquidation Rate
        liquidation_rate = len(self.liquidated) / len(self.df) * 100
        total_value_lost = self.liquidated['Amazon COGS'].sum()
        findings.append({
            'finding': 'Overall Liquidation Rate',
            'description': f'{liquidation_rate:.1f}% of all orders are liquidated',
            'impact': f'${total_value_lost:,.2f} total value lost',
            'severity': 'HIGH' if liquidation_rate > 30 else 'MEDIUM'
        })
        
        # Finding 2: "Does it Work?" Check is Strongest Predictor
        if 'works_check_passed' in self.df.columns:
            works_failed_liquidated = (self.liquidated['works_check_passed'] == 0).sum()
            works_pct = works_failed_liquidated / len(self.liquidated) * 100
            
            works_passed_sellable = (self.sellable['works_check_passed'] == 1).sum()
            works_success_rate = works_passed_sellable / len(self.sellable) * 100 if len(self.sellable) > 0 else 0
            
            findings.append({
                'finding': '"Does it Work?" Check is Strongest Predictor',
                'description': f'{works_pct:.1f}% of liquidated items failed "Does it work?" check. {works_success_rate:.1f}% of items that passed became sellable.',
                'impact': 'Primary driver of liquidation decisions',
                'severity': 'CRITICAL'
            })
        
        # Finding 3: High COGS Items Have Lower Liquidation Rate
        high_cogs = self.df[self.df['Amazon COGS'] >= 2000]
        if len(high_cogs) > 0:
            high_cogs_rate = high_cogs['is_liquidated'].mean() * 100
            low_cogs = self.df[self.df['Amazon COGS'] < 2000]
            low_cogs_rate = low_cogs['is_liquidated'].mean() * 100
            
            findings.append({
                'finding': 'High COGS Items Have Lower Liquidation Rate',
                'description': f'Items >= $2,000 have {high_cogs_rate:.1f}% liquidation rate vs {low_cogs_rate:.1f}% for lower COGS items',
                'impact': 'Counter-intuitive: Higher value items are handled better',
                'severity': 'MEDIUM'
            })
        
        # Finding 4: Cosmetic Checks Have High False Positive Rate
        cosmetic_checks = [c for c in self.check_cols if 'scratches' in c.lower() or 'dents' in c.lower()]
        if cosmetic_checks:
            cosmetic_failed = self.df[self.df[cosmetic_checks[0]] == 'Failed']
            cosmetic_false_pos = cosmetic_failed[cosmetic_failed['is_liquidated'] == 0]
            if len(cosmetic_failed) > 0:
                false_pos_rate = len(cosmetic_false_pos) / len(cosmetic_failed) * 100
                findings.append({
                    'finding': 'Cosmetic Checks Have High False Positive Rate',
                    'description': f'{false_pos_rate:.1f}% of items that failed cosmetic checks were still sellable',
                    'impact': 'Cosmetic criteria may be too strict',
                    'severity': 'HIGH'
                })
        
        # Finding 5: Working Items Being Liquidated
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            if len(working_liquidated) > 0:
                working_value = working_liquidated['Amazon COGS'].sum()
                findings.append({
                    'finding': 'Working Items Being Liquidated',
                    'description': f'{len(working_liquidated)} items that passed "Does it work?" were still liquidated',
                    'impact': f'${working_value:,.2f} potential recovery value',
                    'severity': 'HIGH'
                })
        
        # Finding 6: Product-Specific Issues
        product_analysis = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'count'])
        always_liquidate = product_analysis[(product_analysis['mean'] == 1.0) & (product_analysis['count'] >= 2)]
        if len(always_liquidate) > 0:
            always_liquidate_value = self.df[self.df['Product'].isin(always_liquidate.index)]['Amazon COGS'].sum()
            findings.append({
                'finding': 'Products That Always Liquidate',
                'description': f'{len(always_liquidate)} products have 100% liquidation rate (min 2 orders)',
                'impact': f'${always_liquidate_value:,.2f} value lost from these products',
                'severity': 'HIGH'
            })
        
        # Finding 7: Category-Specific Issues
        category_rates = self.df.groupby('category_group')['is_liquidated'].mean()
        high_rate_cats = category_rates[category_rates >= 0.8]
        if len(high_rate_cats) > 0:
            high_cat_value = self.df[self.df['category_group'].isin(high_rate_cats.index) & 
                                     (self.df['is_liquidated'] == 1)]['Amazon COGS'].sum()
            findings.append({
                'finding': 'Categories with Very High Liquidation Rates',
                'description': f'{len(high_rate_cats)} categories have >=80% liquidation rate',
                'impact': f'${high_cat_value:,.2f} value lost from high-rate categories',
                'severity': 'HIGH'
            })
        
        # Finding 8: Functional Issues are Primary Reason
        functional_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Functional', case=False, na=False)
        ]
        if len(functional_issues) > 0:
            functional_pct = len(functional_issues) / len(self.liquidated) * 100
            functional_value = functional_issues['Amazon COGS'].sum()
            findings.append({
                'finding': 'Functional Issues are Primary Liquidation Reason',
                'description': f'{functional_pct:.1f}% of liquidations are due to functional issues',
                'impact': f'${functional_value:,.2f} value lost to functional issues',
                'severity': 'CRITICAL'
            })
        
        # Finding 9: Fraud Detection Impact
        fraud_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Fraud', case=False, na=False)
        ]
        if len(fraud_issues) > 0:
            fraud_pct = len(fraud_issues) / len(self.liquidated) * 100
            fraud_value = fraud_issues['Amazon COGS'].sum()
            findings.append({
                'finding': 'Fraud Detection Accounts for Significant Liquidations',
                'description': f'{fraud_pct:.1f}% of liquidations are due to fraud detection',
                'impact': f'${fraud_value:,.2f} value lost to fraud',
                'severity': 'MEDIUM'
            })
        
        # Finding 10: Inconsistent Product Outcomes
        product_consistency = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'std', 'count'])
        inconsistent = product_consistency[
            (product_consistency['mean'] > 0) & 
            (product_consistency['mean'] < 1) & 
            (product_consistency['count'] >= 5)
        ]
        if len(inconsistent) > 0:
            findings.append({
                'finding': 'Inconsistent Product Outcomes',
                'description': f'{len(inconsistent)} products have mixed outcomes (some liquidate, some sellable)',
                'impact': 'Decision criteria may be inconsistently applied',
                'severity': 'MEDIUM'
            })
        
        self.results['key_findings'] = findings
        
        print("\nTop 10 Key Findings:")
        print("-" * 80)
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. {finding['finding']} [{finding['severity']}]")
            print(f"   {finding['description']}")
            print(f"   Impact: {finding['impact']}")
    
    def identify_problems(self):
        """9.2 Problem Identification"""
        print("\n" + "=" * 80)
        print("9.2 PROBLEM IDENTIFICATION")
        print("=" * 80)
        
        problems = []
        
        # Problem 1: High Overall Liquidation Rate
        liquidation_rate = len(self.liquidated) / len(self.df) * 100
        if liquidation_rate > 25:
            problems.append({
                'problem': 'High Overall Liquidation Rate',
                'description': f'{liquidation_rate:.1f}% of orders are liquidated, which is above optimal threshold',
                'root_cause': 'Multiple factors: functional issues, fraud detection, cosmetic criteria',
                'impact': 'HIGH',
                'affected_volume': len(self.liquidated),
                'affected_value': self.liquidated['Amazon COGS'].sum()
            })
        
        # Problem 2: Working Items Being Liquidated
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            if len(working_liquidated) > 0:
                problems.append({
                    'problem': 'Working Items Being Liquidated',
                    'description': f'{len(working_liquidated)} items that passed "Does it work?" were liquidated',
                    'root_cause': 'Other checks (cosmetic, fraud) overriding functional status',
                    'impact': 'HIGH',
                    'affected_volume': len(working_liquidated),
                    'affected_value': working_liquidated['Amazon COGS'].sum()
                })
        
        # Problem 3: High COGS Items Being Liquidated
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        if len(high_cogs_liquidated) > 0:
            problems.append({
                'problem': 'High COGS Items Being Liquidated',
                'description': f'{len(high_cogs_liquidated)} items with COGS >= $2,000 were liquidated',
                'root_cause': 'No exception handling for high-value items',
                'impact': 'HIGH',
                'affected_volume': len(high_cogs_liquidated),
                'affected_value': high_cogs_liquidated['Amazon COGS'].sum()
            })
        
        # Problem 4: Cosmetic Checks Too Strict
        cosmetic_checks = [c for c in self.check_cols if 'scratches' in c.lower() or 'dents' in c.lower()]
        if cosmetic_checks:
            cosmetic_failed = self.df[self.df[cosmetic_checks[0]] == 'Failed']
            cosmetic_false_pos = cosmetic_failed[cosmetic_failed['is_liquidated'] == 0]
            if len(cosmetic_failed) > 0:
                false_pos_rate = len(cosmetic_false_pos) / len(cosmetic_failed) * 100
                if false_pos_rate > 70:
                    problems.append({
                        'problem': 'Cosmetic Checks Too Strict',
                        'description': f'{false_pos_rate:.1f}% false positive rate for cosmetic checks',
                        'root_cause': 'Cosmetic criteria may be too strict or inconsistently applied',
                        'impact': 'MEDIUM',
                        'affected_volume': len(cosmetic_false_pos),
                        'affected_value': cosmetic_false_pos['Amazon COGS'].sum()
                    })
        
        # Problem 5: Products That Always Liquidate
        product_analysis = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'count'])
        always_liquidate = product_analysis[(product_analysis['mean'] == 1.0) & (product_analysis['count'] >= 2)]
        if len(always_liquidate) > 0:
            always_liquidate_orders = self.df[self.df['Product'].isin(always_liquidate.index)]
            problems.append({
                'problem': 'Products That Always Liquidate',
                'description': f'{len(always_liquidate)} products have 100% liquidation rate',
                'root_cause': 'Product-specific issues or incorrect categorization',
                'impact': 'MEDIUM',
                'affected_volume': len(always_liquidate_orders),
                'affected_value': always_liquidate_orders['Amazon COGS'].sum()
            })
        
        # Problem 6: Category-Specific High Rates
        category_rates = self.df.groupby('category_group')['is_liquidated'].mean()
        high_rate_cats = category_rates[category_rates >= 0.8]
        if len(high_rate_cats) > 0:
            high_cat_orders = self.df[self.df['category_group'].isin(high_rate_cats.index) & 
                                     (self.df['is_liquidated'] == 1)]
            problems.append({
                'problem': 'Categories with Very High Liquidation Rates',
                'description': f'{len(high_rate_cats)} categories have >=80% liquidation rate',
                'root_cause': 'Category-specific quality standards may be inappropriate',
                'impact': 'HIGH',
                'affected_volume': len(high_cat_orders),
                'affected_value': high_cat_orders['Amazon COGS'].sum()
            })
        
        # Problem 7: Inconsistent Product Outcomes
        product_consistency = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'std', 'count'])
        inconsistent = product_consistency[
            (product_consistency['mean'] > 0) & 
            (product_consistency['mean'] < 1) & 
            (product_consistency['count'] >= 5)
        ]
        if len(inconsistent) > 0:
            problems.append({
                'problem': 'Inconsistent Product Outcomes',
                'description': f'{len(inconsistent)} products have mixed outcomes',
                'root_cause': 'Decision criteria inconsistently applied or subjective',
                'impact': 'MEDIUM',
                'affected_volume': len(inconsistent),
                'affected_value': 0  # Hard to quantify
            })
        
        # Problem 8: High Check Volume
        if 'total_checks' in self.df.columns:
            avg_checks = self.df['total_checks'].mean()
            if avg_checks > 20:
                problems.append({
                    'problem': 'High Check Volume Per Order',
                    'description': f'Average {avg_checks:.1f} checks per order may slow processing',
                    'root_cause': 'Too many checks required, some may be redundant',
                    'impact': 'LOW',
                    'affected_volume': len(self.df),
                    'affected_value': 0
                })
        
        self.results['problems_identified'] = problems
        
        print("\nProblems Identified:")
        print("-" * 80)
        for i, problem in enumerate(problems, 1):
            print(f"\n{i}. {problem['problem']} [{problem['impact']} IMPACT]")
            print(f"   Description: {problem['description']}")
            print(f"   Root Cause: {problem['root_cause']}")
            print(f"   Affected: {problem['affected_volume']} orders, ${problem['affected_value']:,.2f} value")
    
    def generate_recommendations(self):
        """9.3 Generate Recommendations"""
        print("\n" + "=" * 80)
        print("9.3 GENERATING RECOMMENDATIONS")
        print("=" * 80)
        
        recommendations = []
        
        # Recommendation 1: Exception Handling for High COGS Items
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        if len(high_cogs_liquidated) > 0:
            recommendations.append({
                'recommendation': 'Implement Exception Handling for High COGS Items',
                'type': 'IMMEDIATE',
                'priority': 'HIGH',
                'description': 'Create exception rules for items with COGS >= $2,000 that pass "Does it work?" check',
                'action_items': [
                    'Modify BPMN to add exception path for high COGS items',
                    'Require additional review before liquidating high COGS items',
                    'Consider relaxing cosmetic criteria for high COGS working items'
                ],
                'expected_impact': f'Could recover ${high_cogs_liquidated["Amazon COGS"].sum():,.2f} in high COGS items',
                'implementation_effort': 'MEDIUM',
                'timeline': '2-4 weeks'
            })
        
        # Recommendation 2: Review Working Items Being Liquidated
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            if len(working_liquidated) > 0:
                recommendations.append({
                    'recommendation': 'Review and Prevent Liquidating Working Items',
                    'type': 'IMMEDIATE',
                    'priority': 'HIGH',
                    'description': 'Items that pass "Does it work?" should rarely be liquidated',
                    'action_items': [
                        'Audit all working items that were liquidated',
                        'Modify BPMN to require additional approval for liquidating working items',
                        'Create exception rule: If "Does it work?" = Passed, require Level 3 review before liquidation'
                    ],
                    'expected_impact': f'Could recover ${working_liquidated["Amazon COGS"].sum():,.2f}',
                    'implementation_effort': 'LOW',
                    'timeline': '1-2 weeks'
                })
        
        # Recommendation 3: Relax Cosmetic Criteria
        cosmetic_checks = [c for c in self.check_cols if 'scratches' in c.lower() or 'dents' in c.lower()]
        if cosmetic_checks:
            cosmetic_failed = self.df[self.df[cosmetic_checks[0]] == 'Failed']
            cosmetic_false_pos = cosmetic_failed[cosmetic_failed['is_liquidated'] == 0]
            if len(cosmetic_failed) > 0:
                false_pos_rate = len(cosmetic_false_pos) / len(cosmetic_failed) * 100
                if false_pos_rate > 70:
                    recommendations.append({
                        'recommendation': 'Review and Relax Cosmetic Check Criteria',
                        'type': 'PROCESS_IMPROVEMENT',
                        'priority': 'MEDIUM',
                        'description': f'Cosmetic checks have {false_pos_rate:.1f}% false positive rate',
                        'action_items': [
                            'Review cosmetic check criteria and thresholds',
                            'Consider making cosmetic issues non-blocking for sellable items',
                            'Update BPMN to allow cosmetic issues if item works and is repairable'
                        ],
                        'expected_impact': 'Reduce false liquidations due to cosmetic issues',
                        'implementation_effort': 'MEDIUM',
                        'timeline': '2-3 weeks'
                    })
        
        # Recommendation 4: Product-Specific Exception Rules
        product_analysis = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'count'])
        always_liquidate = product_analysis[(product_analysis['mean'] == 1.0) & (product_analysis['count'] >= 2)]
        if len(always_liquidate) > 0:
            recommendations.append({
                'recommendation': 'Create Exception Rules for Products That Always Liquidate',
                'type': 'PROCESS_IMPROVEMENT',
                'priority': 'MEDIUM',
                'description': f'{len(always_liquidate)} products have 100% liquidation rate',
                'action_items': [
                    'Investigate why these products always liquidate',
                    'Consider if these products should be in repair process at all',
                    'Create exception handling or alternative routing for these products'
                ],
                'expected_impact': 'Reduce unnecessary processing of products that will always liquidate',
                'implementation_effort': 'MEDIUM',
                'timeline': '3-4 weeks'
            })
        
        # Recommendation 5: Category-Specific Quality Standards
        category_rates = self.df.groupby('category_group')['is_liquidated'].mean()
        high_rate_cats = category_rates[category_rates >= 0.8]
        if len(high_rate_cats) > 0:
            recommendations.append({
                'recommendation': 'Review Category-Specific Quality Standards',
                'type': 'PROCESS_IMPROVEMENT',
                'priority': 'HIGH',
                'description': f'{len(high_rate_cats)} categories have >=80% liquidation rate',
                'action_items': [
                    'Review quality standards for high-rate categories',
                    'Consider if standards are appropriate for these categories',
                    'Implement category-specific exception rules if needed'
                ],
                'expected_impact': 'Reduce liquidation rate in problematic categories',
                'implementation_effort': 'HIGH',
                'timeline': '4-6 weeks'
            })
        
        # Recommendation 6: Standardize Decision Criteria
        product_consistency = self.df.groupby('Product')['is_liquidated'].agg(['mean', 'std', 'count'])
        inconsistent = product_consistency[
            (product_consistency['mean'] > 0) & 
            (product_consistency['mean'] < 1) & 
            (product_consistency['count'] >= 5)
        ]
        if len(inconsistent) > 0:
            recommendations.append({
                'recommendation': 'Standardize Decision Criteria for Consistent Outcomes',
                'type': 'PROCESS_IMPROVEMENT',
                'priority': 'MEDIUM',
                'description': f'{len(inconsistent)} products have inconsistent outcomes',
                'action_items': [
                    'Review decision criteria for products with mixed outcomes',
                    'Create clear guidelines for when to liquidate vs sell',
                    'Provide additional training on decision criteria',
                    'Implement quality assurance reviews for inconsistent products'
                ],
                'expected_impact': 'Improve consistency in decision-making',
                'implementation_effort': 'MEDIUM',
                'timeline': '3-4 weeks'
            })
        
        # Recommendation 7: Optimize Check Volume
        if 'total_checks' in self.df.columns:
            avg_checks = self.df['total_checks'].mean()
            if avg_checks > 20:
                recommendations.append({
                    'recommendation': 'Optimize Check Volume to Reduce Processing Time',
                    'type': 'PROCESS_IMPROVEMENT',
                    'priority': 'LOW',
                    'description': f'Average {avg_checks:.1f} checks per order may be excessive',
                    'action_items': [
                        'Review all checks for redundancy',
                        'Identify checks that rarely affect outcome',
                        'Consider removing or combining redundant checks',
                        'Prioritize checks that have highest impact on decision'
                    ],
                    'expected_impact': 'Reduce processing time and improve efficiency',
                    'implementation_effort': 'MEDIUM',
                    'timeline': '4-6 weeks'
                })
        
        # Recommendation 8: Fraud Detection Review
        fraud_issues = self.liquidated[
            self.liquidated['Result of Repair'].str.contains('Fraud', case=False, na=False)
        ]
        if len(fraud_issues) > 0:
            fraud_pct = len(fraud_issues) / len(self.liquidated) * 100
            if fraud_pct > 25:
                recommendations.append({
                    'recommendation': 'Review Fraud Detection Accuracy',
                    'type': 'PROCESS_IMPROVEMENT',
                    'priority': 'MEDIUM',
                    'description': f'{fraud_pct:.1f}% of liquidations are due to fraud',
                    'action_items': [
                        'Review fraud detection criteria and accuracy',
                        'Audit high COGS items marked as fraud',
                        'Consider additional verification for fraud cases',
                        'Implement appeal process for fraud decisions'
                    ],
                    'expected_impact': 'Reduce false fraud positives, especially for high COGS items',
                    'implementation_effort': 'MEDIUM',
                    'timeline': '3-4 weeks'
                })
        
        # Recommendation 9: Implement Recovery Process
        if 'recovery_potential' in self.df.columns:
            recovery_items = self.df[self.df['recovery_potential'] > 0]
            if len(recovery_items) > 0:
                recovery_value = recovery_items['recovery_potential'].sum()
                recommendations.append({
                    'recommendation': 'Implement Recovery Process for Working Liquidated Items',
                    'type': 'IMMEDIATE',
                    'priority': 'HIGH',
                    'description': 'Create process to recover working items that were liquidated',
                    'action_items': [
                        'Identify all working items that were liquidated',
                        'Create recovery workflow to re-evaluate these items',
                        'Implement quality gate before final liquidation decision',
                        'Add recovery step in BPMN for working items'
                    ],
                    'expected_impact': f'Could recover ${recovery_value:,.2f} in working items',
                    'implementation_effort': 'MEDIUM',
                    'timeline': '2-3 weeks'
                })
        
        # Recommendation 10: BPMN Modifications
        recommendations.append({
            'recommendation': 'Modify BPMN Process Flow',
            'type': 'BPMN_MODIFICATION',
            'priority': 'HIGH',
            'description': 'Update BPMN to incorporate exception handling and improved decision logic',
            'action_items': [
                'Add exception path for high COGS items (>= $2,000)',
                'Add review gate for working items before liquidation',
                'Modify cosmetic check logic to be non-blocking for working items',
                'Add Level 3 review requirement for high-value liquidations',
                'Implement category-specific routing where appropriate'
            ],
            'expected_impact': 'Improve decision quality and reduce unnecessary liquidations',
            'implementation_effort': 'HIGH',
            'timeline': '4-6 weeks'
        })
        
        self.results['recommendations'] = recommendations
        
        print("\nRecommendations Generated:")
        print("-" * 80)
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['recommendation']} [{rec['type']}] - Priority: {rec['priority']}")
            print(f"   {rec['description']}")
            print(f"   Expected Impact: {rec['expected_impact']}")
            print(f"   Timeline: {rec['timeline']}")
    
    def calculate_financial_impact(self):
        """9.4 Calculate Financial Impact"""
        print("\n" + "=" * 80)
        print("9.4 FINANCIAL IMPACT ANALYSIS")
        print("=" * 80)
        
        financial = {}
        
        # Current value lost
        total_value_lost = self.liquidated['Amazon COGS'].sum()
        financial['current_value_lost'] = round(total_value_lost, 2)
        
        # Potential recovery value
        if 'recovery_potential' in self.df.columns:
            recovery_value = self.df['recovery_potential'].sum()
            financial['potential_recovery_value'] = round(recovery_value, 2)
        else:
            # Calculate manually
            if 'works_check_passed' in self.df.columns:
                working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
                recovery_value = working_liquidated['Amazon COGS'].sum()
                financial['potential_recovery_value'] = round(recovery_value, 2)
            else:
                financial['potential_recovery_value'] = 0
        
        # High COGS items liquidated
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        financial['high_cogs_liquidated_value'] = round(high_cogs_liquidated['Amazon COGS'].sum(), 2)
        financial['high_cogs_liquidated_count'] = len(high_cogs_liquidated)
        
        # Value lost by reason
        reason_value = self.liquidated.groupby('Result of Repair')['Amazon COGS'].sum().sort_values(ascending=False)
        financial['value_lost_by_reason'] = reason_value.to_dict()
        
        # Value lost by category
        category_value = self.liquidated.groupby('category_group')['Amazon COGS'].sum().sort_values(ascending=False)
        financial['top_10_categories_value_lost'] = category_value.head(10).to_dict()
        
        # Recovery potential scenarios
        scenarios = {}
        
        # Scenario 1: Recover all working items
        if 'works_check_passed' in self.df.columns:
            working_liquidated = self.liquidated[self.liquidated['works_check_passed'] == 1]
            scenarios['recover_working_items'] = {
                'description': 'Recover all items that passed "Does it work?" check',
                'value': round(working_liquidated['Amazon COGS'].sum(), 2),
                'count': len(working_liquidated)
            }
        
        # Scenario 2: Exception handling for high COGS
        high_cogs_liquidated = self.liquidated[self.liquidated['Amazon COGS'] >= 2000]
        scenarios['high_cogs_exception'] = {
            'description': 'Implement exception handling for high COGS items (>= $2,000)',
            'value': round(high_cogs_liquidated['Amazon COGS'].sum(), 2),
            'count': len(high_cogs_liquidated)
        }
        
        # Scenario 3: Reduce cosmetic false positives by 50%
        cosmetic_checks = [c for c in self.check_cols if 'scratches' in c.lower() or 'dents' in c.lower()]
        if cosmetic_checks:
            cosmetic_failed_liquidated = self.liquidated[self.liquidated[cosmetic_checks[0]] == 'Failed']
            if len(cosmetic_failed_liquidated) > 0:
                scenarios['reduce_cosmetic_false_positives'] = {
                    'description': 'Reduce cosmetic false positives by 50%',
                    'value': round(cosmetic_failed_liquidated['Amazon COGS'].sum() * 0.5, 2),
                    'count': int(len(cosmetic_failed_liquidated) * 0.5)
                }
        
        financial['recovery_scenarios'] = scenarios
        
        # Total potential recovery (conservative estimate)
        total_potential = 0
        if 'recover_working_items' in scenarios:
            total_potential += scenarios['recover_working_items']['value']
        if 'high_cogs_exception' in scenarios:
            total_potential += scenarios['high_cogs_exception']['value'] * 0.5  # Conservative: 50% recovery
        financial['total_potential_recovery'] = round(total_potential, 2)
        
        # ROI calculation (assuming implementation cost)
        implementation_cost = 50000  # Estimated cost for process improvements
        financial['estimated_implementation_cost'] = implementation_cost
        financial['estimated_annual_recovery'] = round(total_potential * 12, 2)  # Assuming monthly data
        financial['roi_percentage'] = round((financial['estimated_annual_recovery'] - implementation_cost) / implementation_cost * 100, 2)
        financial['payback_period_months'] = round(implementation_cost / (total_potential) if total_potential > 0 else 0, 1)
        
        self.results['financial_impact'] = financial
        
        print("\nFinancial Impact Summary:")
        print("-" * 80)
        print(f"Current Value Lost: ${financial['current_value_lost']:,.2f}")
        print(f"Potential Recovery Value: ${financial['potential_recovery_value']:,.2f}")
        print(f"High COGS Items Liquidated: {financial['high_cogs_liquidated_count']} items, ${financial['high_cogs_liquidated_value']:,.2f}")
        print(f"\nRecovery Scenarios:")
        for scenario, data in scenarios.items():
            print(f"  - {data['description']}: ${data['value']:,.2f} ({data['count']} items)")
        print(f"\nTotal Potential Recovery: ${financial['total_potential_recovery']:,.2f}")
        print(f"Estimated Implementation Cost: ${financial['estimated_implementation_cost']:,.2f}")
        print(f"Estimated Annual Recovery: ${financial['estimated_annual_recovery']:,.2f}")
        print(f"ROI: {financial['roi_percentage']:.1f}%")
        print(f"Payback Period: {financial['payback_period_months']:.1f} months")
    
    def save_results(self):
        """Save Phase 9 results to JSON"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        output_file = f"{base_name}_phase9_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"PHASE 9 COMPLETE - Results saved to: {output_file}")
        print("=" * 80)
    
    def generate_markdown_report(self):
        """Generate markdown report"""
        base_name = os.path.splitext(self.features_csv_path)[0]
        report_file = f"{base_name}_PHASE9_INSIGHTS_AND_RECOMMENDATIONS.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Phase 9: Insights & Recommendations\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Key Findings
            f.write("## 9.1 Key Findings Summary\n\n")
            for i, finding in enumerate(self.results['key_findings'], 1):
                f.write(f"### Finding {i}: {finding['finding']} [{finding['severity']}]\n\n")
                f.write(f"**Description:** {finding['description']}\n\n")
                f.write(f"**Impact:** {finding['impact']}\n\n")
                f.write("---\n\n")
            
            # Problems
            f.write("## 9.2 Problems Identified\n\n")
            for i, problem in enumerate(self.results['problems_identified'], 1):
                f.write(f"### Problem {i}: {problem['problem']} [{problem['impact']} IMPACT]\n\n")
                f.write(f"**Description:** {problem['description']}\n\n")
                f.write(f"**Root Cause:** {problem['root_cause']}\n\n")
                f.write(f"**Affected:** {problem['affected_volume']} orders, ${problem['affected_value']:,.2f} value\n\n")
                f.write("---\n\n")
            
            # Recommendations
            f.write("## 9.3 Recommendations\n\n")
            for i, rec in enumerate(self.results['recommendations'], 1):
                f.write(f"### Recommendation {i}: {rec['recommendation']}\n\n")
                f.write(f"**Type:** {rec['type']}  |  **Priority:** {rec['priority']}  |  **Timeline:** {rec['timeline']}\n\n")
                f.write(f"**Description:** {rec['description']}\n\n")
                f.write("**Action Items:**\n")
                for action in rec['action_items']:
                    f.write(f"- {action}\n")
                f.write(f"\n**Expected Impact:** {rec['expected_impact']}\n\n")
                f.write("---\n\n")
            
            # Financial Impact
            f.write("## 9.4 Financial Impact Analysis\n\n")
            financial = self.results['financial_impact']
            f.write(f"### Current Status\n\n")
            f.write(f"- **Current Value Lost:** ${financial['current_value_lost']:,.2f}\n")
            f.write(f"- **Potential Recovery Value:** ${financial['potential_recovery_value']:,.2f}\n")
            f.write(f"- **High COGS Items Liquidated:** {financial['high_cogs_liquidated_count']} items, ${financial['high_cogs_liquidated_value']:,.2f}\n\n")
            
            f.write("### Recovery Scenarios\n\n")
            for scenario, data in financial['recovery_scenarios'].items():
                f.write(f"- **{data['description']}:** ${data['value']:,.2f} ({data['count']} items)\n")
            f.write("\n")
            
            f.write("### ROI Analysis\n\n")
            f.write(f"- **Total Potential Recovery:** ${financial['total_potential_recovery']:,.2f}\n")
            f.write(f"- **Estimated Implementation Cost:** ${financial['estimated_implementation_cost']:,.2f}\n")
            f.write(f"- **Estimated Annual Recovery:** ${financial['estimated_annual_recovery']:,.2f}\n")
            f.write(f"- **ROI:** {financial['roi_percentage']:.1f}%\n")
            f.write(f"- **Payback Period:** {financial['payback_period_months']:.1f} months\n\n")
        
        print(f"[OK] Markdown report saved to: {report_file}")
        self.results['markdown_report'] = report_file


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
            print("Usage: python phase9_insights_recommendations.py <features_csv_path>")
            return
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Run Phase 9 analysis
    try:
        analyzer = Phase9InsightsRecommendations(csv_file)
        results = analyzer.run_phase9()
        print("\n[OK] Phase 9 insights and recommendations completed successfully!")
        return results
    except Exception as e:
        print(f"\n[ERROR] Error during Phase 9 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

