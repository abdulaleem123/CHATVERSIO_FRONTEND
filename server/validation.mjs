export class RequestError extends Error {
  constructor(message, status = 422) { super(message); this.status = status; }
}

function text(input, name, { required = false, max = 200 } = {}) {
  if (input[name] != null && typeof input[name] !== 'string') throw new RequestError(`Invalid ${name}.`);
  const value = (input[name] || '').trim();
  if ((required && !value) || value.length > max) throw new RequestError(`Please check ${name}.`);
  return value;
}
function localParts(date, timezone) {
  return Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone, year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(date).map(part => [part.type, part.value]));
}
export function validate(kind, input, now = new Date()) {
  if (!input || Array.isArray(input) || typeof input !== 'object') throw new RequestError('Expected a JSON object.', 400);
  if (text(input, 'companyWebsite', { max: 500 })) throw new RequestError('Please leave the extra field empty.');
  const name = text(input, 'name', { required: true, max: 120 });
  const email = text(input, 'email', { required: true, max: 254 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new RequestError('Please enter a valid email address.');
  const timezone = text(input, 'timezone', { max: 100 }) || 'UTC';
  try { new Intl.DateTimeFormat('en', { timeZone: timezone }); } catch { throw new RequestError('Invalid time zone.'); }
  const value = { name, email, timezone };
  if (kind === 'enquiry') {
    value.message = text(input, 'message', { required: true, max: 6000 });
    for (const field of ['business', 'phone', 'website', 'solution']) value[field] = text(input, field, { max: field === 'website' ? 1000 : 200 });
    if (value.website) {
      try {
        const url = new URL(/^[a-z][a-z\d+.-]*:/i.test(value.website) ? value.website : `https://${value.website}`);
        if (!['http:', 'https:'].includes(url.protocol) || !url.hostname.includes('.')) throw new Error();
        value.website = url.href;
      } catch { throw new RequestError('Please check the website address.'); }
    }
  } else {
    value.date = text(input, 'date', { required: true, max: 10 });
    value.time = text(input, 'time', { required: true, max: 5 });
    value.platform = text(input, 'platform', { required: true, max: 30 });
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value.date) || !/^([01]\d|2[0-3]):[0-5]\d$/.test(value.time)) throw new RequestError('Please choose a valid date and time.');
    const date = new Date(`${value.date}T00:00:00Z`);
    if (!Number.isFinite(date.valueOf()) || date.toISOString().slice(0, 10) !== value.date) throw new RequestError('Please choose a valid date.');
    const parts = localParts(now, timezone);
    const today = `${parts.year}-${parts.month}-${parts.day}`;
    if (value.date < today || (value.date === today && value.time <= `${parts.hour}:${parts.minute}`)) throw new RequestError('Please choose a future date and time.');
    if (+value.date.slice(0, 4) > +parts.year + 2) throw new RequestError('Please choose a date within the next two years.');
    if (!['Google Meet', 'Zoom'].includes(value.platform)) throw new RequestError('Please choose Google Meet or Zoom.');
  }
  return value;
}
