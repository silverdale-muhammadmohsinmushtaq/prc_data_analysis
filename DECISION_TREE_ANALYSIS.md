# Amazon Repair Product Routing Decision Tree Analysis

## Overview
This BPMN diagram represents a decision tree that routes Amazon Repair Products to one of four destinations:
1. **Problem Solver** - For items requiring problem resolution
2. **Liquidation Palletizer** - For items to be liquidated
3. **Sellable Palletizer** - For items that can be sold
4. **Cleaner** - For items requiring cleaning (multiple paths)

## Entry Point
**Start**: `Print LPN label QCP00022`

## Destination Paths

### 1. Problem Solver Paths

#### Path A: IOG Items
- **Start** → `Is it IOG? QCP00024` → **No** → `Send to Problem Solve QCP00059` → **Problem Solve**

#### Path B: TREX Failed to Open
- `Did TREX open? QCP284220` → **No** → `Send to Problem Solve QCP284221` → **Problem Solve**

---

### 2. Liquidation Palletizer Paths

The **Liquidation Palletizer** receives items from 7 different paths:

#### Path 1: Empty Box
- `Is there something in the box? QCP00025` → **No** → `Send to Liquidation Palletizer QCP00090` → **Liquidation Palletizer**

#### Path 2: Non-Repairable Items
- `Is the Item Repairable? QCP00033` → **No** → `Complete TREX Liquidation QCP00044` → **Liquidation Palletizer**

#### Path 3: Fraud Detection - Yes
- `Is it Fraud? QCP00028` → **Yes** → `Complete TREX Liquidation QCP00042` → **Liquidation Palletizer**

#### Path 4: Fraud Detection - No
- `Is it Fraud? QCP00028` → **No** → `Complete TREX Liquidation QCP00040` → **Liquidation Palletizer**

#### Path 5: Destroyed Items
- `Does the item Need to be Destroyed QCP00030` → **Yes** → `Complete TREX Liquidation QCP00058` → **Liquidation Palletizer**

#### Path 6: Scratches/Dents
- `Does the item have scratches and dents larger than a badge? QCP00031` → **Yes** → `Complete TREX Liquidation QCP00043` → **Liquidation Palletizer**

#### Path 7: Non-Repairable (Alternative Path)
- `Is the Item Repairable QCP00046` → **No** → `Complete TREX Liquidation QCP00049` → **Liquidation Palletizer**

---

### 3. Sellable Palletizer Paths

#### Path: Factory Sealed Items
- `Is the Item Factory Sealed? QCP00029` → **Yes** → `Complete TREX Sellable QCP00041` → **Sellable Palletizer**

---

### 4. Cleaner Paths

The **Cleaner** receives items from **30+ different paths**, all following various "Complete TREX Sellable" tasks. These paths represent items that:
- Pass quality checks
- Are repairable
- Meet sellable criteria
- Complete various TREX sellable workflows

**Key Cleaner Entry Points:**
- `Complete TREX Sellable QCP00217` → **Cleaner**
- `Complete TREX Sellable QCP284041` → **Cleaner**
- `Complete TREX Sellable QCP284040` → **Cleaner**
- `Complete TREX Sellable QCP284039` → **Cleaner**
- `Complete TREX Sellable QCP284038` → **Cleaner**
- `Complete TREX Sellable QCP244274` → **Cleaner**
- `Complete TREX Sellable QCP244275` → **Cleaner**
- `Complete TREX Sellable QCP244276` → **Cleaner**
- `Complete TREX Sellable QCP244277` → **Cleaner**
- `Complete TREX Sellable QCP00220` → **Cleaner**
- `Complete TREX Sellable QCP244281` → **Cleaner**
- `Complete TREX Sellable QCP244282` → **Cleaner**
- `Complete TREX Sellable QCP00218` → **Cleaner**
- `Complete TREX Sellable QCP244284` → **Cleaner**
- `Complete TREX Sellable QCP00219` → **Cleaner**
- `Complete TREX Sellable QCP244285` → **Cleaner**
- `Complete TREX Sellable QCP244287` → **Cleaner**
- `Complete TREX Sellable QCP244294` → **Cleaner**
- `Complete TREX Sellable QCP244293` → **Cleaner**
- `Complete TREX Sellable QCP244291` → **Cleaner**
- `Complete TREX Sellable QCP244292` → **Cleaner**
- `Complete TREX Sellable QCP00214` → **Cleaner**
- `Complete TREX Sellable QCP00213` → **Cleaner**
- `Complete TREX Sellable QCP244290` → **Cleaner**
- `Complete TREX Sellable QCP284045` → **Cleaner**
- `Complete TREX Sellable QCP284046` → **Cleaner**
- `Complete TREX Sellable QCP284048` → **Cleaner**
- `Complete TREX Sellable QCP284047` → **Cleaner**
- `Complete TREX Sellable QCP00216` → **Cleaner**
- `Complete TREX Sellable QCP244289` → **Cleaner**
- `Complete TREX Sellable QCP244288` → **Cleaner**
- `Complete TREX Sellable QCP244286` → **Cleaner**

---

## Key Decision Points

### Primary Decision Tree Structure:
1. **Print LPN label** (Start)
2. **Is it IOG?** → Routes to Problem Solve if No
3. **Is there something in the box?** → Routes to Liquidation if No
4. **Did TREX open?** → Routes to Problem Solve if No
5. **Is it the Expected Item?**
6. **Is it Fraud?**
7. **Is the Item Factory Sealed?** → Routes to Sellable Palletizer if Yes
8. **Does the item Need to be Destroyed?**
9. **Does the item have scratches and dents larger than a badge?**
10. **Did you do a Factory Reset?**
11. **Does the Item Work?**
12. **Is the Item Repairable?**
13. **Does it need Parts?**
14. **Does it need Sanitization?** (Multiple instances)
15. **Does it need a Manual?** (Multiple instances)
16. **Are you using Harvested Parts?** (Multiple instances)
17. **Will you be using ONLY Harvested Parts?**
18. **Do you have the Parts?**

---

## Process Flow Summary

The decision tree evaluates products through multiple quality checkpoints (QCP codes) to determine:
- **Problem Solve**: Items with issues requiring resolution
- **Liquidation**: Items that cannot be sold or repaired
- **Sellable**: Items ready for sale (factory sealed)
- **Cleaner**: Items that pass quality checks and need cleaning before sale

Each path includes specific TREX completion tasks that track the product through the system.

