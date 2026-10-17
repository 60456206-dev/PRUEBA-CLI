from pathlib import Path
import json,csv,html,shutil
P=Path(__file__).resolve().parents[1]
def put(name,text):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
def s(asset,d,scale,lens,cam,action,english,end,purpose,lines=(),priority='B',state='S1',primary='Kling VIDEO 3.0',previous=None):
 return dict(asset=asset,d=d,scale=scale,lens=lens,camera=cam,action=action,english=english,end=end,purpose=purpose,lines=lines,priority=priority,state=state,primary=primary,previous=previous)
# Dialogue tuples: relative start, relative end, speaker, exact Spanish line. Off-screen coverage by design.
E=[dict(title='El abrigo',question='¿Quién respira dentro de una prenda vacía?',answer='La voz pertenece a Mara, la hermana muerta de Inés.',next='¿Está viva o queda algo de ella?',change='Inés abandona el inventario para escuchar.',shots=[
 s('COAT_START',5,'wide vertical',50,'locked','El pecho del abrigo hueco se eleva una vez. Ninguna cabeza ocupa el cuello.','The empty coat chest gently expands by two centimeters, then falls once. Sleeves stay limp; hanger stays fixed.','Empty collar visible, coat still.','Hacer visible la anomalía antes del diálogo.',priority='A'),
 s('INES_TABLE',6,'medium close-up',85,'slow push-in 8 cm','Inés retira el pincel húmedo de fuera de campo y deja de respirar un instante.','Ines lowers her gaze briefly, then fixes it off-screen left. Her lips remain closed; one shallow breath lifts her shoulders.','Eyes fixed left; shoulders settle.','Anclar fenómeno a una persona.',[(1,3,'ALBA OFF','¿Qué has hecho?')],primary='MiniMax-Hailuo-2.3'),
 s('SALT_DROP',5,'macro insert',100,'locked','Gota suspendida sobre un borde ya húmedo; el pincel sale del plano.','A single clear droplet falls from the glass pipette onto the white salt crust. Only a coin-sized patch darkens.','One wet patch; remaining salt intact.','Explicar causa física mínima.',[(0.5,3,'INÉS OFF','Solo agua. Para quitar la sal.')],priority='A'),
 s('ALBA_DOOR',8,'medium',50,'locked','Alba no mira a Inés. Mira el abrigo. Su mano baja fuera de cuadro.','Alba looks off-screen right, lowers her chin slightly and keeps her mouth closed. Her hands remain below frame.','Chin lowered, eyes fixed right.','Mostrar reconocimiento anterior al de Inés.',[(0.5,4,'INÉS OFF','Lleva doce años en una bolsa.')]),
 s('KEY_HAND',6,'insert',85,'locked','La mano de Alba se cierra alrededor de una llave negra.','The older woman slowly closes her fingers over the single black iron key resting in her palm. Keep all five fingers distinct.','Key hidden inside closed hand.','Sembrar llave mediante ironía dramática.',priority='A'),
 s('COAT_COLLAR',7,'close-up',85,'slow push-in 5 cm','El cuello vacío permanece abierto. Se oye una voz a la altura del tejido.','The empty rust coat collar remains completely hollow. One small fold trembles and settles.','Hollow collar unchanged; no body appears.','Entregar prueba acústica.',[(1,5,'MARA / TELA','Inés. Quédate donde estás.')],priority='A'),
 s('INES_TABLE',6,'close-up',85,'locked','Inés reconoce la voz. Su mandíbula afloja; no sonríe.','Ines holds her gaze left. Her jaw relaxes slightly, her lower eyelids tighten; mouth stays closed.','Recognition without a smile.','Reconocimiento sin diálogo explicativo.',[(1,3,'ALBA OFF','No la escuches.')],primary='MiniMax-Hailuo-2.3'),
 s('COAT_START',8,'medium wide',50,'locked','La manga vacía permanece a la altura de una mano que ya no está.','The empty coat hangs motionless. A tiny residual sway fades without another breathing cycle.','Coat at rest, no second breath.','Identificar relación y abrir esperanza peligrosa.',[(0.5,3,'INÉS OFF','Es mi hermana.'),(4,6,'INÉS OFF','Es Mara.')],priority='A')]),
 dict(title='Una sola vez',question='¿Puede responder Mara?',answer='No: es un registro finito que una grabadora sí conserva.',next='¿Quién cerró cuando aún había gente?',change='Inés guarda una prueba reproducible.',shots=[
 s('SALT_USED',5,'extreme close-up',100,'locked','Inés moja de nuevo la zona limpia. No sucede nada.','One drop lands on an already dark wet patch of wool. No salt appears, no fabric inflation occurs.','Wet patch remains silent.','Pagar de inmediato duda sobre comunicación.',[(0.5,3,'INÉS OFF','Mara. ¿Me oyes?')],priority='A',state='S1'),
 s('INES_TABLE',7,'medium close-up',50,'locked','Inés espera una respuesta y mira hacia la grabadora.','Ines waits, then moves only her eyes downward toward the table. Her lips remain closed.','Eyes lowered toward recorder.','Hacer duelo de la falsa esperanza.',[(1,4,'ALBA OFF','No vuelve. Ya no está.')],state='S1'),
 s('RECORDER',5,'insert',85,'locked','Un dedo pulsa el botón de grabación.','A single index finger presses the recorder record button once, then leaves frame. The recorder stays fixed on the wood.','Recorder running; red status light.','Preparar solución antes del final.',state='S1'),
 s('SALT_DROP',8,'macro',100,'locked','Una gota toca sal intacta junto a la zona gastada.','A clear drop touches untouched salt beside a damp patch. A small white edge dissolves gradually into the wool.','Two adjacent wet zones with dry salt beyond.','Demostrar consumo por zonas.',[(1,6,'MARA / TELA','Son las seis y diez. Han cerrado. Seguimos aquí.')],priority='A',state='S2'),
 s('ALBA_DOOR',6,'close-up',85,'locked','Dos golpes y un arrastre metálico. Alba aprieta la mandíbula.','Alba hears a sound off-screen and tightens her jaw once. Keep her mouth closed and posture still.','Jaw tense, gaze right.','Hacer reconocible el motivo de la compuerta.',state='S2',primary='MiniMax-Hailuo-2.3'),
 s('RECORDER',7,'insert',85,'locked','El mismo sonido se oye desde el pequeño altavoz de la grabadora.','The recorder stays perfectly still. Its status light changes from red to green once. No camera movement.','Playback status green.','Probar que el sonido puede copiarse.',[(1,6,'MARA / PLAYBACK','Son las seis y diez. Han cerrado. Seguimos aquí.')],priority='A',state='S2'),
 s('SALT_USED',6,'macro',100,'locked','La sal consumida no reaparece. El resto del borde espera.','The wet wool patch remains dark and motionless. Focus moves gently from the used patch to the intact white salt beside it.','Dry salt in focus, used patch soft.','Cerrar regla con imagen.',[(0.5,4,'INÉS OFF','La tela se calla. La grabación no.')],state='S2'),
 s('REPORT_TOP',8,'top-down insert',50,'locked','El informe fija evacuación completa a las 18:00. Una grabación habla diez minutos después.','The old paper remains flat on the table. Only a faint shadow shifts at its lower edge. Preserve all geometry.','Report flat, upper section fully visible.','Contradecir oficialmente el accidente.',[(1,6,'INÉS OFF','Aquí pone que a las seis ya no quedaba nadie.')],priority='A',state='S2')]),
 dict(title='La llave',question='¿Quién controlaba la compuerta?',answer='Alba figura como responsable y conserva la llave.',next='¿Qué estaba protegiendo?',change='Inés convierte sospecha en acusación directa.',shots=[
 s('KEY_TABLE',5,'overhead insert',85,'locked','Una llave negra está sobre el dibujo de una compuerta.','The single black iron key lies still across a simple mechanical drawing on paper. Subtle focus settles on its asymmetric teeth.','Key teeth sharp.','Objeto concreto sustituye explicación.',priority='A',state='S2'),
 s('ALBA_DOOR',7,'medium',50,'locked','Alba mantiene la salida a su espalda.','Alba stands rigidly before the green door, eyes directed right. Her mouth stays closed; cardigan does not change.','She still occupies the doorway.','La madre retiene control espacial.',[(1,5,'INÉS OFF','¿Por qué guardabas la llave de la compuerta?')],state='S2'),
 s('REPORT_TOP',6,'POV insert',50,'locked','Bajo la hora aparece responsable: Alba Vidal. La zona de firmas queda fuera de cuadro.','Keep the paper completely flat. Camera makes a very small controlled downward move, stopping before the lower signature area.','Responsibility row centered; signatures not shown.','Vincular llave y documento sin ocultación arbitraria.',[(0.5,4,'ALBA OFF','Yo llevaba las llaves. Eso ya lo sabes.')],state='S2'),
 s('INES_TABLE',8,'close-up',85,'slow push-in 8 cm','Inés aparta la mirada del borde inferior del acta antes de levantarla hacia Alba.','Ines looks down briefly, swallows once, then looks off-screen left. Keep lips closed.','Eyes left, throat settled.','Sembrar la vergüenza de su firma.',[(1,4,'ALBA OFF','No busques solo mi nombre.')],state='S2'),
 s('SALT_DROP',5,'macro',100,'locked','Inés libera otro fragmento con una gota.','A drop touches a narrow unused white salt strip. A small patch turns dark; the surrounding wool stays still.','Third wet zone, remaining central strip white.','La protagonista investiga activamente.',priority='B',state='S3'),
 s('COAT_COLLAR',8,'close-up',85,'locked','Mara reconoce a quien está al otro lado de la puerta.','The hollow coat collar stays open. A tiny vibration moves down one lapel and stops.','Lapel still, collar empty.','Acusación desde evidencia, no intuición.',[(1,6,'MARA / TELA','Mamá. Te oigo al otro lado. Abre.')],priority='A',state='S3'),
 s('ALBA_DOOR',6,'close-up',85,'locked','Alba cierra los ojos una vez, pero no niega.','Alba closes her eyes slowly, holds them shut for one second, then opens them without moving her head. Mouth closed.','Eyes open, gaze lowered.','Negativa ya imposible.',state='S3',primary='MiniMax-Hailuo-2.3'),
 s('TWO_SHOT',8,'two-shot in depth',35,'locked','Inés y Alba quedan separadas por el abrigo. Inés no se acerca.','The two women remain still on opposite sides of the empty coat. The younger woman subtly raises her chin. No one crosses the room.','Coat separates both women; door behind Alba.','Convertir hallazgo en pregunta moral.',[(1,4,'INÉS OFF','La oíste.'),(5,7,'INÉS OFF','Y no abriste.')],priority='A',state='S3')]),
 dict(title='La otra hija',question='¿Por qué Alba cerró?',answer='Quiso proteger la sala donde estaba Inés y luego falseó lo ocurrido.',next='¿Qué responsabilidad tiene la hija salvada?',change='La confesión destruye el relato familiar del accidente.',shots=[
 s('KEY_HAND',5,'insert',85,'locked','La mano se abre: la llave deja una marca en la palma.','The older woman slowly opens her closed hand to reveal the black key. Keep the key supported by the palm, fingers anatomically distinct.','Palm open; key visible.','Invertir el gesto secreto de EP01.',priority='A',state='S3'),
 s('INES_TABLE',8,'close-up',85,'locked','Inés recibe una confesión fuera de campo.','Ines stays very still and looks left. Her breathing pauses then resumes quietly. Mouth closed.','Eyes fixed left.','Escuchar costo antes de juzgar.',[(0.5,6.5,'ALBA OFF','El agua iba hacia la sala norte. Tú estabas allí.')],priority='A',state='S3'),
 s('TWO_SHOT',7,'wide in depth',35,'locked','Alba pone una mano en la puerta actual, sin cerrarla.','Alba rests her fingertips against the green door beside her. Ines remains still near the table. The coat never moves.','Alba touches door; Ines distant.','Presente encarna la decisión pasada.',[(0.5,5,'ALBA OFF','Cerré para que no te alcanzara.')],state='S3'),
 s('ALBA_DOOR',8,'close-up',85,'slow push-in 8 cm','Alba escucha la pregunta que no quería oír.','Alba looks right; her eyelids tighten and her chin lowers a few millimeters. Lips closed, no tears falling.','Chin slightly down, eyes wet but controlled.','Separar motivo de justificación.',[(1,5,'INÉS OFF','¿Sabías que Mara seguía dentro?')],priority='A',state='S3'),
 s('INES_TABLE',5,'close-up',85,'locked','Inés recibe el sí, sin apartar la mirada.','Ines keeps looking left. One small muscle near her jaw tightens. No head turn, no speaking.','Gaze sustained.','Dar respuesta sin cliffhanger falso.',[(1,2,'ALBA OFF','Sí.')],priority='A',state='S3'),
 s('COAT_COLLAR',8,'close-up',85,'locked','El cuello vacío ocupa el lugar de la tercera persona.','The coat collar remains hollow and completely motionless. Hold the frame without camera motion.','Empty collar unchanged.','No convertir a Mara en argumento de ninguna.',[(1,4,'ALBA OFF','No podía perderos a las dos.'),(5,7,'INÉS OFF','La perdiste tú. A mí me mentiste.')],state='S3'),
 s('ALBA_DOOR',6,'medium close-up',50,'locked','Alba baja los ojos hacia el informe fuera de campo.','Alba slowly lowers her gaze toward the table, keeping her mouth closed.','Gaze downward.','Transferir pregunta hacia responsabilidad de Inés.',state='S3',primary='MiniMax-Hailuo-2.3'),
 s('REPORT_FULL',8,'overhead insert',50,'locked','La firma de Inés aparece al pie del acta.','The complete old report lies flat. A soft foreground shadow retreats, exposing the lower section. No fingers cover the signature area.','Whole page visible.','Pagar pista de firma y abrir decisión final.',[(1,6,'ALBA OFF','Yo cerré la puerta. Tú firmaste que no quedaba nadie.')],priority='A',state='S3')]),
 dict(title='Mi firma',question='¿Entregará Inés una prueba que también la acusa?',answer='Reconoce que firmó sin comprobar y decide conservar la página completa.',next='¿Quedará tiempo de registrar lo que falta antes de consumir la sal?',change='Inés pasa de acusadora a testigo implicada.',shots=[
 s('REPORT_FULL',5,'extreme close-up insert',85,'locked','Nombre y frase falsa comparten cuadro.','Hold the paper flat and still. Keep the signature and evacuation statement unobstructed. No new marks appear.','Signature unobstructed.','La protagonista no puede salir del documento.',[(0.5,3,'INÉS OFF','Me dijiste que habías comprobado.')],priority='A',state='S3'),
 s('ALBA_DOOR',7,'close-up',85,'locked','Alba escucha la admisión; esta vez no interviene.','Alba holds a quiet gaze right. Her shoulders drop slightly. Mouth closed.','Shoulders lowered.','No absolver a Inés con desconocimiento.',[(0.5,5.5,'INÉS OFF','Y yo firmé. Sin mirar. Me acuerdo.')],state='S3'),
 s('PHONE',6,'top-down insert',50,'locked','El móvil muestra una foto recortada sin la firma.','The black smartphone lies motionless on the wooden table. Keep its rectangular screen and all edges rigid.','Phone remains fixed.','Materializar tentación de editar verdad.',[(1,4,'ALBA OFF','Puedes mandar solo la grabación.')],priority='A',state='S3'),
 s('INES_TABLE',8,'close-up',85,'slow push-in 8 cm','Inés mira el recorte. Después levanta los ojos hacia el abrigo.','Ines looks down, then slowly raises her gaze off-screen left. Her lips stay closed, no smile.','Gaze meets coat height.','Elegir escuchar a Mara antes de salvarse.',state='S3'),
 s('SALT_DROP',5,'macro',100,'locked','La última franja blanca recibe agua, con la grabadora ya encendida fuera de campo.','A single drop spreads along the last narrow white salt edge. Keep all earlier patches dark.','Last salt strip beginning to dissolve.','Iniciar registro final sin mecanismo nuevo.',priority='A',state='S3'),
 s('COAT_COLLAR',8,'close-up',85,'locked','La voz ya no habla a una persona: cuenta a quienes están allí.','The empty coat collar makes one final very small pulse, then settles. No body or face appears.','Collar motionless after pulse.','Reformular el mensaje como voluntad colectiva.',[(0.5,6,'MARA / TELA','Somos siete. Si alguien oye esto, que no quite a ninguno.')],priority='A',state='S3'),
 s('RECORDER',6,'insert',85,'locked','La luz roja continúa. Inés no detiene el registro.','The recorder remains still with its red recording light steadily illuminated. No hand enters.','Recording continues.','Decisión expresada como no cortar.',[(1,4,'INÉS OFF','La página entera. Y mi nombre.')],state='S3'),
 s('SALT_USED',8,'macro',100,'slow pull-out 5 cm','Desaparece el último borde de cristales. La grabación sigue fuera de campo.','The final tiny white crystals dissolve into the wet wool. Pull back only five centimeters, keeping the same fabric patch centered.','No white crystals in this patch; wet wool still.','Peligro concreto: fuente finita, registro ya activo.',[(1,4,'MARA / TELA','Voy a decir los nombres.')],priority='A',state='S4')]),
 dict(title='Los siete',question='¿Qué queda cuando se termina la última voz?',answer='El registro completo y la responsabilidad de quienes lo entregan.',next='¿Cómo vivirán madre e hija después de decir la verdad?',change='Inés entrega audio, acta íntegra y declaración propia.',shots=[
 s('RECORDER',8,'insert',85,'locked','Desde la grabadora que sigue registrando se oyen los primeros cuatro nombres de Mara.','The recorder stays still on the table, red light steady. No hand touches it.','Recording light remains red.','Recompensar promesa de contar personas.',[(0.5,6.5,'MARA / TELA','Elena Ríos. Tomás Vera. Luz Arce. Bruno Sol.')],priority='A',state='S4'),
 s('COAT_END',7,'medium wide',50,'locked','Se oye el final de la lista; el abrigo deja de moverse para siempre.','The empty damp coat hangs completely still. No inflation, no swaying, no salt reappears.','Coat still and silent.','Nombrar hermana dentro del colectivo.',[(0.5,6,'MARA / TELA','Celia Paz. Samuel Costa. Y yo, Mara Vidal.')],priority='A',state='S4'),
 s('PHONE',6,'top-down insert',50,'locked','El recorte desaparece; ahora se ve página completa y tres adjuntos.','The black smartphone remains perfectly still on the wood. Preserve screen boundaries for later compositing.','Screen unobstructed.','Clímax: entregar también la firma.',[(0.5,5,'INÉS OFF','Firmé sin comprobar. Adjuntaré mi declaración.')],priority='A',state='S4'),
 s('ALBA_DOOR',7,'medium close-up',50,'locked','Alba se aparta unos centímetros del eje de la puerta.','Alba makes one small sideways step, fifteen centimeters, clearing the door center. Mouth closed, gaze right.','Door center clear; Alba beside it.','Devolver decisión y salida a Inés.',[(1,4,'INÉS OFF','No voy a quitar tu nombre.')],state='S4'),
 s('PHONE',5,'insert',85,'locked','La pantalla cambia a entrega confirmada; no hay celebración.','Keep phone, table and lighting absolutely motionless. No finger enters frame.','Screen steady for sent confirmation overlay.','Acción irreversible, no simple intención.',priority='A',state='S4'),
 s('KEY_TABLE',7,'insert',85,'locked','La llave queda junto al acta. Alba ya no la oculta.','The key rests on the paper. An older hand slowly withdraws out of frame, leaving the key behind.','Key alone on document.','Confesión se vuelve trazable.',[(1,5,'ALBA OFF','Deja el mío también. ¿Puedo quedarme?')],state='S4'),
 s('INES_TABLE',6,'close-up',85,'locked','Inés mira a su madre sin sonrisa. Le permite quedarse sin absolverla.','Ines keeps her gaze left, eyes moist, chin level. She exhales once through her nose, mouth closed.','Steady eyes, no smile.','Cierre emocional con condición concreta.',[(0.5,4,'MARA / PLAYBACK','Y yo, Mara Vidal.')],state='S4',primary='MiniMax-Hailuo-2.3'),
 s('COAT_END',9,'wide',35,'slow pull-out 10 cm','El abrigo inmóvil y las otras seis prendas permanecen. La voz está en la grabadora.','Slow controlled pull back ten centimeters from the completely still empty coat. Keep room geometry and the six other coats fixed.','Seven empty garments, room quiet.','Cierre de duelo; memoria fuera del objeto.',[(0.5,3,'INÉS OFF','Si no apagas eso.')],priority='A',state='S4')])]
# continuity chains: only same framing and same object state, not cross-cut camera angles.
E[3]['shots'][4]['previous']=None
# EP05 fabric consumption continues directly into the last close-up only if camera framing matches: use dedicated plate, no blind chain.
# one deliberate continuous reaction extension: EP03 SH04 is independently generated, EP04 SH05 is a fresh angle.
# Runtime reference chain across episode boundary on same recorder position:
E[5]['shots'][0]['previous']='EP05_SH07'
# End of EP05_SH07 is the recorder before the salt insert; camera returns to it with unchanged position.
ASSETS={
 'COAT_START':('SHOT_REFERENCES/COAT_START.png',[], 'PROPS/COAT_MASTER.png','Abrigo vacío entero; sal inicial. Cuello hueco y tres botones.'),
 'COAT_END':('SHOT_REFERENCES/COAT_END.png',[],'PROPS/COAT_MASTER.png','Abrigo vacío húmedo sin sal visible en borde.'),
 'COAT_COLLAR':('SHOT_REFERENCES/COAT_COLLAR.png',[],'PROPS/COAT_MASTER.png','Cuello abierto, ningún cuerpo. El borde inferior queda fuera de campo.'),
 'INES_TABLE':('SHOT_REFERENCES/INES_TABLE.png',['INES'],'','Inés a la mesa, mirada izquierda; boca cerrada; fondo cal, nada de perchas detrás de cabeza.'),
 'ALBA_DOOR':('SHOT_REFERENCES/ALBA_DOOR.png',['ALBA'],'','Alba delante de puerta norte, mirada derecha; encuadre de pecho.'),
 'SALT_DROP':('SHOT_REFERENCES/SALT_DROP.png',[],'PROPS/COAT_MASTER.png','Borde óxido con zona blanca y zona húmeda contigua; pipeta inmóvil encima.'),
 'SALT_USED':('SHOT_REFERENCES/SALT_USED.png',[],'PROPS/COAT_MASTER.png','Lana húmeda oscura y sal intacta en lateral fuera del punto usado.'),
 'KEY_HAND':('SHOT_REFERENCES/KEY_HAND.png',['ALBA'],'PROPS/KEY_MASTER.png','Una llave de hierro negro en palma, puño de cárdigan hueso.'),
 'KEY_TABLE':('SHOT_REFERENCES/KEY_TABLE.png',[],'PROPS/KEY_MASTER.png','Llave sobre plano mecánico simple sin texto generado importante.'),
 'REPORT_TOP':('SHOT_REFERENCES/REPORT_TOP.png',[],'PROPS/REPORT_MASTER.svg','Papel sobre mesa, texto crítico se superpone en edición desde SVG.'),
 'REPORT_FULL':('SHOT_REFERENCES/REPORT_FULL.png',[],'PROPS/REPORT_MASTER.svg','Página completa; nombre de Inés visible mediante overlay preparado.'),
 'RECORDER':('SHOT_REFERENCES/RECORDER.png',[],'PROPS/RECORDER_MASTER.png','Grabadora negra compacta sobre mesa; LED se corrige en post si necesario.'),
 'PHONE':('SHOT_REFERENCES/PHONE.png',[],'PROPS/PHONE_SCREEN.svg','Teléfono negro frontal cenital; pantalla se reemplaza con overlays suministrados.'),
 'TWO_SHOT':('SHOT_REFERENCES/TWO_SHOT.png',['INES','ALBA'],'PROPS/COAT_MASTER.png','Inés derecha junto mesa, Alba posterior en puerta, abrigo entre ellas.')}

def tc(sec):
 ms=round(sec*1000);return f'{ms//60000:02d}:{(ms//1000)%60:02d}.{ms%1000:03d}'
def srt_tc(sec):return '00:'+tc(sec).replace('.',',')
rows=[];all_edit=[];all_audio=[];all_check=[];outlines=[];subcount=0
for ei,ep in enumerate(E,1):
 eid=f'EP{ei:02d}';base=f'EPISODES/{eid}';clock=0;script=[];board=[];sl=[];im=[];vp=[];sound=[];edit=[];checks=[];subs=[];subtitle_n=0
 for si,sh in enumerate(ep['shots'],1):
  sid=f'{eid}_SH{si:02d}';sh.update(id=sid,episode=eid,scene='SC01',start=clock,endtime=clock+sh['d'])
  path,chars,prop,frame=ASSETS[sh['asset']];start=f'reference_frames/{sh["previous"]}_LASTFRAME.png' if sh['previous'] else path
  charpaths=[f'CHARACTERS/{c}_MASTER.png' for c in chars]
  # backup models use their native duration; trim rather than inventing a seven-second Hailuo setting.
  h_d=6 if sh['d']<=6 else 10
  backup='Kling VIDEO 3.0' if sh['primary'].startswith('MiniMax') else ('Wan2.2 TI2V-5B' if not chars and sh['asset'] in ['COAT_START','COAT_END','SALT_DROP','SALT_USED'] else 'MiniMax-Hailuo-2.3')
  inv=f'Preserve exact identity, costume, architecture, object count and lighting from the starting image. State {sh["state"]}: do not restore previously dissolved salt. No cuts, no extra people, no speech or lip movements.'
  prompt=f'{sh["d"]}-second continuous shot. {sh["english"]} {sh["scale"]} composition, natural {sh["lens"]}mm lens feel. Camera: {sh["camera"]}. Keep the diffuse west-window light and restrained warm table-lamp bounce already in the image. Realistic gravity and material weight. {inv} End with: {sh["end"]}'
  hprompt=f'{h_d}-second single take from the supplied first frame. Main visible action: {sh["english"]} Keep the framing {sh["scale"]}; {sh["camera"]}, no secondary camera movement. {sh["lens"]}mm perspective. Retain existing side light. Limit facial performance to the described small change. Complete the action by second {min(sh["d"]-1,h_d-1)} and remain still. {inv} Final pose: {sh["end"]}'
  wan=f'{sh["english"]} A continuous {sh["scale"]} shot in the same mineral-plaster archive. {sh["camera"]}. Soft window light from the existing side. Fixed architecture, stable object identity, physically weighted fabric. No cuts, no new objects, no talking. Finish at rest: {sh["end"]}'
  for model,txt in [('KLING',prompt),('HAILUO',hprompt),('WAN',wan)]:
   put(f'VIDEO_PROMPTS/{model}/{sid}_{model}.txt',txt+'\n')
  # PixVerse short fallback intentionally compact, not copied verbatim.
  pix=f'Animate only the main subject: {sh["english"]} Keep the original vertical composition and lighting. Camera stays nearly still. No transitions or added objects. End at rest. Preserve the supplied first-frame identity.'
  put(f'VIDEO_PROMPTS/PIXVERSE/{sid}_PIXVERSE.txt',pix+'\n')
  card=f'''# {sid} · generation card
DURATION: Kling {sh['d']} seconds; Hailuo {h_d} seconds, trim to {sh['d']}; Wan use workflow duration and follow split rule.
ASPECT: 9:16
INPUT IMAGE: {start}
FALLBACK STILL: {path}
REFERENCES / roles:
- {start}: COMPOSITION / START FRAME.
- LOCATIONS/ARCHIVE_MASTER.png: ENVIRONMENT, quality comparison; do not add as a second starting image.
'''+''.join(f'- {p}: IDENTITY; optional element binding in supported Kling 3.0 interface.\n' for p in charpaths)+f'''- {prop or 'None'}: PROP DESIGN / quality comparison.
PRIMARY: {sh['primary']}
BACKUP: {backup}
RESOLUTION: 1080 vertical if offered; otherwise 720-class preview; do not label upscale as native detail.
FPS: provider native; edit at 24fps.
MULTI-SHOT: OFF
AUDIO: OFF when available, otherwise mute model soundtrack in edit.
PROMPT: VIDEO_PROMPTS/KLING/{sid}_KLING.txt (contains ONLY text to paste).
HAILUO PROMPT: VIDEO_PROMPTS/HAILUO/{sid}_HAILUO.txt
WAN PROMPT: VIDEO_PROMPTS/WAN/{sid}_WAN.txt
EXPECTED END FRAME: {sh['end']}
CONTINUITY: {inv}
SAL STATE: {sh['state']}
PRIORITY: {sh['priority']}
SAVE: shots/{sid}_V1.mp4; accepted copy shots/{sid}_FINAL.mp4.
'''
  put(f'{base}/GENERATION_CARDS/{sid}.md',card)
  dialogue='\n'.join(f'  [{tc(a)}–{tc(b)} relativo] **{who}**: «{line}»' for a,b,who,line in sh['lines']) or '  Sin diálogo. Mantener acción y escucha.'
  script.append(f'### {sid} · {tc(clock)}–{tc(clock+sh["d"])}\n\nINT. ARCHIVO — TARDE CONTINUA.\n\n{sh["action"]}\n\n{dialogue}\n\nIntención: {sh["purpose"]}\n')
  audio=f'ROOM: aire de sala continuo muy bajo. FOLEY: '+('lana y respiración textil' if 'COAT' in sh['asset'] else 'gota breve' if 'SALT' in sh['asset'] else 'papel seco' if 'REPORT' in sh['asset'] else 'roce de manga, sin énfasis')
  if eid=='EP02' and si==5: audio+='; SFX: dos golpes 0.5/1.3 s y arrastre 2–3 s, misma muestra que en replay.'
  if priority:=sh['priority']=='A':audio+='; MUSIC: retirar música 0.5 s antes de revelación, mantener room tone salvo silencio subjetivo indicado.'
  transition='CUT'
  if sh['asset'] in ('REPORT_TOP','REPORT_FULL','KEY_TABLE'):transition='HARD CUT'
  if si>1 and sh['lines']:transition='L CUT' if 'PLAYBACK' in sh['lines'][0][2] else 'CUT'
  # transitions remain at exact picture cut; sound extension is described, not extra timeline time.
  board.append(f'''## {sid}
- SCENE: SC01 / archivo, tarde.
- SHOT: {sh['scale']} / {sh['lens']}mm.
- DURACIÓN: {sh['d']} s ({tc(clock)}–{tc(clock+sh['d'])}).
- COMPOSICIÓN: {frame} 9:16; elementos clave centro útil.
- PERSONAJES: {', '.join(chars) or 'ningún rostro; voces fuera de campo cuando corresponda'}.
- ACCIÓN: {sh['action']}
- CÁMARA: {sh['camera']}.
- LENTE: {sh['lens']}mm equivalente; óptica orientativa, no metadata real.
- MOVIMIENTO / MOTIVO: {sh['camera']}; {sh['purpose']}
- ILUMINACIÓN: ventana oeste difusa y lámpara mesa este; respetar frame de entrada.
- EMOCIÓN: {ep['change']}; microactuación indicada en acción, sin sollozo añadido.
- AUDIO: {audio}
- FRAME INICIAL: {start} — {frame}
- FRAME FINAL: {sh['end']}
- PROPÓSITO NARRATIVO: {sh['purpose']}
- CONTINUIDAD: {sh['state']}; {', '.join(charpaths) or 'objetos sin rostro'}; no invertir imagen.
''')
  sl.append(f'|{sid}|{sh["d"]}|{sh["scale"]}|{sh["lens"]}|{sh["camera"]}|{sh["priority"]}|{start}|')
  imgprompt=f'Use supplied character master(s) {", ".join(charpaths) or "none"} as identity only and LOCATIONS/ARCHIVE_MASTER.png as environment. Create one 9:16 photorealistic cinema start frame. {frame} {sh["scale"]}, {sh["lens"]}mm feel. The action has NOT completed: {sh["english"]} Show a physically plausible starting pose. Preserve light direction and wardrobe; state {sh["state"]}. No captions or invented letters; document and phone text is composited separately.'
  im.append(f'## {sid}\n\nUSE EXISTING: `{start}`.\n\nSolo si falla el asset, regenerar con referencias y este prompt completo:\n\n{imgprompt}\n')
  vp.append(f'## {sid}\n\n{card}\n\nSUBJECT: {frame}\nACTION: {sh["english"]}\nENVIRONMENT: archivo maestro\nCAMERA: {sh["scale"]}\nLENS: {sh["lens"]}\nMOVEMENT: {sh["camera"]}\nLIGHT: oeste difusa / mesa este\nEMOTION: acción observada, no adjetivo abstracto\nPHYSICS: gravedad y escala estables\nAUDIO: post separado\nSTART FRAME: {start}\nEND FRAME: {sh["end"]}\nCONTINUITY NOTES: {inv}\n\n### Prompt pegable\n\n{prompt}\n')
  sound.append(f'## {sid} · {tc(clock)}–{tc(clock+sh["d"])}\n\n{audio}\n\n{dialogue}\n\nVoces en OFF: mostrar al oyente u objeto, nunca pedir boca cerrada a quien se ve hablando. Los planos compartidos mantienen bocas discretas fuera del área de atención; si hay sincronía visible incorrecta sustituir por insert del abrigo.\n')
  edit.append(f'|{tc(clock)}|{tc(clock+sh["d"])}|shots/{sid}_FINAL.mp4|0–{sh["d"]} s|{transition}|{sh["purpose"]}|')
  subtitle_note=''
  for a,b,who,line in sh['lines']:
   subtitle_n+=1;subs.append(f'{subtitle_n}\n{srt_tc(clock+a)} --> {srt_tc(clock+b)}\n{line}\n');all_audio.append(f'|{eid}|{tc(clock+a)}|{tc(clock+b)}|DIALOGUE|{who}|{line}|')
  all_audio.append(f'|{eid}|{tc(clock)}|{tc(clock+sh["d"])}|FOLEY / ROOM|{sid}|{audio}|')
  steps=f'''## {sid} · {ep['title']} · {sh['d']} s útiles
1. Abrir {'Hailuo oficial' if sh['primary'].startswith('MiniMax') else 'Kling oficial'} y seleccionar Image-to-Video, modelo **{sh['primary']}**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **{h_d if sh['primary'].startswith('MiniMax') else sh['d']} s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `{start}`. {'Este archivo se obtiene del plano anterior indicado; no existe hasta aprobar ese vídeo. Si hay discontinuidad, usar '+path+'.' if sh['previous'] else 'El archivo ya pertenece al paquete.'}
4. Referencia de identidad opcional en Elements de Kling: {', '.join('`'+p+'`' for p in charpaths) or 'ninguna'}. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `{prop or 'ninguno'}`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/{'HAILUO' if sh['primary'].startswith('MiniMax') else 'KLING'}/{sid}_{'HAILUO' if sh['primary'].startswith('MiniMax') else 'KLING'}.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: {sh['end']} Identidad/ropa/eje/luz; estado de sal {sh['state']}; ningún miembro extra; movimiento único.
7. Guardar `shots/{sid}_V1.mp4`. Si cumple, copiar a `shots/{sid}_FINAL.mp4`; no borrar V1. Recortar a **{sh['d']} s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/{sid}_FINAL.mp4 reference_frames/{sid}_LASTFRAME.png --at {sh['d']-1/24:.6f}`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **{backup}**, tarjeta `{base}/GENERATION_CARDS/{sid}.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **{eid+'_SH'+str(si+1).zfill(2) if si<8 else ('EP'+str(ei+1).zfill(2)+'_SH01' if ei<6 else 'montar EP06 y comprobar temporada completa')}**.
'''
  checks.append(steps)
  row=dict(EPISODE=eid,SCENE='SC01',SHOT=sid,DURATION=sh['d'],VIDEO_MODEL=sh['primary'],BACKUP_MODEL=backup,ASPECT_RATIO='9:16',START_IMAGE=start,CHARACTER_REFERENCE='; '.join(charpaths) or '-',LOCATION_REFERENCE='LOCATIONS/ARCHIVE_MASTER.png',PROP_REFERENCE=prop or '-',PREVIOUS_FRAME=sh['previous'] or '-',VIDEO_PROMPT=prompt,CAMERA=f'{sh["scale"]}, {sh["lens"]}mm',MOTION=sh['camera'],FPS='native; timeline 24',RESOLUTION='1080 vertical target; 720-class preview',AUDIO_STRATEGY='separate dialogue/foley; mute model',EXPECTED_END_FRAME=sh['end'],CONTINUITY_CHECK=f'{sh["state"]}; face/clothes/geometry/axis/light',GENERATION_PRIORITY=sh['priority'])
  rows.append(row);clock+=sh['d']
 ep['duration']=clock
 put(f'{base}/{eid}_SCRIPT.md',f'# {eid} · {ep["title"]} · {clock}s\n\nGuion FINAL de preproducción. Diálogos exactos; voces en off sobre cobertura.\n\n'+'\n'.join(script))
 put(f'{base}/{eid}_STORYBOARD.md',f'# {eid} · storyboard técnico\n\n'+'\n'.join(board))
 put(f'{base}/{eid}_SHOTLIST.md','# Shotlist\n\n|Shot|s|Escala|Lente|Cámara|Prioridad|Start|\n|---|---|---|---|---|---|---|\n'+'\n'.join(sl))
 put(f'{base}/{eid}_IMAGE_PROMPTS.md','# Imágenes / recuperación de assets\n\n'+'\n'.join(im))
 put(f'{base}/{eid}_VIDEO_PROMPTS.md','# Vídeo / tarjetas completas\n\n'+'\n'.join(vp))
 put(f'{base}/{eid}_SOUND_DESIGN.md','# Sonido por plano\n\n'+'\n'.join(sound))
 put(f'{base}/{eid}_EDIT_PLAN.md','# Montaje\n\nProyecto 1080×1920, 24fps. Sin speed ramp. Audio separado. Cortes al cambio de información; ninguna transición añade duración. Las marcas L CUT significan cola de ambiente, no repetición de diálogo.\n\n|Entrada|Salida|Archivo|Selección fuente|Corte entrada|Motivo|\n|---|---|---|---|---|---|\n'+'\n'.join(edit))
 put(f'{base}/{eid}_SUBTITLES.srt','\n'.join(subs))
 put(f'{base}/{eid}_GENERATE_CHECKLIST.md','\n'.join(checks))
 all_check+=checks;all_edit.append(f'## {eid} · {clock}s\n\n|Entrada|Salida|Archivo|Selección fuente|Corte entrada|Motivo|\n|---|---|---|---|---|---|\n'+'\n'.join(edit))
 outlines.append(f'''## {eid} · {ep['title']} · {clock} segundos
- Hook / pregunta: {ep['question']}
- Respuesta: {ep['answer']}
- Nueva pregunta: {ep['next']}
- Cambio irreversible: {ep['change']}
- Curva: 0–{ep['shots'][0]['d']} anomalía; siguientes dos planos orientación; planos 4–5 complicación; 6–7 pago; 8 consecuencia. Esto describe este montaje, no una ley del algoritmo.
- Imagen memorable: {ep['shots'][0]['action']}
- Satisfacción propia: {ep['answer']}
''')
put('06_EPISODE_OUTLINES.md','# Episodios\n\n'+'\n'.join(outlines))
put('EDIT_TIMELINE.md','# Timeline de imagen · tiempos por episodio\n\nCada episodio empieza en 00:00.000. Concatenar en orden EP01–EP06 para cortometraje; no duplicar cliffhanger como recap.\n\n'+'\n'.join(all_edit))
put('AUDIO_TIMELINE.md','# Timeline de audio · tiempos por episodio\n\nStems: DIALOGUE, ROOM, FOLEY, SFX, MUSIC. No audio nativo obligatorio. Todas las frases y ventanas se especifican abajo.\n\n|Ep|Inicio|Fin|Pista|Fuente|Contenido|\n|---|---|---|---|---|---|\n'+'\n'.join(all_audio))
put('GENERATE_THIS_FIRST.md','# Generar la temporada, paso a paso\n\nPrimera prueba: EP01_SH01. Este checklist cubre los 48 planos. Primero leer START_HERE.md y FREE_VIDEO_TOOLS_CURRENT.md. Todos los archivos TXT de prompts contienen solo instrucciones pegables; ajustes y referencias están en tarjetas separadas. No subir hojas de contacto ni confundir referencia con fotograma inicial.\n\n'+'\n'.join(all_check))
cols=list(rows[0]);put('VIDEO_GENERATION_MATRIX.md','# Matriz completa de temporada\n\nDuración = segundos útiles de montaje. Hailuo requiere 6/10 s: ver tarjetas para duración a generar y recorte. Preferencia por modelo es hipótesis por tipo de plano, no benchmark realizado.\n\n|'+'|'.join(cols)+'|\n|'+'|'.join('---' for _ in cols)+'|\n'+'\n'.join('|'+'|'.join(str(r[c]).replace('|','/') for c in cols)+'|' for r in rows))
with (P/'VIDEO_GENERATION_MATRIX.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
put('TOOLS/season.json',json.dumps(E,ensure_ascii=False,indent=2))
put('TOOLS/assets.json',json.dumps(ASSETS,ensure_ascii=False,indent=2))
print('Built',len(rows),'shots;',sum(e['duration'] for e in E),'seconds')
