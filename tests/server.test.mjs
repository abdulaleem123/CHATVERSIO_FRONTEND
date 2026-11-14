import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readdir, readFile, rm, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { createApp } from '../server/index.mjs';
import { validate } from '../server/validation.mjs';

const enquiry = { name: 'Integration QA', email: 'qa@example.com', message: 'Synthetic integration test. No real customer.', website: 'example.com', timezone: 'Asia/Karachi' };
const booking = { name: 'Integration QA', email: 'qa@example.com', date: '2030-02-02', time: '14:00', platform: 'Google Meet', timezone: 'Asia/Karachi' };
async function setup(t, extra={}) {
  const dir = await mkdtemp(join(tmpdir(), 'chatversio-test-'));
  const publicDir = join(dir,'public'); await mkdir(publicDir);
  await writeFile(join(publicDir, 'index.html'), '<h1>Fixture</h1>');
  await writeFile(join(publicDir, 'clip.mp4'), '0123456789');
  const dataDir = join(dir,'private');
  const app = createApp({ dataDir, publicDir, maxRequests: 100, ...extra });
  await new Promise(resolve=>app.listen(0,'127.0.0.1',resolve));
  const base = `http://127.0.0.1:${app.address().port}`;
  t.after(async()=>{ await new Promise(resolve=>app.close(resolve)); await rm(dir,{recursive:true,force:true}); });
  const post = (payload=enquiry,key=randomUUID(),path='/api/enquiries',headers={})=>fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json','X-Idempotency-Key':key,...headers},body:JSON.stringify(payload)});
  return { base,dataDir,post };
}
test('enquiries are persisted before success; retries and concurrent requests are idempotent',async t=>{
  const {post,dataDir}=await setup(t); const key=randomUUID();
  const results=await Promise.all([post(enquiry,key),post(enquiry,key)]);
  for(const r of results)assert.equal(r.status,201);
  const [a,b]=await Promise.all(results.map(r=>r.json()));assert.equal(a.id,b.id);
  const files=await readdir(dataDir);assert.equal(files.length,1);
  const record=JSON.parse(await readFile(join(dataDir,files[0]),'utf8'));
  assert.equal(record.data.email,enquiry.email);assert.equal(record.data.website,'https://example.com/');
  assert.equal(record.status,'received');assert.equal(record.delivery.status,'pending');
  assert.equal((await post({...enquiry,message:'Different content'},key)).status,409);
});
test('invalid email, honeypot, huge body, wrong method and hostile origin do not produce successful submissions',async t=>{
  const {post,base}=await setup(t);
  assert.equal((await post({...enquiry,email:'bad'})).status,422);
  assert.equal((await post({...enquiry,companyWebsite:'bot-filled'})).status,422);
  assert.equal((await post({...enquiry,message:'x'.repeat(22000)})).status,413);
  assert.equal((await post(enquiry,randomUUID(),'/api/enquiries',{Origin:'https://unrelated.example'})).status,403);
  assert.equal((await fetch(base+'/api/enquiries')).status,405);
});
test('rate limiting provides a retryable response',async t=>{
  const {post}=await setup(t,{maxRequests:1});
  assert.equal((await post()).status,201);assert.equal((await post()).status,429);
});
test('booking requests are requests, not false confirmations',async t=>{
  const {post}=await setup(t);
  const tomorrow = new Date(Date.now()+86400000).toISOString().slice(0,10);
  const response=await post({...booking,date:tomorrow},randomUUID(),'/api/booking-requests');
  assert.equal(response.status,201);assert.equal((await response.json()).status,'requested');
});
test('booking validation rejects past local times, impossible dates and invalid zones',()=>{
  const now = new Date('2030-02-01T08:00:00Z');
  assert.equal(validate('booking',booking,now).date,'2030-02-02');
  assert.throws(()=>validate('booking',{...booking,date:'2030-02-01',time:'12:59'},now));
  assert.throws(()=>validate('booking',{...booking,date:'2030-02-30'},now));
  assert.throws(()=>validate('booking',{...booking,timezone:'No/SuchZone'},now));
  assert.throws(()=>validate('booking',{...booking,platform:'Unsupported'},now));
});
test('private files are not served; media supports byte ranges and HEAD',async t=>{
  const {base}=await setup(t);
  assert.equal((await fetch(base+'/.env')).status,404);
  assert.equal((await fetch(base+'/server/index.mjs')).status,404);
  assert.equal((await fetch(base+'/data/')).status,404);
  const part=await fetch(base+'/clip.mp4',{headers:{Range:'bytes=2-5'}});
  assert.equal(part.status,206);assert.equal(await part.text(),'2345');
  assert.equal(part.headers.get('content-range'),'bytes 2-5/10');
  assert.equal((await fetch(base+'/clip.mp4',{method:'HEAD'})).headers.get('content-length'),'10');
  assert.equal((await fetch(base+'/clip.mp4',{headers:{Range:'bytes=40-50'}})).status,416);
});
test('storage failures never claim successful delivery',async t=>{
  const dir=await mkdtemp(join(tmpdir(),'chatversio-invalid-'));const bad=join(dir,'not-a-directory');await writeFile(bad,'x');
  t.after(()=>rm(dir,{recursive:true,force:true}));
  const {post}=await setup(t,{dataDir:bad});
  const response=await post();assert.equal(response.status,500);assert.equal((await response.json()).ok,false);
});
