import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface BlueprintProps {
  title?: string;
  subtitle?: string;
  componentA?: string;
  statusA?: string;
  metricA?: string;
  componentB?: string;
  statusB?: string;
  metricB?: string;
  componentC?: string;
  statusC?: string;
  metricC?: string;
  blueprintTag?: string;
  theme?: "aviation" | "cyber" | "hardware" | "tech" | "space" | "universal";
}

export const VeritasiumBlueprint: React.FC<BlueprintProps> = ({
  title = "ANÁLISIS DE ARQUITECTURA Y SUBSISTEMAS",
  subtitle = "ESQUEMA DE COMPONENTES CRÍTICOS Y VECTORES DE FALLO",
  componentA = "MECANISMO DE CONTROL PRIMARIO",
  statusA = "VULNERABILIDAD AISLADA",
  metricA = "98.4% INTEGRIDAD",
  componentB = "BUS DE TRANSMISIÓN HIDRÁULICO / DATOS",
  statusB = "REDUNDANCIA ACTIVA",
  metricB = "CANAL DUAL 100%",
  componentC = "SISTEMA DE MITIGACIÓN DE EMERGENCIA",
  statusC = "OPERACIÓN NORMAL",
  metricC = "TIEMPO DE RESPUESTA 42ms",
  blueprintTag = "BLUEPRINT TÉCNICO V3 · AUTODETECCIÓN",
  theme = "aviation",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Animaciones elásticas
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.88, stiffness: 105 },
  });

  const cardOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Láser de barrido vertical que recorre el blueprint
  const scanProgress = interpolate(
    frame % 90,
    [0, 90],
    [0, 100],
    { extrapolateRight: "clamp" }
  );

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

  const components = [
    { name: componentA, status: statusA, metric: metricA, delay: 10 },
    { name: componentB, status: statusB, metric: metricB, delay: 20 },
    { name: componentC, status: statusC, metric: metricC, delay: 30 },
  ];

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

      {/* Tarjeta HUD Blueprint */}
      <div
        style={{
          width: "830px",
          backgroundColor: "rgba(10, 14, 22, 0.94)",
          borderRadius: "32px",
          border: `2px solid ${palette.border}`,
          boxShadow: `0 30px 80px rgba(0, 0, 0, 0.85), 0 0 55px ${palette.glow}`,
          padding: "36px 32px",
          display: "flex",
          flexDirection: "column",
          gap: "24px",
          opacity: cardOpacity,
          transform: `scale(${cardScale * cameraZoom})`,
          position: "relative",
          backdropFilter: "blur(24px)",
        }}
      >
        <TacticalHeader
          sector="ESQUEMA TÉCNICO · BLUEPRINT"
          status="AUDITORÍA"
          statusColor={palette.accent}
        />

        {/* Título Principal */}
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
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
              fontSize: "13px",
              fontWeight: 500,
              letterSpacing: "1px",
              color: "#94A3B8",
              textTransform: "uppercase",
            }}
          >
            {subtitle}
          </span>
        </div>

        {/* Área Técnica con Retícula Vectorial y Láser de Escaneo */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "180px",
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            borderRadius: "20px",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Malla isométrica de fondo */}
          <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.25 }}>
            <pattern id="blueprint-grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke={palette.accent} strokeWidth="1" />
            </pattern>
            <rect width="100%" height="100%" fill="url(#blueprint-grid)" />
          </svg>

          {/* Línea láser de barrido */}
          <div
            style={{
              position: "absolute",
              top: `${scanProgress}%`,
              left: 0,
              right: 0,
              height: "2px",
              backgroundColor: palette.accent,
              boxShadow: `0 0 16px ${palette.accent}, 0 0 30px ${palette.accent}`,
              zIndex: 3,
            }}
          />

          {/* Vectores e infografía interactiva en el diagrama */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              alignItems: "center",
              width: "88%",
              zIndex: 2,
            }}
          >
            {[0, 1, 2, 3].map((nodeIdx) => {
              const pulse = Math.sin((frame / 8) + nodeIdx) * 0.3 + 0.7;
              return (
                <div
                  key={nodeIdx}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "10px",
                      border: `2px solid ${palette.accent}`,
                      backgroundColor: "rgba(10, 14, 22, 0.9)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "12px",
                      fontWeight: 800,
                      color: palette.accent,
                      boxShadow: `0 0 14px ${palette.glow}`,
                      transform: `scale(${1 + (pulse - 0.7) * 0.15})`,
                    }}
                  >
                    N{nodeIdx + 1}
                  </div>
                  <span style={{ fontSize: "10px", color: "#64748B", letterSpacing: "1px" }}>
                    {(nodeIdx * 342 + frame * 3).toString(16).toUpperCase()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Desglose de 3 Subsistemas con chips de estado */}
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {components.map((c, idx) => {
            const compOpacity = interpolate(frame, [c.delay, c.delay + 14], [0, 1], {
              extrapolateRight: "clamp",
            });
            const compTranslateX = interpolate(frame, [c.delay, c.delay + 14], [-15, 0], {
              extrapolateRight: "clamp",
            });

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  backgroundColor: "rgba(18, 24, 38, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  borderRadius: "16px",
                  padding: "16px 20px",
                  opacity: compOpacity,
                  transform: `translateX(${compTranslateX}px)`,
                }}
              >
                <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                  <span style={{ fontSize: "14px", fontWeight: 700, color: "#F8FAFC" }}>
                    {c.name}
                  </span>
                  <span style={{ fontSize: "12px", fontWeight: 600, color: palette.accent }}>
                    {c.metric}
                  </span>
                </div>

                <div
                  style={{
                    padding: "6px 14px",
                    borderRadius: "8px",
                    backgroundColor: "rgba(0, 0, 0, 0.4)",
                    border: `1px solid ${palette.border}`,
                    fontSize: "11px",
                    fontWeight: 800,
                    letterSpacing: "1.2px",
                    color: "#FFFFFF",
                  }}
                >
                  {c.status}
                </div>
              </div>
            );
          })}
        </div>

        {/* Pie de Blueprint */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            paddingTop: "10px",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <span style={{ fontSize: "12px", fontWeight: 600, color: "#64748B", letterSpacing: "1px" }}>
            {blueprintTag}
          </span>
          <span style={{ fontSize: "11px", fontWeight: 700, color: palette.accent }}>
            PRECISIÓN DE PRIMEROS PRINCIPIOS
          </span>
        </div>
      </div>
    </div>
  );
};
