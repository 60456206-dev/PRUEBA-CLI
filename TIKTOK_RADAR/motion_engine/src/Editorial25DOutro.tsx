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

export interface Editorial25DOutroProps {
  kicker?: string;
  headline?: string;
  quote?: string;
  takeaway?: string;
  sourceTag?: string;
  accentColor?: string;
  alertColor?: string;
}

/**
 * Cierre documental 2.5D en papel archival y tinta editorial.
 * Sin cajas UI ni logotipos ajenos; optimizado para Safe Zone TikTok.
 */
export const Editorial25DOutro: React.FC<Editorial25DOutroProps> = ({
  kicker = "PRIMEROS PRINCIPIOS",
  headline = "LO QUE DEJA ESTE CASO",
  quote = "Cuando un sistema complejo enfrenta lo imprevisto, la diferencia la marca el margen de seguridad diseñado antes del fallo.",
  takeaway = "INGENIERÍA Y CRITERIO ANTE LO IMPREVISTO",
  sourceTag = "FUENTE VERIFICADA",
  accentColor = "#E5A93C",
  alertColor = "#E63946",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const headerSpring = spring({ frame, fps, config: { damping: 16, mass: 0.9, stiffness: 105 } });
  const headerY = interpolate(headerSpring, [0, 1], [26, 0]);
  const headerOpacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });

  const camT = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const noteZoom = interpolate(camT, [0, 1], [0.98, 1.07]);
  const noteTiltX = interpolate(camT, [0, 1], [8, 14]);
  const noteRotZ = interpolate(camT, [0, 1], [-1.2, 0.9]);
  const notePanY = interpolate(camT, [0, 1], [12, -16]);

  const quoteSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 95 },
  });
  const quoteSlide = interpolate(quoteSpring, [0, 1], [48, 0]);
  const quoteOpacity = interpolate(frame, [8, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const highlightBar = interpolate(frame, [26, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const sealSpring = spring({
    frame: Math.max(0, frame - 34),
    fps,
    config: { damping: 15, mass: 0.85, stiffness: 95 },
  });
  const sealSlideY = interpolate(sealSpring, [0, 1], [72, 0]);
  const sealOpacity = interpolate(frame, [34, 48], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const qFontSize = quote.length > 130 ? 31 : quote.length > 95 ? 34 : 38;

  return (
    <TactilePaperStage accentColor="rgba(229, 169, 60, 0.16)">
      <EditorialHeadline
        kicker={kicker}
        headline={headline}
        accentColor={accentColor}
        translateY={headerY}
        opacity={headerOpacity}
        top={214}
      />

      {/* CAPA 2: NOTA EDITORIAL DE PAPEL ARCHIVAL EN PERSPECTIVA 2.5D */}
      <div
        style={{
          position: "absolute",
          top: "396px",
          left: "56px",
          width: "780px",
          height: "525px",
          perspective: "1300px",
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            transform: `translate3d(0, ${notePanY}px, 0) scale(${noteZoom}) rotateX(${noteTiltX}deg) rotateZ(${noteRotZ}deg)`,
          }}
        >
          <div
            style={{
              transform: `translateY(${quoteSlide}px)`,
              opacity: quoteOpacity,
            }}
          >
            <DeckledPaperCutout
              width={760}
              height={488}
              rotationDeg={-1.0}
              paperColor="#EFE5CE"
              seed={73}
              style={{ margin: "10px auto 0 auto" }}
            >
              <div
                style={{
                  position: "relative",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  padding: "14px 12px 14px 12px",
                  boxSizing: "border-box",
                }}
              >
                <div
                  style={{
                    fontSize: "94px",
                    lineHeight: 0.7,
                    fontFamily: "Georgia, serif",
                    color: alertColor,
                    opacity: 0.85,
                    marginBottom: "8px",
                  }}
                >
                  “
                </div>

                <div
                  style={{
                    fontSize: `${qFontSize}px`,
                    fontWeight: 800,
                    lineHeight: 1.28,
                    color: "#161B23",
                    letterSpacing: "-0.3px",
                  }}
                >
                  {quote}
                </div>

                <div style={{ marginTop: "20px" }}>
                  <div
                    style={{
                      width: `${highlightBar * 100}%`,
                      height: "5px",
                      backgroundColor: alertColor,
                      marginBottom: "14px",
                    }}
                  />
                  <div
                    style={{
                      fontSize: "21px",
                      fontWeight: 900,
                      letterSpacing: "1.4px",
                      color: "#7A5B2B",
                    }}
                  >
                    {takeaway}
                  </div>
                </div>
              </div>
            </DeckledPaperCutout>
          </div>
        </div>
      </div>

      {/* CAPA 3: SELLO DE FUENTE VERIFICADA EN PIZARRA OSCURA */}
      <div
        style={{
          position: "absolute",
          left: "68px",
          top: "978px",
          transform: `translate3d(0, ${sealSlideY}px, 0)`,
          opacity: sealOpacity,
        }}
      >
        <DeckledPaperCutout
          width={760}
          height={138}
          rotationDeg={0.9}
          paperColor="#171D26"
          seed={89}
        >
          <div
            style={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "18px",
              padding: "0 8px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
              <span
                style={{
                  width: "14px",
                  height: "14px",
                  borderRadius: "50%",
                  backgroundColor: accentColor,
                  display: "inline-block",
                  flexShrink: 0,
                }}
              />
              <div>
                <div
                  style={{
                    fontSize: "17px",
                    fontWeight: 800,
                    letterSpacing: "2px",
                    color: accentColor,
                    marginBottom: "4px",
                  }}
                >
                  CIERRE DOCUMENTAL
                </div>
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: 900,
                    color: "#F8F3E8",
                    letterSpacing: "0.4px",
                  }}
                >
                  {sourceTag}
                </div>
              </div>
            </div>
          </div>
        </DeckledPaperCutout>
      </div>
    </TactilePaperStage>
  );
};
