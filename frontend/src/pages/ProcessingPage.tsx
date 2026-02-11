import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Download,
  FileCheck,
  RefreshCw,
  Sparkles,
  Save,
  TrendingUp,
  TrendingDown,
  Loader2,
  CheckCircle2,
  XCircle,
  Brain,
  Cpu,
  FlaskConical,
} from 'lucide-react'
import { mockPatients } from '@/data/patients'
import { exportReportPdf } from '@/lib/exportPdf'

// ── API URLs ──
const API_BASE = 'http://localhost:8000/api/diagnostics'

// ── Types matching backend DiagnosticReport schema ──
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

interface PipelineStage {
  key: string
  label: string
  description: string
  icon: React.ReactNode
  minProgress: number
}

const PIPELINE_STAGES: PipelineStage[] = [
  {
    key: 'init',
    label: 'Initializing Pipeline',
    description: 'Preparing raw patient data for analysis',
    icon: <Cpu className="w-5 h-5" />,
    minProgress: 0,
  },
  {
    key: 'extract',
    label: 'Medical Detail Extraction',
    description: 'LLM filtering clinical details for MedGemma',
    icon: <FlaskConical className="w-5 h-5" />,
    minProgress: 10,
  },
  {
    key: 'parallel',
    label: 'ML Swarm + MedGemma',
    description: 'Running parallel numeric & text analysis branches',
    icon: <Brain className="w-5 h-5" />,
    minProgress: 20,
  },
  {
    key: 'synthesis',
    label: 'Synthesis Agent',
    description: 'Generating coherent diagnostic report via Groq LLM',
    icon: <Sparkles className="w-5 h-5" />,
    minProgress: 50,
  },
  {
    key: 'validation',
    label: 'Report Validation',
    description: 'Validating report schema and finalizing',
    icon: <CheckCircle2 className="w-5 h-5" />,
    minProgress: 80,
  },
  {
    key: 'complete',
    label: 'Complete',
    description: 'Pipeline finished — report ready',
    icon: <FileCheck className="w-5 h-5" />,
    minProgress: 100,
  },
]

export function ProcessingPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const jobId = searchParams.get('jobId')
  const patientId = searchParams.get('patientId')

  // ── Pipeline polling state ──
  const [progress, setProgress] = useState(0)
  const [pipelineStatus, setPipelineStatus] = useState<'processing' | 'complete' | 'failed'>('processing')
  const [error, setError] = useState<string | null>(null)

  // ── Report display state ──
  const [report, setReport] = useState<DiagnosticReport | null>(null)
  const [reportStatus, setReportStatus] = useState<'draft' | 'finalized'>('draft')
  const [doctorNotes, setDoctorNotes] = useState('')
  const [isRebuilding, setIsRebuilding] = useState(false)
  const [executiveSummary, setExecutiveSummary] = useState('')

  const patient = mockPatients.find((p) => p.id === patientId) || mockPatients[0]

  // ── Poll backend for job status ──
  const pollStatus = useCallback(async () => {
    if (!jobId) return
    try {
      const res = await fetch(`${API_BASE}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jobId }),
      })
      if (!res.ok) return
      const data = await res.json()
      setProgress(data.progress ?? 0)

      if (data.status === 'complete') {
        setPipelineStatus('complete')
        // Now fetch the full report
        const reportRes = await fetch(`${API_BASE}/report`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ jobId }),
        })
        if (reportRes.ok) {
          const reportData: DiagnosticReport = await reportRes.json()
          setReport(reportData)
          setExecutiveSummary(reportData.executiveSummary || '')
        }
      } else if (data.status === 'failed') {
        setPipelineStatus('failed')
        setError(data.error || 'Pipeline failed')
      }
    } catch (err) {
      console.error('Polling error:', err)
    }
  }, [jobId])

  useEffect(() => {
    if (!jobId) {
      navigate('/dashboard')
      return
    }
    // Poll immediately (via setTimeout to avoid sync setState in effect),
    // then every 2 seconds while processing
    const timeout = setTimeout(pollStatus, 0)
    const interval = setInterval(() => {
      if (pipelineStatus === 'processing') {
        pollStatus()
      }
    }, 2000)
    return () => {
      clearTimeout(timeout)
      clearInterval(interval)
    }
  }, [jobId, pipelineStatus, pollStatus, navigate])

  // ── Handlers for report phase ──
  const handleRebuildReport = async () => {
    if (!doctorNotes.trim() || !report) return
    setIsRebuilding(true)
    await new Promise((r) => setTimeout(r, 2000))
    setExecutiveSummary(
      `${executiveSummary}\n\n[Updated based on physician input: ${doctorNotes}]\n\nThe clinical context has been revised to incorporate the attending physician's observations.`
    )
    setDoctorNotes('')
    setIsRebuilding(false)
  }

  const handleFinalize = () => setReportStatus('finalized')

  const handleSaveToRecord = () => {
    alert('Report saved to patient record (PostgreSQL Vector DB)')
    navigate('/dashboard')
  }

  // ── Current pipeline stage ──
  const currentStageIndex = PIPELINE_STAGES.findIndex(
    (_s, i) => i === PIPELINE_STAGES.length - 1 || PIPELINE_STAGES[i + 1].minProgress > progress
  )

  // ── Risk classification ──
  const getRiskClass = (score: number) => {
    if (score >= 70)
      return { label: 'High Risk', color: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-200', ring: '#e11d48', track: '#fecaca' }
    if (score >= 40)
      return { label: 'Moderate Risk', color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', ring: '#d97706', track: '#fde68a' }
    return { label: 'Low Risk', color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', ring: '#059669', track: '#a7f3d0' }
  }

  // ═══════════════════════════════════════════════
  // PHASE 1 — PROCESSING  (poll until done)
  // ═══════════════════════════════════════════════
  if (pipelineStatus === 'processing' || (pipelineStatus === 'complete' && !report)) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-2xl mx-auto px-6"
        >
          {/* Header */}
          <div className="text-center mb-10">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center"
            >
              <Brain className="w-8 h-8 text-primary" />
            </motion.div>
            <h1 className="text-2xl font-display font-bold text-stone-900 mb-2">
              Diagnostic Pipeline Running
            </h1>
            <p className="text-stone-500 text-sm">
              Job: <span className="font-mono text-stone-700">{jobId}</span>
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-stone-600">Progress</span>
              <span className="text-sm font-bold text-primary">{progress}%</span>
            </div>
            <div className="h-3 bg-stone-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-primary-dark rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </div>

          {/* Pipeline Stages */}
          <div className="bg-white rounded-2xl border border-stone-200 p-6 space-y-1">
            {PIPELINE_STAGES.map((stage, i) => {
              const isComplete = progress >= (PIPELINE_STAGES[i + 1]?.minProgress ?? 101)
              const isCurrent = i === currentStageIndex
              const isPending = !isComplete && !isCurrent

              return (
                <motion.div
                  key={stage.key}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-colors ${
                    isCurrent ? 'bg-primary/5' : ''
                  }`}
                >
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors ${
                      isComplete
                        ? 'bg-emerald-100 text-emerald-600'
                        : isCurrent
                          ? 'bg-primary/10 text-primary'
                          : 'bg-stone-100 text-stone-400'
                    }`}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : isCurrent ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      stage.icon
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className={`text-sm font-semibold ${
                        isComplete ? 'text-emerald-700' : isCurrent ? 'text-stone-900' : 'text-stone-400'
                      }`}
                    >
                      {stage.label}
                    </p>
                    <p className={`text-xs ${isPending ? 'text-stone-300' : 'text-stone-500'}`}>
                      {stage.description}
                    </p>
                  </div>
                  {isComplete && (
                    <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md">
                      Done
                    </span>
                  )}
                  {isCurrent && (
                    <span className="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded-md">
                      Running
                    </span>
                  )}
                </motion.div>
              )
            })}
          </div>

          {/* Patient info */}
          <div className="mt-6 text-center">
            <p className="text-sm text-stone-400">
              Processing data for{' '}
              <span className="font-medium text-stone-600">{patient.name}</span>
            </p>
          </div>
        </motion.div>
      </div>
    )
  }

  // ═══════════════════════════════════════════════
  // PHASE 2 — FAILED
  // ═══════════════════════════════════════════════
  if (pipelineStatus === 'failed') {
    return (
      <div className="min-h-screen bg-[#FAFAF9] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-lg mx-auto px-6 text-center"
        >
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-rose-50 flex items-center justify-center">
            <XCircle className="w-8 h-8 text-rose-500" />
          </div>
          <h1 className="text-2xl font-display font-bold text-stone-900 mb-2">Pipeline Failed</h1>
          <p className="text-stone-500 text-sm mb-4">
            Job: <span className="font-mono">{jobId}</span>
          </p>
          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 mb-6 text-left">
              <p className="text-sm text-rose-700 font-mono">{error}</p>
            </div>
          )}
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-stone-900 text-white rounded-xl font-medium hover:bg-stone-800 transition-colors"
          >
            Go Back
          </button>
        </motion.div>
      </div>
    )
  }

  // ═══════════════════════════════════════════════
  // PHASE 3 — RESULTS  (report is loaded)
  // ═══════════════════════════════════════════════
  if (!report) return null

  const riskInfo = getRiskClass(report.riskScore)
  const maxImpact = Math.max(...report.shapFeatures.map((f) => Math.abs(f.impact)), 1)

  return (
    <div className="min-h-screen bg-[#FAFAF9]">
      {/* Top Bar */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(`/patient/${patient.id}`)}
              className="p-2 rounded-lg hover:bg-stone-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-stone-600" />
            </button>
            <div>
              <h1 className="text-lg font-semibold text-stone-900">Report Synthesis</h1>
              <p className="text-xs text-stone-500">
                {patient.name} &bull; {report.jobId}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-stone-400 font-mono">{report.generatedAt}</span>
            <div
              className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                reportStatus === 'draft'
                  ? 'bg-amber-100 text-amber-700 border border-amber-200'
                  : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
              }`}
            >
              {reportStatus === 'draft' ? 'Draft \u2022 AI-Generated' : 'Finalized'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1800px] mx-auto p-6">
        <div className="grid grid-cols-[1fr_380px] gap-6 min-h-[calc(100vh-120px)]">
          {/* ── Left Panel: Report ── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-stone-200 shadow-sm overflow-hidden"
          >
            {/* Report Header */}
            <div className="px-8 py-6 border-b border-stone-100 bg-gradient-to-r from-stone-50 to-white">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-semibold text-primary uppercase tracking-widest mb-1">
                    AI Diagnostic Report
                  </p>
                  <h2 className="text-2xl font-display font-bold text-stone-900">
                    Health Risk Assessment Report
                  </h2>
                </div>
                <div className="text-right text-sm text-stone-500">
                  <p>Generated: {new Date(report.generatedAt).toLocaleDateString()}</p>
                  <p>Job: {report.jobId}</p>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-6 text-sm">
                <div>
                  <span className="text-stone-400">Patient:</span>{' '}
                  <span className="font-medium text-stone-700">{patient.name}</span>
                </div>
                <div>
                  <span className="text-stone-400">ID:</span>{' '}
                  <span className="font-medium text-stone-700">{report.patientId}</span>
                </div>
                <div>
                  <span className="text-stone-400">Age:</span>{' '}
                  <span className="font-medium text-stone-700">{patient.age} years</span>
                </div>
              </div>
            </div>

            {/* Report Body */}
            <div className="p-8 space-y-8 overflow-y-auto max-h-[calc(100vh-280px)] custom-scrollbar">
              {/* A: Executive Summary */}
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-bold text-sm">A</span>
                  </div>
                  <h3 className="font-display text-lg font-semibold text-stone-900">
                    Executive Summary
                  </h3>
                </div>
                <div className="pl-10">
                  <p className="text-stone-700 leading-relaxed text-[15px] text-justify">
                    {executiveSummary}
                  </p>
                </div>
              </section>

              {/* B: Risk Probability */}
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-bold text-sm">B</span>
                  </div>
                  <h3 className="font-display text-lg font-semibold text-stone-900">
                    Risk Probability Analysis
                  </h3>
                </div>
                <div className="pl-10">
                  <div className={`${riskInfo.bg} rounded-xl p-6 border ${riskInfo.border}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500 mb-1">Composite Risk Score</p>
                        <p className={`text-5xl font-display font-bold ${riskInfo.color}`}>
                          {report.riskScore}%
                        </p>
                        <p className={`text-sm ${riskInfo.color} mt-1 font-medium`}>
                          {riskInfo.label} Classification
                        </p>
                      </div>
                      <div className="w-32 h-32 relative">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                          <circle
                            cx="50" cy="50" r="40"
                            fill="none" stroke={riskInfo.track} strokeWidth="12"
                          />
                          <circle
                            cx="50" cy="50" r="40"
                            fill="none" stroke={riskInfo.ring} strokeWidth="12"
                            strokeLinecap="round"
                            strokeDasharray={`${report.riskScore * 2.51} 251`}
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className={`text-2xl font-bold ${riskInfo.color}`}>
                            {report.riskScore}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* C: SHAP Analysis */}
              {report.shapFeatures.length > 0 && (
                <section>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      <span className="text-primary font-bold text-sm">C</span>
                    </div>
                    <h3 className="font-display text-lg font-semibold text-stone-900">
                      Clinical Rationale (SHAP Analysis)
                    </h3>
                  </div>
                  <div className="pl-10 space-y-6">
                    {/* Waterfall */}
                    <div>
                      <p className="text-sm font-medium text-stone-600 mb-3">Feature Impact Waterfall</p>
                      <div className="space-y-2">
                        {report.shapFeatures.map((feature, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <div className="w-44 text-sm text-stone-600 truncate" title={feature.name}>
                              {feature.name}
                            </div>
                            <div className="flex-1 h-6 bg-stone-100 rounded relative overflow-hidden">
                              <div
                                className={`absolute top-0 h-full rounded ${
                                  feature.direction === 'negative' ? 'bg-rose-400' : 'bg-emerald-400'
                                }`}
                                style={{
                                  width: `${(Math.abs(feature.impact) / maxImpact) * 50}%`,
                                  left: feature.direction === 'positive' ? '50%' : undefined,
                                  right: feature.direction === 'negative' ? '50%' : undefined,
                                }}
                              />
                              <div className="absolute left-1/2 top-0 bottom-0 w-px bg-stone-300" />
                            </div>
                            <div className="w-16 text-right">
                              <span
                                className={`text-sm font-semibold ${
                                  feature.direction === 'negative'
                                    ? 'text-rose-600'
                                    : 'text-emerald-600'
                                }`}
                              >
                                {feature.direction === 'negative' ? '' : '+'}
                                {feature.impact}
                              </span>
                            </div>
                            <div className="w-5">
                              {feature.direction === 'negative' ? (
                                <TrendingDown className="w-4 h-4 text-rose-500" />
                              ) : (
                                <TrendingUp className="w-4 h-4 text-emerald-500" />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Heatmap */}
                    {report.featureHeatmap.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-stone-600 mb-3">
                          Feature Risk Heatmap
                        </p>
                        <div className="grid grid-cols-3 gap-2">
                          {report.featureHeatmap.map((entry, i) => {
                            const v = entry.value
                            const bg =
                              v > 0.7
                                ? 'bg-rose-500'
                                : v > 0.5
                                  ? 'bg-orange-400'
                                  : v > 0.3
                                    ? 'bg-amber-300'
                                    : 'bg-emerald-400'
                            return (
                              <div
                                key={i}
                                className={`${bg} rounded-lg p-3 text-center transition-transform hover:scale-105`}
                              >
                                <p className="text-xs font-medium text-white/90">{entry.name}</p>
                                <p className="text-lg font-bold text-white mt-1">
                                  {Math.round(entry.value * 100)}%
                                </p>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* D: Qualitative Factors */}
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-bold text-sm">D</span>
                  </div>
                  <h3 className="font-display text-lg font-semibold text-stone-900">
                    Qualitative Risk Factors
                  </h3>
                </div>
                <div className="pl-10 space-y-4">
                  {report.qualitativeFactors.riskFactors.length > 0 && (
                    <div className="bg-rose-50 rounded-xl p-4 border border-rose-100">
                      <p className="text-sm font-semibold text-rose-700 mb-2">Risk Factors</p>
                      <ul className="space-y-1.5">
                        {report.qualitativeFactors.riskFactors.map((f, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-rose-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {report.qualitativeFactors.protectiveFactors.length > 0 && (
                    <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                      <p className="text-sm font-semibold text-emerald-700 mb-2">Protective Factors</p>
                      <ul className="space-y-1.5">
                        {report.qualitativeFactors.protectiveFactors.map((f, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-emerald-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {report.qualitativeFactors.recommendations.length > 0 && (
                    <div className="bg-sky-50 rounded-xl p-4 border border-sky-100">
                      <p className="text-sm font-semibold text-sky-700 mb-2">
                        Clinical Recommendations
                      </p>
                      <ul className="space-y-1.5">
                        {report.qualitativeFactors.recommendations.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-sky-800">
                            <span className="font-semibold text-sky-500 shrink-0">{i + 1}.</span>
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <details className="group">
                    <summary className="text-xs text-stone-400 cursor-pointer hover:text-stone-600 transition-colors">
                      View raw JSON
                    </summary>
                    <div className="mt-2 bg-stone-50 rounded-xl p-4 font-mono text-sm border border-stone-200">
                      <pre className="text-stone-700 whitespace-pre-wrap text-xs">
{JSON.stringify(report.qualitativeFactors, null, 2)}
                      </pre>
                    </div>
                  </details>
                </div>
              </section>
            </div>
          </motion.div>

          {/* ── Right Panel: Controls ── */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col gap-4"
          >
            {/* Review & Refine */}
            <div className="bg-white rounded-2xl border border-stone-200 p-5 flex-1">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-primary" />
                <h3 className="font-display font-semibold text-stone-900">Physician Review</h3>
              </div>
              <p className="text-sm text-stone-500 mb-3">
                Add clinical notes or corrections to refine the AI-generated summary.
              </p>
              <textarea
                value={doctorNotes}
                onChange={(e) => setDoctorNotes(e.target.value)}
                placeholder="e.g., 'Patient started new medication yesterday...'"
                rows={6}
                className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all resize-none"
              />
              <button
                onClick={handleRebuildReport}
                disabled={!doctorNotes.trim() || isRebuilding}
                className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-stone-100 hover:bg-stone-200 disabled:bg-stone-50 disabled:text-stone-400 text-stone-700 font-medium rounded-xl transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${isRebuilding ? 'animate-spin' : ''}`} />
                {isRebuilding ? 'Rebuilding...' : 'Rebuild Report'}
              </button>
            </div>

            {/* Download */}
            <div className="bg-white rounded-2xl border border-stone-200 p-5">
              <h3 className="font-display font-semibold text-stone-900 mb-3">Preliminary Actions</h3>
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(report, null, 2)], {
                    type: 'application/json',
                  })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `report-${report.jobId}.json`
                  a.click()
                  URL.revokeObjectURL(url)
                }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-stone-200 hover:bg-stone-50 text-stone-700 font-medium rounded-xl transition-colors"
              >
                <Download className="w-4 h-4" />
                Download Report JSON
              </button>
            </div>

            {/* Finalize */}
            <div className="bg-white rounded-2xl border border-stone-200 p-5">
              <h3 className="font-display font-semibold text-stone-900 mb-4">Finalize & Commit</h3>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    exportReportPdf(
                      report,
                      {
                        name: patient.name,
                        age: patient.age,
                        sex: patient.sex,
                        bloodType: patient.bloodType,
                        primaryCondition: patient.primaryCondition,
                      },
                      executiveSummary,
                      doctorNotes || undefined
                    )
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-stone-200 hover:bg-stone-50 text-stone-700 font-medium rounded-xl transition-colors"
                >
                  <FileCheck className="w-4 h-4" />
                  Export Final Report
                </button>
                {reportStatus === 'draft' && (
                  <button
                    onClick={handleFinalize}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-stone-200 hover:bg-stone-50 text-stone-700 font-medium rounded-xl transition-colors"
                  >
                    <FileCheck className="w-4 h-4" />
                    Mark as Finalized
                  </button>
                )}
                <button
                  onClick={handleSaveToRecord}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-xl transition-colors"
                >
                  <Save className="w-5 h-5" />
                  Save to Patient Record
                </button>
              </div>
              <p className="text-xs text-stone-400 text-center mt-3">
                Commits structured data to PostgreSQL Vector DB
              </p>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
