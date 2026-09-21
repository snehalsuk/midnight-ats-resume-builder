import { create } from 'zustand'
import type { User } from '../services/authApi'

interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('accessToken'),
  user: null,
  setAuth: (token, user) => {
    localStorage.setItem('accessToken', token)
    set({ token, user })
  },
  logout: () => {
    localStorage.removeItem('accessToken')
    set({ token: null, user: null })
  },
}))
