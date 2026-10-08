/* Shared ERPNext module browser. Metadata is resolved by the server for this user. */
frappe.SarathiModuleBrowser = class {
	constructor(dashboard, kind) {
		this.dashboard = dashboard;
		this.kind = kind;
		this.root = dashboard.root;
		if (kind === "owner") {
			// Remove ERPNext modules from owner dashboard sidebar & layout per user request
			this.root?.querySelector("#sod-nav")?.querySelector(".scm-owner-nav")?.remove();
			this.root?.querySelector(".scm-launcher")?.remove();
			return;
		}
		this.catalog = null;
		this.busy = false;
		this.loadSequence = 0;
		this.launcher = document.createElement("div");
		this.launcher.className = "scm-launcher";
		this.root.querySelector(kind === "owner" ? ".sod-hero" : ".sd-hero").after(this.launcher);
		this.launcher.addEventListener("click", (e) => {
			if (e.target.closest("[data-scm-open]")) this.open();
		});
		this.onMetadata = () => this.refreshCatalog(true);
		this.onRecords = frappe.utils.debounce(() => this.refreshDetails(), 700);
		frappe.realtime.on("sarathi_catalog_changed", this.onMetadata);
		frappe.realtime.on("sarathi_records_changed", this.onRecords);
		this.timer = setInterval(() => {
			if (this.visible() && !document.hidden) {
				this.refreshCatalog();
				this.refreshDetails();
			}
		}, 15000);
		this.refreshCatalog(true);
	}
	esc(value) {
		return frappe.utils.escape_html(String(value ?? ""));
	}
	visible() {
		return !!this.root?.isConnected && $(this.root).is(":visible");
	}
	icon(name) {
		return frappe.utils.icon(/^[a-z0-9_-]+$/i.test(name || "") ? name : "folder-normal", "sm");
	}
	async refreshCatalog(force = false) {
		if (this.busy) return;
		this.busy = true;
		try {
			const r = await frappe.call({
				method: "sarathi_owner.api.module_catalog.get_catalog",
				args: { known_revision: force ? null : this.catalog?.revision },
				silent: true,
			});
			if (!r.message.unchanged) {
				const changed = !!this.catalog;
				this.catalog = r.message;
				this.renderLauncher();
				this.renderOwnerNav();
				if (this.dialog?.display) {
					this.renderModuleMenu();
					const current = this.catalog.modules.find((m) => m.id === this.moduleId);
					if (current) this.selectModule(current.id, false);
					else this.selectModule(this.catalog.modules[0]?.id);
					if (changed)
						this.setStatus(
							"ERPNext navigation updated. Select an entry to load its current fields."
						);
				}
			}
		} catch (e) {
			this.launcher.innerHTML =
				"<span>ERPNext modules could not be refreshed.</span><button data-scm-open>Retry</button>";
			this.setStatus("Module refresh failed. Check your connection and retry.");
		} finally {
			this.busy = false;
		}
	}
	renderLauncher() {
		this.launcher.innerHTML = `<div><strong>${this.icon("grid")} ERPNext modules</strong><small>${
			this.catalog.counts.modules
		} available workspaces · Installed ERPNext ${this.esc(
			this.catalog.versions.erpnext || ""
		)} · Synced with your permissions</small></div><button data-scm-open>Browse modules →</button>`;
	}
	renderOwnerNav() {
		const nav = this.root?.querySelector("#sod-nav");
		nav?.querySelector(".scm-owner-nav")?.remove();
	}
	openAction(action) {
		if (!this.catalog) return false;
		const url = new URL(action.route, location.origin);
		const key = decodeURIComponent(url.pathname)
			.replace(/^\/app\//, "/desk/")
			.replace(/\/new-[^/]+$/, "");
		for (const module of this.catalog.modules) {
			const entry = module.entries.find((e) => {
				if (!e.route) return false;
				const nativeUrl = new URL(e.route, location.origin);
				return (
					decodeURIComponent(nativeUrl.pathname) === key &&
					[...url.searchParams].every(([k, v]) => String(e.filters[k]) === v) &&
					[...nativeUrl.searchParams].every(
						([k, v]) => k === "ignore_prepared_report" || url.searchParams.get(k) === v
					)
				);
			});
			if (entry) {
				this.open(module.id).then(() => this.selectEntry(entry.id));
				return true;
			}
		}
		return false;
	}
	async open(moduleId) {
		if (!this.catalog) {
			await this.refreshCatalog(true);
			if (!this.catalog) return;
		}
		if (this.dialog?.display) {
			if (moduleId) this.selectModule(moduleId);
			return;
		}
		this.dialog = new frappe.ui.Dialog({
			title: "ERPNext modules",
			size: "extra-large",
			fields: [{ fieldtype: "HTML", fieldname: "browser" }],
		});
		this.dialog.$wrapper.addClass("scm-dialog");
		this.host = this.dialog.fields_dict.browser.$wrapper;
		this.host.html(
			`<div class="scm-shell"><aside class="scm-side"><label>Find a module<input type="search" data-scm-module-search placeholder="Search modules…"></label><nav data-scm-modules aria-label="ERPNext modules"></nav></aside><main class="scm-main"><div class="scm-module-head"><h3 data-scm-heading></h3><button type="button" data-scm-sync>Sync navigation</button></div><p class="scm-status" data-scm-status role="status"></p><div data-scm-entries></div><section data-scm-detail aria-live="polite"></section></main></div>`
		);
		this.host.on("click", "[data-scm-index]", (e) =>
			this.selectModule(this.catalog.modules[Number(e.currentTarget.dataset.scmIndex)].id)
		);
		this.host.on("click", "[data-scm-entry]", (e) => this.selectEntry(e.currentTarget.dataset.scmEntry));
		this.host.on("click", "[data-scm-sync]", () => this.refreshCatalog(true));
		this.host.on("input", "[data-scm-module-search]", (e) => {
			const value = e.target.value.toLowerCase();
			this.host.find("[data-scm-index]").each(function () {
				$(this).toggle($(this).text().toLowerCase().includes(value));
			});
		});
		this.dialog.onhide = () => {
			clearTimeout(this.searchTimer);
			this.loadSequence++;
			this.dialog.$wrapper.remove();
			this.dialog = null;
			this.frame = null;
		};
		this.dialog.show();
		this.renderModuleMenu();
		const key =
			moduleId ||
			(this.kind === "owner"
				? this.dashboard.pagesConfig[this.dashboard.currentPage]?.[3]?.replaceAll("_", " ")
				: "manufacturing");
		this.selectModule(this.catalog.modules.find((m) => m.id === key)?.id || this.catalog.modules[0]?.id);
	}
	renderModuleMenu() {
		let group = "";
		this.host.find("[data-scm-modules]").html(
			this.catalog.modules
				.map((m, i) => {
					const heading = group !== m.group ? `<h4>${this.esc(m.group)}</h4>` : "";
					group = m.group;
					return `${heading}<button type="button" data-scm-index="${i}" class="${
						m.id === this.moduleId ? "active" : ""
					}">${this.icon(m.icon)}<span>${this.esc(m.label)}</span><small>${
						m.entries.length
					}</small></button>`;
				})
				.join("")
		);
	}
	setStatus(text) {
		this.host?.find("[data-scm-status]").text(text);
	}
	selectModule(id, clear = true) {
		const module = this.catalog.modules.find((m) => m.id === id);
		if (!module) return;
		clearTimeout(this.searchTimer);
		this.moduleId = id;
		this.renderModuleMenu();
		this.host.find("[data-scm-heading]").text(module.label);
		let section = "";
		this.host.find("[data-scm-entries]").html(
			`<div class="scm-entry-grid">${module.entries
				.map((e) => {
					const heading = section !== e.section ? `<h4>${this.esc(e.section)}</h4>` : "";
					section = e.section;
					return `${heading}<button type="button" data-scm-entry="${this.esc(e.id)}">${this.icon(
						e.icon
					)}<span>${this.esc(e.label)}<small>${this.esc(e.kind)} · ${
						e.mode === "unsupported"
							? "Integration required"
							: e.mode === "native"
							? "Native tools"
							: "Live records & native tools"
					}</small></span></button>`;
				})
				.join("")}</div>`
		);
		if (clear || !module.entries.some((e) => e.id === this.entryId)) {
			this.entryId = null;
			this.frame = null;
			this.host.find("[data-scm-detail]").empty();
		}
		this.setStatus(
			"Navigation and fields come from your installed ERPNext. Native tools retain ERPNext permissions and validations."
		);
	}
	async selectEntry(id) {
		clearTimeout(this.searchTimer);
		this.entryId = id;
		this.name = null;
		this.start = 0;
		this.search = "";
		this.native = false;
		this.frame = null;
		await this.loadDetail();
	}
	async loadDetail(background = false) {
		if (!this.dialog || !this.entryId) return;
		const request = ++this.loadSequence;
		const moduleId = this.moduleId,
			entryId = this.entryId;
		this.detailBusy = true;
		const area = this.host.find("[data-scm-detail]");
		const scroll = area.find(".scm-table").scrollLeft();
		if (!background) area.html('<p class="scm-empty">Loading current ERPNext details…</p>');
		try {
			const r = await frappe.call({
				method: "sarathi_owner.api.module_catalog.get_entry",
				args: {
					module: moduleId,
					entry: entryId,
					name: this.name,
					start: this.start,
					search: this.search,
				},
				silent: true,
			});
			if (
				request !== this.loadSequence ||
				!this.dialog ||
				moduleId !== this.moduleId ||
				entryId !== this.entryId
			)
				return;
			this.detail = r.message;
			this.setStatus(`Updated ${r.message.updated_at} · ${r.message.entry.label}`);
			this.renderDetail();
			if (!background) area[0].scrollIntoView({ block: "start" });
			if (background) area.find(".scm-table").scrollLeft(scroll);
		} catch (e) {
			if (request === this.loadSequence)
				area.html(
					'<p class="scm-empty" role="alert">This entry could not be loaded. It may have changed or your access may have been removed. Sync navigation and retry.</p>'
				);
		} finally {
			if (request === this.loadSequence) this.detailBusy = false;
		}
	}
	renderDetail() {
		const data = this.detail,
			item = data.entry,
			area = this.host.find("[data-scm-detail]");
		let html = `<div class="scm-detail-head"><h4>${this.esc(item.label)}${
			data.name ? " · " + this.esc(data.name) : ""
		}</h4><div>${
			item.route ? '<button type="button" data-scm-native>Open native tools here</button>' : ""
		}${
			data.rows || data.values ? '<button type="button" data-scm-refresh>Refresh details</button>' : ""
		}${
			data.name && !item.is_single ? '<button type="button" data-scm-back>← Records</button>' : ""
		}</div></div>`;
		if (data.values) {
			html += '<div class="scm-fields">';
			for (const field of data.schema) {
				if (["Tab Break", "Section Break"].includes(field.fieldtype)) {
					if (field.label) html += `<h4>${this.esc(field.label)}</h4>`;
					continue;
				}
				if (!Object.prototype.hasOwnProperty.call(data.values, field.fieldname)) continue;
				html += `<div><small>${this.esc(field.label || field.fieldname)}</small><strong>${this.esc(
					this.value(data.values[field.fieldname], field.fieldtype)
				)}</strong></div>`;
			}
			html += "</div>";
			for (const table of data.tables || [])
				html += `<h4>${this.esc(table.label)} · ${table.total} rows</h4>${this.table(
					table.columns,
					table.rows
				)}${
					table.total > 100
						? "<p>Showing the first 100 rows. Open native tools for the complete table.</p>"
						: ""
				}`;
			html +=
				'<p class="scm-note">Read-only field preview. Native tools apply conditional layouts, workflows and editing rules.</p>';
		} else if (data.rows) {
			html += `<label class="scm-search">Find records<input type="search" data-scm-search value="${this.esc(
				this.search
			)}" placeholder="Search name or ID…"></label>${this.table(
				data.columns,
				data.rows,
				true
			)}<div class="scm-paging"><span>${
				data.rows.length
					? `${data.start + 1}–${data.start + data.rows.length}`
					: "No matching records"
			}</span><button data-scm-prev ${
				data.start ? "" : "disabled"
			}>← Previous</button><button data-scm-next ${
				data.has_more ? "" : "disabled"
			}>Next →</button></div>`;
		} else if (!item.route)
			html +=
				'<p class="scm-empty">This item needs a dedicated integration. No substitute records or actions are shown.</p>';
		else
			html +=
				'<p class="scm-note">Use the complete installed ERPNext screen below, including its current fields, report filters, workflows and actions.</p>';
		html += "<div data-scm-native-host></div>";
		area.html(html);
		area.off("click").off("input");
		area.on("click", "[data-scm-native]", () => this.openNative());
		area.on("click", "[data-scm-refresh]", () => this.loadDetail());
		area.on("click", "[data-scm-back]", () => {
			this.name = null;
			this.loadDetail();
		});
		area.on("click", "[data-scm-record]", (e) => {
			this.name = data.rows[Number(e.currentTarget.dataset.scmRecord)].name;
			this.loadDetail();
		});
		area.on("click", "[data-scm-prev]", () => {
			this.start = Math.max(0, this.start - 25);
			this.loadDetail();
		});
		area.on("click", "[data-scm-next]", () => {
			this.start += 25;
			this.loadDetail();
		});
		area.on("input", "[data-scm-search]", (e) => {
			this.search = e.target.value;
			clearTimeout(this.searchTimer);
			this.searchTimer = setTimeout(() => {
				this.start = 0;
				this.loadDetail();
			}, 400);
		});
		if (!data.rows && !data.values && item.route) this.openNative();
	}
	value(value, type) {
		if (value === null || value === undefined || value === "") return "—";
		if (type === "Check") return value ? "Yes" : "No";
		if (["Currency", "Float", "Int", "Percent"].includes(type) && Number.isFinite(Number(value)))
			return (
				new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(Number(value)) +
				(type === "Percent" ? "%" : "")
			);
		return value;
	}
	table(columns, rows, links = false) {
		return `<div class="scm-table"><table><thead><tr>${columns
			.map((c) => `<th>${this.esc(c.label)}</th>`)
			.join("")}</tr></thead><tbody>${rows
			.map(
				(r, i) =>
					`<tr>${columns
						.map(
							(c, j) =>
								`<td>${
									links && j === 0
										? `<button data-scm-record="${i}">${this.esc(
												r[c.fieldname]
										  )}</button>`
										: this.esc(this.value(r[c.fieldname], c.fieldtype))
								}</td>`
						)
						.join("")}</tr>`
			)
			.join("")}</tbody></table></div>`;
	}
	openNative() {
		const entry = this.detail.entry;
		let route = entry.route;
		if (!route) return;
		if (this.name && !entry.is_single) route = route.split("?")[0] + "/" + encodeURIComponent(this.name);
		if (!/^\/(desk|app)\//.test(route) || route.startsWith("//")) return;
		this.native = true;
		const host = this.host.find("[data-scm-native-host]");
		host.html(
			'<div class="scm-native-bar"><span>Native ERPNext · Changes here use your normal permissions</span><button type="button" data-scm-reload>Reload native screen</button></div>'
		);
		const frame = document.createElement("iframe");
		frame.className = "scm-native-frame";
		frame.title = entry.label;
		frame.src = route;
		host.append(frame);
		this.frame = frame;
		host.find("[data-scm-reload]").on("click", () => frame.contentWindow.location.reload());
		frame.addEventListener("load", () => {
			try {
				const style = frame.contentDocument.createElement("style");
				style.textContent =
					".body-sidebar-container,.navbar {display:none!important}.main-section {margin-left:0!important}";
				frame.contentDocument.head.append(style);
			} catch (e) {
				this.setStatus(
					"The native screen could not be embedded. This item requires a dedicated adapter."
				);
			}
		});
		host[0].scrollIntoView({ block: "nearest" });
	}
	refreshDetails() {
		if (!this.dialog || !this.entryId || this.detailBusy || document.hidden) return;
		if (this.native) {
			try {
				const win = this.frame?.contentWindow;
				if (
					!win?.frappe ||
					win.cur_frm?.is_dirty() ||
					["INPUT", "SELECT", "TEXTAREA"].includes(win.document.activeElement?.tagName)
				)
					return;
				if (win.frappe.query_report?.report_name) {
					win.frappe.query_report.ignore_prepared_report = true;
					win.frappe.query_report.refresh();
				} else if (win.cur_list?.refresh) win.cur_list.refresh();
			} catch (e) {
				/* Native controls retain their own error handling. */
			}
			return;
		}
		if (
			this.host[0].contains(document.activeElement) &&
			["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)
		)
			return;
		this.loadDetail(true);
	}
};
