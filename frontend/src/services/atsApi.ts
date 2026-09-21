import { apiClient } from './apiClient'
import type { AiChange, AtsScoreBreakdown, JobDescription, QualityGateResult, TailorResult } from '../types/ats'

export async function analyzeJobDescription(rawText: string, company?: string): Promise<JobDescription> {
  const { data } = await apiClient.post<JobDescription>('/job-descriptions/analyze', { rawText, company })
  return data
}

export async function listJobDescriptions(): Promise<JobDescription[]> {
  const { data } = await apiClient.get<JobDescription[]>('/job-descriptions')
  return data
}

export async function analyzeAts(resumeId: number, jobDescriptionId?: number): Promise<AtsScoreBreakdown> {
  const { data } = await apiClient.post<AtsScoreBreakdown>(`/resumes/${resumeId}/ats/analyze`, {
    jobDescriptionId: jobDescriptionId ?? null,
  })
  return data
}

export async function validateResume(resumeId: number): Promise<QualityGateResult> {
  const { data } = await apiClient.post<QualityGateResult>(`/resumes/${resumeId}/validate`)
  return data
}

export async function optimizeResume(
  resumeId: number,
  jobDescriptionId: number,
  confirmedSkills: string[] = [],
): Promise<TailorResult> {
  const { data } = await apiClient.post<TailorResult>(`/resumes/${resumeId}/optimize`, {
    jobDescriptionId,
    confirmedSkills,
  })
  return data
}

export async function listAiChanges(resumeId: number): Promise<AiChange[]> {
  const { data } = await apiClient.get<AiChange[]>(`/resumes/${resumeId}/ai-changes`)
  return data
}

export async function acceptAiChange(resumeId: number, changeId: number): Promise<AiChange> {
  const { data } = await apiClient.post<AiChange>(`/resumes/${resumeId}/ai-changes/${changeId}/accept`)
  return data
}

export async function rejectAiChange(resumeId: number, changeId: number): Promise<AiChange> {
  const { data } = await apiClient.post<AiChange>(`/resumes/${resumeId}/ai-changes/${changeId}/reject`)
  return data
}

export async function acceptAllAiChanges(resumeId: number): Promise<void> {
  await apiClient.post(`/resumes/${resumeId}/ai-changes/accept-all`)
}
