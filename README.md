# Clearent - Property Rental Management

Custom ERPNext application for property rental management system.

## Features

- **Property Management**: Track properties with detailed information
- **Property Units**: Manage individual units within properties
- **Lease Agreements**: Handle tenant leases with all relevant details
- **Maintenance Requests**: Track and manage maintenance issues
- **Rent Payments**: Record and track rental payments
- **Subscription Plans**: Define maintenance subscription tiers
- **Customer KYC**: Enhanced customer records with KYC fields

## Installation

```bash
# Get the app
bench get-app https://github.com/xy-kashif/clearent-v1.git

# Install the app
bench install-app clearent

# Run migrations
bench migrate

# Restart bench
bench restart
```

## Requirements

- ERPNext v15+
- Frappe Framework v15+
- Python 3.10+

## DocTypes Included

- Property
- Property Unit
- Lease Agreement
- Maintenance Request
- Rent Payment
- Subscription Plan

## Customer Enhancements

The app includes migration patches that add KYC fields to the Customer DocType:
- Aadhar Number
- PAN Number
- GST Number
- Company PAN
- Director Name
- Director Aadhar Number
- Associated Properties (child table)

## License

MIT License

## Support

For issues or questions, please create an issue in this repository.
