import { useState } from 'react'
import { Lock, Sparkles, Target, X, Zap } from 'lucide-react'

const DISMISS_KEY = 'promoBannerDismissed'

const FEATURES = [
  { icon: Zap, label: '100% Free' },
  { icon: Target, label: 'Real ATS Scoring' },
  { icon: Lock, label: 'Fact-Locked AI' },
  { icon: Sparkles, label: 'One-Page, Every Time' },
]

export function PromoBanner() {
  const [dismissed, setDismissed] = useState(() => localStorage.getItem(DISMISS_KEY) === 'true')

  if (dismissed) return null

  function dismiss() {
    localStorage.setItem(DISMISS_KEY, 'true')
    setDismissed(true)
  }

  return (
    <div className="relative mb-6 overflow-hidden rounded-xl bg-gradient-to-br from-slate-900 via-brand-900 to-brand-700 px-5 py-5 text-white shadow-card sm:px-7 sm:py-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_85%_20%,rgba(96,165,250,0.35),transparent_55%)]" />
      <button
        onClick={dismiss}
        aria-label="Dismiss"
        className="absolute right-3 top-3 rounded-full p-1 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
      >
        <X size={16} />
      </button>

      <div className="relative flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-lg font-bold leading-snug sm:text-xl">
            100% Free — build an ATS-optimized resume that never fabricates a skill.
          </p>
          <p className="mt-1 text-sm text-white/70">
            Real keyword matching, transparent scoring, and AI tailoring that's fact-locked to what you've
            actually done.
          </p>
        </div>
      </div>

      <div className="relative mt-4 flex flex-wrap gap-2">
        {FEATURES.map(({ icon: Icon, label }) => (
          <span
            key={label}
            className="flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-medium backdrop-blur-sm"
          >
            <Icon size={13} />
            {label}
          </span>
        ))}
      </div>
    </div>
  )
}
