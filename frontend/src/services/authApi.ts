import { apiClient } from './apiClient'

export interface User {
  id: number
  email: string
  firstName: string
  lastName: string
}

export async function register(email: string, password: string, firstName: string, lastName: string): Promise<User> {
  const { data } = await apiClient.post<User>('/auth/register', { email, password, firstName, lastName })
  return data
}

export async function login(email: string, password: string): Promise<string> {
  const { data } = await apiClient.post<{ accessToken: string }>('/auth/login', { email, password })
  return data.accessToken
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me')
  return data
}
