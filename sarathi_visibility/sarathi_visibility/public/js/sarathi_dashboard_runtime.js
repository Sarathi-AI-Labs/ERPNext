// Dashboard-scoped cache eviction and deduplicated initialization.
(() => {
 if (frappe.sarathiDashboardRuntime) return;
 const assets = new Map();
 const routes = ["sarathiownertower", "sarathicontroltower"];
 const runtime = frappe.sarathiDashboardRuntime = {
  active: null,
  evict() {
   try {
    for (const route of routes) {
     for (const prefix of ["_page:", "page:", "route:"]) localStorage.removeItem(prefix + route);
    }
   } catch (_) { /* Restricted storage must not break navigation. */ }
  },
  load(paths) {
   return Promise.all(paths.map(path => {
    if (!assets.has(path)) {
     const pending = fetch(path, {cache: "no-cache", credentials: "same-origin"})
      .then(response => { if (!response.ok) throw new Error(`Cannot load ${path}`); return response.text(); })
      .then(source => {
       const node = document.createElement(path.endsWith(".css") ? "style" : "script");
       node.dataset.sarathiAsset = path;
       node.textContent = source;
       document.head.appendChild(node);
      }).catch(error => { assets.delete(path); throw error; });
     assets.set(path, pending);
    }
    return assets.get(path);
   }));
  },
  activate(host) {
   this.evict();
   if (this.active && this.active !== host) {
    this.active.hide();
    this.deactivate(this.active);
   }
   this.active = host;
   frappe.SarathiDashboardAssistant.attach(host);
  },
  deactivate(host) {
   if (this.active !== host) return;
   this.active = null;
   clearTimeout(this.activityTimer);
   frappe.SarathiDashboardAssistant.detach(host);
  },
  activity(event) {
   if (!this.active) return;
   this.evict();
   // Existing filters/navigation own their refresh; typing must retain focus and values.
   if (event.type !== "click" || event.target.closest(".sd-ai-chat-window, .modal, input, select, textarea")) return;
   clearTimeout(this.activityTimer);
   const host = this.active;
   this.activityTimer = setTimeout(() => {
    if (this.active !== host || document.hidden || document.querySelector(".modal.show")) return;
    if (host.smoothRefresh) host.smoothRefresh();
    else if (host.view === "accounting") host.loadAccountingData(true);
    else if (host.view === "subcontracting") host.loadSubcontractingData(true);
    else host.load(true);
   }, 800);
  }
 };
 frappe.router.on("change", () => {
  runtime.evict();
  const host = runtime.active;
  if (host && host.sarathiRoute !== frappe.get_route()[0]) {
   host.hide();
   runtime.deactivate(host);
  }
 });
 for (const type of ["click", "change", "input"]) document.addEventListener(type, event => runtime.activity(event), true);
})();
