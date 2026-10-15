// A shared promise prevents on_page_load/on_page_show from creating duplicate instances.
(() => {
 const route = "sarathicontroltower";
 const initialize = wrapper => {
  if (wrapper.sarathiInitializing) return wrapper.sarathiInitializing;
  const pending = (async () => {
   await frappe.require("/assets/sarathi_visibility/js/sarathi_dashboard_runtime.js");
   const runtime = frappe.sarathiDashboardRuntime;
   runtime.evict();
   await runtime.load([
    "/assets/sarathi_visibility/css/sarathi_ui.css",
    "/assets/sarathi_visibility/js/sarathi_ui.js",
   ]);
   await runtime.load([
    "/assets/sarathi_visibility/css/sarathi_dashboard_assistant.css",
    "/assets/sarathi_visibility/js/sarathi_dashboard_assistant.js",
    "/assets/sarathi_visibility/css/sarathi_dashboard.css",
    "/assets/sarathi_visibility/js/sarathi_dashboard.js",
   ]);
   if (frappe.get_route()[0] !== route) return;
   wrapper.disable_scroll_to_top = true;
   if (!wrapper.sarathi_dashboard) wrapper.sarathi_dashboard = new frappe.SarathiIndustrialDashboard(wrapper);
   wrapper.sarathi_dashboard.sarathiRoute = route;
   wrapper.sarathi_dashboard.show();
   wrapper.page.hide_sidebar = true;
   wrapper.page.disable_scroll_to_top = true;
   frappe.app?.sidebar?.toggle?.(true);
   runtime.activate(wrapper.sarathi_dashboard);
  })();
  wrapper.sarathiInitializing = pending;
  pending.catch(error => {
   console.error(error);
   frappe.msgprint(__("Dashboard could not load. Please retry or check your connection."));
  }).finally(() => { wrapper.sarathiInitializing = null; });
  return pending;
 };
 frappe.pages[route].on_page_load = initialize;
 frappe.pages[route].on_page_show = initialize;
 frappe.pages[route].on_page_hide = wrapper => {
  wrapper.sarathi_dashboard?.hide();
  frappe.sarathiDashboardRuntime?.deactivate(wrapper.sarathi_dashboard);
 };
})();
