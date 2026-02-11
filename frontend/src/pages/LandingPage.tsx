import { useRef } from 'react'
import { motion, useInView, useScroll, useTransform } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Shield,
  Zap,
  Eye,
  Activity,
  Brain,
  FileText,
  ChevronDown,
  Sparkles,
  TrendingUp,
  Heart,
  Droplets,
  Thermometer,
  Building2,
  FlaskConical,
  ShieldCheck,
  Target,
  Clock,
  Lock,
  Layers,
  CreditCard,
  Wrench,
  Check,
} from 'lucide-react'

/* ─── Animated ECG Line ─────────────────────────── */
function ECGLine({ className = '', delay = 0 }: { className?: string; delay?: number }) {
  const path =
    'M0,50 L30,50 L35,50 L38,20 L42,80 L46,35 L50,65 L54,45 L58,50 L90,50 L95,50 L98,15 L102,85 L106,30 L110,70 L114,45 L118,50 L150,50 L180,50 L183,50 L186,22 L190,78 L194,38 L198,62 L202,48 L206,50 L240,50'
  return (
    <svg viewBox="0 0 240 100" className={className} preserveAspectRatio="none">
      <motion.path
        d={path}
        fill="none"
        stroke="url(#ecgGrad)"
        strokeWidth="2"
        strokeLinecap="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 0.7 }}
        transition={{ duration: 3, delay, ease: 'easeInOut' }}
      />
      <defs>
        <linearGradient id="ecgGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#E07A5F" stopOpacity="0" />
          <stop offset="30%" stopColor="#E07A5F" stopOpacity="1" />
          <stop offset="70%" stopColor="#3D8B8B" stopOpacity="1" />
          <stop offset="100%" stopColor="#3D8B8B" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  )
}

/* ─── Architecture Pipeline SVG ─────────────────── */
function PipelineVisualization() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  const nodeVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: (i: number) => ({
      scale: 1,
      opacity: 1,
      transition: { delay: i * 0.15, type: 'spring' as const, stiffness: 200, damping: 15 },
    }),
  }

  const lineVariants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: (i: number) => ({
      pathLength: 1,
      opacity: 1,
      transition: { delay: i * 0.15 + 0.1, duration: 0.6, ease: 'easeInOut' as const },
    }),
  }

  return (
    <div ref={ref} className="w-full overflow-hidden">
      <svg viewBox="0 0 1000 420" className="w-full h-auto" style={{ maxHeight: '420px' }}>
        <defs>
          <linearGradient id="pipeGradA" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#E07A5F" />
            <stop offset="100%" stopColor="#F4A896" />
          </linearGradient>
          <linearGradient id="pipeGradB" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3D8B8B" />
            <stop offset="100%" stopColor="#81B0AA" />
          </linearGradient>
          <linearGradient id="pipeGradC" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#E07A5F" />
            <stop offset="100%" stopColor="#3D8B8B" />
          </linearGradient>
          <filter id="pipeGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="softGlow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ── Connection lines (symmetric layout) ── */}
        {/* Patient → Orchestrator */}
        <motion.path d="M120,210 L210,210" fill="none" stroke="url(#pipeGradC)" strokeWidth="2" variants={lineVariants} custom={0} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* Orchestrator → Separator */}
        <motion.path d="M320,210 L410,210" fill="none" stroke="url(#pipeGradC)" strokeWidth="2" variants={lineVariants} custom={1} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* Separator → Swarm (branch up — symmetric S-curve) */}
        <motion.path d="M520,210 C565,210 565,115 610,115" fill="none" stroke="url(#pipeGradA)" strokeWidth="2" variants={lineVariants} custom={2} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* Separator → MedGemma (branch down — mirror S-curve) */}
        <motion.path d="M520,210 C565,210 565,305 610,305" fill="none" stroke="url(#pipeGradB)" strokeWidth="2" variants={lineVariants} custom={2} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* Swarm → SHAP */}
        <motion.path d="M720,115 L770,115" fill="none" stroke="url(#pipeGradA)" strokeWidth="2" variants={lineVariants} custom={3} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* SHAP → Synthesis (curve down to center) */}
        <motion.path d="M880,115 C905,115 905,210 930,210" fill="none" stroke="url(#pipeGradA)" strokeWidth="2" variants={lineVariants} custom={4} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />
        {/* MedGemma → Synthesis (curve up to center — mirror of SHAP→Synthesis) */}
        <motion.path d="M720,305 L880,305 C905,305 905,210 930,210" fill="none" stroke="url(#pipeGradB)" strokeWidth="2" variants={lineVariants} custom={4} initial="hidden" animate={isInView ? 'visible' : 'hidden'} filter="url(#pipeGlow)" />

        {/* ── Animated data particles ── */}
        {isInView && (
          <>
            <circle r="4" fill="#E07A5F" filter="url(#softGlow)">
              <animateMotion dur="4s" repeatCount="indefinite" begin="0s" path="M120,210 L210,210 L320,210 L410,210 L520,210 C565,210 565,115 610,115 L720,115 L770,115 L880,115 C905,115 905,210 930,210" />
            </circle>
            <circle r="4" fill="#3D8B8B" filter="url(#softGlow)">
              <animateMotion dur="4s" repeatCount="indefinite" begin="1s" path="M120,210 L210,210 L320,210 L410,210 L520,210 C565,210 565,305 610,305 L720,305 L880,305 C905,305 905,210 930,210" />
            </circle>
            <circle r="3" fill="#F4A896" filter="url(#softGlow)" opacity="0.7">
              <animateMotion dur="5s" repeatCount="indefinite" begin="2s" path="M120,210 L210,210 L320,210 L410,210 L520,210 C565,210 565,115 610,115 L720,115 L770,115 L880,115 C905,115 905,210 930,210" />
            </circle>
          </>
        )}

        {/* ── Nodes ── */}
        {/* Patient Data */}
        <motion.g variants={nodeVariants} custom={0} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="30" y="180" width="90" height="60" rx="12" fill="#1C1917" stroke="#E07A5F" strokeWidth="1.5" />
          <text x="75" y="206" textAnchor="middle" fill="#F4A896" fontSize="10" fontWeight="600">Patient</text>
          <text x="75" y="222" textAnchor="middle" fill="#A8A29E" fontSize="9">Data / EHR</text>
        </motion.g>

        {/* Orchestrator */}
        <motion.g variants={nodeVariants} custom={1} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="210" y="180" width="110" height="60" rx="12" fill="#1C1917" stroke="url(#pipeGradC)" strokeWidth="1.5" />
          <text x="265" y="206" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="600">Orchestrator</text>
          <text x="265" y="222" textAnchor="middle" fill="#A8A29E" fontSize="9">Agent Router</text>
        </motion.g>

        {/* Separator */}
        <motion.g variants={nodeVariants} custom={2} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="410" y="180" width="110" height="60" rx="12" fill="#1C1917" stroke="url(#pipeGradC)" strokeWidth="1.5" />
          <text x="465" y="206" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="600">Separator</text>
          <text x="465" y="222" textAnchor="middle" fill="#A8A29E" fontSize="9">Text / Numeric</text>
        </motion.g>

        {/* ML Swarm */}
        <motion.g variants={nodeVariants} custom={3} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="610" y="85" width="110" height="60" rx="12" fill="#292524" stroke="#E07A5F" strokeWidth="1.5" />
          <text x="665" y="111" textAnchor="middle" fill="#E07A5F" fontSize="10" fontWeight="600">ML Swarm</text>
          <text x="665" y="127" textAnchor="middle" fill="#A8A29E" fontSize="9">XGB / RF / LR</text>
        </motion.g>

        {/* SHAP */}
        <motion.g variants={nodeVariants} custom={4} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="770" y="85" width="110" height="60" rx="12" fill="#292524" stroke="#F4A896" strokeWidth="1.5" />
          <text x="825" y="111" textAnchor="middle" fill="#F4A896" fontSize="10" fontWeight="600">SHAP</text>
          <text x="825" y="127" textAnchor="middle" fill="#A8A29E" fontSize="9">Explainability</text>
        </motion.g>

        {/* MedGemma */}
        <motion.g variants={nodeVariants} custom={3} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="610" y="275" width="110" height="60" rx="12" fill="#292524" stroke="#3D8B8B" strokeWidth="1.5" />
          <text x="665" y="301" textAnchor="middle" fill="#3D8B8B" fontSize="10" fontWeight="600">MedGemma</text>
          <text x="665" y="317" textAnchor="middle" fill="#A8A29E" fontSize="9">Text Analysis</text>
        </motion.g>

        {/* Synthesis */}
        <motion.g variants={nodeVariants} custom={5} initial="hidden" animate={isInView ? 'visible' : 'hidden'}>
          <rect x="930" y="180" width="60" height="60" rx="12" fill="#1C1917" stroke="url(#pipeGradC)" strokeWidth="2" />
          <text x="960" y="206" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="600">Synthesis</text>
          <text x="960" y="222" textAnchor="middle" fill="#A8A29E" fontSize="9">Report</text>
        </motion.g>

        {/* ── Branch labels ── */}
        <motion.text x="555" y="95" fill="#E07A5F" fontSize="9" fontWeight="600" opacity="0.7" initial={{ opacity: 0 }} animate={isInView ? { opacity: 0.7 } : {}} transition={{ delay: 0.6 }}>
          Branch A: Numeric
        </motion.text>
        <motion.text x="555" y="355" fill="#3D8B8B" fontSize="9" fontWeight="600" opacity="0.7" initial={{ opacity: 0 }} animate={isInView ? { opacity: 0.7 } : {}} transition={{ delay: 0.6 }}>
          Branch B: Text
        </motion.text>
      </svg>
    </div>
  )
}

/* ─── SHAP Waterfall Chart ──────────────────────── */
const shapFeatures = [
  { name: 'Fasting Glucose', value: 0.32, direction: 'risk' as const },
  { name: 'BMI', value: 0.24, direction: 'risk' as const },
  { name: 'Age', value: 0.18, direction: 'risk' as const },
  { name: 'Blood Pressure', value: 0.14, direction: 'risk' as const },
  { name: 'HDL Cholesterol', value: -0.12, direction: 'protective' as const },
  { name: 'Exercise Freq.', value: -0.16, direction: 'protective' as const },
  { name: 'Sleep Quality', value: -0.08, direction: 'protective' as const },
]

function SHAPChart() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const maxVal = Math.max(...shapFeatures.map((f) => Math.abs(f.value)))

  return (
    <div ref={ref} className="space-y-3">
      {shapFeatures.map((feat, i) => {
        const width = (Math.abs(feat.value) / maxVal) * 100
        const isRisk = feat.direction === 'risk'
        return (
          <motion.div
            key={feat.name}
            className="flex items-center gap-4"
            initial={{ opacity: 0, x: isRisk ? -30 : 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: i * 0.08, duration: 0.5 }}
          >
            <span className="text-sm text-stone-400 w-36 text-right shrink-0 font-medium">{feat.name}</span>
            <div className="flex-1 flex items-center">
              {!isRisk && <div className="flex-1" />}
              <motion.div
                className="h-8 rounded-lg relative overflow-hidden"
                style={{
                  background: isRisk
                    ? 'linear-gradient(90deg, #E07A5F, #C96A52)'
                    : 'linear-gradient(270deg, #3D8B8B, #81B0AA)',
                }}
                initial={{ width: 0 }}
                animate={isInView ? { width: `${width}%` } : {}}
                transition={{ delay: i * 0.08 + 0.2, duration: 0.8, ease: 'easeOut' }}
              >
                <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-white/10" />
                <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-white/90">
                  {isRisk ? '+' : ''}{(feat.value * 100).toFixed(0)}%
                </span>
              </motion.div>
              {isRisk && <div className="flex-1" />}
            </div>
          </motion.div>
        )
      })}
      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-stone-700/50">
        <span className="text-sm text-stone-400 w-36 text-right shrink-0" />
        <div className="flex gap-6 text-xs">
          <span className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm bg-[#E07A5F]" /> Increases Risk
          </span>
          <span className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm bg-[#3D8B8B]" /> Decreases Risk
          </span>
        </div>
      </div>
    </div>
  )
}

/* ─── Animated Counter ──────────────────────────── */
function AnimatedCounter({ value, suffix = '', prefix = '' }: { value: number; suffix?: string; prefix?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <span ref={ref}>
      {isInView ? (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {prefix}{value}{suffix}
        </motion.span>
      ) : (
        <span className="opacity-0">{prefix}{value}{suffix}</span>
      )}
    </span>
  )
}

/* ─── Mini Vital Sparkline ──────────────────────── */
function Sparkline({ data, color, label }: { data: number[]; color: string; label: string }) {
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const h = 40
  const w = 120
  const points = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(' ')

  return (
    <div className="flex items-center gap-3">
      <svg width={w} height={h} className="overflow-visible">
        <motion.polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeInOut' }}
        />
        {/* Glow line */}
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.15"
        />
      </svg>
      <span className="text-xs text-stone-500 font-medium">{label}</span>
    </div>
  )
}

/* ─── Floating Vital Card ───────────────────────── */
function FloatingVitalCard({
  icon: Icon,
  label,
  value,
  unit,
  color,
  delay,
  x,
  y,
}: {
  icon: React.ElementType
  label: string
  value: string
  unit: string
  color: string
  delay: number
  x: number
  y: number
}) {
  return (
    <motion.div
      className="absolute glass-card px-4 py-3 flex items-center gap-3 pointer-events-none"
      style={{ left: `${x}%`, top: `${y}%`, borderColor: color, borderWidth: 1, willChange: 'transform, opacity' }}
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{
        opacity: 1,
        scale: 1,
        y: 0,
      }}
      transition={{
        delay,
        duration: 0.8,
        ease: 'easeOut',
      }}
    >
      <Icon size={16} style={{ color }} />
      <div>
        <div className="text-xs text-stone-500">{label}</div>
        <div className="text-sm font-semibold text-stone-800">
          {value} <span className="text-xs font-normal text-stone-400">{unit}</span>
        </div>
      </div>
    </motion.div>
  )
}

/* ─── Risk Gauge ────────────────────────────────── */
function RiskGauge({ percentage, label, color }: { percentage: number; label: string; color: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const radius = 45
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  return (
    <div ref={ref} className="relative flex flex-col items-center gap-2">
      <svg width="110" height="110" className="-rotate-90">
        <circle cx="55" cy="55" r={radius} fill="none" stroke="#292524" strokeWidth="8" />
        <motion.circle
          cx="55"
          cy="55"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={isInView ? { strokeDashoffset: offset } : {}}
          transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.span
          className="text-2xl font-bold"
          style={{ color }}
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ delay: 0.8 }}
        >
          {percentage}%
        </motion.span>
      </div>
      <span className="text-sm text-stone-400 font-medium mt-1">{label}</span>
    </div>
  )
}

/* ─── Animated Token Comparison Bar Chart ───────── */
function TokenChart() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const data = [
    { label: 'Pure LLM', tokens: 95, color: '#78716C' },
    { label: 'Aegis Hybrid', tokens: 18, color: '#E07A5F' },
  ]

  return (
    <div ref={ref} className="space-y-4">
      {data.map((d, i) => (
        <div key={d.label} className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-stone-400 font-medium">{d.label}</span>
            <span className="font-semibold" style={{ color: d.color }}>{d.tokens}K tokens</span>
          </div>
          <div className="h-4 bg-stone-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: d.color }}
              initial={{ width: 0 }}
              animate={isInView ? { width: `${d.tokens}%` } : {}}
              transition={{ delay: i * 0.2 + 0.3, duration: 1, ease: 'easeOut' }}
            />
          </div>
        </div>
      ))}
      <p className="text-xs text-stone-500 mt-2">Token usage per diagnostic analysis (avg.)</p>
    </div>
  )
}

/* ─── Noise Texture Overlay ─────────────────────── */
function NoiseOverlay() {
  return (
    <div
      className="fixed inset-0 pointer-events-none z-50 opacity-[0.025]"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'repeat',
        backgroundSize: '256px 256px',
      }}
    />
  )
}

/* ─── Section Wrapper ───────────────────────────── */
function Section({
  children,
  className = '',
  dark = false,
  id,
}: {
  children: React.ReactNode
  className?: string
  dark?: boolean
  id?: string
}) {
  return (
    <section
      id={id}
      className={`relative ${dark ? 'bg-stone-900 text-white' : 'bg-stone-50 text-stone-900'} ${className}`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">{children}</div>
    </section>
  )
}

/* ───────────────────────────────────────────────── */
/* ─── MAIN LANDING PAGE ─────────────────────────── */
/* ───────────────────────────────────────────────── */
export function LandingPage() {
  const navigate = useNavigate()
  const heroRef = useRef(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0])
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 100])

  const stagger = {
    visible: { transition: { staggerChildren: 0.1 } },
  }
  const fadeUp = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' as const } },
  }

  return (
    <div className="relative overflow-x-hidden">
      <NoiseOverlay />

      {/* ═══ NAV ═══ */}
      <motion.nav
        className="fixed top-0 inset-x-0 z-40 backdrop-blur-xl bg-stone-900/80 border-b border-stone-800/50"
        initial={{ y: -80 }}
        animate={{ y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#E07A5F] to-[#C96A52] flex items-center justify-center">
              <Shield size={16} className="text-white" />
            </div>
            <span className="text-white font-semibold tracking-tight">Project Aegis</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-stone-400">
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#explainability" className="hover:text-white transition-colors">Explainability</a>
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#business" className="hover:text-white transition-colors">Business</a>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="px-5 py-2 rounded-lg bg-[#E07A5F] text-white text-sm font-semibold hover:bg-[#C96A52] transition-colors"
          >
            Sign In
          </button>
        </div>
      </motion.nav>

      {/* ═══ HERO ═══ */}
      <section ref={heroRef} className="relative min-h-screen bg-stone-900 overflow-hidden flex items-center pt-16">
        {/* Background effects */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-[#E07A5F]/8 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-[#3D8B8B]/6 rounded-full blur-[120px]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-stone-800/30 rounded-full" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-stone-800/20 rounded-full" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] border border-stone-800/10 rounded-full" />
        </div>

        {/* ECG Lines */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <ECGLine className="absolute top-[20%] left-0 w-full h-12 opacity-20" delay={0} />
          <ECGLine className="absolute top-[50%] left-0 w-full h-12 opacity-10" delay={1.5} />
          <ECGLine className="absolute top-[80%] left-0 w-full h-12 opacity-15" delay={0.8} />
        </div>

        <motion.div style={{ opacity: heroOpacity, y: heroY }} className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 w-full">
          <motion.div
            className="max-w-4xl"
            variants={stagger}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={fadeUp} className="flex items-center gap-2 mb-6">
              <span className="px-3 py-1 rounded-full bg-[#E07A5F]/10 border border-[#E07A5F]/20 text-[#F4A896] text-xs font-medium flex items-center gap-1.5">
                <Sparkles size={12} />
                Hybrid Agentic Architecture
              </span>
            </motion.div>

            <motion.h1
              variants={fadeUp}
              className="text-5xl sm:text-6xl lg:text-8xl font-display font-semibold text-white leading-[0.95] tracking-tight mb-6"
            >
              Predict.{' '}
              <span className="bg-gradient-to-r from-[#E07A5F] to-[#F4A896] bg-clip-text text-transparent">
                Explain.
              </span>{' '}
              <br />
              Protect.
            </motion.h1>

            <motion.p variants={fadeUp} className="text-lg sm:text-xl text-stone-400 max-w-2xl leading-relaxed mb-10">
              An AI system that predicts early health risks by analyzing patient data through specialized ML models —
              not LLM wrappers. Every prediction is{' '}
              <span className="text-[#E07A5F] font-medium">explainable</span>,{' '}
              <span className="text-[#3D8B8B] font-medium">cost-efficient</span>, and{' '}
              <span className="text-white font-medium">clinically accurate</span>.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-wrap gap-4">
              <button
                onClick={() => navigate('/login')}
                className="group px-8 py-4 rounded-xl bg-gradient-to-r from-[#E07A5F] to-[#C96A52] text-white font-semibold text-base
                  hover:shadow-lg hover:shadow-[#E07A5F]/25 transition-all duration-300 flex items-center gap-2"
              >
                Get Started
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <a
                href="#architecture"
                className="px-8 py-4 rounded-xl border border-stone-700 text-stone-300 font-medium text-base
                  hover:border-stone-500 hover:text-white transition-all duration-300"
              >
                See How It Works
              </a>
            </motion.div>
          </motion.div>

          {/* Floating vital cards */}
          <div className="hidden lg:block">
            <FloatingVitalCard icon={Heart} label="Heart Rate" value="72" unit="bpm" color="#E07A5F" delay={1} x={65} y={10} />
            <FloatingVitalCard icon={Droplets} label="SpO2" value="98" unit="%" color="#3D8B8B" delay={1.5} x={75} y={45} />
            <FloatingVitalCard icon={Thermometer} label="Temperature" value="36.8" unit="°C" color="#81B0AA" delay={2} x={60} y={75} />
            <FloatingVitalCard icon={Activity} label="BP Systolic" value="128" unit="mmHg" color="#F4A896" delay={2.5} x={80} y={80} />
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-stone-500"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <span className="text-xs tracking-widest uppercase">Scroll</span>
          <ChevronDown size={16} />
        </motion.div>
      </section>

      {/* ═══ PROBLEM STATEMENT ═══ */}
      <Section dark className="py-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            <span className="text-xs uppercase tracking-[0.2em] text-[#E07A5F] font-semibold mb-4 block">The Problem</span>
            <h2 className="text-3xl sm:text-4xl font-display font-semibold text-white mb-6 leading-tight">
              LLMs alone are not enough for clinical diagnostics
            </h2>
            <div className="space-y-5 text-stone-400">
              <div className="flex gap-4">
                <div className="w-1 bg-[#E07A5F]/30 rounded-full shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">The Wrapper Fallacy</p>
                  <p className="text-sm">Feeding raw numerical health data into an LLM results in hallucinations regarding mathematical thresholds.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-1 bg-[#E07A5F]/30 rounded-full shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">The Black Box</p>
                  <p className="text-sm">Medical professionals cannot trust a diagnosis if the reasoning path is hidden within neural network weights.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-1 bg-[#E07A5F]/30 rounded-full shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">Cost & Latency</p>
                  <p className="text-sm">Processing high-volume tabular data via LLM tokens is prohibitively expensive and slow at scale.</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Visual comparison */}
          <motion.div
            className="relative"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <div className="space-y-6">
              {/* Old approach */}
              <div className="p-6 rounded-2xl bg-stone-800/50 border border-stone-700/50">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 rounded-full bg-red-400/80" />
                  <span className="text-sm font-medium text-stone-300">Traditional LLM Wrapper</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-red-400">~95K</div>
                    <div className="text-xs text-stone-500 mt-1">tokens/query</div>
                  </div>
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-red-400">$2.40</div>
                    <div className="text-xs text-stone-500 mt-1">per analysis</div>
                  </div>
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-stone-500">???</div>
                    <div className="text-xs text-stone-500 mt-1">explainability</div>
                  </div>
                </div>
              </div>

              {/* New approach */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-stone-800/80 to-stone-800/40 border border-[#E07A5F]/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 rounded-full bg-[#E07A5F]" />
                  <span className="text-sm font-medium text-white">Aegis Hybrid Architecture</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-[#E07A5F]">~18K</div>
                    <div className="text-xs text-stone-500 mt-1">tokens/query</div>
                  </div>
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-[#3D8B8B]">$0.12</div>
                    <div className="text-xs text-stone-500 mt-1">per analysis</div>
                  </div>
                  <div className="p-3 rounded-lg bg-stone-900/60">
                    <div className="text-2xl font-bold text-[#6EBB8D]">SHAP</div>
                    <div className="text-xs text-stone-500 mt-1">explainability</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* ═══ ARCHITECTURE PIPELINE ═══ */}
      <Section dark id="architecture" className="py-32 overflow-hidden">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="text-xs uppercase tracking-[0.2em] text-[#3D8B8B] font-semibold mb-4 block">System Architecture</span>
          <h2 className="text-3xl sm:text-5xl font-display font-semibold text-white mb-4">
            The Agentic Pipeline
          </h2>
          <p className="text-stone-400 max-w-2xl mx-auto">
            Data flows through specialized branches — numeric vitals to deterministic ML models, clinical text to MedGemma — then converges at the synthesis agent for a unified, explainable report.
          </p>
        </motion.div>

        <PipelineVisualization />
      </Section>

      {/* ═══ THREE PILLARS ═══ */}
      <Section id="features" className="py-32">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-xs uppercase tracking-[0.2em] text-[#E07A5F] font-semibold mb-4 block">Key Advantages</span>
          <h2 className="text-3xl sm:text-5xl font-display font-semibold text-stone-900">
            Why Aegis is Different
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: Eye,
              title: 'Explainability',
              desc: 'SHAP-powered explanations for every prediction. Know exactly which features drive each risk score — no more black boxes.',
              color: '#E07A5F',
              stat: '100%',
              statLabel: 'Traceable',
            },
            {
              icon: Zap,
              title: 'Cost Efficiency',
              desc: 'Offload heavy computation to classical ML models. Only the synthesis step uses LLM tokens — cutting costs by over 80%.',
              color: '#3D8B8B',
              stat: '81%',
              statLabel: 'Cost Reduction',
            },
            {
              icon: Shield,
              title: 'Clinical Accuracy',
              desc: 'Regression and classification models handle vitals with mathematical precision — no hallucinated thresholds.',
              color: '#6EBB8D',
              stat: '0',
              statLabel: 'Hallucinations',
            },
          ].map((item, i) => (
            <motion.div
              key={item.title}
              className="group relative p-8 rounded-2xl bg-white border border-stone-200 hover:border-stone-300
                hover:shadow-xl hover:shadow-stone-200/50 transition-all duration-500"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15, duration: 0.6 }}
            >
              {/* Accent top bar */}
              <div className="absolute top-0 left-8 right-8 h-[2px] rounded-full" style={{ background: item.color }} />

              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-6" style={{ background: `${item.color}15` }}>
                <item.icon size={22} style={{ color: item.color }} />
              </div>

              <h3 className="text-xl font-semibold text-stone-900 mb-3">{item.title}</h3>
              <p className="text-stone-500 text-sm leading-relaxed mb-6">{item.desc}</p>

              <div className="pt-4 border-t border-stone-100">
                <div className="text-3xl font-bold" style={{ color: item.color }}>
                  <AnimatedCounter value={Number(item.stat.replace('%', ''))} suffix={item.stat.includes('%') ? '%' : ''} />
                </div>
                <div className="text-xs text-stone-400 mt-1">{item.statLabel}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </Section>

      {/* ═══ SHAP EXPLAINABILITY ═══ */}
      <Section dark id="explainability" className="py-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <span className="text-xs uppercase tracking-[0.2em] text-[#F4A896] font-semibold mb-4 block">Explainability Engine</span>
            <h2 className="text-3xl sm:text-4xl font-display font-semibold text-white mb-6 leading-tight">
              Every prediction tells you <span className="text-[#E07A5F]">why</span>
            </h2>
            <p className="text-stone-400 mb-8 leading-relaxed">
              Using SHAP (SHapley Additive exPlanations), Aegis generates feature importance heatmaps for each patient.
              Doctors see exactly which vitals and lab values drive each risk score — building trust through transparency.
            </p>
            <div className="flex flex-wrap gap-3">
              <span className="px-3 py-1.5 rounded-lg bg-stone-800 text-stone-300 text-xs font-medium">Global Interpretability</span>
              <span className="px-3 py-1.5 rounded-lg bg-stone-800 text-stone-300 text-xs font-medium">Local Explanations</span>
              <span className="px-3 py-1.5 rounded-lg bg-stone-800 text-stone-300 text-xs font-medium">Feature Heatmaps</span>
              <span className="px-3 py-1.5 rounded-lg bg-stone-800 text-stone-300 text-xs font-medium">Waterfall Plots</span>
            </div>
          </motion.div>

          <motion.div
            className="p-8 rounded-2xl bg-stone-800/50 border border-stone-700/50"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <div className="w-2 h-2 rounded-full bg-[#E07A5F]" />
              <span className="text-xs text-stone-400 font-medium uppercase tracking-wider">SHAP Feature Importance — Patient #4821</span>
            </div>
            <SHAPChart />
          </motion.div>
        </div>
      </Section>

      {/* ═══ ML SWARM DETAIL ═══ */}
      <Section className="py-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Swarm visualization */}
          <motion.div
            className="order-2 lg:order-1"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <div className="p-8 rounded-2xl bg-stone-900 border border-stone-800">
              <div className="flex items-center gap-2 mb-8">
                <Brain size={14} className="text-[#E07A5F]" />
                <span className="text-xs text-stone-400 font-medium uppercase tracking-wider">ML Swarm — Active Models</span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-8">
                {[
                  { name: 'Cardiac', type: 'XGBoost', risk: 78, color: '#E07A5F' },
                  { name: 'Diabetes', type: 'Random Forest', risk: 45, color: '#E9B44C' },
                  { name: 'Sepsis', type: 'Logistic Reg', risk: 12, color: '#6EBB8D' },
                ].map((model, i) => (
                  <motion.div
                    key={model.name}
                    className="p-4 rounded-xl bg-stone-800/80 border border-stone-700/50 text-center"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 + 0.3 }}
                  >
                    <RiskGauge percentage={model.risk} label="" color={model.color} />
                    <div className="text-sm font-semibold text-white mt-3">{model.name}</div>
                    <div className="text-xs text-stone-500">{model.type}</div>
                  </motion.div>
                ))}
              </div>

              {/* Sparklines */}
              <div className="space-y-3 pt-4 border-t border-stone-800">
                <Sparkline data={[72, 74, 71, 78, 82, 79, 76, 80, 77, 73, 75, 78]} color="#E07A5F" label="Heart Rate Trend" />
                <Sparkline data={[120, 118, 125, 122, 130, 128, 135, 132, 129, 126, 124, 128]} color="#3D8B8B" label="Blood Pressure" />
                <Sparkline data={[96, 97, 95, 98, 97, 96, 98, 99, 97, 98, 96, 98]} color="#6EBB8D" label="Oxygen Saturation" />
              </div>
            </div>
          </motion.div>

          <motion.div
            className="order-1 lg:order-2"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <span className="text-xs uppercase tracking-[0.2em] text-[#E07A5F] font-semibold mb-4 block">The ML Swarm</span>
            <h2 className="text-3xl sm:text-4xl font-display font-semibold text-stone-900 mb-6 leading-tight">
              Task-specific models,<br />millisecond inference
            </h2>
            <p className="text-stone-500 mb-8 leading-relaxed">
              Instead of one massive model, we deploy a swarm of lightweight, task-specific ML models.
              Each model is independently updatable — update the Diabetes model without touching Cardiac.
              Inference on tabular data takes <span className="text-stone-800 font-semibold">milliseconds</span>, not seconds.
            </p>
            <div className="space-y-4">
              {[
                { label: 'Modularity', desc: 'Independent model updates & deployments' },
                { label: 'Speed', desc: 'Sub-100ms inference on structured data' },
                { label: 'Precision', desc: 'No calculation hallucinations — deterministic output' },
              ].map((item, i) => (
                <motion.div
                  key={item.label}
                  className="flex gap-4 items-start"
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div className="w-6 h-6 rounded-full bg-[#E07A5F]/10 flex items-center justify-center shrink-0 mt-0.5">
                    <div className="w-2 h-2 rounded-full bg-[#E07A5F]" />
                  </div>
                  <div>
                    <p className="text-stone-900 font-medium">{item.label}</p>
                    <p className="text-sm text-stone-500">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </Section>

      {/* ═══ MEDGEMMA + TOKEN COMPARISON ═══ */}
      <Section dark className="py-32">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <span className="text-xs uppercase tracking-[0.2em] text-[#3D8B8B] font-semibold mb-4 block">Text Analysis</span>
            <h2 className="text-3xl sm:text-4xl font-display font-semibold text-white mb-6 leading-tight">
              MedGemma reads what charts miss
            </h2>
            <p className="text-stone-400 mb-8 leading-relaxed">
              A specialized Small Language Model fine-tuned on medical literature. It extracts symptoms, detects family history, and identifies lifestyle risks buried in clinical notes — structured into actionable JSON.
            </p>

            {/* Mock extraction */}
            <div className="p-5 rounded-xl bg-stone-800/60 border border-stone-700/50 font-mono text-xs space-y-2 overflow-hidden">
              <div className="flex items-center gap-2 text-stone-500 mb-3">
                <FileText size={12} />
                <span>Clinical Note Extraction</span>
              </div>
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 }}
              >
                <span className="text-stone-500">{'{'}</span><br />
                <span className="text-stone-500">{'  '}</span>
                <span className="text-[#3D8B8B]">"smoking"</span>
                <span className="text-stone-500">: </span>
                <span className="text-[#E07A5F]">"1 pack/day, 12 years"</span>
                <span className="text-stone-500">,</span><br />
                <span className="text-stone-500">{'  '}</span>
                <span className="text-[#3D8B8B]">"family_history"</span>
                <span className="text-stone-500">: </span>
                <span className="text-[#E07A5F]">"T2D (maternal)"</span>
                <span className="text-stone-500">,</span><br />
                <span className="text-stone-500">{'  '}</span>
                <span className="text-[#3D8B8B]">"uncharted_symptom"</span>
                <span className="text-stone-500">: </span>
                <span className="text-[#E07A5F]">"intermittent chest tightness"</span>
                <span className="text-stone-500">,</span><br />
                <span className="text-stone-500">{'  '}</span>
                <span className="text-[#3D8B8B]">"risk_flags"</span>
                <span className="text-stone-500">: [</span>
                <span className="text-[#E9B44C]">"sedentary"</span>
                <span className="text-stone-500">, </span>
                <span className="text-[#E9B44C]">"high_stress"</span>
                <span className="text-stone-500">]</span><br />
                <span className="text-stone-500">{'}'}</span>
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="p-8 rounded-2xl bg-stone-800/50 border border-stone-700/50">
              <div className="flex items-center gap-2 mb-8">
                <TrendingUp size={14} className="text-[#3D8B8B]" />
                <span className="text-xs text-stone-400 font-medium uppercase tracking-wider">Token Usage Comparison</span>
              </div>
              <TokenChart />

              <div className="mt-8 pt-6 border-t border-stone-700/50 grid grid-cols-2 gap-6">
                <div>
                  <div className="text-3xl font-bold text-[#3D8B8B]">
                    <AnimatedCounter value={81} suffix="%" />
                  </div>
                  <div className="text-xs text-stone-500 mt-1">Cost Reduction</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-[#E07A5F]">
                    <AnimatedCounter value={20} suffix="x" />
                  </div>
                  <div className="text-xs text-stone-500 mt-1">Faster Inference</div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </Section>

      {/* ═══ HOW IT WORKS — STEPS ═══ */}
      <Section className="py-32">
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-xs uppercase tracking-[0.2em] text-[#3D8B8B] font-semibold mb-4 block">Data Pipeline</span>
          <h2 className="text-3xl sm:text-5xl font-display font-semibold text-stone-900">
            From Data to Diagnosis
          </h2>
        </motion.div>

        <div className="relative">
          {/* Vertical connecting line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-stone-300 to-transparent hidden lg:block" />

          {[
            {
              step: '01',
              title: 'Ingestion',
              desc: 'Raw PDF/JSON patient data hits the API. The Orchestrator validates input and sanitizes PII.',
              icon: FileText,
              color: '#E07A5F',
            },
            {
              step: '02',
              title: 'Separation',
              desc: 'The Separator splits data by modality — structured vitals to the ML fork, free-text clinical notes to MedGemma.',
              icon: Activity,
              color: '#3D8B8B',
            },
            {
              step: '03',
              title: 'Parallel Analysis',
              desc: 'The ML Swarm processes numeric data in milliseconds while MedGemma extracts hidden insights from clinical text — simultaneously.',
              icon: Brain,
              color: '#E07A5F',
            },
            {
              step: '04',
              title: 'Explainability',
              desc: 'SHAP wraps every ML prediction in feature importance — you see exactly why each risk score was generated.',
              icon: Eye,
              color: '#F4A896',
            },
            {
              step: '05',
              title: 'Synthesis & Report',
              desc: 'The Synthesis Agent merges all insights into a human-readable report with risk charts, SHAP waterfall plots, and clinical summary.',
              icon: Sparkles,
              color: '#3D8B8B',
            },
          ].map((item, i) => (
            <motion.div
              key={item.step}
              className={`relative flex items-center gap-8 mb-16 last:mb-0 ${i % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <div className={`flex-1 ${i % 2 === 0 ? 'lg:text-right' : 'lg:text-left'}`}>
                <span className="text-xs font-bold tracking-widest" style={{ color: item.color }}>
                  STEP {item.step}
                </span>
                <h3 className="text-xl font-semibold text-stone-900 mt-1 mb-2">{item.title}</h3>
                <p className="text-sm text-stone-500 max-w-md leading-relaxed inline-block">{item.desc}</p>
              </div>

              {/* Center dot */}
              <div className="hidden lg:flex shrink-0 w-14 h-14 rounded-full items-center justify-center z-10" style={{ background: `${item.color}15` }}>
                <item.icon size={22} style={{ color: item.color }} />
              </div>

              <div className="flex-1 hidden lg:block" />
            </motion.div>
          ))}
        </div>
      </Section>

      {/* ═══ BUSINESS & REVENUE MODEL ═══ */}
      <Section dark className="py-24 overflow-hidden" id="business">
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="text-xs uppercase tracking-[0.2em] text-[#E07A5F] font-semibold mb-4 block">Business & Revenue</span>
          <h2 className="text-3xl sm:text-5xl font-display font-semibold text-white mb-4">
            The Enterprise{' '}
            <span className="bg-gradient-to-r from-[#E07A5F] to-[#F4A896] bg-clip-text text-transparent">
              Intelligence Layer
            </span>
          </h2>
          <p className="text-stone-400 max-w-xl mx-auto text-sm leading-relaxed">
            B2B Hybrid Intelligence — the silent layer behind confident clinical decisions,
            with scalable value-based pricing aligned to partner outcomes.
          </p>
        </motion.div>

        {/* ── Horizontal card strip ── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          {[
            {
              icon: Building2,
              title: 'Hospitals',
              desc: 'Real-time EHR integration to flag Sepsis & Cardiac risk across health systems.',
              accent: '#E07A5F',
              tag: 'Segment',
            },
            {
              icon: FlaskConical,
              title: 'Diagnostic Labs',
              desc: '"The Narrator" enriches raw lab data into contextualized early-warning reports.',
              accent: '#3D8B8B',
              tag: 'Segment',
            },
            {
              icon: ShieldCheck,
              title: 'Payers & Insurers',
              desc: 'Numeric Swarm-powered risk modeling to reduce claims volatility.',
              accent: '#6EBB8D',
              tag: 'Segment',
            },
            {
              icon: CreditCard,
              title: 'API Partners',
              desc: 'Usage-based licensing for third-party apps integrating predictive scores.',
              accent: '#F4A896',
              tag: 'Channel',
            },
          ].map((card, i) => (
            <motion.div
              key={card.title}
              className="group relative"
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
            >
              <div className="relative h-full p-5 rounded-2xl bg-stone-800/40 border border-stone-700/30
                hover:border-stone-600/60 hover:bg-stone-800/70 transition-all duration-400 overflow-hidden">
                {/* Top gradient line */}
                <div className="absolute top-0 inset-x-0 h-[2px]" style={{ background: `linear-gradient(90deg, transparent, ${card.accent}, transparent)` }} />
                {/* Glow orb */}
                <div className="absolute -top-8 -right-8 w-24 h-24 rounded-full blur-2xl opacity-[0.07]" style={{ background: card.accent }} />

                <div className="flex items-center justify-between mb-4">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${card.accent}12` }}>
                    <card.icon size={16} style={{ color: card.accent }} />
                  </div>
                  <span className="text-[9px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full" style={{ background: `${card.accent}10`, color: card.accent }}>
                    {card.tag}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-white mb-1.5">{card.title}</h3>
                <p className="text-xs text-stone-400 leading-relaxed">{card.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* ── Value Pillars + Revenue: side-by-side ── */}
        <div className="grid lg:grid-cols-5 gap-4">
          {/* Left: 3 value pillars stacked tight */}
          <div className="lg:col-span-2 space-y-3">
            {[
              { icon: Target, title: 'Clinical Dependability', desc: 'Friction-free during peak clinical hours — digital dependability, not just access.', accent: '#E07A5F' },
              { icon: Lock, title: 'Accountable AI', desc: 'ML + Knowledge Graphs = human-verifiable reasoning for enterprise clinical trust.', accent: '#3D8B8B' },
              { icon: Clock, title: 'Rapid ROI', desc: 'Modular "Quick Wins" — measurable returns within a single quarter of deployment.', accent: '#6EBB8D' },
            ].map((p, i) => (
              <motion.div
                key={p.title}
                className="flex gap-4 p-4 rounded-xl bg-stone-800/30 border border-stone-700/30"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.5 }}
              >
                <div className="w-9 h-9 rounded-lg shrink-0 flex items-center justify-center mt-0.5" style={{ background: `${p.accent}12` }}>
                  <p.icon size={16} style={{ color: p.accent }} />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white mb-0.5">{p.title}</h4>
                  <p className="text-xs text-stone-400 leading-relaxed">{p.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Right: Revenue tiers as tall vertical cards */}
          <div className="lg:col-span-3 grid grid-cols-3 gap-4">
            {[
              {
                title: 'Essential',
                subtitle: 'Core Swarm',
                accent: '#E07A5F',
                icon: Layers,
                features: ['Numeric Swarm', 'SHAP Reports', 'Vital Scoring', 'API Access'],
                label: 'SaaS',
              },
              {
                title: 'Clinical',
                subtitle: 'Hybrid Insight',
                accent: '#3D8B8B',
                icon: Brain,
                features: ['+ MedGemma NLP', '+ Knowledge Graph', '+ Narrator Agent', '+ Priority SLA'],
                label: 'SaaS Pro',
                featured: true,
              },
              {
                title: 'Enterprise',
                subtitle: 'Custom Deploy',
                accent: '#6EBB8D',
                icon: Wrench,
                features: ['On-prem Setup', 'Custom Swarms', 'Managed Ops', 'Dedicated CSM'],
                label: 'Partnership',
              },
            ].map((tier, i) => (
              <motion.div
                key={tier.title}
                className="group relative"
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 + 0.15, duration: 0.5 }}
              >
                <div
                  className={`relative h-full rounded-2xl p-5 flex flex-col overflow-hidden transition-all duration-400 ${
                    tier.featured
                      ? 'bg-gradient-to-b from-stone-800/80 to-stone-900 border-2'
                      : 'bg-stone-800/30 border border-stone-700/30 hover:border-stone-600/50'
                  }`}
                  style={tier.featured ? { borderColor: `${tier.accent}40` } : undefined}
                >
                  {/* Top gradient bar */}
                  <div className="absolute top-0 inset-x-0 h-[3px] rounded-b-full" style={{ background: `linear-gradient(90deg, transparent 5%, ${tier.accent} 50%, transparent 95%)` }} />

                  {/* Glow */}
                  {tier.featured && (
                    <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-32 h-32 rounded-full blur-3xl opacity-[0.08]" style={{ background: tier.accent }} />
                  )}

                  {/* Badge */}
                  <span className="text-[9px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full self-start mb-4"
                    style={{ background: `${tier.accent}12`, color: tier.accent }}>
                    {tier.label}
                  </span>

                  <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
                    style={{ background: `${tier.accent}10`, border: `1px solid ${tier.accent}20` }}>
                    <tier.icon size={18} style={{ color: tier.accent }} />
                  </div>

                  <h3 className="text-base font-semibold text-white">{tier.title}</h3>
                  <span className="text-[11px] text-stone-500 mb-4">{tier.subtitle}</span>

                  <div className="flex-1" />

                  <div className="space-y-2.5 pt-4 border-t border-stone-700/30">
                    {tier.features.map((f) => (
                      <div key={f} className="flex items-center gap-2">
                        <Check size={12} style={{ color: tier.accent }} className="shrink-0" />
                        <span className="text-xs text-stone-400">{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>

      {/* ═══ FINAL CTA ═══ */}
      <Section dark className="py-32">
        <motion.div
          className="text-center max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="relative inline-block mb-8">
            <div className="absolute -inset-px rounded-2xl bg-gradient-to-r from-[#E07A5F] to-[#3D8B8B] blur-lg opacity-30" />
            <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-[#E07A5F] to-[#C96A52] flex items-center justify-center mx-auto">
              <Shield size={28} className="text-white" />
            </div>
          </div>

          <h2 className="text-3xl sm:text-5xl font-display font-semibold text-white mb-6 leading-tight">
            Ready to see predictions<br />you can actually <span className="text-[#E07A5F]">trust</span>?
          </h2>
          <p className="text-stone-400 text-lg mb-10 max-w-xl mx-auto">
            Project Aegis brings explainable AI to clinical diagnostics. No black boxes. No hallucinations.
            Just precise, transparent health risk predictions.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate('/login')}
              className="group px-10 py-4 rounded-xl bg-gradient-to-r from-[#E07A5F] to-[#C96A52] text-white font-semibold text-base
                hover:shadow-lg hover:shadow-[#E07A5F]/25 transition-all duration-300 flex items-center gap-2"
            >
              Start Diagnosing
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="px-10 py-4 rounded-xl border border-stone-700 text-stone-300 font-medium text-base
                hover:border-stone-500 hover:text-white transition-all duration-300"
            >
              Back to Top
            </button>
          </div>
        </motion.div>
      </Section>

      {/* ═══ FOOTER ═══ */}
      <footer className="bg-stone-900 border-t border-stone-800 py-8">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[#E07A5F] to-[#C96A52] flex items-center justify-center">
              <Shield size={14} className="text-white" />
            </div>
            <span className="text-stone-500 text-sm">Project Aegis — Hybrid Agentic Health Intelligence</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <p className="text-stone-400 text-sm font-medium">
              Made by <span className="text-[#E07A5F] font-semibold">The Big O</span>
            </p>
            <p className="text-stone-600 text-xs">
              Hackathon MVP &middot; &copy; {new Date().getFullYear()} Project Aegis
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
