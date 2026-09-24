app_name = "sarathi_visibility"
app_title = "Sarathi Visibility"
app_publisher = "Sarathi AI Labs"
app_description = "ERPNext-backed manufacturing control tower for Sarathi projects"
app_email = "admin@example.com"
app_license = "MIT"

before_install = "sarathi_visibility.setup.install.before_install"
after_install = "sarathi_visibility.setup.install.after_install"
after_migrate = "sarathi_visibility.setup.install.after_migrate"

app_include_js = "/assets/sarathi_visibility/js/sarathi_desk_prefill.js"

app_include_css = "/assets/sarathi_visibility/css/sarathi_control_tower.css"
before_migrate = "sarathi_visibility.setup.rename_legacy.execute"
extend_bootinfo = ["sarathi_visibility.setup.install.filter_bootinfo_desktop_icons"]


doc_events = {
    "Project": {"validate": "sarathi_visibility.setup.dashboard.validate_project"},
    "BOM": {
        "validate": "sarathi_visibility.setup.dashboard.validate_bom",
        "before_cancel": "sarathi_visibility.setup.dashboard.validate_bom",
        "before_update_after_submit": "sarathi_visibility.setup.dashboard.validate_bom",
        "on_submit": "sarathi_visibility.setup.dashboard.on_bom_submit",
    },
    "Sales Order": {"validate": "sarathi_visibility.setup.dashboard.validate_transaction"},
    "Work Order": {"validate": "sarathi_visibility.setup.dashboard.validate_transaction"},
    "Job Card": {"validate": "sarathi_visibility.setup.dashboard.validate_transaction"},
    "Stock Entry": {"validate": "sarathi_visibility.setup.dashboard.validate_transaction"},
}

for _doctype in ('Material Request', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice', 'Delivery Note', 'Sales Invoice'):
    doc_events.setdefault(_doctype, {})['validate'] = 'sarathi_visibility.setup.dashboard.validate_transaction'

for _doctype in (
    "Material Request",
    "Purchase Order",
    "Purchase Receipt",
    "Purchase Invoice",
    "Delivery Note",
    "Sales Invoice",
    "Quality Inspection",
    "Stock Reservation Entry",
    "Company",
    "Customer",
    "Project",
    "BOM",
    "Sales Order",
    "Work Order",
    "Job Card",
    "Stock Entry",
    "Task",
    "Sarathi Customer Organization",
    "Subcontracting Order",
    "Subcontracting Receipt",
    "Item",
    "Warehouse",
    "Workstation",
    "Operation",
    "Stock Reconciliation",
    "Journal Entry",
    "Payment Entry",
):
    doc_events.setdefault(_doctype, {}).update({
        "on_update": "sarathi_visibility.setup.dashboard.notify_dashboard",
        "on_submit": "sarathi_visibility.setup.dashboard.notify_dashboard",
        "on_update_after_submit": "sarathi_visibility.setup.dashboard.notify_dashboard",
        "on_cancel": "sarathi_visibility.setup.dashboard.notify_dashboard",
        "on_trash": "sarathi_visibility.setup.dashboard.notify_dashboard",
    })

