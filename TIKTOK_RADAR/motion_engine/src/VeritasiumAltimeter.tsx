import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ChiaroscuroBackground } from "./components/ChiaroscuroBackground";
import { TacticalHeader } from "./components/TacticalHeader";

export interface AltimeterProps {
  title: string;
  subtitle: string;
  initialAlt: number;
  finalAlt: number;
  flightNumber: string;
  warningText: string;
  descentRate?: string;
}

export const VeritasiumAltimeter: React.FC<AltimeterProps> = ({
  title = "REGISTRO DE TELEMETRÍA DE CABINA",
  subtitle = "ALTITUD Y TASA DE DESCENSO CRÍTICA",
  initialAlt = 35000,
  finalAlt = 3200,
  flightNumber = "FLIGHT MAYDAY-2026",
  warningText = "ALERTA: TASA DE DESCENSO ANORMAL",
  descentRate = "-3,400 FPM",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Entrada elástica con spring (estilo Veritasium)
  const cardScale = spring({
    frame,
    fps,
    config: {
      damping: 14,
      mass: 0.85,
      stiffness: 110,
    },
  });

  const cardOpacity = interpolate(frame, [0, 14], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 2. Interpolación numérica de altitud (de 35,000 ft a 3,200 ft)
  const currentAltitude = Math.round(
    interpolate(frame, [15, durationInFrames - 15], [initialAlt, finalAlt], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  // 3. Trazado progresivo de la curva de descenso (SVG dashoffset)
  const pathLength = 650;
  const strokeDashoffset = interpolate(
    frame,
    [10, durationInFrames - 20],
    [pathLength, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // 4. Parpadeo de alerta en el tercio final
  const isAlarm = frame > 42;
  const alarmPulse = isAlarm ? Math.sin((frame - 42) * 0.45) * 0.5 + 0.5 : 0;
  const hudColor = isAlarm
    ? `rgb(255, ${Math.round(69 + 90 * (1 - alarmPulse))}, 58)`
    : "#00E5FF";

  // 5. Inclinación del horizonte artificial de cabina (Pitch & Roll)
  const pitchY = interpolate(frame, [15, durationInFrames - 15], [0, 18], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rollAngle = interpolate(frame, [20, 50, durationInFrames], [0, -7, -4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Movimiento de cámara continuo Veritasium (push-in continuo anti-freeze)
  const cameraZoom = 1 + frame * 0.0007;

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
      {/* Fondo Chiaroscuro con partículas orgánicas y viñeta profunda */}
      <ChiaroscuroBackground theme="aviation" />

      {/* Tarjeta HUD Broadcast */}
      <div
        style={{
          width: "940px",
          backgroundColor: "rgba(12, 17, 28, 0.90)",
          borderRadius: "28px",
          border: `2px solid ${hudColor}`,
          boxShadow: `0 24px 70px rgba(0, 0, 0, 0.8), 0 0 45px ${
            isAlarm ? "rgba(255, 69, 58, 0.35)" : "rgba(0, 229, 255, 0.18)"
          }`,
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
        {/* Cabecera Táctica */}
        <TacticalHeader
          tag={flightNumber}
          statusLabel={isAlarm ? "TERRAIN PULL-UP WARNING" : "FLIGHT TELEMETRY NORMAL"}
          statusColor={isAlarm ? "#FF453A" : "#34C759"}
          accentColor={hudColor}
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

        {/* Métrica Heroica: Altímetro Numérico + Indicador de Actitud */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 240px",
            gap: "20px",
            alignItems: "center",
            backgroundColor: "rgba(8, 12, 20, 0.75)",
            borderRadius: "20px",
            padding: "24px 30px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          {/* Lado A: Altitud Digital */}
          <div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: 700,
                color: "rgba(255, 255, 255, 0.5)",
                letterSpacing: "2px",
                marginBottom: "4px",
              }}
            >
              ALTITUD BAROMÉTRICA (MSL)
            </div>
            <div
              style={{
                fontSize: "82px",
                fontWeight: 900,
                fontFamily: "monospace",
                color: isAlarm ? "#FF453A" : "#FFFFFF",
                textShadow: isAlarm
                  ? "0 0 25px rgba(255, 69, 58, 0.6)"
                  : "0 0 20px rgba(0, 229, 255, 0.3)",
                lineHeight: 1,
              }}
            >
              {currentAltitude.toLocaleString("en-US")}
              <span
                style={{
                  fontSize: "30px",
                  fontWeight: 700,
                  marginLeft: "12px",
                  color: hudColor,
                }}
              >
                FT
              </span>
            </div>

            <div
              style={{
                display: "flex",
                gap: "24px",
                marginTop: "14px",
                fontSize: "15px",
                fontFamily: "monospace",
              }}
            >
              <div>
                <span style={{ color: "rgba(255,255,255,0.4)" }}>TASA: </span>
                <span style={{ color: isAlarm ? "#FF9F0A" : "#32D74B", fontWeight: 800 }}>
                  {descentRate}
                </span>
              </div>
              <div>
                <span style={{ color: "rgba(255,255,255,0.4)" }}>VEL: </span>
                <span style={{ color: "#00E5FF", fontWeight: 700 }}>440 KTS</span>
              </div>
            </div>
          </div>

          {/* Lado B: Mini Horizonte Artificial de Cabina (PFD Attitude Indicator) */}
          <div
            style={{
              width: "100%",
              height: "130px",
              backgroundColor: "rgba(4, 7, 12, 0.8)",
              borderRadius: "14px",
              border: "1px solid rgba(255, 255, 255, 0.12)",
              position: "relative",
              overflow: "hidden",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {/* Esfera con rotación e inclinación */}
            <div
              style={{
                position: "absolute",
                width: "200px",
                height: "200px",
                transform: `rotate(${rollAngle}deg) translateY(${pitchY}px)`,
                display: "flex",
                flexDirection: "column",
              }}
            >
              {/* Cielo (Sky) */}
              <div style={{ flex: 1, backgroundColor: "rgba(10, 80, 150, 0.55)" }} />
              {/* Línea del horizonte */}
              <div style={{ height: "2px", backgroundColor: "#FFFFFF" }} />
              {/* Suelo (Ground) */}
              <div style={{ flex: 1, backgroundColor: "rgba(120, 60, 20, 0.55)" }} />
            </div>

            {/* Escala de Pitch (Ladder) */}
            <svg
              viewBox="0 0 160 100"
              style={{
                position: "absolute",
                width: "100%",
                height: "100%",
                pointerEvents: "none",
              }}
            >
              {/* Cruz de referencia del avión (fija al fuselaje) */}
              <line x1="30" y1="50" x2="65" y2="50" stroke="#FFD60A" strokeWidth="3" />
              <line x1="65" y1="50" x2="65" y2="58" stroke="#FFD60A" strokeWidth="3" />
              <circle cx="80" cy="50" r="3" fill="#FFD60A" />
              <line x1="95" y1="58" x2="95" y2="50" stroke="#FFD60A" strokeWidth="3" />
              <line x1="95" y1="50" x2="130" y2="50" stroke="#FFD60A" strokeWidth="3" />
            </svg>

            <span
              style={{
                position: "absolute",
                bottom: "6px",
                fontSize: "11px",
                color: "rgba(255,255,255,0.6)",
                fontFamily: "monospace",
                fontWeight: 700,
              }}
            >
              PFD ATTITUDE
            </span>
          </div>
        </div>

        {/* Gráfico Vectorial Animado (Perfil de Descenso) */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "200px",
            backgroundColor: "rgba(5, 8, 14, 0.75)",
            borderRadius: "18px",
            padding: "16px 20px",
            boxSizing: "border-box",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <svg
            viewBox="0 0 800 160"
            style={{ width: "100%", height: "100%", overflow: "visible" }}
          >
            <defs>
              <linearGradient id="curveGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00E5FF" />
                <stop offset="70%" stopColor="#FF9F0A" />
                <stop offset="100%" stopColor="#FF453A" />
              </linearGradient>
            </defs>

            {/* Líneas guía de altitud */}
            <line
              x1="50"
              y1="25"
              x2="750"
              y2="25"
              stroke="rgba(255,255,255,0.12)"
              strokeDasharray="4 4"
            />
            <text x="60" y="20" fill="rgba(255,255,255,0.4)" fontSize="13" fontFamily="monospace">
              35,000 FT (CRUCERO ESTABLE)
            </text>

            <line
              x1="50"
              y1="135"
              x2="750"
              y2="135"
              stroke="rgba(255,69,58,0.3)"
              strokeDasharray="4 4"
            />
            <text x="60" y="130" fill="rgba(255,69,58,0.75)" fontSize="13" fontFamily="monospace">
              NIVEL CRÍTICO DE COLISIÓN
            </text>

            {/* Curva Bézier de descenso */}
            <path
              d="M 50 25 C 280 25, 460 120, 750 135"
              fill="none"
              stroke="url(#curveGradient)"
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={pathLength}
              strokeDashoffset={strokeDashoffset}
            />

            {/* Marcador de avión animado sobre la trayectoria */}
            {frame > 10 && (
              <g
                transform={`translate(${interpolate(
                  frame,
                  [10, durationInFrames - 20],
                  [50, 750],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                )}, ${interpolate(
                  frame,
                  [10, durationInFrames - 20],
                  [25, 135],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                )})`}
              >
                <circle
                  r="10"
                  fill={isAlarm ? "#FF3B30" : "#00E5FF"}
                  style={{
                    filter: `drop-shadow(0 0 10px ${isAlarm ? "#FF3B30" : "#00E5FF"})`,
                  }}
                />
                <circle r="18" fill="none" stroke={isAlarm ? "#FF3B30" : "#00E5FF"} strokeWidth="1.5" opacity="0.4" />
              </g>
            )}
          </svg>
        </div>

        {/* Píldora de Advertencia */}
        {isAlarm && (
          <div
            style={{
              backgroundColor: "rgba(255, 69, 58, 0.2)",
              border: "1.5px solid rgba(255, 69, 58, 0.7)",
              borderRadius: "14px",
              padding: "16px 20px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "14px",
              opacity: alarmPulse * 0.7 + 0.3,
            }}
          >
            <span style={{ fontSize: "24px" }}>⚠️</span>
            <span
              style={{
                fontSize: "19px",
                fontWeight: 800,
                color: "#FF453A",
                letterSpacing: "2px",
              }}
            >
              {warningText}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
