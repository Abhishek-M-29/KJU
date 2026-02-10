import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-primary text-white hover:bg-primary-dark': variant === 'primary',
            'bg-white text-stone-700 border border-stone-200 hover:bg-stone-50 hover:border-stone-300': variant === 'secondary',
            'bg-transparent text-stone-600 hover:text-stone-900 hover:bg-stone-100': variant === 'ghost',
            'text-sm px-3 py-1.5 rounded-lg': size === 'sm',
            'text-sm px-4 py-2 rounded-lg': size === 'md',
            'text-base px-6 py-3 rounded-xl': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button }
