import { ChevronDown, ChevronUp, Copy, Trash2 } from 'lucide-react'

interface Props {
  onDelete: () => void
  onDuplicate?: () => void
  onMoveUp?: () => void
  onMoveDown?: () => void
  canMoveUp?: boolean
  canMoveDown?: boolean
}

export function ItemActions({ onDelete, onDuplicate, onMoveUp, onMoveDown, canMoveUp = true, canMoveDown = true }: Props) {
  return (
    <div className="flex items-center gap-1 text-slate-400">
      {onMoveUp && (
        <button
          type="button"
          title="Move up"
          onClick={onMoveUp}
          disabled={!canMoveUp}
          className="rounded p-1 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-30"
        >
          <ChevronUp size={14} />
        </button>
      )}
      {onMoveDown && (
        <button
          type="button"
          title="Move down"
          onClick={onMoveDown}
          disabled={!canMoveDown}
          className="rounded p-1 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-30"
        >
          <ChevronDown size={14} />
        </button>
      )}
      {onDuplicate && (
        <button type="button" title="Duplicate" onClick={onDuplicate} className="rounded p-1 hover:bg-slate-100 hover:text-slate-700">
          <Copy size={14} />
        </button>
      )}
      <button type="button" title="Delete" onClick={onDelete} className="rounded p-1 hover:bg-red-50 hover:text-red-600">
        <Trash2 size={14} />
      </button>
    </div>
  )
}
