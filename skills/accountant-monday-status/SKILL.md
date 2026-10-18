---
name: accountant-monday-status
description: Use when an accountant asks for a status of their clients in Invoflux, such as a weekly review, which clients are behind, or what to chase this week.
---

# Accountant: client status

For accountants connected to Invoflux with access to client companies.

1. List the clients with `accounting_clients_list`.
2. Get what is missing across clients with `accounting_get_missing_across_clients`. If `accounting_month_close_status` is available, use it for the month's per-client status.
3. Sort clients by what needs action: missing documents first, then unmatched transactions, then invoices to review.
4. Show a short table: client, what is missing, how many, and the oldest date.

Do not invite or create clients, and do not email anyone, unless the user asks for that action by name.
