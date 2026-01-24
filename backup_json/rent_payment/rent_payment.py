import frappe
from frappe.model.document import Document

class RentPayment(Document):
    def validate(self):
        if not self.payment_date:
            self.payment_date = frappe.utils.today()
        self.calculate_net_amount()
    
    def calculate_net_amount(self):
        self.net_amount = (self.payment_amount or 0) - (self.maintenance_deducted or 0) - (self.balance_deducted or 0) + (self.late_fee or 0)
