// One assistant follows the active dashboard; conversation survives navigation.
frappe.SarathiDashboardAssistant = class {
 static attach(host) {
  const assistant = frappe.sarathiDashboardAssistant ||= new this();
  assistant.host = host;
  assistant.initAiAssistant();
  document.getElementById("sarathiAiFab").style.display = "";
  assistant.refreshAiChips();
  return assistant;
 }
 static detach(host) {
  const assistant = frappe.sarathiDashboardAssistant;
  if (assistant?.host !== host) return;
  assistant.toggleAiChat(false);
  document.getElementById("sarathiAiFab")?.style.setProperty("display", "none");
  document.getElementById("sarathiLiveBanner")?.classList.remove("active");
  assistant.host = null;
 }
 get filters() { return this.host?.getFilters?.() || this.host?.filters || {}; }
 esc(value) { return frappe.utils.escape_html(String(value ?? "")); }
 el(selector) { return this.host?.root?.querySelector(selector); }
 load() {
  const host = this.host;
  if (!host) return;
  if (host.refreshCurrentPage) {
   host.refreshFilterDropdownsOnly();
   return host.refreshCurrentPage();
  }
  if (host.view === "accounting") return host.loadAccountingData(true);
  if (host.view === "subcontracting") return host.loadSubcontractingData(true);
  return host.load(true);
 }
	/* ==========================================================================
     Sarathi Industrial AI Agent Chatbot Methods (Ultra-Modern Live UI)
     ========================================================================== */
	initAiAssistant() {
		if (document.getElementById("sarathiAiFab")) return;

		// 1. Create Top Real-time Live Banner on Dashboard
		if (!document.getElementById("sarathiLiveBanner")) {
			const banner = document.createElement("div");
			banner.className = "sd-live-banner";
			banner.id = "sarathiLiveBanner";
			banner.innerHTML = `
        <span class="sd-live-beacon"></span>
        <span class="sd-live-banner-title">⚡ Real-time Live Change:</span>
        <span class="sd-live-banner-text" id="sarathiLiveBannerText">Record synchronized</span>
        <button type="button" class="sd-live-banner-btn" id="sarathiLiveBannerBtn">Inspect in Dashboard</button>
        <button type="button" class="sd-live-banner-close" id="sarathiLiveBannerClose">✕</button>
      `;
			document.body.appendChild(banner);
			document.getElementById("sarathiLiveBannerClose")?.addEventListener("click", () => {
				banner.classList.remove("active");
			});
		}

		// 2. Create Floating Action Button (FAB)
		const fab = document.createElement("button");
		fab.className = "sd-ai-fab";
		fab.id = "sarathiAiFab";
		fab.title = "Open Sarathi AI Assistant (Autonomous ERPNext v16)";
		fab.innerHTML = `
      <div class="sd-ai-fab-pulse"></div>
      <span class="sd-ai-fab-icon">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h2a5 5 0 0 1 5 5v1h1a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-1v1a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-1H3a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h1v-1a5 5 0 0 1 5-5h2V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2z" fill="#00f2fe"/>
          <circle cx="8.5" cy="13.5" r="1.5" fill="#0b1320"/>
          <circle cx="15.5" cy="13.5" r="1.5" fill="#0b1320"/>
          <path d="M9 17.5c1 .8 2 .8 3 .8s2 0 3-.8" stroke="#0b1320" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="sd-ai-fab-text">✨ AI Agent</span>
      <span class="sd-ai-fab-status-dot"></span>
    `;
		document.body.appendChild(fab);

		// 3. Create Chat Window
		const win = document.createElement("div");
		win.className = "sd-ai-chat-window";
		win.id = "sarathiAiChatWindow";
		win.style.display = "none";
		win.innerHTML = `
      <div class="sd-ai-chat-header">
        <div class="sd-ai-chat-header-title">
          <div class="sd-ai-avatar">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h2a5 5 0 0 1 5 5v1h1a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-1v1a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-1H3a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h1v-1a5 5 0 0 1 5-5h2V5.73A2 2 0 0 1 10 4a2 2 0 0 1 2-2z" fill="#00f2fe"/>
              <circle cx="8.5" cy="13.5" r="1.5" fill="#0b1320"/>
              <circle cx="15.5" cy="13.5" r="1.5" fill="#0b1320"/>
              <path d="M9 17.5c1 .8 2 .8 3 .8s2 0 3-.8" stroke="#0b1320" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="sd-ai-header-text">
            <h3>Sarathi Industrial AI Agent</h3>
            <p><span class="sd-ai-online-dot"></span> Online · ERPNext v16 Engine</p>
          </div>
        </div>
        <div class="sd-ai-chat-actions">
          <button class="sd-ai-btn-icon" id="sarathiAiClearBtn" title="Clear Conversation">🗑️</button>
          <button class="sd-ai-btn-icon" id="sarathiAiResetBtn" title="Reset Session">🔄</button>
          <button class="sd-ai-btn-icon" id="sarathiAiExpandBtn" title="Toggle Wide View">⛶</button>
          <button class="sd-ai-btn-icon" id="sarathiAiCloseBtn" title="Close">✕</button>
        </div>
      </div>
      <div class="sd-ai-chat-body" id="sarathiAiChatBody">
        <div class="sd-ai-msg sd-ai-msg-bot">
          👋 Hello! I am your <strong>Sarathi Industrial AI Agent</strong>.<br><br>
          I provide real-time execution across all 13 ERPNext modules and 98 sections:
          <ul class="sd-ai-ul">
            <li class="sd-ai-li"><strong>🚀 Create Entities:</strong> <em>'Create a project'</em>, <em>'New account setup'</em>, <em>'Add customer'</em>, <em>'New Work Order'</em></li>
            <li class="sd-ai-li"><strong>⚡ Live Changes:</strong> <em>'Show live changes'</em> to see real-time database activity</li>
            <li class="sd-ai-li"><strong>📦 Inventory & Stock:</strong> <em>'Check stock in Stores'</em></li>
          </ul>
          Click a quick action below or type your instruction!
        </div>
      </div>
      <div class="sd-ai-chips" id="sarathiAiChips"></div>
      <div class="sd-ai-chat-footer">
        <textarea class="sd-ai-input" id="sarathiAiInput" rows="1" placeholder="Ask AI... (e.g. 'Create a project', 'Show live changes')"></textarea>
        <button class="sd-ai-send-btn" id="sarathiAiSendBtn" title="Send Instruction">➤</button>
      </div>
    `;
		document.body.appendChild(win);

		// Event listeners
		fab.addEventListener("click", () => this.toggleAiChat());
		document
			.getElementById("sarathiAiCloseBtn")
			?.addEventListener("click", () => this.toggleAiChat(false));
		document.getElementById("sarathiAiClearBtn")?.addEventListener("click", () => {
			this.clearAiConversation();
		});
		document.getElementById("sarathiAiResetBtn")?.addEventListener("click", () => {
			this.sendAiMessage("reset");
		});
		document.getElementById("sarathiAiExpandBtn")?.addEventListener("click", () => {
			win.classList.toggle("sd-ai-expanded");
		});

		const input = document.getElementById("sarathiAiInput");
		const sendBtn = document.getElementById("sarathiAiSendBtn");

		const doSend = () => {
			const txt = input.value.trim();
			if (!txt) return;
			input.value = "";
			this.sendAiMessage(txt);
		};

		sendBtn?.addEventListener("click", doSend);
		input?.addEventListener("keydown", (e) => {
			if (e.key === "Enter" && !e.shiftKey) {
				e.preventDefault();
				doSend();
			}
		});

		this.refreshAiChips();
	}

	clearAiConversation() {
		frappe.call({
			method: "sarathi_visibility.api.agent_chat.send_message",
			args: { message: "reset" },
			callback: () => {},
		});
		const body = document.getElementById("sarathiAiChatBody");
		if (body) {
			body.innerHTML = `
        <div class="sd-ai-msg sd-ai-msg-bot">
          👋 Hello! I am your <strong>Sarathi Industrial AI Agent</strong>.<br><br>
          ✨ <strong>Conversation cleared.</strong> Ready for your next instruction across all 13 ERPNext modules:
          <ul class="sd-ai-ul">
            <li class="sd-ai-li"><strong>🏢 Create Company:</strong> <em>'I want to create a new company'</em></li>
            <li class="sd-ai-li"><strong>🚀 Create Project:</strong> <em>'I want to create a project'</em></li>
            <li class="sd-ai-li"><strong>⚡ Live Changes:</strong> <em>'Show live changes'</em> to see real-time database activity</li>
            <li class="sd-ai-li"><strong>📦 Inventory & Stock:</strong> <em>'Check stock in Stores'</em></li>
          </ul>
          Click a quick action below or type your instruction!
        </div>
      `;
		}
		const input = document.getElementById("sarathiAiInput");
		if (input) {
			input.value = "";
			input.focus();
		}
		frappe.show_alert({ message: "Conversation history cleared", indicator: "blue" }, 2);
	}

	toggleAiChat(open) {
		const win = document.getElementById("sarathiAiChatWindow");
		if (!win) return;
		const isVisible = win.style.display !== "none";
		const nextState = open !== undefined ? open : !isVisible;
		win.style.display = nextState ? "flex" : "none";
		if (nextState) {
			document.getElementById("sarathiAiInput")?.focus();
			this.refreshAiChips();
		}
	}

	triggerLiveBanner(doctype, name, title = "") {
		const banner = document.getElementById("sarathiLiveBanner");
		const textEl = document.getElementById("sarathiLiveBannerText");
		const btn = document.getElementById("sarathiLiveBannerBtn");
		if (!banner || !textEl) return;

		textEl.innerHTML = `Created <strong>${this.esc(
			doctype
		)}</strong> <code style="background:#022c22;color:#6ee7b7;padding:2px 6px;border-radius:4px;">${this.esc(
			name
		)}</code> ${title ? `(${this.esc(title)})` : ""} · Dashboard Synchronized`;
		banner.classList.add("active");

		if (btn) {
			btn.onclick = () => {
				this.highlightDashboardEntity(doctype);
			};
		}

		clearTimeout(this._liveBannerTimer);
		this._liveBannerTimer = setTimeout(() => {
			banner.classList.remove("active");
		}, 8000);
	}

	highlightDashboardEntity(doctype) {
		let target = null;
		const dt = String(doctype || "").toLowerCase();
		if (dt.includes("company") || dt.includes("organization")) {
			target = this.el('[data-filter="company"]');
		} else if (dt.includes("project")) {
			target = this.el("[data-project-panel]") || this.el("[data-projects]");
		} else if (dt.includes("customer")) {
			target = this.el("[data-customer-panel]") || this.el("[data-customers]");
		} else if (dt.includes("account") || dt.includes("cost center")) {
			target = this.el("[data-accounting-card-panel]") || this.el("[data-accounting-cards]");
		} else if (dt.includes("work order") || dt.includes("production")) {
			target = this.el("[data-live-projects]");
		}

		if (target) {
			target.scrollIntoView({ behavior: "smooth", block: "center" });
			target.classList.remove("sd-live-highlight-pulse");
			void target.offsetWidth; // trigger reflow
			target.classList.add("sd-live-highlight-pulse");
			setTimeout(() => {
				target.classList.remove("sd-live-highlight-pulse");
			}, 3000);
		}
	}

	refreshAiChips() {
		const chipsContainer = document.getElementById("sarathiAiChips");
		if (!chipsContainer) return;
		const chips = [
			{ label: "🏢 Create Company", query: "I want to create a new company" },
			{ label: "🚀 Create Project", query: "I want to create a project" },
			{ label: "⚡ Live Changes", query: "Show live changes" },
			{ label: "💼 New Account Setup", query: "I want to create new Account setup" },
			{ label: "👥 Add Customer", query: "Create a new customer" },
			{ label: "📦 Check Stock", query: "Check stock in Stores" },
			{ label: "🏭 List Work Orders", query: "Show all Work Orders" },
		];
		if (this.filters.project) {
			chips.unshift({
				label: `📊 Status of ${this.filters.project}`,
				query: `Check status of ${this.filters.project}`,
			});
		} else if (this.filters.customer) {
			chips.unshift({
				label: `📂 Projects for ${this.filters.customer}`,
				query: `Show projects for ${this.filters.customer}`,
			});
		}
		chipsContainer.innerHTML = chips
			.map(
				(c) =>
					`<button class="sd-ai-chip" data-ai-query="${this.esc(c.query)}">${this.esc(
						c.label
					)}</button>`
			)
			.join("");

		chipsContainer.querySelectorAll("[data-ai-query]").forEach((el) => {
			el.addEventListener("click", () => {
				this.sendAiMessage(el.dataset.aiQuery);
			});
		});
	}

	appendAiMessage(sender, text, payload = null) {
		const body = document.getElementById("sarathiAiChatBody");
		if (!body) return;
		const msg = document.createElement("div");
		msg.className = `sd-ai-msg ${sender === "user" ? "sd-ai-msg-user" : "sd-ai-msg-bot"}`;

		if (sender === "user") {
			msg.innerHTML = `<div class="sd-ai-user-bubble">${this.esc(text)}</div>`;
		} else if (payload && payload.status === "COMPLETED" && payload.verified === true) {
			// 1. MASTERPIECE COLORFUL SUCCESS CARD (STRICT READ-BACK VERIFIED)
			const dt = payload.doctype || "Document";
			const name = payload.name || "Record";
			const dtUrl = `/app/${dt.toLowerCase().replace(/\s+/g, "-")}/${encodeURIComponent(name)}`;
			const fields = payload.fields || {};

			let attrGrid = "";
			const fieldKeys = Object.keys(fields);
			if (fieldKeys.length) {
				attrGrid = `
          <div class="sd-ai-attr-grid">
            ${fieldKeys
				.slice(0, 6)
				.map(
					(k) => `
              <div class="sd-ai-attr-pill">
                <span>${this.esc(k)}</span>
                <strong>${this.esc(fields[k])}</strong>
              </div>
            `
				)
				.join("")}
          </div>
        `;
			}

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-success">
          <div class="sd-ai-card-header">
            <span class="sd-ai-card-badge-live">● LIVE IN ERPNEXT</span>
            <span class="sd-ai-card-badge-verified">✓ READ-BACK VERIFIED</span>
            <h4>✨ ${this.esc(dt)} Created!</h4>
          </div>
          <div class="sd-ai-card-body">
            <div class="sd-ai-id-row">
              <span class="sd-ai-id-label">Record ID:</span>
              <code class="sd-ai-id-code">${this.esc(name)}</code>
            </div>
            ${attrGrid}
            <div class="sd-ai-card-text">${this.renderMarkdownLite(text)}</div>
          </div>
          <div class="sd-ai-card-actions">
            <a href="${dtUrl}" target="_blank" rel="noopener" class="sd-ai-action-btn sd-ai-btn-primary">
              🚀 Open ${this.esc(dt)} in Desk ↗
            </a>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-ai-refresh>
              ↻ Refresh Dashboard
            </button>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-ai-highlight>
              ⚡ Highlight in Dashboard
            </button>
          </div>
        </div>
      `;

			msg.querySelector("[data-ai-refresh]")?.addEventListener("click", (e) => {
				const aiBtn = e.currentTarget || msg.querySelector("[data-ai-refresh]");
				if (aiBtn) aiBtn.classList.add("sd-spinning", "sod-spinning");
				const p = this.load();
				Promise.resolve(p).finally(() => {
					if (aiBtn) setTimeout(() => aiBtn.classList.remove("sd-spinning", "sod-spinning"), 600);
				});
				frappe.show_alert(
					{ message: "Dashboard reloaded with latest live records!", indicator: "green" },
					3
				);
			});
			msg.querySelector("[data-ai-highlight]")?.addEventListener("click", () => {
				this.highlightDashboardEntity(dt);
			});
		} else if (payload && payload.status === "COLLECTING_SLOTS") {
			// 2. INTERACTIVE QUESTIONNAIRE INTAKE CARD
			const dt = payload.doctype || payload.target_doctype || "Record";
			const missingDetails = payload.missing_details || [];
			const primaryMissing = missingDetails[0] ? missingDetails[0].label : "Name";
			const templateVal = `${primaryMissing}: `;

			const CURRENCY_LIST = [
				"INR",
				"USD",
				"EUR",
				"GBP",
				"AED",
				"SAR",
				"JPY",
				"CAD",
				"AUD",
				"SGD",
				"CHF",
				"CNY",
				"KWD",
				"QAR",
				"BHD",
				"OMR",
			];
			const COUNTRY_LIST = [
				"India",
				"United States",
				"United Kingdom",
				"United Arab Emirates",
				"Saudi Arabia",
				"Germany",
				"Canada",
				"Australia",
				"Singapore",
				"Japan",
				"France",
				"China",
				"Brazil",
				"South Africa",
			];

			const KNOWN_OPTIONS = {
				default_currency: CURRENCY_LIST,
				currency: CURRENCY_LIST,
				country: COUNTRY_LIST,
				company: ["SarathiAILabs"],
				customer_type: ["Company", "Individual"],
				supplier_type: ["Company", "Individual"],
				customer_group: [
					"All Customer Groups",
					"Commercial",
					"Individual",
					"Non Profit",
					"Government",
				],
				territory: ["All Territories", "India", "Rest Of The World"],
				supplier_group: [
					"All Supplier Groups",
					"Distributor",
					"Manufacturer",
					"Raw Material",
					"Services",
				],
				item_group: [
					"Products",
					"All Item Groups",
					"Raw Material",
					"Services",
					"Sub Assemblies",
					"Consumables",
				],
				stock_uom: ["Nos", "Box", "Kg", "Meter", "Unit", "Pair", "Set", "Hour"],
				uom: ["Nos", "Box", "Kg", "Meter", "Unit", "Pair", "Set", "Hour"],
				priority: ["Medium", "Low", "High", "Urgent"],
				status: ["Open", "Working", "Pending Review", "Overdue", "Completed", "Cancelled"],
				order_type: ["Sales", "Maintenance", "Shopping Cart"],
				material_request_type: [
					"Purchase",
					"Material Transfer",
					"Material Issue",
					"Manufacture",
					"Customer Provided",
				],
				stock_entry_type: [
					"Material Receipt",
					"Material Issue",
					"Material Transfer",
					"Manufacture",
					"Repack",
				],
				inspection_type: ["Incoming", "In Process", "Outgoing"],
				reference_type: [
					"Stock Entry",
					"Purchase Receipt",
					"Purchase Invoice",
					"Delivery Note",
					"Sales Invoice",
				],
				voucher_type: [
					"Journal Entry",
					"Bank Entry",
					"Cash Entry",
					"Credit Card Entry",
					"Debit Note",
					"Credit Note",
				],
				payment_type: ["Receive", "Pay", "Internal Transfer"],
				party_type: ["Customer", "Supplier", "Employee"],
				root_type: ["Expense", "Asset", "Liability", "Equity", "Income"],
				default_letter_head: ["", "Company Letterhead - Grey", "Standard Letterhead"],
				letter_head: ["", "Company Letterhead - Grey", "Standard Letterhead"],
				valuation_method: ["FIFO", "Moving Average", "LIFO"],
			};

			const formRowsHtml = missingDetails
				.map((m) => {
					const fieldKey = m.field;
					const fieldLabel = m.label || fieldKey.replace(/_/g, " ").toUpperCase();
					const isReqd = m.reqd !== false;
					const defaultVal = m.default !== undefined && m.default !== null ? m.default : "";
					let placeholder = m.hint || `Enter ${fieldLabel}`;

					const reqdBadge = isReqd
						? `<span style="color:#ef4444;font-weight:bold;margin-left:3px;">*</span>`
						: `<span style="color:#94a3b8;font-size:10.5px;font-weight:normal;margin-left:4px;">(Optional)</span>`;

					// Parse options (Array, newline-delimited string, or fallback to KNOWN_OPTIONS)
					let opts = null;
					if (Array.isArray(m.options) && m.options.length > 0) {
						opts = m.options;
					} else if (typeof m.options === "string" && m.options.trim()) {
						opts = m.options
							.split("\n")
							.map((s) => s.trim())
							.filter(Boolean);
					} else if (KNOWN_OPTIONS[fieldKey]) {
						opts = KNOWN_OPTIONS[fieldKey];
					}

					// 1. Dropdown select
					if (opts && opts.length > 0) {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <select class="sd-ai-intake-input sd-ai-intake-select" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(fieldLabel)}">
                ${opts
					.map(
						(opt) =>
							`<option value="${this.esc(opt)}" ${
								String(opt).toLowerCase() === String(defaultVal).toLowerCase()
									? "selected"
									: ""
							}>${this.esc(opt === "" ? "-- None --" : opt)}</option>`
					)
					.join("")}
              </select>
            </div>
          `;
					}

					// 2. Checkbox input
					if (m.fieldtype === "Check") {
						const isChecked = defaultVal == "1" || defaultVal === 1 || defaultVal === true;
						return `
            <div class="sd-ai-intake-form-row" style="margin-top:4px;">
              <label class="sd-ai-intake-label" style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                <input type="checkbox" class="sd-ai-intake-checkbox" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(fieldLabel)}" ${
							isChecked ? "checked" : ""
						} />
                <span>📌 ${this.esc(fieldLabel)} ${reqdBadge}</span>
              </label>
            </div>
          `;
					}

					// 3. Date input
					if (m.fieldtype === "Date") {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <input type="date" class="sd-ai-intake-input" data-intake-field="${this.esc(
					fieldKey
				)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
							fieldLabel
						)}" value="${this.esc(defaultVal)}" />
            </div>
          `;
					}

					// 4. Number / Float / Int / Currency input
					if (["Float", "Int", "Currency", "Percent"].includes(m.fieldtype)) {
						return `
            <div class="sd-ai-intake-form-row">
              <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
              <input type="number" step="${
					m.fieldtype === "Int" ? "1" : "0.01"
				}" class="sd-ai-intake-input" data-intake-field="${this.esc(
							fieldKey
						)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
							fieldLabel
						)}" placeholder="${this.esc(placeholder)}" value="${this.esc(defaultVal)}" />
            </div>
          `;
					}

					// 5. Standard Text Inputs
					if (fieldKey === "company_name")
						placeholder = "e.g. Gaurav Manufacture private limited company";
					else if (fieldKey === "abbr") placeholder = "Auto-generated (e.g. GMplc or gmpl)";
					else if (fieldKey === "project_name") placeholder = "e.g. Office Furniture 2026";
					else if (fieldKey === "customer_name") placeholder = "e.g. Zenith Robotics Ltd";
					else if (fieldKey === "supplier_name") placeholder = "e.g. Precision Fasteners Ltd";
					else if (fieldKey === "item_code") placeholder = "e.g. ITEM-MOTOR-01";
					else if (fieldKey === "warehouse_name") placeholder = "e.g. Finished Goods Pune";

					return `
          <div class="sd-ai-intake-form-row">
            <label class="sd-ai-intake-label">📌 ${this.esc(fieldLabel)} ${reqdBadge}</label>
            <input type="text" class="sd-ai-intake-input" data-intake-field="${this.esc(
				fieldKey
			)}" data-intake-reqd="${isReqd}" data-intake-label="${this.esc(
						fieldLabel
					)}" placeholder="${this.esc(placeholder)}" value="${this.esc(defaultVal)}" />
          </div>
        `;
				})
				.join("");

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-intake">
          <div class="sd-ai-intake-header">
            <h4>📋 Requirements Needed for ${this.esc(dt)}</h4>
            <span class="sd-ai-intake-badge">Slot Intake</span>
          </div>
          <div class="sd-ai-intake-desc">
            ${this.renderMarkdownLite(text)}
          </div>
          <div class="sd-ai-intake-form">
            ${formRowsHtml}
            <div class="sd-ai-intake-actions">
              <button type="button" class="sd-ai-action-btn sd-ai-btn-primary" data-intake-submit>
                🚀 Apply & Proceed
              </button>
              <button type="button" class="sd-ai-action-btn sd-ai-btn-secondary" data-intake-cancel>
                ✕ Cancel
              </button>
            </div>
          </div>
          <div style="margin-top:12px;font-size:11px;color:#94a3b8;">
            💬 <em>Or type directly in the chatbox below (e.g. <code>${this.esc(templateVal)}</code>)</em>
          </div>
        </div>
      `;

			// Auto-generate Abbreviation in real-time when user types company name (e.g. GMplc or gmpl)
			const compInp = msg.querySelector('[data-intake-field="company_name"]');
			const abbrInp = msg.querySelector('[data-intake-field="abbr"]');
			if (compInp && abbrInp) {
				compInp.addEventListener("input", () => {
					const raw = compInp.value.trim();
					if (raw) {
						const words = raw.split(/[\s\-_]+/).filter(Boolean);
						const genAbbr = words.map((w) => w.charAt(0)).join("");
						abbrInp.value = genAbbr;
					} else {
						abbrInp.value = "";
					}
				});
			}

			msg.querySelector("[data-intake-submit]")?.addEventListener("click", () => {
				const inputs = msg.querySelectorAll("[data-intake-field]");
				const vals = [];
				let missingReqd = false;
				let missingLabel = "";
				let primaryVal = "";
				const summaryParts = [];

				inputs.forEach((inp) => {
					let val = "";
					if (inp.type === "checkbox") {
						val = inp.checked ? "1" : "0";
					} else {
						val = inp.value.trim();
					}
					const fKey = inp.dataset.intakeField;
					const isReqd = inp.dataset.intakeReqd === "true";
					const fLabel = inp.dataset.intakeLabel || fKey;

					if (isReqd && !val) {
						missingReqd = true;
						if (!missingLabel) missingLabel = fLabel;
						inp.style.borderColor = "#ef4444";
					} else {
						inp.style.borderColor = "";
					}

					if (val) {
						vals.push(`${fKey}: ${val}`);
						if (
							!primaryVal &&
							[
								"company_name",
								"project_name",
								"customer_name",
								"supplier_name",
								"item_code",
								"warehouse_name",
								"subject",
								"email",
							].includes(fKey)
						) {
							primaryVal = val;
						} else if (fKey !== "doctype" && fKey !== "name") {
							summaryParts.push(`${fLabel}: ${val}`);
						}
					}
				});

				if (missingReqd) {
					frappe.show_alert(
						{ message: `Please enter mandatory field: ${missingLabel}`, indicator: "orange" },
						3
					);
					return;
				}

				if (vals.length > 0) {
					let displayText = vals.join(", ");
					if (primaryVal) {
						displayText =
							summaryParts.length > 0
								? `${primaryVal} (${summaryParts.slice(0, 3).join(", ")})`
								: primaryVal;
					}
					this.sendAiMessage(vals.join(", "), displayText);
				} else {
					frappe.show_alert(
						{
							message: "Please fill in the required field(s) or type in the chatbox below",
							indicator: "orange",
						},
						3
					);
				}
			});

			msg.querySelector("[data-intake-cancel]")?.addEventListener("click", () => {
				this.sendAiMessage("Cancel");
			});
		} else if (payload && payload.status === "AWAITING_CONFIRMATION") {
			// 3. INTERACTIVE PRE-MUTATION CONFIRMATION CARD
			const dt = payload.doctype || payload.target_doctype || "Record";
			const pValues = payload.pending_values || {};
			const actionSteps = payload.action_steps || [
				`${payload.module || dt} Skill loaded`,
				`${dt} DocType identified`,
				"Required fields available",
				"Permission checked",
				"Duplicate check completed",
			];

			const EXCLUDE_KEYS = new Set([
				"doctype",
				"name",
				"is_group",
				"allow_account_creation_against_child_company",
				"book_advance_payments_in_separate_party_account",
				"reconcile_on_advance_payment_date",
				"reconciliation_takes_effect_on",
				"auto_exchange_rate_revaluation",
				"submit_err_jv",
				"enable_perpetual_inventory",
				"enable_item_wise_inventory_account",
				"enable_provisional_accounting_for_non_stock_items",
				"valuation_method",
				"idx",
				"docstatus",
				"naming_series",
				"lft",
				"rgt",
				"old_parent",
				"disabled",
			]);

			let summaryHtml = "";
			const valKeys = Object.keys(pValues).filter(
				(k) =>
					!EXCLUDE_KEYS.has(k.toLowerCase()) &&
					pValues[k] !== undefined &&
					pValues[k] !== null &&
					pValues[k] !== ""
			);
			if (valKeys.length) {
				summaryHtml = `
          <div class="sd-ai-attr-grid" style="margin-top:10px;">
            ${valKeys
				.map(
					(k) => `
              <div class="sd-ai-attr-pill">
                <span>${this.esc(k.replace(/_/g, " ").toUpperCase())}</span>
                <strong>${this.esc(pValues[k])}</strong>
              </div>
            `
				)
				.join("")}
          </div>
        `;
			}

			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-confirmation">
          <div class="sd-ai-confirm-header">
            <h4>📋 Ready to Create: ${this.esc(dt)}</h4>
            <span class="sd-ai-card-badge-confirm">⚡ Validation Complete</span>
          </div>
          <div class="sd-ai-confirm-body">
            <div class="sd-ai-validation-checklist">
              ${actionSteps
					.map(
						(step) => `
                <div class="sd-ai-check-item">
                  <span class="sd-ai-check-icon">✓</span>
                  <span>${this.esc(step)}</span>
                </div>
              `
					)
					.join("")}
            </div>
            ${summaryHtml}
            <div class="sd-ai-confirm-callout">
              Ready to create the <strong>${this.esc(dt)}</strong> in ERPNext. Please confirm to proceed.
            </div>
          </div>
          <div class="sd-ai-card-actions">
            <button type="button" class="sd-ai-action-btn sd-ai-btn-confirm" data-ai-confirm>
              ✓ Confirm & Create
            </button>
            <button type="button" class="sd-ai-action-btn sd-ai-btn-cancel" data-ai-cancel>
              ✕ Cancel
            </button>
          </div>
        </div>
      `;

			msg.querySelector("[data-ai-confirm]")?.addEventListener("click", () => {
				this.sendAiMessage("Confirm");
			});
			msg.querySelector("[data-ai-cancel]")?.addEventListener("click", () => {
				this.sendAiMessage("Cancel");
			});
		} else if (payload && payload.status === "LIVE_CHANGES") {
			// 3. REAL-TIME ACTIVITY STREAM CARD
			const changes = payload.changes || [];
			msg.innerHTML = `
        <div class="sd-ai-card sd-ai-card-changes">
          <div class="sd-ai-changes-header">
            <h4>⚡ Live System Activity</h4>
            <span class="sd-ai-card-badge-live">● REAL-TIME FEED</span>
          </div>
          <div class="sd-ai-changes-list">
            ${
				changes
					.map(
						(c) => `
              <div class="sd-ai-change-item">
                <div>
                  <a href="${c.url}" target="_blank" rel="noopener">${this.esc(c.doctype)}: ${this.esc(
							c.name
						)}</a>
                  <div style="font-size:11px;color:#94a3b8;margin-top:2px;">${this.esc(c.title)}</div>
                </div>
                <span class="sd-pill sd-status-blue">${this.esc(c.status)}</span>
              </div>
            `
					)
					.join("") || '<div class="sd-empty">No recent changes found.</div>'
			}
          </div>
        </div>
      `;
		} else {
			// Default formatted bubble
			msg.innerHTML = `
        <div class="sd-ai-bot-bubble">
          ${this.renderMarkdownLite(text)}
        </div>
      `;
		}

		body.appendChild(msg);
		body.scrollTop = body.scrollHeight;
	}

	sendAiMessage(text, displayText = null) {
		this.appendAiMessage("user", displayText || text);
		const body = document.getElementById("sarathiAiChatBody");

		// Add animated Live Multi-Step Execution Indicator
		const typing = document.createElement("div");
		typing.className = "sd-ai-typing-indicator";
		typing.id = "sarathiAiTyping";
		typing.innerHTML = `
      <div class="sd-ai-typing-top">
        <div class="sd-ai-live-spinner"></div>
        <span class="sd-ai-step-text" id="sarathiAiStepText">🔮 Analyzing intent & scanning 13 modules…</span>
      </div>
      <div class="sd-ai-progress-track">
        <div class="sd-ai-progress-bar"></div>
      </div>
    `;
		body.appendChild(typing);
		body.scrollTop = body.scrollHeight;

		// Dynamic step text cycle while server computes
		const stepEl = typing.querySelector("#sarathiAiStepText");
		const steps = [
			"⚙️ Checking schema prerequisites & dependencies…",
			"🚀 Executing ERPNext database transaction…",
			"📊 Auto-synchronizing live dashboard data…",
		];
		let stepIdx = 0;
		const stepTimer = setInterval(() => {
			if (stepEl && steps[stepIdx]) {
				stepEl.textContent = steps[stepIdx];
				stepIdx = (stepIdx + 1) % steps.length;
			}
		}, 1200);

		frappe.call({
			method: "sarathi_visibility.api.agent_chat.send_message",
			args: {
				message: text,
				company: this.filters.company || "",
				customer: this.filters.customer || "",
				project: this.filters.project || "",
			},
			callback: (r) => {
				clearInterval(stepTimer);
				typing.remove();
				if (r.message && r.message.message) {
					this.appendAiMessage("bot", r.message.message, r.message);

					// LIVE REAL-TIME DASHBOARD SYNCHRONIZATION (ONLY WHEN BACKEND VERIFIED === TRUE)
					if (r.message.status === "COMPLETED" && r.message.verified === true) {
						const dt = r.message.doctype || "Record";
						const name = r.message.name || "";

						// 1. Show Top Floating Live Banner on Dashboard!
						this.triggerLiveBanner(dt, name);

						// 2. Flash Glowing Border on Dashboard Section!
						this.highlightDashboardEntity(dt);

						// 3. Show Native Frappe Alert!
						frappe.show_alert(
							{
								message: `<span style="font-weight:700;">⚡ Real-time Live Change:</span> ${dt} <strong>${name}</strong> created. Dashboard synchronized!`,
								indicator: "green",
							},
							5
						);

						// 4. Reload Dashboard Data Immediately!
						this.load();
					}
				} else {
					this.appendAiMessage("bot", "Received response from agent.");
				}
			},
			error: (err) => {
				clearInterval(stepTimer);
				typing.remove();
				this.appendAiMessage(
					"bot",
					"⚠️ Communication error with Sarathi AI Agent. Please check server logs."
				);
			},
		});
	}

	renderMarkdownLite(md) {
		if (!md) return "";
		let html = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

		// Bold
		html = html.replace(/\*\*(.+?)\*\*/g, "<strong class='sd-ai-bold'>$1</strong>");
		// Italic
		html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
		// Inline code
		html = html.replace(/`([^`]+)`/g, "<code class='sd-ai-code'>$1</code>");
		// Markdown links [text](url)
		html = html.replace(
			/\[([^\]]+)\]\(([^)]+)\)/g,
			'<a href="$2" target="_blank" rel="noopener" class="sd-ai-link">$1 ↗</a>'
		);
		// Blockquotes
		html = html.replace(/^>\s*(.+)$/gm, "<div class='sd-ai-quote'>$1</div>");
		// Lists
		html = html.replace(/^\s*-\s+(.+)$/gm, "<li class='sd-ai-li'>$1</li>");
		html = html.replace(/(<li class='sd-ai-li'>.+<\/li>)/gs, "<ul class='sd-ai-ul'>$1</ul>");
		// Numbered lists
		html = html.replace(
			/^\s*(\d+)\.\s+(.+)$/gm,
			"<div class='sd-ai-num-step'><span class='sd-ai-step-badge'>$1</span><span>$2</span></div>"
		);
		// Line breaks
		html = html.replace(/\n\n/g, "<div class='sd-ai-gap'></div>").replace(/\n/g, "<br>");
		return html;
	}
};
