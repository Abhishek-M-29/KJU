import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Send,
  Upload,
  FileText,
  X,
  Activity,
  Droplets,
  Heart,
  Wind,
  Pill,
  AlertCircle,
  TrendingUp,
  Beaker,
  Play,
  Loader2,
} from 'lucide-react'
import { mockPatients, mockChatHistory } from '@/data/patients'
import type { ChatMessage } from '@/types/patient'

const DOCUMENTS_API_URL = 'http://172.18.4.108:8000/api/patients/uploads'
const DIAGNOSTICS_API_URL = 'http://localhost:8000/api/diagnostics/run'

type TabMode = 'insight' | 'diagnostics'

export function PatientHubPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabMode>('insight')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [queryInput, setQueryInput] = useState('')
  const [observations, setObservations] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isFetchingDocs, setIsFetchingDocs] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const patient = mockPatients.find((p) => p.id === id) || mockPatients[0]

  useEffect(() => {
    const history = mockChatHistory[patient.id] || []
    setChatMessages(history)
  }, [patient.id])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleSendQuery = () => {
    if (!queryInput.trim()) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: queryInput,
      timestamp: new Date(),
    }
    setChatMessages((prev) => [...prev, userMessage])
    setQueryInput('')

    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Based on the patient's medical records: ${patient.clinicalSummary.slice(0, 150)}... Would you like me to elaborate on any specific aspect?`,
        timestamp: new Date(),
      }
      setChatMessages((prev) => [...prev, aiMessage])
    }, 1200)
  }

  const fetchAndAggregateOcrTexts = async () => {
    setIsFetchingDocs(true)
    try {
      const response = await fetch(DOCUMENTS_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: 1 }),
      })
      const data = await response.json()
      if (data.success && Array.isArray(data.documents)) {
        const aggregatedText = data.documents
          .filter((doc: any) => doc.ocr_text)
          .map((doc: any) => {
            const header = `===== ${doc.document_type}: ${doc.document_name} =====`
            return `${header}\n${doc.ocr_text}`
          })
          .join('\n\n')
        setObservations(aggregatedText)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    } finally {
      setIsFetchingDocs(false)
    }
  }

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    setUploadedFiles((prev) => [...prev, ...files])
    fetchAndAggregateOcrTexts()
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      setUploadedFiles((prev) => [...prev, ...files])
      fetchAndAggregateOcrTexts()
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleRunDiagnostics = async () => {
    setIsSubmitting(true)
    try {
      const payload = {
        patientId: patient.id,
        doctorId: 'doc-001',
        name: patient.name,
        age: patient.age,
        sex: patient.sex,
        bloodType: patient.bloodType,
        primaryCondition: patient.primaryCondition,
        symptom: patient.symptom,
        vitals: patient.vitals,
        labResults: patient.labResults,
        medications: patient.medications,
        allergies: patient.allergies,
        clinicalSummary: patient.clinicalSummary,
        data: observations,
      }
      const response = await fetch(DIAGNOSTICS_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await response.json()
      if (result.jobId) {
        navigate(`/processing?jobId=${result.jobId}&patientId=${patient.id}`)
      }
    } catch (error) {
      console.error('Failed to start diagnostics:', error)
      alert('Failed to start diagnostic pipeline. Check backend connection.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const initials = patient.name
    .split(' ')
    .map((n) => n[0])
    .join('')

  const statusColors = {
    critical: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', dot: 'bg-rose-500' },
    watch: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' },
    low: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500' },
  }

  const status = statusColors[patient.riskLevel]
  const maxRisk = Math.max(...patient.riskHistory.map((h) => h.score), 100)

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Top Bar */}
      <header className="bg-white border-b border-stone-100 sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 rounded-lg hover:bg-stone-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-stone-600" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white font-semibold text-sm">
                {initials}
              </div>
              <div>
                <h1 className="text-lg font-semibold text-stone-900">{patient.name}</h1>
                <div className="flex items-center gap-2 text-sm text-stone-500">
                  <span>{patient.age}y</span>
                  <span className="w-1 h-1 rounded-full bg-stone-300" />
                  <span>{patient.sex === 'M' ? 'Male' : 'Female'}</span>
                  <span className="w-1 h-1 rounded-full bg-stone-300" />
                  <span>{patient.id}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Toggle Switch */}
          <div className="flex items-center gap-1 p-1 bg-stone-100 rounded-xl">
            <button
              onClick={() => setActiveTab('insight')}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'insight'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Patient Insight
            </button>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'diagnostics'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Run Diagnostics
            </button>
          </div>

          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${status.bg} ${status.border} border`}>
            <div className={`w-2 h-2 rounded-full ${status.dot}`} />
            <span className={`text-sm font-medium ${status.text}`}>
              {patient.riskLevel === 'critical' ? 'Critical' : patient.riskLevel === 'watch' ? 'Monitor' : 'Stable'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto p-6">
        <AnimatePresence mode="wait">
          {activeTab === 'insight' ? (
            <motion.div
              key="insight"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-[340px_1fr] gap-6 h-[calc(100vh-140px)]"
            >
              {/* Left Column - Patient Summary */}
              <div className="space-y-5 overflow-y-auto pr-2 custom-scrollbar">
                {/* Demographics Card */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/80 to-primary-dark flex items-center justify-center text-white font-bold text-xl shrink-0">
                      {initials}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h2 className="font-display text-xl font-semibold text-stone-900 truncate">{patient.name}</h2>
                      <div className="mt-1 space-y-0.5 text-sm text-stone-500">
                        <p>ID: {patient.id}</p>
                        <p>{patient.age} years • {patient.sex === 'M' ? 'Male' : 'Female'} • Blood: {patient.bloodType}</p>
                      </div>
                    </div>
                  </div>
                  <div className={`mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg ${status.bg}`}>
                    <span className={`text-sm font-medium ${status.text}`}>{patient.primaryCondition}</span>
                  </div>
                </div>

                {/* Clinical Summary */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide mb-3">
                    Clinical Summary
                  </h3>
                  <p className="text-sm text-stone-600 leading-relaxed">{patient.clinicalSummary}</p>
                </div>

                {/* Medications */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <div className="flex items-center gap-2 mb-3">
                    <Pill className="w-4 h-4 text-primary" />
                    <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide">
                      Current Medications
                    </h3>
                  </div>
                  {patient.medications.length > 0 ? (
                    <ul className="space-y-2">
                      {patient.medications.map((med, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-stone-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary/40" />
                          {med}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-stone-400">No current medications</p>
                  )}
                </div>

                {/* Allergies */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertCircle className="w-4 h-4 text-rose-500" />
                    <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide">
                      Known Allergies
                    </h3>
                  </div>
                  {patient.allergies.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {patient.allergies.map((allergy, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 bg-rose-50 text-rose-700 rounded-lg text-sm font-medium"
                        >
                          {allergy}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-stone-400">No known allergies</p>
                  )}
                </div>
              </div>

              {/* Right Column - Chat Interface */}
              <div className="bg-white rounded-2xl border border-stone-100 flex flex-col overflow-hidden">
                <div className="px-5 py-4 border-b border-stone-100">
                  <h2 className="font-display text-lg font-semibold text-stone-900">Knowledge Graph Query</h2>
                  <p className="text-sm text-stone-500 mt-0.5">Ask questions about patient history and records</p>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar">
                  {chatMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                      <div className="w-16 h-16 rounded-2xl bg-stone-100 flex items-center justify-center mb-4">
                        <Activity className="w-8 h-8 text-stone-400" />
                      </div>
                      <p className="text-stone-500 text-sm">No queries yet</p>
                      <p className="text-stone-400 text-xs mt-1">Ask about cardiac history, medications, or lab trends</p>
                    </div>
                  ) : (
                    chatMessages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                            msg.role === 'user'
                              ? 'bg-primary text-white rounded-br-md'
                              : 'bg-stone-100 text-stone-800 rounded-bl-md'
                          }`}
                        >
                          <p className="text-sm leading-relaxed">{msg.content}</p>
                          <p
                            className={`text-xs mt-2 ${
                              msg.role === 'user' ? 'text-white/60' : 'text-stone-400'
                            }`}
                          >
                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </motion.div>
                    ))
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-stone-100">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={queryInput}
                      onChange={(e) => setQueryInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
                      placeholder="Query patient history..."
                      className="flex-1 px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all"
                    />
                    <button
                      onClick={handleSendQuery}
                      disabled={!queryInput.trim()}
                      className="px-4 py-3 bg-primary hover:bg-primary-dark disabled:bg-stone-200 disabled:cursor-not-allowed text-white rounded-xl transition-colors"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="diagnostics"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-2 gap-6 h-[calc(100vh-140px)]"
            >
              {/* Left Column - Statistical Data */}
              <div className="space-y-5 overflow-y-auto pr-2 custom-scrollbar">
                {/* Vitals Widget */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide mb-4">
                    Current Vitals
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-rose-50 rounded-xl">
                      <Heart className="w-5 h-5 text-rose-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-rose-700">{patient.vitals.heartRate}</p>
                      <p className="text-xs text-rose-600 mt-1">BPM</p>
                    </div>
                    <div className="text-center p-4 bg-violet-50 rounded-xl">
                      <Activity className="w-5 h-5 text-violet-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-violet-700">{patient.vitals.bloodPressure}</p>
                      <p className="text-xs text-violet-600 mt-1">mmHg</p>
                    </div>
                    <div className="text-center p-4 bg-sky-50 rounded-xl">
                      <Wind className="w-5 h-5 text-sky-500 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-sky-700">{patient.vitals.oxygenSaturation}%</p>
                      <p className="text-xs text-sky-600 mt-1">SpO2</p>
                    </div>
                  </div>
                </div>

                {/* Lab Results Widget */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <div className="flex items-center gap-2 mb-4">
                    <Beaker className="w-4 h-4 text-accent" />
                    <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide">
                      Lab Results
                    </h3>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Droplets className="w-4 h-4 text-amber-500" />
                        <span className="text-sm text-stone-600">Glucose</span>
                      </div>
                      <span className={`text-sm font-semibold ${patient.labResults.glucose > 125 ? 'text-amber-600' : 'text-stone-900'}`}>
                        {patient.labResults.glucose} mg/dL
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Activity className="w-4 h-4 text-rose-500" />
                        <span className="text-sm text-stone-600">Total Cholesterol</span>
                      </div>
                      <span className={`text-sm font-semibold ${patient.labResults.cholesterol > 200 ? 'text-rose-600' : 'text-stone-900'}`}>
                        {patient.labResults.cholesterol} mg/dL
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Droplets className="w-4 h-4 text-teal-500" />
                        <span className="text-sm text-stone-600">Creatinine</span>
                      </div>
                      <span className={`text-sm font-semibold ${patient.labResults.creatinine > 1.4 ? 'text-amber-600' : 'text-stone-900'}`}>
                        {patient.labResults.creatinine} mg/dL
                      </span>
                    </div>
                  </div>
                </div>

                {/* Risk Score Trend */}
                <div className="bg-white rounded-2xl p-5 border border-stone-100">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="w-4 h-4 text-primary" />
                    <h3 className="font-display text-sm font-semibold text-stone-900 uppercase tracking-wide">
                      Risk Score History
                    </h3>
                  </div>
                  {/* Simple SVG Line Chart */}
                  <div className="relative h-40">
                    <svg className="w-full h-full" viewBox="0 0 300 120" preserveAspectRatio="none">
                      <line x1="0" y1="30" x2="300" y2="30" stroke="#e7e5e4" strokeWidth="1" strokeDasharray="4" />
                      <line x1="0" y1="60" x2="300" y2="60" stroke="#e7e5e4" strokeWidth="1" strokeDasharray="4" />
                      <line x1="0" y1="90" x2="300" y2="90" stroke="#e7e5e4" strokeWidth="1" strokeDasharray="4" />
                      
                      <path
                        d={`M 0 ${120 - (patient.riskHistory[0]?.score / maxRisk) * 100} 
                            ${patient.riskHistory.map((h, i) => 
                              `L ${(i / (patient.riskHistory.length - 1)) * 300} ${120 - (h.score / maxRisk) * 100}`
                            ).join(' ')} 
                            L 300 120 L 0 120 Z`}
                        fill="url(#riskGradient)"
                        opacity="0.3"
                      />
                      
                      <path
                        d={`M ${patient.riskHistory.map((h, i) => 
                          `${(i / (patient.riskHistory.length - 1)) * 300} ${120 - (h.score / maxRisk) * 100}`
                        ).join(' L ')}`}
                        fill="none"
                        stroke="#E07A5F"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      
                      {patient.riskHistory.map((h, i) => (
                        <circle
                          key={i}
                          cx={(i / (patient.riskHistory.length - 1)) * 300}
                          cy={120 - (h.score / maxRisk) * 100}
                          r="4"
                          fill="#E07A5F"
                          stroke="white"
                          strokeWidth="2"
                        />
                      ))}
                      
                      <defs>
                        <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#E07A5F" />
                          <stop offset="100%" stopColor="#E07A5F" stopOpacity="0" />
                        </linearGradient>
                      </defs>
                    </svg>
                    
                    <div className="flex justify-between mt-2 text-xs text-stone-400">
                      {patient.riskHistory.map((h, i) => (
                        <span key={i}>{h.date.split('-').slice(1).join('/')}</span>
                      ))}
                    </div>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm">
                    <span className="text-stone-500">Current Score</span>
                    <span className={`font-bold ${
                      patient.riskPercentage >= 70 ? 'text-rose-600' : 
                      patient.riskPercentage >= 40 ? 'text-amber-600' : 'text-emerald-600'
                    }`}>
                      {patient.riskPercentage}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Column - Action Console */}
              <div className="bg-white rounded-2xl border border-stone-100 flex flex-col overflow-hidden">
                <div className="px-5 py-4 border-b border-stone-100">
                  <h2 className="font-display text-lg font-semibold text-stone-900">Diagnostic Console</h2>
                  <p className="text-sm text-stone-500 mt-0.5">Upload data and run the agentic pipeline</p>
                </div>

                <div className="flex-1 p-5 space-y-5 overflow-y-auto custom-scrollbar">
                  {/* File Upload Zone */}
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Upload Lab Reports (PDF/JSON) or Clinical Notes
                    </label>
                    <div
                      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                      onDragLeave={() => setIsDragging(false)}
                      onDrop={handleFileDrop}
                      onClick={() => fileInputRef.current?.click()}
                      className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                        isDragging
                          ? 'border-primary bg-primary/5'
                          : 'border-stone-200 hover:border-stone-300 hover:bg-stone-50'
                      }`}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept=".pdf,.json,.txt"
                        onChange={handleFileSelect}
                        className="hidden"
                      />
                      <Upload className={`w-8 h-8 mx-auto mb-3 ${isDragging ? 'text-primary' : 'text-stone-400'}`} />
                      <p className="text-sm text-stone-600">
                        Drop files here or <span className="text-primary font-medium">browse</span>
                      </p>
                      <p className="text-xs text-stone-400 mt-1">PDF, JSON, or TXT files</p>
                    </div>

                    {uploadedFiles.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {uploadedFiles.map((file, i) => (
                          <div
                            key={i}
                            className="flex items-center justify-between px-3 py-2 bg-stone-50 rounded-lg"
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <FileText className="w-4 h-4 text-stone-500 shrink-0" />
                              <span className="text-sm text-stone-700 truncate">{file.name}</span>
                            </div>
                            <button
                              onClick={() => removeFile(i)}
                              className="p-1 hover:bg-stone-200 rounded transition-colors"
                            >
                              <X className="w-4 h-4 text-stone-500" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Doctor Observations */}
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Add Symptoms / Clinical Observations
                      {isFetchingDocs && (
                        <span className="ml-2 inline-flex items-center gap-1 text-xs text-primary font-normal">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Fetching documents...
                        </span>
                      )}
                    </label>
                    <textarea
                      value={observations}
                      onChange={(e) => setObservations(e.target.value)}
                      placeholder="Enter clinical observations, symptoms, or notes for MedGamma analysis..."
                      rows={12}
                      className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all resize-none font-mono"
                    />
                  </div>
                </div>

                {/* Run Button */}
                <div className="p-5 border-t border-stone-100">
                  <button
                    onClick={handleRunDiagnostics}
                    disabled={isSubmitting}
                    className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-primary to-primary-dark hover:from-primary-dark hover:to-primary disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Play className="w-5 h-5" />
                    )}
                    {isSubmitting ? 'Starting Pipeline...' : 'Run Diagnostic Swarm'}
                  </button>
                  <p className="text-xs text-stone-400 text-center mt-2">
                    Initiates the ML Swarm & MedGamma pipeline
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
