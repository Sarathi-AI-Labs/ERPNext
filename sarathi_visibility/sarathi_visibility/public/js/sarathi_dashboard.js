frappe.SarathiIndustrialDashboard = class {
  constructor(wrapper) {
    this.page = frappe.ui.make_app_page({parent: wrapper, title: "Sarathi Industrial Dashboard", single_column: true});
    this.root = $(frappe.render_template("sarathicontroltower", {})).appendTo(this.page.main)[0];
    this.filters = {}; this.sequence = 0; this.detailSequence = 0; this.tab = "overview";
    this.search = ""; this.customerPage = this.projectPage = 0;
    this.tabs = {overview: "Overview", sales: "Sales", production: "Production", engineering: "Engineering & BOM", materials: "Materials & Stock", procurement: "Procurement", quality: "Quality & Rework", fulfillment: "Delivery & Billing", reports: "Reports", integrations: "Integrations"};
    this.tabReports = {sales: ["orders", "order_items"], procurement: ["requests", "purchases", "receipts", "purchase_invoices", "procurement_exceptions"], quality: ["quality", "job_cards", "job_logs", "job_suboperations"], fulfillment: ["deliveries", "sales_invoices"], production: ["part_production", "live_activity", "production_summary", "operation_balance", "work_orders", "job_cards", "workstations", "tasks"], engineering: ["tracking_setup", "boms", "components", "operations"], materials: ["material_history", "stock_details", "stock_ledger", "reservations", "wip_stock", "materials", "stock", "finished"], integrations: ["integrations"]};
    this.root.addEventListener("click", e => this.click(e));
    this.root.addEventListener("change", e => { if (e.target.dataset.filter) this.filterChanged(e.target); });
    this.el("[data-search]").addEventListener("input", e => { this.search = e.target.value.toLowerCase(); this.customerPage = this.projectPage = 0; this.renderCards(); });
    window.addEventListener("popstate", () => { if (this.visible) { this.readUrl(); this.load(); } });
    document.addEventListener("visibilitychange", () => { if (!document.hidden && this.visible) this.load(true); });
    frappe.realtime?.on("sarathi_dashboard_changed", () => { if (this.visible) this.load(true); });
    this.show();
  }
  el(s) { return this.root.querySelector(s); }
  esc(v) { return frappe.utils.escape_html(String(v ?? "")); }
  num(v) { return Number(v || 0).toLocaleString(undefined, {maximumFractionDigits: 2}); }
  link(dt, name, label) { return name ? `<a href="/desk/${String(dt).toLowerCase().replaceAll(" ", "-")}/${encodeURIComponent(name)}">${this.esc(label || name)}</a>` : "—"; }
  empty(text = "No linked records for this selection.") { return `<div class="sd-empty">${this.esc(text)}</div>`; }
  statusColor(text) {
    const v = String(text || "").toLowerCase();
    return /cancel|reject|shortage/.test(v) ? "red" : /closure|pending closure/.test(v) ? "violet" : /on hold|stopped|delayed|overdue/.test(v) ? "orange" : /not started|pending|unassigned/.test(v) ? "amber" : /in progress|work in progress|running|active/.test(v) ? "blue" : /completed|finished|current/.test(v) ? "green" : "violet";
  }
  badge(text) { return `<span class="sd-pill sd-status-${this.statusColor(text)}">${this.esc(text)}</span>`; }
  async call(method, args) { const r = await frappe.call({method: `sarathi_visibility.api.dashboard.${method}`, args, silent: true}); return r.message; }
  readUrl() {
    const q = new URLSearchParams(location.search);
    for (const k of ["company", "customer", "project", "from_date", "to_date", "status"]) this.filters[k] = q.get(k) || "";
    this.tab = this.tabs[q.get("tab")] ? q.get("tab") : "overview";
  }
  writeUrl(replace = false) {
    const url = new URL(location.href); url.search = "";
    for (const [k, v] of Object.entries(this.filters)) if (v) url.searchParams.set(k, v);
    if (this.tab !== "overview") url.searchParams.set("tab", this.tab);
    history[replace ? "replaceState" : "pushState"]({}, "", url);
  }
  show() { if (this.visible) return; this.visible = true; this.readUrl(); this.load(); this.timer = setInterval(() => { if (!document.hidden) this.load(true); }, 30000); }
  hide() { this.visible = false; clearInterval(this.timer); this.sequence++; this.detailSequence++; }
  navigate(change) {
    Object.assign(this.filters, change); this.search = ""; this.el("[data-search]").value = "";
    this.customerPage = this.projectPage = 0; this.tab = "overview"; this.reportState = null;
    this.writeUrl(); this.load();
  }
  filterChanged(node) { const change = {[node.dataset.filter]: node.value}; if (node.dataset.filter === "company") Object.assign(change, {customer: "", project: ""}); this.navigate(change); }
  async load(silent = false) {
    const request = ++this.sequence;
    this.root.setAttribute("aria-busy", "true");
    if (!silent) this.el("[data-updated]").textContent = "Loading records…";
    try {
      const data = await this.call("get_summary", {filters: JSON.stringify(this.filters)});
      if (request !== this.sequence || !this.visible) return;
      this.data = data; this.filters = data.filters; this.writeUrl(true);
      this.el("[data-error]").hidden = true; this.render(silent);
      this.el("[data-updated]").textContent = `Updated ${frappe.datetime.str_to_user(data.generated_at)}`;
    } catch (e) {
      if (request !== this.sequence) return;
      this.el("[data-error]").hidden = false;
      this.el("[data-error]").textContent = "Unable to load this selection. Check access and filter values, then click Refresh. Previous results may be out of date.";
      this.el("[data-updated]").textContent = "Refresh failed";
    } finally { if (request === this.sequence) this.root.setAttribute("aria-busy", "false"); }
  }
  render(silent) {
    const d = this.data;
    this.el('[data-filter="company"]').innerHTML = `<option value="">All organizations</option>` + d.companies.map(c => `<option value="${this.esc(c.name)}">${this.esc(c.company_name || c.name)}</option>`).join("");
    for (const n of this.root.querySelectorAll("[data-filter]")) n.value = this.filters[n.dataset.filter];
    const customer = d.customers.find(c => c.name === this.filters.customer);
    const name = customer?.customer_name || (this.filters.customer === "__unassigned__" ? "Unassigned customer" : this.filters.customer);
    this.el("[data-breadcrumb]").innerHTML = `<button data-nav="organization">${this.esc(this.filters.company || "All organizations")}</button>` + (this.filters.customer ? `<span>/</span><button data-nav="customer">${this.esc(name)}</button>` : "") + (this.filters.project ? `<span>/</span><strong>${this.esc(d.selected_project?.project_name || this.filters.project)}</strong>` : "");
    this.el("[data-permissions]").hidden = !d.restricted.length;
    this.el("[data-permissions]").textContent = `Some data is unavailable for your role: ${d.restricted.join(", ")}. Totals include only records you may read.`;
    this.el("[data-live-projects]").innerHTML = this.liveCards();
    this.el("[data-kpis]").innerHTML = d.kpis.map((k, i) => `<button class="sd-kpi sd-tone-${i % 6}" data-kpi-label="${this.esc(k.label)}" data-report="${k.report}" data-subset="${k.subset || ""}"><span>${this.esc(k.label)}</span><strong>${typeof k.value === "number" ? this.num(k.value) : this.esc(k.value)}</strong><small>View records ↗</small></button>`).join("");
    this.el("[data-customer-panel]").hidden = !!this.filters.customer || !!this.filters.project;
    this.el("[data-project-panel]").hidden = !!this.filters.project;
    this.el("[data-project-heading]").textContent = this.filters.customer ? `${name} projects` : "Organization projects";
    this.el('[data-action="associate"]').hidden = !d.can_create["Sarathi Customer Organization"] || !this.filters.company;
    this.el("[data-project-summary]").hidden = !this.filters.project;
    if (this.filters.project) {
      const p = d.selected_project;
      this.el("[data-project-summary]").innerHTML = p ? `<div><small>${this.esc(p.name)} · ${this.esc(name)}</small><h2>${this.esc(p.project_name)}</h2><p>${this.badge(p.status)} ${p.delayed ? this.badge("Delayed") : ""} Main BOM: ${this.link("BOM", p.custom_sarathi_bom)} · ${this.link("Project", p.name, "Open Project / assign links")}</p></div><button class="sd-button" data-nav="customer">← Back to customer projects</button>` : this.empty("This project does not match the selected status filter.");
    }
    this.renderCards(); this.renderTabs();
    if (silent && this.tab !== "overview" && this.el("[data-table-area]")) {
      this.loadReport();
      if (this.el("[data-tab-charts]")) this.el("[data-tab-charts]").innerHTML = this.chartGrid(this.chartsForTab());
    } else this.renderContent();
  }
  pagination(kind, page, total) { return total > 12 ? `<div class="sd-pagination"><button class="sd-button" data-page="${kind}" data-index="${page - 1}" ${!page ? "disabled" : ""}>Previous</button><span>${page * 12 + 1}–${Math.min(total, (page + 1) * 12)} of ${total}</span><button class="sd-button" data-page="${kind}" data-index="${page + 1}" ${(page + 1) * 12 >= total ? "disabled" : ""}>Next</button></div>` : ""; }
  renderCards() {
    if (!this.data) return;
    const matches = r => Object.values(r).join(" ").toLowerCase().includes(this.search);
    const customers = this.data.customers.filter(matches), projects = this.data.projects.filter(matches);
    this.el("[data-customers]").innerHTML = customers.slice(this.customerPage * 12, (this.customerPage + 1) * 12).map(c => `<button class="sd-card" data-customer="${this.esc(c.name)}"><span class="sd-card-icon">${this.esc(c.customer_name.slice(0, 2).toUpperCase())}</span><h3>${this.esc(c.customer_name)}</h3><div>${this.badge(`${c.project_count} projects`)} ${c.delayed ? this.badge(`${c.delayed} delayed`) : ""}</div><p>${c.active} active · ${c.open_orders} open orders</p><small>${c.project_count ? "View customer →" : "No projects yet →"}</small></button>`).join("") || this.empty("No customers linked yet. Create a customer or link an existing customer to this organization.");
    this.el("[data-projects]").innerHTML = projects.slice(this.projectPage * 12, (this.projectPage + 1) * 12).map(p => `<button class="sd-card" data-project="${this.esc(p.name)}" data-project-status="${this.esc(p.status)}"><small>${this.esc(p.name)}</small><h3>${this.esc(p.project_name)}</h3><p>${this.esc(p.customer_name)}</p><div>${this.badge(p.status)} ${p.delayed ? this.badge("Delayed") : ""}</div><div class="sd-progress"><i style="width:${Math.max(0, Math.min(100, Number(p.percent_complete || 0)))}%"></i></div><p>${this.num(p.percent_complete)}% project progress · ${p.work_order_count} WOs</p><small>${p.custom_sarathi_bom ? this.esc(p.custom_sarathi_bom) : "Main BOM pending"}</small></button>`).join("") || this.empty("No projects match this selection.");
    this.el("[data-project-count]").textContent = `${projects.length} projects`;
    this.el("[data-customer-pagination]").innerHTML = this.pagination("customer", this.customerPage, customers.length);
    this.el("[data-project-pagination]").innerHTML = this.pagination("project", this.projectPage, projects.length);
  }
  renderTabs() { this.el(".sd-tabs").innerHTML = Object.entries(this.tabs).map(([k, label]) => `<button role="tab" aria-selected="${this.tab === k}" class="${this.tab === k ? "active" : ""}" data-tab="${k}">${label}</button>`).join(""); }
  chart(c) {
    const colors = ["#2563eb", "#0d9488", "#8b5cf6", "#e39a14", "#e05286", "#ea7041"], labels = c.labels || [], series = c.datasets;
    if (!labels.length) return this.empty("No data for this chart in the current selection.");
    const max = Math.max(1, ...series.flatMap(s => s.values).map(Math.abs));
    const legend = series.map((s, i) => `<span><i style="background:${colors[i % colors.length]}"></i>${this.esc(s.name)}</span>`).join("");
    if (c.type === "donut") {
      const statusPalette = {blue: "#2563eb", green: "#059669", violet: "#8b5cf6", orange: "#ea7041", amber: "#e39a14", red: "#dc4263"};
      const sliceColors = c.report === "projects" || c.report === "production_summary" ? labels.map(l => statusPalette[this.statusColor(l)]) : labels.map((_, i) => colors[i % colors.length]);
      const values = series[0].values, total = values.reduce((a, b) => a + b, 0); let offset = 0;
      const gradient = values.map((v, i) => { const start = offset; offset += total ? v / total * 100 : 0; return `${sliceColors[i]} ${start}% ${offset}%`; }).join(",");
      return `<div class="sd-donut-wrap"><div class="sd-donut" style="background:conic-gradient(${gradient})" role="img" aria-label="${this.esc(labels.map((l, i) => `${l}: ${values[i]}`).join(', '))}"><span>${total}<small>${this.esc(series[0].name)}</small></span></div><div class="sd-chart-legend">${labels.map((l, i) => `<span><i style="background:${sliceColors[i]}"></i>${this.esc(l)} <b>${values[i]}</b></span>`).join("")}</div></div>`;
    }
    if (c.type === "line" && labels.length > 1) {
      const points = series[0].values.map((v, i) => `${25 + i * 450 / (labels.length - 1)},${150 - v / max * 120}`).join(" ");
      return `<svg class="sd-line-chart" viewBox="0 0 500 185" role="img" aria-label="${this.esc(labels.map((l, i) => `${l}: ${series[0].values[i]}`).join(', '))}"><path d="M25 20V150H480" fill="none" stroke="#dbe4ec"/><polyline points="${points}" fill="none" stroke="#2563eb" stroke-width="3"/>${series[0].values.map((v, i) => `<circle cx="${25 + i * 450 / (labels.length - 1)}" cy="${150 - v / max * 120}" r="4" fill="#2563eb"><title>${this.esc(labels[i])}: ${this.num(v)}</title></circle>`).join("")}<text x="25" y="175">${this.esc(labels[0])}</text><text x="410" y="175">${this.esc(labels.at(-1))}</text></svg><div class="sd-chart-legend">${legend}</div>`;
    }
    return `<div class="sd-chart-legend">${legend}</div><div class="sd-bars">${labels.map((label, i) => `<div class="sd-bar-row"><span title="${this.esc(label)}">${this.esc(label)}</span><div>${series.map((s, n) => `<div class="sd-bar-track"><i style="width:${Math.abs(Number(s.values[i] || 0)) / max * 100}%;background:${s.values[i] < 0 ? '#cf7551' : colors[n % colors.length]}"></i><b>${this.num(s.values[i])}</b></div>`).join("")}</div></div>`).join("")}</div>`;
  }
  liveCards() {
    const groups = ["In progress", "Not started", "Completed", "On hold / Stopped", "Production finished · Closure pending", "Cancelled"];
    const summaries = this.data.production_summary;
    const number = v => v === null || v === undefined ? "—" : this.num(v);
    return groups.map(state => {
      const projects = summaries.filter(p => p.live_status === state);
      if (!projects.length && state !== "In progress") return "";
      return `<section class="sd-panel sd-live-group" data-live-state="${this.esc(state)}"><div class="sd-panel-heading"><div><h2>${this.esc(state)} projects <span class="sd-pill">${projects.length}</span></h2>${state === "In progress" ? "<p>Current recorded Job Card activity · Completed projects are shown separately</p>" : ""}</div><button class="sd-text-button" data-report="${state === "Completed" || state === "Cancelled" ? "projects" : "production_summary"}" data-subset="${({"In progress":"in_progress", "Not started":"not_started", "Completed":"completed", "On hold / Stopped":"paused", "Production finished · Closure pending":"closure_pending"})[state] || ""}">View report ↗</button></div><div class="sd-cards">${projects.map(p => `<article class="sd-live-card" data-live-project="${this.esc(p.project)}"><div class="sd-panel-heading"><strong>${this.esc(p.project_name)}</strong>${this.badge(p.live_status)}</div><small>${this.esc(p.project)} · ${this.esc(p.customer || "Unassigned customer")}</small>${p.running_operations.length ? p.running_operations.map(r => `<div class="sd-running-operation"><strong>● Running now: ${this.esc(r.operation)}</strong><p>${this.link("Workstation", r.workstation)} · ${this.link("Job Card", r.job_card)}</p><p>Job Card: Planned ${number(r.planned)} · Completed ${number(r.completed)} · Remaining ${number(r.remaining)} ${this.esc(r.unit || "")}</p><small>Started ${this.esc(frappe.datetime.str_to_user(r.started_at))}</small></div>`).join("") : `<p>${this.esc(p.activity_message)}</p>`}<p class="sd-scope-note">${p.last_activity ? `Last recorded activity: ${this.esc(frappe.datetime.str_to_user(p.last_activity))}` : this.esc(p.note)}</p><button class="sd-button" data-project="${this.esc(p.project)}">Open project analysis ↗</button></article>`).join("") || this.empty("No projects currently in progress in this selection.")}</div></section>`;
    }).join("") + '<p class="sd-scope-note">Running now means an open ERPNext Job Card time log. Operators must record start/stop activity; this is not independent machine telemetry.</p>';
  }
  pipelineOverview() {
    const selected = !!this.filters.project;
    const steps = {requests:"Material requests", purchases:"Purchase orders", receipts:"Purchase receipts", work_orders:"Work Orders", inspections:"Inspections", deliveries:"Delivery notes", sales_invoices:"Sales invoices"};
    const cards = this.data.pipeline_summary.map(p => `<article class="sd-pipeline-project"><strong>${this.esc(p.project)}</strong><div class="sd-pipeline-steps">${Object.entries(steps).map(([key,label]) => `<button class="sd-pipeline-step ${p[key] === null ? 'sd-step-restricted' : p[key] ? 'sd-step-recorded' : ''}" data-report-project="${this.esc(p.project)}" data-report="${key === 'inspections' ? 'quality' : key}"><small>${label}</small><strong>${p[key] === null ? 'Access restricted' : p[key]}</strong><span>${p[key] === null ? 'Read access required' : p[key] ? 'Recorded documents' : 'No submitted records'}</span></button>`).join('')}</div></article>`).join('');
    const setup = this.data.tracking_setup.map(p => `<div class="sd-alert"><span>${this.esc(p.project)} · ${this.esc(p.validation)} · ${this.esc(p.physical_parts)}</span>${this.link('Project',p.project,'Open setup')}${p.main_bom ? this.link('BOM',p.main_bom,'Open main BOM') : ''}</div>`).join('');
    return `<section class="sd-panel"><div class="sd-panel-heading"><div><h2>${selected ? 'Project working pipeline' : 'Project pipelines'}</h2><p>Lifetime records · Steps can run in parallel · Counts are documents, not part quantities</p></div></div>${cards || this.empty()}<div class="sd-production-links"><button class="sd-button" data-report="part_production">Recorded cutting / welding / grinding outputs</button><button class="sd-button" data-report="material_history">Lifetime materials</button><button class="sd-button" data-report="tracking_setup">Part tracking setup</button></div><details class="sd-setup-details"><summary>Project attribution & physical part setup</summary>${setup}</details>${this.data.procurement_exception_count ? `<div class="sd-alert"><span>${this.data.procurement_exception_count} procurement item rows have missing or conflicting project links.</span><button class="sd-text-button" data-report="procurement_exceptions">Review records ↗</button></div>` : ''}</section>`;
  }
  projectHealth() {
    const entries = this.data.project_health || [];
    const selected = !!this.filters.project;
    const visible = selected ? entries : entries.filter(p => !["Completed", "Cancelled"].includes(p.live_status));
    const metric = (project, label, value, report) => `<button class="sd-health-metric" data-report="${report}" data-report-project="${this.esc(project)}"><strong>${value == null ? "—" : this.num(value)}</strong><span>${label}</span></button>`;
    return `<section class="sd-panel sd-health"><div class="sd-panel-heading"><div><h2>${selected ? "Project health at a glance" : "Open project health"}</h2><p>Current recorded operation, next outstanding step, materials, quality and fulfilment · lifetime project records</p></div></div>${visible.map(p => `<article class="sd-health-project"><div class="sd-health-head"><div><strong>${this.esc(p.project)}</strong> ${this.badge(p.live_status)}</div>${p.last_activity ? `<small>Last recorded activity ${this.esc(frappe.datetime.str_to_user(p.last_activity))}</small>` : `<small>No recorded production activity</small>`}</div><div class="sd-health-work"><div><small>Working now</small><strong>${p.current_operations.length ? p.current_operations.map(op => this.esc(op.operation || "Operation unnamed")).join(", ") : "No Job Card time log open"}</strong>${p.current_operations.length ? `<small>${p.current_operations.map(op => this.esc(op.workstation || "Workstation unassigned")).join(" · ")}</small>` : ""}</div><div><small>Next outstanding operation</small><strong>${p.next_operation ? `${this.esc(p.next_operation.operation || "Operation unnamed")} · ${this.link("Work Order", p.next_operation.work_order)}` : "No outstanding recorded operation"}</strong>${p.next_operation ? `<small>${this.num(p.next_operation.remaining)} ${this.esc(p.next_operation.unit || "units")} remaining · ${this.esc(p.next_operation.workstation || "Workstation unassigned")}</small>` : ""}</div></div><div class="sd-health-metrics">${metric(p.project, "Operations finished", p.operations_finished, "operation_balance")}${metric(p.project, "Operations total", p.operations_total, "operation_balance")}${metric(p.project, "Material shortages", p.material_shortages, "materials")}${metric(p.project, "Purchase orders", p.purchase_orders, "purchases")}${metric(p.project, "Receipts", p.receipts, "receipts")}${metric(p.project, "Quality passed", p.inspection_passed, "quality")}${metric(p.project, "Quality rejected", p.inspection_rejected, "quality")}${metric(p.project, "Delivery notes", p.deliveries, "deliveries")}${metric(p.project, "Sales invoices", p.sales_invoices, "sales_invoices")}</div>${p.material_shortages === null && !selected ? `<p class="sd-scope-note">Select this project for its material readiness; warehouse availability is scoped to the project’s Work Orders.</p>` : ""}<button class="sd-text-button" data-project="${this.esc(p.project)}">Open project analysis ↗</button></article>`).join("") || this.empty("No open projects in this selection. Select a completed project to see its full health summary.")}<p class="sd-scope-note">An open Job Card time log is recorded activity, not proof of machine telemetry. A blank metric means read access or stock availability is unavailable. Inspection counts are submitted results, not part quantities.</p></section>`;
  }
  productionOverview() {
    const selected = !!this.filters.project;
    const summaries = this.data.production_summary.filter(p => selected || p.live_status === "In progress");
    const number = v => v === null || v === undefined ? "—" : this.num(v);
    const rows = ops => `<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${["Operation", "Work Order", "Workstation", "Output item / unit", "Planned", "Completed", "Process loss", "Remaining", "Status"].map(x => `<th>${x}</th>`).join("")}</tr></thead><tbody>${ops.map(r => `<tr><td>${this.esc(r.sequence)} · ${this.esc(r.operation)}</td><td>${this.link("Work Order", r.work_order)}<small class="sd-operation-note">${this.esc(r.work_order_status)}</small></td><td>${this.link("Workstation", r.workstation)}</td><td>${this.link("Item", r.item)}<small class="sd-operation-note">${this.esc(r.unit || "Unit unavailable")}</small></td><td>${number(r.planned)}</td><td>${number(r.completed)}</td><td>${number(r.process_loss)}</td><td>${number(r.remaining)}</td><td>${this.badge(r.status)}</td></tr>`).join("")}</tbody></table></div>`;
    return `<section class="sd-panel sd-production-overview"><div class="sd-panel-heading"><div><h2>${selected ? "Project operation progress" : "In progress projects · operation progress"} <span class="sd-pill">${summaries.length}</span></h2><p>Lifetime submitted Work Orders · In progress = recorded production started · Quantities are Work Order output units, not physical warehouse balances</p></div><button class="sd-text-button" data-report="operation_balance" data-subset="${selected ? "" : "in_progress"}">Full operation report ↗</button></div>${summaries.map(p => { const ops = this.data.operation_balance.filter(r => r.project === p.project); return `<details class="sd-production-project" data-production-project="${this.esc(p.project)}" ${selected ? "open" : ""}><summary><span><strong>${this.esc(p.project_name)}</strong><small>${this.esc(p.project)} · ${this.esc(p.customer || "Unassigned customer")}</small></span>${this.badge(p.production_status)}<span>${p.finished_operations}/${p.operations} operations finished</span></summary><div class="sd-production-body"><p>${this.esc(p.note)} · ${p.work_orders} submitted Work Orders · Semi-finished stock tracking: ${this.esc(p.stock_tracking)} <button class="sd-text-button" data-project="${this.esc(p.project)}">Open project analysis ↗</button></p>${ops.length ? rows(ops) : this.empty("No recorded Work Order operations. Create a linked BOM / Work Order with operations to track production.")}</div></details>`; }).join("") || this.empty("No projects in progress in this selection.")}<div class="sd-production-links"><button class="sd-button" data-report="production_summary">All project production summaries</button><button class="sd-button" data-report="projects" data-subset="completed">Completed projects</button><button class="sd-button" data-report="wip_stock">Semi-finished warehouse stock</button></div><p class="sd-scope-note">Remaining = planned − completed − process loss, minimum zero. Cutting/welding/grinding are separate operations; their quantities must not be added as unique finished parts. Warehouse stock requires configured semi-finished items and posted stock movements.</p></section>`;
  }
  renderContent() {
    const content = this.el("[data-content]"); this.root.dataset.currentTab = this.tab; const expanded = new Set(Array.from(content.querySelectorAll("[data-production-project][open]")).map(x => x.dataset.productionProject)); this.detailSequence++;
    if (this.tab === "overview") {
      this.reportState = null;
      content.innerHTML = `${this.projectHealth()}${this.pipelineOverview()}${this.productionOverview()}${this.chartGrid(this.chartsForTab())}<section class="sd-panel"><div class="sd-panel-heading"><h2>Alerts & data quality <span class="sd-pill">${this.data.alert_count}</span></h2><button class="sd-text-button" data-report="issues">View all</button></div>${this.data.alerts.map(a => `<div class="sd-alert">${this.link(a.doctype, a.name)}<span>${this.esc(a.issue)}</span></div>`).join("") || this.empty("No exceptions found in the selected records.")}</section>`;
      content.querySelectorAll("[data-production-project]").forEach(x => { if (expanded.has(x.dataset.productionProject)) x.open = true; });
      return;
    }
    const choices = this.tab === "reports" ? this.data.reports.map(r => r.key) : this.tabReports[this.tab];
    if (!this.reportState || !choices.includes(this.reportState.report)) this.reportState = {report: choices[0], subset: "", search: "", start: 0};
    const r = this.reportState;
    content.innerHTML = `<section class="sd-panel"><div class="sd-report-toolbar"><label>Report<select data-report-select>${choices.map(k => `<option value="${k}" ${r.report === k ? "selected" : ""}>${this.esc(this.data.reports.find(x => x.key === k).title)}</option>`).join("")}</select></label><label>Search report<input data-report-search type="search" value="${this.esc(r.search)}" placeholder="Search all matching rows"></label><button class="sd-button" data-action="export">Export CSV</button><button class="sd-button" data-action="native-report">Open ERPNext report ↗</button></div><p class="sd-scope-note">${r.subset ? `Filtered to ${this.esc(r.subset)} records. ` : ""}Totals cover every matching record. Pipeline, material history, part outputs, purchasing and fulfilment reports use lifetime records. Invoice outstanding is a whole-document amount and must not be summed across item rows. Returns retain signed quantities. Inspection sample size is not a rejected-part count. Document status: 0 Draft · 1 Submitted · 2 Cancelled. ${this.tab === "materials" ? "Semi-finished stock requires enabled tracking, operation output Items and target warehouses. Stock is shared availability; requirements come from open submitted Work Orders. Blank stock means unavailable or no source warehouse." : ""}</p><div data-table-area role="status">Loading report…</div></section>`;
    content.insertAdjacentHTML("afterbegin", `<div data-tab-charts>${this.chartGrid(this.chartsForTab())}</div>`);
    this.el("[data-report-select]").addEventListener("change", e => { this.reportState = {report: e.target.value, subset: "", search: "", start: 0}; this.renderContent(); });
    this.el("[data-report-search]").addEventListener("input", e => { this.reportState.search = e.target.value; this.reportState.start = 0; clearTimeout(this.searchTimer); this.searchTimer = setTimeout(() => this.loadReport(), 300); });
    this.loadReport();
  }
  chartsForTab() {
    const reports = {overview: ["projects", "deadlines", "operation_balance", "production_summary"], sales: ["orders"], production: ["part_production", "work_orders", "job_cards", "finished", "operation_balance"], procurement: ["purchases"], materials: ["materials"]}[this.tab] || [];
    return this.data.charts.filter(c => c.title.startsWith("Manufacturing pipeline") ? this.tab === "overview" : reports.includes(c.report));
  }
  chartGrid(charts) {
    return charts.length ? `<div class="sd-chart-grid">${charts.map(c => `<article class="sd-panel" data-chart-report="${this.esc(c.report)}"><div class="sd-panel-heading"><h2>${this.esc(c.title)}</h2><button class="sd-text-button" data-report="${c.report}" data-subset="${c.subset || ""}">View records ↗</button></div>${this.chart(c)}</article>`).join("")}</div>` : "";
  }
  cell(c, row) {
    const value = row[c.fieldname]; if (value === null || value === undefined || value === "") return "—";
    if (c.fieldtype === "Link") return this.link(c.options, value) + (c.fieldname === "name" ? ` <button class="sd-inspect" data-inspect="${this.esc(value)}" data-doctype="${this.esc(c.options)}" aria-label="Inspect ${this.esc(value)}">Details</button>` : "");
    if (c.fieldtype === "Dynamic Link") return this.link(row[c.options], value);
    if (["Float", "Int", "Currency", "Percent"].includes(c.fieldtype)) return this.num(value) + (c.fieldtype === "Percent" ? "%" : "");
    return this.esc(value);
  }
  async loadReport() {
    const version = ++this.detailSequence, state = {...this.reportState};
    try {
      const r = await this.call("get_report", {filters: JSON.stringify(this.filters), ...state, page_length: 25});
      if (version !== this.detailSequence || !this.el("[data-table-area]")) return;
      this.el("[data-table-area]").innerHTML = (r.rows.length ? `<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${r.columns.map(c => `<th>${this.esc(c.label)}</th>`).join("")}</tr></thead><tbody>${r.rows.map(row => `<tr>${r.columns.map(c => `<td>${this.cell(c, row)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>` : this.empty()) + `<div class="sd-pagination"><button class="sd-button" data-report-page="${Math.max(0, r.start - 25)}" ${!r.start ? "disabled" : ""}>Previous</button><span>${r.total ? r.start + 1 : 0}–${Math.min(r.total, r.start + 25)} of ${r.total}</span><button class="sd-button" data-report-page="${r.start + 25}" ${r.start + 25 >= r.total ? "disabled" : ""}>Next</button></div>`;
    } catch (e) { if (version === this.detailSequence && this.el("[data-table-area]")) this.el("[data-table-area]").innerHTML = this.empty("Report could not load. Check your access and click Refresh."); }
  }
  openReport(report, subset = "") { this.tab = "reports"; this.reportState = {report, subset, search: "", start: 0}; this.writeUrl(); this.renderTabs(); this.renderContent(); this.el(".sd-tabs").scrollIntoView({behavior: "smooth", block: "start"}); }
  click(event) {
    const b = event.target.closest("button"); if (!b || b.disabled) return; const d = b.dataset;
    if (d.inspect) this.inspect(d.doctype, d.inspect);
    else if (d.customer) this.navigate({customer: d.customer, project: ""});
    else if (d.project) this.navigate({project: d.project});
    else if (d.nav) this.navigate(d.nav === "organization" ? {customer: "", project: ""} : {project: ""});
    else if (d.tab) { this.tab = d.tab; this.reportState = null; this.writeUrl(); this.renderTabs(); this.renderContent(); }
    else if (d.report) { if (d.reportProject && d.reportProject !== this.filters.project) this.navigate({project:d.reportProject,customer:""}); this.openReport(d.report, d.subset); }
    else if (d.page) { this[`${d.page}Page`] = Number(d.index); this.renderCards(); }
    else if (d.reportPage !== undefined) { this.reportState.start = Number(d.reportPage); this.loadReport(); }
    else if (d.action === "refresh") this.load();
    else if (d.action === "create" || d.action === "setup") this.creationMenu(d.action === "setup");
    else if (d.action === "associate") this.create("Sarathi Customer Organization");
    else if (d.action === "native-report") { frappe.route_options = {...this.filters, customer: this.filters.customer === "__unassigned__" ? "" : this.filters.customer, unassigned_customer: this.filters.customer === "__unassigned__" ? 1 : 0, report_type: this.data.reports.find(r => r.key === this.reportState.report).title, subset: this.reportState.subset, search: this.reportState.search}; frappe.set_route("query-report", "Sarathi Industrial Analysis"); }
    else if (d.action === "export") { const q = new URLSearchParams({filters: JSON.stringify(this.filters), ...this.reportState}); window.open(`/api/method/sarathi_visibility.api.dashboard.export_report?${q}`, "_blank", "noopener"); }
  }
  async inspect(doctype, name) {
    const dialog = new frappe.ui.Dialog({title: `${doctype} · ${name}`, size: "extra-large", fields: [{fieldname: "detail", fieldtype: "HTML"}], primary_action_label: "Open in ERPNext", primary_action: () => { dialog.hide(); frappe.set_route("Form", doctype, name); }});
    dialog.fields_dict.detail.$wrapper.html(this.empty("Loading linked records…")); dialog.$wrapper.addClass("sd-dashboard-dialog"); dialog.show();
    try {
      const data = await this.call("get_record", {filters: JSON.stringify(this.filters), doctype, name});
      const table = (columns, rows) => `<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${columns.map(c => `<th>${this.esc(c.label)}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${columns.map(c => `<td>${this.cell({...c, fieldname: c.fieldname}, r).replace(/ <button.*?<\/button>/g, "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
      dialog.fields_dict.detail.$wrapper.html(`<div class="sd-detail"><div class="sd-detail-fields">${data.columns.map(c => `<div><small>${this.esc(c.label)}</small><strong>${this.cell(c, data.row).replace(/ <button.*?<\/button>/g, "")}</strong></div>`).join("")}</div>${data.related.map(r => `<h4>${this.esc(r.title)} (${r.total})</h4>${r.total ? table(r.columns, r.rows) : this.empty()}${r.total > 100 ? '<p>First 100 records. Open the full report for all records.</p>' : ''}`).join("")}</div>`);
    } catch (e) { dialog.fields_dict.detail.$wrapper.html(this.empty("Unable to open this record in the current selection.")); }
  }
  creationMenu(setup) {
    if (!this.data) return;
    const types = setup ? ["Company", "Item", "Warehouse", "Operation", "Workstation Type", "Workstation", "Plant Floor", "Routing", "Supplier"] : ["Customer", "Project", "BOM", "Sales Order", "Production Plan", "Material Request", "Work Order", "Pick List", "Stock Entry", "Job Card", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Delivery Note", "Sales Invoice"];
    const dialog = new frappe.ui.Dialog({title: setup ? "Organization setup" : "Create in this selection", fields: [{fieldname: "actions", fieldtype: "HTML"}]});
    dialog.fields_dict.actions.$wrapper.html(`<p>${this.esc(this.filters.company || "Choose an organization for linked records")}</p><div class="sd-create-grid">${types.filter(dt => this.data.can_create[dt]).map(dt => `<button class="sd-button" data-new="${dt}">${dt}</button>`).join("")}</div>`);
    dialog.fields_dict.actions.$wrapper.on("click", "[data-new]", e => { dialog.hide(); this.create(e.currentTarget.dataset.new); }); dialog.$wrapper.addClass("sd-dashboard-dialog"); dialog.show();
  }
  create(doctype) {
    const f = this.filters, p = this.data?.selected_project;
    if (["Customer", "Project", "Sarathi Customer Organization"].includes(doctype) && !f.company) return frappe.msgprint("Choose an organization first.");
    if (doctype === "Project" && (!f.customer || f.customer === "__unassigned__")) return frappe.msgprint("Choose a customer before creating a manufacturing project.");
    if (["BOM", "Sales Order", "Work Order", "Material Request", "Stock Entry", "Pick List", "Job Card", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Delivery Note", "Sales Invoice"].includes(doctype) && !f.project) return frappe.msgprint("Choose a project first so the new record is linked correctly.");
    if (["Job Card", "Stock Entry", "Pick List"].includes(doctype)) { frappe.msgprint(`Open the project's Work Order to create a linked ${doctype} using ERPNext's workflow.`); this.openReport("work_orders"); return; }
    const values = {company: f.company};
    if (f.customer && f.customer !== "__unassigned__") values.customer = f.customer;
    if (doctype === "Project") values.custom_sarathi_manufacturing = 1;
    else if (doctype === "BOM") values.custom_sarathi_project = f.project;
    else if (["Sales Order", "Work Order", "Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Delivery Note", "Sales Invoice"].includes(doctype)) values.project = f.project;
    if (doctype === "Work Order") { if (!p?.custom_sarathi_bom) return frappe.msgprint("Assign an active, submitted main BOM on the Project first."); values.bom_no = p.custom_sarathi_bom; values.production_item = p.main_item; values.sales_order = p.sales_order; }
    if (doctype === "Customer") values.customer_type = "Company";
    frappe.model.with_doctype(doctype, () => {
      const fields = new Set(frappe.get_meta(doctype).fields.map(x => x.fieldname));
      const defaults = Object.fromEntries(Object.entries(values).filter(([k, v]) => fields.has(k) && v !== "" && v != null));
      // Use the full native form so relation validation and after-save linking always run.
      frappe.route_options = defaults;
      const doc = frappe.model.get_new_doc(doctype);
      Object.assign(doc, defaults);
      if (doctype === 'Material Request') sessionStorage.setItem('sarathi_material_request_project', JSON.stringify({docname:doc.name,project:f.project}));
      if (doctype === "Customer") sessionStorage.setItem("sarathi_new_customer_company", JSON.stringify({company: f.company, docname: doc.name}));
      frappe.set_route("Form", doctype, doc.name);
    });
  }
};
