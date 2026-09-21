import { Plus } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input, Label } from '../ui/Input'
import { ItemActions } from '../ui/ItemActions'
import { duplicateAt, genId, moveItem, removeAt, updateAt } from '../../utils/arrayOps'
import type { CertificationItem, SectionContent } from '../../types/resume'

export function CertificationsEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const items = (content.items ?? []) as CertificationItem[]

  function setItems(next: CertificationItem[]) {
    onChange({ ...content, items: next })
  }

  return (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <div key={item.id} className="rounded-md border border-slate-200 p-3">
          <div className="flex items-start justify-between gap-2">
            <div className="grid flex-1 grid-cols-2 gap-2">
              <div>
                <Label>Certification Name</Label>
                <Input value={item.name} onChange={(e) => setItems(updateAt(items, idx, { name: e.target.value }))} />
              </div>
              <div>
                <Label>Issuer</Label>
                <Input value={item.issuer} onChange={(e) => setItems(updateAt(items, idx, { issuer: e.target.value }))} />
              </div>
              <div>
                <Label>Year</Label>
                <Input value={item.year} onChange={(e) => setItems(updateAt(items, idx, { year: e.target.value }))} />
              </div>
              <div>
                <Label>Credential URL</Label>
                <Input value={item.credentialUrl} onChange={(e) => setItems(updateAt(items, idx, { credentialUrl: e.target.value }))} />
              </div>
            </div>
            <ItemActions
              onDelete={() => setItems(removeAt(items, idx))}
              onDuplicate={() => setItems(duplicateAt(items, idx, (i) => ({ ...i, id: genId('cert') })))}
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
        onClick={() => setItems([...items, { id: genId('cert'), name: '', issuer: '', year: '', credentialUrl: '' }])}
      >
        <Plus size={14} /> Add Certification
      </Button>
    </div>
  )
}
