import { Plus } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input, Label } from '../ui/Input'
import { ItemActions } from '../ui/ItemActions'
import { BulletListEditor } from './BulletListEditor'
import { duplicateAt, genId, moveItem, removeAt, updateAt } from '../../utils/arrayOps'
import type { ProjectItem, SectionContent } from '../../types/resume'

export function ProjectsEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const items = (content.items ?? []) as ProjectItem[]

  function setItems(next: ProjectItem[]) {
    onChange({ ...content, items: next })
  }

  function addItem() {
    const item: ProjectItem = { id: genId('proj'), name: '', technologies: [], link: '', bullets: [] }
    setItems([...items, item])
  }

  return (
    <div className="space-y-4">
      {items.map((item, idx) => (
        <div key={item.id} className="rounded-md border border-slate-200 p-3">
          <div className="mb-2 flex items-start justify-between gap-2">
            <div className="flex-1 space-y-2">
              <div>
                <Label>Project Name</Label>
                <Input value={item.name} onChange={(e) => setItems(updateAt(items, idx, { name: e.target.value }))} />
              </div>
              <div>
                <Label>Technologies (comma-separated)</Label>
                <Input
                  value={item.technologies.join(', ')}
                  onChange={(e) => setItems(updateAt(items, idx, { technologies: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) }))}
                />
              </div>
              <div>
                <Label>Link (optional)</Label>
                <Input value={item.link} onChange={(e) => setItems(updateAt(items, idx, { link: e.target.value }))} />
              </div>
            </div>
            <ItemActions
              onDelete={() => setItems(removeAt(items, idx))}
              onDuplicate={() => setItems(duplicateAt(items, idx, (i) => ({ ...i, id: genId('proj') })))}
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
        <Plus size={14} /> Add Project
      </Button>
    </div>
  )
}
