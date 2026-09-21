frappe.query_reports["Sarathi Industrial Analysis"] = {
  filters: [
    {fieldname: "company", label: "Organization", fieldtype: "Link", options: "Company"},
    {fieldname: "customer", label: "Customer", fieldtype: "Link", options: "Customer"},
    {fieldname: "unassigned_customer", label: "Unassigned customer", fieldtype: "Check"},
    {fieldname: "project", label: "Project", fieldtype: "Link", options: "Project"},
    {fieldname: "from_date", label: "From date", fieldtype: "Date"},
    {fieldname: "to_date", label: "To date", fieldtype: "Date"},
    {fieldname: "status", label: "Project status", fieldtype: "Select", options: "\nActive\nOngoing\nCompleted\nDelayed\nCancelled\nOn hold"},
    {fieldname: "report_type", label: "Report", fieldtype: "Select", default: "Project portfolio", options: "Material Request project items\nPurchase Order project items\nPurchase Receipt project items\nPurchase Invoice project items\nDelivery Note project items\nSales Invoice project items\nUnassigned / conflicting procurement\nLifetime material consumption\nLifetime stock movement items\nProject voucher stock ledger\nProject stock reservations\nProject quality inspections\nJob Card time history\nJob Card sub-operations\nProject part tracking setup\nRecorded operation output parts\nLive project activity\nProject production summary\nLifetime operation balances\nSemi-finished shared warehouse stock\nUpcoming and overdue deadlines\nProject portfolio\nSales orders\nOrder items and delivery\nWork orders\nJob cards / shop floor\nEngineering / BOM revisions\nEngineering components / purchased parts\nPlanned BOM operations\nMaterial requirements / shared warehouse stock\nStock movements\nFinished production receipts\nProject tasks / pipeline\nMachine integration logs\nData quality and alerts\nSelected project workstation workload"},
    {fieldname: "subset", label: "Subset", fieldtype: "Select", options: "\nactive\ncompleted\nongoing\non_hold\nin_progress\nnot_started\npaused\nclosure_pending\ndelayed\nopen\nshortages\nplanned\nrework"},
    {fieldname: "search", label: "Search", fieldtype: "Data"}
  ]
};
