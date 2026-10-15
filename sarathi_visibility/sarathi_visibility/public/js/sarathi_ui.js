/* Shared presentation only. No queries, permissions or business calculations. */
(() => {
 "use strict";
 let sequence = 0;
 const mounted = new WeakMap();
 const node = (tag, cls, text) => {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text !== undefined) el.textContent = String(text);
  return el;
 };
 const present = value => value !== null && value !== undefined && value !== "" && !(typeof value === "number" && !Number.isFinite(value));
 const destination = href => {
  if (!href) return null;
  try { const url = new URL(href, location.href); return ["http:", "https:"].includes(url.protocol) && url.origin === location.origin ? url.href : null; }
  catch (_) { return null; }
 };
 function action({ label, onActivate, href, disabled = false, confirm, tone = "secondary" }) {
  const url = destination(href);
  if (typeof onActivate !== "function" && !url) throw new TypeError("An action needs a callback or same-origin destination.");
  const el = node(url ? "a" : "button", "sui-action");
  const caption = node("span", "", label);
  const feedback = node("span", "sui-action-feedback");
  feedback.setAttribute("role", "status");
  el.dataset.tone = ["primary", "secondary", "danger"].includes(tone) ? tone : "secondary";
  if (url) el.href = url; else el.type = "button";
  el.append(caption, feedback);
  let busy = false;
  el.setAttribute("aria-disabled", String(disabled));
  if (!url) el.disabled = disabled;
  el.addEventListener("click", async event => {
   if (busy || disabled) { event.preventDefault(); return; }
   if (!onActivate) return;
   event.preventDefault(); busy = true;
   el.setAttribute("aria-busy", "true");
   el.setAttribute("aria-disabled", "true");
   if (!url) el.disabled = true;
   feedback.textContent = "Working…";
   try {
    if (confirm && !(await confirm())) { feedback.textContent = "Cancelled"; return; }
    const result = await onActivate(event);
    feedback.textContent = result === false ? "" : "Done";
   } catch (_) { feedback.textContent = "Could not complete. Check the record before trying again."; }
   finally { busy = false; el.removeAttribute("aria-busy"); el.setAttribute("aria-disabled", String(disabled)); if (!url) el.disabled = disabled; }
  });
  return el;
 }
 function state(kind = "empty", { message, retry, retryKind } = {}) {
  const messages = { loading: "Loading records…", empty: "No records found.", unavailable: "Data unavailable.", denied: "You do not have access to these records.", error: "Could not load records.", stale: "Showing previously loaded data.", offline: "You are offline. Check your connection." };
  const el = node("div", "sui-state");
  el.dataset.state = kind;
  el.setAttribute("role", kind === "error" ? "alert" : "status");
  if (kind === "loading") el.setAttribute("aria-busy", "true");
  // Only caller-authored business messages, never pass exception objects here.
  el.append(node("p", "", typeof message === "string" ? message : messages[kind] || messages.unavailable));
  if (retry && retryKind === "read") el.append(action({ label: "Retry loading", onActivate: retry }));
  return el;
 }
 function status(value, options = {}) {
  const label = present(value) ? String(value) : "Unavailable";
  const tone = /fail|block|reject|shortage|critical/i.test(label) ? "danger" : /cancel|stopped/i.test(label) ? "neutral" : /delay|overdue|wait|pending|hold|partially ready/i.test(label) ? "warning" : /complete|finish|closed|submitted|accepted|ready/i.test(label) ? "success" : /in progress|working|active|running|production/i.test(label) ? "info" : "neutral";
  const iconMap = { danger: "⛔", warning: "⚠", success: "✓", info: "⚙", neutral: "•" };
  const el = node("span", "sui-status", label);
  el.dataset.tone = tone;
  el.dataset.icon = options.icon || iconMap[tone] || "•";
  return el;
 }
 function severity(level) {
  const label = present(level) ? String(level) : "Informational";
  const iconMap = { Critical: "🔴", High: "🟠", Medium: "🔵", Low: "⚪", Informational: "ℹ" };
  const el = node("span", "sui-severity-badge", label);
  el.dataset.severity = label;
  el.dataset.icon = iconMap[label] || "•";
  el.setAttribute("aria-label", "Severity: " + label);
  return el;
 }
 function announce(message, priority = "polite") {
  if (!message) return;
  let announcer = document.getElementById("sui-live-announcer");
  if (!announcer) {
   announcer = document.createElement("div");
   announcer.id = "sui-live-announcer";
   announcer.className = "sui-sr-only";
   announcer.setAttribute("aria-live", priority);
   announcer.setAttribute("aria-atomic", "true");
   document.body.appendChild(announcer);
  }
  announcer.textContent = "";
  setTimeout(() => { announcer.textContent = String(message); }, 50);
 }
 function progress({ value, label = "Progress", text, status: suppliedStatus } = {}) {
  const valid = present(value) && Number.isFinite(Number(value));
  const el = node("div", "sui-progress");
  el.append(node("span", "sui-progress-label", label + ": " + (valid ? text || String(value) + "%" : "Unavailable")));
  if (valid) {
   const bar = node("div", "sui-progress-track");
   const fill = node("span", "sui-progress-fill");
   const width = Math.min(100, Math.max(0, Number(value)));
   bar.setAttribute("role", "progressbar");
   bar.setAttribute("aria-label", label); bar.setAttribute("aria-valuemin", "0"); bar.setAttribute("aria-valuemax", "100");
   bar.setAttribute("aria-valuenow", String(width)); bar.setAttribute("aria-valuetext", text || String(value) + "%");
   fill.style.width = width + "%"; bar.append(fill); el.append(bar);
  }
  if (suppliedStatus) el.append(status(suppliedStatus));
  return el;
 }
 function kpi({ label, value, unit, description, comparison, icon, onActivate, href, loading = false, error = false }) {
  const interactive = !loading && !error && (typeof onActivate === "function" || destination(href));
  const el = interactive ? action({ label: "", onActivate, href }) : node("article", "");
  el.classList.add("sui-kpi");
  el.prepend(node("span", "sui-kpi-label", label), node("strong", "sui-kpi-value", loading ? "Loading…" : error || !present(value) ? "—" : String(value) + (unit ? " " + unit : "")));
  if (icon instanceof Node) {
   const decoration = icon.cloneNode(true);
   decoration.setAttribute?.("aria-hidden", "true");
   el.querySelector(".sui-kpi-label").prepend(decoration);
  }
  if (interactive) el.setAttribute("aria-label", label + ": " + (present(value) ? value : "Unavailable") + ". View records");
  if (description || error) el.append(node("small", "", error ? "Data unavailable" : description));
  if (comparison) el.append(node("small", "", comparison));
  if (loading) el.setAttribute("aria-busy", "true");
  return el;
 }
 function header({ title, description, company, updatedAt, actions = [] }) {
  const el = node("header", "sui-header");
  const text = node("div", ""); text.append(node("h1", "", title));
  if (description) text.append(node("p", "", description));
  if (company) text.append(node("p", "", "Company: " + company));
  if (updatedAt && Number.isFinite(new Date(updatedAt).getTime())) text.append(node("p", "", "Updated " + new Date(updatedAt).toLocaleString()));
  el.append(text, ...actions); return el;
 }
 function layout({ title, description, company, updatedAt, actions, density = "standard" } = {}) {
  const el = node("section", "sui-layout"); el.dataset.sarathiUi = "";
  el.dataset.density = density === "shop-floor" ? "shop-floor" : "standard";
  if (title) el.append(header({ title, description, company, updatedAt, actions }));
  const content = node("div", "sui-content"); el.append(content); el.content = content; return el;
 }
 function filterBar({ fields = [], onApply, onReset, validate } = {}) {
  if (typeof onApply !== "function") throw new TypeError("Filters need an apply callback.");
  const form = node("form", "sui-filters"); const controls = new Map();
  for (const field of fields) {
   const label = node("label", "", field.label);
   const input = node(field.type === "select" ? "select" : "input", "");
   input.id = "sui-filter-" + ++sequence; label.htmlFor = input.id;
   if (input.tagName === "INPUT") input.type = ["date", "search", "number"].includes(field.type) ? field.type : "text";
   if (field.required) input.required = true;
   label.append(input); form.append(label); controls.set(field.key, input);
   if (field.type === "select") setOptions(field.key, field.options || [], field.optionState);
   input.value = field.value ?? "";
  }
  const feedback = node("p", "sui-filter-feedback"); feedback.setAttribute("role", "status"); form.append(feedback);
  const values = () => Object.fromEntries([...controls].map(([key, el]) => [key, el.value]));
  const apply = action({ label: "Apply filters", tone: "primary", onActivate: async () => {
   if (!form.reportValidity()) return false;
   const message = validate?.(values()); feedback.textContent = message || "";
   if (message) return false;
   await onApply(values());
  }});
  form.append(apply);
  if (onReset) form.append(action({ label: "Reset filters", onActivate: async () => {
   for (const field of fields) controls.get(field.key).value = field.value ?? "";
   feedback.textContent = ""; await onReset(values());
  }}));
  form.addEventListener("submit", event => { event.preventDefault(); apply.click(); });
  function setOptions(key, options, optionState) {
   const input = controls.get(key); const current = input.value;
   input.replaceChildren();
   const placeholder = node("option", "", optionState === "loading" ? "Loading options…" : optionState === "error" ? "Options unavailable" : options.length ? "All" : "No options available");
   placeholder.value = ""; input.append(placeholder);
   for (const option of options) { const el = node("option", "", option.label); el.value = option.value; input.append(el); }
   input.disabled = optionState === "loading" || optionState === "error" || !options.length;
   input.value = current;
  }
  form.values = values; form.setOptions = setOptions; return form;
 }
 function recordList({ columns = [], rows = [], mode = "cards", label = "Records", state: currentState, onSearch, onSort, pagination, rowActions } = {}) {
  const el = node("section", "sui-record-list");
  if (onSearch) { const input = node("input", ""); input.type = "search"; input.setAttribute("aria-label", "Search " + label); input.addEventListener("input", () => onSearch(input.value)); el.append(input); }
  if (currentState || !rows.length) { el.append(state(currentState || "empty")); return el; }
  if (onSort) {
   const sorts = node("div", "sui-sort-actions");
   for (const col of columns.filter(col => col.sortable)) sorts.append(action({ label: "Sort by " + col.label, onActivate: () => onSort(col.key) }));
   el.append(sorts);
  }
  const region = node("div", "sui-table-region"); region.tabIndex = 0; region.setAttribute("role", "region"); region.setAttribute("aria-label", label);
  const table = node("table", "sui-table"); table.dataset.mobile = mode;
  const caption = node("caption", "", label); table.append(caption);
  const head = node("thead", ""), heading = node("tr", "");
  for (const col of columns) { const th = node("th", "", col.label); th.scope = "col"; heading.append(th); }
  if (rowActions) heading.append(node("th", "", "Actions"));
  head.append(heading); table.append(head); const body = node("tbody", "");
  for (const row of rows) {
   const tr = node("tr", "");
   for (const col of columns) { const td = node("td", ""); td.dataset.label = col.label; const value = col.render ? col.render(row[col.key], row) : row[col.key]; td.append(value instanceof Node ? value : document.createTextNode(present(value) ? String(value) : "—")); tr.append(td); }
   if (rowActions) { const td = node("td", ""); td.dataset.label = "Actions"; td.append(...rowActions(row).map(action)); tr.append(td); }
   body.append(tr);
  }
  table.append(body); region.append(table); el.append(region);
  if (pagination) {
   el.append(node("p", "", pagination.label || ""));
   if (pagination.previous) el.append(action({ label: "Previous page", onActivate: pagination.previous }));
   if (pagination.next) el.append(action({ label: "Next page", onActivate: pagination.next }));
  }
  return el;
 }
 function chart({ title, description, render, state: currentState, dataTable } = {}) {
  const el = node("section", "sui-chart");
  el.setAttribute("role", "region");
  el.setAttribute("aria-label", title ? title + " Chart" : "Data Chart");
  if (title) el.append(node("h2", "", title));
  if (description) el.append(node("p", "", description));
  const canvas = node("div", "sui-chart-canvas");
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", (title || "Data visualization") + (description ? ": " + description : ""));
  el.append(canvas);
  if (currentState) canvas.append(state(currentState));
  if (dataTable && Array.isArray(dataTable.columns) && Array.isArray(dataTable.rows)) {
   const tableWrap = node("div", "sui-chart-table-wrap sui-sr-only");
   const t = node("table", "");
   t.append(node("caption", "", (title || "Chart") + " Data"));
   const head = node("thead", "");
   const trH = node("tr", "");
   for (const col of dataTable.columns) {
    const th = node("th", "", col.label || col);
    th.setAttribute("scope", "col");
    trH.append(th);
   }
   head.append(trH); t.append(head);
   const tb = node("tbody", "");
   for (const row of dataTable.rows) {
    const tr = node("tr", "");
    for (const col of dataTable.columns) {
     const key = col.key || col;
     tr.append(node("td", "", String(row[key] ?? "—")));
    }
    tb.append(tr);
   }
   t.append(tb); tableWrap.append(t);
   el.append(tableWrap);
  }
  el.mount = () => { if (!currentState && render) { el.dispose?.(); const instance = render(canvas); el.dispose = observeChart(canvas, instance); } };
  return el;
 }
 function observeChart(el, instance) {
  // Installed Frappe Charts already observes its parent. Do not draw twice during resize.
  if (instance?.resizeObserver) return () => instance.destroy?.();
  let last = 0; let frame;
  const observer = new ResizeObserver(entries => {
   const width = Math.round(entries[0].contentRect.width);
   if (!width || width === last) return; last = width;
   cancelAnimationFrame(frame); frame = requestAnimationFrame(() => { if (typeof instance?.resize === "function") instance.resize(); });
  });
  observer.observe(el); return () => { observer.disconnect(); cancelAnimationFrame(frame); };
 }
 function formatTimestamp(dateOrIso, options = {}) {
  const fallback = options.fallback !== undefined ? options.fallback : (!dateOrIso ? "Not yet loaded" : "--");
  if (!dateOrIso) return fallback;
  try {
   if (window.frappe?.datetime?.str_to_user && typeof dateOrIso === "string" && /^\d{4}-\d{2}-\d{2}/.test(dateOrIso)) {
    return frappe.datetime.str_to_user(dateOrIso);
   }
   const d = dateOrIso instanceof Date ? dateOrIso : new Date(dateOrIso);
   if (!Number.isFinite(d.getTime())) return fallback;
   if (options.timeOnly) {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
   }
   if (options.includeDate) {
    return d.toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" }) + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
   }
   return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch (_) {
   return fallback;
  }
 }
 function refreshStatus({ status: currentStatus = "idle", lastSuccess, lastAttempt, onRetry, label } = {}) {
  const el = node("div", "sui-refresh-status");
  el.dataset.status = currentStatus;
  el.setAttribute("role", currentStatus === "error" ? "alert" : "status");
  el.setAttribute("aria-live", "polite");

  const pulse = node("span", "sui-pulse-dot");
  pulse.setAttribute("aria-hidden", "true");
  el.append(pulse);

  let text = "";
  const successTime = lastSuccess ? formatTimestamp(lastSuccess) : null;

  if (currentStatus === "loading") {
   text = successTime ? `Refreshing… (Last updated: ${successTime})` : "Refreshing…";
   el.setAttribute("aria-busy", "true");
  } else if (currentStatus === "success") {
   text = successTime ? `Last updated: ${successTime}` : "Updated";
  } else if (currentStatus === "stale") {
   text = successTime ? `Refresh failed · Showing data from ${successTime}` : "Showing previously loaded data";
   const badge = node("span", "sui-stale-badge", "Stale");
   badge.setAttribute("role", "note");
   el.append(badge);
  } else if (currentStatus === "error") {
   text = successTime ? `Refresh failed. Showing data from ${successTime}.` : "Unable to load data. Please try again.";
  } else if (currentStatus === "unconfigured") {
   text = "Feature not configured.";
  } else if (currentStatus === "denied") {
   text = "You do not have permission to view this data.";
  } else {
   text = "Not yet loaded";
  }

  const labelEl = node("span", "sui-refresh-label", label ? `${label}: ${text}` : text);
  el.append(labelEl);

  if ((currentStatus === "error" || currentStatus === "stale") && typeof onRetry === "function") {
   const retryBtn = action({ label: "Retry", tone: "secondary", onActivate: onRetry });
   retryBtn.classList.add("sui-refresh-retry-btn");
   el.append(retryBtn);
  }

  return el;
 }
 function staleNotice({ message, lastSuccess, onRetry } = {}) {
  const el = node("div", "sui-stale-banner");
  el.setAttribute("role", "alert");
  const time = lastSuccess ? formatTimestamp(lastSuccess) : null;
  const msgText = message || (time ? `Refresh failed. Showing data from last successful update (${time}).` : "Refresh failed. Showing previously loaded data.");
  const p = node("p", "sui-stale-text", msgText);
  el.append(p);
  if (typeof onRetry === "function") {
   el.append(action({ label: "Retry refresh", onActivate: onRetry }));
  }
  return el;
 }
 function enhance(root) {
  if (mounted.has(root)) return mounted.get(root);
  root.dataset.sarathiUi = "";
  function disclosure(selector, label) {
   const target = root.querySelector(selector); if (!target) return;
   target.id ||= "sui-panel-" + ++sequence;
   const button = node("button", "sui-disclosure", label); button.type = "button";
   button.setAttribute("aria-controls", target.id); button.setAttribute("aria-expanded", "false");
   target.before(button); target.classList.add("sui-collapsible");
   button.addEventListener("click", () => { const open = button.getAttribute("aria-expanded") !== "true"; button.setAttribute("aria-expanded", String(open)); target.classList.toggle("sui-open", open); });
  }
  disclosure("#sod-filters, .sd-controls", "Filters"); disclosure(".sod-side", "Dashboard menu");
  const prepare = () => {
   for (const table of root.querySelectorAll("table")) {
    const region = table.parentElement;
    if (!region || region.matches("td,th")) continue;
    region.classList.add("sui-table-region"); region.setAttribute("role", "region");
    region.setAttribute("aria-label", "Dashboard records; scroll for more columns"); region.tabIndex = 0;
    for (const th of table.querySelectorAll("thead th")) {
     if (!th.getAttribute("scope")) th.setAttribute("scope", "col");
    }
    if (!table.getAttribute("aria-label") && !table.querySelector("caption")) {
     const heading = region.closest("section, div")?.querySelector("h1, h2, h3, h4");
     table.setAttribute("aria-label", heading ? heading.textContent.trim() + " Table" : "Dashboard Records");
    }
   }
   for (const svg of root.querySelectorAll("svg")) {
    if (!svg.getAttribute("aria-hidden") && !svg.getAttribute("role") && !svg.getAttribute("aria-label")) {
     svg.setAttribute("aria-hidden", "true");
     svg.setAttribute("focusable", "false");
    }
   }
  };
  prepare(); const observer = new MutationObserver(prepare); observer.observe(root, { childList: true, subtree: true });
  const keyboard = event => {
   const target = event.target.closest('[role="button"], [tabindex="0"][data-action], .sd-kpi[tabindex="0"], .sf-subview-tab');
   if (target && !target.matches("button,a,input,select,textarea") && event.target === target && ["Enter", " "].includes(event.key)) {
    event.preventDefault(); target.click();
   }
  };
  root.addEventListener("keydown", keyboard);
  const handle = { dispose: () => { observer.disconnect(); root.removeEventListener("keydown", keyboard); mounted.delete(root); } };
  mounted.set(root, handle); return handle;
 }
 window.frappe ||= {};
 frappe.sarathiUI = { action, state, status, severity, progress, kpi, header, layout, filterBar, recordList, chart, observeChart, enhance, announce, formatTimestamp, refreshStatus, staleNotice };
})();
