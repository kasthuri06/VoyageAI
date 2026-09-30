import { Link } from 'react-router-dom'
import { FiCompass, FiMap, FiSun, FiShield, FiArrowRight, FiZap } from 'react-icons/fi'

const FEATURES = [
  { icon: '🤖', title: 'AI Recommendations', desc: 'TF-IDF + Cosine Similarity ML engine personalises attractions to your interests.' },
  { icon: '🗺️', title: 'Route Optimisation', desc: 'Dijkstra & A* algorithms minimise travel time between attractions automatically.' },
  { icon: '☁️', title: 'Weather-Aware', desc: 'Live weather data redirects you to indoor venues when rain is expected.' },
  { icon: '🏨', title: 'Hotel Matching', desc: 'Budget-scored hotel recommendations within your daily spend range.' },
  { icon: '🍽️', title: 'Restaurant Finder', desc: 'Curated nearby restaurants filtered by cuisine, budget, and rating.' },
  { icon: '📅', title: 'Day-wise Planner', desc: 'Morning, afternoon, evening, and night slots for every day of your trip.' },
]

const DESTINATIONS = [
  { name: 'Goa', img: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=400&q=80', tag: 'Beach' },
  { name: 'Jaipur', img: 'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=400&q=80', tag: 'Heritage' },
  { name: 'Munnar', img: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400&q=80', tag: 'Nature' },
  { name: 'Agra', img: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=400&q=80', tag: 'Monument' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700
                            flex items-center justify-center">
              <FiCompass className="text-white text-lg" />
            </div>
            <span className="font-display font-bold text-xl text-primary-700">
              Voyage <span className="text-accent-500">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login"    className="btn-secondary py-2 px-5 text-sm">Login</Link>
            <Link to="/register" className="btn-primary  py-2 px-5 text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative bg-gradient-to-br from-primary-900 via-primary-700 to-primary-500 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&q=80')", backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div className="relative max-w-7xl mx-auto px-6 py-28 text-center">
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            <FiZap className="text-yellow-300" /> AI-Powered Travel Planning
          </div>
          <h1 className="font-display text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Plan Smarter.<br/>
            <span className="text-accent-400">Travel Better.</span>
          </h1>
          <p className="text-xl text-primary-100 max-w-2xl mx-auto mb-10">
            Voyage AI combines Machine Learning, Route Optimization, and Real-time Weather
            to generate your perfect personalised itinerary in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register"
              className="btn-primary py-4 px-8 text-base bg-white text-primary-700 hover:bg-gray-50">
              Start Planning Free <FiArrowRight />
            </Link>
            <Link to="/login"
              className="btn-secondary py-4 px-8 text-base border-white/50 text-white hover:bg-white/10">
              Sign In
            </Link>
          </div>
          <p className="text-primary-300 text-sm mt-6">No credit card required · Free forever</p>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="font-display text-4xl font-bold text-gray-900">Everything you need</h2>
            <p className="text-gray-500 mt-3 text-lg">One platform for end-to-end AI trip planning</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(f => (
              <div key={f.title} className="card p-6 hover:border hover:border-primary-200 transition-all">
                <div className="text-4xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-lg text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="font-display text-4xl font-bold text-gray-900">Popular Destinations</h2>
            <p className="text-gray-500 mt-3">Explore India's most loved travel spots</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {DESTINATIONS.map(d => (
              <div key={d.name} className="card group overflow-hidden cursor-pointer">
                <div className="relative h-48 overflow-hidden">
                  <img src={d.img} alt={d.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                  <div className="absolute bottom-3 left-3 text-white">
                    <p className="font-display font-bold text-lg">{d.name}</p>
                    <span className="badge bg-white/20 text-white text-xs">{d.tag}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-primary-800 text-white text-center">
        <div className="max-w-2xl mx-auto px-6">
          <h2 className="font-display text-4xl font-bold mb-4">Ready to explore?</h2>
          <p className="text-primary-200 text-lg mb-8">
            Join thousands of travellers who plan smarter trips with Voyage AI.
          </p>
          <Link to="/register" className="btn-primary bg-white text-primary-700 hover:bg-gray-50 py-4 px-10 text-base">
            Get Started — It's Free <FiArrowRight />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 text-center text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <FiCompass className="text-primary-400" />
          <span className="font-display font-bold text-white">Voyage AI</span>
        </div>
        <p>© {new Date().getFullYear()} Voyage AI. Built with ❤️ using React + FastAPI + ML.</p>
      </footer>
    </div>
  )
}
