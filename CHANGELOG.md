# Changelog

Forked from `xy-kashif/clearent-v1` (branch: `develop`, commit: `b039c69`) to `xcspl/clearent-v1` (branch: `master`).

## Code Changes

### 1. Clean up v15→v16 structure, fix orphaned Rentclear Worker (`8322581`)

**Problem**: `rentclear worker` doctype deleted as orphan during `bench migrate`. Mix of old v15 doctype paths (`rentclear/rentclear/doctype/<underscore_name>/`) and new v16 paths (`rentclear/<module>/doctype/<Title>/`). 6 doctypes existed in BOTH locations.

**Changes**:
- Deleted `backup_json/` directory (6 backup JSON + Python files)
- Deleted 6 corrupted module-level JSONs (`rentclear/<module>/<name>.json`) — had invalid `,"custom": 1` prefixes
- Deleted 6 old v15 doctype directories that had v16 equivalents: `property/`, `lease_agreement/`, `maintenance_request/`, `property_unit/`, `rent_payment/`, `rent_subscription_plan/`
- Deleted `install_doctypes.py` — referenced corrupted files with wrong paths
- Fixed `rentclear_worker` → `Rentclear Worker`: title case doctype name in JSON, class `RentclearWorker` in Python

### 2. Fix underscore directory naming for Rentclear Worker (`9e7c85f`)

**Problem**: Directory with space (`rentclear worker/`) broke v16's backward-compat doctype lookup. All other old-style doctypes use underscore naming.

**Changes**:
- Renamed directory back to `rentclear_worker/` (underscore convention)

### 3. Comment out home_page hook to fix root URL 404 (`3800a7a`)

**Problem**: `home_page = "rentclear"` in hooks.py was picked up by `get_home_page_via_hooks()` in the website router. "rentclear" is a desk page route (`/app/rentclear`), not a valid website route. The website router failed to render it at `/` → 404.

**Changes**:
- Commented out `home_page = "rentclear"` in hooks.py
- Guest at `/` now gets login page via fallback chain

### 4. Add CAUTION.md (`a1736eb`)

Documented 5 v15→v16 migration pitfalls: home_page hook, doctype directory naming, bench migrate orphan behavior, duplicate doctype conflicts, Redis cache masking fixes.

### 5. Consolidate all doctypes under rentclear/doctype/ (`bc04b8e`, `8720a75`, `a106a13`)

**Problem**: v16 doctypes were at `rentclear/<subdir>/doctype/<Title>/` outside the main `rentclear/doctype/` directory. Frappe only scans `<app>/<module_scrubbed>/doctype/` for the "Rentclear" module. These doctypes were never registered.

**Changes**:
- Moved all 6 v16 doctypes from `rentclear/{property,lease_agreement,maintenance_request,property_unit,rent_payment,subscription_plan}/doctype/` to `rentclear/rentclear/doctype/`
- Deleted the now-empty v16 module directories
- Renamed "Subscription Plan" → "Rent Subscription Plan" to avoid conflict with ERPNext's "Subscription Plan" doctype
- Restored clean v15 JSONs from git history (the v16 copies were corrupted custom exports with `,"custom": 1` markers)
- Created proper `<name>.py` controller files for each doctype (Frappe v15 backward compat expects `<dir>/<dir>.py`, not `__init__.py`)
- Added minimal controller classes (`class Property(Document): pass`, etc.)

## Server / DB Changes

All on `contabo1`, site `dashboard.clearent.in`.

### During initial investigation (day 1)
- Identified 762 tables in `_529e41213aaec037`
- Found `rentclear worker` doctype deleted from `tabDocType`
- Found orphan `tabRentclear Worker` table (dropped)
- Set Website Settings `home_page` to NULL
- Deleted stale `_529e41213aaec037|home_page` from Redis (old cached "rentclear" value)

### During app deployment
- Switched rentclear remote from `xy-kashif/clearent-v1` (develop) → `xcspl/clearent-v1` (master)
- Multiple `bench migrate` runs, `bench restart`, `bench clear-cache`
- Created Desktop Icon entry manually (auto-generate failed due to module import issue)
- Fixed Desktop Icon `type` from NULL to "App" for direct navigation
- Fixed pip editable install: `pip install -e apps/rentclear`

### During recent doctype consolidation (day 5)
- Uninstalled and reinstalled rentclear multiple times
- Manually deleted `tabModule Def` and `tabDocType` records between reinstalls to prevent DuplicateEntryError
- All 13 doctypes now registered under "Rentclear" module

### Frontend issues fix (today, 2026-05-17)

**Fix 1 — Maintenance Request 403**:
```sql
INSERT INTO tabDocPerm (...) VALUES (..., "Maintenance Request", "System Manager", ...);
```
Granted read/write/create/delete to System Manager role on Maintenance Request doctype. This was missing because the restored v15 JSON had no permissions defined for this child table doctype, and the original DB permissions were lost during uninstall/reinstall.

**Fix 2 — Server Scripts enabled**:
```bash
bench --site dashboard.clearent.in set-config -g server_script_enabled 1
bench restart
```
The 6 API methods (`get_owner_dashboard_stats`, `get_property_units_summary`, `get_property_tenants`, `get_maintenance_summary`, `create_tenant_with_agreement`, `onboard_customer_with_kyc`) exist as Server Scripts in the database (module: "Rentclear") but were disabled server-wide.

**Fix 3 — `clearent.api.*` namespace 417**:
Created `rentclear/api/` with proper Python API modules replacing all 6 Server Scripts:
- `dashboard.py`: `get_dashboard_data`
- `tenants.py`: `send_reminder`, `add_note`, `get_property_tenants`, `create_tenant_with_agreement`, `search_tenants`
- `customers.py`: `onboard_with_kyc`
- `properties.py`: `get_units_summary`
- `documents.py`: `update_status`

Added `override_whitelisted_methods` in `hooks.py` mapping all `clearent.api.*` → `rentclear.api.*` for backward compat. Both namespaces work.

**Server Scripts made redundant**:
Removed `server_script.json` fixture. Deleted Server Script records from DB. All business logic now in version-controlled Python modules.

**Dynamic OpenAPI spec**:
Added `rentclear/api/openapi.py` with `@frappe.whitelist(allow_guest=True) get_spec()`. Auto-generates OpenAPI 3.0 spec from registered endpoints and doctypes. Cached in Redis. Served at `/api/method/rentclear.api.openapi.get_spec`.
