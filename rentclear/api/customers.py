import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def signup(email: str, full_name: str, mobile_no: str = ""):
	"""Create User + Customer in one step. Every User gets a Customer.

	Returns the OTP flow — user verifies email by logging in via OTP.
	"""
	email = email.strip().lower()
	if not email or not full_name:
		frappe.throw(_("email and full_name are required"))

	if frappe.db.exists("User", {"email": email}):
		frappe.throw(_("A user with this email already exists"), frappe.DuplicateEntryError)

	# 1. Create User
	user = frappe.new_doc("User")
	user.email = email
	user.first_name = full_name
	user.enabled = 1
	user.user_type = "Website User"
	user.send_welcome_email = 0
	user.flags.ignore_password_policy = True
	user.insert(ignore_permissions=True)

	# 2. Add Customer role
	user.add_roles("Customer")
	frappe.db.commit()

	# 3. Create Customer
	customer = frappe.new_doc("Customer")
	customer.customer_name = full_name
	customer.customer_type = "Individual"
	customer.email_id = email
	customer.mobile_no = mobile_no
	customer.flags.ignore_mandatory = True
	customer.insert(ignore_permissions=True)

	# 4. Create Contact linked to Customer
	contact = frappe.new_doc("Contact")
	contact.first_name = full_name
	contact.email_id = email
	contact.mobile_no = mobile_no
	contact.append("email_ids", {"email_id": email, "is_primary": 1})
	contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
	contact.flags.ignore_mandatory = True
	contact.insert(ignore_permissions=True)

	return {
		"user": user.name,
		"customer": customer.name,
		"customer_id": customer.name,
		"message": "Account created. Verify your email by logging in via OTP.",
	}


@frappe.whitelist()
def onboard_with_kyc(**data):
	"""One-step customer onboarding with KYC. Auto-creates User if needed."""
	customer_name = data.get("customer_name")
	customer_type = data.get("customer_type", "Individual")
	email_id = data.get("email_id")

	if not customer_name:
		frappe.throw(_("customer_name is required"))
	if not email_id:
		frappe.throw(_("email_id is required"))

	if customer_type == "Individual":
		if not data.get("aadhar_number"):
			frappe.throw(_("aadhar_number is required for Individual"))
		if not data.get("pan_number"):
			frappe.throw(_("pan_number is required for Individual"))

	# Auto-create User if no user exists for this email
	if email_id and not frappe.db.exists("User", {"email": email_id}):
		user = frappe.new_doc("User")
		user.email = email_id
		user.first_name = customer_name
		user.enabled = 1
		user.user_type = "Website User"
		user.send_welcome_email = 0
		user.flags.ignore_password_policy = True
		user.insert(ignore_permissions=True)
		user.add_roles("Customer")
		frappe.db.commit()

	# Create ERPNext Customer
	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = customer_type
	customer.salutation = data.get("salutation")
	customer.gender = data.get("gender")
	customer.email_id = email_id
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
