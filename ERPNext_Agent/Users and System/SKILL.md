---
name: Users and System Skill
description: Access control, user provisioning, role-based security (RBAC), user permissions, row-level restrictions, and system settings.
version: 1.0.0
module: Users and System
---

# Users, Security & System Administration Domain Skill

## 1. Domain Overview
The **Users and System** module governs identity, authentication, granular access permissions, row-level data segregation, and site-wide configuration.

### Key Entities:
1. **User**: Login account identity (e.g. `user@sarathiailabs.com`). Contains enabled status, password hash, role assignments, and language/timezone preferences.
2. **Role**: Functional permission profile (e.g. `Stock Manager`, `Manufacturing User`, `Accounts Manager`, `System Manager`).
3. **Role Profile**: Preset bundle of multiple roles assignable to users with one click.
4. **User Permission**: Row-level security restriction limiting a specific user to records linked to a specific entity (e.g., restricting user to Company `SarathiAILabs` or Warehouse `Stores - S`).
5. **System Settings**: Global framework settings (session timeout, default language, date format, two-factor auth).

---

## 2. Field Requirements & Rules

### User
- **email** (Data, Required): Unique login username / email.
- **first_name** (Data, Required).
- **enabled** (Check, Default 1).
- **send_welcome_email** (Check, Default 0 in automated tests).
- **roles** (Table Has Role): Assigned system roles.

### User Permission
- **user** (Link User, Required).
- **allow** (Link DocType, Required): Restricted DocType (e.g. `Company`).
- **for_value** (Dynamic Link, Required): Specific record (e.g. `SarathiAILabs`).
- **is_default** (Check, Default 0).

---

## 3. Workflow & Lifecycle Transitions
- System and user security records are non-submittable (`is_submittable = 0`).
- Permissions take effect on the user's next request or after session reload.
