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

export interface Editorial25DFactSheetProps {
  kicker?: string;
  headline?: string;
  mode?: "metric" | "comparison";
  heroValue?: string;
  heroUnit?: string;
  heroCaption?: string;
  leftLabel?: string;
  leftValue?: string;
  leftRatio?: number;
  rightLabel?: string;
  rightValue?: string;
  rightRatio?: number;
  sourceStamp?: string;
  bottomTakeaway?: string;
  accentColor?: string;
  alertColor?: string;
}

/**
 * Lamina editorial 2.5D de evidencia y magnitud tecnica (sin cajas UI de dashboard).
 * Disenada para lectura instantanea en telefono dentro de la Safe Zone de TikTok.
 */
export const Editorial25DFactSheet: React.FC<Editorial25DFactSheetProps> = ({
  kicker = "DATO VERIFICADO",
  headline = "LA CIFRA QUE EXPLICA EL CASO",
  mode = "comparison",
  heroValue = "CONTENCIÓN",
  heroUnit = "PROTOCOLO ACTIVO",
  heroCaption = "PARÁMETRO REPORTADO EN LA INVESTIGACIÓN OFICIAL",
  leftLabel = "PLAN PREVISTO",
  leftValue = "OPERACIÓN NORMAL",
  leftRatio = 38,
  rightLabel = "EVENTO REAL",
  rightValue = "ACCIÓN CORRECTIVA",
  rightRatio = 86,
  sourceStamp = "FUENTE VERIFICADA",
  bottomTakeaway = "LOS DATOS CONFIRMAN UN CAMBIO DECISIVO",
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
  const sheetZoom = interpolate(camT, [0, 1], [0.98, 1.07]);
  const sheetTiltX = interpolate(camT, [0, 1], [9, 14]);
  const sheetRotZ = interpolate(camT, [0, 1], [-1.3, 1.1]);
  const sheetPanY = interpolate(camT, [0, 1], [10, -14]);

  const barA =
    spring({ frame: Math.max(0, frame - 14), fps, config: { damping: 15, mass: 0.9, stiffness: 90 } }) *
    Math.max(10, Math.min(100, leftRatio));
  const barB =
    spring({ frame: Math.max(0, frame - 24), fps, config: { damping: 14, mass: 0.9, stiffness: 95 } }) *
    Math.max(10, Math.min(100, rightRatio));

  const curveDraw = interpolate(frame, [10, Math.max(54, durationInFrames - 24)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const bottomSpring = spring({
    frame: Math.max(0, frame - 18),
    fps,
    config: { damping: 14, mass: 0.85, stiffness: 95 },
  });
  const bottomSlideY = interpolate(bottomSpring, [0, 1], [86, 0]);
  const bottomOpacity = interpolate(frame, [18, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const heroFontSize = heroValue.length > 14 ? 50 : heroValue.length > 9 ? 68 : 108;
  const hasNumericPair = /\d/.test(leftValue || "") && /\d/.test(rightValue || "");

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

      {/* CAPA 2: HOJA ARCHIVAL EN PERSPECTIVA 2.5D */}
      <div
        style={{
          position: "absolute",
          top: "412px",
          left: "56px",
          width: "780px",
          height: "510px",
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
            height={476}
            rotationDeg={-0.7}
            paperColor="#171D26"
            seed={53}
            style={{ margin: "10px auto 0 auto" }}
          >
            {/* Lineas pautadas de expediente editorial */}
            <svg
              width="708"
              height="430"
              viewBox="0 0 708 430"
              style={{ position: "absolute", left: "26px", top: "22px", pointerEvents: "none" }}
            >
              {[86, 172, 258, 344].map((yPos) => (
                <line
                  key={yPos}
                  x1="0"
                  y1={yPos}
                  x2="708"
                  y2={yPos}
                  stroke="rgba(239, 229, 206, 0.08)"
                  strokeWidth="1.2"
                  strokeDasharray="6 8"
                />
              ))}
              {/* Trazo de tendencia ascendente/inflexion (solo en modo metric para no cruzar barras) */}
              {mode === "metric" && (
                <path
                  d="M 16 292 C 210 282, 410 232, 690 158"
                  fill="none"
                  stroke={accentColor}
                  strokeWidth="4.5"
                  strokeLinecap="round"
                  pathLength={1}
                  strokeDashoffset={1 - curveDraw}
                  opacity="0.72"
                />
              )}
            </svg>

            {mode === "metric" ? (
              <div
                style={{
                  position: "relative",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  padding: "16px 10px 24px 10px",
                  boxSizing: "border-box",
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: "20px",
                      fontWeight: 800,
                      letterSpacing: "2.4px",
                      color: accentColor,
                      marginBottom: "18px",
                    }}
                  >
                    {heroUnit}
                  </div>
                  <div
                    style={{
                      fontSize: `${heroFontSize}px`,
                      fontWeight: 900,
                      lineHeight: 1.03,
                      color: "#F8F3E8",
                      letterSpacing: "-1px",
                      textShadow: "0 8px 24px rgba(0, 0, 0, 0.7)",
                    }}
                  >
                    {heroValue}
                  </div>
                </div>

                <div
                  style={{
                    fontSize: "25px",
                    fontWeight: 700,
                    lineHeight: 1.3,
                    color: "#CBD5E1",
                    maxWidth: "660px",
                    backgroundColor: "rgba(11, 16, 24, 0.72)",
                    padding: "14px 18px",
                    borderLeft: `5px solid ${alertColor}`,
                  }}
                >
                  {heroCaption}
                </div>
              </div>
            ) : hasNumericPair ? (
              <div
                style={{
                  position: "relative",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  gap: "38px",
                  padding: "10px 10px 36px 10px",
                  boxSizing: "border-box",
                }}
              >
                {/* Franja A */}
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      marginBottom: "10px",
                      gap: "12px",
                    }}
                  >
                    <span style={{ fontSize: "20px", fontWeight: 800, letterSpacing: "1.6px", color: "#B8C0CC" }}>
                      {leftLabel}
                    </span>
                    <span style={{ fontSize: "30px", fontWeight: 900, color: "#EFE5CE" }}>{leftValue}</span>
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: "30px",
                      backgroundColor: "rgba(239, 229, 206, 0.10)",
                      borderRadius: "4px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${barA}%`,
                        height: "100%",
                        backgroundColor: "#94A3B8",
                      }}
                    />
                  </div>
                </div>

                {/* Franja B */}
                <div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      marginBottom: "10px",
                      gap: "12px",
                    }}
                  >
                    <span style={{ fontSize: "20px", fontWeight: 800, letterSpacing: "1.6px", color: accentColor }}>
                      {rightLabel}
                    </span>
                    <span style={{ fontSize: "34px", fontWeight: 900, color: accentColor }}>{rightValue}</span>
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: "34px",
                      backgroundColor: "rgba(239, 229, 206, 0.10)",
                      borderRadius: "4px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${barB}%`,
                        height: "100%",
                        background: `linear-gradient(90deg, ${accentColor}, ${alertColor})`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div
                style={{
                  position: "relative",
                  height: "100%",
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "stretch",
                  gap: "24px",
                  padding: "22px 12px 26px 12px",
                  boxSizing: "border-box",
                }}
              >
                {/* Bloque cualitativo A (sin barras porcentuales inventadas) */}
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    padding: "22px 20px",
                    backgroundColor: "rgba(239, 229, 206, 0.06)",
                    borderTop: "5px solid #94A3B8",
                  }}
                >
                  <div style={{ fontSize: "17px", fontWeight: 800, letterSpacing: "1.8px", color: "#94A3B8", marginBottom: "14px" }}>
                    {leftLabel}
                  </div>
                  <div style={{ fontSize: leftValue.length > 16 ? "32px" : "38px", fontWeight: 900, lineHeight: 1.12, color: "#EFE5CE" }}>
                    {leftValue}
                  </div>
                </div>

                {/* Divisor central */}
                <div style={{ width: "2px", backgroundColor: "rgba(239, 229, 206, 0.18)", margin: "12px 0" }} />

                {/* Bloque cualitativo B */}
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    padding: "22px 20px",
                    backgroundColor: "rgba(229, 169, 60, 0.09)",
                    borderTop: `5px solid ${accentColor}`,
                  }}
                >
                  <div style={{ fontSize: "17px", fontWeight: 800, letterSpacing: "1.8px", color: accentColor, marginBottom: "14px" }}>
                    {rightLabel}
                  </div>
                  <div style={{ fontSize: rightValue.length > 16 ? "32px" : "38px", fontWeight: 900, lineHeight: 1.12, color: "#F8F3E8" }}>
                    {rightValue}
                  </div>
                </div>
              </div>
            )}
          </DeckledPaperCutout>
        </div>
      </div>

      {/* CAPA 3: CINTA INFERIOR DE EVIDENCIA EN PAPEL CREMA */}
      <div
        style={{
          position: "absolute",
          left: "68px",
          top: "980px",
          transform: `translate3d(0, ${bottomSlideY}px, 0)`,
          opacity: bottomOpacity,
        }}
      >
        <DeckledPaperCutout
          width={760}
          height={186}
          rotationDeg={1.1}
          paperColor="#EFE5CE"
          seed={61}
        >
          <div
            style={{
              fontSize: "19px",
              fontWeight: 900,
              letterSpacing: "2.2px",
              color: alertColor,
              marginBottom: "10px",
            }}
          >
            {sourceStamp}
          </div>
          <div
            style={{
              fontSize: bottomTakeaway.length > 48 ? "30px" : "35px",
              fontWeight: 900,
              lineHeight: 1.14,
              color: "#151920",
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
