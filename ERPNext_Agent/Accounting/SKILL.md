---
name: Accounting Skill
description: Chart of accounts, General Ledger (GL), double-entry bookkeeping, Journal Entries, Payment Entries, accounts payable, accounts receivable, and tax templates.
version: 1.0.0
module: Accounting
---

# Accounting & Financial Domain Skill

## 1. Domain Overview
The **Accounting** module maintains the general ledger, enforces double-entry bookkeeping, records cash/bank receipts and disbursements, and calculates tax liabilities.

### Key Entities:
1. **Account**: Chart of Accounts tree node. Root types: `Asset`, `Liability`, `Equity`, `Income`, `Expense`. Transactions can only post to leaf accounts (`is_group = 0`).
2. **Journal Entry (JV)**: Submittable multi-currency financial entry where total debits must strictly equal total credits.
3. **Payment Entry**: Standard document for receipts from customers, payments to suppliers, internal transfers, and advance allocations.
4. **Mode of Payment**: Method of financial settlement (e.g., "Bank", "Cash", "Wire Transfer") linked to default company accounts.
5. **Tax Category & Sales/Purchase Taxes Templates**: Tax percentage rules (e.g. GST, VAT) automatically applied to commercial vouchers.

---

## 2. Field Requirements & Strict Invariants

### Double-Entry Invariant:
> [!CRITICAL]
> In any `Journal Entry`, the sum of `debit_in_account_currency` must strictly match the sum of `credit_in_account_currency` for the company base currency:
> `total_debit == total_credit`. Unbalanced entries will be rejected with an immediate Frappe validation error.

### Journal Entry
- **voucher_type** (Select: "Journal Entry", "Bank Entry", "Cash Entry", "Opening Entry", Required).
- **company** (Link Company, Required).
- **posting_date** (Date, Required, defaults to today).
- **accounts** (Table Journal Entry Account, Required):
  - **account** (Link Account, Required): Must have `is_group = 0`.
  - **debit_in_account_currency** (Currency, Default 0)
  - **credit_in_account_currency** (Currency, Default 0)
  - **cost_center** (Link Cost Center, Optional): Required for Expense/Income accounts.

### Payment Entry
- **payment_type** (Select: "Receive", "Pay", "Internal Transfer", Required).
- **company** (Link Company, Required).
- **party_type** (Link DocType): "Customer" or "Supplier".
- **party** (Dynamic Link): Customer or Supplier ID.
- **paid_from** (Link Account, Required).
- **paid_to** (Link Account, Required).
- **paid_amount** (Currency, Required, > 0).

---

## 3. Workflow & Lifecycle Transitions
- `Journal Entry`: Draft (0) -> Submitted (1) -> Cancelled (2).
- `Payment Entry`: Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting writes to `GL Entry` and updates outstanding amounts on linked Invoices.
  - Cancelling creates reversing `GL Entry` rows and restores invoice balances.
