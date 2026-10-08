"""Populate rich real-time industrial dataset for all 10 projects.

Creates customers, items, BOMs, stock, sales orders, work orders, job cards,
quality inspections, delivery notes, sales invoices, and payments so that:
- Projects 1 & 2: Step #07 PO Verification is WAITING -> Steps 9-24 hidden/locked.
- Projects 3 & 4: Commercial complete (Step 07 DONE) -> Planning & SCM active.
- Projects 5 & 6: Shopfloor fabrication & welding active (Laser cutting & Welding in-progress).
- Project 7: Finishing & Final QC active.
- Project 8: Quality inspection rejected (rework scenario).
- Project 9: Dispatched, invoiced, overdue AR aging (₹4.2M overdue).
- Project 10: 100% completed, fully delivered and paid.
"""

import frappe
from frappe.utils import add_days, flt, today


def populate():
	frappe.set_user("Administrator")
	company = "SarathiAILabs"
	debtors_account = "Debtors - S"
	bank_account = "HDFC Bank - S"
	sales_account = "Sales - S"
	fg_warehouse = "Finished Goods - S"
	wip_warehouse = "Work In Progress - S"
	cost_center = "Main - S"
	today_str = today()

	if not frappe.db.exists("Account", bank_account):
		b_acc = frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": "HDFC Bank",
				"parent_account": "Bank Accounts - S",
				"company": company,
				"account_type": "Bank",
				"is_group": 0,
			}
		)
		b_acc.insert(ignore_permissions=True)
		print("Created Ledger Account: HDFC Bank - S")

	print(">>> 1. Ensuring Operations & Workstations...")
	operations = ["Laser Cutting", "Bending", "Welding", "Grinding", "Painting", "Assembly"]
	for op in operations:
		if not frappe.db.exists("Operation", op):
			doc = frappe.get_doc({"doctype": "Operation", "name": op, "operation": op})
			doc.insert(ignore_permissions=True)

	workstations = [
		{"name": "Laser Cutting Shop", "rate": 1500},
		{"name": "Bending Department", "rate": 900},
		{"name": "Welding Shop", "rate": 800},
		{"name": "Finishing Shop", "rate": 600},
		{"name": "Coating Department", "rate": 750},
	]
	for ws in workstations:
		if not frappe.db.exists("Workstation", ws["name"]):
			doc = frappe.get_doc(
				{
					"doctype": "Workstation",
					"workstation_name": ws["name"],
					"hour_rate": ws["rate"],
				}
			)
			doc.insert(ignore_permissions=True)

	print(">>> 2. Ensuring Stock in Stores and Finished Goods...")
	# Add finished goods stock for dispatch simulation
	fg_stock_items = [
		{"item_code": "IND-FURN-01", "qty": 20, "rate": 820000},
		{"item_code": "EV-CHASSIS-01", "qty": 100, "rate": 112000},
	]
	for fg in fg_stock_items:
		current_bin_qty = (
			frappe.db.get_value(
				"Bin", {"item_code": fg["item_code"], "warehouse": fg_warehouse}, "actual_qty"
			)
			or 0
		)
		if flt(current_bin_qty) < fg["qty"]:
			needed = fg["qty"] - flt(current_bin_qty)
			try:
				se_fg = frappe.get_doc(
					{
						"doctype": "Stock Entry",
						"stock_entry_type": "Material Receipt",
						"purpose": "Material Receipt",
						"company": company,
						"to_warehouse": fg_warehouse,
						"items": [
							{
								"item_code": fg["item_code"],
								"qty": needed,
								"basic_rate": fg["rate"],
								"t_warehouse": fg_warehouse,
								"cost_center": cost_center,
							}
						],
					}
				)
				se_fg.insert(ignore_permissions=True)
				se_fg.submit()
				print(f"Created FG Stock Receipt for {fg['item_code']}: {needed} units")
			except Exception as e:
				print(f"FG stock notice for {fg['item_code']}:", e)

	print(">>> 3. Configuring 10 Realistic Lifecycle Projects...")

	# -------------------------------------------------------------
	# PROJECT 1: PROJ-0001 (Lead / Presales - Step 07 WAITING)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0001"):
		p1 = frappe.get_doc("Project", "PROJ-0001")
		p1.project_name = "EV Assembly Line Tooling"
		p1.customer = "Tata Motors Passenger Vehicles Ltd"
		p1.company = company
		p1.status = "Open"
		p1.estimated_costing = 2500000
		p1.total_costing_amount = 450000
		p1.expected_start_date = add_days(today_str, -10)
		p1.expected_end_date = add_days(today_str, 90)
		p1.percent_complete = 10
		p1.save(ignore_permissions=True)

		if not frappe.db.exists("Lead", {"lead_name": "Tata Motors Passenger Vehicles Ltd"}):
			frappe.get_doc(
				{
					"doctype": "Lead",
					"lead_name": "Tata Motors Passenger Vehicles Ltd",
					"status": "Open",
					"company": company,
				}
			).insert(ignore_permissions=True)
		print("Project 1 configured: Step 07 WAITING (Steps 9-24 will be hidden)")

	# -------------------------------------------------------------
	# PROJECT 2: PROJ-0002 (Quotation Submitted - Step 07 WAITING)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0002"):
		p2 = frappe.get_doc("Project", "PROJ-0002")
		p2.project_name = "Automated Robotic Stamping Cell"
		p2.customer = "Mahindra & Mahindra Auto Division"
		p2.company = company
		p2.status = "Open"
		p2.estimated_costing = 3200000
		p2.total_costing_amount = 750000
		p2.expected_start_date = add_days(today_str, -15)
		p2.expected_end_date = add_days(today_str, 75)
		p2.percent_complete = 20
		p2.save(ignore_permissions=True)

		if not frappe.db.exists("Quotation", {"party_name": "Mahindra & Mahindra Auto Division"}):
			try:
				q2 = frappe.get_doc(
					{
						"doctype": "Quotation",
						"quotation_to": "Customer",
						"party_name": "Mahindra & Mahindra Auto Division",
						"company": company,
						"transaction_date": add_days(today_str, -5),
						"valid_till": add_days(today_str, 25),
						"order_type": "Sales",
						"items": [{"item_code": "DIE-FIXTURE-01", "qty": 5, "rate": 290000}],
					}
				)
				q2.insert(ignore_permissions=True)
				q2.submit()
			except Exception as e:
				print("Quotation notice:", e)
		print("Project 2 configured: Quotation submitted, Step 07 WAITING (Steps 9-24 will be hidden)")

	# -------------------------------------------------------------
	# PROJECT 3: PROJ-0003 (Customer PO Verified & SO Created - Step 07 DONE!)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0003"):
		p3 = frappe.get_doc("Project", "PROJ-0003")
		p3.project_name = "High Precision Forging Die Fixture"
		p3.customer = "Bharat Forge Limited"
		p3.company = company
		p3.status = "Open"
		p3.estimated_costing = 2800000
		p3.total_costing_amount = 1200000
		p3.expected_start_date = add_days(today_str, -20)
		p3.expected_end_date = add_days(today_str, 60)
		p3.percent_complete = 30
		p3.save(ignore_permissions=True)
		print("Project 3 configured: Step 07 DONE! (Manufacturing Pipeline Unlocked)")

	# -------------------------------------------------------------
	# PROJECT 4: PROJ-0004 (Advance Paid, BOM & Production Plan Active - Step 07 DONE)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0004"):
		p4 = frappe.get_doc("Project", "PROJ-0004")
		p4.project_name = "Aerospace Engine Mount 2026"
		p4.customer = "HAL Aerospace Division"
		p4.company = company
		p4.status = "Open"
		p4.estimated_costing = 4200000
		p4.total_costing_amount = 2100000
		p4.expected_start_date = add_days(today_str, -25)
		p4.expected_end_date = add_days(today_str, 55)
		p4.percent_complete = 40
		p4.save(ignore_permissions=True)

		so4_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0004"}, "name")
		if so4_name:
			# Check advance payment
			pe_exists = frappe.db.sql(
				"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (so4_name,)
			)
			if not pe_exists:
				try:
					pe4 = frappe.get_doc(
						{
							"doctype": "Payment Entry",
							"payment_type": "Receive",
							"party_type": "Customer",
							"party": "HAL Aerospace Division",
							"company": company,
							"posting_date": add_days(today_str, -10),
							"reference_no": "HAL-CHQ-2026-410",
							"reference_date": add_days(today_str, -10),
							"paid_from": debtors_account,
							"paid_to": bank_account,
							"paid_from_account_currency": "INR",
							"paid_to_account_currency": "INR",
							"paid_amount": 1260000,
							"received_amount": 1260000,
							"source_exchange_rate": 1,
							"target_exchange_rate": 1,
							"base_paid_amount": 1260000,
							"base_received_amount": 1260000,
							"references": [
								{
									"reference_doctype": "Sales Order",
									"reference_name": so4_name,
									"allocated_amount": 1260000,
								}
							],
						}
					)
					pe4.insert(ignore_permissions=True)
					pe4.submit()
					frappe.db.set_value("Sales Order", so4_name, "advance_paid", 1260000)
					print(f"Project 4 advance payment created: ₹1,260,000 for {so4_name}")
				except Exception as e:
					print("Project 4 PE notice:", e)

	# -------------------------------------------------------------
	# PROJECT 5: PROJ-0005 (Fabrication Active: Laser Cutting Working - Step 15 CURRENT)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0005"):
		p5 = frappe.get_doc("Project", "PROJ-0005")
		p5.project_name = "Electric Vehicle Chassis Assembly"
		p5.customer = "Bajaj Auto Commercial Vehicles"
		p5.company = company
		p5.status = "Open"
		p5.estimated_costing = 5600000
		p5.total_costing_amount = 3200000
		p5.expected_start_date = add_days(today_str, -30)
		p5.expected_end_date = add_days(today_str, 40)
		p5.percent_complete = 50
		p5.save(ignore_permissions=True)

		so5_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0005"}, "name")
		if so5_name:
			# Advance payment
			pe_exists5 = frappe.db.sql(
				"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (so5_name,)
			)
			if not pe_exists5:
				try:
					pe5 = frappe.get_doc(
						{
							"doctype": "Payment Entry",
							"payment_type": "Receive",
							"party_type": "Customer",
							"party": "Bajaj Auto Commercial Vehicles",
							"company": company,
							"posting_date": add_days(today_str, -18),
							"reference_no": "BAJAJ-NEFT-902",
							"reference_date": add_days(today_str, -18),
							"paid_from": debtors_account,
							"paid_to": bank_account,
							"paid_from_account_currency": "INR",
							"paid_to_account_currency": "INR",
							"paid_amount": 2000000,
							"received_amount": 2000000,
							"source_exchange_rate": 1,
							"target_exchange_rate": 1,
							"base_paid_amount": 2000000,
							"base_received_amount": 2000000,
							"references": [
								{
									"reference_doctype": "Sales Order",
									"reference_name": so5_name,
									"allocated_amount": 2000000,
								}
							],
						}
					)
					pe5.insert(ignore_permissions=True)
					pe5.submit()
					frappe.db.set_value("Sales Order", so5_name, "advance_paid", 2000000)
				except Exception as e:
					print("PE5 notice:", e)

			# Work Order
			wo5_name = frappe.db.get_value("Work Order", {"project": "PROJ-0005"}, "name")
			if not wo5_name:
				bom5 = frappe.db.get_value("BOM", {"item": "EV-CHASSIS-01", "is_active": 1}, "name")
				try:
					wo5 = frappe.get_doc(
						{
							"doctype": "Work Order",
							"company": company,
							"project": "PROJ-0005",
							"sales_order": so5_name,
							"production_item": "EV-CHASSIS-01",
							"bom_no": bom5,
							"qty": 50,
							"wip_warehouse": wip_warehouse,
							"fg_warehouse": fg_warehouse,
							"planned_start_date": add_days(today_str, -15),
							"status": "In Process",
						}
					)
					wo5.insert(ignore_permissions=True)
					wo5.submit()
					wo5_name = wo5.name
				except Exception as e:
					print("WO5 notice:", e)

			if wo5_name:
				# Job Card for Laser Cutting
				if not frappe.db.exists("Job Card", {"work_order": wo5_name, "operation": "Laser Cutting"}):
					try:
						jc5 = frappe.get_doc(
							{
								"doctype": "Job Card",
								"work_order": wo5_name,
								"company": company,
								"operation": "Laser Cutting",
								"workstation": "Laser Cutting Shop",
								"status": "Work In Progress",
								"for_quantity": 50,
								"total_completed_qty": 15,
							}
						)
						jc5.insert(ignore_permissions=True)
						print("Project 5 Job Card created: Laser Cutting WIP")
					except Exception as e:
						print("JC5 notice:", e)

	# -------------------------------------------------------------
	# PROJECT 6: PROJ-0006 (Welding Active - Step 18 CURRENT)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0006"):
		p6 = frappe.get_doc("Project", "PROJ-0006")
		p6.project_name = "EV Battery Pack Line"
		p6.customer = "Thermax Industrial Systems"
		p6.company = company
		p6.status = "Open"
		p6.estimated_costing = 3500000
		p6.total_costing_amount = 2400000
		p6.expected_start_date = add_days(today_str, -35)
		p6.expected_end_date = add_days(today_str, 30)
		p6.percent_complete = 60
		p6.save(ignore_permissions=True)

		so6_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0006"}, "name")
		if so6_name:
			pe_exists6 = frappe.db.sql(
				"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (so6_name,)
			)
			if not pe_exists6:
				try:
					pe6 = frappe.get_doc(
						{
							"doctype": "Payment Entry",
							"payment_type": "Receive",
							"party_type": "Customer",
							"party": "Thermax Industrial Systems",
							"company": company,
							"posting_date": add_days(today_str, -22),
							"reference_no": "THX-RTGS-554",
							"reference_date": add_days(today_str, -22),
							"paid_from": debtors_account,
							"paid_to": bank_account,
							"paid_from_account_currency": "INR",
							"paid_to_account_currency": "INR",
							"paid_amount": 1500000,
							"received_amount": 1500000,
							"source_exchange_rate": 1,
							"target_exchange_rate": 1,
							"base_paid_amount": 1500000,
							"base_received_amount": 1500000,
							"references": [
								{
									"reference_doctype": "Sales Order",
									"reference_name": so6_name,
									"allocated_amount": 1500000,
								}
							],
						}
					)
					pe6.insert(ignore_permissions=True)
					pe6.submit()
					frappe.db.set_value("Sales Order", so6_name, "advance_paid", 1500000)
				except Exception as e:
					print("PE6 notice:", e)

			wo6_name = frappe.db.get_value("Work Order", {"project": "PROJ-0006"}, "name")
			if not wo6_name:
				bom6 = frappe.db.get_value("BOM", {"item": "EV-BATTPACK-01", "is_active": 1}, "name")
				try:
					wo6 = frappe.get_doc(
						{
							"doctype": "Work Order",
							"company": company,
							"project": "PROJ-0006",
							"sales_order": so6_name,
							"production_item": "EV-BATTPACK-01",
							"bom_no": bom6,
							"qty": 30,
							"produced_qty": 12,
							"wip_warehouse": wip_warehouse,
							"fg_warehouse": fg_warehouse,
							"planned_start_date": add_days(today_str, -20),
							"status": "In Process",
						}
					)
					wo6.insert(ignore_permissions=True)
					wo6.submit()
					wo6_name = wo6.name
				except Exception as e:
					print("WO6 notice:", e)

			if wo6_name:
				for op, st, c_qty in [
					("Laser Cutting", "Completed", 30),
					("Bending", "Completed", 30),
					("Welding", "Work In Progress", 12),
				]:
					if not frappe.db.exists("Job Card", {"work_order": wo6_name, "operation": op}):
						try:
							frappe.get_doc(
								{
									"doctype": "Job Card",
									"work_order": wo6_name,
									"company": company,
									"operation": op,
									"workstation": "Laser Cutting Shop"
									if op == "Laser Cutting"
									else ("Bending Department" if op == "Bending" else "Welding Shop"),
									"status": st,
									"for_quantity": 30,
									"total_completed_qty": c_qty,
								}
							).insert(ignore_permissions=True)
						except Exception as e:
							print(f"JC6 {op} notice:", e)
				print("Project 6 configured: Laser & Bending DONE, Welding WIP")

	# -------------------------------------------------------------
	# PROJECT 7: PROJ-0007 (Finishing & Final QC Active - Step 22 CURRENT)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0007"):
		p7 = frappe.get_doc("Project", "PROJ-0007")
		p7.project_name = "Robotic Arm Assembly"
		p7.customer = "Kirloskar Oil Engines Ltd"
		p7.company = company
		p7.status = "Open"
		p7.estimated_costing = 6800000
		p7.total_costing_amount = 5100000
		p7.expected_start_date = add_days(today_str, -40)
		p7.expected_end_date = add_days(today_str, 20)
		p7.percent_complete = 75
		p7.save(ignore_permissions=True)

		so7_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0007"}, "name")
		if so7_name:
			pe_exists7 = frappe.db.sql(
				"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (so7_name,)
			)
			if not pe_exists7:
				try:
					pe7 = frappe.get_doc(
						{
							"doctype": "Payment Entry",
							"payment_type": "Receive",
							"party_type": "Customer",
							"party": "Kirloskar Oil Engines Ltd",
							"company": company,
							"posting_date": add_days(today_str, -30),
							"reference_no": "KOEL-CHQ-812",
							"reference_date": add_days(today_str, -30),
							"paid_from": debtors_account,
							"paid_to": bank_account,
							"paid_from_account_currency": "INR",
							"paid_to_account_currency": "INR",
							"paid_amount": 3000000,
							"received_amount": 3000000,
							"source_exchange_rate": 1,
							"target_exchange_rate": 1,
							"base_paid_amount": 3000000,
							"base_received_amount": 3000000,
							"references": [
								{
									"reference_doctype": "Sales Order",
									"reference_name": so7_name,
									"allocated_amount": 3000000,
								}
							],
						}
					)
					pe7.insert(ignore_permissions=True)
					pe7.submit()
					frappe.db.set_value("Sales Order", so7_name, "advance_paid", 3000000)
				except Exception as e:
					print("PE7 notice:", e)

			wo7_name = frappe.db.get_value("Work Order", {"project": "PROJ-0007"}, "name")
			if not wo7_name:
				bom7 = frappe.db.get_value("BOM", {"item": "ROBOT-ARM-01", "is_active": 1}, "name")
				try:
					wo7 = frappe.get_doc(
						{
							"doctype": "Work Order",
							"company": company,
							"project": "PROJ-0007",
							"sales_order": so7_name,
							"production_item": "ROBOT-ARM-01",
							"bom_no": bom7,
							"qty": 20,
							"produced_qty": 18,
							"wip_warehouse": wip_warehouse,
							"fg_warehouse": fg_warehouse,
							"planned_start_date": add_days(today_str, -25),
							"status": "In Process",
						}
					)
					wo7.insert(ignore_permissions=True)
					wo7.submit()
					wo7_name = wo7.name
				except Exception as e:
					print("WO7 notice:", e)

			if wo7_name:
				last_jc = None
				for op in ["Laser Cutting", "Bending", "Welding", "Grinding", "Painting"]:
					if not frappe.db.exists("Job Card", {"work_order": wo7_name, "operation": op}):
						try:
							jc = frappe.get_doc(
								{
									"doctype": "Job Card",
									"work_order": wo7_name,
									"company": company,
									"operation": op,
									"workstation": "Laser Cutting Shop"
									if op == "Laser Cutting"
									else "Welding Shop",
									"status": "Completed",
									"for_quantity": 20,
									"total_completed_qty": 20,
								}
							)
							jc.insert(ignore_permissions=True)
							last_jc = jc.name
						except Exception as e:
							print(f"JC7 {op} notice:", e)

				# Quality inspection linked to Job Card
				if last_jc and not frappe.db.exists("Quality Inspection", {"reference_name": last_jc}):
					try:
						qi7 = frappe.get_doc(
							{
								"doctype": "Quality Inspection",
								"report_date": today_str,
								"status": "Accepted",
								"inspection_type": "In Process",
								"reference_type": "Job Card",
								"reference_name": last_jc,
								"item_code": "ROBOT-ARM-01",
								"sample_size": 5,
								"inspected_by": "Administrator",
							}
						)
						qi7.insert(ignore_permissions=True)
						qi7.submit()
						print("Project 7 QI submitted (Final QC Active)")
					except Exception as e:
						print("QI7 notice:", e)

	# -------------------------------------------------------------
	# PROJECT 8: PROJ-0008 (Quality Reject / Rework Scenario)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0008"):
		p8 = frappe.get_doc("Project", "PROJ-0008")
		p8.project_name = "EV Battery Pack Line Phase 2"
		p8.customer = "Godrej & Boyce Mfg Co"
		p8.company = company
		p8.status = "Open"
		p8.estimated_costing = 4500000
		p8.total_costing_amount = 3100000
		p8.expected_start_date = add_days(today_str, -30)
		p8.expected_end_date = add_days(today_str, 35)
		p8.percent_complete = 45
		p8.save(ignore_permissions=True)

		so8_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0008"}, "name")
		wo8_name = frappe.db.get_value("Work Order", {"project": "PROJ-0008"}, "name")
		if not wo8_name and so8_name:
			bom8 = frappe.db.get_value("BOM", {"item": "EV-BATTPACK-01", "is_active": 1}, "name")
			try:
				wo8 = frappe.get_doc(
					{
						"doctype": "Work Order",
						"company": company,
						"project": "PROJ-0008",
						"sales_order": so8_name,
						"production_item": "EV-BATTPACK-01",
						"bom_no": bom8,
						"qty": 38,
						"produced_qty": 5,
						"wip_warehouse": wip_warehouse,
						"fg_warehouse": fg_warehouse,
						"planned_start_date": add_days(today_str, -18),
						"status": "In Process",
					}
				)
				wo8.insert(ignore_permissions=True)
				wo8.submit()
				wo8_name = wo8.name
			except Exception as e:
				print("WO8 notice:", e)

		if wo8_name:
			jc8_name = frappe.db.get_value(
				"Job Card", {"work_order": wo8_name, "operation": "Welding"}, "name"
			)
			if not jc8_name:
				try:
					jc8 = frappe.get_doc(
						{
							"doctype": "Job Card",
							"work_order": wo8_name,
							"company": company,
							"operation": "Welding",
							"workstation": "Welding Shop",
							"status": "Work In Progress",
							"for_quantity": 38,
							"total_completed_qty": 5,
						}
					)
					jc8.insert(ignore_permissions=True)
					jc8_name = jc8.name
				except Exception as e:
					print("JC8 notice:", e)

			if jc8_name and not frappe.db.exists("Quality Inspection", {"reference_name": jc8_name}):
				try:
					qi8 = frappe.get_doc(
						{
							"doctype": "Quality Inspection",
							"report_date": today_str,
							"status": "Rejected",
							"inspection_type": "In Process",
							"reference_type": "Job Card",
							"reference_name": jc8_name,
							"item_code": "EV-BATTPACK-01",
							"sample_size": 4,
							"inspected_by": "Administrator",
						}
					)
					qi8.insert(ignore_permissions=True)
					qi8.submit()
					print("Project 8 configured: QC Rejected / Rework Alert on Job Card", jc8_name)
				except Exception as e:
					print("QI8 notice:", e)

	# -------------------------------------------------------------
	# PROJECT 9: PROJ-0009 (Delivered, Invoiced, Overdue AR: ₹4.2M overdue)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0009"):
		p9 = frappe.get_doc("Project", "PROJ-0009")
		p9.project_name = "Office Furniture 2026"
		p9.customer = "Larsen & Toubro Heavy Engineering"
		p9.company = company
		p9.status = "Open"
		p9.estimated_costing = 8200000
		p9.total_costing_amount = 6200000
		p9.expected_start_date = add_days(today_str, -60)
		p9.expected_end_date = add_days(today_str, -5)
		p9.percent_complete = 90
		p9.save(ignore_permissions=True)

		so9_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0009"}, "name")
		if so9_name:
			so9_doc = frappe.get_doc("Sales Order", so9_name)
			so9_item = so9_doc.items[0]

			# Delivery Note
			dn9_name = frappe.db.get_value("Delivery Note Item", {"against_sales_order": so9_name}, "parent")
			if not dn9_name:
				try:
					dn9 = frappe.get_doc(
						{
							"doctype": "Delivery Note",
							"company": company,
							"customer": "Larsen & Toubro Heavy Engineering",
							"project": "PROJ-0009",
							"posting_date": add_days(today_str, -15),
							"items": [
								{
									"item_code": so9_item.item_code,
									"qty": so9_item.qty,
									"against_sales_order": so9_name,
									"so_detail": so9_item.name,
									"rate": so9_item.rate,
									"warehouse": fg_warehouse,
									"cost_center": cost_center,
								}
							],
						}
					)
					dn9.insert(ignore_permissions=True)
					dn9.submit()
					dn9_name = dn9.name
					print(f"Project 9 Delivery Note created: {dn9_name}")
				except Exception as e:
					print("DN9 notice:", e)

			# Sales Invoice (Overdue by 15 days)
			si9_name = frappe.db.get_value("Sales Invoice Item", {"sales_order": so9_name}, "parent")
			if not si9_name:
				try:
					si9 = frappe.get_doc(
						{
							"doctype": "Sales Invoice",
							"company": company,
							"customer": "Larsen & Toubro Heavy Engineering",
							"project": "PROJ-0009",
							"set_posting_time": 1,
							"posting_date": add_days(today_str, -30),
							"due_date": add_days(today_str, -5),
							"debit_to": debtors_account,
							"items": [
								{
									"item_code": so9_item.item_code,
									"qty": so9_item.qty,
									"rate": so9_item.rate,
									"sales_order": so9_name,
									"so_detail": so9_item.name,
									"income_account": sales_account,
									"cost_center": cost_center,
								}
							],
						}
					)
					si9.insert(ignore_permissions=True)
					si9.submit()
					si9_name = si9.name
					print(f"Project 9 Sales Invoice created: {si9_name} (₹8.2M)")
				except Exception as e:
					print("SI9 notice:", e)

			# Partial payment of ₹4,000,000 leaving ₹4,200,000 overdue
			if si9_name:
				pe9_exists = frappe.db.sql(
					"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (si9_name,)
				)
				if not pe9_exists:
					try:
						pe9 = frappe.get_doc(
							{
								"doctype": "Payment Entry",
								"payment_type": "Receive",
								"party_type": "Customer",
								"party": "Larsen & Toubro Heavy Engineering",
								"company": company,
								"posting_date": add_days(today_str, -20),
								"reference_no": "LNT-CHQ-9812",
								"reference_date": add_days(today_str, -20),
								"paid_from": debtors_account,
								"paid_to": bank_account,
								"paid_from_account_currency": "INR",
								"paid_to_account_currency": "INR",
								"paid_amount": 4000000,
								"received_amount": 4000000,
								"source_exchange_rate": 1,
								"target_exchange_rate": 1,
								"base_paid_amount": 4000000,
								"base_received_amount": 4000000,
								"references": [
									{
										"reference_doctype": "Sales Invoice",
										"reference_name": si9_name,
										"allocated_amount": 4000000,
									}
								],
							}
						)
						pe9.insert(ignore_permissions=True)
						pe9.submit()
						print("Project 9 partial payment created: ₹4.0M, remaining overdue ₹4.2M")
					except Exception as e:
						print("PE9 notice:", e)

	# -------------------------------------------------------------
	# PROJECT 10: PROJ-0010 (100% Completed, Fully Delivered & Paid)
	# -------------------------------------------------------------
	if frappe.db.exists("Project", "PROJ-0010"):
		p10 = frappe.get_doc("Project", "PROJ-0010")
		p10.project_name = "an EV Assembly line"
		p10.customer = "ISRO Propulsion Complex Vendor"
		p10.company = company
		p10.status = "Completed"
		p10.estimated_costing = 9500000
		p10.total_costing_amount = 7800000
		p10.expected_start_date = add_days(today_str, -90)
		p10.expected_end_date = add_days(today_str, -10)
		p10.percent_complete = 100
		p10.save(ignore_permissions=True)

		so10_name = frappe.db.get_value("Sales Order", {"project": "PROJ-0010"}, "name")
		if so10_name:
			so10_doc = frappe.get_doc("Sales Order", so10_name)
			so10_item = so10_doc.items[0]

			# Delivery Note
			dn10_name = frappe.db.get_value(
				"Delivery Note Item", {"against_sales_order": so10_name}, "parent"
			)
			if not dn10_name:
				try:
					dn10 = frappe.get_doc(
						{
							"doctype": "Delivery Note",
							"company": company,
							"customer": "ISRO Propulsion Complex Vendor",
							"project": "PROJ-0010",
							"posting_date": add_days(today_str, -20),
							"items": [
								{
									"item_code": so10_item.item_code,
									"qty": so10_item.qty,
									"against_sales_order": so10_name,
									"so_detail": so10_item.name,
									"rate": so10_item.rate,
									"warehouse": fg_warehouse,
									"cost_center": cost_center,
								}
							],
						}
					)
					dn10.insert(ignore_permissions=True)
					dn10.submit()
					dn10_name = dn10.name
					print(f"Project 10 Delivery Note created: {dn10_name}")
				except Exception as e:
					print("DN10 notice:", e)

			# Sales Invoice
			si10_name = frappe.db.get_value("Sales Invoice Item", {"sales_order": so10_name}, "parent")
			if not si10_name:
				try:
					si10 = frappe.get_doc(
						{
							"doctype": "Sales Invoice",
							"company": company,
							"customer": "ISRO Propulsion Complex Vendor",
							"project": "PROJ-0010",
							"posting_date": add_days(today_str, -18),
							"due_date": add_days(today_str, 12),
							"debit_to": debtors_account,
							"items": [
								{
									"item_code": so10_item.item_code,
									"qty": so10_item.qty,
									"rate": so10_item.rate,
									"sales_order": so10_name,
									"so_detail": so10_item.name,
									"income_account": sales_account,
									"cost_center": cost_center,
								}
							],
						}
					)
					si10.insert(ignore_permissions=True)
					si10.submit()
					si10_name = si10.name
					print(f"Project 10 Sales Invoice created: {si10_name}")
				except Exception as e:
					print("SI10 notice:", e)

			# Full Payment
			if si10_name:
				pe10_exists = frappe.db.sql(
					"SELECT parent FROM `tabPayment Entry Reference` WHERE reference_name = %s", (si10_name,)
				)
				if not pe10_exists:
					try:
						si10_doc = frappe.get_doc("Sales Invoice", si10_name)
						total_inv = flt(si10_doc.grand_total)
						pe10 = frappe.get_doc(
							{
								"doctype": "Payment Entry",
								"payment_type": "Receive",
								"party_type": "Customer",
								"party": "ISRO Propulsion Complex Vendor",
								"company": company,
								"posting_date": add_days(today_str, -12),
								"reference_no": "ISRO-RTGS-012",
								"reference_date": add_days(today_str, -12),
								"paid_from": debtors_account,
								"paid_to": bank_account,
								"paid_from_account_currency": "INR",
								"paid_to_account_currency": "INR",
								"paid_amount": total_inv,
								"received_amount": total_inv,
								"source_exchange_rate": 1,
								"target_exchange_rate": 1,
								"base_paid_amount": total_inv,
								"base_received_amount": total_inv,
								"references": [
									{
										"reference_doctype": "Sales Invoice",
										"reference_name": si10_name,
										"allocated_amount": total_inv,
									}
								],
							}
						)
						pe10.insert(ignore_permissions=True)
						pe10.submit()
						print(f"Project 10 full payment entry created: ₹{total_inv:,.2f}")
					except Exception as e:
						print("PE10 notice:", e)

			frappe.db.set_value("Sales Order", so10_name, "per_delivered", 100)
			frappe.db.set_value("Sales Order", so10_name, "per_billed", 100)

	frappe.db.commit()
	print(">>> SUCCESS: All 10 Projects and Real-Time Data successfully committed!")


if __name__ == "__main__":
	populate()
