/* Contact and schedule forms: submit exactly the fields the original website sent, as JSON.
   Visual interactions stay in studio.js. */
(() => {
  'use strict';
  const config = window.CHATVERSIO_CONFIG || {};
  const one = selector => document.querySelector(selector);
  const SUPPORT = 'saif@chatversio-ai.com or esha@chatversio-ai.com';

  async function post(endpoint, values, key) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.requestTimeoutMs || 15000);
    try {
      const response = await fetch(new URL(endpoint, location.origin), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Idempotency-Key': key },
        credentials: 'same-origin',
        body: JSON.stringify(values),
        signal: controller.signal,
      });
      const result = await response.json().catch(() => ({}));
      return { ok: response.ok, status: response.status, result };
    } finally { clearTimeout(timeout); }
  }
  function wire(form, { endpoint, idle, busy, failure, network, done }) {
    const button = form.querySelector('button[type=submit]');
    const error = form.querySelector('.form-error');
    const idleHTML = button.innerHTML;
    // A retry of the same submission reuses one key, so a lost response cannot create a duplicate.
    let key = crypto.randomUUID();
    form.addEventListener('input', () => { key = crypto.randomUUID(); });
    form.addEventListener('submit', async event => {
      event.preventDefault();
      error.hidden = true; error.textContent = '';
      button.disabled = true;
      button.innerHTML = '<span class="spinner" aria-hidden="true"></span>' + busy;
      const values = Object.fromEntries(new FormData(form));
      try {
        const { ok, status, result } = await post(endpoint, values, key);
        if (ok) { done(values); return; }
        error.textContent = result.error || failure(status);
        error.hidden = false;
      } catch {
        error.textContent = network;
        error.hidden = false;
      } finally {
        button.disabled = false;
        button.innerHTML = idleHTML;
      }
    });
  }

  const contact = one('#brief-form');
  if (contact) {
    const success = one('#contact-success');
    wire(contact, {
      endpoint: config.contactEndpoint || '/api/contact',
      busy: 'Sending…',
      failure: () => `Your message was not sent. Please try again, or email us at ${SUPPORT}.`,
      network: 'Network problem - your message was not sent. Please check your connection and try again.',
      done: () => {
        contact.hidden = true; success.hidden = false;
        document.dispatchEvent(new CustomEvent('chatversio:submitted', { detail: { kind: 'contact' } }));
      },
    });
    one('#contact-again').addEventListener('click', () => {
      contact.reset(); success.hidden = true; contact.hidden = false;
    });
  }

  const booking = one('#booking-form');
  if (booking) {
    const success = one('#booking-success');
    const already = one('#booking-already');
    const showAlready = () => { booking.hidden = true; already.hidden = false; };
    try { if (localStorage.getItem('has_scheduled')) showAlready(); } catch { /* Storage is optional. */ }
    wire(booking, {
      endpoint: config.scheduleEndpoint || '/api/schedule',
      busy: 'Scheduling…',
      failure: status => status === 409
        ? 'That time slot is already taken. Please choose a different time.'
        : `We could not complete your booking. Please try again, or email ${SUPPORT} and we will arrange a time.`,
      network: 'Network problem - your booking was not made. Please check your connection and try again.',
      done: values => {
        try { localStorage.setItem('has_scheduled', 'true'); } catch { /* Booking still succeeded. */ }
        one('#booking-mail').href = 'mailto:' + values.email;
        booking.hidden = true; success.hidden = false;
        document.dispatchEvent(new CustomEvent('chatversio:submitted', { detail: { kind: 'schedule', platform: values.platform } }));
      },
    });
  }
})();
