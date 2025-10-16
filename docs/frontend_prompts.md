# Frontend Prompts & UX Script (Leads Storefront)

Purpose: Provide prompts and microcopy for the frontend so US solar installers can buy targeted leads. Flow: search a city/neighborhood → choose lead count → pay with Stripe → receive leads.

## Global UX & Brand
- Tone: confident, helpful, concise; plain English.
- Accessibility: WCAG 2.1 AA; contrast ≥ 4.5:1.
- Primary color #3B82F6. Avoid solid black backgrounds.
- One clear CTA per step; verb-led buttons.

## System Prompt (for dynamic UI copy)
```
You write production UI copy for a B2B app where US solar installers purchase high‑quality leads.
Constraints: concise, professional, trustworthy; primary #3B82F6; no solid black; high contrast; plain English; one clear CTA per step; describe deliverables (e.g., “10 verified property leads”); give fixable guidance on errors. Return only UI strings.
```

## Flow & Prompts

### 1) Landing / Search
- Fields: location (US city/neighborhood), leadCount (default 10)
- Placeholder: Carmel Valley, San Diego
- Primary CTA: “Search leads”
- Headline prompt: 4–6 word headline inviting B2B solar installers to find leads.
- Subheading prompt: one sentence (≤120 chars) explaining search and buy verified leads.
- Invalid location error: “We couldn’t find that US location. Try a city or neighborhood (e.g., ‘Carmel Valley, San Diego’).”

### 2) Results / Lead Quantity
- Options: 10, 25, 50, 100 (default 10)
- Under-selector text: “Leads are property-level, analyzed from aerial imagery and public data. You’ll receive CSV + JSON and image links.”
- Price line: “Total: ${totalPrice}”
- CTA: “Continue to checkout”

### 3) Checkout (Stripe)
- Required: company name, business email
- “What you get”:
  - Property addresses with map links
  - Aerial image URLs per property
  - Solar prediction (yes/no/unable) + confidence
  - Basic attributes (beds, baths, price estimate when available)
  - CSV + JSON download
- CTA: “Pay securely”
- Trust: “Payments processed by Stripe. You’ll receive your leads instantly after payment.”

### 4) Success / Delivery
- Headline: “Your leads are ready”
- Body: “Download your files below. We’ve also sent a copy to {email}.”
- Buttons: Download CSV | Download JSON | Open in map
- Support: “Questions? Reply to the receipt email and we’ll help.”

### 5) Empty / Error
- No results: “No leads found for this location. Try a nearby neighborhood or a larger city.”
- Payment failed: “Payment didn’t complete. Please try again or use a different card.”
- Upstream/API: “We’re having trouble fetching data. Please wait a moment and retry.”

## Component Prompts
- Autocomplete: “Generate 5 US city/neighborhood suggestions similar to {query}. Return a JSON array of strings.”
- Email subject: “Your {leadCount} solar leads for {location} are ready”
- Email body:
```
Hi {companyName},

Thanks for your purchase. Your {leadCount} leads for {location} are ready.
- Download CSV: {csvUrl}
- Download JSON: {jsonUrl}

You can open individual properties using the map links in the files.

Best,
The NoSolarMap Team
```

## API (frontend usage)
POST /api/v1/leads
```
{
  "location": "Carmel Valley, San Diego",
  "max_properties": 10,
  "imagery": { "zoom": 19, "size": { "w": 512, "h": 512 } },
  "vision": { "model": "gpt-4o-mini", "confidence_threshold": 0.6 }
}
```

## Pricing Copy (placeholders)
- Unit price: ${unitPrice}  ·  Taxes/fees: ${fees}  ·  Total: ${totalPrice}
- Disclaimer: “Pricing may vary by location and demand. Taxes and fees shown at checkout.”

## Design Checklist
- [ ] Primary #3B82F6, no solid black backgrounds
- [ ] One clear CTA per step
- [ ] Helper + error text on inputs
- [ ] Keyboard focus states
- [ ] High-contrast text
- [ ] Skeleton loaders
- [ ] Stripe Elements AA contrast
- [ ] Reuse this copy across web & emails

## DRY Variables
`{location}` `{leadCount}` `{unitPrice}` `{totalPrice}` `{csvUrl}` `{jsonUrl}` `{companyName}` `{email}`

## Notes
- Start with 10 leads default; expose 10/25/50/100.
- Prefer thumbnails without pins.
- If vision returns “unable”, include the record and mark it in CSV/JSON.
