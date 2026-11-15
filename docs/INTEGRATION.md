# Integration guide

## Preserve the approved appearance

Use the provided CSS, fonts, media paths, class names and DOM structure together. The header and footer use the transparent `chatversio-logo-on-dark.png` (light wordmark for the navy background); the About page uses `chatversio-logo-transparent.png`. The old `chatversio-brand-original.jpeg` and `chatversio-footer-logo.png`. Do not approximate either with text or an icon. The footer and its stylesheet are unchanged from approved v7.

The page generator writes all HTML under `dist/`; it does not wipe media or CSS. Edit content in `content.py`, templates in `build.py`, interface behavior in `dist/studio.js`, submission behavior in `dist/integration.js`, and the live hero in `scene/hero.js`.

## Direct integration into the current website

1. Back up the current frontend and stage this handoff on a development domain.
2. Copy **the contents of `dist/`**, including `fonts/`, `media/`, nested service folders and all JS/CSS files, into your frontend's web root or framework `public/` directory. Do not put the source folder, server secrets or request data in a public directory.
3. Route the 23 page URLs to their corresponding `index.html`. Serve real 404s for missing routes. Keep existing backend endpoints, existing privacy policy and terms routes, and any account/dashboard routes.
4. Load `/site-config.js`, `/studio.js` and `/integration.js` once, in that order, using `defer`. The homepage also loads `/hero-3d.js` as a module. Retain the page's inline JSON scenario data and footer CSS link.
5. Your existing `POST /api/contact` and `POST /api/schedule` routes work as they are (same payloads as the original site; see `docs/API.md`), or change the two endpoint URLs in `site-config.js`. Same-origin routes are simplest.
6. Nothing else to configure for booking: the schedule form posts to your backend, which creates the meeting as before.
7. Set production metadata in `build.py` if your domain differs. Its Open Graph image now points to `https://www.chatversio-ai.com/media/home-preview.jpg`.
8. Run `npm run check`, your own backend tests, and the staging checks in `QA.md`, then deploy through your normal process.

The main routes are `/`, `/services/`, `/about/`, `/contact/`, `/schedule-event/`, plus 18 routes under `/services/<slug>/`. Their exact list is in `ROUTES.json`. Existing legacy service URLs should redirect to their matching page; the package does not guess your current server's rewrite rules.

## CSS and framework boundaries

`style.css` includes global resets and typography. Loading it into an unrelated existing layout may affect that layout. Replace the marketing-page layout with this design, or scope the stylesheet during a deliberate component port. An iframe is useful for review but is not the intended final website integration.

Partial HTML files are generated from the same functions as the full pages. Do not render the same partial twice: several interactive sections use unique IDs. `hero.html` includes the showreel dialog and hero module script. `footer.html` includes the footer CSS link.

In JSX, translate `class` to `className`, inline style strings to objects, and SVG attribute spelling as required by your framework. Do not paste the entire document into a component or assume `dangerouslySetInnerHTML` executes scripts. Mount the original page as a full document first; port one component at a time if your team requires React lifecycle behavior.

## Reference Node backend

`npm start` serves `dist/` and the two API routes. It saves validated JSON records privately before returning success. JSON files contain lead details; restrict filesystem access and set your own retention/backups. The server never exposes `data/`, `.env`, or source files.

Copy `.env.example` to `.env` and adjust the origin, port and data path. Behind HTTPS, set `ALLOWED_ORIGIN=https://www.chatversio-ai.com` (or your exact chosen origin). The proxy should redirect any alternate origin consistently. The optional rate limiter keys off the socket address, not untrusted forwarded headers: behind a shared proxy, use your existing edge rate limiter and adapt this reference limiter before launch.

For CRM delivery, configure `WEBHOOK_URL` and optional `WEBHOOK_BEARER_TOKEN` **on the server**, then run `npm run deliver`. The command sends pending records to your receiver and marks them delivered only on a 2xx response. Run it with your own scheduler if desired. Receiver deduplication by `id` is required; a process may stop after the remote receiver accepts a record but before local delivery metadata is saved. Failed records remain pending. The command does not create calendar meetings by itself.

Use a database transaction and distributed rate limiter if you deploy multiple processes, containers or serverless instances. A local JSON directory is not durable storage on an ephemeral host. Integrate authentication/CSRF protection if your existing backend requires it; the public form contract itself does not need a browser-held secret.

## 3D and media

The prebuilt bundle includes Three.js; no CDN or paid 3D player is required. All four `.glb` files, portraits, 40 turntable images, eight voice clips, the 18-second film, subtitles, fallback loop and font files are local.

Live rendering uses WebGL2 when available. If WebGL is unavailable, save-data is enabled, or model loading fails, the supplied illustrated/Blender-rendered fallback stays usable. Motion respects reduced-motion preferences and stops while the page is hidden. Audio starts only after interaction.

Edit models through `art/render.py` / `art/export_stage.py`. Example optional rebuild:

```sh
blender --background --python art/export_stage.py
npm run build
```

Blender is needed only to recreate models/renders; it is not a runtime dependency. Scripts create geometry procedurally, so no `.blend` file is required. `art/prepare.py` uses Pillow. Optional film rebuilding needs Pillow, NumPy, SciPy and FFmpeg; optional voice regeneration needs the indicated sherpa-onnx/Kokoro model files, which are not bundled. All finished media is already included, so those optional tools are unnecessary for integration.

Keep the included font, icon and dependency license files. `ASSETS.json` contains checksums for every shipped frontend file.
