import { Plus } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { ItemActions } from '../ui/ItemActions'
import { duplicateAt, moveItem, removeAt, updateAt } from '../../utils/arrayOps'
import type { SectionContent, SkillCategory } from '../../types/resume'

export function SkillsEditor({ content, onChange }: { content: SectionContent; onChange: (c: SectionContent) => void }) {
  const categories = content.categories ?? []

  function setCategories(next: SkillCategory[]) {
    onChange({ ...content, categories: next })
  }

  return (
    <div className="space-y-3">
      {categories.map((cat, idx) => (
        <div key={idx} className="flex items-start gap-2">
          <div className="w-36 shrink-0">
            <Input
              value={cat.name}
              placeholder="Category"
              onChange={(e) => setCategories(updateAt(categories, idx, { name: e.target.value }))}
            />
          </div>
          <div className="flex-1">
            <Input
              value={cat.items.join(', ')}
              placeholder="Comma-separated skills"
              onChange={(e) =>
                setCategories(updateAt(categories, idx, { items: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) }))
              }
            />
          </div>
          <ItemActions
            onDelete={() => setCategories(removeAt(categories, idx))}
            onDuplicate={() => setCategories(duplicateAt(categories, idx))}
            onMoveUp={() => setCategories(moveItem(categories, idx, -1))}
            onMoveDown={() => setCategories(moveItem(categories, idx, 1))}
            canMoveUp={idx > 0}
            canMoveDown={idx < categories.length - 1}
          />
        </div>
      ))}
      <Button
        variant="secondary"
        size="sm"
        onClick={() => setCategories([...categories, { name: '', items: [] }])}
      >
        <Plus size={14} /> Add Category
      </Button>
    </div>
  )
}
