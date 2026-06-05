# Product vs Service Form Split — Implementation Plan

## Architecture

3 templates + 1 new route:

| Route | Template | Purpose |
|---|---|---|
| `GET /` | `landing.html` | Selection screen — two cards: Products / Services |
| `GET /product-form` | `product_form.html` | Current form (renamed) |
| `GET /service-form` | `service_form.html` | New service-specific form |
| `POST /generate` | — | Same backend endpoint, handles both via `project_type` hidden field |

## Why separate files

`form.html` is already ~3100 lines. Doubling it with show/hide conditional blocks makes it unmaintainable. Separate templates let each form evolve independently. Jinja2 `{% include %}` handles shared sections.

## Shared sections (via Jinja2 include)

These are identical between both forms:
- Project Overview (title, product/service name)
- Proposed Site Location + Pin Code
- Target Customer Segment
- Sizing Mode — Budget-Driven sub-section
- Financial Structure (debt/equity split, interest rate, loan tenor)
- Working Capital (receivables, payables — inventory excluded for services)
- Operations (operating days, shifts, hours)
- Market Geography & Exports
- Certifications & Compliance
- Promoters

## What changes per form

### Commercial Assumptions

| Field | Product Form | Service Form |
|---|---|---|
| Pricing | Selling Price per Unit | Rate / Fee (hourly / per project / per session / per bed / per seat) |
| Revenue Model | — | Dropdown: Hourly / Per Project / Retainer / Per Bed / Per Seat / Subscription |
| Mix | Product Mix (base + by-products) | Service Mix |
| Input costs | Raw Material Consumption Norms | Direct Cost Basis (labor-centric, text) |
| Input pricing | Raw Material Pricing Basis | Consumables (optional, lightweight) |
| Utilisation | Production Ramp-Up Plan | Occupancy / Utilisation Rate (%) + Business Ramp-Up Plan |
| Utilities | Utility Tariff Basis | Utility Basis (de-emphasised) |
| Inventory | Inventory Days | Hidden / removed |

### Sizing Capacity Units

| Product Form | Service Form |
|---|---|
| Units, kg, MT, Liters, kL, MW, kW, sq ft, sq m, Barrels | Beds, Seats, Hours, Clients/Day, Rooms, Consultations, Students, Sq ft |

### Business Model Dropdown

| Product Form | Service Form |
|---|---|
| Manufacturing, Trading (Wholesale), Trading (Retail) | Professional Services, Engineering Services, Education, Hospitals, Hospitality & Recreation, Government Services, R&D |

## Implementation Steps

1. Create `landing.html` — two large clickable cards (Products / Services), clean design consistent with current form style
2. Add routes in `main.py`:
   - `GET /product-form` → renders `product_form.html`
   - `GET /service-form` → renders `service_form.html`
   - Update `GET /` to render `landing.html`
3. Rename current `form.html` → `product_form.html`, add `<input type="hidden" name="project_type" value="product">`
4. Extract shared sections into Jinja2 partials under `app/templates/partials/`
5. Build `service_form.html` using shared partials + service-specific commercial assumptions
6. Update `POST /generate` backend to handle `project_type` field — route to appropriate validation and prompt logic
7. Update example datasets for the service form (service-type examples)
8. Update `validate_critical_inputs()` in `main.py` — skip raw material / inventory checks for service type
