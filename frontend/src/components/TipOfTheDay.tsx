import { Lightbulb } from 'lucide-react'

const TIPS = [
  'Paste the exact job description before running ATS Analysis — the score is meaningless without one to compare against.',
  'Missing keywords are shown for a reason: only add one if you genuinely have that experience. The AI will refuse to invent it for you.',
  "Run \"Optimize\" after every JD analysis — it rewrites your summary and bullets to emphasize what's already true, not add new claims.",
  'Your name, dates, employers, and certifications are fact-locked — no AI suggestion can silently change them, even if you accept everything.',
  'Export blocked? Click Auto Optimize — it tightens spacing and margins in defined safe steps until your resume fits one page.',
  'Drag sections in the left panel to reorder them — the export always mirrors the exact order you see in the editor.',
  'Keep a Company + Role filled in before exporting — it names your file automatically, so you never mix up which version went where.',
]

function tipForToday(): string {
  const dayIndex = Math.floor(Date.now() / (1000 * 60 * 60 * 24))
  return TIPS[dayIndex % TIPS.length]
}

export function TipOfTheDay() {
  return (
    <div className="flex items-start gap-2.5 rounded-xl border border-brand-100 bg-brand-50/60 px-4 py-3 text-sm text-slate-700">
      <Lightbulb size={16} className="mt-0.5 shrink-0 text-brand-600" />
      <p>
        <span className="font-semibold text-brand-700">Tip:</span> {tipForToday()}
      </p>
    </div>
  )
}
