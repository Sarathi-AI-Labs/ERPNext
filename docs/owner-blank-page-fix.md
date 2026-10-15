# Owner blank page repair

Audit: authenticated browser reproduced TypeError in Frappe AssetManager.load_asset from both owner page load and show. The installed loader extracts the extension from the query string, so manually appended ?v= values have no handler.

Retain: dashboard layout, metrics, permissions, existing local edits and core source. Improve: pass plain CSS/JS paths to frappe.require and let its loader add cache versions. Build: no new metrics or services. KPI contracts are unchanged.

Validation: authenticated browser load, navigation and reload; record results after repair. No Frappe or ERPNext core changes. Rollback: restore the two asset URL query strings and version declarations in the custom page.

Verified locally: authenticated Administrator browser renders dashboard at 1440px, reload renders successfully with zero JavaScript exceptions, and dashboard remains visible at 390px. KPI reconciliation and other-role acceptance were outside this loader repair. No core source edited.
