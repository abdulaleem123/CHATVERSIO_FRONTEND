# Form API contract

The contact UI first builds a reviewable brief, then **Send enquiry** posts it. The booking UI reviews preferences, then **Send meeting request** posts them. The form retains values on failure; controls lock during submission; retries reuse an idempotency key. Success requires an HTTP success status plus `{ "ok": true, "id": "…" }` from your server.

## Enquiry

`POST /api/enquiries`

Headers: `Content-Type: application/json`, `X-Idempotency-Key: <UUID>`.

```json
{
  "name": "Example Customer",
  "email": "customer@example.com",
  "business": "Example Company",
  "phone": "",
  "website": "example.com",
  "solution": "voice-assistants",
  "message": "We want to handle after-hours enquiries.",
  "timezone": "Asia/Karachi",
  "companyWebsite": ""
}
```

`companyWebsite` is the empty honeypot field. `website` is the real website field.

Required: name, valid email, message. Optional: business, phone, website, service slug. Validate again on the server. Reference limits: name 120, email 254, message 6000, website 1000, other fields 200 characters; JSON body at most 20,000 bytes.

Successful response: HTTP 201, `{"ok":true,"id":"server-generated-id","status":"received"}`.

## Meeting request

`POST /api/booking-requests`, same headers.

```json
{
  "name": "Example Customer",
  "email": "customer@example.com",
  "date": "2026-12-01",
  "time": "14:30",
  "platform": "Google Meet",
  "timezone": "Asia/Karachi",
  "companyWebsite": ""
}
```

Date/time are the visitor's preferred **local wall-clock time**, paired with an IANA timezone. Do not interpret them as the server's timezone. The reference API validates a future local time and stores the preference; it does not reserve a slot, check clashes, send invites or create Zoom/Meet links. The production calendar backend must resolve daylight-saving ambiguity, check availability atomically and create the real event before claiming a booking.

Successful request response: HTTP 201, `{"ok":true,"id":"server-generated-id","status":"requested"}`.

To use your existing confirmed-booking flow, set `calendarUrl` to the actual external/provider booking URL. The top call-to-action opens that provider; the request form remains an alternative. Provider credentials never go in the frontend.

## Failures and retries

Use a non-2xx code and JSON such as `{"ok":false,"error":"Please enter a valid email address."}`. The frontend displays error text safely with `textContent`. Reference statuses: 400 malformed JSON/key; 403 origin; 409 key reused for a different payload; 413 size; 415 content type; 422 field validation; 429 rate limit; 500 storage failure.

Persist before success. An identical key and payload returns the same ID; a changed payload needs a new key. Do not treat a failed email notification as a new lead if the original request was already saved. The included outbox provides at-least-once delivery; deduplicate downstream on record ID.

## Configuration and analytics

Edit `dist/site-config.js` to change endpoints. If your existing API has a different payload/response shape, adapt `dist/integration.js` in the `send()` function and preserve validation, timeouts and retry handling. If your backend requires a CSRF token, add it there using your existing server-generated token mechanism.

After accepted submission, the document emits `chatversio:submitted` with `{kind, id}`. It intentionally excludes names, emails and message content. Your team can subscribe using `document.addEventListener('chatversio:submitted', handler)`.
