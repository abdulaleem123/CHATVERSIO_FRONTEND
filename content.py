"""Services and illustrated agent roles presented on the site."""

# Keep the established public-facing paths when a service takes a new display name.
services = [
    ('Chat Agent', 'website-assistants', 'Answer questions on your site, turn a conversation into a lead and let your team take over in the CRM.'),
    ('Sales Agent', 'sales-automation', 'Qualify buyers, follow up on the right opportunity and move it towards a meeting.'),
    ('Voice Agent', 'voice-assistants', 'Answer inbound calls, make outbound follow-ups and pass the right details to your team.'),
    ('Document Processing System', 'documents', 'Turn PDFs, scans and Word files into structured records for review.'),
    ('Lead Generation Funnel', 'lead-generation', 'Connect lead capture, qualification, CRM routing and follow-up in one funnel.'),
    ('Instagram Agent', 'instagram-agent', 'Turn an Instagram DM into a product answer, a qualified enquiry or a booking.'),
    ('Facebook Messenger Agent', 'facebook-agent', 'Answer Facebook Page messages and hand interested buyers to the right person.'),
    ('Telegram Agent', 'telegram-agent', 'Handle questions and service requests in your Telegram conversations.'),
    ('Third-Party Integrations', 'integrations', 'Connect your agents to your CRM, calendar, email and the tools you already use.'),
    ('WhatsApp Agent', 'social-agents', 'Answer WhatsApp Business messages and keep the next step connected to your team.'),
    ('Customer Support', 'customer-support', 'Answer recurring questions and pass exceptions to the right person.'),
    ('Appointment Booking', 'appointment-booking', 'Help customers choose, confirm or change a time in your calendar.'),
    ('Multilingual Agents', 'multilingual-agents', 'Welcome customers in the languages your business supports.'),
    ('Internal Helpdesk & HR', 'internal-helpdesk', 'Give staff a first stop for IT requests, onboarding and policy questions.'),
    ('Email Automation', 'email-automation', 'Follow up on enquiries, route replies and keep the lead history together.'),
    ('LinkedIn & Lead Research', 'lead-research', 'Research business prospects and prepare relevant outreach for your sales team.'),
    ('Web Data Extraction', 'web-data', 'Bring selected information from public websites into a structured dataset.'),
    ('Custom Platforms & Websites', 'custom-platforms', 'Build agent-powered websites, internal tools and single- or multi-tenant platforms.'),
]

PERSONAS = [
    {
        'id':'chat', 'slug':'website-assistants', 'name':'Chat Agent', 'short':'Chat',
        'portrait':'Illustrated Chat Agent in a lilac overshirt',
        'line':'“What would you like to know?”', 'outcome':'Turn a website visit into a conversation.',
        'verb':'Answer', 'card':'Website conversations'
    },
    {
        'id':'sales', 'slug':'sales-automation', 'name':'Sales Agent', 'short':'Sales',
        'portrait':'Illustrated Sales Agent in glasses and an orange jacket',
        'line':'“Shall we find a time to talk?”', 'outcome':'Give interested buyers a next step.',
        'verb':'Follow up', 'card':'Leads & follow-ups'
    },
    {
        'id':'voice', 'slug':'voice-assistants', 'name':'Voice Agent', 'short':'Voice',
        'portrait':'Illustrated Voice Agent wearing a copper-coloured headset',
        'line':'“How can I help with your call?”', 'outcome':'Pick up the call, even after hours.',
        'verb':'Pick up', 'card':'Inbound & outbound calls'
    },
]

PROFILES = {
    'website-assistants': ('Core agents', 'agent-chat',
        'A visitor asks which service fits their small business.',
        'Answer from your approved website content, then ask what they would like to do next.',
        'Capture their details in your CRM or let a teammate take over the live conversation.',
        ['Website chat in your brand’s voice', 'Live conversation view and human takeover', 'Contact capture, CRM history and calendar links']),
    'sales-automation': ('Core agents', 'agent-sales',
        'A buyer has requested a quote and still has a question about the options.',
        'Use the enquiry and product information to answer the question and qualify the opportunity.',
        'Update the CRM stage, agree on a follow-up or book time with the sales owner.',
        ['Questions that qualify a buyer', 'Relevant follow-ups and objection handling', 'Pipeline updates, meeting booking and sales handoff']),
    'voice-assistants': ('Core agents', 'agent-voice',
        'A customer calls after hours about a repair. Another has asked for a callback.',
        'Answer the incoming call or place the requested follow-up, gather the details and offer a time.',
        'Transfer the call when needed or send a summary and appointment to dispatch.',
        ['Inbound answering and outbound follow-up', 'Call routing, transfers and human handoff', 'Appointment booking and call summaries']),
    'documents': ('Operations', 'ticket',
        'An operations team receives an invoice as a scanned PDF.',
        'Read the file, extract the supplier, reference and amounts, and flag uncertain fields for review.',
        'Send reviewed fields to a spreadsheet or connected business system.',
        ['OCR for scanned files', 'PDF and Word analysis', 'Field validation, review and export']),
    'lead-generation': ('Growth', 'ticket',
        'A prospective customer requests a quote on a campaign landing page.',
        'Capture the enquiry and ask about their requirements, budget and timing.',
        'Create a CRM record, assign an owner and start the agreed follow-up.',
        ['Landing page and channel capture', 'Qualification questions and lead scoring', 'CRM routing and follow-up ownership']),
    'instagram-agent': ('Channels', 'messenger',
        'A shopper sends an Instagram DM about a product featured in a post.',
        'Answer the product question and check whether they need stock information or a consultation.',
        'Pass the enquiry and conversation history to sales or share a booking link.',
        ['Instagram direct messages', 'Approved product and service answers', 'Lead capture and team handoff']),
    'facebook-agent': ('Channels', 'messenger',
        'A prospective customer messages your Facebook Page about a service.',
        'Explain what is included and ask which location or appointment they need.',
        'Send the qualified Messenger enquiry to your team with the customer’s request.',
        ['Facebook Page messaging', 'Service and availability questions', 'Messenger-to-CRM handoff']),
    'telegram-agent': ('Channels', 'messenger',
        'A customer starts a Telegram conversation about an existing request.',
        'Ask for the reference and return the information your team has made available.',
        'Route an unresolved request to support with its Telegram conversation attached.',
        ['Telegram conversations', 'Knowledge-base replies and reference capture', 'Support routing and escalation']),
    'integrations': ('Operations', 'patch',
        'A chat ends with a lead who wants to speak with sales.',
        'Send the agreed fields to your CRM and offer availability through your calendar.',
        'Keep the lead owner, meeting details and confirmation in the tools the team already uses.',
        ['CRM, calendar, email and meeting connections', 'Third-party APIs and webhooks', 'Field mapping, testing and exception handling']),
    'social-agents': ('Channels', 'messenger',
        'A customer sends a WhatsApp message asking when an order will arrive.',
        'Use approved order details to answer in the same conversation.',
        'Open a support request or hand an interested buyer to the sales team.',
        ['WhatsApp Business messaging', 'Order and service enquiries', 'Shared lead and support routing']),
    'customer-support': ('Support', 'messenger',
        'A customer asks about a delayed delivery.',
        'Look up the available order details and explain what happens next.',
        'Send the order reference and conversation to support when an exception needs review.',
        ['Approved FAQ and policy answers', 'Order or ticket lookup', 'Escalation with the conversation attached']),
    'appointment-booking': ('Operations', 'ticket',
        'A returning customer wants a different appointment.',
        'Check the connected calendar and offer eligible times.',
        'Update the appointment and provide the confirmation details.',
        ['Availability and booking rules', 'Calendar sync and confirmation', 'Reminders and rescheduling']),
    'multilingual-agents': ('Support', 'headset',
        'A customer opens a conversation in Urdu.',
        'Respond in a supported language using the terminology your team approves.',
        'Preserve the original request and give the next person a usable summary.',
        ['Language selection or detection', 'Localized product and policy answers', 'Handoffs across languages']),
    'internal-helpdesk': ('Support', 'patch',
        'A new team member needs system access.',
        'Use your approved onboarding guide to identify the right request.',
        'Route the ticket to the team authorized to handle it.',
        ['IT and HR self-service', 'Onboarding and policy questions', 'Ticket ownership and escalation']),
    'email-automation': ('Growth', 'messenger',
        'A prospect asked for a proposal and agreed to a follow-up by email.',
        'Send a relevant follow-up using the offer, timing and tone approved by your team.',
        'Route replies to the owner and log the conversation against the opportunity.',
        ['Email campaigns and sequences', 'Reply routing and human review', 'CRM activity and follow-up tracking']),
    'lead-research': ('Growth', 'ticket',
        'Sales needs a focused list of businesses in a particular market.',
        'Research relevant companies and prepare context for a LinkedIn introduction.',
        'Give the sales owner a reviewable list with sources and suggested next steps.',
        ['Prospect criteria and research', 'CRM enrichment and deduplication', 'LinkedIn outreach preparation']),
    'web-data': ('Operations', 'patch',
        'Your team checks the same public listings for changes each week.',
        'Collect agreed fields from the selected public pages and identify changes.',
        'Deliver a structured file or feed with source references for review.',
        ['Public web data extraction', 'Structured fields and update schedules', 'Exports to a spreadsheet or internal tool']),
    'custom-platforms': ('Operations', 'patch',
        'A business needs a customer portal and an agent that knows which account it is serving.',
        'Design the website, account structure and agent workflow around how customers use it.',
        'Connect the approved tools and hand the working platform to its operators.',
        ['Website and internal tool design', 'Single-tenant or multi-tenant systems', 'Agent workflows and platform integrations'])
}

faq=[('How do I book a call with the CEO?','Choose a date, time and meeting platform in the booking calendar.'),('Which businesses can use an agent?','Service businesses, online shops, agencies and software teams can start with a recurring customer enquiry.'),('Can you build around our workflow?','Yes. Discovery covers the questions, systems and handoffs specific to your business.'),('Which social channels can we connect?','WhatsApp, Instagram, Facebook Messenger and Telegram can work alongside your website chat.'),('How long does setup take?','A simple setup can take days. Custom workflows may take one to two weeks, depending on integrations and testing.'),('Can we keep our phone number?','The team checks compatibility during discovery and agrees number ownership before setup.'),('What if the agent cannot answer?','You choose the fallback, such as collecting details for a callback. The team tests it before launch.'),('Can we review conversations in our CRM?','Yes. The Chat Agent can capture leads, show conversation history and let a person take over from the agent.'),('Can a person take over?','Yes. You define the handoff point and how the right person receives the conversation.'),('How are recordings and stored data handled?','Recording settings and retention periods are agreed during setup. The website privacy policy covers information submitted here.')]

STORIES = {
    'service': {
        'label':'Home services','channel':'Voice call','solution':'voice-assistants','intro':'An AC repair enquiry comes in after closing.',
        'steps': [
            ['08:42 PM','Pick up.','A homeowner calls when dispatch is closed. The voice agent gets the conversation started.','Caller','My AC stopped cooling. Could someone come tomorrow?','Voice agent','I can help with a visit. What’s your ZIP code?'],
            ['08:43 PM','Get the details.','The agent checks the service area and captures what the technician needs to know.','Caller','94103. The fan runs, but the air is warm.','Voice agent','I have Tuesday at 10 AM. Would that work?'],
            ['08:44 PM','Hand it over.','Dispatch gets the appointment, location and repair note together.','Destination','Dispatch calendar','Request','AC repair · ZIP 94103']
        ],
        'callback':'Dispatch callback','callbackDetail':'Confirm the AC issue and arrange a visit by phone.'
    },
    'property': {
        'label':'Real estate','channel':'Website chat','solution':'website-assistants','intro':'A buyer is browsing listings after work.',
        'steps': [
            ['07:15 PM','Meet the buyer.','A visitor asks about a listing while the sales team is out on viewings.','Visitor','Can I see the two-bedroom apartment on Oak Street?','Web agent','Yes. Are you looking to rent or buy?'],
            ['07:16 PM','Find the fit.','The agent records the listing, intent and preferred viewing time.','Visitor','I’m looking to buy. A morning viewing would be great.','Web agent','Would Tuesday at 10 AM suit you for a tour?'],
            ['07:17 PM','Brief the agent.','The sales agent receives the buyer’s interest and viewing details.','Destination','Property sales CRM','Request','Buyer · Oak Street · Two bedrooms']
        ],
        'callback':'Sales callback','callbackDetail':'Discuss the Oak Street listing and arrange a viewing.'
    },
    'business': {
        'label':'B2B sales','channel':'Sales follow-up','solution':'sales-automation','intro':'A buyer replies after requesting pricing.',
        'steps': [
            ['09:04 AM','Pick up the thread.','The Sales Agent follows up on a pricing request. The buyer replies with a team size.','Buyer','We’re comparing plans for twelve people. Can someone walk us through them?','Sales Agent','Happy to. What would your team like to do first?'],
            ['09:05 AM','Qualify the opportunity.','The agent records what the buyer needs and offers a product demonstration.','Buyer','We need lead routing and a shared inbox.','Sales Agent','I’ll bring those notes. Does Tuesday at ten work for a demo?'],
            ['09:06 AM','Brief the sales rep.','The sales owner gets a meeting, team size and the two features that matter to this buyer.','Destination','Sales CRM and calendar','Request','Product demo · Twelve seats']
        ],
        'callback':'Sales owner callback','callbackDetail':'Talk through lead routing and a shared inbox for a team of twelve.'
    },
    'clinic': {
        'label':'Clinics','channel':'WhatsApp','solution':'appointment-booking','intro':'A patient needs to move an appointment.',
        'steps': [
            ['06:28 PM','Answer the message.','A patient writes on WhatsApp after the reception desk has closed.','Patient','Could I move my appointment to next week?','Booking agent','Of course. What day works best for you?'],
            ['06:29 PM','Check the calendar.','The agent uses the clinic’s scheduling rules to find a suitable time.','Patient','Tuesday morning, if possible.','Booking agent','Tuesday at 10 AM is available. Shall I move it there?'],
            ['06:30 PM','Update reception.','Reception can see the revised time and the original rescheduling request.','Destination','Clinic calendar','Request','Existing patient · Reschedule']
        ],
        'callback':'Reception callback','callbackDetail':'Discuss available times with the reception team.'
    }
}
INTEGRATIONS=[
 ('WhatsApp','Messaging','Customer enquiry','Support or sales queue'),
 ('Instagram','Social','Direct message','Sales enquiry'),
 ('Messenger','Social','Page conversation','Customer support queue'),
 ('Google Calendar','Scheduling','Selected appointment','Calendar event'),
 ('Slack','Internal','Employee question','Helpdesk channel'),
 ('WordPress','Website','Website conversation','Lead record'),
 ('Shopify','Commerce','Product question','Sales follow-up'),
 ('Telegram','Messaging','Support message','Support queue'),
 ('CRM','Sales','Qualified lead and conversation','Owner and pipeline stage'),
 ('Calendly','Scheduling','Requested meeting','Booked time and confirmation'),
 ('Email','Follow-up','Customer reply','Sales owner and CRM history'),
 ('Third-party API','Custom connection','Approved event or webhook','Mapped record in your business tool')
]
DELIVERY=[
 ('Discover','Trace a real enquiry.','Bring a call, chat or form submission. Together we identify where customers wait and what a good outcome looks like.','An agreed use case and success criteria.'),
 ('Design','Write the conversation.','Choose the questions, tone and fallback. Your team reviews the words that customers will actually hear or read.','An approved conversation flow.'),
 ('Build','Give it a working voice.','We build the agent and rehearse ordinary requests, ambiguous answers and situations that need a person.','A working agent you can try.'),
 ('Connect','Put the details to work.','Connect the approved phone line, website, CRM or calendar. Test that each piece of information lands in the right place.','A tested handoff into your tools.'),
 ('Launch','Open the line.','Review test conversations and agree who owns exceptions. Your team signs off on the first live workflow.','A launch plan and a named owner.'),
 ('Optimize','Listen back and refine.','Review missed questions, handoffs and outcomes with your team. Improve the parts that matter to the customer.','A prioritized list of improvements.')
]
