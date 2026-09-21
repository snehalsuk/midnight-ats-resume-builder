import { useEffect, useState } from 'react'
import { BarChart3, Sparkles } from 'lucide-react'
import { AiChangeReview } from './AiChangeReview'
import { AtsScoreCard } from './AtsScoreCard'
import { Button } from './ui/Button'
import { EmptyState } from './ui/EmptyState'
import { Textarea } from './ui/Input'
import {
  acceptAiChange,
  acceptAllAiChanges,
  analyzeAts,
  analyzeJobDescription,
  listAiChanges,
  listJobDescriptions,
  optimizeResume,
  rejectAiChange,
} from '../services/atsApi'
import { getApiErrorMessage } from '../services/apiClient'
import { toastError, toastSuccess } from '../store/toastStore'
import { useResumeEditorStore } from '../store/resumeEditorStore'
import type { AiChange, JobDescription } from '../types/ats'

export function AtsPanel() {
  const { resume, atsResult, setAtsResult, activeJobDescriptionId, setActiveJobDescriptionId, load } = useResumeEditorStore()
  const [jdText, setJdText] = useState('')
  const [jdList, setJdList] = useState<JobDescription[]>([])
  const [aiChanges, setAiChanges] = useState<AiChange[]>([])
  const [busy, setBusy] = useState<string | null>(null)
  const [confirmedSkills, setConfirmedSkills] = useState<Set<string>>(new Set())

  function handleToggleConfirmed(keyword: string) {
    setConfirmedSkills((prev) => {
      const next = new Set(prev)
      if (next.has(keyword)) next.delete(keyword)
      else next.add(keyword)
      return next
    })
  }

  useEffect(() => {
    listJobDescriptions().then(setJdList).catch(() => {})
  }, [])

  useEffect(() => {
    if (resume) listAiChanges(resume.id).then(setAiChanges).catch(() => {})
  }, [resume?.id])

  if (!resume) return null

  async function run<T>(key: string, fn: () => Promise<T>): Promise<T | undefined> {
    setBusy(key)
    try {
      return await fn()
    } catch (err) {
      toastError('Something went wrong', getApiErrorMessage(err))
      return undefined
    } finally {
      setBusy(null)
    }
  }

  async function handleAnalyzeJd() {
    if (!jdText.trim()) return
    const jd = await run('jd', () => analyzeJobDescription(jdText, resume!.company ?? undefined))
    if (jd) {
      setJdList((prev) => [jd, ...prev])
      setActiveJobDescriptionId(jd.id)
      toastSuccess('Job description analyzed', jd.parsed.jobTitle || jd.company || undefined)
    }
  }

  async function handleRunAts() {
    const score = await run('ats', () => analyzeAts(resume!.id, activeJobDescriptionId ?? undefined))
    if (score) setAtsResult(score)
  }

  async function handleOptimize() {
    if (!activeJobDescriptionId) {
      toastError('Select a job description first', 'Analyze a JD above, then Optimize.')
      return
    }
    const result = await run('optimize', () =>
      optimizeResume(resume!.id, activeJobDescriptionId, Array.from(confirmedSkills)),
    )
    if (result) {
      setAiChanges(await listAiChanges(resume!.id))
      const addedSkillCount = result.skillAdditions.length
      toastSuccess(
        'Optimization suggestions ready',
        addedSkillCount > 0
          ? `Includes ${addedSkillCount} confirmed skill${addedSkillCount === 1 ? '' : 's'} to review below.`
          : 'Review the changes below before accepting.',
      )
    }
  }

  // Applying a change rewrites resume content, which can change what's
  // matched/missing — re-score immediately so the panel never shows a
  // keyword as "missing" after the resume was just updated to include it
  // (previously required a manual "Run ATS Analysis" click to notice).
  async function rescoreIfPossible() {
    if (!atsResult) return // nothing was scored yet, nothing to refresh
    const score = await analyzeAts(resume!.id, activeJobDescriptionId ?? undefined)
    setAtsResult(score)
  }

  async function handleAccept(id: number) {
    await run('accept', async () => {
      await acceptAiChange(resume!.id, id)
      setAiChanges(await listAiChanges(resume!.id))
      await load(resume!.id)
      await rescoreIfPossible()
    })
  }

  async function handleReject(id: number) {
    await run('reject', async () => {
      await rejectAiChange(resume!.id, id)
      setAiChanges(await listAiChanges(resume!.id))
    })
  }

  async function handleAcceptAll() {
    await run('acceptAll', async () => {
      await acceptAllAiChanges(resume!.id)
      setAiChanges(await listAiChanges(resume!.id))
      await load(resume!.id)
      await rescoreIfPossible()
      toastSuccess('Changes applied', atsResult ? 'ATS score updated to reflect the changes.' : undefined)
    })
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Job Description</h3>
        {jdList.length > 0 && (
          <select
            className="mb-2 w-full rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 shadow-xs outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
            value={activeJobDescriptionId ?? ''}
            onChange={(e) => setActiveJobDescriptionId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">— Select a saved job description —</option>
            {jdList.map((jd) => (
              <option key={jd.id} value={jd.id}>
                {jd.parsed.jobTitle || jd.company || `JD #${jd.id}`}
              </option>
            ))}
          </select>
        )}
        <Textarea rows={4} placeholder="Paste the job description here..." value={jdText} onChange={(e) => setJdText(e.target.value)} />
        <Button size="sm" className="mt-2 w-full justify-center" onClick={handleAnalyzeJd} loading={busy === 'jd'}>
          Analyze JD
        </Button>
      </div>

      <div className="flex gap-2">
        <Button size="sm" variant="secondary" className="flex-1 justify-center" onClick={handleRunAts} loading={busy === 'ats'}>
          Run ATS Analysis
        </Button>
        <Button
          size="sm"
          variant="secondary"
          className="flex-1 justify-center"
          onClick={handleOptimize}
          loading={busy === 'optimize'}
          disabled={!activeJobDescriptionId}
        >
          <Sparkles size={14} /> Optimize
        </Button>
      </div>

      <AiChangeReview changes={aiChanges} onAccept={handleAccept} onReject={handleReject} onAcceptAll={handleAcceptAll} />

      {atsResult ? (
        <AtsScoreCard score={atsResult} confirmedSkills={confirmedSkills} onToggleConfirmed={handleToggleConfirmed} />
      ) : (
        <EmptyState
          icon={<BarChart3 size={20} />}
          title="No score yet"
          description='Click "Run ATS Analysis" to see your compatibility score and keyword gaps.'
        />
      )}
    </div>
  )
}
