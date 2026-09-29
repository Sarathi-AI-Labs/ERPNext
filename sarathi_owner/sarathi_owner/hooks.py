app_name = "sarathi_owner"
app_title = "Sarathi Owner Dashboard"
app_publisher = "Sarathi AI Labs"
app_description = "Executive owner dashboard and manufacturing pipeline for ERPNext"
app_email = "admin@example.com"
app_license = "MIT"

after_install = "sarathi_owner.setup.install.after_install"
after_migrate = "sarathi_owner.setup.install.after_migrate"

app_include_css = "/assets/sarathi_owner/css/sarathi_owner_dashboard.css"
app_include_js = "/assets/sarathi_owner/js/sarathi_owner_dashboard.js"

DOC_WATCH_LIST = [
    "Project",
    "Company",
    "Customer",
    "Sales Order",
    "Sales Invoice",
    "Payment Entry",
    "Work Order",
    "Stock Entry",
    "Delivery Note",
    "BOM",
    "Task",
    "Warehouse",
    "Item",
]

doc_events = {
    dt: {
        "on_update": "sarathi_owner.api.owner_dashboard.broadcast_live_event",
        "on_submit": "sarathi_owner.api.owner_dashboard.broadcast_live_event",
        "on_cancel": "sarathi_owner.api.owner_dashboard.broadcast_live_event",
        "on_trash": "sarathi_owner.api.owner_dashboard.broadcast_live_event",
    }
    for dt in DOC_WATCH_LIST
}

