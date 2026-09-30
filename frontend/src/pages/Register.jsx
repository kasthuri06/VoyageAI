import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FiCompass, FiMail, FiLock, FiUser } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm]       = useState({ email: '', username: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 6) {
      toast.error('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    try {
      await register(form)
      toast.success('Account created! Let\'s plan your first trip 🌍')
      navigate('/dashboard')
    } catch {
      // handled globally
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700
                          flex items-center justify-center mx-auto shadow-lg mb-4">
            <FiCompass className="text-white text-2xl" />
          </div>
          <h1 className="font-display text-3xl font-bold text-gray-900">Create account</h1>
          <p className="text-gray-500 mt-1">Start planning AI-powered trips today</p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <div className="relative">
                <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="text" className="input-field pl-10" placeholder="Jane Doe"
                  value={form.full_name} onChange={e => set('full_name', e.target.value)} />
              </div>
            </div>
            <div>
              <label className="label">Email address</label>
              <div className="relative">
                <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="email" className="input-field pl-10" placeholder="you@example.com"
                  value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="label">Username</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">@</span>
                <input type="text" className="input-field pl-8" placeholder="travelexplorer"
                  value={form.username} onChange={e => set('username', e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="password" className="input-field pl-10" placeholder="Min. 6 characters"
                  value={form.password} onChange={e => set('password', e.target.value)} required />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full py-3 mt-2">
              {loading ? (
                <span className="flex items-center gap-2 justify-center">
                  <span className="animate-spin h-4 w-4 rounded-full border-2 border-white/30 border-t-white" />
                  Creating account...
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          <p className="text-xs text-gray-400 text-center mt-4">
            By creating an account you agree to our Terms of Service.
          </p>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
