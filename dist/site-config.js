/* Public configuration only. Never put API keys or passwords in this file. */
window.CHATVERSIO_CONFIG = Object.freeze({
  enquiryEndpoint: '/api/enquiries',
  bookingEndpoint: '/api/booking-requests',
  // Set to your real Calendly/calendar URL to use instant provider booking.
  // Empty means visitors can submit a preferred time for your team to confirm.
  calendarUrl: '',
  requestTimeoutMs: 15000,
});
