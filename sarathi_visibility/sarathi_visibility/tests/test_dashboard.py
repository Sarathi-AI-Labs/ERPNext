"""Transactional integration checks. Run with bench execute; all fixtures roll back."""

import unittest

import frappe

from sarathi_visibility.api.dashboard import (
    export_report,
    get_record,
    get_report,
    get_summary,
)
from sarathi_visibility.api.dashboard_data import load, parse_filters
from sarathi_visibility.setup.dashboard import validate_project, validate_transaction


class DashboardTests(unittest.TestCase):
    def test_project_health_is_scoped_and_uses_recorded_operations(self):
        summary = get_summary({"project": self.projects[0]})
        self.assertEqual(
            [row["project"] for row in summary["project_health"]], [self.projects[0]]
        )
        health = summary["project_health"][0]
        production = summary["production_summary"][0]
        self.assertEqual(health["live_status"], production["live_status"])
        self.assertEqual(health["operations_total"], production["operations"])
        self.assertEqual(
            health["operations_finished"], production["finished_operations"]
        )
        self.assertEqual(len(health["current_operations"]), production["running_count"])
        if health["next_operation"]:
            self.assertIn(
                health["next_operation"]["work_order"],
                {row["work_order"] for row in summary["operation_balance"]},
            )
        self.assertTrue(
            all(row["project"] == self.projects[0] for row in summary["project_health"])
        )

    def test_pipeline_line_attribution_and_completed_materials(self):
        from sarathi_visibility.api.pipeline import resolve_project

        header = frappe._dict(project="A")
        self.assertEqual(resolve_project(frappe._dict(project="B"), header, {})[0], "B")
        self.assertEqual(
            resolve_project(
                frappe._dict(material_request_item="MR-A"),
                frappe._dict(),
                {"MR-A": "A"},
            )[0],
            "A",
        )
        self.assertIsNone(
            resolve_project(
                frappe._dict(material_request_item="MR-A", purchase_order_item="PO-B"),
                frappe._dict(),
                {"MR-A": "A", "PO-B": "B"},
            )[0]
        )
        baseline = load({"company": self.company})
        for key in (
            "requests",
            "purchases",
            "receipts",
            "purchase_invoices",
            "deliveries",
            "sales_invoices",
            "material_history",
            "stock_details",
            "stock_ledger",
            "quality",
            "job_logs",
            "job_suboperations",
            "part_production",
        ):
            scoped = load({"project": self.projects[0]})
            self.assertTrue(
                all(r.get("project") == self.projects[0] for r in scoped[key]), key
            )
        dated = load({"company": self.company, "from_date": "2099-01-01"})
        for key in (
            "material_history",
            "stock_details",
            "stock_ledger",
            "requests",
            "purchases",
            "receipts",
        ):
            self.assertEqual(baseline[key], dated[key], key)
        completed = {
            w.name
            for w in baseline["work_orders"]
            if w.status == "Completed" and w.docstatus == 1
        }
        if completed:
            self.assertTrue(
                any(r.work_order in completed for r in baseline["material_history"])
            )

    def test_mixed_project_purchase_items(self):
        existing = frappe.get_all("Purchase Order", pluck="name", limit=1)
        if not existing:
            self.skipTest("Supplier / Item fixture required")
        original = frappe.get_doc("Purchase Order", existing[0])
        item = original.items[0].item_code
        warehouse = frappe.get_all(
            "Warehouse",
            filters={"company": self.company, "is_group": 0},
            pluck="name",
            limit=1,
        )[0]
        doc = frappe.get_doc(
            {
                "doctype": "Purchase Order",
                "supplier": original.supplier,
                "company": self.company,
                "project": self.projects[0],
                "schedule_date": frappe.utils.today(),
                "items": [
                    {
                        "item_code": item,
                        "qty": 3,
                        "warehouse": warehouse,
                        "project": self.projects[0],
                    },
                    {
                        "item_code": item,
                        "qty": 7,
                        "warehouse": warehouse,
                        "project": self.projects[1],
                    },
                ],
            }
        ).insert()
        a = get_report({"project": self.projects[0]}, "purchases")["rows"]
        b = get_report({"project": self.projects[1]}, "purchases")["rows"]
        self.assertEqual([r.qty for r in a if r.name == doc.name], [3])
        self.assertEqual([r.qty for r in b if r.name == doc.name], [7])
        detail = get_record({"project": self.projects[0]}, "Purchase Order", doc.name)
        self.assertEqual(detail["related"][0]["total"], 1)
        self.assertEqual(detail["related"][0]["rows"][0].qty, 3)

    def test_live_activity_reads_permission_scoped_time_logs(self):
        names = frappe.get_all(
            "Job Card", filters={"docstatus": ["<", 2]}, fields=["name", "work_order"]
        )
        candidate = next(
            (
                j
                for j in names
                if frappe.db.get_value("Work Order", j.work_order, "docstatus") == 1
                and frappe.db.exists("Job Card Time Log", {"parent": j.name})
            ),
            None,
        )
        if not candidate:
            self.skipTest("Existing submitted production with a time log required")
        project = frappe.db.get_value("Work Order", candidate.work_order, "project")
        if not project:
            self.skipTest("Project-linked production required")
        log = frappe.db.get_value(
            "Job Card Time Log", {"parent": candidate.name}, "name"
        )
        frappe.db.set_value("Project", project, "status", "Open")
        frappe.db.set_value("Work Order", candidate.work_order, "status", "In Process")
        frappe.db.set_value("Job Card", candidate.name, "status", "Work In Progress")
        frappe.db.set_value(
            "Job Card Time Log",
            log,
            {"from_time": "2026-09-16 10:00:00", "to_time": None},
        )
        f = {"project": project, "from_date": "2099-01-01"}
        running = get_report(f, "live_activity")["rows"]
        self.assertIn(candidate.name, {r["job_card"] for r in running})
        self.assertTrue(all(r["project"] == project for r in running))
        self.assertEqual(get_report(f, "production_summary", "in_progress")["total"], 1)
        self.assertEqual(
            get_report({"project": self.projects[0]}, "live_activity")["total"], 0
        )
        frappe.db.set_value("Project", project, "status", "Completed")
        self.assertEqual(get_report(f, "live_activity")["total"], 0)
        self.assertEqual(get_report(f, "production_summary", "in_progress")["total"], 0)
        self.assertTrue(
            any(
                "Open time log conflicts" in r["issue"]
                for r in get_report(f, "issues")["rows"]
            )
        )

    def test_live_running_and_completion_exclusion(self):
        from sarathi_visibility.api.production import live_activity

        project = frappe._dict(name="P", status="Open", customer="C")
        wo = frappe._dict(name="WO", project="P", docstatus=1, status="In Process")
        jobs = [
            frappe._dict(
                name=name,
                work_order="WO",
                docstatus=0,
                status="Work In Progress",
                operation=operation,
                workstation="Station",
                modified="2026-09-16 12:00:00",
                for_quantity=10,
                total_completed_qty=0,
            )
            for name, operation in [("J1", "Cutting"), ("J2", "Welding")]
        ]
        summary = dict(project="P", production_status="Not started")
        self.assertEqual(live_activity([project], [wo], jobs, [], [], [summary]), [])
        self.assertEqual(summary["live_status"], "Not started")
        logs = [
            frappe._dict(parent=j.name, from_time="2026-09-16 11:00:00", to_time=None)
            for j in jobs
        ]
        self.assertEqual(
            len(live_activity([project], [wo], jobs, logs, [], [summary])), 2
        )
        self.assertEqual(summary["live_status"], "In progress")
        for log in logs:
            log.to_time = "2026-09-16 11:30:00"
        self.assertEqual(live_activity([project], [wo], jobs, logs, [], [summary]), [])
        self.assertEqual(summary["live_status"], "In progress")
        project.status = "Completed"
        for log in logs:
            log.to_time = None
        self.assertEqual(live_activity([project], [wo], jobs, logs, [], [summary]), [])
        self.assertEqual(summary["live_status"], "Completed")
        project.status = "Open"
        wo.status = "Stopped"
        self.assertEqual(live_activity([project], [wo], jobs, logs, [], [summary]), [])
        self.assertEqual(summary["live_status"], "On hold / Stopped")
        wo.status = "Completed"
        summary["production_status"] = "Finished"
        self.assertEqual(live_activity([project], [wo], jobs, logs, [], [summary]), [])
        self.assertEqual(
            summary["live_status"], "Production finished · Closure pending"
        )

    def test_operation_balances_and_shared_stock(self):
        from sarathi_visibility.api.production import analyze

        project = frappe._dict(
            name="P", project_name="Chair", customer="C", status="Open"
        )
        wo = frappe._dict(
            name="WO",
            project="P",
            docstatus=1,
            qty=100,
            produced_qty=0,
            production_item="CHAIR",
            stock_uom="Nos",
            status="In Process",
            track_semi_finished_goods=1,
        )
        cancelled = frappe._dict(dict(wo, name="CANCELLED", docstatus=2))
        operations = [
            frappe._dict(
                name="OP1",
                parent="WO",
                idx=1,
                operation="Cutting",
                completed_qty=70,
                process_loss_qty=5,
                finished_good="CUT",
                fg_warehouse="W",
            ),
            frappe._dict(
                name="OP2",
                parent="WO",
                idx=2,
                operation="Welding",
                completed_qty=40,
                process_loss_qty=0,
                finished_good="CUT",
                fg_warehouse="W",
            ),
            frappe._dict(name="OP3", parent="CANCELLED", idx=1, completed_qty=100),
        ]
        jobs = [
            frappe._dict(
                work_order="WO",
                operation_id="OP1",
                docstatus=1,
                is_corrective_job_card=0,
            ),
            frappe._dict(
                work_order="WO",
                operation_id="OP1",
                docstatus=0,
                is_corrective_job_card=1,
            ),
            frappe._dict(work_order="WO", operation_id="OP1", docstatus=2),
        ]
        balances, summary, stock = analyze(
            [project],
            [wo, cancelled],
            operations,
            jobs,
            {"W"},
            [frappe._dict(item_code="CUT", warehouse="W", actual_qty=12)],
            {"CUT": "Nos"},
        )
        self.assertEqual(len(balances), 2)
        self.assertEqual(balances[0]["planned"], 100)
        self.assertEqual(balances[0]["remaining"], 25)
        self.assertEqual(balances[1]["remaining"], 60)
        self.assertEqual(balances[0]["corrective_jobs"], 1)
        self.assertEqual(summary[0]["production_status"], "In progress")
        self.assertEqual(len(stock), 1)
        self.assertEqual(stock[0]["available"], 12)
        self.assertIsNone(
            analyze([project], [wo], operations, jobs, {"W"}, None, {})[2][0][
                "available"
            ]
        )

    def test_project_status_cards_and_lifetime_operations(self):
        f = {"company": self.company, "customer": self.customers[0]}
        summary = get_summary(f)
        cards = {c["label"]: c["value"] for c in summary["kpis"]}
        self.assertEqual(cards["Total projects"], 1)
        self.assertEqual(cards["Not started"], 1)
        self.assertEqual(cards["Completed projects"], 0)
        frappe.db.set_value("Project", self.projects[0], "status", "Completed")
        self.assertEqual(get_report(f, "projects", "completed")["total"], 1)
        self.assertEqual(get_report(f, "projects", "ongoing")["total"], 0)
        baseline = load({"company": self.company})
        dated = load(
            {
                "company": self.company,
                "from_date": "2099-01-01",
                "to_date": "2099-01-02",
            }
        )
        self.assertEqual(baseline["operation_balance"], dated["operation_balance"])
        self.assertEqual(baseline["production_summary"], dated["production_summary"])
        self.assertEqual(baseline["wip_stock"], dated["wip_stock"])

    def test_project_date_filter_by_creation_date(self):
        t = str(frappe.utils.today())
        f_matching = {
            "company": self.company,
            "from_date": t,
            "to_date": t,
        }
        summary_matching = get_summary(f_matching)
        matching_names = [p["name"] for p in summary_matching["projects"]]
        self.assertIn(self.projects[0], matching_names)
        cards_matching = {c["label"]: c["value"] for c in summary_matching["kpis"]}
        self.assertGreaterEqual(cards_matching["Total projects"], 1)

        f_outside = {
            "company": self.company,
            "from_date": "2020-01-01",
            "to_date": "2020-01-31",
        }
        summary_outside = get_summary(f_outside)
        outside_names = [p["name"] for p in summary_outside["projects"]]
        self.assertNotIn(self.projects[0], outside_names)
        cards_outside = {c["label"]: c["value"] for c in summary_outside["kpis"]}
        self.assertEqual(cards_outside["Total projects"], 0)
        self.assertEqual(cards_outside["Not started"], 0)

    def setUp(self):
        frappe.set_user("Administrator")
        frappe.db.savepoint("sarathi_dashboard_test")
        self.company = frappe.get_all("Company", pluck="name", limit=1)[0]
        self.token = frappe.generate_hash(length=8)
        self.customers = []
        self.projects = []
        for label in ("A", "B", "Empty"):
            customer = frappe.get_doc(
                {
                    "doctype": "Customer",
                    "customer_name": f"Sarathi test {self.token} {label}",
                    "customer_type": "Company",
                    "customer_group": frappe.get_all(
                        "Customer Group", filters={"is_group": 0}, pluck="name", limit=1
                    )[0],
                    "territory": frappe.get_all(
                        "Territory", filters={"is_group": 0}, pluck="name", limit=1
                    )[0],
                }
            ).insert()
            self.customers.append(customer.name)
            frappe.get_doc(
                {
                    "doctype": "Sarathi Customer Organization",
                    "company": self.company,
                    "customer": customer.name,
                }
            ).insert()
            if label != "Empty":
                project = frappe.get_doc(
                    {
                        "doctype": "Project",
                        "project_name": f"Sarathi test {self.token} {label}",
                        "company": self.company,
                        "customer": customer.name,
                        "custom_sarathi_manufacturing": 1,
                    }
                ).insert()
                self.projects.append(project.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback(save_point="sarathi_dashboard_test")
        frappe.clear_cache()

    def test_customer_and_project_isolation(self):
        data = load({"company": self.company, "customer": self.customers[0]})
        self.assertEqual([p.name for p in data["projects"]], [self.projects[0]])
        with self.assertRaises(frappe.PermissionError):
            load(
                {
                    "company": self.company,
                    "customer": self.customers[0],
                    "project": self.projects[1],
                }
            )
        empty = load({"company": self.company, "customer": self.customers[2]})
        for key in ("projects", "work_orders", "job_cards", "boms", "stock", "tasks"):
            self.assertEqual(empty[key], [], key)
        self.assertIn(
            self.customers[2],
            {c["name"] for c in load({"company": self.company})["customers"]},
        )

    def test_same_item_does_not_leak_boms(self):
        original = frappe.get_all(
            "BOM", filters={"company": self.company}, pluck="name", limit=1
        )
        if not original:
            self.skipTest("No existing BOM for this company's fixture")
        names = []
        for project in self.projects:
            bom = frappe.copy_doc(frappe.get_doc("BOM", original[0]))
            bom.docstatus = 0
            bom.is_default = 0
            bom.custom_sarathi_project = project
            bom.insert()
            bom.submit()
            names.append(bom.name)
            self.assertEqual(
                frappe.db.get_value("Project", project, "custom_sarathi_bom"), bom.name
            )
        result = load({"company": self.company, "customer": self.customers[0]})
        self.assertEqual({b.name for b in result["boms"]}, {names[0]})
        self.assertTrue(all(c.parent == names[0] for c in result["components"]))
        project = frappe.get_doc("Project", self.projects[0])
        project.custom_sarathi_bom = names[1]
        with self.assertRaises(frappe.ValidationError):
            validate_project(project)
        with self.assertRaises(frappe.PermissionError):
            get_record(
                {"company": self.company, "customer": self.customers[0]},
                "BOM",
                names[1],
            )

    def test_reports_and_summary_agree(self):
        f = {"company": self.company, "customer": self.customers[0]}
        summary = get_summary(f)
        for kpi in summary["kpis"]:
            report = get_report(f, kpi["report"], kpi.get("subset", ""), page_length=1)
            self.assertEqual(kpi["value"], report["total"])
        report = get_report(f, "projects", search="does-not-exist")
        self.assertEqual(report["total"], 0)
        with self.assertRaises(frappe.ValidationError):
            parse_filters({"from_date": "2026-12-31", "to_date": "2026-01-01"})

    def test_validation_and_guest_permissions(self):
        project = frappe.get_doc("Project", self.projects[0])
        project.customer = None
        with self.assertRaises(frappe.ValidationError):
            validate_project(project)
        order = frappe.get_doc(
            {
                "doctype": "Sales Order",
                "project": self.projects[0],
                "company": self.company,
                "customer": self.customers[1],
            }
        )
        with self.assertRaises(frappe.ValidationError):
            validate_transaction(order)
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_summary({"project": self.projects[0]})

    def test_pagination_export_and_native_report(self):
        import csv
        import io

        from sarathi_visibility.sarathi_visibility.report.sarathi_industrial_analysis.sarathi_industrial_analysis import (
            execute,
        )

        f = {"company": self.company, "customer": self.customers[0]}
        extra = frappe.get_doc(
            {
                "doctype": "Project",
                "project_name": f"=test-{self.token}",
                "company": self.company,
                "customer": self.customers[0],
            }
        ).insert()
        first = get_report(f, "projects", page_length=1)
        second = get_report(f, "projects", start=1, page_length=1)
        self.assertEqual(first["total"], 2)
        self.assertNotEqual(first["rows"][0].name, second["rows"][0].name)
        native = execute(dict(f, report_type="Project portfolio"))
        self.assertEqual({r.name for r in native[1]}, {self.projects[0], extra.name})
        export_report(f, "projects")
        exported = list(csv.reader(io.StringIO(frappe.response.filecontent)))
        self.assertEqual(len(exported), 3)
        self.assertTrue(any("'=test-" in value for row in exported for value in row))
        for key in ("type", "filename", "filecontent", "display_content_as"):
            frappe.response.pop(key, None)

    def test_company_user_permission(self):
        other = frappe.get_all(
            "Company", filters={"name": ["!=", self.company]}, pluck="name", limit=1
        )
        if not other:
            self.skipTest("Second company needed for company permission test")
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": f"sarathi-test-{self.token}@example.invalid",
                "first_name": "Dashboard test",
                "send_welcome_email": 0,
                "roles": [
                    {"role": role}
                    for role in ("Projects User", "Manufacturing User", "Sales User")
                ],
            }
        ).insert()
        frappe.get_doc(
            {
                "doctype": "User Permission",
                "user": user.name,
                "allow": "Company",
                "for_value": self.company,
                "apply_to_all_doctypes": 1,
            }
        ).insert()
        frappe.set_user(user.name)
        data = get_summary({"company": self.company})
        self.assertTrue(all(p.company == self.company for p in data["projects"]))
        with self.assertRaises(frappe.PermissionError):
            get_summary({"company": other[0]})

    def test_project_resource_scoping_isolation(self):
        # A newly created project with no linked resources must return 0 for project masters
        p_filter = {"project": self.projects[0]}
        summary = get_summary(p_filter)
        kpis = {k["report"]: k["value"] for k in summary["kpis"]}
        for report_key in (
            "warehouses",
            "operations_catalogue",
            "workstations",
            "workstation_types",
            "routings",
            "items",
        ):
            self.assertEqual(
                kpis.get(report_key),
                0,
                f"Expected 0 for {report_key} in project summary KPI",
            )
            scoped_report = get_report(p_filter, report_key)
            self.assertEqual(
                scoped_report["total"],
                0,
                f"Expected 0 rows for {report_key} in project scoped report",
            )
            # If user explicitly chooses all records (subset="all"), company records are accessible
            all_report = get_report(p_filter, report_key, subset="all")
            self.assertGreaterEqual(all_report["total"], scoped_report["total"])


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DashboardTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    frappe.db.rollback()
    if not result.wasSuccessful():
        raise AssertionError("Dashboard integration tests failed")
    return {"tests": result.testsRun, "skipped": len(result.skipped), "passed": True}
