import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react'
import clsx from 'clsx'

export function Input({ className, ...rest }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={clsx(
        'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-xs',
        'placeholder:text-slate-400 transition-colors',
        'outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100',
        'disabled:bg-slate-50 disabled:text-slate-400',
        className,
      )}
      {...rest}
    />
  )
}

export function Textarea({ className, ...rest }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={clsx(
        'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-xs',
        'placeholder:text-slate-400 transition-colors',
        'outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100',
        'disabled:bg-slate-50 disabled:text-slate-400',
        className,
      )}
      {...rest}
    />
  )
}

export function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <label className={clsx('mb-1.5 block text-xs font-medium text-slate-500', className)}>{children}</label>
}
