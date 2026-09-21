import { create } from 'zustand'

export type ToastTone = 'success' | 'error' | 'info'

export interface ToastItem {
  id: number
  tone: ToastTone
  title: string
  description?: string
}

interface ToastState {
  toasts: ToastItem[]
  dismiss: (id: number) => void
}

let counter = 0

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

export function toast(tone: ToastTone, title: string, description?: string) {
  const id = ++counter
  useToastStore.setState((s) => ({ toasts: [...s.toasts, { id, tone, title, description }] }))
  setTimeout(() => useToastStore.getState().dismiss(id), 5000)
}

export const toastSuccess = (title: string, description?: string) => toast('success', title, description)
export const toastError = (title: string, description?: string) => toast('error', title, description)
export const toastInfo = (title: string, description?: string) => toast('info', title, description)
