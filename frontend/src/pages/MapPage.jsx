import { useState, useEffect, useRef } from 'react'
import PageLayout from '../components/layout/PageLayout'
import MapView from '../components/map/MapView'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import PlaceCard from '../components/common/PlaceCard'
import { FiSearch, FiMapPin } from 'react-icons/fi'

const CATEGORIES = ['all', 'beach', 'nature', 'monument', 'temple', 'museum', 'adventure', 'park', 'heritage', 'waterfall']

const QUICK_CITIES = [
  'Mumbai', 'Goa', 'Jaipur', 'Delhi', 'Chennai',
  'Hyderabad', 'Bangalore', 'Kolkata', 'Agra', 'Kerala',
  'Varanasi', 'Mysore', 'Pondicherry', 'Shimla', 'Manali',
]

export default function MapPage() {
  const [places,      setPlaces]      = useState([])
  const [hotels,      setHotels]      = useState([])
  const [restaurants, setRestaurants] = useState([])
  const [loading,     setLoading]     = useState(true)
  const [city,        setCity]        = useState('')
  const [inputCity,   setInputCity]   = useState('')
  const [category,    setCategory]    = useState('all')
  const [search,      setSearch]      = useState('')

  const fetchData = async (cityValue, categoryValue) => {
    setLoading(true)
    try {
      const params = { limit: 40 }
      if (cityValue)               params.city     = cityValue
      if (categoryValue !== 'all') params.category = categoryValue

      const pRes = await api.get('/recommend/places', { params })
      setPlaces(pRes.data || [])

      const [hRes, rRes] = await Promise.allSettled([
        api.get('/recommend/hotels',      { params: { city: cityValue, limit: 10 } }),
        api.get('/recommend/restaurants', { params: { city: cityValue, limit: 10 } }),
      ])
      if (hRes.status === 'fulfilled') setHotels(hRes.value.data || [])
      if (rRes.status === 'fulfilled') setRestaurants(rRes.value.data || [])
    } catch (err) {
      console.error('Map fetch error:', err)
      setPlaces([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData('', 'all') }, [])

  useEffect(() => {
    if (city !== '' || category !== 'all') {
      fetchData(city, category)
    }
  }, [city, category])

  const handleCitySearch = () => setCity(inputCity.trim())
  const handleQuickCity  = (c) => { setInputCity(c); setCity(c) }

  const filtered = places.filter(p =>
    !search || p.name?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <PageLayout className="!py-0 !px-0">
      <div className="flex flex-col lg:flex-row h-[calc(100vh-64px)]">

        {/* ── Sidebar ─────────────────────────────────────────── */}
        <div className="lg:w-96 flex flex-col border-r border-gray-200 bg-white overflow-hidden">
          <div className="p-4 border-b border-gray-100 space-y-3">
            <h2 className="font-display font-bold text-lg text-gray-900">🗺️ Explore India</h2>

            {/* Place search */}
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" />
              <input
                type="text"
                className="input-field pl-9 text-sm py-2.5"
                placeholder="Search places by name..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>

            {/* City search */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <FiMapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" />
                <input
                  type="text"
                  className="input-field pl-9 text-sm py-2.5"
                  placeholder="Any city in India..."
                  value={inputCity}
                  onChange={e => setInputCity(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleCitySearch()}
                />
              </div>
              <button
                onClick={handleCitySearch}
                disabled={loading}
                className="px-3 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium
                           hover:bg-primary-700 transition-colors disabled:opacity-50 flex-shrink-0"
              >
                Go
              </button>
            </div>

            {/* Active city chip */}
            {city && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Showing results for:</span>
                <span className="flex items-center gap-1 bg-primary-50 text-primary-700
                                 px-2.5 py-1 rounded-full text-xs font-medium">
                  📍 {city}
                  <button
                    onClick={() => { setCity(''); setInputCity(''); fetchData('', category) }}
                    className="ml-1 text-primary-400 hover:text-primary-700"
                  >×</button>
                </span>
              </div>
            )}

            {/* Quick city chips */}
            <div>
              <p className="text-xs text-gray-400 mb-1.5">Quick select:</p>
              <div className="flex flex-wrap gap-1.5">
                {QUICK_CITIES.map(c => (
                  <button
                    key={c}
                    onClick={() => handleQuickCity(c)}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors border
                      ${city === c
                        ? 'bg-primary-600 text-white border-primary-600'
                        : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300 hover:bg-primary-50'}`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Category filter */}
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                    ${category === cat
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-3 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 inline-block" />
                Places ({filtered.length})
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
                Hotels ({hotels.length})
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
                Restaurants ({restaurants.length})
              </span>
            </div>
          </div>

          {/* Place list */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {loading ? (
              <div className="flex items-center justify-center py-10">
                <LoadingSpinner />
              </div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-10 text-gray-400">
                <div className="text-4xl mb-2">🔍</div>
                <p className="text-sm font-medium">No places found</p>
                <p className="text-xs mt-1">Try a different city or category</p>
              </div>
            ) : (
              filtered.map((p, i) => (
                <PlaceCard key={p.id || i} place={p} rank={i + 1} />
              ))
            )}
          </div>
        </div>

        {/* ── Map ─────────────────────────────────────────────── */}
        <div className="flex-1 relative">
          <MapView
            places={filtered}
            hotels={hotels}
            restaurants={restaurants}
            showRoute={false}
          />
          <div className="absolute bottom-8 left-3 z-[1000]
                          bg-white/90 backdrop-blur rounded-lg px-3 py-1.5
                          text-xs text-gray-500 shadow pointer-events-none">
            🗺️ OpenStreetMap · Free &amp; Open
          </div>
        </div>
      </div>
    </PageLayout>
  )
}
