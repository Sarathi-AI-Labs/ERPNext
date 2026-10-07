---
name: Buying Skill
description: Vendor management, procurement lifecycle, purchase requisitions, RFQs, purchase orders, vendor invoices, and landed cost allocations.
version: 1.0.0
module: Buying
---

# Buying & Procurement Domain Skill

## 1. Domain Overview
The **Buying** module handles supplier interactions and inbound purchasing workflows. Procurement connects requisitions from manufacturing and stock through purchase orders to vendor invoices.

### Key Entities:
1. **Supplier**: Vendor master record. Defines default supplier currency, payment terms, and accounts.
2. **Supplier Group**: Hierarchical classification for vendors (e.g., "Hardware", "Raw Materials", "Services").
3. **Request for Quotation (RFQ)**: Document sent to one or multiple vendors to invite commercial pricing.
4. **Supplier Quotation**: Commercial proposal received from a vendor with rate and delivery lead times.
5. **Purchase Order (PO)**: Legal commitment issued to a vendor specifying items, quantities, rates, tax templates, and expected delivery schedule.
6. **Purchase Invoice (PI)**: Accounts payable bill generated against a PO or Purchase Receipt.

---

## 2. Field Requirements & Rules

### Supplier
- **supplier_name** (Data, Required): Official vendor name.
- **supplier_group** (Link Supplier Group, Required).
- **supplier_type** (Select: "Company" or "Individual", Default "Company").
- **country** (Link Country, Optional).

### Purchase Order
- **supplier** (Link Supplier, Required).
- **company** (Link Company, Required).
- **transaction_date** (Date, Required, defaults to today).
- **schedule_date** (Date, Required): Expected delivery date.
- **items** (Table Purchase Order Item, Required):
  - **item_code** (Link Item, Required)
  - **qty** (Float, Required, > 0)
  - **rate** (Currency, Required, >= 0)
  - **schedule_date** (Date, Required)
  - **warehouse** (Link Warehouse, Required for stock items)

---

## 3. Workflow & Lifecycle Transitions
- `Purchase Order`:
  - Draft (0) -> Submitted (1) -> Cancelled (2).
  - Can be partially received (via `Purchase Receipt`) or partially billed (via `Purchase Invoice`).
  - Status progression: `Draft` -> `To Receive and Bill` -> `To Bill` / `To Receive` -> `Completed`.
- `Purchase Invoice`:
  - Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting posts General Ledger entries (`Creditors` credit, expense/asset debit).

---

## 4. Edge Cases & Constraints
1. **Currency Matching**: If supplier has a fixed foreign currency, PO currency must match or appropriate exchange rate must be set.
2. **Mandatory Delivery Warehouse**: Any stock item in a PO item row must specify a valid target warehouse belonging to the designated company.
