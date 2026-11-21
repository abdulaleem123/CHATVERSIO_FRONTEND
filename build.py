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
    return '<img src="/media/chatversio-logo-on-dark.png" width="798" height="165" alt="Chatversio AI" class="wordmark original-wordmark">'

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
    main_links=[('/','Home','home'),('/about/','About','about'),('/services/','Solutions','services'),('/contact/','Contact','contact'),(BOOK,'Book a Call','calendar')]
    # The footer lists every service shown in the services-page directory (same names, same order).
    service_links=[(slug,name,slug) for name,slug,*_ in SUPPORTING]
    group=lambda pairs: ''.join('<li>'+link(url,icon(symbol)+'<span>'+text+'</span>')+'</li>' for url,text,symbol in pairs)
    social_urls={'Facebook':'https://www.facebook.com/profile.php?id=61595764508818','Instagram':'https://www.instagram.com/chatversio','X':'https://x.com/chatversio','LinkedIn':'https://www.linkedin.com/company/chatversio-ai/'}
    social_colors={'Facebook':'#1877f2','Instagram':'#e4405f','X':'#000000','LinkedIn':'#0a66c2'}
    socials=''.join(f'<a href="{escape(url,quote=True)}" aria-label="{name}" title="{name}" style="--social-brand:{social_colors[name]}" target="_blank" rel="noopener noreferrer">{icon(name)}</a>' for name,url in social_urls.items())
    footer_logo='<img src="/media/chatversio-logo-on-dark.png" width="798" height="165" alt="Chatversio AI">'
    return f'''<footer class="footer" id="footer"><link rel="stylesheet" href="/footer.css?v=18"><div class="footer-glow" aria-hidden="true"></div><div class="wrap">
      <div class="footer-grid"><div class="footer-brand">{link('/',footer_logo,'footer-logo')}
        <p>Turn Conversations Into Conversions. AI-powered Agents that sell, support, and scale your business 24/7.</p>
        <div class="footer-socials" aria-label="Follow Chatversio AI">{socials}</div></div>
        <nav class="footer-nav" aria-labelledby="footer-quick-title"><h2 id="footer-quick-title">Quick Links</h2><ul>{group(main_links)}</ul></nav>
        <nav class="footer-nav footer-services" aria-labelledby="footer-services-title"><h2 id="footer-services-title">Solutions</h2><ul>{group([('/services/'+slug+'/',text,symbol) for slug,text,symbol in service_links])}</ul></nav>
      </div>
      <div class="footer-banner"><p class="footer-signature" aria-hidden="true">Chatversio AI</p></div>
      <div class="footer-bottom"><p>© 2026 Chatversio AI. All rights reserved.</p><p>Built with intelligence. Powered by AI.</p>
        <div class="footer-legal">{link('/privacy-policy/','Privacy Policy')}<span aria-hidden="true">·</span>{link('/terms/','Terms of Service')}</div></div>
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
    <link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" href="/media/favicon-48.png" sizes="48x48"><link rel="icon" type="image/png" href="/media/favicon-96.png" sizes="96x96"><link rel="icon" type="image/png" href="/media/favicon-192.png" sizes="192x192"><link rel="icon" type="image/png" href="/media/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/media/apple-touch-icon.png"><link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
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
    return intro+f'''<section class="story-note light"><div class="wrap editorial-note"><img class="about-wordmark original-wordmark" src="/media/chatversio-logo-transparent.png" width="798" height="165" alt="Chatversio AI">{eyebrow('Our story')}<p>A phone rings while your team is already on a call. A buyer has one more question after closing. <em>That’s where our work begins.</em></p></div></section>
    <section class="about-pair"><div class="wrap"><article>{eyebrow('Our mission')}<h2>Give every enquiry<br>a useful next step.</h2><p>We build the steps that turn a conversation into an answer, an appointment or a handoff to the right person.</p></article><article>{eyebrow('Our vision')}<h2>Make a business<br>easier to reach.</h2><p>Customers should be able to speak, type or message in a familiar channel and keep their place in the conversation.</p></article></div></section>'''+principles+process()+closing()

def field(label,control,full=False):
    return f'<label class="{"full" if full else ""}"><span>{label}</span>{control}</label>'

FORM_ICONS=json.loads((ROOT/'art/footer-icons.json').read_text())
def ficon(name,label,control,full=False):
    """Labelled form control with a leading icon, as on the original contact and schedule forms."""
    return f'<label class="{"full" if full else ""}"><span>{label}</span><div class="input-wrap">{FORM_ICONS[name] if name else ""}{control}</div></label>'

PRIVACY_NOTE='We use your details only to respond to your request. See our <a href="/privacy-policy/">Privacy Policy</a>.'

def contact_page():
    topics=[('voice-agent','AI voice agent / receptionist'),('lead-follow-up','Lead follow-up and CRM automation'),('chatbot-crm','Website chatbot with CRM'),('custom-ai','Custom AI development'),('not-sure','Not sure yet')]
    select='<select name="topic"><option value="">Select an option (optional)</option>'+''.join(f'<option value="{v}">{t}</option>' for v,t in topics)+'</select>'
    fields=(ficon('f_user','Full Name *','<input name="name" type="text" placeholder="John Doe" autocomplete="name" required>')
        +ficon('f_mail','Email Address *','<input name="email" type="email" placeholder="john@company.com" autocomplete="email" required>')
        +ficon('f_phone','Phone Number','<input name="phone" type="tel" placeholder="+1 234 567 8900" autocomplete="tel">')
        +ficon('f_building','Business Name','<input name="business" type="text" placeholder="Your Company" autocomplete="organization">')
        +ficon('f_wand','What do you want to automate?',select)
        +ficon('f_globe','Website','<input name="companyWebsite" type="text" placeholder="yourcompany.com (optional)" maxlength="200">')
        +'<label class="full"><span>Message *</span><textarea name="message" rows="5" placeholder="Tell us about your business, goals, and what kind of Agents you need…" required></textarea></label>')
    return f'''<section class="request-page"><div class="wrap request-layout"><div class="request-copy">{eyebrow('Contact')}<h1>What’s<br><em>on your line?</em></h1><p>Tell us where the conversation starts and where you want it to go.</p>
    {cta('#brief-form','Send an enquiry','primary')}<p class="subtle">Prefer a conversation? {link(BOOK,'Book a 30-minute call.')}</p>{img('messenger','','request-art')}</div>
    <div class="brief-form" id="contact-card"><div class="form-success" id="contact-success" hidden><div class="success-icon">{FORM_ICONS['f_check']}</div><h3>Message Sent!</h3><p>Thanks for reaching out. Our team will get back to you within 24 hours with a custom Agents strategy for your business.</p><button class="button black" type="button" id="contact-again">Send Another Message</button></div>
    <form id="brief-form" method="post" action="/api/contact"><div class="form-head"><h2>Send Us a Message</h2><p>Fill in the details below and we'll get back to you shortly.</p></div>
    <div class="hp-field" aria-hidden="true"><label>Leave this field empty<input type="text" name="hp" tabindex="-1" autocomplete="off"></label></div><div class="fields">{fields}</div>
    <p class="form-error" role="alert" hidden></p>
    <button class="button black" type="submit" id="send-enquiry">Send Message {FORM_ICONS['f_send']}</button>
    <p class="form-note">{PRIVACY_NOTE}</p></form></div></div></section>'''+f'''<section class="case-flow light"><div class="wrap">{eyebrow('What happens next')}<h2>From enquiry <em>to plan.</em></h2><div class="case-chain"><article><span>Share</span><p>Bring a question or workflow your team handles regularly.</p></article><article><span>Discuss</span><p>We’ll talk through your goals and the systems involved.</p></article><article><span>Plan</span><p>Agree on a practical first agent and a way to evaluate it.</p></article></div></div></section>'''+questions([('What should I include?','A typical enquiry and the tools your team uses are enough to begin.'),('When should I expect a reply?','The team aims to reply within 24 hours.'),('Can I book directly?','Yes. Open the booking page to choose an available time with the CEO.')])

def booking_page():
    platforms=''.join(f'<button type="button" class="platform-card" data-platform="{v}" aria-pressed="{"true" if v=="google-meet" else "false"}">{mark}<span>{t}</span></button>' for v,t,mark in [('google-meet','Google Meet','<b class="g-mark" aria-hidden="true">G</b>'),('zoom','Zoom',FORM_ICONS['f_video'])])
    fields=(ficon('f_user','Full Name *','<input name="name" type="text" placeholder="John Doe" autocomplete="name" required>')
        +ficon('f_mail','Email Address *','<input name="email" type="email" placeholder="john@company.com" autocomplete="email" required>')
        +ficon('f_calendar','Select Date *','<input name="date" type="date" required>')
        +ficon('f_clock','Select Time *','<input name="time" type="time" required>')
        +f'<div class="full platform-group" role="group" aria-label="Preferred Platform"><span>Preferred Platform *</span><div class="platform-grid">{platforms}</div><input type="hidden" name="platform" value="google-meet"></div>')
    return f'''<section class="booking-page"><div class="wrap booking-layout"><div class="booking-copy">{eyebrow('Discovery call')}<h1>Let’s find your<br><em>first workflow.</em></h1>
    <p>Spend 30 minutes with our CEO. Bring one customer enquiry and leave with a clear idea of what to automate first.</p>
    <a class="button primary" href="#booking-form">Reserve your slot {arrow(True)}</a>{link('/contact/','Ask a question first '+arrow(),'text-link')}</div>
    <div class="booking-pass"><div class="pass-top">{eyebrow('Session details')}<i class="spark"></i></div><div class="duration">30<span>min</span></div><h2>Discovery call</h2><dl><div><dt>With</dt><dd>Chatversio CEO</dd></div><div><dt>Where</dt><dd>Google Meet or Zoom</dd></div><div><dt>Focus</dt><dd>Your first agent workflow</dd></div></dl><div class="ticket-cut" aria-hidden="true"></div><div class="barcode" aria-hidden="true"></div></div></div></section>
    <section class="booking-plan light"><div class="wrap faq-layout"><div>{eyebrow('Before the call')}<h2>Plan the<br><em>session.</em></h2><p>Pick a time that works for you. We'll send a confirmation with everything you need.</p></div>
    <div><div class="booking-form-card" id="booking-card"><div class="form-success" id="booking-success" hidden><div class="success-icon">{FORM_ICONS['f_cal_check']}</div><h3>You're Booked!</h3><p>Your meeting has been scheduled. Check your inbox for a calendar invite and all the details you need to join the call.</p><div class="success-actions"><a class="button black" id="booking-mail" href="mailto:">{FORM_ICONS['f_mail']} Check Your Email</a><a class="button primary" href="/">{FORM_ICONS['f_house']} Back to Home</a></div></div>
    <div class="form-success" id="booking-already" hidden><div class="success-icon warn">{FORM_ICONS['f_cal_x']}</div><h3>Already Scheduled</h3><p>You've already booked a session with us. Check your email for your meeting details and join link.</p></div>
    <form id="booking-form" method="post" action="/api/schedule"><div class="form-head"><h3>Reserve Your Slot</h3><p>30-minute call. Takes less than 2 minutes to confirm.</p></div><div class="fields">{fields}</div>
    <p class="form-error" role="alert" hidden></p>
    <button type="submit" class="button black" id="send-booking">{FORM_ICONS['f_cal_check']} Confirm My Meeting</button>
    <p class="form-note">{FORM_ICONS['f_shield']} We use your details only to arrange this call. See our <a href="/privacy-policy/">Privacy Policy</a>.</p></form></div>
    <ol class="booking-steps"><li><strong>Pick a Date &amp; Time.</strong> Choose any available slot that fits your schedule.</li><li><strong>Fill the Form.</strong> Share a few details so we come fully prepared for you.</li><li><strong>Get Confirmation.</strong> A calendar invite and reminder land in your inbox instantly.</li><li><strong>Join the Call.</strong> Meet us on Google Meet or Zoom, your choice.</li></ol></div></div></section>'''+questions([('How long is the session?','We set aside 30 minutes for the discovery call.'),('Who will I speak with?','The session is directly with Chatversio’s CEO.'),('What should I bring?','One customer enquiry or repetitive task is a useful starting point.'),('What happens after the call?','Together you’ll identify a suitable use case, key dependencies and a realistic next step.')])

UPDATED='15 November 2026'
def legal_page(title, lead, sections):
    toc=''.join(f'<li><a href="#s{i}">{h}</a></li>' for i,(h,_) in enumerate(sections,1))
    body=''.join(f'<section id="s{i}"><h2>{h}</h2>{b}</section>' for i,(h,b) in enumerate(sections,1))
    return f'''<section class="legal-hero ink"><div class="wrap">{eyebrow('Legal')}<h1>{title}</h1><p>{lead}</p><p class="legal-meta">Last updated {UPDATED}</p></div></section>
    <section class="legal light"><div class="wrap legal-layout"><nav class="legal-toc" aria-label="On this page"><h2>On this page</h2><ol>{toc}</ol></nav><div class="legal-body">{body}</div></div></section>'''

def privacy_page():
    S=[
    ('Who we are','<p>Chatversio AI (“Chatversio”, “we”, “us”) designs and builds AI agents for chat, sales follow-up and voice, along with document processing, social messaging channels, lead generation and integrations. This policy explains what personal information we collect through this website and how we use it. If you are a customer’s end user talking to an agent we built for that customer, the customer’s own privacy policy also applies.</p>'),
    ('Information we collect','<p>We collect only what you choose to send us:</p><ul><li><strong>Enquiry form:</strong> your name, work email, and optionally your company, phone number, website, area of interest and the message you write.</li><li><strong>Discovery call requests:</strong> your name, email, preferred date and time, your time zone and your preferred meeting platform (Google Meet or Zoom).</li><li><strong>Technical data:</strong> like most websites, our servers may process your IP address, browser type and the pages requested so that the site can be delivered securely and kept reliable.</li></ul><p>This site does not use advertising cookies. It stores one small preference in your browser (<code>chatversio-motion</code>) to remember whether you paused animations.</p>'),
    ('How we use your information','<ul><li>To reply to your enquiry and discuss whether an agent suits your business.</li><li>To confirm, reschedule or follow up on a discovery call. A request is treated as pending until our team confirms it.</li><li>To keep the website secure and prevent spam and abuse.</li><li>To improve our website and the way we explain our services.</li></ul><p>We do not sell your personal information.</p>'),
    ('Agents, conversations and customer data','<p>When we build and run agents for a business, the conversations, contact details and documents an agent handles are processed on that business’s behalf and under its instructions. During discovery we agree which information an agent may use, where it is stored and when it hands over to a person. Please contact the business you are speaking with about their use of your data.</p>'),
    ('Sharing and service providers','<p>We share information only with people and providers who help us operate: for example hosting, email and calendar tools, a CRM, and meeting platforms such as Google Meet or Zoom. They may only use it to provide their service to us. We may also disclose information if the law requires it or to protect our rights and users.</p>'),
    ('Retention','<p>We keep enquiries and meeting requests for as long as needed to respond and to maintain a reasonable record of our discussions, then delete or anonymise them. You can ask us to delete your information sooner.</p>'),
    ('Security','<p>Enquiries are stored in a private location that is not publicly accessible, and access is limited to people who need it. No online service is completely secure, so please avoid sending passwords, payment card numbers or other highly sensitive information through the website forms.</p>'),
    ('Your choices and rights','<p>Depending on where you live, you may have the right to access, correct, delete or export your personal information, to object to or restrict certain processing, and to withdraw consent. To make a request, use our <a href="/contact/">contact form</a> and mention “privacy request”. We will respond within a reasonable time and may need to verify your identity first.</p>'),
    ('Children','<p>Our website and services are intended for businesses and are not directed at children. We do not knowingly collect information from children.</p>'),
    ('Changes to this policy','<p>We may update this policy as the website or our services change. The date at the top shows when it was last revised.</p>'),
    ('Contact us','<p>Questions about this policy? Reach us through the <a href="/contact/">contact page</a>.</p>'),
    ]
    return legal_page('Privacy <em>Policy.</em>','How Chatversio AI collects, uses and protects the information you share with us.',S)

def terms_page():
    S=[
    ('Acceptance of these terms','<p>By using the Chatversio AI website you agree to these Terms of Service. If you do not agree, please do not use the site. Work we carry out for a customer is governed by a separate written agreement, which takes priority over these terms where they differ.</p>'),
    ('What this website provides','<p>This website describes Chatversio’s AI agent services (including Chat, Sales and Voice Agents, document processing, social channel agents, lead generation, integrations and custom platforms) and lets you contact us or request a discovery call. Descriptions and demonstrations are for information and illustrate what is possible; they are not an offer or a guarantee of specific results.</p>'),
    ('Enquiries and discovery calls','<p>Sending an enquiry or call request does not create a contract. A requested call time is <strong>pending</strong> until our team confirms it, and we may propose a different time. Proposals and pricing are provided separately and are only binding once agreed in writing.</p>'),
    ('Acceptable use','<p>You agree not to:</p><ul><li>use the site unlawfully or to send spam, malware or misleading information;</li><li>attempt to gain unauthorised access to the site, our servers or other users’ data;</li><li>interfere with the site’s operation, or use automated tools to overload it;</li><li>copy, scrape or resell site content other than as these terms or the law allow.</li></ul>'),
    ('Information you send us','<p>You are responsible for the accuracy of what you submit and for having the right to share it. Please do not submit passwords, payment card details or highly sensitive personal information. We handle submitted details as described in our <a href="/privacy-policy/">Privacy Policy</a>.</p>'),
    ('AI-generated content','<p>AI agents generate responses automatically and can make mistakes. Examples and demo conversations on this site are illustrative. Anything an agent says should be checked before it is relied on for legal, financial, medical or other important decisions.</p>'),
    ('Intellectual property','<p>The Chatversio name, logo, design, text, illustrations, 3D models, audio and software on this site belong to Chatversio AI or its licensors and are protected by intellectual property laws. Third-party components remain under their own licences. You may view the site and share links to it, but may not reproduce or use our materials commercially without permission.</p>'),
    ('Third-party services and links','<p>The site may link to or rely on third-party services such as social networks, meeting platforms and calendar tools. We do not control them and are not responsible for their content or practices.</p>'),
    ('Disclaimers','<p>The website is provided “as is” and “as available”. To the fullest extent permitted by law, we disclaim all warranties, express or implied, including fitness for a particular purpose and uninterrupted or error-free operation.</p>'),
    ('Limitation of liability','<p>To the fullest extent permitted by law, Chatversio AI is not liable for indirect, incidental, special or consequential damages, or for lost profits or data, arising from your use of the website. Nothing in these terms limits liability that cannot be limited by law.</p>'),
    ('Changes and termination','<p>We may change these terms or the website at any time; continued use after a change means you accept the updated terms. We may suspend access to the site for anyone who breaches these terms.</p>'),
    ('Governing law','<p>These terms are governed by the laws that apply where Chatversio AI is established, and disputes will be handled by the courts of that jurisdiction, unless mandatory consumer law says otherwise.</p>'),
    ('Contact us','<p>Questions about these terms? Reach us through the <a href="/contact/">contact page</a>.</p>'),
    ]
    return legal_page('Terms of <em>Service.</em>','The rules for using the Chatversio AI website and requesting our services.',S)

def build():
    (OUT/'media').mkdir(exist_ok=True,parents=True)
    page('/','Chat Agent, Sales Agent & Voice Agent','Meet the three Chatversio AI agents for conversations, sales follow-up and calls. Explore the systems and integrations that support them.',hero()+channel_band()+solution_wall()+story()+coverage()+integrations()+process()+why()+questions()+closing())
    page('/services/','Agent solutions','Explore Chat, Sales and Voice Agents, plus document processing, social channels, lead generation and third-party integrations.',services_page())
    for i,s in enumerate(services):
        page('/services/'+s[1]+'/',s[0],s[2],service_page(i,s))
    page('/about/','About the studio','Meet the thinking behind Chatversio’s conversation systems.',about_page())
    page('/contact/','Tell us about your project','Discuss your customer enquiries and automation needs.',contact_page())
    page('/privacy-policy/','Privacy Policy','How Chatversio AI collects, uses and protects the information you share with us.',privacy_page())
    page('/terms/','Terms of Service','The terms for using the Chatversio AI website and requesting our services.',terms_page())
    page(BOOK,'Book a discovery call','Choose a live time for a 30-minute discovery call with Chatversio.',booking_page())
if __name__=='__main__':
    build()
