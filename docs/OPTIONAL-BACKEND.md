# Optional backend for real enquiry delivery (NOT implemented)

The delivered site is static and has **no** submission backend. This note describes what would be needed to add one safely.
Nothing here has been built, deployed or tested, and the website must keep saying “nothing has been sent” until a backend is
actually connected, tested end to end and approved by the company.

## Why it is not included

* No authorised email service, endpoint or credentials were supplied. Secrets must never be placed in front-end code or in this ZIP.
* The original site's form posted to `sendMail.php` on the original server. That endpoint belongs to the company and was deliberately **not** called or reproduced.

## Minimum design for a safe integration

1. **Endpoint** — a small server-side function (for example a serverless function or an existing company mail relay) that accepts `POST /api/enquiries` with JSON:

   ```json
   {
     "contact": { "name": "", "designation": "", "company": "", "email": "", "phone": "", "address": "", "destination": "", "requirements": "", "message": "" },
     "items": [ { "id": "freshwater-platy-005", "type": "photo", "label": "Platy · photo 005", "source": "…", "qty": 200, "supply": "", "note": "" } ],
     "client": { "page": "enquiry.html", "locale": "en" }
   }
   ```
2. **Server-side validation** — re-validate everything (required fields, email syntax, quantity integers 1–99,999, field lengths, item count limit). Never trust the browser.
3. **Delivery** — send through an authorised email provider (SMTP / transactional email API) from a company-owned sender address, to `sales@sanyoaqm.com.sg` with the plain-text format already produced by `src/js/enquiry.js` (`buildText`). Keep API keys in the host's secret store.
4. **Abuse protection** — rate limiting, a honeypot field or a CAPTCHA, request-size limits, and strict CORS (only the deployed origin).
5. **Receipt** — return the provider's real message id (or a server-generated id) only if the provider accepted the message; show a reference to the visitor **only** then. On any error show a failure state and keep the user's data so they can retry or use the email draft.
6. **Privacy** — tell visitors what is stored and for how long; do not log full payloads; add the retention policy the company requires.
7. **Front end change** — add an endpoint setting to `src/js/enquiry.js`, call it from the *Open email draft* area as an additional “Send to Sanyo” button, and keep the mailto/export fallback. Update `tools/verify_content.py` so the “no ‘sent’ wording” checks distinguish the real-send state.
8. **Test safely** — use a staging mailbox, send a clearly marked test message, confirm receipt, then confirm the failure path (provider down) shows an honest error.

## Out of scope unless requested

Payments, live inventory or pricing, ERP integration, customer login and an admin CMS are separate projects. They are not stubbed here, because fake versions would mislead visitors.
