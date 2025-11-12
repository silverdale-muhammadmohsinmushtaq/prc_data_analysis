"""
Analyze Quality Check Execution Patterns
Identifies which combinations of passed/failed checks lead to liquidation vs sellable
Similar to DECISION_TREE_ANALYSIS.md format
"""

import pandas as pd
import numpy as np
import json
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

def load_data():
    """Load the preprocessed features data"""
    df = pd.read_csv('Repair Order (repair.order)_preprocessed_features.csv')
    return df

def get_quality_check_columns(df):
    """Get all quality check columns (excluding metadata columns)"""
    exclude_cols = [
        'Amazon COGS', 'Completed On', 'Disposition', 'LPN', 'Product', 
        'Product Category', 'Result of Repair', 'Scheduled Date', 
        'Shipped Date', 'Started On', 'LPN/Amazon COGS', 'Checks/Title',
        'Checks/Failed by decision logic Automatically', 'Checks/Status',
        'is_human_executed', 'is_liquidated', 'cogs_bin', 'processing_days',
        'category_group', 'high_value_flag', 'total_checks', 'failed_checks_count',
        'passed_checks_count', 'failure_rate', 'fraud_check_failed', 
        'cosmetic_check_failed', 'repairable_check_failed', 'works_check_passed',
        'factory_sealed_check_passed', 'value_lost', 'recovery_potential',
        'days_to_ship', 'check_efficiency'
    ]
    
    qc_cols = [col for col in df.columns if col not in exclude_cols]
    return qc_cols

def create_check_pattern(row, qc_cols):
    """Create a pattern string representing passed/failed checks"""
    pattern_parts = []
    for col in qc_cols:
        value = row[col]
        if pd.notna(value):
            if value == 'Passed':
                pattern_parts.append(f"{col}:P")
            elif value == 'Failed':
                pattern_parts.append(f"{col}:F")
    return " | ".join(pattern_parts)

def get_key_checks_pattern(row, key_checks):
    """Create a simplified pattern using only key decision checks"""
    pattern_parts = []
    for check_name, col in key_checks.items():
        value = row[col]
        if pd.notna(value):
            if value == 'Passed':
                pattern_parts.append(f"{check_name}:P")
            elif value == 'Failed':
                pattern_parts.append(f"{check_name}:F")
    return " -> ".join(pattern_parts)

def analyze_execution_patterns(df):
    """Analyze execution patterns"""
    print("Loading data...")
    qc_cols = get_quality_check_columns(df)
    print(f"Found {len(qc_cols)} quality check columns")
    
    # Key decision checks based on DECISION_TREE_ANALYSIS.md
    key_checks = {
        'IOG': 'Is_it_IOG_Es_IOG',
        'Something_in_Box': 'Is_there_something_in_the_box_Hay_algo_en_la_caja',
        'TREX_Open': 'Did_T_Rex_Open_Se_abri_T_Rex',
        'Expected_Item': 'Is_it_the_Expected_Item_Es_el_art_culo_esperado',
        'Fraud': 'Is_it_Fraud_Es_fraude',
        'Factory_Sealed': 'Is_the_Item_Factory_Sealed_El_art_culo_est_sellado',
        'Destroy': 'Does_the_item_need_to_be_Destroyed_El_art_culo_nec',
        'Scratches_Dents': 'Does_the_item_have_scratches_or_dents_larger_that_',
        'Works': 'Does_the_item_work_El_art_culo_funciona',
        'Repairable': 'Is_the_item_Repairable_El_art_culo_es_reparable',
        'Needs_Parts': 'Does_it_need_Parts_Necesita_partes',
        'Has_Parts': 'Do_you_have_parts_Tienes_las_partes',
        'Needs_Sanitization': 'Does_it_need_Sanitization_Necesita_sanitizaci_n',
        'Factory_Reset': 'Did_you_do_a_Factory_Reset_Hiciste_un_restablecimi'
    }
    
    # Filter to only checks that exist in the data
    available_key_checks = {k: v for k, v in key_checks.items() if v in df.columns}
    print(f"Found {len(available_key_checks)} key decision checks in data")
    
    # Create patterns
    print("Creating execution patterns...")
    df['full_pattern'] = df.apply(lambda row: create_check_pattern(row, qc_cols), axis=1)
    df['key_pattern'] = df.apply(lambda row: get_key_checks_pattern(row, available_key_checks), axis=1)
    
    # Analyze patterns by disposition
    results = {
        'total_orders': len(df),
        'liquidated_count': len(df[df['Disposition'] == 'Liquidate']),
        'sellable_count': len(df[df['Disposition'] == 'Sellable']),
        'key_checks_used': list(available_key_checks.keys()),
        'patterns': {}
    }
    
    # Analyze liquidation patterns
    liquidated = df[df['Disposition'] == 'Liquidate'].copy()
    sellable = df[df['Disposition'] == 'Sellable'].copy()
    
    # Top liquidation patterns (key checks)
    liquidated_patterns = liquidated['key_pattern'].value_counts().head(20)
    sellable_patterns = sellable['key_pattern'].value_counts().head(20)
    
    results['patterns']['liquidated_top_20'] = liquidated_patterns.to_dict()
    results['patterns']['sellable_top_20'] = sellable_patterns.to_dict()
    
    # Analyze specific paths from DECISION_TREE_ANALYSIS.md
    path_analysis = analyze_decision_paths(df, available_key_checks)
    results['decision_paths'] = path_analysis
    
    # Pattern frequency analysis
    pattern_freq = analyze_pattern_frequency(df, available_key_checks)
    results['pattern_frequency'] = pattern_freq
    
    return results, df, available_key_checks

def analyze_decision_paths(df, key_checks):
    """Analyze specific decision paths from DECISION_TREE_ANALYSIS.md"""
    paths = {}
    
    # Path 1: Empty Box -> Liquidation
    if 'Something_in_Box' in key_checks:
        empty_box = df[df[key_checks['Something_in_Box']] == 'Failed']
        paths['Path_1_Empty_Box'] = {
            'description': 'Is there something in the box? -> No -> Liquidation',
            'total_count': len(empty_box),
            'liquidated': len(empty_box[empty_box['Disposition'] == 'Liquidate']),
            'sellable': len(empty_box[empty_box['Disposition'] == 'Sellable']),
            'liquidation_rate': len(empty_box[empty_box['Disposition'] == 'Liquidate']) / len(empty_box) * 100 if len(empty_box) > 0 else 0
        }
    
    # Path 2: Non-Repairable -> Liquidation
    if 'Repairable' in key_checks:
        non_repairable = df[df[key_checks['Repairable']] == 'Failed']
        paths['Path_2_Non_Repairable'] = {
            'description': 'Is the Item Repairable? -> No -> Liquidation',
            'total_count': len(non_repairable),
            'liquidated': len(non_repairable[non_repairable['Disposition'] == 'Liquidate']),
            'sellable': len(non_repairable[non_repairable['Disposition'] == 'Sellable']),
            'liquidation_rate': len(non_repairable[non_repairable['Disposition'] == 'Liquidate']) / len(non_repairable) * 100 if len(non_repairable) > 0 else 0
        }
    
    # Path 3: Fraud -> Liquidation
    if 'Fraud' in key_checks:
        fraud_yes = df[df[key_checks['Fraud']] == 'Passed']  # "Is it Fraud?" -> Yes means Passed check
        fraud_no = df[df[key_checks['Fraud']] == 'Failed']   # "Is it Fraud?" -> No means Failed check
        paths['Path_3_Fraud_Yes'] = {
            'description': 'Is it Fraud? -> Yes -> Liquidation',
            'total_count': len(fraud_yes),
            'liquidated': len(fraud_yes[fraud_yes['Disposition'] == 'Liquidate']),
            'sellable': len(fraud_yes[fraud_yes['Disposition'] == 'Sellable']),
            'liquidation_rate': len(fraud_yes[fraud_yes['Disposition'] == 'Liquidate']) / len(fraud_yes) * 100 if len(fraud_yes) > 0 else 0
        }
        paths['Path_3_Fraud_No'] = {
            'description': 'Is it Fraud? -> No -> Continue',
            'total_count': len(fraud_no),
            'liquidated': len(fraud_no[fraud_no['Disposition'] == 'Liquidate']),
            'sellable': len(fraud_no[fraud_no['Disposition'] == 'Sellable']),
            'liquidation_rate': len(fraud_no[fraud_no['Disposition'] == 'Liquidate']) / len(fraud_no) * 100 if len(fraud_no) > 0 else 0
        }
    
    # Path 4: Factory Sealed -> Sellable
    if 'Factory_Sealed' in key_checks:
        factory_sealed = df[df[key_checks['Factory_Sealed']] == 'Passed']
        paths['Path_4_Factory_Sealed'] = {
            'description': 'Is the Item Factory Sealed? -> Yes -> Sellable',
            'total_count': len(factory_sealed),
            'liquidated': len(factory_sealed[factory_sealed['Disposition'] == 'Liquidate']),
            'sellable': len(factory_sealed[factory_sealed['Disposition'] == 'Sellable']),
            'sellable_rate': len(factory_sealed[factory_sealed['Disposition'] == 'Sellable']) / len(factory_sealed) * 100 if len(factory_sealed) > 0 else 0
        }
    
    # Path 5: Destroy -> Liquidation
    if 'Destroy' in key_checks:
        destroy = df[df[key_checks['Destroy']] == 'Passed']  # "Does it need to be Destroyed?" -> Yes means Passed
        paths['Path_5_Destroy'] = {
            'description': 'Does the item Need to be Destroyed? -> Yes -> Liquidation',
            'total_count': len(destroy),
            'liquidated': len(destroy[destroy['Disposition'] == 'Liquidate']),
            'sellable': len(destroy[destroy['Disposition'] == 'Sellable']),
            'liquidation_rate': len(destroy[destroy['Disposition'] == 'Liquidate']) / len(destroy) * 100 if len(destroy) > 0 else 0
        }
    
    # Path 6: Scratches/Dents -> Liquidation
    if 'Scratches_Dents' in key_checks:
        scratches = df[df[key_checks['Scratches_Dents']] == 'Passed']  # "Does it have scratches?" -> Yes means Passed
        paths['Path_6_Scratches_Dents'] = {
            'description': 'Does the item have scratches/dents? -> Yes -> Liquidation',
            'total_count': len(scratches),
            'liquidated': len(scratches[scratches['Disposition'] == 'Liquidate']),
            'sellable': len(scratches[scratches['Disposition'] == 'Sellable']),
            'liquidation_rate': len(scratches[scratches['Disposition'] == 'Liquidate']) / len(scratches) * 100 if len(scratches) > 0 else 0
        }
    
    # Path 7: Works -> Sellable (most important)
    if 'Works' in key_checks:
        works_passed = df[df[key_checks['Works']] == 'Passed']
        works_failed = df[df[key_checks['Works']] == 'Failed']
        paths['Path_7_Works_Passed'] = {
            'description': 'Does it Work? -> Yes -> Sellable',
            'total_count': len(works_passed),
            'liquidated': len(works_passed[works_passed['Disposition'] == 'Liquidate']),
            'sellable': len(works_passed[works_passed['Disposition'] == 'Sellable']),
            'sellable_rate': len(works_passed[works_passed['Disposition'] == 'Sellable']) / len(works_passed) * 100 if len(works_passed) > 0 else 0
        }
        paths['Path_7_Works_Failed'] = {
            'description': 'Does it Work? -> No -> Liquidation',
            'total_count': len(works_failed),
            'liquidated': len(works_failed[works_failed['Disposition'] == 'Liquidate']),
            'sellable': len(works_failed[works_failed['Disposition'] == 'Sellable']),
            'liquidation_rate': len(works_failed[works_failed['Disposition'] == 'Liquidate']) / len(works_failed) * 100 if len(works_failed) > 0 else 0
        }
    
    # Path 8: IOG -> Problem Solve
    if 'IOG' in key_checks:
        iog = df[df[key_checks['IOG']] == 'Failed']  # "Is it IOG?" -> No means Failed
        paths['Path_8_IOG'] = {
            'description': 'Is it IOG? -> No -> Problem Solve',
            'total_count': len(iog),
            'liquidated': len(iog[iog['Disposition'] == 'Liquidate']),
            'sellable': len(iog[iog['Disposition'] == 'Sellable']),
            'problem_solve_rate': len(iog) / len(df) * 100 if len(df) > 0 else 0
        }
    
    return paths

def analyze_pattern_frequency(df, key_checks):
    """Analyze frequency of check combinations"""
    # Create binary pattern (simplified)
    pattern_data = []
    
    for idx, row in df.iterrows():
        pattern = {}
        for check_name, col in key_checks.items():
            value = row[col]
            if pd.notna(value):
                pattern[check_name] = 1 if value == 'Passed' else 0
            else:
                pattern[check_name] = -1  # Not checked
        
        pattern['Disposition'] = row['Disposition']
        pattern['LPN'] = row['LPN']
        pattern_data.append(pattern)
    
    pattern_df = pd.DataFrame(pattern_data)
    
    # Find most common patterns
    pattern_cols = [col for col in pattern_df.columns if col not in ['Disposition', 'LPN']]
    
    # Group by pattern and disposition
    pattern_summary = pattern_df.groupby(pattern_cols + ['Disposition']).size().reset_index(name='count')
    
    return {
        'total_unique_patterns': len(pattern_summary),
        'most_common_patterns': pattern_summary.nlargest(20, 'count').to_dict('records')
    }

def create_visualizations(results, df, key_checks):
    """Create visualizations of execution patterns"""
    print("Creating visualizations...")
    
    # 1. Top Liquidation Patterns
    liquidated_patterns = results['patterns']['liquidated_top_20']
    if liquidated_patterns:
        fig, ax = plt.subplots(figsize=(16, 10))
        patterns = list(liquidated_patterns.keys())[:15]
        counts = list(liquidated_patterns.values())[:15]
        
        # Truncate long pattern names
        patterns_short = [p[:80] + '...' if len(p) > 80 else p for p in patterns]
        
        ax.barh(range(len(patterns_short)), counts)
        ax.set_yticks(range(len(patterns_short)))
        ax.set_yticklabels(patterns_short, fontsize=9)
        ax.set_xlabel('Number of Orders', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 Execution Patterns Leading to Liquidation', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        plt.savefig('Execution_Patterns_Top_Liquidation_Patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Top Sellable Patterns
    sellable_patterns = results['patterns']['sellable_top_20']
    if sellable_patterns:
        fig, ax = plt.subplots(figsize=(16, 10))
        patterns = list(sellable_patterns.keys())[:15]
        counts = list(sellable_patterns.values())[:15]
        
        patterns_short = [p[:80] + '...' if len(p) > 80 else p for p in patterns]
        
        ax.barh(range(len(patterns_short)), counts, color='green')
        ax.set_yticks(range(len(patterns_short)))
        ax.set_yticklabels(patterns_short, fontsize=9)
        ax.set_xlabel('Number of Orders', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 Execution Patterns Leading to Sellable', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        plt.savefig('Execution_Patterns_Top_Sellable_Patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Decision Path Analysis
    paths = results['decision_paths']
    if paths:
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        axes = axes.flatten()
        
        path_names = list(paths.keys())[:8]
        for idx, path_name in enumerate(path_names[:4]):
            path_data = paths[path_name]
            ax = axes[idx]
            
            labels = ['Liquidated', 'Sellable']
            sizes = [path_data['liquidated'], path_data['sellable']]
            colors = ['#fa709a', '#4facfe']
            
            if sum(sizes) > 0:
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                ax.set_title(f"{path_data['description'][:50]}...", fontsize=10, fontweight='bold')
        
        plt.suptitle('Decision Path Analysis - Distribution by Disposition', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('Execution_Patterns_Decision_Paths.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print("Visualizations created successfully!")

def main():
    """Main execution"""
    print("=" * 80)
    print("Quality Check Execution Pattern Analysis")
    print("=" * 80)
    
    # Load data
    df = load_data()
    
    # Analyze patterns
    results, df_enhanced, key_checks = analyze_execution_patterns(df)
    
    # Create visualizations
    create_visualizations(results, df_enhanced, key_checks)
    
    # Save results
    output_file = 'Repair Order (repair.order)_preprocessed_features_execution_patterns.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")
    print("\nSummary:")
    print(f"Total Orders: {results['total_orders']}")
    print(f"Liquidated: {results['liquidated_count']}")
    print(f"Sellable: {results['sellable_count']}")
    print(f"Key Checks Analyzed: {len(results['key_checks_used'])}")
    print(f"Decision Paths Analyzed: {len(results['decision_paths'])}")
    print(f"Top Liquidation Patterns: {len(results['patterns']['liquidated_top_20'])}")
    print(f"Top Sellable Patterns: {len(results['patterns']['sellable_top_20'])}")

if __name__ == "__main__":
    main()

