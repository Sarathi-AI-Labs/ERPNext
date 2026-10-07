---
name: Projects Skill
description: Industrial project execution, work breakdown structures (WBS), milestones, Gantt scheduling, timesheets, and Sarathi manufacturing links.
version: 1.0.0
module: Projects
---

# Projects & Work Breakdown Domain Skill

## 1. Domain Overview
The **Projects** module organizes delivery schedules, resource tracking, tasks, and costing. In this environment, Projects can represent internal R&D initiatives, customer delivery contracts, or discrete industrial manufacturing batches.

### Key Entities:
1. **Project**: Central planning and cost tracking container.
2. **Task**: Discrete work unit within a project, featuring hierarchical dependencies (parent/child tasks), milestone flags, assignees, and expected completion dates.
3. **Timesheet**: Submittable log capturing labor hours spent by employees on specific project tasks, calculating billing and costing amounts.
4. **Activity Type**: Standard categorization for labor hours (e.g., "Engineering Design", "Quality Audit", "Assembly").

---

## 2. Field Requirements & Custom Integrations

### Project
- **project_name** (Data, Required): Official title.
- **company** (Link Company, Required): Operating entity.
- **status** (Select: "Open", "Completed", "Cancelled", "On Hold", Default "Open").
- **expected_start_date** (Date, Optional).
- **expected_end_date** (Date, Optional).
- **customer** (Link Customer, Optional).
- **custom_sarathi_manufacturing** (Check, Custom): Flag indicating that this project triggers manufacturing workflows.
- **custom_sarathi_bom** (Link BOM, Custom): Explicit link to engineering BOM produced under this project.

### Task
- **subject** (Data, Required): Short descriptive task title.
- **project** (Link Project, Required): Owning project.
- **exp_start_date** (Date, Optional).
- **exp_end_date** (Date, Optional).
- **status** (Select: "Open", "Working", "Pending Review", "Completed", "Cancelled", Default "Open").
- **is_milestone** (Check, Default 0).

---

## 3. Workflow & Lifecycle Transitions
- `Project`: Open -> Completed / Cancelled / On Hold.
- `Task`: Open -> Working -> Pending Review -> Completed.
- `Timesheet`: Draft (0) -> Submitted (1) -> Cancelled (2).
  - Submitting a timesheet locks logged hours and can generate automated Sales Invoices (if billable) or Salary Slips.
