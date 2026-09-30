/**
 * Voyage AI – MapView
 * Uses React-Leaflet + OpenStreetMap tiles.
 * Completely free — no API key required.
 *
 * Features:
 *  - Tourist place markers (numbered, indigo)
 *  - Hotel markers (green)
 *  - Restaurant markers (orange)
 *  - Optimised route polyline
 *  - Click-to-open info popups
 *  - Auto-fit bounds to all markers
 */
import { useEffect, useRef } from 'react'
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// ── Fix Leaflet's broken default icon paths in Vite/Webpack ──────────────
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// ── Custom SVG marker factory ─────────────────────────────────────────────
function makeIcon(color, label = '') {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="42" viewBox="0 0 32 42">
      <ellipse cx="16" cy="40" rx="6" ry="2.5" fill="rgba(0,0,0,0.25)"/>
      <path d="M16 0 C7.16 0 0 7.16 0 16 C0 28 16 42 16 42 C16 42 32 28 32 16 C32 7.16 24.84 0 16 0Z"
            fill="${color}" stroke="white" stroke-width="2"/>
      <text x="16" y="20" text-anchor="middle" dominant-baseline="middle"
            font-family="Inter,sans-serif" font-size="11" font-weight="bold" fill="white">
        ${label}
      </text>
    </svg>`
  return L.divIcon({
    html: svg,
    iconSize:   [32, 42],
    iconAnchor: [16, 42],
    popupAnchor:[0, -44],
    className:  '',
  })
}

const PLACE_COLOR      = '#4F46E5'   // indigo
const HOTEL_COLOR      = '#10B981'   // emerald
const RESTAURANT_COLOR = '#F59E0B'   // amber

// ── Auto-fit bounds when markers change ──────────────────────────────────
function FitBounds({ positions }) {
  const map = useMap()
  useEffect(() => {
    if (positions.length === 0) return
    if (positions.length === 1) {
      map.setView(positions[0], 13)
      return
    }
    const bounds = L.latLngBounds(positions)
    map.fitBounds(bounds, { padding: [48, 48], maxZoom: 14 })
  }, [positions, map])
  return null
}

// ── Main component ────────────────────────────────────────────────────────
export default function MapView({
  places      = [],
  hotels      = [],
  restaurants = [],
  center,
  zoom        = 11,
  showRoute   = true,
}) {
  // Default centre: India
  const defaultCenter = center
    ? [center.lat, center.lng]
    : [20.5937, 78.9629]

  // All valid coordinates for FitBounds
  const allPositions = [
    ...places.filter(p => p.latitude && p.longitude).map(p => [+p.latitude, +p.longitude]),
    ...hotels.filter(h => h.latitude && h.longitude).map(h => [+h.latitude, +h.longitude]),
  ]

  // Route polyline — connect places in order
  const routePoints = places
    .filter(p => p.latitude && p.longitude)
    .map(p => [+p.latitude, +p.longitude])

  return (
    <div className="w-full h-full min-h-[420px] rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
      <MapContainer
        center={defaultCenter}
        zoom={zoom}
        style={{ height: '100%', width: '100%', minHeight: '420px' }}
        scrollWheelZoom
      >
        {/* OpenStreetMap tile layer — completely free, no key */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
          maxZoom={19}
        />

        {/* Auto-fit to all markers */}
        {allPositions.length > 0 && <FitBounds positions={allPositions} />}

        {/* Route polyline */}
        {showRoute && routePoints.length > 1 && (
          <Polyline
            positions={routePoints}
            pathOptions={{
              color: '#4F46E5',
              weight: 3,
              opacity: 0.75,
              dashArray: '8 4',
            }}
          />
        )}

        {/* Tourist place markers */}
        {places.map((place, i) => {
          if (!place.latitude || !place.longitude) return null
          return (
            <Marker
              key={`place-${i}`}
              position={[+place.latitude, +place.longitude]}
              icon={makeIcon(PLACE_COLOR, i + 1)}
            >
              <Popup maxWidth={240}>
                <div className="font-sans text-sm">
                  <p className="font-bold text-indigo-700 text-base leading-tight">
                    {place.name}
                  </p>
                  <p className="text-gray-500 text-xs mt-0.5">{place.city}</p>
                  {place.category && (
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-full bg-indigo-50
                                     text-indigo-600 text-xs font-medium capitalize">
                      {place.category}
                    </span>
                  )}
                  {place.rating > 0 && (
                    <p className="text-yellow-500 text-xs mt-1">⭐ {place.rating}</p>
                  )}
                  {place.entry_fee > 0 && (
                    <p className="text-gray-500 text-xs">🎫 Entry: ₹{place.entry_fee}</p>
                  )}
                  {place.opening_hours && (
                    <p className="text-gray-500 text-xs">🕐 {place.opening_hours}</p>
                  )}
                  {place.description && (
                    <p className="text-gray-600 text-xs mt-1 line-clamp-3">
                      {place.description}
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          )
        })}

        {/* Hotel markers */}
        {hotels.map((hotel, i) => {
          if (!hotel.latitude || !hotel.longitude) return null
          return (
            <Marker
              key={`hotel-${i}`}
              position={[+hotel.latitude, +hotel.longitude]}
              icon={makeIcon(HOTEL_COLOR, '🏨')}
            >
              <Popup maxWidth={220}>
                <div className="font-sans text-sm">
                  <p className="font-bold text-emerald-700 text-base leading-tight">
                    {hotel.name}
                  </p>
                  <p className="text-gray-500 text-xs mt-0.5">{hotel.city}</p>
                  <p className="text-yellow-500 text-xs">
                    {'⭐'.repeat(hotel.star_rating || 3)}
                  </p>
                  {hotel.price_per_night && (
                    <p className="text-gray-700 text-xs font-medium mt-1">
                      ₹{Number(hotel.price_per_night).toLocaleString('en-IN')}/night
                    </p>
                  )}
                  {hotel.phone && (
                    <p className="text-gray-500 text-xs">📞 {hotel.phone}</p>
                  )}
                </div>
              </Popup>
            </Marker>
          )
        })}

        {/* Restaurant markers */}
        {restaurants.map((r, i) => {
          if (!r.latitude || !r.longitude) return null
          return (
            <Marker
              key={`rest-${i}`}
              position={[+r.latitude, +r.longitude]}
              icon={makeIcon(RESTAURANT_COLOR, '🍽️')}
            >
              <Popup maxWidth={220}>
                <div className="font-sans text-sm">
                  <p className="font-bold text-amber-700 text-base leading-tight">
                    {r.name}
                  </p>
                  <p className="text-gray-500 text-xs mt-0.5">{r.city}</p>
                  {r.cuisine && (
                    <p className="text-gray-600 text-xs">{r.cuisine}</p>
                  )}
                  {r.rating > 0 && (
                    <p className="text-yellow-500 text-xs">⭐ {r.rating}</p>
                  )}
                  {r.avg_cost_for_two && (
                    <p className="text-gray-700 text-xs font-medium mt-1">
                      ₹{Number(r.avg_cost_for_two).toLocaleString('en-IN')} for two
                    </p>
                  )}
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
