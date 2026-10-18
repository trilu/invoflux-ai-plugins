---
name: month-end-close
description: Use when the user asks to close a month, check whether a month is complete, or prepare a month's documents for their accountant in Invoflux.
---

# Month-end close with Invoflux

Help the user check that a month is complete in Invoflux. Do only the steps the user asks for; ask before any step that changes data.

1. Ask which company and which month, unless the user already said. Use `companies_list` if they have more than one company.
2. Check that sources are up to date with `sync_get_status`. If a connection needs attention, tell the user what the status says. Start a sync with `sync_scan_now` only if the user asks.
3. Find bank payments with no invoice: `invoices_get_missing` for the month. List them by supplier, date and amount, with the currency.
4. Find transactions still unmatched: `transactions_get_unmatched`. If the user wants help matching, show `reconciliation_get_suggestions` first. Link a payment with `transactions_link_invoice` or run `reconciliation_run_agent` only after the user agrees.
5. If the user wants a file for their accountant, create it with `exports_create` (CSV, XML or the original files) and give them the link. The link expires after 10 minutes.

Report what is complete and what is still open. Never say a month is closed when documents or matches are missing.
