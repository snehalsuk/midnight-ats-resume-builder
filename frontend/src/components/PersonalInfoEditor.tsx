import { Input, Label } from './ui/Input'
import type { PersonalInfo } from '../types/resume'

const FIELDS: { key: keyof PersonalInfo; label: string; placeholder?: string }[] = [
  { key: 'name', label: 'Full Name' },
  { key: 'title', label: 'Professional Title', placeholder: 'Java Full Stack Developer | React.js Developer' },
  { key: 'location', label: 'Location', placeholder: 'City, State, Country' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'linkedin', label: 'LinkedIn', placeholder: 'linkedin.com/in/username' },
  { key: 'github', label: 'GitHub', placeholder: 'github.com/username' },
  { key: 'portfolio', label: 'Portfolio', placeholder: 'yoursite.com' },
  { key: 'leetcode', label: 'LeetCode' },
  { key: 'hackerrank', label: 'HackerRank' },
]

export function PersonalInfoEditor({ info, onChange }: { info: PersonalInfo; onChange: (patch: Partial<PersonalInfo>) => void }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {FIELDS.map(({ key, label, placeholder }) => (
        <div key={key}>
          <Label>{label}</Label>
          <Input value={info[key]} placeholder={placeholder} onChange={(e) => onChange({ [key]: e.target.value })} />
        </div>
      ))}
    </div>
  )
}
