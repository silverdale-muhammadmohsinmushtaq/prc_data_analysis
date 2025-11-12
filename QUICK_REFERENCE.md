# Quick Reference: Liquidation Decision Points

## Critical Decision Points Leading to Liquidation

Based on your BPMN diagram, these are the 7 main paths to Liquidation Palletizer:

| Path # | Decision Point | QCP Code | Answer | Impact |
|--------|---------------|----------|--------|--------|
| 1 | Is there something in the box? | QCP00025 | **No** | Empty box → Liquidation |
| 2 | Is the Item Repairable? | QCP00033 | **No** | Non-repairable → Liquidation |
| 3 | Is it Fraud? | QCP00028 | **Yes** | Fraud detected → Liquidation |
| 4 | Is it Fraud? | QCP00028 | **No** | (Alternative path) → Liquidation |
| 5 | Does the item Need to be Destroyed? | QCP00030 | **Yes** | Must destroy → Liquidation |
| 6 | Scratches/dents larger than badge? | QCP00031 | **Yes** | Too damaged → Liquidation |
| 7 | Is the Item Repairable? | QCP00046 | **No** | Non-repairable (alt path) → Liquidation |

---

## High COGS Analysis Focus Areas

When analyzing high COGS items (≥$1000) being liquidated, pay special attention to:

### 1. **QCP00031 - Scratches/Dents**
- **Question**: "Does the item have scratches and dents larger than a badge?"
- **Issue**: Minor cosmetic damage shouldn't liquidate high-value items
- **Action**: Review if threshold is too strict for expensive items

### 2. **QCP00033 & QCP00046 - Repairability**
- **Question**: "Is the Item Repairable?"
- **Issue**: High-value items might be worth repairing even if complex
- **Action**: Consider repair cost vs COGS for expensive items

### 3. **QCP00028 - Fraud Detection**
- **Question**: "Is it Fraud?"
- **Issue**: False positives could liquidate legitimate high-value items
- **Action**: Review fraud detection accuracy for expensive items

### 4. **QCP00030 - Destruction Requirement**
- **Question**: "Does the item Need to be Destroyed?"
- **Issue**: High-value items might have salvage value
- **Action**: Implement exception review before destruction

---

## Data Collection Checklist

To perform the analysis, ensure your data includes:

- [ ] Product ID
- [ ] COGS value
- [ ] Final destination (Liquidation/Sellable)
- [ ] QCP00025 answer (Box contents)
- [ ] QCP00028 answer (Fraud)
- [ ] QCP00030 answer (Destruction)
- [ ] QCP00031 answer (Scratches/dents)
- [ ] QCP00033 answer (Repairable - path 1)
- [ ] QCP00046 answer (Repairable - path 2)
- [ ] QCP00029 answer (Factory sealed) - for comparison
- [ ] QCP00037/QCP00045 answer (Item works) - for comparison

---

## Quick Analysis Questions

Answer these to understand your liquidation problem:

1. **What percentage of items go to Liquidation?**
   - Target: <30% (adjust based on your business)
   - If higher: Identify top reason

2. **What percentage of high COGS items (≥$1000) go to Liquidation?**
   - Target: <10% (high-value items should be preserved)
   - If higher: Critical issue - review immediately

3. **Which QCP code has the highest "No" → Liquidation rate?**
   - This is your primary problem area

4. **Are high COGS items failing different checks than low COGS items?**
   - Compare liquidation reasons between high/low COGS groups

5. **What's the total value lost to unnecessary liquidations?**
   - Calculate: Sum of COGS for items that could be sellable

---

## Recommended Actions Based on Findings

### If QCP00031 (Scratches/Dents) is high:
- **Action**: Relax cosmetic damage criteria for items >$500 COGS
- **BPMN Change**: Add COGS check before QCP00031

### If QCP00033/QCP00046 (Repairable) is high:
- **Action**: Calculate repair cost vs COGS ratio
- **BPMN Change**: Add repair cost analysis step

### If QCP00028 (Fraud) is high:
- **Action**: Review fraud detection accuracy
- **BPMN Change**: Add manual review for high COGS + fraud flag

### If QCP00030 (Destruction) is high:
- **Action**: Implement salvage value assessment
- **BPMN Change**: Add exception review before destruction

### If QCP00025 (Empty Box) is high:
- **Action**: Review receiving process
- **BPMN Change**: Add verification step before routing

---

## Expected Analysis Output

The `liquidation_analyzer.py` will show:

```
1. OVERALL STATISTICS
   - Total Items: X
   - Liquidation Rate: X%
   
2. HIGH COGS ANALYSIS
   - High COGS Items: X
   - High COGS → Liquidation: X% (TARGET: <10%)
   - Total Value Lost: $X
   
3. LIQUIDATION REASON ANALYSIS
   - Top reason: [QCP Code] with X items
   
4. DECISION POINT ANALYSIS
   - Each QCP code's impact on liquidation
   
5. RECOMMENDATIONS
   - Specific actions to take
```

---

## Next Steps

1. **Collect Data**: Export quality check results from your system
2. **Run Analysis**: Use `liquidation_analyzer.py`
3. **Review Results**: Identify top 3 problem areas
4. **Take Action**: Modify BPMN or add exception handling
5. **Monitor**: Track improvement after changes


