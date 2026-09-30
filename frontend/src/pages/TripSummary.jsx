import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import ItineraryView from '../components/trip/ItineraryView'
import { tripService } from '../services/tripService'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { FiArrowLeft, FiBookmark, FiTrash2 } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function TripSummary() {
  const { tripId } = useParams()
  const navigate   = useNavigate()
  const [trip, setTrip]     = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    tripService.getTrip(tripId)
      .then(res => setTrip(res.data))
      .catch(() => { toast.error('Trip not found'); navigate('/saved') })
      .finally(() => setLoading(false))
  }, [tripId])

  const handleToggleSave = async () => {
    const res = await tripService.toggleSave(tripId)
    setTrip(t => ({ ...t, is_saved: res.data.is_saved }))
    toast.success(res.data.is_saved ? 'Trip saved!' : 'Removed from saved')
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this trip?')) return
    await tripService.deleteTrip(tripId)
    toast.success('Trip deleted')
    navigate('/saved')
  }

  if (loading) return <PageLayout><LoadingSpinner fullScreen /></PageLayout>
  if (!trip)   return null

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-6">
          <button onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors">
            <FiArrowLeft /> Back
          </button>
          <div className="flex gap-2">
            <button onClick={handleToggleSave}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border-2 transition-all
                ${trip.is_saved ? 'bg-primary-600 border-primary-600 text-white' : 'border-gray-200 text-gray-600 hover:border-primary-300'}`}>
              <FiBookmark /> {trip.is_saved ? 'Saved' : 'Save Trip'}
            </button>
            <button onClick={handleDelete}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border-2
                         border-red-200 text-red-500 hover:bg-red-50 transition-all">
              <FiTrash2 /> Delete
            </button>
          </div>
        </div>

        {/* Full itinerary */}
        {trip.itinerary?.days ? (
          <ItineraryView itinerary={trip.itinerary} />
        ) : (
          <div className="card p-8 text-center">
            <p className="text-gray-500">No detailed itinerary available for this trip.</p>
            <p className="text-sm text-gray-400 mt-2">Trip: {trip.title}</p>
            <p className="text-sm text-gray-400">{trip.start_location} → {trip.end_location} · {trip.travel_days} days</p>
          </div>
        )}
      </div>
    </PageLayout>
  )
}
