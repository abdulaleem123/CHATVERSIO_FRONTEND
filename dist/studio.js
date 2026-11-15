/* Chatversio's interface is usable without accounts, a CMS, or an external 3D player. */
(() => {
  'use strict';
  const one = (selector, root = document) => root.querySelector(selector);
  const all = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const body = document.body;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = window.matchMedia('(max-width: 720px)');
  const lightConnection = navigator.connection?.saveData === true;
  let chosenMotion = null;
  try { chosenMotion = localStorage.getItem('chatversio-motion'); } catch { /* Storage is optional. */ }
  let moving = false;

  function syncMotion() {
    moving = chosenMotion === 'off' ? false : !reduce.matches;
    body.dataset.motion = moving ? 'on' : 'off';
    all('.motion').forEach(button => {
      button.setAttribute('aria-pressed', String(moving));
      button.setAttribute('aria-label', moving ? 'Pause ambient motion' : 'Enable ambient motion');
      one('span', button).textContent = moving ? 'Motion on' : 'Motion off';
      if (reduce.matches) {
        button.setAttribute('aria-label', 'Ambient motion follows your reduced motion setting');
        button.disabled = true;
      } else {
        button.disabled = false;
      }
    });
    document.dispatchEvent(new Event('ambientchange'));
  }
  all('.motion').forEach(button => button.addEventListener('click', () => {
    chosenMotion = moving ? 'off' : 'on';
    try { localStorage.setItem('chatversio-motion', chosenMotion); } catch { /* Session still works. */ }
    syncMotion();
  }));
  reduce.addEventListener('change', syncMotion);
  syncMotion();

  const menu = one('.menu-toggle');
  function toggleMenu(open, returnFocus = false) {
    body.classList.toggle('menu-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    if (returnFocus) menu.focus();
  }
  menu.addEventListener('click', () => toggleMenu(!body.classList.contains('menu-open')));
  all('#main-nav a').forEach(a => a.addEventListener('click', () => toggleMenu(false)));
  document.addEventListener('click', event => {
    if (body.classList.contains('menu-open') && !event.target.closest('.masthead')) toggleMenu(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && body.classList.contains('menu-open')) toggleMenu(false, true);
  });
  mobile.addEventListener('change', () => toggleMenu(false));
  let scrollQueued = false;
  function readPosition() {
    scrollQueued = false;
    body.classList.toggle('scrolled', window.scrollY > 20);
    if(one('.hero'))document.documentElement.style.setProperty('--hero-depth',String(Math.min(1,window.scrollY/Math.max(1,innerHeight*.78))));
    const travel = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    document.documentElement.style.setProperty('--read', String(Math.max(0,Math.min(1,window.scrollY / travel))));
  }
  window.addEventListener('scroll', () => {
    if (!scrollQueued) { scrollQueued = true; requestAnimationFrame(readPosition); }
  }, { passive: true });
  readPosition();

  function setupWavefield(canvas) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let w = 0, h = 0, running = true, raf = 0, previous = 0, phase = 0;
    const hero = canvas.closest('.hero');
    function paint(t) {
      raf = 0;
      if (!running || document.hidden) { previous=0; return; }
      if (moving && previous && t - previous < 48) { raf=requestAnimationFrame(paint); return; }
      if (moving && previous) phase += Math.min(t-previous,100)*.00022;
      previous=t;
      ctx.clearRect(0,0,w,h);
      // A perspective field of signal lines. Only the area beside the copy catches the light.
      const gradient = ctx.createLinearGradient(0,0,w,0);
      gradient.addColorStop(0,'rgba(42,117,246,0)');
      gradient.addColorStop(.27,'rgba(42,117,246,.04)');
      gradient.addColorStop(.55,'rgba(63,157,255,.44)');
      gradient.addColorStop(.82,'rgba(74,205,255,.59)');
      gradient.addColorStop(1,'rgba(86,217,255,.37)');
      ctx.strokeStyle=gradient;
      const narrow = w<721;
      const count=narrow?23:36;
      const baseline = narrow?.86:.79;
      for(let j=0;j<count;j++) {
        const depth=j/(count-1);
        ctx.beginPath();
        ctx.lineWidth=.60+.25*depth;ctx.globalAlpha=.36+.39*depth;
        for(let i=0;i<=124;i++){
          const u=i/124, x=w*u;
          const wave=Math.sin(12.6*u-1.8+depth*1.9+phase*.48)*.050+
            Math.cos(u*20+depth*2.6-phase*.8)*.018;
          const envelope=.17+.86*Math.exp(-((u-.83)**2)/.17);
          const y=h*(baseline+(depth-.5)*.076+wave*envelope
            -.14*Math.exp(-((u-.84-depth*.06)**2)/.013)
            +.075*Math.exp(-((u-.59+depth*.03)**2)/.016));
          if(!i)ctx.moveTo(x,y);else ctx.lineTo(x,y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha=1;
      if(moving)raf=requestAnimationFrame(paint);
    }
    function wake(){
      cancelAnimationFrame(raf);previous=0;
      if(running && !document.hidden)raf=requestAnimationFrame(paint);
    }
    new ResizeObserver(() => {
      const rect=hero.getBoundingClientRect();w=rect.width;h=rect.height;
      const dpr=Math.min(devicePixelRatio||1,1.5);
      canvas.width=Math.max(1,Math.round(w*dpr));canvas.height=Math.max(1,Math.round(h*dpr));
      ctx.setTransform(dpr,0,0,dpr,0,0);wake();
    }).observe(hero);
    new IntersectionObserver(([entry])=>{running=entry.isIntersecting;wake();}).observe(hero);
    document.addEventListener('ambientchange',wake);
    document.addEventListener('visibilitychange',wake);
  }

  function setupCast(stage) {
    const buttons=all('[data-view]',stage);
    const scenes=all('[data-scene-id]',stage);
    function selectView(key) {
      stage.dataset.current=key;
      scenes.forEach(scene=>{scene.hidden=scene.dataset.sceneId!==key;});
      buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===key)));
      stage.dispatchEvent(new Event('viewchange'));
    }
    buttons.forEach(button=>button.addEventListener('click',()=>selectView(button.dataset.view)));
    const canTilt=window.matchMedia('(pointer:fine)');
    let tiltFrame=0,tiltX=0,tiltY=0;
    function paintTilt(){
      tiltFrame=0;
      stage.style.setProperty('--cast-x',tiltX.toFixed(2)+'px');
      stage.style.setProperty('--cast-y',tiltY.toFixed(2)+'px');
    }
    function resetTilt(){
      tiltX=0;tiltY=0;cancelAnimationFrame(tiltFrame);paintTilt();
    }
    stage.addEventListener('pointermove',event=>{
      if(!moving || !canTilt.matches || stage.dataset.current==='gear' || stage.dataset.webgl==='ready')return;
      const bounds=stage.getBoundingClientRect();
      tiltX=((event.clientX-bounds.left)/bounds.width-.5)*13;
      tiltY=((event.clientY-bounds.top)/bounds.height-.5)*7;
      if(!tiltFrame)tiltFrame=requestAnimationFrame(paintTilt);
    },{passive:true});
    stage.addEventListener('pointerleave',resetTilt);
    stage.addEventListener('viewchange',resetTilt);
    document.addEventListener('ambientchange',resetTilt);
  }

  function setupTurntable(table) {
    const stage=table.closest('.soundstage');
    const frame=one('.turn-frame',table), loop=one('.hero-loop',table);
    const total=40, cache=new Map();
    let index=0, isManual=false, visible=false, activeDrag=null, failedLoop=false, alphaChecked=false;
    function getFrame(i) {
      const n=(i%total+total)%total;
      if(cache.has(n))return cache.get(n);
      const image=new Image();
      const promise=new Promise((resolve,reject)=>{
        image.onload=()=>resolve(image);
        image.onerror=()=>{cache.delete(n);reject(new Error('Angle unavailable'));};
      });
      cache.set(n,promise);
      image.src='/media/spin/spin-'+String(n).padStart(2,'0')+'.webp';
      return promise;
    }
    function stopLoop() { loop.pause(); table.classList.remove('playing'); }
    function syncLoop() {
      if(stage.dataset.webgl==='ready' || stage.dataset.current!=='gear' || isManual || !visible || !moving || document.hidden || lightConnection || mobile.matches || failedLoop || !loop.canPlayType('video/webm; codecs="vp9"') || body.classList.contains('film-open')) {
        stopLoop();return;
      }
      if(!loop.hasAttribute('src'))loop.src=loop.dataset.src;
      loop.play().catch(()=>table.classList.remove('playing'));
    }
    loop.addEventListener('playing',()=>{
      if(stage.dataset.webgl==='ready' || stage.dataset.current!=='gear' || isManual || !moving || document.hidden){stopLoop();return;}
      if(!alphaChecked){
        // Browsers that decode VP9 without alpha retain the transparent still.
        const test=document.createElement('canvas');test.width=test.height=2;
        const context=test.getContext('2d',{willReadFrequently:true});
        if(context){
          context.drawImage(loop,0,0,2,2,0,0,2,2);
          if(context.getImageData(0,0,1,1).data[3]>100){failedLoop=true;stopLoop();return;}
        }
        alphaChecked=true;
      }
      table.classList.add('playing');
    });
    loop.addEventListener('error',()=>{failedLoop=true;stopLoop();});
    function showAngle(next) {
      isManual=true;stopLoop();index=(next%total+total)%total;
      if(stage.dataset.webgl==='ready'){
        stage.dispatchEvent(new CustomEvent('rotateproduct',{detail:{angle:index/total*Math.PI*2}}));
        return;
      }
      const requested=index;
      getFrame(requested).then(image=>{
        if(index!==requested)return;
        frame.src=image.src;frame.hidden=false;table.classList.add('turned');
        for(const adjacent of [requested+1,requested-1])getFrame(adjacent).catch(()=>{});
      }).catch(()=>{
        frame.hidden=true;table.classList.remove('turned');
      });
    }
    all('.turn-arrow',stage).forEach((btn,i)=>btn.addEventListener('click',()=>showAngle(index+(i?2:-2))));
    table.addEventListener('keydown',event=>{
      if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
        event.preventDefault();showAngle(index+(event.key==='ArrowRight'?1:-1));
      }
      if(event.key==='Home'){event.preventDefault();showAngle(0);}
    });
    table.addEventListener('pointerdown',event=>{
      if(event.button!==0)return;
      activeDrag={id:event.pointerId,x:event.clientX,y:event.clientY,start:index,dragged:false};
    });
    table.addEventListener('pointermove',event=>{
      if(!activeDrag||event.pointerId!==activeDrag.id)return;
      const dx=event.clientX-activeDrag.x,dy=event.clientY-activeDrag.y;
      if(!activeDrag.dragged){
        if(Math.abs(dy)>12 && Math.abs(dy)>Math.abs(dx)){activeDrag=null;return;}
        if(Math.abs(dx)<5)return;
        activeDrag.dragged=true;table.setPointerCapture(event.pointerId);table.classList.add('dragging');
      }
      const step=Math.round(dx/Math.max(5,table.clientWidth/60));
      const next=(activeDrag.start+step+total*4)%total;
      if(!isManual||next!==index)showAngle(next);
    });
    function release(){activeDrag=null;table.classList.remove('dragging');}
    table.addEventListener('pointerup',release);table.addEventListener('pointercancel',release);table.addEventListener('lostpointercapture',release);
    table.addEventListener('pointerleave',()=>{if(activeDrag&&!activeDrag.dragged)release();});
    new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;syncLoop();},{threshold:.01}).observe(stage);
    document.addEventListener('ambientchange',syncLoop);
    document.addEventListener('visibilitychange',syncLoop);
    mobile.addEventListener('change',syncLoop);
    stage.addEventListener('viewchange',syncLoop);
    document.addEventListener('filmstate',syncLoop);
  }

  function setupReel(dialog) {
    const trigger=one('.film-trigger'),video=one('video',dialog);
    const sound=one('.film-sound',dialog);
    function soundLabel(){
      const audible=!video.muted && video.volume>0;
      sound.textContent=audible?'Sound on':'Sound off';
      sound.setAttribute('aria-pressed',String(audible));
      sound.setAttribute('aria-label',audible?'Mute film sound':'Enable film sound');
    }
    sound.addEventListener('click',()=>{
      if(!video.volume)video.volume=.8;
      video.muted=sound.getAttribute('aria-pressed')==='true';
      soundLabel();
    });
    video.addEventListener('volumechange',soundLabel);
    trigger.addEventListener('click',()=>{
      if(!video.src)video.src=video.dataset.src;
      video.muted=true;soundLabel();
      body.classList.add('film-open');dialog.showModal();
      document.dispatchEvent(new Event('filmstate'));
      video.currentTime=0;
      video.play().catch(()=>{ /* The native player remains available. */ });
    });
    function close(){dialog.close();}
    one('[data-close-film]',dialog).addEventListener('click',close);
    one('.film-demo',dialog).addEventListener('click',close);
    dialog.addEventListener('click',e=>{
      if(e.target!==dialog)return;
      const r=dialog.getBoundingClientRect();
      if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close();
    });
    dialog.addEventListener('close',()=>{
      video.pause();video.muted=true;body.classList.remove('film-open');document.dispatchEvent(new Event('filmstate'));
    });
    document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();});
  }

  function setupStory(storyRoot) {
    const cases=JSON.parse(one('#story-data').textContent);
    const stage=one('.story-stage',storyRoot);
    const prop=one('.scene-prop',stage);
    const articles=all('.chapter',storyRoot);
    const speak=one('#speak',storyRoot);
    const sample=one('audio',storyRoot), sampleLabel=one('span',speak);
    const initialCase=new URLSearchParams(location.search).get('example');
    let industry=Object.hasOwn(cases,initialCase)?initialCase:'service';
    let scene=0,outcome='book',observed=false,scrollCallback=0,lockUntil=0;
    let sampleRun=0;
    function setPlaying(playing){
      sampleLabel.textContent=playing?'Stop sample':'Hear sample';
      speak.setAttribute('aria-pressed',String(playing));
      speak.setAttribute('aria-label',playing?'Stop sample conversation':'Play sample conversation');
    }
    function stopSample(){
      sampleRun++;
      sample.pause();
      if(sample.readyState)sample.currentTime=0;
      setPlaying(false);
    }
    function linesFor(c,i) {
      if(i===2 && outcome==='callback')return ['Destination',c.callback,'Follow-up note',c.callbackDetail];
      const step=c.steps[i];
      if(i===2)return [step[3],step[4],step[5],step[6]+' · Tue, 10 AM'];
      return step.slice(3,7);
    }
    function update(animate=true) {
      stopSample();
      const c=cases[industry],step=c.steps[scene],lines=linesFor(c,scene);
      one('#story-channel').textContent=c.channel;
      one('#scene-time').textContent=step[0];
      ['#speaker-one','#line-one','#speaker-two','#line-two'].forEach((id,i)=>one(id).textContent=lines[i]);
      one('.dialogue',stage).hidden=scene===2;
      one('.handoff-record',stage).hidden=scene!==2;
      if(scene===2){
        const booked=outcome==='book';
        one('#record-status').textContent=booked?'Appointment booked':'Callback requested';
        one('#record-title').textContent=c.steps[2][6];
        one('#record-to').textContent=booked?c.steps[2][4]:c.callback;
        one('#record-field').textContent=booked?'Appointment':'Next action';
        one('#record-value').textContent=booked?'Tuesday, 10 AM':c.callbackDetail;
      }
      const name=scene===0 && industry==='service'?'headset':scene===2?(outcome==='book'?'ticket':'patch'):'messenger';
      const newSrc='/media/'+name+'.webp';
      if(prop.getAttribute('src')!==newSrc){
        prop.srcset='/media/'+name+'-sm.webp 570w, '+newSrc+' '+(name==='headset'?'1230w':'1000w');
        prop.src=newSrc;
      }
      const art=one('.stage-art',stage);
      if(animate && moving){art.classList.remove('swap');void art.offsetWidth;art.classList.add('swap');}
      stage.dataset.scene=String(scene);
      articles.forEach((article,i)=>{
        const callback=i===2&&outcome==='callback';
        article.classList.toggle('current',i===scene);
        one('.chapter-title',article).textContent=callback?'Arrange a callback.':c.steps[i][1];
        one('.chapter-desc',article).textContent=callback?c.callbackDetail:c.steps[i][2];
      });
      all('[data-jump]',storyRoot).forEach(button=>button.setAttribute('aria-current',String(Number(button.dataset.jump)===scene)));
      all('[data-industry]',storyRoot).forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.industry===industry)));
      all('[data-outcome]',storyRoot).forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.outcome===outcome)));
      one('#scene-count').textContent='0'+(scene+1)+' / 03';
      const advance=one('#advance');
      advance.firstChild.textContent=scene===2?'Replay scenes ':'Next scene ';
      one('.story-enquire',storyRoot).href='/contact/?solution='+encodeURIComponent(c.solution)+'&industry='+encodeURIComponent(industry);
      speak.hidden=scene===2;
    }
    function changeScene(next,scrollChapter=false) {
      scene=Math.max(0,Math.min(2,next));lockUntil=performance.now()+900;update();
      if(scrollChapter&&!mobile.matches)articles[scene].scrollIntoView({block:'center',behavior:moving?'smooth':'instant'});
    }
    all('[data-industry]',storyRoot).forEach(btn=>btn.addEventListener('click',()=>{
      industry=btn.dataset.industry;outcome='book';changeScene(0);
    }));
    all('[data-jump]',storyRoot).forEach(btn=>btn.addEventListener('click',()=>changeScene(Number(btn.dataset.jump),true)));
    one('#advance').addEventListener('click',()=>changeScene((scene+1)%3,true));
    all('[data-outcome]',storyRoot).forEach(btn=>btn.addEventListener('click',()=>{
      outcome=btn.dataset.outcome;changeScene(2);
    }));
    function followReading(){
      scrollCallback=0;
      if(!observed||mobile.matches||performance.now()<lockUntil)return;
      const target=Math.max(180,innerHeight*.46);
      const boxes=articles.map(article=>article.getBoundingClientRect());
      if(boxes[0].top>target || boxes[2].bottom<target-100)return;
      let next=0;
      for(let i=1;i<boxes.length;i++)if(boxes[i].top<=target)next=i;
      if(scene!==next){scene=next;update();}
    }
    new IntersectionObserver(([entry])=>{observed=entry.isIntersecting;if(!observed)stopSample();}).observe(one('.story-track',storyRoot));
    window.addEventListener('scroll',()=>{
      if(observed && !mobile.matches && !scrollCallback)scrollCallback=requestAnimationFrame(followReading);
    },{passive:true});
    speak.addEventListener('click',()=>{
      if(speak.getAttribute('aria-pressed')==='true'){stopSample();return;}
      const src='/media/sample-'+industry+'-'+scene+'.mp3';
      if(sample.getAttribute('src')!==src)sample.src=src;
      const request=++sampleRun;
      setPlaying(true);
      sample.play().catch(()=>{if(request===sampleRun)setPlaying(false);});
    });
    sample.addEventListener('ended',()=>setPlaying(false));
    window.addEventListener('pagehide',stopSample);
    document.addEventListener('filmstate',()=>{if(body.classList.contains('film-open'))stopSample();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)stopSample();});
    update(false);
  }

  all('.directory').forEach(dir=>{
    const rows=all('li[data-category]',dir),buttons=all('button[data-group]',dir);
    buttons.forEach(button=>button.addEventListener('click',()=>{
      const group=button.dataset.group;
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      let count=0;
      rows.forEach(row=>{row.hidden=group!=='All'&&row.dataset.category!==group;if(!row.hidden)count++;});
      one('.result-count',dir).textContent=count+' service'+(count===1?'':'s');
    }));
  });
  const integrations=one('#integration-data');
  if(integrations){
    const tools=JSON.parse(integrations.textContent);
    const buttons=all('[data-integration]');
    buttons.forEach((btn,i)=>btn.addEventListener('click',()=>{
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));
      ['#patch-name','#patch-kind','#patch-input','#patch-output'].forEach((id,j)=>one(id).textContent=tools[i][j]);
      document.dispatchEvent(new Event('patchchange'));
      if(moving && one('.jack-art').animate)one('.jack-art').animate([{transform:'translateY(3px) rotate(-2deg)'},{transform:'none'}],{duration:400,easing:'ease-out'});
    }));
  }
  function setupPatchCables(field){
    const canvas=one('.patch-lines',field),ctx=canvas.getContext('2d');
    if(!ctx)return;
    const buttons=all('[data-integration]',field),output=one('.patch-label',field);
    let visible=false,frame=0,last=0,width=0,height=0,paths=[],phase=0;
    function bezierPoint(p,t){
      const u=1-t;
      return [0,1].map(axis=>u*u*u*p[0][axis]+3*u*u*t*p[1][axis]+3*u*t*t*p[2][axis]+t*t*t*p[3][axis]);
    }
    function paint(time){
      frame=0;
      if(!visible||document.hidden){last=0;return;}
      if(moving&&last&&time-last<46){frame=requestAnimationFrame(paint);return;}
      if(last)phase+=(Math.min(100,time-last))*.0004;
      last=time;ctx.clearRect(0,0,width,height);
      for(const {points,active} of paths){
        ctx.beginPath();ctx.moveTo(...points[0]);ctx.bezierCurveTo(...points[1],...points[2],...points[3]);
        ctx.lineWidth=active?1.8:.8;ctx.strokeStyle=active?'#2468d9':'#3b72ad40';ctx.stroke();
        if(active){
          for(const offset of [0,.5]){
            const [x,y]=bezierPoint(points,(phase+offset)%1);
            ctx.fillStyle='#2688fa';ctx.beginPath();ctx.arc(x,y,3.8,0,Math.PI*2);ctx.fill();
          }
        }
      }
      if(moving)frame=requestAnimationFrame(paint);
    }
    function measure(){
      const rect=field.getBoundingClientRect(),end=output.getBoundingClientRect();
      width=rect.width;height=rect.height;
      const dpr=Math.min(devicePixelRatio||1,1.5);
      canvas.width=Math.max(1,Math.round(width*dpr));canvas.height=Math.max(1,Math.round(height*dpr));
      ctx.setTransform(dpr,0,0,dpr,0,0);
      paths=buttons.map((button,i)=>{
        const r=button.getBoundingClientRect();
        const a=mobile.matches?[r.left+r.width*.5-rect.left,r.bottom-rect.top]:[r.right-rect.left,r.top+r.height*.5-rect.top];
        const b=[end.left-rect.left+1,end.top-rect.top+end.height*.48+(i-3)*2];
        const bend=mobile.matches?[[a[0],a[1]+42],[b[0]-58,b[1]]]:[[a[0]+width*.2,a[1]],[b[0]-width*.18,b[1]+(i-3)*9]];
        return {points:[a,...bend,b],active:button.getAttribute('aria-pressed')==='true'};
      });
      cancelAnimationFrame(frame);last=0;frame=requestAnimationFrame(paint);
    }
    new ResizeObserver(measure).observe(field);
    new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;measure();}).observe(field);
    for(const event of ['ambientchange','patchchange','visibilitychange'])document.addEventListener(event,measure);
  }
  if(one('.patch-field'))setupPatchCables(one('.patch-field'));
  all('.process-book').forEach(book=>{
    const items=all('details',book);
    items.forEach(item=>item.addEventListener('toggle',()=>{
      if(item.open)items.forEach(other=>{if(other!==item)other.open=false;});
    }));
  });

  const form=one('#brief-form');
  if(form){
    // Service pages link here with ?solution=<slug>; map it onto the form's "What do you want to automate?" options.
    const query=new URLSearchParams(location.search);
    const topics={'voice-assistants':'voice-agent','sales-automation':'lead-follow-up','lead-generation':'lead-follow-up','website-assistants':'chatbot-crm','custom-platforms':'custom-ai'};
    const topic=topics[query.get('solution')],selector=form.elements.topic;
    if(topic&&Array.from(selector.options).some(o=>o.value===topic))selector.value=topic;
    const industryLabels={service:'home services',property:'real estate',business:'B2B sales',clinic:'clinics'};
    const selectedIndustry=industryLabels[query.get('industry')];
    if(selectedIndustry)form.elements.message.value='I’d like to discuss an enquiry workflow for '+selectedIndustry+'. ';
  }
  const booking=one('#booking-form');
  if(booking){
    const now=new Date();
    booking.elements.date.min=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');
    const cards=all('.platform-card',booking);
    cards.forEach(card=>card.addEventListener('click',()=>{
      booking.elements.platform.value=card.dataset.platform;
      cards.forEach(other=>other.setAttribute('aria-pressed',String(other===card)));
    }));
  }
  if(one('#sound-field'))setupWavefield(one('#sound-field'));
  if(one('.cast-stage'))setupCast(one('.cast-stage'));
  if(one('.turntable'))setupTurntable(one('.turntable'));
  if(one('#showreel'))setupReel(one('#showreel'));
  if(one('#story-data'))setupStory(one('.story'));
})();
