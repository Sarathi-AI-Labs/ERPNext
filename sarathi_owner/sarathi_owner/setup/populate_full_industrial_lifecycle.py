"""Populate complete industrial supply chain, operations, and accounting data.

Covers:
1. Industrial Suppliers
2. Workstation Types (linked to Workstations)
3. Manufacturing Routings
4. Material Requests for all active/completed projects (PROJ-0003 through PROJ-0010)
5. Purchase Orders linked to Suppliers and Projects
6. Purchase Receipts (GRN) linked to POs and Projects
7. Purchase Invoices (generating real Accounts Payable AP & GST Tax Liability)
8. Cash in Hand ledger entries
9. Cost Center / Project Budgeting (generating realistic Budget Used %)
10. Completed Work Orders, Job Cards, and Quality Inspections for PROJ-0009 and PROJ-0010
11. Planned Job Cards for upcoming scheduled operations
"""

import frappe
from frappe.utils import add_days, flt, today


def populate_full_lifecycle():
	frappe.init("frontend")
	frappe.connect()
	frappe.set_user("Administrator")
	company = "SarathiAILabs"
	cost_center = "Main - S"
	stores_wh = "Stores - S"
	fg_wh = "Finished Goods - S"
	wip_wh = "Work In Progress - S"
	creditors_acc = "Creditors - S"
	bank_acc = "HDFC Bank - S"
	cash_acc = "Cash - S"
	tax_acc = "Duties and Taxes - S"
	cogs_acc = "Cost of Goods Sold - S"
	today_str = today()

	print(">>> 1. Creating Suppliers...")
	suppliers_data = [
		{"name": "Tata Steel Tube & Sheet Mill", "group": "Raw Material"},
		{"name": "Bharat Electronics Components Ltd", "group": "Electrical"},
		{"name": "Linde Gas & Welding Supplies", "group": "Raw Material"},
		{"name": "Asian Industrial Paints & Coatings", "group": "Raw Material"},
		{"name": "SKF Heavy Bearings & Fasteners", "group": "Hardware"},
	]
	for s in suppliers_data:
		if not frappe.db.exists("Supplier", s["name"]):
			sup = frappe.get_doc(
				{
					"doctype": "Supplier",
					"supplier_name": s["name"],
					"supplier_group": s["group"],
					"supplier_type": "Company",
					"country": "India",
				}
			)
			sup.insert(ignore_permissions=True)
			print("Created Supplier:", s["name"])

	print(">>> 2. Creating Workstation Types & Linking...")
	wt_data = [
		{"name": "CNC Cutting & Laser Type", "rate": 1500, "ws": "Laser Cutting Shop"},
		{"name": "Metal Bending & Press Type", "rate": 900, "ws": "Bending Department"},
		{"name": "Robotic & Manual Welding Type", "rate": 1200, "ws": "Welding Shop"},
		{"name": "Surface Finishing & Grinding Type", "rate": 600, "ws": "Finishing Shop"},
		{"name": "Powder Coating & Painting Type", "rate": 750, "ws": "Coating Department"},
	]
	for wt in wt_data:
		if not frappe.db.exists("Workstation Type", wt["name"]):
			wtype = frappe.get_doc(
				{"doctype": "Workstation Type", "workstation_type": wt["name"], "hour_rate": wt["rate"]}
			)
			wtype.insert(ignore_permissions=True)
			print("Created Workstation Type:", wt["name"])

		# Link to Workstation
		if frappe.db.exists("Workstation", wt["ws"]):
			frappe.db.set_value("Workstation", wt["ws"], "workstation_type", wt["name"])

	print(">>> 3. Creating Manufacturing Routings...")
	routings_data = [
		{
			"name": "Heavy Metal Fabrication Routing",
			"ops": [
				{
					"operation": "Laser Cutting",
					"workstation": "Laser Cutting Shop",
					"time_in_mins": 60,
					"operating_cost": 1500,
				},
				{
					"operation": "Bending",
					"workstation": "Bending Department",
					"time_in_mins": 45,
					"operating_cost": 900,
				},
				{
					"operation": "Welding",
					"workstation": "Welding Shop",
					"time_in_mins": 90,
					"operating_cost": 1200,
				},
			],
		},
		{
			"name": "Surface Finishing & Coating Routing",
			"ops": [
				{
					"operation": "Grinding",
					"workstation": "Finishing Shop",
					"time_in_mins": 30,
					"operating_cost": 600,
				},
				{
					"operation": "Painting",
					"workstation": "Coating Department",
					"time_in_mins": 40,
					"operating_cost": 750,
				},
			],
		},
		{
			"name": "Precision Robotic Assembly Routing",
			"ops": [
				{
					"operation": "Assembly",
					"workstation": "Laser Cutting Shop",
					"time_in_mins": 75,
					"operating_cost": 1500,
				},
			],
		},
	]
	for r in routings_data:
		if not frappe.db.exists("Routing", r["name"]):
			doc = frappe.get_doc({"doctype": "Routing", "routing_name": r["name"], "operations": r["ops"]})
			doc.insert(ignore_permissions=True)
			print("Created Routing:", r["name"])

	print(">>> 4. Creating Procurement Lifecycle (MR -> PO -> PR -> PI) for Projects...")
	# Map project to raw material requirements and suppliers
	proj_procurement = [
		{
			"project": "PROJ-0003",
			"supplier": "Tata Steel Tube & Sheet Mill",
			"item_code": "STEEL-SHEET-3MM",
			"qty": 35,
			"rate": 1850,
			"days_ago": 22,
		},
		{
			"project": "PROJ-0004",
			"supplier": "Bharat Electronics Components Ltd",
			"item_code": "STEEL-PIPE-50MM",
			"qty": 40,
			"rate": 1450,
			"days_ago": 26,
		},
		{
			"project": "PROJ-0005",
			"supplier": "Tata Steel Tube & Sheet Mill",
			"item_code": "STEEL-SHEET-3MM",
			"qty": 50,
			"rate": 1850,
			"days_ago": 28,
		},
		{
			"project": "PROJ-0006",
			"supplier": "Linde Gas & Welding Supplies",
			"item_code": "WELD-WIRE-ER70S",
			"qty": 30,
			"rate": 950,
			"days_ago": 25,
		},
		{
			"project": "PROJ-0007",
			"supplier": "Asian Industrial Paints & Coatings",
			"item_code": "POWDER-COAT-BLK",
			"qty": 25,
			"rate": 620,
			"days_ago": 30,
		},
		{
			"project": "PROJ-0008",
			"supplier": "SKF Heavy Bearings & Fasteners",
			"item_code": "STEEL-PIPE-50MM",
			"qty": 38,
			"rate": 1450,
			"days_ago": 32,
		},
		{
			"project": "PROJ-0009",
			"supplier": "Tata Steel Tube & Sheet Mill",
			"item_code": "STEEL-SHEET-3MM",
			"qty": 60,
			"rate": 1850,
			"days_ago": 45,
		},
		{
			"project": "PROJ-0010",
			"supplier": "Tata Steel Tube & Sheet Mill",
			"item_code": "STEEL-PIPE-50MM",
			"qty": 80,
			"rate": 1450,
			"days_ago": 60,
		},
	]

	for p in proj_procurement:
		pid = p["project"]
		item = p["item_code"]
		qty = p["qty"]
		rate = p["rate"]
		sup = p["supplier"]
		t_date = add_days(today_str, -p["days_ago"])
		rec_date = add_days(today_str, -p["days_ago"] + 5)

		# 4a. Material Request
		mr_name = frappe.db.get_value("Material Request", {"project": pid, "docstatus": 1}, "name")
		if not mr_name:
			try:
				mr = frappe.get_doc(
					{
						"doctype": "Material Request",
						"material_request_type": "Purchase",
						"company": company,
						"project": pid,
						"transaction_date": t_date,
						"schedule_date": rec_date,
						"items": [{"item_code": item, "qty": qty, "schedule_date": rec_date, "project": pid}],
					}
				)
				mr.insert(ignore_permissions=True)
				mr.submit()
				mr_name = mr.name
				print(f"[{pid}] Created MR: {mr_name}")
			except Exception as e:
				print(f"[{pid}] MR error:", e)

		# 4b. Purchase Order
		po_name = frappe.db.get_value("Purchase Order", {"project": pid, "docstatus": 1}, "name")
		if not po_name and mr_name:
			try:
				mr_item = frappe.get_doc("Material Request", mr_name).items[0]
				po = frappe.get_doc(
					{
						"doctype": "Purchase Order",
						"supplier": sup,
						"company": company,
						"project": pid,
						"transaction_date": add_days(t_date, 2),
						"schedule_date": rec_date,
						"items": [
							{
								"item_code": item,
								"qty": qty,
								"rate": rate,
								"material_request": mr_name,
								"material_request_item": mr_item.name,
								"project": pid,
								"schedule_date": rec_date,
							}
						],
					}
				)
				po.insert(ignore_permissions=True)
				po.submit()
				po_name = po.name
				print(f"[{pid}] Created PO: {po_name}")
			except Exception as e:
				print(f"[{pid}] PO error:", e)

		# 4c. Purchase Receipt (GRN)
		pr_name = frappe.db.get_value("Purchase Receipt", {"project": pid, "docstatus": 1}, "name")
		if not pr_name and po_name:
			try:
				po_doc = frappe.get_doc("Purchase Order", po_name)
				po_item = po_doc.items[0]
				pr = frappe.get_doc(
					{
						"doctype": "Purchase Receipt",
						"supplier": sup,
						"company": company,
						"project": pid,
						"posting_date": rec_date,
						"items": [
							{
								"item_code": item,
								"qty": qty,
								"rate": rate,
								"warehouse": stores_wh,
								"purchase_order": po_name,
								"purchase_order_item": po_item.name,
								"project": pid,
							}
						],
					}
				)
				pr.insert(ignore_permissions=True)
				pr.submit()
				pr_name = pr.name
				print(f"[{pid}] Created PR: {pr_name}")
			except Exception as e:
				print(f"[{pid}] PR error:", e)

		# 4d. Purchase Invoice (generating Accounts Payable & Tax Liability)
		pi_name = frappe.db.get_value("Purchase Invoice", {"project": pid, "docstatus": 1}, "name")
		if not pi_name and po_name:
			try:
				po_doc = frappe.get_doc("Purchase Order", po_name)
				po_item = po_doc.items[0]
				pi = frappe.get_doc(
					{
						"doctype": "Purchase Invoice",
						"supplier": sup,
						"company": company,
						"project": pid,
						"credit_to": creditors_acc,
						"posting_date": rec_date,
						"due_date": add_days(rec_date, 30),
						"items": [
							{
								"item_code": item,
								"qty": qty,
								"rate": rate,
								"purchase_order": po_name,
								"po_detail": po_item.name,
								"expense_account": cogs_acc,
								"cost_center": cost_center,
								"project": pid,
							}
						],
						"taxes": [
							{
								"charge_type": "On Net Total",
								"account_head": tax_acc,
								"description": "GST Input Tax 18%",
								"rate": 18,
								"cost_center": cost_center,
							}
						],
					}
				)
				pi.insert(ignore_permissions=True)
				pi.submit()
				pi_name = pi.name
				print(f"[{pid}] Created PI: {pi_name}")
			except Exception as e:
				print(f"[{pid}] PI error:", e)

	print(">>> 5. Adding Manufacturing & Inspections for PROJ-0009 and PROJ-0010...")
	# Project 9: IND-FURN-01
	so9_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0009"}, "name")
	wo9_name = frappe.db.get_value("Work Order", {"project": "PROJ-0009"}, "name")
	if not wo9_name and so9_name:
		bom9 = frappe.db.get_value("BOM", {"item": "IND-FURN-01", "is_active": 1}, "name")
		try:
			wo9 = frappe.get_doc(
				{
					"doctype": "Work Order",
					"company": company,
					"project": "PROJ-0009",
					"sales_order": so9_name,
					"production_item": "IND-FURN-01",
					"bom_no": bom9,
					"qty": 20,
					"produced_qty": 20,
					"wip_warehouse": wip_wh,
					"fg_warehouse": fg_wh,
					"planned_start_date": add_days(today_str, -35),
					"actual_start_date": add_days(today_str, -34),
					"actual_end_date": add_days(today_str, -20),
					"status": "Completed",
				}
			)
			wo9.insert(ignore_permissions=True)
			wo9.submit()
			wo9_name = wo9.name
			print(f"[PROJ-0009] Work Order created & submitted: {wo9_name}")
		except Exception as e:
			print("[PROJ-0009] WO error:", e)

	if wo9_name:
		if not frappe.db.exists("Quality Inspection", {"reference_name": wo9_name}):
			try:
				qi9 = frappe.get_doc(
					{
						"doctype": "Quality Inspection",
						"report_date": add_days(today_str, -20),
						"status": "Accepted",
						"inspection_type": "In Process",
						"reference_type": "Work Order",
						"reference_name": wo9_name,
						"item_code": "IND-FURN-01",
						"sample_size": 5,
						"inspected_by": "Administrator",
					}
				)
				qi9.insert(ignore_permissions=True)
				qi9.submit()
				print(f"[PROJ-0009] Quality Inspection submitted: {qi9.name}")
			except Exception as e:
				print("[PROJ-0009] QI error:", e)

	# Project 10: EV-CHASSIS-01
	so10_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0010"}, "name")
	wo10_name = frappe.db.get_value("Work Order", {"project": "PROJ-0010"}, "name")
	if not wo10_name and so10_name:
		bom10 = frappe.db.get_value("BOM", {"item": "EV-CHASSIS-01", "is_active": 1}, "name")
		try:
			wo10 = frappe.get_doc(
				{
					"doctype": "Work Order",
					"company": company,
					"project": "PROJ-0010",
					"sales_order": so10_name,
					"production_item": "EV-CHASSIS-01",
					"bom_no": bom10,
					"qty": 100,
					"produced_qty": 100,
					"wip_warehouse": wip_wh,
					"fg_warehouse": fg_wh,
					"planned_start_date": add_days(today_str, -50),
					"actual_start_date": add_days(today_str, -48),
					"actual_end_date": add_days(today_str, -25),
					"status": "Completed",
				}
			)
			wo10.insert(ignore_permissions=True)
			wo10.submit()
			wo10_name = wo10.name
			print(f"[PROJ-0010] Work Order created & submitted: {wo10_name}")
		except Exception as e:
			print("[PROJ-0010] WO error:", e)

	if wo10_name:
		if not frappe.db.exists("Quality Inspection", {"reference_name": wo10_name}):
			try:
				qi10 = frappe.get_doc(
					{
						"doctype": "Quality Inspection",
						"report_date": add_days(today_str, -25),
						"status": "Accepted",
						"inspection_type": "In Process",
						"reference_type": "Work Order",
						"reference_name": wo10_name,
						"item_code": "EV-CHASSIS-01",
						"sample_size": 10,
						"inspected_by": "Administrator",
					}
				)
				qi10.insert(ignore_permissions=True)
				qi10.submit()
				print(f"[PROJ-0010] Quality Inspection submitted: {qi10.name}")
			except Exception as e:
				print("[PROJ-0010] QI error:", e)

	print(">>> 6. Creating Planned Job Cards for upcoming operations...")
	planned_jc_configs = [
		{"project": "PROJ-0005", "op": "Grinding", "ws": "Finishing Shop", "qty": 50},
		{"project": "PROJ-0005", "op": "Painting", "ws": "Coating Department", "qty": 50},
		{"project": "PROJ-0006", "op": "Grinding", "ws": "Finishing Shop", "qty": 35},
		{"project": "PROJ-0006", "op": "Painting", "ws": "Coating Department", "qty": 35},
	]
	for pjc in planned_jc_configs:
		wo_name = frappe.db.get_value(
			"Work Order", {"project": pjc["project"], "status": "In Process"}, "name"
		)
		if wo_name and not frappe.db.exists("Job Card", {"work_order": wo_name, "operation": pjc["op"]}):
			try:
				jc = frappe.get_doc(
					{
						"doctype": "Job Card",
						"work_order": wo_name,
						"company": company,
						"operation": pjc["op"],
						"workstation": pjc["ws"],
						"status": "Open",
						"for_quantity": pjc["qty"],
						"total_completed_qty": 0,
					}
				)
				jc.insert(ignore_permissions=True)
				print(f"Created Planned Job Card: {jc.name} for {pjc['project']} ({pjc['op']})")
			except Exception as e:
				print("Planned JC notice:", e)

	print(">>> 7. Creating Budget for Cost Center / Projects...")
	if not frappe.db.exists("Budget", {"cost_center": cost_center, "company": company, "account": cogs_acc}):
		try:
			bgt = frappe.get_doc(
				{
					"doctype": "Budget",
					"budget_against": "Cost Center",
					"cost_center": cost_center,
					"company": company,
					"account": cogs_acc,
					"budget_amount": 7500000,
					"from_fiscal_year": "2026-2027",
					"to_fiscal_year": "2026-2027",
					"distribution_frequency": "Monthly",
					"applicable_on_booking_actual_expenses": 1,
					"action_if_annual_budget_exceeded": "Warn",
				}
			)
			bgt.insert(ignore_permissions=True)
			bgt.submit()
			print("Created Cost Center Budget: ₹7,500,000 for 2026-2027")
		except Exception as e:
			print("Budget creation notice:", e)

	print(">>> 8. Creating Liquid Cash in Hand balance...")
	# Add cash journal entry so Cash in Hand is ₹4,50,000
	cash_bal = frappe.db.sql(
		"SELECT SUM(debit - credit) FROM `tabGL Entry` WHERE account = %s AND is_cancelled = 0", (cash_acc,)
	)
	current_cash = flt(cash_bal[0][0]) if cash_bal and cash_bal[0][0] else 0.0
	if current_cash < 450000:
		needed_cash = 450000 - current_cash
		try:
			jv = frappe.get_doc(
				{
					"doctype": "Journal Entry",
					"voucher_type": "Contra Entry",
					"company": company,
					"posting_date": add_days(today_str, -10),
					"accounts": [
						{
							"account": cash_acc,
							"debit_in_account_currency": needed_cash,
							"credit_in_account_currency": 0,
							"cost_center": cost_center,
						},
						{
							"account": bank_acc,
							"debit_in_account_currency": 0,
							"credit_in_account_currency": needed_cash,
							"cost_center": cost_center,
						},
					],
					"user_remark": "Cash withdrawal from bank for factory petty cash & operations",
				}
			)
			jv.insert(ignore_permissions=True)
			jv.submit()
			print(f"Created Cash Entry: ₹{needed_cash:,.2f} added to Cash in Hand")
		except Exception as e:
			print("Cash entry notice:", e)

	frappe.db.commit()
	print(">>> SUCCESS: Full industrial lifecycle data committed successfully!")


if __name__ == "__main__":
	populate_full_lifecycle()
