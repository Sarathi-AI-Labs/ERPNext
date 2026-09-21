DEFAULT_COMPANY = "Sarathi Manufacturing Pvt Ltd"
DEFAULT_PROJECT_CODE = "PRJ-MEZZANINE-001"
DEFAULT_PROJECT_DOC = "PROJ-0002"
DEFAULT_SALES_ORDER = "Sales Order 368"

PIPELINE_WEIGHTS = [
    {"stage": "Design", "weight": 10, "task": "Design & CAD"},
    {"stage": "BOM", "weight": 10, "task": "Engineering / BOM"},
    {"stage": "Materials", "weight": 15, "task": "Material Planning"},
    {"stage": "Cutting", "weight": 15, "task": "Cutting"},
    {"stage": "Fabrication", "weight": 15, "task": "Fabrication"},
    {"stage": "Welding", "weight": 10, "task": "Welding"},
    {"stage": "Painting", "weight": 10, "task": "Painting"},
    {"stage": "Inspection", "weight": 10, "task": "Final Inspection"},
    {"stage": "Completion", "weight": 5, "task": "Project Completion"},
]

PROJECT_TASKS = [
    {"id": "01", "subject": "Design & CAD"},
    {"id": "02", "subject": "Engineering / BOM"},
    {"id": "03", "subject": "Material Planning"},
    {"id": "04", "subject": "Procurement"},
    {"id": "05", "subject": "Cutting"},
    {"id": "06", "subject": "Fabrication"},
    {"id": "07", "subject": "Welding"},
    {"id": "08", "subject": "Grinding / Finishing"},
    {"id": "09", "subject": "Painting"},
    {"id": "10", "subject": "Final Assembly"},
    {"id": "11", "subject": "Final Inspection"},
    {"id": "12", "subject": "Project Completion"},
]

ENGINEERING_COMPONENTS = [
    {"no": 1, "material": "SQ. PIPE 100X100 2MM THK", "cutting_size": "2984", "qty": 27},
    {"no": 2, "material": "BASE PLATE-01-8MM", "cutting_size": "200X200", "qty": 32},
    {"no": 3, "material": "COLUMN RIB-5MM", "cutting_size": "80X40", "qty": 216},
    {"no": 4, "material": "GIRDER-2460-01-3MM-LH & RH", "cutting_size": "1278.5X388", "qty": 40},
    {"no": 5, "material": "GIRDER-2460-02-3MM-LH & RH", "cutting_size": "1227X388", "qty": 44},
    {"no": 6, "material": "GIRDER-100-3MM-LH & RH", "cutting_size": "97X388", "qty": 4},
    {"no": 7, "material": "GIRDER JOINT BRK-01-2MM", "cutting_size": "305X100", "qty": 20},
    {"no": 8, "material": "GIRDER JOINT BRK-02-2MM", "cutting_size": "305X100", "qty": 22},
    {"no": 9, "material": "BASE PLATE-02-8MM", "cutting_size": "97X200", "qty": 32},
    {"no": 10, "material": "COLUMN BRACKET-5MM", "cutting_size": "200X439", "qty": 4},
    {"no": 11, "material": "COLUMN BRACKET RIB-5MM", "cutting_size": "150X200", "qty": 4},
    {"no": 12, "material": "SUB GIRDER-2933-2MM-LH & RH", "cutting_size": "1458X335", "qty": 232},
    {"no": 13, "material": "SUB GIRDER-2452-2MM-LH & RH", "cutting_size": "1217.5X335", "qty": 80},
    {"no": 14, "material": "SUB GIRDER-1183-2MM-LH & RH", "cutting_size": "1183X335", "qty": 10},
    {"no": 15, "material": "SUB GIRDER-1100-2MM-LH & RH", "cutting_size": "1070X335", "qty": 2},
    {"no": 16, "material": "SUB GIRDER-1800-2MM-LH & RH", "cutting_size": "1780X335", "qty": 2},
    {"no": 17, "material": "SUB GIRDER-2490-2MM-LH & RH", "cutting_size": "2485X335", "qty": 2},
    {"no": 18, "material": "SUB GIRDER-380-2MM-LH & RH", "cutting_size": "355X335", "qty": 2},
    {"no": 19, "material": "SUB GIRDER-JOINT-2MM-01", "cutting_size": "255X100", "qty": 160},
    {"no": 20, "material": "SUB GIRDER-JOINT-2MM-02", "cutting_size": "255X70", "qty": 320},
    {"no": 21, "material": "SUB GIRDER-JOINT-3MM-03", "cutting_size": "120X190", "qty": 170},
    {"no": 22, "material": "SUB GIRDER RESTING BRK-3MM", "cutting_size": "200X200", "qty": 4},
    {"no": 23, "material": "RAILING GIRDER BRK-5MM-1", "cutting_size": "101X307", "qty": 14},
    {"no": 24, "material": "RAILING SUB GIRDER BRK-5MM-1", "cutting_size": "101X357", "qty": 24},
    {"no": 25, "material": "RAILING PIPE CLAMPING BRK-2MM", "cutting_size": "120X100", "qty": 75},
    {"no": 26, "material": "RAILING PIPE BRK-2MM", "cutting_size": "100X72", "qty": 50},
    {"no": 27, "material": "RAILING PIPE-40X40X1.2 THK", "cutting_size": "1350", "qty": 32},
    {"no": 28, "material": "RAILING PIPE-25X50X1.2 THK", "cutting_size": "2995", "qty": 24},
]

BOP_ITEMS = [
    {"item": "M12 L=40 NUT AND BOLT WITH 2 WASHER", "qty": 600},
    {"item": "M12 L=60 NUT AND BOLT WITH 2 WASHER", "qty": 100},
    {"item": "FASTENER M12 L-100", "qty": 120},
]

RAW_STOCK_PLAN = [
    {"stock": "SQ. PIPE 40X40X1.2 THK-HR", "planned_qty": 8, "weight_kg": 72},
    {"stock": "PIPE 25X50 X 1.2 THK-HR", "planned_qty": 12, "weight_kg": 98.4},
    {"stock": "SQ. PIPE 100X100X2 THK-HR", "planned_qty": 14, "weight_kg": 518},
    {"stock": "1250X2500X8 THK-HR", "planned_qty": 1, "weight_kg": 196.25},
    {"stock": "1250X2500X3 THK-HR", "planned_qty": 16, "weight_kg": 1177.5},
    {"stock": "1500X2500X2 THK-HR", "planned_qty": 48, "weight_kg": 2826},
    {"stock": "1250X2500X5 THK-HR", "planned_qty": 1, "weight_kg": 122.7},
]
