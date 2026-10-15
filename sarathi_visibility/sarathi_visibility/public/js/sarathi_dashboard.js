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
			hide_sidebar: true,
		});
		this.root = $(frappe.render_template("sarathicontroltower", {})).appendTo(this.page.main)[0];
		this.sharedUI = frappe.sarathiUI.enhance(this.root);
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
			if (e.target.dataset.exceptionSearch !== undefined) {
				this.exceptionSearch = e.target.value.trim().toLowerCase();
				this.filterExceptionTable();
			}
		});
		this.root.addEventListener("keydown", (e) => {
			if (e.target.dataset.dateFilter && e.key === "Enter") {
				e.preventDefault();
				this.applyFilters();
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
				this.data = null;
				this.subData = null;
				this.accData = null;
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
			const events = [
				"sarathi_dashboard_changed",
				"sarathi_owner_live_change",
				"doc_update",
				"list_update",
			];
			if (frappe.realtime) {
				events.forEach((ev) => {
					frappe.realtime.off(ev, onRealtimeChange);
					frappe.realtime.on(ev, onRealtimeChange);
				});
			}
			if (frappe.realtime?.socket) {
				events.forEach((ev) => {
					frappe.realtime.socket.off(ev, onRealtimeChange);
					frappe.realtime.socket.on(ev, onRealtimeChange);
				});
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
		return frappe.sarathiUI.state("empty", { message: text }).outerHTML;
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
		return frappe.sarathiUI.status(text).outerHTML;
	}
	async call(method, args = {}) {
		const r = await frappe.call({
			method: `sarathi_visibility.api.dashboard.${method}`,
			args: { ...args, _: Date.now(), force_refresh: 1 },
			silent: true,
		});
		return r.message;
	}
	readUrl() {
		const q = new URLSearchParams(location.search);
		for (const k of ["company", "customer", "project", "from_date", "to_date", "status", "workstation"])
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
		if ("search" in change) {
			this.search = (change.search || "").toLowerCase();
			if (this.el("[data-search]")) this.el("[data-search]").value = change.search || "";
		}
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
	applyFilters() {
		const company = this.el('[data-filter="company"]')?.value || "";
		const status = this.el('[data-filter="status"]')?.value || "";
		const workstation = this.el('[data-filter="workstation"]')?.value || "";
		const from = this.el('[data-date-filter="from_date"]')?.value || "";
		const to = this.el('[data-date-filter="to_date"]')?.value || "";
		if (from && to && from > to) {
			frappe.msgprint(__("From date must be on or before To date."));
			return;
		}
		const searchVal = this.el("[data-search]")?.value || "";
		this.search = searchVal.toLowerCase();
		this.dateFilters = { from_date: from, to_date: to };
		this.data = null;
		this.navigate({
			company,
			status,
			workstation,
			from_date: from,
			to_date: to,
			search: searchVal,
		});
	}
	applyDateFilter() {
		this.applyFilters();
	}
	resetFilters() {
		this.dateFilters = { from_date: "", to_date: "" };
		const fromEl = this.el('[data-date-filter="from_date"]');
		const toEl = this.el('[data-date-filter="to_date"]');
		if (fromEl) {
			fromEl.value = "";
			fromEl.dispatchEvent(new Event("input", { bubbles: true }));
		}
		if (toEl) {
			toEl.value = "";
			toEl.dispatchEvent(new Event("input", { bubbles: true }));
		}
		const searchEl = this.el("[data-search]");
		if (searchEl) {
			searchEl.value = "";
			searchEl.dispatchEvent(new Event("input", { bubbles: true }));
		}
		const statusEl = this.el('[data-filter="status"]');
		if (statusEl) {
			statusEl.value = "";
			if (statusEl._syncCombo) statusEl._syncCombo();
		}
		const wsEl = this.el('[data-filter="workstation"]');
		if (wsEl) {
			wsEl.value = "";
			if (wsEl._syncCombo) wsEl._syncCombo();
		}
		const compEl = this.el('[data-filter="company"]');
		if (compEl) {
			compEl.value = "";
			if (compEl._syncCombo) compEl._syncCombo();
		}
		this.search = "";
		this.data = null;
		this.navigate({
			company: "",
			status: "",
			workstation: "",
			customer: "",
			project: "",
			from_date: "",
			to_date: "",
			search: "",
		});
	}
	clearDateFilter() {
		this.resetFilters();
	}
	async load(silent = false) {
		if (this.view === "accounting") {
			return this.loadAccountingData(silent);
		}
		if (this.view === "subcontracting") {
			return this.loadSubcontractingData(silent);
		}
		const request = ++this.sequence;
		this.isRefreshing = true;
		this.root.setAttribute("aria-busy", "true");
		const prevSuccessFormatted = this.lastSuccessfulRefresh
			? (window.frappe?.sarathiUI?.formatTimestamp
				? frappe.sarathiUI.formatTimestamp(this.lastSuccessfulRefresh)
				: frappe.datetime.str_to_user(this.lastSuccessfulRefresh))
			: null;
		if (!silent) {
			this.el("[data-updated]").textContent = prevSuccessFormatted
				? `Refreshing… (Last updated: ${prevSuccessFormatted})`
				: "Refreshing…";
		}
		try {
			this.data = null;
			const data = await this.call("get_summary", {
				filters: JSON.stringify(this.filters),
			});
			if (request !== this.sequence || !this.visible) return;
			this.data = data;
			this.filters = Object.assign({}, this.filters, data.filters);
			this.lastSuccessfulRefresh = data.generated_at || new Date().toISOString();
			this.lastFailedRefresh = null;
			this.writeUrl(true);
			this.el("[data-error]").hidden = true;
			this.el("[data-error]").innerHTML = "";
			this.render(silent);
			const formattedTime = window.frappe?.sarathiUI?.formatTimestamp
				? frappe.sarathiUI.formatTimestamp(this.lastSuccessfulRefresh)
				: frappe.datetime.str_to_user(this.lastSuccessfulRefresh);
			this.el("[data-updated]").textContent = `Last updated: ${formattedTime}`;
		} catch (e) {
			if (request !== this.sequence) return;
			this.lastFailedRefresh = new Date().toISOString();
			const timeStr = this.lastSuccessfulRefresh
				? (window.frappe?.sarathiUI?.formatTimestamp
					? frappe.sarathiUI.formatTimestamp(this.lastSuccessfulRefresh)
					: frappe.datetime.str_to_user(this.lastSuccessfulRefresh))
				: null;
			this.el("[data-error]").hidden = false;
			if (this.data && timeStr) {
				this.el("[data-error]").innerHTML = `
					<span>Refresh failed. Showing data from last update (${timeStr}).</span>
					<button type="button" class="sd-button sd-btn-retry" style="margin-left:8px;" data-action="refresh">Retry</button>
				`;
				this.el("[data-updated]").textContent = `Last updated: ${timeStr} (Stale)`;
			} else {
				this.data = null;
				this.el("[data-error]").innerHTML = `
					<span>Unable to load Control Tower data. Please check your connection and filter access, then click Retry.</span>
					<button type="button" class="sd-button sd-btn-retry" style="margin-left:8px;" data-action="refresh">Retry</button>
				`;
				this.el("[data-updated]").textContent = "Data unavailable";
			}
		} finally {
			this.isRefreshing = false;
			if (request === this.sequence) this.root.setAttribute("aria-busy", "false");
		}
	}
	render(silent) {
		const d = this.data;
		if (this.el("[data-subcontracting-cards]")) this.renderSubcontractingCard();
		if (this.el("[data-accounting-cards]")) this.renderAccountingCard();
		this.renderFactoryOverview();
		this.renderProductionPipeline();
		this.renderMaterialReadiness();
		this.renderWorkstationDowntime();
		this.renderQualityOverview();
		this.renderReworkOverview();
		this.renderSubcontractingOverview();
		this.renderProductionExceptions();
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
		const wsFilter = this.el('[data-filter="workstation"]');
		if (wsFilter && d.factory_overview?.workstations) {
			const currentWs = this.filters.workstation || "";
			wsFilter.innerHTML =
				`<option value="">All workstations</option>` +
				d.factory_overview.workstations
					.map(
						(w) =>
							`<option value="${this.esc(w.value)}"${w.value === currentWs ? " selected" : ""}>${this.esc(
								w.label
							)}</option>`
					)
					.join("");
		}
		for (const n of this.root.querySelectorAll("[data-filter]")) {
			n.value = this.filters[n.dataset.filter] || "";
			n._syncCombo?.();
		}
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
		if (this.el("[data-live-projects]")) this.el("[data-live-projects]").innerHTML = this.liveCards();
		if (this.el("[data-kpis]")) {
			this.el("[data-kpis]").replaceChildren(...d.kpis.map((k) => {
				const card = frappe.sarathiUI.kpi({
					label: k.label,
					value: typeof k.value === "number" ? this.num(k.value) : k.value,
					description: k.report ? "View records" : "ERPNext records",
					onActivate: k.report ? () => this.showCardDetailsModal(k.report, k.subset || "", k.label) : undefined,
				});
				card.dataset.kpiLabel = k.label;
				return card;
			}));
		}
		if (this.el("[data-customer-panel]")) this.el("[data-customer-panel]").hidden = !!this.filters.customer || !!this.filters.project;
		if (this.el("[data-project-panel]")) this.el("[data-project-panel]").hidden = !!this.filters.project;
		if (this.el("[data-project-heading]")) {
			this.el("[data-project-heading]").textContent = this.filters.customer
				? `${name} projects`
				: "Organization projects";
		}
		if (this.el('[data-action="associate"]')) {
			this.el('[data-action="associate"]').hidden =
				!d.can_create["Sarathi Customer Organization"] || !this.filters.company;
		}
		if (this.el("[data-project-summary]")) {
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
		}
		if (this.el("[data-cards]")) this.renderCards();
		if (this.el(".sd-tabs")) this.renderTabs();
		if (this.el("[data-content]")) {
			if (silent && this.tab !== "overview" && this.el("[data-table-area]")) {
				this.loadReport();
				if (this.el("[data-tab-charts]"))
					this.el("[data-tab-charts]").innerHTML = this.chartGrid(this.chartsForTab());
			} else this.renderContent();
		}
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
            return frappe.sarathiUI.progress({ value: val, label: c.label || "Progress" }).outerHTML;
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
				`<div class="sd-empty" role="alert"><p>Unable to load records for this card. Please check your permissions and try again.</p><button type="button" class="sd-button sd-primary sd-btn-retry" data-action="retry-card">Retry</button></div>`
			);
			dialog.fields_dict.card_content.$wrapper.find("[data-action='retry-card']").on("click", () => {
				this.showCardDetailsModal(reportKey, subset, label, projectContext);
			});
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
		const woLink = event.target.closest("[data-inspect-wo]");
		if (woLink) {
			event.preventDefault();
			frappe.set_route("Form", "Work Order", woLink.dataset.inspectWo);
			return;
		}
		const pill = event.target.closest(".sd-filter-pill");
		if (pill) {
			if (pill.dataset.action === "filter-wo-status") {
				const st = pill.dataset.status;
				this.navigate({ status: this.filters.status === st ? "" : st });
				return;
			}
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
		} else if (d.action === "toggle-ai") {
			this.toggleAiChat();
		} else if (d.action === "switch-owner") {
			frappe.set_route("sarathiownertower");
		} else if (d.action === "apply-dates" || d.action === "apply-filters") {
			this.applyFilters();
		} else if (d.action === "clear-dates" || d.action === "reset-filters") {
			this.resetFilters();
		} else if (d.action === "open-subcontracting") {
			this.openSubcontractingView();
		} else if (d.action === "close-subcontracting") {
			this.closeSubcontractingView();
		} else if (d.action === "refresh-subcontracting") {
			b.classList.add("sd-spinning", "sod-spinning");
			const p = this.loadSubcontractingData();
			Promise.resolve(p).finally(() => {
				setTimeout(() => b.classList.remove("sd-spinning", "sod-spinning"), 600);
			});
		} else if (d.action === "apply-sub-filters") {
			this.applySubFilters();
		} else if (d.action === "reset-sub-filters") {
			this.resetSubFilters();
		} else if (d.action === "open-accounting") {
			this.openAccountingView();
		} else if (d.action === "close-accounting") {
			this.closeAccountingView();
		} else if (d.action === "refresh-accounting") {
			b.classList.add("sd-spinning", "sod-spinning");
			const p = this.loadAccountingData();
			Promise.resolve(p).finally(() => {
				setTimeout(() => b.classList.remove("sd-spinning", "sod-spinning"), 600);
			});
		} else if (d.action === "apply-acc-filters") {
			this.applyAccFilters();
		} else if (d.action === "reset-acc-filters") {
			this.resetAccFilters();
		} else if (d.action === "reset-kpi-selection") {
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
		} else if (d.action === "filter-pipeline-stage") {
			this.pipelineSelectedStage = d.stage;
			this.renderProductionPipeline();
		} else if (d.action === "filter-material-readiness") {
			this.materialSelectedReadiness = d.status;
			this.renderMaterialReadiness();
		} else if (d.action === "filter-workstation-status") {
			this.workstationSelectedStatus = d.status;
			this.renderWorkstationDowntime();
		} else if (d.action === "filter-quality-status") {
			this.qualitySelectedStatus = d.status;
			this.renderQualityOverview();
		} else if (d.action === "filter-rework-status") {
			this.reworkSelectedStatus = d.status;
			this.renderReworkOverview();
		} else if (d.action === "filter-subcontracting-status") {
			this.subcontractingSelectedStatus = d.status;
			this.renderSubcontractingOverview();
		} else if (d.action === "filter-exception-category") {
			this.exceptionSelectedCategory = d.category;
			this.renderProductionExceptions();
		} else if (d.action === "filter-exception-severity") {
			this.exceptionSelectedSeverity = d.severity;
			this.renderProductionExceptions();
		} else if (d.action === "clear-exception-filters") {
			this.exceptionSelectedCategory = "All";
			this.exceptionSelectedSeverity = "All";
			this.exceptionSearch = "";
			this.renderProductionExceptions();
		} else if (d.inspectQi) {
			frappe.set_route("Form", "Quality Inspection", d.inspectQi);
		} else if (d.inspectSco) {
			frappe.set_route("Form", "Subcontracting Order", d.inspectSco);
		} else if (d.inspectSupplier) {
			frappe.set_route("Form", "Supplier", d.inspectSupplier);
		} else if (d.inspectPo) {
			frappe.set_route("Form", "Purchase Order", d.inspectPo);
		} else if (d.inspectWo) {
			frappe.set_route("Form", "Work Order", d.inspectWo);
		} else if (d.inspectJc) {
			frappe.set_route("Form", "Job Card", d.inspectJc);
		} else if (d.inspectItem) {
			frappe.set_route("Form", "Item", d.inspectItem);
		} else if (d.inspectWarehouse) {
			frappe.set_route("Form", "Warehouse", d.inspectWarehouse);
		} else if (d.inspectWorkstation) {
			frappe.set_route("Form", "Workstation", d.inspectWorkstation);
		} else if (d.inspectDowntime) {
			frappe.set_route("Form", "Downtime Entry", d.inspectDowntime);
		} else if (d.customer) {
			this.navigate({ customer: d.customer, project: "" });
		} else if (d.project) {
			this.navigate({ project: d.project });
		} else if (d.nav) {
			this.navigate(d.nav === "organization" ? { customer: "", project: "" } : { project: "" });
		} else if (d.tab) {
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
		} else if (d.action === "refresh") {
			b.classList.add("sd-spinning", "sod-spinning");
			this.data = null;
			this.subData = null;
			this.accData = null;
			const p = this.load();
			Promise.resolve(p).finally(() => {
				setTimeout(() => b.classList.remove("sd-spinning", "sod-spinning"), 600);
			});
		} else if (d.action === "create" || d.action === "setup") {
			this.creationMenu(d.action === "setup");
		} else if (d.action === "associate") {
			this.create("Sarathi Customer Organization");
		} else if (d.action === "native-report") {
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

	renderFactoryOverview() {
		const panel = this.el("[data-factory-overview-panel]");
		if (!panel) return;
		const fo = this.data?.factory_overview;
		if (!fo || fo.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Factory Overview</h2>
						<p>Production progress, shop-floor execution, deadlines, and material readiness</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(fo?.reason || "Factory Overview is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-factory-badge]");
		if (badge) {
			badge.textContent = `As of ${fo.reference_date}`;
		}

		// 1. Render 7 KPI cards
		const kpisContainer = this.el("[data-factory-kpis]");
		if (kpisContainer && fo.kpis) {
			const k = fo.kpis;
			const cards = [
				frappe.sarathiUI.kpi({
					label: k.active_work_orders.label,
					value: this.num(k.active_work_orders.value),
					description: k.active_work_orders.description,
					onActivate: () => frappe.set_route("List", "Work Order", { status: ["in", ["Not Started", "In Process"]] }),
				}),
				frappe.sarathiUI.kpi({
					label: k.planned_production.label,
					value: k.planned_production.value,
					description: k.planned_production.description,
					onActivate: () => frappe.set_route("List", "Work Order"),
				}),
				frappe.sarathiUI.kpi({
					label: k.actual_production.label,
					value: k.actual_production.value,
					description: k.actual_production.description,
					onActivate: () => frappe.set_route("List", "Work Order"),
				}),
				frappe.sarathiUI.kpi({
					label: k.production_achievement.label,
					value: k.production_achievement.value,
					description: k.production_achievement.description,
					status: (k.production_achievement.pct >= 90 ? "success" : k.production_achievement.pct >= 50 ? "info" : "warning"),
				}),
				frappe.sarathiUI.kpi({
					label: k.overdue_work_orders.label,
					value: this.num(k.overdue_work_orders.value),
					description: k.overdue_work_orders.description,
					status: (k.overdue_work_orders.value > 0 ? "danger" : "success"),
					onActivate: () => this.navigate({ status: "Overdue" }),
				}),
				frappe.sarathiUI.kpi({
					label: k.open_job_cards.label,
					value: this.num(k.open_job_cards.value),
					description: k.open_job_cards.description,
					onActivate: () => frappe.set_route("List", "Job Card", { status: ["in", ["Open", "Work In Progress"]] }),
				}),
				frappe.sarathiUI.kpi({
					label: k.material_blockers.label,
					value: this.num(k.material_blockers.value),
					description: k.material_blockers.description,
					status: (k.material_blockers.value > 0 ? "danger" : "success"),
				}),
			];
			cards.forEach((card, idx) => {
				card.dataset.factoryKpi = ["active_wo", "planned", "actual", "achievement", "overdue", "job_cards", "material_blockers"][idx];
			});
			kpisContainer.replaceChildren(...cards);
		}

		// 2. Render Production Summary section
		const summaryContainer = this.el("[data-factory-summary]");
		if (summaryContainer && fo.summary) {
			const s = fo.summary;

			// Status Distribution Badges
			const statusCounts = s.status_distribution || {};
			const statusOrder = ["Not Started", "In Process", "Completed", "Stopped", "Draft", "Cancelled"];
			const statusHtml = Object.keys(statusCounts).length > 0
				? `<div class="sd-factory-status-bar" role="group" aria-label="Work Order Statuses">
					<span class="sd-status-bar-label">Work Order Statuses:</span>
					${statusOrder.filter((st) => statusCounts[st] !== undefined).map((st) => `
						<button type="button" class="sd-pill sd-status-${this.statusColor(st)} sd-filter-pill${this.filters.status === st ? " active" : ""}" data-action="filter-wo-status" data-status="${this.esc(st)}">
							${this.esc(st)}: <b>${statusCounts[st]}</b>
						</button>
					`).join("")}
				</div>`
				: "";

			// Item Production Summary Table
			const itemRows = s.item_production_summary || [];
			const itemTableHtml = itemRows.length > 0
				? `<div class="sd-table-container">
					<table class="sd-table sd-factory-table" aria-label="Planned vs Actual Output by Item">
						<thead>
							<tr>
								<th>Item</th>
								<th>Stock Unit</th>
								<th>Active Orders</th>
								<th>Planned Qty</th>
								<th>Produced Qty</th>
								<th>Achievement</th>
								<th>Work Orders</th>
							</tr>
						</thead>
						<tbody>
							${itemRows.map((row) => `
								<tr>
									<td>
										<div class="sd-item-cell">
											<strong>${this.link("Item", row.item_code, row.item_name)}</strong>
											<span class="sd-item-sub">${this.esc(row.item_code)}</span>
										</div>
									</td>
									<td><span class="sd-badge-subtle">${this.esc(row.stock_uom)}</span></td>
									<td><strong>${row.active_orders}</strong></td>
									<td>${this.num(row.planned_qty)} ${this.esc(row.stock_uom)}</td>
									<td>${this.num(row.produced_qty)} ${this.esc(row.stock_uom)}</td>
									<td>
										<div class="sd-progress-cell">
											<div class="sd-progress-bar">
												<div class="sd-progress-fill ${row.achievement_pct >= 90 ? "sd-bg-green" : row.achievement_pct >= 50 ? "sd-bg-blue" : "sd-bg-amber"}" style="width: ${Math.min(100, row.achievement_pct)}%"></div>
											</div>
											<span class="sd-progress-val">${row.achievement_pct}%</span>
										</div>
									</td>
									<td>
										<div class="sd-wo-tags">
											${(row.work_orders || []).map((wo) => `<a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(wo)}" title="Open ${this.esc(wo)} in Form">${this.esc(wo)}</a>`).join(" ")}
										</div>
									</td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>`
				: `<div class="sd-empty-box">${this.empty("No active manufacturing orders for this selection.")}</div>`;

			// Overdue & Approaching Jobs Tables
			const overdueJobs = s.overdue_jobs || [];
			const overdueHtml = overdueJobs.length > 0
				? `<div class="sd-job-alert-table-wrap">
					<table class="sd-table sd-table-compact" aria-label="Overdue Work Orders">
						<thead>
							<tr>
								<th>Work Order</th>
								<th>Item</th>
								<th>Target Date</th>
								<th>Overdue</th>
								<th>Progress</th>
							</tr>
						</thead>
						<tbody>
							${overdueJobs.map((j) => `
								<tr>
									<td><a href="javascript:void(0)" class="sd-wo-link sd-urgent" data-inspect-wo="${this.esc(j.work_order)}">${this.esc(j.work_order)}</a></td>
									<td>${this.esc(j.item_name || j.production_item)}</td>
									<td>${this.esc(j.target_date || "—")}</td>
									<td><span class="sd-pill sd-status-red">${j.days_overdue}d overdue</span></td>
									<td>${this.num(j.produced_qty)} / ${this.num(j.planned_qty)} ${this.esc(j.stock_uom)}</td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>`
				: `<div class="sd-success-state">
					<span class="sd-pill sd-status-green">✓ 0 Overdue Orders</span>
					<p>All active Work Orders are on schedule or within expected delivery windows.</p>
				</div>`;

			const approachingJobs = s.approaching_jobs || [];
			const approachingHtml = approachingJobs.length > 0
				? `<div class="sd-job-alert-table-wrap">
					<table class="sd-table sd-table-compact" aria-label="Approaching Work Orders">
						<thead>
							<tr>
								<th>Work Order</th>
								<th>Item</th>
								<th>Target Date</th>
								<th>Due</th>
								<th>Progress</th>
							</tr>
						</thead>
						<tbody>
							${approachingJobs.map((j) => `
								<tr>
									<td><a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(j.work_order)}">${this.esc(j.work_order)}</a></td>
									<td>${this.esc(j.item_name || j.production_item)}</td>
									<td>${this.esc(j.target_date || "—")}</td>
									<td><span class="sd-pill sd-status-amber">${j.days_remaining === 0 ? "Due today" : `${j.days_remaining}d remaining`}</span></td>
									<td>${this.num(j.produced_qty)} / ${this.num(j.planned_qty)} ${this.esc(j.stock_uom)}</td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>`
				: `<div class="sd-success-state">
					<span class="sd-pill sd-status-blue">0 Orders Due in 7 Days</span>
					<p>No active Work Orders due within the review window.</p>
				</div>`;

			summaryContainer.innerHTML = `
				<div class="sd-factory-summary-header">
					${statusHtml}
				</div>
				<div class="sd-factory-progress-card">
					<div class="sd-section-title">
						<h3>Planned versus Actual Output by Item</h3>
						<span class="sd-subtle-hint">Production volume in item-specific stock units</span>
					</div>
					${itemTableHtml}
				</div>
				<div class="sd-factory-alerts-grid">
					<div class="sd-factory-alert-box sd-overdue-box">
						<div class="sd-alert-heading">
							<h3>Overdue Work Orders</h3>
							<span class="sd-pill ${overdueJobs.length > 0 ? "sd-status-red" : "sd-status-green"}">${overdueJobs.length}</span>
						</div>
						${overdueHtml}
					</div>
					<div class="sd-factory-alert-box sd-approaching-box">
						<div class="sd-alert-heading">
							<h3>Approaching Due Date (Next 7 Days)</h3>
							<span class="sd-pill sd-status-amber">${approachingJobs.length}</span>
						</div>
						${approachingHtml}
					</div>
				</div>
			`;
		}
	}

	renderProductionPipeline() {
		const panel = this.el("[data-production-pipeline-panel]");
		if (!panel) return;
		const pp = this.data?.production_pipeline;
		if (!pp || pp.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Production Pipeline & Bottlenecks</h2>
						<p>Operational workflow, operation sequences, dependencies, and queue constraints</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(pp?.reason || "Production pipeline is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-pipeline-badge]");
		if (badge) {
			badge.textContent = `As of ${pp.reference_date}`;
		}

		// 1. Render Interactive Stage Cards
		const stagesContainer = this.el("[data-pipeline-stages]");
		if (stagesContainer && pp.stages) {
			const activeStage = this.pipelineSelectedStage || "All";
			const stageIcons = {
				"Material Staging": "📦",
				"In Production": "⚙️",
				"Manufacture Receipt": "📥",
				"Completed": "✅",
			};
			const stagesHtml = `
				<div class="sd-pipeline-stages-grid" role="group" aria-label="Production Pipeline Stages">
					<button type="button" class="sd-pipeline-stage-card ${activeStage === "All" ? "active" : ""}" data-action="filter-pipeline-stage" data-stage="All">
						<div class="sd-stage-header">
							<span class="sd-stage-icon">🏭</span>
							<span class="sd-pill sd-status-blue">${pp.summary.total_work_orders}</span>
						</div>
						<h4>All Pipeline Work Orders</h4>
						<p>Entire factory manufacturing stream</p>
					</button>
					${pp.stages.map((st) => `
						<button type="button" class="sd-pipeline-stage-card ${activeStage === st.key ? "active" : ""}" data-action="filter-pipeline-stage" data-stage="${this.esc(st.key)}">
							<div class="sd-stage-header">
								<span class="sd-stage-icon">${stageIcons[st.key] || "⚙️"}</span>
								<span class="sd-pill ${st.count > 0 ? "sd-status-blue" : "sd-status-subtle"}">${st.count}</span>
							</div>
							<h4>${this.esc(st.label)}</h4>
							<p>${this.esc(st.description)}</p>
						</button>
					`).join("")}
				</div>
			`;
			stagesContainer.innerHTML = stagesHtml;
		}

		// 2. Render Bottlenecks & Delayed Operations Grid
		const bottlenecksContainer = this.el("[data-pipeline-bottlenecks]");
		if (bottlenecksContainer) {
			const bList = pp.bottlenecks || [];
			const dOps = pp.delayed_operations || [];

			const bottlenecksHtml = bList.length > 0
				? `<div class="sd-bottlenecks-list">
					${bList.map((b) => `
						<div class="sd-bottleneck-card sd-severity-${this.esc(b.severity)}">
							<div class="sd-bottleneck-header">
								<div class="sd-bottleneck-title-row">
									<span class="sd-bottleneck-type-badge sd-type-${this.esc(b.type)}">${this.esc(b.type.toUpperCase())}</span>
									<strong>${this.esc(b.title)}</strong>
								</div>
								<span class="sd-pill ${b.severity === "high" ? "sd-status-red" : "sd-status-amber"}">${b.affected_work_orders_count} Orders Affected</span>
							</div>
							<p class="sd-bottleneck-reason">${this.esc(b.reason)}</p>
							<div class="sd-bottleneck-meta">
								${b.workstation ? `<span><b>Workstation:</b> ${this.esc(b.workstation)}</span>` : ""}
								${b.queue_depth ? `<span><b>Queue Depth:</b> ${b.queue_depth} jobs</span>` : ""}
								${b.oldest_overdue_days > 0 ? `<span class="sd-urgent-text"><b>Oldest Overdue:</b> ${b.oldest_overdue_days}d</span>` : ""}
							</div>
							<div class="sd-bottleneck-drilldowns">
								<span class="sd-subtle-hint">Inspect:</span>
								${(b.affected_work_orders || []).slice(0, 4).map((wo) => `
									<a href="javascript:void(0)" class="sd-drilldown-tag" data-inspect-wo="${this.esc(wo)}" title="Open Work Order ${this.esc(wo)}">${this.esc(wo)}</a>
								`).join(" ")}
								${(b.affected_work_orders || []).length > 4 ? `<span class="sd-more-tag">+${b.affected_work_orders.length - 4} more</span>` : ""}
							</div>
						</div>
					`).join("")}
				</div>`
				: `<div class="sd-success-state">
					<span class="sd-pill sd-status-green">✓ No Operational Bottlenecks Detected</span>
					<p>Workstation queues and operation dependencies are running within normal thresholds.</p>
				</div>`;

			const delayedHtml = dOps.length > 0
				? `<div class="sd-delayed-ops-table-wrap">
					<table class="sd-table sd-table-compact" aria-label="Delayed Operations">
						<thead>
							<tr>
								<th>Operation</th>
								<th>Work Order</th>
								<th>Workstation</th>
								<th>Days Overdue</th>
								<th>Action</th>
							</tr>
						</thead>
						<tbody>
							${dOps.map((op) => `
								<tr>
									<td><strong>${this.esc(op.operation)}</strong></td>
									<td><a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(op.work_order)}">${this.esc(op.work_order)}</a></td>
									<td><span class="sd-badge-subtle">${this.esc(op.workstation || "—")}</span></td>
									<td><span class="sd-pill sd-status-red">${op.days_overdue}d</span></td>
									<td><a href="javascript:void(0)" class="sd-btn-xs" data-inspect-jc="${this.esc(op.job_card)}" title="Open Job Card">Open Card ↗</a></td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>`
				: `<div class="sd-success-state">
					<span class="sd-pill sd-status-green">✓ 0 Overdue Operations</span>
					<p>All active Job Cards are progressing on or ahead of schedule.</p>
				</div>`;

			bottlenecksContainer.innerHTML = `
				<div class="sd-pipeline-insights-grid">
					<div class="sd-insights-col">
						<div class="sd-section-title">
							<h3>Identified Operational Bottlenecks</h3>
							<span class="sd-pill ${bList.length > 0 ? "sd-status-red" : "sd-status-green"}">${bList.length}</span>
						</div>
						${bottlenecksHtml}
					</div>
					<div class="sd-insights-col">
						<div class="sd-section-title">
							<h3>Delayed Operations & Job Cards</h3>
							<span class="sd-pill ${dOps.length > 0 ? "sd-status-amber" : "sd-status-green"}">${dOps.length}</span>
						</div>
						${delayedHtml}
					</div>
				</div>
			`;
		}

		// 3. Render Pipeline Work Orders & Operation Sequence Tracking
		const jobsContainer = this.el("[data-pipeline-jobs]");
		if (jobsContainer && pp.pipeline_jobs) {
			const activeStage = this.pipelineSelectedStage || "All";
			const filteredJobs = activeStage === "All"
				? pp.pipeline_jobs
				: pp.pipeline_jobs.filter((j) => j.stage === activeStage);

			const jobsHtml = filteredJobs.length > 0
				? `<div class="sd-pipeline-jobs-table-wrap">
					<div class="sd-section-title">
						<h3>Work Order Flow & Operation Sequences</h3>
						<span class="sd-subtle-hint">Showing ${filteredJobs.length} of ${pp.pipeline_jobs.length} Work Orders</span>
					</div>
					<div class="sd-table-container">
						<table class="sd-table sd-pipeline-jobs-table" aria-label="Work Order Pipeline and Sequence">
							<thead>
								<tr>
									<th>Work Order & Item</th>
									<th>Stage</th>
									<th>Progress</th>
									<th>Current Operation</th>
									<th>Operation Sequence & Dependencies</th>
									<th>Target Date</th>
								</tr>
							</thead>
							<tbody>
								${filteredJobs.map((job) => `
									<tr class="${job.is_overdue ? "sd-row-overdue" : ""}">
										<td>
											<div class="sd-wo-ident-cell">
												<div class="sd-wo-title-line">
													<a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(job.work_order)}"><strong>${this.esc(job.work_order)}</strong></a>
													${job.is_overdue ? `<span class="sd-pill sd-status-red">Overdue</span>` : ""}
													${job.is_material_blocked ? `<span class="sd-pill sd-status-amber" title="Material transfer pending">Material Pending</span>` : ""}
													${job.is_predecessor_blocked ? `<span class="sd-pill sd-status-orange" title="Waiting on predecessor operation">Waiting on Predecessor</span>` : ""}
												</div>
												<div class="sd-wo-item-name">${this.esc(job.item_name)} <span class="sd-item-sub">(${this.esc(job.production_item)})</span></div>
												${job.customer ? `<div class="sd-wo-cust-sub">👤 ${this.esc(job.customer)}</div>` : ""}
											</div>
										</td>
										<td>
											<span class="sd-pill sd-stage-${this.stageClass(job.stage)}">${this.esc(job.stage)}</span>
										</td>
										<td>
											<div class="sd-progress-cell">
												<div class="sd-progress-bar">
													<div class="sd-progress-fill ${job.completion_percent >= 90 ? "sd-bg-green" : job.completion_percent >= 50 ? "sd-bg-blue" : "sd-bg-amber"}" style="width: ${Math.min(100, job.completion_percent)}%"></div>
												</div>
												<span class="sd-progress-val">${job.produced_qty} / ${job.qty} (${job.completion_percent}%)</span>
											</div>
										</td>
										<td>
											${job.current_operation ? `
												<div class="sd-current-op-cell">
													<strong>${this.esc(job.current_operation)}</strong>
													<span class="sd-badge-subtle">${this.esc(job.current_workstation || "Unassigned WS")}</span>
													<span class="sd-op-status-mini sd-status-${this.opStatusClass(job.current_op_status)}">${this.esc(job.current_op_status)}</span>
												</div>
											` : `<span class="sd-subtle-hint">None</span>`}
										</td>
										<td>
											<div class="sd-sequence-chain">
												${job.operations && job.operations.length > 0 ? job.operations.map((op, oIdx) => `
													<span class="sd-sequence-node sd-node-${this.opStatusClass(op.status)}" title="${this.esc(op.operation)} [${this.esc(op.status)}] ${op.waiting_on ? `(Waiting on: ${this.esc(op.waiting_on)})` : ""}">
														<span class="sd-node-seq">${op.sequence}</span>
														<span class="sd-node-name">${this.esc(op.operation)}</span>
														<span class="sd-node-icon">${this.opStatusIcon(op.status)}</span>
													</span>
													${oIdx < job.operations.length - 1 ? `<span class="sd-chain-arrow">→</span>` : ""}
												`).join("") : `<span class="sd-subtle-hint">No routing operations configured</span>`}
											</div>
										</td>
										<td>
											<div class="sd-target-cell">
												<span>${this.esc(job.target_completion_date || "—")}</span>
												${job.days_diff !== null && job.days_diff < 0 ? `
													<span class="sd-pill sd-status-red">${Math.abs(job.days_diff)}d overdue</span>
												` : job.days_diff !== null && job.days_diff <= 7 ? `
													<span class="sd-pill sd-status-amber">${job.days_diff}d left</span>
												` : ""}
											</div>
										</td>
									</tr>
								`).join("")}
							</tbody>
						</table>
					</div>
				</div>`
				: `<div class="sd-empty-box">${this.empty("No Work Orders found for the selected stage and filters.")}</div>`;

			jobsContainer.innerHTML = jobsHtml;
		}
	}

	renderMaterialReadiness() {
		const panel = this.el("[data-material-readiness-panel]");
		if (!panel) return;
		const mr = this.data?.material_readiness;
		if (!mr || mr.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Material Readiness & Warehouse Shortages</h2>
						<p>Component demand vs leaf warehouse available stock, deficit calculations, and Work Order readiness</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(mr?.reason || "Material readiness is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-material-readiness-badge]");
		if (badge) {
			badge.textContent = `As of ${mr.reference_date}`;
		}

		// 1. Render 4 KPI Cards
		const kpisContainer = this.el("[data-material-kpis]");
		if (kpisContainer && mr.summary) {
			const s = mr.summary;
			const cards = [
				frappe.sarathiUI.kpi({
					label: "Ready Work Orders",
					value: this.num(s.ready_work_orders),
					description: "100% component availability in leaf warehouses",
					tone: s.ready_work_orders > 0 ? "positive" : "neutral",
				}),
				frappe.sarathiUI.kpi({
					label: "Partially Ready Orders",
					value: this.num(s.partially_ready_work_orders),
					description: "Some materials staged, remaining components pending",
					tone: s.partially_ready_work_orders > 0 ? "caution" : "neutral",
				}),
				frappe.sarathiUI.kpi({
					label: "Material Shortages",
					value: this.num(s.shortage_work_orders),
					description: `${s.distinct_shortage_items} items facing inventory deficits (${s.total_shortage_units} units)`,
					tone: s.shortage_work_orders > 0 ? "negative" : "positive",
				}),
				frappe.sarathiUI.kpi({
					label: "Critical Shortages",
					value: this.num(s.critical_shortage_orders),
					description: "Shortages on overdue or imminent orders (due in 7d)",
					tone: s.critical_shortage_orders > 0 ? "negative" : "positive",
				}),
			];
			kpisContainer.innerHTML = cards.join("");
		}

		// 2. Render Material Readiness Distribution Filter Bar
		const summaryContainer = this.el("[data-material-summary]");
		if (summaryContainer && mr.readiness_distribution) {
			const dist = mr.readiness_distribution;
			const activeStatus = this.materialSelectedReadiness || "All";
			const distHtml = `
				<div class="sd-material-distribution-wrap">
					<div class="sd-section-title">
						<h3>Work Order Readiness Distribution</h3>
						<span class="sd-subtle-hint">Filter components and orders by readiness status</span>
					</div>
					<div class="sd-material-status-grid" role="group" aria-label="Work Order Material Readiness Filters">
						<button type="button" class="sd-status-pill-btn ${activeStatus === "All" ? "active" : ""}" data-action="filter-material-readiness" data-status="All">
							<span class="sd-status-label">All Active Orders</span>
							<span class="sd-pill sd-status-blue">${mr.summary.total_work_orders}</span>
						</button>
						<button type="button" class="sd-status-pill-btn ${activeStatus === "Ready" ? "active" : ""}" data-action="filter-material-readiness" data-status="Ready">
							<span class="sd-status-label">✓ Ready</span>
							<span class="sd-pill sd-status-green">${dist.Ready || 0}</span>
						</button>
						<button type="button" class="sd-status-pill-btn ${activeStatus === "Partially Ready" ? "active" : ""}" data-action="filter-material-readiness" data-status="Partially Ready">
							<span class="sd-status-label">◐ Partially Ready</span>
							<span class="sd-pill sd-status-blue">${dist["Partially Ready"] || 0}</span>
						</button>
						<button type="button" class="sd-status-pill-btn ${activeStatus === "Shortage" ? "active" : ""}" data-action="filter-material-readiness" data-status="Shortage">
							<span class="sd-status-label">⚠ Shortage</span>
							<span class="sd-pill sd-status-red">${dist.Shortage || 0}</span>
						</button>
						${dist.Unknown > 0 ? `
							<button type="button" class="sd-status-pill-btn ${activeStatus === "Unknown" ? "active" : ""}" data-action="filter-material-readiness" data-status="Unknown">
								<span class="sd-status-label">? Unconfigured Warehouse</span>
								<span class="sd-pill sd-status-amber">${dist.Unknown}</span>
							</button>
						` : ""}
					</div>
				</div>
			`;
			summaryContainer.innerHTML = distHtml;
		}

		// 3. Render Aggregate Component Shortages by Item & Warehouse
		const shortageItemsContainer = this.el("[data-material-shortage-items]");
		if (shortageItemsContainer) {
			const aggItems = mr.shortage_items_aggregate || [];
			const aggHtml = aggItems.length > 0
				? `<div class="sd-material-agg-table-wrap">
					<div class="sd-section-title">
						<h3>Component Deficits by Leaf Warehouse</h3>
						<span class="sd-subtle-hint">Consolidated raw material demand vs physical available stock</span>
					</div>
					<div class="sd-table-container">
						<table class="sd-table sd-table-compact" aria-label="Component Deficits by Warehouse">
							<thead>
								<tr>
									<th>Raw Material Item</th>
									<th>Leaf Warehouse</th>
									<th>Total Demand</th>
									<th>Available Stock</th>
									<th>Physical / Reserved</th>
									<th>Shortage Deficit</th>
									<th>Affected Work Orders</th>
								</tr>
							</thead>
							<tbody>
								${aggItems.map((item) => `
									<tr class="${item.net_shortage > 0 ? "sd-row-shortage" : ""}">
										<td>
											<div class="sd-item-ident-cell">
												<a href="javascript:void(0)" class="sd-item-link" data-inspect-item="${this.esc(item.item_code)}"><strong>${this.esc(item.item_code)}</strong></a>
												<span class="sd-subtle-hint">${this.esc(item.item_name)}</span>
											</div>
										</td>
										<td>
											<a href="javascript:void(0)" class="sd-warehouse-link" data-inspect-warehouse="${this.esc(item.warehouse)}" title="Open Warehouse">${this.esc(item.warehouse)}</a>
										</td>
										<td><strong>${this.num(item.total_remaining_demand)}</strong> <span class="sd-uom-tag">${this.esc(item.stock_uom)}</span></td>
										<td><span class="${item.available_stock > 0 ? "sd-stock-ok" : "sd-stock-zero"}">${this.num(item.available_stock)}</span> ${this.esc(item.stock_uom)}</td>
										<td><span class="sd-subtle-hint">${this.num(item.actual_stock)} act / ${this.num(item.reserved_stock)} res</span></td>
										<td>
											${item.net_shortage > 0 ? `
												<span class="sd-pill sd-status-red sd-deficit-badge">-${this.num(item.net_shortage)} ${this.esc(item.stock_uom)}</span>
											` : `<span class="sd-pill sd-status-green">Stock Covered</span>`}
										</td>
										<td>
											<div class="sd-wo-tags">
												${(item.affected_work_orders || []).slice(0, 4).map((wo) => `
													<a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(wo)}" title="Open ${this.esc(wo)}">${this.esc(wo)}</a>
												`).join(" ")}
												${(item.affected_work_orders || []).length > 4 ? `<span class="sd-more-tag">+${item.affected_work_orders.length - 4} more</span>` : ""}
											</div>
										</td>
									</tr>
								`).join("")}
							</tbody>
						</table>
					</div>
				</div>`
				: `<div class="sd-success-state">
					<span class="sd-pill sd-status-green">✓ 0 Component Deficits</span>
					<p>All active Work Orders have sufficient warehouse stock to fulfill current production demand.</p>
				</div>`;
			shortageItemsContainer.innerHTML = aggHtml;
		}

		// 4. Render Work Order Material Readiness & Component Breakdown Table
		const linesContainer = this.el("[data-material-shortage-lines]");
		if (linesContainer && mr.work_orders_readiness) {
			const activeStatus = this.materialSelectedReadiness || "All";
			const filteredWos = activeStatus === "All"
				? mr.work_orders_readiness
				: mr.work_orders_readiness.filter((w) => w.readiness_status === activeStatus);

			const linesHtml = filteredWos.length > 0
				? `<div class="sd-wo-readiness-table-wrap">
					<div class="sd-section-title">
						<h3>Work Order Component Readiness</h3>
						<span class="sd-subtle-hint">Showing ${filteredWos.length} of ${mr.work_orders_readiness.length} Work Orders</span>
					</div>
					<div class="sd-table-container">
						<table class="sd-table sd-material-lines-table" aria-label="Work Order Material Readiness">
							<thead>
								<tr>
									<th>Work Order & Production Item</th>
									<th>Target Completion</th>
									<th>Readiness Status</th>
									<th>Components Status</th>
									<th>Action</th>
								</tr>
							</thead>
							<tbody>
								${filteredWos.map((wo) => `
									<tr class="${wo.readiness_status === "Shortage" ? "sd-row-shortage" : ""}">
										<td>
											<div class="sd-wo-ident-cell">
												<a href="javascript:void(0)" class="sd-wo-link" data-inspect-wo="${this.esc(wo.work_order)}"><strong>${this.esc(wo.work_order)}</strong></a>
												<span class="sd-subtle-hint">${this.esc(wo.production_item_name)} (${this.num(wo.qty)} ${this.esc(wo.stock_uom)})</span>
											</div>
										</td>
										<td>
											<div class="sd-target-cell">
												<span>${this.esc(wo.target_date || "—")}</span>
												${wo.is_overdue ? `
													<span class="sd-pill sd-status-red">${Math.abs(wo.days_to_target)}d overdue</span>
												` : wo.is_due_soon ? `
													<span class="sd-pill sd-status-amber">${wo.days_to_target}d left</span>
												` : ""}
											</div>
										</td>
										<td>
											<span class="sd-pill sd-status-${this.readinessClass(wo.readiness_status)}">
												${this.readinessIcon(wo.readiness_status)} ${this.esc(wo.readiness_status)}
											</span>
										</td>
										<td>
											<span class="sd-readiness-note">${this.esc(wo.readiness_note)}</span>
											${wo.shortage_components_count > 0 ? `
												<span class="sd-pill sd-status-red sd-mini-badge">${wo.shortage_components_count} short</span>
											` : ""}
										</td>
										<td>
											<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-wo="${this.esc(wo.work_order)}" title="Inspect Work Order">Inspect ↗</a>
										</td>
									</tr>
								`).join("")}
							</tbody>
						</table>
					</div>
				</div>`
				: `<div class="sd-empty-box">${this.empty("No Work Orders found for the selected readiness filter.")}</div>`;

			linesContainer.innerHTML = linesHtml;
		}
	}

	renderWorkstationDowntime() {
		const panel = this.el("[data-workstation-downtime-panel]");
		if (!panel) return;
		const wsd = this.data?.workstation_downtime;
		if (!wsd || wsd.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Workstations & Recorded Downtime</h2>
						<p>Operational workstation activity, Job Card assignments, recorded downtime events, and schedule impacts</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(wsd?.reason || "Workstation and downtime view is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-workstation-downtime-badge]");
		if (badge) {
			badge.textContent = `As of ${wsd.reference_date}`;
		}

		// 1. Render 4 KPI Cards
		const kpisContainer = this.el("[data-workstation-kpis]");
		if (kpisContainer && wsd.summary) {
			const s = wsd.summary;
			const cards = [
				frappe.sarathiUI.kpi({
					label: "Total Workstations",
					value: this.num(s.total_workstations),
					description: `${s.workstations_with_active_jobs} active on shop floor with running jobs`,
					tone: s.total_workstations > 0 ? "neutral" : "caution",
				}),
				frappe.sarathiUI.kpi({
					label: "Running Operations",
					value: this.num(s.recorded_running_jobs),
					description: `${s.total_assigned_operations} total assigned operations across factory`,
					tone: s.recorded_running_jobs > 0 ? "positive" : "neutral",
				}),
				frappe.sarathiUI.kpi({
					label: "Recorded Downtime",
					value: `${s.total_downtime_minutes} m`,
					description: `${s.recorded_downtime_events} recorded stops in period (${s.total_downtime_minutes} mins)`,
					tone: s.total_downtime_minutes > 0 ? "negative" : "positive",
				}),
				frappe.sarathiUI.kpi({
					label: "Delayed Operations",
					value: this.num(s.delayed_operations_count),
					description: "Operations past expected completion date",
					tone: s.delayed_operations_count > 0 ? "negative" : "positive",
				}),
			];
			kpisContainer.innerHTML = cards.join("");
		}

		// 2. Render Workstation Overview Table
		const overviewContainer = this.el("[data-workstation-overview]");
		if (overviewContainer && wsd.workstations_overview) {
			const wsList = wsd.workstations_overview;
			const activeStatus = this.workstationSelectedStatus || "All";
			const filteredWs = activeStatus === "All"
				? wsList
				: activeStatus === "Active"
				? wsList.filter((w) => w.active_job_cards_count > 0)
				: activeStatus === "Impacted"
				? wsList.filter((w) => w.has_production_impact)
				: wsList.filter((w) => w.recorded_status === activeStatus);

			const overviewHtml = `
				<div class="sd-ws-overview-wrap">
					<div class="sd-section-header-flex">
						<div>
							<h3>Workstation Operations Overview</h3>
							<span class="sd-subtle-hint">Recorded ERPNext status, job queue depths, and downtime interruptions</span>
						</div>
						<div class="sd-ws-filter-pills" role="group" aria-label="Workstation Status Filters">
							<button type="button" class="sd-status-pill-btn ${activeStatus === "All" ? "active" : ""}" data-action="filter-workstation-status" data-status="All">
								<span class="sd-status-label">All Stations</span>
								<span class="sd-pill sd-status-blue">${wsList.length}</span>
							</button>
							<button type="button" class="sd-status-pill-btn ${activeStatus === "Active" ? "active" : ""}" data-action="filter-workstation-status" data-status="Active">
								<span class="sd-status-label">⚙️ Running Jobs</span>
								<span class="sd-pill sd-status-green">${wsList.filter((w) => w.active_job_cards_count > 0).length}</span>
							</button>
							<button type="button" class="sd-status-pill-btn ${activeStatus === "Impacted" ? "active" : ""}" data-action="filter-workstation-status" data-status="Impacted">
								<span class="sd-status-label">⚠ Impacted / Delayed</span>
								<span class="sd-pill sd-status-red">${wsList.filter((w) => w.has_production_impact).length}</span>
							</button>
						</div>
					</div>
					<div class="sd-telemetry-disclosure-card">
						<span class="sd-disclosure-icon">ℹ️</span>
						<div class="sd-disclosure-body">
							<strong>Data Sourcing Notice:</strong> Machine status and operational times are derived from native ERPNext Job Cards and Downtime Entries. Machine-telemetry utilization and OEE are marked <em>Unavailable</em> pending IoT/PLC sensor and shift calendar integration.
						</div>
					</div>
					<div class="sd-table-container">
						<table class="sd-table sd-table-compact" aria-label="Workstation Overview Table">
							<thead>
								<tr>
									<th>Workstation</th>
									<th>Type</th>
									<th>Recorded Status</th>
									<th>Queue Breakdown</th>
									<th>Recorded Downtime</th>
									<th>Utilization & OEE</th>
									<th>Action</th>
								</tr>
							</thead>
							<tbody>
								${filteredWs.map((ws) => `
									<tr class="${ws.has_production_impact ? "sd-row-impact" : ""}">
										<td>
											<div class="sd-ws-ident-cell">
												<a href="javascript:void(0)" class="sd-ws-link" data-inspect-workstation="${this.esc(ws.workstation)}"><strong>${this.esc(ws.workstation_name)}</strong></a>
												<span class="sd-subtle-hint">${this.esc(ws.workstation)}</span>
											</div>
										</td>
										<td><span class="sd-badge-subtle">${this.esc(ws.workstation_type || "General")}</span></td>
										<td>
											<span class="sd-pill sd-status-${this.wsStatusClass(ws.recorded_status)}">
												${this.wsStatusIcon(ws.recorded_status)} ${this.esc(ws.derived_status)}
											</span>
										</td>
										<td>
											<div class="sd-queue-pill-group">
												<span class="sd-pill sd-status-green" title="Active in Progress">${ws.active_job_cards_count} running</span>
												<span class="sd-pill sd-status-blue" title="Queued / Open">${ws.queued_job_cards_count} queued</span>
												${ws.delayed_job_cards_count > 0 ? `<span class="sd-pill sd-status-red" title="Delayed Operations">${ws.delayed_job_cards_count} delayed</span>` : ""}
											</div>
										</td>
										<td>
											${ws.total_downtime_minutes > 0 ? `
												<span class="sd-pill sd-status-red"><strong>${ws.total_downtime_minutes} mins</strong> (${ws.downtime_events_count} stops)</span>
											` : `<span class="sd-subtle-hint">0 mins</span>`}
										</td>
										<td>
											<span class="sd-badge-unavailable" title="${this.esc(ws.utilization_note)}">Not Configured</span>
										</td>
										<td>
											<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-workstation="${this.esc(ws.workstation)}" title="Open Workstation Record">Inspect ↗</a>
										</td>
									</tr>
								`).join("")}
							</tbody>
						</table>
					</div>
				</div>
			`;
			overviewContainer.innerHTML = overviewHtml;
		}

		// 3. Render Recorded Downtime Events Container
		const downtimeContainer = this.el("[data-workstation-downtime-events]");
		if (downtimeContainer) {
			const events = wsd.downtime_events || [];
			const dtHtml = `
				<div class="sd-downtime-events-wrap">
					<div class="sd-section-title">
						<h3>Recorded Downtime Interruption Logs</h3>
						<span class="sd-subtle-hint">Official interruption logs from ERPNext Downtime Entry DocType</span>
					</div>
					${events.length > 0 ? `
						<div class="sd-table-container">
							<table class="sd-table sd-table-compact" aria-label="Recorded Downtime Events Table">
								<thead>
									<tr>
										<th>Entry ID</th>
										<th>Workstation</th>
										<th>From Time</th>
										<th>To Time</th>
										<th>Duration</th>
										<th>Stop Reason & Remarks</th>
										<th>Action</th>
									</tr>
								</thead>
								<tbody>
									${events.map((ev) => `
										<tr>
											<td>
												<a href="javascript:void(0)" class="sd-dt-link" data-inspect-downtime="${this.esc(ev.downtime_entry)}"><strong>${this.esc(ev.downtime_entry)}</strong></a>
											</td>
											<td><span class="sd-badge-subtle">${this.esc(ev.workstation)}</span></td>
											<td>${this.esc(ev.from_time)}</td>
											<td>${ev.to_time ? this.esc(ev.to_time) : `<span class="sd-pill sd-status-amber">Open (Ongoing)</span>`}</td>
											<td><strong>${ev.duration_minutes} mins</strong></td>
											<td>
												<span class="sd-dt-reason">${this.esc(ev.stop_reason)}</span>
												${ev.remarks ? `<span class="sd-subtle-hint"> — ${this.esc(ev.remarks)}</span>` : ""}
											</td>
											<td>
												<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-downtime="${this.esc(ev.downtime_entry)}">View ↗</a>
											</td>
										</tr>
									`).join("")}
								</tbody>
							</table>
						</div>
					` : `
						<div class="sd-empty-box sd-empty-bordered">
							<span class="sd-empty-icon">✓</span>
							<p>No machine downtime events recorded in the selected period.</p>
							<span class="sd-subtle-hint">Downtime records are logged via ERPNext <strong>Downtime Entry</strong> records.</span>
						</div>
					`}
				</div>
			`;
			downtimeContainer.innerHTML = dtHtml;
		}

		// 4. Render Production Impact Analysis
		const impactContainer = this.el("[data-workstation-impact]");
		if (impactContainer) {
			const impactList = wsd.production_impact || [];
			if (impactList.length > 0) {
				const impactHtml = `
					<div class="sd-impact-wrap">
						<div class="sd-section-title">
							<h3>Production Schedule Impact</h3>
							<span class="sd-subtle-hint">Workstations with delays or downtime affecting scheduled operations</span>
						</div>
						<div class="sd-impact-cards-grid">
							${impactList.map((imp) => `
								<div class="sd-impact-card">
									<div class="sd-impact-card-header">
										<div>
											<h4>${this.esc(imp.workstation_name)}</h4>
											<span class="sd-badge-subtle">${this.esc(imp.workstation_type || "Station")}</span>
										</div>
										<div class="sd-impact-badges">
											${imp.delayed_jobs_count > 0 ? `<span class="sd-pill sd-status-red">${imp.delayed_jobs_count} Delayed Jobs</span>` : ""}
											${imp.downtime_minutes > 0 ? `<span class="sd-pill sd-status-orange">${imp.downtime_minutes}m Downtime</span>` : ""}
										</div>
									</div>
									<div class="sd-affected-jobs-list">
										<strong>Affected Operations & Jobs:</strong>
										<ul>
											${imp.affected_jobs.map((j) => `
												<li>
													<a href="javascript:void(0)" data-inspect-jc="${this.esc(j.job_card)}"><strong>${this.esc(j.job_card)}</strong></a>:
													${this.esc(j.operation)} (${this.esc(j.production_item || "Item")})
													${j.is_overdue ? `<span class="sd-pill sd-status-red sd-mini-badge">Overdue</span>` : ""}
												</li>
											`).join("")}
										</ul>
									</div>
								</div>
							`).join("")}
						</div>
					</div>
				`;
				impactContainer.innerHTML = impactHtml;
			} else {
				impactContainer.innerHTML = "";
			}
		}

		// 5. Render Paginated Workstation Activity Lines
		const activityContainer = this.el("[data-workstation-activity]");
		if (activityContainer && wsd.workstation_activity) {
			const actLines = wsd.workstation_activity;
			const actHtml = `
				<div class="sd-ws-activity-wrap">
					<div class="sd-section-title">
						<h3>Recorded Workstation Operation Activity</h3>
						<span class="sd-subtle-hint">Showing ${actLines.length} of ${wsd.total_activity_lines} recorded operations</span>
					</div>
					${actLines.length > 0 ? `
						<div class="sd-table-container">
							<table class="sd-table sd-table-compact" aria-label="Workstation Activity Table">
								<thead>
									<tr>
										<th>Job Card & Work Order</th>
										<th>Operation & Workstation</th>
										<th>Status</th>
										<th>Planned / Actual Quantity</th>
										<th>Target Completion</th>
										<th>Time Spent</th>
										<th>Action</th>
									</tr>
								</thead>
								<tbody>
									${actLines.map((row) => `
										<tr class="${row.is_overdue ? "sd-row-overdue" : ""}">
											<td>
												<div class="sd-jc-ident-cell">
													<a href="javascript:void(0)" data-inspect-jc="${this.esc(row.job_card)}"><strong>${this.esc(row.job_card)}</strong></a>
													<span class="sd-subtle-hint">${this.esc(row.work_order || "Standalone")}</span>
												</div>
											</td>
											<td>
												<div class="sd-op-cell">
													<strong>${this.esc(row.operation)}</strong>
													<span class="sd-subtle-hint">📍 ${this.esc(row.workstation || "Unassigned")}</span>
												</div>
											</td>
											<td>
												<span class="sd-pill sd-status-${this.opStatusClass(row.status)}">
													${this.opStatusIcon(row.status)} ${this.esc(row.status)}
												</span>
											</td>
											<td>
												<span class="sd-qty-val">${this.num(row.total_completed_qty)} / ${this.num(row.for_quantity)}</span>
											</td>
											<td>
												<div class="sd-target-cell">
													<span>${this.esc(row.target_completion_date || "—")}</span>
													${row.is_overdue ? `
														<span class="sd-pill sd-status-red">${Math.abs(row.days_to_target)}d overdue</span>
													` : row.is_due_soon ? `
														<span class="sd-pill sd-status-amber">${row.days_to_target}d left</span>
													` : ""}
												</div>
											</td>
											<td>
												${row.time_spent_mins > 0 ? `<span>${row.time_spent_mins} mins</span>` : `<span class="sd-subtle-hint">0 mins</span>`}
											</td>
											<td>
												<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-jc="${this.esc(row.job_card)}" title="Inspect Job Card">View ↗</a>
											</td>
										</tr>
									`).join("")}
								</tbody>
							</table>
						</div>
					` : `
						<div class="sd-empty-box">${this.empty("No recorded operations found matching the selected filters.")}</div>
					`}
				</div>
			`;
			activityContainer.innerHTML = actHtml;
		}
	}

	renderQualityOverview() {
		const panel = this.el("[data-quality-overview-panel]");
		if (!panel) return;
		const qo = this.data?.quality_overview;
		if (!qo || qo.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Quality &amp; Inspection Overview</h2>
						<p>Quality inspection results, pass/fail performance, sample sizes, and defect breakdown</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(qo?.reason || "Quality inspection view is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-quality-badge]");
		if (badge) {
			badge.textContent = `As of ${qo.reference_date}`;
		}

		// 1. Render Quality KPIs
		const kpisContainer = this.el("[data-quality-kpis]");
		if (kpisContainer && qo.summary) {
			const s = qo.summary;
			kpisContainer.replaceChildren(
				frappe.sarathiUI.kpi({
					label: "Total Inspections",
					value: this.num(s.total_inspections),
					description: "Submitted quality reports",
					indicator: "blue",
				}),
				frappe.sarathiUI.kpi({
					label: "Passed Inspections",
					value: this.num(s.passed_inspections),
					description: "Accepted without defects",
					indicator: "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Failed Inspections",
					value: this.num(s.failed_inspections),
					description: s.distinct_rejected_items > 0 ? `${s.distinct_rejected_items} distinct defect item(s)` : "Rejections recorded",
					indicator: s.failed_inspections > 0 ? "red" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Failure Rate",
					value: `${s.failure_rate_percent}%`,
					description: "Defect percentage",
					indicator: s.failure_rate_percent > 5 ? "red" : s.failure_rate_percent > 0 ? "amber" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Draft Inspections",
					value: this.num(s.pending_inspections),
					description: "Pending formal submission",
					indicator: s.pending_inspections > 0 ? "amber" : "gray",
				})
			);
		}

		// 2. Render Defect Breakdown & Status Filter Pills
		const summaryContainer = this.el("[data-quality-summary]");
		if (summaryContainer) {
			const currentStatus = this.qualitySelectedStatus || "All";
			const topDefects = qo.top_rejected_items || [];
			summaryContainer.innerHTML = `
				<div class="sd-quality-summary-card">
					<div class="sd-table-web-toolbar">
						<div class="sd-table-filter-pills">
							<span class="sd-filter-label">Filter Status:</span>
							<button type="button" class="sd-filter-pill ${currentStatus === "All" ? "active" : ""}" data-action="filter-quality-status" data-status="All">All (${qo.total_inspections_count})</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Accepted" ? "active" : ""}" data-action="filter-quality-status" data-status="Accepted">✓ Accepted (${qo.summary.passed_inspections})</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Rejected" ? "active" : ""}" data-action="filter-quality-status" data-status="Rejected">✕ Rejected (${qo.summary.failed_inspections})</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Draft" ? "active" : ""}" data-action="filter-quality-status" data-status="Draft">✎ Draft (${qo.summary.pending_inspections})</button>
						</div>
					</div>
					${topDefects.length > 0 ? `
						<div class="sd-defect-breakdown-bar">
							<span class="sd-defect-bar-title">⚠️ Defect Rejection Breakdown:</span>
							<div class="sd-defect-badges">
								${topDefects.map(d => `
									<span class="sd-pill sd-status-red" title="${this.esc(d.item_name)}: ${d.rejections_count} rejections (${this.num(d.sample_units)} units)">
										<strong>${this.esc(d.item_code)}</strong>: ${d.rejections_count} rejected (${this.num(d.sample_units)} units)
									</span>
								`).join("")}
							</div>
						</div>
					` : ""}
				</div>
			`;
		}

		// 3. Render Quality Inspections Table
		const inspectionsContainer = this.el("[data-quality-inspections]");
		if (inspectionsContainer) {
			const currentStatus = this.qualitySelectedStatus || "All";
			let inspList = qo.inspections || [];
			if (currentStatus !== "All") {
				inspList = inspList.filter(row => row.status === currentStatus);
			}

			inspectionsContainer.innerHTML = `
				<div class="sd-table-section">
					<div class="sd-table-header-row">
						<h3>Quality Inspection Records</h3>
						<span class="sd-subtle-hint">Showing ${inspList.length} of ${qo.total_inspections_count} inspections</span>
					</div>
					${inspList.length > 0 ? `
						<div class="sd-table-container">
							<table class="sd-table sd-table-compact" aria-label="Quality Inspections Table">
								<thead>
									<tr>
										<th>Inspection ID &amp; Date</th>
										<th>Type &amp; Reference Document</th>
										<th>Item Inspected</th>
										<th>Inspection Result</th>
										<th>Sample Size</th>
										<th>Inspector</th>
										<th>Action</th>
									</tr>
								</thead>
								<tbody>
									${inspList.map(row => `
										<tr class="${row.is_rejected ? "sd-row-rejected" : ""}">
											<td>
												<div class="sd-qi-ident-cell">
													<a href="javascript:void(0)" data-inspect-qi="${this.esc(row.name)}"><strong>${this.esc(row.name)}</strong></a>
													<span class="sd-subtle-hint">${this.esc(row.report_date || "—")}</span>
												</div>
											</td>
											<td>
												<div class="sd-ref-cell">
													<span class="sd-badge sd-badge-azure">${this.esc(row.inspection_type)}</span>
													${row.reference_name ? `<span class="sd-subtle-hint">${this.esc(row.reference_type || "")}: ${this.esc(row.reference_name)}</span>` : `<span class="sd-subtle-hint">Standalone</span>`}
												</div>
											</td>
											<td>
												<div class="sd-item-cell">
													<a href="javascript:void(0)" data-inspect-item="${this.esc(row.item_code)}"><strong>${this.esc(row.item_code)}</strong></a>
													<span class="sd-subtle-hint" title="${this.esc(row.item_name)}">${this.esc(row.item_name)}</span>
												</div>
											</td>
											<td>
												<span class="sd-pill sd-status-${row.status === "Accepted" ? "green" : row.status === "Rejected" ? "red" : "amber"}">
													${row.status === "Accepted" ? "✓" : row.status === "Rejected" ? "✕" : "✎"} ${this.esc(row.status)}
												</span>
											</td>
											<td>
												<span class="sd-qty-val">${this.num(row.sample_size)} ${this.esc(row.stock_uom)}</span>
											</td>
											<td>
												<span class="sd-subtle-hint">${this.esc(row.inspected_by)}</span>
											</td>
											<td>
												<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-qi="${this.esc(row.name)}" title="Inspect Quality Record">View ↗</a>
											</td>
										</tr>
									`).join("")}
								</tbody>
							</table>
						</div>
					` : `
						<div class="sd-empty-box">${this.empty("No quality inspection records found matching the selected filter.")}</div>
					`}
				</div>
			`;
		}
	}

	renderReworkOverview() {
		const panel = this.el("[data-rework-overview-panel]");
		if (!panel) return;
		const ro = this.data?.rework_overview;
		if (!ro || ro.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Rework &amp; Corrective Actions</h2>
						<p>Corrective Job Cards, rework operations, parent job linkages, and defect resolution status</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(ro?.reason || "Rework and corrective action view is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		if (ro.rework_configured === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Rework &amp; Corrective Actions</h2>
						<p>Corrective Job Cards, rework operations, parent job linkages, and defect resolution status</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-gray">Feature Not Configured</span>
					</div>
				</div>
				<div class="sd-notice-box">
					<div class="sd-notice-icon">ℹ️</div>
					<div class="sd-notice-content">
						<strong>Rework tracking is not configured</strong>
						<p>${this.esc(ro.rework_note || "ERPNext Job Card is not configured with the corrective rework field (is_corrective_job_card). Rework tracking requires corrective Job Cards linked via for_job_card.")}</p>
					</div>
				</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-rework-badge]");
		if (badge) {
			badge.textContent = `As of ${ro.reference_date}`;
		}

		// 1. Render Rework KPIs
		const kpisContainer = this.el("[data-rework-kpis]");
		if (kpisContainer && ro.summary) {
			const s = ro.summary;
			kpisContainer.replaceChildren(
				frappe.sarathiUI.kpi({
					label: "Total Rework Jobs",
					value: this.num(s.total_rework_jobs),
					description: "Corrective Job Cards created",
					indicator: "blue",
				}),
				frappe.sarathiUI.kpi({
					label: "In Progress Rework",
					value: this.num(s.in_progress_rework),
					description: "Currently being rectified",
					indicator: s.in_progress_rework > 0 ? "blue" : "gray",
				}),
				frappe.sarathiUI.kpi({
					label: "Queued Rework",
					value: this.num(s.queued_rework),
					description: "Awaiting shop-floor start",
					indicator: s.queued_rework > 0 ? "amber" : "gray",
				}),
				frappe.sarathiUI.kpi({
					label: "Completed Rework",
					value: this.num(s.completed_rework),
					description: "Successfully rectified",
					indicator: "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Delayed Rework",
					value: this.num(s.delayed_rework),
					description: "Past target schedule",
					indicator: s.delayed_rework > 0 ? "red" : "green",
				})
			);
		}

		// 2. Render Status Filters
		const summaryContainer = this.el("[data-rework-summary]");
		if (summaryContainer) {
			const currentStatus = this.reworkSelectedStatus || "All";
			summaryContainer.innerHTML = `
				<div class="sd-table-web-toolbar">
					<div class="sd-table-filter-pills">
						<span class="sd-filter-label">Filter Status:</span>
						<button type="button" class="sd-filter-pill ${currentStatus === "All" ? "active" : ""}" data-action="filter-rework-status" data-status="All">All (${ro.total_rework_count})</button>
						<button type="button" class="sd-filter-pill ${currentStatus === "Open" ? "active" : ""}" data-action="filter-rework-status" data-status="Open">Open (${ro.summary.queued_rework})</button>
						<button type="button" class="sd-filter-pill ${currentStatus === "Work In Progress" ? "active" : ""}" data-action="filter-rework-status" data-status="Work In Progress">In Progress (${ro.summary.in_progress_rework})</button>
						<button type="button" class="sd-filter-pill ${currentStatus === "Completed" ? "active" : ""}" data-action="filter-rework-status" data-status="Completed">Completed (${ro.summary.completed_rework})</button>
					</div>
				</div>
			`;
		}

		// 3. Render Rework Table
		const jobsContainer = this.el("[data-rework-jobs]");
		if (jobsContainer) {
			const currentStatus = this.reworkSelectedStatus || "All";
			let jobList = ro.rework_jobs || [];
			if (currentStatus !== "All") {
				jobList = jobList.filter(row => row.status === currentStatus);
			}

			jobsContainer.innerHTML = `
				<div class="sd-table-section">
					<div class="sd-table-header-row">
						<h3>Corrective Rework Jobs</h3>
						<span class="sd-subtle-hint">Showing ${jobList.length} of ${ro.total_rework_count} rework jobs</span>
					</div>
					${jobList.length > 0 ? `
						<div class="sd-table-container">
							<table class="sd-table sd-table-compact" aria-label="Rework Jobs Table">
								<thead>
									<tr>
										<th>Corrective Job Card</th>
										<th>Root Cause / Linked Records</th>
										<th>Work Order &amp; Item</th>
										<th>Operation &amp; Workstation</th>
										<th>Status</th>
										<th>Rework Qty</th>
										<th>Target Date</th>
										<th>Action</th>
									</tr>
								</thead>
								<tbody>
									${jobList.map(row => `
										<tr class="${row.is_overdue ? "sd-row-overdue" : ""}">
											<td>
												<div class="sd-jc-ident-cell">
													<a href="javascript:void(0)" data-inspect-jc="${this.esc(row.job_card)}"><strong>${this.esc(row.job_card)}</strong></a>
													<span class="sd-badge sd-badge-purple">Corrective Job</span>
												</div>
											</td>
											<td>
												<div class="sd-linked-records-cell">
													${row.original_job_card ? `<span>Original Job: <a href="javascript:void(0)" data-inspect-jc="${this.esc(row.original_job_card)}">${this.esc(row.original_job_card)}</a></span>` : ""}
													${row.quality_inspection ? `<span>Defect QI: <a href="javascript:void(0)" data-inspect-qi="${this.esc(row.quality_inspection)}">${this.esc(row.quality_inspection)}</a></span>` : ""}
													${!row.original_job_card && !row.quality_inspection ? `<span class="sd-subtle-hint">—</span>` : ""}
												</div>
											</td>
											<td>
												<div class="sd-wo-cell">
													${row.work_order ? `<a href="javascript:void(0)" data-inspect-wo="${this.esc(row.work_order)}"><strong>${this.esc(row.work_order)}</strong></a>` : "—"}
													<span class="sd-subtle-hint" title="${this.esc(row.production_item_name)}">${this.esc(row.production_item || "—")}</span>
												</div>
											</td>
											<td>
												<div class="sd-op-cell">
													<strong>${this.esc(row.operation)}</strong>
													<span class="sd-subtle-hint">📍 ${this.esc(row.workstation || "Unassigned")}</span>
												</div>
											</td>
											<td>
												<span class="sd-pill sd-status-${row.status === "Completed" ? "green" : row.status === "Work In Progress" ? "blue" : "amber"}">
													${row.status === "Completed" ? "✓" : row.status === "Work In Progress" ? "⚙" : "•"} ${this.esc(row.status)}
												</span>
											</td>
											<td>
												<span class="sd-qty-val">${this.num(row.completed_quantity)} / ${this.num(row.rework_quantity)}</span>
											</td>
											<td>
												<div class="sd-target-cell">
													<span>${this.esc(row.target_completion_date || "—")}</span>
													${row.is_overdue ? `<span class="sd-pill sd-status-red">${Math.abs(row.days_to_target)}d overdue</span>` : ""}
												</div>
											</td>
											<td>
												<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-jc="${this.esc(row.job_card)}" title="Inspect Job Card">View ↗</a>
											</td>
										</tr>
									`).join("")}
								</tbody>
							</table>
						</div>
					` : `
						<div class="sd-empty-box">${this.empty("No rework or corrective Job Cards match the selected filter.")}</div>
					`}
				</div>
			`;
		}
	}

	renderSubcontractingOverview() {
		const panel = this.el("[data-subcontracting-overview-panel]");
		if (!panel) return;
		const sco = this.data?.subcontracting_overview;
		if (!sco || sco.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Subcontracting Operations &amp; Receipts</h2>
						<p>Outsourced production orders, supplier fulfillment, material reconciliation, and overdue receipts</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(sco?.reason || "Subcontracting Order view is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-subcontracting-badge]");
		if (badge) {
			badge.textContent = `As of ${sco.reference_date}`;
		}

		// 1. Render Subcontracting KPIs
		const kpisContainer = this.el("[data-subcontracting-kpis]");
		if (kpisContainer && sco.summary) {
			const s = sco.summary;
			kpisContainer.replaceChildren(
				frappe.sarathiUI.kpi({
					label: "Total Subcontract Orders",
					value: this.num(s.total_subcontract_orders),
					description: "Subcontracting orders recorded",
					indicator: "blue",
				}),
				frappe.sarathiUI.kpi({
					label: "Active Subcontracts",
					value: this.num(s.active_subcontracts),
					description: "In progress with suppliers",
					indicator: "blue",
				}),
				frappe.sarathiUI.kpi({
					label: "Awaiting Receipt",
					value: this.num(s.awaiting_receipt_orders),
					description: "Pending delivery from vendor",
					indicator: s.awaiting_receipt_orders > 0 ? "amber" : "gray",
				}),
				frappe.sarathiUI.kpi({
					label: "Overdue Subcontracts",
					value: this.num(s.overdue_subcontracts),
					description: "Past schedule date",
					indicator: s.overdue_subcontracts > 0 ? "red" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Outstanding Units",
					value: this.num(s.total_outstanding_units),
					description: `Ordered: ${this.num(s.total_ordered_units)} · Received: ${this.num(s.total_received_units)}`,
					indicator: s.total_outstanding_units > 0 ? "amber" : "green",
				})
			);
		}

		// 2. Render Subcontracting Orders Table
		const ordersContainer = this.el("[data-subcontracting-orders]");
		if (ordersContainer) {
			const currentStatus = this.subcontractingSelectedStatus || "All";
			let orderList = sco.orders || [];
			if (currentStatus !== "All") {
				orderList = orderList.filter(row => row.status === currentStatus);
			}

			ordersContainer.innerHTML = `
				<div class="sd-table-section">
					<div class="sd-table-header-row">
						<div>
							<h3>Subcontracting Orders &amp; Receipts</h3>
							<span class="sd-subtle-hint">Showing ${orderList.length} of ${sco.total_orders_count} subcontracting orders</span>
						</div>
						<div class="sd-table-filter-pills">
							<span class="sd-filter-label">Filter:</span>
							<button type="button" class="sd-filter-pill ${currentStatus === "All" ? "active" : ""}" data-action="filter-subcontracting-status" data-status="All">All (${sco.total_orders_count})</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Open" ? "active" : ""}" data-action="filter-subcontracting-status" data-status="Open">Open</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Partially Received" ? "active" : ""}" data-action="filter-subcontracting-status" data-status="Partially Received">Partially Received</button>
							<button type="button" class="sd-filter-pill ${currentStatus === "Completed" ? "active" : ""}" data-action="filter-subcontracting-status" data-status="Completed">Completed</button>
						</div>
					</div>
					${orderList.length > 0 ? `
						<div class="sd-table-container">
							<table class="sd-table sd-table-compact" aria-label="Subcontracting Orders Table">
								<thead>
									<tr>
										<th>Subcontracting Order &amp; PO</th>
										<th>Supplier</th>
										<th>Target Item</th>
										<th>Quantities (Ordered / Recv / Outst)</th>
										<th>Fulfillment Progress</th>
										<th>Status</th>
										<th>Target Date</th>
										<th>Action</th>
									</tr>
								</thead>
								<tbody>
									${orderList.map(row => `
										<tr class="${row.is_overdue ? "sd-row-overdue" : ""}">
											<td>
												<div class="sd-sco-ident-cell">
													<a href="javascript:void(0)" data-inspect-sco="${this.esc(row.subcontracting_order)}"><strong>${this.esc(row.subcontracting_order)}</strong></a>
													${row.purchase_order ? `<span class="sd-subtle-hint">PO: <a href="javascript:void(0)" data-inspect-po="${this.esc(row.purchase_order)}">${this.esc(row.purchase_order)}</a></span>` : ""}
												</div>
											</td>
											<td>
												<div class="sd-supplier-cell">
													<a href="javascript:void(0)" data-inspect-supplier="${this.esc(row.supplier)}"><strong>${this.esc(row.supplier_name)}</strong></a>
													<span class="sd-subtle-hint">${this.esc(row.supplier)}</span>
												</div>
											</td>
											<td>
												<div class="sd-item-cell">
													<a href="javascript:void(0)" data-inspect-item="${this.esc(row.item_code)}"><strong>${this.esc(row.item_code)}</strong></a>
													<span class="sd-subtle-hint" title="${this.esc(row.item_name)}">${this.esc(row.item_name)}</span>
												</div>
											</td>
											<td>
												<div class="sd-qty-cell">
													<span>Ord: <b>${this.num(row.ordered_qty)}</b> ${this.esc(row.stock_uom)}</span>
													<span class="sd-subtle-hint">Rec: ${this.num(row.received_qty)} · Out: ${this.num(row.outstanding_qty)}</span>
												</div>
											</td>
											<td>
												<div class="sd-progress-wrap">
													<div class="sd-progress-bar">
														<div class="sd-progress-fill" style="width: ${Math.min(100, Math.max(0, row.per_received))}%;"></div>
													</div>
													<span class="sd-progress-label">${row.per_received}%</span>
												</div>
											</td>
											<td>
												<span class="sd-pill sd-status-${row.status === "Completed" ? "green" : row.status === "Partially Received" ? "blue" : row.is_overdue ? "red" : "amber"}">
													${row.status === "Completed" ? "✓" : row.status === "Partially Received" ? "◐" : "•"} ${this.esc(row.status)}
												</span>
											</td>
											<td>
												<div class="sd-target-cell">
													<span>${this.esc(row.schedule_date || "—")}</span>
													${row.is_overdue ? `<span class="sd-pill sd-status-red">${Math.abs(row.days_to_target)}d overdue</span>` : ""}
												</div>
											</td>
											<td>
												<a href="javascript:void(0)" class="sd-btn-xs" data-inspect-sco="${this.esc(row.subcontracting_order)}" title="Inspect Subcontracting Order">View ↗</a>
											</td>
										</tr>
									`).join("")}
								</tbody>
							</table>
						</div>
					` : `
						<div class="sd-empty-box">${this.empty("No Subcontracting Orders found matching the selected filter.")}</div>
					`}
				</div>
			`;
		}
	}

	renderProductionExceptions() {
		const panel = this.el("[data-production-exceptions-panel]");
		if (!panel) return;
		const pe = this.data?.production_exceptions;
		if (!pe || pe.available === false) {
			panel.innerHTML = `
				<div class="sd-panel-heading">
					<div>
						<h2>Production Exception &amp; Escalation Queue</h2>
						<p>Prioritized operational bottlenecks, material shortages, machine downtime, quality defects, and vendor delays</p>
					</div>
					<div class="sd-panel-actions">
						<span class="sd-pill sd-status-amber">Restricted Scope</span>
					</div>
				</div>
				<div class="sd-empty-box">${this.empty(pe?.reason || "Production exception queue is unavailable for your permission scope.")}</div>
			`;
			return;
		}

		// Update badge
		const badge = this.el("[data-exceptions-badge]");
		if (badge) {
			const critCount = pe.summary?.critical_exceptions || 0;
			const totalOpen = pe.summary?.total_open_exceptions || 0;
			badge.textContent = `${totalOpen} Open Exceptions (${critCount} Critical)`;
			badge.className = `sd-pill sd-status-${critCount > 0 ? "red" : totalOpen > 0 ? "amber" : "green"}`;
		}

		// 1. Render Exception KPIs
		const kpisContainer = this.el("[data-exceptions-kpis]");
		if (kpisContainer && pe.summary) {
			const s = pe.summary;
			const otherCount = (s.quality_exceptions || 0) + (s.subcontracting_exceptions || 0) + (s.workstation_exceptions || 0);
			kpisContainer.replaceChildren(
				frappe.sarathiUI.kpi({
					label: "Total Open Exceptions",
					value: this.num(s.total_open_exceptions),
					description: `${s.distinct_affected_documents} distinct document(s)`,
					indicator: s.total_open_exceptions > 0 ? "red" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Critical Escalations",
					value: this.num(s.critical_exceptions),
					description: "Immediate action required",
					indicator: s.critical_exceptions > 0 ? "red" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "High Priority",
					value: this.num(s.high_exceptions),
					description: "Significant production risk",
					indicator: s.high_exceptions > 0 ? "amber" : "gray",
				}),
				frappe.sarathiUI.kpi({
					label: "Production Delays",
					value: this.num(s.production_exceptions),
					description: "Overdue WOs & Job Cards",
					indicator: s.production_exceptions > 0 ? "blue" : "gray",
				}),
				frappe.sarathiUI.kpi({
					label: "Material Shortages",
					value: this.num(s.material_exceptions),
					description: "Deficits blocking production",
					indicator: s.material_exceptions > 0 ? "red" : "green",
				}),
				frappe.sarathiUI.kpi({
					label: "Quality & Subcontracts",
					value: this.num(otherCount),
					description: "Defects, downtime & vendor delays",
					indicator: otherCount > 0 ? "purple" : "gray",
				})
			);
		}

		// 2. Render Toolbar (Category Pills, Severity Pills, Search Box)
		const toolbarContainer = this.el("[data-exceptions-toolbar]");
		if (toolbarContainer) {
			const activeCat = this.exceptionSelectedCategory || "All";
			const activeSev = this.exceptionSelectedSeverity || "All";
			const searchVal = this.exceptionSearch || "";

			toolbarContainer.innerHTML = `
				<div class="sd-exc-toolbar">
					<div class="sd-exc-filter-row">
						<div class="sd-table-filter-pills">
							<span class="sd-filter-label">Category:</span>
							<button type="button" class="sd-filter-pill ${activeCat === "All" ? "active" : ""}" data-action="filter-exception-category" data-category="All">All (${pe.total_exceptions_count})</button>
							<button type="button" class="sd-filter-pill ${activeCat === "Production" ? "active" : ""}" data-action="filter-exception-category" data-category="Production">🏭 Production (${pe.summary.production_exceptions})</button>
							<button type="button" class="sd-filter-pill ${activeCat === "Material" ? "active" : ""}" data-action="filter-exception-category" data-category="Material">📦 Material (${pe.summary.material_exceptions})</button>
							<button type="button" class="sd-filter-pill ${activeCat === "Workstation" ? "active" : ""}" data-action="filter-exception-category" data-category="Workstation">⚙️ Downtime (${pe.summary.workstation_exceptions})</button>
							<button type="button" class="sd-filter-pill ${activeCat === "Quality" ? "active" : ""}" data-action="filter-exception-category" data-category="Quality">🔍 Quality (${pe.summary.quality_exceptions})</button>
							<button type="button" class="sd-filter-pill ${activeCat === "Subcontracting" ? "active" : ""}" data-action="filter-exception-category" data-category="Subcontracting">🚚 Subcontracting (${pe.summary.subcontracting_exceptions})</button>
						</div>
					</div>
					<div class="sd-exc-filter-row sd-exc-subrow">
						<div class="sd-table-filter-pills">
							<span class="sd-filter-label">Severity:</span>
							<button type="button" class="sd-filter-pill ${activeSev === "All" ? "active" : ""}" data-action="filter-exception-severity" data-severity="All">All Severities</button>
							<button type="button" class="sd-filter-pill sd-pill-sev-critical ${activeSev === "Critical" ? "active" : ""}" data-action="filter-exception-severity" data-severity="Critical">🔴 Critical (${pe.summary.critical_exceptions})</button>
							<button type="button" class="sd-filter-pill sd-pill-sev-high ${activeSev === "High" ? "active" : ""}" data-action="filter-exception-severity" data-severity="High">🟠 High (${pe.summary.high_exceptions})</button>
							<button type="button" class="sd-filter-pill sd-pill-sev-medium ${activeSev === "Medium" ? "active" : ""}" data-action="filter-exception-severity" data-severity="Medium">🔵 Medium (${pe.summary.medium_exceptions})</button>
							<button type="button" class="sd-filter-pill sd-pill-sev-low ${activeSev === "Low" ? "active" : ""}" data-action="filter-exception-severity" data-severity="Low">⚪ Low (${pe.summary.low_exceptions})</button>
						</div>
						<div class="sd-table-search-wrap">
							<input type="search" class="sd-table-search-input" data-exception-search placeholder="Search exceptions (ID, Item, WO, Supplier)..." value="${this.esc(searchVal)}" aria-label="Search exceptions">
							${(activeCat !== "All" || activeSev !== "All" || searchVal) ? `<button type="button" class="sd-button sd-btn-xs" data-action="clear-exception-filters">Reset Filters</button>` : ""}
						</div>
					</div>
				</div>
			`;
		}

		// 3. Render Exception Table
		this.renderExceptionTable();
	}

	renderExceptionTable() {
		const tableContainer = this.el("[data-exceptions-table]");
		if (!tableContainer) return;
		const pe = this.data?.production_exceptions;
		if (!pe || !pe.exceptions) return;

		const activeCat = this.exceptionSelectedCategory || "All";
		const activeSev = this.exceptionSelectedSeverity || "All";
		const search = (this.exceptionSearch || "").toLowerCase();

		let list = pe.exceptions;
		if (activeCat !== "All") {
			list = list.filter(e => e.category === activeCat);
		}
		if (activeSev !== "All") {
			list = list.filter(e => e.severity === activeSev);
		}
		if (search) {
			list = list.filter(e =>
				(e.title || "").toLowerCase().includes(search) ||
				(e.description || "").toLowerCase().includes(search) ||
				(e.source_document || "").toLowerCase().includes(search) ||
				(e.work_order || "").toLowerCase().includes(search) ||
				(e.item_code || "").toLowerCase().includes(search) ||
				(e.workstation || "").toLowerCase().includes(search) ||
				(e.supplier_name || "").toLowerCase().includes(search)
			);
		}

		const sevClass = (sev) => {
			if (sev === "Critical") return "sd-sev-critical";
			if (sev === "High") return "sd-sev-high";
			if (sev === "Medium") return "sd-sev-medium";
			return "sd-sev-low";
		};

		const catIcon = (cat) => {
			if (cat === "Production") return "🏭";
			if (cat === "Material") return "📦";
			if (cat === "Workstation") return "⚙️";
			if (cat === "Quality") return "🔍";
			if (cat === "Subcontracting") return "🚚";
			return "⚠️";
		};

		tableContainer.innerHTML = `
			<div class="sd-table-section">
				<div class="sd-table-header-row">
					<div>
						<h3>Prioritized Exception Queue</h3>
						<span class="sd-subtle-hint">Showing ${list.length} of ${pe.total_exceptions_count} detected exceptions · Ranked by severity and duration</span>
					</div>
				</div>
				${list.length > 0 ? `
					<div class="sd-table-container">
						<table class="sd-table sd-table-compact sd-exceptions-queue-table" aria-label="Production Exceptions Table">
							<thead>
								<tr>
									<th>Severity</th>
									<th>Exception &amp; Problem Details</th>
									<th>Category &amp; Type</th>
									<th>Source Document</th>
									<th>Related Item / Station</th>
									<th>Due Date &amp; Delay</th>
									<th>Recommended Action</th>
									<th>Action</th>
								</tr>
							</thead>
							<tbody>
								${list.map(e => `
									<tr class="sd-exc-row ${sevClass(e.severity)}">
										<td>
											<span class="sd-pill ${sevClass(e.severity)}">
												${e.severity === "Critical" ? "🔴 " : e.severity === "High" ? "🟠 " : e.severity === "Medium" ? "🔵 " : "⚪ "}
												${this.esc(e.severity)}
											</span>
										</td>
										<td>
											<div class="sd-exc-problem-cell">
												<strong>${this.esc(e.title)}</strong>
												<p class="sd-exc-desc">${this.esc(e.description)}</p>
												<span class="sd-badge sd-badge-azure">${this.esc(e.impact_summary)}</span>
											</div>
										</td>
										<td>
											<div class="sd-exc-type-cell">
												<span class="sd-badge sd-badge-purple">${catIcon(e.category)} ${this.esc(e.category)}</span>
												<span class="sd-subtle-hint">${this.esc(e.exception_type)}</span>
											</div>
										</td>
										<td>
											<div class="sd-exc-doc-cell">
												${this.link(e.source_doctype, e.source_document)}
												<span class="sd-subtle-hint">${this.esc(e.source_doctype)}</span>
											</div>
										</td>
										<td>
											<div class="sd-exc-context-cell">
												${e.item_code ? `<span>Item: <a href="javascript:void(0)" data-inspect-item="${this.esc(e.item_code)}"><strong>${this.esc(e.item_code)}</strong></a></span>` : ""}
												${e.workstation ? `<span>Station: <a href="javascript:void(0)" data-inspect-workstation="${this.esc(e.workstation)}"><strong>${this.esc(e.workstation)}</strong></a></span>` : ""}
												${e.supplier ? `<span>Supplier: <a href="javascript:void(0)" data-inspect-supplier="${this.esc(e.supplier)}"><strong>${this.esc(e.supplier_name || e.supplier)}</strong></a></span>` : ""}
												${!e.item_code && !e.workstation && !e.supplier ? `<span class="sd-subtle-hint">—</span>` : ""}
											</div>
										</td>
										<td>
											<div class="sd-target-cell">
												<span>${this.esc(e.due_date || "—")}</span>
												${e.delay_days !== null && e.delay_days > 0 ? `
													<span class="sd-pill sd-status-red">${e.delay_days}d overdue</span>
												` : e.delay_days === 0 ? `
													<span class="sd-pill sd-status-amber">Due today</span>
												` : ""}
											</div>
										</td>
										<td>
											<div class="sd-exc-rec-cell">
												<p>${this.esc(e.recommended_action)}</p>
											</div>
										</td>
										<td>
											<a href="javascript:void(0)" class="sd-btn-xs" data-inspect="${this.esc(e.source_document)}" data-doctype="${this.esc(e.source_doctype)}" title="Inspect ${this.esc(e.source_doctype)}">Inspect ↗</a>
										</td>
									</tr>
								`).join("")}
							</tbody>
						</table>
					</div>
				` : `
					<div class="sd-empty-box">${this.empty("No open production exceptions found matching the selected category and severity filters.")}</div>
				`}
			</div>
		`;
	}

	filterExceptionTable() {
		this.renderExceptionTable();
	}

	wsStatusClass(status) {
		const map = {
			"Production": "green",
			"Active": "green",
			"Idle": "blue",
			"Off": "gray",
			"Problem": "red",
			"Maintenance": "amber",
			"Setup": "purple",
		};
		return map[status] || "blue";
	}

	wsStatusIcon(status) {
		const map = {
			"Production": "⚙️",
			"Active": "⚙️",
			"Idle": "⏸",
			"Off": "⏹",
			"Problem": "⚠",
			"Maintenance": "🔧",
			"Setup": "🛠",
		};
		return map[status] || "•";
	}

	readinessClass(status) {
		const map = {
			"Ready": "green",
			"Partially Ready": "blue",
			"Shortage": "red",
			"Unknown": "amber",
			"Not Applicable": "gray",
		};
		return map[status] || "gray";
	}

	readinessIcon(status) {
		const map = {
			"Ready": "✓",
			"Partially Ready": "◐",
			"Shortage": "⚠",
			"Unknown": "?",
			"Not Applicable": "—",
		};
		return map[status] || "•";
	}

	stageClass(stage) {
		const map = {
			"Material Staging": "amber",
			"In Production": "blue",
			"Manufacture Receipt": "purple",
			"Completed": "green",
			"Draft": "gray",
			"Cancelled": "red",
		};
		return map[stage] || "subtle";
	}

	opStatusClass(status) {
		const map = {
			"Completed": "completed",
			"In Progress": "in-progress",
			"Waiting on Predecessor": "waiting",
			"Ready to Start": "ready",
			"Cancelled": "cancelled",
		};
		return map[status] || "ready";
	}

	opStatusIcon(status) {
		const map = {
			"Completed": "✓",
			"In Progress": "⚙",
			"Waiting on Predecessor": "⏳",
			"Ready to Start": "•",
			"Cancelled": "✕",
		};
		return map[status] || "•";
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
        <p class="sd-sub-card-mat">Material with Suppliers: <b>${s.material_with_suppliers === undefined ? __("Restricted") : this.formatCompact(s.material_with_suppliers, sym)}</b></p>
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
			"[data-factory-overview-panel]",
			"[data-production-pipeline-panel]",
			"[data-material-readiness-panel]",
			"[data-workstation-downtime-panel]",
			"[data-quality-overview-panel]",
			"[data-rework-overview-panel]",
			"[data-subcontracting-overview-panel]",
			"[data-production-exceptions-panel]",
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
			"[data-factory-overview-panel]",
			"[data-production-pipeline-panel]",
			"[data-material-readiness-panel]",
			"[data-workstation-downtime-panel]",
			"[data-quality-overview-panel]",
			"[data-rework-overview-panel]",
			"[data-subcontracting-overview-panel]",
			"[data-production-exceptions-panel]",
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
		const request = (this.subRequest = (this.subRequest || 0) + 1);
		try {
			const res = await frappe.call({
				method: "sarathi_visibility.api.subcontracting.get_subcontracting_dashboard",
				args: { filters: JSON.stringify(this.subFilters) },
				silent: true,
			});
			if (request !== this.subRequest || this.view !== "subcontracting") return;
			this.subData = res.message;
			this.lastSubSuccessfulRefresh = new Date().toISOString();
			this.renderSubcontractingDetailView();
		} catch (err) {
			if (request !== this.subRequest || this.view !== "subcontracting") return;
			console.error("Subcontracting load error:", err);
			if (this.subData && this.lastSubSuccessfulRefresh) {
				const timeStr = window.frappe?.sarathiUI?.formatTimestamp ? frappe.sarathiUI.formatTimestamp(this.lastSubSuccessfulRefresh) : frappe.datetime.str_to_user(this.lastSubSuccessfulRefresh);
				const existingBanner = viewEl.querySelector(".sui-stale-banner");
				if (!existingBanner) {
					const banner = document.createElement("div");
					banner.className = "sui-stale-banner";
					banner.setAttribute("role", "alert");
					banner.style.margin = "12px 16px";
					banner.innerHTML = `<p style="margin:0;">Subcontracting refresh failed. Showing data from last update (${timeStr}).</p><button type="button" class="sd-button sd-primary" data-action="refresh-subcontracting" style="margin-left:auto;">Retry</button>`;
					viewEl.prepend(banner);
				}
			} else {
				viewEl.innerHTML = `
					<div class="sd-sub-error" role="alert">
						<h3>Unable to load Subcontracting Control Tower</h3>
						<p>Please ensure you have read permissions for Subcontracting Order and Stock Entry.</p>
						<button class="sd-button" data-action="close-subcontracting">← Back to Dashboard</button>
						<button class="sd-button sd-primary" data-action="refresh-subcontracting">↻ Try Again</button>
					</div>
				`;
			}
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
          <strong>${k.material_value_at_subcontractors === undefined ? __("Restricted") : this.formatCompact(k.material_value_at_subcontractors, sym)}</strong>
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
                    <td>${sa.material_value === undefined ? __("Restricted") : this.formatCompact(sa.material_value, sym)}</td>
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
                <td><strong>${m.material_value === undefined ? __("Restricted") : this.formatCompact(m.material_value, sym)}</strong></td>
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
		if (this.data?.accounting_summary?.restricted) {
			container.innerHTML = '<div class="sd-empty">Financial information is restricted by your permissions.</div>';
			return;
		}
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
			"[data-factory-overview-panel]",
			"[data-production-pipeline-panel]",
			"[data-material-readiness-panel]",
			"[data-workstation-downtime-panel]",
			"[data-quality-overview-panel]",
			"[data-rework-overview-panel]",
			"[data-subcontracting-overview-panel]",
			"[data-production-exceptions-panel]",
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
			"[data-factory-overview-panel]",
			"[data-production-pipeline-panel]",
			"[data-material-readiness-panel]",
			"[data-workstation-downtime-panel]",
			"[data-quality-overview-panel]",
			"[data-rework-overview-panel]",
			"[data-subcontracting-overview-panel]",
			"[data-production-exceptions-panel]",
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
			this.lastAccSuccessfulRefresh = new Date().toISOString();
			const staleBanner = viewEl.querySelector(".sui-stale-banner");
			if (staleBanner) staleBanner.remove();
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
				if (this.accData && this.lastAccSuccessfulRefresh) {
					const timeStr = window.frappe?.sarathiUI?.formatTimestamp ? frappe.sarathiUI.formatTimestamp(this.lastAccSuccessfulRefresh) : frappe.datetime.str_to_user(this.lastAccSuccessfulRefresh);
					const existingBanner = viewEl.querySelector(".sui-stale-banner");
					if (!existingBanner) {
						const banner = document.createElement("div");
						banner.className = "sui-stale-banner";
						banner.setAttribute("role", "alert");
						banner.style.margin = "12px 16px";
						banner.innerHTML = `<p style="margin:0;">Accounting refresh failed. Showing data from last update (${timeStr}).</p><button type="button" class="sd-button sd-primary" data-action="refresh-accounting" style="margin-left:auto;">Retry</button>`;
						viewEl.prepend(banner);
					}
				} else {
					viewEl.innerHTML = `
						<div class="sd-sub-error" role="alert">
							<h3>Accounting Data Unavailable</h3>
							<p>Could not fetch accounting intelligence records. Check permissions for General Ledger and accounts.</p>
							<button class="sd-button" data-action="refresh-accounting">Retry</button>
							<button class="sd-button" data-action="close-accounting">← Return to Dashboard</button>
						</div>
					`;
				}
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

	initAiAssistant() {
        frappe.SarathiDashboardAssistant.attach(this);
    }
    toggleAiChat(open) {
        frappe.sarathiDashboardAssistant?.toggleAiChat(open);
    }
};
