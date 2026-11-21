// src/app/api/contact/route.ts

import nodemailer from 'nodemailer'
const SITE_URL = 'https://chatversio-ai.com'

function getTransporter() {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD,
    },
  })
}

// Every notification goes to NOTIFY_EMAIL (comma-separated list allowed, or GMAIL_USER) plus Esha.
const EXTRA_NOTIFY = 'esha@chatversio-ai.com'
function notifyRecipients(): string {
  const base = (process.env.NOTIFY_EMAIL || process.env.GMAIL_USER || '').split(',').map(v => v.trim()).filter(Boolean)
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

// Allowed values for the "What do you want to automate?" dropdown.
const TOPIC_LABELS: Record<string, string> = {
  'voice-agent': 'AI voice agent / receptionist',
  'lead-follow-up': 'Lead follow-up and CRM automation',
  'chatbot-crm': 'Website chatbot with CRM',
  'custom-ai': 'Custom AI development',
  'not-sure': 'Not sure yet',
}

const EMAIL_RE = /^[^\s@<>"']+@[^\s@<>"']+\.[^\s@<>"']+$/

export async function POST(req: Request) {
  try {
    const body = await req.json()

    // Spam trap: real visitors never see or fill this hidden field. Pretend
    // success so bots get no signal, but send nothing.
    if (typeof body.hp === 'string' && body.hp.trim() !== '') {
      return Response.json({ success: true }, { status: 200 })
    }

    const name = typeof body.name === 'string' ? body.name.trim() : ''
    const email = typeof body.email === 'string' ? body.email.trim() : ''
    const message = typeof body.message === 'string' ? body.message.trim() : ''
    const phone = typeof body.phone === 'string' ? body.phone.trim() : ''
    const business = typeof body.business === 'string' ? body.business.trim() : ''
    const companyWebsite = typeof body.companyWebsite === 'string' ? body.companyWebsite.trim() : ''
    const topicValue = typeof body.topic === 'string' ? body.topic.trim() : ''
    const topic = TOPIC_LABELS[topicValue] ?? ''

    if (!name || !email || !message) {
      return Response.json({ error: 'Please fill in your name, email and message.' }, { status: 400 })
    }
    if (!EMAIL_RE.test(email) || email.length > 254) {
      return Response.json({ error: 'Please enter a valid email address.' }, { status: 400 })
    }
    if (name.length > 100 || phone.length > 40 || business.length > 150 || companyWebsite.length > 200 || message.length > 5000) {
      return Response.json({ error: 'One of the fields is too long. Please shorten it and try again.' }, { status: 400 })
    }

    const safeName = esc(name)
    const safeEmail = esc(email)
    const safeMessage = esc(message)
    // Phone and business were collected by the form but never emailed before.
    const extraRows = ([
      phone ? ['Phone', esc(phone)] : null,
      business ? ['Business', esc(business)] : null,
      companyWebsite ? ['Website', esc(companyWebsite)] : null,
      topic ? ['Wants to automate', esc(topic)] : null,
    ].filter(Boolean) as string[][]).map(([label, val]) => `
        <tr style="border-top: 1px solid #f1f5f9;">
          <td style="padding: 10px 0; color: #64748b; vertical-align: top; font-weight: 600; text-transform: uppercase; font-size: 0.75rem;">${label}</td>
          <td style="padding: 10px 0; color: #0d1825; font-weight: 500;">${val}</td>
        </tr>`).join('')

    const transporter = getTransporter()

    // ── Email to YOU (notification) ───────────────────────────
    await transporter.sendMail({
      from: `"Chatversio AI Contact" <${process.env.GMAIL_USER}>`,
      to: notifyRecipients(),
      replyTo: email,
      subject: `📩 New Contact Form Submission - ${name.replace(/[\r\n]+/g, ' ')}`,
      html: `
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 32px 20px; margin: 0;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

    <div style="background: linear-gradient(135deg, #020408, #0d1825); padding: 32px 36px;">
      <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Chatversio<span style="color: #63daff;">AI</span>
      </div>
      <div style="color: rgba(255,255,255,0.45); font-size: 0.82rem; margin-top: 4px;">New Contact Form Submission</div>
    </div>

    <div style="padding: 32px 36px;">
      <h2 style="margin: 0 0 24px; font-size: 1.15rem; color: #0d1825;">You have a new message from your website.</h2>

      <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
        <tr>
          <td style="padding: 10px 0; color: #64748b; width: 100px; vertical-align: top; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.06em;">Name</td>
          <td style="padding: 10px 0; color: #0d1825; font-weight: 500;">${safeName}</td>
        </tr>
        <tr style="border-top: 1px solid #f1f5f9;">
          <td style="padding: 10px 0; color: #64748b; vertical-align: top; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.06em;">Email</td>
          <td style="padding: 10px 0;"><a href="mailto:${safeEmail}" style="color: #0ea5e9; text-decoration: none;">${safeEmail}</a></td>
        </tr>
        ${extraRows}
        <tr style="border-top: 1px solid #f1f5f9;">
          <td style="padding: 10px 0; color: #64748b; vertical-align: top; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.06em;">Message</td>
          <td style="padding: 10px 0; color: #0d1825; line-height: 1.6; white-space: pre-wrap;">${safeMessage}</td>
        </tr>
      </table>

      <div style="margin-top: 28px; padding: 16px 20px; background: #f8fafc; border-radius: 10px; border-left: 3px solid #63daff;">
        <p style="margin: 0; font-size: 0.82rem; color: #64748b;">
          Reply directly to this email to respond to <strong style="color: #0d1825;">${safeName}</strong> at <a href="mailto:${safeEmail}" style="color: #0ea5e9;">${safeEmail}</a>.
        </p>
      </div>
    </div>

    <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 36px; text-align: center;">
      <p style="color: #94a3b8; font-size: 0.78rem; margin: 0;">
        © ${new Date().getFullYear()} Chatversio AI · Karachi, Pakistan
      </p>
    </div>
  </div>
</body>
</html>
      `.trim(),
    })

    // ── Auto-reply to the person who submitted ─────────────────
    // The lead is already delivered above. A failed auto-reply must not show the
    // visitor an error (they would resubmit and create duplicates).
    try {
    await transporter.sendMail({
      from: `"Chatversio AI" <${process.env.GMAIL_USER}>`,
      to: email,
      subject: `We received your message, ${name.split(' ')[0].replace(/[\r\n]+/g, ' ')}!`,
      html: `
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 32px 20px; margin: 0;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

    <div style="background: linear-gradient(135deg, #020408, #0d1825); padding: 32px 36px; text-align: center;">
      <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
        Chatversio<span style="color: #63daff;">AI</span>
      </div>
      <div style="color: rgba(255,255,255,0.45); font-size: 0.82rem; margin-top: 4px;">AI Chatbot Agency</div>
    </div>

    <div style="padding: 36px;">
      <h1 style="margin: 0 0 12px; font-size: 1.4rem; color: #0d1825;">Thanks for reaching out, ${name.split(' ')[0]}!</h1>
      <p style="color: #64748b; line-height: 1.7; margin: 0 0 24px;">
        We've received your message and our team will get back to you within <strong style="color: #0d1825;">24 hours</strong> with a custom chatbot strategy tailored to your business.
      </p>

      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-bottom: 28px;">
        <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 10px;">Your message</div>
        <p style="margin: 0; color: #475569; font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap;">${safeMessage}</p>
      </div>

      <p style="color: #64748b; line-height: 1.7; margin: 0 0 28px; font-size: 0.92rem;">
        In the meantime, feel free to <a href="${process.env.NEXT_PUBLIC_SITE_URL || SITE_URL}/schedule-event" style="color: #63daff; text-decoration: none; font-weight: 600;">schedule a call</a> directly with our CEO to get started faster.
      </p>

      <div style="text-align: center;">
        <a href="${process.env.NEXT_PUBLIC_SITE_URL || SITE_URL}/schedule-event"
           style="display: inline-block; background: #63daff; color: #020408; font-weight: 700; padding: 13px 28px; border-radius: 8px; text-decoration: none; font-size: 0.92rem;">
          Book a Call →
        </a>
      </div>
    </div>

    <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 36px; text-align: center;">
      <p style="color: #94a3b8; font-size: 0.78rem; margin: 0;">
        © ${new Date().getFullYear()} Chatversio AI · Karachi, Pakistan<br/>
        <a href="mailto:saif@chatversio-ai.com" style="color: #94a3b8;">saif@chatversio-ai.com</a> · <a href="mailto:esha@chatversio-ai.com" style="color: #94a3b8;">esha@chatversio-ai.com</a>
      </p>
    </div>
  </div>
</body>
</html>
      `.trim(),
    })
    } catch (autoReplyErr) {
      console.error('Contact auto-reply failed (message was delivered):', autoReplyErr)
    }

    return Response.json({ success: true }, { status: 200 })

  } catch (error) {
    console.error('Contact API error:', error)
    return Response.json({ error: 'Failed to send message. Please try again.' }, { status: 500 })
  }
}