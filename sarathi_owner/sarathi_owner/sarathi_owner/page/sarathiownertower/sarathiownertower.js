frappe.pages["sarathiownertower"].on_page_load = function (wrapper) {
  if (wrapper.sarathi_owner_dashboard || wrapper.sod_initializing) return;
  wrapper.sod_initializing = true;
  frappe.require(
    [
      "/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
      "/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
    ],
    () => {
      if (!wrapper.sarathi_owner_dashboard) {
        wrapper.sarathi_owner_dashboard = new frappe.SarathiOwnerDashboard(wrapper);
      }
      wrapper.sod_initializing = false;
    }
  );
};

frappe.pages["sarathiownertower"].on_page_show = function (wrapper) {
  document.documentElement.classList.add("sod-page-active");
  document.body.classList.add("sod-page-active");
  $(".main-section").scrollTop(0);
  window.scrollTo(0, 0);

  if (wrapper.sarathi_owner_dashboard) {
    wrapper.sarathi_owner_dashboard.show();
  } else if (!wrapper.sod_initializing) {
    wrapper.sod_initializing = true;
    frappe.require(
      [
        "/assets/sarathi_owner/css/sarathi_owner_dashboard.css",
        "/assets/sarathi_owner/js/sarathi_owner_dashboard.js",
      ],
      () => {
        if (!wrapper.sarathi_owner_dashboard) {
          wrapper.sarathi_owner_dashboard = new frappe.SarathiOwnerDashboard(wrapper);
        }
        wrapper.sod_initializing = false;
      }
    );
  }
};

frappe.pages["sarathiownertower"].on_page_hide = function (wrapper) {
  document.documentElement.classList.remove("sod-page-active");
  document.body.classList.remove("sod-page-active");
  wrapper.sarathi_owner_dashboard?.hide();
};
