import { Plus, X } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input, Textarea } from '../ui/Input'
import { removeAt } from '../../utils/arrayOps'
import type { SectionContent } from '../../types/resume'

export function GenericSectionEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const items = (content.items as string[] | undefined) ?? []
  const hasItems = items.length > 0

  return (
    <div className="space-y-3">
      <Textarea
        rows={3}
        placeholder="Free-form text for this section..."
        value={content.text ?? ''}
        onChange={(e) => onChange({ ...content, text: e.target.value })}
      />
      <div className="space-y-1.5">
        {hasItems &&
          items.map((item, idx) => (
            <div key={idx} className="flex items-center gap-1.5">
              <Input
                value={item}
                onChange={(e) => onChange({ ...content, items: items.map((it, i) => (i === idx ? e.target.value : it)) })}
              />
              <button type="button" onClick={() => onChange({ ...content, items: removeAt(items, idx) })} className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600">
                <X size={14} />
              </button>
            </div>
          ))}
        <Button variant="ghost" size="sm" onClick={() => onChange({ ...content, items: [...items, ''] })}>
          <Plus size={14} /> Add Bullet Item
        </Button>
      </div>
    </div>
  )
}
