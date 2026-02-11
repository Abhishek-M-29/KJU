import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

type AutoTableDoc = jsPDF & { lastAutoTable: { finalY: number } }

// ── Types (mirror the ProcessingPage types) ──
interface ShapFeature {
  name: string
  impact: number
  direction: 'positive' | 'negative'
}

interface HeatmapEntry {
  name: string
  value: number
}

interface QualitativeFactors {
  riskFactors: string[]
  protectiveFactors: string[]
  recommendations: string[]
}

interface DiagnosticReport {
  jobId: string
  patientId: string
  generatedAt: string
  status: string
  executiveSummary: string
  riskScore: number
  shapFeatures: ShapFeature[]
  featureHeatmap: HeatmapEntry[]
  qualitativeFactors: QualitativeFactors
}

interface PatientInfo {
  name: string
  age: number
  sex: 'M' | 'F'
  bloodType: string
  primaryCondition: string
}

// ── Color palette ──
const COLORS = {
  primary: [30, 64, 175] as [number, number, number],     // blue-800
  primaryLight: [219, 234, 254] as [number, number, number], // blue-100
  dark: [28, 25, 23] as [number, number, number],          // stone-900
  body: [68, 64, 60] as [number, number, number],          // stone-600
  muted: [120, 113, 108] as [number, number, number],      // stone-500
  light: [245, 245, 244] as [number, number, number],      // stone-100
  white: [255, 255, 255] as [number, number, number],
  red: [190, 18, 60] as [number, number, number],
  redBg: [255, 241, 242] as [number, number, number],
  green: [5, 150, 105] as [number, number, number],
  greenBg: [236, 253, 245] as [number, number, number],
  amber: [217, 119, 6] as [number, number, number],
  amberBg: [255, 251, 235] as [number, number, number],
  skyBg: [240, 249, 255] as [number, number, number],
  sky: [2, 132, 199] as [number, number, number],
  divider: [214, 211, 209] as [number, number, number],
}

function getRiskColor(score: number) {
  if (score >= 70) return { label: 'HIGH RISK', color: COLORS.red, bg: COLORS.redBg }
  if (score >= 40) return { label: 'MODERATE RISK', color: COLORS.amber, bg: COLORS.amberBg }
  return { label: 'LOW RISK', color: COLORS.green, bg: COLORS.greenBg }
}

// ── Helpers ──
function drawHorizontalRule(doc: jsPDF, y: number, margin: number, pageWidth: number) {
  doc.setDrawColor(...COLORS.divider)
  doc.setLineWidth(0.3)
  doc.line(margin, y, pageWidth - margin, y)
  return y + 4
}

function checkPageBreak(doc: jsPDF, y: number, needed: number, margin: number): number {
  const pageHeight = doc.internal.pageSize.getHeight()
  if (y + needed > pageHeight - margin) {
    doc.addPage()
    return margin + 10
  }
  return y
}

function drawSectionHeader(
  doc: jsPDF,
  label: string,
  title: string,
  y: number,
  margin: number,
  pageWidth: number
): number {
  y = checkPageBreak(doc, y, 20, margin)

  // Label badge
  doc.setFillColor(...COLORS.primaryLight)
  doc.roundedRect(margin, y - 5, 18, 8, 2, 2, 'F')
  doc.setFontSize(8)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...COLORS.primary)
  doc.text(label, margin + 9, y, { align: 'center' })

  // Title
  doc.setFontSize(13)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...COLORS.dark)
  doc.text(title, margin + 22, y + 0.5)

  // Underline
  doc.setDrawColor(...COLORS.primary)
  doc.setLineWidth(0.6)
  doc.line(margin, y + 4, pageWidth - margin, y + 4)

  return y + 12
}

function drawBulletList(
  doc: jsPDF,
  items: string[],
  y: number,
  margin: number,
  pageWidth: number,
  bulletColor: [number, number, number]
): number {
  const maxW = pageWidth - margin * 2 - 10
  doc.setFontSize(9.5)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...COLORS.body)

  for (const item of items) {
    y = checkPageBreak(doc, y, 12, margin)
    doc.setFillColor(...bulletColor)
    doc.circle(margin + 4, y - 1.2, 1.3, 'F')
    const lines = doc.splitTextToSize(item, maxW)
    doc.text(lines, margin + 10, y)
    y += lines.length * 4.5 + 2
  }
  return y
}

function drawNumberedList(
  doc: jsPDF,
  items: string[],
  y: number,
  margin: number,
  pageWidth: number,
  numColor: [number, number, number]
): number {
  const maxW = pageWidth - margin * 2 - 14
  doc.setFontSize(9.5)

  for (let i = 0; i < items.length; i++) {
    y = checkPageBreak(doc, y, 12, margin)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...numColor)
    doc.text(`${i + 1}.`, margin + 4, y)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(...COLORS.body)
    const lines = doc.splitTextToSize(items[i], maxW)
    doc.text(lines, margin + 14, y)
    y += lines.length * 4.5 + 2
  }
  return y
}

// ══════════════════════════════════════════
//  MAIN EXPORT
// ══════════════════════════════════════════
export function exportReportPdf(
  report: DiagnosticReport,
  patient: PatientInfo,
  executiveSummary: string,
  doctorNotes?: string
) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 18
  const contentWidth = pageWidth - margin * 2
  let y = 0

  // ════════════════════════════════════════
  //  COVER / HEADER BLOCK
  // ════════════════════════════════════════

  // Top accent bar
  doc.setFillColor(...COLORS.primary)
  doc.rect(0, 0, pageWidth, 3, 'F')

  y = 16

  // Logo area
  doc.setFillColor(...COLORS.primaryLight)
  doc.roundedRect(margin, y - 5, 12, 12, 2, 2, 'F')
  doc.setFontSize(14)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...COLORS.primary)
  doc.text('Q', margin + 6, y + 3, { align: 'center' })

  // Title block
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...COLORS.muted)
  doc.text('AEGIS DIAGNOSTICS', margin + 16, y - 1)

  doc.setFontSize(18)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...COLORS.dark)
  doc.text('AI Diagnostic Report', margin + 16, y + 6)

  // Right side metadata
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...COLORS.muted)
  const genDate = new Date(report.generatedAt)
  doc.text(
    `Generated: ${genDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`,
    pageWidth - margin,
    y - 1,
    { align: 'right' }
  )
  doc.text(`Job ID: ${report.jobId}`, pageWidth - margin, y + 3, { align: 'right' })
  doc.text(`Status: ${report.status.toUpperCase()}`, pageWidth - margin, y + 7, { align: 'right' })

  y += 16

  // Divider
  y = drawHorizontalRule(doc, y, margin, pageWidth)
  y += 2

  // ── Patient Information Table ──
  doc.setFillColor(...COLORS.light)
  doc.roundedRect(margin, y, contentWidth, 22, 2, 2, 'F')

  doc.setFontSize(8)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...COLORS.muted)
  doc.text('PATIENT INFORMATION', margin + 5, y + 5)

  const patientFields = [
    ['Name', patient.name],
    ['Patient ID', report.patientId],
    ['Age / Sex', `${patient.age} yrs / ${patient.sex === 'M' ? 'Male' : 'Female'}`],
    ['Blood Type', patient.bloodType],
    ['Primary Condition', patient.primaryCondition],
  ]

  const colW = contentWidth / 3
  let px = margin + 5
  let py = y + 11
  doc.setFontSize(8.5)
  for (let i = 0; i < patientFields.length; i++) {
    if (i === 3) {
      px = margin + 5
      py += 7
    }
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(...COLORS.muted)
    doc.text(`${patientFields[i][0]}:`, px, py)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...COLORS.dark)
    doc.text(patientFields[i][1], px + doc.getTextWidth(`${patientFields[i][0]}: `) + 1, py)
    px += colW
  }

  y += 30

  // ════════════════════════════════════════
  //  SECTION A — Executive Summary
  // ════════════════════════════════════════
  y = drawSectionHeader(doc, 'A', 'Executive Summary', y, margin, pageWidth)

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...COLORS.body)
  const summaryLines = doc.splitTextToSize(executiveSummary, contentWidth - 4)
  for (let i = 0; i < summaryLines.length; i++) {
    y = checkPageBreak(doc, y, 6, margin)
    doc.text(summaryLines[i], margin + 2, y)
    y += 4.5
  }
  y += 6

  // ════════════════════════════════════════
  //  SECTION B — Risk Probability
  // ════════════════════════════════════════
  y = drawSectionHeader(doc, 'B', 'Risk Probability Analysis', y, margin, pageWidth)

  const risk = getRiskColor(report.riskScore)

  // Risk score box
  y = checkPageBreak(doc, y, 32, margin)
  doc.setFillColor(...risk.bg)
  doc.roundedRect(margin, y, contentWidth, 26, 3, 3, 'F')
  doc.setDrawColor(...risk.color)
  doc.setLineWidth(0.5)
  doc.roundedRect(margin, y, contentWidth, 26, 3, 3, 'S')

  // Score value
  doc.setFontSize(32)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(...risk.color)
  doc.text(`${report.riskScore}%`, margin + 12, y + 17)

  // Label
  doc.setFontSize(10)
  doc.text(risk.label, margin + 12 + doc.getTextWidth(`${report.riskScore}% `), y + 17)

  // Subtitle
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...COLORS.muted)
  doc.text('Composite Risk Score — AI-generated probability assessment', margin + 12, y + 22)

  // Risk scale bar on right
  const barX = pageWidth - margin - 60
  const barW = 50
  const barY = y + 8
  const barH = 6

  // Gradient segments for the scale
  const segments = [
    { color: COLORS.green, w: barW * 0.4 },
    { color: COLORS.amber, w: barW * 0.3 },
    { color: COLORS.red, w: barW * 0.3 },
  ]
  let segX = barX
  for (const seg of segments) {
    doc.setFillColor(...seg.color)
    doc.rect(segX, barY, seg.w, barH, 'F')
    segX += seg.w
  }
  doc.setDrawColor(...COLORS.divider)
  doc.roundedRect(barX, barY, barW, barH, 1, 1, 'S')

  // Marker
  const markerX = barX + (report.riskScore / 100) * barW
  doc.setFillColor(...COLORS.dark)
  doc.triangle(markerX - 2, barY - 1, markerX + 2, barY - 1, markerX, barY + 1, 'F')

  doc.setFontSize(7)
  doc.setTextColor(...COLORS.muted)
  doc.text('0%', barX, barY + barH + 4)
  doc.text('100%', barX + barW, barY + barH + 4, { align: 'right' })
  doc.text('Risk Scale', barX + barW / 2, barY - 3, { align: 'center' })

  y += 34

  // ════════════════════════════════════════
  //  SECTION C — SHAP Analysis
  // ════════════════════════════════════════
  if (report.shapFeatures.length > 0) {
    y = drawSectionHeader(doc, 'C', 'Clinical Rationale (SHAP Analysis)', y, margin, pageWidth)

    // Table with autotable
    const shapData = report.shapFeatures.map((f) => [
      f.name,
      f.direction === 'positive' ? 'Protective' : 'Risk',
      `${f.direction === 'positive' ? '+' : ''}${f.impact.toFixed(3)}`,
    ])

    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [['Feature', 'Direction', 'SHAP Impact']],
      body: shapData,
      theme: 'grid',
      styles: {
        fontSize: 8.5,
        cellPadding: 3,
        textColor: COLORS.body,
        lineColor: COLORS.divider,
        lineWidth: 0.2,
      },
      headStyles: {
        fillColor: COLORS.primary,
        textColor: COLORS.white,
        fontStyle: 'bold',
        fontSize: 8.5,
      },
      columnStyles: {
        0: { cellWidth: 'auto', fontStyle: 'bold' },
        1: { cellWidth: 35, halign: 'center' },
        2: { cellWidth: 30, halign: 'right', fontStyle: 'bold' },
      },
      didParseCell: (data) => {
        if (data.section === 'body' && data.column.index === 1) {
          const val = data.cell.raw as string
          if (val === 'Risk') {
            data.cell.styles.textColor = COLORS.red
          } else {
            data.cell.styles.textColor = COLORS.green
          }
        }
        if (data.section === 'body' && data.column.index === 2) {
          const raw = String(data.cell.raw)
          if (raw.startsWith('+')) {
            data.cell.styles.textColor = COLORS.green
          } else {
            data.cell.styles.textColor = COLORS.red
          }
        }
      },
      alternateRowStyles: {
        fillColor: [250, 250, 249],
      },
    })

    y = (doc as AutoTableDoc).lastAutoTable.finalY + 8

    // Feature Heatmap
    if (report.featureHeatmap.length > 0) {
      y = checkPageBreak(doc, y, 30, margin)

      doc.setFontSize(9)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(...COLORS.dark)
      doc.text('Feature Risk Heatmap', margin + 2, y)
      y += 6

      const heatData = report.featureHeatmap.map((e) => [
        e.name,
        `${Math.round(e.value * 100)}%`,
        e.value > 0.7 ? 'Critical' : e.value > 0.5 ? 'Elevated' : e.value > 0.3 ? 'Moderate' : 'Normal',
      ])

      autoTable(doc, {
        startY: y,
        margin: { left: margin, right: margin },
        head: [['Feature', 'Value', 'Severity']],
        body: heatData,
        theme: 'grid',
        styles: {
          fontSize: 8.5,
          cellPadding: 3,
          textColor: COLORS.body,
          lineColor: COLORS.divider,
          lineWidth: 0.2,
        },
        headStyles: {
          fillColor: COLORS.primary,
          textColor: COLORS.white,
          fontStyle: 'bold',
          fontSize: 8.5,
        },
        columnStyles: {
          0: { fontStyle: 'bold' },
          1: { halign: 'center', cellWidth: 25 },
          2: { halign: 'center', cellWidth: 30 },
        },
        didParseCell: (data) => {
          if (data.section === 'body' && data.column.index === 2) {
            const val = data.cell.raw as string
            if (val === 'Critical') data.cell.styles.textColor = COLORS.red
            else if (val === 'Elevated') data.cell.styles.textColor = COLORS.amber
            else if (val === 'Moderate') data.cell.styles.textColor = COLORS.amber
            else data.cell.styles.textColor = COLORS.green
          }
        },
        alternateRowStyles: {
          fillColor: [250, 250, 249],
        },
      })

      y = (doc as AutoTableDoc).lastAutoTable.finalY + 8
    }
  }

  // ════════════════════════════════════════
  //  SECTION D — Qualitative Risk Factors
  // ════════════════════════════════════════
  y = drawSectionHeader(doc, 'D', 'Qualitative Risk Factors', y, margin, pageWidth)

  // Risk Factors
  if (report.qualitativeFactors.riskFactors.length > 0) {
    y = checkPageBreak(doc, y, 12, margin)
    doc.setFontSize(9.5)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...COLORS.red)
    doc.text('Risk Factors', margin + 2, y)
    y += 5
    y = drawBulletList(doc, report.qualitativeFactors.riskFactors, y, margin, pageWidth, COLORS.red)
    y += 3
  }

  // Protective Factors
  if (report.qualitativeFactors.protectiveFactors.length > 0) {
    y = checkPageBreak(doc, y, 12, margin)
    doc.setFontSize(9.5)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...COLORS.green)
    doc.text('Protective Factors', margin + 2, y)
    y += 5
    y = drawBulletList(doc, report.qualitativeFactors.protectiveFactors, y, margin, pageWidth, COLORS.green)
    y += 3
  }

  // Clinical Recommendations
  if (report.qualitativeFactors.recommendations.length > 0) {
    y = checkPageBreak(doc, y, 12, margin)
    doc.setFontSize(9.5)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(...COLORS.sky)
    doc.text('Clinical Recommendations', margin + 2, y)
    y += 5
    y = drawNumberedList(doc, report.qualitativeFactors.recommendations, y, margin, pageWidth, COLORS.sky)
    y += 3
  }

  // ════════════════════════════════════════
  //  Physician Notes (if any)
  // ════════════════════════════════════════
  if (doctorNotes && doctorNotes.trim()) {
    y += 4
    y = drawSectionHeader(doc, 'E', 'Physician Notes', y, margin, pageWidth)

    doc.setFillColor(...COLORS.light)
    const noteLines = doc.splitTextToSize(doctorNotes, contentWidth - 14)
    const noteH = noteLines.length * 4.5 + 10
    y = checkPageBreak(doc, y, noteH, margin)
    doc.roundedRect(margin, y - 2, contentWidth, noteH, 2, 2, 'F')

    doc.setFontSize(9.5)
    doc.setFont('helvetica', 'italic')
    doc.setTextColor(...COLORS.body)
    doc.text(noteLines, margin + 7, y + 4)
    y += noteH + 4
  }

  // ════════════════════════════════════════
  //  FOOTER on every page
  // ════════════════════════════════════════
  const totalPages = doc.getNumberOfPages()
  for (let p = 1; p <= totalPages; p++) {
    doc.setPage(p)

    // Bottom accent bar
    doc.setFillColor(...COLORS.primary)
    doc.rect(0, pageHeight - 3, pageWidth, 3, 'F')

    // Footer text
    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(...COLORS.muted)
    doc.text(
      'This report was generated by an AI diagnostic system and should be reviewed by a qualified healthcare professional.',
      pageWidth / 2,
      pageHeight - 8,
      { align: 'center' }
    )
    doc.text(
      `AEGIS Diagnostics  •  Confidential  •  Page ${p} of ${totalPages}`,
      pageWidth / 2,
      pageHeight - 5,
      { align: 'center' }
    )
  }

  // ── Download ──
  const filename = `Aegis-Report-${patient.name.replace(/\s+/g, '-')}-${report.jobId}.pdf`
  doc.save(filename)
}
