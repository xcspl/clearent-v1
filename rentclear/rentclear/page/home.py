import frappe

def get_context(context):
    context.properties_count = frappe.db.count('Property')
    context.units_count = frappe.db.count('Property Unit')
    context.leases_count = frappe.db.count('Lease Agreement')
    context.maintenance_count = frappe.db.count('Maintenance Request', {'status': 'Open'})
    return context
