/* DASH-008 adapter. Existing detail/report pages remain owned by their controller. */
(() => {
 "use strict";
 const proto = frappe.SarathiOwnerDashboard.prototype;
 const UI = frappe.sarathiUI;
 const original = Object.fromEntries(["loadContext", "refreshCurrentPage", "smoothRefresh", "getFilters", "selectPage", "refreshFilterDropdownsOnly", "hide"].map(key => [key, proto[key]]));
 const element = (tag, cls, text) => { const node = document.createElement(tag); node.className = cls || ""; if (text !== undefined) node.textContent = text; return node; };
 const salesDefaults = () => ({ interval: "Monthly", top_limit: "5", order_status: "", delivery_from: "", delivery_to: "" });
 const healthDefaults = () => ({ reference_at: "", review_days: "7", project_health: "", project_status: "", task_view: "Attention", delivery_view: "All open" });
 const mfgDefaults = () => ({ warehouse: "", mfg_status: "", shortage_only: "1" });
 const riskDefaults = () => ({ risk_category: "", risk_severity: "" });
 const scopeKey = values => JSON.stringify(Object.entries(values).filter(([, value]) => value !== "" && value != null).sort(([a], [b]) => a.localeCompare(b)));
 const request = async (method, args) => {
  const response = await frappe.call({ method: "sarathi_owner.api.homepage." + method, type: "GET", args, silent: true });
  if (!response.message) throw Error("Unavailable");
  return response.message;
 };

 proto.loadContext = function () {
  if (this.homeReady) return this.homeReady;
  this.homeFilters = this.homeFilters || { company: "", customer: "", project: "", from_date: "", to_date: "", ...salesDefaults(), ...healthDefaults(), ...mfgDefaults(), ...riskDefaults() };
  this.homeOptionState = {};
  this.homeControls = {};
  this.homeScopeEpoch = 0;
  this.homeNotice = element("div", "sod-home-notice"); this.homeNotice.setAttribute("role", "status");
  const fields = [
   { key: "company", label: "Company", type: "select", options: [], required: true },
   { key: "from_date", label: "From date", type: "date" },
   { key: "to_date", label: "To date", type: "date" },
   { key: "customer", label: "Customer", type: "select", options: [] },
   { key: "project", label: "Project", type: "select", options: [] },
   { key: "risk_category", label: "Executive risk category", type: "select", options: ["All", "Receivables", "Deliveries", "Projects", "Manufacturing"].map(value => ({ value: value === "All" ? "" : value, label: value })) },
   { key: "risk_severity", label: "Executive risk severity", type: "select", options: ["All", "Critical", "High", "Medium", "Informational"].map(value => ({ value: value === "All" ? "" : value, label: value })) },
   { key: "interval", label: "Income trend interval", type: "select", value: "Monthly", options: ["Monthly", "Daily"].map(value => ({value, label: value})) },
   { key: "top_limit", label: "Top customers", type: "select", value: "5", required: true, options: [5, 10, 20].map(value => ({value: String(value), label: String(value)})) },
   { key: "order_status", label: "Backlog status", type: "select", options: ["To Deliver and Bill", "To Deliver", "On Hold"].map(value => ({value, label: value})) },
   { key: "delivery_from", label: "Delivery from (backlog)", type: "date" },
   { key: "delivery_to", label: "Delivery to (backlog)", type: "date" },
   { key: "reference_at", label: "Health reference time (site)", type: "datetime-local" },
   { key: "review_days", label: "Review window (days)", type: "select", value: "7", required: true, options: [0,7,14,30,60,90].map(value=>({value:String(value),label:String(value)})) },
   { key: "project_health", label: "Project health (list)", type: "select", options: ["Overdue","At risk","Due soon","Unknown","Not overdue","Completed","Cancelled"].map(value=>({value,label:value})) },
   { key: "project_status", label: "Project recorded status", type: "select", options: ["Open","On hold","Completed","Cancelled"].map(value=>({value,label:value})) },
   { key: "task_view", label: "Task deadline view", type: "select", value: "Attention", options: ["Attention","All incomplete","Overdue","Due soon","Milestones"].map(value=>({value,label:value})) },
   { key: "delivery_view", label: "Delivery health (list)", type: "select", value: "All open", options: ["All open","Overdue","Due soon","Held","Unknown"].map(value=>({value,label:value})) },
   { key: "warehouse", label: "Warehouse (inventory)", type: "select", options: [] },
   { key: "mfg_status", label: "Work Order status", type: "select", options: ["Active","Completed","Overdue","Due soon","Draft","Cancelled","Stopped"].map(value=>({value,label:value})) },
   { key: "shortage_only", label: "Shortage filter", type: "select", value: "1", options: [{value:"1",label:"Shortages only"},{value:"0",label:"All material requirements"}] },
  ];
  this.homeForm = UI.filterBar({ fields, onApply: async values => {
   this.homeFilters = values; this.copyHomeFiltersToLegacy(); await this.refreshHomepage();
   if (matchMedia("(max-width:1023px)").matches) this.homePanel.open = false;
  }, onReset: async () => {
   const company = this.homeControls.company.value || this.homeFilters.company;
   this.homeFilters = { company, customer: "", project: "", from_date: "", to_date: "", ...salesDefaults(), ...healthDefaults(), ...mfgDefaults(), ...riskDefaults() };
   for (const [key, control] of Object.entries(this.homeControls)) control.value = this.homeFilters[key];
   this.homeScopeEpoch++; await this.loadHomeOptions("projects"); await this.loadHomeOptions("warehouses"); this.copyHomeFiltersToLegacy(); await this.refreshHomepage();
  }, validate: values => !values.company ? "Select an authorized Company." : values.from_date && values.to_date && values.from_date > values.to_date ? "From date must be on or before To date." : "" });
  fields.forEach(field => {
   const control = this.homeForm.querySelector(`[name="${field.key}"]`) || this.homeForm.querySelector(`#sui-filter-${field.key}`);
   if (control) { control.name = field.key; this.homeControls[field.key] = control; }
  });
  this.homePanel = element("details", "sod-home-filters"); this.homePanel.open = matchMedia("(min-width:1024px)").matches;
  this.homePanel.append(element("summary", "", "Dashboard filters"), this.homeForm);
  const searches = element("div", "sod-home-option-searches");
  for (const resource of ["companies", "customers", "projects", "warehouses"]) {
   const key = { companies: "company", customers: "customer", projects: "project", warehouses: "warehouse" }[resource];
   const group = element("div", "sod-home-option-search");
   const label = element("label", "", "Find " + key);
   const search = element("input", ""); search.type = "search"; search.id = "sod-home-find-" + key; label.htmlFor = search.id;
   let timer;
   search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => this.loadHomeOptions(resource, search.value), 250); });
   const more = UI.action({ label: "More " + resource, onActivate: () => this.loadHomeOptions(resource, search.value, true) }); more.hidden = true;
   group.append(label, search, more); searches.append(group);
   this.homeOptionState[resource] = { search: "", rows: [], start: 0, more, searchControl: search, sequence: 0 };
  }
  const optionSearchPanel = element("details", "sod-home-search-panel");
  optionSearchPanel.append(element("summary", "", "Search additional options"), searches);
  this.homePanel.append(optionSearchPanel, this.homeNotice);
  this.homeIntro = element("div", "sod-home-intro");
  this.homeIntro.append(UI.header({ title: "Owner & Executive Dashboard", description: "Business oversight for your authorized company." }));
  this.$el.find("#sod-filters")[0].before(this.homeIntro, this.homePanel);
  matchMedia("(max-width:1023px)").addEventListener("change", event => { this.homePanel.open = !event.matches; });
  this.homeControls.company.addEventListener("change", async () => {
   this.homeScopeEpoch++; this.homeControls.project.value = ""; this.selectedProject = "";
   this.homeControls.warehouse.value = "";
   this.homeData = null; this.activeData = null;
   await this.loadHomeOptions("projects");
   await this.loadHomeOptions("warehouses");
   this.homeNotice.textContent = "Company changed. Apply filters to update the overview.";
  });
  this.homeControls.customer.addEventListener("change", async () => {
   this.homeScopeEpoch++; this.homeControls.project.value = ""; this.selectedProject = "";
   await this.loadHomeOptions("projects");
  });
  // Refresh is a side-effect-free read; never invoke the legacy cache-clearing mutation.
  this.$el.off("click", "[data-action='refresh']");
  this.$el.on("click", "[data-action='refresh']", () => {
   if (this.homeBusy) return;
   if (this.currentPage === 0) this.refreshHomepage(); else original.refreshCurrentPage.call(this);
  });
  this.homeReady = (async () => {
   await this.loadHomeOptions("companies"); await this.loadHomeOptions("customers");
   const companies = this.homeOptionState.companies;
   if (companies.rows.length === 1 && !companies.hasNext) this.homeControls.company.value = companies.rows[0].value;
   this.homeFilters.company = this.homeControls.company.value;
   if (this.homeFilters.company) {
    await this.loadHomeOptions("projects");
    await this.loadHomeOptions("warehouses");
   }
   this.copyHomeFiltersToLegacy();
   if (this.currentPage === 0) await this.refreshHomepage();
  })();
  return this.homeReady;
 };

 proto.loadHomeOptions = async function (resource, search = "", append = false) {
  const state = this.homeOptionState[resource];
  const sequence = ++state.sequence;
  const epoch = this.homeScopeEpoch;
  const key = { companies: "company", customers: "customer", projects: "project", warehouses: "warehouse" }[resource];
  const control = this.homeControls[key];
  const selected = control.value;
  const selectedLabel = control.selectedOptions[0]?.textContent;
  if ((resource === "projects" || resource === "warehouses") && !this.homeControls.company.value) {
   this.homeForm.setOptions(key, []); state.rows = []; state.more.hidden = true; return;
  }
  const start = append ? state.start + 25 : 0;
  control.disabled = true;
  try {
   const extraArgs = resource === "projects" ? { company: this.homeControls.company.value, customer: this.homeControls.customer.value } : resource === "warehouses" ? { company: this.homeControls.company.value } : {};
   const data = await request("options", { resource, search, start, ...extraArgs });
   if (sequence !== state.sequence || (resource === "projects" && epoch !== this.homeScopeEpoch)) return;
   state.rows = append ? [...state.rows, ...data.options] : data.options;
   state.start = start; state.hasNext = data.has_next; state.more.hidden = !data.has_next;
   const options = [...state.rows];
   if (selected && !options.some(row => row.value === selected)) options.push({ value: selected, label: selectedLabel || selected });
   this.homeForm.setOptions(key, options); control.value = selected;
   if (key === "company") control.options[0].textContent = "Select Company";
   this.context ||= {}; this.context[resource] = state.rows.map(row => ({ name: row.value, customer_name: row.label, project_name: row.label }));
   this.populateFilterDropdowns();
   this.homeNotice.textContent = data.has_next ? "More matches are available. Search or load more options." : "";
  } catch (_) {
   if (sequence !== state.sequence) return;
   this.homeForm.setOptions(key, [], "error"); state.more.hidden = true;
   this.homeNotice.textContent = "Options could not load. Check your connection and search again.";
  }
 };

 proto.copyHomeFiltersToLegacy = function () {
  const values = this.homeFilters;
  for (const key of ["customer", "project"]) {
   const select = this.$el.find("#sod-filter-" + key)[0];
   if (values[key] && ![...select.options].some(option => option.value === values[key])) select.add(new Option(values[key], values[key]));
   select.value = values[key] || "";
   this.$el.find("#sod-filter-" + key + "-input").val(values[key] || "");
  }
  this.selectedProject = values.project || "";
  this.$el.find("#sod-filter-from-date").val(values.from_date || "");
  this.$el.find("#sod-filter-to-date").val(values.to_date || "");
  this.$el.find("#sod-filter-date").val(values.from_date || values.to_date ? "custom" : "all");
 };

 proto.getFilters = function () {
  return { ...original.getFilters.call(this), company: this.homeFilters?.company || "" };
 };
 proto.selectPage = function (index) {
  if (this.homePanel) this.homePanel.hidden = index !== 0;
  if (this.homeIntro) this.homeIntro.hidden = index !== 0;
  const legacy = this.$el.find("#sod-filters")[0]; if (legacy) legacy.hidden = index === 0;
  this.$el.find('.sui-disclosure[aria-controls="sod-filters"]').toggle(index !== 0);
  original.selectPage.call(this, index);
 };
 proto.refreshCurrentPage = function () {
  if (this.currentPage !== 0) return original.refreshCurrentPage.call(this);
  if (!this.homeReady) return this.loadContext();
  return this.homeReady.then(() => this.refreshHomepage());
 };
 proto.smoothRefresh = function () {
  if (this.currentPage !== 0) return original.smoothRefresh.call(this);
  if (this.homeReady && !this.homeBusy) return this.refreshHomepage(true);
 };
 proto.refreshFilterDropdownsOnly = function () {
  if (!this.homeReady) return;
  if (this.currentPage !== 0) this.populateFilterDropdowns();
 };

 proto.refreshHomepage = async function (silent = false) {
  if (!this.homeControls || this.currentPage !== 0) return;
  this.$el.find("#sod-filters").prop("hidden", true);
  this.$el.find('.sui-disclosure[aria-controls="sod-filters"]').hide();
  if (!this.homeFilters.company) {
   this.$content.empty().append(UI.state("unavailable", { message: "Select an authorized Company, then apply filters to view its records." }));
   this.$el.find("#sod-live-status-text").text("Select Company"); return;
  }
  if (this.homeBusy) { this.homePending = true; this.pageRequest = (this.pageRequest || 0) + 1; return; }
  this.homeBusy = true;
  const sequence = (this.pageRequest = (this.pageRequest || 0) + 1);
  const filters = { ...this.homeFilters };
  if (!silent || !this.homeData) { this.disposeSalesCharts(); this.$content.empty().append(UI.state("loading")); }
  const lastSuccessFormatted = this.lastSuccessfulRefresh ? UI.formatTimestamp(this.lastSuccessfulRefresh) : null;
  this.$el.find("#sod-live-status-text").text(lastSuccessFormatted ? `Refreshing… (Last updated: ${lastSuccessFormatted})` : "Refreshing…");
  try {
   const data = await request("get_homepage", { filters });
   if (sequence !== this.pageRequest || this.currentPage !== 0 || !this.visible) return;
   this.homeData = data; this.activeData = data;
   this.lastSuccessfulRefresh = data.generated_at || new Date().toISOString();
   this.lastFailedRefresh = null;
   this.renderHomepage(data);
   const updatedTime = UI.formatTimestamp(this.lastSuccessfulRefresh);
   this.$el.find("#sod-live-status-text").text("Last updated: " + updatedTime);
   this.homeNotice.textContent = "";
  } catch (error) {
   if (sequence !== this.pageRequest || this.currentPage !== 0) return;
   this.lastFailedRefresh = new Date().toISOString();
   const denied = error?.status === 403 || error?.exc_type === "PermissionError";
   // A failed new scope never retains data from a previously selected company.
   this.disposeSalesCharts(); this.$content.empty();
   const retain = silent && this.homeData && scopeKey(filters) === scopeKey(this.homeData.applied_filters) && !denied;
   if (retain) {
    this.renderHomepage(this.homeData);
    const staleTime = this.lastSuccessfulRefresh ? UI.formatTimestamp(this.lastSuccessfulRefresh) : "earlier";
    this.$content.prepend(UI.staleNotice({
     message: `Refresh failed. Showing data from last successful update (${staleTime}).`,
     lastSuccess: this.lastSuccessfulRefresh,
     onRetry: () => this.refreshHomepage()
    }));
    this.$el.find("#sod-live-status-text").text(`Refresh failed · Showing data from ${staleTime}`);
   } else {
    this.homeData = null; this.activeData = null;
    this.$content.prepend(UI.state(denied ? "denied" : navigator.onLine ? "error" : "offline", {
     message: denied ? "You do not have access to records for this company." : "Unable to load dashboard data. Please try again.",
     retry: () => this.refreshHomepage(),
     retryKind: "read"
    }));
    this.$el.find("#sod-live-status-text").text(denied ? "Access restricted" : "Data unavailable");
   }
  } finally { this.homeBusy = false; if (this.homePending) { this.homePending = false; this.refreshHomepage(); } }
 };

 proto.renderHomepage = function (data) {
  this.disposeSalesCharts();
  const content = element("div", "sod-homepage");
  this.homeIntro.replaceChildren(UI.header({ title: "Owner & Executive Dashboard", description: "Company overview and authorized records", company: data.applied_filters.company }));
  this.homeNotice.textContent = "";
  const scope = element("p", "sod-home-scope", ["Schedule dates: " + (data.applied_filters.from_date || "Beginning") + " – " + (data.applied_filters.to_date || "Latest"), "Customer: " + (data.applied_filters.customer || "All permitted customers"), "Project: " + (data.applied_filters.project || "All permitted projects")].join(" · "));
  content.append(scope, element("p", "sod-home-date-basis", data.date_basis));
  if (data.executive_risks) content.append(this.renderExecutiveRisks(data.executive_risks));
  const availability = element("section", "sod-home-availability");
  availability.append(element("h2", "", "Financial overview"));
  if (data.finance?.available) {
   const finance = data.finance.data;
   availability.append(element("p", "sod-home-date-basis", "Accounting period: " + finance.period.from_date + " – " + finance.period.to_date + ". Receivables/payables as of " + finance.as_of_date + ". Currency: " + finance.currency));
   const cards = element("div", "sod-finance-kpis");
   for (const metric of finance.metrics) {
    const value = !metric.available ? null : metric.unit === "%" ? metric.value.toLocaleString(undefined, {maximumFractionDigits:2}) : format_currency(metric.value, finance.currency);
    const description = metric.reason || (metric.key === "receivables" || metric.key === "payables" ? "As of " + finance.as_of_date : finance.period.from_date + " – " + finance.period.to_date);
    cards.append(UI.kpi({ label: metric.label, value, unit: metric.available && metric.unit === "%" ? "%" : undefined, description,
     onActivate: metric.available ? () => { frappe.route_options = metric.report_filters; return frappe.set_route("query-report", metric.source); } : undefined }));
   }
   availability.append(cards);
   for (const warning of finance.warnings || []) availability.append(element("p", "sod-home-date-basis", warning));
  } else availability.append(UI.state("unavailable", { message: data.finance?.reason || data.availability.finance }));
  availability.append(element("p", "", data.availability.analytics));
  content.append(availability);
  content.append(this.renderProjectHealth(data.project_health));
  content.append(this.renderSalesAnalytics(data.sales));
  content.append(this.renderManufacturingInventory(data.manufacturing_inventory));
  const grid = element("div", "sod-home-grid");
  const projects = element("section", "sod-home-panel"); projects.append(element("h2", "", "Project records"));
  projects.append(UI.recordList({ label: "Projects in the selected scope", columns: [{key:"project_name",label:"Project"},{key:"status",label:"Recorded status",render:UI.status},{key:"expected_start_date",label:"Expected start"}], rows: data.projects.rows,
   rowActions: row => [{ label: "Open project", onActivate: () => frappe.set_route("Form", "Project", row.name) }] }));
  if (data.projects.has_next) projects.append(element("p", "", "Showing the first six matching projects. Use Project search to narrow the overview."));
  const manufacturing = element("section", "sod-home-panel"); manufacturing.append(element("h2", "", "Manufacturing records"));
  if (!data.work_orders.available) manufacturing.append(UI.state("unavailable", { message: data.work_orders.reason }));
  else {
   manufacturing.append(UI.recordList({ label: "Work Orders in the selected scope", columns: [{key:"name",label:"Work Order"},{key:"status",label:"Recorded status",render:UI.status},{key:"planned_start_date",label:"Planned start"}], rows:data.work_orders.rows,
    rowActions: row => [{ label:"Open Work Order", onActivate: () => frappe.set_route("Form", "Work Order", row.name) }] }));
   if (data.work_orders.has_next) manufacturing.append(element("p", "", "Showing the first six matching Work Orders. Open the Control Tower for detailed investigation."));
  }
  grid.append(projects, manufacturing); content.append(grid);
  content.append(UI.action({label:"Open Production Control Tower",onActivate:()=>frappe.set_route("sarathicontroltower")}));
  this.$content.empty().append(content);
  for (const chart of this.salesCharts || []) chart.mount();
 };

 proto.disposeSalesCharts = function () {
  for (const chart of this.salesCharts || []) chart.dispose?.();
  this.salesCharts = [];
 };
 proto.hide = function () { this.disposeSalesCharts(); return original.hide.call(this); };

 proto.renderProjectHealth = function (payload) {
  const section=element("section","sod-home-panel sod-project-health");
  section.append(element("h2","","Projects & Delivery Health"));
  if (!payload?.available) { section.append(UI.state("unavailable",{message:payload?.reason || "Project health could not load."})); return section; }
  const data=payload.data, filters=data.applied_filters;
  section.append(element("p","sod-home-date-basis","Site reference: "+data.reference_at+" · Review window: "+data.review_days+" days. Project/order dates use "+data.reference_date+"; Task deadlines use the full reference time."));
  const page=(key,start)=>{this.homeFilters={...this.homeFilters,[key]:start};return this.refreshHomepage();};
  const listPaging=(prefix,hasNext,label)=>({label,previous:filters[prefix+"_start"]?()=>page(prefix+"_start",Math.max(0,filters[prefix+"_start"]-filters[prefix+"_page_length"])):null,next:hasNext?()=>page(prefix+"_start",filters[prefix+"_start"]+filters[prefix+"_page_length"]):null});
  const days=value=>value==null?"Unknown":value<0?Math.abs(value)+" days past due":value===0?"Due today":value+" days remaining";
  const projectPanel=element("div","sod-project-portfolio"); projectPanel.append(element("h3","","Project portfolio"));
  const projects=data.projects;
  if (!projects.available) projectPanel.append(UI.state("unavailable",{message:projects.reason}));
  else {
   const cards=element("div","sod-finance-kpis");
   for (const [label,key] of [["Relevant Projects","total"],["Active Projects","active"],["Completed Projects","completed"],["Cancelled Projects","cancelled"],["Overdue Projects","overdue"],["Projects due soon","due_soon"],["At risk · recorded evidence","at_risk"],["Unknown Project health","unknown"]]) cards.append(UI.kpi({label,value:projects.counts[key],description:key==="due_soon"?"Open Projects in the selected review window.":key==="at_risk"?"Recorded hold or accessible overdue Task; excludes already-overdue Projects.":key==="cancelled"?"Cancelled is distinct from completed.":"Current readable portfolio; independent of detail pagination."}));
   projectPanel.append(cards,element("p","sod-home-date-basis",projects.basis),element("p","sod-home-date-basis",projects.forecast));
   const progress=(value,row)=>{
    const box=element("div","sod-project-progress");box.append(UI.progress({value,label:"Recorded progress",text:value==null?undefined:value.toLocaleString(undefined,{maximumFractionDigits:2})+"%"}));
    box.append(element("small","",row.progress_method));
    for (const warning of row.progress_warnings) box.append(element("small","",warning));
    return box;
   };
   projectPanel.append(UI.recordList({label:"Project health · "+(filters.project_health || "all classifications"),rows:projects.rows,
    columns:[{key:"project_name",label:"Project"},{key:"customer",label:"Customer"},{key:"status",label:"Recorded status",render:UI.status},{key:"health",label:"Health",render:UI.status},{key:"progress",label:"Recorded progress",render:progress},{key:"expected_start_date",label:"Expected start"},{key:"expected_end_date",label:"Expected end"},{key:"days_to_end",label:"Deadline",render:days},{key:"reason",label:"Recorded evidence"}],
    rowActions:row=>[{label:"Open Project",onActivate:()=>frappe.set_route("Form","Project",row.name)},{label:"Review Project Tasks & deliveries",onActivate:()=>{
     const control=this.homeControls.project;if(![...control.options].some(option=>option.value===row.name)) control.add(new Option(row.project_name,row.name));control.value=row.name;
     this.homeFilters={...this.homeFilters,project:row.name,project_health:"",project_start:0,task_start:0,health_delivery_start:0,start:0,backlog_start:0};this.homeControls.project_health.value="";this.copyHomeFiltersToLegacy();return this.refreshHomepage();
    }}],pagination:listPaging("project",projects.has_next,"Showing "+projects.rows.length+" of "+projects.matching_count+" matching Projects. Portfolio counts retain the full selected cohort.")}));
   const taskPanel=element("div","sod-project-tasks");taskPanel.append(element("h3","","Tasks & milestones"));
   const tasks=projects.tasks;
   if (!tasks.available) taskPanel.append(UI.state("unavailable",{message:tasks.reason}));
   else {
    const counts=tasks.counts;
    taskPanel.append(element("p","sod-home-date-basis",(counts.overdue_tasks || 0)+" visible overdue Tasks · "+(counts.due_soon_tasks || 0)+" due soon · "+(counts.overdue_milestones || 0)+" overdue milestones · "+(counts.due_soon_milestones || 0)+" upcoming milestones · "+(counts.unknown_dates || 0)+" unknown deadlines. "+tasks.coverage));
    taskPanel.append(UI.recordList({label:"Incomplete Tasks · "+filters.task_view,rows:tasks.rows,columns:[{key:"subject",label:"Task"},{key:"project",label:"Project"},{key:"status",label:"Recorded status",render:UI.status},{key:"exp_end_date",label:"Expected end (site time)"},{key:"is_milestone",label:"Milestone",render:value=>value?"Yes":"No"},{key:"health",label:"Deadline health",render:UI.status}],rowActions:row=>[{label:"Open Task",onActivate:()=>frappe.set_route("Form","Task",row.name)}],pagination:listPaging("task",tasks.has_next,"Task deadlines are distinct from the Project end date; Completed, Cancelled and Template Tasks are excluded.")}));
   }
   projectPanel.append(taskPanel);
  }
  section.append(projectPanel);
  const deliveries=data.deliveries, deliveryPanel=element("div","sod-project-deliveries"); deliveryPanel.append(element("h3","","Customer delivery commitments · quantity health"));
  if (!deliveries.available) deliveryPanel.append(UI.state("unavailable",{message:deliveries.reason}));
  else {
   const cards=element("div","sod-finance-kpis");
   for (const [label,key] of [["Open delivery orders","open_orders"],["Overdue delivery orders","overdue_orders"],["Delivery orders due soon","due_soon_orders"],["Partially delivered orders","partially_delivered_orders"],["Held delivery orders","held_orders"],["Orders with unknown dates","unknown_date_orders"]]) cards.append(UI.kpi({label,value:deliveries.counts[key],description:"Distinct orders in the delivery cohort; deadline buckets can overlap."}));
   deliveryPanel.append(cards,element("p","sod-home-date-basis",deliveries.basis),element("p","sod-home-date-basis",deliveries.coverage));
   deliveryPanel.append(UI.recordList({label:"Delivery lines · "+filters.delivery_view,rows:deliveries.rows,columns:[{key:"sales_order",label:"Sales Order"},{key:"customer",label:"Customer"},{key:"project",label:"Explicit Project"},{key:"item_code",label:"Item"},{key:"delivery_date",label:"Order-line delivery date"},{key:"health",label:"Delivery health",render:UI.status},{key:"days_to_delivery",label:"Deadline",render:days},{key:"remaining_qty",label:"Remaining stock quantity",render:(value,row)=>value.toLocaleString(undefined,{maximumFractionDigits:6})+" "+row.stock_uom}],rowActions:row=>[{label:"Open Sales Order",onActivate:()=>frappe.set_route("Form","Sales Order",row.sales_order)}],pagination:listPaging("health_delivery",deliveries.has_next,"Detail filters select lines; summary counts retain all matching commitments. These are not recognized revenue or historical delivery-performance metrics.")}));
   const quantities=element("details",""); quantities.append(element("summary","","Remaining quantities by item / stock UOM"),UI.recordList({label:"Delivery stock quantities",rows:deliveries.quantities,columns:[{key:"item_code",label:"Item"},{key:"stock_uom",label:"Stock UOM"},{key:"remaining_qty",label:"Remaining quantity"}]}));
   if (deliveries.quantity_group_count>100) quantities.append(element("p","","Showing the first 100 of "+deliveries.quantity_group_count+" groups; narrow Customer or Project filters for more detail."));
   deliveryPanel.append(quantities);
  }
  section.append(deliveryPanel);return section;
 };

 proto.renderSalesAnalytics = function (payload) {
  const section = element("section", "sod-home-panel sod-sales-analytics");
  section.append(element("h2", "", "Customers & Sales"));
  if (!payload?.available) { section.append(UI.state("unavailable", {message: payload?.reason || "Sales analytics are unavailable."})); return section; }
  const data = payload.data, filters = data.applied_filters;
  const money = value => format_currency(value, data.currency);
  const percent = value => value == null ? "N/A" : value.toLocaleString(undefined, {maximumFractionDigits: 2}) + "%";
  section.append(element("p", "sod-home-date-basis", "Income posting period and order-date cohort: " + filters.from_date + " – " + filters.to_date + ". Currency: " + data.currency));
  section.append(element("p", "sod-home-date-basis", "Backlog status: " + (filters.order_status || "All open statuses") + ". Expected delivery: " + (filters.delivery_from || "Beginning / unknown") + " – " + (filters.delivery_to || "Latest / unknown") + ". These filters apply only to commitments."));
  const page = (key, start) => { this.homeFilters = {...this.homeFilters, [key]: start}; return this.refreshHomepage(); };
  const revenue = element("div", "sod-sales-revenue");
  if (!data.revenue.available) revenue.append(UI.state("unavailable", {message: data.revenue.reason}));
  else {
   const info = data.revenue;
   const summary = element("div", "sod-finance-kpis");
   summary.append(UI.kpi({label: "Included accounting income", value: money(info.included_income), description: "Customer selection applies to attributable income only."}),
    UI.kpi({label: "Attributed customer income", value: money(info.customer_total), description: info.customer_count + " customers in scope"}),
    UI.kpi({label: "Unattributed accounting income", value: money(info.unattributed), description: "No verified Customer link; never distributed to customers."}));
   revenue.append(summary, element("p", "sod-home-date-basis", info.basis), element("p", "sod-home-date-basis", info.share_basis));
   revenue.append(element("h3", "", "Top customers by accounting income"));
   revenue.append(element("p", "sod-home-date-basis", "Bar length shows absolute magnitude; signed amounts and shares are written beside every customer."));
   const comparison = element("ol", "sod-customer-ranking");
   const largest = Math.max(...info.top_customers.map(row => Math.abs(row.amount)), 0);
   for (const row of info.top_customers) {
    const item = element("li", "");
    const label = element("span", "", row.customer_name + " · " + money(row.amount) + " · " + percent(row.share));
    const track = element("div", "sod-sales-bar-track"); track.setAttribute("aria-hidden", "true");
    const bar = element("div", "sod-sales-bar"); bar.style.width = (largest ? Math.abs(row.amount) / largest * 100 : 0) + "%"; track.append(bar);
    item.append(label, track); comparison.append(item);
   }
   revenue.append(info.top_customers.length ? comparison : UI.state("empty", {message: "No customer-attributed income in this period."}));
   revenue.append(UI.recordList({label: "Revenue by Customer · accounting income", rows: info.rows,
    columns: [{key:"rank",label:"Rank"}, {key:"customer_name",label:"Customer"}, {key:"amount",label:"Accounting income",render:money}, {key:"share",label:"Customer share",render:percent}],
    rowActions: row => [{label:"Open Customer",onActivate:()=>frappe.set_route("Form","Customer",row.customer)},
     {label:"Customer income details",onActivate:()=>{this.homeControls.customer.value=row.customer; if(this.homeControls.customer.value!==row.customer) this.homeControls.customer.add(new Option(row.customer_name,row.customer,true,true)); this.homeControls.project.value=""; this.homeFilters={...this.homeFilters,customer:row.customer,project:"",start:0,backlog_start:0}; this.copyHomeFiltersToLegacy(); return this.refreshHomepage();}}],
    pagination: {label: "Showing " + info.rows.length + " of " + info.customer_count + " customers", previous: filters.start ? ()=>page("start",Math.max(0,filters.start-filters.page_length)) : null, next: info.has_next ? ()=>page("start",filters.start+filters.page_length) : null} }));
   const trend = UI.chart({title:"Accounting income trend",description:filters.interval + " posting-date totals in " + data.currency + "; axis abbreviations K = thousand, M = million. Empty measured periods are zero. Includes unattributed income when no Customer is selected.",
    // Installed Charts can race its SVG entry animation against rapid resizing.
    // Its public options disable animation while retaining responsive rendering.
    render:canvas=>new frappe.Chart(canvas,{type:"bar",height:260,animate:0,disableEntryAnimation:1,colors:["#2266b4"],data:{labels:info.trend.map(row=>row.period),datasets:[{name:"Accounting income ("+data.currency+")",values:info.trend.map(row=>row.amount)}]},axisOptions:{xAxisMode:"tick",xIsSeries:1,shortenYAxisNumbers:1},tooltipOptions:{formatTooltipY:money}})});
   this.salesCharts.push(trend); revenue.append(trend);
   // A visible keyboard/touch-readable table is also the chart's accessible data alternative.
   const trendDetails = element("details", "sod-trend-data"); trendDetails.append(element("summary", "", "View trend values"), UI.recordList({label:"Accounting income trend values ("+data.currency+")",rows:info.trend,columns:[{key:"period",label:"Posting period"},{key:"amount",label:"Accounting income",render:money}]}));
   revenue.append(trendDetails);
   revenue.append(UI.action({label:"Open matching Profit and Loss report",onActivate:()=>{frappe.route_options=info.reference_filters; frappe.set_route("query-report","Profit and Loss Statement");}}));
   if (filters.customer) revenue.append(element("p","sod-home-date-basis","P&L drill-down shows the full equivalent company/dimension scope; Customer attribution is shown in this dashboard, since native P&L has no Customer filter."));
  }
  section.append(revenue);
  const backlog = element("div", "sod-sales-backlog"); backlog.append(element("h3", "", "Sales Order delivery backlog · commitments"));
  if (!data.backlog.available) backlog.append(UI.state("unavailable", {message:data.backlog.reason}));
  else {
   const info = data.backlog, summary = element("div", "sod-finance-kpis");
   for (const [label,key] of [["Open delivery commitments","remaining_value"],["Overdue delivery commitments","overdue_value"],["Held demand (On Hold)","held_value"]]) summary.append(UI.kpi({label,value:money(info[key]),description:"Commitment, separate from recognized income."}));
   backlog.append(summary,element("p","sod-home-date-basis",info.basis + " Current recorded state: " + info.source_as_of));
   backlog.append(element("p","sod-home-date-basis",info.open_order_count+" open orders · "+info.held_order_count+" held orders"));
   backlog.append(UI.recordList({label:"Current delivery backlog lines",rows:info.rows,
    columns:[{key:"sales_order",label:"Sales Order"},{key:"customer",label:"Customer"},{key:"transaction_date",label:"Order date"},{key:"item_code",label:"Item"},{key:"status",label:"Status",render:UI.status},{key:"delivery_date",label:"Expected delivery"},{key:"due_state",label:"Delivery state"},{key:"remaining_qty",label:"Remaining stock qty",render:(value,row)=>value.toLocaleString()+" "+row.stock_uom},{key:"remaining_value",label:"Delivery net value",render:money}],
    rowActions:row=>[{label:"Open Sales Order",onActivate:()=>frappe.set_route("Form","Sales Order",row.sales_order)}],
    pagination:{label:"Showing "+info.rows.length+" matching lines. Held demand is excluded from open totals.",previous:filters.backlog_start?()=>page("backlog_start",Math.max(0,filters.backlog_start-filters.backlog_page_length)):null,next:info.has_next?()=>page("backlog_start",filters.backlog_start+filters.backlog_page_length):null}}));
   const quantities=element("details",""); quantities.append(element("summary","","Remaining quantities by item and stock UOM"),UI.recordList({label:"Executable backlog quantities",rows:info.quantities,columns:[{key:"item_code",label:"Item"},{key:"stock_uom",label:"Stock UOM"},{key:"remaining_qty",label:"Remaining quantity"}]})); backlog.append(quantities);
   if (info.quantities_has_next) quantities.append(element("p","","Showing the first 100 of "+info.quantity_group_count+" item/UOM groups. Narrow Customer or Project filters to inspect additional groups. Monetary totals include every matching group."));
  }
  section.append(backlog); return section;
 };

 proto.renderManufacturingInventory = function (payload) {
  const section = element("section", "sod-home-panel sod-mfg-inventory");
  section.append(element("h2", "", "Manufacturing & Inventory"));
  if (!payload?.available) {
   section.append(UI.state("unavailable", { message: payload?.reason || "Manufacturing and inventory summary could not load." }));
   return section;
  }
  const data = payload.data, filters = data.applied_filters;
  const currency = data.currency;
  const money = value => format_currency(value, currency);
  const page = (key, start) => { this.homeFilters = { ...this.homeFilters, [key]: start }; return this.refreshHomepage(); };
  const listPaging = (prefix, hasNext, label) => ({
   label,
   previous: filters[prefix + "_start"] ? () => page(prefix + "_start", Math.max(0, filters[prefix + "_start"] - filters[prefix + "_page_length"])) : null,
   next: hasNext ? () => page(prefix + "_start", filters[prefix + "_start"] + filters[prefix + "_page_length"]) : null
  });
  const days = value => value == null ? "Unknown" : value < 0 ? Math.abs(value) + " days past due" : value === 0 ? "Due today" : value + " days remaining";

  section.append(element("p", "sod-home-date-basis", "Site reference: " + data.reference_at + " · Review window: " + data.review_days + " days · Warehouse scope: " + (filters.warehouse || "All leaf warehouses") + " · Currency: " + currency));

  // --- 1. Manufacturing Summary ---
  const mfg = data.manufacturing;
  const mfgPanel = element("div", "sod-mfg-summary");
  mfgPanel.append(element("h3", "", "Manufacturing commitments & production output"));
  if (!mfg.available) {
   mfgPanel.append(UI.state("unavailable", { message: mfg.reason }));
  } else {
   const mfgCards = element("div", "sod-finance-kpis");
   for (const [label, key] of [
    ["Active Work Orders", "active"],
    ["Completed Work Orders", "completed"],
    ["Overdue Work Orders", "overdue"],
    ["Jobs due soon", "due_soon"],
    ["Draft Work Orders", "draft"],
    ["Cancelled Work Orders", "cancelled"],
   ]) {
    mfgCards.append(UI.kpi({
     label,
     value: mfg.counts[key],
     description: key === "overdue" ? "Target completion date < site reference date." : key === "due_soon" ? "Approaching target date within " + data.review_days + " days." : key === "active" ? "In Process or Not Started." : "Portfolio total."
    }));
   }
   mfgPanel.append(mfgCards, element("p", "sod-home-date-basis", mfg.basis));

   // Planned vs Actual Output per UOM
   const uomSummaries = mfg.production_output.uom_summaries || [];
   if (uomSummaries.length) {
    const uomGrid = element("div", "sod-uom-cards");
    for (const u of uomSummaries) {
     const card = element("div", "sod-uom-card");
     card.append(
      element("div", "sod-uom-card-title", "Output · " + u.stock_uom),
      element("div", "sod-uom-card-stat", "Planned: " + u.planned_qty.toLocaleString() + " " + u.stock_uom),
      element("div", "sod-uom-card-stat", "Produced: " + u.produced_qty.toLocaleString() + " " + u.stock_uom),
      element("div", "sod-uom-card-stat", "Variance: " + (u.variance >= 0 ? "+" : "") + u.variance.toLocaleString() + " " + u.stock_uom),
      UI.progress({ value: u.achievement_pct, label: "Achievement", text: u.achievement_pct + "%" })
     );
     uomGrid.append(card);
    }
    mfgPanel.append(uomGrid);
   }

   // Work Order table
   const progress = (value, row) => {
    const box = element("div", "sod-project-progress");
    box.append(UI.progress({ value: row.progress_pct, label: "Produced progress", text: row.progress_pct + "%" }));
    box.append(element("small", "", row.produced_qty + " / " + row.qty + " " + row.stock_uom));
    return box;
   };

   mfgPanel.append(UI.recordList({
    label: "Work Orders · " + (filters.mfg_status || "All statuses"),
    rows: mfg.rows,
    columns: [
     { key: "name", label: "Work Order" },
     { key: "production_item", label: "Item" },
     { key: "status", label: "Recorded status", render: UI.status },
     { key: "health", label: "Health", render: UI.status },
     { key: "progress_pct", label: "Progress", render: progress },
     { key: "planned_start_date", label: "Planned start" },
     { key: "target_completion_date", label: "Target completion" },
     { key: "days_to_target", label: "Deadline", render: days },
     { key: "project", label: "Project" }
    ],
    rowActions: row => [{
     label: "Open Work Order",
     onActivate: () => frappe.set_route("Form", "Work Order", row.name)
    }],
    pagination: listPaging("wo", mfg.has_next, "Showing " + mfg.rows.length + " of " + mfg.matching_count + " matching Work Orders. Aggregates retain the full company portfolio.")
   }));
  }
  section.append(mfgPanel);

  // --- 2. Inventory Valuation & Stock Availability ---
  const inv = data.inventory;
  const risk = data.stock_risk;
  const invPanel = element("div", "sod-inv-summary");
  invPanel.append(element("h3", "", "Inventory valuation & stock availability"));
  if (!inv.available) {
   invPanel.append(UI.state("unavailable", { message: inv.reason }));
  } else {
   const invCards = element("div", "sod-finance-kpis");
   invCards.append(
    UI.kpi({
     label: "Total inventory valuation",
     value: money(inv.valuation),
     description: inv.method,
     onActivate: () => {
      frappe.route_options = { company: filters.company, warehouse: filters.warehouse || "" };
      frappe.set_route("query-report", "Stock Balance");
     }
    }),
    UI.kpi({ label: "Total actual stock", value: inv.total_actual_qty.toLocaleString(), description: "Physical recorded balance across " + inv.total_items + " items." }),
    UI.kpi({ label: "Total reserved stock", value: inv.total_reserved_qty.toLocaleString(), description: "Committed to sales, manufacture, or subcontracting." }),
    UI.kpi({ label: "Total projected stock", value: inv.total_projected_qty.toLocaleString(), description: "Standard ERPNext projected stock quantity." })
   );
   invPanel.append(invCards, element("p", "sod-home-date-basis", inv.basis + " Drill-down opens standard Stock Balance report."));

   // Stock risk summary counts
   if (risk.available) {
    const riskCounts = element("div", "sod-finance-kpis");
    riskCounts.append(
     UI.kpi({ label: "Low-stock items", value: risk.counts.low_stock_items, description: "Below warehouse reorder level or item safety stock." }),
     UI.kpi({ label: "Negative projected items", value: risk.counts.negative_projected_items, description: "Demand exceeds physical stock plus open supply." }),
     UI.kpi({ label: "Zero stock with demand", value: risk.counts.zero_stock_with_demand, description: "Zero physical stock but active commitments exist." }),
     UI.kpi({ label: "Unconfigured thresholds", value: risk.counts.unconfigured_items, description: "No reorder level or safety stock set in ERPNext." })
    );
    invPanel.append(riskCounts, element("p", "sod-home-date-basis", risk.basis));

    invPanel.append(UI.recordList({
     label: "Inventory items & stock risk",
     rows: risk.rows,
     columns: [
      { key: "item_code", label: "Item" },
      { key: "item_name", label: "Item description" },
      { key: "warehouse", label: "Warehouse" },
      { key: "actual_qty", label: "Actual stock", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "reserved_qty", label: "Reserved", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "available_qty", label: "Available", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "projected_qty", label: "Projected", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "threshold", label: "Threshold", render: (v, r) => v != null ? v.toLocaleString() + " " + r.stock_uom : "Unconfigured" },
      { key: "risk_status", label: "Risk status", render: UI.status },
      { key: "stock_value", label: "Stock value", render: money }
     ],
     rowActions: row => [{
      label: "Open Item",
      onActivate: () => frappe.set_route("Form", "Item", row.item_code)
     }],
     pagination: listPaging("stock", risk.has_next, "Showing " + risk.rows.length + " of " + risk.total_count + " matching stock items.")
    }));
   }
  }
  section.append(invPanel);

  // --- 3. Material Shortages Affecting Production ---
  const shortages = data.shortages;
  const shortagePanel = element("div", "sod-shortage-summary");
  shortagePanel.append(element("h3", "", "Material shortages affecting active production"));
  if (!shortages.available) {
   shortagePanel.append(UI.state("unavailable", { message: shortages.reason }));
  } else {
   const shortageCards = element("div", "sod-finance-kpis");
   shortageCards.append(
    UI.kpi({ label: "Affected Work Orders", value: shortages.counts.shortage_work_orders, description: "Active Work Orders missing required raw materials." }),
    UI.kpi({ label: "Shortage materials", value: shortages.counts.shortage_items, description: "Distinct raw material items in shortage." }),
    UI.kpi({ label: "Shortage lines", value: shortages.counts.total_shortage_lines, description: "Material requirement lines exceeding available stock." })
   );
   shortagePanel.append(shortageCards, element("p", "sod-home-date-basis", shortages.basis));

   if (shortages.rows.length === 0) {
    shortagePanel.append(UI.state("empty", { message: "No material shortages detected for active Work Orders in the selected warehouse scope." }));
   } else {
    shortagePanel.append(UI.recordList({
     label: "Material requirements & shortages · " + (filters.shortage_only !== "0" ? "Shortages only" : "All material lines"),
     rows: shortages.rows,
     columns: [
      { key: "work_order", label: "Work Order" },
      { key: "production_item", label: "Assembling item" },
      { key: "item_code", label: "Raw material" },
      { key: "source_warehouse", label: "Source warehouse" },
      { key: "required_qty", label: "Total required", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "transferred_qty", label: "Transferred", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "remaining_required", label: "Remaining required", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "available_stock", label: "Available in warehouse", render: (v, r) => v.toLocaleString() + " " + r.stock_uom },
      { key: "shortage_qty", label: "Shortage quantity", render: (v, r) => v > 0 ? v.toLocaleString() + " " + r.stock_uom : "None" },
      { key: "expected_completion", label: "Target completion" }
     ],
     rowActions: row => [{
      label: "Open Work Order",
      onActivate: () => frappe.set_route("Form", "Work Order", row.work_order)
     }],
     pagination: listPaging("shortage", shortages.has_next, "Showing " + shortages.rows.length + " of " + shortages.matching_count + " matching requirement lines.")
    }));
   }
  }
  section.append(shortagePanel);

  return section;
 };

 proto.renderExecutiveRisks = function (payload) {
  const section = element("section", "sod-home-panel sod-executive-risks");
  section.append(element("h2", "", "Executive Risks, Exceptions & Approvals"));
  if (!payload?.available) {
   section.append(UI.state("unavailable", { message: payload?.reason || "Executive risks and approvals could not load." }));
   return section;
  }
  const data = payload.data, filters = data.applied_filters;
  section.append(element("p", "sod-home-date-basis", "Site reference: " + data.reference_at + " · Review window: " + data.review_days + " days. Currency: " + data.currency + ". Business risks and pending approvals are evaluated from verified transactions and workflow assignments."));

  const page = (key, start) => { this.homeFilters = { ...this.homeFilters, [key]: start }; return this.refreshHomepage(); };
  const listPaging = (prefix, hasNext, label) => ({
   label,
   previous: filters[prefix + "_start"] ? () => page(prefix + "_start", Math.max(0, filters[prefix + "_start"] - (filters[prefix + "_page_length"] || 10))) : null,
   next: hasNext ? () => page(prefix + "_start", (filters[prefix + "_start"] || 0) + (filters[prefix + "_page_length"] || 10)) : null
  });

  // 1. Executive Summary KPIs
  const summary = data.summary;
  const kpis = element("div", "sod-finance-kpis");
  kpis.append(
   UI.kpi({
    label: "Critical risks",
    value: summary.critical,
    description: "Verified urgent issues requiring immediate executive action."
   }),
   UI.kpi({
    label: "High risks",
    value: summary.high,
    description: "Significant overdue invoices, delivery delays, or blockers."
   }),
   UI.kpi({
    label: "Medium risks",
    value: summary.medium,
    description: "Approaching deadlines and commitments due within review window."
   }),
   UI.kpi({
    label: "Pending approvals",
    value: summary.pending_approvals,
    description: "Workflow actions and assignments allocated to your account."
   })
  );
  section.append(kpis);

  // 2. Business Exceptions & Risk Alerts Panel
  const risks = data.risks;
  const riskPanel = element("div", "sod-risk-exceptions");
  riskPanel.append(element("h3", "", "Business exceptions & risk alerts"));
  riskPanel.append(element("p", "sod-home-date-basis", risks.basis));

  const renderSeverity = val => {
   const badge = element("span", "sod-severity-badge", val);
   badge.setAttribute("data-severity", val);
   const icons = { Critical: "🔴", High: "🟠", Medium: "🔵", Informational: "ℹ" };
   badge.setAttribute("data-icon", icons[val] || "•");
   badge.setAttribute("aria-label", "Severity: " + val);
   return badge;
  };

  const renderRiskItem = (val, row) => {
   const box = element("div", "sod-risk-item-cell");
   box.append(element("div", "sod-risk-item-title", row.title));
   box.append(element("div", "sod-risk-item-desc", row.explanation));
   return box;
  };

  const renderEntity = (val, row) => {
   const box = element("div", "sod-risk-item-cell");
   box.append(element("div", "sod-risk-item-title", row.entity_type + ": " + row.entity_name));
   if (row.customer) box.append(element("div", "sod-risk-item-desc", "Customer: " + row.customer));
   else if (row.project) box.append(element("div", "sod-risk-item-desc", "Project: " + row.project));
   return box;
  };

  const renderDueDate = (val, row) => {
   const box = element("div", "sod-risk-meta-cell");
   if (!row.due_date) {
    box.textContent = "—";
    return box;
   }
   box.append(element("div", "", row.due_date));
   if (row.days_due < 0) {
    box.append(element("span", "sod-risk-overdue-tag", Math.abs(row.days_due) + "d overdue"));
   } else if (row.days_due === 0) {
    box.append(element("span", "sod-risk-due-soon-tag", "Due today"));
   } else {
    box.append(element("span", "sod-risk-due-soon-tag", "In " + row.days_due + "d"));
   }
   return box;
  };

  const money = (val, row) => row.amount != null ? format_currency(row.amount, data.currency) : "—";

  if (!risks.available) {
   riskPanel.append(UI.state("unavailable", { message: risks.reason }));
  } else if (risks.rows.length === 0) {
   riskPanel.append(UI.state("empty", { message: "No business risks or exceptions detected for the selected company and filters." }));
  } else {
   riskPanel.append(UI.recordList({
    label: "Business risks · " + (filters.risk_severity || "all severities") + " · " + (filters.risk_category || "all categories"),
    rows: risks.rows,
    columns: [
     { key: "severity", label: "Severity", render: renderSeverity },
     { key: "category", label: "Category" },
     { key: "title", label: "Exception & Impact", render: renderRiskItem },
     { key: "entity_name", label: "Source Record", render: renderEntity },
     { key: "due_date", label: "Target / Due Date", render: renderDueDate },
     { key: "amount", label: "Exposure / Amount", render: money },
     { key: "trigger_reason", label: "Documented Trigger" }
    ],
    rowActions: row => [{
     label: "Open " + row.entity_type,
     onActivate: () => frappe.set_route(row.drilldown.route)
    }],
    pagination: listPaging("risk", risks.has_next, "Showing " + risks.rows.length + " of " + risks.matching_count + " matching exceptions. Summary counts reflect the full cohort.")
   }));
  }
  section.append(riskPanel);

  // 3. Pending Approvals Queue
  const approvals = data.approvals;
  const approvalPanel = element("div", "sod-approvals-queue");
  approvalPanel.append(element("h3", "", "Pending approvals assigned to you"));
  approvalPanel.append(element("p", "sod-home-date-basis", approvals.basis));

  if (!approvals.available) {
   approvalPanel.append(UI.state("unavailable", { message: approvals.reason }));
  } else if (approvals.rows.length === 0) {
   approvalPanel.append(UI.state("empty", { message: "No pending approvals or workflow tasks currently assigned to your account." }));
  } else {
   approvalPanel.append(UI.recordList({
    label: "Assigned approvals & workflow tasks",
    rows: approvals.rows,
    columns: [
     { key: "doctype", label: "Document", render: (val, row) => row.doctype + ": " + row.docname },
     { key: "source_type", label: "Source" },
     { key: "status", label: "Workflow State", render: UI.status },
     { key: "description", label: "Description / Subject" },
     { key: "allocated_to", label: "Allocated To" },
     { key: "date", label: "Submission / Date" }
    ],
    rowActions: row => [{
     label: "Review in ERPNext",
     onActivate: () => frappe.set_route(row.drilldown.route)
    }],
    pagination: listPaging("approval", approvals.has_next, "Showing " + approvals.rows.length + " of " + approvals.matching_count + " assigned approvals.")
   }));
  }
  section.append(approvalPanel);

  return section;
 };
})();
