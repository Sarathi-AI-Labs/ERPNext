---
name: Stock Skill
description: Inventory management, item master catalog, serialized/batched tracking, multi-warehouse movements, stock ledger, and valuation.
version: 1.0.0
module: Stock
---

# Stock & Inventory Domain Skill

## 1. Domain Overview
The **Stock** module governs physical and perpetual inventory in ERPNext. Every stock movement updates the **Stock Ledger Entry (SLE)** and recalculates the **Bin** balance per `(item_code, warehouse)`.

### Key Entities:
1. **Item**: Central catalog item. Can be stocked (`is_stock_item = 1`), purchased (`is_purchase_item = 1`), sold (`is_sales_item = 1`), or manufactured.
2. **Item Group**: Classification tree node.
3. **Warehouse**: Physical or virtual location where items reside (e.g. `Stores - S`, `Work In Progress - S`, `Finished Goods - S`).
4. **Bin**: Dynamic inventory snapshot record holding `actual_qty`, `reserved_qty`, `ordered_qty`, `projected_qty`, and `valuation_rate`.
5. **Stock Entry**: Core inventory transaction document supporting multiple purposes:
   - `Material Receipt`: Brings initial stock or surplus into a target warehouse.
   - `Material Issue`: Consumes or scraps stock from a source warehouse.
   - `Material Transfer`: Moves stock from source warehouse to target warehouse.
   - `Manufacture`: Consumes raw materials and yields finished goods (associated with Work Order).
   - `Material Transfer for Manufacture`: Stages raw materials from Stores to WIP.
6. **Delivery Note**: Submittable fulfillment document shipping goods to customers.
7. **Purchase Receipt**: Submittable receipt document taking goods in from suppliers.

---

## 2. Field Requirements & Rules

### Item
- **item_code** (Data, Required): Unique identifier/SKU.
- **item_name** (Data, Required): Display name.
- **item_group** (Link Item Group, Required): Category (e.g., "Raw Material", "Products", "Sub Assemblies").
- **stock_uom** (Link UOM, Required): Base unit of measure (e.g., "Nos", "Kg", "Meter").
- **is_stock_item** (Check): 1 to track balance in inventory; 0 for services/non-stock.
- **valuation_rate** (Currency, Optional): Standard initial cost for valuation.

### Stock Entry
- **stock_entry_type** (Link Stock Entry Type, Required): e.g. "Material Receipt", "Material Issue", "Material Transfer", "Manufacture".
- **company** (Link Company, Required): Operating entity.
- **items** (Table Stock Entry Detail, Required):
  - **item_code** (Link Item, Required)
  - **qty** (Float, Required, must be > 0)
  - **uom** (Link UOM, Required)
  - **s_warehouse** (Link Warehouse): Source warehouse (Required for Issue and Transfer).
  - **t_warehouse** (Link Warehouse): Target warehouse (Required for Receipt and Transfer).
  - **basic_rate** (Currency): Incoming valuation rate (Required for Material Receipt).

---

## 3. Strict Pre-Transaction Checks & Constraints

> [!CRITICAL]
> **Zero Negative Stock Rule**: In this ERPNext instance, `Stock Settings.allow_negative_stock` is strictly set to `0`. 
> Before creating or submitting any `Material Issue`, `Material Transfer`, `Delivery Note`, or `Manufacture` entry, the AI Agent MUST query the `Bin` table:
> ```python
> bin = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": source_warehouse}, ["actual_qty"])
> assert bin.actual_qty >= required_qty
> ```
> Failure to verify stock availability will result in an immediate ERPNext submission error: `NegativeStockError`.

---

## 4. Lifecycle & Workflow Transitions
- `Stock Entry`: Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting writes immutable records to `Stock Ledger Entry` and `GL Entry` (if perpetual inventory is enabled).
  - Cancelling creates offsetting reversing entries in `Stock Ledger Entry`.
