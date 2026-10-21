// Control local sobre pipe; sin puerto TCP ni exportación de la sesión.
const fs = require('node:fs');
const path = require('node:path');
const net = require('node:net');
const os = require('node:os');
const state = path.join(os.homedir(), '.local/share/master-series-flow-codespaces');
const {chromium} = require(path.join(state, 'automation/node_modules/playwright'));
const socketPath = path.join(state, 'control.sock');
(async () => {
  process.umask(0o077);
  const context = await chromium.launchPersistentContext(path.join(state,'browser'), {
    executablePath:'/usr/bin/chromium', headless:false, viewport:null,
    args:['--no-sandbox','--disable-dev-shm-usage','--start-maximized'],
    acceptDownloads:true
  });
  const downloads = path.join(state,'downloads'); fs.mkdirSync(downloads,{recursive:true,mode:0o700});
  function watch(p) {
    p.on('download', async d => {
      const name=Date.now()+'-'+path.basename(d.suggestedFilename());
      await d.saveAs(path.join(downloads,name));
    });
  }
  context.pages().forEach(watch);context.on('page',watch);
  const page = context.pages()[0] || await context.newPage();
  await page.goto('https://flow.google.com/project/df0139d1-e7fe-4650-8b3c-99aa3a94162b', {waitUntil:'domcontentloaded'});
  if(fs.existsSync(socketPath)) fs.unlinkSync(socketPath);
  let busy=false;
  const server=net.createServer(s=>{
    let input='';s.on('data', async b=>{
      input+=b.toString();if(!input.includes('\n'))return;
      if(busy){s.end(JSON.stringify({error:'busy'})+'\n');return;}busy=true;
      try{
        const q=JSON.parse(input.split('\n')[0]);
        const p=context.pages().find(p=>p.url().startsWith('https://flow.google.com/')) || context.pages()[0];
        const result=await new (Object.getPrototypeOf(async function(){}).constructor)('page','context','require',q.code)(p,context,require);
        s.end(JSON.stringify({result:result??null})+'\n');
      }catch(e){s.end(JSON.stringify({error:e.message})+'\n');}finally{busy=false;}
    });
  });
  server.listen(socketPath,()=>fs.chmodSync(socketPath,0o600));
  async function close(){server.close();await context.close();try{fs.unlinkSync(socketPath)}catch{}process.exit(0);}
  process.on('SIGTERM',close);process.on('SIGINT',close);
})();
