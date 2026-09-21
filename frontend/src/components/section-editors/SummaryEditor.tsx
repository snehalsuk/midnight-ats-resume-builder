import { Textarea } from '../ui/Input'
import type { SectionContent } from '../../types/resume'

export function SummaryEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  return (
    <Textarea
      rows={5}
      value={content.text ?? ''}
      onChange={(e) => onChange({ ...content, text: e.target.value })}
      placeholder="Write a 2-4 sentence professional summary tailored to your target role..."
    />
  )
}
