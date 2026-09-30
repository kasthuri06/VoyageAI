import { FiMapPin, FiStar, FiClock, FiDollarSign } from 'react-icons/fi'
import clsx from 'clsx'

const CATEGORY_COLORS = {
  beach:    'bg-cyan-100 text-cyan-700',
  nature:   'bg-green-100 text-green-700',
  monument: 'bg-amber-100 text-amber-700',
  temple:   'bg-orange-100 text-orange-700',
  museum:   'bg-purple-100 text-purple-700',
  adventure:'bg-red-100 text-red-700',
  default:  'bg-gray-100 text-gray-600',
}

export default function PlaceCard({ place, rank, onClick }) {
  const catColor = CATEGORY_COLORS[place.category] || CATEGORY_COLORS.default

  return (
    <div
      className="card cursor-pointer hover:scale-[1.02] transition-transform duration-200"
      onClick={() => onClick?.(place)}
    >
      {/* Image */}
      <div className="relative h-44 bg-gradient-to-br from-primary-100 to-primary-200 overflow-hidden">
        {place.image_url ? (
          <img
            src={place.image_url}
            alt={place.name}
            className="w-full h-full object-cover"
            onError={e => { e.target.style.display = 'none' }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-5xl">
            {place.category === 'beach' ? '🏖️'
            : place.category === 'temple' ? '🛕'
            : place.category === 'museum' ? '🏛️'
            : place.category === 'nature' ? '🌿'
            : '🗺️'}
          </div>
        )}
        {rank && (
          <div className="absolute top-3 left-3 w-7 h-7 rounded-full bg-primary-600 text-white
                          text-xs font-bold flex items-center justify-center shadow">
            {rank}
          </div>
        )}
        <span className={clsx('absolute top-3 right-3 badge text-xs font-medium', catColor)}>
          {place.category}
        </span>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-1">{place.name}</h3>
        <div className="flex items-center gap-1 text-gray-500 text-sm mt-1">
          <FiMapPin className="text-xs flex-shrink-0" />
          <span className="line-clamp-1">{place.city}</span>
        </div>
        {place.description && (
          <p className="text-xs text-gray-500 mt-2 line-clamp-2">{place.description}</p>
        )}

        <div className="flex items-center gap-3 mt-3">
          <div className="flex items-center gap-1 text-gold-500">
            <FiStar className="text-xs fill-current" />
            <span className="text-sm font-medium">{place.rating}</span>
          </div>
          {place.estimated_duration_hours && (
            <div className="flex items-center gap-1 text-gray-400">
              <FiClock className="text-xs" />
              <span className="text-xs">{place.estimated_duration_hours}h</span>
            </div>
          )}
          {place.entry_fee > 0 && (
            <div className="flex items-center gap-1 text-gray-400">
              <FiDollarSign className="text-xs" />
              <span className="text-xs">₹{place.entry_fee}</span>
            </div>
          )}
          {place.is_indoor && (
            <span className="badge bg-blue-50 text-blue-600 text-xs">Indoor</span>
          )}
        </div>

        {/* Tags */}
        {place.tags?.length > 0 && (
          <div className="flex gap-1 flex-wrap mt-2">
            {place.tags.slice(0, 3).map(tag => (
              <span key={tag} className="badge bg-gray-100 text-gray-500 text-xs">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
