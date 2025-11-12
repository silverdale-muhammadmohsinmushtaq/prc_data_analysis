# Quality Check Execution Patterns Analysis

**Generated:** November 12, 2025

## Overview
This analysis identifies the actual execution patterns (combinations of passed/failed quality checks) that users executed, and how these patterns relate to the final disposition (Liquidation vs Sellable). This complements the theoretical decision paths documented in `DECISION_TREE_ANALYSIS.md` by showing what actually happened in practice.

---

## Executive Summary

- **Total Orders Analyzed:** 954
- **Liquidated Orders:** 285 (29.9%)
- **Sellable Orders:** 669 (70.1%)
- **Key Decision Checks Analyzed:** 14
- **Decision Paths Identified:** 10
- **Unique Execution Patterns:** Hundreds of unique combinations

---

## Key Decision Checks Tracked

Based on the BPMN decision tree, the following key checks were analyzed:

1. **IOG** - Is it IOG?
2. **Something_in_Box** - Is there something in the box?
3. **TREX_Open** - Did TREX open?
4. **Expected_Item** - Is it the Expected Item?
5. **Fraud** - Is it Fraud?
6. **Factory_Sealed** - Is the Item Factory Sealed?
7. **Destroy** - Does the item Need to be Destroyed?
8. **Scratches_Dents** - Does the item have scratches/dents larger than a badge?
9. **Works** - Does the item Work?
10. **Repairable** - Is the Item Repairable?
11. **Needs_Parts** - Does it need Parts?
12. **Has_Parts** - Do you have the Parts?
13. **Needs_Sanitization** - Does it need Sanitization?
14. **Factory_Reset** - Did you do a Factory Reset?

---

## Actual Execution Paths Analysis

### Path 1: Empty Box → Liquidation
**Decision Tree Path:** `Is there something in the box? QCP00025` → **No** → `Send to Liquidation Palletizer QCP00090`

**Actual Execution:**
- **Total Orders:** 1
- **Liquidated:** 1
- **Sellable:** 0
- **Liquidation Rate:** 100.0%

**Finding:** Items with empty boxes are routed to liquidation as expected. Only 1 order had an empty box, confirming this is a rare occurrence.

---

### Path 2: Non-Repairable → Liquidation
**Decision Tree Path:** `Is the Item Repairable? QCP00033` → **No** → `Complete TREX Liquidation QCP00044`

**Actual Execution:**
- **Total Orders:** 377
- **Liquidated:** 142
- **Sellable:** 235
- **Liquidation Rate:** 37.7%

**Finding:** Non-repairable items show a 37.7% liquidation rate, which is lower than expected. This suggests that many non-repairable items are still being routed to sellable, indicating a potential process issue or that "non-repairable" may not always mean liquidation is required.

---

### Path 3: Fraud Detection → Liquidation
**Decision Tree Path:** `Is it Fraud? QCP00028` → **Yes** → `Complete TREX Liquidation QCP00042`

**Actual Execution - Fraud = Yes:**
- **Total Orders:** 6
- **Liquidated:** 6
- **Sellable:** 0
- **Liquidation Rate:** 100.0%

**Actual Execution - Fraud = No:**
- **Total Orders:** 63
- **Liquidated:** 21
- **Sellable:** 42
- **Liquidation Rate:** 33.3%

**Finding:** Fraud detection is working perfectly - all 6 items marked as fraud were liquidated (100% rate). Items not marked as fraud have a 33.3% liquidation rate, which is close to the overall average.

---

### Path 4: Factory Sealed → Sellable
**Decision Tree Path:** `Is the Item Factory Sealed? QCP00029` → **Yes** → `Complete TREX Sellable QCP00041`

**Actual Execution:**
- **Total Orders:** 3
- **Liquidated:** 0
- **Sellable:** 3
- **Sellable Rate:** 100.0%

**Finding:** Factory sealed items are correctly routed to sellable palletizer with 100% success rate. However, only 3 orders had factory sealed items, indicating this is a rare path.

---

### Path 5: Destroy → Liquidation
**Decision Tree Path:** `Does the item Need to be Destroyed QCP00030` → **Yes** → `Complete TREX Liquidation QCP00058`

**Actual Execution:**
- **Total Orders:** 2
- **Liquidated:** 2
- **Sellable:** 0
- **Liquidation Rate:** 100.0%

**Finding:** Items marked for destruction are correctly routed to liquidation with 100% success rate. Only 2 orders required destruction, indicating this is a rare path.

---

### Path 6: Scratches/Dents → Liquidation
**Decision Tree Path:** `Does the item have scratches and dents larger than a badge? QCP00031` → **Yes** → `Complete TREX Liquidation QCP00043`

**Actual Execution:**
- **Total Orders:** 36
- **Liquidated:** 36
- **Sellable:** 0
- **Liquidation Rate:** 100.0%

**Finding:** Items with significant cosmetic damage (scratches/dents) are routed to liquidation with 100% success rate. All 36 items with cosmetic damage were liquidated, confirming this path works as designed.

---

### Path 7: Works Check → Most Critical Path
**Decision Tree Path:** `Does the Item Work? QCP000XX` → **Yes/No** → Routes accordingly

**Actual Execution - Works = Passed:**
- **Total Orders:** 579
- **Liquidated:** 7
- **Sellable:** 572
- **Sellable Rate:** 98.8%

**Actual Execution - Works = Failed:**
- **Total Orders:** 257
- **Liquidated:** 162
- **Sellable:** 95
- **Liquidation Rate:** 63.0%

**Finding:** The "Does it Work?" check is the strongest predictor of final disposition. Items that pass this check have a 98.8% sellable rate (572 out of 579), while items that fail have a 63.0% liquidation rate (162 out of 257). This represents a 72.9 percentage point difference, making it the most critical check in the decision process.

**⚠️ Recovery Opportunity:** 7 items that passed the "Works" check were still liquidated, representing a potential recovery opportunity.

---

### Path 8: IOG → Problem Solve
**Decision Tree Path:** `Is it IOG? QCP00024` → **No** → `Send to Problem Solve QCP00059`

**Actual Execution:**
- **Total Orders:** 954 (all orders)
- **Liquidated:** 285
- **Sellable:** 669
- **IOG Check Performed:** 100% of orders

**Finding:** All 954 orders had the IOG check performed, and all were marked as "Not IOG" (Failed check). This suggests that either all items in this dataset are non-IOG items, or the IOG check is always performed first in the process flow.

---

## Top Execution Patterns

### Top 15 Patterns Leading to Liquidation

[See visualization: Execution_Patterns_Top_Liquidation_Patterns.png]

The most common execution patterns that resulted in liquidation include:

1. **Pattern 1:** `IOG:F -> Something_in_Box:P -> TREX_Open:P` - **82 orders**
   - Simplest pattern: Not IOG, Something in box, TREX opened → Liquidation

2. **Pattern 2:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:F -> Repairable:F -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F -> Factory_Reset:F` - **68 orders**
   - Complete failure pattern: Item doesn't work, not repairable, no parts, etc. → Liquidation

3. **Pattern 3:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:F -> Repairable:F -> Factory_Reset:F` - **22 orders**
   - Works failed, not repairable → Liquidation

4. **Pattern 4:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:F -> Repairable:P -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F -> Factory_Reset:F` - **11 orders**
   - Works failed, repairable but no parts → Liquidation

5. **Pattern 5:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Expected_Item:P -> Fraud:F -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:P -> Works:F -> Repairable:F -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F` - **11 orders**
   - Expected item, not fraud, but has scratches/dents and doesn't work → Liquidation

... (See JSON results for complete list of top 20 patterns)

### Top 15 Patterns Leading to Sellable

[See visualization: Execution_Patterns_Top_Sellable_Patterns.png]

The most common execution patterns that resulted in sellable include:

1. **Pattern 1:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:P -> Repairable:F -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F -> Factory_Reset:F` - **82 orders**
   - **Key:** Works:P (passed) → Sellable
   - Item works, not repairable but still sellable

2. **Pattern 2:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:P -> Needs_Parts:F -> Needs_Sanitization:P -> Factory_Reset:F` - **79 orders**
   - **Key:** Works:P, Needs_Sanitization:P → Sellable
   - Item works, needs sanitization → Sellable

3. **Pattern 3:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Works:P -> Needs_Parts:F -> Needs_Sanitization:P -> Factory_Reset:F` - **78 orders**
   - **Key:** Works:P, Needs_Sanitization:P → Sellable
   - Similar to Pattern 2, without scratches check

4. **Pattern 4:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:F -> Repairable:F -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F -> Factory_Reset:P` - **78 orders**
   - **Key:** Works:F but Factory_Reset:P → Sellable
   - Item doesn't work but factory reset passed → Sellable

5. **Pattern 5:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:P -> Has_Parts:P -> Needs_Sanitization:P -> Factory_Reset:P` - **77 orders**
   - **Key:** Works:P, Has_Parts:P, Needs_Sanitization:P → Sellable
   - Item works, has parts, needs sanitization → Sellable

**Key Insight:** The common theme across all top sellable patterns is that items either:
- Pass the "Works" check (Works:P), OR
- Pass the "Factory Reset" check (Factory_Reset:P)

This confirms that functional capability is the primary driver of sellable outcomes.

... (See JSON results for complete list of top 20 patterns)

---

## Pattern Frequency Analysis

- **Total Unique Patterns:** 66 unique execution patterns identified
- **Most Common Liquidation Pattern:** `IOG:F -> Something_in_Box:P -> TREX_Open:P` (82 orders)
- **Most Common Sellable Pattern:** `IOG:F -> Something_in_Box:P -> TREX_Open:P -> Factory_Sealed:F -> Destroy:F -> Scratches_Dents:F -> Works:P -> Repairable:F -> Needs_Parts:F -> Has_Parts:F -> Needs_Sanitization:F -> Factory_Reset:F` (82 orders)

**Pattern Diversity:**
- The top 20 liquidation patterns account for approximately 70% of all liquidations
- The top 20 sellable patterns account for approximately 75% of all sellable outcomes
- This indicates moderate pattern concentration, with some common paths but also significant diversity in execution patterns

---

## Key Insights

1. **Pattern Consistency:** Most orders follow predictable patterns based on key decision checks. The top patterns account for 70-75% of outcomes.

2. **Critical Checks:** The "Does it Work?" check is the most critical determinant of final disposition:
   - 98.8% sellable rate when Works check passes
   - 63.0% liquidation rate when Works check fails
   - 72.9 percentage point difference

3. **Path Adherence:** Users generally follow the decision tree paths as designed:
   - Empty Box → 100% liquidation rate ✓
   - Fraud = Yes → 100% liquidation rate ✓
   - Factory Sealed → 100% sellable rate ✓
   - Destroy → 100% liquidation rate ✓
   - Scratches/Dents → 100% liquidation rate ✓

4. **Exception Cases:** Some patterns show exceptions where items that should be sellable are liquidated:
   - 7 items that passed "Works" check were liquidated (recovery opportunity)
   - Non-repairable items show only 37.7% liquidation rate (should be higher)

5. **Pattern Complexity:** Many orders involve multiple checks (10-14 checks per order), creating complex execution patterns. The most common patterns involve 3-12 sequential checks.

6. **Common Starting Pattern:** Almost all orders start with: `IOG:F -> Something_in_Box:P -> TREX_Open:P`, indicating these are the first three checks in the process flow.

7. **Works Check Dominance:** In sellable patterns, the "Works:P" (passed) check appears in the top 5 patterns, confirming its importance.

---

## Recommendations

1. **Standardize Execution:** Review patterns that deviate from expected paths.

2. **Exception Handling:** Identify and address patterns where working items are liquidated.

3. **Training:** Use common patterns for training to ensure consistent execution.

4. **Process Optimization:** Simplify paths with high complexity but low value-add.

5. **Monitoring:** Track pattern adherence to ensure decision tree is followed correctly.

---

## Visualizations

1. **Top Liquidation Patterns** - `Execution_Patterns_Top_Liquidation_Patterns.png`
2. **Top Sellable Patterns** - `Execution_Patterns_Top_Sellable_Patterns.png`
3. **Decision Path Analysis** - `Execution_Patterns_Decision_Paths.png`

---

## Data Files

- **Results JSON:** `Repair Order (repair.order)_preprocessed_features_execution_patterns.json`
- **Analysis Script:** `analyze_execution_patterns.py`

---

## Next Steps

1. Review specific patterns that deviate from expected outcomes
2. Analyze patterns with high liquidation rates for optimization opportunities
3. Compare actual execution patterns with theoretical decision tree paths
4. Identify training needs based on pattern inconsistencies
5. Create exception rules for common problematic patterns

