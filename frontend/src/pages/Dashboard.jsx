import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import { useAuth } from '../context/AuthContext'
import { tripService } from '../services/tripService'
import LoadingSpinner from '../components/common/LoadingSpinner'
import WeatherBadge from '../components/weather/WeatherBadge'
import { FiPlus, FiMapPin, FiCalendar, FiTrendingUp, FiBookmark } from 'react-icons/fi'

const QUICK_DESTINATIONS = [
  { name: 'Goa',    emoji: '🏖️', interests: ['beach', 'food', 'nightlife'] },
  { name: 'Jaipur', emoji: '🏰', interests: ['history', 'heritage', 'shopping'] },
  { name: 'Munnar', emoji: '🌿', interests: ['nature', 'trekking', 'scenic'] },
  { name: 'Leh',    emoji: '🏔️', interests: ['adventure', 'nature', 'solo'] },
]

export default function Dashboard() {
  const { user } = useAuth()
  const [recentTrips, setRecentTrips] = useState([])
  const [weather, setWeather]         = useState(null)
  const [loading, setLoading]         = useState(true)
  const [weatherCity, setWeatherCity] = useState('')

  // Resolve weather city: browser geolocation → last trip destination → 'Delhi'
  const resolveWeatherCity = async (trips) => {
    // 1. Try last trip's destination
    if (trips.length > 0 && trips[0].end_location) {
      return trips[0].end_location
    }
    // 2. Try browser geolocation → reverse geocode
    if (navigator.geolocation) {
      try {
        const pos = await new Promise((res, rej) =>
          navigator.geolocation.getCurrentPosition(res, rej, { timeout: 5000 })
        )
        const { latitude, longitude } = pos.coords
        const r = await fetch(
          `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
        )
        const data = await r.json()
        const city =
          data.address?.city ||
          data.address?.town ||
          data.address?.village ||
          data.address?.county
        if (city) return city
      } catch {
        // geolocation denied or failed — fall through
      }
    }
    // 3. Generic fallback
    return 'Delhi'
  }

  useEffect(() => {
    const load = async () => {
      try {
        const [tripsRes] = await Promise.allSettled([tripService.listTrips()])
        const trips = tripsRes.status === 'fulfilled' ? tripsRes.value.data.slice(0, 4) : []
        setRecentTrips(trips)

        const city = await resolveWeatherCity(trips)
        setWeatherCity(city)
        const w = await tripService.getWeather(city)
        setWeather(w.data)
      } catch {
        // weather is non-critical — silent fail
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <PageLayout>
      {/* Welcome */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-gray-900">
            {greeting}, {user?.full_name?.split(' ')[0] || user?.username}! 👋
          </h1>
          <p className="text-gray-500 mt-1">Where are you travelling next?</p>
        </div>
        <Link to="/plan" className="btn-primary">
          <FiPlus /> Plan New Trip
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Trips',    value: recentTrips.length, icon: FiMapPin,    color: 'text-primary-600 bg-primary-50' },
          { label: 'Saved Trips',    value: recentTrips.filter(t => t.is_saved).length, icon: FiBookmark, color: 'text-green-600 bg-green-50' },
          { label: 'Days Travelled', value: recentTrips.reduce((a, t) => a + (t.travel_days || 0), 0), icon: FiCalendar, color: 'text-amber-600 bg-amber-50' },
          { label: 'Total Spent',    value: `₹${recentTrips.reduce((a, t) => a + (t.total_cost || 0), 0).toLocaleString('en-IN')}`, icon: FiTrendingUp, color: 'text-purple-600 bg-purple-50' },
        ].map(stat => (
          <div key={stat.label} className="card p-5">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${stat.color}`}>
              <stat.icon />
            </div>
            <div className="text-2xl font-bold text-gray-900">{loading ? '—' : stat.value}</div>
            <div className="text-sm text-gray-500">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Plan */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">Quick Destinations</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {QUICK_DESTINATIONS.map(d => (
              <Link
                key={d.name}
                to={`/plan?destination=${d.name}`}
                className="card p-4 text-center hover:scale-105 transition-transform"
              >
                <div className="text-4xl mb-2">{d.emoji}</div>
                <p className="font-semibold text-gray-900 text-sm">{d.name}</p>
                <div className="flex flex-wrap gap-1 justify-center mt-2">
                  {d.interests.slice(0, 2).map(i => (
                    <span key={i} className="badge bg-primary-50 text-primary-600 text-xs">{i}</span>
                  ))}
                </div>
              </Link>
            ))}
          </div>

          {/* Recent trips */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title">Recent Trips</h2>
              <Link to="/saved" className="text-sm text-primary-600 hover:underline">View all</Link>
            </div>
            {loading ? (
              <div className="flex justify-center py-8"><LoadingSpinner /></div>
            ) : recentTrips.length === 0 ? (
              <div className="card p-10 text-center">
                <div className="text-5xl mb-3">🗺️</div>
                <p className="text-gray-500">No trips yet. Plan your first adventure!</p>
                <Link to="/plan" className="btn-primary mt-4 inline-flex">
                  <FiPlus /> Plan a Trip
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recentTrips.map(trip => (
                  <Link key={trip.id} to={`/trip/${trip.id}`}
                    className="card p-4 flex items-center justify-between hover:border hover:border-primary-200 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center text-xl">
                        🗺️
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">{trip.title}</p>
                        <p className="text-xs text-gray-500">
                          {trip.start_location} → {trip.end_location} · {trip.travel_days}d
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`badge text-xs ${
                        trip.status === 'completed' ? 'bg-green-100 text-green-700'
                        : trip.status === 'active'  ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-600'
                      }`}>{trip.status}</span>
                      <p className="text-xs text-gray-400 mt-1">
                        ₹{trip.total_cost?.toLocaleString('en-IN')}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Weather widget */}
        <div>
          <h2 className="section-title mb-4">Weather</h2>

          {/* City search */}
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              className="input-field text-sm py-2"
              placeholder="Enter city..."
              defaultValue={weatherCity}
              key={weatherCity}
              onKeyDown={async (e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  try {
                    const w = await tripService.getWeather(e.target.value.trim())
                    setWeather(w.data)
                    setWeatherCity(e.target.value.trim())
                  } catch {}
                }
              }}
            />
            <button
              className="px-3 py-2 bg-primary-600 text-white rounded-xl text-sm hover:bg-primary-700 transition-colors flex-shrink-0"
              onClick={async (e) => {
                const input = e.currentTarget.previousSibling
                if (input.value.trim()) {
                  try {
                    const w = await tripService.getWeather(input.value.trim())
                    setWeather(w.data)
                    setWeatherCity(input.value.trim())
                  } catch {}
                }
              }}
            >
              Go
            </button>
          </div>

          {weather ? (
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-900">{weather.city}</p>
                  <p className="text-4xl font-bold text-primary-700 mt-1">{weather.temperature}°C</p>
                  <p className="text-gray-500 text-sm mt-1">{weather.description}</p>
                </div>
                <div className="text-5xl">
                  {weather.is_bad_weather ? '🌧️' : '☀️'}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-50 rounded-xl p-3 text-center">
                  <p className="text-gray-400 text-xs">Humidity</p>
                  <p className="font-semibold">{weather.humidity}%</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-3 text-center">
                  <p className="text-gray-400 text-xs">Wind</p>
                  <p className="font-semibold">{weather.wind_speed} m/s</p>
                </div>
              </div>
              {weather.is_bad_weather && (
                <div className="mt-3 p-3 bg-blue-50 rounded-xl text-xs text-blue-700">
                  🌧️ Rain expected — we'll recommend indoor attractions today
                </div>
              )}
            </div>
          ) : (
            <div className="card p-6 flex items-center justify-center h-40">
              <LoadingSpinner />
            </div>
          )}

          {/* Tips */}
          <div className="card p-5 mt-4">
            <h3 className="font-semibold text-gray-900 mb-3">✨ AI Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex gap-2"><span>🗓️</span> Book trips 2–3 weeks ahead for best hotel rates</li>
              <li className="flex gap-2"><span>☀️</span> Oct–Feb is peak season for most Indian destinations</li>
              <li className="flex gap-2"><span>💰</span> Our AI auto-optimises your budget across days</li>
            </ul>
          </div>
        </div>
      </div>
    </PageLayout>
  )
}
