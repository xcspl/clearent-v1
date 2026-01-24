import frappe

def execute():
    """Add custom KYC fields to Customer DocType"""

    # Check if fields already exist
    if frappe.db.exists('Custom Field', {'dt': 'Customer', 'fieldname': 'aadhar_no'}):
        print('Customer custom fields already exist. Skipping patch.')
        return

    # Define custom fields
    fields = [
        {
            'dt': 'Customer',
            'fieldname': 'aadhar_no',
            'label': 'Aadhar Number',
            'fieldtype': 'Data',
            'insert_after': 'customer_details',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'pan_document',
            'label': 'PAN number',
            'fieldtype': 'Data',
            'insert_after': 'aadhar_no',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'gst_no',
            'label': 'GST Number',
            'fieldtype': 'Data',
            'insert_after': 'pan_document',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'company_pan_number',
            'label': 'Company PAN',
            'fieldtype': 'Data',
            'insert_after': 'gst_no',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'director_name',
            'label': 'Director Name',
            'fieldtype': 'Data',
            'insert_after': 'company_pan_number',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'director_aadhar_number',
            'label': 'Director Aadhar Number',
            'fieldtype': 'Data',
            'insert_after': 'director_name',
            'module': 'Rentclear',
            'hidden': 0
        },
        {
            'dt': 'Customer',
            'fieldname': 'associated_properties',
            'label': 'Associated Properties',
            'fieldtype': 'Table',
            'options': 'Associated Properties',
            'insert_after': 'director_aadhar_number',
            'module': 'Rentclear',
            'hidden': 0
        }
    ]

    # Create custom fields
    for field_data in fields:
        field = frappe.new_doc('Custom Field')
        field.update(field_data)
        field.insert()

    frappe.db.commit()
    print('Customer KYC custom fields added successfully')
