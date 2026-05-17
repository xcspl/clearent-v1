import frappe
from frappe import _


@frappe.whitelist()
def update_status(customer_id: str, document_type: str, status: str):
	"""Update KYC document verification status for a Rentclear Customer."""
	if not customer_id or not document_type:
		frappe.throw(_("customer_id and document_type are required"))

	valid_docs = {
		"aadhar": "aadhar_verified",
		"pan": "pan_verified",
		"gst": "gst_verified",
		"company_id": "company_id_verified",
	}
	doc_field = valid_docs.get(document_type)
	if not doc_field:
		frappe.throw(_("Invalid document_type. Valid: {0}").format(", ".join(valid_docs.keys())))

	frappe.db.set_value("Rentclear Customer", customer_id, doc_field, 1 if status == "verified" else 0)

	return {"message": "Document status updated", "customer_id": customer_id, "field": doc_field}
