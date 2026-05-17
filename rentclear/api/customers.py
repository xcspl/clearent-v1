import frappe
from frappe import _


@frappe.whitelist()
def onboard_with_kyc(**data):
	"""One-step customer onboarding with KYC. Wraps the onboard_customer_with_kyc server script."""
	customer_name = data.get("customer_name")
	customer_type = data.get("customer_type", "Individual")
	if not customer_name:
		frappe.throw(_("customer_name is required"))

	if customer_type == "Individual":
		if not data.get("aadhar_number"):
			frappe.throw(_("aadhar_number is required for Individual"))
		if not data.get("pan_number"):
			frappe.throw(_("pan_number is required for Individual"))

	# Create ERPNext Customer
	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = customer_type
	customer.salutation = data.get("salutation")
	customer.gender = data.get("gender")
	customer.email_id = data.get("email_id")
	customer.mobile_no = data.get("mobile_no")
	customer.phone = data.get("phone")
	customer.customer_group = "Individual"
	customer.territory = "All Territories"
	customer.default_currency = "INR"
	customer.language = "en"
	customer.insert()

	# Create Rentclear Customer
	rc = frappe.new_doc("Rentclear Customer")
	rc.naming_series = "RC-.####"
	rc.erpnext_customer = customer.name
	rc.customer_type = customer_type
	rc.is_property_owner = data.get("is_property_owner", 0)
	rc.is_tenant = data.get("is_tenant", 0)
	rc.aadhar_number = data.get("aadhar_number")
	rc.aadhar_document = data.get("aadhar_document")
	rc.pan_number = data.get("pan_number")
	rc.pan_document = data.get("pan_document")
	rc.gst_number = data.get("gst_number")
	rc.gst_certificate = data.get("gst_certificate")
	rc.company_pan_number = data.get("company_pan_number")
	rc.company_id_type = data.get("company_id_type")
	rc.company_id_number = data.get("company_id_number")
	rc.company_id = data.get("company_id")
	rc.director_name = data.get("director_name")
	rc.director_aadhar_number = data.get("director_aadhar_number")
	rc.director_aadhar_document = data.get("director_aadhar_document")
	rc.director_pan_for_proprietorship = data.get("director_pan_for_proprietorship")
	rc.kyc_verified = data.get("kyc_verified", 0)
	rc.notes = data.get("notes")
	rc.insert()

	return {
		"erpnext_customer_id": customer.name,
		"rentclear_customer_id": rc.name,
		"customer_name": customer_name,
		"customer_type": customer_type,
		"message": "Customer onboarded successfully with KYC",
	}
