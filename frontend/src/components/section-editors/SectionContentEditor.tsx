import { CertificationsEditor } from './CertificationsEditor'
import { EducationEditor } from './EducationEditor'
import { ExperienceEditor } from './ExperienceEditor'
import { GenericSectionEditor } from './GenericSectionEditor'
import { ProjectsEditor } from './ProjectsEditor'
import { SkillsEditor } from './SkillsEditor'
import { SummaryEditor } from './SummaryEditor'
import type { ResumeSection, SectionContent } from '../../types/resume'

export function SectionContentEditor({ section, onChange }: { section: ResumeSection; onChange: (c: SectionContent) => void }) {
  switch (section.type) {
    case 'summary':
      return <SummaryEditor content={section.content} onChange={onChange} />
    case 'skills':
      return <SkillsEditor content={section.content} onChange={onChange} />
    case 'experience':
      return <ExperienceEditor content={section.content} onChange={onChange} />
    case 'projects':
      return <ProjectsEditor content={section.content} onChange={onChange} />
    case 'education':
      return <EducationEditor content={section.content} onChange={onChange} />
    case 'certifications':
      return <CertificationsEditor content={section.content} onChange={onChange} />
    default:
      return <GenericSectionEditor content={section.content} onChange={onChange} />
  }
}
