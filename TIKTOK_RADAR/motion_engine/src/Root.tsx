import React from "react";
import { Composition } from "remotion";
import { VeritasiumAltimeter, AltimeterProps } from "./VeritasiumAltimeter";
import { VeritasiumTechChip, TechChipProps } from "./VeritasiumTechChip";
import { VeritasiumCyberRadar, CyberRadarProps } from "./VeritasiumCyberRadar";
import { VeritasiumStatComparison, StatComparisonProps } from "./VeritasiumStatComparison";
import { VeritasiumDocumentaryOutro, DocumentaryOutroProps } from "./VeritasiumDocumentaryOutro";
import { VeritasiumBlueprint, BlueprintProps } from "./VeritasiumBlueprint";

export const Root: React.FC = () => {
  return (
    <>
      {/* 1. G1 AVIACIÓN / TELEMETRÍA */}
      <Composition
        id="VeritasiumAltimeter"
        component={VeritasiumAltimeter}
        durationInFrames={120} // 5.0 segundos a 24 fps
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as AltimeterProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 120,
          };
        }}
        defaultProps={{
          title: "REGISTRO DE TELEMETRÍA DE CABINA",
          subtitle: "ALTITUD Y TASA DE DESCENSO CRÍTICA",
          initialAlt: 35000,
          finalAlt: 3200,
          flightNumber: "FL-892 MAYDAY",
          warningText: "ALERTA: PULL UP · TERRAIN AHEAD",
          descentRate: "-3,400 FPM",
        }}
      />

      {/* 2. G3 TECH / HARDWARE / CHIPS 2NM / IA */}
      <Composition
        id="VeritasiumTechChip"
        component={VeritasiumTechChip}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as TechChipProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 120,
          };
        }}
        defaultProps={{
          title: "ARQUITECTURA DE SILICIO 2NM",
          subtitle: "LITOGRAFÍA EXTREMA EUV Y NANOSHEETS GAA",
          nodeSize: "2 NM",
          transistorCount: "33.7 BILLONES",
          efficiencyGain: "+30% EFICIENCIA / +15% VELOCIDAD",
          architectureTag: "GAA NANOSHEET 3D",
        }}
      />

      {/* 3. G2 CIBERATAQUES / ZERO-DAY / GUERRA DIGITAL */}
      <Composition
        id="VeritasiumCyberRadar"
        component={VeritasiumCyberRadar}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as CyberRadarProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 120,
          };
        }}
        defaultProps={{
          title: "ATAQUE DDOS MULTIVECTORIAL DETECTADO",
          subtitle: "COLAPSO DE ENRUTAMIENTO BGP Y SOBRECARGA DE NODOS",
          packetRate: "14.8 M PPS",
          cveSeverity: "CVSS 9.8 · CRÍTICO",
          threatVector: "ZERO-DAY EXPLOITATION",
          targetCount: "184 NODOS COMPROMETIDOS",
        }}
      />

      {/* 4. G4 / UNIVERSAL: COMPARATIVA DE DATOS Y ESCALA */}
      <Composition
        id="VeritasiumStatComparison"
        component={VeritasiumStatComparison}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as StatComparisonProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 120,
          };
        }}
        defaultProps={{
          title: "ESCALA DE IMPACTO Y TELEMETRÍA",
          subtitle: "COMPARATIVA DE MAGNITUD TÉCNICA Y OPERATIVA",
          labelA: "PARÁMETRO BASE",
          valA: "FASE 01",
          percentA: 28,
          labelB: "UMBRAL REPORTADO",
          valB: "FASE 02",
          percentB: 94,
          multiplierTag: "COMPARATIVA TÉCNICA DOCUMENTADA",
          sourceTag: "AUDITORÍA OFICIAL REGISTRADA",
          theme: "universal",
        }}
      />

      {/* 5. BLUEPRINT / WIREFRAME / ARQUITECTURA TÉCNICA */}
      <Composition
        id="VeritasiumBlueprint"
        component={VeritasiumBlueprint}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as BlueprintProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 120,
          };
        }}
        defaultProps={{
          title: "DESGLOSE DE ARQUITECTURA CRÍTICA",
          subtitle: "ESQUEMA DE COMPONENTES Y VECTORES DE FALLO",
          componentA: "MECANISMO DE CONTROL PRIMARIO",
          statusA: "VULNERABILIDAD AISLADA",
          metricA: "98.4% INTEGRIDAD",
          componentB: "BUS DE TRANSMISIÓN PRINCIPAL",
          statusB: "REDUNDANCIA ACTIVA",
          metricB: "CANAL DUAL 100%",
          componentC: "SISTEMA DE MITIGACIÓN DE EMERGENCIA",
          statusC: "OPERACIÓN NORMAL",
          metricC: "TIEMPO RESPUESTA 42ms",
          blueprintTag: "BLUEPRINT TÉCNICO V3 · AUDITORÍA",
          theme: "aviation",
        }}
      />

      {/* 6. CIERRE DOCUMENTAL / CONCLUSIÓN VERITASIUM */}
      <Composition
        id="VeritasiumDocumentaryOutro"
        component={VeritasiumDocumentaryOutro}
        durationInFrames={144} // 6.0 segundos a 24 fps
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as DocumentaryOutroProps & { durationInFrames?: number };
          return {
            durationInFrames: customProps.durationInFrames || 144,
          };
        }}
        defaultProps={{
          title: "CONCLUSIÓN Y PRIMEROS PRINCIPIOS",
          subtitle: "LECCIÓN TÉCNICA · SISTEMAS COMPLEJOS Y RESILIENCIA",
          quote: "La tecnología avanzada no elimina la incertidumbre: diseña sistemas capaces de sobrevivir a ella.",
          takeaway: "INGENIO Y RESILIENCIA ANTE LO IMPREVISTO",
          sourceTag: "AUDITORÍA TÉCNICA VERIFICADA · TIKTOK RADAR",
          theme: "aviation",
        }}
      />
    </>
  );
};
