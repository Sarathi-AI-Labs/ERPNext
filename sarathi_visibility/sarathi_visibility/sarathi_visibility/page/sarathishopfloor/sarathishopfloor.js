// A shared promise prevents on_page_load/on_page_show from creating duplicate instances.
(() => {
	const route = "sarathishopfloor";
	const initialize = wrapper => {
		if (wrapper.sarathiShopfloorInitializing) return wrapper.sarathiShopfloorInitializing;
		const pending = (async () => {
			await frappe.require("/assets/sarathi_visibility/js/sarathi_dashboard_runtime.js");
			const runtime = frappe.sarathiDashboardRuntime;
			runtime.evict();
			await runtime.load([
				"/assets/sarathi_visibility/css/sarathi_ui.css",
				"/assets/sarathi_visibility/js/sarathi_ui.js",
			]);
			await runtime.load([
				"/assets/sarathi_visibility/css/sarathi_shopfloor.css",
				"/assets/sarathi_visibility/js/sarathi_shopfloor.js",
			]);
			if (frappe.get_route()[0] !== route) return;
			wrapper.disable_scroll_to_top = true;
			if (!wrapper.sarathi_shopfloor) {
				wrapper.sarathi_shopfloor = new frappe.SarathiShopFloorWorkboard(wrapper);
			}
			wrapper.sarathi_shopfloor.sarathiRoute = route;
			wrapper.sarathi_shopfloor.show();
			wrapper.page.hide_sidebar = true;
			wrapper.page.disable_scroll_to_top = true;
			frappe.app?.sidebar?.toggle?.(true);
			runtime.activate(wrapper.sarathi_shopfloor);
		})();
		wrapper.sarathiShopfloorInitializing = pending;
		pending.catch(error => {
			console.error("Shop-Floor Workboard load error:", error);
			frappe.msgprint(__("Shop-Floor Workboard could not load. Please retry or check your connection."));
		}).finally(() => { wrapper.sarathiShopfloorInitializing = null; });
		return pending;
	};
	frappe.pages[route].on_page_load = initialize;
	frappe.pages[route].on_page_show = initialize;
	frappe.pages[route].on_page_hide = wrapper => {
		wrapper.sarathi_shopfloor?.hide();
		frappe.sarathiDashboardRuntime?.deactivate(wrapper.sarathi_shopfloor);
	};
})();
