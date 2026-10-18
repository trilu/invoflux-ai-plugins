---
name: send-receipts-to-invoflux
description: Use when the user wants to send an invoice, receipt or other document to Invoflux from the conversation.
---

# Send documents to Invoflux

Pick the path that fits where the document is. Ask which company it belongs to if the user has more than one.

- **A file in the conversation, up to 2 MB:** send it with `invoices_upload_content` (base64 content, one document per call).
- **A file at a public https link:** `invoices_upload_from_url` with that link.
- **A larger file, or several:** `invoices_create_upload_link` gives a link the user opens in a browser, or uses with curl from a shell.
- **A document that came by email:** `companies_get_forwarding_address` gives the company's Invoflux address; the user forwards the email there.

After an upload, check the result with `invoices_get_upload_status` and tell the user where the document was filed. If Invoflux says the document was sent before or was deleted earlier, tell the user what it says; do not send it again.
