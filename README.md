# Clearent — Property Rental Management

ERPNext app for property rental management. Built for Frappe v16.

## Core Principle: Bidirectional User ↔ Customer

**Every User is a Customer. Every Customer is a User.** This is enforced by design, not convention.

- `signup` API creates User + Customer + Contact in one atomic step
- `onboard_with_kyc` API auto-creates a User if one doesn't exist for that email
- No user exists without a corresponding Customer record
- No customer exists without login access

This means a tenant can log in and see their dashboard. A property owner can log in and manage their properties. One person can be both — just toggle `is_tenant` and `is_property_owner` flags.

## Installation

```bash
bench get-app https://github.com/xcspl/clearent-v1.git --branch master
bench --site your-site install-app rentclear
```

## Quick Start: Create a User/Customer

```bash
curl -X POST https://your-site/api/method/rentclear.api.customers.signup \
  -H "Content-Type: application/json" \
  -d '{"email":"tenant@email.com","full_name":"John Doe","mobile_no":"9999999999"}'
```

User verifies their email by logging in via OTP. That's it.

## DocTypes

| Doctype | Purpose |
|---------|---------|
| Property | Buildings and properties |
| Property Unit | Individual units within properties |
| Lease Agreement | Tenant leases |
| Maintenance Request | Repair and maintenance tracking |
| Rent Payment | Payment records |
| Rent Subscription Plan | Maintenance subscription tiers |
| Rentclear Customer | KYC data and role flags (is_tenant, is_property_owner) |
| Clearent Member | Property managers, vendors, representatives |
| Property Manager Profile | Extended manager profiles |

## API

All endpoints work with both `rentclear.api.*` and `clearent.api.*` namespaces.
Full spec: `GET /api/method/rentclear.api.openapi.get_spec`

| Endpoint | Purpose |
|----------|---------|
| `customers.signup` | Create User + Customer in one step |
| `customers.onboard_with_kyc` | Full KYC onboarding |
| `dashboard.get_dashboard_data` | Owner/property dashboard stats |
| `tenants.search_tenants` | Search tenants by email/phone/name |
| `tenants.get_property_tenants` | List tenants for a property |
| `tenants.create_tenant_with_agreement` | Create tenant + lease in one call |
| `tenants.send_reminder` | Send rent reminder |
| `tenants.add_note` | Add note to tenant record |
| `properties.get_units_summary` | Unit counts by status |
| `documents.update_status` | Update KYC document verification |

## OTP Login

The `frappe_otp_login` app adds passwordless login. OTP verification = email verification.

```bash
# 1. Sign up
curl -X POST /api/method/rentclear.api.customers.signup \
  -d '{"email":"...","full_name":"..."}'

# 2. Send OTP
curl -X POST /api/method/frappe_otp_login.api.send_otp \
  -d '{"identifier":"...","channel":"Email"}'

# 3. Verify OTP → logged in + token returned
curl -X POST /api/method/frappe_otp_login.api.verify_otp \
  -d '{"identifier":"...","otp":"123456"}'
```

## License

MIT
