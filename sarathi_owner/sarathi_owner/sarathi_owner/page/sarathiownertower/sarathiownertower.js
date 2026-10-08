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
	if (wrapper.page) wrapper.page.disable_scroll_to_top = true;

	frappe.require(
		[
			"/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
			"/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
		],
		() => {
			wrapper.disable_scroll_to_top = true;
			if (wrapper.page) wrapper.page.disable_scroll_to_top = true;
			if (!wrapper.sarathi_owner_dashboard) {
				wrapper.sarathi_owner_dashboard = new frappe.SarathiOwnerDashboard(wrapper);
			}
		}
	);
};

frappe.pages["sarathiownertower"].on_page_show = function (wrapper) {
	if (wrapper.sarathi_owner_dashboard) {
		wrapper.sarathi_owner_dashboard.show?.();
	} else {
		frappe.require(
			[
				"/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
				"/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
			],
			() => {
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
