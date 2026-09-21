import clsx from 'clsx'

type Tone = 'green' | 'red' | 'amber' | 'slate' | 'blue'

const toneClasses: Record<Tone, string> = {
  green: 'bg-success-100 text-success-700 ring-1 ring-inset ring-success-600/15',
  red: 'bg-danger-100 text-danger-700 ring-1 ring-inset ring-danger-600/15',
  amber: 'bg-warning-100 text-warning-700 ring-1 ring-inset ring-warning-600/15',
  slate: 'bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-500/10',
  blue: 'bg-brand-100 text-brand-700 ring-1 ring-inset ring-brand-600/15',
}

export function Badge({ children, tone = 'slate', className }: { children: React.ReactNode; tone?: Tone; className?: string }) {
  return (
    <span className={clsx('inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium', toneClasses[tone], className)}>
      {children}
    </span>
  )
}
