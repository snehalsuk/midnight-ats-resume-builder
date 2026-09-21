import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileCheck2, ShieldCheck, Target } from 'lucide-react'
import { login, register } from '../services/authApi'
import { getApiErrorMessage } from '../services/apiClient'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Input, Label } from '../components/ui/Input'

export function RegisterPage() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await register(email, password, firstName, lastName)
      const token = await login(email, password)
      setAuth(token, null)
      navigate('/dashboard')
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-slate-900 p-10 text-white lg:flex">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.25),transparent_45%)]" />
        <div className="relative flex items-center gap-2.5 text-sm font-semibold">
          <img src="/logo.png" alt="Midnight" className="h-10 w-auto rounded-md" />
          <span>ATS Resume Builder</span>
        </div>
        <div className="relative space-y-6">
          <h1 className="text-3xl font-bold leading-tight">
            One master resume. Unlimited honest, tailored versions.
          </h1>
          <div className="space-y-4 text-sm text-slate-300">
            <div className="flex items-start gap-3">
              <FileCheck2 size={18} className="mt-0.5 shrink-0 text-brand-400" />
              Every tailored version starts from your real experience — nothing invented.
            </div>
            <div className="flex items-start gap-3">
              <Target size={18} className="mt-0.5 shrink-0 text-brand-400" />
              See exactly which keywords match, which are missing, and why.
            </div>
            <div className="flex items-start gap-3">
              <ShieldCheck size={18} className="mt-0.5 shrink-0 text-brand-400" />
              Export a validated, one-page, true-text PDF — every time, automatically.
            </div>
          </div>
        </div>
        <p className="relative text-xs text-slate-500">Free to use. Your data stays yours.</p>
      </div>

      <div className="flex items-center justify-center bg-slate-50 px-4 py-12 lg:px-10">
        <form onSubmit={handleSubmit} className="w-full max-w-sm animate-fade-in">
          <h2 className="text-xl font-semibold text-slate-900">Create your account</h2>
          <p className="mt-1 text-sm text-slate-500">Build an ATS-optimized resume from your existing one.</p>

          {error && (
            <div className="mt-4 rounded-lg border border-danger-100 bg-danger-50 px-3 py-2 text-sm text-danger-700">
              {error}
            </div>
          )}

          <div className="mt-6 space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>First name</Label>
                <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              </div>
              <div>
                <Label>Last name</Label>
                <Input value={lastName} onChange={(e) => setLastName(e.target.value)} />
              </div>
            </div>
            <div>
              <Label>Email</Label>
              <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div>
              <Label>Password (min 8 characters)</Label>
              <Input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
          </div>

          <Button type="submit" size="lg" className="mt-6 w-full justify-center" loading={loading}>
            {loading ? 'Creating account…' : 'Create account'}
          </Button>

          <p className="mt-5 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
