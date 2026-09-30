import { useState } from 'react'
import { FiSun, FiClock, FiDollarSign, FiMapPin, FiCloudRain, FiStar } from 'react-icons/fi'
import clsx from 'clsx'
import WeatherBadge from '../weather/WeatherBadge'

const SLOT_ICONS  = { morning: '🌅', afternoon: '☀️', evening: '🌆', night: '🌙' }
const SLOT_COLORS = {
  morning:   'bg-amber-50   border-amber-200',
  afternoon: 'bg-orange-50  border-orange-200',
  evening:   'bg-purple-50  border-purple-200',
  night:     'bg-indigo-50  border-indigo-200',
}

export default function ItineraryView({ itinerary, onSave, saving }) {
  const [activeDay, setActiveDay] = useState(1)

  if (!itinerary?.days?.length) return null

  const day = itinerary.days.find(d => d.day === activeDay) || itinerary.days[0]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Summary banner */}
      <div className="card p-6 bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="font-display text-2xl font-bold">{itinerary.title}</h2>
            <p className="text-primary-200 mt-1">
              {itinerary.start_location} → {itinerary.end_location} ·
              {itinerary.travel_days} days · {itinerary.group_size} pax
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">
              ₹{itinerary.estimated_total_cost?.toLocaleString('en-IN')}
            </div>
            <div className="text-primary-200 text-sm">Estimated cost</div>
            <div className="text-primary-300 text-xs">
              Budget: ₹{itinerary.total_budget?.toLocaleString('en-IN')}
            </div>
          </div>
        </div>

        {/* Stat pills */}
        <div className="flex flex-wrap gap-3 mt-4">
          {itinerary.transport_mode && (
            <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
              🚗 {itinerary.transport_mode}
            </span>
          )}
          {itinerary.route_summary?.total_distance_km > 0 && (
            <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
              📍 {itinerary.route_summary.total_distance_km} km total
            </span>
          )}
          {itinerary.weather_summary && (
            <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
              ☁️ Avg rain: {Math.round((itinerary.weather_summary.avg_rain_probability || 0) * 100)}%
            </span>
          )}
        </div>
      </div>

      {/* Day selector */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {itinerary.days.map(d => (
          <button
            key={d.day}
            onClick={() => setActiveDay(d.day)}
            className={clsx(
              'flex-shrink-0 px-4 py-2.5 rounded-xl text-sm font-medium transition-all border',
              activeDay === d.day
                ? 'bg-primary-600 text-white border-primary-600 shadow-md'
                : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300'
            )}
          >
            <div>Day {d.day}</div>
            {d.date && <div className="text-xs opacity-70">{d.date}</div>}
          </button>
        ))}
      </div>

      {/* Day card */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-display font-semibold text-lg">
            Day {day.day} — {day.date || ''}
          </h3>
          <div className="flex items-center gap-3">
            {day.weather && <WeatherBadge weather={day.weather} />}
            <span className="badge bg-green-100 text-green-700">
              ₹{day.estimated_cost?.toLocaleString('en-IN')} est.
            </span>
          </div>
        </div>

        {/* Slots */}
        <div className="space-y-3">
          {day.slots?.map((slot, idx) => (
            <div key={idx}
              className={clsx('rounded-xl border p-4', SLOT_COLORS[slot.time_slot])}>
              <div className="flex items-start gap-3">
                <div className="text-2xl">{SLOT_ICONS[slot.time_slot]}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold capitalize text-gray-800">
                      {slot.time_slot}
                    </span>
                    {slot.time_range && (
                      <span className="text-xs text-gray-500">{slot.time_range}</span>
                    )}
                    {slot.travel_time_minutes > 0 && (
                      <span className="badge bg-white/70 text-gray-600 text-xs">
                        🚗 {slot.travel_time_minutes}m travel
                      </span>
                    )}
                  </div>

                  {/* Place */}
                  {slot.place && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2">
                        <FiMapPin className="text-primary-500 text-sm flex-shrink-0" />
                        <span className="font-medium text-gray-900">{slot.place.name}</span>
                        <div className="flex items-center gap-0.5 text-gold-500 text-xs">
                          <FiStar className="fill-current" />
                          <span>{slot.place.rating}</span>
                        </div>
                      </div>
                      {slot.place.description && (
                        <p className="text-sm text-gray-600 mt-1 ml-5 line-clamp-2">
                          {slot.place.description}
                        </p>
                      )}
                      {slot.notes && (
                        <p className="text-xs text-gray-500 mt-1 ml-5">{slot.notes}</p>
                      )}
                      {slot.place.entry_fee > 0 && (
                        <span className="ml-5 text-xs text-amber-600">
                          🎫 Entry: ₹{slot.place.entry_fee}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Hotel (night) */}
                  {slot.hotel && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">🏨</span>
                        <span className="font-medium">{slot.hotel.name}</span>
                        <span className="badge bg-white text-yellow-600">
                          {'⭐'.repeat(slot.hotel.star_rating || 3)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 ml-5">
                        ₹{slot.hotel.price_per_night?.toLocaleString('en-IN')}/night
                      </p>
                    </div>
                  )}

                  {/* Nearby restaurants */}
                  {slot.nearby_restaurants?.length > 0 && (
                    <div className="mt-2 ml-5">
                      <p className="text-xs text-gray-500 font-medium mb-1">Nearby eats:</p>
                      <div className="flex gap-2 flex-wrap">
                        {slot.nearby_restaurants.map((r, i) => (
                          <span key={i} className="badge bg-white text-gray-600 border border-gray-200 text-xs">
                            🍽️ {r.name} · {r.distance_km}km
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {!slot.place && !slot.hotel && (
                    <p className="text-sm text-gray-500 italic mt-1">{slot.notes || 'Free time'}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Hotels */}
      {itinerary.recommended_hotels?.length > 0 && (
        <div className="card p-6">
          <h3 className="font-display font-semibold text-lg mb-4">🏨 Recommended Hotels</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {itinerary.recommended_hotels.slice(0, 3).map((h, i) => (
              <div key={i} className="border border-gray-100 rounded-xl p-4 hover:border-primary-200 transition-colors">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-sm text-gray-900">{h.name}</p>
                    <p className="text-xs text-gray-500">{h.city}</p>
                    <p className="text-xs text-yellow-600 mt-0.5">{'⭐'.repeat(h.star_rating || 3)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-primary-700">
                      ₹{h.price_per_night?.toLocaleString('en-IN')}
                    </p>
                    <p className="text-xs text-gray-400">per night</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Save button */}
      {onSave && (
        <button onClick={onSave} disabled={saving} className="btn-primary w-full py-4">
          {saving ? '💾 Saving...' : '💾 Save This Trip'}
        </button>
      )}
    </div>
  )
}
