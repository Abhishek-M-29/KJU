import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Server,
  Database,
  Globe,
  Brain,
  Shield,
  Zap,
  Layers,
  GitBranch,
  Network,
  Lock,
  BarChart3,
  ArrowUpRight,
  ArrowRightLeft,
  TrendingUp,
} from 'lucide-react'

/* ═══════════════════════════════════════════════════
   ANIMATED SVG VISUAL: Horizontal Node Expansion
   ═══════════════════════════════════════════════════ */
function HorizontalNodeGraph() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-50px' })

  const nodes = [
    { cx: 100, cy: 90, label: 'K8s\nCluster A', delay: 0.2 },
    { cx: 260, cy: 50, label: 'K8s\nCluster B', delay: 0.5 },
    { cx: 260, cy: 130, label: 'K8s\nCluster C', delay: 0.7 },
    { cx: 420, cy: 30, label: 'Hospital\nNode 1', delay: 0.9 },
    { cx: 420, cy: 90, label: 'Hospital\nNode 2', delay: 1.0 },
    { cx: 420, cy: 150, label: 'Hospital\nNode 3', delay: 1.1 },
    { cx: 560, cy: 60, label: 'Neo4j\nShard α', delay: 1.3 },
    { cx: 560, cy: 120, label: 'Neo4j\nShard β', delay: 1.4 },
  ]

  const edges = [
    [0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 5], [3, 6], [4, 6], [4, 7], [5, 7],
  ]

  return (
    <svg ref={ref} viewBox="0 0 660 180" className="w-full" style={{ maxHeight: 280 }}>
      <defs>
        <linearGradient id="hEdge" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#E07A5F" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#3D8B8B" stopOpacity="0.6" />
        </linearGradient>
        <filter id="hGlow">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <radialGradient id="nodeGrad" cx="50%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#fff" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Edges */}
      {edges.map(([a, b], i) => (
        <motion.line
          key={`edge-${i}`}
          x1={nodes[a].cx} y1={nodes[a].cy}
          x2={nodes[b].cx} y2={nodes[b].cy}
          stroke="url(#hEdge)"
          strokeWidth="1.5"
          strokeDasharray="6 4"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={inView ? { pathLength: 1, opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: Math.min(nodes[a].delay, nodes[b].delay) + 0.2 }}
        />
      ))}

      {/* Nodes */}
      {nodes.map((n, i) => (
        <motion.g
          key={`node-${i}`}
          initial={{ scale: 0, opacity: 0 }}
          animate={inView ? { scale: 1, opacity: 1 } : {}}
          transition={{ type: 'spring', stiffness: 200, damping: 20, delay: n.delay }}
        >
          <circle cx={n.cx} cy={n.cy} r="26" fill="#1C1917" stroke="#E07A5F" strokeWidth="1.5" opacity="0.9" />
          <circle cx={n.cx} cy={n.cy} r="26" fill="url(#nodeGrad)" />
          {/* Pulse ring */}
          <motion.circle
            cx={n.cx} cy={n.cy} r="26"
            fill="none" stroke="#E07A5F" strokeWidth="1"
            initial={{ r: 26, opacity: 0.6 }}
            animate={inView ? { r: 38, opacity: 0 } : {}}
            transition={{ duration: 2, delay: n.delay + 0.5, repeat: Infinity, repeatDelay: 3 }}
          />
          {n.label.split('\n').map((line, li) => (
            <text
              key={li}
              x={n.cx} y={n.cy + (li - 0.5) * 11 + 2}
              textAnchor="middle"
              fill="#F5F5F4"
              fontSize="8"
              fontFamily="'Instrument Sans', sans-serif"
              fontWeight="500"
            >
              {line}
            </text>
          ))}
        </motion.g>
      ))}
    </svg>
  )
}

/* ═══════════════════════════════════════════════════
   ANIMATED SVG VISUAL: Vertical Power Stack
   ═══════════════════════════════════════════════════ */
function VerticalPowerStack() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-50px' })

  const layers = [
    { y: 220, label: 'Base Infrastructure', sub: 'Standard CPU / RAM', color: '#78716C', delay: 0.2 },
    { y: 175, label: 'Enhanced Compute', sub: 'Multi-modal Models', color: '#81B0AA', delay: 0.5 },
    { y: 130, label: 'Knowledge Depth', sub: '100TB+ Graph In-Memory', color: '#3D8B8B', delay: 0.8 },
    { y: 85, label: 'Sanitization Power', sub: 'AI-Driven PII Scrubbing', color: '#C96A52', delay: 1.1 },
    { y: 40, label: 'SHAP Explainability', sub: 'Real-time 1000+ Features', color: '#E07A5F', delay: 1.4 },
  ]

  return (
    <svg ref={ref} viewBox="0 0 420 270" className="w-full" style={{ maxHeight: 320 }}>
      <defs>
        <linearGradient id="vArrow" x1="50%" y1="100%" x2="50%" y2="0%">
          <stop offset="0%" stopColor="#78716C" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#E07A5F" stopOpacity="0.8" />
        </linearGradient>
        <filter id="layerShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.15" />
        </filter>
      </defs>

      {/* Rising arrow */}
      <motion.line
        x1="50" y1="250" x2="50" y2="20"
        stroke="url(#vArrow)" strokeWidth="2" strokeDasharray="4 3"
        initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}}
        transition={{ duration: 1.5, delay: 0.1 }}
      />
      <motion.polygon
        points="50,12 44,24 56,24"
        fill="#E07A5F"
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}}
        transition={{ delay: 1.6 }}
      />
      <motion.text
        x="50" y="8" textAnchor="middle" fill="#A8A29E" fontSize="7"
        fontFamily="'Instrument Sans', sans-serif"
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}}
        transition={{ delay: 1.7 }}
      >
        POWER
      </motion.text>

      {/* Layers */}
      {layers.map((l, i) => (
        <motion.g
          key={i}
          initial={{ x: -60, opacity: 0 }}
          animate={inView ? { x: 0, opacity: 1 } : {}}
          transition={{ type: 'spring', stiffness: 100, damping: 18, delay: l.delay }}
          filter="url(#layerShadow)"
        >
          <rect x="75" y={l.y} width={280 + i * 15} height="36" rx="8"
            fill={l.color} opacity="0.15"
            stroke={l.color} strokeWidth="1"
          />
          {/* Filled capacity bar */}
          <motion.rect
            x="75" y={l.y} height="36" rx="8"
            fill={l.color} opacity="0.08"
            initial={{ width: 0 }}
            animate={inView ? { width: 280 + i * 15 } : {}}
            transition={{ duration: 1.2, delay: l.delay + 0.3 }}
          />
          <text x="85" y={l.y + 16} fill="#F5F5F4" fontSize="10" fontWeight="600"
            fontFamily="'Instrument Sans', sans-serif">
            {l.label}
          </text>
          <text x="85" y={l.y + 28} fill="#A8A29E" fontSize="7.5"
            fontFamily="'Instrument Sans', sans-serif">
            {l.sub}
          </text>
          {/* Tier badge */}
          <rect x={280 + i * 15 + 58} y={l.y + 8} width="30" height="18" rx="9" fill={l.color} opacity="0.3" />
          <text x={280 + i * 15 + 73} y={l.y + 21} textAnchor="middle" fill={l.color} fontSize="8" fontWeight="700"
            fontFamily="'Instrument Sans', sans-serif">
            T{i + 1}
          </text>
        </motion.g>
      ))}
    </svg>
  )
}

/* ═══════════════════════════════════════════════════
   ANIMATED SVG VISUAL: Diagonal Scaling Path
   ═══════════════════════════════════════════════════ */
function DiagonalScalingPath() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <svg ref={ref} viewBox="0 0 600 300" className="w-full" style={{ maxHeight: 360 }}>
      <defs>
        <linearGradient id="diagGrad" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3D8B8B" />
          <stop offset="50%" stopColor="#E07A5F" />
          <stop offset="100%" stopColor="#C96A52" />
        </linearGradient>
        <linearGradient id="zoneV" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stopColor="#3D8B8B" stopOpacity="0" />
          <stop offset="100%" stopColor="#3D8B8B" stopOpacity="0.08" />
        </linearGradient>
        <linearGradient id="zoneH" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#E07A5F" stopOpacity="0" />
          <stop offset="100%" stopColor="#E07A5F" stopOpacity="0.08" />
        </linearGradient>
        <filter id="diagGlow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {/* Grid */}
      {[0, 1, 2, 3, 4, 5, 6].map(i => (
        <line key={`gv-${i}`} x1={80 + i * 80} y1="30" x2={80 + i * 80} y2="260" stroke="#44403C" strokeWidth="0.5" opacity="0.3" />
      ))}
      {[0, 1, 2, 3, 4, 5].map(i => (
        <line key={`gh-${i}`} x1="60" y1={40 + i * 44} x2="570" y2={40 + i * 44} stroke="#44403C" strokeWidth="0.5" opacity="0.3" />
      ))}

      {/* Axis labels */}
      <text x="315" y="290" textAnchor="middle" fill="#78716C" fontSize="10" fontWeight="600"
        fontFamily="'Instrument Sans', sans-serif">
        HORIZONTAL SCALE → Nodes / Instances
      </text>
      <text transform="rotate(-90, 25, 150)" x="25" y="150" textAnchor="middle" fill="#78716C" fontSize="10" fontWeight="600"
        fontFamily="'Instrument Sans', sans-serif">
        VERTICAL SCALE → Compute Power
      </text>

      {/* Vertical zone */}
      <rect x="60" y="30" width="140" height="230" fill="url(#zoneV)" rx="8" />
      <text x="130" y="52" textAnchor="middle" fill="#3D8B8B" fontSize="8" fontWeight="600"
        fontFamily="'Instrument Sans', sans-serif" opacity="0.7">
        VERTICAL PHASE
      </text>

      {/* Horizontal zone */}
      <rect x="300" y="30" width="270" height="140" fill="url(#zoneH)" rx="8" />
      <text x="435" y="52" textAnchor="middle" fill="#E07A5F" fontSize="8" fontWeight="600"
        fontFamily="'Instrument Sans', sans-serif" opacity="0.7">
        HORIZONTAL PHASE
      </text>

      {/* The Diagonal Path */}
      <motion.path
        d="M 90,240 C 120,220 140,180 180,150 C 220,120 260,100 320,85 C 380,70 440,60 540,50"
        fill="none"
        stroke="url(#diagGrad)"
        strokeWidth="3"
        strokeLinecap="round"
        filter="url(#diagGlow)"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={inView ? { pathLength: 1, opacity: 1 } : {}}
        transition={{ duration: 2.5, delay: 0.3, ease: 'easeInOut' }}
      />

      {/* Waypoints on the diagonal */}
      {[
        { cx: 90, cy: 240, label: 'Start', delay: 0.5 },
        { cx: 180, cy: 150, label: 'Threshold', delay: 1.2 },
        { cx: 320, cy: 85, label: 'Clone', delay: 1.8 },
        { cx: 540, cy: 50, label: 'Optimal', delay: 2.5 },
      ].map((p, i) => (
        <motion.g key={i}
          initial={{ scale: 0, opacity: 0 }}
          animate={inView ? { scale: 1, opacity: 1 } : {}}
          transition={{ type: 'spring', stiffness: 200, damping: 20, delay: p.delay }}
        >
          <circle cx={p.cx} cy={p.cy} r="6" fill="#1C1917" stroke="url(#diagGrad)" strokeWidth="2" />
          <motion.circle cx={p.cx} cy={p.cy} r="6" fill="none" stroke="#E07A5F" strokeWidth="1"
            initial={{ r: 6, opacity: 0.8 }} animate={inView ? { r: 14, opacity: 0 } : {}}
            transition={{ duration: 2, delay: p.delay + 0.3, repeat: Infinity, repeatDelay: 4 }}
          />
          <text x={p.cx} y={p.cy - 12} textAnchor="middle" fill="#F5F5F4" fontSize="8" fontWeight="600"
            fontFamily="'Instrument Sans', sans-serif">
            {p.label}
          </text>
        </motion.g>
      ))}

      {/* Diagonal label */}
      <motion.text
        x="300" y="200" textAnchor="middle" fill="#E07A5F" fontSize="11" fontWeight="700"
        fontFamily="'Fraunces', serif"
        transform="rotate(-22, 300, 200)"
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 0.6 } : {}}
        transition={{ delay: 2.8 }}
      >
        DIAGONAL STRATEGY
      </motion.text>
    </svg>
  )
}

/* ═══════════════════════════════════════════════════
   CARD COMPONENTS
   ═══════════════════════════════════════════════════ */

interface ScalingCardProps {
  icon: React.ReactNode
  title: string
  description: string
  accent: string
  index: number
}

function ScalingCard({ icon, title, description, accent, index }: ScalingCardProps) {
  return (
    <motion.div
      className="group relative"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      {/* Hover glow */}
      <div
        className="absolute -inset-[1px] rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"
        style={{ background: `linear-gradient(135deg, ${accent}33, transparent)` }}
      />
      <div className="relative glass-card p-6 hover:shadow-lg transition-shadow duration-300">
        {/* Icon badge */}
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
          style={{ backgroundColor: `${accent}18`, color: accent }}
        >
          {icon}
        </div>

        <h4 className="text-sm font-semibold text-stone-800 mb-2 leading-tight">{title}</h4>
        <p className="text-xs text-stone-500 leading-relaxed">{description}</p>

        {/* Bottom accent bar */}
        <div className="mt-4 h-[2px] rounded-full overflow-hidden bg-stone-100">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: accent }}
            initial={{ width: '0%' }}
            whileInView={{ width: '60%' }}
            viewport={{ once: true }}
            transition={{ duration: 1.2, delay: index * 0.1 + 0.3 }}
          />
        </div>
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════════
   SECTION HEADER
   ═══════════════════════════════════════════════════ */
function SectionHeader({
  number,
  title,
  subtitle,
  accentColor,
}: {
  number: string
  title: string
  subtitle: string
  accentColor: string
}) {
  return (
    <motion.div
      className="flex items-start gap-5 mb-10"
      initial={{ opacity: 0, x: -30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.6 }}
    >
      <div
        className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 text-xl font-display font-semibold"
        style={{ backgroundColor: `${accentColor}15`, color: accentColor, border: `1px solid ${accentColor}30` }}
      >
        {number}
      </div>
      <div>
        <h3
          className="text-2xl md:text-3xl font-display font-semibold tracking-tight"
          style={{ color: accentColor }}
        >
          {title}
        </h3>
        <p className="text-sm text-stone-500 mt-1 max-w-xl">{subtitle}</p>
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════════
   METRIC PILL
   ═══════════════════════════════════════════════════ */
function MetricPill({ value, label, color }: { value: string; label: string; color: string }) {
  return (
    <motion.div
      className="flex items-center gap-2 px-3 py-1.5 rounded-full border"
      style={{ borderColor: `${color}30`, backgroundColor: `${color}08` }}
      initial={{ scale: 0.8, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      viewport={{ once: true }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <span className="text-xs font-bold" style={{ color }}>{value}</span>
      <span className="text-[10px] text-stone-500 uppercase tracking-wider">{label}</span>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════════
   FLOATING PARTICLE BACKGROUND
   ═══════════════════════════════════════════════════ */
/* Deterministic pseudo-random seed for pure render */
const PARTICLES = Array.from({ length: 18 }, (_, i) => {
  const seed = (i * 7 + 3) % 17
  return {
    id: i,
    x: ((seed * 31 + i * 13) % 100),
    y: ((seed * 47 + i * 23) % 100),
    size: 2 + (seed % 4),
    duration: 15 + (seed * 1.5),
    delay: (i * 0.55),
    color: i % 3 === 0 ? '#E07A5F' : i % 3 === 1 ? '#3D8B8B' : '#78716C',
  }
})

function FloatingParticles() {
  const particles = PARTICLES

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            backgroundColor: p.color,
            opacity: 0.15,
          }}
          animate={{
            y: [0, -40, 0],
            x: [0, 20, -10, 0],
            opacity: [0.1, 0.25, 0.1],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

/* ═══════════════════════════════════════════════════
   CONNECTION LINE BETWEEN SECTIONS
   ═══════════════════════════════════════════════════ */
function SectionDivider({ direction }: { direction: 'horizontal' | 'vertical' | 'diagonal' }) {
  const colors = {
    horizontal: ['#E07A5F', '#C96A52'],
    vertical: ['#3D8B8B', '#81B0AA'],
    diagonal: ['#E07A5F', '#3D8B8B'],
  }
  const [from, to] = colors[direction]

  return (
    <div className="flex justify-center my-8">
      <motion.div
        className="flex items-center gap-2"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: from }} />
        <div className="w-24 h-[1px]" style={{ background: `linear-gradient(90deg, ${from}, ${to})` }} />
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: to }} />
      </motion.div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════
   MAIN SCALING PAGE
   ═══════════════════════════════════════════════════ */
export function ScalingPage() {
  const navigate = useNavigate()

  const horizontalCards = [
    {
      icon: <Server className="w-5 h-5" />,
      title: 'Distributed Swarm Nodes',
      description:
        'Kubernetes replicates the ML Swarm across geographical nodes. New hospital clusters auto-spin and process local tensors in parallel.',
      accent: '#E07A5F',
    },
    {
      icon: <Database className="w-5 h-5" />,
      title: 'Graph Sharding & Federation',
      description:
        'Neo4j Infinigraph shards the Clinical Knowledge Graph to 100TB+, distributing medical data across servers while maintaining a unified view.',
      accent: '#C96A52',
    },
    {
      icon: <Globe className="w-5 h-5" />,
      title: 'API Gateway Load Balancing',
      description:
        'The Orchestrator sits behind a global load balancer, routing Branch A and B requests to nearest compute resources for real-time ICU alerts.',
      accent: '#E07A5F',
    },
    {
      icon: <GitBranch className="w-5 h-5" />,
      title: 'Stateless Agentic Workflows',
      description:
        'LangGraph manages agent states as stateless objects. Any distributed node can pick up a Narrator session for high availability.',
      accent: '#C96A52',
    },
  ]

  const verticalCards = [
    {
      icon: <Brain className="w-5 h-5" />,
      title: 'Model Complexity — The Swarm',
      description:
        'Upgrade from XGBoost ensembles to Foundation Models for Tabular Data. Nodes scale with more RAM and higher-tier CPUs for multi-modal inputs.',
      accent: '#3D8B8B',
    },
    {
      icon: <Network className="w-5 h-5" />,
      title: 'Knowledge Graph Depth',
      description:
        'Expand from SNOMED-CT ontologies to high-hop biomedical pathway retrieval. Vertically upgrade memory for sub-second in-memory traversal.',
      accent: '#81B0AA',
    },
    {
      icon: <Lock className="w-5 h-5" />,
      title: 'Orchestrator Sanitization Power',
      description:
        'Scale compute for AI-driven PII sanitization on clinical notes — staying ahead of India\'s DPDP Act and evolving privacy regulations.',
      accent: '#3D8B8B',
    },
    {
      icon: <BarChart3 className="w-5 h-5" />,
      title: 'Enhanced SHAP Explainability',
      description:
        'Generate SHAP values for 1000+ features simultaneously, enabling real-time logical context even in complex comorbidity cases.',
      accent: '#81B0AA',
    },
  ]

  return (
    <div className="min-h-screen bg-stone-900 text-stone-100 relative overflow-hidden">
      <FloatingParticles />

      {/* ─── Subtle grid texture ─── */}
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* ─── Top gradient bleed ─── */}
      <div className="fixed top-0 left-0 w-full h-[500px] pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse at 20% -10%, rgba(224,122,95,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% -10%, rgba(61,139,139,0.06) 0%, transparent 60%)',
        }}
      />

      {/* ═══════════════ NAVIGATION BAR ════════════════ */}
      <nav className="relative z-20 px-6 py-5 flex items-center justify-between max-w-7xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-stone-400 hover:text-stone-200 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm">Back</span>
        </button>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#E07A5F] animate-pulse" />
          <span className="text-xs text-stone-500 uppercase tracking-widest">Architecture</span>
        </div>
      </nav>

      {/* ═══════════════ HERO ═══════════════════════════ */}
      <header className="relative z-10 max-w-5xl mx-auto px-6 pt-10 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-stone-700/60 bg-stone-800/40 backdrop-blur mb-6">
            <Layers className="w-3.5 h-3.5 text-[#E07A5F]" />
            <span className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">Scaling Strategy</span>
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-display font-semibold tracking-tight leading-[0.95] mb-5">
            <span className="text-stone-100">Scaling </span>
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: 'linear-gradient(135deg, #E07A5F, #3D8B8B)' }}
            >
              Aegis
            </span>
          </h1>

          <p className="text-base md:text-lg text-stone-400 max-w-2xl mx-auto leading-relaxed">
            How our diagnostic pipeline grows from a single hospital to a continent-wide network — without
            ever dropping a heartbeat.
          </p>

          {/* Metric pills row */}
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            <MetricPill value="100TB+" label="Graph Scale" color="#3D8B8B" />
            <MetricPill value="<50ms" label="Latency" color="#E07A5F" />
            <MetricPill value="∞" label="Node Expansion" color="#81B0AA" />
            <MetricPill value="99.99%" label="Uptime SLA" color="#C96A52" />
          </div>
        </motion.div>
      </header>

      <div className="relative z-10 max-w-6xl mx-auto px-6 pb-32">

        {/* ═══════════════════════════════════════════════
           SECTION 1: HORIZONTAL SCALING
           ═══════════════════════════════════════════════ */}
        <section className="mb-24">
          <SectionHeader
            number="01"
            title="Horizontal Scaling"
            subtitle="Widening the reach — increasing capacity to handle thousands of concurrent users and hospitals without performance degradation."
            accentColor="#E07A5F"
          />

          {/* Visual: Node graph */}
          <motion.div
            className="glass-card p-6 md:p-8 mb-10 bg-stone-800/30 border-stone-700/40"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <ArrowRightLeft className="w-4 h-4 text-[#E07A5F]" />
              <span className="text-xs text-stone-400 uppercase tracking-widest font-medium">Distributed Node Topology</span>
            </div>
            <HorizontalNodeGraph />
            <p className="text-[11px] text-stone-500 mt-4 text-center italic">
              K8s clusters auto-provision → Hospital nodes expand → Graph shards federate across regions
            </p>
          </motion.div>

          {/* Cards grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {horizontalCards.map((card, i) => (
              <ScalingCard key={i} index={i} {...card} />
            ))}
          </div>
        </section>

        <SectionDivider direction="horizontal" />

        {/* ═══════════════════════════════════════════════
           SECTION 2: VERTICAL SCALING
           ═══════════════════════════════════════════════ */}
        <section className="mb-24">
          <SectionHeader
            number="02"
            title="Vertical Scaling"
            subtitle="Deepening the intelligence — increasing the power and complexity of individual components for sophisticated medical cases."
            accentColor="#3D8B8B"
          />

          {/* Visual: Power stack */}
          <motion.div
            className="glass-card p-6 md:p-8 mb-10 bg-stone-800/30 border-stone-700/40"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-4 h-4 text-[#3D8B8B]" />
              <span className="text-xs text-stone-400 uppercase tracking-widest font-medium">Computational Power Tiers</span>
            </div>
            <VerticalPowerStack />
            <p className="text-[11px] text-stone-500 mt-4 text-center italic">
              Each tier represents a vertical upgrade — from base infrastructure to real-time explainability at scale
            </p>
          </motion.div>

          {/* Cards grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {verticalCards.map((card, i) => (
              <ScalingCard key={i} index={i} {...card} />
            ))}
          </div>
        </section>

        <SectionDivider direction="diagonal" />

        {/* ═══════════════════════════════════════════════
           SECTION 3: DIAGONAL STRATEGY
           ═══════════════════════════════════════════════ */}
        <section className="mb-16">
          <SectionHeader
            number="03"
            title="The Diagonal Strategy"
            subtitle="The 2026 standard — scale vertically until hitting a performance-to-cost threshold, then shift to horizontal cloning for resilience."
            accentColor="#E07A5F"
          />

          {/* Visual: The diagonal path */}
          <motion.div
            className="glass-card p-6 md:p-10 mb-10 bg-stone-800/30 border-stone-700/40"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <ArrowUpRight className="w-4 h-4 text-[#E07A5F]" />
              <span className="text-xs text-stone-400 uppercase tracking-widest font-medium">Cost–Performance Optimization Path</span>
            </div>
            <DiagonalScalingPath />
            <p className="text-[11px] text-stone-500 mt-4 text-center italic">
              Vertical-first → Hit cost threshold → Clone horizontally across optimized nodes → Balanced resilience
            </p>
          </motion.div>

          {/* Strategy breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                phase: 'Phase 1',
                title: 'Vertical Push',
                desc: 'Maximize single-node power. Upgrade CPUs, RAM, and GPU tiers. Best cost-efficiency per operation.',
                icon: <TrendingUp className="w-5 h-5" />,
                accent: '#3D8B8B',
              },
              {
                phase: 'Phase 2',
                title: 'Threshold Detection',
                desc: 'Monitor performance-to-cost ratio. When marginal gains flatten, trigger horizontal expansion signal.',
                icon: <Zap className="w-5 h-5" />,
                accent: '#E07A5F',
              },
              {
                phase: 'Phase 3',
                title: 'Horizontal Clone',
                desc: 'Replicate the optimized instance across nodes. Achieves linear scaling with cost-predictable infrastructure.',
                icon: <Layers className="w-5 h-5" />,
                accent: '#C96A52',
              },
            ].map((phase, i) => (
              <motion.div
                key={i}
                className="relative group"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, duration: 0.5 }}
              >
                <div className="glass-card p-6 bg-stone-800/30 border-stone-700/40 h-full">
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className="w-9 h-9 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${phase.accent}18`, color: phase.accent }}
                    >
                      {phase.icon}
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-widest font-medium" style={{ color: phase.accent }}>
                        {phase.phase}
                      </div>
                      <div className="text-sm font-semibold text-stone-200">{phase.title}</div>
                    </div>
                  </div>
                  <p className="text-xs text-stone-400 leading-relaxed">{phase.desc}</p>

                  {/* Phase connector arrow */}
                  {i < 2 && (
                    <div className="hidden md:flex absolute top-1/2 -right-3 z-10 w-6 h-6 rounded-full bg-stone-800 border border-stone-700/60 items-center justify-center">
                      <ArrowUpRight className="w-3 h-3 text-stone-500" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ═══════════════════ FOOTER TAG ═══════════════════ */}
        <motion.div
          className="text-center pt-12"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.3 }}
        >
          <div className="inline-flex items-center gap-2 text-stone-600 text-xs">
            <Shield className="w-3.5 h-3.5" />
            <span className="uppercase tracking-widest">Project Aegis · Scaling Architecture · 2026</span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
