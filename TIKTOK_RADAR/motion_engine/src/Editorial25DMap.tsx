import React, { useMemo } from "react";
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { geoGraticule, geoInterpolate, geoMercator, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import countries50m from "world-atlas/countries-50m.json";
import {
  DeckledPaperCutout,
  EditorialHeadline,
  TactilePaperStage,
} from "./components/TactilePaperStage";

export interface MapPlace {
  name: string;
  code?: string;
  lon: number;
  lat: number;
}

export type MapMode = "diversion" | "route" | "epicenter";
export type MapMarkerIcon = "plane" | "rocket" | "pulse" | "chip";

export interface Editorial25DMapProps {
  kicker?: string;
  headline?: string;
  mapMode?: MapMode;
  markerIcon?: MapMarkerIcon;
  origin?: MapPlace;
  plannedDest?: MapPlace;
  diversionDest?: MapPlace;
  diversionRatio?: number;
  highlightCountries?: string[];
  stampText?: string;
  cardKicker?: string;
  cardHeadline?: string;
  cardLines?: string[];
  accentColor?: string;
  alertColor?: string;
}

const MAP_W = 1520;
const MAP_H = 2320;
const MAP_OFFSET_X = -220;
const MAP_OFFSET_Y = -200;

function sampleGeodesic(
  from: [number, number],
  to: [number, number],
  proj: (coords: [number, number]) => [number, number] | null,
  steps = 56
): Array<[number, number]> {
  const interp = geoInterpolate(from, to);
  const pts: Array<[number, number]> = [];
  for (let i = 0; i <= steps; i++) {
    const pt = proj(interp(i / steps));
    if (pt) pts.push(pt);
  }
  return pts;
}

function buildPolylineLength(pts: Array<[number, number]>): number[] {
  const cum = [0];
  for (let i = 1; i < pts.length; i++) {
    const dx = pts[i][0] - pts[i - 1][0];
    const dy = pts[i][1] - pts[i - 1][1];
    cum.push(cum[i - 1] + Math.hypot(dx, dy));
  }
  return cum;
}

function pointAtProgress(
  pts: Array<[number, number]>,
  cumLen: number[],
  t: number
): { x: number; y: number; angleDeg: number } {
  if (pts.length === 0) return { x: 0, y: 0, angleDeg: 0 };
  if (pts.length === 1) return { x: pts[0][0], y: pts[0][1], angleDeg: 0 };
  const clamped = Math.max(0, Math.min(1, t));
  const total = cumLen[cumLen.length - 1] || 1;
  const target = clamped * total;

  let idx = 1;
  while (idx < cumLen.length - 1 && cumLen[idx] < target) {
    idx++;
  }
  const prevLen = cumLen[idx - 1];
  const segLen = Math.max(1e-6, cumLen[idx] - prevLen);
  const localT = (target - prevLen) / segLen;
  const p0 = pts[idx - 1];
  const p1 = pts[idx];
  const x = p0[0] + (p1[0] - p0[0]) * localT;
  const y = p0[1] + (p1[1] - p0[1]) * localT;
  const angleDeg = (Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) * 180) / Math.PI;
  return { x, y, angleDeg };
}

function ptsToPathD(pts: Array<[number, number]>): string {
  return pts
    .map(([x, y], i) => `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ");
}

function clampLabel(
  pt: [number, number],
  dx: number,
  dy: number,
  anchor: "start" | "end" | "middle" = "start"
): { x: number; y: number; anchor: "start" | "end" | "middle" } {
  const minX = anchor === "end" ? 500 : anchor === "middle" ? 410 : 300;
  const maxX = anchor === "end" ? 1055 : anchor === "middle" ? 940 : 865;
  const x = Math.max(minX, Math.min(maxX, pt[0] + dx));
  const y = Math.max(615, Math.min(1090, pt[1] + dy));
  return { x, y, anchor };
}

function samePoint(a?: MapPlace, b?: MapPlace): boolean {
  if (!a || !b) return true;
  return Math.hypot(a.lon - b.lon, a.lat - b.lat) < 0.4;
}

export const Editorial25DMap: React.FC<Editorial25DMapProps> = ({
  kicker = "LOCALIZACIÓN GLOBAL",
  headline = "EL PUNTO CLAVE DEL REPORTE",
  mapMode,
  markerIcon = "plane",
  origin = { name: "ORIGEN", code: "", lon: -3.7038, lat: 40.4168 },
  plannedDest,
  diversionDest,
  diversionRatio = 0.56,
  highlightCountries = [],
  stampText = "REGISTRO ACTIVO",
  cardKicker = "COORDENADAS VERIFICADAS",
  cardHeadline = "CONTEXTO GEOGRÁFICO",
  cardLines = [
    "LOCALIZACIÓN DEL EVENTO REPORTADO",
    "SEGUIMIENTO POR CARTOGRAFÍA EN TIEMPO REAL",
  ],
  accentColor = "#E5A93C",
  alertColor = "#E63946",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const resolvedMode: MapMode = useMemo(() => {
    if (mapMode) return mapMode;
    if (diversionDest && plannedDest && !samePoint(origin, plannedDest) && !samePoint(plannedDest, diversionDest)) {
      return "diversion";
    }
    if (plannedDest && !samePoint(origin, plannedDest)) {
      return "route";
    }
    return "epicenter";
  }, [mapMode, origin, plannedDest, diversionDest]);

  const safePlanned = plannedDest || origin;
  const safeDiversion = diversionDest || safePlanned;

  const mapData = useMemo(() => {
    const topo: any = countries50m;
    const countriesGeo: any = feature(topo, topo.objects.countries);

    const rawPoints: Array<[number, number]> = [[origin.lon, origin.lat]];
    if (resolvedMode !== "epicenter") {
      rawPoints.push([safePlanned.lon, safePlanned.lat]);
    }
    if (resolvedMode === "diversion") {
      rawPoints.push([safeDiversion.lon, safeDiversion.lat]);
    }

    // Asegurar un encuadre minimo regional cuando hay 1 punto o puntos muy cercanos
    const lons = rawPoints.map((p) => p[0]);
    const lats = rawPoints.map((p) => p[1]);
    const spanLon = Math.max(...lons) - Math.min(...lons);
    const spanLat = Math.max(...lats) - Math.min(...lats);
    const padLon = spanLon < 16 ? 12 : 4;
    const padLat = spanLat < 12 ? 9 : 3;

    const minLon = Math.max(-175, Math.min(...lons) - padLon);
    const maxLon = Math.min(175, Math.max(...lons) + padLon);
    const minLat = Math.max(-72, Math.min(...lats) - padLat);
    const maxLat = Math.min(76, Math.max(...lats) + padLat);

    const routeBounds: any = {
      type: "FeatureCollection",
      features: [
        ...rawPoints.map(([lon, lat]) => ({
          type: "Feature",
          geometry: { type: "Point", coordinates: [lon, lat] },
          properties: {},
        })),
        { type: "Feature", geometry: { type: "Point", coordinates: [minLon, minLat] }, properties: {} },
        { type: "Feature", geometry: { type: "Point", coordinates: [maxLon, maxLat] }, properties: {} },
      ],
    };

    const proj = geoMercator().fitExtent(
      [
        [395, 655],
        [1015, 1080],
      ],
      routeBounds
    );
    const pathGen = geoPath(proj);
    const graticulePath = pathGen(geoGraticule().step([10, 10])()) || "";

    const highlightSet = new Set(highlightCountries.map((c) => c.toLowerCase()));
    const countryShapes = countriesGeo.features
      .map((f: any, i: number) => {
        const d = pathGen(f);
        if (!d) return null;
        const name = String(f.properties?.name || "").toLowerCase();
        return {
          id: f.id || i,
          d,
          highlighted: highlightSet.has(name),
        };
      })
      .filter(Boolean);

    const originPt = proj([origin.lon, origin.lat]) || [700, 860];
    const plannedPt = proj([safePlanned.lon, safePlanned.lat]) || originPt;
    const divPt = proj([safeDiversion.lon, safeDiversion.lat]) || plannedPt;

    const plannedPts =
      resolvedMode === "epicenter"
        ? [originPt]
        : sampleGeodesic([origin.lon, origin.lat], [safePlanned.lon, safePlanned.lat], proj, 64);
    const plannedCum = buildPolylineLength(plannedPts);
    const plannedTotal = plannedCum[plannedCum.length - 1] || 1;

    let leg1Pts = plannedPts;
    let leg1Cum = plannedCum;
    let leg1Total = plannedTotal;
    let turnPt = plannedPt;
    let leg2Pts: Array<[number, number]> = [];
    let leg2Cum = [0];
    let leg2Total = 1;

    if (resolvedMode === "diversion") {
      const turnGeo = geoInterpolate(
        [origin.lon, origin.lat],
        [safePlanned.lon, safePlanned.lat]
      )(diversionRatio);
      leg1Pts = sampleGeodesic([origin.lon, origin.lat], turnGeo, proj, 42);
      leg1Cum = buildPolylineLength(leg1Pts);
      leg1Total = leg1Cum[leg1Cum.length - 1] || 1;
      turnPt = proj(turnGeo) || originPt;

      const leg1EndPrev = leg1Pts[Math.max(0, leg1Pts.length - 2)] || turnPt;
      const tangentDx = turnPt[0] - leg1EndPrev[0];
      const tangentDy = turnPt[1] - leg1EndPrev[1];
      const tangLen = Math.hypot(tangentDx, tangentDy) || 1;
      const ctrlDist = Math.hypot(divPt[0] - turnPt[0], divPt[1] - turnPt[1]) * 0.45;
      const ctrlX = turnPt[0] + (tangentDx / tangLen) * ctrlDist;
      const ctrlY = turnPt[1] + (tangentDy / tangLen) * ctrlDist;

      for (let i = 0; i <= 40; i++) {
        const u = i / 40;
        const omt = 1 - u;
        const bx = omt * omt * turnPt[0] + 2 * omt * u * ctrlX + u * u * divPt[0];
        const by = omt * omt * turnPt[1] + 2 * omt * u * ctrlY + u * u * divPt[1];
        leg2Pts.push([bx, by]);
      }
      leg2Cum = buildPolylineLength(leg2Pts);
      leg2Total = leg2Cum[leg2Cum.length - 1] || 1;
    }

    // Ubicacion inteligente de etiquetas para evitar choques y salidas de Safe Zone
    const goingEast = plannedPt[0] >= originPt[0];
    const originLabel = clampLabel(
      originPt,
      goingEast ? -10 : 16,
      originPt[1] < 720 ? 48 : -46,
      goingEast ? "start" : "end"
    );
    const plannedLabel = clampLabel(
      plannedPt,
      goingEast ? -12 : 14,
      plannedPt[1] > 980 ? -36 : 44,
      goingEast ? "end" : "start"
    );
    const divLeftOfPlanned = divPt[0] <= plannedPt[0];
    const divLabel = clampLabel(
      divPt,
      divLeftOfPlanned ? -58 : 58,
      divPt[1] > 950 ? -52 : 76,
      divLeftOfPlanned ? "end" : "start"
    );

    return {
      graticulePath,
      countryShapes,
      originPt,
      plannedPt,
      diversionPt: divPt,
      turnPt,
      originLabel,
      plannedLabel,
      divLabel,
      plannedPathD: ptsToPathD(plannedPts),
      plannedTotal,
      leg1PathD: ptsToPathD(leg1Pts),
      leg1Pts,
      leg1Cum,
      leg1Total,
      leg2PathD: ptsToPathD(leg2Pts),
      leg2Pts,
      leg2Cum,
      leg2Total,
    };
  }, [origin, safePlanned, safeDiversion, diversionRatio, highlightCountries, resolvedMode]);

  const plannedDraw = interpolate(frame, [6, 46], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const turnFrame = 36;
  const leg1Progress = interpolate(
    frame,
    [6, resolvedMode === "diversion" ? turnFrame : Math.max(54, durationInFrames - 22)],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    }
  );

  const leg2Progress = interpolate(frame, [turnFrame, Math.max(68, durationInFrames - 24)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const pose =
    resolvedMode === "diversion" && frame >= turnFrame
      ? pointAtProgress(mapData.leg2Pts, mapData.leg2Cum, leg2Progress)
      : pointAtProgress(mapData.leg1Pts, mapData.leg1Cum, leg1Progress);

  const camProgress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });
  const camZoom = interpolate(camProgress, [0, 0.4, 1], [1.0, 1.08, 1.18]);
  const camTiltX = interpolate(camProgress, [0, 1], [11, 18]);
  const camYawZ = interpolate(camProgress, [0, 1], [-1.4, 1.8]);
  const camPanX = interpolate(camProgress, [0, 0.35, 1], [10, -6, -34]);
  const camPanY = interpolate(camProgress, [0, 0.35, 1], [14, -4, -28]);

  const turnRippleT = interpolate(frame, [turnFrame - 2, turnFrame + 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const destImpactT = interpolate(frame, [durationInFrames - 30, durationInFrames - 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.9, stiffness: 105 },
  });
  const titleY = interpolate(titleSpring, [0, 1], [26, 0]);
  const titleOpacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });

  const cardDelay = resolvedMode === "epicenter" ? 20 : 34;
  const cardSpring = spring({
    frame: Math.max(0, frame - cardDelay),
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 95 },
  });
  const cardSlideY = interpolate(cardSpring, [0, 1], [105, 0]);
  const cardOpacity = interpolate(frame, [cardDelay, cardDelay + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cardParallaxX = camPanX * 0.16;
  const cardParallaxY = camPanY * 0.12;

  const pinScaleOrigin = spring({ frame: Math.max(0, frame - 3), fps, config: { damping: 13 } });
  const pinScalePlanned = spring({ frame: Math.max(0, frame - 22), fps, config: { damping: 13 } });
  const pinScaleDiv = spring({ frame: Math.max(0, frame - 42), fps, config: { damping: 12 } });
  const pulseWave = (frame % 36) / 36;

  const renderMovingMarker = () => {
    if (resolvedMode === "epicenter") {
      return (
        <g transform={`translate(${mapData.originPt[0]}, ${mapData.originPt[1]})`}>
          <circle
            r={16 + pulseWave * 74}
            fill="none"
            stroke={alertColor}
            strokeWidth={3.5 * (1 - pulseWave)}
            opacity={1 - pulseWave}
          />
          <circle
            r={14 + ((pulseWave + 0.5) % 1) * 74}
            fill="none"
            stroke={accentColor}
            strokeWidth={2.5 * (1 - ((pulseWave + 0.5) % 1))}
            opacity={1 - ((pulseWave + 0.5) % 1)}
          />
        </g>
      );
    }

    if (markerIcon === "pulse" || markerIcon === "chip") {
      return (
        <g transform={`translate(${pose.x}, ${pose.y})`}>
          <circle r="18" fill="rgba(230, 57, 70, 0.25)" />
          <rect
            x="-9"
            y="-9"
            width="18"
            height="18"
            rx={markerIcon === "chip" ? "3" : "9"}
            transform={markerIcon === "chip" ? "rotate(45)" : undefined}
            fill="#FBF6EA"
            stroke={alertColor}
            strokeWidth="3"
          />
        </g>
      );
    }

    const shapePath =
      markerIcon === "rocket"
        ? "M0,-26 L7,-8 L7,14 L15,24 L6,21 L0,27 L-6,21 L-15,24 L-7,14 L-7,-8 Z"
        : "M0,-26 L5,-8 L26,4 L26,10 L5,4 L4,18 L12,24 L12,28 L0,25 L-12,28 L-12,24 L-4,18 L-5,4 L-26,10 L-26,4 L-5,-8 Z";

    return (
      <g>
        <g
          transform={`translate(${pose.x + 22}, ${pose.y + 34}) rotate(${pose.angleDeg + 90}) scale(0.92)`}
          opacity="0.52"
        >
          <path d={shapePath} fill="#000000" />
        </g>
        <g transform={`translate(${pose.x}, ${pose.y}) rotate(${pose.angleDeg + 90}) scale(1.16)`}>
          <path d={shapePath} fill="#FBF6EA" stroke="#1C222B" strokeWidth="1.5" />
        </g>
      </g>
    );
  };

  return (
    <TactilePaperStage accentColor="rgba(229, 169, 60, 0.15)">
      {/* CAPA 1: MAPA CARTOGRAFICO REAL EN PERSPECTIVA 2.5D */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          perspective: "1350px",
          perspectiveOrigin: "50% 45%",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: `${MAP_OFFSET_X}px`,
            top: `${MAP_OFFSET_Y}px`,
            width: `${MAP_W}px`,
            height: `${MAP_H}px`,
            transformOrigin: "54% 48%",
            transform: `translate3d(${camPanX}px, ${camPanY}px, 0px) scale(${camZoom}) rotateX(${camTiltX}deg) rotateZ(${camYawZ}deg)`,
          }}
        >
          <svg width={MAP_W} height={MAP_H} viewBox={`0 0 ${MAP_W} ${MAP_H}`}>
            <defs>
              <filter id="land-elevation" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="#020408" floodOpacity="0.82" />
              </filter>
              <filter id="route-glow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <linearGradient id="diversion-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={accentColor} />
                <stop offset="100%" stopColor={alertColor} />
              </linearGradient>
            </defs>

            <rect width={MAP_W} height={MAP_H} fill="#0B1018" />
            <path
              d={mapData.graticulePath}
              fill="none"
              stroke="rgba(235, 224, 198, 0.055)"
              strokeWidth="1.2"
            />

            <g filter="url(#land-elevation)">
              {mapData.countryShapes.map((c: any) => (
                <path
                  key={c.id}
                  d={c.d}
                  fill={c.highlighted ? "#2B3442" : "#181F29"}
                  stroke={
                    c.highlighted
                      ? "rgba(229, 169, 60, 0.44)"
                      : "rgba(226, 214, 185, 0.14)"
                  }
                  strokeWidth={c.highlighted ? "1.8" : "0.9"}
                />
              ))}
            </g>

            {resolvedMode === "diversion" && (
              <path
                d={mapData.plannedPathD}
                fill="none"
                stroke="rgba(239, 229, 206, 0.42)"
                strokeWidth="4"
                strokeDasharray="11 10"
                strokeLinecap="round"
                pathLength={1}
                strokeDashoffset={1 - plannedDraw}
              />
            )}

            {resolvedMode !== "epicenter" && (
              <path
                d={mapData.leg1PathD}
                fill="none"
                stroke={accentColor}
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={mapData.leg1Total}
                strokeDashoffset={mapData.leg1Total * (1 - leg1Progress)}
                filter="url(#route-glow)"
              />
            )}

            {resolvedMode === "diversion" && frame >= turnFrame - 2 && (
              <path
                d={mapData.leg2PathD}
                fill="none"
                stroke="url(#diversion-grad)"
                strokeWidth="7"
                strokeLinecap="round"
                strokeDasharray={mapData.leg2Total}
                strokeDashoffset={mapData.leg2Total * (1 - leg2Progress)}
                filter="url(#route-glow)"
              />
            )}

            {resolvedMode === "diversion" && turnRippleT > 0 && turnRippleT < 1 && (
              <g transform={`translate(${mapData.turnPt[0]}, ${mapData.turnPt[1]})`}>
                <circle
                  r={12 + turnRippleT * 62}
                  fill="none"
                  stroke={alertColor}
                  strokeWidth={4 * (1 - turnRippleT)}
                  opacity={1 - turnRippleT}
                />
                <circle r={7} fill={accentColor} />
              </g>
            )}

            {resolvedMode !== "epicenter" && destImpactT > 0 && (
              <g
                transform={`translate(${
                  resolvedMode === "diversion" ? mapData.diversionPt[0] : mapData.plannedPt[0]
                }, ${resolvedMode === "diversion" ? mapData.diversionPt[1] : mapData.plannedPt[1]})`}
              >
                <circle
                  r={10 + (destImpactT % 1) * 56}
                  fill="none"
                  stroke={alertColor}
                  strokeWidth="3.5"
                  opacity={1 - destImpactT}
                />
              </g>
            )}

            {/* Pin origen / epicentro */}
            <g transform={`translate(${mapData.originPt[0]}, ${mapData.originPt[1]}) scale(${pinScaleOrigin})`}>
              {resolvedMode === "epicenter" ? (
                <>
                  <circle r="24" fill="rgba(230, 57, 70, 0.28)" />
                  <circle r="12" fill={alertColor} stroke="#EFE5CE" strokeWidth="3" />
                </>
              ) : (
                <>
                  <circle r="11" fill="#EFE5CE" />
                  <circle r="5" fill="#0B1018" />
                </>
              )}
            </g>

            {/* Pin destino previsto */}
            {resolvedMode !== "epicenter" && (
              <g transform={`translate(${mapData.plannedPt[0]}, ${mapData.plannedPt[1]}) scale(${pinScalePlanned})`}>
                {resolvedMode === "route" ? (
                  <>
                    <circle r="20" fill="rgba(230, 57, 70, 0.22)" />
                    <circle r="10" fill={alertColor} stroke="#EFE5CE" strokeWidth="3" />
                  </>
                ) : (
                  <>
                    <circle
                      r="9"
                      fill="none"
                      stroke="rgba(239, 229, 206, 0.65)"
                      strokeWidth="3"
                      strokeDasharray="4 4"
                    />
                    <circle r="4" fill="rgba(239, 229, 206, 0.7)" />
                  </>
                )}
              </g>
            )}

            {/* Pin desvio */}
            {resolvedMode === "diversion" && (
              <g transform={`translate(${mapData.diversionPt[0]}, ${mapData.diversionPt[1]}) scale(${pinScaleDiv})`}>
                <circle r="22" fill="rgba(230, 57, 70, 0.24)" />
                <circle r="11" fill={alertColor} stroke="#EFE5CE" strokeWidth="3" />
              </g>
            )}

            {/* Etiqueta origen / epicentro */}
            <g
              transform={`translate(${mapData.originLabel.x}, ${mapData.originLabel.y})`}
              opacity={pinScaleOrigin}
            >
              <text
                x="0"
                y="0"
                textAnchor={mapData.originLabel.anchor}
                fill="#F8F3E8"
                fontSize="28"
                fontWeight="900"
                letterSpacing="1.3"
                style={{ textShadow: "0 4px 12px rgba(0,0,0,0.95)" }}
              >
                {origin.name}
              </text>
              <text
                x="0"
                y="26"
                textAnchor={mapData.originLabel.anchor}
                fill={resolvedMode === "epicenter" ? alertColor : accentColor}
                fontSize="17"
                fontWeight="800"
                letterSpacing="1.8"
              >
                {resolvedMode === "epicenter"
                  ? "EPICENTRO DEL REPORTE"
                  : origin.code
                  ? `ORIGEN · ${origin.code}`
                  : "PUNTO DE ORIGEN"}
              </text>
            </g>

            {/* Etiqueta destino */}
            {resolvedMode !== "epicenter" && (
              <g
                transform={`translate(${mapData.plannedLabel.x}, ${mapData.plannedLabel.y})`}
                opacity={pinScalePlanned * 0.92}
              >
                <text
                  x="0"
                  y="0"
                  textAnchor={mapData.plannedLabel.anchor}
                  fill="rgba(248, 243, 232, 0.92)"
                  fontSize="24"
                  fontWeight="800"
                  letterSpacing="1.1"
                >
                  {safePlanned.name}
                </text>
                <text
                  x="0"
                  y="24"
                  textAnchor={mapData.plannedLabel.anchor}
                  fill={resolvedMode === "route" ? alertColor : "rgba(239, 229, 206, 0.64)"}
                  fontSize="16"
                  fontWeight="700"
                  letterSpacing="1.5"
                >
                  {resolvedMode === "route"
                    ? safePlanned.code
                      ? `DESTINO · ${safePlanned.code}`
                      : "PUNTO DE IMPACTO"
                    : "DESTINO PREVISTO"}
                </text>
              </g>
            )}

            {/* Etiqueta desvio */}
            {resolvedMode === "diversion" && frame >= turnFrame && (
              <g opacity={pinScaleDiv}>
                <path
                  d={`M ${mapData.diversionPt[0]} ${mapData.diversionPt[1]} L ${mapData.divLabel.x} ${mapData.divLabel.y - 26}`}
                  fill="none"
                  stroke={alertColor}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <g transform={`translate(${mapData.divLabel.x}, ${mapData.divLabel.y})`}>
                  <text
                    x="0"
                    y="0"
                    textAnchor={mapData.divLabel.anchor}
                    fill="#FFFFFF"
                    fontSize="32"
                    fontWeight="900"
                    letterSpacing="1.2"
                  >
                    {safeDiversion.name}
                  </text>
                  <text
                    x="0"
                    y="28"
                    textAnchor={mapData.divLabel.anchor}
                    fill={alertColor}
                    fontSize="19"
                    fontWeight="800"
                    letterSpacing="1.6"
                  >
                    DESVÍO DE EMERGENCIA
                  </text>
                </g>
              </g>
            )}

            {renderMovingMarker()}
          </svg>
        </div>
      </div>

      {/* Gradiente editorial superior e inferior */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "linear-gradient(180deg, rgba(8,10,15,0.88) 0%, rgba(8,10,15,0.34) 20%, transparent 34%, transparent 65%, rgba(8,10,15,0.88) 100%)",
        }}
      />

      {/* CAPA 2: TITULAR EDITORIAL */}
      <EditorialHeadline
        kicker={kicker}
        headline={headline}
        accentColor={accentColor}
        translateX={camPanX * 0.08}
        translateY={titleY}
        opacity={titleOpacity}
        top={214}
      />

      {/* CAPA 3: FICHA DE PAPEL ARCHIVAL EN PARALAJE 2.5D */}
      <div
        style={{
          position: "absolute",
          left: "68px",
          top: "968px",
          transform: `translate3d(${cardParallaxX}px, ${cardSlideY + cardParallaxY}px, 0)`,
          opacity: cardOpacity,
        }}
      >
        <DeckledPaperCutout
          width={760}
          height={216}
          rotationDeg={-1.8}
          paperColor="#EFE5CE"
          seed={19}
        >
          <div
            style={{
              position: "absolute",
              right: "24px",
              top: "20px",
              border: `3.5px solid ${alertColor}`,
              padding: "4px 11px",
              transform: "rotate(4deg)",
              color: alertColor,
              fontSize: stampText.length > 14 ? "15px" : "17px",
              fontWeight: 900,
              letterSpacing: "1.4px",
              opacity: 0.9,
              maxWidth: "275px",
              whiteSpace: "nowrap",
              overflow: "hidden",
            }}
          >
            {stampText}
          </div>

          <div
            style={{
              fontSize: "19px",
              fontWeight: 800,
              letterSpacing: "2px",
              color: "#7A5B2B",
              marginBottom: "8px",
              maxWidth: "440px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {cardKicker}
          </div>

          <div
            style={{
              fontSize: cardHeadline.length > 26 ? "27px" : cardHeadline.length > 19 ? "31px" : "36px",
              fontWeight: 900,
              color: "#171B22",
              letterSpacing: "-0.3px",
              marginBottom: "14px",
              maxWidth: "495px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {cardHeadline}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {cardLines.slice(0, 2).map((ln, idx) => (
              <div
                key={idx}
                style={{
                  fontSize: "23px",
                  fontWeight: 700,
                  color: "#2C3340",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                }}
              >
                <span
                  style={{
                    width: "10px",
                    height: "10px",
                    borderRadius: "50%",
                    backgroundColor: idx === 1 ? alertColor : "#171B22",
                    display: "inline-block",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {ln}
                </span>
              </div>
            ))}
          </div>
        </DeckledPaperCutout>
      </div>
    </TactilePaperStage>
  );
};
