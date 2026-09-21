import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'
import { useToastStore, type ToastTone } from '../../store/toastStore'

const toneConfig: Record<ToastTone, { icon: React.ReactNode; classes: string }> = {
  success: { icon: <CheckCircle2 size={18} />, classes: 'border-success-100 bg-success-50 text-success-700' },
  error: { icon: <AlertCircle size={18} />, classes: 'border-danger-100 bg-danger-50 text-danger-700' },
  info: { icon: <Info size={18} />, classes: 'border-brand-100 bg-brand-50 text-brand-700' },
}

export function Toaster() {
  const { toasts, dismiss } = useToastStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      {toasts.map((t) => {
        const cfg = toneConfig[t.tone]
        return (
          <div
            key={t.id}
            className={`animate-fade-in flex items-start gap-2.5 rounded-lg border p-3 shadow-popover ${cfg.classes}`}
          >
            <span className="mt-0.5 shrink-0">{cfg.icon}</span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">{t.title}</p>
              {t.description && <p className="mt-0.5 text-xs opacity-90">{t.description}</p>}
            </div>
            <button onClick={() => dismiss(t.id)} className="shrink-0 rounded p-0.5 opacity-60 hover:opacity-100">
              <X size={14} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
