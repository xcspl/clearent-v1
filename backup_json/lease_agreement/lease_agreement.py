import frappe
from frappe.model.document import Document

class LeaseAgreement(Document):
    def on_submit(self):
        if self.property_unit:
            frappe.db.set_value('Property Unit', self.property_unit, {
                'status': 'Occupied',
                'current_tenant': self.tenant,
                'current_lease': self.name
            })
    
    def on_cancel(self):
        if self.property_unit:
            frappe.db.set_value('Property Unit', self.property_unit, {
                'status': 'Available',
                'current_tenant': None,
                'current_lease': None
            })
