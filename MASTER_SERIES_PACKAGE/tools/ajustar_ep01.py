"""Montaje EP01 V2 reproducible, solo materiales existentes. Sin llamadas API."""
from pathlib import Path
import subprocess,json,wave
import numpy as np
R=Path(__file__).resolve().parents[1]; A=R/'AUDIO/EP01'; O=A/'AJUSTE_V2'; F=R/'FINAL';O.mkdir(exist_ok=True)
SR=48000
segments=[(0,5),(5,8.5),(11,15),(16,21),(24,27.5),(30,34.75),(37,40.25),(43,49.25)]
starts=np.cumsum([0]+[b-a for a,b in segments]).tolist();duration=starts[-1];N=round(duration*SR)
def run(cmd):return subprocess.run(cmd,check=True,capture_output=True)
def read(p):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','1','-f','f32le','-']).stdout,dtype='<f4').copy()
def save(p,x):
 with wave.open(str(p),'wb') as w:w.setparams((1,2,SR,0,'NONE','not compressed'));w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def process(x,f):
 p=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0','-af',f,'-f','f32le','pipe:1'],input=x.astype('<f4').tobytes(),capture_output=True,check=True)
 return np.frombuffer(p.stdout,dtype='<f4').copy()
def add(dst,x,t):
 i=round(t*SR);n=min(len(x),len(dst)-i);dst[i:i+n]+=x[:n]
def remap(x):return np.concatenate([x[round(a*SR):round(b*SR)] for a,b in segments])
room=remap(read(A/'STEMS/EP01_ROOM.wav'));foley=np.zeros(N);sfx=np.zeros(N);dialogue=np.zeros(N)
old=read(A/'STEMS/EP01_FOLEY.wav')
# Reutilizar roces, desplazando el de la llave al cierre de dedos.
for a,b,new in [(1,3,.85),(7.8,8.5,7.5),(18,18.6,14.5),(26,26.9,18.35),(30.2,31.3,21.2),(39.7,40.2,27.9),(45.5,46.8,31.5)]:add(foley,old[round(a*SR):round(b*SR)]*.75,new)
# Gota existente, oscurecida y baja: contacto principal y escurrimientos visibles.
drop=read(A/'STEMS/EP01_SFX.wav')[12*SR:round(12.28*SR)];drop=process(drop,'lowpass=f=1800')
for t,gain in [(9.625,.65),(10.625,.25),(11.375,.18)]:add(sfx,drop*gain,t)
q=json.loads((A/'revision_tecnica.json').read_text());timings=[6,9,13,22,26.75,29.5,33];events=[]
texts=['¿Qué has hecho?','Solo agua. Para quitar la sal.','Lleva doce años en una bolsa.','Inés. Quédate donde estás.','No la escuches.','Es mi hermana.','Es Mara.']
for item,t,txt in zip([v for v in q if v['id'].startswith('L')],timings,texts):
 x=read(A/item['edited']);mara=item['id']=='L04'
 x=process(x,'highpass=f=85,lowpass=f='+('6500' if mara else '10000')+',acompressor=threshold=0.09:ratio=2:attack=8:release=100:makeup=1')
 target=-24 if mara else -22
 gain=min(10**(target/20)/max(np.sqrt(np.mean(x*x)),1e-8),.78/max(np.max(np.abs(x)),1e-8));x*=gain
 if mara:x=process(x,'aecho=0.96:1:27|53:0.045|0.025')
 save(O/f"{item['id']}.wav",x);add(dialogue,x,t);events.append({'id':item['id'],'start':t,'end':t+len(x)/SR,'text':txt})
breath=read(A/'EDITADOS/EP01_MARA_X01_EDIT.wav');breath=process(breath,'highpass=f=120,lowpass=f=5500')*.36;add(foley,breath,.9)
for x in [room,foley,sfx]:
 n=round(.15*SR);x[-n:]*=np.linspace(1,0,n)
for name,x in [('DIALOGUE',dialogue),('ROOM',room),('FOLEY',foley),('SFX',sfx)]:save(O/f'EP01_{name}_V2.wav',x)
save(O/'PREMASTER.wav',dialogue+room+foley+sfx)
p=run(['ffmpeg','-hide_banner','-i',str(O/'PREMASTER.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']);log=p.stderr.decode();meas=json.JSONDecoder().raw_decode(log[log.rfind('{'):])[0];
f='loudnorm=I=-16:TP=-1.5:LRA=9:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**meas)
run(['ffmpeg','-y','-v','error','-i',str(O/'PREMASTER.wav'),'-af',f+',volume=-0.85dB,atrim=duration='+str(duration),'-ar',str(SR),'-c:a','pcm_s24le',str(O/'EP01_MEZCLA_V2.wav')])
(O/'PREMASTER.wav').unlink()
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
srt='\n\n'.join(f"{i+1}\n{stamp(e['start'])} --> {stamp(e['end']+.1)}\n{e['text']}" for i,e in enumerate(events))+'\n'
(F/'EP01_AJUSTADO_V2.srt').write_text(srt)
manifest={'duration':duration,'segments':[{'shot':i+1,'source_in':a,'source_out':b,'start':starts[i],'end':starts[i+1]} for i,(a,b) in enumerate(segments)],'dialogue':events,'first_pass_loudness':meas}
(O/'montaje.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
filters=['[0:v]split=8'+''.join(f'[s{i}]' for i in range(8))]
for i,(a,b) in enumerate(segments):
 # Suave ajuste por cobertura, sin levantar artificialmente el negro del abrigo.
 contrast=1.025 if i in (0,5,7) else 1.015
 filters.append(f'[s{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,eq=contrast={contrast}:saturation=1.015[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(8))+"concat=n=8:v=1:a=0,subtitles="+str(F/'EP01_AJUSTADO_V2.srt')+":force_style='FontName=DejaVu Sans,FontSize=19,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=1.5,Shadow=0.5,Alignment=2,MarginV=52,MarginL=24,MarginR=24'[out]")
print('Audio/subtítulos preparados; renderizando',duration,'s',flush=True)
run(['ffmpeg','-y','-v','error','-filter_complex_threads','2','-i',str(F/'EP01_PICTURE_LOCK.mp4'),'-i',str(O/'EP01_MEZCLA_V2.wav'),'-filter_complex',';'.join(filters),'-map','[out]','-map','1:a:0','-c:v','libx264','-threads','2','-preset','medium','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(F/'EP01_AJUSTADO_V2.mp4')])
print('Render completo',flush=True)
