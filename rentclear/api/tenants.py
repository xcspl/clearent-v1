import frappe
from frappe import _


@frappe.whitelist()
def send_reminder(tenant_id: str):
	"""Send a rent reminder to a tenant."""
	tenant = frappe.get_doc("Rentclear Customer", tenant_id)
	if not tenant.erpnext_customer:
		frappe.throw(_("No linked ERPNext Customer found"))

	customer = frappe.get_doc("Customer", tenant.erpnext_customer)
	if not customer.email_id and not customer.mobile_no:
		frappe.throw(_("Tenant has no email or phone number on file"))

	leases = frappe.get_all("Lease Agreement",
		filters={"tenant": tenant_id, "status": "Active"},
		fields=["name", "rent_amount", "payment_due_day", "property"],
		limit=1)

	if not leases:
		frappe.throw(_("No active lease found for this tenant"))

	lease = leases[0]
	property_name = frappe.db.get_value("Property", lease.property, "property_name")

	message = _("Dear Tenant, your rent of {0} for {1} is due by day {2}. Please make payment at your earliest convenience.").format(
		frappe.utils.fmt_money(lease.rent_amount, currency="INR"),
		property_name or "your property",
		lease.payment_due_day or 5,
	)

	comm = frappe.new_doc("Communication")
	comm.subject = _("Rent Reminder - {0}").format(property_name or "Property")
	comm.content = message
	comm.communication_type = "Automated Message"
	comm.reference_doctype = "Rentclear Customer"
	comm.reference_name = tenant_id
	comm.sender = frappe.session.user
	comm.recipients = customer.email_id
	comm.insert(ignore_permissions=True)

	return {"message": "Reminder sent", "communication": comm.name}


@frappe.whitelist()
def add_note(tenant_id: str, note: str):
	"""Add a note/comment to a tenant record."""
	if not note or not note.strip():
		frappe.throw(_("Note text is required"))

	tenant = frappe.get_doc("Rentclear Customer", tenant_id)
	tenant.add_comment("Comment", note.strip())

	return {"message": "Note added", "tenant": tenant_id}


@frappe.whitelist()
def get_property_tenants(property_id: str):
	"""Get all active tenants for a property with lease details."""
	if not property_id:
		frappe.throw(_("property_id is required"))

	agreements = frappe.get_all("Lease Agreement",
		filters={"property": property_id, "status": "Active"},
		fields=["name", "tenant", "property_unit", "start_date", "end_date", "rent_amount"],
		order_by="start_date desc")

	result = []
	for a in agreements:
		tenant_fields = frappe.db.get_value("Rentclear Customer", a.tenant,
			["erpnext_customer", "customer_type"])
		customer_name = customer_mobile = customer_email = ""
		if tenant_fields:
			cust = frappe.db.get_value("Customer", tenant_fields[0],
				["customer_name", "mobile_no", "email_id"])
			if cust:
				customer_name = cust[0] or ""
				customer_mobile = cust[1] or ""
				customer_email = cust[2] or ""

		unit = frappe.db.get_value("Property Unit", a.property_unit, ["unit_number", "unit_type"])

		result.append({
			"agreement_id": a.name,
			"tenant_id": a.tenant,
			"tenant_name": customer_name,
			"tenant_mobile": customer_mobile,
			"tenant_email": customer_email,
			"unit_id": a.property_unit,
			"unit_number": unit[0] if unit else "",
			"unit_type": unit[1] if unit else "",
			"start_date": str(a.start_date),
			"end_date": str(a.end_date),
			"rent_amount": a.rent_amount,
		})

	return result


@frappe.whitelist()
def create_tenant_with_agreement(**data):
	"""Create a tenant (Customer + Rentclear Customer) and a lease agreement in one call."""
	customer_name = data.get("customer_name")
	if not customer_name:
		frappe.throw(_("customer_name is required"))

	# Create ERPNext Customer
	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = data.get("customer_type", "Individual")
	customer.email_id = data.get("email")
	customer.mobile_no = data.get("phone")
	customer.insert()

	# Create Rentclear Customer
	rc = frappe.new_doc("Rentclear Customer")
	rc.erpnext_customer = customer.name
	rc.customer_type = data.get("customer_type", "Individual")
	rc.aadhar_number = data.get("aadhar_number", "")
	rc.pan_number = data.get("pan_number", "")
	rc.is_tenant = 1
	rc.insert()

	# Create Lease Agreement
	lease = frappe.new_doc("Lease Agreement")
	lease.property = data.get("property_id")
	lease.property_unit = data.get("property_unit_id")
	lease.tenant = rc.name
	lease.start_date = data.get("start_date")
	lease.end_date = data.get("end_date")
	lease.rent_amount = data.get("rent_amount")
	lease.security_deposit = data.get("security_deposit", 0)
	lease.payment_due_day = data.get("payment_due_day", 5)
	lease.status = "Active"
	lease.insert()

	# Update Property Unit status
	frappe.db.set_value("Property Unit", data.get("property_unit_id"), {
		"status": "Occupied",
		"current_tenant": rc.name,
		"current_lease": lease.name,
	})

	return {
		"customer_id": rc.name,
		"lease_agreement_id": lease.name,
		"message": "Tenant and agreement created successfully",
	}
