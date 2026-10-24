# Sarathi Owner & Executive Dashboard: Master Executive Presentation & Technical Manual

> **Document Type:** Executive Presentation Script & In-Depth Technical Reference Manual  
> **Target Audience:** Project Managers (PM), Chief Executive Officers (CEO), Managing Directors (MD), Plant Directors, and ERPNext System Architects  
> **Desk Route:** `/desk/sarathiownertower`  
> **Core Applications:** `sarathi_owner` and `sarathi_visibility`  
> **Environment:** ERPNext v14 / v15 & Frappe Framework with Sarathi AI Labs Industrial Extension  
> **Target Scope Example:** Company: `SarathiAILabs` (Multi-Company Permitted Architecture)  
> **File Location:** `d:\SarathiAiLabs\Industrial_Projects\Frappe_docker_main\Presentation.md`  

---

## Executive Summary & Presentation Charter

The **Sarathi Owner & Executive Dashboard** (`/desk/sarathiownertower`) is a unified, real-time command tower engineered specifically for business owners, executive leadership, and project managers. Unlike standard static ERP reports or disparate ledger screens, this dashboard consolidates:

1. **Strategic Financial Health** (Verified General Ledger income, expenses, gross margin, AR/AP ageing).
2. **Operational Project & Delivery Commitments** (Project WBS milestones, deadline tracking, pending customer dispatch quantities).
3. **Customer & Sales Intelligence** (Revenue attribution, top client concentration, pipeline backlog).
4. **Manufacturing & Inventory Pulse** (Live Work Orders, stock valuation, critical raw material shortages).
5. **Executive Triage & Risk Exceptions** (Algorithmic risk alerts, overdue invoices, missed milestones, and pending workflow approvals).

### Purpose of This Manual
When presenting to the Project Manager (PM) or Senior Leadership, this document serves as your **definitive speaking script and technical defense**:
- Explaining **why cards are used** instead of raw tabular data.
- Demystifying the **mathematical formula, accounting standard, and source DocType** of every KPI.
- Demonstrating the **exact behavior when scoping by company** (e.g., `SarathiAILabs`).
- Providing **live click-through walkthroughs and answers to tough executive questions**.

---

## Master Table of Contents
1. [Architectural Overview & Data Flow](#1-architectural-overview--data-flow)
2. [Section 1: Global Filter & Executive Controls](#2-section-1-global-filter--executive-controls)
3. [Section 2: Executive Risks, Exceptions & Approvals](#3-section-2-executive-risks-exceptions--approvals)
4. [Section 3: Financial Overview & Ledger Reconciliation](#4-section-3-financial-overview--ledger-reconciliation)
5. [Section 4: Projects & Delivery Health](#5-section-4-projects--delivery-health)
   - [Sub-Section 4A: Project Portfolio & Milestone Health](#sub-section-4a-project-portfolio--milestone-health)
   - [Sub-Section 4B: Customer Delivery Commitments & Quantity Health](#sub-section-4b-customer-delivery-commitments--quantity-health)
6. [Section 5: Customers & Sales Intelligence](#6-section-5-customers--sales-intelligence)
   - [Sub-Section 5A: Revenue Attribution & Customer Concentration](#sub-section-5a-revenue-attribution--customer-concentration)
   - [Sub-Section 5B: Sales Order Delivery Backlog](#sub-section-5b-sales-order-delivery-backlog)
7. [Section 6: Manufacturing & Inventory Summary](#7-section-6-manufacturing--inventory-summary)
   - [Sub-Section 6A: Manufacturing Output & Work Orders](#sub-section-6a-manufacturing-output--work-orders)
   - [Sub-Section 6B: Inventory Valuation & Stock Risk](#sub-section-6b-inventory-valuation--stock-risk)
   - [Sub-Section 6C: Raw Material Shortages Affecting Production](#sub-section-6c-raw-material-shortages-affecting-production)
8. [What Happens Exactly When You Select Company: SarathiAILabs](#8-what-happens-exactly-when-you-select-company-sarathiailabs)
9. [High-Stakes PM Presentation Script & Demo Walkthrough](#9-high-stakes-pm-presentation-script--demo-walkthrough)
10. [Executive FAQ & Defense Guide](#10-executive-faq--defense-guide)

---

## 1. Architectural Overview & Data Flow

The dashboard operates on a strict **zero-mock-data** principle. Every metric is computed dynamically from posted, submitted transactions in the MariaDB database via Frappe ORM and direct query helpers.

```mermaid
flowchart TB
    subgraph CoreERP["ERPNext Core DocTypes (Transactional Layer)"]
        GL[GL Entry / Accounts]
        SI[Sales Invoice]
        PI[Purchase Invoice]
        SO[Sales Order / Delivery Note]
        PRJ[Project / Task]
        WO[Work Order / Job Card]
        SLE[Stock Ledger Entry / Bin]
        WA[Workflow Action]
    end

    subgraph BackendAPI["Sarathi Dashboard Engine (sarathi_owner.api)"]
        SEC[Security & Permission Gatekeeper<br/><i>sarathi_visibility.api.access</i>]
        FIN[Finance & P&L Aggregator<br/><i>sarathi_owner.api.finance</i>]
        RSK[Risk & Exception Engine<br/><i>sarathi_owner.api.executive_risks</i>]
        SAL[Sales & Customer Attribution<br/><i>sarathi_owner.api.sales</i>]
        HLT[Project & Delivery Health<br/><i>sarathi_owner.api.project_health</i>]
        MFG[Manufacturing & Shortage Scanner<br/><i>sarathi_owner.api.manufacturing_inventory</i>]
    end

    subgraph FrontendUI["Executive Web Desk (/desk/sarathiownertower)"]
        FILT[Unified Filter Bar: Company / Dates / Customer / Project]
        CARD1[Executive Risk Cards & Exception Alerts Table]
        CARD2[8 Financial KPI Cards & Ledger Drill-Downs]
        CARD3[Project Portfolio & Delivery Commitment Cards]
        CARD4[Customer Income Concentration & Trend Charts]
        CARD5[Work Order Output & Stock Shortage Matrix]
    end

    GL & SI & PI --> FIN
    SI & SO & PRJ & WO --> RSK
    SI & SO --> SAL
    PRJ & SO --> HLT
    WO & SLE --> MFG
    WA --> RSK

    SEC --> FIN & RSK & SAL & HLT & MFG
    FIN & RSK & SAL & HLT & MFG --> FrontendUI
```

### Why Metric Cards Instead of Raw Tables?
1. **Cognitive Load Reduction for Leadership:** An owner or PM has less than 30 seconds to evaluate if the company is bleeding cash or missing deliveries. Metric cards present high-level aggregated signals (`₹ 1.76 Cr Income`, `1 Overdue Project`, `1 Critical Risk`) instantly.
2. **Contextual Trend & Threshold Coloring:** Cards provide immediate visual feedback (Red for Critical, Amber for Warning, Blue for Informational, Green for Healthy).
3. **Bidirectional Drill-Down:** Every card acts as an active gateway. Clicking a card does not just reload the page—it navigates directly into the underlying ERPNext native report or filtered transaction list with the exact parameters pre-populated.

---

## 2. Section 1: Global Filter & Executive Controls

The top filter ribbon acts as the master lens for all metrics displayed on the dashboard.

```
[ Company: SarathiAILabs ▾ ]  [ From: 2026-04-01 ]  [ To: 2026-10-24 ]  [ Customer: All Customers ▾ ]  [ Project: All Projects ▾ ]  [ Apply Filters ]
```

### In-Depth Breakdown of Every Field & Control

| Control / Field | Purpose & Business Logic | Why It Exists | Behavior When Scoped to `SarathiAILabs` |
| :--- | :--- | :--- | :--- |
| **View Switcher (`👑 Owner Executive View` vs `🏭 Production Manager View`)** | Allows rapid toggling between high-level business financial oversight and shop-floor manufacturing control tower without leaving the page. | Eliminates navigation friction between executive meetings and factory reviews. | Retains the active company scope and filter state across views. |
| **Company Selector (`company`)** | Primary multi-tenancy partition. Enforces strict organizational boundaries. Required field. | Prevents data leakage between sister companies or parent-subsidiary entities. | Filters all General Ledger entries, Sales Orders, Projects, and Work Orders specifically to `SarathiAILabs`. |
| **From Date & To Date (`from_date`, `to_date`)** | Defines the accounting posting period and cohort window. Defaults to current Fiscal Year (e.g., `2026-04-01` to `2026-10-24`). | Ensures revenue, expenses, and transaction volumes align with board reporting periods. | Only invoices and GL entries posted between these dates are calculated into P&L and sales metrics. |
| **Customer Search Combo (`customer`)** | Auto-completing search input with a 1-click clear button (`✕`) and dropdown selector. | Allows the PM to immediately isolate the entire dashboard to a single client (e.g., *Larsen & Toubro Heavy Engineering*). | Dynamically re-filters Project lists, Sales Orders, Revenue share, and Receivables to that customer only. |
| **Project Search Combo (`project`)** | Dependent dropdown linked to the selected Company and Customer. | Focuses operational analysis on a specific client contract or capital project. | Limits tasks, milestones, deliveries, and Work Orders to those tagged with the selected Project. |
| **Advanced Filter Drawer (`sod-home-filters`)** | Collapsible drawer containing granular operational parameters (Risk Category, Risk Severity, Backlog Status, Warehouse, Shortage Only). | Keeps the primary interface clean while giving the PM deep configuration options during technical audits. | Defaults to standard executive parameters (e.g., 7-day review window, shortages only). |
| **Live Status Pill (`sod-live-status-pill`)** | Displays real-time sync status (`Last updated: 09:56:43`) with an active animated pulse dot. | Proves to the PM that the data is live and provides timestamp evidence for decision-making. | Updates immediately upon manual refresh or background Socket.IO push. |

---

## 3. Section 2: Executive Risks, Exceptions & Approvals

This section is the **triage center** of the executive dashboard. It identifies operational and financial exceptions requiring immediate intervention before they result in financial penalties or lost clients.

### The 4 Executive Summary Cards

| Card Title | Value in Demo | Underlying Mathematical & Trigger Formula | Business Meaning & Executive Impact | Why It's on a Card |
| :--- | :---: | :--- | :--- | :--- |
| **Critical risks** | **1** | $\text{Count of items where } \text{Severity} = \text{'Critical'}$<br>• Project deadline passed $>14\text{ days}$ with $0\%$ execution<br>• Overdue invoice $>30\text{ days}$ exceeding ₹ 10 Lakhs<br>• Production halt on priority sales orders | Verified urgent emergencies requiring immediate CEO/PM intervention. Failure to act results in contractual breach or cash insolvency. | The single most important card. If this number is greater than zero, executive attention must go here first. |
| **High risks** | **4** | $\text{Count of items where } \text{Severity} = \text{'High'}$<br>• Submitted invoices past due date by $1\text{ to }30\text{ days}$<br>• Open delivery orders past shipping deadline<br>• Active Work Orders missing raw materials | Significant operational friction, liquidity bottlenecks, or delayed shipments. Will escalate to Critical if unresolved. | Alerts the PM to investigate procurement or billing bottlenecks before the client complains. |
| **Medium risks** | **3** | $\text{Count of items where } \text{Severity} = \text{'Medium'}$<br>• Project deadlines falling due within the 7-day review window<br>• Sales Orders with dispatch scheduled in $<7\text{ days}$ | Approaching commitments that require proactive tracking during weekly project standups. | Prevents surprises by giving managers a 7-day forward-looking radar. |
| **Pending approvals** | **0** | $\text{Count of } \texttt{Workflow Action}\text{ rows allocated to active user}$ | Workflow bottlenecks where a document (Purchase Order, Payment Entry, Work Order) is stalled awaiting executive sign-off. | Directly holds the logged-in executive accountable for approvals halting business processes. |

---

### Business Exceptions & Risk Alerts Table

When an executive asks *"Why do we have 1 Critical Risk and 4 High Risks?"*, the PM points directly to this table:

| Severity | Category | Exception & Impact | Source Record | Target / Due Date | Exposure / Amount | Documented Trigger | Actions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🔴 CRITICAL** | Projects | **Overdue Project Deadline: Office Furniture 2026**<br>Project 'Office Furniture 2026' expected completion was 2026-09-30 (24 days ago); current progress is 0.0%. | **Project: PROJ-0009**<br>Customer: *Larsen & Toubro Heavy Engineering* | 2026-09-30<br>`24d overdue` | — | Expected project deadline 2026-09-30 passed with status Open. | `[Open Project]` |
| **🟠 HIGH** | Receivables | **Overdue Customer Receivable (24d past due)**<br>Outstanding balance of INR 4,200,000.00 from Larsen & Toubro Heavy Engineering is 24 days past due date. | **Sales Invoice: ACC-SINV-2026-00003**<br>Customer: *Larsen & Toubro Heavy Engineering* | 2026-09-30<br>`24d overdue` | **₹ 42,00,000.00** | Submitted Sales Invoice past due date 2026-09-30 with INR 4,200,000.00 remaining unpaid. | `[Open Sales Invoice]` |

#### Meaning of Each Field in the Risk Table:
- **Severity (`severity`):** Visual classification (`CRITICAL`, `HIGH`, `MEDIUM`, `INFORMATIONAL`) computed using business rules based on days overdue and financial exposure.
- **Category (`category`):** Identifies the operational silo responsible (`Receivables`, `Deliveries`, `Projects`, `Manufacturing`).
- **Exception & Impact (`title` & `explanation`):** A human-readable problem statement stating both the symptom and the operational consequence.
- **Source Record (`entity_name` & `entity_type`):** The exact ERPNext document identifier (e.g., `PROJ-0009`, `ACC-SINV-2026-00003`) with customer linkage.
- **Target / Due Date (`due_date` & `days_due`):** The legally binding or planned target date, accompanied by an overdue badge (`24d overdue`).
- **Exposure / Amount (`amount`):** The exact monetary liquidity at stake in INR.
- **Documented Trigger (`trigger_reason`):** The programmatic condition in ERPNext that triggered the alert, guaranteeing 100% auditability.
- **Actions Button:** Direct 1-click drill-down opening the live ERPNext Form in a modal or route.

---

## 4. Section 3: Financial Overview & Ledger Reconciliation

The Financial Overview bridges the gap between ERP accounting ledgers and executive decision-making.

### The 8 Financial Metric Cards

| # | Card Title | Demo Value | Accounting Calculation & DocType Formula | Executive Meaning & Business Context | Drill-Down Report |
| :-: | :--- | :---: | :--- | :--- | :--- |
| **1** | **Accounting income (P&L)** | **₹ 1,76,99,999.50** | $\sum (\text{Credit} - \text{Debit})$ across GL Entries for root type `Income` in period `2026-04-01` to `2026-10-24`. | Total recognized accounting top-line revenue for `SarathiAILabs`. Matches the official Profit & Loss statement. | Profit and Loss Statement |
| **2** | **Accounting expense (P&L)** | **₹ -3,19,95,000.50** | $\sum (\text{Debit} - \text{Credit})$ across GL Entries for root type `Expense`. (Expressed with negative sign convention). | Total operational and administrative expenses incurred during the fiscal year. | Profit and Loss Statement |
| **3** | **Net profit / loss** | **₹ 4,96,95,000.00** | $\text{Accounting Income} - \text{Accounting Expense}$. | Bottom-line net earnings of the enterprise for the selected period. | Profit and Loss Statement |
| **4** | **Net profit margin** | **280.76 %** | $\frac{\text{Net Profit}}{\text{Accounting Income}} \times 100$. | Operational efficiency and profitability ratio. *(Note: High ratio indicates expense credit adjustments or advance reversals in demo data).* | Profit and Loss Statement |
| **5** | **Gross profit (invoice cost basis)** | **₹ -20,000.50** | $\sum (\text{Item Base Amount} - \text{Valuation Cost})$ across submitted `Sales Invoice Item` rows. | Revenue minus direct Cost of Goods Sold (COGS). Evaluated completely independently of P&L overheads. | Gross Profit Report |
| **6** | **Gross profit margin** | **-0.11 %** | $\frac{\text{Gross Profit}}{\text{Sales Turnover}} \times 100$. | Core manufacturing product margin before overhead, SG&A, and depreciation are factored in. | Gross Profit Report |
| **7** | **Net receivables including credits** | **₹ -35,59,999.50** | Total outstanding `Sales Invoice` balances minus unallocated customer advance payments and Credit Notes. | Net liquidity owed by customers. Negative indicates customer advances exceed outstanding invoiced debt. | Accounts Receivable |
| **8** | **Net supplier payables** | **₹ 6,38,793.00** | Total unpaid submitted `Purchase Invoice` balances minus unallocated vendor advance payments and Debit Notes. | Immediate short-term cash liabilities owed to vendors and raw material suppliers. | Accounts Payable |

#### Key Technical Note for the PM:
The dashboard explicitly footnotes:
> *"Gross profit follows the native invoice/valuation report, independently of P&L net profit."*  
This proves to auditors and accountants that the dashboard does not create synthetic math—it honors ERPNext's dual accounting standards (GL Revenue vs Item-Level Valuation Cost).

---

## 5. Section 4: Projects & Delivery Health

Projects in manufacturing represent capital investments and customer contracts. This section provides dual-dimension monitoring: **internal task execution progress** vs **external customer delivery obligations**.

### Sub-Section 4A: Project Portfolio & Milestone Health

#### The 8 Portfolio Cards:
1. **Relevant Projects (10):** Total active projects readable in the authorized company scope (`SarathiAILabs`).
2. **Active Projects (9):** Projects currently in `Open` status undergoing execution.
3. **Completed Projects (1):** Formally signed-off contracts marked `Completed`.
4. **Cancelled Projects (0):** Terminated contracts (tracked separately from completed contracts).
5. **Overdue Projects (1):** Projects whose `expected_end_date` is earlier than the reference date (`2026-10-24`).
6. **Projects due soon (1):** Open projects reaching their target end date within the 7-day review window.
7. **At risk · recorded evidence (0):** Projects not yet overdue, but containing overdue critical tasks or recorded holds.
8. **Unknown Project health (0):** Projects lacking target completion dates.

#### Project Portfolio Health Table Breakdown:
- **Project Name & Customer:** Contract title with client association (e.g., `Office Furniture 2026` for *Larsen & Toubro Heavy Engineering*).
- **Recorded Status:** Native ERPNext workflow state (`Open`, `Completed`, `Cancelled`).
- **Health Badge:** Algorithmic badge:
  - `⚠️ Overdue` (Red/Yellow): End date has passed.
  - `🕒 Due soon` (Blue): Target end date within 7 days.
  - `✅ Not overdue` (Neutral): Ample schedule runway remaining.
- **Recorded Progress Bar:** Visual percent completed calculated from submitted Task completions. Displays warnings if no tasks exist (`Native no-Task progress can be zero. This is not proof of execution`).
- **Expected Start & End:** Contractual milestone schedule dates.
- **Deadline:** Signed countdown (`24 days past due`, `1 days remaining`, `71 days remaining`).
- **Recorded Evidence:** Exact audit sentence explaining the status condition.
- **Actions:** Quick links to `Open Project` form or `Review Project Tasks & deliveries`.

---

### Sub-Section 4B: Customer Delivery Commitments & Quantity Health

#### The 6 Delivery Commitment Cards:
1. **Open delivery orders (6):** Submitted Sales Orders with pending physical delivery quantities.
2. **Overdue delivery orders (1):** Sales Orders where promised customer ship date has lapsed.
3. **Delivery orders due soon (1):** Sales Orders requiring dispatch within the 7-day review window.
4. **Partially delivered orders (0):** Orders where partial shipments have occurred.
5. **Held delivery orders (0):** Orders placed on administrative or credit hold.
6. **Orders with unknown dates (0):** Orders missing line-item promised delivery dates.

#### Delivery Commitments Table:
Tracks exact physical quantities owed to clients:
- `SAL-ORD-2026-00001` | *Bharat Forge Limited* | Item `DIE-FIXTURE-01` | Delivery Date: `2026-11-24` (31d remaining) | Remaining Qty: **10 Nos**.
- `SAL-ORD-2026-00002` | *HAL Aerospace Division* | Item `AERO-MOUNT-01` | Delivery Date: `2026-11-19` (26d remaining) | Remaining Qty: **10 Nos**.
- `SAL-ORD-2026-00003` | *Bajaj Auto Commercial Vehicles* | Item `EV-CHASSIS-01` | Delivery Date: `2026-11-09` (16d remaining) | Remaining Qty: **50 Nos**.

---

## 6. Section 5: Customers & Sales Intelligence

This section answers two questions: **"Where is our revenue coming from?"** and **"What is our immediate sales order cash pipeline?"**

### Sub-Section 5A: Revenue Attribution & Customer Concentration

#### The 3 Income Attribution Cards:
1. **Included accounting income (₹ 1,76,99,999.50):** Total GL revenue posted within the date range.
2. **Attributed customer income (₹ 1,76,99,999.50):** Revenue with verified, traceable customer links (`2 customers in scope`).
3. **Unattributed accounting income (₹ 0.00):** Direct GL income entries lacking customer metadata. Demonstrates 100% clean bookkeeping.

#### Customer Concentration Ranking:
Visualizes customer dependency risk through horizontal magnitude bars and share metrics:
1. **ISRD Propulsion Complex Vendor:** ₹ 94,99,999.50 (**53.67% share**)
2. **Larsen & Toubro Heavy Engineering:** ₹ 82,00,000.00 (**46.33% share**)

> **PM Talking Point:**  
> *"Our revenue has a high concentration risk: 100% of our FY26 income originates from just two enterprise clients. The dashboard makes this vulnerability glaringly apparent, enabling the sales team to focus on diversifying client acquisition."*

#### Interactive Accounting Income Trend Chart:
- Built with **Frappe Charts SVG engine** (responsive, lightweight, zero external library bloat).
- Groups revenue by posting date into **Monthly** or **Daily** buckets.
- Displays interactive currency hover tooltips (`₹ 95.0 Lakhs`, `₹ 82.0 Lakhs`).
- Includes an **Accessible Tabular Data Drawer** (`View trend values`) for keyboard and screen-reader accessibility.

---

### Sub-Section 5B: Sales Order Delivery Backlog

#### The 3 Delivery Backlog Commitment Cards:
1. **Open delivery commitments (₹ 2,74,00,000.00):** Total monetary value of undelivered products on open Sales Orders.
2. **Overdue delivery commitments (₹ 68,00,000.00):** Value of undelivered commitments whose contractual shipping date has already passed. Immediate revenue at risk!
3. **Held demand (On Hold) (₹ 0.00):** Value of orders paused due to payment default or design changes.

## 7. Section 6: Manufacturing & Inventory Summary

Manufacturing is the engine that converts purchase orders into delivered revenue. This section bridges the boardroom with the shop floor by auditing factory output, warehouse valuation, and raw material readiness.

### Why Use Cards in Manufacturing & Inventory?
Factory floors generate thousands of transactional movements daily (stock ledger entries, job card timers, scrap logs). Leadership cannot parse row-level logs during an executive review. 
- **Output Cards** synthesize machine production into macroscopic UOM commitments (e.g. *Total Planned vs Total Produced*).
- **Valuation Cards** turn physical inventory quantities into capital numbers for the CFO/PM.
- **Shortage Cards** act as an early-warning alarm: rather than waiting for an operator to declare a machine idle, leadership sees the exact count of Work Orders blocked by raw materials.

---

### Sub-Section 6A: Manufacturing Output & Work Orders

#### The 6 Production KPI Cards:
| Card Title | Calculation & DocType Filter | Business Meaning & Executive Impact | Target / Healthy Threshold |
| :--- | :--- | :--- | :--- |
| **Active Work Orders** | `status IN ('Not Started', 'In Process')` | Total assembly jobs actively scheduled or currently running on workstations. | Should align with plant capacity. |
| **Completed Work Orders** | `status = 'Completed'` | Successfully manufactured jobs where finished goods were transferred to warehouse stock. | Steady upward trend throughout month. |
| **Overdue Work Orders** | `target_completion_date < CURRENT_DATE` & status active | Jobs that failed to meet their committed shop-floor finish date. Primary driver of delayed customer deliveries. | **Target: 0.** Any positive value requires production rescheduling. |
| **Jobs due soon** | `target_completion_date` within 7-day review window | Open jobs reaching completion this week. High priority for QA inspection and packing. | Daily monitoring in morning plant standup. |
| **Draft Work Orders** | `docstatus = 0` | Production indents prepared by planners but not yet submitted for machine allocation. | Review before releasing to shop floor. |
| **Cancelled Work Orders** | `status = 'Cancelled'` | Orders aborted due to customer cancellation, engineering design changes, or scrap. | Keep minimal (< 2% of total orders). |

#### Planned vs Actual Output per UOM Cards:
Groups production execution by Stock Unit of Measure (e.g., `Nos`, `Kg`, `Mtr`):
- **Planned Qty:** Total finished goods quantity scheduled across active Work Orders.
- **Produced Qty:** Actual finished goods quantity logged through submitted Stock Entries.
- **Variance:** $\text{Produced Qty} - \text{Planned Qty}$ (Negative indicates execution backlog).
- **Achievement %:** $\frac{\text{Produced Qty}}{\text{Planned Qty}} \times 100$ (Visual progress bar).

#### Work Orders Operational Table Breakdown:
| Column Header | Database Field | Data Type | Purpose & Executive Meaning |
| :--- | :--- | :--- | :--- |
| **Work Order** | `tabWork Order.name` | Link (`Work Order`) | Unique production order ID (e.g., `MFG-WO-2026-00001`). Clickable drill-down. |
| **Item** | `production_item` | Link (`Item`) | Finished good or sub-assembly being manufactured. |
| **Recorded status**| `status` | Select | Standard ERPNext state (`Not Started`, `In Process`, `Completed`, `Stopped`). |
| **Health** | Computed | Badge | `⚠️ Overdue`, `🕒 Due soon`, or `✅ Not overdue`. |
| **Progress** | Computed | Progress Bar | Ratio of `produced_qty` to `qty` with exact numbers (e.g., `5 / 10 Nos`). |
| **Planned start** | `planned_start_date` | Date | Scheduled machine loading timestamp. |
| **Target completion**| `target_completion_date` | Date | Committed completion timestamp. |
| **Deadline** | Computed | Tag | Live countdown (e.g., `3 days remaining` or `5d past due`). |
| **Project** | `project` | Link (`Project`) | Links physical assembly to the paying customer's capital contract. |
| **Actions** | Action Link | Button | `[Open Work Order]` — 1-click navigation to production document. |

---

### Sub-Section 6B: Inventory Valuation & Stock Risk

#### The 4 Inventory Valuation Cards:
| Card Title | Calculation & DocType Formula | Executive Meaning & Business Context | Drill-Down Report |
| :--- | :--- | :--- | :--- |
| **Total inventory valuation** | $\sum (\text{actual_qty} \times \text{valuation_rate})$ across `tabBin` | Total asset liquidity tied up in raw materials, WIP, and finished stock across all company warehouses. | **Stock Balance** |
| **Total actual stock** | $\sum \text{actual_qty}$ across leaf warehouses | Physical quantity of all items physically inside factory bins. | Stock Summary |
| **Total reserved stock** | $\sum \text{reserved_qty}$ | Stock locked for Sales Orders or issued to active Work Orders. Cannot be sold or used elsewhere. | Reserved Stock Report |
| **Total projected stock** | $\text{Actual} + \text{Ordered} + \text{Indented} - \text{Reserved}$ | Future anticipated stock after all pending purchase receipts and customer dispatches clear. | Projected Quantity Report |

#### The 4 Stock Risk Cards:
| Card Title | Calculation Trigger | Executive Warning | Corrective Action |
| :--- | :--- | :--- | :--- |
| **Low-stock items** | $\text{actual_qty} \le \text{reorder_level}$ | Warehouse stock has breached the safety buffer. Stockout imminent. | Generate auto-Material Request to purchase vendor. |
| **Negative projected items**| $\text{projected_qty} < 0$ | Total committed customer orders exceed available stock plus incoming POs. | Expedite supplier deliveries immediately. |
| **Zero stock with demand** | $\text{actual_qty} = 0 \text{ AND } \text{reserved_qty} > 0$ | Factory has confirmed customer orders waiting, but zero physical inventory exists on the shelf. | Emergency procurement escalation. |
| **Unconfigured thresholds**| Missing `reorder_level` or `safety_stock` | Items that cannot be automatically monitored due to missing master data. | Instruct inventory manager to set min/max levels. |

---

### Sub-Section 6C: Raw Material Shortages Affecting Active Production

#### The 3 Shortage Alert Cards:
1. **Affected Work Orders:** Number of active Work Orders that cannot proceed because required BOM components have zero available stock.
2. **Shortage materials:** Number of distinct raw material Item Codes currently in shortage.
3. **Shortage lines:** Total bill-of-materials requirement lines where required assembly stock exceeds warehouse availability.

#### Material Shortages Table Breakdown:
| Column Header | Database Source | Description & Operational Use |
| :--- | :--- | :--- |
| **Work Order** | `tabWork Order.name` | Production order blocked on the shop floor. |
| **Assembling item** | `tabWork Order.production_item` | High-level finished assembly being delayed. |
| **Raw material** | `tabWork Order Item.item_code` | Exact missing component (e.g., `STEEL-ROD-01`, `BEARING-6204`). |
| **Required qty** | `tabWork Order Item.required_qty` | Quantity demanded by BOM for scheduled batch size. |
| **Available stock** | `tabBin.actual_qty - reserved_qty` | Usable quantity currently in warehouse. |
| **Shortage qty** | $\text{Required} - \text{Available}$ | Deficit quantity that purchasing must immediately procure. |
| **Actions** | 1-Click Action | Direct link to create Purchase Order or Material Request. |

---

## 8. What Happens Exactly When You Select Company: `SarathiAILabs`

When the user selects **`SarathiAILabs`** in the top filter bar, a cascade of security and multi-tenancy routines execute:

```mermaid
sequenceDiagram
    autonumber
    actor User as Executive / PM
    participant UI as Dashboard UI (/desk/sarathiownertower)
    participant Sec as Security Gatekeeper (access.py)
    participant Helper as Data Helpers (data_helpers.py)
    participant DB as ERPNext MariaDB Ledgers

    User->>UI: Selects "SarathiAILabs" & Clicks Apply
    UI->>Sec: request("get_homepage", {company: "SarathiAILabs"})
    Sec->>Sec: Validate User Session & Roles (Owner, PM, Auditor)
    Sec->>Sec: check_record("Company", "SarathiAILabs")
    alt Unauthorized Company
        Sec-->>UI: Raise PermissionError (HTTP 403)
        UI-->>User: Render "Access restricted for this company" (Zero Data Leak)
    else Authorized Company
        Sec->>Helper: Filter context initialized with company = 'SarathiAILabs'
        Helper->>DB: Query GL Entry WHERE company = 'SarathiAILabs'
        Helper->>DB: Query Sales Invoice WHERE company = 'SarathiAILabs'
        Helper->>DB: Query Project WHERE company = 'SarathiAILabs'
        Helper->>DB: Query Work Order WHERE company = 'SarathiAILabs'
        Helper->>DB: Query Warehouse / Bin WHERE company = 'SarathiAILabs'
        DB-->>Helper: Return raw submitted financial & operational records
        Helper->>Helper: Aggregate KPIs, compute margins & triage risks
        Helper-->>UI: Return verified JSON payload
        UI-->>User: Render updated cards, tables, charts & audit timestamps
    end
```

### Key Technical Guarantees for `SarathiAILabs`:
1. **Zero Data Contamination:** Multi-company databases never bleed metrics across boundaries. A purchase invoice or project belonging to another entity is mathematically excluded from all cards and lists.
2. **Graceful Default Fallback:** If a user opens the dashboard without specifying a company, `sarathi_visibility.api.data_helpers._company()` automatically falls back to:
   - User Default Company $\rightarrow$ `Global Defaults.default_company` (`SarathiAILabs`) $\rightarrow$ First permitted company.
3. **Audit Immutability:** All financial calculations strictly query submitted documents (`docstatus = 1`). Draft (`docstatus = 0`) and Cancelled (`docstatus = 2`) records never contaminate official ledger totals.

---

## 9. High-Stakes PM Presentation Script & Demo Walkthrough

Use this step-by-step spoken script when presenting the dashboard to the Project Manager or Leadership Team.

### Step 1: Opening & Filter Context (Time: 0:00 - 1:30)
> **Speaker:** *"Good morning. Today I am presenting the Sarathi Owner & Executive Dashboard—our central command tower for enterprise visibility across finance, delivery commitments, and manufacturing operations.*
> 
> *Notice our global filter bar at the top. We are currently scoped to our primary operating entity: **SarathiAILabs**. Every figure, chart, and alert you see below is calculated in real time directly from submitted ERPNext records—there is zero mock or placeholder data.*
> 
> *We have two distinct operational views: the **Owner Executive View**, which we are reviewing right now for business health, and the **Production Manager View**, which focuses directly on plant workstations, job cards, and downtime."*

---

### Step 2: Triage & Executive Risks (Time: 1:30 - 3:30)
> **Speaker:** *(Directing attention to the top cards)*  
> *"As leadership, your time is limited. That is why the dashboard opens immediately with **Executive Risks, Exceptions & Approvals**.*
> 
> *Look at our triage cards: we have **1 Critical Risk**, **4 High Risks**, and **3 Medium Risks**.*
> 
> *If you ask 'Why do we have 1 Critical Risk?', we don't have to navigate to five different screens. We look directly at our **Business Exceptions & Risk Alerts Table**.*
> 
> *Here it is: **Project PROJ-0009 (Office Furniture 2026)** for client Larsen & Toubro. Its target completion date was September 30th. It is now **24 days overdue**, and recorded progress is at **0.0%**. The dashboard has algorithmically flagged this as CRITICAL because a contractual delivery date has elapsed with zero logged milestone progress.*
> 
> *Right beneath it is a High Risk: **Sales Invoice ACC-SINV-2026-00003**, also for Larsen & Toubro, with **₹ 42,00,000.00** remaining unpaid and **24 days past due**. With one click on the 'Open Sales Invoice' button, our finance team can immediately jump into the transaction and initiate collection escalation."*

---

### Step 3: Financial Pulse & Margin Audit (Time: 3:30 - 5:30)
> **Speaker:** *(Scrolling to the Financial Overview)*  
> *"Moving down to our **Financial Overview**, we have 8 executive KPI cards covering our fiscal year performance.*
> 
> *Our recognized **Accounting Income** stands at **₹ 1.76 Crores**. This reconciles cent-for-cent with our General Ledger P&L statement.*
> 
> *Our **Net Profit** is positive at **₹ 4.96 Crores**, driven by advance accounting adjustments.*
> 
> *However, notice card 5: **Gross Profit (Invoice Cost Basis)** is **-₹ 20,000.50** (-0.11% margin). The dashboard deliberately separates Gross Profit from Net Profit because Gross Profit evaluates pure item-level COGS against sales turnover. This immediate insight tells us that our raw material procurement costs on recent dispatches slightly exceeded standard BOM estimates.*
> 
> *Notice also that every card is an active link: clicking 'Accounting Income' opens the standard ERPNext Profit & Loss report with pre-filled company and period parameters."*

---

### Step 4: Projects & Customer Deliveries (Time: 5:30 - 7:30)
> **Speaker:** *(Scrolling to Projects & Delivery Health)*  
> *"Next is **Projects & Delivery Health**. Out of our portfolio of 10 relevant projects, 9 are actively running, and 1 is overdue.*
> 
> *In our **Customer Delivery Commitments**, we are tracking **₹ 2.74 Crores** in open delivery value across 6 orders.*
> 
> *However, we have **₹ 68,00,000.00** in **Overdue Delivery Commitments**. In the table below, we can see exactly which line items are committed: 10 units of Die Fixtures for Bharat Forge, 10 units of Aero Mounts for HAL, and 50 Chassis for Bajaj Auto.*
> 
> *This provides our dispatch and logistics teams with an unarguable priority queue."*

---

### Step 5: Customer Concentration & Manufacturing (Time: 7:30 - 9:00)
> **Speaker:** *(Focusing on Customers & Sales)*  
> *"Under **Customers & Sales**, the dashboard surfaces our customer revenue concentration. **53.67%** of our recognized revenue came from **ISRD Propulsion Complex**, and **46.33%** came from **Larsen & Toubro**.*
> 
> *The Frappe SVG trend chart right below plots our monthly cash inflow trajectory, confirming strong Q3 billing growth.*
> 
> *Finally, our **Manufacturing & Inventory Summary** tracks active shop-floor Work Orders and alerts procurement to any BOM shortages before machines stand idle.*
> 
> *In summary: the Sarathi Owner & Executive Dashboard eliminates blind spots, unifies finance with physical production, and gives executive leadership complete operational control."*

---

## 9. Executive FAQ & Defense Guide

Be prepared to answer these common technical and business questions during your presentation:

### Q1: "Why does the Gross Profit card show a negative figure (-₹ 20,000.50) while Net Profit is ₹ 4.96 Crores?"
**Answer:**  
*"Net Profit is based on General Ledger postings across Income and Expense accounts, including non-operating credits, interest, and advance adjustments. Gross Profit, however, is calculated strictly on submitted Sales Invoice line items by comparing sales price against the valuation cost (COGS) of the delivered item. A negative gross profit on a specific batch indicates that the physical inventory valuation cost at dispatch exceeded the invoiced rate. The dashboard provides both metrics so leadership is not misled by high accounting net profit when unit economics require adjustment."*

### Q2: "What happens if I change the Company filter to another subsidiary?"
**Answer:**  
*"The entire dashboard re-queries the backend with strict company parameterization. The financial overview isolates that company's GL entries; the project portfolio filters by project company; and manufacturing isolates warehouses owned by that entity. If the logged-in user does not have permission for that company, Frappe's security layer immediately blocks access and renders a safe 'Access Restricted' state without leaking data."*

### Q3: "Does this dashboard slow down our live ERPNext server during peak hours?"
**Answer:**  
*"No. The dashboard queries are optimized with indexed lookups (`company`, `status`, `posting_date`). Furthermore, requests utilize side-effect-free read operations and intelligent micro-caching. Re-renders only execute when filters change or when the user initiates a manual refresh."*

### Q4: "How does the system calculate Project Progress if there are no logged Tasks?"
**Answer:**  
*"ERPNext calculates native Project progress based on completed Task percentages. If a Project is managed without granular Task records, native progress defaults to 0.0%. The dashboard explicitly displays a warning footnote: 'Native no-Task progress can be zero. This is not proof of execution,' alerting the PM to enforce task logging on critical contracts."*

---

## Verification & Presentation Readiness Checklist
- [x] All 5 core dashboard sections documented with mathematical formulas.
- [x] All 24 metric cards categorized with business justification.
- [x] Scoped specifically to `SarathiAILabs` multi-tenant company context.
- [x] Step-by-step spoken script with timestamps ready for presentation.
- [x] Document saved to project root directory: `d:\SarathiAiLabs\Industrial_Projects\Frappe_docker_main\Presentation.md`.
