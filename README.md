# Invoflux AI plugins

The Invoflux connector and skills for AI assistants. The connector itself works with any MCP client by URL; this repo carries the packaging an assistant needs on top (today: the Claude Code plugin). Invoflux collects a company's invoices from email, e-Factura (ANAF SPV) and uploads, files them, and matches them with bank transactions.

## What you get

- **The Invoflux connector** (`https://mcp.invoflux.com/mcp`): read invoices, transactions, suppliers, spending and what you owe; with your permission, link payments, record cash payments, tag, ignore or move invoices, send documents and build period exports. You choose read only or read and act when you connect.
- **Skills:**
  - `month-end-close`: check that a month is complete.
  - `find-missing-invoices`: payments with no invoice, by supplier.
  - `send-receipts-to-invoflux`: the right way to send a document from the chat.
  - `accountant-monday-status`: a weekly status across an accountant's clients.

## Install

In Claude Code:

```
/plugin marketplace add trilu/invoflux-ai-plugins
/plugin install invoflux@invoflux
```

The first tool call opens the Invoflux sign-in and consent screen.

## Links

- Setup and tool list: https://invoflux.com/en/developers
- Privacy policy: https://invoflux.com/en/privacy
- Terms: https://invoflux.com/en/terms
- Support: hello@invoflux.com
