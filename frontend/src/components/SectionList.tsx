import { useState } from 'react'
import { DndContext, PointerSensor, closestCenter, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core'
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  Award,
  Briefcase,
  Copy,
  Eye,
  EyeOff,
  FileEdit,
  FolderKanban,
  GraduationCap,
  GripVertical,
  Heart,
  Languages,
  Plus,
  Trash2,
  Undo2,
  Users,
  Wrench,
} from 'lucide-react'
import { Button } from './ui/Button'
import { ConfirmDialog } from './ui/ConfirmDialog'
import { useResumeEditorStore } from '../store/resumeEditorStore'
import { DEFAULT_SECTION_TITLES, SECTION_TYPE_LABELS, type ResumeSection, type SectionType } from '../types/resume'

const ADDABLE_TYPES: SectionType[] = [
  'summary', 'skills', 'experience', 'projects', 'education', 'certifications',
  'achievements', 'publications', 'awards', 'open_source', 'volunteer', 'languages', 'interests', 'custom',
]

const SECTION_ICONS: Record<SectionType, React.ComponentType<{ size?: number }>> = {
  summary: FileEdit,
  skills: Wrench,
  experience: Briefcase,
  projects: FolderKanban,
  education: GraduationCap,
  certifications: Award,
  achievements: Award,
  publications: FileEdit,
  awards: Award,
  open_source: FolderKanban,
  volunteer: Users,
  languages: Languages,
  interests: Heart,
  custom: FileEdit,
}

function SortableRow({ section, onSelect, selected }: { section: ResumeSection; onSelect: () => void; selected: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: section.id })
  const [confirmOpen, setConfirmOpen] = useState(false)
  const { deleteSection, duplicateSection, toggleSectionVisibility } = useResumeEditorStore()
  const Icon = SECTION_ICONS[section.type]

  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.6 : 1 }

  return (
    <div
      ref={setNodeRef}
      style={style}
      onClick={onSelect}
      className={`group flex cursor-pointer items-center gap-2 rounded-lg border px-2 py-2 text-sm transition-colors ${
        selected ? 'border-brand-200 bg-brand-50 text-brand-800' : 'border-transparent text-slate-700 hover:bg-slate-50'
      } ${isDragging ? 'shadow-popover' : ''}`}
    >
      <span {...attributes} {...listeners} className="shrink-0 cursor-grab text-slate-300 hover:text-slate-500 active:cursor-grabbing">
        <GripVertical size={14} />
      </span>
      <Icon size={14} />
      <span className={`flex-1 truncate ${section.visible ? '' : 'text-slate-400 line-through'}`}>{section.title}</span>
      <div className="hidden shrink-0 items-center gap-0.5 group-hover:flex">
        <button
          type="button"
          title={section.visible ? 'Hide' : 'Show'}
          onClick={(e) => {
            e.stopPropagation()
            toggleSectionVisibility(section.id)
          }}
          className="rounded p-1 text-slate-400 hover:bg-slate-200"
        >
          {section.visible ? <Eye size={13} /> : <EyeOff size={13} />}
        </button>
        <button
          type="button"
          title="Duplicate"
          onClick={(e) => {
            e.stopPropagation()
            duplicateSection(section.id)
          }}
          className="rounded p-1 text-slate-400 hover:bg-slate-200"
        >
          <Copy size={13} />
        </button>
        <button
          type="button"
          title="Delete"
          onClick={(e) => {
            e.stopPropagation()
            setConfirmOpen(true)
          }}
          className="rounded p-1 text-slate-400 hover:bg-danger-100 hover:text-danger-600"
        >
          <Trash2 size={13} />
        </button>
      </div>
      <ConfirmDialog
        open={confirmOpen}
        title="Delete this section?"
        description={`"${section.title}" will be removed. You can undo this right after.`}
        onConfirm={() => {
          deleteSection(section.id)
          setConfirmOpen(false)
        }}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  )
}

export function SectionList({ selectedId, onSelect }: { selectedId: string | null; onSelect: (id: string) => void }) {
  const { resume, reorderSections, addSection, lastDeleted, undoDeleteSection } = useResumeEditorStore()
  const [addMenuOpen, setAddMenuOpen] = useState(false)
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }))

  if (!resume) return null
  const sections = [...resume.sections].sort((a, b) => a.order - b.order)

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over || active.id === over.id) return
    const ids = sections.map((s) => s.id)
    const oldIndex = ids.indexOf(String(active.id))
    const newIndex = ids.indexOf(String(over.id))
    const reordered = [...ids]
    reordered.splice(oldIndex, 1)
    reordered.splice(newIndex, 0, String(active.id))
    reorderSections(reordered)
  }

  return (
    <div className="space-y-1">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Resume Structure</h3>
        {lastDeleted && (
          <button onClick={undoDeleteSection} className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:underline">
            <Undo2 size={12} /> Undo
          </button>
        )}
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={sections.map((s) => s.id)} strategy={verticalListSortingStrategy}>
          <div className="space-y-1">
            {sections.map((s) => (
              <SortableRow key={s.id} section={s} selected={selectedId === s.id} onSelect={() => onSelect(s.id)} />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      <div className="relative mt-3">
        <Button variant="secondary" size="sm" className="w-full justify-center" onClick={() => setAddMenuOpen((v) => !v)}>
          <Plus size={14} /> Add Section
        </Button>
        {addMenuOpen && (
          <div className="thin-scroll absolute z-10 mt-1 max-h-64 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-popover">
            {ADDABLE_TYPES.map((type) => (
              <button
                key={type}
                onClick={() => {
                  addSection(type, DEFAULT_SECTION_TITLES[type])
                  setAddMenuOpen(false)
                }}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm text-slate-700 hover:bg-slate-50"
              >
                {SECTION_TYPE_LABELS[type]}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
