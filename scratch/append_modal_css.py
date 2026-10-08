"""
Append In-Dashboard Card Details & Record Inspector modal CSS to sarathi_dashboard.css
"""

css_path = 'sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css'
with open(css_path, encoding='utf-8') as f:
    css = f.read()

modal_css = """

/* ==========================================================================
   SARATHI CONTROL TOWER · IN-DASHBOARD CARD DETAILS (LIST, TABLE & FORMS)
   Opens card-specific records in an elegant modal table and interactive form view
   without leaving the dashboard or navigating into ERPNext desk standard views.
   ========================================================================== */

.sd-record-link {
  color: #2563eb !important;
  text-decoration: underline !important;
  font-weight: 600 !important;
  cursor: pointer !important;
}

.sd-record-link:hover {
  color: #1d4ed8 !important;
}

/* Modal Dialog Sizing & Aesthetics */
.sd-card-details-dialog .modal-dialog {
  max-width: 1120px !important;
  width: 95vw !important;
  margin: 28px auto !important;
}

.sd-card-details-dialog .modal-content {
  border-radius: 18px !important;
  box-shadow: 0 25px 60px -12px rgba(15, 23, 42, 0.28) !important;
  border: 1.5px solid #cbd5e1 !important;
  overflow: hidden !important;
  background: #ffffff !important;
}

.sd-card-details-dialog .modal-header {
  background: #f8fafc !important;
  border-bottom: 1.5px solid #e2e8f0 !important;
  padding: 16px 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}

.sd-card-details-dialog .modal-title {
  font-family: 'Outfit', sans-serif !important;
  font-size: 19px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin: 0 !important;
}

.sd-card-details-dialog .modal-title .sarathi-ui-icon {
  width: 22px !important;
  height: 22px !important;
  color: #2563eb !important;
}

.sd-card-details-dialog .modal-body {
  padding: 22px 24px !important;
  max-height: 78vh !important;
  overflow-y: auto !important;
  background: #ffffff !important;
}

/* Modal Toolbar */
.sd-modal-toolbar {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 14px !important;
  margin-bottom: 16px !important;
  flex-wrap: wrap !important;
}

.sd-modal-search-wrap {
  position: relative !important;
  flex: 1 1 300px !important;
}

.sd-modal-search-svg {
  position: absolute !important;
  left: 12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  color: #64748b !important;
  pointer-events: none !important;
}

.sd-modal-search-input {
  width: 100% !important;
  height: 40px !important;
  padding: 6px 14px 6px 38px !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  background: #f8fafc !important;
  color: #0f172a !important;
  outline: none !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
}

.sd-modal-search-input:focus {
  border-color: #2563eb !important;
  background: #ffffff !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

.sd-modal-meta-pills {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}

/* Modal Table View */
.sd-modal-table-scroll {
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 12px !important;
  overflow: auto !important;
  max-height: 56vh !important;
  background: #ffffff !important;
}

.sd-modal-table {
  width: 100% !important;
  border-collapse: collapse !important;
  text-align: left !important;
  font-size: 13px !important;
}

.sd-modal-table th {
  position: sticky !important;
  top: 0 !important;
  background: #f1f5f9 !important;
  color: #334155 !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
  padding: 12px 14px !important;
  border-bottom: 2px solid #cbd5e1 !important;
  z-index: 2 !important;
  white-space: nowrap !important;
}

.sd-modal-table td {
  padding: 11px 14px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  color: #1e293b !important;
  vertical-align: middle !important;
}

.sd-modal-row {
  cursor: pointer !important;
  transition: background-color 0.15s ease !important;
}

.sd-modal-row:nth-child(even) {
  background: #fbfcfe !important;
}

.sd-modal-row:hover {
  background: #eff6ff !important;
}

.sd-modal-btn-view {
  padding: 5px 12px !important;
  font-size: 11.5px !important;
  font-weight: 750 !important;
  border-radius: 8px !important;
  background: #eff6ff !important;
  border: 1px solid #bfdbfe !important;
  color: #1d4ed8 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.sd-modal-btn-view:hover {
  background: #2563eb !important;
  color: #ffffff !important;
  border-color: #2563eb !important;
  transform: translateY(-1px) !important;
}

/* Modal In-Dashboard Form View */
.sd-modal-form-view {
  display: flex !important;
  flex-direction: column !important;
  gap: 18px !important;
}

.sd-modal-form-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  padding-bottom: 16px !important;
  border-bottom: 1.5px solid #e2e8f0 !important;
  gap: 16px !important;
  flex-wrap: wrap !important;
}

.sd-modal-form-header-left {
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
}

.sd-modal-form-back-btn {
  background: #f1f5f9 !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  color: #334155 !important;
  font-size: 12.5px !important;
  font-weight: 750 !important;
  padding: 8px 16px !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.sd-modal-form-back-btn:hover {
  background: #e2e8f0 !important;
  color: #0f172a !important;
  transform: translateX(-2px) !important;
}

.sd-modal-form-title-badge {
  display: flex !important;
  flex-direction: column !important;
}

.sd-form-doctype-tag {
  font-size: 11px !important;
  font-weight: 850 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  color: #2563eb !important;
}

.sd-form-docname-title {
  font-family: 'Outfit', sans-serif !important;
  font-size: 20px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  margin: 2px 0 0 0 !important;
  letter-spacing: -0.4px !important;
}

.sd-modal-form-header-right {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}

.sd-modal-form-section-title {
  font-family: 'Outfit', sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 800 !important;
  color: #334155 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  margin-top: 4px !important;
}

.sd-modal-form-section-title::after {
  content: "" !important;
  flex: 1 !important;
  height: 1px !important;
  background: #e2e8f0 !important;
}

.sd-modal-form-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)) !important;
  gap: 12px !important;
}

.sd-modal-field-card {
  background: #f8fafc !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 10px !important;
  padding: 10px 14px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  transition: all 0.2s ease !important;
}

.sd-modal-field-card:hover {
  background: #ffffff !important;
  border-color: #cbd5e1 !important;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
}

.sd-modal-field-label {
  font-size: 10.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
  color: #64748b !important;
}

.sd-modal-field-val {
  font-size: 13.5px !important;
  font-weight: 750 !important;
  color: #0f172a !important;
  word-break: break-word !important;
}

.sd-modal-nested-link {
  color: #2563eb !important;
  font-weight: 750 !important;
  text-decoration: underline !important;
  cursor: pointer !important;
}

.sd-modal-nested-link:hover {
  color: #1d4ed8 !important;
}

.sd-modal-related-block {
  margin-top: 12px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
}

.sd-modal-related-title {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}

.sd-modal-related-title h4 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 14px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  margin: 0 !important;
}

.sd-btn-xs {
  padding: 3px 8px !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  border-radius: 6px !important;
  background: #eff6ff !important;
  border: 1px solid #bfdbfe !important;
  color: #1d4ed8 !important;
  cursor: pointer !important;
}

.sd-btn-xs:hover {
  background: #2563eb !important;
  color: #ffffff !important;
}

.sd-modal-loading {
  text-align: center !important;
  padding: 40px !important;
  color: #64748b !important;
}

.sd-modal-spinner {
  width: 32px !important;
  height: 32px !important;
  border: 3px solid #e2e8f0 !important;
  border-top-color: #2563eb !important;
  border-radius: 50% !important;
  animation: sd-spin 0.8s linear infinite !important;
  margin: 0 auto 12px auto !important;
}

@keyframes sd-spin {
  to { transform: rotate(360deg); }
}
"""

if 'sd-card-details-dialog' not in css:
    css = css + modal_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Appended modal CSS to sarathi_dashboard.css successfully!")
else:
    print("Modal CSS already exists in sarathi_dashboard.css")
