import { Plus } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input, Label } from '../ui/Input'
import { ItemActions } from '../ui/ItemActions'
import { BulletListEditor } from './BulletListEditor'
import { duplicateAt, genId, moveItem, removeAt, updateAt } from '../../utils/arrayOps'
import type { ExperienceItem, SectionContent } from '../../types/resume'

export function ExperienceEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const items = (content.items ?? []) as ExperienceItem[]

  function setItems(next: ExperienceItem[]) {
    onChange({ ...content, items: next })
  }

  function addItem() {
    const item: ExperienceItem = {
      id: genId('exp'),
      title: '',
      company: '',
      location: '',
      startDate: '',
      endDate: '',
      current: false,
      bullets: [],
    }
    setItems([...items, item])
  }

  return (
    <div className="space-y-4">
      {items.map((item, idx) => (
        <div key={item.id} className="rounded-md border border-slate-200 p-3">
          <div className="mb-2 flex items-start justify-between gap-2">
            <div className="grid flex-1 grid-cols-2 gap-2">
              <div>
                <Label>Job Title</Label>
                <Input value={item.title} onChange={(e) => setItems(updateAt(items, idx, { title: e.target.value }))} />
              </div>
              <div>
                <Label>Company</Label>
                <Input value={item.company} onChange={(e) => setItems(updateAt(items, idx, { company: e.target.value }))} />
              </div>
              <div>
                <Label>Start Date</Label>
                <Input placeholder="Oct 2023" value={item.startDate} onChange={(e) => setItems(updateAt(items, idx, { startDate: e.target.value }))} />
              </div>
              <div>
                <Label>End Date</Label>
                <Input
                  placeholder="Present"
                  value={item.endDate}
                  onChange={(e) => setItems(updateAt(items, idx, { endDate: e.target.value, current: e.target.value.trim().toLowerCase() === 'present' }))}
                />
              </div>
            </div>
            <ItemActions
              onDelete={() => setItems(removeAt(items, idx))}
              onDuplicate={() => setItems(duplicateAt(items, idx, (i) => ({ ...i, id: genId('exp') })))}
              onMoveUp={() => setItems(moveItem(items, idx, -1))}
              onMoveDown={() => setItems(moveItem(items, idx, 1))}
              canMoveUp={idx > 0}
              canMoveDown={idx < items.length - 1}
            />
          </div>
          <Label>Bullets</Label>
          <BulletListEditor bullets={item.bullets} onChange={(bullets) => setItems(updateAt(items, idx, { bullets }))} />
        </div>
      ))}
      <Button variant="secondary" size="sm" onClick={addItem}>
        <Plus size={14} /> Add Experience
      </Button>
    </div>
  )
}
