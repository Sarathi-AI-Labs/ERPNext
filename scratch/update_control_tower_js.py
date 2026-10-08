with open('sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js', encoding='utf-8') as f:
    js_content = f.read()

# 1. Update this.tabs
old_tabs_block = '''    this.tabs = {
      overview: "Overview",
      sales: "Sales",
      production: "Production",
      engineering: "Engineering & BOM",
      materials: "Materials & Stock",
      procurement: "Procurement",
      quality: "Quality & Rework",
      fulfillment: "Delivery & Billing",
      reports: "Reports",
      integrations: "Integrations",
    };'''

new_tabs_block = '''    this.tabs = {
      overview: "Overview",
      subcontracting: "Subcontracting",
      accounting: "Accounting Intelligence",
      sales: "Sales & Orders",
      production: "Production & Plant",
      engineering: "Engineering & BOM",
      materials: "Materials & Stock",
      procurement: "Procurement",
      quality: "Quality & Rework",
      fulfillment: "Delivery & Billing",
      reports: "Reports Catalogue",
      integrations: "Integrations",
    };'''

if old_tabs_block in js_content:
    js_content = js_content.replace(old_tabs_block, new_tabs_block, 1)
    print("1. Replaced this.tabs definition")
else:
    print("Warning: old_tabs_block not found!")

# 2. Update renderTabs()
old_render_tabs = '''  renderTabs() {
    this.el(".sd-tabs").innerHTML = Object.entries(this.tabs)
      .map(
        ([k, label]) =>
          `<button role="tab" aria-selected="${this.tab === k}" class="${this.tab === k ? "active" : ""}" data-tab="${k}">${this.workspaceIcon(label)}<span>${label}</span></button>`,
      )
      .join("");
  }'''

new_render_tabs = '''  renderTabs() {
    const activeKey = this.view === "subcontracting" ? "subcontracting" : (this.view === "accounting" ? "accounting" : this.tab);
    const tabsContainer = this.el(".sd-tabs");
    if (!tabsContainer) return;
    tabsContainer.innerHTML = Object.entries(this.tabs)
      .map(
        ([k, label]) =>
          `<button role="tab" aria-selected="${activeKey === k}" class="${activeKey === k ? "active" : ""}" data-tab="${k}">${this.workspaceIcon(label)}<span>${label}</span></button>`,
      )
      .join("");
  }'''

if old_render_tabs in js_content:
    js_content = js_content.replace(old_render_tabs, new_render_tabs, 1)
    print("2. Replaced renderTabs definition")
else:
    print("Warning: old_render_tabs not found!")

# 3. Update click(event) for d.tab
old_tab_click = '''    else if (d.tab) {
      this.tab = d.tab;
      this.reportState = null;
      this.writeUrl();
      this.renderTabs();
      this.renderContent();
    }'''

new_tab_click = '''    else if (d.tab) {
      if (d.tab === "subcontracting") {
        this.openSubcontractingView();
      } else if (d.tab === "accounting") {
        this.openAccountingView();
      } else {
        if (this.view === "subcontracting") this.closeSubcontractingView();
        if (this.view === "accounting") this.closeAccountingView();
        this.tab = d.tab;
        this.reportState = null;
        this.writeUrl();
        this.renderTabs();
        this.renderContent();
      }
    }'''

if old_tab_click in js_content:
    js_content = js_content.replace(old_tab_click, new_tab_click, 1)
    print("3. Replaced tab click handler")
else:
    print("Warning: old_tab_click not found!")

# 4. Remove .sd-tabs from hideSelectors in showSubcontractingView
old_sub_hide = '''    const hideSelectors = [
      ".sd-hero",
      ".sd-controls",
      ".sd-breadcrumb",
      ".sd-scope-note",
      ".sd-kpis",
      "[data-live-projects]",
      "[data-subcontracting-card-panel]",
      "[data-accounting-card-panel]",
      "[data-customer-panel]",
      "[data-project-panel]",
      "[data-project-summary]",
      ".sd-tabs",
      "[data-content]",
    ];'''

new_sub_hide = '''    const hideSelectors = [
      ".sd-hero",
      ".sd-controls",
      ".sd-breadcrumb",
      ".sd-scope-note",
      ".sd-kpis",
      "[data-live-projects]",
      "[data-subcontracting-card-panel]",
      "[data-accounting-card-panel]",
      "[data-customer-panel]",
      "[data-project-panel]",
      "[data-project-summary]",
      "[data-content]",
    ];'''

# Replace all occurrences (both subcontracting and accounting hideSelectors)
if old_sub_hide in js_content:
    js_content = js_content.replace(old_sub_hide, new_sub_hide)
    print("4. Removed .sd-tabs from hideSelectors")
else:
    print("Warning: old_sub_hide not found!")

# 5. Remove .sd-tabs from showSelectors
old_sub_show = '''    const showSelectors = [
      ".sd-hero",
      ".sd-controls",
      ".sd-breadcrumb",
      ".sd-scope-note",
      ".sd-kpis",
      "[data-live-projects]",
      "[data-subcontracting-card-panel]",
      "[data-accounting-card-panel]",
      ".sd-tabs",
      "[data-content]",
    ];'''

new_sub_show = '''    const showSelectors = [
      ".sd-hero",
      ".sd-controls",
      ".sd-breadcrumb",
      ".sd-scope-note",
      ".sd-kpis",
      "[data-live-projects]",
      "[data-subcontracting-card-panel]",
      "[data-accounting-card-panel]",
      "[data-content]",
    ];'''

if old_sub_show in js_content:
    js_content = js_content.replace(old_sub_show, new_sub_show)
    print("5. Removed .sd-tabs from showSelectors")
else:
    print("Warning: old_sub_show not found!")

# 6. Add renderTabs() to openSubcontractingView and openAccountingView
old_open_sub = '''  openSubcontractingView() {
    this.view = "subcontracting";
    this.writeUrl();
    this.showSubcontractingView();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }'''

new_open_sub = '''  openSubcontractingView() {
    this.view = "subcontracting";
    this.writeUrl();
    this.showSubcontractingView();
    this.renderTabs();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }'''

if old_open_sub in js_content:
    js_content = js_content.replace(old_open_sub, new_open_sub, 1)
    print("6. Added renderTabs() to openSubcontractingView")

old_close_sub = '''  closeSubcontractingView() {
    this.view = "";
    this.writeUrl();
    this.hideSubcontractingView();
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (!this.data) {
      this.load();
    }
  }'''

new_close_sub = '''  closeSubcontractingView() {
    this.view = "";
    this.writeUrl();
    this.hideSubcontractingView();
    this.renderTabs();
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (!this.data) {
      this.load();
    }
  }'''

if old_close_sub in js_content:
    js_content = js_content.replace(old_close_sub, new_close_sub, 1)
    print("7. Added renderTabs() to closeSubcontractingView")

old_open_acc = '''  openAccountingView() {
    this.view = "accounting";
    this.writeUrl();
    this.showAccountingView();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }'''

new_open_acc = '''  openAccountingView() {
    this.view = "accounting";
    this.writeUrl();
    this.showAccountingView();
    this.renderTabs();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }'''

if old_open_acc in js_content:
    js_content = js_content.replace(old_open_acc, new_open_acc, 1)
    print("8. Added renderTabs() to openAccountingView")

old_close_acc = '''  closeAccountingView() {
    this.view = "";
    this.writeUrl();
    this.hideAccountingView();
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (!this.data) {
      this.load();
    }
  }'''

new_close_acc = '''  closeAccountingView() {
    this.view = "";
    this.writeUrl();
    this.hideAccountingView();
    this.renderTabs();
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (!this.data) {
      this.load();
    }
  }'''

if old_close_acc in js_content:
    js_content = js_content.replace(old_close_acc, new_close_acc, 1)
    print("9. Added renderTabs() to closeAccountingView")

# 10. Add live clock updater to constructor
old_ai_init = '''    this.initAiAssistant();'''
new_ai_init = '''    this.initAiAssistant();
    const updateLiveTime = () => {
      const timeEl = document.getElementById("sd-live-time");
      if (timeEl) {
        timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      }
    };
    updateLiveTime();
    setInterval(updateLiveTime, 1000);'''

if old_ai_init in js_content:
    js_content = js_content.replace(old_ai_init, new_ai_init, 1)
    print("10. Added live clock updater")

target_js = r'sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js'
with open(target_js, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully updated {target_js}!")
