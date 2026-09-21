export function moveItem<T>(arr: T[], index: number, direction: -1 | 1): T[] {
  const target = index + direction
  if (target < 0 || target >= arr.length) return arr
  const copy = [...arr]
  ;[copy[index], copy[target]] = [copy[target], copy[index]]
  return copy
}

export function removeAt<T>(arr: T[], index: number): T[] {
  return arr.filter((_, i) => i !== index)
}

export function duplicateAt<T>(arr: T[], index: number, transform?: (item: T) => T): T[] {
  const item = arr[index]
  if (item === undefined) return arr
  const copy = transform ? transform(item) : { ...(item as object) } as T
  return [...arr.slice(0, index + 1), copy, ...arr.slice(index + 1)]
}

export function updateAt<T>(arr: T[], index: number, patch: Partial<T>): T[] {
  return arr.map((item, i) => (i === index ? { ...item, ...patch } : item))
}

export function genId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`
}
