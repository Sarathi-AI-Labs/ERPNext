frappe.SarathiIndustrialDashboard = class {
	workspaceIcon(label = "") {
		const text = String(label).toLowerCase();
		const shapes = [
			[
				/customer|supplier|share|people/,
				'<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 4v2"/>',
			],
			[
				/stock|material|warehouse|inventory|item/,
				'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 9 9-4M12 12 3 8m9 4v10M7 5.8l9 5"/>',
			],
			[
				/manufactur|production|operation|work order|workstation|job card|subcontract/,
				'<path d="M3 21V10l6 3V8l6 3V3h5v18H3Zm4-4h1m4 0h1m4 0h1"/>',
			],
			[
				/bank|company|tax|account.*setup/,
				'<path d="m3 8 9-5 9 5H3Zm0 13h18M5 11v7m5-7v7m4-7v7m5-7v7"/>',
			],
			[
				/payment|cash|capital|budget|profit|revenue|expense/,
				'<rect x="3" y="5" width="18" height="15" rx="3"/><path d="M3 10h18m-6 5h3M7 3v2"/>',
			],
			[/quality|approval|verified/, '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6"/>'],
			[
				/report|overview|home|analytics|intelligence/,
				'<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 16v-4m5 4V7m5 9v-6"/>',
			],
			[
				/setting|integration|engineering|bom|routing/,
				'<path d="m14 4 1-2 3 2-1 2 2 3 3 1v4l-3 1-2 3 1 2-3 2-1-2h-4l-1 2-3-2 1-2-2-3-3-1v-4l3-1 2-3-1-2 3-2 1 2h4Z"/><circle cx="12" cy="12" r="3"/>',
			],
			[
				/delivery|transport/,
				'<path d="M3 5h11v12H3V5Zm11 5h4l3 4v3h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
			],
			[/project|cost center/, '<path d="M3 7V5h7l2 3h9v12H3V7Z"/><path d="M7 13h10m-10 3h6"/>'],
		];
		const shape =
			shapes.find(([pattern]) => pattern.test(text))?.[1] ||
			'<path d="M6 3h9l4 4v14H6V3Zm9 0v5h4M9 12h7m-7 4h7"/>';
		return `<svg class="sarathi-ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${shape}</svg>`;
	}

	constructor(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: "Sarathi Industrial Dashboard",
			single_column: true,
		});
		this.root = $(frappe.render_template("sarathicontroltower", {})).appendTo(this.page.main)[0];
		this.filters = {};
		this.dateFilters = { from_date: "", to_date: "" };
		this.sequence = 0;
		this.detailSequence = 0;
		this.tab = "overview";
		this.view = "";
		this.subFilters = {
			cost_granularity: "monthly",
			company: "",
			supplier: "",
			project: "",
			status: "",
			from_date: "",
			to_date: "",
		};
		this.subData = null;
		this.subSearch = "";
		this.subOrdersPage = 0;
		this.subMaterialsPage = 0;
		this.subSelectedStage = "";
		this.subSelectedStatus = "";
		this.accFilters = {
			period: "this_month",
			company: "",
			project: "",
			customer: "",
			supplier: "",
			cost_center: "",
			account: "",
			from_date: "",
			to_date: "",
		};
		this.accData = null;
		this.accSearch = "";
		this.accTab = "overview";
		this.accActiveKpi = "";
		this.search = "";
		this.customerPage = this.projectPage = 0;
		this.customerViewMode = "table";
		this.projectViewMode = "table";
		this.tabs = {
			overview: "Overview",
			sales: "Sales",
			production: "Production",
			engineering: "Engineering & BOM",
			materials: "Materials & Stock",
			procurement: "Procurement",
			quality: "Quality & Rework",
			fulfillment: "Delivery & Billing",
			reports: "Reports",
			integrations: "Integrations",
		};
		this.tabReports = {
			sales: ["customers", "orders", "order_items"],
			procurement: [
				"suppliers",
				"requests",
				"purchases",
				"receipts",
				"purchase_invoices",
				"procurement_exceptions",
			],
			quality: ["quality", "job_cards", "job_logs", "job_suboperations"],
			fulfillment: ["deliveries", "sales_invoices"],
			production: [
				"workstations",
				"workstation_types",
				"plant_floors",
				"part_production",
				"live_activity",
				"production_summary",
				"operation_balance",
				"work_orders",
				"job_cards",
				"tasks",
			],
			engineering: [
				"tracking_setup",
				"boms",
				"components",
				"operations_catalogue",
				"operations",
				"routings",
			],
			materials: [
				"items",
				"inventory",
				"warehouses",
				"material_history",
				"stock_details",
				"stock_ledger",
				"reservations",
				"wip_stock",
				"materials",
				"stock",
				"finished",
			],
			integrations: ["integrations"],
		};

		this.root.addEventListener("click", (e) => this.click(e));
		this.root.addEventListener("change", (e) => {
			if (e.target.dataset.filter) this.filterChanged(e.target);
			if (e.target.dataset.dateFilter) {
				this.dateFilters[e.target.dataset.dateFilter] = e.target.value;
			}
			if (e.target.dataset.subFilter) this.subFilterChanged(e.target);
			if (e.target.dataset.accFilter) this.accFilterChanged(e.target);
		});
		this.root.addEventListener("input", (e) => {
			if (e.target.dataset.dateFilter) {
				this.dateFilters[e.target.dataset.dateFilter] = e.target.value;
			}
			if (e.target.dataset.tableSearch) {
				this.filterTable(e.target.dataset.tableSearch);
			}
		});
		this.root.addEventListener("keydown", (e) => {
			if (e.target.dataset.dateFilter && e.key === "Enter") {
				e.preventDefault();
				this.applyDateFilter();
			}
		});
		this.el("[data-search]").addEventListener("input", (e) => {
			this.search = e.target.value.toLowerCase();
			this.customerPage = this.projectPage = 0;
			this.renderCards();
		});
		this.initAiAssistant();
		window.addEventListener("popstate", () => {
			if (this.visible) {
				const oldView = this.view;
				this.readUrl();
				if (this.view === oldView && (this.view === "accounting" || this.view === "subcontracting")) {
					return;
				}
				this.load();
			}
		});
		window.addEventListener("focus", () => {
			if (
				this.visible &&
				(!document.activeElement ||
					!["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName))
			) {
				if (this.view === "accounting") {
					this.loadAccountingData(true);
				} else if (this.view === "subcontracting") {
					this.loadSubcontractingData(true);
				} else {
					this.load(true);
				}
			}
		});
		document.addEventListener("visibilitychange", () => {
			if (!document.hidden && this.visible) {
				if (this.view === "accounting") {
					this.loadAccountingData(true);
				} else if (this.view === "subcontracting") {
					this.loadSubcontractingData(true);
				} else {
					this.load(true);
				}
			}
		});

		const onRealtimeChange = () => {
			if (!this.visible) return;
			clearTimeout(this._rtDebounce);
			this._rtDebounce = setTimeout(() => {
				if (this.view === "accounting") {
					this.loadAccountingData(true);
				} else if (this.view === "subcontracting") {
					this.loadSubcontractingData(true);
				} else {
					this.load(true);
				}
			}, 1500);
		};
		const setupRealtime = () => {
			if (frappe.realtime) {
				frappe.realtime.off("sarathi_dashboard_changed", onRealtimeChange);
				frappe.realtime.on("sarathi_dashboard_changed", onRealtimeChange);
			}
			if (frappe.realtime?.socket) {
				frappe.realtime.socket.off("sarathi_dashboard_changed", onRealtimeChange);
				frappe.realtime.socket.on("sarathi_dashboard_changed", onRealtimeChange);
				frappe.realtime.socket.off("connect", setupRealtime);
				frappe.realtime.socket.on("connect", setupRealtime);
			}
		};
		setupRealtime();
		this.rtInterval = setInterval(() => {
			if (frappe.realtime?.socket) {
				setupRealtime();
				clearInterval(this.rtInterval);
			}
		}, 1000);
		this.show();
		this.root?.querySelector(".scm-launcher")?.remove();
		if (this.root && typeof $ !== "undefined") {
			$(this.root).find(".scm-launcher").remove();
		}
		frappe.require(
			[
				"/assets/sarathi_owner/css/sarathi_module_browser.css",
				"/assets/sarathi_owner/js/sarathi_module_browser.js",
			],
			() => {
				this.root?.querySelector(".scm-launcher")?.remove();
				if (this.root && typeof $ !== "undefined") {
					$(this.root).find(".scm-launcher").remove();
				}
				this.moduleBrowser ||= new frappe.SarathiModuleBrowser(this, "industrial");
			}
		);
	}
	el(s) {
		return this.root.querySelector(s);
	}
	esc(v) {
		return frappe.utils.escape_html(String(v ?? ""));
	}
	num(v) {
		return Number(v || 0).toLocaleString(undefined, {
			maximumFractionDigits: 2,
		});
	}
	link(dt, name, label) {
		return name
			? `<a href="javascript:void(0)" class="sd-record-link" data-inspect="${this.esc(
					name
			  )}" data-doctype="${this.esc(dt)}" title="View ${this.esc(dt)} details">${this.esc(
					label || name
			  )}</a>`
			: "—";
	}
	empty(text = "No linked records for this selection.") {
		return `<div class="sd-empty">${this.esc(text)}</div>`;
	}
	statusColor(text) {
		const v = String(text || "").toLowerCase();
		return /cancel|reject|shortage/.test(v)
			? "red"
			: /closure|pending closure/.test(v)
			? "violet"
			: /on hold|stopped|delayed|overdue/.test(v)
			? "orange"
			: /not started|pending|unassigned/.test(v)
			? "amber"
			: /in progress|work in progress|running|active/.test(v)
			? "blue"
			: /completed|finished|current/.test(v)
			? "green"
			: "violet";
	}
	badge(text) {
		return `<span class="sd-pill sd-status-${this.statusColor(text)}">${this.esc(text)}</span>`;
	}
	async call(method, args) {
		const r = await frappe.call({
			method: `sarathi_visibility.api.dashboard.${method}`,
			args,
			silent: true,
		});
		return r.message;
	}
	readUrl() {
		const q = new URLSearchParams(location.search);
		for (const k of ["company", "customer", "project", "from_date", "to_date", "status"])
			this.filters[k] = q.get(k) || "";
		this.dateFilters = {
			from_date: this.filters.from_date || "",
			to_date: this.filters.to_date || "",
		};
		this.tab = this.tabs[q.get("tab")] ? q.get("tab") : "overview";
		this.view = q.get("view") || "";
	}
	writeUrl(replace = false) {
		const url = new URL(location.href);
		url.search = "";
		for (const [k, v] of Object.entries(this.filters)) if (v) url.searchParams.set(k, v);
		if (this.tab !== "overview") url.searchParams.set("tab", this.tab);
		if (this.view) url.searchParams.set("view", this.view);
		if (url.search === location.search) {
			return;
		}
		history[replace ? "replaceState" : "pushState"]({}, "", url);
	}
	show() {
		if (this.visible) return;
		this.visible = true;
		this.root?.querySelector(".scm-launcher")?.remove();
		if (this.root && typeof $ !== "undefined") {
			$(this.root).find(".scm-launcher").remove();
		}
		this.readUrl();
		if (this.view === "accounting") {
			this.showAccountingView();
		} else if (this.view === "subcontracting") {
			this.showSubcontractingView();
		} else {
			this.load();
		}
		this.timer = setInterval(() => {
			if (!document.hidden && this.visible) {
				if (this.view === "accounting") {
					this.loadAccountingData(true);
				} else if (this.view === "subcontracting") {
					this.loadSubcontractingData(true);
				} else {
					this.load(true);
				}
			}
		}, 15000);
	}
	hide() {
		this.visible = false;
		clearInterval(this.timer);
		clearInterval(this.rtInterval);
		this.sequence++;
		this.detailSequence++;
	}
	navigate(change) {
		Object.assign(this.filters, change);
		if ("from_date" in change) {
			this.dateFilters.from_date = change.from_date || "";
		}
		if ("to_date" in change) {
			this.dateFilters.to_date = change.to_date || "";
		}
		this.search = "";
		this.el("[data-search]").value = "";
		this.customerPage = this.projectPage = 0;
		this.tab = "overview";
		this.reportState = null;
		this.writeUrl();
		this.load();
	}
	filterChanged(node) {
		const change = { [node.dataset.filter]: node.value };
		if (node.dataset.filter === "company") Object.assign(change, { customer: "", project: "" });
		this.navigate(change);
	}
	applyDateFilter() {
		const from = this.dateFilters?.from_date || this.el('[data-date-filter="from_date"]')?.value || "";
		const to = this.dateFilters?.to_date || this.el('[data-date-filter="to_date"]')?.value || "";
		if (!from || !to) {
			frappe.msgprint(__("Please select both From date and To date."));
			return;
		}
		if (from > to) {
			frappe.msgprint(__("From date must be on or before To date."));
			return;
		}
		this.navigate({ from_date: from, to_date: to });
	}
	clearDateFilter() {
		this.dateFilters = { from_date: "", to_date: "" };
		const fromEl = this.el('[data-date-filter="from_date"]');
		const toEl = this.el('[data-date-filter="to_date"]');
		if (fromEl) fromEl.value = "";
		if (toEl) toEl.value = "";
		this.navigate({ from_date: "", to_date: "" });
	}
	async load(silent = false) {
		if (this.view === "accounting") {
			return this.loadAccountingData(silent);
		}
		if (this.view === "subcontracting") {
			return this.loadSubcontractingData(silent);
		}
		const request = ++this.sequence;
		this.root.setAttribute("aria-busy", "true");
		if (!silent) this.el("[data-updated]").textContent = "Loading records…";
		try {
			const data = await this.call("get_summary", {
				filters: JSON.stringify(this.filters),
			});
			if (request !== this.sequence || !this.visible) return;
			this.data = data;
			this.filters = data.filters;
			this.writeUrl(true);
			this.el("[data-error]").hidden = true;
			this.render(silent);
			this.el("[data-updated]").textContent = `Updated ${frappe.datetime.str_to_user(
				data.generated_at
			)}`;
		} catch (e) {
			if (request !== this.sequence) return;
			this.el("[data-error]").hidden = false;
			this.el("[data-error]").textContent =
				"Unable to load this selection. Check access and filter values, then click Refresh. Previous results may be out of date.";
			this.el("[data-updated]").textContent = "Refresh failed";
		} finally {
			if (request === this.sequence) this.root.setAttribute("aria-busy", "false");
		}
	}
	render(silent) {
		const d = this.data;
		this.renderSubcontractingCard();
		this.renderAccountingCard();
		if (this.view === "subcontracting") {
			const accEl = this.el("[data-accounting-view]");
			if (accEl) accEl.hidden = true;
			const viewEl = this.el("[data-subcontracting-view]");
			if (!viewEl || viewEl.hidden) {
				this.showSubcontractingView(silent);
			} else if (silent && !this.subData) {
				this.loadSubcontractingData(true);
			}
			return;
		} else if (this.view === "accounting") {
			const subEl = this.el("[data-subcontracting-view]");
			if (subEl) subEl.hidden = true;
			const viewEl = this.el("[data-accounting-view]");
			if (!viewEl || viewEl.hidden) {
				this.showAccountingView(silent);
			} else if (silent && !this.accData) {
				this.loadAccountingData(true);
			}
			return;
		} else {
			const subEl = this.el("[data-subcontracting-view]");
			if (subEl) subEl.hidden = true;
			const accEl = this.el("[data-accounting-view]");
			if (accEl) accEl.hidden = true;
		}
		this.el('[data-filter="company"]').innerHTML =
			`<option value="">All organizations</option>` +
			d.companies
				.map(
					(c) =>
						`<option value="${this.esc(c.name)}">${this.esc(c.company_name || c.name)}</option>`
				)
				.join("");
		for (const n of this.root.querySelectorAll("[data-filter]"))
			n.value = this.filters[n.dataset.filter] || "";
		for (const n of this.root.querySelectorAll("[data-date-filter]")) {
			const field = n.dataset.dateFilter;
			const targetVal =
				this.dateFilters?.[field] !== undefined && this.dateFilters[field] !== ""
					? this.dateFilters[field]
					: this.filters[field] || "";
			if (document.activeElement !== n && n.value !== targetVal) {
				n.value = targetVal;
			}
		}
		const customer = d.customers.find((c) => c.name === this.filters.customer);
		const name =
			customer?.customer_name ||
			(this.filters.customer === "__unassigned__" ? "Unassigned customer" : this.filters.customer);
		this.el("[data-breadcrumb]").innerHTML =
			`<button data-nav="organization">${this.esc(
				this.filters.company || "All organizations"
			)}</button>` +
			(this.filters.customer
				? `<span>/</span><button data-nav="customer">${this.esc(name)}</button>`
				: "") +
			(this.filters.project
				? `<span>/</span><strong>${this.esc(
						d.selected_project?.project_name || this.filters.project
				  )}</strong>`
				: "");
		this.el("[data-permissions]").hidden = !d.restricted.length;
		this.el(
			"[data-permissions]"
		).textContent = `Some data is unavailable for your role: ${d.restricted.join(
			", "
		)}. Totals include only records you may read.`;
		this.el("[data-live-projects]").innerHTML = this.liveCards();
		this.el("[data-kpis]").innerHTML = d.kpis
			.map((k, i) => {
				const isDate = typeof k.value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(k.value);
				const isText =
					isDate || (typeof k.value === "string" && (k.value.length > 3 || isNaN(k.value)));
				const formatted = typeof k.value === "number" ? this.num(k.value) : this.esc(k.value);
				return `<button class="sd-kpi sd-tone-${i % 6}" data-kpi-label="${this.esc(
					k.label
				)}" data-report="${k.report}" data-subset="${
					k.subset || ""
				}"><span class="sd-metric-label">${this.workspaceIcon(k.label)}${this.esc(
					k.label
				)}</span><strong class="${
					isText ? "sd-kpi-val-text" : ""
				}">${formatted}</strong><small>View records ↗</small></button>`;
			})
			.join("");
		this.el("[data-customer-panel]").hidden = !!this.filters.customer || !!this.filters.project;
		this.el("[data-project-panel]").hidden = !!this.filters.project;
		this.el("[data-project-heading]").textContent = this.filters.customer
			? `${name} projects`
			: "Organization projects";
		this.el('[data-action="associate"]').hidden =
			!d.can_create["Sarathi Customer Organization"] || !this.filters.company;
		this.el("[data-project-summary]").hidden = !this.filters.project;
		if (this.filters.project) {
			const p = d.selected_project;
			const getKpi = (key) => d.kpis.find((k) => k.report === key)?.value ?? 0;
			this.el("[data-project-summary]").innerHTML = p
				? `
        <div class="sd-project-summary-box">
          <div class="sd-project-summary-info">
            <small>${this.esc(p.name)} · ${this.esc(name)}</small>
            <h2>${this.esc(p.project_name)}</h2>
            <p>${this.badge(p.status)} ${p.delayed ? this.badge("Delayed") : ""} Main BOM: ${this.link(
						"BOM",
						p.custom_sarathi_bom
				  )} · ${this.link("Project", p.name, "Open Project / assign links")}</p>
          </div>
          <div class="sd-project-quick-links">
            <button class="sd-button sd-tone-blue" data-report="warehouses">🏢 Warehouses (${this.num(
				getKpi("warehouses")
			)})</button>
            <button class="sd-button sd-tone-teal" data-report="operations_catalogue">⚙️ Operations (${this.num(
				getKpi("operations_catalogue")
			)})</button>
            <button class="sd-button sd-tone-violet" data-report="workstations">🏭 Workstations (${this.num(
				getKpi("workstations")
			)})</button>
            <button class="sd-button sd-tone-amber" data-report="workstation_types">🏷️ Workstation Types (${this.num(
				getKpi("workstation_types")
			)})</button>
            <button class="sd-button sd-tone-pink" data-report="routings">🔄 Routings (${this.num(
				getKpi("routings")
			)})</button>
            <button class="sd-button sd-tone-orange" data-report="items">📦 Items (${this.num(
				getKpi("items")
			)})</button>
          </div>
          <button class="sd-button" data-nav="customer">← Back to customer projects</button>
        </div>`
				: this.empty("This project does not match the selected status filter.");
		}
		this.renderCards();
		this.renderTabs();
		if (silent && this.tab !== "overview" && this.el("[data-table-area]")) {
			this.loadReport();
			if (this.el("[data-tab-charts]"))
				this.el("[data-tab-charts]").innerHTML = this.chartGrid(this.chartsForTab());
		} else this.renderContent();
	}
	pagination(kind, page, total) {
		return total > 12
			? `<div class="sd-pagination"><button class="sd-button" data-page="${kind}" data-index="${
					page - 1
			  }" ${!page ? "disabled" : ""}>Previous</button><span>${page * 12 + 1}–${Math.min(
					total,
					(page + 1) * 12
			  )} of ${total}</span><button class="sd-button" data-page="${kind}" data-index="${page + 1}" ${
					(page + 1) * 12 >= total ? "disabled" : ""
			  }>Next</button></div>`
			: "";
	}
	renderCustomerTable(customers) {
		const perPage = this.customerViewMode === "table" ? 10 : 12;
		const pageItems = customers.slice(this.customerPage * perPage, (this.customerPage + 1) * perPage);
		if (!pageItems.length) {
			return this.empty(
				"No customers linked yet. Create a customer or link an existing customer to this organization."
			);
		}
		return `
		<div class="sd-table-web-toolbar">
			<div class="sd-table-search-wrap">
				<svg class="sd-table-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
				<input type="text" class="sd-table-search-input" data-table-search="customers" placeholder="Search customers..." autocomplete="off" spellcheck="false" aria-label="Search customers">
			</div>
			<div class="sd-table-filter-pills" data-table-filters="customers">
				<button type="button" class="sd-filter-pill active" data-table-filter="all">All (${customers.length})</button>
				<button type="button" class="sd-filter-pill" data-table-filter="active">Active Ops</button>
				<button type="button" class="sd-filter-pill" data-table-filter="orders">Open Orders</button>
				<button type="button" class="sd-filter-pill" data-table-filter="delayed">Delayed</button>
			</div>
			<div class="sd-table-count-badge">
				<span class="sd-pill sd-tone-blue"><strong data-table-count="customers">${
					pageItems.length
				}</strong> records</span>
			</div>
		</div>
		<div class="sd-color-table-wrapper">
			<table class="sd-color-table" data-table-id="customers" aria-label="Customers Table">
				<thead>
					<tr class="sd-color-table-header-row">
						<th class="sd-th-pin sd-th-purple">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏢</span>
								<span class="sd-pin-text">Customer / Organization</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-blue">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🛡️</span>
								<span class="sd-pin-text">Projects Total</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-azure">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⭐</span>
								<span class="sd-pin-text">Active Ops</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-teal">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">👍</span>
								<span class="sd-pin-text">Open Orders</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-forest">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⏱️</span>
								<span class="sd-pin-text">Delivery Track</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-lime">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">💎</span>
								<span class="sd-pin-text">System Health</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-olive">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏷️</span>
								<span class="sd-pin-text">Direct Action</span>
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					${pageItems
						.map((c, i) => {
							const isEven = i % 2 === 0;
							const initials = (c.customer_name || c.name || "CU").slice(0, 2).toUpperCase();
							return `
						<tr class="sd-color-tr ${isEven ? "sd-tr-even" : "sd-tr-odd"}" data-customer="${this.esc(
								c.name
							)}" data-active="${c.active > 0 ? "yes" : "no"}" data-orders="${
								c.open_orders > 0 ? "yes" : "no"
							}" data-delayed="${c.delayed > 0 ? "yes" : "no"}" role="button" tabindex="0">
							<td class="sd-td-ribbon">
								<div class="sd-row-ribbon sd-ribbon-purple">
									<div class="sd-ribbon-box">
										<span class="sd-ribbon-initials">${this.esc(initials)}</span>
									</div>
									<div class="sd-ribbon-content">
										<strong class="sd-ribbon-name" title="${this.esc(c.customer_name)}">${this.esc(c.customer_name)}</strong>
										<span class="sd-ribbon-sub">${this.esc(c.name)}</span>
									</div>
									<div class="sd-ribbon-chevron"></div>
								</div>
							</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-blue">
									<strong>${c.project_count}</strong> ${c.project_count === 1 ? "Project" : "Projects"}
								</span>
							</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-azure">
									<span class="sd-dot-pulse ${c.active > 0 ? "live-green" : "live-gray"}"></span>
									<strong>${c.active}</strong> Active
								</span>
							</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-teal">
									<span class="sd-order-icon">📦</span>
									<strong>${c.open_orders}</strong> Orders
								</span>
							</td>
							<td class="sd-td-cell">
								${
									c.delayed > 0
										? `<span class="sd-status-tag sd-tag-delayed"><span class="sd-tag-icon">✕</span> ${c.delayed} Delayed</span>`
										: `<span class="sd-status-tag sd-tag-ontrack"><span class="sd-tag-icon">✓</span> On Track</span>`
								}
							</td>
							<td class="sd-td-cell">
								<div class="sd-traffic-capsule" title="${
									c.delayed > 0
										? "Requires attention (" + c.delayed + " delayed)"
										: "Healthy operational flow"
								}">
									<span class="sd-cap-dot ${c.delayed === 0 ? "dot-green-active" : ""}"></span>
									<span class="sd-cap-dot ${c.delayed === 1 ? "dot-amber-active" : ""}"></span>
									<span class="sd-cap-dot ${c.delayed > 1 ? "dot-red-active" : ""}"></span>
								</div>
							</td>
							<td class="sd-td-cell sd-td-action">
								<button type="button" class="sd-row-action-btn" data-customer="${this.esc(c.name)}">
									Focus Customer ➔
								</button>
							</td>
						</tr>
						`;
						})
						.join("")}
				</tbody>
			</table>
		</div>
		`;
	}

	renderProjectTable(projects) {
		const perPage = this.projectViewMode === "table" ? 10 : 12;
		const pageItems = projects.slice(this.projectPage * perPage, (this.projectPage + 1) * perPage);
		if (!pageItems.length) {
			return this.empty("No projects match this selection.");
		}
		return `
		<div class="sd-table-web-toolbar">
			<div class="sd-table-search-wrap">
				<svg class="sd-table-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
				<input type="text" class="sd-table-search-input" data-table-search="projects" placeholder="Search projects..." autocomplete="off" spellcheck="false" aria-label="Search projects">
			</div>
			<div class="sd-table-filter-pills" data-table-filters="projects">
				<button type="button" class="sd-filter-pill active" data-table-filter="all">All (${projects.length})</button>
				<button type="button" class="sd-filter-pill" data-table-filter="in_progress">In Progress</button>
				<button type="button" class="sd-filter-pill" data-table-filter="completed">Completed</button>
				<button type="button" class="sd-filter-pill" data-table-filter="delayed">Delayed</button>
			</div>
			<div class="sd-table-count-badge">
				<span class="sd-pill sd-tone-blue"><strong data-table-count="projects">${
					pageItems.length
				}</strong> records</span>
			</div>
		</div>
		<div class="sd-color-table-wrapper">
			<table class="sd-color-table" data-table-id="projects" aria-label="Projects Table">
				<thead>
					<tr class="sd-color-table-header-row">
						<th class="sd-th-pin sd-th-purple">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">📦</span>
								<span class="sd-pin-text">Project & ID</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-blue">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🛡️</span>
								<span class="sd-pin-text">Customer Entity</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-azure">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⭐</span>
								<span class="sd-pin-text">Lifecycle Status</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-teal">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">👍</span>
								<span class="sd-pin-text">Progress Completion</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-forest">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⏱️</span>
								<span class="sd-pin-text">Timeline Health</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-lime">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">💎</span>
								<span class="sd-pin-text">Main BOM</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-olive">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏷️</span>
								<span class="sd-pin-text">Project Action</span>
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					${pageItems
						.map((p, i) => {
							const isEven = i % 2 === 0;
							const pct = Math.max(0, Math.min(100, Number(p.percent_complete || 0)));
							const statusSlug = (p.status || "").toLowerCase().replace(/[^a-z0-9]/g, "-");
							return `
						<tr class="sd-color-tr ${isEven ? "sd-tr-even" : "sd-tr-odd"}" data-project="${this.esc(
								p.name
							)}" data-project-status="${this.esc(p.status)}" data-delayed="${
								p.delayed ? "yes" : "no"
							}" role="button" tabindex="0">
							<td class="sd-td-ribbon">
								<div class="sd-row-ribbon sd-ribbon-purple">
									<div class="sd-ribbon-box">
										<span class="sd-ribbon-symbol">⚙</span>
									</div>
									<div class="sd-ribbon-content">
										<strong class="sd-ribbon-name" title="${this.esc(p.project_name)}">${this.esc(p.project_name)}</strong>
										<span class="sd-ribbon-sub">${this.esc(p.name)}</span>
									</div>
									<div class="sd-ribbon-chevron"></div>
								</div>
							</td>
							<td class="sd-td-cell">
								<span class="sd-customer-chip" title="${this.esc(p.customer_name)}">
									<span class="sd-chip-icon">🏢</span>
									<strong>${this.esc(p.customer_name || "Unassigned")}</strong>
								</span>
							</td>
							<td class="sd-td-cell">
								<span class="sd-status-pill sd-pill-${statusSlug}">
									${this.esc(p.status || "Open")}
								</span>
							</td>
							<td class="sd-td-cell sd-td-progress">
								<div class="sd-table-progress-box">
									<div class="sd-table-progress-bar">
										<div class="sd-table-progress-fill" style="width: ${pct}%;"></div>
									</div>
									<div class="sd-table-progress-meta">
										<span class="sd-prog-pct">${this.num(p.percent_complete)}%</span>
										<span class="sd-prog-wo">${p.work_order_count || 0} WOs</span>
									</div>
								</div>
							</td>
							<td class="sd-td-cell">
								<div class="sd-traffic-capsule" title="${p.delayed ? "Project Delayed" : "Project On Track"}">
									<span class="sd-cap-dot ${!p.delayed ? "dot-green-active" : ""}"></span>
									<span class="sd-cap-dot ${p.delayed ? "dot-amber-active" : ""}"></span>
									<span class="sd-cap-dot ${p.status === "Cancelled" ? "dot-red-active" : ""}"></span>
								</div>
								<span class="sd-sub-track ${p.delayed ? "track-delayed" : "track-ontrack"}">
									${p.delayed ? "Delayed" : "On Track"}
								</span>
							</td>
							<td class="sd-td-cell">
								<span class="sd-bom-badge ${p.custom_sarathi_bom ? "has-bom" : "no-bom"}" title="${this.esc(
								p.custom_sarathi_bom || ""
							)}">
									${p.custom_sarathi_bom ? "✓ " + this.esc(p.custom_sarathi_bom) : "Main BOM pending"}
								</span>
							</td>
							<td class="sd-td-cell sd-td-action">
								<button type="button" class="sd-row-action-btn" data-project="${this.esc(p.name)}">
									Inspect Project ➔
								</button>
							</td>
						</tr>
						`;
						})
						.join("")}
				</tbody>
			</table>
		</div>
		`;
	}

	updateViewToggleButtons() {
		this.root.querySelectorAll("[data-action='toggle-customer-view']").forEach((btn) => {
			btn.classList.toggle("active", btn.dataset.mode === this.customerViewMode);
		});
		this.root.querySelectorAll("[data-action='toggle-project-view']").forEach((btn) => {
			btn.classList.toggle("active", btn.dataset.mode === this.projectViewMode);
		});
	}

	renderCards() {
		if (!this.data) return;
		const matches = (r) => Object.values(r).join(" ").toLowerCase().includes(this.search);
		const customers = this.data.customers.filter(matches),
			projects = this.data.projects.filter(matches);
		const custPerPage = this.customerViewMode === "table" ? 10 : 12;
		const projPerPage = this.projectViewMode === "table" ? 10 : 12;

		if (this.customerViewMode === "cards") {
			this.el("[data-customers]").innerHTML =
				`<div class="sd-cards">${customers
					.slice(this.customerPage * custPerPage, (this.customerPage + 1) * custPerPage)
					.map(
						(c) =>
							`<button class="sd-card" data-customer="${this.esc(
								c.name
							)}"><span class="sd-card-icon">${this.esc(
								c.customer_name.slice(0, 2).toUpperCase()
							)}</span><h3>${this.esc(c.customer_name)}</h3><div>${this.badge(
								`${c.project_count} projects`
							)} ${c.delayed ? this.badge(`${c.delayed} delayed`) : ""}</div><p>${
								c.active
							} active · ${c.open_orders} open orders</p><small>${
								c.project_count ? "View customer →" : "No projects yet →"
							}</small></button>`
					)
					.join("")}</div>` ||
				this.empty(
					"No customers linked yet. Create a customer or link an existing customer to this organization."
				);
		} else {
			this.el("[data-customers]").innerHTML = this.renderCustomerTable(customers);
		}

		if (this.projectViewMode === "cards") {
			this.el("[data-projects]").innerHTML =
				`<div class="sd-cards">${projects
					.slice(this.projectPage * projPerPage, (this.projectPage + 1) * projPerPage)
					.map(
						(p) =>
							`<button class="sd-card" data-project="${this.esc(
								p.name
							)}" data-project-status="${this.esc(p.status)}"><small>${this.esc(
								p.name
							)}</small><h3>${this.esc(p.project_name)}</h3><p>${this.esc(
								p.customer_name
							)}</p><div>${this.badge(p.status)} ${
								p.delayed ? this.badge("Delayed") : ""
							}</div><div class="sd-progress"><i style="width:${Math.max(
								0,
								Math.min(100, Number(p.percent_complete || 0))
							)}%"></i></div><p>${this.num(p.percent_complete)}% project progress · ${
								p.work_order_count
							} WOs</p><small>${
								p.custom_sarathi_bom ? this.esc(p.custom_sarathi_bom) : "Main BOM pending"
							}</small></button>`
					)
					.join("")}</div>` || this.empty("No projects match this selection.");
		} else {
			this.el("[data-projects]").innerHTML = this.renderProjectTable(projects);
		}

		this.el("[data-project-count]").textContent = `${projects.length} projects`;
		this.el("[data-customer-pagination]").innerHTML = this.pagination(
			"customer",
			this.customerPage,
			customers.length
		);
		this.el("[data-project-pagination]").innerHTML = this.pagination(
			"project",
			this.projectPage,
			projects.length
		);
		this.updateViewToggleButtons();
	}
	renderTabs() {
		this.el(".sd-tabs").innerHTML = Object.entries(this.tabs)
			.map(
				([k, label]) =>
					`<button role="tab" aria-selected="${this.tab === k}" class="${
						this.tab === k ? "active" : ""
					}" data-tab="${k}">${this.workspaceIcon(label)}<span>${label}</span></button>`
			)
			.join("");
	}
	chart(c) {
		const colors = ["#2563eb", "#0d9488", "#8b5cf6", "#e39a14", "#e05286", "#ea7041"],
			labels = c.labels || [],
			series = c.datasets;
		if (!labels.length) return this.empty("No data for this chart in the current selection.");
		const max = Math.max(1, ...series.flatMap((s) => s.values).map(Math.abs));
		const legend = series
			.map(
				(s, i) =>
					`<span><i style="background:${colors[i % colors.length]}"></i>${this.esc(s.name)}</span>`
			)
			.join("");
		if (c.type === "donut") {
			const statusPalette = {
				blue: "#2563eb",
				green: "#059669",
				violet: "#8b5cf6",
				orange: "#ea7041",
				amber: "#e39a14",
				red: "#dc4263",
			};
			const sliceColors =
				c.report === "projects" || c.report === "production_summary"
					? labels.map((l) => statusPalette[this.statusColor(l)])
					: labels.map((_, i) => colors[i % colors.length]);
			const values = series[0].values,
				total = values.reduce((a, b) => a + b, 0);
			let offset = 0;
			const gradient = values
				.map((v, i) => {
					const start = offset;
					offset += total ? (v / total) * 100 : 0;
					return `${sliceColors[i]} ${start}% ${offset}%`;
				})
				.join(",");
			return `<div class="sd-donut-wrap"><div class="sd-donut" style="background:conic-gradient(${gradient})" role="img" aria-label="${this.esc(
				labels.map((l, i) => `${l}: ${values[i]}`).join(", ")
			)}"><span>${total}<small>${this.esc(
				series[0].name
			)}</small></span></div><div class="sd-chart-legend">${labels
				.map(
					(l, i) =>
						`<span><i style="background:${sliceColors[i]}"></i>${this.esc(l)} <b>${
							values[i]
						}</b></span>`
				)
				.join("")}</div></div>`;
		}
		if (c.type === "line" && labels.length > 1) {
			const points = series[0].values
				.map((v, i) => `${25 + (i * 450) / (labels.length - 1)},${150 - (v / max) * 120}`)
				.join(" ");
			return `<svg class="sd-line-chart" viewBox="0 0 500 185" role="img" aria-label="${this.esc(
				labels.map((l, i) => `${l}: ${series[0].values[i]}`).join(", ")
			)}"><path d="M25 20V150H480" fill="none" stroke="#dbe4ec"/><polyline points="${points}" fill="none" stroke="#2563eb" stroke-width="3"/>${series[0].values
				.map(
					(v, i) =>
						`<circle cx="${25 + (i * 450) / (labels.length - 1)}" cy="${
							150 - (v / max) * 120
						}" r="4" fill="#2563eb"><title>${this.esc(labels[i])}: ${this.num(
							v
						)}</title></circle>`
				)
				.join("")}<text x="25" y="175">${this.esc(labels[0])}</text><text x="410" y="175">${this.esc(
				labels.at(-1)
			)}</text></svg><div class="sd-chart-legend">${legend}</div>`;
		}
		return `<div class="sd-chart-legend">${legend}</div><div class="sd-bars">${labels
			.map(
				(label, i) =>
					`<div class="sd-bar-row"><span title="${this.esc(label)}">${this.esc(
						label
					)}</span><div>${series
						.map(
							(s, n) =>
								`<div class="sd-bar-track"><i style="width:${
									(Math.abs(Number(s.values[i] || 0)) / max) * 100
								}%;background:${
									s.values[i] < 0 ? "#cf7551" : colors[n % colors.length]
								}"></i><b>${this.num(s.values[i])}</b></div>`
						)
						.join("")}</div></div>`
			)
			.join("")}</div>`;
	}
	liveCards() {
		const groups = [
			"In progress",
			"Not started",
			"Completed",
			"On hold / Stopped",
			"Production finished · Closure pending",
			"Cancelled",
		];
		const summaries = this.data.production_summary;
		const number = (v) => (v === null || v === undefined ? "—" : this.num(v));
		return (
			groups
				.map((state) => {
					const projects = summaries.filter((p) => p.live_status === state);
					if (!projects.length && state !== "In progress") return "";
					return `<section class="sd-panel sd-live-group" data-live-state="${this.esc(
						state
					)}"><div class="sd-panel-heading"><div><h2>${this.esc(
						state
					)} projects <span class="sd-pill">${projects.length}</span></h2>${
						state === "In progress"
							? "<p>Current recorded Job Card activity · Completed projects are shown separately</p>"
							: ""
					}</div><button class="sd-text-button" data-report="${
						state === "Completed" || state === "Cancelled" ? "projects" : "production_summary"
					}" data-subset="${
						{
							"In progress": "in_progress",
							"Not started": "not_started",
							Completed: "completed",
							"On hold / Stopped": "paused",
							"Production finished · Closure pending": "closure_pending",
						}[state] || ""
					}">View report ↗</button></div><div class="sd-cards">${
						projects
							.map(
								(p) =>
									`<article class="sd-live-card" data-live-project="${this.esc(
										p.project
									)}"><div class="sd-panel-heading"><strong>${this.esc(
										p.project_name
									)}</strong>${this.badge(p.live_status)}</div><small>${this.esc(
										p.project
									)} · ${this.esc(p.customer || "Unassigned customer")}</small>${
										p.running_operations.length
											? p.running_operations
													.map(
														(r) =>
															`<div class="sd-running-operation"><strong>● Running now: ${this.esc(
																r.operation
															)}</strong><p>${this.link(
																"Workstation",
																r.workstation
															)} · ${this.link(
																"Job Card",
																r.job_card
															)}</p><p>Job Card: Planned ${number(
																r.planned
															)} · Completed ${number(
																r.completed
															)} · Remaining ${number(r.remaining)} ${this.esc(
																r.unit || ""
															)}</p><small>Started ${this.esc(
																frappe.datetime.str_to_user(r.started_at)
															)}</small></div>`
													)
													.join("")
											: `<p>${this.esc(p.activity_message)}</p>`
									}<p class="sd-scope-note">${
										p.last_activity
											? `Last recorded activity: ${this.esc(
													frappe.datetime.str_to_user(p.last_activity)
											  )}`
											: this.esc(p.note)
									}</p><button class="sd-button" data-project="${this.esc(
										p.project
									)}">Open project analysis ↗</button></article>`
							)
							.join("") || this.empty("No projects currently in progress in this selection.")
					}</div></section>`;
				})
				.join("") +
			'<p class="sd-scope-note">Running now means an open ERPNext Job Card time log. Operators must record start/stop activity; this is not independent machine telemetry.</p>'
		);
	}
	pipelineOverview() {
		const selected = !!this.filters.project;
		const projects = this.data.pipeline_summary || [];
		const setup = this.data.tracking_setup
			.map(
				(p) =>
					`<div class="sd-alert"><span>${this.esc(p.project)} · ${this.esc(
						p.validation
					)} · ${this.esc(p.physical_parts)}</span>${this.link(
						"Project",
						p.project,
						"Open setup"
					)}${p.main_bom ? this.link("BOM", p.main_bom, "Open main BOM") : ""}</div>`
			)
			.join("");

		const tableContent = projects.length
			? `
		<div class="sd-table-web-toolbar">
			<div class="sd-table-search-wrap">
				<svg class="sd-table-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
				<input type="text" class="sd-table-search-input" data-table-search="pipelines" placeholder="Search pipeline projects..." autocomplete="off" spellcheck="false" aria-label="Search pipeline projects">
			</div>
			<div class="sd-table-filter-pills" data-table-filters="pipelines">
				<button type="button" class="sd-filter-pill active" data-table-filter="all">All (${projects.length})</button>
				<button type="button" class="sd-filter-pill" data-table-filter="active">With Work Orders</button>
				<button type="button" class="sd-filter-pill" data-table-filter="inspections">With Inspections</button>
				<button type="button" class="sd-filter-pill" data-table-filter="deliveries">With Deliveries</button>
			</div>
			<div class="sd-table-count-badge">
				<span class="sd-pill sd-tone-blue"><strong data-table-count="pipelines">${
					projects.length
				}</strong> records</span>
			</div>
		</div>
		<div class="sd-color-table-wrapper">
			<table class="sd-color-table" data-table-id="pipelines" aria-label="Project Pipelines Table">
				<thead>
					<tr class="sd-color-table-header-row">
						<th class="sd-th-pin sd-th-purple">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">📦</span>
								<span class="sd-pin-text">Project</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-blue">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">📋</span>
								<span class="sd-pin-text">Material Requests</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-azure">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🛒</span>
								<span class="sd-pin-text">Purchase Orders</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-teal">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">📥</span>
								<span class="sd-pin-text">Purchase Receipts</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-forest">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⚙️</span>
								<span class="sd-pin-text">Work Orders</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-amber">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🔍</span>
								<span class="sd-pin-text">Inspections</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-rose">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🚚</span>
								<span class="sd-pin-text">Delivery Notes</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-violet">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🧾</span>
								<span class="sd-pin-text">Sales Invoices</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-olive">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏷️</span>
								<span class="sd-pin-text">Action</span>
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					${projects
						.map((p, i) => {
							const isEven = i % 2 === 0;
							const pipeBtn = (key, reportName, label) => {
								const val = p[key];
								const isRestricted = val === null;
								const cls = isRestricted
									? "step-restricted"
									: val
									? "step-recorded"
									: "step-zero";
								const text = isRestricted ? "Restricted" : val ?? 0;
								return `<button type="button" class="sd-pipeline-step-pill ${cls}" data-report-project="${this.esc(
									p.project
								)}" data-report="${reportName}" data-kpi-label="${this.esc(
									label
								)}" title="${label}: ${text}"><strong>${text}</strong></button>`;
							};
							return `
						<tr class="sd-color-tr ${isEven ? "sd-tr-even" : "sd-tr-odd"}" data-project="${this.esc(
								p.project
							)}" data-wo="${p.work_orders > 0 ? "yes" : "no"}" data-insp="${
								p.inspections > 0 ? "yes" : "no"
							}" data-del="${p.deliveries > 0 ? "yes" : "no"}" role="button" tabindex="0">
							<td class="sd-td-ribbon">
								<div class="sd-row-ribbon sd-ribbon-purple">
									<div class="sd-ribbon-box">
										<span class="sd-ribbon-symbol">⚙</span>
									</div>
									<div class="sd-ribbon-content">
										<strong class="sd-ribbon-name" title="${this.esc(p.project)}">${this.esc(p.project)}</strong>
									</div>
									<div class="sd-ribbon-chevron"></div>
								</div>
							</td>
							<td class="sd-td-cell">${pipeBtn("requests", "requests", "Material Requests")}</td>
							<td class="sd-td-cell">${pipeBtn("purchases", "purchases", "Purchase Orders")}</td>
							<td class="sd-td-cell">${pipeBtn("receipts", "receipts", "Purchase Receipts")}</td>
							<td class="sd-td-cell">${pipeBtn("work_orders", "work_orders", "Work Orders")}</td>
							<td class="sd-td-cell">${pipeBtn("inspections", "quality", "Inspections")}</td>
							<td class="sd-td-cell">${pipeBtn("deliveries", "deliveries", "Delivery Notes")}</td>
							<td class="sd-td-cell">${pipeBtn("sales_invoices", "sales_invoices", "Sales Invoices")}</td>
							<td class="sd-td-cell sd-td-action">
								<button type="button" class="sd-row-action-btn" data-project="${this.esc(p.project)}">
									Inspect ➔
								</button>
							</td>
						</tr>`;
						})
						.join("")}
				</tbody>
			</table>
		</div>`
			: this.empty();

		return `<section class="sd-panel" data-pipeline-panel><div class="sd-panel-heading"><div><h2>${
			selected ? "Project working pipeline" : "Project pipelines"
		}</h2><p>Lifetime records · Steps can run in parallel · Counts are documents, not part quantities</p></div></div>${tableContent}<div class="sd-production-links"><button class="sd-button" data-report="part_production">Recorded cutting / welding / grinding outputs</button><button class="sd-button" data-report="material_history">Lifetime materials</button><button class="sd-button" data-report="tracking_setup">Part tracking setup</button></div><details class="sd-setup-details"><summary>Project attribution & physical part setup</summary>${setup}</details>${
			this.data.procurement_exception_count
				? `<div class="sd-alert"><span>${this.data.procurement_exception_count} procurement item rows have missing or conflicting project links.</span><button class="sd-text-button" data-report="procurement_exceptions">Review records ↗</button></div>`
				: ""
		}</section>`;
	}
	projectHealth() {
		const entries = this.data.project_health || [];
		const selected = !!this.filters.project;
		const visible = selected
			? entries
			: entries.filter((p) => !["Completed", "Cancelled"].includes(p.live_status));

		const tableContent = visible.length
			? `
		<div class="sd-table-web-toolbar">
			<div class="sd-table-search-wrap">
				<svg class="sd-table-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
				<input type="text" class="sd-table-search-input" data-table-search="health" placeholder="Search project health..." autocomplete="off" spellcheck="false" aria-label="Search project health">
			</div>
			<div class="sd-table-filter-pills" data-table-filters="health">
				<button type="button" class="sd-filter-pill active" data-table-filter="all">All (${visible.length})</button>
				<button type="button" class="sd-filter-pill" data-table-filter="in_progress">In Progress</button>
				<button type="button" class="sd-filter-pill" data-table-filter="shortages">Shortages</button>
				<button type="button" class="sd-filter-pill" data-table-filter="delayed">Delayed</button>
			</div>
			<div class="sd-table-count-badge">
				<span class="sd-pill sd-tone-blue"><strong data-table-count="health">${visible.length}</strong> records</span>
			</div>
		</div>
		<div class="sd-color-table-wrapper">
			<table class="sd-color-table" data-table-id="health" aria-label="Project Health Table">
				<thead>
					<tr class="sd-color-table-header-row">
						<th class="sd-th-pin sd-th-purple">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">📦</span>
								<span class="sd-pin-text">Project</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-blue">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⭐</span>
								<span class="sd-pin-text">Live Status</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-azure">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏭</span>
								<span class="sd-pin-text">Working Now</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-teal">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⏱️</span>
								<span class="sd-pin-text">Next Operation</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-forest">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⚙️</span>
								<span class="sd-pin-text">Ops Finished/Total</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-amber">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">⚠️</span>
								<span class="sd-pin-text">Shortages</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-rose">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🛒</span>
								<span class="sd-pin-text">PO & Receipts</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-violet">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🔍</span>
								<span class="sd-pin-text">Quality Pass/Fail</span>
							</div>
						</th>
						<th class="sd-th-pin sd-th-olive">
							<div class="sd-pin-badge">
								<span class="sd-pin-icon">🏷️</span>
								<span class="sd-pin-text">Action</span>
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					${visible
						.map((p, i) => {
							const isEven = i % 2 === 0;
							const curOps = p.current_operations.length
								? `<span class="sd-cell-badge sd-badge-azure"><span class="sd-dot-pulse live-green"></span> <strong>${this.esc(
										p.current_operations.map((op) => op.operation || "Unnamed").join(", ")
								  )}</strong></span>`
								: `<span class="sd-cell-text" style="color:var(--sd-muted)">No Job Card open</span>`;
							const nextOp = p.next_operation
								? `<span class="sd-cell-text"><strong>${this.esc(
										p.next_operation.operation || "Unnamed"
								  )}</strong> · ${this.link(
										"Work Order",
										p.next_operation.work_order
								  )}</span>`
								: `<span class="sd-cell-text" style="color:var(--sd-muted)">None</span>`;
							return `
						<tr class="sd-color-tr ${isEven ? "sd-tr-even" : "sd-tr-odd"}" data-project="${this.esc(
								p.project
							)}" data-health-status="${this.esc(p.live_status)}" data-shortages="${
								p.material_shortages > 0 ? "yes" : "no"
							}" data-delayed="${p.delayed ? "yes" : "no"}" role="button" tabindex="0">
							<td class="sd-td-ribbon">
								<div class="sd-row-ribbon sd-ribbon-purple">
									<div class="sd-ribbon-box">
										<span class="sd-ribbon-symbol">⚙</span>
									</div>
									<div class="sd-ribbon-content">
										<strong class="sd-ribbon-name" title="${this.esc(p.project)}">${this.esc(p.project)}</strong>
										${
											p.last_activity
												? `<span class="sd-ribbon-sub">Active ${this.esc(
														frappe.datetime.str_to_user(p.last_activity)
												  )}</span>`
												: `<span class="sd-ribbon-sub">No recent activity</span>`
										}
									</div>
									<div class="sd-ribbon-chevron"></div>
								</div>
							</td>
							<td class="sd-td-cell">${this.badge(p.live_status)}</td>
							<td class="sd-td-cell">${curOps}</td>
							<td class="sd-td-cell">${nextOp}</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-blue">
									<strong>${this.num(p.operations_finished)}</strong> / ${this.num(p.operations_total)}
								</span>
							</td>
							<td class="sd-td-cell">
								${
									p.material_shortages > 0
										? `<span class="sd-status-tag sd-tag-delayed"><strong>${this.num(
												p.material_shortages
										  )}</strong> Shortages</span>`
										: `<span class="sd-status-tag sd-tag-ontrack">0 Shortages</span>`
								}
							</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-teal">
									PO: <strong>${this.num(p.purchase_orders)}</strong> · PR: <strong>${this.num(p.receipts)}</strong>
								</span>
							</td>
							<td class="sd-td-cell">
								<span class="sd-cell-badge sd-badge-violet">
									Pass: <strong>${this.num(p.inspection_passed)}</strong> · Fail: <strong>${this.num(
								p.inspection_rejected
							)}</strong>
								</span>
							</td>
							<td class="sd-td-cell sd-td-action">
								<button type="button" class="sd-row-action-btn" data-project="${this.esc(p.project)}">
									Analysis ➔
								</button>
							</td>
						</tr>`;
						})
						.join("")}
				</tbody>
			</table>
		</div>`
			: this.empty(
					"No open projects in this selection. Select a completed project to see its full health summary."
			  );

		return `<section class="sd-panel sd-health" data-health-panel><div class="sd-panel-heading"><div><h2>${
			selected ? "Project health at a glance" : "Open project health"
		}</h2><p>Current recorded operation, next outstanding step, materials, quality and fulfillment · lifetime project records</p></div></div>${tableContent}<p class="sd-scope-note">An open Job Card time log is recorded activity, not proof of machine telemetry. A blank metric means read access or stock availability is unavailable. Inspection counts are submitted results, not part quantities.</p></section>`;
	}
	productionOverview() {
		const selected = !!this.filters.project;
		const summaries = this.data.production_summary.filter(
			(p) => selected || p.live_status === "In progress"
		);
		const number = (v) => (v === null || v === undefined ? "—" : this.num(v));
		const rows = (ops) =>
			`<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${[
				"Operation",
				"Work Order",
				"Workstation",
				"Output item / unit",
				"Planned",
				"Completed",
				"Process loss",
				"Remaining",
				"Status",
			]
				.map((x) => `<th>${x}</th>`)
				.join("")}</tr></thead><tbody>${ops
				.map(
					(r) =>
						`<tr><td>${this.esc(r.sequence)} · ${this.esc(r.operation)}</td><td>${this.link(
							"Work Order",
							r.work_order
						)}<small class="sd-operation-note">${this.esc(
							r.work_order_status
						)}</small></td><td>${this.link("Workstation", r.workstation)}</td><td>${this.link(
							"Item",
							r.item
						)}<small class="sd-operation-note">${this.esc(
							r.unit || "Unit unavailable"
						)}</small></td><td>${number(r.planned)}</td><td>${number(
							r.completed
						)}</td><td>${number(r.process_loss)}</td><td>${number(
							r.remaining
						)}</td><td>${this.badge(r.status)}</td></tr>`
				)
				.join("")}</tbody></table></div>`;
		return `<section class="sd-panel sd-production-overview"><div class="sd-panel-heading"><div><h2>${
			selected ? "Project operation progress" : "In progress projects · operation progress"
		} <span class="sd-pill">${
			summaries.length
		}</span></h2><p>Lifetime submitted Work Orders · In progress = recorded production started · Quantities are Work Order output units, not physical warehouse balances</p></div><button class="sd-text-button" data-report="operation_balance" data-subset="${
			selected ? "" : "in_progress"
		}">Full operation report ↗</button></div>${
			summaries
				.map((p) => {
					const ops = this.data.operation_balance.filter((r) => r.project === p.project);
					return `<details class="sd-production-project" data-production-project="${this.esc(
						p.project
					)}" ${selected ? "open" : ""}><summary><span><strong>${this.esc(
						p.project_name
					)}</strong><small>${this.esc(p.project)} · ${this.esc(
						p.customer || "Unassigned customer"
					)}</small></span>${this.badge(p.production_status)}<span>${p.finished_operations}/${
						p.operations
					} operations finished</span></summary><div class="sd-production-body"><p>${this.esc(
						p.note
					)} · ${p.work_orders} submitted Work Orders · Semi-finished stock tracking: ${this.esc(
						p.stock_tracking
					)} <button class="sd-text-button" data-project="${this.esc(
						p.project
					)}">Open project analysis ↗</button></p>${
						ops.length
							? rows(ops)
							: this.empty(
									"No recorded Work Order operations. Create a linked BOM / Work Order with operations to track production."
							  )
					}</div></details>`;
				})
				.join("") || this.empty("No projects in progress in this selection.")
		}<div class="sd-production-links"><button class="sd-button" data-report="production_summary">All project production summaries</button><button class="sd-button" data-report="projects" data-subset="completed">Completed projects</button><button class="sd-button" data-report="wip_stock">Semi-finished warehouse stock</button></div><p class="sd-scope-note">Remaining = planned − completed − process loss, minimum zero. Cutting/welding/grinding are separate operations; their quantities must not be added as unique finished parts. Warehouse stock requires configured semi-finished items and posted stock movements.</p></section>`;
	}
	setupOverview() {
		const d = this.data;
		const isProj = !!this.filters.project;
		const p = d.selected_project;
		const title = isProj
			? `Project Setup & Master Records (${p?.project_name || p?.name})`
			: "Manufacturing & Setup Masters";
		const sub = isProj
			? "Warehouses, operations, workstations, and items configured for this project"
			: "Click any card to inspect all records, or click + New to create one";

		const getCount = (reportKey) => {
			const k = d.kpis.find((x) => x.report === reportKey);
			return k ? k.value : 0;
		};

		const cards = [
			{
				key: "warehouses",
				title: "Warehouses",
				icon: "🏢",
				dt: "Warehouse",
				desc: isProj ? "Project storage & WIP locations" : "Stores, WIP, FG & transit warehouses",
				count: getCount("warehouses"),
			},
			{
				key: "operations_catalogue",
				title: "Operations",
				icon: "⚙️",
				dt: "Operation",
				desc: isProj
					? "Standard operations in this project"
					: "Fabrication, welding & assembly operations",
				count: getCount("operations_catalogue"),
			},
			{
				key: "workstations",
				title: "Workstations",
				icon: "🏭",
				dt: "Workstation",
				desc: isProj
					? "Assigned machinery & workstations"
					: "Active production machines & capacities",
				count: getCount("workstations"),
			},
			{
				key: "workstation_types",
				title: "Workstation Types",
				icon: "🏷️",
				dt: "Workstation Type",
				desc: "Machine classes & standard cost centers",
				count: getCount("workstation_types"),
			},
			{
				key: "routings",
				title: "Routings",
				icon: "🔄",
				dt: "Routing",
				desc: "Standard multi-operation sequences",
				count: getCount("routings"),
			},
			{
				key: "items",
				title: "Items Catalogue",
				icon: "📦",
				dt: "Item",
				desc: isProj ? "Finished parts & raw materials" : "Products, parts & raw materials",
				count: getCount("items"),
			},
		];

		return `
      <section class="sd-panel sd-setup-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>${this.esc(title)}</h2>
            <p>${this.esc(sub)}</p>
          </div>
          ${
				isProj
					? `<button class="sd-button sd-text-button" data-action="clear-project-setup">View All Master Lists ↗</button>`
					: ""
			}
        </div>
        <div class="sd-cards sd-setup-cards">
          ${cards
				.map(
					(c) => `
            <article class="sd-card sd-setup-card" data-report="${c.key}">
              <div class="sd-setup-header">
                <span class="sd-setup-icon">${this.workspaceIcon(c.title || c.label || c.key)}</span>
                <span class="sd-pill sd-tone-blue">${this.num(c.count)}</span>
              </div>
              <h3>${this.esc(c.title)}</h3>
              <p>${this.esc(c.desc)}</p>
              <div class="sd-setup-actions">
                <button class="sd-button sd-tone-blue" data-report="${c.key}">Show List ↗</button>
                <button class="sd-button" data-new="${c.dt}" title="Create new ${c.dt}">+ New</button>
              </div>
            </article>
          `
				)
				.join("")}
        </div>
      </section>
    `;
	}
	renderContent() {
		const content = this.el("[data-content]");
		this.root.dataset.currentTab = this.tab;
		const expanded = new Set(
			Array.from(content.querySelectorAll("[data-production-project][open]")).map(
				(x) => x.dataset.productionProject
			)
		);
		this.detailSequence++;
		if (this.tab === "overview") {
			this.reportState = null;
			content.innerHTML = `${this.projectHealth()}${this.pipelineOverview()}${this.productionOverview()}${this.setupOverview()}${this.chartGrid(
				this.chartsForTab()
			)}<section class="sd-panel"><div class="sd-panel-heading"><h2>Alerts & data quality <span class="sd-pill">${
				this.data.alert_count
			}</span></h2><button class="sd-text-button" data-report="issues">View all</button></div>${
				this.data.alerts
					.map(
						(a) =>
							`<div class="sd-alert">${this.link(a.doctype, a.name)}<span>${this.esc(
								a.issue
							)}</span></div>`
					)
					.join("") || this.empty("No exceptions found in the selected records.")
			}</section>`;
			content.querySelectorAll("[data-production-project]").forEach((x) => {
				if (expanded.has(x.dataset.productionProject)) x.open = true;
			});
			return;
		}
		const choices =
			this.tab === "reports" ? this.data.reports.map((r) => r.key) : this.tabReports[this.tab];
		if (!this.reportState || !choices.includes(this.reportState.report))
			this.reportState = {
				report: choices[0],
				subset: "",
				search: "",
				start: 0,
			};
		const r = this.reportState;
		const isMasterReport = [
			"warehouses",
			"workstations",
			"operations_catalogue",
			"workstation_types",
			"routings",
			"items",
		].includes(r.report);
		const scopeToggle =
			this.filters.project && isMasterReport
				? `
      <div class="sd-scope-toggle">
        <span class="sd-pill sd-tone-blue">Project: <strong>${this.esc(
			this.data.selected_project?.project_name || this.filters.project
		)}</strong></span>
        <button class="sd-button ${
			r.subset === "all" ? "" : "sd-primary"
		}" data-scope-subset="">Show Project Records</button>
        <button class="sd-button ${
			r.subset === "all" ? "sd-primary" : ""
		}" data-scope-subset="all">Show All Organization Records</button>
      </div>`
				: "";
		content.innerHTML = `<section class="sd-panel"><div class="sd-report-toolbar"><label>Report<select data-report-select>${choices
			.map(
				(k) =>
					`<option value="${k}" ${r.report === k ? "selected" : ""}>${this.esc(
						this.data.reports.find((x) => x.key === k).title
					)}</option>`
			)
			.join(
				""
			)}</select></label><label>Search report<input data-report-search type="search" value="${this.esc(
			r.search
		)}" placeholder="Search all matching rows"></label><button class="sd-button" data-action="export">Export CSV</button><button class="sd-button" data-action="native-report">Open ERPNext report ↗</button></div><p class="sd-scope-note">${
			r.subset ? `Filtered to ${this.esc(r.subset)} records. ` : ""
		}Totals cover every matching record. Pipeline, material history, part outputs, purchasing and fulfillment reports use lifetime records. Invoice outstanding is a whole-document amount and must not be summed across item rows. Returns retain signed quantities. Inspection sample size is not a rejected-part count. Document status: 0 Draft · 1 Submitted · 2 Cancelled. ${
			this.tab === "materials"
				? "Semi-finished stock requires enabled tracking, operation output Items and target warehouses. Stock is shared availability; requirements come from open submitted Work Orders. Blank stock means unavailable or no source warehouse."
				: ""
		}</p>${scopeToggle}<div data-table-area role="status">Loading report…</div></section>`;
		content.insertAdjacentHTML(
			"afterbegin",
			`<div data-tab-charts>${this.chartGrid(this.chartsForTab())}</div>`
		);
		this.el("[data-report-select]").addEventListener("change", (e) => {
			this.reportState = {
				report: e.target.value,
				subset: "",
				search: "",
				start: 0,
			};
			this.renderContent();
		});
		this.el("[data-report-search]").addEventListener("input", (e) => {
			this.reportState.search = e.target.value;
			this.reportState.start = 0;
			clearTimeout(this.searchTimer);
			this.searchTimer = setTimeout(() => this.loadReport(), 300);
		});
		this.loadReport();
	}
	chartsForTab() {
		const reports =
			{
				overview: ["projects", "deadlines", "operation_balance", "production_summary"],
				sales: ["orders"],
				production: ["part_production", "work_orders", "job_cards", "finished", "operation_balance"],
				procurement: ["purchases"],
				materials: ["materials"],
			}[this.tab] || [];
		return this.data.charts.filter((c) =>
			c.title.startsWith("Manufacturing pipeline")
				? this.tab === "overview"
				: reports.includes(c.report)
		);
	}
	chartGrid(charts) {
		return charts.length
			? `<div class="sd-chart-grid">${charts
					.map(
						(c) =>
							`<article class="sd-panel" data-chart-report="${this.esc(
								c.report
							)}"><div class="sd-panel-heading"><h2>${this.esc(
								c.title
							)}</h2><button class="sd-text-button" data-report="${c.report}" data-subset="${
								c.subset || ""
							}">View records ↗</button></div>${this.chart(c)}</article>`
					)
					.join("")}</div>`
			: "";
	}
	cell(c, row) {
		const value = row[c.fieldname];
		if (value === null || value === undefined || value === "") return "—";
		if (c.fieldtype === "Link")
			return (
				this.link(c.options, value) +
				(c.fieldname === "name"
					? ` <button class="sd-inspect" data-inspect="${this.esc(value)}" data-doctype="${this.esc(
							c.options
					  )}" aria-label="Inspect ${this.esc(value)}">Details</button>`
					: "")
			);
		if (c.fieldtype === "Dynamic Link") return this.link(row[c.options], value);
		if (["Float", "Int", "Currency", "Percent"].includes(c.fieldtype))
			return this.num(value) + (c.fieldtype === "Percent" ? "%" : "");
		return this.esc(value);
	}
	async loadReport() {
		const version = ++this.detailSequence,
			state = { ...this.reportState };
		try {
			const r = await this.call("get_report", {
				filters: JSON.stringify(this.filters),
				...state,
				page_length: 25,
			});
			if (version !== this.detailSequence || !this.el("[data-table-area]")) return;
			const isMasterReport = [
				"warehouses",
				"workstations",
				"operations_catalogue",
				"workstation_types",
				"routings",
				"items",
			].includes(r.report || state.report);
			const emptyMsg =
				this.filters.project && isMasterReport && state.subset !== "all"
					? `No ${this.esc(r.title || "records")} linked to project ${this.esc(
							this.data?.selected_project?.project_name || this.filters.project
					  )}. Click "Show All Organization Records" above to see all organization records, or configure this project's records.`
					: "No linked records for this selection.";
			this.el("[data-table-area]").innerHTML =
				(r.rows.length
					? `<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${r.columns
							.map((c) => `<th>${this.esc(c.label)}</th>`)
							.join("")}</tr></thead><tbody>${r.rows
							.map(
								(row) =>
									`<tr>${r.columns
										.map((c) => `<td>${this.cell(c, row)}</td>`)
										.join("")}</tr>`
							)
							.join("")}</tbody></table></div>`
					: this.empty(emptyMsg)) +
				`<div class="sd-pagination"><button class="sd-button" data-report-page="${Math.max(
					0,
					r.start - 25
				)}" ${!r.start ? "disabled" : ""}>Previous</button><span>${
					r.total ? r.start + 1 : 0
				}–${Math.min(r.total, r.start + 25)} of ${
					r.total
				}</span><button class="sd-button" data-report-page="${r.start + 25}" ${
					r.start + 25 >= r.total ? "disabled" : ""
				}>Next</button></div>`;
		} catch (e) {
			if (version === this.detailSequence && this.el("[data-table-area]"))
				this.el("[data-table-area]").innerHTML = this.empty(
					"Report could not load. Check your access and click Refresh."
				);
		}
	}
	openReport(report, subset = "") {
		this.tab = "reports";
		this.reportState = { report, subset, search: "", start: 0 };
		this.writeUrl();
		this.renderTabs();
		this.renderContent();
		this.el(".sd-tabs").scrollIntoView({ behavior: "smooth", block: "start" });
	}

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
		if (val === null || val === undefined || val === "" || val === "—") {
			return '<span style="color:#94a3b8; font-weight:500;">—</span>';
		}
		if (c.fieldtype === "Currency") {
			return `<span class="sd-cell-badge sd-badge-azure" style="white-space:nowrap;"><strong>₹${this.num(
				val
			)}</strong></span>`;
		}
		if (c.fieldtype === "Percent") {
			const pct = Math.min(100, Math.max(0, Number(val) || 0));
			return `<div class="sd-table-progress-box" style="margin: 0 auto; min-width: 100px;"><div class="sd-table-progress-bar"><div class="sd-table-progress-fill" style="width: ${pct}%;"></div></div><div class="sd-table-progress-meta" style="justify-content: center;"><span class="sd-prog-pct">${this.num(
				val
			)}%</span></div></div>`;
		}
		if (["Float", "Int"].includes(c.fieldtype)) {
			return `<span class="sd-cell-badge sd-badge-teal" style="white-space:nowrap;"><strong>${this.num(
				val
			)}</strong></span>`;
		}
		if (c.fieldtype === "Date" || c.fieldtype === "Datetime") {
			const formatted = frappe.datetime?.str_to_user ? frappe.datetime.str_to_user(val) : String(val);
			return `<span class="sd-cell-badge sd-badge-blue" style="white-space:nowrap;"><span style="font-size:12px;">📅</span> ${this.esc(
				formatted
			)}</span>`;
		}
		const strVal = String(val);
		const fieldName = String(c.fieldname || "").toLowerCase();
		const colLabel = String(c.label || "").toLowerCase();
		if (fieldName.includes("status") || colLabel.includes("status") || fieldName.includes("state")) {
			const lower = strVal.toLowerCase();
			if (/completed|finished|delivered|closed|submitted/.test(lower)) {
				return `<span class="sd-status-tag sd-tag-ontrack" style="white-space:nowrap;"><span class="sd-tag-icon">✓</span> ${this.esc(
					val
				)}</span>`;
			}
			if (/delayed|overdue|shortage|cancelled|failed|rejected/.test(lower)) {
				return `<span class="sd-status-tag sd-tag-delayed" style="white-space:nowrap;"><span class="sd-tag-icon">✕</span> ${this.esc(
					val
				)}</span>`;
			}
			if (/in progress|working|active|running/.test(lower)) {
				return `<span class="sd-cell-badge sd-badge-blue" style="white-space:nowrap;"><span class="sd-dot-pulse live-green"></span> ${this.esc(
					val
				)}</span>`;
			}
			return `<span class="sd-status-pill sd-pill-${this.statusColor(
				val
			)}" style="white-space:nowrap;">${this.esc(val)}</span>`;
		}
		if (c.fieldtype === "Link" && c.options && val) {
			return `<a href="javascript:void(0)" class="sd-record-link sd-cell-link" data-inspect="${this.esc(
				val
			)}" data-doctype="${this.esc(
				c.options
			)}" style="white-space:nowrap; font-weight:600; color:#2563eb;">${this.esc(val)} ↗</a>`;
		}
		return `<span class="sd-cell-text" style="white-space:nowrap;">${this.esc(val)}</span>`;
	}

	async showCardDetailsModal(reportKey, subset = "", label = "", projectContext = "") {
		if (!reportKey) return;
		const project = projectContext || this.filters.project || "";
		const activeFilters = { ...this.filters };
		if (project) activeFilters.project = project;

		let dialogTitle = label;
		if (
			!dialogTitle ||
			/^\d+$/.test(String(dialogTitle).trim()) ||
			String(dialogTitle).trim().length <= 2
		) {
			dialogTitle =
				this.data?.reports?.find((r) => r.key === reportKey)?.title ||
				frappe.unscrub(this.getDocTypeForReport(reportKey) || reportKey);
		}

		const dialog = new frappe.ui.Dialog({
			title: `${this.workspaceIcon(dialogTitle)} ${this.esc(dialogTitle)}`,
			size: "extra-large",
			fields: [{ fieldname: "card_content", fieldtype: "HTML" }],
		});
		dialog.$wrapper.addClass("sd-card-details-dialog");
		dialog.fields_dict.card_content.$wrapper.html(
			`<div class="sd-modal-loading"><div class="sd-modal-spinner"></div><p>Fetching ${this.esc(
				dialogTitle
			)} records…</p></div>`
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

			this.renderCardDetailsTable(dialog, data, reportKey, subset, dialogTitle, project);
		} catch (err) {
			dialog.fields_dict.card_content.$wrapper.html(
				`<div class="sd-empty">Unable to load records for this card. ${this.esc(
					err.message || ""
				)}</div>`
			);
		}
	}

	renderCardDetailsTable(dialog, data, reportKey, subset, title, project, initialSearch = "") {
		const $container = dialog.fields_dict.card_content.$wrapper;
		const columns = data.columns || [];
		const rows = data.rows || [];
		const total = data.total || rows.length;
		let currentSearch = initialSearch;

		let resolvedTitle = title;
		if (
			!resolvedTitle ||
			/^\d+$/.test(String(resolvedTitle).trim()) ||
			String(resolvedTitle).trim().length <= 2
		) {
			resolvedTitle =
				this.data?.reports?.find((r) => r.key === reportKey)?.title ||
				frappe.unscrub(this.getDocTypeForReport(reportKey) || reportKey);
		}
		const baseTitle = String(resolvedTitle)
			.replace(/\s*\(\d+\)$/, "")
			.trim();
		dialog.set_title(`${this.workspaceIcon(baseTitle)} ${this.esc(baseTitle)} (${total})`);

		const defaultDt = this.getDocTypeForReport(reportKey);

		const PIN_THEMES = [
			{ cls: "sd-th-purple", defaultIcon: "🏢" },
			{ cls: "sd-th-blue", defaultIcon: "🛡️" },
			{ cls: "sd-th-azure", defaultIcon: "⭐" },
			{ cls: "sd-th-teal", defaultIcon: "👍" },
			{ cls: "sd-th-forest", defaultIcon: "⏱️" },
			{ cls: "sd-th-amber", defaultIcon: "⚠️" },
			{ cls: "sd-th-rose", defaultIcon: "🛒" },
			{ cls: "sd-th-violet", defaultIcon: "🔍" },
			{ cls: "sd-th-lime", defaultIcon: "💎" },
			{ cls: "sd-th-olive", defaultIcon: "🏷️" },
		];

		const getColumnIcon = (col, idx) => {
			const s = `${col.label || ""} ${col.fieldname || ""}`.toLowerCase();
			if (/customer|client|organization|party/.test(s)) return "🏢";
			if (/project|task|operation|work_order|wo/.test(s)) return "📋";
			if (/item|part|product|material|bom/.test(s)) return "📦";
			if (/status|state|workflow/.test(s)) return "🛡️";
			if (/date|time|schedule|due/.test(s)) return "📅";
			if (/qty|quantity|count|delivered|produced/.test(s)) return "⏱️";
			if (/amount|cost|price|total|value|rate|curr|balance|tax/.test(s)) return "💰";
			if (/percent|pct|progress|compl/.test(s)) return "⭐";
			if (/warehouse|location/.test(s)) return "🏬";
			if (/supplier|vendor/.test(s)) return "🤝";
			if (/user|manager|assign|owner/.test(s)) return "👤";
			return PIN_THEMES[idx % PIN_THEMES.length].defaultIcon;
		};

		const renderTableBody = (filteredRows) => {
			if (!filteredRows.length) {
				return `<tr><td colspan="${
					columns.length + 1
				}" style="text-align: center; padding: 48px; color: #64748b; font-size: 14px; font-weight: 600;">No matching records found.</td></tr>`;
			}
			return filteredRows
				.map((row, rIdx) => {
					const docName = row.name || row.parent || row.project || row.item_code || "";
					const doctype = row.doctype || defaultDt;
					const isEven = rIdx % 2 === 0;

					const firstCol = columns[0];
					const firstVal = firstCol ? row[firstCol.fieldname] ?? docName : docName;
					const primaryName =
						row.customer_name ||
						row.project_name ||
						row.item_name ||
						row.title ||
						firstVal ||
						docName ||
						"—";
					const subName =
						primaryName !== docName && docName ? docName : row.doctype || defaultDt || "";
					const initials =
						String(primaryName)
							.replace(/[^a-zA-Z0-9]/g, "")
							.slice(0, 2)
							.toUpperCase() || "ID";

					return `
          <tr class="sd-color-tr sd-modal-row ${isEven ? "sd-tr-even" : "sd-tr-odd"}" data-name="${this.esc(
						docName
					)}" data-doctype="${this.esc(doctype)}">
            <td class="sd-td-ribbon">
              <div class="sd-row-ribbon ${rIdx % 2 === 0 ? "sd-ribbon-purple" : "sd-ribbon-plum"}">
                <div class="sd-ribbon-box">
                  <span class="sd-ribbon-initials">${this.esc(initials)}</span>
                </div>
                <div class="sd-ribbon-content">
                  <strong class="sd-ribbon-name" title="${this.esc(primaryName)}">${this.esc(
						primaryName
					)}</strong>
                  ${
						subName
							? `<span class="sd-ribbon-sub" title="${this.esc(subName)}">${this.esc(
									subName
							  )}</span>`
							: ""
					}
                </div>
                <div class="sd-ribbon-chevron"></div>
              </div>
            </td>
            ${columns
				.slice(1)
				.map((c) => {
					const val = row[c.fieldname];
					return `<td class="sd-td-cell">${this.formatCellValue(c, val)}</td>`;
				})
				.join("")}
            <td class="sd-td-cell sd-td-action" style="text-align: center; white-space: nowrap;">
              ${
					docName
						? `<button type="button" class="sd-row-action-btn sd-modal-btn-view" data-action="view-row-form" data-name="${this.esc(
								docName
						  )}" data-doctype="${this.esc(doctype)}">View Form ➔</button>`
						: "—"
				}
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
					(v) => v !== null && v !== undefined && String(v).toLowerCase().includes(t)
				)
			);
		};

		const html = `
      <div class="sd-modal-view-container">
        <!-- Top Toolbar -->
        <div class="sd-modal-toolbar">
          <div class="sd-modal-search-wrap">
            <svg class="sd-modal-search-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="search" class="sd-modal-search-input" value="${this.esc(
				currentSearch
			)}" placeholder="Search across all fields in this list..." />
          </div>
          <div class="sd-modal-meta-pills">
            <span class="sd-pill sd-status-blue">${total} Records</span>
            ${project ? `<span class="sd-pill sd-status-amber">Project: ${this.esc(project)}</span>` : ""}
            ${subset ? `<span class="sd-pill sd-status-purple">Subset: ${this.esc(subset)}</span>` : ""}
          </div>
        </div>

        <!-- Table Scroll Container -->
        <div class="sd-color-table-wrapper sd-modal-table-scroll">
          <table class="sd-color-table sd-modal-table" aria-label="${this.esc(title)} Table">
            <thead>
              <tr class="sd-color-table-header-row">
                ${columns
					.map((c, i) => {
						const theme = PIN_THEMES[i % PIN_THEMES.length];
						const pinIcon = getColumnIcon(c, i);
						return `
                  <th class="sd-th-pin ${theme.cls}">
                    <div class="sd-pin-badge">
                      <span class="sd-pin-icon">${pinIcon}</span>
                      <span class="sd-pin-text">${this.esc(c.label)}</span>
                    </div>
                  </th>
                `;
					})
					.join("")}
                <th class="sd-th-pin sd-th-olive" style="text-align: center; width: 130px;">
                  <div class="sd-pin-badge">
                    <span class="sd-pin-icon">⚡</span>
                    <span class="sd-pin-text">Action</span>
                  </div>
                </th>
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
		$container.on("click", ".sd-modal-btn-view, .sd-modal-row td:not(:last-child)", (e) => {
			if ($(e.target).closest("a, button:not(.sd-modal-btn-view)").length) {
				return;
			}
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
						currentSearch
					);
				});
			}
		});

		$container.off("click", ".sd-record-link");
		$container.on("click", ".sd-record-link", (e) => {
			e.stopPropagation();
			const targetName =
				$(e.target).attr("data-inspect") || $(e.target).text().trim().replace(/ ↗$/, "");
			const targetDt = $(e.target).attr("data-doctype") || defaultDt;
			if (targetName && targetDt) {
				this.showRecordFormModal(dialog, targetDt, targetName, () => {
					this.renderCardDetailsTable(
						dialog,
						data,
						reportKey,
						subset,
						title,
						project,
						currentSearch
					);
				});
			}
		});
	}

	async showRecordFormModal(dialog, doctype, name, onBackCallback = null) {
		let targetDialog = dialog;
		if (!targetDialog) {
			targetDialog = new frappe.ui.Dialog({
				title: `${this.workspaceIcon(doctype)} ${this.esc(doctype)}: ${this.esc(name)}`,
				size: "extra-large",
				fields: [{ fieldname: "card_content", fieldtype: "HTML" }],
			});
			targetDialog.$wrapper.addClass("sd-card-details-dialog");
			targetDialog.show();
		} else {
			targetDialog.set_title(`${this.workspaceIcon(doctype)} ${this.esc(doctype)}: ${this.esc(name)}`);
		}

		const $container = targetDialog.fields_dict.card_content.$wrapper;
		$container.html(
			`<div class="sd-modal-loading"><div class="sd-modal-spinner"></div><p>Loading ${this.esc(
				doctype
			)} ${this.esc(name)} form details…</p></div>`
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
			const status = row.status || row.workflow_state || row.docstatus_name || "";

			const PIN_THEMES = [
				{ cls: "sd-th-purple", defaultIcon: "🏢" },
				{ cls: "sd-th-blue", defaultIcon: "🛡️" },
				{ cls: "sd-th-azure", defaultIcon: "⭐" },
				{ cls: "sd-th-teal", defaultIcon: "👍" },
				{ cls: "sd-th-forest", defaultIcon: "⏱️" },
				{ cls: "sd-th-amber", defaultIcon: "⚠️" },
				{ cls: "sd-th-rose", defaultIcon: "🛒" },
				{ cls: "sd-th-violet", defaultIcon: "🔍" },
				{ cls: "sd-th-lime", defaultIcon: "💎" },
				{ cls: "sd-th-olive", defaultIcon: "🏷️" },
			];

			const getColumnIcon = (col, idx) => {
				const s = `${col.label || ""} ${col.fieldname || ""}`.toLowerCase();
				if (/customer|client|organization|party/.test(s)) return "🏢";
				if (/project|task|operation|work_order|wo/.test(s)) return "📋";
				if (/item|part|product|material|bom/.test(s)) return "📦";
				if (/status|state|workflow/.test(s)) return "🛡️";
				if (/date|time|schedule|due/.test(s)) return "📅";
				if (/qty|quantity|count|delivered|produced/.test(s)) return "⏱️";
				if (/amount|cost|price|total|value|rate|curr|balance|tax/.test(s)) return "💰";
				if (/percent|pct|progress|compl/.test(s)) return "⭐";
				if (/warehouse|location/.test(s)) return "🏬";
				if (/supplier|vendor/.test(s)) return "🤝";
				if (/user|manager|assign|owner/.test(s)) return "👤";
				return PIN_THEMES[idx % PIN_THEMES.length].defaultIcon;
			};

			let formHtml = `
        <div class="sd-modal-form-view">
          <!-- Top Action & Navigation Bar -->
          <div class="sd-modal-form-header">
            <div class="sd-modal-form-header-left">
              ${
					onBackCallback
						? `<button type="button" class="sd-button sd-modal-form-back-btn">← Back to Records List</button>`
						: ""
				}
              <div class="sd-modal-form-title-badge">
                <span class="sd-form-doctype-tag">${this.esc(doctype)}</span>
                <h3 class="sd-form-docname-title">${this.esc(name)}</h3>
              </div>
            </div>
            <div class="sd-modal-form-header-right">
              ${status ? this.badge(status) : ""}
              <span class="sd-pill sd-status-blue">${this.esc(
					row.company || this.filters.company || "SarathiAILabs"
				)}</span>
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
							? `<a href="javascript:void(0)" class="sd-modal-nested-link" data-doctype="${this.esc(
									c.options
							  )}" data-name="${this.esc(val)}">${this.esc(val)} ↗</a>`
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
                <div class="sd-color-table-wrapper sd-modal-table-scroll sd-modal-nested-table-wrap">
                  <table class="sd-color-table sd-modal-table sd-modal-nested-table" aria-label="${this.esc(
						rel.title
					)} Table">
                    <thead>
                      <tr class="sd-color-table-header-row">
                        ${rel.columns
							.map((rc, ci) => {
								const theme = PIN_THEMES[ci % PIN_THEMES.length];
								const pinIcon = getColumnIcon(rc, ci);
								return `
                          <th class="sd-th-pin ${theme.cls}">
                            <div class="sd-pin-badge">
                              <span class="sd-pin-icon">${pinIcon}</span>
                              <span class="sd-pin-text">${this.esc(rc.label)}</span>
                            </div>
                          </th>
                        `;
							})
							.join("")}
                        <th class="sd-th-pin sd-th-olive" style="width: 120px; text-align: center;">
                          <div class="sd-pin-badge">
                            <span class="sd-pin-icon">⚡</span>
                            <span class="sd-pin-text">Action</span>
                          </div>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      ${rel.rows
							.map((rrow, ri) => {
								const rname = rrow.name || rrow.parent || "";
								const rdt = rrow.doctype || rel.doctype || "";
								const isEvenRow = ri % 2 === 0;
								const firstRelCol = rel.columns[0];
								const firstRelVal = firstRelCol
									? rrow[firstRelCol.fieldname] ?? rname
									: rname;
								const rPrimary =
									rrow.project_name ||
									rrow.customer_name ||
									rrow.item_name ||
									firstRelVal ||
									rname ||
									"—";
								const rSub = rPrimary !== rname && rname ? rname : rdt || "";
								const rInitials =
									String(rPrimary)
										.replace(/[^a-zA-Z0-9]/g, "")
										.slice(0, 2)
										.toUpperCase() || "ID";
								return `
                          <tr class="sd-color-tr ${
								isEvenRow ? "sd-tr-even" : "sd-tr-odd"
							}" data-name="${this.esc(rname)}" data-doctype="${this.esc(rdt)}">
                            <td class="sd-td-ribbon">
                              <div class="sd-row-ribbon ${
									ri % 2 === 0 ? "sd-ribbon-purple" : "sd-ribbon-plum"
								}">
                                <div class="sd-ribbon-box">
                                  <span class="sd-ribbon-initials">${this.esc(rInitials)}</span>
                                </div>
                                <div class="sd-ribbon-content">
                                  <strong class="sd-ribbon-name" title="${this.esc(rPrimary)}">${this.esc(
									rPrimary
								)}</strong>
                                  ${
										rSub
											? `<span class="sd-ribbon-sub" title="${this.esc(
													rSub
											  )}">${this.esc(rSub)}</span>`
											: ""
									}
                                </div>
                                <div class="sd-ribbon-chevron"></div>
                              </div>
                            </td>
                            ${rel.columns
								.slice(1)
								.map(
									(rc) =>
										`<td class="sd-td-cell">${this.formatCellValue(
											rc,
											rrow[rc.fieldname]
										)}</td>`
								)
								.join("")}
                            <td class="sd-td-cell sd-td-action" style="text-align: center; white-space: nowrap;">
                              ${
									rname
										? `<button type="button" class="sd-row-action-btn sd-btn-xs sd-modal-nested-btn" data-doctype="${this.esc(
												rdt
										  )}" data-name="${this.esc(rname)}">Inspect ➔</button>`
										: "—"
								}
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
          `
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
			$container.on("click", ".sd-modal-nested-link, .sd-modal-nested-btn", (e) => {
				const $el = $(e.target).closest("[data-name]");
				const ndt = $el.attr("data-doctype");
				const nname = $el.attr("data-name");
				if (ndt && nname) {
					this.showRecordFormModal(targetDialog, ndt, nname, () => {
						this.showRecordFormModal(targetDialog, doctype, name, onBackCallback);
					});
				}
			});
		} catch (err) {
			$container.html(
				`<div class="sd-empty">Unable to load form details for ${this.esc(doctype)} ${this.esc(
					name
				)}. ${this.esc(err.message || "")}</div>`
			);
		}
	}

	filterTable(tableId) {
		const table = this.root.querySelector(`table[data-table-id="${tableId}"]`);
		if (!table) return;
		const searchInput = this.root.querySelector(`input[data-table-search="${tableId}"]`);
		const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
		const activePill = this.root.querySelector(
			`[data-table-filters="${tableId}"] .sd-filter-pill.active`
		);
		const filter = activePill ? activePill.dataset.tableFilter : "all";

		const rows = table.querySelectorAll("tbody tr");
		let visibleCount = 0;
		rows.forEach((row) => {
			const textMatch = !query || row.textContent.toLowerCase().includes(query);
			let filterMatch = true;

			if (filter !== "all") {
				if (tableId === "customers") {
					if (filter === "active") filterMatch = row.dataset.active === "yes";
					else if (filter === "orders") filterMatch = row.dataset.orders === "yes";
					else if (filter === "delayed") filterMatch = row.dataset.delayed === "yes";
				} else if (tableId === "projects") {
					if (filter === "in_progress")
						filterMatch = (row.dataset.projectStatus || "").toLowerCase() === "in progress";
					else if (filter === "completed")
						filterMatch = (row.dataset.projectStatus || "").toLowerCase() === "completed";
					else if (filter === "delayed") filterMatch = row.dataset.delayed === "yes";
				} else if (tableId === "health") {
					if (filter === "in_progress")
						filterMatch = (row.dataset.healthStatus || "").toLowerCase() === "in progress";
					else if (filter === "shortages") filterMatch = row.dataset.shortages === "yes";
					else if (filter === "delayed") filterMatch = row.dataset.delayed === "yes";
				} else if (tableId === "pipelines") {
					if (filter === "active") filterMatch = row.dataset.wo === "yes";
					else if (filter === "inspections") filterMatch = row.dataset.insp === "yes";
					else if (filter === "deliveries") filterMatch = row.dataset.del === "yes";
				}
			}

			const visible = textMatch && filterMatch;
			row.style.display = visible ? "" : "none";
			if (visible) visibleCount++;
		});

		const countBadge = this.root.querySelector(`[data-table-count="${tableId}"]`);
		if (countBadge) countBadge.textContent = visibleCount;
	}

	click(event) {
		const pill = event.target.closest(".sd-filter-pill");
		if (pill) {
			const group = pill.closest("[data-table-filters]");
			if (group) {
				group.querySelectorAll(".sd-filter-pill").forEach((p) => p.classList.remove("active"));
				pill.classList.add("active");
				const tableId = group.dataset.tableFilters;
				this.filterTable(tableId);
			}
			return;
		}
		const b = event.target.closest(
			"button, .sd-setup-card, .sd-card, .sd-color-tr, a.sd-record-link, a[data-inspect], .sd-health-metric, .sd-pipeline-step, [data-customer], [data-project], [data-action]"
		);
		if (!b || b.disabled) return;
		const d = b.dataset;
		if (d.inspect) {
			event.preventDefault();
			this.showRecordFormModal(null, d.doctype, d.inspect);
		} else if (d.action === "toggle-customer-view") {
			this.customerViewMode = d.mode || (this.customerViewMode === "table" ? "cards" : "table");
			this.customerPage = 0;
			this.renderCards();
		} else if (d.action === "toggle-project-view") {
			this.projectViewMode = d.mode || (this.projectViewMode === "table" ? "cards" : "table");
			this.projectPage = 0;
			this.renderCards();
		} else if (d.action === "toggle-ai") this.toggleAiChat();
		else if (d.action === "switch-owner") frappe.set_route("sarathiownertower");
		else if (d.action === "apply-dates") this.applyDateFilter();
		else if (d.action === "clear-dates") this.clearDateFilter();
		else if (d.action === "open-subcontracting") this.openSubcontractingView();
		else if (d.action === "close-subcontracting") this.closeSubcontractingView();
		else if (d.action === "refresh-subcontracting") this.loadSubcontractingData();
		else if (d.action === "apply-sub-filters") this.applySubFilters();
		else if (d.action === "reset-sub-filters") this.resetSubFilters();
		else if (d.action === "open-accounting") this.openAccountingView();
		else if (d.action === "close-accounting") this.closeAccountingView();
		else if (d.action === "refresh-accounting") this.loadAccountingData();
		else if (d.action === "apply-acc-filters") this.applyAccFilters();
		else if (d.action === "reset-acc-filters") this.resetAccFilters();
		else if (d.action === "reset-kpi-selection") {
			this.accActiveKpi = "";
			this.accTab = "overview";
			this.renderAccountingDetailView();
		} else if (d.action === "open-kpi-records") {
			this.showCardDetailsModal(d.report, d.subset || "", d.label || "");
		} else if (d.accKpi) this.selectAccKpi(d.accKpi, d.accTargetTab, d.accFocus);
		else if (d.accPeriod) this.setAccPeriod(d.accPeriod);
		else if (d.accTab) this.setAccTab(d.accTab);
		else if (d.quickDate) this.setQuickDate(d.quickDate);
		else if (d.costGranularity) this.setCostGranularity(d.costGranularity);
		else if (d.pipeStage) this.setPipeStage(d.pipeStage);
		else if (d.subStatusFilter) this.setSubStatusFilter(d.subStatusFilter);
		else if (d.subSupplierFilter) this.setSubSupplierFilter(d.subSupplierFilter);
		else if (d.subProjectFilter) this.setSubProjectFilter(d.subProjectFilter);
		else if (d.subOrdersPage !== undefined) {
			this.subOrdersPage = Number(d.subOrdersPage);
			this.renderSubOrdersTable();
		} else if (d.subMaterialsPage !== undefined) {
			this.subMaterialsPage = Number(d.subMaterialsPage);
			this.renderSubMaterialsTable();
		} else if (d.action === "clear-stage-filter") {
			this.subSelectedStage = "";
			this.renderSubcontractingDetailView();
		} else if (d.customer) this.navigate({ customer: d.customer, project: "" });
		else if (d.project) this.navigate({ project: d.project });
		else if (d.nav)
			this.navigate(d.nav === "organization" ? { customer: "", project: "" } : { project: "" });
		else if (d.tab) {
			this.tab = d.tab;
			this.reportState = null;
			this.writeUrl();
			this.renderTabs();
			this.renderContent();
		} else if (d.report) {
			let cardLabel = d.kpiLabel;
			if (!cardLabel) {
				const labelText =
					b.querySelector(".sd-metric-label")?.textContent?.trim() ||
					b.querySelector("small")?.textContent?.trim() ||
					b.querySelector("h3")?.textContent?.trim() ||
					b.textContent?.trim() ||
					"";
				if (!/^\d+$/.test(labelText) && labelText.length > 2) {
					cardLabel = labelText;
				}
			}
			this.showCardDetailsModal(d.report, d.subset || "", cardLabel, d.reportProject);
		} else if (d.scopeSubset !== undefined) {
			this.reportState.subset = d.scopeSubset;
			this.reportState.start = 0;
			this.renderContent();
		} else if (d.new) {
			this.create(d.new);
		} else if (d.action === "clear-project-setup") {
			this.navigate({ project: "", customer: "" });
		} else if (d.page) {
			this[`${d.page}Page`] = Number(d.index);
			this.renderCards();
		} else if (d.reportPage !== undefined) {
			this.reportState.start = Number(d.reportPage);
			this.loadReport();
		} else if (d.action === "refresh") this.load();
		else if (d.action === "create" || d.action === "setup") this.creationMenu(d.action === "setup");
		else if (d.action === "associate") this.create("Sarathi Customer Organization");
		else if (d.action === "native-report") {
			frappe.route_options = {
				...this.filters,
				customer: this.filters.customer === "__unassigned__" ? "" : this.filters.customer,
				unassigned_customer: this.filters.customer === "__unassigned__" ? 1 : 0,
				report_type: this.data.reports.find((r) => r.key === this.reportState.report).title,
				subset: this.reportState.subset,
				search: this.reportState.search,
			};
			frappe.set_route("query-report", "Sarathi Industrial Analysis");
		} else if (d.action === "export") {
			const q = new URLSearchParams({
				filters: JSON.stringify(this.filters),
				...this.reportState,
			});
			window.open(
				`/api/method/sarathi_visibility.api.dashboard.export_report?${q}`,
				"_blank",
				"noopener"
			);
		}
	}
	async inspect(doctype, name) {
		const dialog = new frappe.ui.Dialog({
			title: `${doctype} · ${name}`,
			size: "extra-large",
			fields: [{ fieldname: "detail", fieldtype: "HTML" }],
			primary_action_label: "Open in ERPNext",
			primary_action: () => {
				dialog.hide();
				frappe.set_route("Form", doctype, name);
			},
		});
		dialog.fields_dict.detail.$wrapper.html(this.empty("Loading linked records…"));
		dialog.$wrapper.addClass("sd-dashboard-dialog");
		dialog.show();
		try {
			const data = await this.call("get_record", {
				filters: JSON.stringify(this.filters),
				doctype,
				name,
			});
			const table = (columns, rows) =>
				`<div class="sd-table-wrap"><table class="sd-table"><thead><tr>${columns
					.map((c) => `<th>${this.esc(c.label)}</th>`)
					.join("")}</tr></thead><tbody>${rows
					.map(
						(r) =>
							`<tr>${columns
								.map(
									(c) =>
										`<td>${this.cell({ ...c, fieldname: c.fieldname }, r).replace(
											/ <button.*?<\/button>/g,
											""
										)}</td>`
								)
								.join("")}</tr>`
					)
					.join("")}</tbody></table></div>`;
			dialog.fields_dict.detail.$wrapper.html(
				`<div class="sd-detail"><div class="sd-detail-fields">${data.columns
					.map(
						(c) =>
							`<div><small>${this.esc(c.label)}</small><strong>${this.cell(c, data.row).replace(
								/ <button.*?<\/button>/g,
								""
							)}</strong></div>`
					)
					.join("")}</div>${data.related
					.map(
						(r) =>
							`<h4>${this.esc(r.title)} (${r.total})</h4>${
								r.total ? table(r.columns, r.rows) : this.empty()
							}${
								r.total > 100
									? "<p>First 100 records. Open the full report for all records.</p>"
									: ""
							}`
					)
					.join("")}</div>`
			);
		} catch (e) {
			dialog.fields_dict.detail.$wrapper.html(
				this.empty("Unable to open this record in the current selection.")
			);
		}
	}
	creationMenu(setup) {
		if (!this.data) return;
		const types = setup
			? [
					"Company",
					"Item",
					"Warehouse",
					"Operation",
					"Workstation Type",
					"Workstation",
					"Plant Floor",
					"Routing",
					"Supplier",
			  ]
			: [
					"Customer",
					"Project",
					"BOM",
					"Sales Order",
					"Production Plan",
					"Material Request",
					"Work Order",
					"Pick List",
					"Stock Entry",
					"Job Card",
					"Purchase Order",
					"Purchase Receipt",
					"Purchase Invoice",
					"Delivery Note",
					"Sales Invoice",
			  ];
		const dialog = new frappe.ui.Dialog({
			title: setup ? "Organization setup" : "Create in this selection",
			fields: [{ fieldname: "actions", fieldtype: "HTML" }],
		});
		dialog.fields_dict.actions.$wrapper.html(
			`<p>${this.esc(
				this.filters.company || "Choose an organization for linked records"
			)}</p><div class="sd-create-grid">${types
				.filter((dt) => this.data.can_create[dt])
				.map((dt) => `<button class="sd-button" data-new="${dt}">${dt}</button>`)
				.join("")}</div>`
		);
		dialog.fields_dict.actions.$wrapper.on("click", "[data-new]", (e) => {
			dialog.hide();
			this.create(e.currentTarget.dataset.new);
		});
		dialog.$wrapper.addClass("sd-dashboard-dialog");
		dialog.show();
	}
	create(doctype) {
		const f = this.filters,
			p = this.data?.selected_project;
		if (["Project", "Sarathi Customer Organization"].includes(doctype) && !f.company)
			return frappe.msgprint("Choose an organization first.");
		if (doctype === "Project" && (!f.customer || f.customer === "__unassigned__"))
			return frappe.msgprint("Choose a customer before creating a manufacturing project.");
		if (
			[
				"BOM",
				"Sales Order",
				"Work Order",
				"Material Request",
				"Stock Entry",
				"Pick List",
				"Job Card",
				"Purchase Order",
				"Purchase Receipt",
				"Purchase Invoice",
				"Delivery Note",
				"Sales Invoice",
			].includes(doctype) &&
			!f.project
		)
			return frappe.msgprint("Choose a project first so the new record is linked correctly.");
		if (["Job Card", "Stock Entry", "Pick List"].includes(doctype)) {
			frappe.msgprint(
				`Open the project's Work Order to create a linked ${doctype} using ERPNext's workflow.`
			);
			this.openReport("work_orders");
			return;
		}
		const values = { company: f.company };
		if (f.customer && f.customer !== "__unassigned__") values.customer = f.customer;
		if (doctype === "Project") values.custom_sarathi_manufacturing = 1;
		else if (doctype === "BOM") values.custom_sarathi_project = f.project;
		else if (
			[
				"Sales Order",
				"Work Order",
				"Material Request",
				"Purchase Order",
				"Purchase Receipt",
				"Purchase Invoice",
				"Delivery Note",
				"Sales Invoice",
			].includes(doctype)
		)
			values.project = f.project;
		if (doctype === "Work Order") {
			if (!p?.custom_sarathi_bom)
				return frappe.msgprint("Assign an active, submitted main BOM on the Project first.");
			values.bom_no = p.custom_sarathi_bom;
			values.production_item = p.main_item;
			values.sales_order = p.sales_order;
		}
		if (doctype === "Customer") values.customer_type = "Company";
		frappe.model.with_doctype(doctype, () => {
			const fields = new Set(frappe.get_meta(doctype).fields.map((x) => x.fieldname));
			const defaults = Object.fromEntries(
				Object.entries(values).filter(([k, v]) => fields.has(k) && v !== "" && v != null)
			);
			// Use the full native form so relation validation and after-save linking always run.
			frappe.route_options = defaults;
			const doc = frappe.model.get_new_doc(doctype);
			Object.assign(doc, defaults);
			if (doctype === "Material Request")
				sessionStorage.setItem(
					"sarathi_material_request_project",
					JSON.stringify({ docname: doc.name, project: f.project })
				);
			if (doctype === "Customer")
				sessionStorage.setItem(
					"sarathi_new_customer_company",
					JSON.stringify({ company: f.company, docname: doc.name })
				);
			frappe.set_route("Form", doctype, doc.name);
		});
	}

	formatCompact(v, prefix = "₹") {
		const n = Number(v || 0);
		const sign = n < 0 ? "-" : "";
		const abs = Math.abs(n);
		if (abs >= 10000000) return `${sign}${prefix}${(abs / 10000000).toFixed(2)} Cr`;
		if (abs >= 100000) return `${sign}${prefix}${(abs / 100000).toFixed(2)} L`;
		if (abs >= 1000) return `${sign}${prefix}${(abs / 1000).toFixed(1)} k`;
		return `${sign}${prefix}${abs.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
	}

	renderSubcontractingCard() {
		const container = this.el("[data-subcontracting-cards]");
		if (!container) return;
		const s = this.data?.subcontracting_summary || {
			active_subcontracts: 0,
			material_with_suppliers: 0,
			pending_subcontracts: 0,
			currency: "INR",
		};
		const sym = s.currency === "INR" ? "₹" : s.currency ? s.currency + " " : "₹";
		container.innerHTML = `
      <button class="sd-card sd-subcontracting-main-card" data-action="open-subcontracting" title="Click to open Subcontracting Control Tower">
        <span class="sd-card-icon">${this.workspaceIcon("subcontract")}</span>
        <h3>Subcontracting</h3>
        <div>
          <span class="sd-pill sd-status-blue">${s.active_subcontracts} Active</span>
          <span class="sd-pill sd-status-amber">${s.pending_subcontracts} Pending</span>
        </div>
        <p><b>${s.active_subcontracts}</b> Active Subcontracts · <b>${
			s.pending_subcontracts
		}</b> Pending Delivery</p>
        <p class="sd-sub-card-mat">Material with Suppliers: <b>${this.formatCompact(
			s.material_with_suppliers,
			sym
		)}</b></p>
        <small>Open Subcontracting Control Tower →</small>
      </button>
    `;
	}

	showSubcontractingView(silent = false) {
		const hideSelectors = [
			".sd-hero",
			".sd-controls",
			".sd-breadcrumb",
			".sd-scope-note",
			".sd-kpis",
			"[data-live-projects]",
			"[data-subcontracting-card-panel]",
			"[data-accounting-card-panel]",
			"[data-customer-panel]",
			"[data-project-panel]",
			"[data-project-summary]",
			".sd-tabs",
			"[data-content]",
		];
		hideSelectors.forEach((sel) => {
			const n = this.el(sel);
			if (n) n.hidden = true;
		});
		const viewEl = this.el("[data-subcontracting-view]");
		if (viewEl) viewEl.hidden = false;
		if (this.filters.company && !this.subFilters.company) this.subFilters.company = this.filters.company;
		if (this.filters.project && !this.subFilters.project) this.subFilters.project = this.filters.project;
		this.loadSubcontractingData(silent);
	}

	hideSubcontractingView() {
		const viewEl = this.el("[data-subcontracting-view]");
		if (viewEl) viewEl.hidden = true;
		const showSelectors = [
			".sd-hero",
			".sd-controls",
			".sd-breadcrumb",
			".sd-scope-note",
			".sd-kpis",
			"[data-live-projects]",
			"[data-subcontracting-card-panel]",
			"[data-accounting-card-panel]",
			".sd-tabs",
			"[data-content]",
		];
		showSelectors.forEach((sel) => {
			const n = this.el(sel);
			if (n) n.hidden = false;
		});
		if (this.el("[data-customer-panel]"))
			this.el("[data-customer-panel]").hidden = !!this.filters.customer || !!this.filters.project;
		if (this.el("[data-project-panel]")) this.el("[data-project-panel]").hidden = !!this.filters.project;
		if (this.el("[data-project-summary]"))
			this.el("[data-project-summary]").hidden = !this.filters.project;
	}

	openSubcontractingView() {
		this.view = "subcontracting";
		this.writeUrl();
		this.showSubcontractingView();
		window.scrollTo({ top: 0, behavior: "smooth" });
	}

	closeSubcontractingView() {
		this.view = "";
		this.writeUrl();
		this.hideSubcontractingView();
		window.scrollTo({ top: 0, behavior: "smooth" });
		if (!this.data) {
			this.load();
		}
	}

	subFilterChanged(target) {
		this.subFilters[target.dataset.subFilter] = target.value;
	}

	applySubFilters() {
		for (const sel of ["company", "supplier", "project", "status", "from_date", "to_date"]) {
			const inp = this.el(`[data-sub-filter="${sel}"]`);
			if (inp) this.subFilters[sel] = inp.value;
		}
		this.subOrdersPage = 0;
		this.subMaterialsPage = 0;
		this.loadSubcontractingData();
	}

	resetSubFilters() {
		this.subFilters = {
			cost_granularity: "monthly",
			company: "",
			supplier: "",
			project: "",
			status: "",
			from_date: "",
			to_date: "",
		};
		this.subSearch = "";
		this.subSelectedStage = "";
		this.subSelectedStatus = "";
		this.subOrdersPage = 0;
		this.subMaterialsPage = 0;
		this.loadSubcontractingData();
	}

	setQuickDate(period) {
		const now = new Date();
		const pad = (n) => String(n).padStart(2, "0");
		const format = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
		const todayStr = format(now);
		let from = "",
			to = todayStr;
		if (period === "today") {
			from = todayStr;
		} else if (period === "this_week") {
			const day = now.getDay() || 7;
			const mon = new Date(now);
			mon.setDate(now.getDate() - day + 1);
			from = format(mon);
		} else if (period === "this_month") {
			from = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-01`;
		} else if (period === "this_quarter") {
			const qMonth = Math.floor(now.getMonth() / 3) * 3 + 1;
			from = `${now.getFullYear()}-${pad(qMonth)}-01`;
		} else if (period === "this_year") {
			from = `${now.getFullYear()}-01-01`;
		} else if (period === "all") {
			from = "";
			to = "";
		}
		this.subFilters.from_date = from;
		this.subFilters.to_date = to;
		this.loadSubcontractingData();
	}

	setCostGranularity(granularity) {
		this.subFilters.cost_granularity = granularity;
		this.loadSubcontractingData();
	}

	setPipeStage(stage) {
		this.subSelectedStage = this.subSelectedStage === stage ? "" : stage;
		this.subOrdersPage = 0;
		this.renderSubcontractingDetailView();
	}

	setSubStatusFilter(status) {
		this.subSelectedStatus = this.subSelectedStatus === status ? "" : status;
		this.subOrdersPage = 0;
		this.renderSubcontractingDetailView();
	}

	setSubSupplierFilter(supplier) {
		this.subFilters.supplier = supplier;
		this.subOrdersPage = 0;
		this.loadSubcontractingData();
	}

	setSubProjectFilter(project) {
		this.subFilters.project = project;
		this.subOrdersPage = 0;
		this.loadSubcontractingData();
	}

	async loadSubcontractingData(silent = false) {
		const viewEl = this.el("[data-subcontracting-view]");
		if (!viewEl) return;
		if (!silent && !this.subData) {
			viewEl.innerHTML = `<div class="sd-sub-loading"><div class="sd-sub-spinner"></div><span>Loading Subcontracting Control Tower…</span></div>`;
		}
		try {
			const res = await frappe.call({
				method: "sarathi_visibility.api.subcontracting.get_subcontracting_dashboard",
				args: { filters: JSON.stringify(this.subFilters) },
				silent: true,
			});
			this.subData = res.message;
			this.renderSubcontractingDetailView();
		} catch (err) {
			console.error("Subcontracting load error:", err);
			viewEl.innerHTML = `
        <div class="sd-sub-error">
          <h3>Unable to load Subcontracting Control Tower</h3>
          <p>Please ensure you have read permissions for Subcontracting Order and Stock Entry.</p>
          <button class="sd-button" data-action="close-subcontracting">← Back to Dashboard</button>
          <button class="sd-button sd-primary" data-action="refresh-subcontracting">↻ Try Again</button>
        </div>
      `;
		}
	}

	renderSubcontractingDetailView() {
		const viewEl = this.el("[data-subcontracting-view]");
		if (!viewEl || !this.subData) return;
		const d = this.subData;
		const f = this.subFilters;
		const sym = d.currency === "INR" ? "₹" : d.currency ? d.currency + " " : "₹";
		const k = d.kpis || {};

		const companies = this.data?.companies || [];
		const suppliers = d.suppliers || [];
		const projects = d.projects || [];

		const statusOptions = [
			"",
			"Draft",
			"Open",
			"Material Transferred",
			"Partial Material Transferred",
			"Partially Received",
			"Completed",
			"Closed",
			"Cancelled",
		];

		viewEl.innerHTML = `
      <header class="sd-sub-header">
        <div class="sd-sub-header-left">
          <button class="sd-button sd-sub-back-btn" data-action="close-subcontracting" title="Return to Main Dashboard">
            ← Back to Dashboard
          </button>
          <div class="sd-sub-title-group">
            <div class="sd-eyebrow">SARATHI INDUSTRIAL CONTROL TOWER · OPERATIONS</div>
            <h1>🔧 Subcontracting Control Tower</h1>
            <p>Outsourced manufacturing tracking, supplier materials, PO links, quality inspections and reconciliation</p>
          </div>
        </div>
        <div class="sd-sub-header-right">
          <span class="sd-sub-live-indicator"><span class="sd-sub-live-dot"></span> Live ERPNext Data</span>
          <button class="sd-button sd-sub-refresh-btn" data-action="refresh-subcontracting" title="Refresh Live Data">
            🔄 Refresh
          </button>
        </div>
      </header>

      <section class="sd-controls sd-sub-controls" aria-label="Subcontracting filters">
        <label>Organization
          <select data-sub-filter="company" aria-label="Organization">
            <option value="">All organizations</option>
            ${companies
				.map(
					(c) =>
						`<option value="${this.esc(c.name)}" ${
							f.company === c.name ? "selected" : ""
						}>${this.esc(c.company_name || c.name)}</option>`
				)
				.join("")}
          </select>
        </label>
        <label>Supplier
          <select data-sub-filter="supplier" aria-label="Supplier">
            <option value="">All Suppliers</option>
            ${suppliers
				.map(
					(s) =>
						`<option value="${this.esc(s.name)}" ${
							f.supplier === s.name ? "selected" : ""
						}>${this.esc(s.supplier_name || s.name)}</option>`
				)
				.join("")}
          </select>
        </label>
        <label>Project
          <select data-sub-filter="project" aria-label="Project">
            <option value="">All Projects</option>
            ${projects
				.map(
					(p) =>
						`<option value="${this.esc(p.name)}" ${
							f.project === p.name ? "selected" : ""
						}>${this.esc(p.project_name || p.name)}</option>`
				)
				.join("")}
          </select>
        </label>
        <label>Status
          <select data-sub-filter="status" aria-label="Status">
            ${statusOptions
				.map(
					(st) =>
						`<option value="${this.esc(st)}" ${f.status === st ? "selected" : ""}>${
							st || "All Statuses"
						}</option>`
				)
				.join("")}
          </select>
        </label>
        <label>From date
          <input type="date" data-sub-filter="from_date" value="${this.esc(
				f.from_date
			)}" aria-label="From date">
        </label>
        <label>To date
          <input type="date" data-sub-filter="to_date" value="${this.esc(f.to_date)}" aria-label="To date">
        </label>
        <label class="sd-search">Search
          <input type="search" data-sub-search value="${this.esc(
				this.subSearch
			)}" placeholder="Search orders, suppliers, items…" aria-label="Search subcontracting">
        </label>
        <button class="sd-button sd-primary" data-action="apply-sub-filters">Apply Filters</button>
        <button class="sd-button" data-action="reset-sub-filters">Reset</button>
      </section>

      <div class="sd-sub-quick-filters">
        <span class="sd-sub-quick-label">Quick Filters:</span>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="today">Today</button>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="this_week">This Week</button>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="this_month">This Month</button>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="this_quarter">This Quarter</button>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="this_year">This Year</button>
        <button class="sd-button sd-sub-quick-pill" data-quick-date="all">All</button>
      </div>

      <section class="sd-kpis sd-sub-kpis" aria-label="Subcontracting KPIs">
        <div class="sd-kpi sd-tone-0">
          <span>Total Subcontract Orders</span>
          <strong>${this.num(k.total_subcontract_orders || 0)}</strong>
          <small>All registered orders</small>
        </div>
        <div class="sd-kpi sd-tone-1">
          <span>Active / In-Progress Orders</span>
          <strong>${this.num(k.active_orders || 0)}</strong>
          <small>Currently in processing</small>
        </div>
        <div class="sd-kpi sd-tone-2">
          <span>Material Value at Subcontractors</span>
          <strong>${this.formatCompact(k.material_value_at_subcontractors, sym)}</strong>
          <small>Raw material in supplier field</small>
        </div>
        <div class="sd-kpi sd-tone-3">
          <span>Pending Scrap / Reconciliation</span>
          <strong>${this.num(k.pending_scrap_reconciliation || 0)}</strong>
          <small>Items pending return or write-off</small>
        </div>
        <div class="sd-kpi sd-tone-4">
          <span>Orders Pending Delivery</span>
          <strong>${this.num(k.orders_pending_delivery || 0)}</strong>
          <small>Awaiting finished goods receipt</small>
        </div>
        <div class="sd-kpi sd-tone-5">
          <span>On-Time Delivery Rate</span>
          <strong>${this.esc(k.on_time_delivery_rate || "100%")}</strong>
          <small>Receipts before required date</small>
        </div>
        <div class="sd-kpi sd-tone-1">
          <span>Total Subcontracting Spend</span>
          <strong>${this.formatCompact(k.total_subcontracting_spend, sym)}</strong>
          <small>Service + consumed material</small>
        </div>
        <div class="sd-kpi sd-tone-0">
          <span>Rejected / Rework Quantity</span>
          <strong>${this.num(k.rejected_rework_quantity || 0)}</strong>
          <small>Units failed inspection</small>
        </div>
      </section>

      <section class="sd-panel sd-sub-pipeline-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Subcontracting Pipeline & Lifecycle</h2>
            <p>Interactive tracking across all 7 manufacturing stages · Click stage to filter orders</p>
          </div>
          ${
				this.subSelectedStage
					? `<button class="sd-text-button" data-action="clear-stage-filter">Clear Stage Filter (${this.esc(
							this.subSelectedStage
					  )})</button>`
					: ""
			}
        </div>
        <div class="sd-sub-pipeline-flow">
          ${(d.pipeline || [])
				.map(
					(p, idx) => `
            <button class="sd-sub-pipe-node ${
				this.subSelectedStage === p.key ? "active" : ""
			}" data-pipe-stage="${this.esc(p.key)}" title="${this.esc(p.description)}">
              <div class="sd-sub-pipe-head">
                <span class="sd-sub-pipe-num">${idx + 1}</span>
                <span class="sd-sub-pipe-label">${this.esc(p.label)}</span>
              </div>
              <strong class="sd-sub-pipe-count">${this.num(p.count)}</strong>
              <small class="sd-sub-pipe-desc">${this.esc(p.description)}</small>
            </button>
            ${
				idx < (d.pipeline || []).length - 1
					? '<div class="sd-sub-pipe-arrow"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></div>'
					: ""
			}
          `
				)
				.join("")}
        </div>
      </section>

      <div class="sd-sub-grid-2">
        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Subcontracting Status Breakdown</h2>
              <p>Distribution of orders across operational lifecycle statuses</p>
            </div>
            ${
				this.subSelectedStatus
					? `<button class="sd-text-button" data-action="clear-status-filter">Clear Status Filter (${this.esc(
							this.subSelectedStatus
					  )})</button>`
					: ""
			}
          </div>
          ${this.renderSubDonutChart(d.status_distribution || { labels: [], values: [] })}
        </article>

        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Subcontracting Cost Trends</h2>
              <p>Service cost and raw material expenditure over time</p>
            </div>
            <div class="sd-sub-granularity-toggle">
              <button class="sd-button ${
					f.cost_granularity === "daily" ? "active" : ""
				}" data-cost-granularity="daily">Daily</button>
              <button class="sd-button ${
					!f.cost_granularity || f.cost_granularity === "monthly" ? "active" : ""
				}" data-cost-granularity="monthly">Monthly</button>
              <button class="sd-button ${
					f.cost_granularity === "yearly" ? "active" : ""
				}" data-cost-granularity="yearly">Yearly</button>
            </div>
          </div>
          ${this.renderSubCostChart(
				d.cost_trends || { labels: [], total: [], service: [], material: [] },
				sym
			)}
        </article>
      </div>

      <div class="sd-sub-grid-2">
        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Supplier Subcontracting Analysis</h2>
              <p>Active workload, financial spend and overdue volume by supplier</p>
            </div>
          </div>
          <div class="sd-table-wrap">
            <table class="sd-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Orders</th>
                  <th>Completed</th>
                  <th>Overdue</th>
                  <th>Material Val</th>
                  <th>Service Cost</th>
                  <th>Total Spend</th>
                </tr>
              </thead>
              <tbody>
                ${
					(d.supplier_analysis || [])
						.map(
							(sa) => `
                  <tr class="sd-sub-clickable-row" data-sub-supplier-filter="${this.esc(
						sa.supplier
					)}" title="Click to filter by ${this.esc(sa.supplier)}">
                    <td><strong>${this.esc(sa.supplier)}</strong></td>
                    <td>${sa.orders}</td>
                    <td><span class="sd-pill sd-status-green">${sa.completed}</span></td>
                    <td>${sa.overdue ? `<span class="sd-pill sd-status-red">${sa.overdue}</span>` : "0"}</td>
                    <td>${this.formatCompact(sa.material_value, sym)}</td>
                    <td>${this.formatCompact(sa.service_cost, sym)}</td>
                    <td><strong>${this.formatCompact(sa.total_cost, sym)}</strong></td>
                  </tr>
                `
						)
						.join("") ||
					'<tr><td colspan="7" class="sd-empty">No supplier subcontracting records in this selection.</td></tr>'
				}
              </tbody>
            </table>
          </div>
        </article>

        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Project Subcontracting Analysis</h2>
              <p>Outsourced production tracking tied to manufacturing projects</p>
            </div>
          </div>
          <div class="sd-table-wrap">
            <table class="sd-table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Suppliers</th>
                  <th>Orders</th>
                  <th>Received Qty</th>
                  <th>Pending Qty</th>
                  <th>Total Cost</th>
                </tr>
              </thead>
              <tbody>
                ${
					(d.project_analysis || [])
						.map(
							(pa) => `
                  <tr class="sd-sub-clickable-row" data-sub-project-filter="${this.esc(
						pa.project
					)}" title="Click to filter by ${this.esc(pa.project)}">
                    <td><strong>${this.esc(pa.project)}</strong></td>
                    <td><small>${this.esc(pa.supplier)}</small></td>
                    <td>${pa.orders}</td>
                    <td>${this.num(pa.received)}</td>
                    <td>${this.num(pa.pending)}</td>
                    <td><strong>${this.formatCompact(pa.total_cost, sym)}</strong></td>
                  </tr>
                `
						)
						.join("") ||
					'<tr><td colspan="6" class="sd-empty">No project subcontracting records in this selection.</td></tr>'
				}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <section class="sd-panel" data-sub-materials-panel>
        <div class="sd-panel-heading">
          <div>
            <h2>Material With Subcontractors</h2>
            <p>Raw materials dispatched to supplier reserve warehouses awaiting consumption or return</p>
          </div>
        </div>
        <div data-sub-materials-table-area></div>
      </section>

      <section class="sd-panel" data-sub-orders-panel>
        <div class="sd-panel-heading">
          <div>
            <h2>Subcontracting Orders</h2>
            <p>Live registry of Subcontracting Orders with Purchase Order links, fulfillment and actions</p>
          </div>
        </div>
        <div data-sub-orders-table-area></div>
      </section>

      <div class="sd-sub-grid-2">
        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Overdue / Attention Required</h2>
              <p>Operational bottlenecks, delivery delays and pending dispatches</p>
            </div>
          </div>
          <div class="sd-table-wrap">
            <table class="sd-table">
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Supplier</th>
                  <th>Issue / Bottleneck</th>
                  <th>Delay</th>
                  <th>Severity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${
					(d.attention_required || [])
						.map((att) => {
							const isCrit = att.days_pending > 7 || att.issue.includes("Overdue");
							return `
                    <tr>
                      <td>${this.link("Subcontracting Order", att.subcontracting_order)}</td>
                      <td>${this.esc(att.supplier)}</td>
                      <td>${this.esc(att.issue)}</td>
                      <td>${att.days_pending ? `<b>${att.days_pending} d</b>` : "—"}</td>
                      <td><span class="sd-pill sd-status-${isCrit ? "red" : "amber"}">${
								isCrit ? "Critical" : "Attention"
							}</span></td>
                      <td><button class="sd-inspect" data-inspect="${this.esc(
							att.subcontracting_order
						)}" data-doctype="Subcontracting Order">Inspect</button></td>
                    </tr>
                  `;
						})
						.join("") ||
					'<tr><td colspan="6" class="sd-empty">No overdue orders or critical bottlenecks found.</td></tr>'
				}
              </tbody>
            </table>
          </div>
        </article>

        <article class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Supplier Performance</h2>
              <p>Vendor fulfillment velocity, average lead times and quality rating</p>
            </div>
          </div>
          <div class="sd-table-wrap">
            <table class="sd-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Orders</th>
                  <th>Completed</th>
                  <th>Overdue</th>
                  <th>Avg Lead Time</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                ${
					(d.supplier_performance || [])
						.map((sp) => {
							const rating =
								sp.overdue === 0 && sp.completed > 0
									? "Excellent"
									: sp.overdue > 2
									? "Needs Attention"
									: "Good";
							const rCol =
								rating === "Excellent" ? "green" : rating === "Good" ? "blue" : "red";
							return `
                    <tr>
                      <td><strong>${this.esc(sp.supplier)}</strong></td>
                      <td>${sp.total_orders}</td>
                      <td><span class="sd-pill sd-status-green">${sp.completed}</span></td>
                      <td>${
							sp.overdue ? `<span class="sd-pill sd-status-red">${sp.overdue}</span>` : "0"
						}</td>
                      <td>${this.esc(sp.average_processing_time)}</td>
                      <td><span class="sd-pill sd-status-${rCol}">${rating}</span></td>
                    </tr>
                  `;
						})
						.join("") ||
					'<tr><td colspan="6" class="sd-empty">No supplier performance history in this selection.</td></tr>'
				}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <section class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Live Subcontracting Activity</h2>
            <p>Real-time audit log of subcontracting transactions, dispatches and receipts</p>
          </div>
          <button class="sd-button" data-action="refresh-subcontracting">🔄 Refresh Feed</button>
        </div>
        <div class="sd-sub-activity-feed">
          ${
				(d.live_activity || [])
					.map((act) => {
						const icon =
							act.doctype === "Subcontracting Receipt"
								? "📦"
								: act.doctype === "Stock Entry"
								? "🚚"
								: "📄";
						return `
              <div class="sd-sub-activity-item">
                <span class="sd-sub-activity-icon">${icon}</span>
                <div class="sd-sub-activity-body">
                  <div class="sd-sub-activity-title">
                    <strong>${this.esc(act.activity)}</strong> · ${this.link(act.doctype, act.name)}
                  </div>
                  <div class="sd-sub-activity-meta">
                    <span>Supplier: <b>${this.esc(act.supplier)}</b></span>
                    ${act.project !== "—" ? `<span>· Project: <b>${this.esc(act.project)}</b></span>` : ""}
                  </div>
                </div>
                <time class="sd-sub-activity-time">${frappe.datetime.str_to_user(act.timestamp)}</time>
              </div>
            `;
					})
					.join("") || this.empty("No recent subcontracting activity recorded.")
			}
        </div>
      </section>
    `;

		// Render nested tables
		this.renderSubMaterialsTable();
		this.renderSubOrdersTable();

		// Attach search input listener
		const sInput = viewEl.querySelector("[data-sub-search]");
		if (sInput) {
			sInput.addEventListener("input", (e) => {
				this.subSearch = e.target.value.toLowerCase();
				this.subOrdersPage = 0;
				this.subMaterialsPage = 0;
				this.renderSubMaterialsTable();
				this.renderSubOrdersTable();
			});
		}
	}

	renderSubDonutChart(dist) {
		const labels = dist.labels || [];
		const values = dist.values || [];
		const total = values.reduce((a, b) => a + b, 0);
		if (!labels.length || total === 0) {
			return this.empty("No subcontracting orders for this chart.");
		}
		const statusPalette = {
			blue: "#2563eb",
			green: "#059669",
			violet: "#8b5cf6",
			orange: "#ea7041",
			amber: "#e39a14",
			red: "#dc4263",
		};
		const colors = labels.map((l) => statusPalette[this.statusColor(l)] || "#64748b");
		let offset = 0;
		const gradient = values
			.map((v, i) => {
				const start = offset;
				offset += (v / total) * 100;
				return `${colors[i]} ${start}% ${offset}%`;
			})
			.join(",");

		return `
      <div class="sd-donut-wrap">
        <div class="sd-donut" style="background:conic-gradient(${gradient})" role="img" aria-label="${this.esc(
			labels.map((l, i) => `${l}: ${values[i]}`).join(", ")
		)}">
          <span>${total}<small>Total Orders</small></span>
        </div>
        <div class="sd-chart-legend">
          ${labels
				.map(
					(l, i) => `
            <button class="sd-sub-legend-pill ${
				this.subSelectedStatus === l ? "active" : ""
			}" data-sub-status-filter="${this.esc(l)}">
              <i style="background:${colors[i]}"></i>${this.esc(l)} <b>${values[i]}</b> (${Math.round(
						(values[i] / total) * 100
					)}%)
            </button>
          `
				)
				.join("")}
        </div>
      </div>
    `;
	}

	renderSubCostChart(costTrends, sym) {
		const labels = costTrends.labels || [];
		const totals = costTrends.total || [];
		const services = costTrends.service || [];
		if (!labels.length) {
			return this.empty("No cost history available for this time window.");
		}
		const max = Math.max(100, ...totals);
		const n = labels.length;
		const getX = (i) => (n > 1 ? 40 + (i * 420) / (n - 1) : 250);
		const getY = (v) => 150 - (Math.max(0, v) / max) * 110;

		const totalPoints = totals.map((v, i) => `${getX(i)},${getY(v)}`).join(" ");
		const servicePoints = services.map((v, i) => `${getX(i)},${getY(v)}`).join(" ");

		return `
      <svg class="sd-line-chart" viewBox="0 0 500 185" role="img" aria-label="Subcontracting Cost Trends">
        <line x1="40" y1="40" x2="480" y2="40" stroke="#f1f5f9" stroke-dasharray="4"/>
        <line x1="40" y1="95" x2="480" y2="95" stroke="#f1f5f9" stroke-dasharray="4"/>
        <line x1="40" y1="150" x2="480" y2="150" stroke="#cbd5e1"/>

        <polyline points="${totalPoints}" fill="none" stroke="#2563eb" stroke-width="3"/>
        <polyline points="${servicePoints}" fill="none" stroke="#059669" stroke-width="2" stroke-dasharray="3"/>

        ${totals
			.map(
				(v, i) => `
          <circle cx="${getX(i)}" cy="${getY(v)}" r="4" fill="#2563eb">
            <title>${this.esc(labels[i])} Total Spend: ${this.formatCompact(v, sym)}</title>
          </circle>
        `
			)
			.join("")}

        <text x="40" y="175" font-size="11" fill="#64748b">${this.esc(labels[0])}</text>
        ${
			n > 2
				? `<text x="${getX(Math.floor(n / 2)) - 20}" y="175" font-size="11" fill="#64748b">${this.esc(
						labels[Math.floor(n / 2)]
				  )}</text>`
				: ""
		}
        <text x="420" y="175" font-size="11" fill="#64748b">${this.esc(labels[n - 1])}</text>
      </svg>
      <div class="sd-chart-legend">
        <span><i style="background:#2563eb"></i>Total Spend</span>
        <span><i style="background:#059669"></i>Service Cost</span>
      </div>
    `;
	}

	renderSubMaterialsTable() {
		const area = this.el("[data-sub-materials-table-area]");
		if (!area || !this.subData) return;
		const sym =
			this.subData.currency === "INR" ? "₹" : this.subData.currency ? this.subData.currency + " " : "₹";
		let rows = this.subData.materials_with_subcontractors || [];

		if (this.subSearch) {
			rows = rows.filter((r) =>
				Object.values(r).some((v) => String(v).toLowerCase().includes(this.subSearch))
			);
		}

		const pageSize = 10;
		const total = rows.length;
		const page = Math.min(this.subMaterialsPage, Math.max(0, Math.ceil(total / pageSize) - 1));
		const pageRows = rows.slice(page * pageSize, (page + 1) * pageSize);

		area.innerHTML = `
      <div class="sd-table-wrap">
        <table class="sd-table">
          <thead>
            <tr>
              <th>Supplier</th>
              <th>Raw Material Item</th>
              <th>Reserve Warehouse</th>
              <th>Sent Qty</th>
              <th>Consumed Qty</th>
              <th>Remaining Qty</th>
              <th>Unit Rate</th>
              <th>Material Value</th>
              <th>Subcontracting Order</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${
				pageRows
					.map(
						(m) => `
              <tr>
                <td><strong>${this.esc(m.supplier)}</strong></td>
                <td>${this.link("Item", m.item_code, m.item)}</td>
                <td><small>${this.esc(m.warehouse)}</small></td>
                <td>${this.num(m.sent_quantity)} ${this.esc(m.uom)}</td>
                <td>${this.num(m.consumed_quantity)} ${this.esc(m.uom)}</td>
                <td><strong>${this.num(m.remaining_quantity)} ${this.esc(m.uom)}</strong></td>
                <td>${this.formatCompact(m.rate, sym)}</td>
                <td><strong>${this.formatCompact(m.material_value, sym)}</strong></td>
                <td>${this.link("Subcontracting Order", m.subcontracting_order)}</td>
                <td><span class="sd-pill sd-status-${m.remaining_quantity > 0 ? "blue" : "green"}">${this.esc(
							m.status
						)}</span></td>
              </tr>
            `
					)
					.join("") ||
				'<tr><td colspan="10" class="sd-empty">No materials currently stationed with subcontractors.</td></tr>'
			}
          </tbody>
        </table>
      </div>
      ${
			total > pageSize
				? `
        <div class="sd-pagination">
          <button class="sd-button" data-sub-materials-page="${page - 1}" ${
						!page ? "disabled" : ""
				  }>Previous</button>
          <span>${page * pageSize + 1}–${Math.min(total, (page + 1) * pageSize)} of ${total}</span>
          <button class="sd-button" data-sub-materials-page="${page + 1}" ${
						(page + 1) * pageSize >= total ? "disabled" : ""
				  }>Next</button>
        </div>
      `
				: ""
		}
    `;
	}

	renderSubOrdersTable() {
		const area = this.el("[data-sub-orders-table-area]");
		if (!area || !this.subData) return;
		const sym =
			this.subData.currency === "INR" ? "₹" : this.subData.currency ? this.subData.currency + " " : "₹";
		let rows = this.subData.orders || [];

		if (this.subSearch) {
			rows = rows.filter((r) =>
				Object.values(r).some((v) => String(v).toLowerCase().includes(this.subSearch))
			);
		}
		if (this.subSelectedStatus) {
			rows = rows.filter((r) => r.status === this.subSelectedStatus);
		}
		if (this.subSelectedStage) {
			const stg = this.subSelectedStage;
			if (stg === "po") rows = rows.filter((r) => r.purchase_order && r.purchase_order !== "—");
			else if (stg === "stock_transfer")
				rows = rows.filter(
					(r) =>
						(r.material_sent || "").includes("Sent") ||
						(r.material_sent || "").includes("Transferred")
				);
			else if (stg === "in_production")
				rows = rows.filter((r) =>
					["Material Transferred", "Partial Material Transferred", "Partially Received"].includes(
						r.status
					)
				);
			else if (stg === "receipt") rows = rows.filter((r) => Number(r.received_qty || 0) > 0);
			else if (stg === "billing" || stg === "completed")
				rows = rows.filter((r) => r.status === "Completed");
		}

		const pageSize = 10;
		const total = rows.length;
		const page = Math.min(this.subOrdersPage, Math.max(0, Math.ceil(total / pageSize) - 1));
		const pageRows = rows.slice(page * pageSize, (page + 1) * pageSize);

		area.innerHTML = `
      <div class="sd-table-wrap">
        <table class="sd-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Purchase Order</th>
              <th>Supplier</th>
              <th>Project</th>
              <th>Finished Goods Item</th>
              <th>Ordered Qty</th>
              <th>Fulfillment Progress</th>
              <th>Material Dispatched</th>
              <th>Service Cost</th>
              <th>Expected Delivery</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${
				pageRows
					.map((o) => {
						const pct = o.ordered_qty ? Math.round((o.received_qty / o.ordered_qty) * 100) : 0;
						const isOverdue =
							o.expected_date &&
							o.expected_date < frappe.datetime.get_today() &&
							!["Completed", "Cancelled", "Closed"].includes(o.status);
						return `
                <tr>
                  <td><strong>${this.link("Subcontracting Order", o.subcontracting_order)}</strong></td>
                  <td>${o.purchase_order !== "—" ? this.link("Purchase Order", o.purchase_order) : "—"}</td>
                  <td>${this.esc(o.supplier)}</td>
                  <td>${o.project !== "—" ? this.link("Project", o.project) : "—"}</td>
                  <td>${this.esc(o.item)}</td>
                  <td>${this.num(o.ordered_qty)}</td>
                  <td>
                    <div class="sd-progress-cell">
                      <span>${this.num(o.received_qty)} / ${this.num(o.ordered_qty)} (${pct}%)</span>
                      <div class="sd-progress"><i style="width:${Math.min(100, pct)}%"></i></div>
                    </div>
                  </td>
                  <td><span class="sd-pill sd-status-blue">${this.esc(o.material_sent)}</span></td>
                  <td>${this.formatCompact(o.service_cost, sym)}</td>
                  <td class="${isOverdue ? "sd-sub-overdue-date" : ""}">
                    ${this.esc(o.expected_date || "—")}
                    ${isOverdue ? ' <span class="sd-pill sd-status-red">Overdue</span>' : ""}
                  </td>
                  <td>${this.badge(o.status)}</td>
                  <td>
                    <button class="sd-inspect" data-inspect="${this.esc(
						o.subcontracting_order
					)}" data-doctype="Subcontracting Order">Inspect</button>
                  </td>
                </tr>
              `;
					})
					.join("") ||
				'<tr><td colspan="12" class="sd-empty">No Subcontracting Orders match current filters.</td></tr>'
			}
          </tbody>
        </table>
      </div>
      ${
			total > pageSize
				? `
        <div class="sd-pagination">
          <button class="sd-button" data-sub-orders-page="${page - 1}" ${
						!page ? "disabled" : ""
				  }>Previous</button>
          <span>${page * pageSize + 1}–${Math.min(total, (page + 1) * pageSize)} of ${total}</span>
          <button class="sd-button" data-sub-orders-page="${page + 1}" ${
						(page + 1) * pageSize >= total ? "disabled" : ""
				  }>Next</button>
        </div>
      `
				: ""
		}
    `;
	}

	// ==========================================
	// SARATHI ACCOUNTING CONTROL TOWER
	// ==========================================

	renderAccountingCard() {
		const container = this.el("[data-accounting-cards]");
		if (!container) return;
		const a = this.data?.accounting_summary || {
			currency: "INR",
			revenue: 0,
			expense: 0,
			net_profit: 0,
			net_margin: 0,
			receivables: 0,
			payables: 0,
			cash_and_bank: 0,
			budget_used_pct: 0,
		};
		const sym = a.currency === "INR" ? "₹" : a.currency ? a.currency + " " : "₹";
		const isProfit = a.net_profit >= 0;
		const profitSign = isProfit ? "+" : "";
		container.innerHTML = `
      <button class="sd-card sd-accounting-main-card" data-action="open-accounting" title="Click to open Accounting Control Tower">
        <div class="sd-acc-card-top-strip"></div>
        <div class="sd-acc-card-header">
          <div class="sd-acc-card-title-wrap">
            <span class="sd-acc-card-icon">${this.workspaceIcon("bank")}</span>
            <div>
              <div class="sd-acc-card-tag">FINANCE & ACCOUNTING</div>
              <h3>Accounting Control Tower</h3>
            </div>
          </div>
          <span class="sd-pill ${isProfit ? "sd-status-green" : "sd-status-red"}">
            ${isProfit ? "▲ Net Profit" : "▼ Net Loss"} ${profitSign}${this.formatCompact(
			a.net_profit,
			sym
		)} (${a.net_margin}%)
          </span>
        </div>
        <div class="sd-acc-card-main-val">
          <small>Net Financial Result</small>
          <strong class="${
				isProfit ? "sd-acc-positive" : "sd-acc-negative"
			}">${profitSign}${this.formatCompact(a.net_profit, sym)}</strong>
        </div>
        <div class="sd-acc-card-chips">
          <div class="sd-acc-chip sd-acc-chip-blue" title="Gross Income / Sales">
            <span>Revenue</span>
            <b>${this.formatCompact(a.revenue, sym)}</b>
          </div>
          <div class="sd-acc-chip sd-acc-chip-rose" title="Total Expenses">
            <span>Expenses</span>
            <b>${this.formatCompact(a.expense, sym)}</b>
          </div>
          <div class="sd-acc-chip sd-acc-chip-amber" title="Receivables (AR)">
            <span>AR</span>
            <b>${this.formatCompact(a.receivables, sym)}</b>
          </div>
          <div class="sd-acc-chip sd-acc-chip-crimson" title="Payables (AP)">
            <span>AP</span>
            <b>${this.formatCompact(a.payables, sym)}</b>
          </div>
          <div class="sd-acc-chip sd-acc-chip-teal" title="Cash & Bank Balances">
            <span>Bank & Cash</span>
            <b>${this.formatCompact(a.cash_and_bank, sym)}</b>
          </div>
          <div class="sd-acc-chip sd-acc-chip-purple" title="Budget Utilization">
            <span>Budget</span>
            <b>${a.budget_used_pct}%</b>
          </div>
        </div>
        <div class="sd-acc-card-footer">
          <span>Traceable to ERPNext GL & Payment Ledger</span>
          <small>Open Accounting Control Tower →</small>
        </div>
      </button>
    `;
	}

	showAccountingView(silent = false) {
		const hideSelectors = [
			".sd-hero",
			".sd-controls",
			".sd-breadcrumb",
			".sd-scope-note",
			".sd-kpis",
			"[data-live-projects]",
			"[data-subcontracting-card-panel]",
			"[data-accounting-card-panel]",
			"[data-customer-panel]",
			"[data-project-panel]",
			"[data-project-summary]",
			".sd-tabs",
			"[data-content]",
		];
		hideSelectors.forEach((sel) => {
			const n = this.el(sel);
			if (n) n.hidden = true;
		});
		const viewEl = this.el("[data-accounting-view]");
		if (viewEl) viewEl.hidden = false;
		if (this.filters.company && !this.accFilters.company) this.accFilters.company = this.filters.company;
		if (this.filters.project && !this.accFilters.project) this.accFilters.project = this.filters.project;
		this.loadAccountingData(silent);
	}

	hideAccountingView() {
		const viewEl = this.el("[data-accounting-view]");
		if (viewEl) viewEl.hidden = true;
		const showSelectors = [
			".sd-hero",
			".sd-controls",
			".sd-breadcrumb",
			".sd-scope-note",
			".sd-kpis",
			"[data-live-projects]",
			"[data-subcontracting-card-panel]",
			"[data-accounting-card-panel]",
			".sd-tabs",
			"[data-content]",
		];
		showSelectors.forEach((sel) => {
			const n = this.el(sel);
			if (n) n.hidden = false;
		});
		if (this.el("[data-customer-panel]"))
			this.el("[data-customer-panel]").hidden = !!this.filters.customer || !!this.filters.project;
		if (this.el("[data-project-panel]")) this.el("[data-project-panel]").hidden = !!this.filters.project;
		if (this.el("[data-project-summary]"))
			this.el("[data-project-summary]").hidden = !this.filters.project;
	}

	openAccountingView() {
		this.view = "accounting";
		this.writeUrl();
		this.showAccountingView();
		window.scrollTo({ top: 0, behavior: "smooth" });
	}

	closeAccountingView() {
		this.view = "";
		this.writeUrl();
		this.hideAccountingView();
		window.scrollTo({ top: 0, behavior: "smooth" });
		if (!this.data) {
			this.load();
		}
	}

	accFilterChanged(target) {
		this.accFilters[target.dataset.accFilter] = target.value;
	}

	applyAccFilters() {
		for (const sel of [
			"company",
			"project",
			"customer",
			"supplier",
			"cost_center",
			"from_date",
			"to_date",
		]) {
			const inp = this.el(`[data-acc-filter="${sel}"]`);
			if (inp) this.accFilters[sel] = inp.value;
		}
		this.loadAccountingData();
	}

	resetAccFilters() {
		this.accFilters = {
			period: "this_month",
			company: "",
			project: "",
			customer: "",
			supplier: "",
			cost_center: "",
			account: "",
			from_date: "",
			to_date: "",
		};
		this.accSearch = "";
		this.loadAccountingData();
	}

	setAccPeriod(period) {
		this.accFilters.period = period;
		if (period !== "custom") {
			this.accFilters.from_date = "";
			this.accFilters.to_date = "";
		}
		this.loadAccountingData();
	}

	setAccTab(tab) {
		this.accTab = tab;
		this.accActiveKpi = "";
		this.renderAccountingDetailView();
	}

	selectAccKpi(kpiId, targetTab, focusAnchor) {
		this.accActiveKpi = kpiId;
		this.accTab = targetTab;
		this.renderAccountingDetailView();
		setTimeout(() => {
			let targetEl = this.el(`[data-acc-section="${focusAnchor}"]`);
			if (!targetEl) {
				targetEl = this.el(".sd-acc-tab-content");
			}
			if (targetEl) {
				targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
				targetEl.classList.add("sd-acc-highlight-pulse");
				setTimeout(() => targetEl.classList.remove("sd-acc-highlight-pulse"), 2000);
			}
		}, 80);
	}

	async loadAccountingData(silent = false) {
		const viewEl = this.el("[data-accounting-view]");
		if (!viewEl) return;
		const hasContainer = !!viewEl.querySelector(".sd-acc-container");
		if (!silent && !this.accData && !hasContainer) {
			viewEl.innerHTML = `
        <div class="sd-sub-loading">
          <div class="sd-sub-spinner"></div>
          <span>Loading Sarathi Accounting Intelligence…</span>
        </div>
      `;
		}
		const request = (this.accountingRequest = (this.accountingRequest || 0) + 1);
		try {
			const r = await frappe.call({
				method: "sarathi_visibility.api.accounting.get_accounting_dashboard",
				args: { filters: JSON.stringify(this.accFilters) },
				silent: true,
			});
			if (request !== this.accountingRequest || this.view !== "accounting") return;
			this.accData = r.message;
			if (hasContainer) {
				this.renderAccountingDetailView();
			} else {
				const scrollPos = window.scrollY;
				this.renderAccountingDetailView();
				if (scrollPos > 0) {
					window.scrollTo({ top: scrollPos, behavior: "instant" });
				}
			}
		} catch (e) {
			console.error("Failed to load accounting data:", e);
			if (request === this.accountingRequest && this.view === "accounting") {
				viewEl.innerHTML = `
          <div class="sd-sub-error">
            <h3>Accounting Data Unavailable</h3>
            <p>Could not fetch accounting intelligence records. Check permissions for General Ledger and accounts.</p>
            <button class="sd-button" data-action="refresh-accounting">Retry</button>
            <button class="sd-button" data-action="close-accounting">← Return to Dashboard</button>
          </div>
        `;
			}
		}
	}

	updateAccountingDetailViewSmoothly(d) {
		const viewEl = this.el("[data-accounting-view]");
		if (!viewEl || !d) return;
		const sym = d.currency === "INR" ? "₹" : d.currency ? d.currency + " " : "₹";
		const k = d.kpis;
		if (!k) return;

		const values = {
			rev: {
				val: this.formatCompact(k.revenue.value, sym),
				sub: `${k.revenue.change >= 0 ? "▲ +" : "▼ "}${k.revenue.change}% vs prev period`,
			},
			exp: {
				val: this.formatCompact(k.expense.value, sym),
				sub: `COGS: ${this.formatCompact(k.expense.cogs, sym)} · OpEx: ${this.formatCompact(
					k.expense.opex,
					sym
				)}`,
			},
			np: {
				val: this.formatCompact(k.net_profit.value, sym),
				sub: `Net Margin: ${k.net_profit.margin}% · ${k.net_profit.change >= 0 ? "▲ +" : "▼ "}${
					k.net_profit.change
				}%`,
			},
			cash: {
				val: this.formatCompact(k.cash_in_hand.value, sym),
				sub: "Liquid cash account balance",
			},
			ar: {
				val: this.formatCompact(k.receivables.value, sym),
				sub: `Overdue: ${this.formatCompact(k.receivables.overdue, sym)} (${
					k.receivables.count
				} invoices)`,
			},
			ap: {
				val: this.formatCompact(k.payables.value, sym),
				sub: `Overdue: ${this.formatCompact(k.payables.overdue, sym)} (${k.payables.count} bills)`,
			},
			tax: {
				val: this.formatCompact(k.tax_liability.value, sym),
				sub: `Output: ${this.formatCompact(
					k.tax_liability.output_tax,
					sym
				)} · Input: ${this.formatCompact(k.tax_liability.input_tax, sym)}`,
			},
			bgt: {
				val: `${k.budget_used.pct}%`,
				sub: `Approved: ${this.formatCompact(k.budget_used.approved, sym)}`,
			},
			bank: {
				val: this.formatCompact(k.bank_balance.value, sym),
				sub: `${k.bank_balance.accounts_count} active bank account(s)`,
			},
		};

		Object.keys(values).forEach((id) => {
			const card = viewEl.querySelector(`[data-acc-kpi="${id}"]`);
			if (card) {
				const valEl = card.querySelector(".sd-acc-kpi-value");
				const subEl = card.querySelector(".sd-acc-kpi-sub");
				if (valEl && valEl.textContent.trim() !== values[id].val.trim()) {
					valEl.textContent = values[id].val;
					valEl.style.transition = "color 0.4s";
					valEl.style.color = "#3b82f6";
					setTimeout(() => {
						valEl.style.color = "";
					}, 800);
				}
				if (subEl && values[id].sub) {
					subEl.textContent = values[id].sub;
				}
			}
		});
	}

	renderAccountingDetailView() {
		const viewEl = this.el("[data-accounting-view]");
		if (!viewEl || !this.accData) return;
		const scrollPos = window.scrollY;
		const d = this.accData;
		const sym = d.currency === "INR" ? "₹" : d.currency ? d.currency + " " : "₹";
		const periods = [
			{ k: "today", l: "Today" },
			{ k: "yesterday", l: "Yesterday" },
			{ k: "this_week", l: "This Week" },
			{ k: "this_month", l: "This Month" },
			{ k: "last_month", l: "Last Month" },
			{ k: "this_quarter", l: "This Quarter" },
			{ k: "this_year", l: "This Year" },
			{ k: "last_year", l: "Last Year" },
			{ k: "custom", l: "Custom Range" },
		];
		const tabs = [
			{ k: "overview", l: "4. Overview Dashboard", icon: "📊" },
			{ k: "revenue_expense", l: "5. Revenue & Expense Analytics", icon: "📈" },
			{
				k: "profit_cash",
				l: "6. Profitability & Cash Control Tower",
				icon: "💵",
			},
			{
				k: "receivables_payables",
				l: "7. Receivables, Payables & Banking",
				icon: "⏱️",
			},
			{ k: "taxes_budget", l: "8. Taxes & Budget Control Tower", icon: "⚖️" },
			{
				k: "project_finance",
				l: "9. Project, Customer & Supplier Finance",
				icon: "🏗️",
			},
		];

		viewEl.innerHTML = `
      <div class="sd-acc-container">
        <!-- Hero Header -->
        <header class="sd-hero sd-acc-hero">
          <div>
            <div class="sd-eyebrow">SARATHI AI LABS · FINANCE → ACCOUNTING CONTROL TOWER</div>
            <h1>Accounting Control Tower</h1>
            <p>Executive management intelligence · ERPNext General Ledger & Payment Ledger system of record</p>
          </div>
          <div class="sd-hero-actions">
            <button class="sd-button sd-acc-back-btn" data-action="close-accounting">← Back to Dashboard</button>
            <button class="sd-button" data-action="refresh-accounting">↻ Refresh</button>
          </div>
        </header>

        <!-- Global Filter Bar -->
        <section class="sd-acc-filter-section" aria-label="Accounting Filters">
          <div class="sd-acc-period-bar">
            <span class="sd-acc-period-label">Period:</span>
            <div class="sd-acc-period-pills">
              ${periods
					.map(
						(p) => `
                <button class="sd-acc-period-pill ${
					this.accFilters.period === p.k ? "active" : ""
				}" data-acc-period="${p.k}">
                  ${p.l}
                </button>
              `
					)
					.join("")}
            </div>
          </div>

          <div class="sd-controls sd-acc-controls">
            <label>Organization
              <select data-acc-filter="company">
                <option value="">All organizations</option>
                ${(d.options?.companies || [])
					.map(
						(c) =>
							`<option value="${this.esc(c.name)}" ${
								this.accFilters.company === c.name ? "selected" : ""
							}>${this.esc(c.company_name || c.name)}</option>`
					)
					.join("")}
              </select>
            </label>
            <label>Project
              <select data-acc-filter="project">
                <option value="">All projects</option>
                ${(d.options?.projects || [])
					.map(
						(p) =>
							`<option value="${this.esc(p.name)}" ${
								this.accFilters.project === p.name ? "selected" : ""
							}>${this.esc(p.project_name || p.name)}</option>`
					)
					.join("")}
              </select>
            </label>
            <label>Cost Center
              <select data-acc-filter="cost_center">
                <option value="">All cost centers</option>
                ${(d.options?.cost_centers || [])
					.map(
						(cc) =>
							`<option value="${this.esc(cc.name)}" ${
								this.accFilters.cost_center === cc.name ? "selected" : ""
							}>${this.esc(cc.cost_center_name || cc.name)}</option>`
					)
					.join("")}
              </select>
            </label>
            <label>From Date
              <input type="date" data-acc-filter="from_date" value="${this.esc(
					this.accFilters.from_date || d.period_dates.start_date
				)}">
            </label>
            <label>To Date
              <input type="date" data-acc-filter="to_date" value="${this.esc(
					this.accFilters.to_date || d.period_dates.end_date
				)}">
            </label>
            <button class="sd-button sd-primary" data-action="apply-acc-filters">Apply Filters</button>
            <button class="sd-button" data-action="reset-acc-filters">Reset</button>
          </div>
          <div class="sd-acc-date-badge">
            <span>Active Range: <b>${this.esc(d.period_dates.start_date)}</b> to <b>${this.esc(
			d.period_dates.end_date
		)}</b></span>
            <span>· Comparison Base: <b>${this.esc(d.period_dates.prev_start)}</b> to <b>${this.esc(
			d.period_dates.prev_end
		)}</b></span>
          </div>
        </section>

        <!-- 9 Core Overview KPI Strip (Page 5 & 14) -->
        <section class="sd-acc-kpis-grid" aria-label="9 Core Accounting KPIs">
          ${this.renderAccountingKpis(d.kpis, sym)}
        </section>

        <!-- Active KPI Selection Header Banner -->
        ${this.renderActiveKpiBanner()}

        <!-- Navigation Sub-Tabs -->
        <nav class="sd-acc-tabs" role="tablist">
          ${tabs
				.map(
					(t) => `
            <button class="sd-acc-tab-btn ${this.accTab === t.k ? "active" : ""}" data-acc-tab="${t.k}">
              ${this.workspaceIcon(t.l)} ${t.l}
            </button>
          `
				)
				.join("")}
        </nav>

        <!-- Dynamic Content Area (6 Exact Sections) -->
        <div class="sd-acc-tab-content">
          ${
				this.accTab === "overview"
					? `
            <div class="sd-acc-section-block">
              ${this.renderOverviewDashboard(d, sym)}
            </div>
          `
					: ""
			}

          ${
				this.accTab === "revenue_expense"
					? `
            <div class="sd-acc-section-block">
              ${this.renderRevenueExpenseAnalytics(d, sym)}
            </div>
          `
					: ""
			}

          ${
				this.accTab === "profit_cash"
					? `
            <div class="sd-acc-section-block">
              ${this.renderProfitabilityCashTower(d, sym)}
            </div>
          `
					: ""
			}

          ${
				this.accTab === "receivables_payables"
					? `
            <div class="sd-acc-section-block">
              ${this.renderReceivablesPayablesBanking(d, sym)}
            </div>
          `
					: ""
			}

          ${
				this.accTab === "taxes_budget"
					? `
            <div class="sd-acc-section-block">
              ${this.renderTaxesBudgetTower(d, sym)}
            </div>
          `
					: ""
			}

          ${
				this.accTab === "project_finance"
					? `
            <div class="sd-acc-section-block">
              ${this.renderProjectCustomerSupplierFinance(d, sym)}
            </div>
          `
					: ""
			}
        </div>
      </div>
    `;
		if (scrollPos > 0) {
			window.scrollTo({ top: scrollPos, behavior: "instant" });
		}
	}

	renderActiveKpiBanner() {
		const kpiNames = {
			rev: {
				title: "4. Total Revenue Analytics (Section 5)",
				desc: "Commercial performance, monthly moving average, collection rate, customer & project revenue",
				tab: "revenue_expense",
				icon: "📈",
			},
			exp: {
				title: "5. Total Expense Intelligence (Section 5)",
				desc: "Operating & overhead costs, direct production COGS, cost center & project expense allocation",
				tab: "revenue_expense",
				icon: "📉",
			},
			np: {
				title: "6. Profitability & Net Margins (Section 6)",
				desc: "7-step profitability waterfall explaining how gross revenue translates into net profit",
				tab: "profit_cash",
				icon: "💎",
			},
			cash: {
				title: "6. Cash in Hand & Liquidity Control (Section 6)",
				desc: "Liquid cash balances, petty cash drawers, customer collections vs supplier disbursements",
				tab: "profit_cash",
				icon: "💵",
			},
			bank: {
				title: "6. Bank Balances & Clearance (Section 6)",
				desc: "Active bank accounts, live balances, clearance tracking, and general ledger links",
				tab: "profit_cash",
				icon: "🏦",
			},
			ar: {
				title: "7. Accounts Receivable (AR) Ageing Control (Section 7)",
				desc: "Customer outstanding ageing buckets (Current, 1–30d, 31–60d, 61–90d, 90+d) and invoices",
				tab: "receivables_payables",
				icon: "📥",
			},
			ap: {
				title: "7. Accounts Payable (AP) Ageing Control (Section 7)",
				desc: "Supplier bills ageing buckets (Due This Week, Month, 31–60d, 90+d) and payment liabilities",
				tab: "receivables_payables",
				icon: "📤",
			},
			tax: {
				title: "8. Statutory Tax & GST Liabilities (Section 8)",
				desc: "Sales output tax, purchase input tax credit (ITC offset), and net statutory liability",
				tab: "taxes_budget",
				icon: "⚖️",
			},
			bgt: {
				title: "8. Departmental Budget vs Actual (Section 8)",
				desc: "Approved budget limits, actual debited expenses, variance, and utilization meters",
				tab: "taxes_budget",
				icon: "🎯",
			},
		};
		if (!this.accActiveKpi || !kpiNames[this.accActiveKpi]) {
			return `
        <div class="sd-acc-active-banner sd-acc-banner-neutral">
          <div class="sd-acc-banner-info">
            <span class="sd-acc-banner-pill">💡 Interactive Control Tower</span>
            <span class="sd-acc-banner-text">Click any of the <b>9 KPI cards</b> above to immediately show its related details, reports & analytics below.</span>
          </div>
        </div>
      `;
		}
		const info = kpiNames[this.accActiveKpi];
		return `
      <div class="sd-acc-active-banner sd-acc-banner-highlight">
        <div class="sd-acc-banner-info">
          <span class="sd-acc-banner-pill active">${info.icon} Selected Card Section</span>
          <div>
            <h4 class="sd-acc-banner-title">${info.title}</h4>
            <p class="sd-acc-banner-desc">${info.desc}</p>
          </div>
        </div>
        <button class="sd-button sd-acc-banner-btn" data-action="reset-kpi-selection">View Full Overview Dashboard</button>
      </div>
    `;
	}

	// ==========================================
	// SECTION 4: Overview Dashboard (Page 5)
	// ==========================================
	renderOverviewDashboard(d, sym) {
		return `
      <!-- Profit Waterfall Overview -->
      ${this.renderProfitWaterfall(d.waterfall, sym)}

      <!-- Primary Financial Trends -->
      <div class="sd-acc-grid-2">
        ${this.renderRevenueExpenseTrend(d.trends, sym)}
        ${this.renderExpenseCategories(d.expense_categories, sym)}
      </div>

      <!-- Quick Cash & Ageing Snapshot -->
      <div class="sd-acc-grid-2">
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Cash & Liquidity Snapshot</h2>
              <p>Liquid funds and net movement</p>
            </div>
            <span class="sd-pill sd-status-blue">${this.formatCompact(d.cash_control.total_cash, sym)}</span>
          </div>
          <div class="sd-acc-sub-kpis" style="grid-template-columns: repeat(3, 1fr);">
            <div class="sd-acc-sub-kpi">
              <span>Bank Balance</span>
              <strong>${this.formatCompact(d.cash_control.bank_balance, sym)}</strong>
            </div>
            <div class="sd-acc-sub-kpi">
              <span>Cash in Hand</span>
              <strong>${this.formatCompact(d.cash_control.cash_in_hand, sym)}</strong>
            </div>
            <div class="sd-acc-sub-kpi">
              <span>Net Movement</span>
              <strong class="${d.cash_control.net_cash_movement >= 0 ? "sd-acc-green" : "sd-acc-red"}">
                ${d.cash_control.net_cash_movement >= 0 ? "+" : ""}${this.formatCompact(
			d.cash_control.net_cash_movement,
			sym
		)}
              </strong>
            </div>
          </div>
        </div>

        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Receivables & Payables Snapshot</h2>
              <p>Working capital balance</p>
            </div>
          </div>
          <div class="sd-acc-sub-kpis" style="grid-template-columns: repeat(2, 1fr);">
            <div class="sd-acc-sub-kpi">
              <span>Receivables (AR)</span>
              <strong class="sd-acc-amber">${this.formatCompact(d.kpis.receivables.value, sym)}</strong>
              <small class="${d.kpis.receivables.overdue > 0 ? "sd-acc-red" : "sd-acc-green"}">
                Overdue: ${this.formatCompact(d.kpis.receivables.overdue, sym)}
              </small>
            </div>
            <div class="sd-acc-sub-kpi">
              <span>Payables (AP)</span>
              <strong class="sd-acc-rose">${this.formatCompact(d.kpis.payables.value, sym)}</strong>
              <small class="${d.kpis.payables.overdue > 0 ? "sd-acc-red" : "sd-acc-sub"}">
                Overdue: ${this.formatCompact(d.kpis.payables.overdue, sym)}
              </small>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-End Review Checklist -->
      ${this.renderAuditChecklist(d.checklist)}
    `;
	}

	// ==========================================
	// SECTION 5: Revenue & Expense Analytics (Page 6)
	// ==========================================
	renderRevenueExpenseAnalytics(d, sym) {
		const rev = d.kpis?.revenue || {};
		const revA = d.revenue_analytics || {};
		const expA = d.expense_analytics || {};

		return `
      <!-- Revenue KPIs (Page 6) -->
      <div class="sd-panel" data-acc-section="revenue">
        <div class="sd-panel-heading">
          <div>
            <h2>5. Revenue KPIs & Commercial Performance (Page 6)</h2>
            <p>Directly analyzed by time, account, customer, project and accounting dimension</p>
          </div>
          <span class="sd-pill sd-status-green">Collection Rate: ${rev.collection_rate || 0}%</span>
        </div>
        <div class="sd-acc-sub-kpis">
          <div class="sd-acc-sub-kpi">
            <span>Total Revenue</span>
            <strong class="sd-acc-blue">${this.formatCompact(rev.value || 0, sym)}</strong>
            <small class="${rev.change >= 0 ? "sd-acc-green" : "sd-acc-red"}">
              ${rev.change >= 0 ? "▲ +" : "▼ "}${rev.change || 0}% vs prev
            </small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Invoice Revenue</span>
            <strong>${this.formatCompact(rev.invoice_revenue || 0, sym)}</strong>
            <small class="sd-acc-sub">Submitted Sales Invoices</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Other Income</span>
            <strong>${this.formatCompact(rev.other_income || 0, sym)}</strong>
            <small class="sd-acc-sub">Operational & Non-sales</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Avg Monthly Revenue</span>
            <strong>${this.formatCompact(rev.avg_monthly || 0, sym)}</strong>
            <small class="sd-acc-sub">6-Month Moving Average</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Outstanding Sales</span>
            <strong class="sd-acc-amber">${this.formatCompact(rev.outstanding_sales || 0, sym)}</strong>
            <small class="sd-acc-sub">Uncollected customer balance</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Collection Rate</span>
            <strong class="sd-acc-green">${rev.collection_rate || 0}%</strong>
            <small class="sd-acc-sub">Collections / Revenue</small>
          </div>
        </div>
      </div>

      <!-- Revenue Visualizations (Page 6) -->
      <div class="sd-acc-grid-2">
        <!-- Revenue by Customer (Horizontal bar) -->
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Revenue by Customer (Horizontal Bar)</h2>
              <p>Top customer revenue contribution</p>
            </div>
          </div>
          <div class="sd-acc-hbar-list">
            ${
				(revA.by_customer || [])
					.map(
						(c) => `
              <div class="sd-acc-hbar-row">
                <div class="sd-acc-hbar-head">
                  <span class="sd-acc-hbar-label">${this.esc(c.customer_name || c.customer)}</span>
                  <span class="sd-acc-hbar-val">${this.formatCompact(c.amount, sym)} <b>(${c.pct}%)</b></span>
                </div>
                <div class="sd-progress sd-acc-hbar-track">
                  <i style="width:${Math.min(100, c.pct)}%; background:#2563eb;"></i>
                </div>
              </div>
            `
					)
					.join("") ||
				'<div class="sd-empty">No customer sales invoices found for this selection.</div>'
			}
          </div>
        </div>

        <!-- Revenue by Project (Bar) -->
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Revenue by Project (Bar)</h2>
              <p>Project billing distribution</p>
            </div>
          </div>
          <div class="sd-acc-hbar-list">
            ${
				(revA.by_project || [])
					.map(
						(p) => `
              <div class="sd-acc-hbar-row">
                <div class="sd-acc-hbar-head">
                  <span class="sd-acc-hbar-label">${this.esc(p.project)}</span>
                  <span class="sd-acc-hbar-val">${this.formatCompact(p.amount, sym)} <b>(${p.pct}%)</b></span>
                </div>
                <div class="sd-progress sd-acc-hbar-track">
                  <i style="width:${Math.min(100, p.pct)}%; background:#059669;"></i>
                </div>
              </div>
            `
					)
					.join("") || '<div class="sd-empty">No project-linked sales invoices found.</div>'
			}
          </div>
        </div>
      </div>

      <!-- Revenue Mix & Expense Trends -->
      <div class="sd-acc-grid-2">
        <!-- Revenue Mix (Donut / Composition) -->
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Revenue Mix (Category Composition)</h2>
              <p>Operating income distribution</p>
            </div>
          </div>
          <div class="sd-acc-mix-grid">
            ${(revA.mix || [])
				.map(
					(m) => `
              <div class="sd-acc-mix-card">
                <div class="sd-acc-mix-dot" style="background:${m.color}"></div>
                <div class="sd-acc-mix-info">
                  <span class="sd-acc-mix-title">${this.esc(m.category)}</span>
                  <strong class="sd-acc-mix-val">${this.formatCompact(m.amount, sym)}</strong>
                </div>
              </div>
            `
				)
				.join("")}
          </div>
        </div>

        <!-- Expense Composition by Category -->
        ${this.renderExpenseCategories(d.expense_categories, sym)}
      </div>

      <!-- Expense by Cost Center & Project -->
      <div class="sd-acc-grid-2">
        <!-- Expense by Cost Center (Horizontal bar) -->
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Expense by Cost Center (Horizontal Bar)</h2>
              <p>Cost center allocation from General Ledger</p>
            </div>
          </div>
          <div class="sd-acc-hbar-list">
            ${
				(expA.by_cost_center || [])
					.map(
						(cc) => `
              <div class="sd-acc-hbar-row">
                <div class="sd-acc-hbar-head">
                  <span class="sd-acc-hbar-label">${this.esc(cc.cost_center)}</span>
                  <span class="sd-acc-hbar-val">${this.formatCompact(cc.amount, sym)} <b>(${
							cc.pct
						}%)</b></span>
                </div>
                <div class="sd-progress sd-acc-hbar-track">
                  <i style="width:${Math.min(100, cc.pct)}%; background:#7c3aed;"></i>
                </div>
              </div>
            `
					)
					.join("") ||
				'<div class="sd-empty">No cost-center expenses recorded for this period.</div>'
			}
          </div>
        </div>

        <!-- Expense by Project (Bar) -->
        <div class="sd-panel">
          <div class="sd-panel-heading">
            <div>
              <h2>Expense by Project (Bar)</h2>
              <p>Project procurement and operational expenses</p>
            </div>
          </div>
          <div class="sd-acc-hbar-list">
            ${
				(expA.by_project || [])
					.map(
						(p) => `
              <div class="sd-acc-hbar-row">
                <div class="sd-acc-hbar-head">
                  <span class="sd-acc-hbar-label">${this.esc(p.project)}</span>
                  <span class="sd-acc-hbar-val">${this.formatCompact(p.amount, sym)} <b>(${p.pct}%)</b></span>
                </div>
                <div class="sd-progress sd-acc-hbar-track">
                  <i style="width:${Math.min(100, p.pct)}%; background:#e11d48;"></i>
                </div>
              </div>
            `
					)
					.join("") || '<div class="sd-empty">No project expenses recorded.</div>'
			}
          </div>
        </div>
      </div>
    `;
	}

	// ==========================================
	// SECTION 6: Profitability & Cash Control Tower (Page 7)
	// ==========================================
	renderProfitabilityCashTower(d, sym) {
		const w = d.waterfall || {};
		return `
      <!-- Profitability KPIs (Page 7) -->
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>6. Profitability KPIs (Page 7)</h2>
            <p>Explaining how gross revenue becomes gross profit, operating profit and net profit</p>
          </div>
          <span class="sd-pill ${w.net_profit >= 0 ? "sd-status-green" : "sd-status-red"}">
            Net Margin: ${w.net_margin}%
          </span>
        </div>
        <div class="sd-acc-sub-kpis" style="grid-template-columns: repeat(4, 1fr);">
          <div class="sd-acc-sub-kpi">
            <span>Revenue</span>
            <strong class="sd-acc-blue">${this.formatCompact(w.gross_revenue, sym)}</strong>
            <small class="sd-acc-sub">Total billed income</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>COGS</span>
            <strong class="sd-acc-red">-${this.formatCompact(w.cogs, sym)}</strong>
            <small class="sd-acc-sub">Direct production cost</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Gross Profit</span>
            <strong class="sd-acc-emerald">${this.formatCompact(w.gross_profit, sym)}</strong>
            <small class="sd-acc-green">${w.gross_margin}% Gross Margin</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Gross Margin</span>
            <strong class="sd-acc-emerald">${w.gross_margin}%</strong>
            <small class="sd-acc-sub">(Revenue - COGS) / Revenue</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Operating Expense</span>
            <strong class="sd-acc-orange">-${this.formatCompact(w.operating_expense, sym)}</strong>
            <small class="sd-acc-sub">Admin, Selling & Utility</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Operating Profit</span>
            <strong class="sd-acc-purple">${this.formatCompact(w.operating_profit, sym)}</strong>
            <small class="sd-acc-sub">EBIT operational base</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Net Profit</span>
            <strong class="${w.net_profit >= 0 ? "sd-acc-green" : "sd-acc-red"}">
              ${w.net_profit >= 0 ? "+" : ""}${this.formatCompact(w.net_profit, sym)}
            </strong>
            <small class="${w.net_profit >= 0 ? "sd-acc-green" : "sd-acc-red"}">${
			w.net_margin
		}% Net Margin</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Net Margin</span>
            <strong class="${w.net_profit >= 0 ? "sd-acc-green" : "sd-acc-red"}">${w.net_margin}%</strong>
            <small class="sd-acc-sub">Bottom-line ratio</small>
          </div>
        </div>
      </div>

      <!-- Profit Waterfall (Page 7) -->
      ${this.renderProfitWaterfall(w, sym)}

      <!-- Cash Control Tower (Page 7) -->
      ${this.renderCashLiquidity(d.cash_control, sym)}
    `;
	}

	// ==========================================
	// SECTION 7: Receivables, Payables & Banking (Page 8)
	// ==========================================
	renderReceivablesPayablesBanking(d, sym) {
		return `
      ${this.renderAgeingSection(d.ageing, sym)}
    `;
	}

	// ==========================================
	// SECTION 8: Taxes & Budget Control Tower (Page 9)
	// ==========================================
	renderTaxesBudgetTower(d, sym) {
		const tax = d.kpis?.tax_liability || {};
		const bgt = d.kpis?.budget_used || {};

		return `
      <!-- Tax & Budget KPIs Strip (Page 9) -->
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>8. Taxes & Budget Control Tower (Page 9)</h2>
            <p>Statutory liability management and departmental budget variance</p>
          </div>
          <span class="sd-pill ${bgt.pct > 100 ? "sd-status-red" : "sd-status-purple"}">
            Budget Utilization: ${bgt.pct}%
          </span>
        </div>

        <h3 class="sd-acc-subhead">Tax KPIs</h3>
        <div class="sd-acc-sub-kpis" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 20px;">
          <div class="sd-acc-sub-kpi">
            <span>Output Tax</span>
            <strong class="sd-acc-blue">${this.formatCompact(tax.output_tax, sym)}</strong>
            <small class="sd-acc-sub">Sales GST / VAT collected</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Input Tax</span>
            <strong class="sd-acc-teal">${this.formatCompact(tax.input_tax, sym)}</strong>
            <small class="sd-acc-sub">Purchase GST / VAT credit</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Net Tax Liability</span>
            <strong class="sd-acc-orange">${this.formatCompact(tax.value, sym)}</strong>
            <small class="sd-acc-sub">Payable after ITC offset</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Tax Paid</span>
            <strong class="sd-acc-green">${this.formatCompact(tax.tax_paid, sym)}</strong>
            <small class="sd-acc-sub">Statutory payments deposited</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Tax Payable</span>
            <strong class="sd-acc-red">${this.formatCompact(tax.tax_payable, sym)}</strong>
            <small class="sd-acc-sub">Due to statutory authorities</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Tax Receivable</span>
            <strong class="sd-acc-emerald">${this.formatCompact(tax.tax_receivable, sym)}</strong>
            <small class="sd-acc-sub">Excess ITC carry-forward</small>
          </div>
        </div>

        <h3 class="sd-acc-subhead">Budget KPIs</h3>
        <div class="sd-acc-sub-kpis" style="grid-template-columns: repeat(3, 1fr);">
          <div class="sd-acc-sub-kpi">
            <span>Approved Budget</span>
            <strong class="sd-acc-purple">${this.formatCompact(bgt.approved, sym)}</strong>
            <small class="sd-acc-sub">Total authorized ceiling</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Actual Expense</span>
            <strong class="sd-acc-rose">${this.formatCompact(bgt.actual, sym)}</strong>
            <small class="sd-acc-sub">Total debited expenses</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Committed Expense</span>
            <strong class="sd-acc-sky">${this.formatCompact(bgt.committed, sym)}</strong>
            <small class="sd-acc-sub">Open Purchase Orders</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Available Budget</span>
            <strong class="sd-acc-emerald">${this.formatCompact(bgt.available, sym)}</strong>
            <small class="sd-acc-sub">Remaining budget headroom</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Variance</span>
            <strong class="${bgt.variance >= 0 ? "sd-acc-green" : "sd-acc-red"}">
              ${bgt.variance >= 0 ? "+" : ""}${this.formatCompact(bgt.variance, sym)}
            </strong>
            <small class="${bgt.variance >= 0 ? "sd-acc-green" : "sd-acc-red"}">Approved minus Actual</small>
          </div>
          <div class="sd-acc-sub-kpi">
            <span>Utilization</span>
            <strong class="${bgt.pct > 100 ? "sd-acc-red" : "sd-acc-purple"}">${bgt.pct}%</strong>
            <small class="sd-acc-sub">Actual / Approved</small>
          </div>
        </div>
      </div>

      <!-- Budget vs Actual Table (Page 9) -->
      ${this.renderBudgetTaxes(d.budget_vs_actual, tax, sym)}
    `;
	}

	// ==========================================
	// SECTION 9: Project, Customer & Supplier Finance (Page 10)
	// ==========================================
	renderProjectCustomerSupplierFinance(d, sym) {
		return `
      <!-- Project Financial Intelligence (Page 10) -->
      ${this.renderProjectFinance(d.project_finance, sym)}

      <!-- Customer Finance Analysis (Page 10) -->
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Customer Finance & Credit Exposure (Page 10)</h2>
            <p>Customer billing, collections, outstanding ageing and credit risk</p>
          </div>
        </div>
        <div class="sd-table-wrap">
          <table class="sd-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Total Invoiced</th>
                <th>Collected</th>
                <th>Outstanding Balance</th>
                <th>Collection Rate</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${
					(d.customer_finance || [])
						.map(
							(c) => `
                <tr>
                  <td><strong>${this.link("Customer", c.customer, c.customer_name)}</strong></td>
                  <td>${this.formatCompact(c.invoiced, sym)}</td>
                  <td>${this.formatCompact(c.collected, sym)}</td>
                  <td><span class="${c.outstanding > 0 ? "sd-acc-amber" : ""}">${this.formatCompact(
								c.outstanding,
								sym
							)}</span></td>
                  <td><span class="sd-pill ${
						c.collection_rate >= 80
							? "sd-status-green"
							: c.collection_rate >= 50
							? "sd-status-blue"
							: "sd-status-orange"
					}">${c.collection_rate}%</span></td>
                  <td><span class="sd-pill ${
						c.status === "Cleared" ? "sd-status-green" : "sd-status-orange"
					}">${this.esc(c.status)}</span></td>
                  <td>
                    <a class="sd-text-button" href="/desk/query-report/Accounts Receivable?customer=${encodeURIComponent(
						c.customer
					)}" target="_blank" rel="noopener">AR Ledger ↗</a>
                  </td>
                </tr>
              `
						)
						.join("") ||
					'<tr><td colspan="7" class="sd-empty">No customer financial records found.</td></tr>'
				}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Supplier Finance Analysis (Page 10) -->
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Supplier Finance & Spend Analysis (Page 10)</h2>
            <p>Purchase value, billed amounts, disbursements and payment obligations</p>
          </div>
        </div>
        <div class="sd-table-wrap">
          <table class="sd-table">
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Total Billed</th>
                <th>Disbursed / Paid</th>
                <th>Outstanding Payable</th>
                <th>Disbursement Rate</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${
					(d.supplier_finance || [])
						.map(
							(s) => `
                <tr>
                  <td><strong>${this.link("Supplier", s.supplier, s.supplier_name)}</strong></td>
                  <td>${this.formatCompact(s.billed, sym)}</td>
                  <td>${this.formatCompact(s.paid, sym)}</td>
                  <td><span class="${s.outstanding > 0 ? "sd-acc-crimson" : ""}">${this.formatCompact(
								s.outstanding,
								sym
							)}</span></td>
                  <td><span class="sd-pill ${s.payment_rate >= 80 ? "sd-status-green" : "sd-status-blue"}">${
								s.payment_rate
							}%</span></td>
                  <td><span class="sd-pill ${
						s.status === "Paid" ? "sd-status-green" : "sd-status-red"
					}">${this.esc(s.status)}</span></td>
                  <td>
                    <a class="sd-text-button" href="/desk/query-report/Accounts Payable?supplier=${encodeURIComponent(
						s.supplier
					)}" target="_blank" rel="noopener">AP Ledger ↗</a>
                  </td>
                </tr>
              `
						)
						.join("") ||
					'<tr><td colspan="7" class="sd-empty">No supplier financial records found.</td></tr>'
				}
            </tbody>
          </table>
        </div>
      </div>
    `;
	}

	renderAccountingKpis(k, sym) {
		if (!k) return "";
		const items = [
			{
				id: "rev",
				label: "Total Revenue",
				val: this.formatCompact(k.revenue.value, sym),
				sub: `${k.revenue.change >= 0 ? "▲ +" : "▼ "}${k.revenue.change}% vs prev period`,
				subClass: k.revenue.change >= 0 ? "sd-acc-green" : "sd-acc-red",
				accent: "blue",
				icon: "📈",
				tab: "revenue_expense",
				focus: "revenue",
				reportKey: "sales_invoices",
				reportLink: "/desk/query-report/General Ledger?account_type=Income Account",
			},
			{
				id: "exp",
				label: "Total Expenses",
				val: this.formatCompact(k.expense.value, sym),
				sub: `COGS: ${this.formatCompact(k.expense.cogs, sym)} · OpEx: ${this.formatCompact(
					k.expense.opex,
					sym
				)}`,
				subClass: "sd-acc-sub",
				accent: "rose",
				icon: "📉",
				tab: "revenue_expense",
				focus: "expense",
				reportKey: "purchase_invoices",
				reportLink: "/desk/query-report/General Ledger?account_type=Expense Account",
			},
			{
				id: "np",
				label: "Net Profit",
				val: this.formatCompact(k.net_profit.value, sym),
				sub: `Net Margin: ${k.net_profit.margin}% · ${k.net_profit.change >= 0 ? "▲ +" : "▼ "}${
					k.net_profit.change
				}%`,
				subClass: k.net_profit.value >= 0 ? "sd-acc-green" : "sd-acc-red",
				accent: "emerald",
				icon: "💎",
				tab: "profit_cash",
				focus: "waterfall",
				reportKey: "orders",
				reportLink: "/desk/query-report/Profit and Loss Statement",
			},
			{
				id: "cash",
				label: "Cash in Hand",
				val: this.formatCompact(k.cash_in_hand.value, sym),
				sub: "Liquid cash account balance",
				subClass: "sd-acc-sub",
				accent: "sky",
				icon: "💵",
				tab: "profit_cash",
				focus: "cash",
				reportKey: "inventory",
				reportLink: "/desk/query-report/General Ledger?account_type=Cash",
			},
			{
				id: "ar",
				label: "Receivables (AR)",
				val: this.formatCompact(k.receivables.value, sym),
				sub: `Overdue: ${this.formatCompact(k.receivables.overdue, sym)} (${
					k.receivables.count
				} invoices)`,
				subClass: k.receivables.overdue > 0 ? "sd-acc-orange" : "sd-acc-green",
				accent: "amber",
				icon: "📥",
				tab: "receivables_payables",
				focus: "ar",
				reportKey: "sales_invoices",
				subset: "overdue",
				reportLink: "/desk/query-report/Accounts Receivable",
			},
			{
				id: "ap",
				label: "Payables (AP)",
				val: this.formatCompact(k.payables.value, sym),
				sub: `Overdue: ${this.formatCompact(k.payables.overdue, sym)} (${k.payables.count} bills)`,
				subClass: k.payables.overdue > 0 ? "sd-acc-red" : "sd-acc-sub",
				accent: "crimson",
				icon: "📤",
				tab: "receivables_payables",
				focus: "ap",
				reportKey: "purchase_invoices",
				subset: "overdue",
				reportLink: "/desk/query-report/Accounts Payable",
			},
			{
				id: "tax",
				label: "Tax Liability",
				val: this.formatCompact(k.tax_liability.value, sym),
				sub: `Output: ${this.formatCompact(
					k.tax_liability.output_tax,
					sym
				)} · Input: ${this.formatCompact(k.tax_liability.input_tax, sym)}`,
				subClass: "sd-acc-sub",
				accent: "orange",
				icon: "⚖️",
				tab: "taxes_budget",
				focus: "tax",
				reportKey: "sales_invoices",
				reportLink: "/desk/query-report/General Ledger?account_type=Tax",
			},
			{
				id: "bgt",
				label: "Budget Used",
				val: `${k.budget_used.pct}%`,
				sub: `Approved: ${this.formatCompact(k.budget_used.approved, sym)}`,
				subClass: k.budget_used.pct > 100 ? "sd-acc-red" : "sd-acc-purple",
				accent: "purple",
				icon: "🎯",
				tab: "taxes_budget",
				focus: "budget",
				reportKey: "purchase_invoices",
				reportLink: "/desk/query-report/Budget Variance Report",
			},
			{
				id: "bank",
				label: "Bank Balance",
				val: this.formatCompact(k.bank_balance.value, sym),
				sub: `${k.bank_balance.accounts_count} active bank account(s)`,
				subClass: "sd-acc-sub",
				accent: "teal",
				icon: "🏦",
				tab: "profit_cash",
				focus: "bank",
				reportKey: "inventory",
				reportLink: "/desk/query-report/Bank Clearance Summary",
			},
		];

		return items
			.map((it) => {
				const isActive = this.accActiveKpi === it.id;
				return `
        <div class="sd-acc-kpi-card sd-acc-kpi-${it.accent} ${isActive ? "active" : ""}" data-acc-kpi="${
					it.id
				}" data-acc-target-tab="${it.tab}" data-acc-focus="${
					it.focus
				}" role="button" tabindex="0" title="Click to view ${it.label} details">
          <div class="sd-acc-kpi-bar"></div>
          <div class="sd-acc-kpi-head">
            <span class="sd-acc-kpi-icon">${this.workspaceIcon(it.label)}</span>
            <span class="sd-acc-kpi-label">${it.label}</span>
            <span class="sd-acc-kpi-badge ${
				isActive ? "active" : ""
			}" data-action="open-kpi-records" data-report="${it.reportKey}" data-subset="${
					it.subset || ""
				}" data-label="${this.esc(it.label)}" title="Click to view records list in dialog">${
					isActive ? "Active" : "Details ➔"
				}</span>
          </div>
          <div class="sd-acc-kpi-value">${it.val}</div>
          <div class="sd-acc-kpi-sub ${it.subClass}">${it.sub}</div>
          <div class="sd-acc-kpi-foot">
            <span class="sd-acc-kpi-hint">${isActive ? "▼ Viewing Section" : "Click for details"}</span>
            <button type="button" class="sd-acc-kpi-modal-btn" data-action="open-kpi-records" data-report="${
				it.reportKey
			}" data-subset="${it.subset || ""}" data-label="${this.esc(it.label)}" title="View ${this.esc(
					it.label
				)} records list">View Records ▤</button>
          </div>
        </div>
      `;
			})
			.join("");
	}

	renderProfitWaterfall(w, sym) {
		if (!w) return "";
		const isProfit = w.net_profit >= 0;
		return `
      <div class="sd-panel sd-acc-waterfall-panel" data-acc-section="waterfall">
        <div class="sd-panel-heading">
          <div>
            <h2>Profitability Waterfall Architecture (Page 7)</h2>
            <p>Explaining how Revenue translates into Gross Profit, Operating Profit and Net Profit</p>
          </div>
          <span class="sd-pill ${isProfit ? "sd-status-green" : "sd-status-red"}">
            Net Margin: ${w.net_margin}%
          </span>
        </div>
        <div class="sd-acc-waterfall-container">
          <div class="sd-acc-wf-step sd-acc-wf-inflow">
            <div class="sd-acc-wf-badge">1. INFLOW</div>
            <div class="sd-acc-wf-val">+${this.formatCompact(w.gross_revenue, sym)}</div>
            <div class="sd-acc-wf-title">Gross Revenue</div>
            <small>Sales Invoices & Income</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-outflow">
            <div class="sd-acc-wf-badge">2. DIRECT</div>
            <div class="sd-acc-wf-val">-${this.formatCompact(w.cogs, sym)}</div>
            <div class="sd-acc-wf-title">COGS</div>
            <small>Direct Material & Production</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-subtotal">
            <div class="sd-acc-wf-badge">3. SUB-RESULT</div>
            <div class="sd-acc-wf-val">${this.formatCompact(w.gross_profit, sym)}</div>
            <div class="sd-acc-wf-title">Gross Profit</div>
            <small>${w.gross_margin}% Margin</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-outflow">
            <div class="sd-acc-wf-badge">4. OVERHEAD</div>
            <div class="sd-acc-wf-val">-${this.formatCompact(w.operating_expense, sym)}</div>
            <div class="sd-acc-wf-title">Operating Expenses</div>
            <small>Admin, Selling, Utilities</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-subtotal">
            <div class="sd-acc-wf-badge">5. OPERATING</div>
            <div class="sd-acc-wf-val">${this.formatCompact(w.operating_profit, sym)}</div>
            <div class="sd-acc-wf-title">Operating Profit</div>
            <small>EBIT Operational Base</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-outflow">
            <div class="sd-acc-wf-badge">6. DEDUCTIONS</div>
            <div class="sd-acc-wf-val">-${this.formatCompact(w.finance_cost + w.tax_expense, sym)}</div>
            <div class="sd-acc-wf-title">Finance & Taxes</div>
            <small>Interest, GST/VAT & Taxes</small>
          </div>
          <div class="sd-acc-wf-connector">➔</div>

          <div class="sd-acc-wf-step sd-acc-wf-final ${isProfit ? "positive" : "negative"}">
            <div class="sd-acc-wf-badge">7. BOTTOM LINE</div>
            <div class="sd-acc-wf-val">${isProfit ? "+" : ""}${this.formatCompact(w.net_profit, sym)}</div>
            <div class="sd-acc-wf-title">Net Profit</div>
            <small>${w.net_margin}% Net Margin</small>
          </div>
        </div>
      </div>
    `;
	}

	renderRevenueExpenseTrend(trends, sym) {
		if (!trends || !trends.labels || !trends.labels.length) return "";
		const maxVal = Math.max(...trends.revenue, ...trends.expense, 100);
		const n = trends.labels.length;
		const w = 620,
			h = 200,
			padLeft = 45,
			padRight = 20,
			padTop = 20,
			padBottom = 30;
		const plotW = w - padLeft - padRight;
		const plotH = h - padTop - padBottom;

		const getX = (i) => padLeft + (i / (n - 1 || 1)) * plotW;
		const getY = (v) => padTop + plotH - (Math.max(0, v) / maxVal) * plotH;

		const revPoints = trends.revenue.map((v, i) => `${getX(i)},${getY(v)}`).join(" ");
		const expPoints = trends.expense.map((v, i) => `${getX(i)},${getY(v)}`).join(" ");
		const profitPoints = trends.profit.map((v, i) => `${getX(i)},${getY(v)}`).join(" ");

		return `
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Revenue vs Expense Trend (Last 6 Months)</h2>
            <p>Monthly performance from submitted GL entries</p>
          </div>
          <div class="sd-acc-chart-legend">
            <span class="sd-acc-leg-item"><i style="background:#2563eb"></i> Revenue</span>
            <span class="sd-acc-leg-item"><i style="background:#e11d48"></i> Expenses</span>
            <span class="sd-acc-leg-item"><i style="background:#059669"></i> Profit</span>
          </div>
        </div>
        <div class="sd-acc-svg-wrap">
          <svg class="sd-acc-trend-svg" viewBox="0 0 ${w} ${h}">
            <!-- Grid Lines -->
            <line x1="${padLeft}" y1="${padTop}" x2="${
			w - padRight
		}" y2="${padTop}" stroke="#f1f5f9" stroke-width="1" />
            <line x1="${padLeft}" y1="${padTop + plotH / 2}" x2="${w - padRight}" y2="${
			padTop + plotH / 2
		}" stroke="#f1f5f9" stroke-width="1" />
            <line x1="${padLeft}" y1="${padTop + plotH}" x2="${w - padRight}" y2="${
			padTop + plotH
		}" stroke="#e2e8f0" stroke-width="1" />

            <!-- Polylines -->
            <polyline fill="none" stroke="#2563eb" stroke-width="3" points="${revPoints}" />
            <polyline fill="none" stroke="#e11d48" stroke-width="3" stroke-dasharray="4" points="${expPoints}" />
            <polyline fill="none" stroke="#059669" stroke-width="3" points="${profitPoints}" />

            <!-- Circles -->
            ${trends.revenue
				.map(
					(v, i) =>
						`<circle cx="${getX(i)}" cy="${getY(
							v
						)}" r="4" fill="#2563eb"><title>Revenue: ${this.formatCompact(
							v,
							sym
						)}</title></circle>`
				)
				.join("")}
            ${trends.expense
				.map(
					(v, i) =>
						`<circle cx="${getX(i)}" cy="${getY(
							v
						)}" r="4" fill="#e11d48"><title>Expense: ${this.formatCompact(
							v,
							sym
						)}</title></circle>`
				)
				.join("")}
            ${trends.profit
				.map(
					(v, i) =>
						`<circle cx="${getX(i)}" cy="${getY(
							v
						)}" r="4" fill="#059669"><title>Profit: ${this.formatCompact(
							v,
							sym
						)}</title></circle>`
				)
				.join("")}

            <!-- X Labels -->
            ${trends.labels
				.map(
					(l, i) =>
						`<text x="${getX(i)}" y="${
							h - 8
						}" text-anchor="middle" font-size="11" fill="#64748b">${this.esc(l)}</text>`
				)
				.join("")}
          </svg>
        </div>
      </div>
    `;
	}

	renderExpenseCategories(categories, sym) {
		if (!categories || !categories.length) return "";
		return `
      <div class="sd-panel" data-acc-section="expense">
        <div class="sd-panel-heading">
          <div>
            <h2>Expense Composition by Category (Page 6)</h2>
            <p>Operational cost allocation across accounting groups</p>
          </div>
        </div>
        <div class="sd-acc-categories-list">
          ${categories
				.map(
					(c) => `
            <div class="sd-acc-cat-row">
              <div class="sd-acc-cat-header">
                <span class="sd-acc-cat-name">${this.esc(c.category)}</span>
                <span class="sd-acc-cat-val">${this.formatCompact(c.amount, sym)} <b>(${c.pct}%)</b></span>
              </div>
              <div class="sd-progress sd-acc-cat-bar">
                <i style="width:${Math.min(100, c.pct)}%; background:${c.color};"></i>
              </div>
            </div>
          `
				)
				.join("")}
        </div>
      </div>
    `;
	}

	renderCashLiquidity(cash, sym) {
		if (!cash) return "";
		return `
      <div class="sd-panel" data-acc-section="cash">
        <div class="sd-panel-heading">
          <div>
            <h2>Cash & Liquidity Control Tower (Page 7)</h2>
            <p>Cash movement, active bank balances and real-time reconciliation</p>
          </div>
          <span class="sd-pill sd-status-blue">Total Liquid Funds: ${this.formatCompact(
				cash.total_cash,
				sym
			)}</span>
        </div>

        <div class="sd-acc-kpis-grid sd-acc-cash-strip">
          <div class="sd-acc-kpi-card sd-acc-kpi-teal">
            <div class="sd-acc-kpi-bar"></div>
            <div class="sd-acc-kpi-label">Bank Balances</div>
            <div class="sd-acc-kpi-value">${this.formatCompact(cash.bank_balance, sym)}</div>
            <small class="sd-acc-sub">Across all connected accounts</small>
          </div>
          <div class="sd-acc-kpi-card sd-acc-kpi-sky">
            <div class="sd-acc-kpi-bar"></div>
            <div class="sd-acc-kpi-label">Cash in Hand</div>
            <div class="sd-acc-kpi-value">${this.formatCompact(cash.cash_in_hand, sym)}</div>
            <small class="sd-acc-sub">Petty cash & physical drawers</small>
          </div>
          <div class="sd-acc-kpi-card sd-acc-kpi-emerald">
            <div class="sd-acc-kpi-bar"></div>
            <div class="sd-acc-kpi-label">Customer Collections</div>
            <div class="sd-acc-kpi-value">${this.formatCompact(cash.collections, sym)}</div>
            <small class="sd-acc-green">Payment Entries received</small>
          </div>
          <div class="sd-acc-kpi-card sd-acc-kpi-crimson">
            <div class="sd-acc-kpi-bar"></div>
            <div class="sd-acc-kpi-label">Supplier Payments</div>
            <div class="sd-acc-kpi-value">${this.formatCompact(cash.supplier_payments, sym)}</div>
            <small class="sd-acc-red">Payment Entries disbursed</small>
          </div>
          <div class="sd-acc-kpi-card ${
				cash.net_cash_movement >= 0 ? "sd-acc-kpi-emerald" : "sd-acc-kpi-rose"
			}">
            <div class="sd-acc-kpi-bar"></div>
            <div class="sd-acc-kpi-label">Net Cash Movement</div>
            <div class="sd-acc-kpi-value">${cash.net_cash_movement >= 0 ? "+" : ""}${this.formatCompact(
			cash.net_cash_movement,
			sym
		)}</div>
            <small class="${
				cash.net_cash_movement >= 0 ? "sd-acc-green" : "sd-acc-red"
			}">Inflow minus Outflow</small>
          </div>
        </div>

        <h3 class="sd-acc-subhead">Bank Accounts Ledger Status</h3>
        <div class="sd-table-wrap" data-acc-section="bank">
          <table class="sd-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Type</th>
                <th>Currency</th>
                <th>Current Balance</th>
                <th>Reconciliation</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${
					(cash.bank_accounts || [])
						.map(
							(b) => `
                <tr>
                  <td><strong>${this.link("Account", b.account, b.account_name || b.account)}</strong></td>
                  <td>${this.esc(b.account_type)}</td>
                  <td><span class="sd-pill">${this.esc(b.currency)}</span></td>
                  <td><b>${this.formatCompact(b.balance, sym)}</b></td>
                  <td><span class="sd-pill sd-status-green">● ${this.esc(b.reconciliation_status)}</span></td>
                  <td>
                    <a class="sd-text-button" href="/desk/query-report/General Ledger?account=${encodeURIComponent(
						b.account
					)}" target="_blank" rel="noopener">Ledger ↗</a>
                  </td>
                </tr>
              `
						)
						.join("") ||
					'<tr><td colspan="6" class="sd-empty">No Bank/Cash accounts found for this selection.</td></tr>'
				}
            </tbody>
          </table>
        </div>
      </div>
    `;
	}

	renderAgeingSection(ageing, sym) {
		if (!ageing) return "";
		const ar = ageing.receivables || { buckets: {}, items: [] };
		const ap = ageing.payables || { buckets: {}, items: [] };

		return `
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>7. Receivables, Payables & Banking Ageing Control (Page 8)</h2>
            <p>Aging analysis, credit exposure and payment obligation tracking</p>
          </div>
        </div>

        <div class="sd-acc-grid-2">
          <!-- Receivables Ageing Buckets -->
          <div class="sd-acc-sub-panel" data-acc-section="ar">
            <h3 class="sd-acc-subhead">📥 Accounts Receivable (AR) Ageing</h3>
            <div class="sd-acc-buckets-grid">
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="sales_invoices" data-label="AR Current Invoices" role="button" tabindex="0" title="Click to view AR Invoices">
                <span>Current</span>
                <strong>${this.formatCompact(ar.buckets.current, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="sales_invoices" data-subset="overdue" data-label="AR 1-30 Days Invoices" role="button" tabindex="0" title="Click to view AR Invoices">
                <span>1–30 Days</span>
                <strong class="sd-acc-amber">${this.formatCompact(ar.buckets.days_1_30, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="sales_invoices" data-subset="overdue" data-label="AR 31-60 Days Invoices" role="button" tabindex="0" title="Click to view AR Invoices">
                <span>31–60 Days</span>
                <strong class="sd-acc-orange">${this.formatCompact(ar.buckets.days_31_60, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="sales_invoices" data-subset="overdue" data-label="AR 61-90 Days Invoices" role="button" tabindex="0" title="Click to view AR Invoices">
                <span>61–90 Days</span>
                <strong class="sd-acc-red">${this.formatCompact(ar.buckets.days_61_90, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="sales_invoices" data-subset="overdue" data-label="AR 90+ Days Invoices" role="button" tabindex="0" title="Click to view AR Invoices">
                <span>90+ Days</span>
                <strong class="sd-acc-red">${this.formatCompact(ar.buckets.days_90_plus, sym)}</strong>
              </div>
            </div>
            <div class="sd-table-wrap">
              <table class="sd-table">
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Invoice</th>
                    <th>Due Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  ${
						(ar.items || [])
							.slice(0, 8)
							.map(
								(it) => `
                    <tr>
                      <td>${this.link("Customer", it.party)}</td>
                      <td>${this.link("Sales Invoice", it.document)}</td>
                      <td>${this.esc(it.due_date)}</td>
                      <td><b>${this.formatCompact(it.amount, sym)}</b></td>
                      <td><span class="sd-pill ${it.is_overdue ? "sd-status-red" : "sd-status-green"}">${
									it.status
								}</span></td>
                    </tr>
                  `
							)
							.join("") ||
						'<tr><td colspan="5" class="sd-empty">No outstanding customer invoices.</td></tr>'
					}
                </tbody>
              </table>
            </div>
          </div>

          <!-- Payables Ageing Buckets -->
          <div class="sd-acc-sub-panel" data-acc-section="ap">
            <h3 class="sd-acc-subhead">📤 Accounts Payable (AP) Ageing</h3>
            <div class="sd-acc-buckets-grid">
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="purchase_invoices" data-subset="overdue" data-label="AP Due This Week" role="button" tabindex="0" title="Click to view AP Bills">
                <span>Due This Week</span>
                <strong>${this.formatCompact(ap.buckets.due_week, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="purchase_invoices" data-subset="overdue" data-label="AP Due This Month" role="button" tabindex="0" title="Click to view AP Bills">
                <span>Due This Month</span>
                <strong class="sd-acc-amber">${this.formatCompact(ap.buckets.due_month, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="purchase_invoices" data-subset="overdue" data-label="AP 31-60 Days Bills" role="button" tabindex="0" title="Click to view AP Bills">
                <span>31–60 Days</span>
                <strong class="sd-acc-orange">${this.formatCompact(ap.buckets.days_31_60, sym)}</strong>
              </div>
              <div class="sd-acc-bucket-box" data-action="open-kpi-records" data-report="purchase_invoices" data-subset="overdue" data-label="AP 90+ Days Bills" role="button" tabindex="0" title="Click to view AP Bills">
                <span>90+ Days</span>
                <strong class="sd-acc-red">${this.formatCompact(ap.buckets.days_90_plus, sym)}</strong>
              </div>
            </div>
            <div class="sd-table-wrap">
              <table class="sd-table">
                <thead>
                  <tr>
                    <th>Supplier</th>
                    <th>Bill</th>
                    <th>Due Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  ${
						(ap.items || [])
							.slice(0, 8)
							.map(
								(it) => `
                    <tr>
                      <td>${this.link("Supplier", it.party)}</td>
                      <td>${this.link("Purchase Invoice", it.document)}</td>
                      <td>${this.esc(it.due_date)}</td>
                      <td><b>${this.formatCompact(it.amount, sym)}</b></td>
                      <td><span class="sd-pill ${it.is_overdue ? "sd-status-red" : "sd-status-blue"}">${
									it.status
								}</span></td>
                    </tr>
                  `
							)
							.join("") ||
						'<tr><td colspan="5" class="sd-empty">No outstanding supplier payables.</td></tr>'
					}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
	}

	renderBudgetTaxes(bva, taxes, sym) {
		return `
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Budget vs Actual Performance (Page 9)</h2>
            <p>Budget variance, statutory liabilities and tax optimization</p>
          </div>
        </div>

        <div class="sd-acc-grid-2">
          <!-- Tax KPIs -->
          <div class="sd-acc-sub-panel" data-acc-section="tax">
            <h3 class="sd-acc-subhead">Statutory & Tax Liability</h3>
            <div class="sd-acc-tax-cards">
              <div class="sd-acc-tax-card">
                <span>Output Tax (Sales GST/VAT)</span>
                <strong>${this.formatCompact(taxes?.output_tax || 0, sym)}</strong>
              </div>
              <div class="sd-acc-tax-card">
                <span>Input Tax (Purchases GST/VAT)</span>
                <strong>${this.formatCompact(taxes?.input_tax || 0, sym)}</strong>
              </div>
              <div class="sd-acc-tax-card sd-acc-tax-highlight">
                <span>Net Tax Liability</span>
                <strong class="sd-acc-orange">${this.formatCompact(taxes?.value || 0, sym)}</strong>
              </div>
            </div>
          </div>

          <!-- Budget vs Actual Table -->
          <div class="sd-acc-sub-panel" data-acc-section="budget">
            <h3 class="sd-acc-subhead">Budget vs Actual Utilization</h3>
            <div class="sd-table-wrap">
              <table class="sd-table">
                <thead>
                  <tr>
                    <th>Cost Center / Account</th>
                    <th>Budget</th>
                    <th>Actual</th>
                    <th>Variance</th>
                    <th>Utilization</th>
                  </tr>
                </thead>
                <tbody>
                  ${
						(bva || [])
							.map(
								(b) => `
                    <tr>
                      <td><strong>${this.esc(b.cost_center)}</strong><br><small>${this.esc(
									b.account
								)}</small></td>
                      <td>${this.formatCompact(b.budget, sym)}</td>
                      <td>${this.formatCompact(b.actual, sym)}</td>
                      <td class="${b.variance >= 0 ? "sd-acc-green" : "sd-acc-red"}">
                        ${b.variance >= 0 ? "+" : ""}${this.formatCompact(b.variance, sym)}
                      </td>
                      <td>
                        <div class="sd-progress-cell">
                          <span>${b.utilization}%</span>
                          <div class="sd-progress">
                            <i style="width:${Math.min(100, b.utilization)}%; background:${
									b.utilization > 100 ? "#dc2626" : "#7c3aed"
								};"></i>
                          </div>
                        </div>
                      </td>
                    </tr>
                  `
							)
							.join("") ||
						'<tr><td colspan="5" class="sd-empty">No budget records found.</td></tr>'
					}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
	}

	renderProjectFinance(projects, sym) {
		return `
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Project Financial Intelligence (Page 10)</h2>
            <p>Bridging manufacturing shop-floor execution with project commercial profitability</p>
          </div>
        </div>

        <div class="sd-table-wrap">
          <table class="sd-table">
            <thead>
              <tr>
                <th>Project</th>
                <th>Customer</th>
                <th>Contract Value</th>
                <th>Invoiced</th>
                <th>Collected</th>
                <th>Outstanding</th>
                <th>Total Cost</th>
                <th>Profit</th>
                <th>Margin %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${
					(projects || [])
						.map(
							(p) => `
                <tr>
                  <td><strong>${this.link("Project", p.project, p.project_name)}</strong></td>
                  <td>${this.esc(p.customer)}</td>
                  <td>${this.formatCompact(p.contract_value, sym)}</td>
                  <td>${this.formatCompact(p.invoiced, sym)}</td>
                  <td>${this.formatCompact(p.collected, sym)}</td>
                  <td><span class="${p.outstanding > 0 ? "sd-acc-amber" : ""}">${this.formatCompact(
								p.outstanding,
								sym
							)}</span></td>
                  <td>${this.formatCompact(p.total_cost, sym)}</td>
                  <td class="${p.profit >= 0 ? "sd-acc-green" : "sd-acc-red"}">
                    <b>${p.profit >= 0 ? "+" : ""}${this.formatCompact(p.profit, sym)}</b>
                  </td>
                  <td><span class="sd-pill ${
						p.margin_pct >= 20
							? "sd-status-green"
							: p.margin_pct >= 0
							? "sd-status-blue"
							: "sd-status-red"
					}">${p.margin_pct}%</span></td>
                  <td>${this.badge(p.status)}</td>
                </tr>
              `
						)
						.join("") ||
					'<tr><td colspan="10" class="sd-empty">No project financial records found.</td></tr>'
				}
            </tbody>
          </table>
        </div>
      </div>
    `;
	}

	renderAuditChecklist(checklist) {
		return `
      <div class="sd-panel">
        <div class="sd-panel-heading">
          <div>
            <h2>Month-End & Year-End Control Tower Checklist (Page 16 & 17)</h2>
            <p>Operational verification checklist ensuring GL integrity and reporting readiness</p>
          </div>
        </div>

        <div class="sd-acc-checklist-grid">
          ${(checklist || [])
				.map(
					(c) => `
            <div class="sd-acc-check-item ${c.done ? "checked" : ""}">
              <div class="sd-acc-check-box">${c.done ? "✓" : "○"}</div>
              <div class="sd-acc-check-text">
                <strong>${this.esc(c.check)}</strong>
                <a href="/desk/query-report/${encodeURIComponent(
					c.report
				)}" target="_blank" rel="noopener">Open ${this.esc(c.report)} ↗</a>
              </div>
            </div>
          `
				)
				.join("")}
        </div>
      </div>
    `;
	}

	/* ==========================================================================
     Sarathi Industrial AI Agent Chatbot Methods (Ultra-Modern Live UI)
     ========================================================================== */
	initAiAssistant() {
		if (document.getElementById("sarathiAiFab")) return;

		// 1. Create Top Real-time Live Banner on Dashboard
		if (!document.getElementById("sarathiLiveBanner")) {
			const banner = document.createElement("div");
			banner.className = "sd-live-banner";
			banner.id = "sarathiLiveBanner";
			banner.innerHTML = `
        <span class="sd-live-beacon"></span>
        <span class="sd-live-banner-title">⚡ Real-time Live Change:</span>
        <span class="sd-live-banner-text" id="sarathiLiveBannerText">Record synchronized</span>
        <button type="button" class="sd-live-banner-btn" id="sarathiLiveBannerBtn">Inspect in Dashboard</button>
        <button type="button" class="sd-live-banner-close" id="sarathiLiveBannerClose">✕</button>
      `;
			document.body.appendChild(banner);
			document.getElementById("sarathiLiveBannerClose")?.addEventListener("click", () => {
				banner.classList.remove("active");
			});
		}

		// 2. Create Floating Action Button (FAB)
		const fab = document.createElement("button");
		fab.className = "sd-ai-fab";
		fab.id = "sarathiAiFab";
		fab.title = "Open Sarathi AI Assistant (Autonomous ERPNext v16)";
		fab.innerHTML = `
      <div class="sd-ai-fab-pulse"></div>
      <span class="sd-ai-fab-icon">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h2a5 5 0 0 1 5 5v1h1a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-1v1a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-1H3a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h1v-1a5 5 0 0 1 5-5h2V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2z" fill="#00f2fe"/>
          <circle cx="8.5" cy="13.5" r="1.5" fill="#0b1320"/>
          <circle cx="15.5" cy="13.5" r="1.5" fill="#0b1320"/>
          <path d="M9 17.5c1 .8 2 .8 3 .8s2 0 3-.8" stroke="#0b1320" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="sd-ai-fab-text">✨ AI Agent</span>
      <span class="sd-ai-fab-status-dot"></span>
    `;
		document.body.appendChild(fab);

		// 3. Create Chat Window
		const win = document.createElement("div");
		win.className = "sd-ai-chat-window";
		win.id = "sarathiAiChatWindow";
		win.style.display = "none";
		win.innerHTML = `
      <div class="sd-ai-chat-header">
        <div class="sd-ai-chat-header-title">
          <div class="sd-ai-avatar">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h2a5 5 0 0 1 5 5v1h1a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-1v1a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-1H3a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h1v-1a5 5 0 0 1 5-5h2V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2z" fill="#00f2fe"/>
              <circle cx="8.5" cy="13.5" r="1.5" fill="#0b1320"/>
              <circle cx="15.5" cy="13.5" r="1.5" fill="#0b1320"/>
              <path d="M9 17.5c1 .8 2 .8 3 .8s2 0 3-.8" stroke="#0b1320" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="sd-ai-header-text">
            <h3>Sarathi Industrial AI Agent</h3>
            <p><span class="sd-ai-online-dot"></span> Online · ERPNext v16 Engine</p>
          </div>
        </div>
        <div class="sd-ai-chat-actions">
          <button class="sd-ai-btn-icon" id="sarathiAiClearBtn" title="Clear Conversation">🗑️</button>
          <button class="sd-ai-btn-icon" id="sarathiAiResetBtn" title="Reset Session">🔄</button>
          <button class="sd-ai-btn-icon" id="sarathiAiExpandBtn" title="Toggle Wide View">⛶</button>
          <button class="sd-ai-btn-icon" id="sarathiAiCloseBtn" title="Close">✕</button>
        </div>
      </div>
      <div class="sd-ai-chat-body" id="sarathiAiChatBody">
        <div class="sd-ai-msg sd-ai-msg-bot">
          👋 Hello! I am your <strong>Sarathi Industrial AI Agent</strong>.<br><br>
          I provide real-time execution across all 13 ERPNext modules and 98 sections:
          <ul class="sd-ai-ul">
            <li class="sd-ai-li"><strong>🚀 Create Entities:</strong> <em>'Create a project'</em>, <em>'New account setup'</em>, <em>'Add customer'</em>, <em>'New Work Order'</em></li>
            <li class="sd-ai-li"><strong>⚡ Live Changes:</strong> <em>'Show live changes'</em> to see real-time database activity</li>
            <li class="sd-ai-li"><strong>📦 Inventory & Stock:</strong> <em>'Check stock in Stores'</em></li>
          </ul>
          Click a quick action below or type your instruction!
        </div>
      </div>
      <div class="sd-ai-chips" id="sarathiAiChips"></div>
      <div class="sd-ai-chat-footer">
        <textarea class="sd-ai-input" id="sarathiAiInput" rows="1" placeholder="Ask AI... (e.g. 'Create a project', 'Show live changes')"></textarea>
        <button class="sd-ai-send-btn" id="sarathiAiSendBtn" title="Send Instruction">➤</button>
      </div>
    `;
		document.body.appendChild(win);

		// Event listeners
		fab.addEventListener("click", () => this.toggleAiChat());
		document
			.getElementById("sarathiAiCloseBtn")
			?.addEventListener("click", () => this.toggleAiChat(false));
		document.getElementById("sarathiAiClearBtn")?.addEventListener("click", () => {
			this.clearAiConversation();
		});
		document.getElementById("sarathiAiResetBtn")?.addEventListener("click", () => {
			this.sendAiMessage("reset");
		});
		document.getElementById("sarathiAiExpandBtn")?.addEventListener("click", () => {
			win.classList.toggle("sd-ai-expanded");
		});

		const input = document.getElementById("sarathiAiInput");
		const sendBtn = document.getElementById("sarathiAiSendBtn");

		const doSend = () => {
			const txt = input.value.trim();
			if (!txt) return;
			input.value = "";
			this.sendAiMessage(txt);
		};

		sendBtn?.addEventListener("click", doSend);
		input?.addEventListener("keydown", (e) => {
			if (e.key === "Enter" && !e.shiftKey) {
				e.preventDefault();
				doSend();
			}
		});

		this.refreshAiChips();
	}

	clearAiConversation() {
		frappe.call({
			method: "sarathi_visibility.api.agent_chat.send_message",
			args: { message: "reset" },
			callback: () => {},
		});
		const body = document.getElementById("sarathiAiChatBody");
		if (body) {
			body.innerHTML = `
        <div class="sd-ai-msg sd-ai-msg-bot">
          👋 Hello! I am your <strong>Sarathi Industrial AI Agent</strong>.<br><br>
          ✨ <strong>Conversation cleared.</strong> Ready for your next instruction across all 13 ERPNext modules:
          <ul class="sd-ai-ul">
            <li class="sd-ai-li"><strong>🏢 Create Company:</strong> <em>'I want to create a new company'</em></li>
            <li class="sd-ai-li"><strong>🚀 Create Project:</strong> <em>'I want to create a project'</em></li>
            <li class="sd-ai-li"><strong>⚡ Live Changes:</strong> <em>'Show live changes'</em> to see real-time database activity</li>
            <li class="sd-ai-li"><strong>📦 Inventory & Stock:</strong> <em>'Check stock in Stores'</em></li>
          </ul>
          Click a quick action below or type your instruction!
        </div>
      `;
		}
		const input = document.getElementById("sarathiAiInput");
		if (input) {
			input.value = "";
			input.focus();
		}
		frappe.show_alert({ message: "Conversation history cleared", indicator: "blue" }, 2);
	}

	toggleAiChat(open) {
		const win = document.getElementById("sarathiAiChatWindow");
		if (!win) return;
		const isVisible = win.style.display !== "none";
		const nextState = open !== undefined ? open : !isVisible;
		win.style.display = nextState ? "flex" : "none";
		if (nextState) {
			document.getElementById("sarathiAiInput")?.focus();
			this.refreshAiChips();
		}
	}

	triggerLiveBanner(doctype, name, title = "") {
		const banner = document.getElementById("sarathiLiveBanner");
		const textEl = document.getElementById("sarathiLiveBannerText");
		const btn = document.getElementById("sarathiLiveBannerBtn");
		if (!banner || !textEl) return;

		textEl.innerHTML = `Created <strong>${this.esc(
			doctype
		)}</strong> <code style="background:#022c22;color:#6ee7b7;padding:2px 6px;border-radius:4px;">${this.esc(
			name
		)}</code> ${title ? `(${this.esc(title)})` : ""} · Dashboard Synchronized`;
		banner.classList.add("active");

		if (btn) {
			btn.onclick = () => {
				this.highlightDashboardEntity(doctype);
			};
		}

		clearTimeout(this._liveBannerTimer);
		this._liveBannerTimer = setTimeout(() => {
			banner.classList.remove("active");
		}, 8000);
	}

	highlightDashboardEntity(doctype) {
		let target = null;
		const dt = String(doctype || "").toLowerCase();
		if (dt.includes("company") || dt.includes("organization")) {
			target = this.el('[data-filter="company"]');
		} else if (dt.includes("project")) {
			target = this.el("[data-project-panel]") || this.el("[data-projects]");
		} else if (dt.includes("customer")) {
			target = this.el("[data-customer-panel]") || this.el("[data-customers]");
		} else if (dt.includes("account") || dt.includes("cost center")) {
			target = this.el("[data-accounting-card-panel]") || this.el("[data-accounting-cards]");
		} else if (dt.includes("work order") || dt.includes("production")) {
			target = this.el("[data-live-projects]");
		}

		if (target) {
			target.scrollIntoView({ behavior: "smooth", block: "center" });
			target.classList.remove("sd-live-highlight-pulse");
			void target.offsetWidth; // trigger reflow
			target.classList.add("sd-live-highlight-pulse");
			setTimeout(() => {
				target.classList.remove("sd-live-highlight-pulse");
			}, 3000);
		}
	}

	refreshAiChips() {
		const chipsContainer = document.getElementById("sarathiAiChips");
		if (!chipsContainer) return;
		const chips = [
			{ label: "🏢 Create Company", query: "I want to create a new company" },
			{ label: "🚀 Create Project", query: "I want to create a project" },
			{ label: "⚡ Live Changes", query: "Show live changes" },
			{ label: "💼 New Account Setup", query: "I want to create new Account setup" },
			{ label: "👥 Add Customer", query: "Create a new customer" },
			{ label: "📦 Check Stock", query: "Check stock in Stores" },
			{ label: "🏭 List Work Orders", query: "Show all Work Orders" },
		];
		if (this.filters.project) {
			chips.unshift({
				label: `📊 Status of ${this.filters.project}`,
				query: `Check status of ${this.filters.project}`,
			});
		} else if (this.filters.customer) {
			chips.unshift({
				label: `📂 Projects for ${this.filters.customer}`,
				query: `Show projects for ${this.filters.customer}`,
			});
		}
		chipsContainer.innerHTML = chips
			.map(
				(c) =>
					`<button class="sd-ai-chip" data-ai-query="${this.esc(c.query)}">${this.esc(
						c.label
					)}</button>`
			)
			.join("");

		chipsContainer.querySelectorAll("[data-ai-query]").forEach((el) => {
			el.addEventListener("click", () => {
				this.sendAiMessage(el.dataset.aiQuery);
			});
		});
	}

	appendAiMessage(sender, text, payload = null) {
		const body = document.getElementById("sarathiAiChatBody");
		if (!body) return;
		const msg = document.createElement("div");
		msg.className = `sd-ai-msg ${sender === "user" ? "sd-ai-msg-user" : "sd-ai-msg-bot"}`;

		if (sender === "user") {
			msg.innerHTML = `<div class="sd-ai-user-bubble">${this.esc(text)}</div>`;
		} else if (payload && payload.status === "COMPLETED" && payload.verified === true) {
			// 1. MASTERPIECE COLORFUL SUCCESS CARD (STRICT READ-BACK VERIFIED)
			const dt = payload.doctype || "Document";
			const name = payload.name || "Record";
			const dtUrl = `/app/${dt.toLowerCase().replace(/\s+/g, "-")}/${encodeURIComponent(name)}`;
			const fields = payload.fields || {};

			let attrGrid = "";
			const fieldKeys = Object.keys(fields);
			if (fieldKeys.length) {
				attrGrid = `
          <div class="sd-ai-attr-grid">
            ${fieldKeys
				.slice(0, 6)
				.map(
					(k) => `
              <div class="sd-ai-attr-pill">
                <span>${this.esc(k)}</span>
                <strong>${this.esc(fields[k])}</strong>
              </div>
            `
				)
				.join("")}
          </div>
        `;
			}

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-success">
          <div class="sd-ai-card-header">
            <span class="sd-ai-card-badge-live">● LIVE IN ERPNEXT</span>
            <span class="sd-ai-card-badge-verified">✓ READ-BACK VERIFIED</span>
            <h4>✨ ${this.esc(dt)} Created!</h4>
          </div>
          <div class="sd-ai-card-body">
            <div class="sd-ai-id-row">
              <span class="sd-ai-id-label">Record ID:</span>
              <code class="sd-ai-id-code">${this.esc(name)}</code>
            </div>
            ${attrGrid}
            <div class="sd-ai-card-text">${this.renderMarkdownLite(text)}</div>
          </div>
          <div class="sd-ai-card-actions">
            <a href="${dtUrl}" target="_blank" rel="noopener" class="sd-ai-action-btn sd-ai-btn-primary">
              🚀 Open ${this.esc(dt)} in Desk ↗
            </a>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-ai-refresh>
              ↻ Refresh Dashboard
            </button>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-ai-highlight>
              ⚡ Highlight in Dashboard
            </button>
          </div>
        </div>
      `;

			msg.querySelector("[data-ai-refresh]")?.addEventListener("click", () => {
				this.load();
				frappe.show_alert(
					{ message: "Dashboard reloaded with latest live records!", indicator: "green" },
					3
				);
			});
			msg.querySelector("[data-ai-highlight]")?.addEventListener("click", () => {
				this.highlightDashboardEntity(dt);
			});
		} else if (payload && payload.status === "COLLECTING_SLOTS") {
			// 2. INTERACTIVE QUESTIONNAIRE INTAKE CARD
			const dt = payload.doctype || payload.target_doctype || "Record";
			const missingDetails = payload.missing_details || [];
			const primaryMissing = missingDetails[0] ? missingDetails[0].label : "Name";
			const templateVal = `${primaryMissing}: `;

			const CURRENCY_LIST = [
				"INR",
				"USD",
				"EUR",
				"GBP",
				"AED",
				"SAR",
				"JPY",
				"CAD",
				"AUD",
				"SGD",
				"CHF",
				"CNY",
				"KWD",
				"QAR",
				"BHD",
				"OMR",
			];
			const COUNTRY_LIST = [
				"India",
				"United States",
				"United Kingdom",
				"United Arab Emirates",
				"Saudi Arabia",
				"Germany",
				"Canada",
				"Australia",
				"Singapore",
				"Japan",
				"France",
				"China",
				"Brazil",
				"South Africa",
			];

			const KNOWN_OPTIONS = {
				default_currency: CURRENCY_LIST,
				currency: CURRENCY_LIST,
				country: COUNTRY_LIST,
				company: ["SarathiAILabs"],
				customer_type: ["Company", "Individual"],
				supplier_type: ["Company", "Individual"],
				customer_group: [
					"All Customer Groups",
					"Commercial",
					"Individual",
					"Non Profit",
					"Government",
				],
				territory: ["All Territories", "India", "Rest Of The World"],
				supplier_group: [
					"All Supplier Groups",
					"Distributor",
					"Manufacturer",
					"Raw Material",
					"Services",
				],
				item_group: [
					"Products",
					"All Item Groups",
					"Raw Material",
					"Services",
					"Sub Assemblies",
					"Consumables",
				],
				stock_uom: ["Nos", "Box", "Kg", "Meter", "Unit", "Pair", "Set", "Hour"],
				uom: ["Nos", "Box", "Kg", "Meter", "Unit", "Pair", "Set", "Hour"],
				priority: ["Medium", "Low", "High", "Urgent"],
				status: ["Open", "Working", "Pending Review", "Overdue", "Completed", "Cancelled"],
				order_type: ["Sales", "Maintenance", "Shopping Cart"],
				material_request_type: [
					"Purchase",
					"Material Transfer",
					"Material Issue",
					"Manufacture",
					"Customer Provided",
				],
				stock_entry_type: [
					"Material Receipt",
					"Material Issue",
					"Material Transfer",
					"Manufacture",
					"Repack",
				],
				inspection_type: ["Incoming", "In Process", "Outgoing"],
				reference_type: [
					"Stock Entry",
					"Purchase Receipt",
					"Purchase Invoice",
					"Delivery Note",
					"Sales Invoice",
				],
				voucher_type: [
					"Journal Entry",
					"Bank Entry",
					"Cash Entry",
					"Credit Card Entry",
					"Debit Note",
					"Credit Note",
				],
				payment_type: ["Receive", "Pay", "Internal Transfer"],
				party_type: ["Customer", "Supplier", "Employee"],
				root_type: ["Expense", "Asset", "Liability", "Equity", "Income"],
				default_letter_head: ["", "Company Letterhead - Grey", "Standard Letterhead"],
				letter_head: ["", "Company Letterhead - Grey", "Standard Letterhead"],
				valuation_method: ["FIFO", "Moving Average", "LIFO"],
			};

			const formRowsHtml = missingDetails
				.map((m) => {
					const fieldKey = m.field;
					const fieldLabel = m.label || fieldKey.replace(/_/g, " ").toUpperCase();
					const isReqd = m.reqd !== false;
					const defaultVal = m.default !== undefined && m.default !== null ? m.default : "";
					let placeholder = m.hint || `Enter ${fieldLabel}`;

					const reqdBadge = isReqd
						? `<span style="color:#ef4444;font-weight:bold;margin-left:3px;">*</span>`
						: `<span style="color:#94a3b8;font-size:10.5px;font-weight:normal;margin-left:4px;">(Optional)</span>`;

					// Parse options (Array, newline-delimited string, or fallback to KNOWN_OPTIONS)
					let opts = null;
					if (Array.isArray(m.options) && m.options.length > 0) {
						opts = m.options;
					} else if (typeof m.options === "string" && m.options.trim()) {
						opts = m.options
							.split("\n")
							.map((s) => s.trim())
							.filter(Boolean);
					} else if (KNOWN_OPTIONS[fieldKey]) {
						opts = KNOWN_OPTIONS[fieldKey];
					}

					// 1. Dropdown select
					if (opts && opts.length > 0) {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <select class="sd-ai-intake-input sd-ai-intake-select" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(fieldLabel)}">
                ${opts
					.map(
						(opt) =>
							`<option value="${this.esc(opt)}" ${
								String(opt).toLowerCase() === String(defaultVal).toLowerCase()
									? "selected"
									: ""
							}>${this.esc(opt === "" ? "-- None --" : opt)}</option>`
					)
					.join("")}
              </select>
            </div>
          `;
					}

					// 2. Checkbox input
					if (m.fieldtype === "Check") {
						const isChecked = defaultVal == "1" || defaultVal === 1 || defaultVal === true;
						return `
            <div class="sd-ai-intake-form-row" style="margin-top:4px;">
              <label class="sd-ai-intake-label" style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                <input type="checkbox" class="sd-ai-intake-checkbox" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(fieldLabel)}" ${
							isChecked ? "checked" : ""
						} />
                <span>📌 ${this.esc(fieldLabel)} ${reqdBadge}</span>
              </label>
            </div>
          `;
					}

					// 3. Date input
					if (m.fieldtype === "Date") {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <input type="date" class="sd-ai-intake-input" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
							fieldLabel
						)}" value="${this.esc(defaultVal)}" />
            </div>
          `;
					}

					// 4. Number / Float / Int / Currency input
					if (["Float", "Int", "Currency", "Percent"].includes(m.fieldtype)) {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <input type="number" step="${
					m.fieldtype === "Int" ? "1" : "0.01"
				}" class="sd-ai-intake-input" data-intake-field="${this.esc(
							fieldKey
						)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
							fieldLabel
						)}" placeholder="${this.esc(placeholder)}" value="${this.esc(defaultVal)}" />
            </div>
          `;
					}

					// 5. Standard Text Inputs
					if (fieldKey === "company_name")
						placeholder = "e.g. Gaurav Manufacture private limited company";
					else if (fieldKey === "abbr") placeholder = "Auto-generated (e.g. GMplc or gmpl)";
					else if (fieldKey === "project_name") placeholder = "e.g. Office Furniture 2026";
					else if (fieldKey === "customer_name") placeholder = "e.g. Zenith Robotics Ltd";
					else if (fieldKey === "supplier_name") placeholder = "e.g. Precision Fasteners Ltd";
					else if (fieldKey === "item_code") placeholder = "e.g. ITEM-MOTOR-01";
					else if (fieldKey === "warehouse_name") placeholder = "e.g. Finished Goods Pune";

					return `
          <div class="sd-ai-intake-form-row">
            <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
            <input type="text" class="sd-ai-intake-input" data-intake-field="${this.esc(
				fieldKey
			)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
						fieldLabel
					)}" placeholder="${this.esc(placeholder)}" value="${this.esc(defaultVal)}" />
          </div>
        `;
				})
				.join("");

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-intake">
          <div class="sd-ai-intake-header">
            <h4>📋 Requirements Needed for ${this.esc(dt)}</h4>
            <span class="sd-ai-intake-badge">Slot Intake</span>
          </div>
          <div class="sd-ai-intake-desc">
            ${this.renderMarkdownLite(text)}
          </div>
          <div class="sd-ai-intake-form">
            ${formRowsHtml}
            <div class="sd-ai-intake-actions">
              <button type="button" class="sd-ai-action-btn sd-ai-btn-primary" data-intake-submit>
                🚀 Apply & Proceed
              </button>
              <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-intake-cancel>
                ✕ Cancel
              </button>
            </div>
          </div>
          <div style="margin-top:12px;font-size:11px;color:#94a3b8;">
            💬 <em>Or type directly in the chatbox below (e.g. <code>${this.esc(templateVal)}</code>)</em>
          </div>
        </div>
      `;

			// Auto-generate Abbreviation in real-time when user types company name (e.g. GMplc or gmpl)
			const compInp = msg.querySelector('[data-intake-field="company_name"]');
			const abbrInp = msg.querySelector('[data-intake-field="abbr"]');
			if (compInp && abbrInp) {
				compInp.addEventListener("input", () => {
					const raw = compInp.value.trim();
					if (raw) {
						const words = raw.split(/[\s\-_]+/).filter(Boolean);
						const genAbbr = words.map((w) => w.charAt(0)).join("");
						abbrInp.value = genAbbr;
					} else {
						abbrInp.value = "";
					}
				});
			}

			msg.querySelector("[data-intake-submit]")?.addEventListener("click", () => {
				const inputs = msg.querySelectorAll("[data-intake-field]");
				const vals = [];
				let missingReqd = false;
				let missingLabel = "";
				let primaryVal = "";
				const summaryParts = [];

				inputs.forEach((inp) => {
					let val = "";
					if (inp.type === "checkbox") {
						val = inp.checked ? "1" : "0";
					} else {
						val = inp.value.trim();
					}
					const fKey = inp.dataset.intakeField;
					const isReqd = inp.dataset.intakeReqd === "true";
					const fLabel = inp.dataset.intakeLabel || fKey;

					if (isReqd && !val) {
						missingReqd = true;
						if (!missingLabel) missingLabel = fLabel;
						inp.style.borderColor = "#ef4444";
					} else {
						inp.style.borderColor = "";
					}

					if (val) {
						vals.push(`${fKey}: ${val}`);
						if (
							!primaryVal &&
							[
								"company_name",
								"project_name",
								"customer_name",
								"supplier_name",
								"item_code",
								"warehouse_name",
								"subject",
								"email",
							].includes(fKey)
						) {
							primaryVal = val;
						} else if (fKey !== "doctype" && fKey !== "name") {
							summaryParts.push(`${fLabel}: ${val}`);
						}
					}
				});

				if (missingReqd) {
					frappe.show_alert(
						{ message: `Please enter mandatory field: ${missingLabel}`, indicator: "orange" },
						3
					);
					return;
				}

				if (vals.length > 0) {
					let displayText = vals.join(", ");
					if (primaryVal) {
						displayText =
							summaryParts.length > 0
								? `${primaryVal} (${summaryParts.slice(0, 3).join(", ")})`
								: primaryVal;
					}
					this.sendAiMessage(vals.join(", "), displayText);
				} else {
					frappe.show_alert(
						{
							message: "Please fill in the required field(s) or type in the chatbox below",
							indicator: "orange",
						},
						3
					);
				}
			});

			msg.querySelector("[data-intake-cancel]")?.addEventListener("click", () => {
				this.sendAiMessage("Cancel");
			});
		} else if (payload && payload.status === "AWAITING_CONFIRMATION") {
			// 3. INTERACTIVE PRE-MUTATION CONFIRMATION CARD
			const dt = payload.doctype || payload.target_doctype || "Record";
			const pValues = payload.pending_values || {};
			const actionSteps = payload.action_steps || [
				`${payload.module || dt} Skill loaded`,
				`${dt} DocType identified`,
				"Required fields available",
				"Permission checked",
				"Duplicate check completed",
			];

			const EXCLUDE_KEYS = new Set([
				"doctype",
				"name",
				"is_group",
				"allow_account_creation_against_child_company",
				"book_advance_payments_in_separate_party_account",
				"reconcile_on_advance_payment_date",
				"reconciliation_takes_effect_on",
				"auto_exchange_rate_revaluation",
				"submit_err_jv",
				"enable_perpetual_inventory",
				"enable_item_wise_inventory_account",
				"enable_provisional_accounting_for_non_stock_items",
				"valuation_method",
				"idx",
				"docstatus",
				"naming_series",
				"lft",
				"rgt",
				"old_parent",
				"disabled",
			]);

			let summaryHtml = "";
			const valKeys = Object.keys(pValues).filter(
				(k) =>
					!EXCLUDE_KEYS.has(k.toLowerCase()) &&
					pValues[k] !== undefined &&
					pValues[k] !== null &&
					pValues[k] !== ""
			);
			if (valKeys.length) {
				summaryHtml = `
          <div class="sd-ai-attr-grid" style="margin-top:10px;">
            ${valKeys
				.map(
					(k) => `
              <div class="sd-ai-attr-pill">
                <span>${this.esc(k.replace(/_/g, " ").toUpperCase())}</span>
                <strong>${this.esc(pValues[k])}</strong>
              </div>
            `
				)
				.join("")}
          </div>
        `;
			}

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-confirmation">
          <div class="sd-ai-confirm-header">
            <h4>📋 Ready to Create: ${this.esc(dt)}</h4>
            <span class="sd-ai-card-badge-confirm">⚡ Validation Complete</span>
          </div>
          <div class="sd-ai-confirm-body">
            <div class="sd-ai-validation-checklist">
              ${actionSteps
					.map(
						(step) => `
                <div class="sd-ai-check-item">
                  <span class="sd-ai-check-icon">✓</span>
                  <span>${this.esc(step)}</span>
                </div>
              `
					)
					.join("")}
            </div>
            ${summaryHtml}
            <div class="sd-ai-confirm-callout">
              Ready to create the <strong>${this.esc(dt)}</strong> in ERPNext. Please confirm to proceed.
            </div>
          </div>
          <div class="sd-ai-card-actions">
            <button type="button" class="sd-ai-action-btn sd-ai-btn-confirm" data-ai-confirm>
              ✓ Confirm & Create
            </button>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-cancel" data-ai-cancel>
              ✕ Cancel
            </button>
          </div>
        </div>
      `;

			msg.querySelector("[data-ai-confirm]")?.addEventListener("click", () => {
				this.sendAiMessage("Confirm");
			});
			msg.querySelector("[data-ai-cancel]")?.addEventListener("click", () => {
				this.sendAiMessage("Cancel");
			});
		} else if (payload && payload.status === "LIVE_CHANGES") {
			// 3. REAL-TIME ACTIVITY STREAM CARD
			const changes = payload.changes || [];
			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-changes">
          <div class="sd-ai-changes-header">
            <h4>⚡ Live System Activity</h4>
            <span class="sd-ai-card-badge-live">● REAL-TIME FEED</span>
          </div>
          <div class="sd-ai-changes-list">
            ${
				changes
					.map(
						(c) => `
              <div class="sd-ai-change-item">
                <div>
                  <a href="${c.url}" target="_blank" rel="noopener">${this.esc(c.doctype)}: ${this.esc(
							c.name
						)}</a>
                  <div style="font-size:11px;color:#94a3b8;margin-top:2px;">${this.esc(c.title)}</div>
                </div>
                <span class="sd-pill sd-status-blue">${this.esc(c.status)}</span>
              </div>
            `
					)
					.join("") || '<div class="sd-empty">No recent changes found.</div>'
			}
          </div>
        </div>
      `;
		} else {
			// Default formatted bubble
			msg.innerHTML = `
        <div class="sd-ai-bot-bubble">
          ${this.renderMarkdownLite(text)}
        </div>
      `;
		}

		body.appendChild(msg);
		body.scrollTop = body.scrollHeight;
	}

	sendAiMessage(text, displayText = null) {
		this.appendAiMessage("user", displayText || text);
		const body = document.getElementById("sarathiAiChatBody");

		// Add animated Live Multi-Step Execution Indicator
		const typing = document.createElement("div");
		typing.className = "sd-ai-typing-indicator";
		typing.id = "sarathiAiTyping";
		typing.innerHTML = `
      <div class="sd-ai-typing-top">
        <div class="sd-ai-live-spinner"></div>
        <span class="sd-ai-step-text" id="sarathiAiStepText">🔮 Analyzing intent & scanning 13 modules…</span>
      </div>
      <div class="sd-ai-progress-track">
        <div class="sd-ai-progress-bar"></div>
      </div>
    `;
		body.appendChild(typing);
		body.scrollTop = body.scrollHeight;

		// Dynamic step text cycle while server computes
		const stepEl = typing.querySelector("#sarathiAiStepText");
		const steps = [
			"⚙️ Checking schema prerequisites & dependencies…",
			"🚀 Executing ERPNext database transaction…",
			"📊 Auto-synchronizing live dashboard data…",
		];
		let stepIdx = 0;
		const stepTimer = setInterval(() => {
			if (stepEl && steps[stepIdx]) {
				stepEl.textContent = steps[stepIdx];
				stepIdx = (stepIdx + 1) % steps.length;
			}
		}, 1200);

		frappe.call({
			method: "sarathi_visibility.api.agent_chat.send_message",
			args: {
				message: text,
				company: this.filters.company || "SarathiAILabs",
				customer: this.filters.customer || "",
				project: this.filters.project || "",
			},
			callback: (r) => {
				clearInterval(stepTimer);
				typing.remove();
				if (r.message && r.message.message) {
					this.appendAiMessage("bot", r.message.message, r.message);

					// LIVE REAL-TIME DASHBOARD SYNCHRONIZATION (ONLY WHEN BACKEND VERIFIED === TRUE)
					if (r.message.status === "COMPLETED" && r.message.verified === true) {
						const dt = r.message.doctype || "Record";
						const name = r.message.name || "";

						// 1. Show Top Floating Live Banner on Dashboard!
						this.triggerLiveBanner(dt, name);

						// 2. Flash Glowing Border on Dashboard Section!
						this.highlightDashboardEntity(dt);

						// 3. Show Native Frappe Alert!
						frappe.show_alert(
							{
								message: `<span style="font-weight:700;">⚡ Real-time Live Change:</span> ${dt} <strong>${name}</strong> created. Dashboard synchronized!`,
								indicator: "green",
							},
							5
						);

						// 4. Reload Dashboard Data Immediately!
						this.load();
					}
				} else {
					this.appendAiMessage("bot", "Received response from agent.");
				}
			},
			error: (err) => {
				clearInterval(stepTimer);
				typing.remove();
				this.appendAiMessage(
					"bot",
					"⚠️ Communication error with Sarathi AI Agent. Please check server logs."
				);
			},
		});
	}

	renderMarkdownLite(md) {
		if (!md) return "";
		let html = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

		// Bold
		html = html.replace(/\*\*(.+?)\*\*/g, "<strong class='sd-ai-bold'>$1</strong>");
		// Italic
		html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
		// Inline code
		html = html.replace(/`([^`]+)`/g, "<code class='sd-ai-code'>$1</code>");
		// Markdown links [text](url)
		html = html.replace(
			/\[([^\]]+)\]\(([^)]+)\)/g,
			'<a href="$2" target="_blank" rel="noopener" class="sd-ai-link">$1 ↗</a>'
		);
		// Blockquotes
		html = html.replace(/^>\s*(.+)$/gm, "<div class='sd-ai-quote'>$1</div>");
		// Lists
		html = html.replace(/^\s*-\s+(.+)$/gm, "<li class='sd-ai-li'>$1</li>");
		html = html.replace(/(<li class='sd-ai-li'>.+<\/li>)/gs, "<ul class='sd-ai-ul'>$1</ul>");
		// Numbered lists
		html = html.replace(
			/^\s*(\d+)\.\s+(.+)$/gm,
			"<div class='sd-ai-num-step'><span class='sd-ai-step-badge'>$1</span><span>$2</span></div>"
		);
		// Line breaks
		html = html.replace(/\n\n/g, "<div class='sd-ai-gap'></div>").replace(/\n/g, "<br>");
		return html;
	}
};
