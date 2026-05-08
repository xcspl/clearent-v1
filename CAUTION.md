# CAUTION — v15 to v16 Migration Issues

This app was originally built for Frappe v15 and migrated to v16. Below are the known pitfalls and their fixes (applied 2026-05-08).

## 1. Do Not Set `home_page` in hooks.py to a Desk-Only Route

Setting `home_page = "rentclear"` in `hooks.py` broke the root `/` URL on the website because Frappe's `get_home_page_via_hooks()` tries to render it as a **website** page. Desk pages (like `/app/rentclear`) are not valid website routes.

**Fix**: Leave `home_page` commented out in hooks.py. The fallback chain handles it:
- Guest at `/` → login page
- System user after login → "me" → "desk"

## 2. Doctype Directory Naming Matters in v16

Frappe v16's doctype loader expects either:
- **v16 style**: `doctype/<Exact Name>/<Exact Name>.json` (directory matches doctype name exactly, including spaces)
- **v15 fallback**: `doctype/<underscore_name>/<underscore_name>.json`

The doctype `name` field in the JSON must be **proper title case** (e.g., "Rentclear Worker", not "rentclear worker"). A mismatch causes the doctype to be flagged as **orphaned** and deleted during `bench migrate`.

## 3. `bench migrate` Deletes Orphaned Doctypes

Running `bench migrate` after a v15→v16 upgrade scans all installed apps. If a doctype's JSON file can't be found at a recognized path, the DocType record is **deleted** from `tabDocType`. The table remains but is empty. Fix the app code and re-run migrate to re-register.

## 4. Duplicate Doctypes Cause Conflicts

Having the same doctype JSON in both old v15 path (`doctype/<name>/`) and new v16 path (`<module>/doctype/<Title>/`) creates ambiguity. Keep only one copy — prefer the v16 module structure.

## 5. Stale Redis Cache Can Mask Fixes

`get_home_page()` caches its result in Redis as `{site}|home_page`. After changing `home_page` in hooks or Website Settings, delete this key or run `bench clear-cache`. A bench restart alone does NOT clear it.
