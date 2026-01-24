import frappe
import json
import os

def install_doctypes():
    doctypes = [
        ('Property', 'property'),
        ('Property Unit', 'property_unit'),
        ('Lease Agreement', 'lease_agreement'),
        ('Maintenance Request', 'maintenance_request'),
        ('Rent Payment', 'rent_payment'),
        ('Subscription Plan', 'subscription_plan')
    ]
    
    app_path = '/home/devpctwo/frappe-bench/apps/rentclear/rentclear'
    
    for dt_name, folder_name in doctypes:
        json_path = os.path.join(app_path, folder_name, f'{folder_name}.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            if not frappe.db.exists('DocType', dt_name):
                print(f'Creating {dt_name}...')
                doc = frappe.get_doc(data)
                doc.insert()
                print(f'{dt_name} created successfully')
            else:
                print(f'{dt_name} already exists')
    
    frappe.db.commit()
    print('All DocTypes installed!')

if __name__ == '__main__':
    install_doctypes()
