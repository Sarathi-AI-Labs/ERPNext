/* global frappe, __ */
frappe.provide("frappe");

/**
 * DASH-023: Mobile-First Shop-Floor Workboard Controller
 * Provides operational job queue, active operation highlighting, blocker alerts,
 * and role-appropriate assignment navigation for shop-floor operators and supervisors.
 */
frappe.SarathiShopFloorWorkboard = class SarathiShopFloorWorkboard {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.root = this.wrapper.find(".sarathi-shopfloor-app");
		this.data = null;
		this.activeStatusFilter = "All";
		this.searchQuery = "";
		this.isLoading = false;
		this.setup();
	}

	setup() {
		// Cache UI elements
		this.userRoleTag = this.root.find("[data-user-role]");
		this.userNameTag = this.root.find("[data-user-name]");
		this.refreshBtn = this.root.find("[data-refresh-btn]");
		this.refreshTimeTag = this.root.find("[data-refresh-time]");

		// KPIs
		this.kpiAssigned = this.root.find("[data-kpi-assigned]");
		this.kpiProgress = this.root.find("[data-kpi-progress]");
		this.kpiWaiting = this.root.find("[data-kpi-waiting]");
		this.kpiCompleted = this.root.find("[data-kpi-completed]");
		this.kpiBlocked = this.root.find("[data-kpi-blocked]");

		// Current operation
		this.currentOpContainer = this.root.find("[data-current-op-container]");
		this.currentOpBadge = this.root.find("[data-current-op-badge]");

		// Blockers
		this.blockersWrapper = this.root.find("[data-blockers-wrapper]");
		this.blockersList = this.root.find("[data-blockers-list]");
		this.blockerCount = this.root.find("[data-blocker-count]");

		// Queue
		this.jobsBadge = this.root.find("[data-jobs-badge]");
		this.jobsContainer = this.root.find("[data-jobs-container]");
		this.emptyState = this.root.find("[data-empty-state]");
		this.emptyTitle = this.root.find("[data-empty-title]");
		this.emptyDesc = this.root.find("[data-empty-desc]");
		this.clearFiltersBtn = this.root.find("[data-clear-filters]");

		// Filters & Search
		this.statusPills = this.root.find("[data-filter-status]");
		this.jobSearchInput = this.root.find("[data-job-search]");
		this.clearSearchBtn = this.root.find("[data-clear-search]");

		// DASH-026 Subview Elements
		this.subviewBar = this.root.find("[data-subview-bar]");
		this.subviewTabs = this.root.find("[data-subview]");
		this.operatorSubview = this.root.find("[data-operator-subview]");
		this.supervisorSubview = this.root.find("[data-supervisor-subview]");
		this.activeSubview = "operator";
		this.supervisorData = null;
		this._initialSubviewSet = false;

		// Supervisor Toolbar & Filters
		this.supScopeLabel = this.root.find("[data-sup-scope-label]");
		this.supResetFiltersBtn = this.root.find("[data-sup-reset-filters]");
		this.supFromDate = this.root.find("[data-sup-from-date]");
		this.supToDate = this.root.find("[data-sup-to-date]");
		this.supOpSelect = this.root.find("[data-sup-op-select]");
		this.supWsSelect = this.root.find("[data-sup-ws-select]");
		this.supStatusSelect = this.root.find("[data-sup-status-select]");
		this.supSearchInput = this.root.find("[data-sup-search]");
		this.supClearSearchBtn = this.root.find("[data-sup-clear-search]");

		// Supervisor Unconfigured State
		this.supUnconfiguredCard = this.root.find("[data-sup-unconfigured]");
		this.supUnconfiguredText = this.root.find("[data-sup-unconfigured-text]");

		// Supervisor 9 KPIs
		this.supKpiMembers = this.root.find("[data-sup-kpi-members]");
		this.supKpiActiveOps = this.root.find("[data-sup-kpi-active-ops]");
		this.supKpiWithJobs = this.root.find("[data-sup-kpi-with-jobs]");
		this.supKpiWithoutWork = this.root.find("[data-sup-kpi-without-work]");
		this.supKpiActiveJcs = this.root.find("[data-sup-kpi-active-jcs]");
		this.supKpiWaitingJcs = this.root.find("[data-sup-kpi-waiting-jcs]");
		this.supKpiCompletedJcs = this.root.find("[data-sup-kpi-completed-jcs]");
		this.supKpiBlockedJcs = this.root.find("[data-sup-kpi-blocked-jcs]");
		this.supKpiOverdueJcs = this.root.find("[data-sup-kpi-overdue-jcs]");

		// Supervisor Containers
		this.supWorkloadContainer = this.root.find("[data-sup-workload-container]");
		this.supWorkloadCount = this.root.find("[data-sup-workload-count]");
		this.supActiveContainer = this.root.find("[data-sup-active-container]");
		this.supActiveCount = this.root.find("[data-sup-active-count]");
		this.supBlockersWrapper = this.root.find("[data-sup-blockers-wrapper]");
		this.supBlockersList = this.root.find("[data-sup-blockers-list]");
		this.supBlockersCount = this.root.find("[data-sup-blockers-count]");
		this.supCompletedContainer = this.root.find("[data-sup-completed-container]");
		this.supCompletedCount = this.root.find("[data-sup-completed-count]");
		this.supWorkstationsContainer = this.root.find("[data-sup-workstations-container]");
		this.supWorkstationsCount = this.root.find("[data-sup-workstations-count]");

		this.bindEvents();
	}

	bindEvents() {
		// Refresh
		this.refreshBtn.on("click", () => this.refresh());

		// DASH-026 Subview tab switching
		this.subviewTabs.on("click", (e) => {
			const subview = $(e.currentTarget).attr("data-subview");
			this.switchSubview(subview);
		});

		// Supervisor filter events
		this.supFromDate.on("change", () => this.fetchSupervisorOverview());
		this.supToDate.on("change", () => this.fetchSupervisorOverview());
		this.supOpSelect.on("change", () => this.fetchSupervisorOverview());
		this.supWsSelect.on("change", () => this.fetchSupervisorOverview());
		this.supStatusSelect.on("change", () => this.fetchSupervisorOverview());

		let supSearchTimer = null;
		this.supSearchInput.on("input", (e) => {
			const val = ($(e.target).val() || "").trim();
			if (val) {
				this.supClearSearchBtn.show();
			} else {
				this.supClearSearchBtn.hide();
			}
			clearTimeout(supSearchTimer);
			supSearchTimer = setTimeout(() => {
				this.fetchSupervisorOverview();
			}, 300);
		});

		this.supClearSearchBtn.on("click", () => {
			this.supSearchInput.val("");
			this.supClearSearchBtn.hide();
			this.fetchSupervisorOverview();
		});

		this.supResetFiltersBtn.on("click", () => {
			this.supFromDate.val("");
			this.supToDate.val("");
			this.supOpSelect.val("");
			this.supWsSelect.val("");
			this.supStatusSelect.val("All");
			this.supSearchInput.val("");
			this.supClearSearchBtn.hide();
			this.fetchSupervisorOverview();
		});

		// Status filter pills
		this.statusPills.on("click", (e) => {
			const target = $(e.currentTarget);
			this.statusPills.removeClass("active");
			target.addClass("active");
			this.activeStatusFilter = target.attr("data-filter-status") || "All";
			this.renderJobCards();
		});

		// Search input
		this.jobSearchInput.on("input", (e) => {
			this.searchQuery = ($(e.target).val() || "").trim().toLowerCase();
			if (this.searchQuery) {
				this.clearSearchBtn.show();
			} else {
				this.clearSearchBtn.hide();
			}
			this.renderJobCards();
		});

		// Clear search
		this.clearSearchBtn.on("click", () => {
			this.jobSearchInput.val("");
			this.searchQuery = "";
			this.clearSearchBtn.hide();
			this.renderJobCards();
		});

		// Clear all filters
		this.clearFiltersBtn.on("click", () => {
			this.activeStatusFilter = "All";
			this.searchQuery = "";
			this.jobSearchInput.val("");
			this.clearSearchBtn.hide();
			this.statusPills.removeClass("active");
			this.root.find('[data-filter-status="All"]').addClass("active");
			this.renderJobCards();
		});

		// DASH-025 Shop-Floor Reporting Actions
		this.root.on("click", "[data-action]", (e) => {
			e.preventDefault();
			const btn = $(e.currentTarget);
			const action = btn.attr("data-action");
			const jobCard = btn.attr("data-job");
			const forQty = parseFloat(btn.attr("data-for") || "0");
			const completedQty = parseFloat(btn.attr("data-completed") || "0");
			const stockUom = btn.attr("data-uom") || "Nos";

			if (!jobCard) return;

			if (action === "start-job") {
				this.handleStartJob(jobCard, btn);
			} else if (action === "report-progress") {
				this.handleReportProgress(jobCard, forQty, completedQty, stockUom, btn);
			} else if (action === "pause-job") {
				this.handlePauseJob(jobCard, btn);
			} else if (action === "resume-job") {
				this.handleResumeJob(jobCard, btn);
			} else if (action === "stop-job") {
				this.handleStopJob(jobCard, stockUom, btn);
			} else if (action === "complete-job") {
				this.handleCompleteJob(jobCard, forQty, completedQty, stockUom, btn);
			}
		});
	}

	show() {
		this.wrapper.show();
		this.refresh();
	}

	hide() {
		this.wrapper.hide();
	}

	formatTime(date) {
		if (!date) return "--";
		const d = date instanceof Date ? date : new Date(date);
		return Number.isFinite(d.getTime()) ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "--";
	}

	async refresh() {
		if (this.isLoading) return;
		this.isLoading = true;
		this.refreshBtn.addClass("sf-spinning");
		const prevTimeStr = this.lastSuccessfulRefresh ? this.formatTime(this.lastSuccessfulRefresh) : null;
		this.refreshTimeTag.text(prevTimeStr ? `Refreshing… (${prevTimeStr})` : "Refreshing…");

		try {
			const res = await frappe.call({
				method: "sarathi_visibility.api.shopfloor.get_shopfloor_workboard",
				args: {},
			});

			if (res && res.message) {
				this.data = res.message;
				this.lastSuccessfulRefresh = new Date();
				this.lastFailedRefresh = null;
				this.render();
				this.root.find("[data-sf-stale-banner]").remove();
				this.refreshTimeTag.text(this.formatTime(this.lastSuccessfulRefresh));
				frappe.sarathiUI?.announce?.("Shop-Floor Workboard refreshed.");
			}
		} catch (err) {
			console.error("Shop-Floor Workboard fetch failed:", err);
			this.lastFailedRefresh = new Date();
			if (this.data && this.lastSuccessfulRefresh) {
				const staleTime = this.formatTime(this.lastSuccessfulRefresh);
				this.refreshTimeTag.text(`${staleTime} (Stale)`);
				if (!this.root.find("[data-sf-stale-banner]").length) {
					const banner = $(`
						<div class="sui-stale-banner" data-sf-stale-banner role="alert" style="margin: 12px 24px;">
							<p style="margin:0;">Refresh failed. Showing shop-floor records from last successful update (${staleTime}).</p>
							<button type="button" class="sf-btn sf-btn-primary" style="margin-left:auto; min-height:36px; padding:4px 12px;" data-action="retry-workboard">Retry</button>
						</div>
					`);
					banner.find("[data-action='retry-workboard']").on("click", () => this.refresh());
					this.root.find(".sf-last-refreshed-bar").after(banner);
				}
			} else {
				this.data = null;
				this.refreshTimeTag.text("Data unavailable");
				this.root.find(".sf-main-content").html(`
					<div class="sui-state" data-state="error" role="alert" style="margin:24px;">
						<p style="margin:0 0 12px;">Could not load shop-floor workboard. Please verify your connection and try again.</p>
						<button type="button" class="sf-btn sf-btn-primary" data-action="retry-workboard">Retry</button>
					</div>
				`);
				this.root.find("[data-action='retry-workboard']").on("click", () => this.refresh());
			}
			frappe.show_alert({
				message: __("Failed to refresh shop-floor data. Please check your connection."),
				indicator: "red",
			});
			frappe.sarathiUI?.announce?.("Failed to refresh shop-floor data.", "assertive");
		} finally {
			this.isLoading = false;
			this.refreshBtn.removeClass("sf-spinning");
		}
	}

	render() {
		if (!this.data) return;

		// 1. User Context
		const ctx = this.data.user_context || {};
		this.userRoleTag.text(ctx.role_label || "Operator");
		const fullName = ctx.user_name || ctx.user_id || "";
		const empInfo = ctx.employee_id ? ` &middot; ${frappe.utils.escape_html(ctx.employee_id)}` : "";
		this.userNameTag.html(`${frappe.utils.escape_html(fullName)}${empInfo}`);

		// 2. Summary KPIs
		const s = this.data.summary || {};
		this.kpiAssigned.text(s.total_assigned_jobs || 0);
		this.kpiProgress.text(s.jobs_in_progress || 0);
		this.kpiWaiting.text(s.waiting_jobs || 0);
		this.kpiCompleted.text(s.completed_jobs || 0);
		this.kpiBlocked.text(s.blocked_jobs || 0);

		// 3. Pill Counts
		const allJobs = this.data.assigned_jobs || [];
		const wipCount = allJobs.filter(j => j.status === "Work In Progress").length;
		const openCount = allJobs.filter(j => j.status === "Open").length;
		const blockedCount = allJobs.filter(j => j.has_blocker).length;
		const compCount = allJobs.filter(j => j.status === "Completed").length;

		this.root.find("[data-count-all]").text(allJobs.length);
		this.root.find("[data-count-wip]").text(wipCount);
		this.root.find("[data-count-open]").text(openCount);
		this.root.find("[data-count-blocked]").text(blockedCount);
		this.root.find("[data-count-completed]").text(compCount);

		// 4. Current Operation
		this.renderCurrentOperation();

		// 5. Blockers
		this.renderBlockers();

		// 6. Job Cards Queue
		this.renderJobCards();

		// 7. DASH-026: Subview Gating & Initial Display
		if (ctx.is_supervisor || ctx.is_manager) {
			this.subviewBar.show();
			if (!this._initialSubviewSet) {
				this._initialSubviewSet = true;
				this.switchSubview("supervisor");
			} else if (this.activeSubview === "supervisor") {
				this.fetchSupervisorOverview();
			}
		} else {
			this.subviewBar.hide();
			this.switchSubview("operator");
		}
	}

	renderCurrentOperation() {
		const activeOps = this.data.active_operations || (this.data.current_operation ? [this.data.current_operation] : []);
		const nextQueued = this.data.next_queued_job;

		if (activeOps.length > 0) {
			const badgeText = activeOps.length === 1 ? "Active Operation" : `${activeOps.length} Active Operations`;
			this.currentOpBadge.text(badgeText).attr("class", "sf-live-badge sf-live-pulse");

			const cardsHtml = activeOps.map(op => {
				const fq = op.for_quantity || 0;
				const cq = op.total_completed_qty || 0;
				const pct = op.completion_percent || 0;
				const rem = op.remaining_qty || 0;
				const uom = frappe.utils.escape_html(op.stock_uom || "Nos");

				return `
					<div class="sf-active-card">
						<div class="sf-active-header">
							<div class="sf-active-title-group">
								<span class="sf-status-tag sf-status-wip">In Progress</span>
								<h3 class="sf-active-op-title">${frappe.utils.escape_html(op.operation || "Operation")}</h3>
								<span class="sf-station-badge">${frappe.utils.escape_html(op.workstation || "Unassigned Station")}</span>
							</div>
							<div class="sf-active-actions">
								<a href="${op.drill_down_link}" class="sf-btn sf-btn-primary sf-touch-btn" target="_blank" rel="noopener">
									<span>Open Job Card (${frappe.utils.escape_html(op.name)})</span>
									<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
										<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
										<polyline points="15 3 21 3 21 9"></polyline>
										<line x1="10" y1="14" x2="21" y2="3"></line>
									</svg>
								</a>
							</div>
						</div>

						<div class="sf-active-body">
							<div class="sf-active-meta">
								<div class="sf-meta-item">
									<span class="sf-meta-label">Work Order</span>
									<a href="${op.work_order_link || '#'}" class="sf-meta-link">${frappe.utils.escape_html(op.work_order || "--")}</a>
								</div>
								<div class="sf-meta-item">
									<span class="sf-meta-label">Production Item</span>
									<span class="sf-meta-val">${frappe.utils.escape_html(op.item_name || op.production_item || "--")}</span>
								</div>
								<div class="sf-meta-item">
									<span class="sf-meta-label">Started At</span>
									<span class="sf-meta-val">${op.actual_start_date || op.expected_start_date || "Today"}</span>
								</div>
								<div class="sf-meta-item">
									<span class="sf-meta-label">Target Completion</span>
									<span class="sf-meta-val">${op.expected_end_date || "Not Specified"}</span>
								</div>
							</div>

							<div class="sf-progress-block">
								<div class="sf-progress-labels">
									<span>Output Progress: <strong>${cq}</strong> of <strong>${fq} ${uom}</strong></span>
									<span><strong>${pct}%</strong> (${rem} ${uom} remaining)</span>
								</div>
								<div class="sf-progress-track">
									<div class="sf-progress-bar" style="width: ${Math.min(pct, 100)}%;"></div>
								</div>
							</div>

							${op.has_blocker ? `
								<div class="sf-card-blocker-alert">
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
										<circle cx="12" cy="12" r="10"></circle>
										<line x1="12" y1="8" x2="12" y2="12"></line>
										<line x1="12" y1="16" x2="12.01" y2="16"></line>
									</svg>
									<span><strong>${frappe.utils.escape_html(op.blocker.type)}:</strong> ${frappe.utils.escape_html(op.blocker.description)}</span>
								</div>
							` : ""}

							<div class="sf-action-row">
								${op.is_paused ? `
									<button type="button" class="sf-btn sf-btn-sm sf-btn-success sf-touch-btn" data-action="resume-job" data-job="${op.name}">
										&#9654; Resume Operation
									</button>
								` : `
									<button type="button" class="sf-btn sf-btn-sm sf-btn-primary sf-touch-btn" data-action="report-progress" data-job="${op.name}" data-for="${fq}" data-completed="${cq}" data-uom="${uom}">
										&#9998; Report Progress
									</button>
									<button type="button" class="sf-btn sf-btn-sm sf-btn-secondary sf-touch-btn" data-action="pause-job" data-job="${op.name}">
										&#10074;&#10074; Pause
									</button>
									<button type="button" class="sf-btn sf-btn-sm sf-btn-ghost sf-touch-btn" data-action="stop-job" data-job="${op.name}">
										&#9632; Stop Cycle
									</button>
									<button type="button" class="sf-btn sf-btn-sm sf-btn-success sf-touch-btn" data-action="complete-job" data-job="${op.name}" data-for="${fq}" data-completed="${cq}" data-uom="${uom}">
										&#10004; Complete Job
									</button>
								`}
							</div>
						</div>
					</div>
				`;
			}).join("");

			this.currentOpContainer.html(cardsHtml);
		} else if (nextQueued) {
			this.currentOpBadge.text("No Active Job · Next Up").attr("class", "sf-live-badge sf-badge-neutral");
			this.currentOpContainer.html(`
				<div class="sf-next-queued-card">
					<div class="sf-next-badge">Next Queued Operation</div>
					<div class="sf-next-content">
						<div class="sf-next-left">
							<h3 class="sf-next-title">${frappe.utils.escape_html(nextQueued.operation || "Operation")}</h3>
							<p class="sf-next-desc">
								Job Card <strong>${frappe.utils.escape_html(nextQueued.name)}</strong> &middot;
								Work Order <strong>${frappe.utils.escape_html(nextQueued.work_order || "--")}</strong> &middot;
								Station <strong>${frappe.utils.escape_html(nextQueued.workstation || "TBD")}</strong>
							</p>
							<div class="sf-next-details">
								<span>Target Quantity: <strong>${nextQueued.for_quantity} ${frappe.utils.escape_html(nextQueued.stock_uom || "Nos")}</strong></span>
								<span>Scheduled: <strong>${nextQueued.expected_start_date || "Today"}</strong></span>
							</div>
						</div>
						<div class="sf-next-right">
							<button type="button" class="sf-btn sf-btn-primary sf-touch-btn" data-action="start-job" data-job="${nextQueued.name}">
								&#9654; Start Job Now
							</button>
							<a href="${nextQueued.drill_down_link}" class="sf-btn sf-btn-ghost sf-touch-btn" target="_blank" rel="noopener">
								Review Job Card
							</a>
						</div>
					</div>
				</div>
			`);
		} else {
			this.currentOpBadge.text("Idle").attr("class", "sf-live-badge sf-badge-neutral");
			this.currentOpContainer.html(`
				<div class="sf-idle-card">
					<div class="sf-idle-icon">&#x2714;</div>
					<h3 class="sf-idle-title">No Operations Currently in Progress</h3>
					<p class="sf-idle-desc">You have no active running jobs on your assigned workstation. Check your queue below for waiting work.</p>
				</div>
			`);
		}
	}

	renderBlockers() {
		const blockers = this.data.blockers || [];
		if (!blockers.length) {
			this.blockersWrapper.hide();
			return;
		}

		this.blockersWrapper.show();
		this.blockerCount.text(`${blockers.length} Blocker${blockers.length > 1 ? "s" : ""}`);

		const itemsHtml = blockers.map(b => `
			<div class="sf-blocker-item sf-blocker-${(b.severity || "high").toLowerCase()}">
				<div class="sf-blocker-icon-box" aria-hidden="true">&#x26A0;</div>
				<div class="sf-blocker-info">
					<div class="sf-blocker-top">
						<span class="sf-blocker-type">${frappe.utils.escape_html(b.type || "Production Hold")}</span>
						<span class="sf-blocker-source">Job Card: <strong>${frappe.utils.escape_html(b.job_card)}</strong></span>
						${b.workstation ? `<span class="sf-blocker-station">Station: <strong>${frappe.utils.escape_html(b.workstation)}</strong></span>` : ""}
					</div>
					<p class="sf-blocker-text">${frappe.utils.escape_html(b.description || "")}</p>
				</div>
				<div class="sf-blocker-action">
					<a href="/desk#Form/Job Card/${b.job_card}" class="sf-btn sf-btn-sm" target="_blank" rel="noopener">Inspect</a>
				</div>
			</div>
		`).join("");

		this.blockersList.html(itemsHtml);
	}

	renderJobCards() {
		const allJobs = this.data.assigned_jobs || [];

		// Filter by status
		let filtered = allJobs;
		if (this.activeStatusFilter === "Blocked") {
			filtered = filtered.filter(j => j.has_blocker);
		} else if (this.activeStatusFilter !== "All") {
			filtered = filtered.filter(j => j.status === this.activeStatusFilter);
		}

		// Filter by search
		if (this.searchQuery) {
			const q = this.searchQuery;
			filtered = filtered.filter(j => (
				String(j.name).toLowerCase().includes(q) ||
				String(j.work_order || "").toLowerCase().includes(q) ||
				String(j.operation || "").toLowerCase().includes(q) ||
				String(j.production_item || "").toLowerCase().includes(q) ||
				String(j.item_name || "").toLowerCase().includes(q) ||
				String(j.workstation || "").toLowerCase().includes(q)
			));
		}

		this.jobsBadge.text(`${filtered.length} Job${filtered.length !== 1 ? "s" : ""}`);

		if (!filtered.length) {
			this.jobsContainer.hide();
			this.emptyState.show();

			if (this.data.unconfigured_reason && !allJobs.length) {
				this.emptyTitle.text("Assignment Configuration Required");
				this.emptyDesc.text(this.data.unconfigured_reason);
				this.clearFiltersBtn.hide();
			} else {
				this.emptyTitle.text("No Matching Jobs Found");
				this.emptyDesc.text(`No assigned jobs matched filter: "${this.activeStatusFilter}"${this.searchQuery ? ` and search: "${this.searchQuery}"` : ""}.`);
				this.clearFiltersBtn.show();
			}
			return;
		}

		this.emptyState.hide();
		this.jobsContainer.show();

		const cardsHtml = filtered.map(j => {
			const statusClass = (j.status || "open").toLowerCase().replace(/\s+/g, "-");
			const fq = j.for_quantity || 0;
			const cq = j.total_completed_qty || 0;
			const pct = j.completion_percent || 0;
			const rem = j.remaining_qty || 0;

			return `
				<div class="sf-job-card sf-job-${statusClass}">
					<div class="sf-job-header">
						<div class="sf-job-title-row">
							<span class="sf-status-tag sf-status-${statusClass}">${frappe.utils.escape_html(j.status || "Open")}</span>
							${j.is_corrective ? '<span class="sf-rework-tag">Rework</span>' : ""}
							${j.has_blocker ? '<span class="sf-blocked-tag">Blocked</span>' : ""}
							${j.is_overdue ? `<span class="sf-overdue-tag">${j.delay_days}d Overdue</span>` : ""}
						</div>
						<a href="${j.drill_down_link}" class="sf-job-id" target="_blank" rel="noopener">${frappe.utils.escape_html(j.name)} &rarr;</a>
					</div>

					<div class="sf-job-body">
						<h4 class="sf-job-op">${frappe.utils.escape_html(j.operation || "Operation")}</h4>
						<div class="sf-job-details">
							<span class="sf-station-chip">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
									<rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
								</svg>
								${frappe.utils.escape_html(j.workstation || "No Station")}
							</span>
							<span class="sf-wo-chip">
								WO: <strong>${frappe.utils.escape_html(j.work_order || "--")}</strong>
							</span>
						</div>

						<div class="sf-job-item">
							<span class="sf-item-name">${frappe.utils.escape_html(j.item_name || j.production_item || "--")}</span>
							${j.production_item && j.production_item !== j.item_name ? `<span class="sf-item-code">(${frappe.utils.escape_html(j.production_item)})</span>` : ""}
						</div>

						<div class="sf-job-progress">
							<div class="sf-prog-info">
								<span>Completed: <strong>${cq}</strong> / ${fq} ${frappe.utils.escape_html(j.stock_uom || "Nos")}</span>
								<span><strong>${pct}%</strong> (${rem} ${frappe.utils.escape_html(j.stock_uom || "Nos")} left)</span>
							</div>
							<div class="sf-progress-track">
								<div class="sf-progress-bar" style="width: ${Math.min(pct, 100)}%;"></div>
							</div>
						</div>

						${j.has_blocker ? `
							<div class="sf-job-blocker-note">
								<strong>${frappe.utils.escape_html(j.blocker.type)}:</strong> ${frappe.utils.escape_html(j.blocker.description)}
							</div>
						` : ""}
					</div>

					<div class="sf-job-footer">
						<div class="sf-job-actions">
							${(j.status === "Open" || j.status === "Material Transferred" || j.status === "Partially Transferred") ? `
								<button type="button" class="sf-btn sf-btn-sm sf-btn-primary sf-touch-btn" data-action="start-job" data-job="${j.name}">
									&#9654; Start
								</button>
							` : ""}
							${j.status === "Work In Progress" ? `
								${j.is_paused ? `
									<button type="button" class="sf-btn sf-btn-sm sf-btn-success sf-touch-btn" data-action="resume-job" data-job="${j.name}">
										&#9654; Resume
									</button>
								` : `
									<button type="button" class="sf-btn sf-btn-sm sf-btn-primary sf-touch-btn" data-action="report-progress" data-job="${j.name}" data-for="${fq}" data-completed="${cq}" data-uom="${frappe.utils.escape_html(j.stock_uom || 'Nos')}">
										Report
									</button>
									<button type="button" class="sf-btn sf-btn-sm sf-btn-success sf-touch-btn" data-action="complete-job" data-job="${j.name}" data-for="${fq}" data-completed="${cq}" data-uom="${frappe.utils.escape_html(j.stock_uom || 'Nos')}">
										Complete
									</button>
								`}
							` : ""}
							<a href="${j.drill_down_link}" class="sf-btn sf-btn-sm sf-btn-ghost sf-touch-target" target="_blank" rel="noopener">
								Inspect
							</a>
						</div>
						<span class="sf-job-due">Due: <strong>${j.expected_end_date || "Not set"}</strong></span>
					</div>
				</div>
			`;
		}).join("");

		this.jobsContainer.html(cardsHtml);
	}

	// --------------------------------------------------------------------------
	// Action Handlers
	// --------------------------------------------------------------------------

	setBtnLoading(btn, isLoading) {
		if (!btn || !btn.length) return;
		if (isLoading) {
			btn.prop("disabled", true).addClass("sf-btn-loading");
		} else {
			btn.prop("disabled", false).removeClass("sf-btn-loading");
		}
	}

	handleStartJob(jobCard, btn) {
		frappe.confirm(
			__("Start operation on Job Card {0}?", [jobCard]),
			() => {
				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.start_job",
					args: { job_card: jobCard },
					freeze: true,
					freeze_message: __("Starting Job Card {0}...", [jobCard]),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "green" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			}
		);
	}

	handleReportProgress(jobCard, forQty, completedQty, stockUom, btn) {
		const remaining = Math.max(0, forQty - completedQty);
		frappe.prompt(
			[
				{
					fieldtype: "HTML",
					fieldname: "summary_info",
					options: `<div style="margin-bottom: 12px; color: #475569; font-size: 0.9rem;">
						Target Qty: <strong>${forQty} ${stockUom}</strong> &middot; Already Recorded: <strong>${completedQty} ${stockUom}</strong><br>
						Remaining to Complete: <strong>${remaining} ${stockUom}</strong>
					</div>`,
				},
				{
					fieldtype: "Float",
					label: __("Additional Completed Qty in this Cycle ({0})", [stockUom]),
					fieldname: "completed_qty",
					reqd: 1,
					default: remaining > 0 ? (remaining > 1 ? 1 : remaining) : 0,
				},
				{
					fieldtype: "Small Text",
					label: __("Production Remarks (optional)"),
					fieldname: "remarks",
				},
			],
			(vals) => {
				const cq = parseFloat(vals.completed_qty || 0);
				if (cq < 0) {
					frappe.msgprint(__("Completed quantity cannot be negative."));
					return;
				}
				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.record_job_progress",
					args: {
						job_card: jobCard,
						completed_qty: cq,
						remarks: vals.remarks || "",
					},
					freeze: true,
					freeze_message: __("Recording production progress..."),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "green" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			},
			__("Report Progress: {0}", [jobCard]),
			__("Save Progress")
		);
	}

	handlePauseJob(jobCard, btn) {
		frappe.confirm(
			__("Pause operation on Job Card {0}?", [jobCard]),
			() => {
				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.pause_job",
					args: { job_card: jobCard },
					freeze: true,
					freeze_message: __("Pausing operation..."),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "orange" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			}
		);
	}

	handleResumeJob(jobCard, btn) {
		frappe.confirm(
			__("Resume operation on Job Card {0}?", [jobCard]),
			() => {
				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.resume_job",
					args: { job_card: jobCard },
					freeze: true,
					freeze_message: __("Resuming operation..."),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "green" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			}
		);
	}

	handleStopJob(jobCard, stockUom, btn) {
		frappe.prompt(
			[
				{
					fieldtype: "HTML",
					fieldname: "stop_info",
					options: `<p style="color: #475569; font-size: 0.9rem;">
						Stop the active time log for this working shift. Enter any completed quantity produced in this cycle before stopping.
					</p>`,
				},
				{
					fieldtype: "Float",
					label: __("Completed Qty in this Cycle ({0})", [stockUom || "Nos"]),
					fieldname: "completed_qty",
					default: 0.0,
				},
			],
			(vals) => {
				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.stop_job",
					args: {
						job_card: jobCard,
						completed_qty: parseFloat(vals.completed_qty || 0),
					},
					freeze: true,
					freeze_message: __("Stopping operation..."),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "blue" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			},
			__("Stop Shift / Operation: {0}", [jobCard]),
			__("Confirm Stop")
		);
	}

	handleCompleteJob(jobCard, forQty, completedQty, stockUom, btn) {
		const remaining = Math.max(0, forQty - completedQty);
		frappe.prompt(
			[
				{
					fieldtype: "HTML",
					fieldname: "complete_info",
					options: `<div style="margin-bottom: 12px; color: #475569; font-size: 0.9rem;">
						Target: <strong>${forQty} ${stockUom}</strong> &middot; Already Recorded: <strong>${completedQty} ${stockUom}</strong><br>
						Remaining: <strong>${remaining} ${stockUom}</strong><br>
						<span style="font-size: 0.8rem; color: #64748b;">(Completed + Pending + Process Loss must account for remaining production)</span>
					</div>`,
				},
				{
					fieldtype: "Float",
					label: __("Final Completed Qty ({0})", [stockUom]),
					fieldname: "completed_qty",
					reqd: 1,
					default: remaining,
				},
				{
					fieldtype: "Float",
					label: __("Pending Qty ({0})", [stockUom]),
					fieldname: "pending_qty",
					default: 0.0,
				},
				{
					fieldtype: "Float",
					label: __("Process Loss / Scrapped Qty ({0})", [stockUom]),
					fieldname: "process_loss_qty",
					default: 0.0,
				},
			],
			(vals) => {
				const cq = parseFloat(vals.completed_qty || 0);
				const pq = parseFloat(vals.pending_qty || 0);
				const plq = parseFloat(vals.process_loss_qty || 0);

				if (cq < 0 || pq < 0 || plq < 0) {
					frappe.msgprint(__("Quantities cannot be negative."));
					return;
				}

				this.setBtnLoading(btn, true);
				frappe.call({
					method: "sarathi_visibility.api.shopfloor.complete_job",
					args: {
						job_card: jobCard,
						completed_qty: cq,
						pending_qty: pq,
						process_loss_qty: plq,
						auto_submit: true,
					},
					freeze: true,
					freeze_message: __("Completing and submitting Job Card {0}...", [jobCard]),
					callback: (r) => {
						this.setBtnLoading(btn, false);
						if (r.message && r.message.success) {
							frappe.show_alert({ message: r.message.message, indicator: "green" });
							frappe.sarathiUI?.announce?.(r.message.message);
							this.refresh();
						}
					},
					error: () => this.setBtnLoading(btn, false),
				});
			},
			__("Complete Operation: {0}", [jobCard]),
			__("Confirm & Complete")
		);
	}

	// =========================================================================
	// DASH-026 Supervisor Team Overview Controller Methods
	// =========================================================================

	switchSubview(subview) {
		this.activeSubview = subview;
		this.subviewTabs.removeClass("active").attr("aria-selected", "false");
		const activeTab = this.root.find(`[data-subview="${subview}"]`);
		activeTab.addClass("active").attr("aria-selected", "true");

		if (subview === "supervisor") {
			this.operatorSubview.hide();
			this.supervisorSubview.show();
			frappe.sarathiUI?.announce?.("Switched to Supervisor Team Overview");
			if (!this.supervisorData) {
				this.fetchSupervisorOverview();
			}
		} else {
			this.supervisorSubview.hide();
			this.operatorSubview.show();
			frappe.sarathiUI?.announce?.("Switched to Operator Workboard");
		}
	}

	async fetchSupervisorOverview() {
		const request = (this.supSequence = (this.supSequence || 0) + 1);
		const filters = {};
		const fromDate = this.supFromDate.val();
		const toDate = this.supToDate.val();
		const op = this.supOpSelect.val();
		const ws = this.supWsSelect.val();
		const st = this.supStatusSelect.val();
		const q = (this.supSearchInput.val() || "").trim();

		if (fromDate) filters.from_date = fromDate;
		if (toDate) filters.to_date = toDate;
		if (op) filters.employee = op;
		if (ws) filters.workstation = ws;
		if (st && st !== "All") filters.status = st;
		if (q) filters.search = q;

		try {
			const res = await frappe.call({
				method: "sarathi_visibility.api.shopfloor.get_supervisor_team_overview",
				args: { filters },
			});
			if (request !== this.supSequence) return;
			if (res && res.message) {
				this.supervisorData = res.message;
				this.lastSupSuccessfulRefresh = new Date();
				this.lastSupFailedRefresh = null;
				this.root.find("[data-sup-stale-banner]").remove();
				this.renderSupervisorOverview();
			}
		} catch (err) {
			if (request !== this.supSequence) return;
			console.error("Failed to load supervisor team overview:", err);
			this.lastSupFailedRefresh = new Date();
			if (this.supervisorData && this.lastSupSuccessfulRefresh) {
				const staleTime = this.formatTime(this.lastSupSuccessfulRefresh);
				if (!this.root.find("[data-sup-stale-banner]").length) {
					const banner = $(`
						<div class="sui-stale-banner" data-sup-stale-banner role="alert" style="margin: 12px 0;">
							<p style="margin:0;">${__("Refresh failed. Retaining last successful supervisor data from {0}.", [staleTime])}</p>
							<button type="button" class="sf-btn sf-btn-primary" style="margin-left:auto; min-height:32px; padding:2px 10px;" data-action="retry-sup">${__("Retry")}</button>
						</div>
					`);
					banner.find("[data-action='retry-sup']").on("click", () => this.fetchSupervisorOverview());
					this.supervisorSubview.find(".sf-sup-header").after(banner);
				}
				frappe.show_alert?.({
					message: __("Supervisor refresh failed. Showing last successful data."),
					indicator: "orange",
				});
			} else {
				this.supervisorData = null;
				this.supWorkloadContainer.html(`
					<div class="sui-state" data-state="error" role="alert" style="padding:24px; text-align:center;">
						<p style="margin:0 0 12px;">${__("Unable to load supervisor overview. Please try again.")}</p>
						<button type="button" class="sf-btn sf-btn-primary" data-action="retry-sup">${__("Retry")}</button>
					</div>
				`);
				this.supWorkloadContainer.find("[data-action='retry-sup']").on("click", () => this.fetchSupervisorOverview());
			}
		}
	}

	renderSupervisorOverview() {
		if (!this.supervisorData) return;
		const d = this.supervisorData;
		const ctx = d.user_context || {};
		const s = d.team_summary || {};

		// Scope label
		const wsList = ctx.supervisor_workstations || [];
		if (wsList.length > 0) {
			this.supScopeLabel.text(`Workstations: ${wsList.join(", ")}`);
		} else if (ctx.is_manager) {
			this.supScopeLabel.text("Factory-wide Manufacturing Scope");
		} else {
			this.supScopeLabel.text("Team Supervisor Scope");
		}

		// Check unconfigured
		if (d.unconfigured_reason) {
			this.supUnconfiguredCard.show();
			this.supUnconfiguredText.text(d.unconfigured_reason);
			this.supKpiMembers.text("0");
			this.supKpiActiveOps.text("0");
			this.supKpiWithJobs.text("0");
			this.supKpiWithoutWork.text("0");
			this.supKpiActiveJcs.text("0");
			this.supKpiWaitingJcs.text("0");
			this.supKpiCompletedJcs.text("0");
			this.supKpiBlockedJcs.text("0");
			this.supKpiOverdueJcs.text("0");

			this.supWorkloadContainer.empty();
			this.supWorkloadCount.text("0 Operators");
			this.supActiveContainer.empty();
			this.supActiveCount.text("0 Running");
			this.supBlockersWrapper.hide();
			this.supCompletedContainer.empty();
			this.supCompletedCount.text("0 Completed");
			this.supWorkstationsContainer.empty();
			this.supWorkstationsCount.text("0 Stations");
			return;
		}

		this.supUnconfiguredCard.hide();

		// Populate select options if needed
		const currentOpVal = this.supOpSelect.val();
		if (this.supOpSelect.children().length <= 1 && d.team_workload) {
			d.team_workload.forEach(op => {
				this.supOpSelect.append(`<option value="${frappe.utils.escape_html(op.employee_id)}">${frappe.utils.escape_html(op.employee_name)}</option>`);
			});
			if (currentOpVal) this.supOpSelect.val(currentOpVal);
		}

		const currentWsVal = this.supWsSelect.val();
		if (this.supWsSelect.children().length <= 1 && d.workstations) {
			d.workstations.forEach(ws => {
				this.supWsSelect.append(`<option value="${frappe.utils.escape_html(ws.workstation)}">${frappe.utils.escape_html(ws.workstation)}</option>`);
			});
			if (currentWsVal) this.supWsSelect.val(currentWsVal);
		}

		// 9 KPIs
		this.supKpiMembers.text(s.total_team_members || 0);
		this.supKpiActiveOps.text(s.operators_active || 0);
		this.supKpiWithJobs.text(s.operators_with_jobs || 0);
		this.supKpiWithoutWork.text(s.operators_without_work || 0);
		this.supKpiActiveJcs.text(s.active_job_cards || 0);
		this.supKpiWaitingJcs.text(s.waiting_job_cards || 0);
		this.supKpiCompletedJcs.text(s.completed_job_cards || 0);
		this.supKpiBlockedJcs.text(s.blocked_job_cards || 0);
		this.supKpiOverdueJcs.text(s.overdue_job_cards || 0);

		// Render Team Workload Cards
		const workload = d.team_workload || [];
		this.supWorkloadCount.text(`${workload.length} Operators`);
		if (workload.length === 0) {
			this.supWorkloadContainer.html(`<div class="sf-empty-state"><p>No operators matching filters.</p></div>`);
		} else {
			const workloadHtml = workload.map(op => {
				const initials = (op.employee_name || "OP").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
				const statusClass = op.workload_status === "Working" ? "sf-status-working" : (op.workload_status === "Assigned" ? "sf-status-assigned" : "sf-status-idle");

				let activeOpHtml = "";
				if (op.active_operation) {
					const a = op.active_operation;
					activeOpHtml = `
						<div class="sf-active-op-mini">
							<div class="sf-active-op-mini-header">
								<a href="/desk#Form/Job Card/${a.job_card}" class="sf-active-op-mini-title" target="_blank" rel="noopener">
									${frappe.utils.escape_html(a.operation)} (${frappe.utils.escape_html(a.job_card)})
								</a>
								<span class="sf-station-badge">${frappe.utils.escape_html(a.workstation || "--")}</span>
							</div>
							<div class="sf-active-op-mini-details">
								<span>Qty: <strong>${a.total_completed_qty} / ${a.for_quantity} ${frappe.utils.escape_html(a.stock_uom)}</strong> (${a.completion_percent}%)</span>
								<span>Elapsed: <strong>${a.elapsed_mins} mins</strong></span>
							</div>
							<div class="sf-progress-track">
								<div class="sf-progress-fill" style="width: ${Math.min(100, a.completion_percent)}%;"></div>
							</div>
						</div>
					`;
				}

				const multipleAlert = op.has_multiple_active
					? `<div class="sf-multiple-active-alert">&#x26A0;&#xFE0F; Multiple Active Jobs (${op.in_progress_count})</div>`
					: "";

				return `
					<div class="sf-operator-card">
						<div class="sf-operator-card-header">
							<div class="sf-operator-info">
								<div class="sf-operator-avatar">${initials}</div>
								<div>
									<h4 class="sf-operator-name">${frappe.utils.escape_html(op.employee_name)}</h4>
									<p class="sf-operator-role">${frappe.utils.escape_html(op.designation || "Operator")}${op.department ? ` &middot; ${frappe.utils.escape_html(op.department)}` : ""}</p>
								</div>
							</div>
							<span class="sf-status-pill ${statusClass}">${frappe.utils.escape_html(op.workload_status)}</span>
						</div>

						${multipleAlert}

						<div class="sf-workload-counts-row">
							<span class="sf-count-chip">WIP: <strong>${op.in_progress_count}</strong></span>
							<span class="sf-count-chip">Waiting: <strong>${op.waiting_count}</strong></span>
							<span class="sf-count-chip">Completed: <strong>${op.completed_count}</strong></span>
							${op.blocked_count > 0 ? `<span class="sf-count-chip" style="color: #b91c1c;">Blocked: <strong>${op.blocked_count}</strong></span>` : ""}
						</div>

						${activeOpHtml}
					</div>
				`;
			}).join("");
			this.supWorkloadContainer.html(workloadHtml);
		}

		// Render Active Floor Operations
		const activeOps = d.active_operations || [];
		this.supActiveCount.text(`${activeOps.length} Running`);
		if (activeOps.length === 0) {
			this.supActiveContainer.html(`<div class="sf-table-card" style="padding: 24px; text-align: center; color: var(--sf-ink-muted);">No active operations currently in progress on the shop floor.</div>`);
		} else {
			const activeHtml = `
				<div class="sf-table-card">
					<table class="sf-data-table">
						<thead>
							<tr>
								<th>Job Card</th>
								<th>Work Order</th>
								<th>Operation</th>
								<th>Workstation</th>
								<th>Operator</th>
								<th>Output Progress</th>
								<th>Elapsed Time</th>
								<th>Status / Blockers</th>
							</tr>
						</thead>
						<tbody>
							${activeOps.map(op => `
								<tr>
									<td><a href="${op.drill_down_link}" target="_blank" rel="noopener"><strong>${frappe.utils.escape_html(op.name)}</strong></a></td>
									<td><a href="${op.work_order_link || '#'}" target="_blank" rel="noopener">${frappe.utils.escape_html(op.work_order || "--")}</a></td>
									<td><strong>${frappe.utils.escape_html(op.operation)}</strong></td>
									<td><span class="sf-station-badge">${frappe.utils.escape_html(op.workstation || "--")}</span></td>
									<td>${frappe.utils.escape_html(op.assigned_operator_name || op.employee || "Unassigned")}</td>
									<td>
										${op.total_completed_qty} / ${op.for_quantity} ${frappe.utils.escape_html(op.stock_uom)} (${op.completion_percent}%)
										<div class="sf-progress-track" style="margin-top: 4px; height: 6px;">
											<div class="sf-progress-fill" style="width: ${Math.min(100, op.completion_percent)}%;"></div>
										</div>
									</td>
									<td><strong>${op.elapsed_mins || 0} mins</strong></td>
									<td>
										${op.has_blocker && op.blocker ? `<span class="sf-blocker-pill ${op.blocker.severity === 'Critical' ? 'sf-pill-critical' : 'sf-pill-high'}">${frappe.utils.escape_html(op.blocker.type)}</span>` : `<span class="sf-status-tag sf-status-wip">In Progress</span>`}
									</td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>
			`;
			this.supActiveContainer.html(activeHtml);
		}

		// Render Completed Work
		const completed = d.completed_work || [];
		this.supCompletedCount.text(`${completed.length} Completed`);
		if (completed.length === 0) {
			this.supCompletedContainer.html(`<div class="sf-table-card" style="padding: 24px; text-align: center; color: var(--sf-ink-muted);">No completed production operations found for the selected period.</div>`);
		} else {
			const completedHtml = `
				<div class="sf-table-card">
					<table class="sf-data-table">
						<thead>
							<tr>
								<th>Job Card</th>
								<th>Work Order</th>
								<th>Item</th>
								<th>Operation</th>
								<th>Workstation</th>
								<th>Operator</th>
								<th>Completed Qty</th>
								<th>Duration</th>
								<th>Completion Date</th>
							</tr>
						</thead>
						<tbody>
							${completed.map(c => `
								<tr>
									<td><a href="${c.drill_down_link}" target="_blank" rel="noopener"><strong>${frappe.utils.escape_html(c.name)}</strong></a></td>
									<td><a href="${c.work_order_link || '#'}" target="_blank" rel="noopener">${frappe.utils.escape_html(c.work_order || "--")}</a></td>
									<td>${frappe.utils.escape_html(c.item_name || c.production_item || "--")}</td>
									<td>${frappe.utils.escape_html(c.operation)}</td>
									<td><span class="sf-station-badge">${frappe.utils.escape_html(c.workstation || "--")}</span></td>
									<td>${frappe.utils.escape_html(c.assigned_operator_name || c.employee || "--")}</td>
									<td><strong>${c.total_completed_qty} ${frappe.utils.escape_html(c.stock_uom)}</strong></td>
									<td>${c.total_time_in_mins || 0} mins</td>
									<td>${c.actual_end_date || (c.modified ? c.modified.slice(0, 16) : "--")}</td>
								</tr>
							`).join("")}
						</tbody>
					</table>
				</div>
			`;
			this.supCompletedContainer.html(completedHtml);
		}

		// Render Blockers & Attention Queue
		const blockers = d.blockers || [];
		this.supBlockersCount.text(`${blockers.length} Notices`);
		if (blockers.length === 0) {
			this.supBlockersWrapper.hide();
		} else {
			this.supBlockersWrapper.show();
			const blockersHtml = blockers.map(b => {
				const sevClass = b.severity === "Critical" ? "sf-blocker-critical" : (b.severity === "High" ? "sf-blocker-high" : "sf-blocker-med");
				const linkHtml = b.drill_down_link
					? `<a href="${b.drill_down_link}" class="sf-blocker-link" target="_blank" rel="noopener">Open ${frappe.utils.escape_html(b.source_doc || b.affected_entity)} &rarr;</a>`
					: "";

				return `
					<div class="sf-blocker-item ${sevClass}">
						<div class="sf-blocker-badge-col">
							<span class="sf-blocker-pill ${b.severity === 'Critical' ? 'sf-pill-critical' : (b.severity === 'High' ? 'sf-pill-high' : 'sf-pill-med')}">${frappe.utils.escape_html(b.severity)}</span>
							<span class="sf-blocker-type-label">${frappe.utils.escape_html(b.category)}</span>
						</div>
						<div class="sf-blocker-content-col">
							<h4 class="sf-blocker-item-title">${frappe.utils.escape_html(b.title)}</h4>
							<p class="sf-blocker-item-desc">${frappe.utils.escape_html(b.description)}</p>
							${b.suggested_action ? `<p class="sf-blocker-item-sub"><strong>Action:</strong> ${frappe.utils.escape_html(b.suggested_action)}</p>` : ""}
						</div>
						<div class="sf-blocker-action-col">
							${linkHtml}
						</div>
					</div>
				`;
			}).join("");
			this.supBlockersList.html(blockersHtml);
		}

		// Render Workstations Grid
		const stations = d.workstations || [];
		this.supWorkstationsCount.text(`${stations.length} Stations`);
		if (stations.length === 0) {
			this.supWorkstationsContainer.html(`<div class="sf-table-card" style="padding: 20px; color: var(--sf-ink-muted);">No workstation records under current supervisor scope.</div>`);
		} else {
			const stationsHtml = stations.map(ws => {
				const statusBadge = ws.status === "Downtime"
					? `<span class="sf-status-pill" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca;">Breakdown</span>`
					: (ws.status === "Running"
						? `<span class="sf-status-pill sf-status-working">Running (${ws.active_job_count})</span>`
						: `<span class="sf-status-pill sf-status-idle">Idle</span>`);

				return `
					<div class="sf-station-card">
						<div class="sf-station-card-header">
							<a href="${ws.drill_down_link}" class="sf-station-name" target="_blank" rel="noopener">${frappe.utils.escape_html(ws.workstation)}</a>
							${statusBadge}
						</div>
						<div class="sf-station-meta">
							<span>Active WIP: <strong>${ws.active_job_count}</strong></span>
							<span>Queued: <strong>${ws.waiting_job_count}</strong></span>
						</div>
					</div>
				`;
			}).join("");
			this.supWorkstationsContainer.html(stationsHtml);
		}
	}
};

