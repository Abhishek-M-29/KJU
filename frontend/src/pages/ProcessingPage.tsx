import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
  Minus,
} from 'lucide-react'
import { mockPatients } from '@/data/patients'

// Mock data for the synthesis report
const mockReportData = {
  patientId: 'pat-003',
  generatedAt: new Date(),
  status: 'draft' as 'draft' | 'finalized',
  executiveSummary: `Based on comprehensive analysis of clinical data, laboratory results, and historical trends, the patient presents with elevated cardiovascular risk requiring immediate clinical attention. The integrated ML swarm analysis identified persistent atrial fibrillation with suboptimal rate control as the primary driver, compounded by progressive heart failure symptoms evidenced by reduced ejection fraction (35%) and new-onset dyspnea. Anticoagulation therapy appears adequate with therapeutic INR levels. However, the confluence of uncontrolled hypertension, elevated fasting glucose, and declining renal function creates a synergistic risk profile warranting aggressive intervention and close monitoring.`,
  riskScore: 85,
  shapFeatures: [
    { name: 'Ejection Fraction (35%)', impact: -22, direction: 'negative' as const },
    { name: 'Atrial Fibrillation', impact: -18, direction: 'negative' as const },
    { name: 'Blood Pressure (165/105)', impact: -15, direction: 'negative' as const },
    { name: 'Fasting Glucose (142)', impact: -8, direction: 'negative' as const },
    { name: 'Age (71)', impact: -6, direction: 'negative' as const },
    { name: 'Therapeutic INR', impact: +5, direction: 'positive' as const },
    { name: 'No Prior MI', impact: +4, direction: 'positive' as const },
  ],
  featureHeatmap: [
    { name: 'Cardiac Function', value: 0.92 },
    { name: 'Blood Pressure', value: 0.78 },
    { name: 'Metabolic', value: 0.65 },
    { name: 'Renal Function', value: 0.58 },
    { name: 'Coagulation', value: 0.25 },
    { name: 'Lifestyle', value: 0.45 },
  ],
  qualitativeFactors: {
    riskFactors: ['Persistent AF', 'Heart Failure', 'Hypertension Stage 2', 'Pre-diabetic'],
    protectiveFactors: ['Anticoagulated', 'No smoking history', 'Compliant with medications'],
    recommendations: ['Urgent cardiology referral', 'Consider cardioversion', 'Optimize rate control'],
  },
}

export function ProcessingPage() {
  const navigate = useNavigate()
  const [reportStatus, setReportStatus] = useState<'draft' | 'finalized'>('draft')
  const [doctorNotes, setDoctorNotes] = useState('')
  const [isRebuilding, setIsRebuilding] = useState(false)
  const [executiveSummary, setExecutiveSummary] = useState(mockReportData.executiveSummary)

  const patient = mockPatients.find((p) => p.id === mockReportData.patientId) || mockPatients[0]

  const handleRebuildReport = async () => {
    if (!doctorNotes.trim()) return
    setIsRebuilding(true)
    // Simulate AI regeneration
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setExecutiveSummary(
      `${executiveSummary}\n\n[Updated based on physician input: ${doctorNotes}]\n\nThe clinical context has been revised to incorporate the attending physician's observations. `
    )
    setDoctorNotes('')
    setIsRebuilding(false)
  }

  const handleFinalize = () => {
    setReportStatus('finalized')
  }

  const handleSaveToRecord = () => {
    alert('Report saved to patient record (PostgreSQL Vector DB)')
    navigate('/dashboard')
  }

  // Calculate max impact for scaling
  const maxImpact = Math.max(...mockReportData.shapFeatures.map((f) => Math.abs(f.impact)))

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
              <p className="text-xs text-stone-500">{patient.name} • {patient.id}</p>
            </div>
          </div>
          <div
            className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
              reportStatus === 'draft'
                ? 'bg-amber-100 text-amber-700 border border-amber-200'
                : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
            }`}
          >
            {reportStatus === 'draft' ? 'Draft • AI-Generated' : 'Finalized'}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1800px] mx-auto p-6">
        <div className="grid grid-cols-[1fr_380px] gap-6 min-h-[calc(100vh-120px)]">
          {/* Left Panel - Report Preview */}
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
                    Preliminary Assessment
                  </p>
                  <h2 className="text-2xl font-display font-bold text-stone-900">
                    Health Risk Assessment Report
                  </h2>
                </div>
                <div className="text-right text-sm text-stone-500">
                  <p>Generated: {mockReportData.generatedAt.toLocaleDateString()}</p>
                  <p>Ref: Dr. Sarah Chen</p>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-6 text-sm">
                <div>
                  <span className="text-stone-400">Patient:</span>{' '}
                  <span className="font-medium text-stone-700">{patient.name}</span>
                </div>
                <div>
                  <span className="text-stone-400">ID:</span>{' '}
                  <span className="font-medium text-stone-700">{patient.id}</span>
                </div>
                <div>
                  <span className="text-stone-400">DOB:</span>{' '}
                  <span className="font-medium text-stone-700">{patient.age} years</span>
                </div>
              </div>
            </div>

            {/* Report Body */}
            <div className="p-8 space-y-8 overflow-y-auto max-h-[calc(100vh-280px)] custom-scrollbar">
              {/* Section A: Executive Summary */}
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

              {/* Section B: Risk Probability */}
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
                  <div className="bg-gradient-to-br from-rose-50 to-orange-50 rounded-xl p-6 border border-rose-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-stone-500 mb-1">Composite Risk Score</p>
                        <p className="text-5xl font-display font-bold text-rose-600">
                          {mockReportData.riskScore}%
                        </p>
                        <p className="text-sm text-rose-600 mt-1 font-medium">High Risk Classification</p>
                      </div>
                      <div className="w-32 h-32 relative">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke="#fecaca"
                            strokeWidth="12"
                          />
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke="#e11d48"
                            strokeWidth="12"
                            strokeLinecap="round"
                            strokeDasharray={`${mockReportData.riskScore * 2.51} 251`}
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-2xl font-bold text-rose-700">{mockReportData.riskScore}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Section C: SHAP Analysis */}
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
                  {/* SHAP Waterfall */}
                  <div>
                    <p className="text-sm font-medium text-stone-600 mb-3">Feature Impact Waterfall</p>
                    <div className="space-y-2">
                      {mockReportData.shapFeatures.map((feature, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <div className="w-40 text-sm text-stone-600 truncate">{feature.name}</div>
                          <div className="flex-1 h-6 bg-stone-100 rounded relative overflow-hidden">
                            <div
                              className={`absolute top-0 h-full rounded ${
                                feature.direction === 'negative' ? 'bg-rose-400' : 'bg-emerald-400'
                              }`}
                              style={{
                                width: `${(Math.abs(feature.impact) / maxImpact) * 100}%`,
                                left: feature.direction === 'positive' ? '50%' : undefined,
                                right: feature.direction === 'negative' ? '50%' : undefined,
                              }}
                            />
                            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-stone-300" />
                          </div>
                          <div className="w-12 text-right">
                            <span
                              className={`text-sm font-semibold ${
                                feature.direction === 'negative' ? 'text-rose-600' : 'text-emerald-600'
                              }`}
                            >
                              {feature.direction === 'negative' ? '' : '+'}
                              {feature.impact}%
                            </span>
                          </div>
                          <div className="w-5">
                            {feature.direction === 'negative' ? (
                              <TrendingDown className="w-4 h-4 text-rose-500" />
                            ) : feature.direction === 'positive' ? (
                              <TrendingUp className="w-4 h-4 text-emerald-500" />
                            ) : (
                              <Minus className="w-4 h-4 text-stone-400" />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Feature Heatmap */}
                  <div>
                    <p className="text-sm font-medium text-stone-600 mb-3">Feature Risk Heatmap</p>
                    <div className="grid grid-cols-3 gap-2">
                      {mockReportData.featureHeatmap.map((feature, i) => {
                        const intensity = feature.value
                        const bgColor =
                          intensity > 0.7
                            ? 'bg-rose-500'
                            : intensity > 0.5
                              ? 'bg-orange-400'
                              : intensity > 0.3
                                ? 'bg-amber-300'
                                : 'bg-emerald-400'
                        return (
                          <div
                            key={i}
                            className={`${bgColor} rounded-lg p-3 text-center transition-transform hover:scale-105`}
                          >
                            <p className="text-xs font-medium text-white/90">{feature.name}</p>
                            <p className="text-lg font-bold text-white mt-1">
                              {Math.round(feature.value * 100)}%
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              </section>

              {/* Section D: Textual Insights */}
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-bold text-sm">D</span>
                  </div>
                  <h3 className="font-display text-lg font-semibold text-stone-900">
                    Qualitative Risk Factors (MedGamma)
                  </h3>
                </div>
                <div className="pl-10">
                  <div className="bg-stone-50 rounded-xl p-4 font-mono text-sm border border-stone-200">
                    <pre className="text-stone-700 whitespace-pre-wrap">
{JSON.stringify(mockReportData.qualitativeFactors, null, 2)}
                    </pre>
                  </div>
                </div>
              </section>
            </div>
          </motion.div>

          {/* Right Panel - Control Console */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col gap-4"
          >
            {/* Module A: Review & Refine */}
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
                placeholder="e.g., 'Patient started new medication yesterday, which may affect BP readings...'"
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

            {/* Module B: Preliminary Actions */}
            <div className="bg-white rounded-2xl border border-stone-200 p-5">
              <h3 className="font-display font-semibold text-stone-900 mb-3">Preliminary Actions</h3>
              <button
                onClick={() => alert('Downloading preliminary draft...')}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-stone-200 hover:bg-stone-50 text-stone-700 font-medium rounded-xl transition-colors"
              >
                <Download className="w-4 h-4" />
                Download Preliminary Draft
              </button>
            </div>

            {/* Module C: Finalize & Commit */}
            <div className="bg-white rounded-2xl border border-stone-200 p-5">
              <h3 className="font-display font-semibold text-stone-900 mb-4">Finalize & Commit</h3>
              <div className="space-y-3">
                <button
                  onClick={() => alert('Exporting final PDF...')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-stone-200 hover:bg-stone-50 text-stone-700 font-medium rounded-xl transition-colors"
                >
                  <FileCheck className="w-4 h-4" />
                  Export Final PDF
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
