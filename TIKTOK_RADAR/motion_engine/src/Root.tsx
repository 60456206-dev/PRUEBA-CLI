import React from "react";
import { Composition } from "remotion";
import { VeritasiumAltimeter, AltimeterProps } from "./VeritasiumAltimeter";
import { VeritasiumTechChip, TechChipProps } from "./VeritasiumTechChip";
import { VeritasiumCyberRadar, CyberRadarProps } from "./VeritasiumCyberRadar";
import { VeritasiumStatComparison, StatComparisonProps } from "./VeritasiumStatComparison";
import { VeritasiumDocumentaryOutro, DocumentaryOutroProps } from "./VeritasiumDocumentaryOutro";
import { VeritasiumBlueprint, BlueprintProps } from "./VeritasiumBlueprint";
import { Editorial25DMap, Editorial25DMapProps } from "./Editorial25DMap";
import { Editorial25DDiagram, Editorial25DDiagramProps } from "./Editorial25DDiagram";
import { Editorial25DFactSheet, Editorial25DFactSheetProps } from "./Editorial25DFactSheet";
import { Editorial25DOutro, Editorial25DOutroProps } from "./Editorial25DOutro";
import { Editorial25DReceipt, Editorial25DReceiptProps } from "./Editorial25DReceipt";

export const Root: React.FC = () => {
  return (
    <>
      {/* SUITE PRINCIPAL: ANIMACIÓN EDITORIAL 2.5D TÁCTIL */}
      <Composition
        id="Editorial25DMap"
        component={Editorial25DMap}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as Editorial25DMapProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
        }}
        defaultProps={{
          kicker: "LOCALIZACIÓN DEL REPORTE",
          headline: "MAPA EDITORIAL EN PERSPECTIVA",
          markerIcon: "plane",
          origin: { name: "MADRID", code: "MAD", lon: -3.7038, lat: 40.4168 },
          highlightCountries: ["Spain"],
          stampText: "REGISTRO ACTIVO",
          cardKicker: "COORDENADAS VERIFICADAS",
          cardHeadline: "CONTEXTO GEOGRÁFICO",
          cardLines: [
            "UBICACIÓN REPORTADA EN PRENSA OFICIAL",
            "SEGUIMIENTO CARTOGRÁFICO EN TIEMPO REAL",
          ],
          accentColor: "#E5A93C",
          alertColor: "#E63946",
        }}
      />

      <Composition
        id="Editorial25DDiagram"
        component={Editorial25DDiagram}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as Editorial25DDiagramProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
        }}
        defaultProps={{
          kicker: "DECONSTRUCCIÓN TÉCNICA",
          headline: "EL MECANISMO DETRÁS DE LA NOTICIA",
          diagramKind: "aircraft",
          calloutTitle: "PUNTO CRÍTICO",
          calloutDetail: "ALERTA PREVENTIVA",
          secondaryLabel: "RESPUESTA TÉCNICA",
          secondaryCallout: "PROTOCOLO DE SEGURIDAD",
          bottomStamp: "CLAVE OPERATIVA",
          bottomTakeaway: "PRIORIZAR EL MARGEN ANTE LO INCIERTO",
          accentColor: "#E5A93C",
          alertColor: "#E63946",
        }}
      />

      <Composition
        id="Editorial25DFactSheet"
        component={Editorial25DFactSheet}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as Editorial25DFactSheetProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
        }}
        defaultProps={{
          kicker: "EVIDENCIA DEL REPORTE",
          headline: "EL DATO QUE EXPLICA EL CASO",
          mode: "comparison",
          heroValue: "CLAVE",
          heroUnit: "DATO REPORTADO",
          heroCaption: "PARÁMETRO CONTRASTADO EN EL REPORTE",
          leftLabel: "CONDICIÓN PREVISTA",
          leftValue: "OPERACIÓN ESTÁNDAR",
          leftRatio: 42,
          rightLabel: "HECHO CONFIRMADO",
          rightValue: "MANIOBRA PREVENTIVA",
          rightRatio: 88,
          sourceStamp: "FUENTE OFICIAL",
          bottomTakeaway: "EL MARGEN DE SEGURIDAD DEFINE EL DESENLACE",
          accentColor: "#E5A93C",
          alertColor: "#E63946",
        }}
      />

      <Composition
        id="Editorial25DReceipt"
        component={Editorial25DReceipt}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as Editorial25DReceiptProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
        }}
        defaultProps={{
          kicker: "EVIDENCIA DOCUMENTAL",
          headline: "LO QUE CONFIRMA EL REPORTE",
          sourceName: "PRENSA OFICIAL",
          publicationDate: "REGISTRO CONTRASTADO",
          articleTitle: "Reporte técnico verificado en fuentes primarias",
          receiptQuote: "Los registros operativos confirman la detección temprana de una anomalía antes de comprometer la seguridad del sistema.",
          highlightPhrase: "detección temprana de una anomalía",
          keyMetricBadge: "",
          bottomTakeaway: "LA EVIDENCIA DOCUMENTAL EXPLICA EL GIRO DEL CASO",
          accentColor: "#E5A93C",
          alertColor: "#E63946",
        }}
      />

      <Composition
        id="Editorial25DOutro"
        component={Editorial25DOutro}
        durationInFrames={144}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as Editorial25DOutroProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 144 };
        }}
        defaultProps={{
          kicker: "PRIMEROS PRINCIPIOS",
          headline: "LO QUE DEJA ESTE CASO",
          quote: "La seguridad moderna no depende de esperar la falla, sino de actuar antes de perder el margen.",
          takeaway: "CRITERIO PREVENTIVO ANTE LO IMPREVISTO",
          sourceTag: "PRENSA OFICIAL VERIFICADA",
          accentColor: "#E5A93C",
          alertColor: "#E63946",
        }}
      />

      {/* ALIAS DE COMPATIBILIDAD LEGADA (NO USADOS POR EL ROUTER POR DEFECTO) */}
      <Composition
        id="VeritasiumAltimeter"
        component={VeritasiumAltimeter}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as AltimeterProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
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
      <Composition
        id="VeritasiumTechChip"
        component={VeritasiumTechChip}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as TechChipProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
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
      <Composition
        id="VeritasiumCyberRadar"
        component={VeritasiumCyberRadar}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as CyberRadarProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
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
      <Composition
        id="VeritasiumStatComparison"
        component={VeritasiumStatComparison}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as StatComparisonProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
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
      <Composition
        id="VeritasiumBlueprint"
        component={VeritasiumBlueprint}
        durationInFrames={120}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as BlueprintProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 120 };
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
      <Composition
        id="VeritasiumDocumentaryOutro"
        component={VeritasiumDocumentaryOutro}
        durationInFrames={144}
        fps={24}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const customProps = props as DocumentaryOutroProps & { durationInFrames?: number };
          return { durationInFrames: customProps.durationInFrames || 144 };
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
