import { useState } from 'react'
import { AlertTriangle, Check, Plus, Sparkles, X } from 'lucide-react'
import { Button } from './ui/Button'
import type { AiChange } from '../types/ats'

interface Props {
  changes: AiChange[]
  onAccept: (id: number) => Promise<void>
  onReject: (id: number) => Promise<void>
  onAcceptAll: () => Promise<void>
}

export function AiChangeReview({ changes, onAccept, onReject, onAcceptAll }: Props) {
  const [busyId, setBusyId] = useState<number | 'all' | null>(null)
  const pending = changes.filter((c) => c.status === 'PENDING')
  if (pending.length === 0) return null

  async function withBusy(id: number | 'all', fn: () => Promise<void>) {
    setBusyId(id)
    try {
      await fn()
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="animate-fade-in rounded-xl border border-brand-100 bg-brand-50/60 p-3.5">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
          <Sparkles size={13} className="text-brand-600" />
          AI Suggested Changes ({pending.length})
        </h4>
        <Button size="sm" variant="secondary" loading={busyId === 'all'} onClick={() => withBusy('all', onAcceptAll)}>
          Accept All
        </Button>
      </div>
      <div className="thin-scroll max-h-80 space-y-2.5 overflow-y-auto">
        {pending.map((change) => (
          <div key={change.id} className="rounded-lg border border-slate-100 bg-white p-3 text-xs shadow-xs">
            {change.blockedLockedField ? (
              <p className="flex items-center gap-1.5 text-danger-600">
                <AlertTriangle size={13} />
                Blocked — this suggestion touches a locked field and was not applied.
              </p>
            ) : change.changeType === 'skill' ? (
              <>
                <div className="flex items-center gap-1.5 leading-relaxed text-slate-800">
                  <Plus size={13} className="text-success-600" />
                  Add <span className="font-semibold">{change.suggestedValue}</span> to{' '}
                  <span className="font-semibold">{change.targetPath.replace(/^skills\./, '')}</span>
                </div>
                <div className="mt-1.5 flex items-center gap-1.5 rounded-md bg-brand-50 px-2 py-1 text-brand-700">
                  <Check size={12} />
                  You confirmed you genuinely have this skill.
                </div>
                <div className="mt-2.5 flex justify-end gap-1.5">
                  <Button size="sm" variant="ghost" loading={busyId === change.id} onClick={() => withBusy(change.id, () => onReject(change.id))}>
                    <X size={13} /> Reject
                  </Button>
                  <Button size="sm" variant="primary" loading={busyId === change.id} onClick={() => withBusy(change.id, () => onAccept(change.id))}>
                    <Check size={13} /> Accept
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="mb-1.5 leading-relaxed text-slate-400 line-through">{change.originalValue || '(empty)'}</div>
                <div className="leading-relaxed text-slate-800">{change.suggestedValue}</div>
                {change.fabricationRisk && (
                  <div className="mt-2 flex items-center gap-1.5 rounded-md bg-warning-50 px-2 py-1 text-warning-700">
                    <AlertTriangle size={12} />
                    Flagged as possible fabrication risk — review carefully.
                  </div>
                )}
                <div className="mt-2.5 flex justify-end gap-1.5">
                  <Button size="sm" variant="ghost" loading={busyId === change.id} onClick={() => withBusy(change.id, () => onReject(change.id))}>
                    <X size={13} /> Reject
                  </Button>
                  <Button size="sm" variant="primary" loading={busyId === change.id} onClick={() => withBusy(change.id, () => onAccept(change.id))}>
                    <Check size={13} /> Accept
                  </Button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
