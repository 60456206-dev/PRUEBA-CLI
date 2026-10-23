const status = document.getElementById('status');
document.getElementById('start').onclick = async () => {
  const [tab] = await browser.tabs.query({active:true, currentWindow:true});
  const result = await browser.runtime.sendMessage({type:'start', tabId:tab.id, token:document.getElementById('token').value.trim()});
  status.textContent = result;
  document.getElementById('token').value = '';
};
document.getElementById('stop').onclick = async () => {
  status.textContent = await browser.runtime.sendMessage({type:'stop'});
};
browser.runtime.sendMessage({type:'status'}).then(s => status.textContent = s);
