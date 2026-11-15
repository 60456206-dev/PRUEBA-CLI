import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface TechChipProps {
  title: string;
  subtitle: string;
  nodeSize?: string;
  transistorCount?: string;
  efficiencyGain?: string;
  architectureTag?: string;
}

export const VeritasiumTechChip: React.FC<TechChipProps> = ({
  title = "ARQUITECTURA DE SILICIO 2NM",
  subtitle = "LITOGRAFÍA EXTREMA EUV Y COMPUESTOS CUÁNTICOS",
  nodeSize = "2 NM",
  transistorCount = "33.7 BILLONES",
  efficiencyGain = "+30% EFICIENCIA / +15% VELOCIDAD",
  architectureTag = "GAA NANOSHEET 3D",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Entrada elástica de tarjeta
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

  // 2. Pulso de láser EUV (13.5 nm)
  const laserPulse = (Math.sin(frame * 0.35) * 0.5 + 0.5);
  const busFlow = (frame * 6) % 100;

  // 3. Crecimiento dinámico de la barra de potencia de cálculo
  const barProgress = interpolate(frame, [15, durationInFrames - 20], [10, 94], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
      <ChiaroscuroBackground theme="tech" />

      {/* Tarjeta HUD Broadcast */}
      <div
        style={{
          width: "940px",
          backgroundColor: "rgba(10, 15, 26, 0.92)",
          borderRadius: "28px",
          border: "2px solid #0A84FF",
          boxShadow: "0 24px 70px rgba(0, 0, 0, 0.8), 0 0 45px rgba(10, 132, 255, 0.25)",
          padding: "44px 40px",
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
          tag="SILICON FOUNDRY · TSMC / ASML"
          statusLabel="HIGH-NA EUV ACTIVE"
          statusColor="#0A84FF"
          accentColor="#5E5CE6"
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

        {/* Métrica Heroica: Escala Nanométrica & Transistores */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "20px",
            backgroundColor: "rgba(6, 10, 18, 0.8)",
            borderRadius: "20px",
            padding: "24px 30px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          {/* Nodo y Arquitectura */}
          <div>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 700,
                color: "rgba(255, 255, 255, 0.5)",
                letterSpacing: "2px",
                marginBottom: "4px",
              }}
            >
              NODO LITOGRÁFICO
            </div>
            <div
              style={{
                fontSize: "76px",
                fontWeight: 900,
                fontFamily: "monospace",
                color: "#5E5CE6",
                textShadow: "0 0 25px rgba(94, 92, 230, 0.5)",
                lineHeight: 1,
              }}
            >
              {nodeSize}
            </div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: 700,
                color: "#0A84FF",
                marginTop: "10px",
                fontFamily: "monospace",
              }}
            >
              {architectureTag}
            </div>
          </div>

          {/* Densidad de Transistores */}
          <div>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 700,
                color: "rgba(255, 255, 255, 0.5)",
                letterSpacing: "2px",
                marginBottom: "4px",
              }}
            >
              DENSIDAD TOTAL
            </div>
            <div
              style={{
                fontSize: "52px",
                fontWeight: 900,
                fontFamily: "monospace",
                color: "#FFFFFF",
                textShadow: "0 0 20px rgba(255, 255, 255, 0.3)",
                lineHeight: 1.1,
              }}
            >
              {transistorCount}
            </div>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 700,
                color: "#30D158",
                marginTop: "10px",
                fontFamily: "monospace",
              }}
            >
              {efficiencyGain}
            </div>
          </div>
        </div>

        {/* Esquema Vectorial de Silicio: Pistas de Bus y Láser EUV */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "200px",
            backgroundColor: "rgba(4, 7, 14, 0.8)",
            borderRadius: "18px",
            padding: "16px 20px",
            boxSizing: "border-box",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            overflow: "hidden",
          }}
        >
          <svg viewBox="0 0 800 160" style={{ width: "100%", height: "100%" }}>
            <defs>
              <linearGradient id="busGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#0A84FF" />
                <stop offset="50%" stopColor="#5E5CE6" />
                <stop offset="100%" stopColor="#BF5AF2" />
              </linearGradient>
            </defs>

            {/* Pistas de circuito integradas (Circuit buses) */}
            <path d="M 40 40 L 220 40 L 260 80 L 480 80 L 520 40 L 760 40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
            <path d="M 40 120 L 220 120 L 260 80 L 480 80 L 520 120 L 760 120" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />

            {/* Bus animado con pulsos de fotones */}
            <path
              d="M 40 80 L 760 80"
              fill="none"
              stroke="url(#busGrad)"
              strokeWidth="5"
              strokeDasharray="20 10"
              strokeDashoffset={-busFlow}
            />

            {/* Núcleos del procesador (Die blocks) */}
            <rect x="120" y="25" width="100" height="110" rx="10" fill="rgba(10, 132, 255, 0.15)" stroke="#0A84FF" strokeWidth="2" />
            <text x="170" y="85" textAnchor="middle" fill="#FFFFFF" fontSize="14" fontWeight="800" fontFamily="monospace">
              NPU 120T
            </text>

            <rect x="350" y="25" width="100" height="110" rx="10" fill="rgba(94, 92, 230, 0.2)" stroke="#5E5CE6" strokeWidth="2" />
            <text x="400" y="85" textAnchor="middle" fill="#FFFFFF" fontSize="14" fontWeight="800" fontFamily="monospace">
              2NM CORE
            </text>

            <rect x="580" y="25" width="100" height="110" rx="10" fill="rgba(191, 90, 242, 0.15)" stroke="#BF5AF2" strokeWidth="2" />
            <text x="630" y="85" textAnchor="middle" fill="#FFFFFF" fontSize="14" fontWeight="800" fontFamily="monospace">
              SRAM 3D
            </text>

            {/* Pulso de emisión láser EUV */}
            <circle
              cx="400"
              cy="80"
              r={20 + laserPulse * 15}
              fill="none"
              stroke="#BF5AF2"
              strokeWidth="2"
              opacity={1 - laserPulse}
            />
          </svg>
        </div>

        {/* Barra de Comparación de Rendimiento / Eficiencia */}
        <div
          style={{
            backgroundColor: "rgba(6, 10, 18, 0.8)",
            borderRadius: "14px",
            padding: "16px 20px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "8px",
              fontSize: "14px",
              fontFamily: "monospace",
            }}
          >
            <span style={{ color: "rgba(255,255,255,0.6)" }}>ESCALABILIDAD COMPRESIÓN TÉRMICA</span>
            <span style={{ color: "#30D158", fontWeight: 800 }}>{Math.round(barProgress)}% ÓPTIMO</span>
          </div>
          <div
            style={{
              width: "100%",
              height: "12px",
              backgroundColor: "rgba(255,255,255,0.08)",
              borderRadius: "6px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${barProgress}%`,
                height: "100%",
                background: "linear-gradient(90deg, #0A84FF, #5E5CE6, #30D158)",
                borderRadius: "6px",
                boxShadow: "0 0 12px rgba(48, 209, 88, 0.5)",
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
