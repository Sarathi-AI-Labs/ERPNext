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

doc_events = {
    "Sales Order": {
        "on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"
    },
    "Sales Invoice": {
        "on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"
    },
    "Payment Entry": {
        "on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"
    },
    "Work Order": {
        "on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"
    },
    "Stock Entry": {
        "on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"
    },
    "Project": {"on_change": "sarathi_owner.api.owner_dashboard.broadcast_live_event"},
}
