import { useState } from 'react'
import { FiMapPin, FiCalendar, FiDollarSign, FiUsers, FiNavigation } from 'react-icons/fi'
import clsx from 'clsx'

const INTERESTS = [
  { id: 'adventure',  label: '🏔️ Adventure' },
  { id: 'nature',     label: '🌿 Nature' },
  { id: 'beach',      label: '🏖️ Beach' },
  { id: 'temple',     label: '🛕 Temple' },
  { id: 'museum',     label: '🏛️ Museum' },
  { id: 'shopping',   label: '🛍️ Shopping' },
  { id: 'food',       label: '🍜 Food' },
  { id: 'luxury',     label: '💎 Luxury' },
  { id: 'family',     label: '👨‍👩‍👧 Family' },
  { id: 'romantic',   label: '💑 Romantic' },
  { id: 'wildlife',   label: '🐾 Wildlife' },
  { id: 'history',    label: '🏰 History' },
]

const TRANSPORT_MODES = ['car', 'bike', 'walk', 'public', 'flight']
const TRAVEL_STYLES   = ['solo', 'couple', 'family', 'group']
const TRAVEL_TIMES    = ['morning', 'afternoon', 'evening']

const defaultForm = {
  start_location: '',
  end_location: '',
  travel_days: 3,
  budget: 15000,
  transport_mode: 'car',
  interests: [],
  group_size: 1,
  preferred_hotel_rating: 3,
  travel_style: 'solo',
  preferred_travel_time: 'morning',
}

export default function TripPlannerForm({ onSubmit, loading }) {
  const [form, setForm] = useState(defaultForm)

  const set = (key, val) => setForm(prev => ({ ...prev, [key]: val }))

  const toggleInterest = (id) => {
    set('interests', form.interests.includes(id)
      ? form.interests.filter(i => i !== id)
      : [...form.interests, id]
    )
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.start_location || !form.end_location) return
    if (form.interests.length === 0) return
    onSubmit(form)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Locations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="label">Starting Location</label>
          <div className="relative">
            <FiMapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              className="input-field pl-10"
              placeholder="e.g. Mumbai"
              value={form.start_location}
              onChange={e => set('start_location', e.target.value)}
              required
            />
          </div>
        </div>
        <div>
          <label className="label">Destination</label>
          <div className="relative">
            <FiNavigation className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              className="input-field pl-10"
              placeholder="e.g. Goa"
              value={form.end_location}
              onChange={e => set('end_location', e.target.value)}
              required
            />
          </div>
        </div>
      </div>

      {/* Days & Budget */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="label">
            <FiCalendar className="inline mr-1" /> Travel Days
          </label>
          <input
            type="number" min={1} max={30}
            className="input-field"
            value={form.travel_days}
            onChange={e => set('travel_days', parseInt(e.target.value))}
          />
        </div>
        <div>
          <label className="label">
            <FiDollarSign className="inline mr-1" /> Total Budget (₹)
          </label>
          <input
            type="number" min={1000}
            className="input-field"
            value={form.budget}
            onChange={e => set('budget', parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label className="label">
            <FiUsers className="inline mr-1" /> Group Size
          </label>
          <input
            type="number" min={1} max={50}
            className="input-field"
            value={form.group_size}
            onChange={e => set('group_size', parseInt(e.target.value))}
          />
        </div>
      </div>

      {/* Interests */}
      <div>
        <label className="label">Interests <span className="text-red-500">*</span></label>
        <p className="text-xs text-gray-500 mb-3">Select at least one interest for personalised recommendations</p>
        <div className="flex flex-wrap gap-2">
          {INTERESTS.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => toggleInterest(id)}
              className={clsx(
                'px-4 py-2 rounded-xl text-sm font-medium border-2 transition-all duration-150',
                form.interests.includes(id)
                  ? 'bg-primary-600 border-primary-600 text-white shadow-md'
                  : 'bg-white border-gray-200 text-gray-700 hover:border-primary-300 hover:bg-primary-50'
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Transport & Style */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="label">Transport Mode</label>
          <select className="input-field" value={form.transport_mode}
            onChange={e => set('transport_mode', e.target.value)}>
            {TRANSPORT_MODES.map(m => (
              <option key={m} value={m}>{m.charAt(0).toUpperCase() + m.slice(1)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Travel Style</label>
          <select className="input-field" value={form.travel_style}
            onChange={e => set('travel_style', e.target.value)}>
            {TRAVEL_STYLES.map(s => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Preferred Travel Time</label>
          <select className="input-field" value={form.preferred_travel_time}
            onChange={e => set('preferred_travel_time', e.target.value)}>
            {TRAVEL_TIMES.map(t => (
              <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Hotel Rating */}
      <div>
        <label className="label">Minimum Hotel Rating</label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map(n => (
            <button
              key={n} type="button"
              onClick={() => set('preferred_hotel_rating', n)}
              className={clsx(
                'px-4 py-2 rounded-xl text-sm font-medium border-2 transition-all',
                form.preferred_hotel_rating === n
                  ? 'bg-gold-500 border-gold-500 text-white'
                  : 'bg-white border-gray-200 text-gray-600 hover:border-gold-300'
              )}
            >
              {'⭐'.repeat(n)}
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
      <button type="submit" disabled={loading || form.interests.length === 0}
        className="btn-primary w-full py-4 text-base">
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white" />
            Generating Your AI Itinerary...
          </span>
        ) : '✨ Generate AI Itinerary'}
      </button>
    </form>
  )
}
