import type { ButtonHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'
import clsx from 'clsx'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
type Size = 'sm' | 'md' | 'lg'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
}

const variantClasses: Record<Variant, string> = {
  // Charcoal, not brand blue — matches the Midnight logo's black identity
  // and reads as a more deliberate, premium primary action than a stock
  // blue button.
  primary:
    'bg-slate-900 text-white shadow-xs hover:bg-slate-800 active:bg-slate-950 disabled:bg-slate-400',
  secondary:
    'bg-white text-slate-700 border border-slate-200 shadow-xs hover:bg-slate-50 hover:border-slate-300 active:bg-slate-100',
  outline:
    'bg-transparent text-brand-700 border border-brand-200 hover:bg-brand-50 active:bg-brand-100',
  ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 active:bg-slate-200',
  danger: 'bg-danger-600 text-white shadow-xs hover:bg-danger-700 active:bg-red-800',
}

const sizeClasses: Record<Size, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-9 px-4 text-sm gap-1.5',
  lg: 'h-11 px-5 text-sm gap-2',
}

export function Button({ variant = 'primary', size = 'md', loading, disabled, className, children, ...rest }: Props) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-1',
        'disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none',
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <Loader2 size={14} className="animate-spin" />}
      {children}
    </button>
  )
}
