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

export type DiagramKind = "aircraft" | "chip" | "network" | "spacecraft" | "seismic";

export interface Editorial25DDiagramProps {
  kicker?: string;
  headline?: string;
  diagramKind?: DiagramKind;
  calloutTitle?: string;
  calloutDetail?: string;
  secondaryLabel?: string;
  secondaryCallout?: string;
  bottomStamp?: string;
  bottomTakeaway?: string;
  accentColor?: string;
  alertColor?: string;
}

function splitTwoLines(text: string): [string, string] {
  const words = (text || "").trim().split(/\s+/).filter(Boolean);
  if (words.length <= 2) return [words.join(" "), ""];
  const mid = Math.ceil(words.length / 2);
  return [words.slice(0, mid).join(" "), words.slice(mid).join(" ")];
}

export const Editorial25DDiagram: React.FC<Editorial25DDiagramProps> = ({
  kicker = "DECONSTRUCCIÓN TÉCNICA",
  headline = "EL MECANISMO DETRÁS DE LA NOTICIA",
  diagramKind = "aircraft",
  calloutTitle = "PUNTO CRÍTICO",
  calloutDetail = "ANOMALÍA DETECTADA",
  secondaryLabel = "RESPUESTA TÉCNICA",
  secondaryCallout = "PROTOCOLO DE SEGURIDAD",
  bottomStamp = "CLAVE OPERATIVA",
  bottomTakeaway = "PRIORIZAR EL MARGEN ANTE LO INCIERTO",
  accentColor = "#E5A93C",
  alertColor = "#E63946",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const headerSpring = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.9, stiffness: 105 },
  });
  const headerY = interpolate(headerSpring, [0, 1], [26, 0]);
  const headerOpacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });

  const outlineEnd = Math.min(26, Math.max(12, Math.round(durationInFrames * 0.28)));
  const outlineReveal = interpolate(frame, [4, outlineEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const hlStart = Math.min(16, Math.round(durationInFrames * 0.20));
  const hlEnd = Math.min(28, Math.max(hlStart + 8, Math.round(durationInFrames * 0.34)));
  const highlightFade = interpolate(frame, [hlStart, hlEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const c1Start = Math.min(18, Math.round(durationInFrames * 0.22));
  const c1End = Math.min(34, Math.max(c1Start + 10, Math.round(durationInFrames * 0.40)));
  const callout1Draw = interpolate(frame, [c1Start, c1End], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const c2Start = Math.min(24, Math.round(durationInFrames * 0.28));
  const c2End = Math.min(42, Math.max(c2Start + 10, Math.round(durationInFrames * 0.48)));
  const callout2Draw = interpolate(frame, [c2Start, c2End], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const camT = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const sheetZoom = interpolate(camT, [0, 1], [0.98, 1.08]);
  const sheetTiltX = interpolate(camT, [0, 1], [10, 16]);
  const sheetRotZ = interpolate(camT, [0, 1], [-1.5, 1.3]);
  const sheetPanY = interpolate(camT, [0, 1], [12, -16]);

  const bottomStart = Math.min(16, Math.round(durationInFrames * 0.18));
  const bottomSpring = spring({
    frame: Math.max(0, frame - bottomStart),
    fps,
    config: { damping: 14, mass: 0.85, stiffness: 95 },
  });
  const bottomSlideY = interpolate(bottomSpring, [0, 1], [90, 0]);
  const bottomOpacity = interpolate(frame, [bottomStart, bottomStart + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pulseScale = 1 + Math.sin(frame * 0.22) * 0.12;
  const [calLine1, calLine2] = splitTwoLines(calloutDetail);
  const [secLine1, secLine2] = splitTwoLines(secondaryCallout);

  const pointerByKind: Record<DiagramKind, { p1: string; p2: string }> = {
    aircraft: { p1: "M368 176 L262 154 L224 112", p2: "M492 238 L545 162 L615 162" },
    chip: { p1: "M314 232 L248 164 L214 114", p2: "M478 268 L552 172 L618 172" },
    network: { p1: "M372 165 L268 150 L228 112", p2: "M534 218 L576 164 L626 164" },
    spacecraft: { p1: "M382 175 L270 156 L224 114", p2: "M438 338 L548 184 L618 184" },
    seismic: { p1: "M388 282 L272 174 L228 116", p2: "M438 320 L552 184 L618 184" },
  };
  const pointers = pointerByKind[diagramKind] || pointerByKind.aircraft;

  const renderSchematic = () => {
    if (diagramKind === "chip") {
      return (
        <>
          {/* Sombra 2.5D del encapsulado */}
          <rect x="256" y="162" width="310" height="270" rx="18" fill="#06080B" opacity="0.55" />
          {/* Oblea / dado de silicio */}
          <rect
            x="244"
            y="144"
            width="312"
            height="272"
            rx="16"
            fill="rgba(239, 229, 206, 0.08)"
            stroke="#EFE5CE"
            strokeWidth="4"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          {/* Pines de conexion laterales */}
          <g stroke={accentColor} strokeWidth="3.5" strokeLinecap="round" opacity={outlineReveal}>
            {[178, 220, 262, 304, 346, 382].map((yPos, idx) => (
              <React.Fragment key={idx}>
                <line x1="214" y1={yPos} x2="244" y2={yPos} />
                <line x1="556" y1={yPos} x2="586" y2={yPos} />
              </React.Fragment>
            ))}
          </g>
          {/* Capas internas nanosheet */}
          <g fill="none" stroke="rgba(239,229,206,0.55)" strokeWidth="2.5">
            <rect x="282" y="182" width="236" height="196" rx="10" pathLength={1} strokeDashoffset={1 - outlineReveal} />
            <line x1="400" y1="182" x2="400" y2="378" pathLength={1} strokeDashoffset={1 - outlineReveal} />
            <line x1="282" y1="280" x2="518" y2="280" pathLength={1} strokeDashoffset={1 - outlineReveal} />
          </g>
          {/* Nucleo critico resaltado */}
          <g opacity={highlightFade}>
            <rect
              x="312"
              y="206"
              width="76"
              height="62"
              rx="8"
              fill="rgba(230, 57, 70, 0.30)"
              stroke={alertColor}
              strokeWidth="3"
            />
            <circle cx="350" cy="237" r={12 * pulseScale} fill="rgba(230, 57, 70, 0.34)" />
            <circle cx="350" cy="237" r="6.5" fill={alertColor} />
          </g>
        </>
      );
    }

    if (diagramKind === "network") {
      const nodes = [
        { x: 245, y: 235 },
        { x: 400, y: 165 },
        { x: 555, y: 235 },
        { x: 300, y: 385 },
        { x: 500, y: 385 },
      ];
      const edges = [
        [0, 1],
        [1, 2],
        [0, 3],
        [2, 4],
        [3, 4],
        [1, 3],
        [1, 4],
      ];
      return (
        <>
          <g stroke="rgba(239, 229, 206, 0.55)" strokeWidth="3.5" strokeLinecap="round">
            {edges.map(([a, b], idx) => (
              <line
                key={idx}
                x1={nodes[a].x}
                y1={nodes[a].y}
                x2={nodes[b].x}
                y2={nodes[b].y}
                pathLength={1}
                strokeDashoffset={1 - outlineReveal}
              />
            ))}
          </g>
          <g opacity={outlineReveal}>
            {nodes.map((n, idx) => (
              <g key={idx}>
                <circle cx={n.x + 10} cy={n.y + 18} r="28" fill="#06080B" opacity="0.55" />
                <circle
                  cx={n.x}
                  cy={n.y}
                  r="28"
                  fill="#171D26"
                  stroke={idx === 1 ? alertColor : "#EFE5CE"}
                  strokeWidth={idx === 1 ? "4" : "3"}
                />
                <circle cx={n.x} cy={n.y} r="9" fill={idx === 4 ? accentColor : "#EFE5CE"} />
              </g>
            ))}
          </g>
          <g opacity={highlightFade}>
            <circle cx="400" cy="165" r={38 * pulseScale} fill="none" stroke={alertColor} strokeWidth="3" />
            <circle cx="400" cy="165" r="12" fill={alertColor} />
          </g>
        </>
      );
    }

    if (diagramKind === "spacecraft") {
      return (
        <>
          {/* Sombra 2.5D del cohete / sonda */}
          <g transform="translate(16, 26)" opacity="0.52">
            <path d="M400 72 C428 118 440 176 440 235 L440 385 L498 442 L498 468 L434 438 L422 470 L378 470 L366 438 L302 468 L302 442 L360 385 L360 235 C360 176 372 118 400 72 Z" fill="#06080B" />
          </g>
          <path
            d="M400 72 C428 118 440 176 440 235 L440 385 L498 442 L498 468 L434 438 L422 470 L378 470 L366 438 L302 468 L302 442 L360 385 L360 235 C360 176 372 118 400 72 Z"
            fill="rgba(239, 229, 206, 0.10)"
            opacity={outlineReveal}
          />
          <path
            d="M400 72 C428 118 440 176 440 235 L440 385 L498 442 L498 468 L434 438 L422 470 L378 470 L366 438 L302 468 L302 442 L360 385 L360 235 C360 176 372 118 400 72 Z"
            fill="none"
            stroke="#EFE5CE"
            strokeWidth="4.5"
            strokeLinejoin="round"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <line x1="362" y1="210" x2="438" y2="210" stroke={accentColor} strokeWidth="3.5" opacity={outlineReveal} />
          <line x1="362" y1="340" x2="438" y2="340" stroke={accentColor} strokeWidth="3.5" opacity={outlineReveal} />
          <g opacity={highlightFade}>
            <ellipse cx="400" cy="456" rx="44" ry="22" fill="rgba(230, 57, 70, 0.30)" stroke={alertColor} strokeWidth="3" />
            <circle cx="400" cy="175" r={12 * pulseScale} fill="rgba(230, 57, 70, 0.32)" />
            <circle cx="400" cy="175" r="7" fill={alertColor} />
          </g>
        </>
      );
    }

    if (diagramKind === "seismic") {
      return (
        <>
          {/* Capas geologicas / ondas de energia */}
          <path
            d="M 140 365 Q 290 330 400 355 T 660 345"
            fill="none"
            stroke="#EFE5CE"
            strokeWidth="4"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <path
            d="M 160 420 Q 310 390 420 412 T 640 404"
            fill="none"
            stroke="rgba(239, 229, 206, 0.5)"
            strokeWidth="3"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <line
            x1="345"
            y1="155"
            x2="455"
            y2="455"
            stroke={accentColor}
            strokeWidth="4"
            strokeDasharray="10 8"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <g opacity={highlightFade}>
            {[62, 108, 154].map((rad, i) => (
              <circle
                key={i}
                cx="400"
                cy="295"
                r={rad * (i === 0 ? pulseScale : 1)}
                fill="none"
                stroke={alertColor}
                strokeWidth={3 - i * 0.6}
                opacity={0.85 - i * 0.24}
              />
            ))}
            <circle cx="400" cy="295" r="11" fill={alertColor} />
          </g>
        </>
      );
    }

    // Default: "aircraft"
    return (
      <>
        <g transform="translate(14, 42) scale(0.92)" style={{ transformOrigin: "400px 280px" }} opacity="0.52">
          <path
            d="M400 66 C420 66 430 112 430 154 L430 194 L668 294 L668 332 L430 278 L428 408 L512 464 L512 492 L400 462 L288 492 L288 464 L372 408 L370 278 L132 332 L132 294 L370 194 L370 154 C370 112 380 66 400 66 Z"
            fill="#06080B"
          />
        </g>

        <g transform="translate(0, 18) scale(0.92)" style={{ transformOrigin: "400px 280px" }}>
          <path
            d="M400 66 C420 66 430 112 430 154 L430 194 L668 294 L668 332 L430 278 L428 408 L512 464 L512 492 L400 462 L288 492 L288 464 L372 408 L370 278 L132 332 L132 294 L370 194 L370 154 C370 112 380 66 400 66 Z"
            fill="rgba(239, 229, 206, 0.10)"
            opacity={outlineReveal}
          />
          <path
            d="M400 66 C420 66 430 112 430 154 L430 194 L668 294 L668 332 L430 278 L428 408 L512 464 L512 492 L400 462 L288 492 L288 464 L372 408 L370 278 L132 332 L132 294 L370 194 L370 154 C370 112 380 66 400 66 Z"
            fill="none"
            stroke="#EFE5CE"
            strokeWidth="4.5"
            strokeLinejoin="round"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <g opacity={outlineReveal}>
            <rect x="288" y="210" width="24" height="54" rx="10" fill="#171D26" stroke="#EFE5CE" strokeWidth="3" />
            <rect x="488" y="210" width="24" height="54" rx="10" fill="#171D26" stroke="#EFE5CE" strokeWidth="3" />
          </g>
          <path
            d="M400 84 L400 448 M224 274 L224 302 M576 274 L576 302"
            fill="none"
            stroke="rgba(229, 169, 60, 0.65)"
            strokeWidth="3"
            strokeLinecap="round"
            pathLength={1}
            strokeDashoffset={1 - outlineReveal}
          />
          <g opacity={highlightFade}>
            <ellipse
              cx="400"
              cy="144"
              rx="24"
              ry="48"
              fill="rgba(230, 57, 70, 0.28)"
              stroke={alertColor}
              strokeWidth="3"
            />
            <circle cx="400" cy="132" r={12 * pulseScale} fill="rgba(230, 57, 70, 0.32)" />
            <circle cx="400" cy="132" r="7" fill={alertColor} />
          </g>
        </g>
      </>
    );
  };

  return (
    <TactilePaperStage accentColor="rgba(229, 169, 60, 0.14)">
      {/* CAPA 1: TITULAR EDITORIAL LIMPIO */}
      <EditorialHeadline
        kicker={kicker}
        headline={headline}
        accentColor={accentColor}
        translateY={headerY}
        opacity={headerOpacity}
        top={214}
      />

      {/* CAPA 2: HOJA DE CROQUIS 2.5D */}
      <div
        style={{
          position: "absolute",
          top: "396px",
          left: "55px",
          width: "780px",
          height: "575px",
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
            height={530}
            rotationDeg={-0.8}
            paperColor="#171D26"
            seed={31}
            style={{ margin: "12px auto 0 auto" }}
          >
            <svg width="708" height="480" viewBox="0 0 800 535" style={{ overflow: "visible" }}>
              <g stroke="rgba(239, 229, 206, 0.08)" strokeWidth="1">
                <line x1="0" y1="268" x2="800" y2="268" strokeDasharray="6 8" />
                <line x1="400" y1="20" x2="400" y2="515" strokeDasharray="6 8" />
                <circle cx="400" cy="268" r="190" fill="none" strokeDasharray="4 10" />
                <circle cx="400" cy="268" r="275" fill="none" strokeDasharray="3 12" />
              </g>

              {renderSchematic()}

              {/* Cota animada 1 (Izquierda superior) */}
              <g opacity={callout1Draw > 0 ? 1 : 0}>
                <path
                  d={pointers.p1}
                  fill="none"
                  stroke={alertColor}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  pathLength={1}
                  strokeDashoffset={1 - callout1Draw}
                />
                {callout1Draw > 0.6 && (
                  <g transform="translate(18, 62)" opacity={(callout1Draw - 0.6) / 0.4}>
                    <text fill={alertColor} fontSize="19" fontWeight="800" letterSpacing="1.5">
                      {calloutTitle}
                    </text>
                    <text y="28" fill="#F8F3E8" fontSize="22" fontWeight="900">
                      {calLine1}
                    </text>
                    {calLine2 && (
                      <text y="54" fill="#F8F3E8" fontSize="22" fontWeight="900">
                        {calLine2}
                      </text>
                    )}
                  </g>
                )}
              </g>

              {/* Cota animada 2 (Derecha superior) */}
              <g opacity={callout2Draw > 0 ? 1 : 0}>
                <path
                  d={pointers.p2}
                  fill="none"
                  stroke={accentColor}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  pathLength={1}
                  strokeDashoffset={1 - callout2Draw}
                />
                {callout2Draw > 0.6 && (
                  <g transform="translate(778, 72)" opacity={(callout2Draw - 0.6) / 0.4}>
                    <text textAnchor="end" fill={accentColor} fontSize="18" fontWeight="800" letterSpacing="1.4">
                      {secondaryLabel}
                    </text>
                    <text y="28" textAnchor="end" fill="#F8F3E8" fontSize="22" fontWeight="900">
                      {secLine1}
                    </text>
                    {secLine2 && (
                      <text y="54" textAnchor="end" fill="#F8F3E8" fontSize="22" fontWeight="900">
                        {secLine2}
                      </text>
                    )}
                  </g>
                )}
              </g>
            </svg>
          </DeckledPaperCutout>
        </div>
      </div>

      {/* CAPA 3: CINTA DE PAPEL RASGADO CON CONCLUSION LEGIBLE EN MOVIL */}
      <div
        style={{
          position: "absolute",
          left: "68px",
          top: "1004px",
          transform: `translate3d(0, ${bottomSlideY}px, 0)`,
          opacity: bottomOpacity,
        }}
      >
        <DeckledPaperCutout
          width={760}
          height={176}
          rotationDeg={1.2}
          paperColor="#EFE5CE"
          seed={47}
        >
          <div
            style={{
              fontSize: "19px",
              fontWeight: 900,
              letterSpacing: "2.3px",
              color: alertColor,
              marginBottom: "8px",
            }}
          >
            {bottomStamp}
          </div>
          <div
            style={{
              fontSize: bottomTakeaway.length > 46 ? "31px" : "36px",
              fontWeight: 900,
              lineHeight: 1.12,
              color: "#151920",
              letterSpacing: "-0.4px",
            }}
          >
            {bottomTakeaway}
          </div>
        </DeckledPaperCutout>
      </div>
    </TactilePaperStage>
  );
};
