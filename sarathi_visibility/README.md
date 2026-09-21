# Sarathi Visibility

Custom Frappe app for the Sarathi Industrial Manufacturing Control Tower.

This app adds a Desk page at `/desk/sarathicontroltower` that reads ERPNext
Project, BOM, Work Order, Job Card, Stock Entry, Warehouse and Item data for
`PRJ-MEZZANINE-001` / `PROJ-0002`.

## Install in a running bench

```sh
bench get-app /workspace/sarathi_visibility
bench --site <site-name> install-app sarathi_visibility
bench --site <site-name> migrate
```

## Default project context

- Company: `Sarathi Manufacturing Pvt Ltd`
- Project display name: `PRJ-MEZZANINE-001`
- ERPNext Project document: `PROJ-0002`
- Sales reference: `Sales Order 368`
