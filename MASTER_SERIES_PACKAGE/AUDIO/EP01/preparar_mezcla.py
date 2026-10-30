"""Prepara stems originales sintetizados y voces; no regenera ni recorta palabras."""
import json,subprocess,wave
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent; SR=48000; N=51*SR
rng=np.random.default_rng(101)
def save(path,x):
 path.parent.mkdir(exist_ok=True,parents=True)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,SR,0,'NONE','not compressed'));w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def noise(n,width):
 x=rng.normal(size=n);x=np.convolve(x,np.ones(width)/width,mode='same');return x/(np.std(x)+1e-9)
def add(dst,x,start):
 p=round(start*SR);n=min(len(x),len(dst)-p);dst[p:p+n]+=x[:n]
def rustle(seconds,amp):
 n=int(seconds*SR);t=np.arange(n)/SR;return noise(n,18)*np.sin(np.pi*np.arange(n)/n)**2*(.65+.35*np.sin(2*np.pi*7*t))*amp
room=noise(N,200)*.0012;room*=np.minimum(1,np.arange(N)/SR)*np.minimum(1,np.arange(N)[::-1]/SR)
foley=np.zeros(N);sfx=np.zeros(N);dialog=np.zeros(N)
for t,d,a in [(1,2,.006),(7.8,.7,.004),(18,.6,.004),(26,.9,.005),(30.2,1.1,.007),(39.7,.5,.004),(45.5,1.3,.006)]:add(foley,rustle(d,a),t)
t=np.arange(int(.28*SR))/SR;drop=.035*np.sin(2*np.pi*(1450*t-1100*t*t))*np.exp(-t*28);add(sfx,drop,12)
records=json.loads((R/'generacion.json').read_text());times=[6,11.5,16.5,31,38,43.5,47];qa=[]
for r in records:
 if not r.get('file'):continue
 p=R/r['file'];raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar',str(SR),'-ac','1','-']);x=np.frombuffer(raw,dtype='<f4').copy()
 peak=float(np.max(np.abs(x)));rms=float(np.sqrt(np.mean(x*x)));active=np.where(np.abs(x)>.003)[0]
 if len(active): x=x[max(0,active[0]-int(.06*SR)):min(len(x),active[-1]+int(.12*SR))]
 ratio=len(x)/SR/r['target_seconds']
 if 1 < ratio <= 1.10:
  converted=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f'atempo={ratio:.8f}','-f','f32le','pipe:1'],input=x.astype('<f4').tobytes(),capture_output=True,check=True).stdout
  x=np.frombuffer(converted,dtype='<f4').copy()
 x*=min(3,.45/max(peak,1e-8));fade=min(240,len(x)//2);x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade)
 out=R/'EDITADOS'/p.name.replace('_T1','_EDIT').replace('_T2','_EDIT');save(out,x)
 qa.append({'id':r['id'],'source':r['file'],'edited':str(out.relative_to(R)),'seconds':len(x)/SR,'tempo_ratio':ratio if 1 < ratio <= 1.10 else 1,'peak_source':peak,'rms_source':rms,'clipped_samples':int(np.sum(np.abs(np.frombuffer(raw,dtype='<f4'))>=.9999)),'fits_window':len(x)/SR<=r['target_seconds'],'review':'Technical only; performance and exact words require listening.'})
 if r['id'].startswith('L'):add(dialog,x,times[int(r['id'][1:])-1])
for name,x in [('DIALOGUE',dialog),('ROOM',room),('FOLEY',foley),('SFX',sfx)]:save(R/'STEMS'/f'EP01_{name}.wav',x)
mix=dialog+room+foley+sfx;save(R/'EP01_MEZCLA_PREVIA.wav',mix)
(R/'revision_tecnica.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False));print(json.dumps(qa,indent=2))
