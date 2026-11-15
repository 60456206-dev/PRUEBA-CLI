import React, { useMemo } from "react";
import { staticFile, useCurrentFrame } from "remotion";

const FONT_FACE_CSS = `
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 400; src: url('${staticFile("fonts/Montserrat-Regular.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 600; src: url('${staticFile("fonts/Montserrat-SemiBold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 700; src: url('${staticFile("fonts/Montserrat-Bold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 800; src: url('${staticFile("fonts/Montserrat-ExtraBold.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat'; font-style: normal; font-weight: 900; src: url('${staticFile("fonts/Montserrat-Black.ttf")}') format('truetype'); }
@font-face { font-family: 'Montserrat Black'; font-style: normal; font-weight: 900; src: url('${staticFile("fonts/Montserrat-Black.ttf")}') format('truetype'); }
`;

interface BackgroundProps {
  theme?: "aviation" | "tech" | "hardware" | "cyber" | "space" | "universal";
  showScanlines?: boolean;
}

export const ChiaroscuroBackground: React.FC<BackgroundProps> = ({
  theme = "universal",
  showScanlines = true,
}) => {
  const frame = useCurrentFrame();

  // Configuración de acentos de color según temática
  const themeColors = useMemo(() => {
    switch (theme) {
      case "aviation":
        return {
          glow: "rgba(255, 159, 10, 0.08)", // Ámbar sutil
          grid: "rgba(0, 229, 255, 0.03)",  // Cian de cabina
        };
      case "tech":
      case "hardware":
        return {
          glow: "rgba(10, 132, 255, 0.10)", // Azul silicio
          grid: "rgba(94, 92, 230, 0.04)",  // Púrpura litografía
        };
      case "cyber":
        return {
          glow: "rgba(255, 69, 58, 0.09)",  // Rojo amenaza
          grid: "rgba(48, 209, 88, 0.03)",  // Verde terminal
        };
      case "space":
        return {
          glow: "rgba(191, 90, 242, 0.08)", // Violeta cósmico
          grid: "rgba(255, 255, 255, 0.03)",
        };
      default:
        return {
          glow: "rgba(255, 214, 10, 0.08)", // Oro editorial
          grid: "rgba(255, 255, 255, 0.03)",
        };
    }
  }, [theme]);

  // Partículas ambientales generadas pseudo-aleatoriamente
  const particles = useMemo(() => {
    return Array.from({ length: 24 }).map((_, i) => {
      const seed = i * 137.5;
      const x = (Math.sin(seed) * 0.5 + 0.5) * 100;
      const yBase = (Math.cos(seed * 1.3) * 0.5 + 0.5) * 100;
      const speed = 0.04 + (i % 5) * 0.02;
      const size = 1.5 + (i % 3) * 1.2;
      const maxOpacity = 0.2 + (i % 4) * 0.1;
      return { x, yBase, speed, size, maxOpacity, id: i };
    });
  }, []);

  // Respiración de viñeteado ambiental
  const breathing = Math.sin(frame * 0.05) * 0.05 + 0.95;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "#070A0F",
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      <style>{FONT_FACE_CSS}</style>
      {/* 1. Malla de Grilla Técnica de Precisión */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            linear-gradient(to right, ${themeColors.grid} 1px, transparent 1px),
            linear-gradient(to bottom, ${themeColors.grid} 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* 2. Iluminación Chiaroscuro: Halo Volumétrico Difuso */}
      <div
        style={{
          position: "absolute",
          top: "10%",
          left: "50%",
          width: "900px",
          height: "900px",
          transform: `translate(-50%, -30%) scale(${breathing})`,
          background: `radial-gradient(circle, ${themeColors.glow} 0%, transparent 70%)`,
          filter: "blur(60px)",
        }}
      />

      {/* 3. Partículas Ambientales Cinematográficas (Polvo de estudio) */}
      {particles.map((p) => {
        const currentY = (p.yBase - frame * p.speed) % 100;
        const normalizedY = currentY < 0 ? currentY + 100 : currentY;
        const pulse = Math.sin(frame * 0.08 + p.id) * 0.2 + 0.8;
        return (
          <div
            key={p.id}
            style={{
              position: "absolute",
              left: `${p.x}%`,
              top: `${normalizedY}%`,
              width: `${p.size}px`,
              height: `${p.size}px`,
              borderRadius: "50%",
              backgroundColor: "#FFFFFF",
              opacity: p.maxOpacity * pulse,
              boxShadow: `0 0 6px rgba(255, 255, 255, ${p.maxOpacity})`,
            }}
          />
        );
      })}

      {/* 4. Viñeta Radial Profunda estilo Estudio Veritasium */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            "radial-gradient(circle at center, transparent 35%, rgba(3, 5, 8, 0.75) 75%, rgba(2, 3, 5, 0.96) 100%)",
        }}
      />

      {/* 5. Micro Scanlines Analógicas Broadcast */}
      {showScanlines && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage:
              "repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.015) 0px, rgba(255, 255, 255, 0.015) 1px, transparent 1px, transparent 3px)",
            opacity: 0.7,
          }}
        />
      )}
    </div>
  );
};
