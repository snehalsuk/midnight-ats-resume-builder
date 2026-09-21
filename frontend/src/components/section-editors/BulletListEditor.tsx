import { Plus, X } from 'lucide-react'
import { Button } from '../ui/Button'
import { Textarea } from '../ui/Input'
import { moveItem, removeAt } from '../../utils/arrayOps'

export function BulletListEditor({ bullets, onChange }: { bullets: string[]; onChange: (b: string[]) => void }) {
  function setBulletText(index: number, text: string) {
    onChange(bullets.map((b, i) => (i === index ? text : b)))
  }

  return (
    <div className="space-y-1.5">
      {bullets.map((bullet, idx) => (
        <div key={idx} className="flex items-start gap-1.5">
          <span className="mt-2 select-none text-slate-400">•</span>
          <Textarea rows={2} value={bullet} onChange={(e) => setBulletText(idx, e.target.value)} className="flex-1" />
          <div className="mt-1 flex flex-col">
            <button type="button" title="Move up" onClick={() => onChange(moveItem(bullets, idx, -1))} disabled={idx === 0} className="p-0.5 text-slate-400 hover:text-slate-700 disabled:opacity-30">
              ▲
            </button>
            <button type="button" title="Move down" onClick={() => onChange(moveItem(bullets, idx, 1))} disabled={idx === bullets.length - 1} className="p-0.5 text-slate-400 hover:text-slate-700 disabled:opacity-30">
              ▼
            </button>
          </div>
          <button type="button" title="Remove bullet" onClick={() => onChange(removeAt(bullets, idx))} className="mt-1.5 rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600">
            <X size={14} />
          </button>
        </div>
      ))}
      <Button variant="ghost" size="sm" onClick={() => onChange([...bullets, ''])}>
        <Plus size={14} /> Add Bullet
      </Button>
    </div>
  )
}
