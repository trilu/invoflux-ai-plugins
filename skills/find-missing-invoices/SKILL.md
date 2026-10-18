---
name: find-missing-invoices
description: Use when the user asks which invoices are missing, which payments have no document, or what to ask suppliers for in Invoflux.
---

# Find missing invoices

1. Ask for the company and the period, unless the user already gave them.
2. Call `invoices_get_missing` for that period. Group the result by supplier and show each payment's date and amount with its currency.
3. For a supplier with several missing documents, `suppliers_get` gives the supplier's details the user may need to contact them.
4. If the user has a missing document at hand, offer the ways to send it (see the send-receipts-to-invoflux skill).

Do not contact suppliers yourself. If the user wants a message to a supplier, draft it for them to send.
