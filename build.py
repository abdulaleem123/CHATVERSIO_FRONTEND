"""Generate Chatversio's static, server-independent presentation pages."""
from html import escape
from pathlib import Path
import json
from content import services, faq, PERSONAS, PROFILES, STORIES, INTEGRATIONS, DELIVERY

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
SITE = 'https://www.chatversio-ai.com'
BOOK = '/schedule-event/'
AGENTS = {slug: name for name, slug, *_ in services}
PRIMARY = {p['slug'] for p in PERSONAS}
SUPPORTING = [service for service in services if service[1] not in PRIMARY]

def link(url, text, style=''):
    return f'<a href="{escape(url, quote=True)}" class="{style}">{text}</a>'

def arrow(diagonal=False):
    return '<i aria-hidden="true" class="arrow'+(' diagonal' if diagonal else '')+'"></i>'

def cta(url=BOOK, text='Book a discovery call', style='primary'):
    return link(url,text+arrow(True),'button '+style)

def brand():
    return '<img src="/media/chatversio-brand-original.jpeg" width="860" height="290" alt="Chatversio AI" class="wordmark original-wordmark">'

def eyebrow(text, dot=False):
    return '<p class="eyebrow">'+('<i class="status-dot"></i>' if dot else '')+text+'</p>'

def img(name, alt='', css='', priority=False, sizes='(max-width: 700px) 94vw, 48vw'):
    loading='fetchpriority="high"' if priority else 'loading="lazy"'
    small,large=(390,724) if name.startswith('agent-') else (570,1230 if name=='headset' else 920 if name=='driver' else 1000)
    return (f'<img class="{css}" src="/media/{name}.webp" srcset="/media/{name}-sm.webp {small}w, /media/{name}.webp '
            f'{large}w" sizes="{sizes}" width="{large}" height="{large}" '
            f'alt="{escape(alt,quote=True)}" decoding="async" {loading}>')

def icon_play():
    return '<i class="play-icon" aria-hidden="true"></i>'

def motion_button():
    return '<button class="motion" type="button" aria-label="Pause ambient motion" aria-pressed="true"><i class="motion-icon" aria-hidden="true"></i><span>Motion on</span></button>'

def nav(path):
    items=[('/services/','Solutions'),('/#process','Process'),('/about/','About'),('/contact/','Contact')]
    links=[]
    for url,text in items:
        active=' aria-current="page"' if path==url or (url=='/services/' and path.startswith('/services/')) else ''
        links.append(f'<a href="{url}"{active}>{text}</a>')
    return (f'<header class="masthead"><div class="wrap nav-wrap">{link("/",brand(),"brand")}'
            f'<nav id="main-nav" aria-label="Main navigation">{"".join(links)}</nav>'
            f'{cta(BOOK,"Book a call","nav-cta")}<button type="button" class="menu-toggle" aria-controls="main-nav" aria-expanded="false" aria-label="Open navigation"><i></i><i></i></button>'
            '</div><div class="reading-progress" aria-hidden="true"></div></header>')

def footer():
    icons=json.loads((ROOT/'art/footer-icons.json').read_text())
    icon=lambda name: icons[name]
    main_links=[('/','Home','home'),('/about/','About','about'),('/services/','Services','services'),('/contact/','Contact','contact'),(BOOK,'Book a Call','calendar')]
    service_links=[
        ('customer-support','Customer Support Agent','support'),('lead-generation','Lead Generation','leads'),
        ('sales-automation','Sales Automation','sales'),('social-agents','WhatsApp Agent','chat'),
        ('website-assistants','Website AI Assistants','web'),('appointment-booking','Appointment Booking Agent','booking'),
        ('voice-assistants','Voice AI Assistants','voice'),('multilingual-agents','Multilingual Agents','language'),
        ('internal-helpdesk','Internal Helpdesk Agent','helpdesk')]
    group=lambda pairs: ''.join('<li>'+link(url,icon(symbol)+'<span>'+text+'</span>')+'</li>' for url,text,symbol in pairs)
    social_urls={'Facebook':'https://www.facebook.com/profile.php?id=61595764508818','Instagram':'https://www.instagram.com/chatversio','X':'https://x.com/chatversio'}
    social_colors={'Facebook':'#1877f2','Instagram':'#e4405f','X':'#000000'}
    socials=''.join(f'<a href="{escape(url,quote=True)}" aria-label="{name}" title="{name}" style="--social-brand:{social_colors[name]}" target="_blank" rel="noopener noreferrer">{icon(name)}</a>' for name,url in social_urls.items())
    footer_logo='<img src="/media/chatversio-footer-logo.png" width="860" height="290" alt="Chatversio AI">'
    return f'''<footer class="footer" id="footer"><link rel="stylesheet" href="/footer.css?v=7"><div class="footer-glow" aria-hidden="true"></div><div class="wrap">
      <div class="footer-invitation"><span class="footer-phone-wrap" aria-hidden="true"><span class="footer-phone">{icon('phone')}</span></span>
        <h2>Ready to Turn Conversations Into Customers?</h2>
        <p>See how Chatversio AI can automate conversations, capture leads, and help your business grow.</p>
        {link(BOOK,'Schedule a Call'+icon('arrow'),'footer-cta')}</div>
      <div class="footer-grid"><div class="footer-brand">{link('/',footer_logo,'footer-logo')}
        <p>Turn Conversations Into Conversions. AI-powered Agents that sell, support, and scale your business 24/7.</p>
        <div class="footer-socials" aria-label="Follow Chatversio AI">{socials}</div></div>
        <nav class="footer-nav" aria-labelledby="footer-quick-title"><h2 id="footer-quick-title">Quick Links</h2><ul>{group(main_links)}</ul></nav>
        <nav class="footer-nav footer-services" aria-labelledby="footer-services-title"><h2 id="footer-services-title">Services</h2><ul>{group([('/services/'+slug+'/',text,symbol) for slug,text,symbol in service_links])}</ul></nav>
      </div>
      <div class="footer-banner"><p class="footer-signature" aria-hidden="true">Chatversio AI</p></div>
      <div class="footer-bottom"><p>© 2026 Chatversio AI. All rights reserved.</p><p>Built with intelligence. Powered by AI.</p>
        <div class="footer-legal">{link(SITE+'/privacy-policy','Privacy Policy')}<span aria-hidden="true">·</span>{link(SITE+'/terms','Terms of Service')}</div></div>
    </div></footer>'''

def page(path, name, description, body, theme='dark'):
    f=OUT/path.strip('/')/'index.html'
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(f'''<!doctype html><html lang="en" id="top"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
    <meta name="theme-color" content="#060f26"><meta name="description" content="{escape(description,quote=True)}">
    <title>{escape(name)} · Chatversio AI</title>
    <meta property="og:title" content="{escape(name,quote=True)} · Chatversio AI"><meta property="og:description" content="{escape(description,quote=True)}">
    <meta property="og:image" content="https://www.chatversio-ai.com/media/home-preview.jpg">
    <link rel="icon" href="/media/favicon.png" type="image/png"><link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/fonts/jakarta-700.woff" as="font" type="font/woff" crossorigin>
    <link rel="stylesheet" href="/style.css"><script src="/site-config.js" defer></script><script src="/studio.js" defer></script><script src="/integration.js" defer></script></head>
    <body class="theme-{theme}"><a class="skip" href="#main">Skip to content</a>{nav(path)}
    <main id="main" tabindex="-1">{body}</main>{footer()}</body></html>''')

def film():
    return f'''<dialog id="showreel" aria-labelledby="film-title">
      <div class="film-head"><div>{eyebrow('Chatversio / Demo film')}<h2 id="film-title">After hours.</h2></div>
      <button type="button" data-close-film class="round icon-close" aria-label="Close demo film"></button></div>
      <video controls muted playsinline preload="none" data-src="/media/after-hours.mp4" poster="/media/film-poster.webp">
        <track kind="captions" srclang="en" label="English" src="/media/after-hours.vtt">
      </video><div class="film-foot"><details><summary>Read the transcript</summary><p>The caller asks, “My AC stopped cooling. Can I get a visit tomorrow?” The agent replies, “What’s your ZIP code? And does tomorrow morning work?” Dispatch receives the repair request, service area and requested visit time.</p></details>
      <button type="button" class="film-sound" aria-pressed="false" aria-label="Enable film sound">Sound off</button>
      {link('/#demo','Try the workflow '+arrow(),'film-demo')}</div></dialog>'''

def hero():
    views=[]
    switches=[]
    for i,p in enumerate(PERSONAS):
        key=p['id']
        visible='' if i==0 else ' hidden'
        views.append(f'''<div class="portrait-scene" id="view-{key}" data-scene-id="{key}"{visible}>
          <div class="portrait-light" aria-hidden="true"></div><div class="portrait-orbit" aria-hidden="true"></div>
          <div class="portrait-float">{img('agent-'+key,p['portrait'],'hero-person',i==0,'(max-width:720px) 78vw, 40vw')}</div>
          <a class="persona-note" href="/services/{p['slug']}/"><span>{p['card']}</span><strong>{p['name']}</strong>{arrow(True)}</a>
        </div>''')
        switches.append(f'''<button type="button" data-view="{key}" aria-controls="view-{key}" aria-pressed="{str(i==0).lower()}">{p['short']}</button>''')
    return f'''<section class="hero" aria-labelledby="hero-title">
    <div class="hero-light" aria-hidden="true"></div><canvas id="sound-field" aria-hidden="true"></canvas>
    <div class="wrap hero-layout"><div class="hero-copy">
    {eyebrow('Chat · Sales · Voice',True)}<h1 id="hero-title"><span>Never miss</span><em>a hello.</em></h1>
    <p class="hero-deck">Answer website visitors, follow up with buyers and take calls after hours. Your team gets the lead, the context and the next step.</p>
    <div class="actions">{cta()}<button type="button" class="film-trigger">{icon_play()}<span>Watch the demo<small>00:18</small></span></button></div></div>
    <figure class="soundstage cast-stage" data-current="chat" aria-label="Explore the three agent characters and the studio headset">
      <canvas class="hero-3d" aria-hidden="true"></canvas>
      <div class="stage-fallback" aria-hidden="true">
        <img class="fallback-frame" src="/media/speech-frame.webp" width="1000" height="1000" alt="" decoding="async">
        <img class="fallback-prop prop-chat" src="/media/messenger-sm.webp" width="570" height="570" alt="" decoding="async">
        <img class="fallback-prop prop-sales" src="/media/ticket-sm.webp" width="570" height="570" alt="" decoding="async">
        <img class="fallback-prop prop-voice" src="/media/headset-sm.webp" width="570" height="570" alt="" decoding="async">
      </div>
      {''.join(views)}
      <div class="gear-view" id="view-gear" data-scene-id="gear" hidden>
        <div class="turntable" tabindex="0" role="group" aria-label="3D studio headset. Drag horizontally or use the left and right arrow keys to rotate.">
          {img('headset','Chrome and blue studio headset with a boom microphone','hero-poster',False,'(max-width:720px) 90vw, 48vw')}
          <video class="hero-loop" data-src="/media/operator-loop.webm" muted loop playsinline disablepictureinpicture aria-hidden="true" preload="none"></video>
          <img class="turn-frame" alt="" hidden width="690" height="690"></div>
        <div class="turn-controls"><button class="turn-arrow prev" aria-label="Rotate headset left" type="button">{arrow()}</button>
        <span>Drag to turn <i>360°</i></span><button type="button" class="turn-arrow" aria-label="Rotate headset right">{arrow()}</button></div>
      </div>
      <figcaption class="cast-dock"><div class="cast-switches" role="group" aria-label="Choose an agent character">{''.join(switches)}</div>
      <button type="button" class="gear-switch" data-view="gear" aria-controls="view-gear" aria-pressed="false" aria-label="Explore the 360-degree headset"><i aria-hidden="true" class="orbit-icon"></i>360°</button></figcaption>
    </figure></div>
    <div class="hero-end wrap"><a href="#solutions" class="scroll-cue"><i></i> Meet the agents</a>{motion_button()}</div>
    </section><script type="module" src="/hero-3d.js"></script>'''+film()

def channel_band():
    entries=[('Chat Agent','website-assistants'),('Sales Agent','sales-automation'),('Voice Agent','voice-assistants'),('Document processing','documents'),('Lead generation','lead-generation'),('Connected workflows','integrations')]
    visible=''.join(link('/services/'+s+'/',n)+'<i class="spark" aria-hidden="true"></i>' for n,s in entries)
    duplicate=''.join('<span>'+n+'</span><i class="spark"></i>' for n,s in entries)
    return f'<div class="channel-band" aria-label="Explore channels"><div class="ribbon-track"><div>{visible}</div><div aria-hidden="true">{duplicate}</div></div></div>'

def story():
    d=STORIES['service']
    tabs=''.join(f'<button type="button" data-industry="{key}" aria-pressed="{str(i==0).lower()}">{v["label"]}</button>' for i,(key,v) in enumerate(STORIES.items()))
    rows=''
    for i,item in enumerate(d['steps']):
        rows+=f'''<article class="chapter{' current' if i==0 else ''}" data-chapter="{i}">
          <button type="button" class="chapter-jump" data-jump="{i}" aria-current="{str(i==0).lower()}"><span class="chapter-num">0{i+1}</span>
          <span class="chapter-title">{item[1]}</span>{arrow()}</button>
          <p class="chapter-desc">{item[2]}</p></article>'''
    return f'''<section class="story light" id="demo" aria-labelledby="demo-title"><div class="wrap">
    <div class="section-lead"><div>{eyebrow('Interactive workflow')}<h2 id="demo-title">One enquiry.<br><em>See where it goes.</em></h2></div>
    <div class="lead-aside"><p>Choose a business and follow a sample conversation from first contact to handoff.</p><div class="industry pills" aria-label="Choose a sample business">{tabs}</div></div></div>
    <div class="story-track"><div class="stage-holder"><div class="story-stage" data-scene="0">
      <div class="stage-meta"><span class="scene-channel"><i class="status-dot"></i><b id="story-channel">Voice call</b></span><time id="scene-time">08:42 PM</time></div>
      <div class="stage-art">{img('headset','','scene-prop')}</div>
      <div class="dialogue" aria-live="polite" aria-atomic="true"><div><small id="speaker-one">Caller</small><p id="line-one">{d['steps'][0][4]}</p></div>
      <div><small id="speaker-two">Voice agent</small><p id="line-two">{d['steps'][0][6]}</p></div></div>
      <div class="handoff-record" hidden aria-live="polite"><div class="record-status"><i></i><span id="record-status">Appointment booked</span></div><h3 id="record-title">AC repair</h3><dl><div><dt>Sent to</dt><dd id="record-to">Dispatch calendar</dd></div><div><dt id="record-field">Visit</dt><dd id="record-value">Tuesday, 10 AM</dd></div></dl></div>
      <div class="sample-audio"><audio preload="none"></audio><button type="button" id="speak" aria-label="Play sample conversation" aria-pressed="false" hidden>{icon_play()}<span>Hear sample</span></button></div>
    </div>
    <div class="stage-steps"><div class="scene-dots" aria-label="Choose a scene">{''.join(f'<button type="button" data-jump="{i}" aria-label="Show {text} scene" aria-current="{str(i==0).lower()}"></button>' for i,text in enumerate(['answer','qualify','handoff']))}</div>
    <span id="scene-count">01 / 03</span><button type="button" id="advance">Next scene {arrow()}</button></div></div>
    <div class="chapters">{rows}
    <div class="handoff-options" aria-label="Choose an example handoff"><span>Try a different outcome</span>
      <div class="pills"><button type="button" data-outcome="book" aria-pressed="true">Book a time</button><button type="button" data-outcome="callback" aria-pressed="false">Request a callback</button></div></div>
    {link('/contact/?solution=voice-assistants','Plan a similar workflow '+arrow(True),'text-link story-enquire')}</div></div>
    </div><script type="application/json" id="story-data">{json.dumps(STORIES,ensure_ascii=False)}</script></section>'''

def posters():
    posts=[]
    for p in PERSONAS:
        art=img('agent-'+p['id'],p['portrait'],'poster-person',sizes='(max-width:720px) 68vw, 31vw')
        posts.append(f'''<a class="profile-poster poster-{p['id']}" href="/services/{p['slug']}/">
          <div class="profile-kicker"><span>{p['card']}</span><i class="circle-arrow">{arrow(True)}</i></div>
          <div class="profile-image">{art}</div><div class="profile-copy"><h3>{p['name']}</h3><p>{p['outcome']}</p></div>
        </a>''')
    return '<div class="cast-posters">'+''.join(posts)+'</div>'

def directory():
    filters=['All','Channels','Growth','Operations','Support']
    buttons=''.join(f'<button type="button" data-group="{f}" aria-pressed="{str(i==0).lower()}">{f}</button>' for i,f in enumerate(filters))
    rows=[]
    for i,(name,slug,desc) in enumerate(SUPPORTING,1):
        rows.append(f'''<li data-category="{PROFILES[slug][0]}"><a href="/services/{slug}/"><span class="row-num">{i:02d}</span><span class="service-name">{name}</span><span class="row-desc">{desc}</span>{arrow(True)}</a></li>''')
    return f'''<div class="directory"><div class="directory-tools"><div class="pills" aria-label="Filter supporting services">{buttons}</div><span class="result-count" aria-live="polite">{len(rows)} services</span></div>
    <ul class="directory-list">{''.join(rows)}</ul></div>'''

def coverage():
    items=[('24/7','Agent coverage'),('03','Main agents'),(str(len(SUPPORTING)).zfill(2),'Supporting services'),('06','Delivery steps')]
    return '<div class="coverage"><dl class="wrap">'+''.join(f'<div><dt>{name}</dt><dd>{n}</dd></div>' for n,name in items)+'</dl></div>'

def solution_wall():
    highlights=['documents','lead-generation','instagram-agent','facebook-agent','telegram-agent','integrations']
    services_list=''.join(link('/services/'+s+'/',AGENTS[s]+arrow(True)) for s in highlights)
    return f'''<section id="solutions" class="solutions ink"><div class="wrap">
    <div class="section-lead"><div>{eyebrow('Our three main services')}<h2>Meet the <em>agents.</em></h2></div><div class="lead-aside"><p>One answers the first question. One keeps the sale moving. One picks up the phone. Choose the job your team needs help with.</p>{link('/services/','Explore our services '+arrow(),'text-link')}</div></div>
    {posters()}<div class="supporting-preview"><div><h3>Supporting services</h3>{link('/services/#directory','View all '+arrow(),'text-link')}</div><div class="supporting-links">{services_list}</div></div></div></section>'''

def integrations():
    buttons=''.join(f'<button type="button" data-integration="{i}" aria-pressed="{str(i==0).lower()}">{v[0]}</button>' for i,v in enumerate(INTEGRATIONS))
    return f'''<section class="integrations" id="integrations"><div class="wrap">
    <div class="section-lead"><div>{eyebrow('Integrations')}<h2>Already part of<br><em>your setup.</em></h2></div>
    <div class="lead-aside"><p>Pick a tool to see one way an agent can receive an enquiry or hand work to your team.</p></div></div>
    <div class="patch-field"><canvas class="patch-lines" aria-hidden="true"></canvas>
    <div class="patch-select" aria-label="Choose an integration">{buttons}</div>
    <div class="jack-art">{img('patch','Two machined audio connectors with blue and cyan leads')}</div>
    <div class="patch-label" aria-live="polite"><small id="patch-kind">Messaging</small><h3 id="patch-name">WhatsApp</h3><dl>
    <div><dt>Input</dt><dd id="patch-input">Customer enquiry</dd></div><div><dt>Handoff</dt><dd id="patch-output">Support or sales queue</dd></div></dl></div></div>
    <script type="application/json" id="integration-data">{json.dumps(INTEGRATIONS)}</script></div></section>'''

def process():
    panels=''
    for i,(name,heading,body,result) in enumerate(DELIVERY):
        panels+=f'''<details class="process-item" {'open' if i==0 else ''}><summary><span class="step-number">{i+1:02d}</span><span>{name}</span><i class="plus"></i></summary>
        <div class="process-detail"><h3>{heading}</h3><p>{body}</p><div class="deliverable"><b>Deliverable</b>{result}</div></div></details>'''
    return f'''<section id="process" class="process light"><div class="wrap process-layout">
    <div class="process-heading">{eyebrow('The delivery process')}<h2>Built with<br><em>your team.</em></h2>
    <p>Six steps from the first conversation to a working agent. Open a step to see what you’ll review.</p>
    <div class="parts-photo">{img('assembly','Exploded view of the headset, separating the drivers from the headband')}</div></div>
    <div class="process-book">{panels}</div></div></section>'''

def why():
    items=[('Made for your industry','Give the agent your service catalogue, preferred tone and the questions customers really ask.'),('A controlled launch','Approve a working example and test the handoff before it goes live.'),('People on standby','Define when an agent should involve your team and who receives the request.'),('Outcomes you can track','Review leads, appointments and the enquiries that needed extra help.')]
    return f'''<section class="why"><div class="wrap why-layout"><div>{eyebrow('Why Chatversio')}<h2>Your business.<br><em>Your rules.</em></h2>{link('/about/','About the studio '+arrow(),'text-link')}</div>
    <div class="principles">{''.join(f'<article><h3>{n}</h3><p>{d}</p></article>' for n,d in items)}</div></div></section>'''

def questions(items=faq):
    rows=''.join(f'<details><summary>{q}<i class="plus"></i></summary><p>{a}</p></details>' for q,a in items)
    return f'''<section class="faq light"><div class="wrap faq-layout"><div>{eyebrow('FAQ')}<h2>Good<br><em>questions.</em></h2>{link('/contact/','Ask us something else '+arrow(),'text-link')}</div><div class="faqs">{rows}</div></div></section>'''

def closing():
    return f'''<section class="closing"><div class="wrap closing-inner"><div>{eyebrow('Start with one workflow')}<h2>Let’s <em>talk.</em></h2>
    <p>Bring us one call or message your team handles every day. We’ll explore what an agent could do with it.</p>
    <div class="actions">{cta(BOOK,'Book a discovery call','black')}{link('/contact/','Send an enquiry '+arrow(),'text-link')}</div></div>
    <div class="closing-art">{img('messenger','A blue messenger displaying hello')}</div></div></section>'''

def page_intro(k,title,copy,asset,tone,crumb=None,action=''):
    crumbs=link(crumb[0],crumb[1],'backlink') if crumb else ''
    return f'''<section class="page-intro {tone}"><div class="wrap intro-layout"><div class="intro-copy">{crumbs}{eyebrow(k)}<h1>{title}</h1><p>{copy}</p>{action}</div>
    <div class="intro-art">{img(asset,'','',True)}<i aria-hidden="true"></i></div></div></section>'''

def services_page():
    portraits=''.join(img('agent-'+p['id'],'','group-person',i==0,'(max-width:720px) 33vw, 17vw') for i,p in enumerate(PERSONAS))
    intro=f'''<section class="page-intro grape services-intro"><div class="wrap intro-layout"><div class="intro-copy">{eyebrow('Chatversio AI / Services')}<h1>Choose your<br><em>agent.</em></h1>
      <p>Start with Chat, Sales or Voice. Add the channels, documents and connected tools your team relies on.</p>{link('#directory','Browse supporting services ↓','text-link')}</div>
      <div class="group-portrait" role="img" aria-label="The illustrated Chat, Sales and Voice Agents">{portraits}</div></div></section>'''
    core='''<section class="solutions ink service-core"><div class="wrap">'''+eyebrow('Our three main services')+'<h2>Find your <em>starting point.</em></h2>'+posters()+'</div></section>'
    catalogue='<section id="directory" class="full-directory light"><div class="wrap">'+eyebrow('Service directory')+'<h2>Supporting <em>services.</em></h2>'+directory()+'</div></section>'
    return intro+core+catalogue+process()+questions([('Where should we start?','Choose one recurring enquiry where faster replies or better details would help your team.'),('What systems can you connect?','Discovery covers your existing calendar, CRM, phone or messaging tools and the access each integration requires.'),('Will our team need to code?','Your team can review conversations and manage handoffs in familiar tools.'),faq[4],('Can a person take over?','Yes. You choose the handoff point and how the right person receives the conversation.')])+closing()

def service_page(index,item):
    name,slug,desc=item
    category,art,trigger,reply,handoff,features=PROFILES[slug]
    colors={'Support':'grape','Growth':'clay','Operations':'inkblue','Channels':'grape','website-assistants':'grape','sales-automation':'clay','voice-assistants':'inkblue'}
    core=slug in PRIMARY
    action=cta('/contact/?solution='+slug,'Discuss this agent' if core else 'Discuss this service','white')
    if core:
        example={'website-assistants':'property','sales-automation':'business','voice-assistants':'service'}[slug]
        action+='<span class="example-link">'+link('/?example='+example+'#demo','Try a sample '+arrow(),'text-link')+'</span>'
    intro=page_intro('Our three agents' if core else 'Supporting services / '+category,name+'<em>.</em>',desc,art,colors[slug if core else category],('/services/','← All services'),action)
    chain=''.join(f'<article><span>{stage}</span><p>{s}</p></article>' for stage,s in [('Incoming',trigger),('What happens',reply),('Team handoff',handoff)])
    spec=''.join(f'<li>{text}</li>' for text in features)
    nxt=services[(index+1)%len(services)]
    return intro+f'''<section class="case-flow light"><div class="wrap">{eyebrow('Illustrative workflow')}<h2>In <em>practice.</em></h2><div class="case-chain">{chain}</div></div></section>
    <section class="specification"><div class="wrap faq-layout"><div>{eyebrow('Implementation')}<h2>What we<br><em>configure.</em></h2></div><div><ul class="spec-list">{spec}</ul>
    <p>During discovery, we agree which information the agent can use and who handles exceptions.</p>{link('/services/'+nxt[1]+'/','Next solution · '+nxt[0]+' '+arrow(),'text-link')}</div></div></section>'''+closing()

def about_page():
    intro=page_intro('About Chatversio','Behind<br><em>the line.</em>','We design AI agents for the people who answer phones, handle enquiries and keep the follow-up moving.','assembly','grape')
    values=[('Results you can check','Choose a measure with us, such as qualified leads or resolved support requests.'),('A fit for your business','Start with the conversations your customers actually bring to you.'),('A working partnership','Give your team a say in the scripts, integrations and handoffs.'),('An early working version','Review a small, working flow before expanding it across channels.'),('Reliable by design','Agree on access, fallback and review rules for each connection.'),('Decisions from real use','Look at where conversations stall and refine the next version together.')]
    principles='<section class="why"><div class="wrap why-layout"><div>'+eyebrow('Our core values')+'<h2>How we<br><em>work.</em></h2></div><div class="principles">'+''.join(f'<article><h3>{n}</h3><p>{d}</p></article>' for n,d in values)+'</div></div></section>'
    return intro+f'''<section class="story-note light"><div class="wrap editorial-note"><img class="about-wordmark original-wordmark" src="/media/chatversio-brand-original.jpeg" width="860" height="290" alt="Chatversio AI">{eyebrow('Our story')}<p>A phone rings while your team is already on a call. A buyer has one more question after closing. <em>That’s where our work begins.</em></p></div></section>
    <section class="about-pair"><div class="wrap"><article>{eyebrow('Our mission')}<h2>Give every enquiry<br>a useful next step.</h2><p>We build the steps that turn a conversation into an answer, an appointment or a handoff to the right person.</p></article><article>{eyebrow('Our vision')}<h2>Make a business<br>easier to reach.</h2><p>Customers should be able to speak, type or message in a familiar channel and keep their place in the conversation.</p></article></div></section>'''+principles+process()+closing()

def field(label,control,full=False):
    return f'<label class="{"full" if full else ""}"><span>{label}</span>{control}</label>'

def contact_page():
    options=lambda items: ''.join(f'<option value="{s}">{n}</option>' for n,s,*_ in items)
    listing='<optgroup label="Our three agents">'+options([x for x in services if x[1] in PRIMARY])+'</optgroup><optgroup label="Supporting services">'+options(SUPPORTING)+'</optgroup>'
    fields=field('Full name','<input name="name" autocomplete="name" required>')+field('Work email','<input name="email" autocomplete="email" type="email" required>')+field('Company · optional','<input name="business" autocomplete="organization">')+field('Phone · optional','<input name="phone" type="tel" autocomplete="tel">')+field('Website · optional','<input name="website" placeholder="yourcompany.com">')+field('Area of interest','<select name="solution"><option value="">Help me choose</option>'+listing+'</select>')+field('What would you like to automate?','<textarea required name="message" rows="4" placeholder="For example, we miss repair calls when our dispatchers are busy."></textarea>',True)
    return f'''<section class="request-page"><div class="wrap request-layout"><div class="request-copy">{eyebrow('Contact')}<h1>What’s<br><em>on your line?</em></h1><p>Tell us where the conversation starts and where you want it to go.</p>
    {cta('#brief-form','Send an enquiry','primary')}<p class="subtle">Prefer a conversation? {link(BOOK,'Book a 30-minute call.')}</p>{img('messenger','','request-art')}</div>
    <form class="brief-form" id="brief-form" method="post" action="/api/enquiries"><div class="form-head">{eyebrow('Project brief')}<h2>Plan your enquiry.</h2><p>Draft your brief, review the details, then send it to our team.</p></div>
    <input name="companyWebsite" value="" tabindex="-1" autocomplete="off" hidden><div class="fields">{fields}</div><button class="button black" type="submit">Prepare my brief {arrow()}</button>
    <div id="brief-review" hidden><h3>Your enquiry brief</h3><textarea aria-label="Prepared project brief" readonly rows="7"></textarea><div class="actions"><button class="button black copy-brief" type="button">Copy brief</button><button class="button black" id="send-enquiry" type="button">Send enquiry {arrow()}</button></div><p class="copy-status" role="status"></p><p class="copy-status" id="enquiry-status" role="status" aria-live="polite"></p></div>
    </form></div></section>'''+f'''<section class="case-flow light"><div class="wrap">{eyebrow('What happens next')}<h2>From enquiry <em>to plan.</em></h2><div class="case-chain"><article><span>Share</span><p>Bring a question or workflow your team handles regularly.</p></article><article><span>Discuss</span><p>We’ll talk through your goals and the systems involved.</p></article><article><span>Plan</span><p>Agree on a practical first agent and a way to evaluate it.</p></article></div></div></section>'''+questions([('What should I include?','A typical enquiry and the tools your team uses are enough to begin.'),('When should I expect a reply?','The team aims to reply within 24 hours.'),('Can I book directly?','Yes. Open the booking page to choose an available time with the CEO.')])

def booking_page():
    fields=field('Full name','<input name="name" autocomplete="name" required>')+field('Email address','<input name="email" type="email" autocomplete="email" required>')+field('Preferred date','<input name="date" type="date" required>')+field('Preferred time · local','<input name="time" type="time" required>')+field('Meeting platform','<select name="platform"><option>Google Meet</option><option>Zoom</option></select>',True)
    return f'''<section class="booking-page"><div class="wrap booking-layout"><div class="booking-copy">{eyebrow('Discovery call')}<h1>Let’s find your<br><em>first workflow.</em></h1>
    <p>Spend 30 minutes with our CEO. Bring one customer enquiry and leave with a clear idea of what to automate first.</p>
    <a class="button primary" href="#booking-form" data-calendar-link>Request a time {arrow(True)}</a>{link('/contact/','Ask a question first '+arrow(),'text-link')}</div>
    <div class="booking-pass"><div class="pass-top">{eyebrow('Session details')}<i class="spark"></i></div><div class="duration">30<span>min</span></div><h2>Discovery call</h2><dl><div><dt>With</dt><dd>Chatversio CEO</dd></div><div><dt>Where</dt><dd>Google Meet or Zoom</dd></div><div><dt>Focus</dt><dd>Your first agent workflow</dd></div></dl><div class="ticket-cut" aria-hidden="true"></div><div class="barcode" aria-hidden="true"></div></div></div></section>
    <section class="booking-plan light"><div class="wrap faq-layout"><div>{eyebrow('Before the call')}<h2>Plan the<br><em>session.</em></h2><p>Share your preferred time below. Our team will confirm availability and send your meeting details.</p></div>
    <div><details class="booking-preview"><summary>Preview meeting preferences<i class="plus"></i></summary><form id="booking-form" method="post" action="/api/booking-requests"><input name="companyWebsite" value="" tabindex="-1" autocomplete="off" hidden><div class="fields">{fields}</div>
    <button type="submit" class="button black">Review preferences {arrow()}</button><p class="booking-result" role="status"></p><p class="subtle" id="booking-timezone"></p><button class="button black" id="send-booking" type="button" hidden>Send meeting request {arrow()}</button><p class="copy-status" id="booking-status" role="status" aria-live="polite"></p><a class="text-link" href="#booking-form" data-calendar-link>Request a time {arrow(True)}</a></form></details>
    <ol class="booking-steps"><li>Choose a preferred date and time.</li><li>Add your details and meeting platform.</li><li>Wait for our team to confirm the time.</li><li>Join the conversation.</li></ol></div></div></section>'''+questions([('How long is the session?','We set aside 30 minutes for the discovery call.'),('Who will I speak with?','The session is directly with Chatversio’s CEO.'),('What should I bring?','One customer enquiry or repetitive task is a useful starting point.'),('What happens after the call?','Together you’ll identify a suitable use case, key dependencies and a realistic next step.')])

def build():
    (OUT/'media').mkdir(exist_ok=True,parents=True)
    page('/','Chat Agent, Sales Agent & Voice Agent','Meet the three Chatversio AI agents for conversations, sales follow-up and calls. Explore the systems and integrations that support them.',hero()+channel_band()+solution_wall()+story()+coverage()+integrations()+process()+why()+questions()+closing())
    page('/services/','Agent solutions','Explore Chat, Sales and Voice Agents, plus document processing, social channels, lead generation and third-party integrations.',services_page())
    for i,s in enumerate(services):
        page('/services/'+s[1]+'/',s[0],s[2],service_page(i,s))
    page('/about/','About the studio','Meet the thinking behind Chatversio’s conversation systems.',about_page())
    page('/contact/','Tell us about your project','Discuss your customer enquiries and automation needs.',contact_page())
    page(BOOK,'Book a discovery call','Choose a live time for a 30-minute discovery call with Chatversio.',booking_page())
if __name__=='__main__':
    build()
