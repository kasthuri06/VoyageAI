import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import { tripService } from '../services/tripService'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { FiMapPin, FiCalendar, FiTrash2, FiArrowRight, FiBookmark } from 'react-icons/fi'
import toast from 'react-hot-toast'

const STATUS_FILTERS = ['all', 'draft', 'active', 'completed', 'cancelled']

export default function SavedTrips() {
  const [trips, setTrips]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [statusFilter, setStatusFilter] = useState('all')

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await tripService.listTrips(statusFilter !== 'all' ? statusFilter : undefined)
      setTrips(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [statusFilter])

  const handleDelete = async (id, e) => {
    e.preventDefault()
    if (!window.confirm('Delete this trip?')) return
    await tripService.deleteTrip(id)
    toast.success('Deleted')
    setTrips(t => t.filter(trip => trip.id !== id))
  }

  const handleToggleSave = async (id, e) => {
    e.preventDefault()
    const res = await tripService.toggleSave(id)
    setTrips(t => t.map(trip => trip.id === id ? { ...trip, is_saved: res.data.is_saved } : trip))
  }

  return (
    <PageLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-gray-900">My Trips</h1>
          <p className="text-gray-500 text-sm">{trips.length} total trips</p>
        </div>
        <Link to="/plan" className="btn-primary text-sm py-2.5">+ New Trip</Link>
      </div>

      {/* Status filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
        {STATUS_FILTERS.map(s => (
          <button key={s} onClick={() => setStatusFilter(s)}
            className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-colors
              ${statusFilter === s ? 'bg-primary-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:border-primary-300'}`}>
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
      ) : trips.length === 0 ? (
        <div className="card p-14 text-center">
          <div className="text-5xl mb-4">🗺️</div>
          <h3 className="font-semibold text-gray-900 text-lg">No trips found</h3>
          <p className="text-gray-500 mt-2">Start planning your next adventure</p>
          <Link to="/plan" className="btn-primary mt-5 inline-flex">Plan a Trip</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {trips.map(trip => (
            <Link key={trip.id} to={`/trip/${trip.id}`}
              className="card p-5 flex flex-col gap-3 hover:border hover:border-primary-200 transition-all group">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{trip.title}</h3>
                  <div className="flex items-center gap-1 text-gray-500 text-xs mt-1">
                    <FiMapPin className="flex-shrink-0" />
                    <span className="truncate">{trip.start_location} → {trip.end_location}</span>
                  </div>
                </div>
                <span className={`badge flex-shrink-0 text-xs ${
                  trip.status === 'completed' ? 'bg-green-100 text-green-700'
                  : trip.status === 'active'  ? 'bg-blue-100 text-blue-700'
                  : trip.status === 'cancelled' ? 'bg-red-100 text-red-600'
                  : 'bg-gray-100 text-gray-600'
                }`}>{trip.status}</span>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <FiCalendar /> {trip.travel_days} days
                </span>
                <span>₹{trip.total_cost?.toLocaleString('en-IN') || 0}</span>
              </div>

              <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-100">
                <button
                  onClick={e => handleToggleSave(trip.id, e)}
                  className={`flex items-center gap-1 text-xs font-medium transition-colors
                    ${trip.is_saved ? 'text-primary-600' : 'text-gray-400 hover:text-primary-500'}`}>
                  <FiBookmark className={trip.is_saved ? 'fill-current' : ''} />
                  {trip.is_saved ? 'Saved' : 'Save'}
                </button>
                <div className="flex items-center gap-2">
                  <button onClick={e => handleDelete(trip.id, e)}
                    className="text-xs text-red-400 hover:text-red-600 transition-colors">
                    <FiTrash2 />
                  </button>
                  <span className="text-primary-500 group-hover:text-primary-700 transition-colors">
                    <FiArrowRight />
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </PageLayout>
  )
}
