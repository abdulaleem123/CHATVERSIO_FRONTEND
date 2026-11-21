import nodemailer from 'nodemailer'
import { google } from 'googleapis'
import axios from 'axios'
import { MEETING_DURATION_MINUTES, MEETING_DURATION_MS } from './_booking'


// Accept the Vercel names already in use (EMAIL_USER / EMAIL_PASS) or the Gmail-style names.
const MAIL_USER = process.env.EMAIL_USER || process.env.GMAIL_USER
const MAIL_PASS = process.env.EMAIL_PASS || process.env.GMAIL_APP_PASSWORD

const bookedSlots = new Set<string>()

// Every notification goes to NOTIFY_EMAIL (comma-separated list allowed, or GMAIL_USER) plus Esha.
const EXTRA_NOTIFY = 'esha@chatversio-ai.com'
function notifyRecipients(): string {
  const base = (process.env.NOTIFY_EMAIL || MAIL_USER || '').split(',').map(v => v.trim()).filter(Boolean)
  const all = [...base, EXTRA_NOTIFY]
  return [...new Set(all.map(v => v.toLowerCase()))].join(', ')
}

// Escape user input before it is placed inside HTML emails.
function esc(value: unknown): string {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const EMAIL_RE = /^[^\s@<>"']+@[^\s@<>"']+\.[^\s@<>"']+$/

// ── Google OAuth ─────────────────────────────────────────────
function getOAuthClient() {
  const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    'https://developers.google.com/oauthplayground'
  )
  oauth2Client.setCredentials({
    refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
  })
  return oauth2Client
}

// ── Gmail ────────────────────────────────────────────────────
function getMailTransporter() {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: MAIL_USER,
      pass: MAIL_PASS,
    },
  })
}

// ── Zoom access token ─────────────────────────────────────────
async function getZoomAccessToken() {
  const accountId = process.env.ZOOM_ACCOUNT_ID
  const clientId = process.env.ZOOM_CLIENT_ID
  const clientSecret = process.env.ZOOM_CLIENT_SECRET
  const tokenUrl = `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${accountId}`
  const response = await axios.post(tokenUrl, {}, {
    headers: {
      Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
    },
  })
  return response.data.access_token
}

// ── Create Zoom meeting ───────────────────────────────────────
async function createZoomMeeting(data: {
  name: string; email: string; date: string; time: string
}) {
  try {
    const token = await getZoomAccessToken()
    const start_time = new Date(`${data.date}T${data.time}:00`).toISOString()
    const res = await axios.post(
      'https://api.zoom.us/v2/users/me/meetings',
      {
        topic: `Strategy Call with ${data.name}`,
        type: 2,
        start_time,
        duration: MEETING_DURATION_MINUTES,
        timezone: 'Asia/Karachi',
        settings: { join_before_host: false, approval_type: 0 },
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )
    return res.data.join_url as string
  } catch (err: any) {
    console.error('Zoom creation failed:', err.response?.data || err.message)
    return null
  }
}

// ── Check slot availability ───────────────────────────────────
async function isSlotAvailable(date: string, time: string) {
  const auth = getOAuthClient()
  const calendar = google.calendar({ version: 'v3', auth })
  const start = new Date(`${date}T${time}:00`)
  const end = new Date(start.getTime() + MEETING_DURATION_MS)
  const res = await calendar.events.list({
    calendarId: process.env.GOOGLE_CALENDAR_ID || 'primary',
    timeMin: start.toISOString(),
    timeMax: end.toISOString(),
    singleEvents: true,
  })
  return res.data.items?.length === 0
}

// ── Add to Google Calendar ────────────────────────────────────
async function addToCalendar(data: {
  name: string; email: string; date: string; time: string
  platform: string; meetingLink?: string
}) {
  const auth = getOAuthClient()
  const calendar = google.calendar({ version: 'v3', auth })
  const startDateTime = new Date(`${data.date}T${data.time}:00`)
  const endDateTime = new Date(startDateTime.getTime() + MEETING_DURATION_MS)
  const platformLabel = data.platform === 'zoom' ? 'Zoom' : 'Google Meet'

  const event = {
    summary: `Strategy Call - ${data.name}`,
    description: `Client: ${data.name}
Email: ${data.email}
Platform: ${platformLabel}
${data.meetingLink ? `\nJoin Link: ${data.meetingLink}` : ''}`.trim(),
    start: { dateTime: startDateTime.toISOString(), timeZone: 'Asia/Karachi' },
    end: { dateTime: endDateTime.toISOString(), timeZone: 'Asia/Karachi' },
    attendees: [{ email: data.email }],
    conferenceData: data.platform === 'google-meet' ? {
      createRequest: {
        requestId: `meet-${Date.now()}`,
        conferenceSolutionKey: { type: 'hangoutsMeet' },
      },
    } : undefined,
  }

  const response = await calendar.events.insert({
    calendarId: process.env.GOOGLE_CALENDAR_ID || 'primary',
    requestBody: event,
    conferenceDataVersion: data.platform === 'google-meet' ? 1 : 0,
    sendUpdates: 'all',
  })

  // Return full event so caller can extract the Meet link
  return response.data
}

// ── Confirmation email to user ────────────────────────────────
async function sendConfirmationEmail(data: {
  name: string; email: string; date: string; time: string
  platform: string; meetingLink?: string
}) {
  const transporter = getMailTransporter()
  const platformLabel = data.platform === 'zoom' ? 'Zoom' : 'Google Meet'
  const dateObj = new Date(`${data.date}T${data.time}:00`)
  const formattedDate = dateObj.toLocaleDateString('en-PK', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  })
  const formattedTime = dateObj.toLocaleTimeString('en-PK', {
    hour: '2-digit', minute: '2-digit',
  })

  await transporter.sendMail({
    from: `"Chatversio AI" <${MAIL_USER}>`,
    to: data.email,
    subject: `Your Strategy Call is Confirmed - ${formattedDate}`,
    html: `
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 40px 20px; margin: 0;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">

    <div style="background: linear-gradient(135deg, #020408, #0d1825); padding: 40px 40px 32px; text-align: center;">
      <div style="font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Chatversio<span style="color: #63daff;">AI</span>
      </div>
      <div style="color: rgba(255,255,255,0.45); font-size: 0.82rem; margin-top: 6px;">AI Chatbot Agency · Karachi, Pakistan</div>
    </div>

    <div style="background: linear-gradient(135deg, rgba(99,218,255,0.08), rgba(99,218,255,0.03)); border-bottom: 1px solid rgba(99,218,255,0.12); padding: 24px 40px; text-align: center;">
      <div style="display: inline-block; background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.3); border-radius: 100px; padding: 6px 18px; font-size: 0.78rem; font-weight: 700; color: #4ade80; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 12px;">
        ✓ Confirmed
      </div>
      <h1 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #0d1825; letter-spacing: -0.02em;">
        You're Booked, ${esc(data.name.split(' ')[0])}!
      </h1>
    </div>

    <div style="padding: 36px 40px;">
      <p style="color: #64748b; line-height: 1.7; margin: 0 0 28px; font-size: 0.95rem;">
        Your strategy call with the Chatversio AI team is confirmed. Here are your meeting details:
      </p>

      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 28px;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0;">
              <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">📅 Date</div>
              <div style="font-weight: 600; color: #0d1825; font-size: 0.95rem;">${formattedDate}</div>
            </td>
          </tr>
          <tr>
            <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0;">
              <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">🕐 Time</div>
              <div style="font-weight: 600; color: #0d1825; font-size: 0.95rem;">${formattedTime} <span style="color: #94a3b8; font-weight: 400; font-size: 0.85rem;">(PKT - Karachi)</span></div>
            </td>
          </tr>
          <tr>
            <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0;">
              <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">💻 Platform</div>
              <div style="font-weight: 600; color: #0d1825; font-size: 0.95rem;">${platformLabel}</div>
            </td>
          </tr>
          ${data.meetingLink ? `
          <tr>
            <td style="padding: 16px 20px; border-bottom: 1px solid #e2e8f0;">
              <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">🔗 Meeting Link</div>
              <div style="font-size: 0.9rem;">
                <a href="${data.meetingLink}" style="color: #63daff; text-decoration: none; font-weight: 600; word-break: break-all;">${data.meetingLink}</a>
              </div>
            </td>
          </tr>
          ` : ''}
          <tr>
            <td style="padding: 16px 20px;">
              <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 4px;">⏱ Duration</div>
              <div style="font-weight: 600; color: #0d1825; font-size: 0.95rem;">${MEETING_DURATION_MINUTES} minutes</div>
            </td>
          </tr>
        </table>
      </div>

      ${data.meetingLink ? `
      <div style="text-align: center; margin-bottom: 28px;">
        <a href="${data.meetingLink}"
           style="display: inline-block; background: #63daff; color: #020408; font-weight: 700; padding: 14px 32px; border-radius: 10px; text-decoration: none; font-size: 0.95rem;">
          Join ${platformLabel} Call →
        </a>
      </div>
      ` : ''}

      <div style="background: #f8fafc; border-left: 3px solid #63daff; border-radius: 0 10px 10px 0; padding: 16px 20px; margin-bottom: 28px;">
        <div style="font-weight: 700; color: #0d1825; font-size: 0.88rem; margin-bottom: 8px;">What to expect on the call</div>
        <ul style="margin: 0; padding-left: 16px; color: #64748b; font-size: 0.85rem; line-height: 1.8;">
          <li>Review your current business &amp; goals</li>
          <li>Identify the right AI chatbot solution for you</li>
          <li>Walk away with a clear action plan</li>
        </ul>
      </div>

      <p style="color: #64748b; line-height: 1.7; margin: 0 0 8px; font-size: 0.88rem;">
        A calendar invite has been sent to this email. You'll also receive a reminder before the call.
      </p>
      <p style="color: #64748b; line-height: 1.7; margin: 0; font-size: 0.88rem;">
        Need to reschedule? Reply to this email and we'll find a time that works for you.
      </p>
    </div>

    <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 24px 40px; text-align: center;">
      <p style="color: #94a3b8; font-size: 0.78rem; margin: 0 0 6px;">© ${new Date().getFullYear()} Chatversio AI · Karachi, Pakistan</p>
      <p style="color: #94a3b8; font-size: 0.78rem; margin: 0;">
        <a href="mailto:saif@chatversio-ai.com" style="color: #63daff; text-decoration: none;">saif@chatversio-ai.com</a> · <a href="mailto:esha@chatversio-ai.com" style="color: #63daff; text-decoration: none;">esha@chatversio-ai.com</a>
      </p>
    </div>

  </div>
</body>
</html>`.trim(),
  })
}

// ── Owner notification ────────────────────────────────────────
async function sendOwnerNotification(data: {
  name: string; email: string; date: string; time: string
  platform: string; meetingLink?: string
}) {
  const transporter = getMailTransporter()
  const platformLabel = data.platform === 'zoom' ? 'Zoom' : 'Google Meet'
  await transporter.sendMail({
    from: `"Chatversio AI Bookings" <${MAIL_USER}>`,
    to: notifyRecipients(),
    subject: `New Meeting Booked - ${data.name} on ${data.date} at ${data.time}`,
    html: `
      <h2>New Strategy Call Booking</h2>
      <p><strong>Name:</strong> ${esc(data.name)}</p>
      <p><strong>Email:</strong> <a href="mailto:${esc(data.email)}">${esc(data.email)}</a></p>
      <p><strong>Date:</strong> ${data.date}</p>
      <p><strong>Time:</strong> ${data.time} (PKT)</p>
      <p><strong>Platform:</strong> ${platformLabel}</p>
      ${data.meetingLink ? `<p><strong>Meeting Link:</strong> <a href="${data.meetingLink}">${data.meetingLink}</a></p>` : ''}
    `,
  })
}

// ── Main POST handler ─────────────────────────────────────────
export async function POST(req: Request) {
  try {
    const body = await req.json()
    const name = typeof body.name === 'string' ? body.name.trim() : ''
    const email = typeof body.email === 'string' ? body.email.trim() : ''
    const date = typeof body.date === 'string' ? body.date.trim() : ''
    const time = typeof body.time === 'string' ? body.time.trim() : ''
    const platform = typeof body.platform === 'string' ? body.platform.trim() : ''

    // 1. Validate (return a clear message the form can show to the visitor)
    if (!name || !email || !date || !time || !platform) {
      return Response.json({ error: 'Please fill in your name, email, date, time and platform.' }, { status: 400 })
    }
    if (!EMAIL_RE.test(email) || email.length > 254) {
      return Response.json({ error: 'Please enter a valid email address.' }, { status: 400 })
    }
    if (name.length > 100) {
      return Response.json({ error: 'Please use a shorter name.' }, { status: 400 })
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(time) || Number.isNaN(new Date(`${date}T${time}:00`).getTime())) {
      return Response.json({ error: 'Please choose a valid date and time.' }, { status: 400 })
    }
    if (platform !== 'zoom' && platform !== 'google-meet') {
      return Response.json({ error: 'Please choose Google Meet or Zoom.' }, { status: 400 })
    }

    // 2. Block past times
    const slotDateTime = new Date(`${date}T${time}:00`)
    const nowPlus5 = new Date(Date.now() + 5 * 60 * 1000)
    if (slotDateTime < nowPlus5) {
      return Response.json({ error: 'That time has already passed. Please choose a future time.' }, { status: 400 })
    }

    // 3. Duplicate slot check (in-memory)
    const slotKey = `${date}|${time}`
    if (bookedSlots.has(slotKey)) {
      return Response.json({ error: 'That time slot is already taken. Please choose a different time.' }, { status: 409 })
    }

    // 4. Check Google Calendar for conflicts
    const available = await isSlotAvailable(date, time)
    if (!available) {
      return Response.json(
        { error: 'This time conflicts with another meeting. Please choose a different time.' },
        { status: 409 }
      )
    }

    // 5. Create Zoom link before calendar (so it can be embedded in event description)
    let meetingLink: string | undefined
    if (platform === 'zoom') {
      meetingLink = (await createZoomMeeting({ name, email, date, time })) || undefined
    }

    // 6. Add to Google Calendar — capture response to extract Meet link
    const calendarEvent = await addToCalendar({ name, email, date, time, platform, meetingLink })

    // 7. Extract Google Meet link from Calendar API response
    if (platform === 'google-meet') {
      const entryPoints = calendarEvent?.conferenceData?.entryPoints
      const videoEntry = (entryPoints as any[])?.find((ep: any) => ep.entryPointType === 'video')
      meetingLink = videoEntry?.uri || (entryPoints as any[])?.[0]?.uri || undefined
    }

    // 8. Mark slot as booked
    bookedSlots.add(slotKey)

    // 9. Send confirmation email (non-critical)
    try {
      await sendConfirmationEmail({ name, email, date, time, platform, meetingLink })
    } catch (emailErr: any) {
      console.error('Confirmation email failed (booking still succeeded):', emailErr.message)
    }

    // 10. Notify owner (non-critical)
    try {
      await sendOwnerNotification({ name, email, date, time, platform, meetingLink })
    } catch (notifyErr: any) {
      console.error('Owner notification failed:', notifyErr.message)
    }

    return Response.json({ success: true })

  } catch (err) {
    console.error('Schedule API error:', err)
    return Response.json({ error: 'We could not complete your booking. Please try again, or email saif@chatversio-ai.com or esha@chatversio-ai.com and we will arrange a time.' }, { status: 500 })
  }
}