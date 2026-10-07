---
name: Quality Skill
description: Quality assurance, incoming raw material inspections, in-process testing, final product inspections, parameters, and corrective actions.
version: 1.0.0
module: Quality
---

# Quality & Inspection Domain Skill

## 1. Domain Overview
The **Quality** module guarantees standard adherence across procurement, in-house manufacturing, and customer delivery. Quality inspections can be mandatory gates before goods are accepted into stock or dispatched.

### Key Entities:
1. **Quality Inspection Parameter**: Atomic measurable metric (e.g., "Tensile Strength", "Outer Diameter", "Surface Roughness", "Input Voltage").
2. **Quality Inspection Template**: Standardized checklist aggregating parameters with acceptance criteria, minimum, maximum, and target values.
3. **Quality Inspection (QI)**: Submittable audit record comparing sampled measurements against template thresholds, resulting in a binary `Accepted` or `Rejected` verdict.
4. **Quality Action (CAPA)**: Corrective and Preventive Action record logged to address recurring defects or non-conformances.

---

## 2. Field Requirements & Rules

### Quality Inspection
- **inspection_type** (Select: "Incoming", "Outgoing", "In Process", Required).
- **reference_type** (Link DocType): e.g. `Purchase Receipt`, `Delivery Note`, `Stock Entry`, `Job Card`.
- **reference_name** (Dynamic Link): Document identifier.
- **item_code** (Link Item, Required): Item being tested.
- **sample_size** (Float, Required, default 1.0).
- **status** (Select: "Accepted", "Rejected", Required).
- **readings** (Table Quality Inspection Reading, Required):
  - **specification** (Link Quality Inspection Parameter, Required)
  - **min_value** (Float)
  - **max_value** (Float)
  - **reading_1** (Data, Required)
  - **status** (Select: "Accepted", "Rejected")

---

## 3. Workflow & Lifecycle Transitions
- `Quality Inspection`:
  - Draft (0) -> Submitted (1) -> Cancelled (2).
  - If linked to a Purchase Receipt with inspection required, the receipt cannot be submitted until QI has status `Accepted` and `docstatus = 1`.
