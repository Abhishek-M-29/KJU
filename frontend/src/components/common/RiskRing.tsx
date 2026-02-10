import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface RiskRingProps {
  riskLevel: 'low' | 'watch' | 'critical'
  percentage: number
  size?: number
  strokeWidth?: number
  className?: string
}

export function RiskRing({
  riskLevel,
  percentage,
  size = 60,
  strokeWidth = 6,
  className,
}: RiskRingProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const colorMap = {
    low: {
      stroke: 'var(--color-risk-low)',
      bg: 'rgba(34, 197, 94, 0.15)',
      label: 'Low',
    },
    watch: {
      stroke: 'var(--color-risk-watch)',
      bg: 'rgba(234, 179, 8, 0.15)',
      label: 'Watch',
    },
    critical: {
      stroke: 'var(--color-risk-critical)',
      bg: 'rgba(239, 68, 68, 0.15)',
      label: 'Critical',
    },
  }

  const { stroke, bg, label } = colorMap[riskLevel]

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={bg}
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-xs font-bold"
          style={{ color: stroke }}
        >
          {percentage}%
        </span>
      </div>
      <span
        className="absolute -bottom-5 text-[10px] font-medium"
        style={{ color: stroke }}
      >
        {label}
      </span>
    </div>
  )
}
