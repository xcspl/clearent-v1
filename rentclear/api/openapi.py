"""Auto-generate OpenAPI 3.0 spec for rentclear/clearent API.

Cached in Redis, invalidated on bench migrate or clear-cache.
Served at /api/method/rentclear.api.openapi.get_spec
"""

import json
import frappe


@frappe.whitelist(allow_guest=True)
def get_spec():
	"""Return OpenAPI 3.0 JSON spec. Cached until next deploy."""
	cache_key = frappe.cache.make_key("openapi_spec")
	spec = frappe.cache.get_value(cache_key)
	if spec:
		return spec

	spec = _build_spec()
	frappe.cache.set_value(cache_key, spec, expires_in_sec=None)
	return spec


def _build_spec():
	base_url = frappe.utils.get_url()
	site_name = frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or "Frappe"

	spec = {
		"openapi": "3.0.3",
		"info": {
			"title": "Clearent API",
			"version": "v3",
			"description": "API for Clearent property rental management. All endpoints accept token auth (Authorization: token <key>:<secret>) or cookie auth.",
		},
		"servers": [{"url": base_url, "description": site_name}],
		"paths": {},
		"components": {
			"securitySchemes": {
				"token": {"type": "http", "scheme": "bearer", "bearerFormat": "token <key>:<secret>"},
			}
		},
		"security": [{"token": []}],
	}

	_add_api_methods(spec)
	_add_doctype_crud(spec)
	_add_frappe_endpoints(spec)

	return spec


def _add_api_methods(spec):
	"""Add all rentclear.api.* whitelisted methods with docstring-based descriptions."""
	methods = [
		# Dashboard
		("rentclear.api.dashboard.get_dashboard_data", "GET", "Dashboard",
		 "Get owner/property dashboard stats", [("customer_id", "str"), ("property_id", "str")]),
		# Tenants
		("rentclear.api.tenants.get_property_tenants", "GET", "Tenants",
			"List tenants for a property", [("property_id", "str")]),
		("rentclear.api.tenants.search_tenants", "GET", "Tenants",
			"Search tenants by email, phone, or name", [("search", "str"), ("search_field", "str")]),
		("rentclear.api.tenants.send_reminder", "POST", "Tenants",
			"Send rent reminder to tenant", [("tenant_id", "str")]),
		("rentclear.api.tenants.add_note", "POST", "Tenants",
			"Add note to tenant record", [("tenant_id", "str"), ("note", "str")]),
		("rentclear.api.tenants.create_tenant_with_agreement", "POST", "Tenants",
			"Create tenant with lease agreement in one call", []),
		# Properties
		("rentclear.api.properties.get_units_summary", "GET", "Properties",
			"Get property units grouped by status", [("property_id", "str")]),
		# Customers
		("rentclear.api.customers.signup", "POST", "Customers",
		"Create User + Customer in one step. OTP verifies email.", [("email", "str"), ("full_name", "str"), ("mobile_no", "str")]),
		("rentclear.api.customers.onboard_with_kyc", "POST", "Customers",
			"One-step customer onboarding with KYC", []),
		# Documents
		("rentclear.api.documents.update_status", "POST", "Documents",
			"Update KYC document verification status", [("customer_id", "str"), ("document_type", "str"), ("status", "str")]),
		# OTP Login
		("frappe_otp_login.api.get_available_channels", "GET", "Auth",
			"List available OTP channels", []),
		("frappe_otp_login.api.send_otp", "POST", "Auth",
			"Send OTP via channel", [("identifier", "str"), ("channel", "str")]),
		("frappe_otp_login.api.verify_otp", "POST", "Auth",
			"Verify OTP and get auth token", [("identifier", "str"), ("otp", "str")]),
	]

	for path, method, tag, summary, params in methods:
		op = {
			"tags": [tag],
			"summary": summary,
			"operationId": path.replace(".", "_"),
			"responses": {"200": {"description": "Success"}},
		}
		if params:
			op["parameters"] = [
				{"name": p[0], "in": "query" if method == "GET" else "query", "schema": {"type": p[1]}}
				for p in params
			]
		spec["paths"].setdefault(f"/api/method/{path}", {})[method.lower()] = op

		# Also add clearent.api.* alias
		clearent_path = path.replace("rentclear.api.", "clearent.api.")
		if clearent_path != path:
			spec["paths"].setdefault(f"/api/method/{clearent_path}", {})[method.lower()] = dict(op)


def _add_doctype_crud(spec):
	"""Add standard Frappe REST CRUD for rentclear doctypes."""
	doctypes = [
		("Property", "Properties"),
		("Property Unit", "Properties"),
		("Lease Agreement", "Lease Agreements"),
		("Maintenance Request", "Maintenance"),
		("Rent Payment", "Rent Payments"),
		("Rentclear Customer", "Customers"),
		("Rent Subscription Plan", "Subscriptions"),
		("Clearent member", "Customers"),
		("Property Manager Profile", "Properties"),
	]

	for dt, tag in doctypes:
		dt_slug = dt.replace(" ", "%20")
		base = f"/api/resource/{dt_slug}"

		# GET list
		spec["paths"].setdefault(base, {})["get"] = {
			"tags": [tag], "summary": f"List {dt}",
			"operationId": f"list_{dt.lower().replace(' ','_')}",
			"responses": {"200": {"description": "Success"}},
		}

		# POST create
		spec["paths"].setdefault(base, {})["post"] = {
			"tags": [tag], "summary": f"Create {dt}",
			"operationId": f"create_{dt.lower().replace(' ','_')}",
			"responses": {"200": {"description": "Success"}},
		}

		# GET by ID
		detail = f"{base}/{{id}}"
		for method, summary in [("get", "Get"), ("put", "Update"), ("delete", "Delete")]:
			spec["paths"].setdefault(detail, {})[method] = {
				"tags": [tag], "summary": f"{summary} {dt} by ID",
				"operationId": f"{method}_{dt.lower().replace(' ','_')}",
				"parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
				"responses": {"200": {"description": "Success"}},
			}


def _add_frappe_endpoints(spec):
	"""Add Frappe built-in endpoints used by the frontend."""
	endpoints = [
		("/api/method/upload_file", "POST", "Files", "Upload a file"),
		("/api/method/login", "POST", "Auth", "Password login"),
		("/api/method/logout", "POST", "Auth", "Logout"),
		("/api/method/frappe.auth.get_logged_user", "GET", "Auth", "Get current user"),
	]
	for path, method, tag, summary in endpoints:
		spec["paths"].setdefault(path, {})[method.lower()] = {
			"tags": [tag], "summary": summary, "operationId": path.replace("/", "_"),
			"responses": {"200": {"description": "Success"}},
		}
