import { create } from 'zustand'
import { getResume, updateResume } from '../services/resumeApi'
import type { AtsScoreBreakdown } from '../types/ats'
import type { PersonalInfo, Resume, ResumeSection, SectionType } from '../types/resume'
import { DEFAULT_SECTION_TITLES, defaultContentFor } from '../types/resume'

const AUTOSAVE_DEBOUNCE_MS = 1200

interface DeletedSectionSnapshot {
  section: ResumeSection
}

interface ResumeEditorState {
  resume: Resume | null
  loading: boolean
  saving: boolean
  dirty: boolean
  lastDeleted: DeletedSectionSnapshot | null
  atsResult: AtsScoreBreakdown | null
  activeJobDescriptionId: number | null

  load: (id: number) => Promise<void>
  setAtsResult: (result: AtsScoreBreakdown | null) => void
  setActiveJobDescriptionId: (id: number | null) => void

  updatePersonalInfo: (patch: Partial<PersonalInfo>) => void
  updateMeta: (patch: { name?: string; company?: string | null; roleTitle?: string | null; templateId?: string }) => void

  addSection: (type: SectionType, title?: string) => void
  deleteSection: (sectionId: string) => void
  undoDeleteSection: () => void
  duplicateSection: (sectionId: string) => void
  renameSection: (sectionId: string, title: string) => void
  toggleSectionVisibility: (sectionId: string) => void
  reorderSections: (orderedIds: string[]) => void
  updateSectionContent: (sectionId: string, content: ResumeSection['content']) => void

  saveNow: () => Promise<void>
}

let autosaveTimer: ReturnType<typeof setTimeout> | null = null

export const useResumeEditorStore = create<ResumeEditorState>((set, get) => {
  function scheduleAutosave() {
    if (autosaveTimer) clearTimeout(autosaveTimer)
    autosaveTimer = setTimeout(() => {
      get().saveNow()
    }, AUTOSAVE_DEBOUNCE_MS)
  }

  function mutateResume(mutator: (resume: Resume) => Resume) {
    const current = get().resume
    if (!current) return
    const next = mutator(current)
    set({ resume: next, dirty: true })
    scheduleAutosave()
  }

  return {
    resume: null,
    loading: false,
    saving: false,
    dirty: false,
    lastDeleted: null,
    atsResult: null,
    activeJobDescriptionId: null,

    load: async (id) => {
      set({ loading: true })
      try {
        const resume = await getResume(id)
        set({ resume, loading: false, dirty: false, atsResult: null })
      } catch (err) {
        set({ loading: false })
        throw err
      }
    },

    setAtsResult: (result) => set({ atsResult: result }),
    setActiveJobDescriptionId: (id) => set({ activeJobDescriptionId: id }),

    updatePersonalInfo: (patch) => {
      mutateResume((r) => ({ ...r, personalInfo: { ...r.personalInfo, ...patch } }))
    },

    updateMeta: (patch) => {
      mutateResume((r) => ({ ...r, ...patch }))
    },

    addSection: (type, title) => {
      mutateResume((r) => {
        const id = `${type}-${Date.now().toString(36)}`
        const newSection: ResumeSection = {
          id,
          type,
          title: title ?? DEFAULT_SECTION_TITLES[type],
          order: r.sections.length + 1,
          visible: true,
          content: defaultContentFor(type),
        }
        return { ...r, sections: [...r.sections, newSection] }
      })
    },

    deleteSection: (sectionId) => {
      const current = get().resume
      if (!current) return
      const section = current.sections.find((s) => s.id === sectionId)
      if (!section) return
      set({ lastDeleted: { section } })
      mutateResume((r) => ({ ...r, sections: r.sections.filter((s) => s.id !== sectionId) }))
    },

    undoDeleteSection: () => {
      const snapshot = get().lastDeleted
      if (!snapshot) return
      mutateResume((r) => ({ ...r, sections: [...r.sections, snapshot.section] }))
      set({ lastDeleted: null })
    },

    duplicateSection: (sectionId) => {
      mutateResume((r) => {
        const section = r.sections.find((s) => s.id === sectionId)
        if (!section) return r
        const copy: ResumeSection = {
          ...section,
          id: `${section.type}-${Date.now().toString(36)}`,
          title: `${section.title} (copy)`,
          order: r.sections.length + 1,
        }
        return { ...r, sections: [...r.sections, copy] }
      })
    },

    renameSection: (sectionId, title) => {
      mutateResume((r) => ({
        ...r,
        sections: r.sections.map((s) => (s.id === sectionId ? { ...s, title } : s)),
      }))
    },

    toggleSectionVisibility: (sectionId) => {
      mutateResume((r) => ({
        ...r,
        sections: r.sections.map((s) => (s.id === sectionId ? { ...s, visible: !s.visible } : s)),
      }))
    },

    reorderSections: (orderedIds) => {
      mutateResume((r) => {
        const byId = new Map(r.sections.map((s) => [s.id, s]))
        const reordered = orderedIds
          .map((id, idx) => {
            const s = byId.get(id)
            return s ? { ...s, order: idx + 1 } : null
          })
          .filter((s): s is ResumeSection => s !== null)
        return { ...r, sections: reordered }
      })
    },

    updateSectionContent: (sectionId, content) => {
      mutateResume((r) => ({
        ...r,
        sections: r.sections.map((s) => (s.id === sectionId ? { ...s, content } : s)),
      }))
    },

    saveNow: async () => {
      const current = get().resume
      if (!current) return
      set({ saving: true })
      try {
        const saved = await updateResume(current.id, {
          name: current.name,
          templateId: current.templateId,
          personalInfo: current.personalInfo,
          sections: current.sections,
          company: current.company,
          roleTitle: current.roleTitle,
        })
        set({ resume: saved, saving: false, dirty: false })
      } catch (err) {
        set({ saving: false })
        throw err
      }
    },
  }
})
