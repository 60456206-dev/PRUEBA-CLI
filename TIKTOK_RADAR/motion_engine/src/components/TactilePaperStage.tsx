import React, { useMemo } from "react";
import { staticFile, useCurrentFrame } from "remotion";

export const EDITORIAL_FONT_FACE_CSS = `
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 400; src: url('${staticFile("fonts/Montserrat-Regular.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 600; src: url('${staticFile("fonts/Montserrat-SemiBold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 700; src: url('${staticFile("fonts/Montserrat-Bold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 800; src: url('${staticFile("fonts/Montserrat-ExtraBold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 900; src: url('${staticFile("fonts/Montserrat-Black.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat Black'; font-style: normal; font-weight: 900; src: url('${staticFile("fonts/Montserrat-Black.ttf")}') format('truetype'); }
`;

interface StageProps {
  accentColor?: string;
  children?: React.ReactNode;
}

/**
 * Escenario editorial 2.5D con iluminacion direccional de mesa de estudio,
 * textura organica de papel/grano y motas ambientales en movimiento lento.
 */
export const TactilePaperStage: React.FC<StageProps> = ({
  accentColor = "rgba(229, 169, 60, 0.14)",
  children,
}) => {
  const frame = useCurrentFrame();

  const dustMotes = useMemo(() => {
    return Array.from({ length: 22 }).map((_, i) => {
      const seed = i * 97.31;
      const x = (Math.sin(seed) * 0.5 + 0.5) * 100;
      const yBase = (Math.cos(seed * 1.43) * 0.5 + 0.5) * 100;
      const speed = 0.035 + (i % 4) * 0.018;
      const size = 1.6 + (i % 3) * 1.1;
      const opacity = 0.12 + (i % 4) * 0.06;
      return { id: i, x, yBase, speed, size, opacity };
    });
  }, []);

  const paperFibers = useMemo(() => {
    return Array.from({ length: 48 }).map((_, i) => {
      const s = i * 41.7;
      const x1 = (Math.sin(s) * 0.5 + 0.5) * 180;
      const y1 = (Math.cos(s * 1.7) * 0.5 + 0.5) * 180;
      const angle = (s % 180) * (Math.PI / 180);
      const len = 5 + (i % 5) * 2.5;
      const x2 = x1 + Math.cos(angle) * len;
      const y2 = y1 + Math.sin(angle) * len;
      const isWarm = i % 3 === 0;
      return { id: i, x1, y1, x2, y2, isWarm };
    });
  }, []);

  const spotDriftX = Math.sin(frame * 0.025) * 32;
  const spotDriftY = Math.cos(frame * 0.02) * 22;

  return (
    <div
      style={{
        position: "relative",
        width: "1080px",
        height: "1920px",
        backgroundColor: "#0B0E14",
        overflow: "hidden",
        fontFamily: "'Montserrat', sans-serif",
      }}
    >
      <style>{EDITORIAL_FONT_FACE_CSS}</style>

      {/* Luz direccional de estudio (lampara de mesa cartografica) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at calc(44% + ${spotDriftX}px) calc(40% + ${spotDriftY}px), ${accentColor} 0%, rgba(28, 36, 48, 0.35) 38%, rgba(8, 10, 15, 0.96) 88%)`,
          pointerEvents: "none",
        }}
      />

      {/* Contenido en espacio 2.5D */}
      {children}

      {/* Textura tactil de papel / fibra analogica encima de toda la composicion */}
      <svg
        width="1080"
        height="1920"
        viewBox="0 0 1080 1920"
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          mixBlendMode: "overlay",
          opacity: 0.42,
        }}
      >
        <defs>
          <pattern
            id="editorial-paper-grain"
            width="180"
            height="180"
            patternUnits="userSpaceOnUse"
          >
            <rect width="180" height="180" fill="rgba(128,128,128,0.03)" />
            {paperFibers.map((f) => (
              <line
                key={f.id}
                x1={f.x1}
                y1={f.y1}
                x2={f.x2}
                y2={f.y2}
                stroke={
                  f.isWarm
                    ? "rgba(255, 240, 210, 0.24)"
                    : "rgba(255, 255, 255, 0.16)"
                }
                strokeWidth="0.9"
                strokeLinecap="round"
              />
            ))}
          </pattern>
        </defs>
        <rect width="1080" height="1920" fill="url(#editorial-paper-grain)" />
      </svg>

      {/* Motas suaves en primer plano (sensacion de estudio optico) */}
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
        {dustMotes.map((m) => {
          const y = ((m.yBase - frame * m.speed) % 100 + 100) % 100;
          const x = m.x + Math.sin(frame * 0.03 + m.id) * 0.6;
          return (
            <div
              key={m.id}
              style={{
                position: "absolute",
                left: `${x}%`,
                top: `${y}%`,
                width: `${m.size}px`,
                height: `${m.size}px`,
                borderRadius: "50%",
                backgroundColor: "#F5E6C8",
                opacity: m.opacity,
              }}
            />
          );
        })}
      </div>

      {/* Vineteado calido cinematografico en bordes */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "radial-gradient(ellipse at center, transparent 48%, rgba(4, 6, 9, 0.72) 86%, rgba(2, 3, 5, 0.94) 100%)",
        }}
      />
    </div>
  );
};

/**
 * Genera un contorno SVG determinista con bordes ligeramente rasgados tipo papel cortado.
 */
export function buildDeckledPaperPath(
  width: number,
  height: number,
  step = 18,
  roughness = 3.2,
  seed = 7
): string {
  const pts: Array<[number, number]> = [];
  const jitter = (idx: number, axis: number) =>
    Math.sin(idx * 12.9898 + seed * 78.233 + axis * 43.17) * roughness;

  let stepIdx = 0;
  for (let x = 0; x <= width; x += step) {
    pts.push([x, jitter(stepIdx++, 1)]);
  }
  for (let y = step; y <= height; y += step) {
    pts.push([width + jitter(stepIdx++, 2), y]);
  }
  for (let x = width - step; x >= 0; x -= step) {
    pts.push([x, height + jitter(stepIdx++, 3)]);
  }
  for (let y = height - step; y >= step; y -= step) {
    pts.push([jitter(stepIdx++, 4), y]);
  }

  return (
    pts
      .map(
        ([px, py], i) =>
          `${i === 0 ? "M" : "L"} ${px.toFixed(1)} ${py.toFixed(1)}`
      )
      .join(" ") + " Z"
  );
}

interface CutoutProps {
  width: number;
  height: number;
  rotationDeg?: number;
  paperColor?: string;
  seed?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

/**
 * Recorte fisico de papel archival con borde rasgado y sombra proyectada en 2.5D.
 */
export const DeckledPaperCutout: React.FC<CutoutProps> = ({
  width,
  height,
  rotationDeg = -2.2,
  paperColor = "#EFE5CE",
  seed = 11,
  style,
  children,
}) => {
  const path = useMemo(
    () => buildDeckledPaperPath(width, height, 16, 2.8, seed),
    [width, height, seed]
  );

  return (
    <div
      style={{
        position: "relative",
        width: `${width}px`,
        height: `${height}px`,
        transform: `rotate(${rotationDeg}deg)`,
        filter: "drop-shadow(10px 24px 22px rgba(0, 0, 0, 0.72))",
        ...style,
      }}
    >
      <svg
        width={width + 12}
        height={height + 12}
        viewBox={`-6 -6 ${width + 12} ${height + 12}`}
        style={{ position: "absolute", left: -6, top: -6, overflow: "visible" }}
      >
        <path d={path} fill={paperColor} />
        <path
          d={path}
          fill="none"
          stroke="rgba(120, 96, 62, 0.25)"
          strokeWidth="1.5"
        />
      </svg>
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            padding: "22px 26px",
            boxSizing: "border-box",
          }}
        >
          {children}
        </div>
      </div>
    );
  };

interface HeadlineProps {
  kicker: string;
  headline: string;
  accentColor?: string;
  translateX?: number;
  translateY?: number;
  opacity?: number;
  fontSize?: number;
  top?: number;
}

/**
 * Titular editorial compartido en Safe Zone superior (sin cajas UI y con espacio bajo el rotulo superior).
 */
export const EditorialHeadline: React.FC<HeadlineProps> = ({
  kicker,
  headline,
  accentColor = "#E5A93C",
  translateX = 0,
  translateY = 0,
  opacity = 1,
  fontSize = 50,
  top = 214,
}) => {
  const autoSize =
    headline.length > 52 ? Math.max(36, fontSize - 10) : headline.length > 38 ? Math.max(40, fontSize - 6) : fontSize;

  return (
    <div
      style={{
        position: "absolute",
        top: `${top}px`,
        left: "68px",
        width: "820px",
        transform: `translate3d(${translateX}px, ${translateY}px, 0)`,
        opacity,
        zIndex: 5,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          marginBottom: "10px",
        }}
      >
        <div
          style={{
            width: "34px",
            height: "4px",
            backgroundColor: accentColor,
          }}
        />
        <span
          style={{
            fontSize: "20px",
            fontWeight: 800,
            letterSpacing: "2.8px",
            color: accentColor,
          }}
        >
          {kicker}
        </span>
      </div>

      <div
        style={{
          fontSize: `${autoSize}px`,
          fontWeight: 900,
          lineHeight: 1.07,
          color: "#F8F3E8",
          letterSpacing: "-0.5px",
          textShadow: "0 8px 26px rgba(0, 0, 0, 0.85)",
        }}
      >
        {headline}
      </div>
    </div>
  );
};
