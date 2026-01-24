import frappe
from frappe.model.document import Document

class MaintenanceRequest(Document):
    def validate(self):
        if not self.reported_date:
            self.reported_date = frappe.utils.today()
        
        if self.status == 'Resolved' and not self.resolution_date:
            self.resolution_date = frappe.utils.today()
