/* Sarathi Visibility & Owner - Global Desk & Form Enhancements */

// 1. Desk Icons Management (Guaranteed delivery for Owner & Production Manager)
(function () {
	const OWNER_ICON = {
		name: "Owner",
		label: "Owner",
		link: "/desk/sarathiownertower",
		link_type: "External",
		icon_type: "App",
		app: "sarathi_owner",
		logo_url: "/assets/sarathi_owner/icons/owner.png",
		hidden: 0,
		standard: 1,
		restrict_removal: 1,
		idx: 0,
	};

	const PM_ICON = {
		name: "Production Manager",
		label: "Production Manager",
		link: "/desk/sarathicontroltower",
		link_type: "External",
		icon_type: "App",
		app: "sarathi_visibility",
		logo_url: "/assets/sarathi_visibility/icons/production_manager.png",
		hidden: 0,
		standard: 1,
		restrict_removal: 1,
		idx: 1,
	};

	function purgeStaleDesktopCache() {
		try {
			const user = window.frappe?.session?.user;
			if (user) {
				const cacheKey = `${user}:desktop`;
				const cached = localStorage.getItem(cacheKey);
				if (cached) {
					if (!cached.includes("Owner") || !cached.includes("Production Manager")) {
						localStorage.removeItem(cacheKey);
					}
				}
			}
		} catch (error) {
			void error;
		}
	}

	function ensureBootIcons() {
		if (Array.isArray(window.frappe?.boot?.desktop_icons)) {
			const bootIcons = window.frappe.boot.desktop_icons;
			if (!bootIcons.some((i) => i && (i.name === "Owner" || i.label === "Owner"))) {
				bootIcons.push(OWNER_ICON);
			}
			if (
				!bootIcons.some(
					(i) => i && (i.name === "Production Manager" || i.label === "Production Manager")
				)
			) {
				bootIcons.push(PM_ICON);
			}
		}
		if (Array.isArray(window.frappe?.desktop_icons)) {
			const dIcons = window.frappe.desktop_icons;
			if (!dIcons.some((i) => i && (i.name === "Owner" || i.label === "Owner"))) {
				dIcons.push(OWNER_ICON);
			}
			if (
				!dIcons.some(
					(i) => i && (i.name === "Production Manager" || i.label === "Production Manager")
				)
			) {
				dIcons.push(PM_ICON);
			}
		}
	}

	function ensureDomIcons() {
		const $container = $(".desktop-container .icons").first();
		if (!$container.length) return;

		if (!$container.find('.desktop-icon[data-id="Owner"]').length) {
			const ownerHtml = `
				<a class="desktop-icon sarathi-desk-icon" data-id="Owner" href="/desk/sarathiownertower" style="text-decoration:none">
					<div class="icon-container" style="padding:0;background:transparent;">
						<img class="app-icon" src="/assets/sarathi_owner/icons/owner.png" alt="Owner" style="width:54px;height:54px;object-fit:contain;border-radius:14px;" />
					</div>
					<div class="icon-caption">
						<div class="icon-title" data-toggle="tooltip" data-original-title="Owner">Owner</div>
					</div>
				</a>`;
			$container.append(ownerHtml);
		}

		if (!$container.find('.desktop-icon[data-id="Production Manager"]').length) {
			const pmHtml = `
				<a class="desktop-icon sarathi-desk-icon" data-id="Production Manager" href="/desk/sarathicontroltower" style="text-decoration:none">
					<div class="icon-container" style="padding:0;background:transparent;">
						<img class="app-icon" src="/assets/sarathi_visibility/icons/production_manager.png" alt="Production Manager" style="width:54px;height:54px;object-fit:contain;border-radius:14px;" />
					</div>
					<div class="icon-caption">
						<div class="icon-title" data-toggle="tooltip" data-original-title="Production Manager">Production Manager</div>
					</div>
				</a>`;
			$container.append(pmHtml);
		}
	}

	function runDesktopCheck() {
		purgeStaleDesktopCache();
		ensureBootIcons();
		ensureDomIcons();
	}

	// Route bindings
	$(document).on("click", '.desktop-icon[data-id="Owner"], .desktop-icon[data-id="owner"]', function (e) {
		e.preventDefault();
		if (window.frappe?.set_route) {
			window.frappe.set_route("sarathiownertower");
		} else {
			window.location.href = "/desk/sarathiownertower";
		}
	});

	$(document).on(
		"click",
		'.desktop-icon[data-id="Production Manager"], .desktop-icon[data-id="production-manager"], .desktop-icon[data-id="production_manager"]',
		function (e) {
			e.preventDefault();
			if (window.frappe?.set_route) {
				window.frappe.set_route("sarathicontroltower");
			} else {
				window.location.href = "/desk/sarathicontroltower";
			}
		}
	);

	function enforceSidebarState() {
		const route = window.frappe?.get_route ? window.frappe.get_route() : [];
		const current = route[0] || "";
		if (current === "sarathiownertower" || current === "sarathicontroltower") {
			window.frappe?.app?.sidebar?.toggle?.(true);
			window.frappe?.app?.sidebar?.hide?.();
			$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();
		}
	}

	runDesktopCheck();
	$(document).ready(runDesktopCheck);
	$(document).ready(enforceSidebarState);
	$(document).on("desktop_screen", runDesktopCheck);
	$(document).on("page-change", runDesktopCheck);
	$(document).on("page-change", enforceSidebarState);
	if (window.frappe?.router?.on) {
		window.frappe.router.on("change", enforceSidebarState);
	}
	setTimeout(runDesktopCheck, 50);
	setTimeout(runDesktopCheck, 150);
	setTimeout(runDesktopCheck, 350);
	setTimeout(runDesktopCheck, 800);
	setTimeout(runDesktopCheck, 1500);
	setTimeout(enforceSidebarState, 100);
	setTimeout(enforceSidebarState, 500);
})();

// 2. Job Card List Filter Handler
(function () {
	function checkJobCardListFilter() {
		const params = new URLSearchParams(window.location.search || "");
		const wo = params.get("work_order") || window.frappe?.route_options?.work_order;
		if (!wo) {
			return;
		}

		const route = window.frappe?.get_route ? window.frappe.get_route() : [];
		if (
			route &&
			(route[0] === "List" || route[0] === "list") &&
			(route[1] === "Job Card" || route[1] === "job-card")
		) {
			if (window.frappe) {
				window.frappe.route_options = window.frappe.route_options || {};
				window.frappe.route_options.work_order = wo;
			}

			const applyFilterToList = () => {
				if (
					window.cur_list &&
					(window.cur_list.doctype === "Job Card" || window.cur_list.doctype === "job-card")
				) {
					const filterArea = window.cur_list.filter_area;
					if (filterArea) {
						const currentFilters = filterArea.get() || [];
						const hasWoFilter = currentFilters.some((f) => f[1] === "work_order" && f[3] === wo);
						if (!hasWoFilter) {
							filterArea.remove("work_order");
							filterArea.add([["Job Card", "work_order", "=", wo]]);
						}
					}
				}
			};

			setTimeout(applyFilterToList, 50);
			setTimeout(applyFilterToList, 300);
			setTimeout(applyFilterToList, 800);
		}
	}

	$(document).on("page-change", checkJobCardListFilter);
	if (window.frappe?.router?.on) {
		window.frappe.router.on("change", checkJobCardListFilter);
	}
	$(document).ready(checkJobCardListFilter);
})();

// 3. Form Handlers & Prefill
(function () {
	const PREFIX = "sarathi_prefill_";
	const PENDING_PROJECT_KEY = "sarathi_pending_project_after_company";
	let formsRegistered = false;

	function routeSlug(doctype) {
		return String(doctype || "")
			.toLowerCase()
			.replaceAll(" ", "-");
	}

	function storageKey(doctype) {
		return `${PREFIX}${routeSlug(doctype)}`;
	}

	function isNewDeskRoute(doctype) {
		const slug = routeSlug(doctype);
		const path = window.location.pathname || "";
		return path.includes(`/app/${slug}/new`) || path.includes(`/desk/${slug}/new`);
	}

	function readQueryOptions(doctype, fields) {
		const params = new URLSearchParams(window.location.search || "");
		if (!isNewDeskRoute(doctype) || params.get("sarathi_prefill") !== "1") {
			return {};
		}

		if (!fields || fields[0] === "*") {
			const options = {};
			params.forEach((value, key) => {
				if (key !== "sarathi_prefill" && value) {
					options[key] = value;
				}
			});
			return options;
		}

		return fields.reduce((options, fieldname) => {
			const value = params.get(fieldname);
			if (value) {
				options[fieldname] = value;
			}
			return options;
		}, {});
	}

	function readStorageOptions(doctype) {
		try {
			return JSON.parse(sessionStorage.getItem(storageKey(doctype)) || "{}") || {};
		} catch (error) {
			return {};
		}
	}

	function readOptions(doctype, fields) {
		return {
			...readStorageOptions(doctype),
			...readQueryOptions(doctype, fields),
		};
	}

	function openDeskForm(doctype, options) {
		const clean = Object.entries(options || {}).reduce((result, [key, val]) => {
			const text = String(val || "").trim();
			if (text) {
				result[key] = text;
			}
			return result;
		}, {});
		const slug = routeSlug(doctype);
		const params = new URLSearchParams({ sarathi_prefill: "1", ...clean });
		sessionStorage.setItem(storageKey(doctype), JSON.stringify(clean));
		window.location.href = `/desk/${slug}/new-${slug}?${params.toString()}`;
	}

	function applyOptions(frm, fields = ["*"]) {
		if (!frm || !frm.is_new() || frm.__sarathi_prefill_applied) {
			return;
		}

		const options = readOptions(frm.doctype, fields);
		const entries = Object.entries(options).filter(
			([fieldname, value]) => value && frm.fields_dict[fieldname]
		);
		if (!entries.length) {
			return;
		}

		frm.__sarathi_prefill_applied = true;
		entries.forEach(([fieldname, value]) => {
			frm.set_value(fieldname, value);
		});
		sessionStorage.removeItem(storageKey(frm.doctype));
	}

	function continueToPendingProject(frm) {
		let pending = null;
		try {
			pending = JSON.parse(sessionStorage.getItem(PENDING_PROJECT_KEY) || "{}") || {};
		} catch (error) {
			pending = {};
		}

		if (!pending.project_name) {
			return;
		}

		sessionStorage.removeItem(PENDING_PROJECT_KEY);
		pending.company = frm.doc.name || frm.doc.company_name || pending.company;
		frappe.show_alert({
			message: "Opening ERPNext Project form with your saved organization.",
			indicator: "green",
		});
		setTimeout(() => openDeskForm("Project", pending), 400);
	}

	function initFormPrefill() {
		if (!window.frappe?.ui?.form?.on || formsRegistered) {
			return;
		}
		formsRegistered = true;

		function fixProjectSalesOrderRoutes(frm) {
			const so = frm.get_docfield("sales_order");
			if (so) {
				so.get_route_options_for_new_doc = () => {
					if (frm.is_new()) return {};
					return {
						customer: frm.doc.customer,
						company: frm.doc.company,
						project: frm.doc.name,
						project_name: frm.doc.name,
					};
				};
			}
		}

		frappe.ui.form.on("Project", {
			onload(frm) {
				applyOptions(frm);
				fixProjectSalesOrderRoutes(frm);
			},
			refresh(frm) {
				applyOptions(frm);
				fixProjectSalesOrderRoutes(frm);
			},
			setup(frm) {
				frm.set_query("custom_sarathi_bom", () => ({
					filters: {
						custom_sarathi_project: frm.doc.name,
						company: frm.doc.company,
						docstatus: 1,
						is_active: 1,
					},
				}));
			},
		});

		frappe.ui.form.on("Sales Order", {
			onload(frm) {
				applyOptions(frm);
				if (frm.is_new()) {
					const routeOpts = frappe.route_options || {};
					const project = routeOpts.project || routeOpts.project_name;
					if (project && !frm.doc.project) {
						frm.set_value("project", project);
					}
					if (routeOpts.customer && !frm.doc.customer) {
						frm.set_value("customer", routeOpts.customer);
					}
					if (routeOpts.company && !frm.doc.company) {
						frm.set_value("company", routeOpts.company);
					}
				}
			},
			refresh(frm) {
				applyOptions(frm);
				if (frm.is_new()) {
					const routeOpts = frappe.route_options || {};
					const project = routeOpts.project || routeOpts.project_name;
					if (project && !frm.doc.project) {
						frm.set_value("project", project);
					}
				}
			},
		});

		frappe.ui.form.on("Company", {
			onload(frm) {
				applyOptions(frm);
			},
			refresh(frm) {
				applyOptions(frm);
			},
			after_save(frm) {
				continueToPendingProject(frm);
			},
		});

		frappe.ui.form.on("BOM", {
			onload(frm) {
				applyOptions(frm, [
					"custom_sarathi_project",
					"project",
					"custom_project",
					"sarathi_project",
					"project_name",
					"company",
					"item",
				]);
			},
			refresh(frm) {
				applyOptions(frm, [
					"custom_sarathi_project",
					"project",
					"custom_project",
					"sarathi_project",
					"project_name",
					"company",
					"item",
				]);
			},
		});

		frappe.ui.form.on("Customer", {
			onload(frm) {
				let pending;
				try {
					pending = JSON.parse(sessionStorage.getItem("sarathi_new_customer_company") || "null");
				} catch (e) {
					pending = null;
				}
				if (frm.is_new() && pending?.docname === frm.doc.name) {
					frm.__sarathi_company = pending.company;
					sessionStorage.removeItem("sarathi_new_customer_company");
				}
			},
			async after_save(frm) {
				if (!frm.__sarathi_company) return;
				await frappe.call({
					method: "sarathi_visibility.api.dashboard.associate_customer",
					args: { company: frm.__sarathi_company, customer: frm.doc.name },
				});
				sessionStorage.removeItem("sarathi_new_customer_company");
				frm.__sarathi_company = null;
				frappe.show_alert({
					message: "Customer linked to the selected organization.",
					indicator: "green",
				});
			},
		});

		frappe.ui.form.on("Material Request", {
			onload(frm) {
				if (!frm.is_new()) return;
				let context;
				try {
					context = JSON.parse(
						sessionStorage.getItem("sarathi_material_request_project") || "null"
					);
				} catch (_) {
					return;
				}
				if (context?.docname !== frm.doc.name) return;
				frm.__sarathi_project = context.project;
				sessionStorage.removeItem("sarathi_material_request_project");
			},
			before_save(frm) {
				if (frm.__sarathi_project)
					(frm.doc.items || []).forEach((r) => {
						if (!r.project) r.project = frm.__sarathi_project;
					});
			},
		});

		frappe.ui.form.on("Material Request Item", {
			items_add(frm, cdt, cdn) {
				if (frm.__sarathi_project) frappe.model.set_value(cdt, cdn, "project", frm.__sarathi_project);
			},
		});

		[
			"Sales Order",
			"Purchase Order",
			"Purchase Receipt",
			"Delivery Note",
			"Sales Invoice",
			"Stock Entry",
		].forEach((doctype) => {
			frappe.ui.form.on(doctype, {
				project(frm) {
					if (frm.doc.project && frm.doc.items) {
						frm.doc.items.forEach((row) => {
							if (!row.project) {
								frappe.model.set_value(row.doctype, row.name, "project", frm.doc.project);
							}
						});
					}
				},
				before_save(frm) {
					if (frm.doc.project && frm.doc.items) {
						frm.doc.items.forEach((row) => {
							if (!row.project) {
								frappe.model.set_value(row.doctype, row.name, "project", frm.doc.project);
							}
						});
					}
				},
			});
		});

		[
			"Sales Order Item",
			"Purchase Order Item",
			"Purchase Receipt Item",
			"Delivery Note Item",
			"Sales Invoice Item",
			"Stock Entry Detail",
		].forEach((childtype) => {
			frappe.ui.form.on(childtype, {
				items_add(frm, cdt, cdn) {
					if (frm?.doc?.project) {
						frappe.model.set_value(cdt, cdn, "project", frm.doc.project);
					}
				},
			});
		});
	}

	initFormPrefill();
	$(document).ready(initFormPrefill);
	$(document).on("page-change", initFormPrefill);
})();
