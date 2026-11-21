// Single source of truth for how long a booked discovery call lasts.
// Used by the /schedule-event page copy AND the /api/schedule route
// (Zoom meeting length, Google Calendar event length, conflict check,
// confirmation email), so what we promise is what we actually book.
// To change the call length, change this one number.
export const MEETING_DURATION_MINUTES = 30

export const MEETING_DURATION_MS = MEETING_DURATION_MINUTES * 60 * 1000
