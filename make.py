import json, zipfile, os
from pathlib import Path

html = r'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#160f1c">
<title>Vasilisa — Admin</title>
<style>
:root{--bg:#100b14;--panel:#1b1320;--panel2:#241725;--gold:#c79a52;--gold2:#e0bd7f;--text:#f3ebe1;--muted:#b9adbd;--line:#3a2c3e;--danger:#d96a72;--ok:#82c49b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Arial,sans-serif}button,input,select,textarea{font:inherit}button{cursor:pointer}.hidden{display:none!important}
.wrap{max-width:1180px;margin:auto;padding:24px}.login{min-height:100vh;display:grid;place-items:center;padding:20px;background:radial-gradient(circle at 50% 10%,#2b1c32 0,#100b14 55%)}
.card{background:rgba(27,19,32,.98);border:1px solid var(--line);border-radius:18px;box-shadow:0 18px 60px #0006}.login .card{width:min(430px,100%);padding:32px}.brand{color:var(--gold2);letter-spacing:.16em;text-transform:uppercase;font-size:12px}.login h1{font:38px Georgia,serif;margin:8px 0 26px}.field{display:grid;gap:7px;margin:14px 0}.field label{color:var(--muted);font-size:13px}.field input,.field textarea,.field select{width:100%;background:#120d16;border:1px solid var(--line);color:var(--text);border-radius:10px;padding:12px;outline:none}.field input:focus,.field textarea:focus,.field select:focus{border-color:var(--gold)}
.btn{border:1px solid var(--gold);background:var(--gold);color:#171019;border-radius:10px;padding:11px 15px;font-weight:700}.btn.secondary{background:transparent;color:var(--gold2)}.btn.danger{border-color:var(--danger);background:transparent;color:#ffadb2}.btn.small{padding:7px 10px;font-size:13px}.top{position:sticky;top:0;z-index:10;background:#100b14ee;border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}.topin{max-width:1180px;margin:auto;padding:14px 24px;display:flex;align-items:center;gap:18px}.logo{font:22px Georgia,serif;color:var(--gold2);margin-right:auto}.nav{display:flex;gap:6px;flex-wrap:wrap}.nav button{background:transparent;border:1px solid transparent;color:var(--muted);padding:8px 10px;border-radius:8px}.nav button.active,.nav button:hover{color:var(--text);border-color:var(--line);background:var(--panel2)}
main{padding:28px 0 60px}.title{font:38px Georgia,serif;margin:0 0 6px}.sub{color:var(--muted);margin:0 0 24px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}.stat{padding:18px;border:1px solid var(--line);border-radius:14px;background:var(--panel)}.stat small{color:var(--muted)}.stat b{display:block;font-size:27px;color:var(--gold2);margin-top:4px}.grid{display:grid;grid-template-columns:1.3fr .7fr;gap:18px}.panel{padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:16px}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:14px}.table{width:100%;border-collapse:collapse}.table th,.table td{text-align:left;padding:11px 8px;border-bottom:1px solid var(--line);vertical-align:top}.table th{color:var(--muted);font-weight:500;font-size:13px}.badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 8px;font-size:12px}.badge.ok{color:var(--ok);border-color:#31583e}.badge.cancel{color:#ffadb2;border-color:#65343a}.calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}.day{min-height:72px;padding:8px;border:1px solid var(--line);border-radius:10px;background:#151019;text-align:left;color:var(--text)}.day.muted{opacity:.35}.day.closed{border-color:#71353c;background:#261419}.day.today{outline:1px solid var(--gold)}.day strong{display:block}.hours{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.hour{padding:9px;border:1px solid var(--line);background:#151019;color:var(--text);border-radius:8px}.hour.closed{border-color:#71353c;color:#ffadb2}.notice{padding:11px 13px;border-radius:10px;background:#171019;border:1px solid var(--line);color:var(--muted);margin:12px 0}.notice.ok{border-color:#31583e;color:#a9d7b8}.notice.err{border-color:#65343a;color:#ffadb2}.cards{display:grid;gap:12px}.proc{display:grid;grid-template-columns:1fr auto;gap:10px;padding:15px;border:1px solid var(--line);border-radius:12px;background:#171019}.proc h3{margin:0 0 4px}.price{color:var(--gold2);font-size:20px}.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.lang{color:var(--gold2);font-size:12px}.empty{color:var(--muted);padding:18px 0}.mobileOnly{display:none}
@media(max-width:800px){.wrap{padding:18px}.topin{padding:12px 18px;align-items:flex-start}.nav{display:none}.mobileOnly{display:block}.stats{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.hours{grid-template-columns:repeat(3,1fr)}.title{font-size:32px}.table{font-size:13px}.tableWrap{overflow:auto}.top .btn.small{margin-left:8px}}
</style>
</head>
<body>
<div id="app"></div>
<script>
(function(){
'use strict';
var app=document.getElementById('app'), state={user:null,tab:'dashboard',stats:null,bookings:[],procedures:[],closedDays:[],closedHours:[],selectedDate:null,notice:''};
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function api(path,opt){opt=opt||{};var o={method:opt.method||'GET',headers:{'Content-Type':'application/json'}};if(opt.body!==undefined)o.body=JSON.stringify(opt.body);return fetch(path,o).then(function(r){return r.json().catch(function(){return {ok:false,error:'Ответ сервера не JSON'}}).then(function(x){if(!r.ok)throw new Error(x.error||('HTTP '+r.status));return x})})}
function toast(msg,ok){state.notice=msg;render();setTimeout(function(){state.notice='';render()},2500)}
function login(){app.innerHTML='<div class="login"><div class="card"><div class="brand">Cosmetology by Vasilisa</div><h1>Админ-панель</h1><form id="loginForm"><div class="field"><label>Логин</label><input id="u" autocomplete="username" required></div><div class="field"><label>Пароль</label><input id="p" type="password" autocomplete="current-password" required></div><button class="btn" style="width:100%">Войти</button></form><div id="loginErr"></div></div></div>';document.getElementById('loginForm').onsubmit=function(e){e.preventDefault();var er=document.getElementById('loginErr');er.innerHTML='';api('/api/login',{method:'POST',body:{user:document.getElementById('u').value,password:document.getElementById('p').value}}).then(function(){boot()}).catch(function(e){er.innerHTML='<div class="notice err">'+esc(e.message)+'</div>'})}}
function nav(){return '<div class="top"><div class="topin"><div class="logo">Vasilisa Admin</div><button class="btn small mobileOnly" onclick="toggleNav()">Меню</button><div class="nav" id="nav">'+[['dashboard','Обзор'],['calendar','Календарь'],['bookings','Записи'],['procedures','Процедуры'],['quiz','Квиз'],['gallery','До / После'],['reviews','Отзывы'],['settings','Настройки']].map(function(x){return '<button class="'+(state.tab===x[0]?'active':'')+'" onclick="go(\''+x[0]+'\')">'+x[1]+'</button>'}).join('')+'</div><button class="btn secondary small" onclick="logout()">Выйти</button></div></div>'}
function base(title,sub,body){return nav()+'<main><div class="wrap"><h1 class="title">'+title+'</h1><p class="sub">'+sub+'</p>'+(state.notice?'<div class="notice ok">'+esc(state.notice)+'</div>':'')+body+'</div></main>'}
function dashboard(){var s=state.stats||{};return base('Обзор','Управление записью и расписанием', '<div class="stats"><div class="stat"><small>Всего записей</small><b>'+esc(s.total||0)+'</b></div><div class="stat"><small>Сегодня</small><b>'+esc(s.today||0)+'</b></div><div class="stat"><small>Активные процедуры</small><b>'+esc(s.procedures||0)+'</b></div><div class="stat"><small>Закрытых дней</small><b>'+esc(s.closedDays||0)+'</b></div></div><div class="grid"><div class="panel"><h2>Последние записи</h2>'+bookingTable(state.bookings.slice(0,8))+'</div><div class="panel"><h2>Быстрые действия</h2><div class="cards"><button class="btn" onclick="go(\'calendar\')">Открыть календарь</button><button class="btn secondary" onclick="go(\'bookings\')">Посмотреть записи</button><button class="btn secondary" onclick="go(\'procedures\')">Изменить процедуры</button></div></div></div>')}
function bookingTable(rows){if(!rows.length)return '<div class="empty">Пока нет записей.</div>';return '<div class="tableWrap"><table class="table"><thead><tr><th>Дата</th><th>Клиент</th><th>Процедура</th><th>Статус</th></tr></thead><tbody>'+rows.map(function(b){return '<tr><td>'+esc(b.date||b.booking_date||'')+'<br>'+esc(b.time||b.booking_time||'')+'</td><td>'+esc(b.client_name||b.name||'')+'<br><span style="color:var(--muted)">'+esc(b.phone||'')+'</span></td><td>'+esc(b.procedure_name||b.procedure||'')+'</td><td>'+badge(b.status)+'</td></tr>'}).join('')+'</tbody></table></div>'}
function badge(s){s=s||'pending';var cls=s==='confirmed'?'ok':s==='cancelled'?'cancel':'';return '<span class="badge '+cls+'">'+esc(s==='confirmed'?'Подтверждена':s==='cancelled'?'Отменена':'Ожидает')+'</span>'}
function bookings(){return base('Записи','Все заявки клиентов','<div class="panel"><div class="toolbar"><button class="btn secondary small" onclick="loadAll()">Обновить</button></div>'+bookingTable(state.bookings)+'</div>')}
function calendar(){var d=new Date(),y=d.getFullYear(),m=d.getMonth();if(state.calYear!=null){y=state.calYear;m=state.calMonth}var first=new Date(y,m,1),start=(first.getDay()+6)%7,days=new Date(y,m+1,0).getDate(),html='<div class="panel"><div class="toolbar"><button class="btn secondary small" onclick="month(-1)">←</button><b>'+['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'][m]+' '+y+'</b><button class="btn secondary small" onclick="month(1)">→</button></div><div class="calendar">';for(var i=0;i<start;i++)html+='<div></div>';for(var n=1;n<=days;n++){var ds=y+'-'+String(m+1).padStart(2,'0')+'-'+String(n).padStart(2,'0'),closed=state.closedDays.indexOf(ds)>=0,today=new Date().toISOString().slice(0,10);html+='<button class="day '+(closed?'closed ':'')+(ds===today?'today ':'')+'" onclick="selectDay(\''+ds+'\')"><strong>'+n+'</strong><small>'+(closed?'Закрыт':'Открыт')+'</small></button>'}html+='</div></div>';var detail='';if(state.selectedDate){var c=state.closedDays.indexOf(state.selectedDate)>=0;detail='<div class="panel"><h2>'+esc(state.selectedDate)+'</h2><div class="toolbar"><button class="btn '+(c?'secondary':'')+'" onclick="toggleDay()">'+(c?'Открыть день':'Закрыть день')+'</button></div><p class="sub">Закрыть отдельные часы:</p><div class="hours">'+Array.from({length:13},function(_,i){var h=9+i,ds=state.selectedDate+'T'+String(h).padStart(2,'0')+':00',cl=state.closedHours.indexOf(ds)>=0;return '<button class="hour '+(cl?'closed':'')+'" onclick="toggleHour(\''+ds+'\')">'+String(h).padStart(2,'0')+':00 · '+(cl?'закрыт':'открыт')+'</button>'}).join('')+'</div></div>'}return base('Календарь','Закрывайте целые дни или отдельные часы', '<div class="grid">'+html+detail+'</div>')}
function procedures(){return base('Процедуры','Редактирование цены и активности','<div class="cards">'+state.procedures.map(function(p){return '<div class="proc"><div><div class="lang">RU · '+(p.active?'АКТИВНА':'СКРЫТА')+'</div><h3>'+esc(p.name)+'</h3><div style="color:var(--muted)">'+esc(p.description)+'</div></div><div style="text-align:right"><div class="price">'+esc(p.price)+' €</div><button class="btn secondary small" onclick="editProc('+p.id+')">Изменить</button></div></div>'}).join('')+'</div>')}
function placeholder(title,text){return base(title,text,'<div class="panel"><div class="notice">Раздел готов к подключению к базе. Основные данные сайта при этом не затрагиваются.</div></div>')}
function render(){if(!state.user){login();return}var body=state.tab==='dashboard'?dashboard():state.tab==='calendar'?calendar():state.tab==='bookings'?bookings():state.tab==='procedures'?procedures():state.tab==='quiz'?placeholder('Квиз кожи','Вопросы и связи с процедурами'):state.tab==='gallery'?placeholder('До / После','Галерея результатов'):state.tab==='reviews'?placeholder('Отзывы','Отзывы клиентов'):placeholder('Настройки','Контакты и настройки сайта');app.innerHTML=body}
window.go=function(t){state.tab=t;loadAll()};window.toggleNav=function(){var n=document.getElementById('nav');n.style.display=n.style.display==='flex'?'none':'flex'};window.month=function(delta){var d=new Date(state.calYear||new Date().getFullYear(),(state.calMonth==null?new Date().getMonth():state.calMonth)+delta,1);state.calYear=d.getFullYear();state.calMonth=d.getMonth();render()};window.selectDay=function(ds){state.selectedDate=ds;render()};window.toggleDay=function(){api('/api/calendar/day',{method:'POST',body:{date:state.selectedDate,closed:state.closedDays.indexOf(state.selectedDate)<0}}).then(loadAll).catch(function(e){toast(e.message,false)})};window.toggleHour=function(ds){api('/api/calendar/hour',{method:'POST',body:{datetime:ds,closed:state.closedHours.indexOf(ds)<0}}).then(loadAll).catch(function(e){toast(e.message,false)})};window.editProc=function(id){var p=state.procedures.find(function(x){return x.id===id});if(!p)return;var name=prompt('Название процедуры',p.name);if(name===null)return;var price=prompt('Цена',p.price);if(price===null)return;var desc=prompt('Описание',p.description||'');if(desc===null)return;api('/api/procedures/'+id,{method:'POST',body:{name:name,price:Number(price),description:desc,active:!!p.active}}).then(loadAll).catch(function(e){toast(e.message,false)})};window.logout=function(){fetch('/api/logout',{method:'POST'}).finally(function(){location.reload()})};
function loadAll(){Promise.all([api('/api/me'),api('/api/dashboard'),api('/api/bookings'),api('/api/procedures'),api('/api/calendar')]).then(function(a){state.user=a[0].user;state.stats=a[1];state.bookings=a[2].items||[];state.procedures=a[3].items||[];state.closedDays=a[4].closedDays||[];state.closedHours=a[4].closedHours||[];render()}).catch(function(e){if(String(e.message).toLowerCase().indexOf('auth')>=0){state.user=null;render()}else{state.user=state.user||{name:'admin'};state.notice=e.message;render()}})}
function boot(){api('/api/me').then(function(x){state.user=x.user;loadAll()}).catch(function(){state.user=null;render()})}boot();
})();
</script>
</body></html>'''

worker = r'''export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      if (url.pathname === "/favicon.ico") return new Response(null,{status:204});
      if (url.pathname.startsWith("/api/")) return await api(request, env, url);
      if (request.method !== "GET") return json({ok:false,error:"Method not allowed"},405);
      return new Response(PAGE,{headers:{"content-type":"text/html;charset=UTF-8","cache-control":"no-store"}});
    } catch (e) {
      return new Response("Admin Worker error: " + (e && e.message ? e.message : String(e)), {status:500,headers:{"content-type":"text/plain;charset=UTF-8"}});
    }
  }
};

const PAGE = PAGE_CONTENT;

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json;charset=UTF-8","cache-control":"no-store"}})}
function cookie(req,name){const s=req.headers.get("Cookie")||"";const m=s.match(new RegExp("(?:^|; )"+name.replace(/[.*+?^${}()|[\\]\\\\]/g,"\\$&")+"=([^;]+)"));return m?decodeURIComponent(m[1]):""}
function setCookie(v){return "va_session="+encodeURIComponent(v)+"; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400"}
async function sign(text,secret){const key=await crypto.subtle.importKey("raw",new TextEncoder().encode(secret),{name:"HMAC",hash:"SHA-256"},false,["sign"]);const b=await crypto.subtle.sign("HMAC",key,new TextEncoder().encode(text));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("")}
async function session(req,env){const v=cookie(req,"va_session");if(!v||!env.SESSION_SECRET)return null;const p=v.split(".");if(p.length!==3)return null;const raw=p[0]+"."+p[1];const sig=await sign(raw,env.SESSION_SECRET);if(sig!==p[2])return null;const exp=Number(p[1]);if(!Number.isFinite(exp)||exp<Date.now())return null;return {user:p[0]}}
async function requireAuth(req,env){const s=await session(req,env);if(!s)throw Object.assign(new Error("auth"),{status:401});return s}
async function db(env){if(!env.DB)throw Object.assign(new Error("D1 binding DB is missing"),{status:503});await env.DB.batch([
  env.DB.prepare("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, phone TEXT, procedure_name TEXT, booking_date TEXT, booking_time TEXT, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT CURRENT_TIMESTAMP)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS procedures (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, description TEXT, active INTEGER DEFAULT 1)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS closed_days (date TEXT PRIMARY KEY)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS closed_hours (datetime TEXT PRIMARY KEY)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS quiz_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, active INTEGER DEFAULT 1)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS gallery (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, image_url TEXT, active INTEGER DEFAULT 1)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, text TEXT, active INTEGER DEFAULT 1)"),
  env.DB.prepare("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
]);
return env.DB}
async function api(req,env,url){
  try{
    if(url.pathname==="/api/login"&&req.method==="POST"){
      const b=await req.json();if(!env.ADMIN_USER||!env.ADMIN_PASSWORD||!env.SESSION_SECRET)return json({ok:false,error:"Admin secrets are not configured in Cloudflare"},500);
      if(String(b.user)!==String(env.ADMIN_USER)||String(b.password)!==String(env.ADMIN_PASSWORD))return json({ok:false,error:"Неверный логин или пароль"},401);
      const exp=Date.now()+86400000;const raw=String(env.ADMIN_USER)+"."+exp;const sig=await sign(raw,env.SESSION_SECRET);return new Response(JSON.stringify({ok:true}),{headers:{"content-type":"application/json","set-cookie":setCookie(raw+"."+sig)}})
    }
    if(url.pathname==="/api/logout")return new Response(JSON.stringify({ok:true}),{headers:{"content-type":"application/json","set-cookie":"va_session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax"}});
    const s=await requireAuth(req,env);
    if(url.pathname==="/api/me")return json({ok:true,user:s.user});
    const D=await db(env);
    if(url.pathname==="/api/dashboard"){
      const [a,b,c,d]=await D.batch([D.prepare("SELECT COUNT(*) n FROM bookings"),D.prepare("SELECT COUNT(*) n FROM bookings WHERE booking_date=?").bind(new Date().toISOString().slice(0,10)),D.prepare("SELECT COUNT(*) n FROM procedures WHERE active=1"),D.prepare("SELECT COUNT(*) n FROM closed_days")]);
      return json({ok:true,total:a.results[0]?.n||0,today:b.results[0]?.n||0,procedures:c.results[0]?.n||0,closedDays:d.results[0]?.n||0})
    }
    if(url.pathname==="/api/bookings")return json({ok:true,items:(await D.prepare("SELECT * FROM bookings ORDER BY booking_date DESC, booking_time DESC, id DESC LIMIT 500").all()).results||[]});
    if(url.pathname==="/api/procedures"&&req.method==="GET")return json({ok:true,items:(await D.prepare("SELECT * FROM procedures ORDER BY id").all()).results||[]});
    if(url.pathname.startsWith("/api/procedures/")&&req.method==="POST"){
      const id=Number(url.pathname.split("/").pop()),b=await req.json();await D.prepare("UPDATE procedures SET name=?,price=?,description=?,active=? WHERE id=?").bind(String(b.name||""),Number(b.price||0),String(b.description||""),b.active?1:0,id).run();return json({ok:true})
    }
    if(url.pathname==="/api/calendar")return json({ok:true,closedDays:(await D.prepare("SELECT date FROM closed_days ORDER BY date").all()).results.map(x=>x.date),closedHours:(await D.prepare("SELECT datetime FROM closed_hours ORDER BY datetime").all()).results.map(x=>x.datetime)});
    if(url.pathname==="/api/calendar/day"&&req.method==="POST"){
      const b=await req.json();if(b.closed)await D.prepare("INSERT OR IGNORE INTO closed_days(date) VALUES(?)").bind(String(b.date)).run();else await D.prepare("DELETE FROM closed_days WHERE date=?").bind(String(b.date)).run();return json({ok:true})
    }
    if(url.pathname==="/api/calendar/hour"&&req.method==="POST"){
      const b=await req.json();if(b.closed)await D.prepare("INSERT OR IGNORE INTO closed_hours(datetime) VALUES(?)").bind(String(b.datetime)).run();else await D.prepare("DELETE FROM closed_hours WHERE datetime=?").bind(String(b.datetime)).run();return json({ok:true})
    }
    return json({ok:false,error:"Not found"},404)
  }catch(e){return json({ok:false,error:e.message||String(e)},e.status||500)}
}
'''
# Insert page as JSON JS string
worker = worker.replace('PAGE_CONTENT', json.dumps(html, ensure_ascii=False))
Path('/mnt/data/admin_new/_worker.js').write_text(worker, encoding='utf-8')
Path('/mnt/data/admin_new/README.md').write_text('''# Vasilisa Admin — clean Worker\n\nThis is a standalone Cloudflare Worker-style admin panel. It does not use `env.ASSETS`, React, npm, or a build step.\n\nRequired Cloudflare bindings/secrets:\n- D1 binding: `DB` -> `vasilisa-db`\n- Secret `ADMIN_USER`\n- Secret `ADMIN_PASSWORD`\n- Secret `SESSION_SECRET`\n\nThe worker creates the small required D1 tables automatically if they do not exist.\n''',encoding='utf-8')
Path('/mnt/data/admin_new/DEPLOY.md').write_text('''# Deploy\n\n1. Put `_worker.js` in the root of the Pages/Workers project.\n2. Remove old worker files so there is only one active `_worker.js`.\n3. Keep D1 binding `DB` -> `vasilisa-db`.\n4. Keep secrets `ADMIN_USER`, `ADMIN_PASSWORD`, `SESSION_SECRET`.\n5. No build command is required.\n6. Open `/login`.\n\nThe worker returns its own HTML and does not call `env.ASSETS`, so it is independent of a static-assets configuration.\n''',encoding='utf-8')
# syntax check
os.system('node --check /mnt/data/admin_new/_worker.js')
# zip
zip_path='/mnt/data/vasilisa-admin-from-scratch.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in Path('/mnt/data/admin_new').iterdir(): z.write(p,p.name)
print(zip_path, os.path.getsize(zip_path))
