# TODO

## API Facade — Hide ERPNext from Frontend

Currently the frontend hits both ERPNext and rentclear endpoints:

```
/api/resource/Customer              ← ERPNext (contact info)
/api/resource/Rentclear Customer     ← rentclear (KYC data)
```

The frontend shouldn't know ERPNext exists under the hood. Wrap everything behind `rentclear.api.customers.*` so all CRUD + search goes through one surface.

### New endpoints needed

| Method | What it does |
|--------|-------------|
| `rentclear.api.customers.create` | Creates Customer + Rentclear Customer in one call (already have `onboard_with_kyc`) |
| `rentclear.api.customers.get` | Returns a merged/flattened record with all fields from both doctypes |
| `rentclear.api.customers.list` | List/search with filters across both doctypes (already have `search_tenants`) |
| `rentclear.api.customers.update` | Updates fields on either doctype transparently |
| `rentclear.api.customers.delete` | Cascading delete of both records |

### Why

- Single API surface for frontend
- Can swap ERPNext for another backend without frontend changes
- No 2-step lookups, no "Field not permitted in query" errors
- Cleaner Swagger docs

### When

After current features stabilize. Not blocking.
