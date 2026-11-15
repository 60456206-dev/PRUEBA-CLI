import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface StatComparisonProps {
  title: string;
  subtitle: string;
  labelA?: string;
  valA?: string;
  percentA?: number;
  labelB?: string;
  valB?: string;
  percentB?: number;
  multiplierTag?: string;
  sourceTag?: string;
  theme?: "aviation" | "cyber" | "hardware" | "tech" | "space" | "universal";
}

export const VeritasiumStatComparison: React.FC<StatComparisonProps> = ({
  title = "ESCALA DE IMPACTO Y TELEMETRÍA",
  subtitle = "COMPARATIVA DE MAGNITUD TÉCNICA Y OPERATIVA",
  labelA = "PARÁMETRO BASE",
  valA = "FASE 01",
  percentA = 28,
  labelB = "UMBRAL REPORTADO",
  valB = "FASE 02",
  percentB = 94,
  multiplierTag = "COMPARATIVA TÉCNICA DOCUMENTADA",
  sourceTag = "AUDITORÍA OFICIAL REGISTRADA",
  theme = "universal",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const palette = {
    aviation: { accent: "#FFB703", gradStart: "#FB8500", glow: "rgba(251, 133, 0, 0.22)", border: "#FFB703" },
    cyber: { accent: "#FF4D6D", gradStart: "#E63946", glow: "rgba(230, 57, 70, 0.22)", border: "#FF4D6D" },
    hardware: { accent: "#00F5D4", gradStart: "#0A84FF", glow: "rgba(10, 132, 255, 0.22)", border: "#00BBF9" },
    tech: { accent: "#00F5D4", gradStart: "#0A84FF", glow: "rgba(10, 132, 255, 0.22)", border: "#00BBF9" },
    space: { accent: "#FFD166", gradStart: "#A855F7", glow: "rgba(191, 90, 242, 0.22)", border: "#FFD166" },
    universal: { accent: "#FFD166", gradStart: "#FF9F0A", glow: "rgba(255, 209, 102, 0.20)", border: "#FFD166" },
  }[theme] || { accent: "#FFD166", gradStart: "#FF9F0A", glow: "rgba(255, 209, 102, 0.20)", border: "#FFD166" };

  const curveLen = 780;
  const curveDashOffset = interpolate(frame, [10, Math.max(25, durationInFrames - 18)], [curveLen, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 1. Entrada elástica
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 13, mass: 0.85, stiffness: 105 },
  });

  const cardOpacity = interpolate(frame, [0, 14], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Movimiento de cámara continuo Veritasium (push-in continuo anti-freeze)
  const cameraZoom = 1 + frame * 0.0007;

  // 2. Animación de barras
  const progressA = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 16, mass: 1, stiffness: 80 },
  }) * percentA;

  const progressB = spring({
    frame: Math.max(0, frame - 22),
    fps,
    config: { damping: 14, mass: 1, stiffness: 90 },
  }) * percentB;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Montserrat', sans-serif",
        color: "#FFFFFF",
        padding: "110px 40px 150px",
        boxSizing: "border-box",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <ChiaroscuroBackground theme={theme} />

      {/* Tarjeta HUD Broadcast */}
      <div
        style={{
          width: "940px",
          backgroundColor: "rgba(12, 16, 24, 0.92)",
          borderRadius: "28px",
          border: `2px solid ${palette.border}`,
          boxShadow: `0 24px 70px rgba(0, 0, 0, 0.8), 0 0 45px ${palette.glow}`,
          padding: "38px 40px",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          opacity: cardOpacity,
          transform: `scale(${cardScale * cameraZoom})`,
          position: "relative",
          backdropFilter: "blur(24px)",
        }}
      >
        <TacticalHeader
          tag="EMPIRICAL METRICS · VERITASIUM ANALYSIS"
          statusLabel="VERIFIED STATISTICAL DATA"
          statusColor={palette.accent}
          accentColor={palette.accent}
        />

        {/* Título y Subtítulo */}
        <div>
          <div
            style={{
              fontSize: "30px",
              fontWeight: 900,
              letterSpacing: "0.5px",
              lineHeight: 1.22,
              marginBottom: "8px",
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontSize: "19px",
              fontWeight: 500,
              color: "rgba(255, 255, 255, 0.7)",
            }}
          >
            {subtitle}
          </div>
        </div>

        {/* Multiplicador Heroico */}
        <div
          style={{
            backgroundColor: "rgba(6, 10, 16, 0.8)",
            borderRadius: "18px",
            padding: "18px 26px",
            border: `1px solid ${palette.glow}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: "16px", fontWeight: 700, color: "rgba(255,255,255,0.6)", letterSpacing: "1.5px" }}>
            DISRUPCIÓN CUANTITATIVA
          </span>
          <span
            style={{
              fontSize: "24px",
              fontWeight: 900,
              color: palette.accent,
              fontFamily: "monospace",
              textShadow: `0 0 15px ${palette.glow}`,
            }}
          >
            {multiplierTag}
          </span>
        </div>

        {/* Curva Vectorial Animada SVG */}
        <svg width="860" height="82" viewBox="0 0 860 82" style={{ display: "block", opacity: 0.92 }}>
          <line x1="10" y1="68" x2="850" y2="68" stroke="rgba(255,255,255,0.12)" strokeWidth="1.5" strokeDasharray="6 6" />
          <path
            d="M 18 66 Q 280 62, 460 44 T 842 14"
            fill="none"
            stroke={palette.accent}
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={curveLen}
            strokeDashoffset={curveDashOffset}
          />
        </svg>

        {/* Comparativa Visual de Barras Proporcionales */}
        <div
          style={{
            backgroundColor: "rgba(6, 10, 16, 0.8)",
            borderRadius: "20px",
            padding: "28px 30px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            flexDirection: "column",
            gap: "28px",
          }}
        >
          {/* Métrica A (Referencia / Antes) */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <span style={{ fontSize: "16px", fontWeight: 700, color: "rgba(255,255,255,0.6)" }}>
                {labelA}
              </span>
              <span style={{ fontSize: "28px", fontWeight: 900, fontFamily: "monospace", color: "#A0AEC0" }}>
                {valA}
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: "22px",
                backgroundColor: "rgba(255,255,255,0.06)",
                borderRadius: "8px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(100, Math.max(2, progressA))}%`,
                  height: "100%",
                  backgroundColor: "#718096",
                  borderRadius: "8px",
                }}
              />
            </div>
          </div>

          {/* Métrica B (Salto Monumental / Ahora) */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <span style={{ fontSize: "16px", fontWeight: 800, color: palette.accent, letterSpacing: "0.5px" }}>
                {labelB}
              </span>
              <span
                style={{
                  fontSize: "34px",
                  fontWeight: 900,
                  fontFamily: "monospace",
                  color: palette.accent,
                  textShadow: `0 0 20px ${palette.glow}`,
                }}
              >
                {valB}
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: "26px",
                backgroundColor: "rgba(255,255,255,0.06)",
                borderRadius: "10px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(100, Math.max(2, progressB))}%`,
                  height: "100%",
                  background: `linear-gradient(90deg, ${palette.gradStart}, ${palette.accent})`,
                  borderRadius: "10px",
                  boxShadow: `0 0 15px ${palette.glow}`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Footer de Fuente Oficial */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "12px 18px",
            backgroundColor: "rgba(255, 255, 255, 0.04)",
            borderRadius: "12px",
            fontSize: "13px",
            fontFamily: "monospace",
            color: "rgba(255, 255, 255, 0.6)",
          }}
        >
          <span>✓ DATOS EXTRAÍDOS DE FUENTES TÉCNICAS VERIFICADAS</span>
          <span style={{ color: palette.accent, fontWeight: 700 }}>{sourceTag}</span>
        </div>
      </div>
    </div>
  );
};
