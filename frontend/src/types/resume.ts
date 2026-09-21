export type SectionType =
  | 'summary'
  | 'skills'
  | 'experience'
  | 'projects'
  | 'education'
  | 'certifications'
  | 'achievements'
  | 'publications'
  | 'awards'
  | 'open_source'
  | 'volunteer'
  | 'languages'
  | 'interests'
  | 'custom'

export interface PersonalInfo {
  name: string
  title: string
  location: string
  email: string
  phone: string
  linkedin: string
  github: string
  portfolio: string
  leetcode: string
  hackerrank: string
}

export interface SkillCategory {
  name: string
  items: string[]
}

export interface ExperienceItem {
  id: string
  title: string
  company: string
  location: string
  startDate: string
  endDate: string
  current: boolean
  bullets: string[]
}

export interface ProjectItem {
  id: string
  name: string
  technologies: string[]
  link: string
  bullets: string[]
}

export interface EducationItem {
  id: string
  degree: string
  institution: string
  location: string
  gpa: string
  year: string
}

export interface CertificationItem {
  id: string
  name: string
  issuer: string
  year: string
  credentialUrl: string
}

export interface SectionContent {
  text?: string
  categories?: SkillCategory[]
  items?: (ExperienceItem | ProjectItem | EducationItem | CertificationItem | string)[]
}

export interface ResumeSection {
  id: string
  type: SectionType
  title: string
  order: number
  visible: boolean
  content: SectionContent
}

export interface Resume {
  id: number
  kind: 'MASTER' | 'VERSION'
  name: string
  company: string | null
  roleTitle: string | null
  templateId: string
  fontFamily: string
  fontSizePt: number
  headingSizePt: number
  lineSpacing: number
  sectionSpacingPt: number
  bulletSpacingPt: number
  marginIn: number
  pageCount: number | null
  lastAtsScore: number | null
  parentId: number | null
  jobDescriptionId: number | null
  personalInfo: PersonalInfo
  sections: ResumeSection[]
}

export const SECTION_TYPE_LABELS: Record<SectionType, string> = {
  summary: 'Professional Summary',
  skills: 'Technical Skills',
  experience: 'Professional Experience',
  projects: 'Projects',
  education: 'Education',
  certifications: 'Certifications',
  achievements: 'Achievements',
  publications: 'Publications',
  awards: 'Awards',
  open_source: 'Open Source',
  volunteer: 'Volunteer Experience',
  languages: 'Languages',
  interests: 'Interests',
  custom: 'Custom Section',
}

export const DEFAULT_SECTION_TITLES: Record<SectionType, string> = {
  summary: 'PROFESSIONAL SUMMARY',
  skills: 'TECHNICAL SKILLS',
  experience: 'PROFESSIONAL EXPERIENCE',
  projects: 'KEY PROJECTS',
  education: 'EDUCATION',
  certifications: 'CERTIFICATIONS',
  achievements: 'ACHIEVEMENTS',
  publications: 'PUBLICATIONS',
  awards: 'AWARDS',
  open_source: 'OPEN SOURCE',
  volunteer: 'VOLUNTEER EXPERIENCE',
  languages: 'LANGUAGES',
  interests: 'INTERESTS',
  custom: 'CUSTOM SECTION',
}

export interface TemplateStyle {
  id: string
  name: string
  description: string
  accentColor: string
}

export function defaultContentFor(type: SectionType): SectionContent {
  if (type === 'summary' || type === 'custom' || type === 'achievements' || type === 'publications' || type === 'awards' || type === 'languages' || type === 'interests') {
    return { text: '' }
  }
  if (type === 'skills') return { categories: [] }
  return { items: [] }
}
