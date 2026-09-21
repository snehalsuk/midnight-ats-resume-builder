import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Download, FileText, Layers, ListChecks, PenSquare, Save, Palette } from 'lucide-react'
import { AtsPanel } from '../components/AtsPanel'
import { PersonalInfoEditor } from '../components/PersonalInfoEditor'
import { PreviewPane } from '../components/PreviewPane'
import { SectionContentEditor } from '../components/section-editors/SectionContentEditor'
import { SectionList } from '../components/SectionList'
import { TemplatePickerModal } from '../components/TemplatePickerModal'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Skeleton } from '../components/ui/Skeleton'
import { getApiErrorMessage } from '../services/apiClient'
import { downloadBase64File, exportDocx, exportPdf } from '../services/resumeApi'
import { toastError, toastSuccess } from '../store/toastStore'
import { useResumeEditorStore } from '../store/resumeEditorStore'

const MOBILE_TABS = [
  { key: 'structure', label: 'Structure', icon: Layers },
  { key: 'edit', label: 'Edit', icon: PenSquare },
  { key: 'preview', label: 'Preview', icon: FileText },
  { key: 'ats', label: 'ATS', icon: ListChecks },
] as const
type MobileTab = (typeof MOBILE_TABS)[number]['key']

export function ResumeEditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { resume, loading, saving, load, updatePersonalInfo, updateMeta, updateSectionContent } = useResumeEditorStore()
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null)
  const [centerTab, setCenterTab] = useState<'edit' | 'preview'>('edit')
  const [mobileTab, setMobileTab] = useState<MobileTab>('edit')
  const [exporting, setExporting] = useState<string | null>(null)
  const [showTemplatePicker, setShowTemplatePicker] = useState(false)

  useEffect(() => {
    if (id) load(Number(id)).catch(() => navigate('/dashboard'))
  }, [id])

  if (loading || !resume) {
    return (
      <div className="grid h-[calc(100vh-56px)] grid-cols-[240px_1fr_320px] gap-px bg-slate-200 p-px">
        <Skeleton className="rounded-none" />
        <Skeleton className="rounded-none" />
        <Skeleton className="rounded-none" />
      </div>
    )
  }

  const sections = [...resume.sections].sort((a, b) => a.order - b.order)
  const selectedSection = sections.find((s) => s.id === selectedSectionId) ?? sections[0]

  async function handleExport(format: 'pdf' | 'docx') {
    setExporting(format)
    try {
      const result = format === 'pdf' ? await exportPdf(resume!.id) : await exportDocx(resume!.id)
      downloadBase64File(
        result.filename,
        result.contentBase64,
        format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      )
      toastSuccess('Export ready', result.filename)
    } catch (err) {
      toastError('Export failed', getApiErrorMessage(err))
    } finally {
      setExporting(null)
    }
  }

  const editPanel = (
    <div className="thin-scroll h-full overflow-y-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardBody>
          <PersonalInfoEditor info={resume.personalInfo} onChange={updatePersonalInfo} />
        </CardBody>
      </Card>

      {selectedSection && (
        <Card>
          <CardHeader>
            <CardTitle>{selectedSection.title}</CardTitle>
          </CardHeader>
          <CardBody>
            <SectionContentEditor section={selectedSection} onChange={(content) => updateSectionContent(selectedSection.id, content)} />
          </CardBody>
        </Card>
      )}
    </div>
  )

  const structurePanel = (
    <div className="thin-scroll h-full overflow-y-auto p-3">
      <SectionList selectedId={selectedSection?.id ?? null} onSelect={setSelectedSectionId} />
    </div>
  )

  const previewPanel = <PreviewPane resume={resume} />

  const atsPanel = (
    <div className="thin-scroll h-full overflow-y-auto p-3">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">ATS Analysis</h3>
      <AtsPanel />
    </div>
  )

  return (
    <div className="flex h-[calc(100vh-56px)] flex-col">
      {/* Top bar */}
      <div className="flex flex-wrap items-center gap-2.5 border-b border-slate-200 bg-white px-4 py-2.5 sm:gap-3">
        <span className="max-w-[140px] truncate text-sm font-semibold text-slate-800 sm:max-w-none">{resume.name}</span>
        <div className="hidden items-center gap-1.5 sm:flex">
          <span className="text-xs text-slate-400">Company:</span>
          <Input className="w-36" value={resume.company ?? ''} onChange={(e) => updateMeta({ company: e.target.value })} placeholder="Barclays" />
        </div>
        <div className="hidden items-center gap-1.5 md:flex">
          <span className="text-xs text-slate-400">Role:</span>
          <Input
            className="w-52"
            value={resume.roleTitle ?? ''}
            onChange={(e) => updateMeta({ roleTitle: e.target.value })}
            placeholder="Java Full Stack Developer"
          />
        </div>
        <span className="hidden items-center gap-1 text-xs text-slate-400 lg:flex">
          <Save size={12} className={saving ? 'animate-pulse' : ''} />
          {saving ? 'Saving…' : 'Saved'}
        </span>
        <div className="ml-auto flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => setShowTemplatePicker(true)}>
            <Palette size={14} /> <span className="hidden sm:inline">Template</span>
          </Button>
          <Button variant="secondary" size="sm" onClick={() => handleExport('docx')} disabled={exporting !== null} loading={exporting === 'docx'}>
            <FileText size={14} /> <span className="hidden sm:inline">Export DOCX</span>
          </Button>
          <Button size="sm" onClick={() => handleExport('pdf')} disabled={exporting !== null} loading={exporting === 'pdf'}>
            <Download size={14} /> <span className="hidden sm:inline">Export PDF</span>
          </Button>
        </div>
      </div>

      {/* Desktop: 3-panel layout */}
      <div className="hidden flex-1 grid-cols-[240px_1fr_320px] overflow-hidden lg:grid">
        <div className="overflow-hidden border-r border-slate-200 bg-white">{structurePanel}</div>

        <div className="flex flex-col overflow-hidden bg-slate-50">
          <div className="flex gap-1 border-b border-slate-200 bg-white px-3 pt-2">
            {(['edit', 'preview'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setCenterTab(tab)}
                className={`rounded-t-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                  centerTab === tab ? 'border border-b-0 border-slate-200 bg-slate-50 text-brand-600' : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-hidden">{centerTab === 'preview' ? previewPanel : editPanel}</div>
        </div>

        <div className="overflow-hidden border-l border-slate-200 bg-white">{atsPanel}</div>
      </div>

      {/* Mobile / tablet: tabbed single-column layout */}
      <div className="flex flex-1 flex-col overflow-hidden lg:hidden">
        <div className="flex-1 overflow-hidden bg-slate-50">
          {mobileTab === 'structure' && <div className="h-full bg-white">{structurePanel}</div>}
          {mobileTab === 'edit' && editPanel}
          {mobileTab === 'preview' && previewPanel}
          {mobileTab === 'ats' && <div className="h-full bg-white">{atsPanel}</div>}
        </div>
        <nav className="grid grid-cols-4 border-t border-slate-200 bg-white">
          {MOBILE_TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setMobileTab(key)}
              className={`flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium ${
                mobileTab === key ? 'text-brand-600' : 'text-slate-400'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {showTemplatePicker && (
        <TemplatePickerModal
          currentTemplateId={resume.templateId}
          onClose={() => setShowTemplatePicker(false)}
          onSelect={(templateId) => {
            updateMeta({ templateId })
            setShowTemplatePicker(false)
          }}
        />
      )}
    </div>
  )
}
