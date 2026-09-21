import { Check, CheckCircle2, FileText, XCircle } from 'lucide-react'
import { Badge } from './ui/Badge'
import { Meter, ScoreHero, severityFor } from './ui/Meter'
import type { AtsScoreBreakdown } from '../types/ats'

interface Props {
  score: AtsScoreBreakdown
  confirmedSkills?: Set<string>
  onToggleConfirmed?: (keyword: string) => void
}

export function AtsScoreCard({ score, confirmedSkills, onToggleConfirmed }: Props) {
  const pageSeverity = score.onePageOk ? 'good' : 'critical'

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-4">
        <div className="mb-2 flex items-center justify-between gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-400">ATS Compatibility</span>
          <div
            className={`flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
              pageSeverity === 'good' ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'
            }`}
          >
            <FileText size={13} />
            {score.pageCount ?? '?'} page{score.pageCount === 1 ? '' : 's'}
            {score.onePageOk ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
          </div>
        </div>
        <ScoreHero score={score.overallScore} />
      </div>

      <div>
        <Meter label="Keyword Match" pct={score.keywordMatchPct} />
        <Meter label="Skills Match" pct={score.skillsMatchPct} />
        <Meter label="Job Title Match" pct={score.titleMatchPct} />
        <Meter label="Experience Relevance" pct={score.experienceRelevancePct} />
        <Meter label="Section Completeness" pct={score.sectionCompletenessPct} />
        <Meter label="Parsing Accuracy" pct={score.parsingAccuracyPct} />
        <Meter label="Formatting Compatibility" pct={score.formattingCompatibilityPct} />
        <Meter label="Readability" pct={score.readabilityPct} />
      </div>

      {score.matchedKeywords.length > 0 && (
        <div>
          <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Matched Keywords</h4>
          <div className="flex flex-wrap gap-1">
            {score.matchedKeywords.map((k) => (
              <Badge key={k} tone="green">
                {k}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {score.missingKeywords.length > 0 && (
        <div>
          <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Missing Keywords</h4>
          <div className="flex flex-wrap gap-1">
            {score.missingKeywords.map((k) => {
              const confirmed = confirmedSkills?.has(k) ?? false
              if (!onToggleConfirmed) {
                return (
                  <Badge key={k} tone="red">
                    {k}
                  </Badge>
                )
              }
              return (
                <button
                  key={k}
                  type="button"
                  onClick={() => onToggleConfirmed(k)}
                  title={confirmed ? 'Confirmed — Optimize may suggest adding this' : 'I genuinely have this skill'}
                  className={`inline-flex cursor-pointer items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium transition-colors ${
                    confirmed
                      ? 'border-success-200 bg-success-100 text-success-700'
                      : 'border-danger-100 bg-danger-50 text-danger-700 hover:border-danger-200'
                  }`}
                >
                  {confirmed && <Check size={11} />}
                  {k}
                </button>
              )
            })}
          </div>
          <p className="mt-1.5 text-[11px] leading-relaxed text-slate-400">
            {onToggleConfirmed
              ? 'Not found in current resume. Tap any you genuinely have — Optimize will then suggest adding only those, for you to review and accept.'
              : 'Not found in current resume — only add if genuinely supported by your experience.'}
          </p>
        </div>
      )}

      {score.relatedKeywords.length > 0 && (
        <div>
          <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Related Keywords</h4>
          <div className="flex flex-wrap gap-1">
            {score.relatedKeywords.map((k) => (
              <Badge key={k} tone="blue">
                {k}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {(score.formattingWarnings.length > 0 || score.sectionWarnings.length > 0) && (
        <div>
          <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Warnings</h4>
          <ul className="space-y-1">
            {[...score.formattingWarnings, ...score.sectionWarnings].map((w, i) => (
              <li key={i} className="rounded-md bg-warning-50 px-2 py-1.5 text-[11px] leading-relaxed text-warning-700">
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {score.suggestions.length > 0 && (
        <div>
          <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Potential Improvements</h4>
          <ul className="space-y-1 text-[11px] leading-relaxed text-slate-600">
            {score.suggestions.map((s, i) => (
              <li key={i} className="flex gap-1.5">
                <span className="mt-0.5 text-slate-300">•</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h4 className="mb-1.5 text-xs font-semibold text-slate-600">Parsing Checklist</h4>
        <div className="grid grid-cols-2 gap-x-3 gap-y-1.5">
          {Object.entries(score.parsingChecklist).map(([key, item]) => (
            <div
              key={key}
              title={item.reason ?? undefined}
              className={`flex items-center gap-1 text-[11px] capitalize ${item.detected ? 'text-success-700' : 'text-danger-700'}`}
            >
              {item.detected ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
              {key}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export { severityFor }
