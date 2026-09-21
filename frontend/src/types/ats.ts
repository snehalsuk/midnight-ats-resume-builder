export interface ParsingChecklistItem {
  detected: boolean
  reason: string | null
}

export interface AtsScoreBreakdown {
  overallScore: number
  keywordMatchPct: number
  skillsMatchPct: number
  titleMatchPct: number
  experienceRelevancePct: number
  sectionCompletenessPct: number
  parsingAccuracyPct: number
  formattingCompatibilityPct: number
  readabilityPct: number
  matchedKeywords: string[]
  missingKeywords: string[]
  relatedKeywords: string[]
  formattingWarnings: string[]
  sectionWarnings: string[]
  suggestions: string[]
  parsingChecklist: Record<string, ParsingChecklistItem>
  pageCount: number | null
  onePageOk: boolean
}

export interface QualityGateResult {
  passed: boolean
  failedChecks: string[]
}

export interface ParsedJobDescription {
  jobTitle: string
  requiredSkills: string[]
  preferredSkills: string[]
  technologies: string[]
  yearsOfExperience: string
  educationRequirements: string[]
  certifications: string[]
  responsibilities: string[]
  domainKeywords: string[]
  softSkills: string[]
  tools: string[]
  cloudTechnologies: string[]
  frameworks: string[]
  databases: string[]
}

export interface JobDescription {
  id: number
  company: string | null
  rawText: string
  parsed: ParsedJobDescription
}

export interface BulletChange {
  targetPath: string
  originalText: string
  suggestedText: string
}

export interface SkillAddition {
  category: string
  skill: string
}

export interface TailorResult {
  summary: string
  recommendedSkills: string[]
  skillAdditions: SkillAddition[]
  skillReorder: { category: string; orderedItems: string[] }[]
  keywordMatches: string[]
  missingKeywords: string[]
  bulletChanges: BulletChange[]
  warnings: string[]
  fabricationRisk: boolean
}

export interface AiChange {
  id: number
  targetPath: string
  changeType: string
  originalValue: string
  suggestedValue: string
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED'
  fabricationRisk: boolean
  blockedLockedField: boolean
}
