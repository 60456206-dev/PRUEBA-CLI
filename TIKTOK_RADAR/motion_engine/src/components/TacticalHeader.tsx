import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

interface TacticalHeaderProps {
  tag?: string;
  sector?: string;
  statusLabel?: string;
  status?: string;
  statusColor?: string;
  accentColor?: string;
}

export const TacticalHeader: React.FC<TacticalHeaderProps> = ({
  tag,
  sector,
  statusLabel,
  status,
  statusColor = "#34C759",
  accentColor = "#00E5FF",
}) => {
  const displayTag = tag || sector || "TELEMETRY LOG";
  const displayStatus = statusLabel || status || "STREAM LIVE";
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Código de tiempo SMPTE exacto
  const sec = Math.floor(frame / fps);
  const fr = frame % fps;
  const timecode = `00:00:${String(sec).padStart(2, "0")}:${String(fr).padStart(2, "0")}`;

  // Pulso del indicador de estado
  const pulse = Math.sin(frame * 0.25) * 0.4 + 0.6;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        borderBottom: "1px solid rgba(255, 255, 255, 0.12)",
        paddingBottom: "18px",
        width: "100%",
        boxSizing: "border-box",
      }}
    >
      {/* Lado izquierdo: Status & Tag */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div
          style={{
            width: "12px",
            height: "12px",
            borderRadius: "50%",
            backgroundColor: statusColor,
            opacity: pulse,
            boxShadow: `0 0 10px ${statusColor}`,
          }}
        />
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span
            style={{
              fontSize: "20px",
              fontWeight: 800,
              letterSpacing: "2.5px",
              color: accentColor,
              textTransform: "uppercase",
              fontFamily: "'Montserrat', sans-serif",
            }}
          >
            {displayTag}
          </span>
          {displayStatus && (
            <span
              style={{
                fontSize: "11px",
                fontWeight: 600,
                letterSpacing: "1px",
                color: "rgba(255, 255, 255, 0.45)",
                fontFamily: "monospace",
              }}
            >
              [{displayStatus}]
            </span>
          )}
        </div>
      </div>

      {/* Lado derecho: SMPTE Timecode & Frame */}
      <div style={{ textAlign: "right", fontFamily: "monospace" }}>
        <div
          style={{
            fontSize: "20px",
            fontWeight: 700,
            color: "rgba(255, 255, 255, 0.8)",
            letterSpacing: "1px",
          }}
        >
          {timecode}
        </div>
        <div
          style={{
            fontSize: "11px",
            color: "rgba(255, 255, 255, 0.35)",
            letterSpacing: "0.5px",
          }}
        >
          FR.{String(frame).padStart(4, "0")} · 24 FPS
        </div>
      </div>
    </div>
  );
};
