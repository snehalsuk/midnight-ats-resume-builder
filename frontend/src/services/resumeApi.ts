import { apiClient } from './apiClient'
import type { PersonalInfo, Resume, ResumeSection, TemplateStyle } from '../types/resume'

export async function uploadResume(file: File): Promise<Resume> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<Resume>('/resumes/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function listTemplates(): Promise<TemplateStyle[]> {
  const { data } = await apiClient.get<TemplateStyle[]>('/resumes/templates')
  return data
}

export interface ResumeCreatePayload {
  name?: string
  templateId?: string
}

export async function createResume(payload: ResumeCreatePayload): Promise<Resume> {
  const { data } = await apiClient.post<Resume>('/resumes', payload)
  return data
}

export async function listResumes(kind?: 'MASTER' | 'VERSION'): Promise<Resume[]> {
  const { data } = await apiClient.get<Resume[]>('/resumes', { params: kind ? { kind } : {} })
  return data
}

export async function getResume(id: number): Promise<Resume> {
  const { data } = await apiClient.get<Resume>(`/resumes/${id}`)
  return data
}

export interface ResumeUpdatePayload {
  name?: string
  templateId?: string
  personalInfo?: PersonalInfo
  sections?: ResumeSection[]
  company?: string | null
  roleTitle?: string | null
  fontSizePt?: number
  marginIn?: number
  sectionSpacingPt?: number
  bulletSpacingPt?: number
}

export async function updateResume(id: number, payload: ResumeUpdatePayload): Promise<Resume> {
  const { data } = await apiClient.put<Resume>(`/resumes/${id}`, payload)
  return data
}

export async function deleteResume(id: number): Promise<void> {
  await apiClient.delete(`/resumes/${id}`)
}

export async function duplicateResume(id: number): Promise<Resume> {
  const { data } = await apiClient.post<Resume>(`/resumes/${id}/duplicate`)
  return data
}

export async function listVersions(masterId: number): Promise<Resume[]> {
  const { data } = await apiClient.get<Resume[]>(`/resumes/${masterId}/versions`)
  return data
}

export interface ResumeDiffResult {
  added: string[]
  removed: string[]
  modified: { section: string; diffLines: string[] }[]
  unchanged: string[]
  reordered: boolean
}

export async function diffResumes(resumeId: number, compareToId: number): Promise<ResumeDiffResult> {
  const { data } = await apiClient.get<ResumeDiffResult>(`/resumes/${resumeId}/diff`, { params: { compare_to_id: compareToId } })
  return data
}

export interface PreviewResult {
  html: string
  pageCount: number
}

export async function previewResumeDraft(id: number, personalInfo: PersonalInfo, sections: ResumeSection[]): Promise<PreviewResult> {
  const { data } = await apiClient.post<PreviewResult>(`/resumes/${id}/preview`, { personalInfo, sections })
  return data
}

export interface ExportFileResult {
  filename: string
  pageCount: number | null
  contentBase64: string
}

export async function exportPdf(id: number): Promise<ExportFileResult> {
  const { data } = await apiClient.post<ExportFileResult>(`/resumes/${id}/export/pdf`)
  return data
}

export async function exportDocx(id: number): Promise<ExportFileResult> {
  const { data } = await apiClient.post<ExportFileResult>(`/resumes/${id}/export/docx`)
  return data
}

export function downloadBase64File(filename: string, base64: string, mimeType: string) {
  const byteChars = atob(base64)
  const byteNumbers = new Array(byteChars.length)
  for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i)
  const blob = new Blob([new Uint8Array(byteNumbers)], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
