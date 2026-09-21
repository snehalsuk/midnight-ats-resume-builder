import { Plus } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input, Label } from '../ui/Input'
import { ItemActions } from '../ui/ItemActions'
import { duplicateAt, genId, moveItem, removeAt, updateAt } from '../../utils/arrayOps'
import type { EducationItem, SectionContent } from '../../types/resume'

export function EducationEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const items = (content.items ?? []) as EducationItem[]

  function setItems(next: EducationItem[]) {
    onChange({ ...content, items: next })
  }

  return (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <div key={item.id} className="rounded-md border border-slate-200 p-3">
          <div className="flex items-start justify-between gap-2">
            <div className="grid flex-1 grid-cols-2 gap-2">
              <div>
                <Label>Degree</Label>
                <Input value={item.degree} onChange={(e) => setItems(updateAt(items, idx, { degree: e.target.value }))} />
              </div>
              <div>
                <Label>Institution</Label>
                <Input value={item.institution} onChange={(e) => setItems(updateAt(items, idx, { institution: e.target.value }))} />
              </div>
              <div>
                <Label>GPA / CGPA</Label>
                <Input value={item.gpa} onChange={(e) => setItems(updateAt(items, idx, { gpa: e.target.value }))} />
              </div>
              <div>
                <Label>Year</Label>
                <Input value={item.year} onChange={(e) => setItems(updateAt(items, idx, { year: e.target.value }))} />
              </div>
            </div>
            <ItemActions
              onDelete={() => setItems(removeAt(items, idx))}
              onDuplicate={() => setItems(duplicateAt(items, idx, (i) => ({ ...i, id: genId('edu') })))}
              onMoveUp={() => setItems(moveItem(items, idx, -1))}
              onMoveDown={() => setItems(moveItem(items, idx, 1))}
              canMoveUp={idx > 0}
              canMoveDown={idx < items.length - 1}
            />
          </div>
        </div>
      ))}
      <Button
        variant="secondary"
        size="sm"
        onClick={() => setItems([...items, { id: genId('edu'), degree: '', institution: '', location: '', gpa: '', year: '' }])}
      >
        <Plus size={14} /> Add Education
      </Button>
    </div>
  )
}
