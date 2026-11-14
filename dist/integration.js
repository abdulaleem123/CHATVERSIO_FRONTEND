/* Connect the approved UI to your server; visual interactions stay in studio.js. */
(() => {
  'use strict';
  const config = window.CHATVERSIO_CONFIG || {};
  const one = selector => document.querySelector(selector);
  const states = new WeakMap();
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';

  function stateFor(form) {
    if (!states.has(form)) states.set(form, { key: crypto.randomUUID(), pending: false, sent: false });
    return states.get(form);
  }
  function payload(form) {
    const values = Object.fromEntries(new FormData(form));
    // The generated review textarea has no name and is not sent twice.
    values.timezone = timeZone;
    return values;
  }
  async function send(form, button, status, endpoint, kind) {
    if (!form.reportValidity()) return;
    const state = stateFor(form);
    if (state.pending || state.sent) return;
    const values = payload(form);
    const fields = Array.from(form.querySelectorAll('input, select, textarea'));
    const disabled = fields.map(field => field.disabled);
    fields.forEach(field => { field.disabled = true; });
    state.pending = true;
    button.disabled = true;
    form.setAttribute('aria-busy', 'true');
    status.textContent = 'Sending…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.requestTimeoutMs || 15000);
    try {
      const target = new URL(endpoint, location.origin);
      if (!['http:', 'https:'].includes(target.protocol)) throw new Error('Invalid form endpoint.');
      const response = await fetch(target, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Idempotency-Key': state.key },
        credentials: 'same-origin',
        body: JSON.stringify(values),
        signal: controller.signal,
      });
      const result = await response.json().catch(() => null);
      if (!response.ok || !result?.ok || !result.id) {
        throw new Error(result?.error || 'Your request was not accepted. Please try again.');
      }
      state.sent = true;
      status.textContent = kind === 'booking'
        ? `Request received. Your meeting is not booked yet; our team will confirm the time. Reference: ${result.id}`
        : `Enquiry received. Our team will review your brief. Reference: ${result.id}`;
      // Analytics may subscribe to this event; no personal form values are exposed.
      document.dispatchEvent(new CustomEvent('chatversio:submitted', { detail: { kind, id: result.id } }));
    } catch (error) {
      status.textContent = error.name === 'AbortError'
        ? 'The request timed out. Please retry; the same request will not be saved twice.'
        : error.message === 'Failed to fetch'
          ? 'We could not reach the server. Please check your connection and try again.'
          : error.message;
    } finally {
      clearTimeout(timeout);
      fields.forEach((field, index) => { field.disabled = disabled[index]; });
      state.pending = false;
      button.disabled = state.sent;
      form.removeAttribute('aria-busy');
    }
  }
  function resetOnEdit(form, button, status) {
    form.addEventListener('input', event => {
      if (event.target.readOnly) return;
      const current = stateFor(form);
      if (current.pending) return;
      states.set(form, { key: crypto.randomUUID(), pending: false, sent: false });
      button.disabled = false;
      status.textContent = '';
    });
  }
  const brief = one('#brief-form');
  if (brief) {
    const button = one('#send-enquiry');
    const status = one('#enquiry-status');
    button.addEventListener('click', () => send(brief, button, status, config.enquiryEndpoint || '/api/enquiries', 'enquiry'));
    resetOnEdit(brief, button, status);
  }
  const booking = one('#booking-form');
  if (booking) {
    const button = one('#send-booking');
    const status = one('#booking-status');
    const preview = one('.booking-preview');
    const provider = config.calendarUrl?.trim();
    let providerURL;
    try {
      if (provider) {
        providerURL = new URL(provider, location.origin);
        if (!['http:', 'https:'].includes(providerURL.protocol)) providerURL = null;
        // Prevent looping back to this page when replacing the original website.
        if (providerURL?.origin === location.origin && providerURL.pathname.replace(/\/$/, '') === location.pathname.replace(/\/$/, '')) providerURL = null;
      }
    } catch { /* Use the request form if the provider address is invalid. */ }
    document.querySelectorAll('[data-calendar-link]').forEach(link => {
      link.href = providerURL ? providerURL.href : '#booking-form';
      link.firstChild.textContent = providerURL ? 'Choose a live time ' : 'Request a time ';
      if (!providerURL) link.addEventListener('click', () => { preview.open = true; });
    });
    booking.addEventListener('submit', () => { button.hidden = false; });
    button.addEventListener('click', () => send(booking, button, status, config.bookingEndpoint || '/api/booking-requests', 'booking'));
    resetOnEdit(booking, button, status);
    const timezoneLabel = one('#booking-timezone');
    timezoneLabel.textContent = `Times are in ${timeZone}. Requests are confirmed by our team.`;
    if (location.hash === '#booking-form') preview.open = true;
  }
})();
