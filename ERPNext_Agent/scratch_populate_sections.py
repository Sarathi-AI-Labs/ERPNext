"""Script to populate all 98 section subfolders with comprehensive SKILL.md and section_info.json."""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = r"C:\Users\Gaurav Ramane\.gemini\antigravity-ide\brain\170122e2-2297-41b5-bc09-634e5f6be2d5\modules_fields_data.json"

with open(DATA_PATH, encoding="utf-8") as f:
    fields_data = json.load(f)

# Comprehensive mapping of Module -> Section Folder -> Primary DocTypes & Description
SECTION_DEFINITIONS = {
    "Accounting": {
        "Accounts Setup": {
            "doctypes": ["Account", "Cost Center", "Fiscal Year"],
            "desc": "Chart of Accounts management, cost center budget trees, and fiscal year configurations.",
            "questions": {
                "Account": {
                    "account_name": "What is the name of the new Account?",
                    "company": "Which Company does this account belong to? (Default: SarathiAILabs)",
                    "root_type": "What is the root type? (Asset, Liability, Equity, Income, Expense)",
                    "parent_account": "What is the parent group account in the Chart of Accounts?"
                }
            }
        },
        "Banking": {
            "doctypes": ["Bank", "Bank Account", "Payment Entry"],
            "desc": "Bank master setup, company bank accounts, and bank clearing reconciliation.",
            "questions": {
                "Bank Account": {
                    "bank": "Which bank (e.g., HDFC, SBI, Citibank)?",
                    "account_name": "What is the account title?",
                    "bank_account_no": "What is the bank account number?",
                    "company": "Which Company owns this bank account? (Default: SarathiAILabs)"
                }
            }
        },
        "Budget": {
            "doctypes": ["Cost Center", "Account"],
            "desc": "Cost center and project budget variance tracking and monthly expense limits."
        },
        "Financial Reports": {
            "doctypes": ["Journal Entry", "GL Entry"],
            "desc": "General Ledger, Trial Balance, Profit and Loss, and Balance Sheet analysis."
        },
        "Invoicing": {
            "doctypes": ["Sales Invoice", "Purchase Invoice"],
            "desc": "Customer and vendor commercial invoices, GST/tax calculations, and receivables/payables."
        },
        "Payments": {
            "doctypes": ["Payment Entry", "Payment Request", "Mode of Payment"],
            "desc": "Customer receipts, vendor remittances, advance payments, and internal bank transfers."
        },
        "Share Management": {
            "doctypes": ["Company"],
            "desc": "Equity allocation, shareholder register, and share transfers."
        },
        "Subscription": {
            "doctypes": ["Customer"],
            "desc": "Recurring billing plans, customer subscriptions, and automated renewal invoices."
        },
        "Taxes": {
            "doctypes": ["Tax Category", "Sales Taxes and Charges Template", "Purchase Taxes and Charges Template"],
            "desc": "Tax categories, GST rate templates, withholding tax, and tax calculation rules."
        }
    },
    "Assets": {
        "Asset": {
            "doctypes": ["Asset", "Asset Category"],
            "desc": "Fixed asset master registry, asset tags, custodian assignments, and location tracking."
        },
        "Asset Capitalization": {
            "doctypes": ["Asset"],
            "desc": "Capital work in progress (CWIP) capitalization into operational fixed assets."
        },
        "Asset Movement": {
            "doctypes": ["Asset Movement", "Asset"],
            "desc": "Transfer of capital equipment between employees, workstations, or locations."
        },
        "Depreciation Schedule": {
            "doctypes": ["Asset Depreciation Schedule", "Asset"],
            "desc": "Straight line and written down value depreciation schedules and automated monthly posting."
        },
        "Maintenance": {
            "doctypes": ["Asset Repair", "Asset"],
            "desc": "Preventive maintenance schedules, repair logs, and maintenance team dispatch."
        },
        "Reports": {
            "doctypes": ["Asset"],
            "desc": "Asset ledger, historical depreciation balances, and capital expenditure analytics."
        },
        "Settings": {
            "doctypes": ["Asset Category"],
            "desc": "Asset numbering series, automated depreciation posting toggles, and default ledgers."
        },
        "Setup": {
            "doctypes": ["Asset Category", "Location"],
            "desc": "Asset categories, depreciation rate tables, and plant floor locations."
        }
    },
    "Buying": {
        "Material Request": {
            "doctypes": ["Material Request"],
            "desc": "Internal purchase requisitions, indent approvals, and manufacturing component demand."
        },
        "Purchase Invoice": {
            "doctypes": ["Purchase Invoice", "Supplier"],
            "desc": "Accounts payable billing against purchase orders and incoming goods receipts."
        },
        "Purchase Order": {
            "doctypes": ["Purchase Order", "Supplier"],
            "desc": "Legally binding vendor procurement contracts with delivery lead times and pricing terms."
        },
        "Reports": {
            "doctypes": ["Purchase Order", "Purchase Invoice"],
            "desc": "Procurement analytics, supplier delivery performance, and purchase order tracking."
        },
        "Request for Quotation": {
            "doctypes": ["Request for Quotation", "Supplier"],
            "desc": "Tendering documents sent to multiple vendors to solicit competitive bids."
        },
        "Settings": {
            "doctypes": ["Buying Settings"],
            "desc": "Buying tolerances, purchase order approval rules, and supplier scorecards."
        },
        "Setup": {
            "doctypes": ["Supplier", "Supplier Group"],
            "desc": "Vendor registry, payment terms, and vendor categorization."
        },
        "Supplier Quotation": {
            "doctypes": ["Supplier Quotation", "Supplier"],
            "desc": "Commercial quotations received from vendors with price validity periods."
        }
    },
    "ERPNext Settings": {
        "Accounts Settings": {"doctypes": ["Accounts Settings"], "desc": "Credit limit enforcement and fiscal defaults."},
        "Buying Settings": {"doctypes": ["Buying Settings"], "desc": "Purchase order tolerances and approvals."},
        "Global Defaults": {"doctypes": ["Global Defaults"], "desc": "Default company, currency, and date formats."},
        "Manufacturing Settings": {"doctypes": ["Manufacturing Settings"], "desc": "Work order backflush rules and capacity tolerances."},
        "Other Settings": {"doctypes": ["Global Defaults"], "desc": "Miscellaneous ERPNext configuration parameters."},
        "POS Settings": {"doctypes": ["POS Settings"], "desc": "Point of sale cash register configurations."},
        "Projects Settings": {"doctypes": ["Projects Settings"], "desc": "Project costing and timesheet validation rules."},
        "Selling Settings": {"doctypes": ["Selling Settings"], "desc": "Sales order credit verification and pricing policies."},
        "Stock Settings": {"doctypes": ["Stock Settings"], "desc": "Negative stock prohibition (strictly 0) and valuation rules."},
        "System Settings": {"doctypes": ["System Settings"], "desc": "Session timeouts, backups, and site-wide defaults."}
    },
    "Framework": {
        "Client Scripts": {"doctypes": ["Client Script"], "desc": "Browser-side JavaScript hooks for desk forms."},
        "Customization": {"doctypes": ["Custom Field", "Property Setter"], "desc": "DocType schema extensions and field overrides."},
        "DocType": {"doctypes": ["DocType"], "desc": "Frappe core meta-schema builder and controller definitions."},
        "Page": {"doctypes": ["Page"], "desc": "Custom single-page applications inside Frappe desk."},
        "Report": {"doctypes": ["Report"], "desc": "Query and script report definitions."},
        "Server Scripts": {"doctypes": ["Server Script"], "desc": "Sandboxed Python hooks on document save/submit."},
        "Workspace": {"doctypes": ["Workspace"], "desc": "Desk sidebar and dashboard workspace layouts."}
    },
    "Manufacturing": {
        "Bill of Materials": {
            "doctypes": ["BOM"],
            "desc": "Multi-level engineering recipes, raw material explosion, operations, and Sarathi Project links."
        },
        "Job Card": {
            "doctypes": ["Job Card"],
            "desc": "Shop-floor machine/operator work assignments and actual cycle time tracking."
        },
        "Material Planning": {
            "doctypes": ["Production Plan"],
            "desc": "Master production scheduling, material demand aggregation, and automated work order generation."
        },
        "Reports": {
            "doctypes": ["Work Order", "BOM"],
            "desc": "Production progress, workstation utilization, and BOM cost comparison."
        },
        "Settings": {
            "doctypes": ["Manufacturing Settings"],
            "desc": "Overproduction allowances and shop floor backflush rules."
        },
        "Setup": {
            "doctypes": ["Operation", "Workstation", "Workstation Type", "Routing"],
            "desc": "Manufacturing operations, machinery workstations, and routing stages."
        },
        "Stock Entry": {
            "doctypes": ["Stock Entry"],
            "desc": "Manufacture stock entries, WIP staging, and scrap recording."
        },
        "Tools": {
            "doctypes": ["BOM"],
            "desc": "BOM rate replacement tools and bulk revision replanning."
        },
        "Work Order": {
            "doctypes": ["Work Order"],
            "desc": "Production batch authorization, WIP warehouse staging, and finished goods assembly."
        }
    },
    "Organization": {
        "Branch": {"doctypes": ["Branch"], "desc": "Physical corporate branch offices."},
        "Company": {"doctypes": ["Company"], "desc": "Root legal entity and chart of accounts container."},
        "Department": {"doctypes": ["Department"], "desc": "Internal operational divisions and reporting lines."},
        "Email Account": {"doctypes": ["Email Account"], "desc": "SMTP/IMAP company mailboxes."},
        "Letter Head": {"doctypes": ["Letter Head"], "desc": "Official document letterheads and headers."},
        "Role Permissions": {"doctypes": ["User Permission", "Role"], "desc": "Role based access control and row permissions."},
        "Sarathi Customer Organization": {"doctypes": ["Customer"], "desc": "Sarathi multi-tenant client organization mapping."},
        "User": {"doctypes": ["User"], "desc": "System user profiles, credentials, and roles."}
    },
    "Projects": {
        "Project": {
            "doctypes": ["Project"],
            "desc": "Industrial project planning, customer delivery tracking, and Sarathi BOM/Manufacturing links."
        },
        "Reports": {"doctypes": ["Project"], "desc": "Project costing, budget variance, and Gantt tracking."},
        "Settings": {"doctypes": ["Projects Settings"], "desc": "Timesheet billing rates and project defaults."},
        "Setup": {"doctypes": ["Project Type", "Activity Type"], "desc": "Project types and labor activity categorizations."},
        "Task": {"doctypes": ["Task"], "desc": "Discrete project work breakdown items, milestones, and dependencies."},
        "Timesheet": {"doctypes": ["Timesheet"], "desc": "Employee labor hour logging and billable project charges."}
    },
    "Quality": {
        "Non Conformance": {"doctypes": ["Quality Action"], "desc": "Corrective and preventive action (CAPA) logs."},
        "Quality Feedback": {"doctypes": ["Quality Feedback"], "desc": "Customer and supplier quality complaints."},
        "Quality Goals and Reviews": {"doctypes": ["Quality Goal"], "desc": "ISO quality objectives and management reviews."},
        "Quality Inspection": {"doctypes": ["Quality Inspection"], "desc": "Measurement testing and acceptance/rejection verdicts."},
        "Setup": {"doctypes": ["Quality Inspection Parameter", "Quality Inspection Template"], "desc": "Inspection parameters, tolerances, and checklists."}
    },
    "Selling": {
        "Items and Pricing": {"doctypes": ["Item", "Item Price"], "desc": "Sales product catalog, price lists, and discounts."},
        "POS": {"doctypes": ["POS Profile"], "desc": "Retail checkout profiles and cashier registers."},
        "Quotation": {"doctypes": ["Quotation"], "desc": "Sales proposals and commercial estimates for leads and customers."},
        "Reports": {"doctypes": ["Sales Order", "Sales Invoice"], "desc": "Sales funnel, revenue trends, and booking reports."},
        "Sales Invoice": {"doctypes": ["Sales Invoice"], "desc": "Customer tax invoices and accounts receivable recognition."},
        "Sales Order": {"doctypes": ["Sales Order"], "desc": "Confirmed customer orders and demand commitments."},
        "Settings": {"doctypes": ["Selling Settings"], "desc": "Credit limit verification and price list policies."},
        "Setup": {"doctypes": ["Customer", "Customer Group"], "desc": "Customer master records, territories, and sales partners."}
    },
    "Stock": {
        "Delivery Note": {"doctypes": ["Delivery Note"], "desc": "Outbound shipment and customer delivery fulfillment."},
        "Material Request": {"doctypes": ["Material Request"], "desc": "Internal inventory requisitions and purchase indents."},
        "Pick List": {"doctypes": ["Pick List"], "desc": "Warehouse picking slips for batch and serial item fulfillment."},
        "Purchase Receipt": {"doctypes": ["Purchase Receipt"], "desc": "Inbound vendor delivery receipts and inventory intake."},
        "Reports": {"doctypes": ["Stock Entry", "Bin"], "desc": "Perpetual stock ledger, valuation balances, and ageing."},
        "Settings": {"doctypes": ["Stock Settings"], "desc": "Zero negative stock rule and serial/batch defaults."},
        "Setup": {"doctypes": ["Item", "Item Group", "Warehouse"], "desc": "Item masters, units of measure, and warehouse hierarchy."},
        "Stock Entry": {"doctypes": ["Stock Entry"], "desc": "Material receipts, material issues, and inter-warehouse transfers."},
        "Tools": {"doctypes": ["Stock Reconciliation"], "desc": "Physical stock count reconciliations and landed cost vouchers."}
    },
    "Subcontracting": {
        "Inward Order": {"doctypes": ["Subcontracting Order"], "desc": "Outsourced job work commitments with vendor component supply."},
        "Outward Order": {"doctypes": ["Subcontracting Receipt"], "desc": "Receipt of finished subcontracted items and raw material consumption."},
        "Reports": {"doctypes": ["Subcontracting Order"], "desc": "Vendor stock tracking and material reconciliation."},
        "Settings": {"doctypes": ["Subcontracting Settings"], "desc": "Subcontracting parameters and scrap tolerances."},
        "Setup": {"doctypes": ["Subcontracting BOM"], "desc": "Service items and outsourced process specifications."},
        "Subcontracting BOM": {"doctypes": ["Subcontracting BOM"], "desc": "Bill of materials for outsourced production."}
    },
    "Users and System": {
        "Audits": {"doctypes": ["Activity Log"], "desc": "System access logs, document modification trails, and security audits."},
        "Permissions": {"doctypes": ["User Permission"], "desc": "Row level security restricting users to specific companies/records."},
        "Roles": {"doctypes": ["Role"], "desc": "System roles and module permission matrices."},
        "System Settings": {"doctypes": ["System Settings"], "desc": "Platform session controls, timezone, and security configurations."},
        "Users": {"doctypes": ["User"], "desc": "User accounts, passwords, and role allocations."}
    }
}

count_created = 0

for module_name, sections in SECTION_DEFINITIONS.items():
    mod_dir = os.path.join(BASE_DIR, module_name)
    if not os.path.isdir(mod_dir):
        continue

    for section_name, sec_meta in sections.items():
        sec_dir = os.path.join(mod_dir, section_name)
        os.makedirs(sec_dir, exist_ok=True)

        primary_dts = sec_meta.get("doctypes", [])
        desc = sec_meta.get("desc", f"{section_name} operations in {module_name}.")

        # Collect detailed field metadata for primary doctypes
        dt_fields_summary = []
        slot_questions = {}

        for dt in primary_dts:
            dt_meta = None
            mod_data = fields_data.get(module_name, {})
            if dt in mod_data:
                dt_meta = mod_data[dt]
            else:
                for other_mod, dts in fields_data.items():
                    if dt in dts:
                        dt_meta = dts[dt]
                        break

            f_list = dt_meta.get("fields", []) if isinstance(dt_meta, dict) else []

            req_fields = []
            opt_fields = []

            for fld in f_list:
                fname = fld.get("name")
                flabel = fld.get("label") or fname
                ftype = fld.get("type")
                is_req = fld.get("reqd") == 1

                if fname in ("naming_series", "docstatus", None):
                    continue

                if is_req:
                    req_fields.append(f"`{fname}` ({flabel} - {ftype})")
                    slot_questions[fname] = f"What is the {flabel}?"
                else:
                    opt_fields.append(f"`{fname}` ({flabel})")

            dt_fields_summary.append({
                "doctype": dt,
                "required": req_fields,
                "optional": opt_fields[:8]
            })

        # Generate SKILL.md for this section
        skill_lines = [
            f"# {module_name} - {section_name} Domain Skill",
            "",
            "## 1. Section Overview & Purpose",
            desc,
            "",
            f"**Module:** `{module_name}`  ",
            f"**Section Folder:** `ERPNext_Agent/{module_name}/{section_name}`  ",
            f"**Primary DocTypes:** {', '.join(primary_dts)}",
            "",
            "## 2. DocTypes & Field Requirements",
        ]

        for item in dt_fields_summary:
            skill_lines.append(f"### {item['doctype']}")
            if item['required']:
                skill_lines.append("**Mandatory Fields:**")
                for rf in item['required']:
                    skill_lines.append(f"- {rf}")
            else:
                skill_lines.append("- *No strictly required custom fields or uses standard defaults.*")

            if item['optional']:
                skill_lines.append("\n**Key Contextual Fields:**")
                for of in item['optional']:
                    skill_lines.append(f"- {of}")
            skill_lines.append("")

        skill_lines.extend([
            "## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)",
            "When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):",
            "1. **Analyze input:** Check if mandatory fields were provided.",
            "2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.",
            "3. **Required Questions:**",
        ])

        if slot_questions:
            for f_name, q_text in slot_questions.items():
                skill_lines.append(f"- **{f_name}**: *\"{q_text}\"*")
        else:
            skill_lines.append("- Identify the target DocType and ask the user for its primary identifier and owning Company.")

        skill_lines.extend([
            "",
            "## 4. Execution & Validation Workflow",
            "1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).",
            "2. Invoke `create_document` with sanitized parameters.",
            "3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.",
            "4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).",
            "5. Return a user-friendly confirmation with direct ERPNext document links.",
        ])

        skill_content = "\n".join(skill_lines)
        with open(os.path.join(sec_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_content)

        # Write section_info.json
        sec_json = {
            "module": module_name,
            "section": section_name,
            "description": desc,
            "primary_doctypes": primary_dts,
            "slot_filling_questions": slot_questions
        }
        with open(os.path.join(sec_dir, "section_info.json"), "w", encoding="utf-8") as f:
            json.dump(sec_json, f, indent=2)

        count_created += 1

print(f"Successfully generated skills for {count_created} section subfolders.")
