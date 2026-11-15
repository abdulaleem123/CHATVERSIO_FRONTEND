# Handoff verification — 14 November 2026

## Automated checks

`npm run build` regenerates all 23 pages, 15 section partials and the bundled Three.js scene. `npm run check` verifies page structure, unique IDs, local anchors, 951 page-to-route/asset references, 40 turntable frames, four GLB files and eight voice clips. `npm test` verifies the request API and 3D model parsing.

API coverage includes durable saving before success, concurrent duplicate retries, conflicting payloads, invalid email, honeypot input, body limit, forbidden origin, wrong method, rate limiting, future local booking time, invalid date/timezone, byte-range video delivery, private-file protection and storage-failure responses.

No real customers, messages, CRM updates, emails or calendar events were used in testing. Synthetic local request records are excluded from the archive.

## Observed in the browser

| Area | Result |
| --- | --- |
| Chat / Sales / Voice / 360° selection | Correct selected state and visible content |
| Motion control | On/off state changes and stored preference |
| Showreel | Modal open/close, 18-second video loaded without media error, sound switch |
| Interactive workflow | All four industries, callback outcome, scene buttons and sample playback |
| Integration panel | All 12 tool selectors update the panel |
| Process / FAQ | Disclosure works; process keeps one item open |
| Service directory | Channels 4, Growth 3, Operations 5, Support 3, All 15 |
| Contact | Same fields as the original site, direct submission and success state |
| Booking | CTA opens form, date/time/preferences, actual request saved, pending-confirmation wording |
| Mobile navigation | Opens/closes and closes with Escape |
| Mobile width | No page-level horizontal overflow at the 390px test frame (375px content width) |
| Headset fallback | Desktop next-angle button and mobile keyboard rotation load distinct frame assets |
| Desktop width | No page-level horizontal overflow at 1348px content width |

## Verification limits

The browser reported WebGL disabled by its execution environment. Actual GPU rendering could not be visually verified in this handoff run. All four real GLB models parse successfully, the scene bundle builds, and the intended fallback renders and rotates correctly. Repeat the live-WebGL check on a GPU-enabled browser.

Live CRM delivery, email notifications, calendar conflict checking and invitations require the team's own backend/provider accounts. Their external delivery was not exercised. `npm run deliver` is an optional outbox connector, not a preconfigured CRM.

The original website's privacy/terms and social links remain external destinations; this package does not replace those legal pages. The original marketing demos are sample conversations and integration illustrations, not real agent services.

## Staging acceptance checks for your developer

1. Confirm all routes and existing legal pages on the final domain; load a deep service URL directly and refresh it.
2. Check the final CSS/fonts against the approved design at phone, tablet and desktop sizes.
3. On a GPU-enabled device, confirm `.cast-stage` gets `data-webgl="ready"`, select each agent, rotate the headset, and check the console for scene errors.
4. On a low-power device or with WebGL unavailable, confirm the fallback remains usable. Check reduced-motion mode and keyboard navigation.
5. Test both forms against your staging backend, including timeout, validation and retry. Confirm the request arrives in your actual CRM/outbox and is not duplicated.
6. Configure the real calendar URL or connect your booking backend; verify the timezone, conflicts and genuine invitation email. Keep the request wording until that is implemented.
7. Test video/audio on your supported Safari/iOS and Android devices; this run used Chromium, not a full browser/device matrix.
8. Confirm analytics excludes personal message contents, configure HTTPS and the exact allowed origin, and deploy your database/retention/rate-limit policy with your existing infrastructure.
