# CHATBOX ARCHITECTURE SPECIFICATION

## 1. UI Integration in Sarathi Control Tower

The Sarathi Industrial AI Agent Chatbox is natively embedded into the Sarathi Control Tower dashboard (`sarathi_visibility` Frappe app):
- **Page Wrapper**: `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html`
- **Application Controller**: `sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`
- **Modern Dark-Glass Styling**: `sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css`
- **Floating Action Button (FAB)**: `#sarathiAiFab` with breathing animation, located at the bottom-right corner.
- **Chat Window Modal**: `#sarathiAiChatModal` supporting expand/collapse (`.sd-ai-expanded`), maximize, and real-time reset.

---

## 2. Interactive Card Components

The chat UI supports specialized interactive cards:

### 2.1 Pre-Mutation Confirmation Card (`.sd-ai-card-confirmation`)
- **Trigger**: Returned when backend status is `AWAITING_CONFIRMATION`.
- **Contents**:
  - Badge: `⚡ Validation Complete`
  - Checklist: Shows verification checkmarks:
    - `✓ Organization Skill loaded`
    - `✓ Company DocType identified`
    - `✓ Required fields available`
    - `✓ Permission checked`
    - `✓ Duplicate check completed`
  - Attribute Grid: Summarizes pending field values.
  - Buttons:
    - Primary: `[✓ Confirm & Create]` (clicking immediately sends `"Confirm"` into the chat).
    - Secondary: `[✕ Cancel]` (clicking resets the session).

### 2.2 Mutation Success Card (`.sd-ai-card-success`)
- **Trigger**: Returned when backend status is `COMPLETED`.
- **Contents**:
  - Badge: `● LIVE IN ERPNEXT`
  - Record ID: Highlighted code block with the newly created document identifier.
  - Field Pill Grid: Displays primary attributes (Company Name, Abbreviation, Currency, Country).
  - Desk Link: Direct button `[🚀 Open Document in Desk ↗]` pointing to `/app/<doctype-slug>/<name>`.
  - Actions: `[↻ Refresh Dashboard]` and `[⚡ Highlight in Dashboard]`.

### 2.3 Interactive Intake Card (`.sd-ai-card-intake`)
- **Trigger**: Returned when backend status is `COLLECTING_SLOTS`.
- **Contents**:
  - Badge: `Slot Intake`
  - Missing field rows with field labels and business hints.
  - Button: `[📋 Insert Template in Chat]` which auto-fills the input box for user convenience.

### 2.4 Live Activity Card (`.sd-ai-card-changes`)
- **Trigger**: Returned when backend status is `LIVE_CHANGES`.
- **Contents**:
  - Lists real-time recently modified documents with direct desk links and status pills.

---

## 3. Real-Time Dashboard Synchronization

When the agent successfully creates a document (`status === "COMPLETED"`):
1. **Top Floating Live Banner (`.sd-live-banner`)**:
   - Slides down from top of the screen: `⚡ Real-time Live Change: <DocType> <Name> created. Dashboard synchronized!`
2. **Dashboard Entity Glow (`.sd-live-highlight-pulse`)**:
   - Locates corresponding dashboard cards or tables and triggers a glowing pulse animation.
3. **Native Frappe Toast Alert**:
   - Calls `frappe.show_alert({ message, indicator: "green" }, 5)`.
4. **Immediate Data Reload**:
   - Invokes `this.load()`, automatically updating charts, KPI counters, and table records without requiring a page refresh.

---

## 4. REST API Contract

### Endpoint: `sarathi_visibility.api.agent_chat.send_message`
- **Method**: `POST`
- **Parameters**:
  - `message` (str, required): User natural language text.
  - `session_id` (str, optional): User/session identifier (defaults to `frappe.session.user`).
  - `company` (str, optional): Currently selected dashboard company filter.
  - `customer` (str, optional): Currently selected dashboard customer filter.
  - `project` (str, optional): Currently selected dashboard project filter.
- **Response Schema**:
  ```json
  {
    "message": "Markdown formatted conversational response",
    "status": "COLLECTING_SLOTS | AWAITING_CONFIRMATION | COMPLETED | FAILED | IDLE",
    "doctype": "Company",
    "name": "Gaurav Manufacturing",
    "verified": true,
    "fields": {
      "Company Name": "Gaurav Manufacturing",
      "Abbr": "GM",
      "Country": "India"
    },
    "url": "/app/company/Gaurav%20Manufacturing",
    "action_steps": [ ... ],
    "follow_ups": [ ... ]
  }
  ```
