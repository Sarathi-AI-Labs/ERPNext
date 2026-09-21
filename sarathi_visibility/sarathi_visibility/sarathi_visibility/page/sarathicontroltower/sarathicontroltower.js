frappe.pages['sarathicontroltower'].on_page_load = function(wrapper) {
  frappe.require(['/assets/sarathi_visibility/css/sarathi_dashboard.css', '/assets/sarathi_visibility/js/sarathi_dashboard.js'], () => {
    wrapper.sarathi_dashboard = new frappe.SarathiIndustrialDashboard(wrapper);
  });
};
frappe.pages['sarathicontroltower'].on_page_show = function(wrapper) { wrapper.sarathi_dashboard?.show(); };
frappe.pages['sarathicontroltower'].on_page_hide = function(wrapper) { wrapper.sarathi_dashboard?.hide(); };
