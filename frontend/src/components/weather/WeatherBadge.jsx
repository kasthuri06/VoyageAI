import clsx from 'clsx'

export default function WeatherBadge({ weather, className }) {
  if (!weather) return null
  const isBad = weather.is_bad_weather
  return (
    <span className={clsx(
      'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium',
      isBad ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700',
      className
    )}>
      {isBad ? '🌧️' : '☀️'}
      {weather.description || (isBad ? 'Rain expected' : 'Clear')}
      {weather.temperature && ` · ${weather.temperature}°C`}
    </span>
  )
}
