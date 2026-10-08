---
name: Assets Skill
description: Fixed asset management, capitalization, depreciation schedules, location movements, maintenance logs, and asset scrap/disposal.
version: 1.0.0
module: Assets
---

# Fixed Assets Domain Skill

## 1. Domain Overview
The **Assets** module oversees capital equipment, machinery, IT hardware, and vehicles throughout their operational lifecycle, managing acquisition, scheduled depreciation, physical movement, and retirement.

### Key Entities:
1. **Asset Category**: Classification governing standard depreciation method (Straight Line, Double Declining, Written Down Value), frequency, and linked accounting ledger books (Fixed Asset, Accumulated Depreciation, Depreciation Expense).
2. **Asset**: Individual capital unit with serial number, gross purchase value, custodian, location, and depreciation books.
3. **Asset Movement**: Submittable document recording reassignment of an asset to a new employee/custodian or physical warehouse/location.
4. **Asset Depreciation Schedule**: Auto-generated posting schedule calculating period depreciation expense.
5. **Asset Repair**: Maintenance log recording repair costs and deciding whether to capitalize costs into asset value.

---

## 2. Field Requirements & Rules

### Asset
- **item_code** (Link Item, Required): Master item (must have `is_fixed_asset = 1`).
- **asset_name** (Data, Required).
- **company** (Link Company, Required).
- **asset_category** (Link Asset Category, Required).
- **gross_purchase_amount** (Currency, Required, > 0).
- **purchase_date** (Date, Required).
- **available_for_use_date** (Date, Required).
- **location** (Link Location, Optional).
- **custodian** (Link Employee, Optional).

### Asset Movement
- **company** (Link Company, Required).
- **transaction_date** (Date, Required).
- **purpose** (Select: "Transfer", "Issue", "Receipt", Required).
- **assets** (Table Asset Movement Item, Required):
  - **asset** (Link Asset, Required)
  - **target_location** (Link Location)
  - **to_employee** (Link Employee)

---

## 3. Workflow & Lifecycle Transitions
- `Asset`: Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting an Asset locks the purchase cost and activates the automated depreciation schedule.
- `Asset Movement`: Draft (0) -> Submitted (1) -> Cancelled (2).
