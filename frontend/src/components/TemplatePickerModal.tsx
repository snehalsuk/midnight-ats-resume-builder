import { useEffect, useState } from 'react'
import { Check, X } from 'lucide-react'
import { listTemplates } from '../services/resumeApi'
import { getApiErrorMessage } from '../services/apiClient'
import type { TemplateStyle } from '../types/resume'

function TemplateThumbnail({ template }: { template: TemplateStyle }) {
  const accent = template.accentColor
  const isMinimal = template.id === 'minimal'
  const isExecutive = template.id === 'executive'
  const isCompact = template.id === 'compact'
  const isModern = template.id === 'modern'
  const isBold = template.id === 'bold'
  const isAccent = template.id === 'accent'

  if (isBold) {
    return (
      <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
        <div className="space-y-1 px-3 py-2.5" style={{ background: accent }}>
          <div className="h-2 w-2/3 rounded-sm bg-white/90" />
          <div className="h-1 w-2/5 rounded-sm bg-white/60" />
        </div>
        <div className="space-y-2 p-3">
          {[0, 1].map((i) => (
            <div key={i}>
              <div className="h-1 w-1/4 rounded-sm" style={{ background: accent }} />
              <div className="mt-1 space-y-0.5">
                <div className="h-0.5 w-full rounded-sm bg-slate-200" />
                <div className="h-0.5 w-5/6 rounded-sm bg-slate-200" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (isAccent) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-3">
        <div className="h-2 w-2/3 rounded-sm bg-slate-800" />
        <div className="mt-1 h-1 w-1/3 rounded-sm" style={{ background: accent }} />
        <div className="mt-3 space-y-2">
          <div>
            <div className="h-1.5 w-1/4 rounded-sm" style={{ borderLeft: `2px solid ${accent}`, paddingLeft: 2 }} />
            <div className="mt-1 flex flex-wrap gap-1">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-1.5 w-5 rounded-sm" style={{ background: accent }} />
              ))}
            </div>
          </div>
          <div>
            <div className="h-1.5 w-1/3 rounded-sm" style={{ borderLeft: `2px solid ${accent}`, paddingLeft: 2 }} />
            <div className="mt-1 space-y-0.5">
              <div className="h-0.5 w-full rounded-sm bg-slate-200" />
              <div className="h-0.5 w-5/6 rounded-sm bg-slate-200" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className={isModern ? 'text-left' : 'text-center'}>
        <div
          className="mx-auto h-2 w-2/3 rounded-sm"
          style={{ background: isModern ? accent : '#1e293b', marginLeft: isModern ? 0 : undefined }}
        />
        <div className="mx-auto mt-1 h-1 w-1/3 rounded-sm bg-slate-300" style={{ marginLeft: isModern ? 0 : undefined }} />
      </div>
      <div className={`mt-3 space-y-${isCompact ? '1' : '2'}`}>
        {[0, 1, isExecutive ? 2 : null].filter((v) => v !== null).map((_, i) => (
          <div key={i}>
            <div
              className="h-1 w-1/4 rounded-sm"
              style={{ background: isMinimal ? '#94a3b8' : accent, opacity: isExecutive ? 0.85 : 1 }}
            />
            <div className={`mt-1 space-y-0.5 ${isExecutive ? 'rounded-sm bg-slate-50 p-1' : ''}`}>
              <div className="h-0.5 w-full rounded-sm bg-slate-200" />
              <div className="h-0.5 w-5/6 rounded-sm bg-slate-200" />
              {!isCompact && <div className="h-0.5 w-4/6 rounded-sm bg-slate-200" />}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function TemplatePickerModal({
  onSelect,
  onClose,
  currentTemplateId,
  submitting = false,
}: {
  onSelect: (templateId: string) => void
  onClose: () => void
  currentTemplateId?: string
  submitting?: boolean
}) {
  const [templates, setTemplates] = useState<TemplateStyle[]>([])
  const [error, setError] = useState<string | null>(null)
  const [picked, setPicked] = useState<string | null>(currentTemplateId ?? null)

  useEffect(() => {
    listTemplates()
      .then(setTemplates)
      .catch((err) => setError(getApiErrorMessage(err)))
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex max-h-[85vh] w-full max-w-2xl flex-col rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h3 className="text-sm font-semibold text-slate-800">Choose an ATS-friendly template</h3>
          <button onClick={onClose} className="rounded p-1 text-slate-400 hover:bg-slate-100">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {error && <p className="text-sm text-red-600">{error}</p>}
          {!error && templates.length === 0 && <p className="text-sm text-slate-400">Loading templates…</p>}

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {templates.map((t) => {
              const selected = picked === t.id
              return (
                <button
                  key={t.id}
                  onClick={() => setPicked(t.id)}
                  className={`relative rounded-lg border-2 p-2 text-left transition-colors ${
                    selected ? 'border-slate-900' : 'border-transparent hover:border-slate-200'
                  }`}
                >
                  {selected && (
                    <span className="absolute right-2.5 top-2.5 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-white">
                      <Check size={12} />
                    </span>
                  )}
                  <TemplateThumbnail template={t} />
                  <p className="mt-2 text-sm font-semibold text-slate-800">{t.name}</p>
                  <p className="mt-0.5 text-xs leading-snug text-slate-500">{t.description}</p>
                </button>
              )
            })}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-4 py-3">
          <button onClick={onClose} className="rounded-md px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100">
            Cancel
          </button>
          <button
            disabled={!picked || submitting}
            onClick={() => picked && onSelect(picked)}
            className="rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:bg-slate-400"
          >
            {submitting ? 'Creating…' : 'Use this template'}
          </button>
        </div>
      </div>
    </div>
  )
}
