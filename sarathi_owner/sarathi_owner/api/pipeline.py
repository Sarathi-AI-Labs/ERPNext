"""Manufacturing & Industrial Process Pipeline Resolver for Sarathi Owner Dashboard.

Implements the complete 24-step industrial flowchart across 3 connected lines (8-8-8):
- Line 1: Commercial & Sales Engineering (Steps 1–8)
  1. Lead / Inquiry (Sakshi Sawant / Narendra Sir)
  2. Requirement Collection (Narendra Sir / Raj / Samir Patil)
  3. Technical Evaluation (Drawing) (Ubed / Tejas Patil)
  4. Costing / Estimation (Estimation Team)
  5. Quotation (Sales Department)
  6. Customer PO & Approval (Akshay Patil)
  7. PO Verification (Akshay Patil)
  8. Create Sales Order (Akshay Patil)

- Line 2: Accounts, SCM, Planning & Fabrication (Steps 9–16)
  9. Accounts Advance Approval (Pooja Chougule)
  10. Production Planning (Swapnil Mohite)
  11. Production Drawing (BOM) (Suraj Jirage)
  12. Store Dept (Material Avail) (Abhishek Mohite)
  13. Purchase & Material Receipt (Stores / Purchase Department)
  14. Raw Material QC (QC Department)
  15. Laser Cutting (Sheet & Pipe) (Laser Cutting Shop)
  16. Bending (as per Drawing) (Bending Department)

- Line 3: Welding, Finishing, Quality & Dispatch (Steps 17–24)
  17. Cutting & Bending QC (QC Department)
  18. Welding (Dhashrat Salavi)
  19. Welding Quality Check (QC Department)
  20. Grinding / Finishing (Dhashrat Salavi)
  21. Painting / Powder Coating (Babaso Aagale)
  22. Final QC & Rework Assembly (QC / Shrikant Magdum)
  23. Packing & Transportation (Logistics Team)
  24. Documentation & Dispatch (Pooja Chougule / Samir Patil)
"""

import frappe

from sarathi_visibility.api.access import (check_record, scoped_rows, scoped_value)
from frappe.utils import flt


def get_project_pipeline(project_name: str) -> dict:
	"""Builds the comprehensive 26-step industrial pipeline for a single Project."""
	if not frappe.db.exists("Project", project_name):
		return {}

	project = check_record("Project", project_name)

	# 1. Resolve Customer and Sales Orders
	customer = project.customer
	sales_orders = scoped_rows(
		"Sales Order",
		filters={"project": project_name, "docstatus": ["!=", 2]},
		fields=[
			"name",
			"customer",
			"status",
			"delivery_date",
			"grand_total",
			"advance_paid",
			"po_no",
			"docstatus",
			"per_delivered",
			"per_billed",
		],
	)
	so_names = [so.name for so in sales_orders]
	if not customer and sales_orders:
		customer = sales_orders[0].customer or "Unassigned Customer"
	elif not customer:
		customer = "Unassigned Customer"

	# 2. Quotations and Leads
	quotations = []
	if so_names and frappe.db.has_column("Sales Order", "prevdoc_docname"):
		quotations = scoped_rows(
			"Quotation",
			filters={
				"name": ["in", [s.get("prevdoc_docname") for s in sales_orders if s.get("prevdoc_docname")]],
				"docstatus": ["!=", 2],
			},
			fields=["name", "status", "docstatus", "grand_total"],
		)
	if not quotations and customer and customer != "Unassigned Customer":
		quotations = scoped_rows(
			"Quotation",
			filters={"party_name": customer, "docstatus": ["!=", 2]},
			fields=["name", "status", "docstatus", "grand_total"],
			limit=10,
		)

	leads = []
	if customer and customer != "Unassigned Customer":
		leads = scoped_rows(
			"Lead",
			filters={"lead_name": ["like", f"%{customer[:15]}%"], "docstatus": ["!=", 2]},
			fields=["name", "lead_name", "status"],
			limit=5,
		)

	# 3. BOMs
	boms = _resolve_project_boms(project)
	submitted_active_boms = [b for b in boms if b.get("docstatus") == 1 and b.get("is_active")]

	# 4. Production Plans
	plans = _resolve_production_plans(project_name, so_names)
	submitted_plans = [p for p in plans if p.get("docstatus") == 1]

	# 5. Work Orders
	work_orders = scoped_rows(
		"Work Order",
		filters={"project": project_name, "docstatus": ["!=", 2]},
		fields=[
			"name",
			"status",
			"production_item",
			"qty",
			"produced_qty",
			"bom_no",
			"planned_start_date",
			"planned_end_date",
			"docstatus",
		],
	)
	if not work_orders and so_names:
		work_orders = scoped_rows(
			"Work Order",
			filters={"sales_order": ["in", so_names], "docstatus": ["!=", 2]},
			fields=[
				"name",
				"status",
				"production_item",
				"qty",
				"produced_qty",
				"bom_no",
				"planned_start_date",
				"planned_end_date",
				"docstatus",
			],
		)

	wo_names = [w.name for w in work_orders]
	wo_planned_qty = sum(flt(w.qty) for w in work_orders if w.docstatus != 2)
	wo_produced_qty = sum(flt(w.produced_qty) for w in work_orders if w.docstatus != 2)
	mfg_progress = (
		round((wo_produced_qty / wo_planned_qty) * 100, 1)
		if wo_planned_qty > 0
		else (100.0 if (work_orders and all(w.status == "Completed" for w in work_orders)) else 0.0)
	)

	# 6. Job Cards
	job_cards = []
	if wo_names:
		job_cards = scoped_rows(
			"Job Card",
			filters={"work_order": ["in", wo_names], "docstatus": ["!=", 2]},
			fields=["name", "operation", "status", "for_quantity", "total_completed_qty", "work_order"],
		)

	# 7. Stock Entries (Manufacture & Material Transfer)
	stock_entries_mfg = []
	stock_entries_transfer = []
	if wo_names:
		stock_entries_mfg = scoped_rows(
			"Stock Entry",
			filters={"work_order": ["in", wo_names], "purpose": "Manufacture", "docstatus": 1},
			fields=["name", "work_order", "fg_completed_qty", "posting_date"],
		)
		stock_entries_transfer = scoped_rows(
			"Stock Entry",
			filters={
				"work_order": ["in", wo_names],
				"purpose": "Material Transfer for Manufacture",
				"docstatus": 1,
			},
			fields=["name", "work_order", "posting_date"],
		)
	if not stock_entries_mfg:
		stock_entries_mfg = scoped_rows(
			"Stock Entry",
			filters={"project": project_name, "purpose": "Manufacture", "docstatus": 1},
			fields=["name", "work_order", "fg_completed_qty", "posting_date"],
		)
	if not stock_entries_transfer:
		stock_entries_transfer = scoped_rows(
			"Stock Entry",
			filters={"project": project_name, "purpose": "Material Transfer for Manufacture", "docstatus": 1},
			fields=["name", "work_order", "posting_date"],
		)

	fg_completed_total = sum(flt(se.fg_completed_qty) for se in stock_entries_mfg)

	# 8. Payments & Advances
	total_advance_paid = sum(flt(so.advance_paid) for so in sales_orders)
	payment_entries = []
	if so_names and frappe.db.table_exists("Payment Entry Reference"):
		pe_names = scoped_rows(
			"Payment Entry Reference",
			filters={"reference_name": ["in", so_names], "docstatus": 1},
			pluck="parent",
		)
		if pe_names:
			payment_entries = scoped_rows(
				"Payment Entry",
				filters={"name": ["in", list(set(pe_names))], "docstatus": 1},
				fields=["name", "paid_amount", "posting_date"],
			)
			pe_sum = sum(flt(pe.paid_amount) for pe in payment_entries)
			if pe_sum > total_advance_paid:
				total_advance_paid = pe_sum

	# 9. Quality Inspections
	quality_inspections = scoped_rows(
		"Quality Inspection",
		filters={"docstatus": ["!=", 2]},
		fields=["name", "status", "inspection_type", "reference_type", "reference_name"],
		limit=20,
	)
	# Filter to this project or work orders
	relevant_qis = [
		qi
		for qi in quality_inspections
		if qi.reference_name in wo_names or qi.reference_name in so_names or qi.reference_name == project_name
	]

	# 10. Delivery Notes
	delivery_notes = []
	if so_names:
		dn_items = scoped_rows(
			"Delivery Note Item",
			filters={"against_sales_order": ["in", so_names], "docstatus": 1},
			pluck="parent",
		)
		if dn_items:
			delivery_notes = scoped_rows(
				"Delivery Note",
				filters={"name": ["in", list(set(dn_items))], "docstatus": 1},
				fields=["name", "status", "posting_date", "grand_total"],
			)
	if not delivery_notes:
		delivery_notes = scoped_rows(
			"Delivery Note",
			filters={"project": project_name, "docstatus": 1},
			fields=["name", "status", "posting_date", "grand_total"],
		)

	# 11. Sales Invoices
	sales_invoices = []
	if so_names:
		si_items = scoped_rows(
			"Sales Invoice Item",
			filters={"sales_order": ["in", so_names], "docstatus": 1},
			pluck="parent",
		)
		if si_items:
			sales_invoices = scoped_rows(
				"Sales Invoice",
				filters={"name": ["in", list(set(si_items))], "docstatus": 1},
				fields=["name", "status", "posting_date", "grand_total", "outstanding_amount"],
			)
	if not sales_invoices:
		sales_invoices = scoped_rows(
			"Sales Invoice",
			filters={"project": project_name, "docstatus": 1},
			fields=["name", "status", "posting_date", "grand_total", "outstanding_amount"],
		)

	# 12. Helper to inspect Job Cards by operation keywords
	def _get_op_status(keyword: str):
		matching_jcs = [jc for jc in job_cards if keyword.lower() in (jc.operation or "").lower()]
		if not matching_jcs:
			return None, []
		if all(jc.status == "Completed" for jc in matching_jcs):
			return "done", [jc.name for jc in matching_jcs]
		if any(jc.status in ("Work In Progress", "Open") for jc in matching_jcs):
			return "current", [jc.name for jc in matching_jcs]
		return "wait", [jc.name for jc in matching_jcs]

	# =========================================================================
	# RESOLVE ALL 26 INDIVIDUAL PIPELINE STEPS
	# =========================================================================
	stages = []

	# -------------------------------------------------------------------------
	# PHASE 1: COMMERCIAL & SALES ENGINEERING (Steps 1 to 8)
	# -------------------------------------------------------------------------

	# Step 1: Lead / Inquiry (Sakshi Sawant / Narendra Sir)
	lead_status = "done" if (leads or sales_orders or quotations or project.status != "Cancelled") else "wait"
	lead_badge = (
		f"{len(leads)} Lead(s) Logged"
		if leads
		else ("Lead Converted" if sales_orders else "Inquiry Received")
	)
	stages.append(
		{
			"id": "lead",
			"step_no": 1,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "1. Lead / Inquiry",
			"in_charge": "Sakshi Sawant / Narendra Sir",
			"department": "Sales & Marketing",
			"doctype": "Lead",
			"icon": "💬",
			"status": lead_status,
			"badge": lead_badge,
			"count": len(leads),
			"records": [l.name for l in leads],
			"info": "Initial customer market inquiry qualification",
		}
	)

	# Step 2: Requirement Collection (Narendra Sir / Raj / Samir Patil)
	req_status = "done" if (sales_orders or quotations or boms) else "current"
	req_badge = "Specs Gathered" if (sales_orders or quotations) else "Collecting Specs"
	stages.append(
		{
			"id": "req_collection",
			"step_no": 2,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "2. Requirement Collection",
			"in_charge": "Narendra Sir / Raj / Samir Patil",
			"department": "Technical Sales",
			"doctype": "Opportunity",
			"icon": "📋",
			"status": req_status,
			"badge": req_badge,
			"count": 1 if req_status == "done" else 0,
			"records": [],
			"info": "Technical and dimensional scope collection",
		}
	)

	# Step 3: Technical Evaluation & Marketing Drawing (Ubed / Tejas Patil)
	tech_status = "done" if (boms or sales_orders) else ("current" if quotations else "wait")
	tech_badge = (
		"Drawings Approved"
		if (boms or sales_orders)
		else ("Evaluation in Progress" if quotations else "Pending Specs")
	)
	stages.append(
		{
			"id": "tech_eval",
			"step_no": 3,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "3. Technical Evaluation (Drawing)",
			"in_charge": "Ubed / Tejas Patil",
			"department": "Design & Engineering",
			"doctype": "BOM",
			"icon": "📐",
			"status": tech_status,
			"badge": tech_badge,
			"count": len(boms),
			"records": [b.name for b in boms],
			"info": "Engineering feasibility & 2D/3D layout drawings",
		}
	)

	# Step 4: Costing / Estimation
	costing_status = "done" if (sales_orders or quotations) else "wait"
	costing_badge = "Costing Finalized" if (sales_orders or quotations) else "Pending Costing"
	stages.append(
		{
			"id": "costing",
			"step_no": 4,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "4. Costing / Estimation",
			"in_charge": "Estimation Team",
			"department": "Costing & Finance",
			"doctype": "Quotation",
			"icon": "🧮",
			"status": costing_status,
			"badge": costing_badge,
			"count": 1 if costing_status == "done" else 0,
			"records": [],
			"info": "BOM cost simulation, margins, and labor hours",
		}
	)

	# Step 5: Quotation (Sales)
	submitted_quotes = [q for q in quotations if q.get("docstatus") == 1]
	quote_status = "done" if (sales_orders or submitted_quotes) else ("current" if quotations else "wait")
	quote_badge = (
		f"{len(submitted_quotes)} Quote Submitted"
		if submitted_quotes
		else ("Quotation Accepted" if sales_orders else ("Draft Quote" if quotations else "No Quotation"))
	)
	stages.append(
		{
			"id": "quotation",
			"step_no": 5,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "5. Quotation",
			"in_charge": "Sales Department",
			"department": "Sales",
			"doctype": "Quotation",
			"icon": "📑",
			"status": quote_status,
			"badge": quote_badge,
			"count": len(quotations),
			"records": [q.name for q in quotations],
			"info": "Commercial proposal with pricing and delivery terms",
		}
	)

	# Step 6: Customer Approval & PO
	has_po = any(so.get("po_no") for so in sales_orders)
	cust_po_status = (
		"done"
		if (sales_orders and (has_po or any(s.docstatus == 1 for s in sales_orders)))
		else ("current" if quotations else "wait")
	)
	cust_po_badge = (
		f"PO: {sales_orders[0].get('po_no') or 'Approved'}"
		if (sales_orders and has_po)
		else ("Approved by Customer" if sales_orders else "Awaiting Approval")
	)
	stages.append(
		{
			"id": "customer_po",
			"step_no": 6,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "6. Customer PO & Approval",
			"in_charge": "Akshay Patil",
			"department": "Sales Administration",
			"doctype": "Sales Order",
			"icon": "🤝",
			"status": cust_po_status,
			"badge": cust_po_badge,
			"count": len(sales_orders),
			"records": so_names,
			"info": "Customer Purchase Order receipt and authorization",
		}
	)

	# Step 7: PO Verification (Akshay Patil)
	po_verif_status = (
		"done" if any(so.docstatus == 1 for so in sales_orders) else ("current" if sales_orders else "wait")
	)
	po_verif_badge = (
		"PO Verified & Logged"
		if po_verif_status == "done"
		else ("Under Verification" if sales_orders else "Awaiting PO")
	)
	stages.append(
		{
			"id": "po_verification",
			"step_no": 7,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "7. PO Verification",
			"in_charge": "Akshay Patil",
			"department": "Sales Operations",
			"doctype": "Sales Order",
			"icon": "🔍",
			"status": po_verif_status,
			"badge": po_verif_badge,
			"count": len(sales_orders),
			"records": so_names,
			"info": "Cross-verifying pricing, delivery schedules, and specs",
		}
	)

	# Step 8: Create Sales Order (Akshay Patil)
	submitted_sos = [so for so in sales_orders if so.docstatus == 1]
	so_status = "done" if submitted_sos else ("current" if sales_orders else "wait")
	so_badge = (
		f"{len(submitted_sos)} SO Submitted"
		if submitted_sos
		else (f"{len(sales_orders)} Draft SO" if sales_orders else "No Sales Order")
	)
	stages.append(
		{
			"id": "sales_order",
			"step_no": 8,
			"phase": "Commercial & Sales Engineering",
			"phase_no": 1,
			"label": "8. Create Sales Order",
			"in_charge": "Akshay Patil",
			"department": "Sales Operations",
			"doctype": "Sales Order",
			"icon": "📝",
			"status": so_status,
			"badge": so_badge,
			"count": len(sales_orders),
			"records": so_names,
			"info": "Confirmed sales order booking in ERPNext",
		}
	)

	# -------------------------------------------------------------------------
	# PHASE 2: ACCOUNTS, SCM, PLANNING & FABRICATION (Steps 9 to 16)
	# -------------------------------------------------------------------------

	# Step 9: Accounts Advance Approval (Pooja Chougule)
	if total_advance_paid > 0:
		accts_status = "done"
		accts_badge = f"Advance Received: ₹{total_advance_paid:,.0f}"
	elif submitted_sos:
		accts_status = "current"
		accts_badge = "Awaiting Advance Approval"
	else:
		accts_status = "wait"
		accts_badge = "Pending Sales Order"
	stages.append(
		{
			"id": "accounts_approval",
			"step_no": 9,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "9. Accounts Advance Approval",
			"in_charge": "Pooja Chougule",
			"department": "Accounts Team",
			"doctype": "Payment Entry",
			"icon": "💳",
			"status": accts_status,
			"badge": accts_badge,
			"count": len(payment_entries),
			"records": [p.name for p in payment_entries],
			"info": "Financial clearance & advance payment sign-off",
		}
	)

	# Step 10: Production Planning (Swapnil Mohite)
	if submitted_plans:
		plan_status = "done"
		plan_badge = f"{len(submitted_plans)} Submitted Plan"
	elif plans:
		plan_status = "current"
		plan_badge = f"{len(plans)} Draft Plan"
	elif work_orders:
		plan_status = "done"
		plan_badge = f"{len(work_orders)} Direct Work Orders"
	elif so_status == "done":
		plan_status = "current"
		plan_badge = "Ready for Planning"
	else:
		plan_status = "wait"
		plan_badge = "Pending Sales Order"
	stages.append(
		{
			"id": "production_plan",
			"step_no": 10,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "10. Production Planning",
			"in_charge": "Swapnil Mohite",
			"department": "PPC Department",
			"doctype": "Production Plan",
			"icon": "📊",
			"status": plan_status,
			"badge": plan_badge,
			"count": len(plans),
			"records": [p.name for p in plans],
			"info": "Master production scheduling and capacity reservation",
		}
	)

	# Step 11: Production Drawing (BOM) (Suraj Jirage)
	if submitted_active_boms:
		bom_status = "done"
		bom_badge = f"{len(submitted_active_boms)} Active BOM"
	elif boms:
		bom_status = "current"
		bom_badge = f"{len(boms)} Draft BOM"
	elif plan_status in ("done", "current"):
		bom_status = "current"
		bom_badge = "Drafting BOM"
	else:
		bom_status = "wait"
		bom_badge = "No BOM linked"
	stages.append(
		{
			"id": "bom",
			"step_no": 11,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "11. Production Drawing (BOM)",
			"in_charge": "Suraj Jirage",
			"department": "Design & Engineering",
			"doctype": "BOM",
			"icon": "📄",
			"status": bom_status,
			"badge": bom_badge,
			"count": len(boms),
			"records": [b.name for b in boms],
			"info": "Multi-level Bill of Materials and manufacturing drawings",
		}
	)

	# Step 12: Store Department (Abhishek Mohite) - Material Availability
	if stock_entries_transfer or stock_entries_mfg:
		store_status = "done"
		store_badge = f"{len(stock_entries_transfer)} Transfers Issued"
	elif work_orders:
		store_status = "current"
		store_badge = "Verifying Material Availability"
	elif bom_status == "done":
		store_status = "current"
		store_badge = "Checking Stock"
	else:
		store_status = "wait"
		store_badge = "Awaiting BOM"
	stages.append(
		{
			"id": "store_avail",
			"step_no": 12,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "12. Store Dept (Material Avail)",
			"in_charge": "Abhishek Mohite",
			"department": "Store Department",
			"doctype": "Stock Entry",
			"icon": "🏢",
			"status": store_status,
			"badge": store_badge,
			"count": len(stock_entries_transfer),
			"records": [s.name for s in stock_entries_transfer],
			"info": "Stock availability evaluation and store staging",
		}
	)

	# Step 13: Purchase Request & Material Receipt (Stores / Purchase Department)
	if stock_entries_transfer or (boms and wo_produced_qty > 0):
		purch_status = "done"
		purch_badge = "Materials In-Stock / Received"
	elif store_status == "current":
		purch_status = "current"
		purch_badge = "PO / Procurement Active"
	else:
		purch_status = "wait"
		purch_badge = "Pending Store Release"
	stages.append(
		{
			"id": "purchase_receipt",
			"step_no": 13,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "13. Purchase & Material Receipt",
			"in_charge": "Stores / Purchase Department",
			"department": "Purchase",
			"doctype": "Purchase Receipt",
			"icon": "📦",
			"status": purch_status,
			"badge": purch_badge,
			"count": 1 if purch_status == "done" else 0,
			"records": [],
			"info": "Material procurement, supplier PO, and Goods Receipt",
		}
	)

	# Step 14: Quality Check (QC Department) - Pass / Reject
	raw_qi_fail = [qi for qi in relevant_qis if qi.status == "Rejected"]
	if raw_qi_fail:
		raw_qc_status = "fail"
		raw_qc_badge = "⚠ Rejected (Return to Supplier)"
	elif purch_status == "done" or work_orders:
		raw_qc_status = "done"
		raw_qc_badge = "✓ Inbound QC Passed"
	elif purch_status == "current":
		raw_qc_status = "current"
		raw_qc_badge = "Inspecting Incoming Stock"
	else:
		raw_qc_status = "wait"
		raw_qc_badge = "Awaiting Delivery"
	stages.append(
		{
			"id": "raw_qc",
			"step_no": 14,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "14. Raw Material QC",
			"in_charge": "QC Department",
			"department": "Quality Control",
			"doctype": "Quality Inspection",
			"icon": "🔬",
			"status": raw_qc_status,
			"badge": raw_qc_badge,
			"count": len(relevant_qis),
			"records": [q.name for q in relevant_qis],
			"info": "Chemical, dimension, and hardness verification",
		}
	)

	# Step 15: Laser Cutting (Sheet & Pipe)
	op_cut_status, op_cut_recs = _get_op_status("cut")
	if op_cut_status:
		laser_status = op_cut_status
		laser_badge = "Cutting Completed" if op_cut_status == "done" else "Laser Cutting Active"
	elif wo_produced_qty > 0 or all(w.status == "Completed" for w in work_orders if work_orders):
		laser_status = "done"
		laser_badge = f"{wo_produced_qty:g} Units Cut"
	elif work_orders and any(w.status == "In Process" for w in work_orders):
		laser_status = "current"
		laser_badge = "Cutting Sheets & Pipes"
	elif work_orders:
		laser_status = "current"
		laser_badge = f"{len(work_orders)} WO Scheduled"
	else:
		laser_status = "wait"
		laser_badge = "Pending Work Orders"
	stages.append(
		{
			"id": "laser_cutting",
			"step_no": 15,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "15. Laser Cutting (Sheet & Pipe)",
			"in_charge": "Laser Cutting Shop",
			"department": "Fabrication",
			"doctype": "Job Card",
			"icon": "⚡",
			"status": laser_status,
			"badge": laser_badge,
			"count": len(op_cut_recs) or len(work_orders),
			"records": op_cut_recs or wo_names,
			"info": "CNC Laser Sheet Cutting & Rotary Tube/Pipe Profiling",
		}
	)

	# Step 16: Bending (as per Drawing)
	op_bend_status, op_bend_recs = _get_op_status("bend")
	if op_bend_status:
		bend_status = op_bend_status
		bend_badge = "Bending Completed" if op_bend_status == "done" else "Press Brake Bending"
	elif laser_status == "done" and (mfg_progress >= 40 or fg_completed_total > 0):
		bend_status = "done"
		bend_badge = "Bending Formed"
	elif laser_status in ("done", "current"):
		bend_status = "current"
		bend_badge = "Press Brake Bending"
	else:
		bend_status = "wait"
		bend_badge = "Awaiting Cutting"
	stages.append(
		{
			"id": "bending",
			"step_no": 16,
			"phase": "Accounts, SCM, Planning & Fabrication",
			"phase_no": 2,
			"label": "16. Bending (as per Drawing)",
			"in_charge": "Bending Department",
			"department": "Fabrication",
			"doctype": "Job Card",
			"icon": "📐",
			"status": bend_status,
			"badge": bend_badge,
			"count": len(op_bend_recs),
			"records": op_bend_recs,
			"info": "CNC hydraulic press brake bending as per engineering drawing",
		}
	)

	# -------------------------------------------------------------------------
	# PHASE 3: WELDING, FINISHING, QUALITY & DISPATCH (Steps 17 to 24)
	# -------------------------------------------------------------------------

	# Step 17: Cutting & Bending QC
	cut_qc_fail = any(
		"cut" in (q.reference_name or "").lower() and q.status == "Rejected" for q in relevant_qis
	)
	if cut_qc_fail:
		cut_qc_status = "fail"
		cut_qc_badge = "⚠ Dimensional Reject"
	elif bend_status == "done":
		cut_qc_status = "done"
		cut_qc_badge = "✓ Cutting QC Passed"
	elif bend_status == "current":
		cut_qc_status = "current"
		cut_qc_badge = "Checking Radii & Angles"
	else:
		cut_qc_status = "wait"
		cut_qc_badge = "Awaiting Bending"
	stages.append(
		{
			"id": "cutting_qc",
			"step_no": 17,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "17. Cutting & Bending QC",
			"in_charge": "QC Department",
			"department": "Quality Control",
			"doctype": "Quality Inspection",
			"icon": "🔍",
			"status": cut_qc_status,
			"badge": cut_qc_badge,
			"count": 1 if cut_qc_status == "done" else 0,
			"records": [],
			"info": "Dimensional tolerance, flange angles, and hole alignment",
		}
	)

	# Step 18: Welding (Dhashrat Salavi)
	op_weld_status, op_weld_recs = _get_op_status("weld")
	if op_weld_status:
		weld_status = op_weld_status
		weld_badge = "Welding Finished" if op_weld_status == "done" else "Welding In-Progress"
	elif mfg_progress >= 60 or fg_completed_total > 0:
		weld_status = "done"
		weld_badge = "Welding Completed"
	elif cut_qc_status == "done" or laser_status == "done":
		weld_status = "current"
		weld_badge = "TIG / MIG Welding Active"
	else:
		weld_status = "wait"
		weld_badge = "Awaiting Fabrication"
	stages.append(
		{
			"id": "welding",
			"step_no": 18,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "18. Welding",
			"in_charge": "Dhashrat Salavi",
			"department": "Welding Shop",
			"doctype": "Job Card",
			"icon": "🔥",
			"status": weld_status,
			"badge": weld_badge,
			"count": len(op_weld_recs),
			"records": op_weld_recs,
			"info": "Precision TIG/MIG welding and structural tacking",
		}
	)

	# Step 19: Welding QC
	if weld_status == "done":
		weld_qc_status = "done"
		weld_qc_badge = "✓ Weld Seams QC Passed"
	elif weld_status == "current":
		weld_qc_status = "current"
		weld_qc_badge = "Weld Inspection Active"
	else:
		weld_qc_status = "wait"
		weld_qc_badge = "Awaiting Welding"
	stages.append(
		{
			"id": "welding_qc",
			"step_no": 19,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "19. Welding Quality Check",
			"in_charge": "QC Department",
			"department": "Quality Control",
			"doctype": "Quality Inspection",
			"icon": "🔎",
			"status": weld_qc_status,
			"badge": weld_qc_badge,
			"count": 1 if weld_qc_status == "done" else 0,
			"records": [],
			"info": "Penetration check, weld bead consistency, and dye penetrant testing",
		}
	)

	# Step 20: Grinding / Finishing (Dhashrat Salavi)
	op_grind_status, op_grind_recs = _get_op_status("grind")
	if op_grind_status:
		grind_status = op_grind_status
		grind_badge = "Grinding Finished" if op_grind_status == "done" else "Deburring & Polishing"
	elif mfg_progress >= 75 or fg_completed_total > 0:
		grind_status = "done"
		grind_badge = "Grinding Completed"
	elif weld_qc_status == "done":
		grind_status = "current"
		grind_badge = "Grinding & Buffing"
	else:
		grind_status = "wait"
		grind_badge = "Awaiting Weld QC"
	stages.append(
		{
			"id": "grinding",
			"step_no": 20,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "20. Grinding / Finishing",
			"in_charge": "Dhashrat Salavi",
			"department": "Finishing Shop",
			"doctype": "Job Card",
			"icon": "✨",
			"status": grind_status,
			"badge": grind_badge,
			"count": len(op_grind_recs),
			"records": op_grind_recs,
			"info": "Weld spatter removal, seam leveling, and surface preparation",
		}
	)

	# Step 21: Painting / Powder Coating (Babaso Aagale)
	op_paint_status, op_paint_recs = _get_op_status("paint")
	if op_paint_status:
		paint_status = op_paint_status
		paint_badge = "Coating Completed" if op_paint_status == "done" else "Powder Coating In-Chamber"
	elif mfg_progress >= 90 or fg_completed_total > 0:
		paint_status = "done"
		paint_badge = "Powder Coating Done"
	elif grind_status == "done":
		paint_status = "current"
		paint_badge = "Pretreatment & Powder Coat"
	else:
		paint_status = "wait"
		paint_badge = "Awaiting Surface Finish"
	stages.append(
		{
			"id": "painting",
			"step_no": 21,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "21. Painting / Powder Coating",
			"in_charge": "Babaso Aagale",
			"department": "Coating Department",
			"doctype": "Job Card",
			"icon": "🎨",
			"status": paint_status,
			"badge": paint_badge,
			"count": len(op_paint_recs),
			"records": op_paint_recs,
			"info": "Phosphating, powder electrostatic spray, and oven curing",
		}
	)

	# Step 22: Final QC & Rework Assembly (QC / Shrikant Magdum)
	final_fail = any(
		"final" in (q.reference_name or "").lower() and q.status == "Rejected" for q in relevant_qis
	)
	if final_fail:
		final_qc_status = "fail"
		final_qc_badge = "⚠ Rework Required (Shrikant Magdum)"
	elif fg_completed_total >= wo_planned_qty and wo_planned_qty > 0:
		final_qc_status = "done"
		final_qc_badge = "✓ 100% Passed Final QC"
	elif paint_status == "done":
		final_qc_status = "current"
		final_qc_badge = "Final Assembly QC Active"
	else:
		final_qc_status = "wait"
		final_qc_badge = "Awaiting Coating"
	stages.append(
		{
			"id": "final_qc",
			"step_no": 22,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "22. Final QC & Rework Assembly",
			"in_charge": "QC / Shrikant Magdum",
			"department": "Quality Assurance",
			"doctype": "Quality Inspection",
			"icon": "🎯",
			"status": final_qc_status,
			"badge": final_qc_badge,
			"count": 1 if final_qc_status == "done" else 0,
			"records": [],
			"info": "Micrometer tolerance, DFT coating thickness, and final signoff",
		}
	)

	# Step 23: Packing & Transportation
	if delivery_notes or any(so.per_delivered >= 100 for so in sales_orders):
		pack_status = "done"
		pack_badge = "Packed & Transport Staged"
	elif final_qc_status == "done":
		pack_status = "current"
		pack_badge = "Packing & Crating Active"
	else:
		pack_status = "wait"
		pack_badge = "Awaiting Final QC"
	stages.append(
		{
			"id": "packing",
			"step_no": 23,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "23. Packing & Transportation",
			"in_charge": "Logistics Team",
			"department": "Logistics",
			"doctype": "Delivery Note",
			"icon": "📦",
			"status": pack_status,
			"badge": pack_badge,
			"count": len(delivery_notes),
			"records": [d.name for d in delivery_notes],
			"info": "Protective bubble/crate packaging and carrier dispatching",
		}
	)

	# Step 24: Documentation & Dispatch (Pooja Chougule / Samir Patil)
	# Encapsulates GST Tax Invoicing, Government E-Way Bill, Delivery Challan, Customer Gate Delivery, and Samir Patil Site Installation & Customer Feedback.
	submitted_sis = [si for si in sales_invoices if si.docstatus == 1]
	delivered_dns = [dn for dn in delivery_notes if dn.status in ("Delivered", "Completed")]
	if project.status == "Completed" or flt(project.percent_complete) >= 100:
		doc_disp_status = "done"
		doc_disp_badge = "✓ Invoiced, Delivered & Closed"
	elif submitted_sis and (delivered_dns or any(so.per_delivered >= 100 for so in sales_orders)):
		doc_disp_status = "done"
		doc_disp_badge = f"✓ {len(submitted_sis)} Invoiced & Delivered"
	elif submitted_sis or delivered_dns:
		doc_disp_status = "done"
		doc_disp_badge = f"✓ {len(submitted_sis)} Invoiced & Staged"
	elif pack_status == "done" or delivery_notes or sales_invoices:
		doc_disp_status = "current"
		doc_disp_badge = "⚡ Invoicing & Dispatch Active"
	else:
		doc_disp_status = "wait"
		doc_disp_badge = "Awaiting Packaging"

	stages.append(
		{
			"id": "documentation_dispatch",
			"step_no": 24,
			"phase": "Welding, Finishing, Quality & Dispatch",
			"phase_no": 3,
			"label": "24. Documentation & Dispatch",
			"in_charge": "Pooja Chougule / Samir Patil",
			"department": "Accounts, Dispatch & Field",
			"doctype": "Sales Invoice / Delivery Note",
			"icon": "🚚",
			"status": doc_disp_status,
			"badge": doc_disp_badge,
			"count": len(sales_invoices) + len(delivery_notes),
			"records": [s.name for s in sales_invoices] + [d.name for d in delivery_notes],
			"info": "Encapsulates GST Tax Invoicing, Government E-Way Bill, Delivery Challan, Customer Gate Delivery, and Samir Patil Site Installation & Customer Feedback",
		}
	)

	# Backward compatibility aliases for legacy stage tests/consumers
	stages_by_id = {s["id"]: s for s in stages}
	doc_disp_stage = stages_by_id.get("documentation_dispatch", stages[-1])
	legacy_stages = {
		"work_order": dict(
			stages_by_id.get("laser_cutting", stages[0]),
			id="work_order",
			label="Work Order",
			doctype="Work Order",
		),
		"job_card": dict(
			stages_by_id.get("welding", stages[0]),
			id="job_card",
			label="Production Execution",
			doctype="Work Order",
		),
		"stock_entry": dict(
			stages_by_id.get("final_qc", stages[0]),
			id="stock_entry",
			label="Manufactured Stock",
			doctype="Stock Entry",
		),
		"dispatch": dict(
			doc_disp_stage, id="dispatch", label="Documentation & Dispatch", doctype="Delivery Note"
		),
		"documentation": dict(
			doc_disp_stage, id="documentation", label="Documentation & Dispatch", doctype="Sales Invoice"
		),
		"installation_feedback": dict(
			doc_disp_stage, id="installation_feedback", label="Documentation & Dispatch", doctype="Task"
		),
	}

	# If project is marked Completed, mark all 24 stages as completed
	if project.status == "Completed":
		for s in stages:
			s["status"] = "done"
			if not str(s.get("badge") or "").startswith("✓"):
				s["badge"] = "✓ Completed & Signed Off"

	# Find the current active step in progress
	current_step = next((s for s in stages if s["status"] == "current"), None)
	if not current_step:
		current_step = next((s for s in stages if s["status"] == "wait"), stages[-1])

	completed_count = sum(1 for s in stages if s["status"] == "done")
	total_steps = len(stages)
	pipeline_percent = round((completed_count / total_steps) * 100, 1)

	# Step 7 (PO Verification - Akshay Patil) check
	step7_stage = next((s for s in stages if s.get("step_no") == 7), None)
	step7_completed = bool(step7_stage and step7_stage.get("status") == "done")

	# Phase 1: Commercial & Sales Engineering (Steps 1 to 8)
	line1_stages = stages[:8]
	line1_completed_count = sum(1 for s in line1_stages if s.get("status") == "done")
	line1_percent = round((line1_completed_count / 8.0) * 100, 1)
	# Line 1 is completed if all 8 steps are done OR if Step 8 (Create Sales Order) is submitted/done
	line1_completed = (line1_completed_count >= 8) or (len(stages) >= 8 and stages[7].get("status") == "done")

	line1_current_step = next((s for s in line1_stages if s.get("status") == "current"), None)
	if not line1_current_step:
		line1_current_step = next(
			(s for s in line1_stages if s.get("status") == "wait"), line1_stages[-1] if line1_stages else None
		)

	# Phase 2 & 3: Manufacturing & Delivery (Steps 9 to 24)
	mfg_stages = stages[8:24]
	mfg_completed_count = sum(1 for s in mfg_stages if s.get("status") == "done")
	mfg_total_steps = len(mfg_stages)  # 16
	mfg_percent = round((mfg_completed_count / (mfg_total_steps or 1)) * 100, 1)

	mfg_current_step = next((s for s in mfg_stages if s.get("status") == "current"), None)
	if not mfg_current_step:
		mfg_current_step = next(
			(s for s in mfg_stages if s.get("status") == "wait"), mfg_stages[-1] if mfg_stages else None
		)

	return {
		"project": project.name,
		"project_name": project.project_name or project.name,
		"customer": customer,
		"status": project.status,
		"step7_completed": step7_completed,
		"po_verified": step7_completed,
		"percent_complete": flt(project.percent_complete),
		"manufacturing_progress": mfg_progress,
		"pipeline_percent": pipeline_percent,
		"completed_count": completed_count,
		"total_steps": total_steps,
		"current_step": current_step,
		"wo_planned_qty": wo_planned_qty,
		"wo_produced_qty": wo_produced_qty,
		"expected_end_date": str(project.expected_end_date or ""),
		"sales_orders": sales_orders,
		"stages": stages,
		"legacy_stages": legacy_stages,
		"line1_completed": line1_completed,
		"line1_completed_count": line1_completed_count,
		"line1_percent": line1_percent,
		"line1_current_step": line1_current_step,
		"mfg_completed_count": mfg_completed_count,
		"mfg_total_steps": mfg_total_steps,
		"mfg_percent": mfg_percent,
		"mfg_current_step": mfg_current_step,
	}


def _resolve_project_boms(project) -> list:
	"""Finds all explicit and Work Order linked BOMs for this Project."""
	boms = {}

	# Check custom_sarathi_bom on Project
	if hasattr(project, "custom_sarathi_bom") and project.custom_sarathi_bom:
		info = scoped_value(
			"BOM",
			project.custom_sarathi_bom,
			["name", "item", "docstatus", "is_active"],
			as_dict=True,
		)
		if info:
			boms[info.name] = info

	# Check custom_sarathi_project on BOM
	if frappe.db.has_column("BOM", "custom_sarathi_project"):
		for b in scoped_rows(
			"BOM",
			filters={"custom_sarathi_project": project.name, "docstatus": ["!=", 2]},
			fields=["name", "item", "docstatus", "is_active"],
		):
			boms[b.name] = b

	# Check BOMs on project Work Orders
	wo_boms = scoped_rows(
		"Work Order",
		filters={"project": project.name, "docstatus": ["!=", 2]},
		pluck="bom_no",
	)
	for bom_no in set(wo_boms) - {None, ""}:
		if bom_no not in boms and frappe.db.exists("BOM", bom_no):
			info = scoped_value(
				"BOM", bom_no, ["name", "item", "docstatus", "is_active"], as_dict=True
			)
			if info:
				boms[info.name] = info

	return list(boms.values())


def _resolve_production_plans(project_name: str, so_names: list) -> list:
	"""Resolves Production Plans directly linked or linked via Sales Orders."""
	plans = {}

	if frappe.db.has_column("Production Plan", "project"):
		for p in scoped_rows(
			"Production Plan",
			filters={"project": project_name, "docstatus": ["!=", 2]},
			fields=["name", "docstatus", "status"],
		):
			plans[p.name] = p

	# Check via Sales Orders
	if so_names and frappe.db.table_exists("Production Plan Sales Order"):
		pp_so = scoped_rows(
			"Production Plan Sales Order",
			filters={"sales_order": ["in", so_names]},
			pluck="parent",
		)
		for parent in set(pp_so):
			if parent not in plans and frappe.db.exists("Production Plan", parent):
				info = scoped_value(
					"Production Plan",
					parent,
					["name", "docstatus", "status"],
					as_dict=True,
				)
				if info and info.docstatus != 2:
					plans[info.name] = info

	# Check child table Production Plan Item
	if so_names and frappe.db.table_exists("Production Plan Item"):
		if frappe.db.has_column("Production Plan Item", "sales_order"):
			pp_items = scoped_rows(
				"Production Plan Item",
				filters={"sales_order": ["in", so_names]},
				pluck="parent",
			)
			for parent in set(pp_items):
				if parent not in plans and frappe.db.exists("Production Plan", parent):
					info = scoped_value(
						"Production Plan",
						parent,
						["name", "docstatus", "status"],
						as_dict=True,
					)
					if info and info.docstatus != 2:
						plans[info.name] = info

	return list(plans.values())
