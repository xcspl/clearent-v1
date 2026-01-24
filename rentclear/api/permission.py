import frappe

def has_app_permission():
    """Check if user has access to Rentclear app"""
    return frappe.session.user != 'Guest'
