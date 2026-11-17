import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface CyberRadarProps {
  title: string;
  subtitle: string;
  packetRate?: string;
  cveSeverity?: string;
  threatVector?: string;
  targetCount?: string;
}

export const VeritasiumCyberRadar: React.FC<CyberRadarProps> = ({
  title = "ATAQUE DDOS MULTIVECTORIAL DETECTADO",
  subtitle = "COLAPSO DE ENRUTAMIENTO BGP Y SOBRECARGA DE NODOS",
  packetRate = "14.8 M PPS",
  cveSeverity = "CVSS 9.8 · CRÍTICO",
  threatVector = "ZERO-DAY EXPLOITATION",
  targetCount = "184 NODOS COMPROMETIDOS",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

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

  // 2. Alarma pulsante constante
  const pulse = Math.sin(frame * 0.4) * 0.5 + 0.5;
  const radarSweep = (frame * 5) % 360;

  // 3. Simulación de paquetes infectados
  const packetCount = Math.round(
    interpolate(frame, [10, durationInFrames - 10], [1200000, 14800000], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

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
      <ChiaroscuroBackground theme="cyber" />

      {/* Tarjeta HUD Broadcast */}
      <div
        style={{
          width: "830px",
          backgroundColor: "rgba(16, 10, 14, 0.92)",
          borderRadius: "28px",
          border: "2px solid #FF453A",
          boxShadow: `0 24px 70px rgba(0, 0, 0, 0.8), 0 0 45px rgba(255, 69, 58, ${0.2 + pulse * 0.2})`,
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
          tag="CYBER COMMAND · DEFCON 2"
          statusLabel="INFRASTRUCTURE BREACH"
          statusColor="#FF453A"
          accentColor="#FF3B30"
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

        {/* Métricas Principales */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 1fr",
            gap: "20px",
            backgroundColor: "rgba(10, 6, 8, 0.85)",
            borderRadius: "20px",
            padding: "24px 30px",
            border: "1px solid rgba(255, 69, 58, 0.2)",
          }}
        >
          {/* Tasa de paquetes */}
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
              FLUJO DE ATAQUE (PEAK TRAFFIC)
            </div>
            <div
              style={{
                fontSize: "72px",
                fontWeight: 900,
                fontFamily: "monospace",
                color: "#FF453A",
                textShadow: "0 0 25px rgba(255, 69, 58, 0.6)",
                lineHeight: 1,
              }}
            >
              {packetRate}
            </div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: 700,
                color: "#FF9F0A",
                marginTop: "10px",
                fontFamily: "monospace",
              }}
            >
              {packetCount.toLocaleString("en-US")} PAQ/SEG
            </div>
          </div>

          {/* Gravedad y Vector */}
          <div style={{ textAlign: "right" }}>
            <div
              style={{
                fontSize: "14px",
                fontWeight: 700,
                color: "rgba(255, 255, 255, 0.5)",
                letterSpacing: "2px",
                marginBottom: "4px",
              }}
            >
              SEVERIDAD DE IMPACTO
            </div>
            <div
              style={{
                fontSize: "30px",
                fontWeight: 900,
                color: "#FF375F",
                fontFamily: "monospace",
                lineHeight: 1.2,
              }}
            >
              {cveSeverity}
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
              VECTOR: {threatVector}
            </div>
            <div
              style={{
                fontSize: "13px",
                color: "rgba(255,255,255,0.4)",
                marginTop: "4px",
                fontFamily: "monospace",
              }}
            >
              {targetCount}
            </div>
          </div>
        </div>

        {/* Constelación de Nodos / Radar Vectorial */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "200px",
            backgroundColor: "rgba(6, 4, 8, 0.8)",
            borderRadius: "18px",
            padding: "16px 20px",
            boxSizing: "border-box",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            overflow: "hidden",
          }}
        >
          <svg viewBox="0 0 800 160" style={{ width: "100%", height: "100%" }}>
            {/* Círculos concéntricos de radar */}
            <circle cx="400" cy="80" r="40" fill="none" stroke="rgba(255,69,58,0.15)" strokeWidth="1" />
            <circle cx="400" cy="80" r="90" fill="none" stroke="rgba(255,69,58,0.12)" strokeWidth="1" />
            <circle cx="400" cy="80" r="140" fill="none" stroke="rgba(255,69,58,0.08)" strokeWidth="1" />

            {/* Aguja de barrido de radar */}
            <line
              x1="400"
              y1="80"
              x2={400 + Math.cos((radarSweep * Math.PI) / 180) * 150}
              y2={80 + Math.sin((radarSweep * Math.PI) / 180) * 150}
              stroke="#FF453A"
              strokeWidth="2"
              opacity="0.7"
            />

            {/* Nodos de red interconectados */}
            {[
              { x: 120, y: 50, label: "DNS-ROOT" },
              { x: 260, y: 110, label: "TIER-1" },
              { x: 400, y: 80, label: "BGP-GATEWAY" },
              { x: 540, y: 40, label: "CLOUD-EDGE" },
              { x: 680, y: 120, label: "DATACENTER" },
            ].map((node, i) => (
              <g key={i}>
                <circle cx={node.x} cy={node.y} r="8" fill="#FF453A" opacity={0.4 + pulse * 0.4} />
                <circle cx={node.x} cy={node.y} r="4" fill="#FFFFFF" />
                <text x={node.x} y={node.y + 20} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="11" fontFamily="monospace">
                  {node.label}
                </text>
              </g>
            ))}

            {/* Líneas de conexión atacadas */}
            <line x1="120" y1="50" x2="260" y2="110" stroke="#FF453A" strokeWidth="2" strokeDasharray="6 4" />
            <line x1="260" y1="110" x2="400" y2="80" stroke="#FF3B30" strokeWidth="3" />
            <line x1="400" y1="80" x2="540" y2="40" stroke="#FF453A" strokeWidth="2" strokeDasharray="6 4" />
            <line x1="540" y1="40" x2="680" y2="120" stroke="#FF375F" strokeWidth="2" />
          </svg>
        </div>

        {/* Banner de Estado de Contención */}
        <div
          style={{
            backgroundColor: "rgba(255, 69, 58, 0.18)",
            border: "1.5px solid rgba(255, 69, 58, 0.7)",
            borderRadius: "14px",
            padding: "16px 20px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "22px" }}>🛡️</span>
            <span style={{ fontSize: "17px", fontWeight: 800, color: "#FF453A", letterSpacing: "1px" }}>
              PROTOCOLOS DE MITIGACIÓN NEGRA ACTIVADOS
            </span>
          </div>
          <span style={{ fontFamily: "monospace", fontSize: "14px", color: "rgba(255,255,255,0.7)" }}>
            TTL: 00:14s
          </span>
        </div>
      </div>
    </div>
  );
};
