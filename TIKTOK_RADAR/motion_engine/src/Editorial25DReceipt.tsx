import React from "react";
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  DeckledPaperCutout,
  EditorialHeadline,
  TactilePaperStage,
} from "./components/TactilePaperStage";

export interface Editorial25DReceiptProps {
  kicker?: string;
  headline?: string;
  sourceName?: string;
  publicationDate?: string;
  articleTitle?: string;
  receiptQuote?: string;
  highlightPhrase?: string;
  keyMetricBadge?: string;
  bottomTakeaway?: string;
  accentColor?: string;
  alertColor?: string;
}

/**
 * Recorte editorial 2.5D de prensa o documento verificado ("Receipt")
 * con barrido animado de resaltador amarillo sobre la frase clave real.
 */
export const Editorial25DReceipt: React.FC<Editorial25DReceiptProps> = ({
  kicker = "EVIDENCIA DOCUMENTAL",
  headline = "LO QUE CONFIRMA EL REPORTE",
  sourceName = "PRENSA OFICIAL",
  publicationDate = "REGISTRO VERIFICADO",
  articleTitle = "Reporte técnico contrastado en fuentes primarias",
  receiptQuote = "Los registros operativos confirman la detección temprana de una desviación técnica antes de comprometer el margen de seguridad.",
  highlightPhrase = "detección temprana de una desviación técnica",
  keyMetricBadge = "",
  bottomTakeaway = "LA EVIDENCIA DOCUMENTAL EXPLICA EL GIRO DEL CASO",
  accentColor = "#E5A93C",
  alertColor = "#E63946",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const headerSpring = spring({ frame, fps, config: { damping: 16, mass: 0.9, stiffness: 105 } });
  const headerY = interpolate(headerSpring, [0, 1], [24, 0]);
  const headerOpacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });

  const camT = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const sheetZoom = interpolate(camT, [0, 1], [0.97, 1.06]);
  const sheetTiltX = interpolate(camT, [0, 1], [8, 13]);
  const sheetRotZ = interpolate(camT, [0, 1], [-1.2, 0.8]);
  const sheetPanY = interpolate(camT, [0, 1], [10, -12]);

  const highlightProgress = interpolate(frame, [14, Math.min(50, Math.max(26, durationInFrames - 16))], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const bottomSpring = spring({
    frame: Math.max(0, frame - 16),
    fps,
    config: { damping: 14, mass: 0.85, stiffness: 95 },
  });
  const bottomSlideY = interpolate(bottomSpring, [0, 1], [76, 0]);
  const bottomOpacity = interpolate(frame, [16, 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Localizar la frase exacta a resaltar dentro de receiptQuote
  const cleanQuote = (receiptQuote || "").trim();
  const targetPhrase = (highlightPhrase || "").trim();
  let beforeTxt = "";
  let matchTxt = cleanQuote;
  let afterTxt = "";

  if (targetPhrase && cleanQuote) {
    const idx = cleanQuote.toLowerCase().indexOf(targetPhrase.toLowerCase());
    if (idx >= 0) {
      beforeTxt = cleanQuote.slice(0, idx);
      matchTxt = cleanQuote.slice(idx, idx + targetPhrase.length);
      afterTxt = cleanQuote.slice(idx + targetPhrase.length);
    } else {
      const words = cleanQuote.split(/\s+/);
      const cutN = Math.min(5, words.length);
      matchTxt = words.slice(0, cutN).join(" ");
      afterTxt = words.length > cutN ? " " + words.slice(cutN).join(" ") : "";
    }
  }

  const cleanBadge = (keyMetricBadge || "").trim();
  const quoteFontSize = cleanQuote.length > 140 ? 25 : cleanQuote.length > 95 ? 28 : 31;

  return (
    <TactilePaperStage accentColor="rgba(229, 169, 60, 0.14)">
      <EditorialHeadline
        kicker={kicker}
        headline={headline}
        accentColor={accentColor}
        translateY={headerY}
        opacity={headerOpacity}
        top={214}
      />

      {/* CAPA 2: RECORTE DE PRENSA EN PAPEL ARCHIVAL 2.5D */}
      <div
        style={{
          position: "absolute",
          top: "406px",
          left: "56px",
          width: "780px",
          height: "550px",
          perspective: "1300px",
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            transform: `translate3d(0, ${sheetPanY}px, 0) scale(${sheetZoom}) rotateX(${sheetTiltX}deg) rotateZ(${sheetRotZ}deg)`,
          }}
        >
          <DeckledPaperCutout
            width={760}
            height={528}
            rotationDeg={-0.8}
            paperColor="#F4ECD8"
            seed={79}
            style={{ margin: "6px auto 0 auto" }}
          >
            {/* Lineas sutiles de papel impreso */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                height: "100%",
                justifyContent: "space-between",
                padding: "8px 12px 14px 12px",
                boxSizing: "border-box",
              }}
            >
              {/* Cabecera editorial de la fuente */}
              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "10px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <div
                      style={{
                        width: "12px",
                        height: "12px",
                        borderRadius: "50%",
                        backgroundColor: alertColor,
                      }}
                    />
                    <span
                      style={{
                        fontSize: "20px",
                        fontWeight: 900,
                        letterSpacing: "1.8px",
                        color: "#151920",
                      }}
                    >
                      {sourceName.toUpperCase()}
                    </span>
                  </div>
                  <span
                    style={{
                      fontSize: "16px",
                      fontWeight: 700,
                      letterSpacing: "1.4px",
                      color: "#5B5549",
                    }}
                  >
                    {publicationDate.toUpperCase()}
                  </span>
                </div>

                <div
                  style={{
                    height: "2px",
                    width: "100%",
                    backgroundColor: "rgba(21, 25, 32, 0.22)",
                    marginBottom: "14px",
                  }}
                />

                {/* Titular del articulo citado */}
                <div
                  style={{
                    fontSize: "22px",
                    fontWeight: 800,
                    lineHeight: 1.25,
                    color: "#2C313B",
                    marginBottom: "18px",
                  }}
                >
                  {articleTitle}
                </div>

                {/* Cita factual con resaltador amarillo animado */}
                <div
                  style={{
                    fontSize: `${quoteFontSize}px`,
                    fontWeight: 600,
                    lineHeight: 1.42,
                    color: "#181C24",
                    borderLeft: `5px solid ${alertColor}`,
                    paddingLeft: "18px",
                  }}
                >
                  <span>“{beforeTxt}</span>
                  <span
                    style={{
                      display: "inline",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      fontWeight: 900,
                      color: "#0B0E14",
                      backgroundImage: "linear-gradient(rgba(250, 204, 21, 0.72), rgba(250, 204, 21, 0.72))",
                      backgroundRepeat: "no-repeat",
                      backgroundSize: `${Math.round(highlightProgress * 100)}% 88%`,
                      backgroundPosition: "0 75%",
                      boxDecorationBreak: "clone",
                      WebkitBoxDecorationBreak: "clone",
                    }}
                  >
                    {matchTxt}
                  </span>
                  <span>{afterTxt}”</span>
                </div>
              </div>

              {/* Pie del recorte con identificador/metrica real solo si existe */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  paddingTop: "12px",
                  borderTop: "1px dashed rgba(21, 25, 32, 0.25)",
                }}
              >
                <span
                  style={{
                    fontSize: "16px",
                    fontWeight: 800,
                    letterSpacing: "1.6px",
                    color: "#5B5549",
                  }}
                >
                  ARCHIVO CONTRASTADO · DOCUMENTO VERIFICADO
                </span>
                {cleanBadge ? (
                  <span
                    style={{
                      fontSize: "19px",
                      fontWeight: 900,
                      color: "#F8F3E8",
                      backgroundColor: "#151920",
                      padding: "6px 14px",
                      borderRadius: "6px",
                      letterSpacing: "1px",
                    }}
                  >
                    {cleanBadge}
                  </span>
                ) : null}
              </div>
            </div>
          </DeckledPaperCutout>
        </div>
      </div>

      {/* CAPA 3: CINTA INFERIOR EN PIZARRA OSCURA */}
      <div
        style={{
          position: "absolute",
          left: "68px",
          top: "996px",
          transform: `translate3d(0, ${bottomSlideY}px, 0)`,
          opacity: bottomOpacity,
        }}
      >
        <DeckledPaperCutout
          width={760}
          height={166}
          rotationDeg={1.0}
          paperColor="#171D26"
          seed={83}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 900,
              letterSpacing: "2.2px",
              color: accentColor,
              marginBottom: "8px",
            }}
          >
            LECTURA CLAVE DEL CASO
          </div>
          <div
            style={{
              fontSize: bottomTakeaway.length > 48 ? "28px" : "33px",
              fontWeight: 900,
              lineHeight: 1.15,
              color: "#F8F3E8",
              letterSpacing: "-0.3px",
            }}
          >
            {bottomTakeaway}
          </div>
        </DeckledPaperCutout>
      </div>
    </TactilePaperStage>
  );
};
