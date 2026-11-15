# Form API contract

The contact and schedule forms are the same forms used on the original Chatversio website. They post JSON with exactly the same fields, so an existing backend can be reused unchanged. A form succeeds on any HTTP 2xx response; on failure it shows `error` from the JSON body (or the original fallback message). Retries reuse an `X-Idempotency-Key` header, which an existing backend can ignore.

## Contact form

`POST /api/contact`

```json
{
  "name": "Example Customer",
  "email": "customer@example.com",
  "phone": "",
  "business": "Example Company",
  "topic": "voice-agent",
  "companyWebsite": "example.com",
  "message": "We want to handle after-hours enquiries.",
  "hp": ""
}
```

`hp` is the hidden honeypot (must stay empty). `companyWebsite` is the visitor's real website. `topic` is one of `voice-agent`, `lead-follow-up`, `chatbot-crm`, `custom-ai`, `not-sure` or empty. Required: name, valid email, message.

## Schedule form

`POST /api/schedule`

```json
{
  "name": "Example Customer",
  "email": "customer@example.com",
  "date": "2026-12-01",
  "time": "14:30",
  "platform": "google-meet"
}
```

`platform` is `google-meet` or `zoom`. The form blocks a repeat booking in the same browser (`has_scheduled` in localStorage); one booking per email is enforced by your backend, as before, and a 409 response shows "That time slot is already taken."

The bundled reference server (`/api/contact`, `/api/schedule`; the older `/api/enquiries` and `/api/booking-requests` still work) only saves the submission to `data/`. It does not create Zoom/Google Meet events, check clashes or send email. Your production backend does that, exactly as the original site does.

## Failures and retries

Use a non-2xx code and JSON such as `{"ok":false,"error":"Please enter a valid email address."}`. The frontend displays error text safely with `textContent`. Reference statuses: 400 malformed JSON/key; 403 origin; 409 key reused for a different payload; 413 size; 415 content type; 422 field validation; 429 rate limit; 500 storage failure.

Persist before success. An identical key and payload returns the same ID; a changed payload needs a new key. Do not treat a failed email notification as a new lead if the original request was already saved. The included outbox provides at-least-once delivery; deduplicate downstream on record ID.

## Configuration and analytics

Edit `dist/site-config.js` to change endpoints. If your existing API has a different payload/response shape, adapt `dist/integration.js` in the `send()` function and preserve validation, timeouts and retry handling. If your backend requires a CSRF token, add it there using your existing server-generated token mechanism.

After accepted submission, the document emits `chatversio:submitted` with `{kind, id}`. It intentionally excludes names, emails and message content. Your team can subscribe using `document.addEventListener('chatversio:submitted', handler)`.
