(function () {
	const PREFIX = "sarathi_prefill_";
	const PENDING_PROJECT_KEY = "sarathi_pending_project_after_company";

	if (!window.frappe?.ui?.form) {
		return;
	}

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

	frappe.ui.form.on("Project", {
		onload(frm) {
			applyOptions(frm);
		},
		refresh(frm) {
			applyOptions(frm);
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

	frappe.ui.form.on("Project", {
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

frappe.ui.form.on("Material Request", {
	onload(frm) {
		if (!frm.is_new()) return;
		let context;
		try {
			context = JSON.parse(sessionStorage.getItem("sarathi_material_request_project") || "null");
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
