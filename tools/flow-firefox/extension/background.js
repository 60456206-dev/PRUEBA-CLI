let session = null;
let state = 'Desconectado';
const endpoint = 'http://127.0.0.1:8765';
function allowed(url) {
  const u = new URL(url);
  return u.protocol === 'https:' && (u.hostname === 'flow.google.com' || (u.hostname === 'labs.google' && u.pathname.startsWith('/fx/')));
}
async function request(s, path, data) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const response = await fetch(endpoint + path, {
      method:data === undefined ? 'GET' : 'POST',
      headers:{'Authorization':'Bearer ' + s.token, 'Content-Type':'application/json'},
      body:data === undefined ? undefined : JSON.stringify(data), signal:controller.signal
    });
    if (!response.ok) throw new Error('Conexión: HTTP ' + response.status);
    return await response.json();
  } finally {clearTimeout(timer);}
}
// Esta función se ejecuta solo en la pestaña elegida. No lee cookies ni contraseñas.
function operate(command) {
  const visible = el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden';
  if (document.querySelector('input[type=password]')) throw new Error('Página de acceso: control detenido');
  const selector = 'button,a,input,textarea,[role=button],[role=textbox],[role=option],[role=menuitem],[contenteditable=true]';
  if (command.op === 'snapshot') {
    const elements = [...document.querySelectorAll(selector)].filter(el => visible(el) || el.type === 'file');
    window.__flowLocalElements = elements;
    return {url:location.href, text:document.body.innerText.slice(0,20000), controls:elements.map((el,id) => ({
      id,tag:el.tagName,role:el.getAttribute('role'),type:el.type,
      label:el.getAttribute('aria-label'),text:(el.innerText || el.getAttribute('placeholder') || '').slice(0,250)
    }))};
  }
  const el = (window.__flowLocalElements || [])[command.id];
  if (!el || !el.isConnected) throw new Error('Control desactualizado: solicitar snapshot');
  if (command.op === 'click') {
    if (!visible(el)) throw new Error('Control oculto');
    el.click(); return 'Pulsado';
  }
  if (command.op === 'fill') {
    if (!visible(el) || el.type === 'password' || el.type === 'file') throw new Error('Campo no permitido');
    el.focus();
    if (el.isContentEditable) {
      const range=document.createRange();range.selectNodeContents(el);
      const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
      document.execCommand('insertText',false,command.text);
    } else {
      const proto=el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto,'value').set.call(el,command.text);
      el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
    }
    return 'Texto introducido';
  }
  if (command.op === 'upload') {
    if (el.type !== 'file' || command.mime !== 'image/png') throw new Error('Solo imagen PNG en selector de archivo');
    const bytes=Uint8Array.from(atob(command.base64), c=>c.charCodeAt(0));
    const transfer=new DataTransfer();transfer.items.add(new File([bytes],command.name,{type:'image/png'}));
    el.files=transfer.files;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
    return 'Imagen cargada';
  }
  throw new Error('Acción desconocida');
}
async function loop(s) {
  while (session === s) {
    try {
      const tab=await browser.tabs.get(s.tabId);
      if (!allowed(tab.url)) throw new Error('La pestaña salió de Flow');
      const job=await request(s,'/next');
      if (session !== s) break;
      if (job.id) {
        let result;
        try {
          if (!allowed((await browser.tabs.get(s.tabId)).url)) throw new Error('La pestaña salió de Flow');
          if (job.command.op === 'screenshot') {
            const current=await browser.tabs.get(s.tabId);
            if (!current.active) throw new Error('Flow debe ser la pestaña visible');
            result=await browser.tabs.captureVisibleTab(current.windowId,{format:'png'});
            const after=await browser.tabs.get(s.tabId);
            if (!after.active || !allowed(after.url)) throw new Error('Cambió la pestaña: captura descartada');
          } else {
            [result]=await browser.tabs.executeScript(s.tabId,{code:'(' + operate.toString() + ')(' + JSON.stringify(job.command) + ')'});
          }
        } catch (e) { result={error:e.message}; }
        await request(s,'/result',{id:job.id,result});
      }
      if (session === s) state='Conectado a Flow';
    } catch(e) {
      if (session === s) {session=null;state=e.message + '. Vuelve a conectar.';}
      break;
    }
    await new Promise(r=>setTimeout(r,1000));
  }
  if (!session) browser.browserAction.setBadgeText({text:''});
}
browser.runtime.onMessage.addListener(async message => {
  if (message.type === 'status') return state;
  if (message.type === 'stop') {session=null;state='Desconectado';await browser.browserAction.setBadgeText({text:''});return state;}
  if (message.type === 'start') {
    if (session) return 'Ya conectado. Pulsa Detener antes de cambiar de pestaña.';
    if (!/^[a-f0-9]{64}$/.test(message.token)) return 'Introduce la clave de conexión completa.';
    const tab=await browser.tabs.get(message.tabId);
    if (!allowed(tab.url)) return 'Abre tu proyecto de Flow y pulsa aquí de nuevo.';
    session={token:message.token,tabId:message.tabId};state='Conectando…';
    browser.browserAction.setBadgeText({text:'ON'});loop(session);return state;
  }
});
