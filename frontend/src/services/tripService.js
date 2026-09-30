import api from './api'

export const tripService = {
  /** Run the full ML pipeline and get an itinerary */
  generateItinerary: (payload) => api.post('/recommend/itinerary', payload),

  /** Save the generated itinerary as a trip */
  saveTrip: (payload) => api.post('/trips/', payload),

  /** List all trips */
  listTrips: (status) => api.get('/trips/', { params: { status } }),

  /** Get single trip with full itinerary */
  getTrip: (id) => api.get(`/trips/${id}`),

  /** Toggle saved flag */
  toggleSave: (id) => api.put(`/trips/${id}/save`),

  /** Delete trip */
  deleteTrip: (id) => api.delete(`/trips/${id}`),

  /** Update status */
  updateStatus: (id, status) => api.put(`/trips/${id}/status`, null, { params: { status } }),

  /** Get weather for city */
  getWeather: (city) => api.get('/weather/current', { params: { city } }),

  /** Get forecast */
  getForecast: (city, days = 5) => api.get('/weather/forecast', { params: { city, days } }),

  /** Get places */
  getPlaces: (params) => api.get('/recommend/places', { params }),

  /** Get hotels */
  getHotels: (params) => api.get('/recommend/hotels', { params }),

  /** Recommend hotels (budget-based) */
  recommendHotels: (payload) => api.post('/hotels/recommend', payload),

  /** Get restaurants */
  getRestaurants: (params) => api.get('/recommend/restaurants', { params }),

  /** Recommend restaurants */
  recommendRestaurants: (payload) => api.post('/restaurants/recommend', payload),

  /** Optimize route */
  optimizeRoute: (payload) => api.post('/routes/optimize', payload),

  /** Get directions */
  getDirections: (payload) => api.post('/routes/directions', payload),
}
