import { Heart, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

interface VitalsBadgeProps {
  type: 'heartRate' | 'bloodPressure'
  value: number | string
  className?: string
}

export function VitalsBadge({ type, value, className }: VitalsBadgeProps) {
  const isHeartRate = type === 'heartRate'

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/50 backdrop-blur-sm border border-white/30',
        className
      )}
    >
      {isHeartRate ? (
        <Heart className="w-4 h-4 text-risk-critical" fill="currentColor" />
      ) : (
        <Activity className="w-4 h-4 text-primary" />
      )}
      <span className="text-sm font-medium text-text-primary">
        {value}
        {isHeartRate && <span className="text-text-muted text-xs ml-0.5">bpm</span>}
      </span>
    </div>
  )
}
