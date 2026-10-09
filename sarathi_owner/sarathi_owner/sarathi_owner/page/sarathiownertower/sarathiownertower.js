// Clear any stale cached page payload from older versions
if (typeof localStorage !== "undefined") {
	try {
		localStorage.removeItem("_page:sarathiownertower");
	} catch (e) {
		// Local storage can be unavailable in restricted browser contexts.
	}
}

frappe.pages["sarathiownertower"].on_page_load = function (wrapper) {
	wrapper.disable_scroll_to_top = true;
	if (wrapper.page) {
		wrapper.page.disable_scroll_to_top = true;
		wrapper.page.hide_sidebar = true;
	}
	frappe.app?.sidebar?.toggle?.(true);
	frappe.app?.sidebar?.hide?.();
	$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();

	frappe.require(
		[
			"/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
			"/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
		],
		() => {
			wrapper.disable_scroll_to_top = true;
			if (wrapper.page) {
				wrapper.page.disable_scroll_to_top = true;
				wrapper.page.hide_sidebar = true;
			}
			frappe.app?.sidebar?.toggle?.(true);
			frappe.app?.sidebar?.hide?.();
			$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();
			if (!wrapper.sarathi_owner_dashboard) {
				wrapper.sarathi_owner_dashboard = new frappe.SarathiOwnerDashboard(wrapper);
			}
		}
	);
};

frappe.pages["sarathiownertower"].on_page_show = function (wrapper) {
	if (wrapper.page) wrapper.page.hide_sidebar = true;
	frappe.app?.sidebar?.toggle?.(true);
	frappe.app?.sidebar?.hide?.();
	$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();

	if (wrapper.sarathi_owner_dashboard) {
		wrapper.sarathi_owner_dashboard.show?.();
	} else {
		frappe.require(
			[
				"/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
				"/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
			],
			() => {
				if (wrapper.page) wrapper.page.hide_sidebar = true;
				frappe.app?.sidebar?.toggle?.(true);
				frappe.app?.sidebar?.hide?.();
				$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();
				if (!wrapper.sarathi_owner_dashboard) {
					wrapper.sarathi_owner_dashboard = new frappe.SarathiOwnerDashboard(wrapper);
				}
				wrapper.sarathi_owner_dashboard.show?.();
			}
		);
	}
};

frappe.pages["sarathiownertower"].on_page_hide = function (wrapper) {
	wrapper.sarathi_owner_dashboard?.hide?.();
};
