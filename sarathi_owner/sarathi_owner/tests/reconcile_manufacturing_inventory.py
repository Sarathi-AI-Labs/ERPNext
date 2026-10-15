"""DASH-012 Live reconciliation between dashboard manufacturing/inventory metrics and ERPNext source records."""
from datetime import date
import json
import frappe
from frappe.utils import flt, getdate

from sarathi_owner.api.manufacturing_inventory import get_manufacturing_inventory_summary


def reconcile():
	frappe.set_user("Administrator")
	companies = frappe.get_all("Company", pluck="name")
	results = []

	for company in companies:
		summary = get_manufacturing_inventory_summary({"company": company, "shortage_only": False})
		mfg = summary["manufacturing"]
		inv = summary["inventory"]
		risk = summary["stock_risk"]
		shortages = summary["shortages"]

		# 1. Reconcile Work Orders with native tabWork Order
		wo_sql = frappe.db.sql(
			"""
			SELECT 
				COUNT(*) as total,
				SUM(CASE WHEN docstatus = 1 AND status IN ('Not Started', 'In Process', 'Submitted') THEN 1 ELSE 0 END) as active,
				SUM(CASE WHEN docstatus = 1 AND status = 'Completed' THEN 1 ELSE 0 END) as completed,
				SUM(CASE WHEN docstatus = 0 OR status = 'Draft' THEN 1 ELSE 0 END) as draft,
				SUM(CASE WHEN docstatus = 2 OR status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
				SUM(CASE WHEN status = 'Stopped' THEN 1 ELSE 0 END) as stopped
			FROM `tabWork Order`
			WHERE company = %s
			""",
			(company,),
			as_dict=True,
		)[0]

		mfg_diffs = {
			"total": mfg["counts"]["total"] - (wo_sql.total or 0),
			"active": mfg["counts"]["active"] - (wo_sql.active or 0),
			"completed": mfg["counts"]["completed"] - (wo_sql.completed or 0),
			"draft": mfg["counts"]["draft"] - (wo_sql.draft or 0),
			"cancelled": mfg["counts"]["cancelled"] - (wo_sql.cancelled or 0),
			"stopped": mfg["counts"]["stopped"] - (wo_sql.stopped or 0),
		}

		# 2. Reconcile Inventory Valuation with native leaf warehouse Bin stock_value
		bin_sql = frappe.db.sql(
			"""
			SELECT 
				IFNULL(SUM(b.stock_value), 0.0) as total_val,
				IFNULL(SUM(b.actual_qty), 0.0) as actual_qty,
				IFNULL(SUM(b.reserved_qty), 0.0) as reserved_qty,
				IFNULL(SUM(b.projected_qty), 0.0) as projected_qty,
				COUNT(DISTINCT b.item_code) as item_count
			FROM `tabBin` b
			INNER JOIN `tabWarehouse` w ON b.warehouse = w.name
			WHERE w.company = %s AND w.is_group = 0
			""",
			(company,),
			as_dict=True,
		)[0]

		inv_diffs = {
			"valuation_diff": round(inv["valuation"] - flt(bin_sql.total_val), 2),
			"actual_qty_diff": round(inv["total_actual_qty"] - flt(bin_sql.actual_qty), 2),
			"reserved_qty_diff": round(inv["total_reserved_qty"] - flt(bin_sql.reserved_qty), 2),
			"projected_qty_diff": round(inv["total_projected_qty"] - flt(bin_sql.projected_qty), 2),
			"item_count_diff": inv["total_items"] - (bin_sql.item_count or 0),
		}

		# 3. Compare with standard ERPNext Stock Balance report
		report_val = 0.0
		report_qty = 0.0
		try:
			from erpnext.stock.report.stock_balance.stock_balance import execute as execute_stock_balance
			_, rep_rows = execute_stock_balance(frappe._dict({"company": company, "to_date": str(getdate())}))
			report_val = sum(flt(r.get("bal_val", 0)) for r in rep_rows if isinstance(r, dict))
			report_qty = sum(flt(r.get("bal_qty", 0)) for r in rep_rows if isinstance(r, dict))
		except Exception as e:
			pass

		report_diffs = {
			"report_val_diff": round(inv["valuation"] - report_val, 2),
			"report_qty_diff": round(inv["total_actual_qty"] - report_qty, 2),
		}

		results.append({
			"company": company,
			"work_orders": {
				"dashboard_counts": mfg["counts"],
				"db_counts": dict(wo_sql),
				"diffs": mfg_diffs,
			},
			"inventory": {
				"dashboard_valuation": inv["valuation"],
				"db_bin_valuation": round(flt(bin_sql.total_val), 2),
				"diffs": inv_diffs,
				"report_reconciliation": report_diffs,
			},
			"stock_risk_counts": risk["counts"],
			"shortage_counts": shortages["counts"],
			"reconciled": (
				all(v == 0 for v in mfg_diffs.values()) and
				all(v == 0.0 for v in inv_diffs.values()) and
				report_diffs["report_val_diff"] == 0.0
			),
		})

	return results


if __name__ == "__main__":
	frappe.init(site="frontend")
	frappe.connect()
	report = reconcile()
	print(json.dumps(report, indent=2))
