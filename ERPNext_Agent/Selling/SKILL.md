---
name: Selling Skill
description: Sales pipeline, customer management, quotations, sales orders, accounts receivable, and credit limits.
version: 1.0.0
module: Selling
---

# Selling & Commercial Domain Skill

## 1. Domain Overview
The **Selling** module manages customer relationships and outbound sales transactions from prospect acquisition through quotation and confirmed order booking.

### Key Entities:
1. **Customer**: Client master record. Specifies payment terms, currency, billing currency, default price list, and credit limits.
2. **Customer Group**: Categorization tree node (e.g., "Commercial", "Industrial", "Government").
3. **Quotation**: Formal price quote issued to a lead or customer with validity dates.
4. **Sales Order (SO)**: Submittable sales contract confirming customer purchase. Triggers reservation of stock or creates production demands (via Production Plan / Work Order).
5. **Sales Invoice (SI)**: Submittable billing document recognizing revenue and posting Accounts Receivable.

---

## 2. Field Requirements & Rules

### Customer
- **customer_name** (Data, Required).
- **customer_group** (Link Customer Group, Required, default "All Customer Groups" or "Individual").
- **customer_type** (Select: "Company" or "Individual", Default "Company").
- **territory** (Link Territory, Required, default "All Territories").

### Sales Order
- **customer** (Link Customer, Required).
- **company** (Link Company, Required).
- **transaction_date** (Date, Required, defaults to today).
- **delivery_date** (Date, Required): Committed fulfillment date.
- **items** (Table Sales Order Item, Required):
  - **item_code** (Link Item, Required)
  - **qty** (Float, Required, > 0)
  - **rate** (Currency, Required, >= 0)
  - **delivery_date** (Date, Required)

---

## 3. Workflow & Lifecycle Transitions
- `Sales Order`:
  - Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting changes status to `To Deliver and Bill`.
  - Can be progressed to `Delivery Note` (Stock fulfillment) and `Sales Invoice` (Accounts Receivable).

---

## 4. Edge Cases & Constraints
1. **Stock Reservation**: If stock reservation is enabled in Stock Settings, submitting a Sales Order reserves stock against available inventory.
2. **Credit Limit Enforcement**: If customer exceeds credit limit, submitting Sales Order requires authorization bypass or fails.
