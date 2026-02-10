import { type ReactNode } from 'react'
import { motion, type HTMLMotionProps } from 'framer-motion'
import { cn } from '@/lib/utils'

interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode
  hover?: boolean
  className?: string
}

export function GlassCard({ children, hover = false, className, ...props }: GlassCardProps) {
  return (
    <motion.div
      className={cn('glass-card p-6', className)}
      whileHover={
        hover
          ? {
              y: -8,
              boxShadow: '0 20px 60px rgba(79, 156, 249, 0.25)',
            }
          : undefined
      }
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      {...props}
    >
      {children}
    </motion.div>
  )
}
