"""
Script to add in-dashboard Card Details & Record Inspector (List, Table, Form format)
without navigating into ERPNext.
"""

js_path = 'sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js'
with open(js_path, encoding='utf-8') as f:
    js = f.read()

# 1. Update this.link to not navigate to /desk/...
old_link = '''  link(dt, name, label) {
    return name
      ? `<a href="/desk/${String(dt).toLowerCase().replaceAll(" ", "-")}/${encodeURIComponent(name)}">${this.esc(label || name)}</a>`
      : "—";
  }'''

new_link = '''  link(dt, name, label) {
    return name
      ? `<a href="javascript:void(0)" class="sd-record-link" data-inspect="${this.esc(name)}" data-doctype="${this.esc(dt)}" title="View ${this.esc(dt)} details">${this.esc(label || name)}</a>`
      : "—";
  }'''

if old_link in js:
    js = js.replace(old_link, new_link, 1)
    print("1. Replaced this.link to stay in dashboard")
else:
    print("Warning: old_link not matched")

# 2. Add showCardDetailsModal, renderCardDetailsTable, showRecordFormModal, formatCellValue, getDocTypeForReport
new_methods = '''
  // ==========================================
  // IN-DASHBOARD CARD DETAILS (LIST, TABLE & FORMS)
  // ==========================================

  getDocTypeForReport(report) {
    const map = {
      items: "Item",
      inventory: "Bin",
      warehouses: "Warehouse",
      workstations: "Workstation",
      workstation_types: "Workstation Type",
      operations_catalogue: "Operation",
      routings: "Routing",
      boms: "BOM",
      components: "BOM",
      operations: "BOM",
      customers: "Customer",
      suppliers: "Supplier",
      orders: "Sales Order",
      order_items: "Sales Order",
      work_orders: "Work Order",
      job_cards: "Job Card",
      job_logs: "Job Card",
      job_suboperations: "Job Card",
      projects: "Project",
      requests: "Material Request",
      purchases: "Purchase Order",
      receipts: "Purchase Receipt",
      purchase_invoices: "Purchase Invoice",
      deliveries: "Delivery Note",
      sales_invoices: "Sales Invoice",
      quality: "Quality Inspection",
      stock: "Stock Entry",
      finished: "Stock Entry",
      part_production: "Stock Entry",
      stock_details: "Stock Entry",
      stock_ledger: "Stock Ledger Entry",
      reservations: "Stock Reservation Entry",
      tasks: "Task",
      integrations: "Sarathi Machine Integration Log",
      issues: "Project",
      production_summary: "Project",
      deadlines: "Project",
      material_history: "Work Order",
      operation_balance: "Work Order",
    };
    return map[report] || "Item";
  }

  formatCellValue(c, val) {
    if (val === null || val === undefined || val === "") return "—";
    if (c.fieldtype === "Currency") return "₹" + this.num(val);
    if (["Float", "Int", "Percent"].includes(c.fieldtype))
      return this.num(val) + (c.fieldtype === "Percent" ? "%" : "");
    if (c.fieldtype === "Date") return frappe.datetime.str_to_user(val);
    if (
      String(c.fieldname).toLowerCase().includes("status") ||
      String(c.label).toLowerCase().includes("status")
    ) {
      return this.badge(val);
    }
    return this.esc(val);
  }

  async showCardDetailsModal(reportKey, subset = "", label = "", projectContext = "") {
    if (!reportKey) return;
    const project = projectContext || this.filters.project || "";
    const activeFilters = { ...this.filters };
    if (project) activeFilters.project = project;

    const dialogTitle =
      label ||
      this.data?.reports?.find((r) => r.key === reportKey)?.title ||
      reportKey;

    const dialog = new frappe.ui.Dialog({
      title: `${this.workspaceIcon(dialogTitle)} ${this.esc(dialogTitle)}`,
      size: "extra-large",
      fields: [{ fieldname: "card_content", fieldtype: "HTML" }],
    });
    dialog.$wrapper.addClass("sd-card-details-dialog");
    dialog.fields_dict.card_content.$wrapper.html(
      `<div class="sd-modal-loading"><div class="sd-modal-spinner"></div><p>Fetching ${this.esc(dialogTitle)} records…</p></div>`,
    );
    dialog.show();

    try {
      const data = await this.call("get_report", {
        report: reportKey,
        subset: subset || "",
        search: "",
        start: 0,
        page_length: 100,
        filters: JSON.stringify(activeFilters),
      });

      this.renderCardDetailsTable(
        dialog,
        data,
        reportKey,
        subset,
        dialogTitle,
        project,
      );
    } catch (err) {
      dialog.fields_dict.card_content.$wrapper.html(
        `<div class="sd-empty">Unable to load records for this card. ${this.esc(err.message || "")}</div>`,
      );
    }
  }

  renderCardDetailsTable(
    dialog,
    data,
    reportKey,
    subset,
    title,
    project,
    initialSearch = "",
  ) {
    const $container = dialog.fields_dict.card_content.$wrapper;
    const columns = data.columns || [];
    const rows = data.rows || [];
    const total = data.total || rows.length;
    let currentSearch = initialSearch;

    const defaultDt = this.getDocTypeForReport(reportKey);

    const renderTableBody = (filteredRows) => {
      if (!filteredRows.length) {
        return `<tr><td colspan="${columns.length + 1}" style="text-align: center; padding: 36px; color: #64748b;">No matching records found.</td></tr>`;
      }
      return filteredRows
        .map((row) => {
          const docName =
            row.name || row.parent || row.project || row.item_code || "";
          const doctype = row.doctype || defaultDt;
          return `
          <tr class="sd-modal-row" data-name="${this.esc(docName)}" data-doctype="${this.esc(doctype)}">
            ${columns
              .map((c) => {
                const val = row[c.fieldname];
                return `<td>${this.formatCellValue(c, val)}</td>`;
              })
              .join("")}
            <td style="text-align: right; white-space: nowrap;">
              ${docName ? `<button type="button" class="sd-button sd-modal-btn-view" data-action="view-row-form" data-name="${this.esc(docName)}" data-doctype="${this.esc(doctype)}">View Form 📄</button>` : "—"}
            </td>
          </tr>
        `;
        })
        .join("");
    };

    const getFiltered = (term) => {
      if (!term) return rows;
      const t = term.toLowerCase();
      return rows.filter((r) =>
        Object.values(r).some(
          (v) =>
            v !== null &&
            v !== undefined &&
            String(v).toLowerCase().includes(t),
        ),
      );
    };

    const html = `
      <div class="sd-modal-view-container">
        <!-- Top Toolbar -->
        <div class="sd-modal-toolbar">
          <div class="sd-modal-search-wrap">
            <svg class="sd-modal-search-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="search" class="sd-modal-search-input" value="${this.esc(currentSearch)}" placeholder="Search across all fields in this list..." />
          </div>
          <div class="sd-modal-meta-pills">
            <span class="sd-pill sd-status-blue">${total} Records</span>
            ${project ? `<span class="sd-pill sd-status-amber">Project: ${this.esc(project)}</span>` : ""}
            ${subset ? `<span class="sd-pill sd-status-purple">Subset: ${this.esc(subset)}</span>` : ""}
          </div>
        </div>

        <!-- Table Scroll Container -->
        <div class="sd-modal-table-scroll">
          <table class="sd-modal-table">
            <thead>
              <tr>
                ${columns.map((c) => `<th>${this.esc(c.label)}</th>`).join("")}
                <th style="text-align: right; width: 110px;">Action</th>
              </tr>
            </thead>
            <tbody class="sd-modal-tbody">
              ${renderTableBody(getFiltered(currentSearch))}
            </tbody>
          </table>
        </div>
      </div>
    `;

    $container.html(html);

    // Wire search input
    const $input = $container.find(".sd-modal-search-input");
    const $tbody = $container.find(".sd-modal-tbody");
    $input.on("input", (e) => {
      currentSearch = e.target.value;
      $tbody.html(renderTableBody(getFiltered(currentSearch)));
    });

    // Wire row click / View Form button
    $container.off("click", ".sd-modal-btn-view, .sd-modal-row td:not(:last-child)");
    $container.on(
      "click",
      ".sd-modal-btn-view, .sd-modal-row td:not(:last-child)",
      (e) => {
        const $target = $(e.target).closest("tr");
        const name = $target.attr("data-name");
        let dt = $target.attr("data-doctype");
        if (!dt || dt === "undefined") {
          dt = defaultDt;
        }
        if (name && dt) {
          this.showRecordFormModal(dialog, dt, name, () => {
            this.renderCardDetailsTable(
              dialog,
              data,
              reportKey,
              subset,
              title,
              project,
              currentSearch,
            );
          });
        }
      },
    );
  }

  async showRecordFormModal(dialog, doctype, name, onBackCallback = null) {
    let targetDialog = dialog;
    if (!targetDialog) {
      targetDialog = new frappe.ui.Dialog({
        title: `${doctype} · ${name}`,
        size: "extra-large",
        fields: [{ fieldname: "card_content", fieldtype: "HTML" }],
      });
      targetDialog.$wrapper.addClass("sd-card-details-dialog");
      targetDialog.show();
    }

    const $container = targetDialog.fields_dict.card_content.$wrapper;
    $container.html(
      `<div class="sd-modal-loading"><div class="sd-modal-spinner"></div><p>Loading ${this.esc(doctype)} ${this.esc(name)} form details…</p></div>`,
    );

    try {
      const data = await this.call("get_record", {
        filters: JSON.stringify(this.filters),
        doctype,
        name,
      });

      const row = data.row || {};
      const columns = data.columns || [];
      const related = data.related || [];
      const status =
        row.status || row.workflow_state || row.docstatus_name || "";

      let formHtml = `
        <div class="sd-modal-form-view">
          <!-- Top Action & Navigation Bar -->
          <div class="sd-modal-form-header">
            <div class="sd-modal-form-header-left">
              ${onBackCallback ? `<button type="button" class="sd-button sd-modal-form-back-btn">← Back to Records List</button>` : ""}
              <div class="sd-modal-form-title-badge">
                <span class="sd-form-doctype-tag">${this.esc(doctype)}</span>
                <h3 class="sd-form-docname-title">${this.esc(name)}</h3>
              </div>
            </div>
            <div class="sd-modal-form-header-right">
              ${status ? this.badge(status) : ""}
              <span class="sd-pill sd-status-blue">${this.esc(row.company || this.filters.company || "SarathiAILabs")}</span>
            </div>
          </div>

          <!-- Document Key Fields Grid (Form View) -->
          <div class="sd-modal-form-section-title">
            <span>Document Information</span>
          </div>
          <div class="sd-modal-form-grid">
            ${columns
              .map((c) => {
                const val = row[c.fieldname];
                if (val === null || val === undefined || val === "") return "";
                return `
                <div class="sd-modal-field-card">
                  <span class="sd-modal-field-label">${this.esc(c.label)}</span>
                  <div class="sd-modal-field-val">
                    ${
                      c.fieldtype === "Link"
                        ? `<a href="javascript:void(0)" class="sd-modal-nested-link" data-doctype="${this.esc(c.options)}" data-name="${this.esc(val)}">${this.esc(val)} ↗</a>`
                        : this.formatCellValue(c, val)
                    }
                  </div>
                </div>
              `;
              })
              .join("")}
          </div>

          <!-- Related / Child Tables -->
          ${
            related.length
              ? related
                  .map(
                    (rel) => `
            <div class="sd-modal-related-block">
              <div class="sd-modal-related-title">
                <h4>${this.esc(rel.title)}</h4>
                <span class="sd-pill sd-status-teal">${rel.total} items</span>
              </div>
              ${
                rel.total
                  ? `
                <div class="sd-modal-table-scroll sd-modal-nested-table-wrap">
                  <table class="sd-modal-table sd-modal-nested-table">
                    <thead>
                      <tr>
                        ${rel.columns.map((rc) => `<th>${this.esc(rc.label)}</th>`).join("")}
                        <th style="width: 80px; text-align: right;">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${rel.rows
                        .map((rrow) => {
                          const rname = rrow.name || rrow.parent;
                          const rdt = rrow.doctype || rel.doctype || "";
                          return `
                          <tr>
                            ${rel.columns.map((rc) => `<td>${this.formatCellValue(rc, rrow[rc.fieldname])}</td>`).join("")}
                            <td style="text-align: right;">
                              ${rname ? `<button type="button" class="sd-button sd-btn-xs sd-modal-nested-btn" data-doctype="${this.esc(rdt)}" data-name="${this.esc(rname)}">Inspect</button>` : "—"}
                            </td>
                          </tr>
                        `;
                        })
                        .join("")}
                    </tbody>
                  </table>
                </div>
              `
                  : `<div class="sd-empty" style="margin: 8px 0; padding: 14px;">No linked records found.</div>`
              }
            </div>
          `,
                  )
                  .join("")
              : ""
          }
        </div>
      `;

      $container.html(formHtml);

      // Back button click handler
      if (onBackCallback) {
        $container.find(".sd-modal-form-back-btn").on("click", () => {
          onBackCallback();
        });
      }

      // Nested record links click handlers
      $container.off("click", ".sd-modal-nested-link, .sd-modal-nested-btn");
      $container.on(
        "click",
        ".sd-modal-nested-link, .sd-modal-nested-btn",
        (e) => {
          const $el = $(e.target).closest("[data-name]");
          const ndt = $el.attr("data-doctype");
          const nname = $el.attr("data-name");
          if (ndt && nname) {
            this.showRecordFormModal(targetDialog, ndt, nname, () => {
              this.showRecordFormModal(
                targetDialog,
                doctype,
                name,
                onBackCallback,
              );
            });
          }
        },
      );
    } catch (err) {
      $container.html(
        `<div class="sd-empty">Unable to load form details for ${this.esc(doctype)} ${this.esc(name)}. ${this.esc(err.message || "")}</div>`,
      );
    }
  }
'''

# 3. Update inspect method to use showRecordFormModal
old_inspect = '''  async inspect(doctype, name) {
    const dialog = new frappe.ui.Dialog({
      title: `${doctype} · ${name}`,
      size: "extra-large",
      fields: [{ fieldname: "detail", fieldtype: "HTML" }],
      primary_action_label: "Open in ERPNext",
      primary_action: () => {
        dialog.hide();
        frappe.set_route("Form", doctype, name);
      },
    });'''

# Let's add new_methods before click(event)
click_pos = js.find('  click(event) {')
if click_pos != -1:
    js = js[:click_pos] + new_methods + '\n' + js[click_pos:]
    print("2. Added new card & form modal methods")
else:
    print("Warning: click(event) not found")

# 4. Update click(event) to intercept cards and data-inspect
old_click_start = '''  click(event) {
    const b = event.target.closest("button, .sd-setup-card");
    if (!b || b.disabled) return;
    const d = b.dataset;
    if (d.inspect) this.inspect(d.doctype, d.inspect);'''

new_click_start = '''  click(event) {
    const b = event.target.closest("button, .sd-setup-card, .sd-card, a.sd-record-link, a[data-inspect], .sd-health-metric, .sd-pipeline-step");
    if (!b || b.disabled) return;
    const d = b.dataset;
    if (d.inspect) {
      event.preventDefault();
      this.showRecordFormModal(null, d.doctype, d.inspect);
    }'''

if old_click_start in js:
    js = js.replace(old_click_start, new_click_start, 1)
    print("3. Replaced click starting lines")
else:
    print("Warning: old_click_start not found")

# Also update d.report handling in click(event)
old_report_handle = '''    } else if (d.report) {
      if (d.reportProject && d.reportProject !== this.filters.project)
        this.navigate({ project: d.reportProject, customer: "" });
      this.openReport(d.report, d.subset);'''

new_report_handle = '''    } else if (d.report) {
      const cardLabel = d.kpiLabel || b.querySelector(".sd-metric-label")?.textContent?.trim() || b.querySelector("small")?.textContent?.trim() || b.querySelector("h3")?.textContent?.trim() || b.textContent?.trim();
      this.showCardDetailsModal(d.report, d.subset || "", cardLabel, d.reportProject);'''

if old_report_handle in js:
    js = js.replace(old_report_handle, new_report_handle, 1)
    print("4. Replaced d.report handling to open in-dashboard modal")
else:
    print("Warning: old_report_handle not found")

# Write updated JS
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Successfully patched sarathi_dashboard.js!")
