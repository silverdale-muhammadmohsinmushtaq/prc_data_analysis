# Data Documentation: Liquidation Analysis

**Generated:** November 12, 2025

---

## Data Dictionary

### Order-Level Columns

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| LPN | String | License Plate Number - Unique identifier for each repair order |
| Amazon COGS | Float | Cost of Goods Sold - Financial value of the product |
| Disposition | String | Final outcome: 'Sellable' or 'Liquidate' |
| Product | String | Product identifier/name |
| Product Category | String | Product category classification |
| Result of Repair | String | Specific reason for liquidation (if liquidated) |
| Started On | DateTime | When repair process started |
| Completed On | DateTime | When repair process completed |
| Scheduled Date | DateTime | Scheduled completion date |
| Shipped Date | DateTime | When item was shipped (if applicable) |

### Quality Check Columns

Quality check columns represent individual checks performed during the repair process.
Each check can have values: 'Passed', 'Failed', or NaN (not applicable).

**Key Quality Checks:**

- Does_the_item_work_El_art_culo_funciona
- Is_it_Fraud_Es_fraude
- Is_the_item_Repairable_El_art_culo_es_reparable
- Does_the_item_have_scratches_or_dents_larger_that_
- Is_the_Item_Factory_Sealed_El_art_culo_est_sellado

### Derived Features

| Feature | Description |
|---------|-------------|
| is_liquidated | Binary flag: 1 if liquidated, 0 if sellable |
| cogs_bin | COGS value binned into ranges |
| processing_days | Days from 'Started On' to 'Completed On' |
| category_group | Grouped product categories |
| total_checks | Total number of checks performed |
| failed_checks_count | Number of failed checks |
| passed_checks_count | Number of passed checks |
| failure_rate | Percentage of checks that failed |
| works_check_passed | Binary: 1 if 'Does it work?' passed |
| fraud_check_failed | Binary: 1 if fraud check failed |
| cosmetic_check_failed | Binary: 1 if cosmetic check failed |
| repairable_check_failed | Binary: 1 if repairable check failed |
| value_lost | COGS value if liquidated, 0 otherwise |
| recovery_potential | COGS value if working item was liquidated |

## Business Rules

### Data Filtering Rules

1. **Human-Executed Checks Only:** Only quality checks where 'Checks/Failed by decision logic Automatically' is False or empty are included
2. **Multi-Row Data:** Quality checks for a single repair order are spread across multiple rows, transformed to wide format
3. **Missing Values:** Missing check values indicate the check was not performed or not applicable

### Disposition Rules

- **Sellable:** Item passed quality checks and can be sold
- **Liquidate:** Item failed critical checks and must be liquidated
- Liquidation reasons include: Functional Issues, Fraud, Cosmetic Issues, Wrong Item Description

## Known Data Quality Issues

1. **Multi-Row Format:** Original data had quality checks in multiple rows per order - transformed to wide format
2. **Missing Dates:** Some orders have missing date fields - handled in preprocessing
3. **Inconsistent Check Names:** Some checks have slight variations in naming - standardized during preprocessing
4. **Automated Checks:** Checks marked as 'Failed by decision logic Automatically' were excluded from analysis

