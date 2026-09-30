import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import TripPlannerForm from '../components/trip/TripPlannerForm'
import ItineraryView from '../components/trip/ItineraryView'
import { tripService } from '../services/tripService'
import toast from 'react-hot-toast'
import { FiArrowLeft } from 'react-icons/fi'

export default function PlanTrip() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [itinerary, setItinerary] = useState(null)
  const [loading, setLoading]     = useState(false)
  const [saving, setSaving]       = useState(false)

  const handleGenerate = async (formData) => {
    setLoading(true)
    setItinerary(null)
    try {
      const { data } = await tripService.generateItinerary(formData)
      setItinerary({ ...data, _formData: formData })
      toast.success('Itinerary generated! 🎉')
      // Scroll to results
      setTimeout(() => {
        document.getElementById('itinerary-result')?.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    } catch (err) {
      toast.error('Failed to generate itinerary. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!itinerary) return
    setSaving(true)
    try {
      const payload = {
        title: itinerary.title,
        start_location: itinerary.start_location,
        end_location:   itinerary.end_location,
        travel_days:    itinerary.travel_days,
        budget:         itinerary.total_budget,
        transport_mode: itinerary.transport_mode,
        group_size:     itinerary.group_size,
        itinerary:      itinerary,
      }
      const { data } = await tripService.saveTrip(payload)
      toast.success('Trip saved! ✅')
      navigate(`/trip/${data.id}`)
    } catch {
      toast.error('Failed to save trip.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => navigate(-1)}
            className="p-2 rounded-xl hover:bg-gray-100 transition-colors text-gray-500">
            <FiArrowLeft size={20} />
          </button>
          <div>
            <h1 className="font-display text-2xl font-bold text-gray-900">Plan Your Trip</h1>
            <p className="text-gray-500 text-sm">Fill in your preferences — our AI will do the rest</p>
          </div>
        </div>

        {/* Form card */}
        <div className="card p-6 md:p-8">
          <div className="flex items-center gap-3 mb-6 pb-6 border-b border-gray-100">
            <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center text-xl">✨</div>
            <div>
              <h2 className="font-semibold text-gray-900">AI Trip Planner</h2>
              <p className="text-xs text-gray-500">Powered by ML recommendation engine</p>
            </div>
          </div>
          <TripPlannerForm onSubmit={handleGenerate} loading={loading} />
        </div>

        {/* Itinerary result */}
        {loading && (
          <div className="mt-8 card p-12 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-primary-100 border-t-primary-600 animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center text-2xl">✨</div>
              </div>
              <div>
                <p className="font-semibold text-gray-900">Generating your AI itinerary...</p>
                <p className="text-sm text-gray-500 mt-1">
                  Running recommendations → route optimization → weather check → hotel matching
                </p>
              </div>
            </div>
          </div>
        )}

        {itinerary && !loading && (
          <div id="itinerary-result" className="mt-8">
            <ItineraryView
              itinerary={itinerary}
              onSave={handleSave}
              saving={saving}
            />
          </div>
        )}
      </div>
    </PageLayout>
  )
}
