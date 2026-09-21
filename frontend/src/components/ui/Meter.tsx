import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'

export type Severity = 'good' | 'warning' | 'critical'

export function severityFor(pct: number): Severity {
  if (pct >= 80) return 'good'
  if (pct >= 50) return 'warning'
  return 'critical'
}

const SEVERITY_COLORS: Record<Severity, { fill: string; track: string; text: string }> = {
  good: { fill: 'bg-success-600', track: 'bg-success-100', text: 'text-success-700' },
  warning: { fill: 'bg-warning-600', track: 'bg-warning-100', text: 'text-warning-700' },
  critical: { fill: 'bg-danger-600', track: 'bg-danger-100', text: 'text-danger-700' },
}

const SEVERITY_ICON: Record<Severity, React.ReactNode> = {
  good: <CheckCircle2 size={14} />,
  warning: <AlertTriangle size={14} />,
  critical: <XCircle size={14} />,
}

/** A single-ratio-against-a-limit meter: fill carries severity, the
 * unfilled track is a lighter step of the same ramp so state reads across
 * the whole bar (dataviz skill: marks-and-anatomy.md). */
export function Meter({ label, pct }: { label: string; pct: number }) {
  const severity = severityFor(pct)
  const colors = SEVERITY_COLORS[severity]
  return (
    <div className="py-1">
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-slate-600">{label}</span>
        <span className={`font-semibold tabular-nums ${colors.text}`}>{Math.round(pct)}%</span>
      </div>
      <div className={`h-1.5 w-full overflow-hidden rounded-full ${colors.track}`}>
        <div
          className={`h-full rounded-full ${colors.fill} transition-[width] duration-500 ease-out`}
          style={{ width: `${Math.max(0, Math.min(100, pct))}%` }}
        />
      </div>
    </div>
  )
}

/** The hero figure for a dashboard's headline number — score paired with
 * an icon + short label, never color alone (palette.md mitigation for
 * sub-3:1-contrast status hues). */
export function ScoreHero({ score, oneLine }: { score: number; oneLine?: string }) {
  const severity = severityFor(score)
  const colors = SEVERITY_COLORS[severity]
  const statusLabel = severity === 'good' ? 'Strong match' : severity === 'warning' ? 'Needs work' : 'Weak match'
  return (
    <div className="flex flex-wrap items-end gap-x-3 gap-y-1.5">
      <div className="flex items-baseline">
        <span className={`text-5xl font-bold ${colors.text}`} style={{ fontVariantNumeric: 'proportional-nums' }}>
          {Math.round(score)}
        </span>
        <span className="ml-1 text-lg font-medium text-slate-400">/100</span>
      </div>
      <div className={`mb-1.5 flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${colors.track} ${colors.text}`}>
        {SEVERITY_ICON[severity]}
        {oneLine ?? statusLabel}
      </div>
    </div>
  )
}
