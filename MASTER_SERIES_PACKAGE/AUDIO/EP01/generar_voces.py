"""Generación secuencial; máximo dos solicitudes por línea, registro persistente."""
import time
import os,json,base64,urllib.request,urllib.error,wave,io
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LINES=[('L01','ALBA','Gacrux','¿Qué has hecho?','Seca, alarmada, voz baja.',2),('L02','INES','Kore','Solo agua. Para quitar la sal.','Técnica, a la defensiva, contenida.',2.5),('L03','INES','Kore','Lleva doce años en una bolsa.','Cansada, casi para sí misma.',3.5),('L04','MARA','Vindemiatrix','<breath> Inés. Quédate donde estás.','Susurro cercano, tenso, respiración difícil sin exagerar.',4),('L05','ALBA','Gacrux','No la escuches.','Orden urgente, miedo contenido.',2),('L06','INES','Kore','Es mi hermana.','Asombro contenido, voz baja.',2.5),('L07','INES','Kore','Es Mara.','Muy baja, certeza.',2),('X01','MARA','Vindemiatrix','<breath>','Una sola inhalación lenta y cercana, sin palabras, sin agonía.',2),('X02','MARA','Vindemiatrix','<breath> Inés. Quédate donde estás.','Susurro muy cercano, más aire, muy bajo, tensión contenida.',4)]
def main():
 key=os.environ['GEMINI_API_KEY']; log=ROOT/'generacion.json'; records=json.loads(log.read_text()) if log.exists() else []
 for id,person,voice,txt,style,secs in LINES:
  old=[r for r in records if r['id']==id]
  if any(r.get('file') for r in old) or len(old)>=2: continue
  n=len(old)+1; record={'id':id,'take':n,'model':'gemini-3.8-flash-tts','voice':voice,'text':txt,'style':style,'target_seconds':secs,'status':'requested'}
  records.append(record);log.write_text(json.dumps(records,ensure_ascii=False,indent=2))
  body={'contents':[{'role':'user','parts':[{'text':txt,'speech_metadata':{'style':style+f' Interpretación cinematográfica natural, sin música. Duración aproximada {secs} segundos.'}}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'voice':voice}}}}
  req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent',data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=100) as resp: data=json.load(resp)
   parts=data['candidates'][0]['content']['parts']; inline=next(p['inlineData'] for p in parts if 'inlineData' in p); raw=base64.b64decode(inline['data'])
   if raw[:4]!=b'RIFF':
    buf=io.BytesIO()
    with wave.open(buf,'wb') as w: w.setparams((1,2,24000,0,'NONE','not compressed'));w.writeframes(raw)
    raw=buf.getvalue()
   with wave.open(io.BytesIO(raw)) as w: record['seconds']=w.getnframes()/w.getframerate()
   path=ROOT/'TAKES'/f'EP01_{person}_{id}_T{n}.wav';path.write_bytes(raw);record.update(file=str(path.relative_to(ROOT)),status='generated_technical_review_pending')
  except urllib.error.HTTPError as e:
   record.update(status='http_error',http=e.code,error=e.read().decode().replace(key,'[REDACTED]'))
  except Exception as e: record.update(status='error',error=type(e).__name__)
  log.write_text(json.dumps(records,ensure_ascii=False,indent=2));print(id,record['status'],record.get('http',record.get('seconds','')),flush=True)
  if record['status'] in ('http_error','error'): break
  time.sleep(25)
if __name__=='__main__':main()
