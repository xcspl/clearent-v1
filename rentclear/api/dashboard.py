import frappe
from frappe import _


@frappe.whitelist()
def get_dashboard_data(customer_id: str | None = None, property_id: str | None = None):
	"""Aggregate owner/property dashboard data."""
	result = {
		"total_properties": 0, "total_units": 0, "occupied_units": 0,
		"pending_maintenance": 0, "active_tenants": 0, "monthly_revenue": 0,
		"occupancy_rate": 0, "open_requests": 0, "in_progress": 0,
		"high_priority": 0, "emergency": 0, "resolved_this_month": 0,
	}

	if customer_id:
		# Owner stats
		result["total_properties"] = frappe.db.count("Property", {"prop_owner": customer_id})
		result["total_units"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabProperty Unit`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
		""", customer_id)[0][0]
		result["occupied_units"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabProperty Unit`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status = 'Occupied'
		""", customer_id)[0][0]
		result["pending_maintenance"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status != 'Resolved'
		""", customer_id)[0][0]
		result["active_tenants"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabLease Agreement`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status = 'Active'
		""", customer_id)[0][0]
		result["monthly_revenue"] = frappe.db.sql("""
			SELECT COALESCE(SUM(payment_amount), 0) FROM `tabRent Payment`
			WHERE payment_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
			AND payment_status = 'Paid'
			AND lease_agreement IN (
				SELECT name FROM `tabLease Agreement`
				WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			)
		""", customer_id)[0][0]
		if result["total_units"] > 0:
			result["occupancy_rate"] = round(result["occupied_units"] * 100.0 / result["total_units"], 1)

		# Maintenance summary
		result["open_requests"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status = 'Open'
		""", customer_id)[0][0]
		result["in_progress"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status = 'In Progress'
		""", customer_id)[0][0]
		result["high_priority"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND priority = 'High'
		""", customer_id)[0][0]
		result["emergency"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND priority = 'Emergency'
		""", customer_id)[0][0]
		one_month_ago = frappe.utils.add_months(frappe.utils.now(), -1)
		result["resolved_this_month"] = frappe.db.sql("""
			SELECT COUNT(*) FROM `tabMaintenance Request`
			WHERE property IN (SELECT name FROM `tabProperty` WHERE prop_owner = %s)
			AND status = 'Resolved' AND modified >= %s
		""", (customer_id, one_month_ago))[0][0]

	elif property_id:
		result["total_units"] = frappe.db.count("Property Unit", {"property": property_id})
		result["open_requests"] = frappe.db.count("Maintenance Request", {"property": property_id, "status": "Open"})
		result["in_progress"] = frappe.db.count("Maintenance Request", {"property": property_id, "status": "In Progress"})
		result["high_priority"] = frappe.db.count("Maintenance Request", {"property": property_id, "priority": "High"})
		result["emergency"] = frappe.db.count("Maintenance Request", {"property": property_id, "priority": "Emergency"})
		one_month_ago = frappe.utils.add_months(frappe.utils.now(), -1)
		result["resolved_this_month"] = frappe.db.count("Maintenance Request",
			{"property": property_id, "status": "Resolved", "modified": (">=", one_month_ago)})

	return result
