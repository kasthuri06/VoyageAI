import { useState, useEffect } from 'react'
import PageLayout from '../components/layout/PageLayout'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import toast from 'react-hot-toast'
import { FiUser, FiMail, FiPhone, FiSave } from 'react-icons/fi'

const INTERESTS = ['adventure','nature','beach','temple','museum','shopping','food','luxury','family','romantic','wildlife','history']

export default function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState({ full_name: '', phone: '' })
  const [prefs, setPrefs]     = useState({
    interests: [], preferred_transport: 'car', preferred_hotel_rating: 3,
    max_budget_per_day: '', travel_style: 'solo', preferred_travel_time: 'morning',
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) setProfile({ full_name: user.full_name || '', phone: '' })
    api.get('/user/preferences').then(r => setPrefs(p => ({ ...p, ...r.data }))).catch(() => {})
  }, [user])

  const toggleInterest = (id) =>
    setPrefs(p => ({
      ...p,
      interests: p.interests?.includes(id)
        ? p.interests.filter(i => i !== id)
        : [...(p.interests || []), id]
    }))

  const handleSave = async () => {
    setLoading(true)
    try {
      await Promise.all([
        api.put('/user/profile', profile),
        api.put('/user/preferences', prefs),
      ])
      toast.success('Profile saved!')
    } catch {
      toast.error('Failed to save')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="font-display text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

        {/* Avatar */}
        <div className="card p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-primary-100 flex items-center justify-center">
              {user?.profile_picture
                ? <img src={user.profile_picture} className="w-16 h-16 rounded-2xl object-cover" alt="" />
                : <FiUser className="text-primary-600 text-2xl" />
              }
            </div>
            <div>
              <p className="font-bold text-gray-900 text-lg">{user?.username}</p>
              <p className="text-gray-500 text-sm">{user?.email}</p>
              <span className={`badge text-xs mt-1 ${user?.role === 'admin' ? 'bg-amber-100 text-amber-700' : 'bg-primary-50 text-primary-700'}`}>
                {user?.role}
              </span>
            </div>
          </div>
        </div>

        {/* Edit info */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4">Personal Info</h2>
          <div className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <div className="relative">
                <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="text" className="input-field pl-10"
                  value={profile.full_name}
                  onChange={e => setProfile(p => ({ ...p, full_name: e.target.value }))} />
              </div>
            </div>
            <div>
              <label className="label">Email (read only)</label>
              <div className="relative">
                <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="email" className="input-field pl-10 bg-gray-50" value={user?.email || ''} readOnly />
              </div>
            </div>
            <div>
              <label className="label">Phone</label>
              <div className="relative">
                <FiPhone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="tel" className="input-field pl-10"
                  value={profile.phone}
                  onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))} />
              </div>
            </div>
          </div>
        </div>

        {/* Travel Preferences */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4">Travel Preferences</h2>
          <div className="space-y-5">
            <div>
              <label className="label">My Interests</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {INTERESTS.map(id => (
                  <button key={id} type="button" onClick={() => toggleInterest(id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium border-2 transition-all
                      ${prefs.interests?.includes(id) ? 'bg-primary-600 border-primary-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-primary-300'}`}>
                    {id}
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Transport</label>
                <select className="input-field" value={prefs.preferred_transport || 'car'}
                  onChange={e => setPrefs(p => ({ ...p, preferred_transport: e.target.value }))}>
                  {['car','bike','walk','public','flight'].map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Travel Style</label>
                <select className="input-field" value={prefs.travel_style || 'solo'}
                  onChange={e => setPrefs(p => ({ ...p, travel_style: e.target.value }))}>
                  {['solo','couple','family','group'].map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="label">Max Budget per Day (₹)</label>
              <input type="number" className="input-field"
                value={prefs.max_budget_per_day || ''}
                onChange={e => setPrefs(p => ({ ...p, max_budget_per_day: e.target.value }))} />
            </div>
          </div>
        </div>

        <button onClick={handleSave} disabled={loading} className="btn-primary w-full py-3.5">
          <FiSave /> {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </PageLayout>
  )
}
