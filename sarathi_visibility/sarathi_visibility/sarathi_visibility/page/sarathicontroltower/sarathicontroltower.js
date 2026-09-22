frappe.pages['sarathicontroltower'].on_page_load = function(wrapper) {
  const ver = frappe.boot?.versions?.sarathi_visibility || Date.now();
  frappe.require([
    `/assets/sarathi_visibility/css/sarathi_dashboard.css?v=${ver}`,
    `/assets/sarathi_visibility/js/sarathi_dashboard.js?v=${ver}`
  ], () => {
    wrapper.sarathi_dashboard = new frappe.SarathiIndustrialDashboard(wrapper);
  });
};
frappe.pages['sarathicontroltower'].on_page_show = function(wrapper) { wrapper.sarathi_dashboard?.show(); };
frappe.pages['sarathicontroltower'].on_page_hide = function(wrapper) { wrapper.sarathi_dashboard?.hide(); };
