# Chatversio AI — frontend developer handoff

This is the complete source for the approved blue Chatversio design, including the final original-style footer and supplied logo. It contains 23 ready-to-serve pages, 15 reusable HTML sections, all local media and fonts, four real GLB models, editable Blender scripts, the Three.js scene, and form integration code.

The visual baseline is approved website version 7 (source commit `88629d9f62e97cca44f671003ec496b461127d15`). This export adds enquiry and meeting-request submission to the previously preview-only forms. It does not change the published website.

## Run it immediately

Install Node.js 22 or newer, extract this folder, open a terminal here, and run:

```sh
npm start
```

Open **http://127.0.0.1:3000/**. The compiled frontend is included, and the reference server uses only Node built-ins: no package install or Python is needed just to run it. Use HTTP/HTTPS, not a double-clicked `file://` page, for modules, media, clipboard and form APIs.

Enquiries and meeting requests are genuinely saved in the private `data/` directory. No email, CRM update or calendar invitation is sent until you connect your own system. A meeting request is shown as **pending confirmation**, never falsely booked.

## Rebuild after editing

Python 3.10+ is used for the small page/content generator. JavaScript dependency versions are locked.

```sh
npm ci
npm run build
npm test
npm run check
```

`npm run build:pages` regenerates HTML and component partials without rebuilding the Three.js bundle. Set `PYTHON` if your Python executable has a different name. On Windows the build script uses `py -3` by default.

## Files to give your frontend developer

| Path | What it contains |
| --- | --- |
| `dist/` | Complete deployable frontend: all pages, CSS, scripts and media |
| `build.py` | Named components and page composition; main source of the HTML |
| `content.py` | Service content, scenarios, integrations, FAQs and process steps |
| `components/` | 15 exported HTML partials for adapting sections into your stack |
| `dist/style.css`, `dist/footer.css` | Approved responsive styling and final footer styling |
| `dist/studio.js` | Navigation, audio, demo, filters, accordions, animation controls |
| `dist/integration.js`, `dist/site-config.js` | Actual form submission and public endpoint configuration |
| `scene/hero.js` | Readable Three.js hero source |
| `dist/media/3d/`, `art/` | GLB models, Blender creation/export scripts and media source |
| `server/` | Optional working Node reference API and private request storage |
| `docs/INTEGRATION.md` | How to merge into your existing website |
| `docs/API.md` | Exact request/response contract and calendar setup |
| `docs/COMPONENTS.md` | Component, selector, behavior and dependency map |
| `docs/QA.md` | Verified behavior and checks your team should repeat on staging |

## Choose the integration path

**Existing backend:** copy the contents of `dist/` to your frontend's public output and implement the two API routes in `docs/API.md`, or point `dist/site-config.js` at your existing endpoints. Preserve your existing `/privacy-policy` and `/terms` pages. All internal routes use root-relative URLs.

**Node deployment:** run the bundled server behind your HTTPS proxy, set `.env` from `.env.example`, and put `DATA_DIRECTORY` on a persistent private volume. Connect the outbox to your CRM using `npm run deliver`, or replace storage with your existing database. The reference backend is a single-process implementation; production infrastructure belongs to your team.

**React / Next / Vue:** use the partials and component map as the source of the presentation. These are actual HTML/CSS/JavaScript components, not a React project. The current scripts initialize once per full page load. Preserve normal page navigation for the direct drop-in; a SPA conversion needs framework lifecycle cleanup for listeners, observers and WebGL. Do not repeatedly execute the scripts on route transitions.

## What still needs your accounts

Set your real enquiry endpoint / CRM receiver, optionally your actual calendar booking URL, and your production origin. Keep credentials server-side. The interactive agent workflows are the original illustrative demos; they are not deployed conversational AI agents. Live calling, chat, social-channel automation, CRM and scheduling services use your own existing integrations.

See `docs/INTEGRATION.md` before replacing routes on the live domain.
