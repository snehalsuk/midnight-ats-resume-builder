import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, Loader2, XCircle } from 'lucide-react'
import { previewResumeDraft } from '../services/resumeApi'
import { getApiErrorMessage } from '../services/apiClient'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { Button } from './ui/Button'
import type { Resume } from '../types/resume'

const MIN_IFRAME_HEIGHT = 1100

export function PreviewPane({ resume }: { resume: Resume }) {
  const debouncedResume = useDebouncedValue(resume, 400)
  const [html, setHtml] = useState<string>('')
  const [pageCount, setPageCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryToken, setRetryToken] = useState(0)
  const [iframeHeight, setIframeHeight] = useState(MIN_IFRAME_HEIGHT)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    previewResumeDraft(debouncedResume.id, debouncedResume.personalInfo, debouncedResume.sections)
      .then((result) => {
        if (!cancelled) {
          setHtml(result.html)
          setPageCount(result.pageCount)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(getApiErrorMessage(err))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [debouncedResume, retryToken])

  function handleIframeLoad() {
    // Size the iframe to its actual content height so the outer pane's
    // scrollbar is the only one in play — without this, tall resumes get
    // their own nested scrollbar inside a fixed-height iframe.
    const doc = iframeRef.current?.contentDocument
    if (doc?.body) {
      setIframeHeight(Math.max(MIN_IFRAME_HEIGHT, doc.body.scrollHeight))
    }
  }

  const onePage = pageCount === 1

  if (error && !html) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 bg-slate-50 px-6 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger-100 text-danger-600">
          <AlertTriangle size={22} />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-800">Couldn't load the preview</p>
          <p className="mt-1 max-w-sm text-sm text-slate-500">{error}</p>
        </div>
        <Button size="sm" variant="secondary" onClick={() => setRetryToken((t) => t + 1)}>
          Try again
        </Button>
      </div>
    )
  }

  return (
    <div className="thin-scroll relative h-full overflow-auto bg-slate-200 p-4 sm:p-6">
      <div className="absolute right-4 top-4 z-10 flex items-center gap-2 sm:right-6 sm:top-6">
        {loading && (
          <div className="flex items-center gap-1.5 rounded-full bg-white/95 px-2.5 py-1 text-xs font-medium text-slate-500 shadow-popover">
            <Loader2 size={12} className="animate-spin" />
            Updating
          </div>
        )}
        {error && (
          <div
            title={error}
            className="flex items-center gap-1.5 rounded-full bg-danger-100 px-2.5 py-1 text-xs font-medium text-danger-700 shadow-popover"
          >
            <AlertTriangle size={13} />
            Update failed
          </div>
        )}
        {pageCount != null && (
          <div
            title="Authoritative page count from the same PDF pipeline Export uses — not a visual estimate."
            className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium shadow-popover ${
              onePage ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'
            }`}
          >
            {onePage ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
            {pageCount} page{pageCount === 1 ? '' : 's'}
          </div>
        )}
      </div>
      <div className="mx-auto max-w-[850px] rounded-sm bg-white shadow-lg">
        <iframe
          ref={iframeRef}
          title="Resume preview"
          srcDoc={html}
          onLoad={handleIframeLoad}
          style={{ height: iframeHeight }}
          className="w-full rounded-sm border-0"
        />
      </div>
    </div>
  )
}
