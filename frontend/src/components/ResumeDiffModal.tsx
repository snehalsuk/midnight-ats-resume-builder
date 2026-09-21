import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { diffResumes, type ResumeDiffResult } from '../services/resumeApi'
import { getApiErrorMessage } from '../services/apiClient'

function diffLineClass(line: string): string {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'bg-green-50 text-green-800'
  if (line.startsWith('-') && !line.startsWith('---')) return 'bg-red-50 text-red-800'
  if (line.startsWith('@@')) return 'bg-slate-100 text-slate-500'
  return 'text-slate-500'
}

export function ResumeDiffModal({ masterId, versionId, onClose }: { masterId: number; versionId: number; onClose: () => void }) {
  const [diff, setDiff] = useState<ResumeDiffResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    diffResumes(masterId, versionId).then(setDiff).catch((err) => setError(getApiErrorMessage(err)))
  }, [masterId, versionId])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex max-h-[85vh] w-full max-w-3xl flex-col rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h3 className="text-sm font-semibold text-slate-800">Master Resume vs. Tailored Version</h3>
          <button onClick={onClose} className="rounded p-1 text-slate-400 hover:bg-slate-100">
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 text-sm">
          {error && <p className="text-red-600">{error}</p>}
          {!diff && !error && <p className="text-slate-400">Loading comparison…</p>}
          {diff && (
            <div className="space-y-4">
              {diff.reordered && (
                <p className="rounded-md bg-amber-50 p-2 text-xs text-amber-700">Section order differs between the two resumes.</p>
              )}

              {diff.added.length > 0 && (
                <div>
                  <h4 className="mb-1 text-xs font-semibold text-green-700">Added Sections</h4>
                  <ul className="list-inside list-disc text-xs text-green-700">
                    {diff.added.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {diff.removed.length > 0 && (
                <div>
                  <h4 className="mb-1 text-xs font-semibold text-red-700">Removed Sections</h4>
                  <ul className="list-inside list-disc text-xs text-red-700">
                    {diff.removed.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {diff.modified.map((m) => (
                <div key={m.section}>
                  <h4 className="mb-1 text-xs font-semibold text-slate-700">Modified — {m.section}</h4>
                  <pre className="overflow-x-auto rounded-md bg-slate-50 p-2 text-[11px] leading-5">
                    {m.diffLines.map((line, i) => (
                      <div key={i} className={diffLineClass(line)}>
                        {line}
                      </div>
                    ))}
                  </pre>
                </div>
              ))}

              {diff.unchanged.length > 0 && (
                <div>
                  <h4 className="mb-1 text-xs font-semibold text-slate-500">Unchanged Sections</h4>
                  <p className="text-xs text-slate-400">{diff.unchanged.join(', ')}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
