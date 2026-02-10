import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import type { Patient } from '@/types/patient'

interface PatientCardProps {
  patient: Patient
  onViewDetails?: (patientId: string) => void
}

export function PatientCard({ patient, onViewDetails }: PatientCardProps) {
  const initials = patient.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()

  // Subtle status indicator colors
  const statusColors = {
    critical: 'bg-rose-500',
    watch: 'bg-amber-400',
    low: 'bg-emerald-400',
  }

  return (
    <motion.div
      className="group relative bg-white rounded-2xl p-5 cursor-pointer border border-stone-100 hover:border-stone-200 transition-all duration-300"
      whileHover={{ y: -2, boxShadow: '0 12px 40px -12px rgba(0,0,0,0.12)' }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      onClick={() => onViewDetails?.(patient.id)}
    >
      {/* Status indicator - subtle left edge */}
      <div className={cn(
        'absolute left-0 top-4 bottom-4 w-1 rounded-full',
        statusColors[patient.riskLevel]
      )} />

      <div className="flex items-start gap-4 pl-3">
        {/* Avatar */}
        <div className="relative shrink-0">
          {patient.avatar ? (
            <img
              src={patient.avatar}
              alt={patient.name}
              className="w-12 h-12 rounded-full object-cover ring-2 ring-stone-100"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-stone-100 to-stone-200 flex items-center justify-center">
              <span className="text-stone-600 font-semibold text-sm">{initials}</span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          {/* Name & Demographics */}
          <div className="flex items-baseline gap-2 mb-1">
            <h3 className="font-semibold text-stone-900 truncate">{patient.name}</h3>
            <span className="text-xs text-stone-400 font-medium shrink-0">
              {patient.sex} · {patient.age}y
            </span>
          </div>

          {/* Symptom note */}
          <p className="text-sm text-stone-500 leading-relaxed line-clamp-2">
            {patient.symptom}
          </p>
        </div>

        {/* Arrow indicator on hover */}
        <div className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 self-center">
          <svg className="w-5 h-5 text-stone-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </motion.div>
  )
}
