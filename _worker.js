const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function cols(db, table){
  try{
    const r = await db.prepare(`PRAGMA table_info("${table}")`).all();
    return (r.results || []).map(x => x.name);
  }catch(e){ return []; }
}
async function rows(db, table, limit=200){
  try{
    const r = await db.prepare(`SELECT * FROM "${table}" LIMIT ${limit}`).all();
    return r.results || [];
  }catch(e){ return []; }
}
function pick(o, names, fallback=""){
  for(const n of names) if(o && o[n] !== undefined && o[n] !== null) return o[n];
  return fallback;
}
async function tableInfo(db, table){
  return { columns: await cols(db, table), data: await rows(db, table) };
}

async function ensure(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS admin_sessions (
    token TEXT PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, expires_at TEXT NOT NULL
  )`).run();
  await db.prepare(`CREATE TABLE IF NOT EXISTS admin_settings (
    key TEXT PRIMARY KEY, value TEXT
  )`).run();
}

function cookie(name, value, maxAge=604800){
  return `${name}=${encodeURIComponent(value)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}
async function authorized(req, env){
  const c = req.headers.get("Cookie") || "";
  const m = c.match(/va_session=([^;]+)/);
  if(!m) return false;
  try{
    const token = decodeURIComponent(m[1]);
    const r = await env.DB.prepare(
      `SELECT token FROM admin_sessions WHERE token=? AND expires_at > CURRENT_TIMESTAMP`
    ).bind(token).first();
    return !!r;
  }catch(e){ return false; }
}
function rand(){
  return crypto.randomUUID().replaceAll("-","") + crypto.randomUUID().replaceAll("-","");
}

const CSS = `
*{box-sizing:border-box}html,body{margin:0;background:#160f1c;color:#f3ebe1;font-family:Inter,Arial,sans-serif}
body{min-height:100vh}.wrap{max-width:1200px;margin:auto;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:8px 0 24px;border-bottom:1px solid #3a2b3e}
.brand{font-family:Georgia,serif;font-size:28px}.muted{color:#b9aeba}.gold{color:#c79a52}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}button,.btn{border:1px solid #c79a52;background:#241725;color:#f3ebe1;padding:11px 15px;border-radius:8px;cursor:pointer}button:hover,.btn:hover{background:#312035}
input,select,textarea{width:100%;background:#211621;border:1px solid #55435b;color:#f3ebe1;padding:11px;border-radius:8px}textarea{min-height:90px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:#211621;border:1px solid #3a2b3e;border-radius:12px;padding:18px}.stat b{display:block;font-size:28px;margin-top:8px}
.panel{background:#211621;border:1px solid #3a2b3e;border-radius:12px;padding:20px;margin-top:18px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:11px;border-bottom:1px solid #3a2b3e;vertical-align:top}th{color:#c79a52}
.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}.actions{display:flex;flex-wrap:wrap;gap:8px}.error{border:1px solid #a94d5e;background:#28141d;color:#ffb8c2;padding:14px;border-radius:9px;margin:15px 0}
.login{max-width:430px;margin:10vh auto}.title{font-family:Georgia,serif;font-size:38px;margin:0 0 8px}
@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}.row{grid-template-columns:1fr}.wrap{padding:14px}table{font-size:13px;display:block;overflow:auto;white-space:nowrap}}
@media(max-width:520px){.grid{grid-template-columns:1fr}.brand{font-size:23px}}
`;

async function api(req, env, url){
  await ensure(env.DB);
  const p = url.pathname;
  if(p === "/api/login" && req.method==="POST"){
    const b = await req.json().catch(()=>({}));
    if(String(b.user||"") !== String(env.ADMIN_USER||"") || String(b.password||"") !== String(env.ADMIN_PASSWORD||""))
      return Response.json({ok:false,error:"Неверный логин или пароль"},{status:401});
    const token=rand();
    await env.DB.prepare(`INSERT INTO admin_sessions(token,expires_at) VALUES(?,datetime('now','+7 days'))`).bind(token).run();
    return new Response(JSON.stringify({ok:true}),{headers:{'content-type':'application/json','set-cookie':cookie("va_session",token)}});
  }
  if(p === "/api/logout"){
    const c=req.headers.get("Cookie")||"",m=c.match(/va_session=([^;]+)/);
    if(m) await env.DB.prepare("DELETE FROM admin_sessions WHERE token=?").bind(decodeURIComponent(m[1])).run().catch(()=>{});
    return new Response(JSON.stringify({ok:true}),{headers:{'content-type':'application/json','set-cookie':cookie("va_session","",-1)}});
  }
  if(!(await authorized(req,env))) return Response.json({ok:false,error:"auth"},{status:401});

  if(p === "/api/data"){
    const [proc,book,closedD,closedH,quiz,gallery,reviews,settings] = await Promise.all([
      tableInfo(env.DB,"procedures"),tableInfo(env.DB,"bookings"),tableInfo(env.DB,"closed_days"),
      tableInfo(env.DB,"closed_hours"),tableInfo(env.DB,"quiz_concerns"),tableInfo(env.DB,"gallery"),
      tableInfo(env.DB,"reviews"),tableInfo(env.DB,"settings")
    ]);
    return Response.json({ok:true,procedures:proc.data,procedureColumns:proc.columns,bookings:book.data,bookingColumns:book.columns,
      closedDays:closedD.data,closedDayColumns:closedD.columns,closedHours:closedH.data,closedHourColumns:closedH.columns,
      quiz:quiz.data,gallery:gallery.data,reviews:reviews.data,settings:settings.data});
  }

  if(p === "/api/procedure" && req.method==="POST"){
    const b=await req.json();
    const id=Number(b.id);
    const c=await cols(env.DB,"procedures");
    const sets=[],vals=[];
    if(c.includes("price") && b.price!==undefined){sets.push("price=?");vals.push(b.price)}
    if(c.includes("description") && b.description!==undefined){sets.push("description=?");vals.push(b.description)}
    if(c.includes("active") && b.active!==undefined){sets.push("active=?");vals.push(b.active?1:0)}
    if(c.includes("name") && b.name!==undefined){sets.push("name=?");vals.push(b.name)}
    if(!sets.length) return Response.json({ok:true});
    await env.DB.prepare(`UPDATE procedures SET ${sets.join(",")} WHERE id=?`).bind(...vals,id).run();
    return Response.json({ok:true});
  }

  if(p === "/api/close-day" && req.method==="POST"){
    const b=await req.json(), c=await cols(env.DB,"closed_days");
    const date=b.date, closed=b.closed!==false;
    if(!c.includes("date")) return Response.json({ok:false,error:"В таблице closed_days нет колонки date"},{status:500});
    if(closed){
      if(c.includes("day")) await env.DB.prepare(`INSERT OR REPLACE INTO closed_days(date,day) VALUES(?,?)`).bind(date,date).run();
      else await env.DB.prepare(`INSERT OR REPLACE INTO closed_days(date) VALUES(?)`).bind(date).run();
    } else await env.DB.prepare(`DELETE FROM closed_days WHERE date=?`).bind(date).run();
    return Response.json({ok:true});
  }

  if(p === "/api/close-hour" && req.method==="POST"){
    const b=await req.json(), c=await cols(env.DB,"closed_hours");
    if(!c.includes("date") || !c.includes("hour")) return Response.json({ok:false,error:"closed_hours требует date и hour"},{status:500});
    if(b.closed!==false) await env.DB.prepare(`INSERT OR REPLACE INTO closed_hours(date,hour) VALUES(?,?)`).bind(b.date,Number(b.hour)).run();
    else await env.DB.prepare(`DELETE FROM closed_hours WHERE date=? AND hour=?`).bind(b.date,Number(b.hour)).run();
    return Response.json({ok:true});
  }

  if(p === "/api/booking-status" && req.method==="POST"){
    const b=await req.json(), c=await cols(env.DB,"bookings");
    if(!c.includes("status")) return Response.json({ok:false,error:"В таблице bookings нет status"},{status:500});
    const id = b.id;
    await env.DB.prepare(`UPDATE bookings SET status=? WHERE id=?`).bind(String(b.status),id).run();
    return Response.json({ok:true});
  }

  return Response.json({ok:false,error:"Not found"},{status:404});
}

function loginPage(msg=""){
return `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vasilisa — Admin</title><style>${CSS}</style></head><body><main class="login"><div class="card"><div class="gold">COSMETOLOGY BY VASILISA</div><h1 class="title">Админ-панель</h1><p class="muted">Управление сайтом и записями</p>${msg?`<div class="error">${esc(msg)}</div>`:""}<form method="post" action="/login"><p><label>Логин<input name="user" autocomplete="username"></label></p><p><label>Пароль<input type="password" name="password" autocomplete="current-password"></label></p><button type="submit">Войти</button></form></div></main></body></html>`;
}

function shell(){
return `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vasilisa — Admin</title><style>${CSS}</style></head><body><div class="wrap"><header><div><div class="gold">COSMETOLOGY BY VASILISA</div><div class="brand">Админ-панель</div></div><button id="logout">Выйти</button></header><nav><button data-tab="dashboard">Обзор</button><button data-tab="bookings">Записи</button><button data-tab="procedures">Процедуры</button><button data-tab="calendar">Календарь</button><button data-tab="quiz">Квиз кожи</button></nav><div id="app"></div></div><script>
const $=s=>document.querySelector(s), app=$("#app"); let data={};
async function get(){let r=await fetch("/api/data"); if(r.status===401){location="/login";return} let j=await r.json(); if(!j.ok) throw Error(j.error); data=j}
async function act(url,body){let r=await fetch(url,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body)});let j=await r.json();if(!j.ok)throw Error(j.error||"Ошибка");await get();render()}
function esc(s){return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function pick(o,names){for(const n of names)if(o&&o[n]!=null)return o[n];return ""}
function render(){
 const tab=window.tab||"dashboard";
 if(tab==="dashboard"){app.innerHTML=\`<div class="grid"><div class="card stat"><span class="muted">Процедуры</span><b>\${data.procedures.length}</b></div><div class="card stat"><span class="muted">Записи</span><b>\${data.bookings.length}</b></div><div class="card stat"><span class="muted">Закрытые дни</span><b>\${data.closedDays.length}</b></div><div class="card stat"><span class="muted">Фото</span><b>\${data.gallery.length}</b></div></div><div class="panel"><h2>Система</h2><p class="muted">Админка подключена к существующей базе vasilisa-db. Колонки таблиц определяются автоматически, поэтому старую базу пересоздавать не нужно.</p></div>\`}
 if(tab==="bookings"){let rows=data.bookings.map(b=>\`<tr><td>\${esc(b.id)}</td><td>\${esc(pick(b,["client_name","name","client","customer_name"]))}</td><td>\${esc(pick(b,["phone","telephone"]))}</td><td>\${esc(pick(b,["procedure_name","procedure","service"]))}</td><td>\${esc(pick(b,["booking_date","date","appointment_date"]))} \${esc(pick(b,["booking_time","time","appointment_time"]))}</td><td>\${esc(pick(b,["status","state"]))}</td></tr>\`).join("");app.innerHTML=\`<div class="panel"><h2>Записи</h2><div style="overflow:auto"><table><thead><tr><th>ID</th><th>Клиент</th><th>Телефон</th><th>Процедура</th><th>Дата / время</th><th>Статус</th></tr></thead><tbody>\${rows||"<tr><td colspan=6>Пока нет записей</td></tr>"}</tbody></table></div></div>\`}
 if(tab==="procedures"){app.innerHTML=\`<div class="panel"><h2>Процедуры</h2>\${data.procedures.map(p=>\`<div class="card" style="margin:12px 0"><div class="row"><label>Название<input id="n\${p.id}" value="\${esc(p.name)}"></label><label>Цена<input id="p\${p.id}" value="\${esc(p.price)}"></label></div><p><label>Описание<textarea id="d\${p.id}">\${esc(p.description)}</textarea></label></p><div class="actions"><button onclick="saveProc(\${p.id})">Сохранить</button></div></div>\`).join("")}</div>\`}
 if(tab==="calendar"){let today=new Date().toISOString().slice(0,10);app.innerHTML=\`<div class="panel"><h2>Календарь</h2><div class="row"><label>Дата<input type="date" id="cd" value="\${today}"></label><div class="actions" style="align-items:end"><button onclick="closeDay(true)">Закрыть день</button><button onclick="closeDay(false)">Открыть день</button></div></div><p class="muted">Для отдельных часов:</p><div class="actions">\${[9,10,11,12,13,14,15,16].map(h=>\`<button onclick="closeHour(\${h},true)">\${h}:00 закрыть</button><button onclick="closeHour(\${h},false)">\${h}:00 открыть</button>\`).join("")}</div></div>\`}
 if(tab==="quiz"){app.innerHTML=\`<div class="panel"><h2>Квиз кожи</h2><p class="muted">В этой версии раздел подключён безопасно: данные читаются из quiz_concerns, если таблица существует. Старые данные не изменяются.</p><div class="grid">\${data.quiz.map(q=>\`<div class="card"><b>\${esc(pick(q,["name","title","concern","question"]))}</b></div>\`).join("")||"<div class=card>Пока нет данных</div>"}</div></div>\`}
}
async function saveProc(id){await act("/api/procedure",{id,name:$("#n"+id).value,price:$("#p"+id).value,description:$("#d"+id).value})}
async function closeDay(v){await act("/api/close-day",{date:$("#cd").value,closed:v})}
async function closeHour(h,v){await act("/api/close-hour",{date:$("#cd").value,hour:h,closed:v})}
document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>{window.tab=b.dataset.tab;render()});
$("#logout").onclick=async()=>{await fetch("/api/logout");location="/login"};
get().then(render).catch(e=>app.innerHTML='<div class="error">'+esc(e.message)+'</div>');
</script></body></html>`;
}

export default {
 async fetch(req, env){
  const url=new URL(req.url);
  try{
    if(!env.DB) return new Response("D1 binding DB is missing",{status:500});
    if(url.pathname.startsWith("/api/")) return api(req,env,url);
    if(url.pathname==="/login" && req.method==="POST"){
      const f=await req.formData(), u=String(f.get("user")||""), p=String(f.get("password")||"");
      if(u!==String(env.ADMIN_USER||"") || p!==String(env.ADMIN_PASSWORD||"")) return new Response(loginPage("Неверный логин или пароль"),{headers:{"content-type":"text/html;charset=utf-8"}});
      await ensure(env.DB); const token=rand();
      await env.DB.prepare(`INSERT INTO admin_sessions(token,expires_at) VALUES(?,datetime('now','+7 days'))`).bind(token).run();
      return new Response(shell(),{headers:{"content-type":"text/html;charset=utf-8","set-cookie":cookie("va_session",token)}});
    }
    if(url.pathname==="/login" || !(await authorized(req,env))) return new Response(loginPage(),{headers:{"content-type":"text/html;charset=utf-8"}});
    return new Response(shell(),{headers:{"content-type":"text/html;charset=utf-8","cache-control":"no-store"}});
  }catch(e){
    return new Response(`<!doctype html><meta charset="utf-8"><style>body{font-family:Arial;background:#160f1c;color:#f3ebe1;padding:30px}pre{white-space:pre-wrap;color:#ffb8c2}</style><h1>Vasilisa Admin — ошибка</h1><pre>${esc(e.stack||e.message||e)}</pre>`,{status:500,headers:{"content-type":"text/html;charset=utf-8","cache-control":"no-store"}});
  }
 }
};
