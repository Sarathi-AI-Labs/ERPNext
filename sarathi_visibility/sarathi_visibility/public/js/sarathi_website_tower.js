(function () {
  const state = {
    data: null,
    employeePreview: false,
    filter: "",
    selectedCompany:
      new URLSearchParams(window.location.search).get("company") || "",
    selectedProject:
      new URLSearchParams(window.location.search).get("project") || "",
    selectedBom: new URLSearchParams(window.location.search).get("bom") || "",
    formSchemas: {},
  };

  const root = document.querySelector(".sarathi-website");
  if (!root) return;
  const BOM_SELECTION_PREFIX = "sarathi_selected_bom_";

  const escapeHtml = (input) =>
    String(input ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const value = (input) => escapeHtml(input ?? "");
  const number = (input) => Number(input || 0);
  const pct = (input) => Math.max(0, Math.min(100, Number(input || 0)));
  const deskRoot = () => "/desk";

  const projectShortcutDoctypes = [
    ["Item", "Create product, raw materials and finished goods"],
    ["Warehouse", "Define WIP, finished goods, scrap and source stores"],
    ["Operation", "Create cutting, drilling, welding and inspection steps"],
    ["Workstation Type", "Group machine and station categories"],
    ["Workstation", "Create shop-floor stations for job cards"],
    ["Plant Floor", "Group production areas"],
    ["Routing", "Build the manufacturing operation sequence"],
    ["BOM", "Attach item, materials, operations and routing"],
    ["Production Plan", "Plan material and manufacturing demand"],
    ["Work Order", "Start manufacturing execution"],
    ["Stock Entry", "Move material through stores, WIP and FG"],
    ["Job Card", "Track operator-level production work"],
  ];

  function routeProject() {
    return new URLSearchParams(window.location.search).get("project") || "";
  }

  function isProjectMode() {
    return Boolean(routeProject());
  }

  function routeCompany() {
    return new URLSearchParams(window.location.search).get("company") || "";
  }

  function selectedBomKey() {
    return `${BOM_SELECTION_PREFIX}${routeProject() || "default"}`;
  }

  function setActiveNav(hash) {
    const activeHash = hash || "#projects";
    root.querySelectorAll(".sarathi-nav a").forEach((link) => {
      link.classList.toggle("active", link.getAttribute("href") === activeHash);
    });
  }

  function persistSelectedBom(name) {
    state.selectedBom = name || "";
    const url = new URL(window.location.href);
    if (state.selectedBom) {
      url.searchParams.set("bom", state.selectedBom);
      sessionStorage.setItem(selectedBomKey(), state.selectedBom);
    } else {
      url.searchParams.delete("bom");
      sessionStorage.removeItem(selectedBomKey());
    }
    window.history.replaceState({}, "", url);
  }

  function closeBomDetail() {
    persistSelectedBom("");
    renderBomDetail(state.data?.data || {});
  }

  function badgeClass(label) {
    const text = String(label || "").toLowerCase();
    if (
      text.includes("complete") ||
      text.includes("received") ||
      text.includes("available") ||
      text.includes("submitted")
    )
      return "success";
    if (
      text.includes("progress") ||
      text.includes("running") ||
      text.includes("open") ||
      text.includes("process")
    )
      return "info";
    if (
      text.includes("short") ||
      text.includes("critical") ||
      text.includes("down") ||
      text.includes("cancel") ||
      text.includes("blocked")
    )
      return "critical";
    if (
      text.includes("delay") ||
      text.includes("warning") ||
      text.includes("pending") ||
      text.includes("not configured") ||
      text.includes("hold")
    )
      return "warning";
    return "";
  }

  function setText(field, text) {
    const node = root.querySelector(`[data-field="${field}"]`);
    if (node) node.textContent = text || "";
  }

  function filtered(rows, fields) {
    if (!state.filter) return rows || [];
    return (rows || []).filter((row) =>
      (fields || Object.keys(row))
        .map((field) => row[field])
        .join(" ")
        .toLowerCase()
        .includes(state.filter),
    );
  }

  function recordUrl(doctype, name) {
    if (!doctype || !name) return "";
    return `${deskRoot()}/${doctype.toLowerCase().replaceAll(" ", "-")}/${encodeURIComponent(name)}`;
  }

  function listUrl(doctype) {
    if (!doctype) return "";
    return `${deskRoot()}/${doctype.toLowerCase().replaceAll(" ", "-")}`;
  }

  function newDocUrl(doctype) {
    if (!doctype) return "";
    const slug = doctype.toLowerCase().replaceAll(" ", "-");
    return `${deskRoot()}/${slug}/new-${slug}`;
  }

  function link(label, doctype, name) {
    if (!label) return "";
    const href = recordUrl(doctype, name);
    return href
      ? `<a class="sarathi-link" href="${href}">${value(label)}</a>`
      : value(label);
  }

  function permission() {
    return state.data?.permission || {};
  }

  function isEmployeeView() {
    return state.employeePreview || permission().view_mode === "employee";
  }

  function canEditSetup() {
    return Boolean(permission().can_edit_setup) && !state.employeePreview;
  }

  function applyViewMode() {
    if (!isProjectMode()) {
      root.classList.remove("sarathi-employee-view");
      root.classList.add("sarathi-admin-view");
      setText("view-mode", "Organization View");
      return;
    }

    const employee = isEmployeeView();
    root.classList.toggle("sarathi-employee-view", employee);
    root.classList.toggle("sarathi-admin-view", !employee);
    setText("view-mode", employee ? "Employee View" : "Admin View");
    const toggle = root.querySelector("[data-action='toggle-employee-view']");
    if (toggle) {
      toggle.textContent = employee ? "Admin View" : "Employee View";
      toggle.hidden = !permission().can_edit_setup;
    }
  }

  function badge(label) {
    return `<span class="sarathi-badge ${badgeClass(label)}">${value(label || "No data")}</span>`;
  }

  function docstatus(input) {
    return badge(["Draft", "Submitted", "Cancelled"][Number(input)] || input);
  }

  function shortage(input) {
    if (input === null || input === undefined || input === "") return "";
    return `<span class="sarathi-number ${number(input) > 0 ? "critical" : "success"}">${value(input)}</span>`;
  }

  function renderKpis(summary) {
    const kpis = [
      [
        "Active Projects",
        summary.active_projects,
        "info",
        listUrl("Project"),
        "projects",
        "ERPNext project portfolio",
      ],
      [
        "Completed",
        summary.completed_projects,
        "success",
        listUrl("Project"),
        "completed",
        "Completed manufacturing projects",
      ],
      [
        "Delayed",
        summary.delayed_projects,
        "warning",
        listUrl("Project"),
        "delayed",
        "Projects needing attention",
      ],
      [
        "Active WOs",
        summary.active_work_orders,
        "info",
        listUrl("Work Order"),
        "work-order",
        "Open production execution",
      ],
      [
        "Open Job Cards",
        summary.open_job_cards,
        "warning",
        listUrl("Job Card"),
        "job-card",
        "Shop-floor work queue",
      ],
      [
        "Shortages",
        summary.shortages,
        "critical",
        listUrl("Material Request"),
        "shortage",
        "Material exceptions",
      ],
      [
        "Production Today",
        summary.production_today,
        "success",
        listUrl("Stock Entry"),
        "production",
        "Today stock movement",
      ],
      [
        "Finished Goods",
        summary.finished_goods,
        "success",
        listUrl("Item"),
        "finished",
        "Finished inventory signal",
      ],
    ];

    root.querySelector("[data-section='kpis']").innerHTML = kpis
      .map(
        ([label, amount, tone, href, icon, detail]) => `
          <a class="sarathi-kpi ${tone}" href="${value(href)}" aria-label="Open ${value(label)}">
            <span class="sarathi-kpi-icon" aria-hidden="true">${kpiIcon(icon)}</span>
            <span class="sarathi-kpi-label">${value(label)}</span>
            <strong>${value(amount ?? 0)}</strong>
            <em>${value(detail)}</em>
            <small>Open</small>
            <i aria-hidden="true"></i>
          </a>
        `,
      )
      .join("");
  }

  function kpiIcon(name) {
    const icons = {
      projects:
        '<svg viewBox="0 0 24 24"><path d="M3 7.5h6l2 2h10v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M3 7.5V6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1.5"/></svg>',
      completed:
        '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m8 12 2.6 2.7L16.5 9"/></svg>',
      delayed:
        '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>',
      "work-order":
        '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2.8v3M12 18.2v3M4.8 4.8l2.1 2.1M17.1 17.1l2.1 2.1M2.8 12h3M18.2 12h3M4.8 19.2l2.1-2.1M17.1 6.9l2.1-2.1"/></svg>',
      "job-card":
        '<svg viewBox="0 0 24 24"><path d="M9 4h6l1 2h3v14H5V6h3Z"/><path d="M9 10h6M9 14h5"/></svg>',
      shortage:
        '<svg viewBox="0 0 24 24"><path d="M12 3 22 20H2Z"/><path d="M12 9v4M12 17h.01"/></svg>',
      production:
        '<svg viewBox="0 0 24 24"><path d="M4 8 12 4l8 4-8 4Z"/><path d="M4 8v8l8 4 8-4V8"/><path d="M12 12v8"/></svg>',
      finished:
        '<svg viewBox="0 0 24 24"><path d="M3 9h8v10H3Z"/><path d="M13 5h8v14h-8Z"/><path d="M5 12h4M15 9h4"/></svg>',
    };
    return icons[name] || icons.projects;
  }

  function renderOrganizations(companies, selectedCompany) {
    const visible = filtered(companies || [], ["name", "company_name", "abbr"]);
    const current = selectedCompany || "";
    setText("organization-count", `${visible.length} organizations`);
    const node = root.querySelector("[data-section='organizations']");
    if (!node) return;

    node.innerHTML = visible.length
      ? visible
          .map((company) => {
            const name = company.name || company.company_name || "";
            const isActive = name === current;
            return `
              <button class="sarathi-organization-option ${isActive ? "active" : ""}" type="button" data-company-name="${value(name)}">
                <span>${value(company.abbr || "Company")}</span>
                <strong>${value(company.company_name || name)}</strong>
                <em>${value(company.project_count || 0)} projects in ERPNext</em>
                <div class="sarathi-organization-metrics">
                  <b><small>Active</small>${value(company.active_projects || 0)}</b>
                  <b><small>Completed</small>${value(company.completed_projects || 0)}</b>
                  <b><small>WOs</small>${value(company.active_work_orders || 0)}</b>
                  <b><small>Shortages</small>${value(company.shortages || 0)}</b>
                </div>
              </button>
            `;
          })
          .join("")
      : `<div class="sarathi-empty">No ERPNext companies found</div>`;
  }

  function renderProjects(projects, selectedProject) {
    const visible = filtered(projects || [], [
      "name",
      "project_name",
      "status",
      "company",
      "customer",
    ]);
    setText("project-count", `${visible.length} projects`);
    const node = root.querySelector("[data-section='projects']");
    if (!node) return;
    node.innerHTML = visible.length
      ? visible
          .map((project) => {
            const isActive = project.name === selectedProject;
            const progress = pct(project.percent_complete);
            return `
              <button class="sarathi-project-option ${isActive ? "active" : ""} ${badgeClass(project.status)}" type="button" data-project-name="${value(project.name)}">
                <span>${value(project.name)}</span>
                <strong>${value(project.project_name || project.display_name || project.name)}</strong>
                <em>${value(project.company || "No company")}</em>
                <div class="sarathi-project-option-meta">
                  <b>${value(project.status || "Open")}</b>
                  <b>${value(project.work_order_count || 0)} WOs</b>
                  <b>${value(project.completed_job_cards || 0)} / ${value(project.job_card_count || 0)} JCs</b>
                </div>
                <i class="sarathi-progress"><i style="width:${progress}%"></i></i>
              </button>
            `;
          })
          .join("")
      : `<div class="sarathi-empty">No projects found for this organization</div>`;
  }

  function renderBomDetail(payload) {
    const boms = payload.boms || [];
    if (
      state.selectedBom &&
      !boms.some((row) => row.name === state.selectedBom)
    ) {
      persistSelectedBom("");
    }
    const bom = boms.find((row) => row.name === state.selectedBom) || {};
    const workOrder = (payload.work_orders || [])[0] || {};
    const operations = payload.bom_operations || [];
    const materials = payload.materials || [];
    const selectedOperations = bom.name
      ? operations.filter((row) => row.parent === bom.name)
      : operations;
    const selectedMaterials = bom.name
      ? materials.filter(
          (row) => row.bom === bom.name || row.parent === bom.name,
        )
      : materials;
    const visibleOperations =
      bom.name && selectedOperations.length ? selectedOperations : operations;
    const visibleMaterials =
      bom.name && selectedMaterials.length ? selectedMaterials : materials;
    const cards = root.querySelector("[data-section='bom-cards']");
    const detailPanel = root.querySelector("[data-section='bom-detail-panel']");
    const summary = root.querySelector("[data-section='bom-summary']");
    if (!summary || !detailPanel) return;

    if (cards) {
      const visibleBoms = filtered(boms, [
        "name",
        "item",
        "item_name",
        "routing",
        "company",
        "source",
      ]);
      cards.innerHTML = visibleBoms.length
        ? visibleBoms
            .map((row) => {
              const status =
                ["Draft", "Submitted", "Cancelled"][Number(row.docstatus)] ||
                "Open";
              const productName =
                row.product_name ||
                row.custom_product_name ||
                row.item_name ||
                row.item;
              return `
                <article class="sarathi-bom-card ${row.name === state.selectedBom ? "active" : ""} ${badgeClass(status)}" data-bom-card data-bom-name="${value(row.name)}" role="button" tabindex="0">
                  <span>${value(status)}</span>
                  <strong>${value(row.name)}</strong>
                  <div class="sarathi-bom-card-fields">
                    <b><small>BOM</small><span>${value(row.name)}</span></b>
                    <b><small>Production Item</small><span>${value(row.item || "No item")}</span></b>
                    <b><small>Item Name</small><span>${value(row.item_name || "No item name")}</span></b>
                    <b><small>Company</small><span>${value(row.company || "No company")}</span></b>
                    <b><small>Product Name</small><span>${value(productName || "No product name")}</span></b>
                    <b><small>Routing</small><span>${value(row.routing || "No routing")}</span></b>
                  </div>
                  <a class="sarathi-link" href="${value(recordUrl("BOM", row.name))}">Open in ERPNext</a>
                </article>
              `;
            })
            .join("")
        : `<div class="sarathi-empty">No ERPNext BOM found for this project</div>`;
    }

    if (!bom.name) {
      detailPanel.hidden = true;
      summary.innerHTML = "";
      return;
    }

    detailPanel.hidden = false;
    const facts = [
      ["BOM", link(bom.name, "BOM", bom.name)],
      [
        "Production Item",
        link(
          bom.item || workOrder.production_item,
          "Item",
          bom.item || workOrder.production_item,
        ),
      ],
      ["Item Name", value(bom.item_name || workOrder.item_name)],
      ["Company", value(bom.company)],
      [
        "Quantity",
        `${value(bom.quantity)} ${value(bom.uom || workOrder.stock_uom || "Nos")}`,
      ],
      ["Routing", link(bom.routing, "Routing", bom.routing)],
      ["Operations", value(visibleOperations.length)],
      ["Components", value(bom.component_count || visibleMaterials.length)],
      ["Total Cost", value(bom.total_cost)],
      ["Status", docstatus(bom.docstatus)],
    ];
    summary.innerHTML = facts
      .map(
        ([label, text]) =>
          `<div><span>${value(label)}</span><strong>${text}</strong></div>`,
      )
      .join("");

    table(
      "bom-operations-summary",
      [
        "No",
        "Operation",
        "Workstation Type",
        "Workstation",
        "Operation Time",
        "Cost",
      ],
      visibleOperations,
      (row, index) => [
        value(row.idx || index + 1),
        link(row.operation, "Operation", row.operation),
        link(row.workstation_type, "Workstation Type", row.workstation_type),
        link(row.workstation, "Workstation", row.workstation),
        value(row.time_in_mins),
        value(row.operating_cost),
      ],
    );

    table(
      "bom-components-summary",
      [
        "No",
        "Item Code",
        "Item Name",
        "Required",
        "Available",
        "Shortage",
        "Warehouse",
      ],
      visibleMaterials,
      (row, index) => [
        value(index + 1),
        link(row.item_code, "Item", row.item_code),
        value(row.item_name),
        value(row.required_qty),
        value(row.available_qty),
        shortage(row.shortage_qty),
        value(row.warehouse),
      ],
    );
  }

  function renderManufacturingProcess(rows) {
    const visible = filtered(rows || [], [
      "phase",
      "label",
      "doctype",
      "summary",
      "status",
    ]);
    const node = root.querySelector("[data-section='manufacturing-process']");
    if (!node) return;
    node.innerHTML = visible.length
      ? visible
          .map((row) => {
            const progress = pct(row.progress);
            const editable = canEditSetup();
            return `
              <article class="sarathi-process-card tone-${value(row.tone)} ${badgeClass(row.status)}" data-process-card="${value(row.key)}" role="button" tabindex="0">
                <span class="sarathi-process-index">${String(row.index).padStart(2, "0")}</span>
                <em>${value(row.phase)}</em>
                <strong>${value(row.label)}</strong>
                <b>${value(row.count)} records</b>
                <span>${value(row.summary)}</span>
                <i class="sarathi-progress"><i style="width:${progress}%"></i></i>
                <small>${value(row.status)} / ${Math.round(progress)}%</small>
                <div class="sarathi-card-actions">
                  <a href="${value(row.list_url)}">Open</a>
                  ${editable ? `<a href="${value(row.create_url)}">Create</a>` : ""}
                  ${row.recent && row.recent[0] ? `<a href="${value(row.recent[0].url)}">${editable ? "Edit" : "View"}</a>` : ""}
                </div>
              </article>
            `;
          })
          .join("")
      : `<div class="sarathi-empty">No process records</div>`;
  }

  function openProcessDrawer(key) {
    const payload = state.data?.data || {};
    const step = (payload.manufacturing_process || []).find(
      (row) => row.key === key,
    );
    if (!step) return;

    const recentRows = (step.recent || [])
      .map(
        (row) => `
          <tr>
            <td><a class="sarathi-link" href="${value(row.url)}">${value(row.name)}</a></td>
            <td>${value(row.title || row.name)}</td>
            <td>${badge(row.status || ["Draft", "Submitted", "Cancelled"][Number(row.docstatus)] || "Open")}</td>
            <td>${value(row.modified || "")}</td>
          </tr>
        `,
      )
      .join("");

    const latestUrl = step.recent && step.recent[0] ? step.recent[0].url : "";
    const drawer = root.querySelector("[data-section='process-drawer']");
    const body = root.querySelector("[data-section='process-drawer-body']");
    const editable = canEditSetup();
    body.innerHTML = `
      <div class="sarathi-drawer-title">
        <span>${value(step.phase)}</span>
        <h3>${value(step.label)}</h3>
        <p>${value(step.summary)}</p>
      </div>
      <div class="sarathi-drawer-actions">
        ${editable ? `<a class="btn btn-primary btn-sm" href="${value(step.create_url)}">Create New</a>` : ""}
        <a class="btn btn-default btn-sm" href="${value(step.list_url)}">Open List</a>
        ${latestUrl ? `<a class="btn btn-default btn-sm" href="${value(latestUrl)}">${editable ? "Edit Latest" : "View Latest"}</a>` : ""}
      </div>
      <div class="sarathi-drawer-stats">
        <div><span>DocType</span><strong>${value(step.doctype)}</strong></div>
        <div><span>Status</span><strong>${value(step.status)}</strong></div>
        <div><span>Records</span><strong>${value(step.count)}</strong></div>
        <div><span>Progress</span><strong>${Math.round(pct(step.progress))}%</strong></div>
      </div>
      <div class="sarathi-table-wrap">
        <table class="sarathi-table">
          <thead><tr><th>Record</th><th>Title</th><th>Status</th><th>Modified</th></tr></thead>
          <tbody>${recentRows || `<tr><td colspan="4" class="sarathi-empty-cell">No records yet. Use Create New to start this step.</td></tr>`}</tbody>
        </table>
      </div>
    `;
    drawer.classList.remove("sarathi-fullscreen-form");
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
  }

  function closeProcessDrawer() {
    const drawer = root.querySelector("[data-section='process-drawer']");
    if (!drawer) return;
    drawer.classList.remove("open", "sarathi-fullscreen-form");
    drawer.setAttribute("aria-hidden", "true");
  }

  function optionTags(options, selected) {
    return (options || [])
      .map(
        (option) =>
          `<option value="${value(option)}" ${option === selected ? "selected" : ""}>${value(option || "Not Set")}</option>`,
      )
      .join("");
  }

  function shortcutTiles() {
    return projectShortcutDoctypes
      .map(([doctype, detail]) => {
        const url = listUrl(doctype);
        return `
          <a class="sarathi-setup-shortcut" href="${value(url)}">
            <strong>${value(doctype)}</strong>
            <span>${value(detail)}</span>
          </a>
        `;
      })
      .join("");
  }

  async function getFormSchema(doctype) {
    if (state.formSchemas[doctype]) {
      return state.formSchemas[doctype];
    }
    const params = new URLSearchParams({ doctype });
    const response = await fetch(
      `/api/method/sarathi_visibility.api.control_tower.get_form_schema?${params}`,
      {
        credentials: "same-origin",
      },
    );
    const payload = await response.json();
    if (!response.ok || payload.exc || !payload.message?.success) {
      throw new Error(
        payload._server_messages ||
          payload.exception ||
          `Unable to load ${doctype} fields.`,
      );
    }
    state.formSchemas[doctype] = payload.message.data.schema;
    return state.formSchemas[doctype];
  }

  function formDefault(field, overrides = {}) {
    if (Object.prototype.hasOwnProperty.call(overrides, field.fieldname)) {
      return overrides[field.fieldname];
    }
    if (field.default !== undefined && field.default !== null) {
      return field.default;
    }
    if (field.fieldtype === "Check") {
      return "0";
    }
    return "";
  }

  function renderMetaControl(field, overrides = {}, doctype = "Project") {
    const fieldname = field.fieldname || "";
    const fieldtype = field.fieldtype || "Data";
    const fieldValue = formDefault(field, overrides);
    const required = field.reqd ? `data-required="1"` : "";
    const disabled = field.read_only ? "disabled" : "";
    const common = `name="${value(fieldname)}" data-doctype="${value(doctype)}" data-fieldname="${value(fieldname)}" class="sarathi-erpnext-field" ${required} ${disabled}`;
    const placeholder =
      field.options && fieldtype === "Link"
        ? `Select ${field.options}`
        : field.label || fieldname;

    if (fieldtype === "Select") {
      const choices = field.select_options || [];
      const options = field.reqd ? choices : ["", ...choices];
      return `
        <div class="sarathi-select-wrap">
          <select ${common}>${optionTags(options, fieldValue)}</select>
        </div>
      `;
    }

    if (fieldtype === "Link") {
      const choices = field.link_options || [];
      const linkDoctype = field.options || "";
      const renderedOptions = choices
        .map((row) => {
          const displayLabel =
            row.label && row.label !== row.value
              ? `${row.label} (${row.value})`
              : row.value;
          const isSelected =
            String(row.value || "") === String(fieldValue || "");
          return `
            <button type="button" class="sarathi-combobox-item ${isSelected ? "selected" : ""}" data-value="${value(row.value)}" data-label="${value(displayLabel)}">
              <span class="sarathi-combobox-item-title">${value(displayLabel)}</span>
              ${isSelected ? `<svg class="sarathi-combobox-check" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5l3.5 3.5 6.5-7"/></svg>` : ""}
            </button>
          `;
        })
        .join("");

      const hasVal = Boolean(String(fieldValue || "").trim());
      return `
        <div class="sarathi-link-field-wrap" data-combobox-wrap>
          <div class="sarathi-link-input-box">
            <input ${common} type="text" value="${value(fieldValue)}" placeholder="${value(placeholder)}" data-link-doctype="${value(linkDoctype)}" autocomplete="off">
            <div class="sarathi-link-input-actions">
              <button type="button" class="sarathi-link-clear-btn" data-combobox-clear title="Clear value" style="${hasVal ? "display:flex;" : "display:none;"}">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8"/></svg>
              </button>
              <button type="button" class="sarathi-link-trigger-btn" data-combobox-trigger title="Show ${value(linkDoctype || "options")}">
                <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M6 8l4 4 4-4"></path>
                </svg>
              </button>
            </div>
          </div>
          <div class="sarathi-link-dropdown" data-combobox-dropdown>
            <div class="sarathi-combobox-list">
              ${choices.length ? renderedOptions : `<div class="sarathi-combobox-empty">No ${value(linkDoctype || "record")} records available</div>`}
            </div>
            <div class="sarathi-link-actions">
              <a class="sarathi-link-action-btn create" href="${value(newDocUrl(linkDoctype))}" target="_blank">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
                <span>+ Create a new ${value(linkDoctype || "record")}</span>
              </a>
              <a class="sarathi-link-action-btn search" href="${value(listUrl(linkDoctype))}" target="_blank">
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="7" cy="7" r="4.5"/><path d="M13 13l-3-3"/></svg>
                <span>Advanced Search</span>
              </a>
            </div>
          </div>
        </div>
      `;
    }

    if (fieldtype === "Check") {
      const isChecked = String(fieldValue) === "1";
      return `
        <label class="sarathi-check-card ${isChecked ? "checked" : ""}" data-doctype="${value(doctype)}" data-fieldname="${value(fieldname)}">
          <input type="checkbox" ${common} value="1" ${isChecked ? "checked" : ""}>
          <span class="sarathi-check-box" aria-hidden="true">
            <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2.5 7.5L5.5 10.5L11.5 3.5"></path>
            </svg>
          </span>
          <span class="sarathi-check-title">${value(field.label || fieldname)}</span>
        </label>
      `;
    }

    if (fieldtype === "Table") {
      return `
        <div class="sarathi-child-table-note" data-doctype="${value(doctype)}" data-fieldname="${value(fieldname)}">
          <div class="sarathi-child-table-icon">
            <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="14" height="12" rx="2"/><path d="M3 8h14M8 4v12"/></svg>
          </div>
          <div class="sarathi-child-table-info">
            <strong>${value(field.label || fieldname)}</strong>
            <span>${value(field.options || "Child Table")} opens in ERPNext native grid after Continue.</span>
          </div>
        </div>
      `;
    }

    if (
      ["Text", "Text Editor", "Small Text", "Long Text", "Code"].includes(
        fieldtype,
      )
    ) {
      return `<textarea ${common} rows="3" placeholder="${value(placeholder)}">${value(fieldValue)}</textarea>`;
    }

    const typeMap = {
      Date: "date",
      Datetime: "datetime-local",
      Time: "time",
      Currency: "number",
      Float: "number",
      Percent: "number",
      Int: "number",
      Data: "text",
    };
    return `<input ${common} type="${value(typeMap[fieldtype] || "text")}" value="${value(fieldValue)}" placeholder="${value(placeholder)}">`;
  }

  function renderMetaField(field, overrides = {}, doctype = "Project") {
    const fieldname = field.fieldname || "";
    if (!fieldname) return "";
    const conditionallyRequired = !field.reqd && field.mandatory_depends_on;
    const requiredBadge = field.reqd
      ? `<em class="sarathi-badge-req">Required</em>`
      : conditionallyRequired
        ? `<em class="sarathi-badge-cond">Conditional</em>`
        : "";
    const roBadge = field.read_only
      ? `<em class="sarathi-badge-ro">Read Only</em>`
      : "";

    if (field.fieldtype === "Check") {
      return `
        <div class="sarathi-meta-field check-wrap">
          ${renderMetaControl(field, overrides, doctype)}
          ${field.description ? `<small class="sarathi-field-desc">${value(field.description)}</small>` : ""}
        </div>
      `;
    }
    if (field.fieldtype === "Table") {
      return `
        <div class="sarathi-meta-field wide">
          ${renderMetaControl(field, overrides, doctype)}
        </div>
      `;
    }
    const isWide = [
      "Text",
      "Text Editor",
      "Small Text",
      "Long Text",
      "Code",
    ].includes(field.fieldtype);
    const wideClass = isWide ? "wide" : "";
    const roClass = field.read_only ? "is-readonly" : "";

    return `
      <label class="sarathi-meta-field ${wideClass} ${roClass}">
        <span class="sarathi-field-label">
          <strong>${value(field.label || fieldname)}</strong>
          ${requiredBadge}
          ${roBadge}
        </span>
        ${renderMetaControl(field, overrides, doctype)}
        ${field.description ? `<small class="sarathi-field-desc">${value(field.description)}</small>` : ""}
      </label>
    `;
  }

  function schemaTone(index) {
    return ["blue", "teal", "orange", "purple", "green", "slate"][index % 6];
  }

  function renderSchemaTabs(schema, doctype, overrides = {}, skipFields = []) {
    const skip = new Set(skipFields);
    const tabs = [];
    let currentTab = {
      key: "details",
      title: "Details",
      sections: [],
    };
    tabs.push(currentTab);

    let currentSection = {
      title: "",
      detail: "",
      columns: [[]],
    };
    currentTab.sections.push(currentSection);

    (schema?.fields || []).forEach((field) => {
      const ftype = field.fieldtype;

      if (ftype === "Tab Break") {
        const tabKey =
          field.fieldname ||
          String(field.label || `tab_${tabs.length}`)
            .toLowerCase()
            .replace(/\s+/g, "_");
        const tabTitle = field.label || field.fieldname || "Details";
        currentTab = {
          key: tabKey,
          title: tabTitle,
          sections: [],
        };
        tabs.push(currentTab);
        currentSection = {
          title: "",
          detail: "",
          columns: [[]],
        };
        currentTab.sections.push(currentSection);
        return;
      }

      if (ftype === "Section Break") {
        currentSection = {
          title: field.label || "",
          detail: "",
          columns: [[]],
        };
        currentTab.sections.push(currentSection);
        return;
      }

      if (ftype === "Column Break") {
        currentSection.columns.push([]);
        return;
      }

      if (!field.fieldname || skip.has(field.fieldname)) {
        return;
      }

      const lastCol = currentSection.columns[currentSection.columns.length - 1];
      lastCol.push(field);
    });

    const visibleTabs = tabs
      .map((tab) => {
        const validSections = tab.sections
          .map((sec) => {
            const validCols = sec.columns
              .map((col) =>
                col
                  .map((f) => renderMetaField(f, overrides, doctype))
                  .filter(Boolean),
              )
              .filter((col) => col.length > 0);
            return {
              ...sec,
              renderedCols: validCols,
            };
          })
          .filter((sec) => sec.renderedCols.length > 0);
        return {
          ...tab,
          sections: validSections,
        };
      })
      .filter((tab) => tab.sections.length > 0);

    const buttons = visibleTabs
      .map(
        (tab, index) => `
          <button class="${index === 0 ? "active" : ""}" type="button" data-wrapper-tab-button="${value(doctype)}:${value(tab.key)}">
            ${value(tab.title)}
          </button>
        `,
      )
      .join("");

    const panels = visibleTabs
      .map((tab, tabIndex) => {
        const sectionsHtml = tab.sections
          .map((sec, secIndex) => {
            const colCount = Math.min(sec.renderedCols.length, 3);
            const columnsHtml = sec.renderedCols
              .map(
                (colFields) => `
                  <div class="sarathi-form-col">
                    ${colFields.join("")}
                  </div>
                `,
              )
              .join("");

            return `
              <section class="sarathi-form-section ${schemaTone(tabIndex + secIndex)}">
                ${
                  sec.title
                    ? `
                  <div class="sarathi-form-section-title">
                    <h4>${value(sec.title)}</h4>
                    ${sec.detail ? `<p>${value(sec.detail)}</p>` : ""}
                  </div>
                `
                    : ""
                }
                <div class="sarathi-form-columns" data-cols="${colCount}">
                  ${columnsHtml}
                </div>
              </section>
            `;
          })
          .join("");

        return `
          <div class="sarathi-wrapper-tab-panel ${tabIndex === 0 ? "active" : ""}" data-wrapper-tab-panel="${value(doctype)}:${value(tab.key)}">
            ${sectionsHtml}
          </div>
        `;
      })
      .join("");

    return `
      <div class="sarathi-wrapper-tabs" data-wrapper-tabs="${value(doctype)}">
        <div class="sarathi-wrapper-tab-list">${buttons}</div>
        <div class="sarathi-wrapper-tab-panels">${panels}</div>
      </div>
    `;
  }

  async function openCreateProjectPanel() {
    const payload = state.data?.data || {};
    const companies = payload.companies || [];
    const currentCompany =
      routeCompany() || payload.organization?.company || "";
    const hasCompanies = companies.length > 0;
    const drawer = root.querySelector("[data-section='process-drawer']");
    const body = root.querySelector("[data-section='process-drawer-body']");
    if (!body || !drawer) return;

    drawer.classList.add("open", "sarathi-fullscreen-form");
    drawer.setAttribute("aria-hidden", "false");
    body.innerHTML = `
      <div class="sarathi-drawer-title">
        <span>Sarathi ERPNext Wrapper</span>
        <h3>Create Manufacturing Project</h3>
        <p>Loading live ERPNext form fields and dropdown options...</p>
      </div>
      <div class="sarathi-empty">Reading Project and Company metadata from ERPNext</div>
    `;

    let projectSchema = null;
    let companySchema = null;
    try {
      [projectSchema, companySchema] = await Promise.all([
        getFormSchema("Project"),
        getFormSchema("Company"),
      ]);
    } catch (error) {
      body.innerHTML = `
        <div class="sarathi-drawer-title">
          <span>Sarathi ERPNext Wrapper</span>
          <h3>Create Manufacturing Project</h3>
          <p>Unable to read ERPNext form schema.</p>
        </div>
        <div class="sarathi-form-error">${value(error.message || error)}</div>
      `;
      return;
    }

    const options = companies
      .map((company) => {
        const name = company.name || company.company_name || "";
        const label = `${company.company_name || name}${company.abbr ? ` / ${company.abbr}` : ""}`;
        return `<option value="${value(name)}" ${name === currentCompany ? "selected" : ""}>${value(label)}</option>`;
      })
      .join("");
    const projectDefaults = {
      company: currentCompany,
      naming_series: "PROJ-.####",
      status: "Open",
      priority: "Medium",
      is_active: "Yes",
      percent_complete_method: "Manual",
      percent_complete: "0",
    };
    const companyDefaults = {
      default_currency: "INR",
      country: "India",
      valuation_method: "FIFO",
    };

    body.innerHTML = `
      <div class="sarathi-drawer-title">
        <span>Sarathi ERPNext Wrapper</span>
        <h3>Create Manufacturing Project</h3>
        <p>Fill the launch details here using live ERPNext fields and options, then continue to the real ERPNext form for final review and save.</p>
      </div>
      <form class="sarathi-form" data-form="project-create">
        <div class="sarathi-native-form-header">
          <div class="sarathi-native-title">
            <span class="sarathi-breadcrumb-path">/ Projects / Project /</span>
            <strong>New Project</strong>
            <em class="sarathi-status-pill">Not Saved</em>
          </div>
          <div class="sarathi-native-header-actions">
            <div class="sarathi-mode-switch">
              <label class="${hasCompanies ? "active" : "disabled"}">
                <input type="radio" name="org_mode" value="existing" ${hasCompanies ? "checked" : "disabled"}>
                <span>Existing Organization</span>
              </label>
              <label class="${hasCompanies ? "" : "active"}">
                <input type="radio" name="org_mode" value="new" ${hasCompanies ? "" : "checked"}>
                <span>New Organization</span>
              </label>
            </div>
            <button class="sarathi-native-save" type="submit">Save</button>
          </div>
        </div>

        <section class="sarathi-form-section teal" data-existing-company>
          <div class="sarathi-form-section-title">
            <h4>Existing Organization</h4>
            <p>Select the ERPNext company that will own this project.</p>
          </div>
          <div class="sarathi-form-columns" data-cols="1">
            <div class="sarathi-form-col">
              <label class="sarathi-meta-field">
                <span class="sarathi-field-label"><strong>Organization</strong> <em class="sarathi-badge-req">Required</em></span>
                <div class="sarathi-select-wrap">
                  <select name="company" class="sarathi-erpnext-field" ${hasCompanies ? "required" : ""}>
                    ${options || `<option value="">No organizations available</option>`}
                  </select>
                </div>
              </label>
            </div>
          </div>
        </section>

        <div data-new-company-fields ${hasCompanies ? "hidden" : ""}>
          <div class="sarathi-form-section-title">
            <h4>New Organization Form</h4>
            <p>These are live ERPNext Company fields. ERPNext Company opens first, then Sarathi opens the Project form after save.</p>
          </div>
          ${renderSchemaTabs(companySchema, "Company", companyDefaults, [])}
        </div>

        <div class="sarathi-project-form-container" data-project-form-section>
          <div class="sarathi-form-section-title">
            <h4>ERPNext Project Form</h4>
            <p>Details, Costing, Progress and More Info fields are rendered from ERPNext DocType metadata.</p>
          </div>
          ${renderSchemaTabs(projectSchema, "Project", projectDefaults, [])}
        </div>

        <section class="sarathi-form-section slate">
          <div class="sarathi-form-section-title">
            <h4>Manufacturing Setup Shortcuts</h4>
            <p>Open ERPNext setup and execution documents needed after the project is saved.</p>
          </div>
          <div class="sarathi-setup-shortcuts">
            ${shortcutTiles()}
          </div>
        </section>

        <div class="sarathi-form-error" data-form-error hidden></div>
        <div class="sarathi-drawer-actions">
          <button class="btn btn-primary btn-sm" type="submit">Continue to ERPNext Form</button>
          <a class="btn btn-default btn-sm" href="/desk/project/new-project" target="_blank">Open Blank Project Form</a>
          <a class="btn btn-default btn-sm" href="/desk/company/new-company" target="_blank">Open Blank Company Form</a>
        </div>
      </form>
    `;
    drawer.classList.add("open", "sarathi-fullscreen-form");
    drawer.setAttribute("aria-hidden", "false");
    syncCreateProjectMode(body.querySelector("[data-form='project-create']"));
  }

  function syncCreateProjectMode(form) {
    if (!form) return;
    const mode = new FormData(form).get("org_mode") || "existing";
    const existing = form.querySelector("[data-existing-company]");
    const fresh = form.querySelector("[data-new-company-fields]");
    const breadcrumb = form.querySelector(".sarathi-breadcrumb-path");
    const docTitle = form.querySelector(".sarathi-native-title strong");
    const saveBtn = form.querySelector(".sarathi-native-save");
    const submitBtn = form.querySelector("[type='submit'].btn-primary");

    if (existing) existing.hidden = mode !== "existing";
    if (fresh) fresh.hidden = mode !== "new";
    if (existing) {
      existing
        .querySelectorAll("input, select, textarea")
        .forEach((control) => {
          control.disabled = mode !== "existing";
        });
    }
    if (fresh) {
      fresh.querySelectorAll("input, select, textarea").forEach((control) => {
        control.disabled = mode !== "new";
      });
    }

    if (mode === "existing") {
      if (breadcrumb) breadcrumb.textContent = "/ Projects / Project /";
      if (docTitle) docTitle.textContent = "New Project";
      if (saveBtn) saveBtn.textContent = "Save Project";
      if (submitBtn) submitBtn.textContent = "Continue to ERPNext Form";
    } else {
      if (breadcrumb) breadcrumb.textContent = "/ Organization / Company /";
      if (docTitle) docTitle.textContent = "New Company";
      if (saveBtn) saveBtn.textContent = "Save Company & Continue";
      if (submitBtn) submitBtn.textContent = "Continue with New Company";
    }

    const existingCompany = form.querySelector(
      "[data-existing-company] select[name='company']",
    );
    const newCompanyNameInput = form.querySelector(
      "[data-doctype='Company'][data-fieldname='company_name']",
    );
    const projectCompany = form.querySelector(
      "[data-doctype='Project'][data-fieldname='company']",
    );
    if (mode === "existing" && existingCompany && projectCompany) {
      projectCompany.value = existingCompany.value || "";
    } else if (mode === "new" && newCompanyNameInput && projectCompany) {
      projectCompany.value = newCompanyNameInput.value || "";
    }

    form.querySelectorAll(".sarathi-mode-switch label").forEach((label) => {
      const input = label.querySelector("input");
      label.classList.toggle("active", input?.checked);
    });
  }

  function activateWrapperTab(button) {
    const target = button?.dataset?.wrapperTabButton;
    if (!target) return;
    const group = button.closest("[data-wrapper-tabs]");
    if (!group) return;
    group.querySelectorAll("[data-wrapper-tab-button]").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    group.querySelectorAll("[data-wrapper-tab-panel]").forEach((panel) => {
      panel.classList.toggle(
        "active",
        panel.dataset.wrapperTabPanel === target,
      );
    });
  }

  function openDeskForm(doctype, options) {
    const clean = Object.entries(options || {}).reduce((result, [key, val]) => {
      const text = String(val || "").trim();
      if (text) {
        result[key] = text;
      }
      return result;
    }, {});
    const slug = doctype.toLowerCase().replaceAll(" ", "-");
    const params = new URLSearchParams({ sarathi_prefill: "1", ...clean });
    sessionStorage.setItem(`sarathi_prefill_${slug}`, JSON.stringify(clean));
    window.location.href = `${deskRoot()}/${slug}/new-${slug}?${params.toString()}`;
  }

  function collectDoctypeOptions(form, doctype) {
    const options = {};
    form
      .querySelectorAll(`[data-doctype="${doctype}"][data-fieldname]`)
      .forEach((control) => {
        if (control.disabled) return;
        const fieldname = control.dataset.fieldname;
        if (!fieldname) return;
        if (control.type === "checkbox") {
          options[fieldname] = control.checked ? "1" : "0";
          return;
        }
        const text = String(control.value || "").trim();
        if (text) {
          options[fieldname] = text;
        }
      });
    return options;
  }

  function firstMissingRequired(form, doctype) {
    const missing = Array.from(
      form.querySelectorAll(`[data-doctype="${doctype}"][data-required="1"]`),
    ).find((control) => {
      if (control.disabled || control.readOnly) return false;
      if (control.type === "checkbox") return !control.checked;
      return !String(control.value || "").trim();
    });
    if (!missing) return "";
    const field = missing.closest(".sarathi-meta-field");
    const label =
      field?.querySelector("span")?.textContent ||
      missing.dataset.fieldname ||
      "Required field";
    return label.replace("Required", "").trim();
  }

  function continueToErpNextForm(form) {
    const formData = new FormData(form);
    const mode = formData.get("org_mode") || "existing";
    const error = form.querySelector("[data-form-error]");

    if (error) {
      error.hidden = true;
      error.textContent = "";
    }

    if (mode === "existing") {
      const company = String(formData.get("company") || "").trim();
      const projectOptions = collectDoctypeOptions(form, "Project");
      const missingProjectField = firstMissingRequired(form, "Project");
      if (!company) {
        if (error) {
          error.hidden = false;
          error.textContent =
            "Choose an organization before opening the ERPNext Project form.";
        }
        return;
      }
      if (missingProjectField || !projectOptions.project_name) {
        if (error) {
          error.hidden = false;
          error.textContent = `${missingProjectField || "Project Name"} is required before opening the ERPNext Project form.`;
        }
        return;
      }
      openDeskForm("Project", { ...projectOptions, company });
      return;
    }

    const companyOptions = collectDoctypeOptions(form, "Company");
    const projectOptions = collectDoctypeOptions(form, "Project");
    const companyName = String(companyOptions.company_name || "").trim();
    const missingCompanyField = firstMissingRequired(form, "Company");
    const missingProjectField = firstMissingRequired(form, "Project");
    if (missingCompanyField || !companyName) {
      if (error) {
        error.hidden = false;
        error.textContent = `${missingCompanyField || "Organization Name"} is required before opening the ERPNext Company form.`;
      }
      return;
    }
    if (missingProjectField || !projectOptions.project_name) {
      if (error) {
        error.hidden = false;
        error.textContent = `${missingProjectField || "Project Name"} is required before opening the ERPNext Project form.`;
      }
      return;
    }

    sessionStorage.setItem(
      "sarathi_pending_project_after_company",
      JSON.stringify({ ...projectOptions, company: companyName }),
    );
    openDeskForm("Company", { ...companyOptions, sarathi_continue: "project" });
  }

  function renderProjectFacts(project, payload) {
    const materials = payload.materials || [];
    const required = materials.reduce(
      (total, row) => total + number(row.required_qty),
      0,
    );
    const available = materials.reduce(
      (total, row) => total + number(row.available_qty),
      0,
    );
    const shortageQty = materials.reduce(
      (total, row) => total + number(row.shortage_qty),
      0,
    );
    const workOrders = payload.work_orders || [];
    const jobCards = payload.job_cards || [];
    const completedJobCards = jobCards.filter((row) =>
      String(row.status || "")
        .toLowerCase()
        .includes("complete"),
    ).length;

    root.querySelector("[data-section='project-facts']").innerHTML = [
      [
        "ERPNext Project",
        link(project.name || "PROJ-0002", "Project", project.name),
        recordUrl("Project", project.name),
      ],
      [
        "Sales Reference",
        value(project.sales_order || "No sales order linked"),
        listUrl("Sales Order"),
      ],
      ["Material Required", value(required), listUrl("BOM")],
      ["Material Available", value(available), listUrl("Stock Ledger Entry")],
      [
        "Shortage Qty",
        `<span class="${shortageQty ? "sarathi-text-critical" : "sarathi-text-success"}">${value(shortageQty)}</span>`,
        listUrl("Material Request"),
      ],
      ["Work Orders", value(workOrders.length), listUrl("Work Order")],
      [
        "Job Cards",
        `${completedJobCards} / ${jobCards.length}`,
        listUrl("Job Card"),
      ],
      [
        "Finished Goods",
        value(
          (payload.finished_goods || []).reduce(
            (total, row) => total + number(row.balance_qty),
            0,
          ),
        ),
        listUrl("Item"),
      ],
    ]
      .map(
        ([label, text, href]) =>
          `<a href="${value(href)}"><span>${label}</span><strong>${text}</strong></a>`,
      )
      .join("");
  }

  function renderEmployeeWork(payload) {
    const jobCards = payload.job_cards || [];
    const workOrders = payload.work_orders || [];
    const materials = payload.materials || [];
    const shortageQty = materials.reduce(
      (total, row) => total + number(row.shortage_qty),
      0,
    );
    const currentWorkOrder = workOrders[0] || {};
    const cards = [
      {
        title: "Current Work Order",
        value: currentWorkOrder.name || "No active work order",
        detail: currentWorkOrder.production_item || "Waiting for assignment",
        href: currentWorkOrder.name
          ? recordUrl("Work Order", currentWorkOrder.name)
          : listUrl("Work Order"),
        tone: badgeClass(currentWorkOrder.status || "Open"),
      },
      {
        title: "Completed Job Cards",
        value: `${
          jobCards.filter((row) =>
            String(row.status || "")
              .toLowerCase()
              .includes("complete"),
          ).length
        } / ${jobCards.length}`,
        detail:
          jobCards
            .map((row) => row.operation)
            .filter(Boolean)
            .slice(0, 4)
            .join(", ") || "No operations assigned",
        href: listUrl("Job Card"),
        tone: "success",
      },
      {
        title: "Material Shortage",
        value: shortageQty ? `Short ${shortageQty}` : "Ready",
        detail: shortageQty
          ? "Check material exception before starting next batch"
          : "Material is available for this order",
        href: shortageQty
          ? listUrl("Material Request")
          : listUrl("Stock Entry"),
        tone: shortageQty ? "critical" : "success",
      },
      {
        title: "Next Operation",
        value:
          (
            jobCards.find(
              (row) =>
                !String(row.status || "")
                  .toLowerCase()
                  .includes("complete"),
            ) ||
            jobCards[0] ||
            {}
          ).operation || "Inspection complete",
        detail: (jobCards[0] || {}).workstation || "No workstation assigned",
        href: jobCards[0]
          ? recordUrl("Job Card", jobCards[0].name)
          : listUrl("Job Card"),
        tone: "info",
      },
    ];

    const queue = jobCards
      .slice(0, 6)
      .map(
        (row) => `
          <a class="sarathi-employee-task ${badgeClass(row.status)}" href="${recordUrl("Job Card", row.name)}">
            <span>${value(row.operation || "Operation")}</span>
            <strong>${value(row.name)}</strong>
            <em>${value(row.workstation || "No workstation")} / ${value(row.status || "Open")}</em>
          </a>
        `,
      )
      .join("");

    root.querySelector("[data-section='employee-work']").innerHTML = `
      <div class="sarathi-employee-summary">
        ${cards
          .map(
            (card) => `
              <a class="sarathi-employee-card ${card.tone}" href="${value(card.href)}">
                <span>${value(card.title)}</span>
                <strong>${value(card.value)}</strong>
                <em>${value(card.detail)}</em>
              </a>
            `,
          )
          .join("")}
      </div>
      <div class="sarathi-employee-queue">
        ${queue || `<div class="sarathi-empty">No job cards assigned for this project</div>`}
      </div>
    `;
  }

  function renderProgressRing(name, label, percent, detail, tone) {
    const safePercent = pct(percent);
    const dash = `${safePercent} ${100 - safePercent}`;
    const node = root.querySelector(`[data-chart='${name}']`);
    if (!node) return;
    node.innerHTML = `
      <svg viewBox="0 0 42 42" role="img" aria-label="${value(label)} ${safePercent}%">
        <circle class="ring-bg" cx="21" cy="21" r="15.915"></circle>
        <circle class="ring-value ${tone || ""}" cx="21" cy="21" r="15.915" stroke-dasharray="${dash}" stroke-dashoffset="25"></circle>
      </svg>
      <div>
        <strong>${Math.round(safePercent)}%</strong>
        <span>${value(label)}</span>
        <em>${value(detail || "")}</em>
      </div>
    `;
  }

  function setRingRoutes() {
    const project = state.data?.data?.project || {};
    const routes = {
      "project-progress": project.name
        ? recordUrl("Project", project.name)
        : listUrl("Project"),
      "jobcard-progress": listUrl("Job Card"),
      "workorder-progress": listUrl("Work Order"),
    };
    Object.entries(routes).forEach(([name, route]) => {
      const node = root.querySelector(`[data-chart='${name}']`);
      if (node) {
        node.dataset.dashboardRoute = route;
        node.setAttribute("role", "button");
        node.setAttribute("tabindex", "0");
      }
    });
  }

  function renderLiveAnalysis(rows) {
    const node = root.querySelector("[data-section='live-analysis']");
    node.innerHTML =
      filtered(rows, ["label", "title", "value", "detail", "status"])
        .map((row) => {
          const href = recordUrl(row.doctype, row.name);
          const tag = href ? "a" : "div";
          const attr = href ? `href="${href}"` : "";
          return `
            <${tag} class="sarathi-analysis-card ${badgeClass(row.status)}" ${attr}>
              <span>${value(row.label)}</span>
              <strong>${value(row.title)}</strong>
              <b>${value(row.value)}</b>
              <em>${value(row.detail)}</em>
            </${tag}>
          `;
        })
        .join("") || `<div class="sarathi-empty">No project analysis</div>`;
  }

  function renderPipeline(rows) {
    root.querySelector("[data-section='pipeline']").innerHTML = (rows || [])
      .map((row, index) => {
        const progress = pct(row.progress);
        return `
          <article class="sarathi-stage ${badgeClass(row.status)}" data-pipeline-stage="${value(row.stage)}" role="button" tabindex="0">
            <div class="sarathi-stage-index">${String(index + 1).padStart(2, "0")}</div>
            <span class="sarathi-stage-title">${value(row.stage)}</span>
            <span class="sarathi-badge ${badgeClass(row.status)}">${value(row.status || "Open")}</span>
            <span class="sarathi-progress"><i style="width:${progress}%"></i></span>
            <span class="sarathi-stage-foot">${Math.round(progress)}% complete / ${value(row.weight)}% weight</span>
          </article>
        `;
      })
      .join("");
  }

  function renderMaterialBars(rows) {
    const visible = (rows || []).slice(0, 5);
    const max = Math.max(
      1,
      ...visible.map((row) =>
        Math.max(number(row.required_qty), number(row.available_qty)),
      ),
    );
    const node = root.querySelector("[data-chart='material-bars']");
    node.innerHTML = visible.length
      ? visible
          .map((row) => {
            const requiredPct = (number(row.required_qty) / max) * 100;
            const availablePct = (number(row.available_qty) / max) * 100;
            const short = number(row.shortage_qty);
            return `
              <div class="sarathi-bar-row">
                <div>
                  <strong><a href="${recordUrl("Item", row.item_code)}">${value(row.item_code || row.item_name)}</a></strong>
                  <span>Required ${value(row.required_qty)} / Available ${value(row.available_qty)}</span>
                </div>
                <div class="sarathi-bars">
                  <span class="required" style="width:${requiredPct}%"></span>
                  <span class="available" style="width:${availablePct}%"></span>
                </div>
                <em class="${short ? "critical" : "success"}">${short ? `Short ${value(short)}` : "Ready"}</em>
              </div>
            `;
          })
          .join("")
      : `<div class="sarathi-empty">No material data</div>`;
  }

  function renderAlerts(rows) {
    const visible = filtered(rows, ["type", "severity", "title", "detail"]);
    setText("alert-count", String(visible.length));
    root.querySelector("[data-section='alerts']").innerHTML = visible.length
      ? visible
          .map(
            (row) => `
              <a class="sarathi-alert ${badgeClass(row.severity || row.type)}" href="${value(alertUrl(row))}">
                <strong>${value(row.title || row.type)}</strong>
                <span>${value(row.detail || row.severity)}</span>
              </a>
            `,
          )
          .join("")
      : `<div class="sarathi-empty">No alerts</div>`;
  }

  function alertUrl(row) {
    const payload = state.data?.data || {};
    const title = String(row?.title || "").toLowerCase();
    const material = (payload.materials || []).find(
      (item) =>
        String(item.item_name || "").toLowerCase() === title ||
        String(item.item_code || "").toLowerCase() === title,
    );
    return material
      ? recordUrl("Item", material.item_code)
      : listUrl("Material Request");
  }

  function renderWorkstations(rows) {
    const visible = filtered(rows, [
      "name",
      "workstation_type",
      "current_work_order",
      "current_operation",
      "live_status",
    ]);
    root.querySelector("[data-section='workstations']").innerHTML =
      visible.length
        ? visible
            .map(
              (row) => `
              <a class="sarathi-machine ${badgeClass(row.live_status || row.status)}" href="${recordUrl("Workstation", row.name)}">
                <strong>${value(row.workstation_name || row.name || "Workstation")}</strong>
                <span>${value(row.workstation_type || "Not configured")}</span>
                <span>${value(row.current_operation || "Idle")}</span>
                <em class="${badgeClass(row.live_status || row.status)}">${value(row.live_status || row.status || "Available")}</em>
              </a>
            `,
            )
            .join("")
        : `<div class="sarathi-empty">No workstations</div>`;
  }

  function renderIntegrations(rows) {
    const visible = filtered(rows, [
      "source_system",
      "machine",
      "program",
      "sync_status",
    ]);
    root.querySelector("[data-section='integrations']").innerHTML =
      visible.length
        ? visible
            .map(
              (row) => `
              <a class="sarathi-machine ${badgeClass(row.sync_status)}" href="${listUrl("Sarathi Machine Integration Log")}">
                <strong>${value(row.source_system || "Integration")}</strong>
                <span>${value(row.machine || row.program || "No endpoint connected")}</span>
                <span>Pending syncs: ${value(row.pending_syncs ?? 0)}</span>
                <em class="${badgeClass(row.sync_status)}">${value(row.sync_status || "Not configured")}</em>
              </a>
            `,
            )
            .join("")
        : `<div class="sarathi-empty">No integrations</div>`;
  }

  function table(name, headers, rows, mapRow) {
    const visible = filtered(rows || []);
    const node = root.querySelector(`[data-table='${name}']`);
    if (!node) return;
    node.innerHTML = `
      <thead><tr>${headers.map((head) => `<th>${value(head)}</th>`).join("")}</tr></thead>
      <tbody>
        ${
          visible.length
            ? visible
                .map(
                  (row, index) =>
                    `<tr>${mapRow(row, index)
                      .map((cell) => `<td>${cell}</td>`)
                      .join("")}</tr>`,
                )
                .join("")
            : `<tr><td colspan="${headers.length}" class="sarathi-empty-cell">No data</td></tr>`
        }
      </tbody>
    `;
  }

  function renderTables(payload) {
    table(
      "boms",
      [
        "BOM",
        "Item",
        "Item Name",
        "Qty",
        "Routing",
        "Operations",
        "Components",
        "Status",
      ],
      payload.boms,
      (row) => [
        link(row.name, "BOM", row.name),
        link(row.item, "Item", row.item),
        value(row.item_name),
        value(row.quantity),
        link(row.routing, "Routing", row.routing),
        value(row.with_operations ? "Yes" : "No"),
        value(row.component_count),
        docstatus(row.docstatus),
      ],
    );

    table(
      "materials",
      [
        "Item",
        "Required",
        "Available",
        "Reserved",
        "Transferred",
        "Consumed",
        "Shortage",
        "Purchase",
      ],
      payload.materials,
      (row) => [
        link(row.item_code || row.item_name, "Item", row.item_code),
        value(row.required_qty),
        value(row.available_qty),
        value(row.reserved_qty),
        value(row.transferred_qty),
        value(row.consumed_qty),
        shortage(row.shortage_qty),
        badge(row.purchase_status || row.status || "Not configured"),
      ],
    );

    table(
      "work-orders",
      ["Work Order", "Item", "Qty", "Produced", "Status", "BOM"],
      payload.work_orders,
      (row) => [
        link(row.name, "Work Order", row.name),
        link(row.production_item || row.item_name, "Item", row.production_item),
        value(row.qty),
        value(row.produced_qty),
        badge(row.status),
        link(row.bom_no, "BOM", row.bom_no),
      ],
    );

    table(
      "job-cards",
      ["Job Card", "Operation", "Workstation", "Status", "Qty", "Done", "Time"],
      payload.job_cards,
      (row) => [
        link(row.name, "Job Card", row.name),
        value(row.operation),
        link(row.workstation, "Workstation", row.workstation),
        badge(row.status),
        value(row.for_quantity),
        value(row.total_completed_qty),
        value(row.total_time_in_mins),
      ],
    );

    table(
      "bom-operations",
      [
        "BOM / Source",
        "Operation",
        "Workstation",
        "Type",
        "Time",
        "Cost",
        "Status",
      ],
      payload.bom_operations,
      (row) => [
        link(
          row.parent,
          row.source === "Job Card" ? "Work Order" : "BOM",
          row.parent,
        ),
        link(row.operation, "Operation", row.operation),
        link(row.workstation, "Workstation", row.workstation),
        link(row.workstation_type, "Workstation Type", row.workstation_type),
        value(row.time_in_mins),
        value(row.operating_cost),
        badge(row.status || row.source || "Ready"),
      ],
    );

    table(
      "stock-entries",
      [
        "Stock Entry",
        "Purpose",
        "Work Order",
        "From",
        "To",
        "Status",
        "Posting",
      ],
      payload.stock_entries,
      (row) => [
        link(row.name, "Stock Entry", row.name),
        value(row.purpose),
        link(row.work_order, "Work Order", row.work_order),
        value(row.from_warehouse),
        value(row.to_warehouse),
        docstatus(row.docstatus),
        value(row.posting_date),
      ],
    );

    table(
      "finished-goods",
      ["Item", "Warehouse", "Balance", "Source"],
      payload.finished_goods,
      (row) => [
        link(row.item_code, "Item", row.item_code),
        value(row.warehouse),
        value(row.balance_qty),
        value(row.source),
      ],
    );

    table(
      "engineering-components",
      ["No", "Material", "Cutting Size", "Qty"],
      payload.engineering_components,
      (row) => [
        value(row.no),
        value(row.material),
        value(row.cutting_size),
        value(row.qty),
      ],
    );

    table("bop-items", ["BOP Item", "Qty"], payload.bop_items, (row) => [
      value(row.item),
      value(row.qty),
    ]);

    table(
      "raw-stock",
      ["Raw Stock", "Planned Qty", "Weight Kg"],
      payload.raw_stock_plan,
      (row) => [value(row.stock), value(row.planned_qty), value(row.weight_kg)],
    );
  }

  function renderCompletionCharts(payload) {
    const project = payload.project || {};
    const jobCards = payload.job_cards || [];
    const completedJobCards = jobCards.filter((row) =>
      String(row.status || "")
        .toLowerCase()
        .includes("complete"),
    ).length;
    const jobCardPercent = jobCards.length
      ? (completedJobCards / jobCards.length) * 100
      : 0;
    const workOrders = payload.work_orders || [];
    const produced = workOrders.reduce(
      (total, row) => total + number(row.produced_qty),
      0,
    );
    const planned = workOrders.reduce(
      (total, row) => total + number(row.qty),
      0,
    );
    const workOrderPercent = planned ? (produced / planned) * 100 : 0;

    renderProgressRing(
      "project-progress",
      "Project progress",
      project.percent_complete || 0,
      project.status || "Open",
      "info",
    );
    renderProgressRing(
      "jobcard-progress",
      "Job cards",
      jobCardPercent,
      `${completedJobCards} of ${jobCards.length} completed`,
      "success",
    );
    renderProgressRing(
      "workorder-progress",
      "Work orders",
      workOrderPercent,
      `${produced} of ${planned} produced`,
      "success",
    );
    setRingRoutes();
  }

  function processKeyForStage(stage) {
    const text = String(stage || "").toLowerCase();
    if (text.includes("bom")) return "bom";
    if (text.includes("material")) return "material_request";
    if (text.includes("completion")) return "stock_entry";
    if (
      ["cutting", "fabrication", "welding", "painting", "inspection"].some(
        (name) => text.includes(name),
      )
    )
      return "job_card";
    return "work_order";
  }

  function openSectionPanel(section) {
    const payload = state.data?.data || {};
    const project = payload.project || {};
    const body = root.querySelector("[data-section='process-drawer-body']");
    const drawer = root.querySelector("[data-section='process-drawer']");
    if (!body || !drawer) return;

    const summary = {
      organizations: {
        title: "Organizations",
        detail:
          "ERPNext companies available on the Sarathi Industrial Dashboard.",
        actions: [
          ["Open Companies", listUrl("Company")],
          ["Open Projects", listUrl("Project")],
        ],
        stats: [
          ["Organizations", (payload.companies || []).length],
          ["Selected", (payload.organization || {}).company || ""],
          ["Projects", (payload.projects || []).length],
          ["Shortages", (payload.organization || {}).shortages || 0],
        ],
      },
      process: {
        title: "Manufacturing Process Builder",
        detail:
          "All ERPNext setup and execution documents for the selected project.",
        actions: [
          ["Open Items", listUrl("Item")],
          ["Open BOMs", listUrl("BOM")],
          ["Open Work Orders", listUrl("Work Order")],
        ],
        stats: [
          ["Steps", (payload.manufacturing_process || []).length],
          [
            "Ready Steps",
            (payload.manufacturing_process || []).filter(
              (row) => row.progress > 0,
            ).length,
          ],
          ["Job Cards", (payload.job_cards || []).length],
          ["Stock Entries", (payload.stock_entries || []).length],
        ],
      },
      projects: {
        title: "Organization Projects",
        detail:
          "Every ERPNext project for the selected company. Click a project card to load its own manufacturing dashboard.",
        actions: [
          ["Open ERPNext Projects", listUrl("Project")],
          ["Open Work Orders", listUrl("Work Order")],
        ],
        stats: [
          ["Projects", (payload.projects || []).length],
          [
            "Active",
            (payload.projects || []).filter(
              (row) => row.status !== "Completed" && row.status !== "Cancelled",
            ).length,
          ],
          [
            "Completed",
            (payload.projects || []).filter((row) => row.status === "Completed")
              .length,
          ],
          [
            "Company",
            (payload.organization || {}).company || project.company || "",
          ],
        ],
      },
      project: {
        title: "Project Command",
        detail:
          "Project, sales reference, material quantity, shortage and finished goods status.",
        actions: [
          ["Open Project", recordUrl("Project", project.name || "PROJ-0002")],
          ["Open Work Orders", listUrl("Work Order")],
          ["Open Job Cards", listUrl("Job Card")],
        ],
        stats: [
          ["Project", project.name || "No project selected"],
          ["Status", project.status || "Open"],
          ["Sales", project.sales_order || "No sales order linked"],
          [
            "Finished Goods",
            (payload.finished_goods || []).reduce(
              (total, row) => total + number(row.balance_qty),
              0,
            ),
          ],
        ],
      },
      exceptions: {
        title: "Exception Console",
        detail:
          "Current material shortages, delays and machine/integration issues.",
        actions: [
          ["Open Material Requests", listUrl("Material Request")],
          ["Open Items", listUrl("Item")],
        ],
        stats: [
          ["Alerts", (payload.alerts || []).length],
          [
            "Shortage Qty",
            (payload.materials || []).reduce(
              (total, row) => total + number(row.shortage_qty),
              0,
            ),
          ],
          [
            "Critical",
            (payload.alerts || []).filter(
              (row) => badgeClass(row.severity) === "critical",
            ).length,
          ],
          ["Integrations", (payload.integrations || []).length],
        ],
      },
      analysis: {
        title: "Live Project Analysis",
        detail:
          "Clickable summary of project, BOM, work order, job cards, finished goods and current alert.",
        actions: [
          ["Open Project", recordUrl("Project", project.name || "PROJ-0002")],
          [
            "Open BOM",
            (payload.boms || [])[0]
              ? recordUrl("BOM", payload.boms[0].name)
              : listUrl("BOM"),
          ],
          [
            "Open Work Order",
            (payload.work_orders || [])[0]
              ? recordUrl("Work Order", payload.work_orders[0].name)
              : listUrl("Work Order"),
          ],
        ],
        stats: [
          ["Cards", (payload.live_analysis || []).length],
          ["BOMs", (payload.boms || []).length],
          ["Work Orders", (payload.work_orders || []).length],
          ["Job Cards", (payload.job_cards || []).length],
        ],
      },
      "bom-detail": {
        title: "Project BOM Details",
        detail:
          "BOM header, production item, routing, operation sequence and component demand for this project.",
        actions: [
          [
            "Open BOM",
            (payload.boms || [])[0]
              ? recordUrl("BOM", payload.boms[0].name)
              : listUrl("BOM"),
          ],
          [
            "Open Routing",
            (payload.boms || [])[0]?.routing
              ? recordUrl("Routing", payload.boms[0].routing)
              : listUrl("Routing"),
          ],
          ["Open Items", listUrl("Item")],
        ],
        stats: [
          ["BOMs", (payload.boms || []).length],
          ["Operations", (payload.bom_operations || []).length],
          ["Components", (payload.materials || []).length],
          [
            "Shortage Qty",
            (payload.materials || []).reduce(
              (total, row) => total + number(row.shortage_qty),
              0,
            ),
          ],
        ],
      },
      pipeline: {
        title: "Manufacturing Pipeline",
        detail:
          "Design to finished goods stage visibility. Click a stage card to open the matching ERPNext process.",
        actions: [
          ["Open Work Orders", listUrl("Work Order")],
          ["Open Job Cards", listUrl("Job Card")],
        ],
        stats: [
          ["Stages", (payload.pipeline || []).length],
          [
            "Average Progress",
            `${Math.round((payload.pipeline || []).reduce((total, row) => total + number(row.progress), 0) / Math.max(1, (payload.pipeline || []).length))}%`,
          ],
          [
            "Completed Cards",
            (payload.job_cards || []).filter((row) =>
              String(row.status || "")
                .toLowerCase()
                .includes("complete"),
            ).length,
          ],
          ["Work Orders", (payload.work_orders || []).length],
        ],
      },
      "material-readiness": {
        title: "Material Readiness",
        detail:
          "Required quantity, available quantity and shortages from BOM material demand.",
        actions: [
          ["Open Items", listUrl("Item")],
          ["Open Material Requests", listUrl("Material Request")],
          ["Open Stock Entries", listUrl("Stock Entry")],
        ],
        stats: [
          ["Materials", (payload.materials || []).length],
          [
            "Required",
            (payload.materials || []).reduce(
              (total, row) => total + number(row.required_qty),
              0,
            ),
          ],
          [
            "Available",
            (payload.materials || []).reduce(
              (total, row) => total + number(row.available_qty),
              0,
            ),
          ],
          [
            "Shortage",
            (payload.materials || []).reduce(
              (total, row) => total + number(row.shortage_qty),
              0,
            ),
          ],
        ],
      },
      "production-completion": {
        title: "Production Completion",
        detail:
          "Work order production completion and job card operation completion.",
        actions: [
          ["Open Work Orders", listUrl("Work Order")],
          ["Open Job Cards", listUrl("Job Card")],
          ["Open Stock Entries", listUrl("Stock Entry")],
        ],
        stats: [
          ["Work Orders", (payload.work_orders || []).length],
          [
            "Produced",
            (payload.work_orders || []).reduce(
              (total, row) => total + number(row.produced_qty),
              0,
            ),
          ],
          ["Job Cards", (payload.job_cards || []).length],
          [
            "Completed",
            (payload.job_cards || []).filter((row) =>
              String(row.status || "")
                .toLowerCase()
                .includes("complete"),
            ).length,
          ],
        ],
      },
      "employee-work": {
        title: "Employee Shop-Floor View",
        detail:
          "View-only work queue for operators: work order, job card sequence, workstation and shortage status.",
        actions: [
          ["Open Job Cards", listUrl("Job Card")],
          ["Open Work Orders", listUrl("Work Order")],
          ["Open Workstations", listUrl("Workstation")],
        ],
        stats: [
          ["View Mode", isEmployeeView() ? "Employee" : "Admin"],
          ["User", permission().user || ""],
          ["Job Cards", (payload.job_cards || []).length],
          ["Shortages", (payload.alerts || []).length],
        ],
      },
      tables: {
        title: "ERPNext Detail Tables",
        detail:
          "Materials, Manufacturing, Inventory, Workstations, Integrations and Engineering Source views.",
        actions: [
          ["Open Materials", listUrl("Item")],
          ["Open Manufacturing", listUrl("Work Order")],
          ["Open Inventory", listUrl("Stock Entry")],
          ["Open Workstations", listUrl("Workstation")],
        ],
        stats: [
          ["Materials", (payload.materials || []).length],
          ["BOMs", (payload.boms || []).length],
          ["Work Orders", (payload.work_orders || []).length],
          ["Stock Entries", (payload.stock_entries || []).length],
          ["Workstations", (payload.workstations || []).length],
        ],
      },
    }[section];

    if (!summary) return;
    body.innerHTML = `
      <div class="sarathi-drawer-title">
        <span>Dashboard Section</span>
        <h3>${value(summary.title)}</h3>
        <p>${value(summary.detail)}</p>
      </div>
      <div class="sarathi-drawer-actions">
        ${summary.actions.map(([label, href]) => `<a class="btn btn-default btn-sm" href="${value(href)}">${value(label)}</a>`).join("")}
      </div>
      <div class="sarathi-drawer-stats">
        ${summary.stats.map(([label, amount]) => `<div><span>${value(label)}</span><strong>${value(amount)}</strong></div>`).join("")}
      </div>
    `;
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
  }

  function render() {
    if (!state.data) return;
    const payload = state.data.data || {};
    const project = payload.project || {};
    const organization = payload.organization || {};
    const projectLabel = [
      project.name,
      project.display_name || project.project_name,
    ]
      .filter(Boolean)
      .join(" / ");
    const projectMode = isProjectMode();
    const selectedCompany = projectMode
      ? project.company || routeCompany() || state.selectedCompany
      : routeCompany();

    root.classList.toggle("sarathi-project-mode", projectMode);
    root.classList.toggle("sarathi-organization-mode", !projectMode);

    setText(
      "organization-title",
      organization.company || project.company || "Organization Dashboard",
    );
    setText(
      "organization-projects",
      `${(payload.projects || []).length} Projects`,
    );
    setText(
      "organization-status",
      projectMode ? "Selected project dashboard" : "All organization projects",
    );
    setText(
      "selected-project-summary",
      projectLabel
        ? `${projectLabel} / ${project.status || "Not configured"}`
        : "Select a project to load live data",
    );
    state.selectedProject = projectMode
      ? project.name || state.selectedProject
      : "";
    state.selectedCompany = selectedCompany || "";

    setText(
      "generated-at",
      state.data.generated_at
        ? new Date(state.data.generated_at).toLocaleString()
        : "",
    );

    renderKpis(payload.organization || {});
    renderOrganizations(payload.companies || [], selectedCompany);
    applyViewMode();
    renderProjects(payload.projects || [], projectMode ? project.name : "");

    if (!projectMode) {
      return;
    }

    renderEmployeeWork(payload);
    renderManufacturingProcess(payload.manufacturing_process || []);
    renderProjectFacts(project, payload);
    renderCompletionCharts(payload);
    renderLiveAnalysis(payload.live_analysis || []);
    renderBomDetail(payload);
    renderPipeline(payload.pipeline || []);
    renderMaterialBars(payload.materials || []);
    renderAlerts(payload.alerts || []);
    renderWorkstations(payload.workstations || []);
    renderIntegrations(payload.integrations || []);
    renderTables(payload);
  }

  async function load() {
    root.classList.add("loading");
    try {
      state.selectedProject = routeProject();
      state.selectedCompany = routeCompany() || state.selectedCompany;
      state.selectedBom =
        new URLSearchParams(window.location.search).get("bom") ||
        sessionStorage.getItem(selectedBomKey()) ||
        "";
      const params = new URLSearchParams();
      const method = state.selectedProject
        ? "sarathi_visibility.api.control_tower.get_dashboard"
        : "sarathi_visibility.api.control_tower.get_organization_summary";
      if (state.selectedProject) {
        params.set("project", state.selectedProject);
      } else if (state.selectedCompany) {
        params.set("company", state.selectedCompany);
      }
      const query = params.toString();
      const response = await fetch(
        `/api/method/${method}${query ? `?${query}` : ""}`,
        {
          credentials: "same-origin",
        },
      );
      const payload = await response.json();
      state.data = payload.message;
      render();
    } catch (error) {
      root.querySelector("[data-section='live-analysis']").innerHTML =
        `<div class="sarathi-empty">Unable to load dashboard data</div>`;
    } finally {
      root.classList.remove("loading");
    }
  }

  root.querySelector("[data-action='refresh']").addEventListener("click", load);
  root
    .querySelector("[data-action='open-project-create']")
    ?.addEventListener("click", openCreateProjectPanel);
  root
    .querySelector("[data-action='toggle-employee-view']")
    ?.addEventListener("click", () => {
      state.employeePreview = !state.employeePreview;
      render();
    });
  root
    .querySelector("[data-action='filter']")
    .addEventListener("input", (event) => {
      state.filter = event.target.value.toLowerCase();
      render();
    });

  root.addEventListener("input", (event) => {
    const input = event.target;

    // Synchronize Company name to Project company field in New Org mode
    if (
      input.dataset?.doctype === "Company" &&
      input.dataset?.fieldname === "company_name"
    ) {
      const projectCompany = root.querySelector(
        "[data-doctype='Project'][data-fieldname='company']",
      );
      if (projectCompany) {
        projectCompany.value = input.value || "";
      }
    }

    const wrap = input.closest("[data-combobox-wrap]");
    if (wrap) {
      const query = input.value.toLowerCase().trim();
      const clearBtn = wrap.querySelector("[data-combobox-clear]");
      if (clearBtn) {
        clearBtn.style.display = input.value ? "flex" : "none";
      }

      wrap.classList.add("is-open");
      const items = wrap.querySelectorAll(".sarathi-combobox-item");
      let matchesCount = 0;
      items.forEach((item) => {
        const text = (
          item.dataset.label ||
          item.textContent ||
          ""
        ).toLowerCase();
        const matches = !query || text.includes(query);
        item.style.display = matches ? "flex" : "none";
        if (matches) matchesCount++;
      });
      let emptyMsg = wrap.querySelector(".sarathi-combobox-no-match");
      if (matchesCount === 0 && items.length > 0) {
        if (!emptyMsg) {
          emptyMsg = document.createElement("div");
          emptyMsg.className =
            "sarathi-combobox-empty sarathi-combobox-no-match";
          emptyMsg.textContent = "No matching records found";
          wrap.querySelector(".sarathi-combobox-list")?.appendChild(emptyMsg);
        }
        emptyMsg.style.display = "block";
      } else if (emptyMsg) {
        emptyMsg.style.display = "none";
      }
    }
  });

  root.addEventListener("focusin", (event) => {
    const wrap = event.target.closest("[data-combobox-wrap]");
    if (wrap) {
      document
        .querySelectorAll("[data-combobox-wrap].is-open")
        .forEach((el) => {
          if (el !== wrap) el.classList.remove("is-open");
        });
      wrap.classList.add("is-open");
    }
  });

  root.addEventListener("change", (event) => {
    const target = event.target;
    if (target.type === "checkbox") {
      const card = target.closest(".sarathi-check-card");
      if (card) {
        card.classList.toggle("checked", target.checked);
      }
    }

    const form = target.closest("[data-form='project-create']");
    if (form && target.name === "org_mode") {
      syncCreateProjectMode(form);
    }
    if (
      form &&
      target.closest("[data-existing-company]") &&
      target.name === "company"
    ) {
      syncCreateProjectMode(form);
    }
  });

  root.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      if (state.selectedBom) {
        closeBomDetail();
      }
      document
        .querySelectorAll("[data-combobox-wrap].is-open")
        .forEach((el) => el.classList.remove("is-open"));
    }
  });

  root.addEventListener("submit", (event) => {
    const form = event.target.closest("[data-form='project-create']");
    if (!form) return;
    event.preventDefault();
    continueToErpNextForm(form);
  });

  root.addEventListener("click", (event) => {
    const navLink = event.target.closest(".sarathi-nav a[href^='#']");
    if (navLink) {
      setActiveNav(navLink.getAttribute("href"));
    }

    const clearBtn = event.target.closest("[data-combobox-clear]");
    if (clearBtn) {
      event.stopPropagation();
      const wrap = clearBtn.closest("[data-combobox-wrap]");
      if (wrap) {
        const input = wrap.querySelector("input");
        if (input) {
          input.value = "";
          clearBtn.style.display = "none";
          wrap.querySelectorAll(".sarathi-combobox-item").forEach((item) => {
            item.style.display = "flex";
            item.classList.remove("selected");
          });
          const emptyMsg = wrap.querySelector(".sarathi-combobox-no-match");
          if (emptyMsg) emptyMsg.style.display = "none";
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
          input.focus();
        }
      }
      return;
    }

    const trigger = event.target.closest("[data-combobox-trigger]");
    if (trigger) {
      event.stopPropagation();
      const wrap = trigger.closest("[data-combobox-wrap]");
      if (wrap) {
        const isOpen = wrap.classList.contains("is-open");
        document
          .querySelectorAll("[data-combobox-wrap].is-open")
          .forEach((el) => el.classList.remove("is-open"));
        if (!isOpen) {
          wrap.classList.add("is-open");
          wrap.querySelector("input")?.focus();
        }
      }
      return;
    }

    const comboboxItem = event.target.closest(".sarathi-combobox-item");
    if (comboboxItem) {
      event.stopPropagation();
      const wrap = comboboxItem.closest("[data-combobox-wrap]");
      if (wrap) {
        const input = wrap.querySelector("input");
        if (input) {
          input.value = comboboxItem.dataset.value || "";
          const clearBtn = wrap.querySelector("[data-combobox-clear]");
          if (clearBtn) clearBtn.style.display = input.value ? "flex" : "none";
          wrap
            .querySelectorAll(".sarathi-combobox-item")
            .forEach((it) =>
              it.classList.toggle("selected", it === comboboxItem),
            );
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
        wrap.classList.remove("is-open");
      }
      return;
    }

    if (!event.target.closest("[data-combobox-wrap]")) {
      document
        .querySelectorAll("[data-combobox-wrap].is-open")
        .forEach((el) => el.classList.remove("is-open"));
    }

    const wrapperTab = event.target.closest("[data-wrapper-tab-button]");
    if (wrapperTab) {
      activateWrapperTab(wrapperTab);
      return;
    }

    if (event.target.closest("[data-action='close-drawer']")) {
      closeProcessDrawer();
      return;
    }

    const bomBackdrop = event.target.closest(
      "[data-section='bom-detail-panel']",
    );
    if (
      state.selectedBom &&
      bomBackdrop &&
      !event.target.closest(".sarathi-bom-window")
    ) {
      closeBomDetail();
      return;
    }

    if (event.target.closest("[data-action='close-bom-detail']")) {
      closeBomDetail();
      return;
    }

    const card = event.target.closest("[data-process-card]");
    if (card) {
      if (event.target.closest("a")) return;
      openProcessDrawer(card.dataset.processCard);
      return;
    }

    const bomCard = event.target.closest("[data-bom-card]");
    if (bomCard) {
      if (event.target.closest("a")) return;
      persistSelectedBom(bomCard.dataset.bomName || "");
      renderBomDetail(state.data?.data || {});
      return;
    }

    if (
      state.selectedBom &&
      !event.target.closest("[data-section='bom-detail-panel']")
    ) {
      closeBomDetail();
    }

    const projectCard = event.target.closest("[data-project-name]");
    if (projectCard) {
      const selectedProject = projectCard.dataset.projectName;
      if (selectedProject) {
        window.location.href = `/desk/sarathicontroltower?project=${encodeURIComponent(selectedProject)}`;
      }
      return;
    }

    const organizationCard = event.target.closest("[data-company-name]");
    if (organizationCard) {
      const selectedCompany = organizationCard.dataset.companyName;
      if (selectedCompany) {
        state.selectedCompany = selectedCompany;
        state.selectedProject = "";
        window.location.href = `/desk/sarathicontroltower?company=${encodeURIComponent(selectedCompany)}`;
      }
      return;
    }

    const stage = event.target.closest("[data-pipeline-stage]");
    if (stage) {
      openProcessDrawer(processKeyForStage(stage.dataset.pipelineStage));
      return;
    }

    const routeTarget = event.target.closest("[data-dashboard-route]");
    if (routeTarget && !event.target.closest("a, button, input")) {
      window.location.href = routeTarget.dataset.dashboardRoute;
      return;
    }

    const section = event.target.closest("[data-section-panel]");
    if (
      section &&
      !event.target.closest(
        "a, button, input, table, [data-process-card], [data-pipeline-stage]",
      )
    ) {
      openSectionPanel(section.dataset.sectionPanel);
    }
  });

  root.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document
        .querySelectorAll("[data-combobox-wrap].is-open")
        .forEach((el) => el.classList.remove("is-open"));
    }
    const card = event.target.closest("[data-process-card]");
    const bomCard = event.target.closest("[data-bom-card]");
    const stage = event.target.closest("[data-pipeline-stage]");
    const routeTarget = event.target.closest("[data-dashboard-route]");
    if (
      (!card && !bomCard && !stage && !routeTarget) ||
      (event.key !== "Enter" && event.key !== " ")
    )
      return;
    event.preventDefault();
    if (card) {
      openProcessDrawer(card.dataset.processCard);
    } else if (bomCard) {
      persistSelectedBom(bomCard.dataset.bomName || "");
      renderBomDetail(state.data?.data || {});
    } else if (stage) {
      openProcessDrawer(processKeyForStage(stage.dataset.pipelineStage));
    } else if (routeTarget) {
      window.location.href = routeTarget.dataset.dashboardRoute;
    }
  });

  root.querySelectorAll("[data-tab-target]").forEach((button) => {
    button.addEventListener("click", () => {
      root
        .querySelectorAll("[data-tab-target]")
        .forEach((node) => node.classList.remove("active"));
      root
        .querySelectorAll("[data-tab]")
        .forEach((node) => node.classList.remove("active"));
      button.classList.add("active");
      root
        .querySelector(`[data-tab='${button.dataset.tabTarget}']`)
        ?.classList.add("active");
    });
  });

  window.addEventListener("hashchange", () =>
    setActiveNav(window.location.hash || "#projects"),
  );
  setActiveNav(window.location.hash || "#projects");
  load();
  setInterval(load, 30000);
})();
