import { useState, useEffect } from 'react'
import PageLayout from '../components/layout/PageLayout'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import toast from 'react-hot-toast'
import { FiUsers, FiMapPin, FiUpload, FiBarChart2, FiDollarSign } from 'react-icons/fi'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const TABS = ['Analytics', 'Users', 'Upload Data']

export default function AdminDashboard() {
  const [tab, setTab]           = useState('Analytics')
  const [analytics, setAnalytics] = useState(null)
  const [users, setUsers]       = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [aRes, uRes] = await Promise.allSettled([
          api.get('/admin/analytics'),
          api.get('/admin/users'),
        ])
        if (aRes.status === 'fulfilled') setAnalytics(aRes.value.data)
        if (uRes.status === 'fulfilled') setUsers(uRes.value.data)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleUpload = async (type, file) => {
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await api.post(`/admin/upload/${type}`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success(`Uploaded ${res.data.inserted} ${type} ✅`)
    } catch {
      toast.error('Upload failed')
    }
  }

  if (loading) return <PageLayout><LoadingSpinner fullScreen /></PageLayout>

  return (
    <PageLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-500 text-sm">Manage data, users, and view analytics</p>
        </div>
        <span className="badge bg-amber-100 text-amber-700">Admin</span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px
              ${tab === t ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
            {t}
          </button>
        ))}
      </div>

      {/* Analytics */}
      {tab === 'Analytics' && analytics && (
        <div className="space-y-6 animate-fade-in">
          {/* Stat cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { label: 'Users',       value: analytics.users,       icon: '👥' },
              { label: 'Trips',       value: analytics.trips,       icon: '🗺️' },
              { label: 'Places',      value: analytics.places,      icon: '📍' },
              { label: 'Hotels',      value: analytics.hotels,      icon: '🏨' },
              { label: 'Restaurants', value: analytics.restaurants, icon: '🍽️' },
              { label: 'Reviews',     value: analytics.reviews,     icon: '⭐' },
            ].map(s => (
              <div key={s.label} className="card p-4 text-center">
                <div className="text-2xl mb-1">{s.icon}</div>
                <div className="text-2xl font-bold text-gray-900">{s.value}</div>
                <div className="text-xs text-gray-500">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Top Cities by Places</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={analytics.top_cities}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="city" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4F46E5" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Avg Trip Cost</h3>
              <div className="flex items-center justify-center h-48">
                <div className="text-center">
                  <div className="text-5xl font-bold text-primary-700">
                    ₹{analytics.avg_trip_cost?.toLocaleString('en-IN')}
                  </div>
                  <p className="text-gray-500 mt-2">Average across all trips</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Users */}
      {tab === 'Users' && (
        <div className="card overflow-hidden animate-fade-in">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500">
              <tr>
                {['Username','Email','Role','Status','Joined'].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{u.username}</td>
                  <td className="px-4 py-3 text-gray-500">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${u.role === 'admin' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload */}
      {tab === 'Upload Data' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
          {[
            { type: 'places',      label: 'Tourist Places CSV',  icon: '📍' },
            { type: 'hotels',      label: 'Hotels CSV',          icon: '🏨' },
            { type: 'restaurants', label: 'Restaurants CSV',     icon: '🍽️' },
          ].map(({ type, label, icon }) => (
            <div key={type} className="card p-6 text-center">
              <div className="text-4xl mb-3">{icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1">{label}</h3>
              <p className="text-xs text-gray-500 mb-4">Upload CSV to populate the database</p>
              <label className="btn-secondary cursor-pointer text-sm py-2 px-4">
                <FiUpload /> Choose File
                <input type="file" accept=".csv" className="hidden"
                  onChange={e => e.target.files[0] && handleUpload(type, e.target.files[0])} />
              </label>
            </div>
          ))}
        </div>
      )}
    </PageLayout>
  )
}
