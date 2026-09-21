import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FilePlus2, FileText, FileUp, GitCompare, LayoutGrid, Plus, Sparkles } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { EmptyState } from '../components/ui/EmptyState'
import { Skeleton } from '../components/ui/Skeleton'
import { ScoreHero } from '../components/ui/Meter'
import { PromoBanner } from '../components/PromoBanner'
import { ResumeDiffModal } from '../components/ResumeDiffModal'
import { TemplatePickerModal } from '../components/TemplatePickerModal'
import { TipOfTheDay } from '../components/TipOfTheDay'
import { getApiErrorMessage } from '../services/apiClient'
import { createResume, duplicateResume, listResumes, uploadResume } from '../services/resumeApi'
import { toastError, toastSuccess } from '../store/toastStore'
import type { Resume } from '../types/resume'

function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <Skeleton className="h-40 md:col-span-2" />
      <Skeleton className="h-40" />
      <Skeleton className="h-32 md:col-span-3" />
    </div>
  )
}

export function DashboardPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const [compareVersionId, setCompareVersionId] = useState<number | null>(null)
  const [showTemplatePicker, setShowTemplatePicker] = useState(false)
  const [creatingFromTemplate, setCreatingFromTemplate] = useState(false)

  useEffect(() => {
    refresh()
  }, [])

  function refresh() {
    setLoading(true)
    listResumes()
      .then(setResumes)
      .finally(() => setLoading(false))
  }

  async function handleFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const resume = await uploadResume(file)
      toastSuccess('Resume parsed', `Master Resume created from ${file.name}.`)
      navigate(`/editor/${resume.id}`)
    } catch (err) {
      toastError('Upload failed', getApiErrorMessage(err))
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleStartFromScratch(templateId: string) {
    setCreatingFromTemplate(true)
    try {
      const resume = await createResume({ name: 'Master Resume', templateId })
      toastSuccess('Resume created', 'Blank Master Resume ready to edit.')
      navigate(`/editor/${resume.id}`)
    } catch (err) {
      toastError('Could not create resume', getApiErrorMessage(err))
    } finally {
      setCreatingFromTemplate(false)
      setShowTemplatePicker(false)
    }
  }

  async function handleTailorFrom(resume: Resume) {
    try {
      const version = await duplicateResume(resume.id)
      navigate(`/editor/${version.id}`)
    } catch (err) {
      toastError('Could not create version', getApiErrorMessage(err))
    }
  }

  const master = resumes.find((r) => r.kind === 'MASTER')
  const versions = resumes.filter((r) => r.kind === 'VERSION')

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <PromoBanner />

      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="mt-0.5 text-sm text-slate-500">Your master resume and job-tailored versions.</p>
        </div>
        <div className="flex gap-2">
          <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFileSelected} />
          <Button variant="outline" onClick={() => setShowTemplatePicker(true)}>
            <FilePlus2 size={16} /> Start from Scratch
          </Button>
          <Button variant="secondary" onClick={() => fileInputRef.current?.click()} loading={uploading}>
            <FileUp size={16} /> {uploading ? 'Uploading…' : 'Upload Resume'}
          </Button>
        </div>
      </div>

      {!loading && master && (
        <div className="mb-6">
          <TipOfTheDay />
        </div>
      )}

      {loading ? (
        <DashboardSkeleton />
      ) : !master ? (
        <Card>
          <EmptyState
            icon={<FileUp size={24} />}
            title="Upload your resume to get started"
            description="PDF, DOCX, or TXT — parsed deterministically into a structured Master Resume that every tailored version is generated from."
            action={
              <div className="flex flex-wrap justify-center gap-2">
                <Button loading={uploading} onClick={() => fileInputRef.current?.click()}>
                  <FileUp size={16} /> Upload Resume
                </Button>
                <Button variant="outline" onClick={() => setShowTemplatePicker(true)}>
                  <FilePlus2 size={16} /> Start from Scratch
                </Button>
              </div>
            }
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card className="md:col-span-2">
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Master Resume</CardTitle>
              <Button size="sm" onClick={() => navigate(`/editor/${master.id}`)}>
                Open
              </Button>
            </CardHeader>
            <CardBody>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <p className="text-base font-semibold text-slate-900">{master.personalInfo.name}</p>
                  <p className="text-sm text-slate-500">{master.personalInfo.title}</p>
                  <Button variant="outline" size="sm" className="mt-4" onClick={() => handleTailorFrom(master)}>
                    <Plus size={14} /> Create Tailored Version
                  </Button>
                </div>
                {master.lastAtsScore != null && (
                  <div className="shrink-0 sm:text-right">
                    <ScoreHero score={master.lastAtsScore} />
                  </div>
                )}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardBody className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-slate-500">
                  <LayoutGrid size={14} /> Tailored versions
                </span>
                <span className="font-semibold text-slate-800">{versions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-slate-500">
                  <FileText size={14} /> Page count
                </span>
                <span className="font-semibold text-slate-800">{master.pageCount ?? '—'}</span>
              </div>
            </CardBody>
          </Card>

          <Card className="md:col-span-3">
            <CardHeader>
              <CardTitle>Tailored Resume Versions</CardTitle>
            </CardHeader>
            <CardBody>
              {versions.length === 0 ? (
                <EmptyState
                  icon={<Sparkles size={22} />}
                  title="No tailored versions yet"
                  description='Create one from your Master Resume above, then run "Optimize Resume" against a job description in the editor.'
                />
              ) : (
                <div className="divide-y divide-slate-100">
                  {versions.map((v) => (
                    <div key={v.id} className="flex items-center justify-between py-3 text-sm">
                      <div>
                        <span className="font-medium text-slate-800">{v.company ?? v.name}</span>
                        {v.roleTitle && <span className="ml-2 text-slate-500">{v.roleTitle}</span>}
                      </div>
                      <div className="flex items-center gap-2">
                        {v.lastAtsScore != null && (
                          <span className="text-xs font-semibold text-slate-500">{Math.round(v.lastAtsScore)}/100</span>
                        )}
                        <Button size="sm" variant="ghost" onClick={() => setCompareVersionId(v.id)}>
                          <GitCompare size={13} /> Compare
                        </Button>
                        <Button size="sm" variant="secondary" onClick={() => navigate(`/editor/${v.id}`)}>
                          Open
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      )}

      {compareVersionId && master && (
        <ResumeDiffModal masterId={master.id} versionId={compareVersionId} onClose={() => setCompareVersionId(null)} />
      )}

      {showTemplatePicker && (
        <TemplatePickerModal
          onSelect={handleStartFromScratch}
          onClose={() => setShowTemplatePicker(false)}
          submitting={creatingFromTemplate}
        />
      )}
    </div>
  )
}
