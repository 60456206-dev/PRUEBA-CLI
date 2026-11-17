import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface DocumentaryOutroProps {
  title?: string;
  subtitle?: string;
  quote?: string;
  takeaway?: string;
  sourceTag?: string;
  theme?: "aviation" | "cyber" | "hardware" | "tech" | "space" | "universal";
}

export const VeritasiumDocumentaryOutro: React.FC<DocumentaryOutroProps> = ({
  title = "CONCLUSIÓN Y PRIMEROS PRINCIPIOS",
  subtitle = "LECCIÓN TÉCNICA · SISTEMAS COMPLEJOS Y RESILIENCIA",
  quote = "La tecnología avanzada no elimina el error humano ni la incertidumbre física: diseña sistemas capaces de sobrevivir a ambos.",
  takeaway = "INGENIO Y RESILIENCIA ANTE LO IMPREVISTO",
  sourceTag = "AUDITORÍA TÉCNICA VERIFICADA · TIKTOK RADAR",
  theme = "aviation",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animaciones elásticas
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 100 },
  });

  const cardOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Animación suave de aparición para la cita
  const quoteOpacity = interpolate(frame, [18, 38], [0, 1], {
    extrapolateRight: "clamp",
  });
  const quoteTranslateY = interpolate(frame, [18, 38], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Movimiento de cámara continuo Veritasium (push-in continuo anti-freeze)
  const cameraZoom = 1 + frame * 0.0007;

  // Paleta por tema
  const palette = {
    aviation: { accent: "#FB8500", glow: "rgba(251, 133, 0, 0.25)", border: "#FFB703" },
    cyber: { accent: "#E63946", glow: "rgba(230, 57, 70, 0.25)", border: "#FF4D6D" },
    hardware: { accent: "#00F5D4", glow: "rgba(0, 245, 212, 0.25)", border: "#00BBF9" },
    tech: { accent: "#00F5D4", glow: "rgba(0, 245, 212, 0.25)", border: "#00BBF9" },
    space: { accent: "#FFD166", glow: "rgba(255, 209, 102, 0.25)", border: "#F77F00" },
    universal: { accent: "#FFD166", glow: "rgba(255, 209, 102, 0.25)", border: "#FFAA00" },
  }[theme] || { accent: "#FFD166", glow: "rgba(255, 209, 102, 0.25)", border: "#FFAA00" };

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
        padding: "250px 165px 650px 45px",
        boxSizing: "border-box",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <ChiaroscuroBackground theme={theme} />

      {/* Tarjeta Monolítica de Cierre Chiaroscuro */}
      <div
        style={{
          width: "830px",
          backgroundColor: "rgba(11, 15, 23, 0.94)",
          borderRadius: "32px",
          border: `2px solid ${palette.border}`,
          boxShadow: `0 30px 80px rgba(0, 0, 0, 0.85), 0 0 55px ${palette.glow}`,
          padding: "40px 36px",
          display: "flex",
          flexDirection: "column",
          gap: "28px",
          opacity: cardOpacity,
          transform: `scale(${cardScale * cameraZoom})`,
          position: "relative",
          backdropFilter: "blur(24px)",
        }}
      >
        <TacticalHeader
          sector={`DECONSTRUCCIÓN · ${theme.toUpperCase()}`}
          status="DOCUMENTAL"
          statusColor={palette.accent}
        />

        {/* Título Principal */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <span
            style={{
              fontSize: "19px",
              fontWeight: 800,
              letterSpacing: "3px",
              color: palette.accent,
              textTransform: "uppercase",
            }}
          >
            {title}
          </span>
          <span
            style={{
              fontSize: "14px",
              fontWeight: 500,
              letterSpacing: "1px",
              color: "#94A3B8",
              textTransform: "uppercase",
            }}
          >
            {subtitle}
          </span>
        </div>

        {/* Bloque Central de la Cita Filosófica / Primeros Principios */}
        <div
          style={{
            position: "relative",
            backgroundColor: "rgba(18, 24, 38, 0.75)",
            borderRadius: "22px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            padding: "40px 36px 36px 44px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            opacity: quoteOpacity,
            transform: `translateY(${quoteTranslateY}px)`,
          }}
        >
          {/* Comilla Decorativa Gigante Chiaroscuro */}
          <div
            style={{
              position: "absolute",
              top: "-22px",
              left: "24px",
              fontSize: "88px",
              lineHeight: "1",
              fontFamily: "Georgia, serif",
              color: palette.accent,
              opacity: 0.55,
              pointerEvents: "none",
            }}
          >
            “
          </div>

          <p
            style={{
              fontSize: "27px",
              fontWeight: 600,
              lineHeight: 1.45,
              color: "#F8FAFC",
              margin: 0,
              letterSpacing: "-0.2px",
              zIndex: 2,
            }}
          >
            {quote}
          </p>

          {/* Insignia de Primeros Principios */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              paddingTop: "14px",
              borderTop: "1px solid rgba(255, 255, 255, 0.1)",
              zIndex: 2,
            }}
          >
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: palette.accent,
                boxShadow: `0 0 14px ${palette.accent}`,
              }}
            />
            <span
              style={{
                fontSize: "14px",
                fontWeight: 700,
                letterSpacing: "1.8px",
                color: palette.accent,
                textTransform: "uppercase",
              }}
            >
              {takeaway}
            </span>
          </div>
        </div>

        {/* Pie de Página: Certificación de Fuente y Sello Oficial */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            paddingTop: "12px",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                backgroundColor: "rgba(0, 230, 118, 0.2)",
                color: "#00E676",
                fontSize: "13px",
                fontWeight: 900,
              }}
            >
              ✓
            </span>
            <span
              style={{
                fontSize: "13px",
                fontWeight: 600,
                letterSpacing: "1px",
                color: "#94A3B8",
              }}
            >
              {sourceTag}
            </span>
          </div>

          <span
            style={{
              fontSize: "12px",
              fontWeight: 700,
              letterSpacing: "2px",
              color: palette.accent,
              opacity: 0.85,
            }}
          >
            VERITASIUM STANDARD
          </span>
        </div>
      </div>
    </div>
  );
};
