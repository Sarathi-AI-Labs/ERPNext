frappe.pages["sarathicontroltower"].on_page_load = function (wrapper) {
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
			"/assets/sarathi_visibility/css/sarathi_dashboard.css",
			"/assets/sarathi_visibility/js/sarathi_dashboard.js",
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
			wrapper.sarathi_dashboard = new frappe.SarathiIndustrialDashboard(wrapper);
		}
	);
};
frappe.pages["sarathicontroltower"].on_page_show = function (wrapper) {
	if (wrapper.page) wrapper.page.hide_sidebar = true;
	frappe.app?.sidebar?.toggle?.(true);
	frappe.app?.sidebar?.hide?.();
	$(".layout-side-section, .desk-sidebar, .body-sidebar").addClass("hidden").hide();
	wrapper.sarathi_dashboard?.show();
};
frappe.pages["sarathicontroltower"].on_page_hide = function (wrapper) {
	wrapper.sarathi_dashboard?.hide();
};
