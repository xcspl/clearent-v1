import frappe
from frappe import _


@frappe.whitelist()
def get_units_summary(property_id: str):
	"""Get property units grouped by status."""
	if not property_id:
		frappe.throw(_("property_id is required"))

	units_by_status = frappe.db.sql("""
		SELECT status, COUNT(*) as count
		FROM `tabProperty Unit`
		WHERE property = %s
		GROUP BY status
	""", property_id, as_dict=True)

	total_units = frappe.db.count("Property Unit", {"property": property_id})
	by_status = {row.status: row["count"] for row in units_by_status}

	return {"total_units": total_units, "by_status": by_status}
