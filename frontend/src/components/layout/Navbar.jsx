import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  FiCompass, FiMap, FiBookmark, FiUser,
  FiLogOut, FiMenu, FiX, FiLayout
} from 'react-icons/fi'
import clsx from 'clsx'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard', icon: FiLayout },
  { to: '/plan',      label: 'Plan Trip',  icon: FiCompass },
  { to: '/map',       label: 'Map',        icon: FiMap },
  { to: '/saved',     label: 'Saved',      icon: FiBookmark },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => { logout(); navigate('/') }

  return (
    <nav className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700
                            flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <FiCompass className="text-white text-lg" />
            </div>
            <span className="font-display font-bold text-xl text-primary-700 hidden sm:block">
              Voyage <span className="text-accent-500">AI</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => clsx(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <Icon className="text-base" />
                {label}
              </NavLink>
            ))}
            {user?.role === 'admin' && (
              <NavLink
                to="/admin"
                className={({ isActive }) => clsx(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive ? 'bg-amber-50 text-amber-700' : 'text-gray-600 hover:bg-gray-50'
                )}
              >
                Admin
              </NavLink>
            )}
          </div>

          {/* User menu */}
          <div className="hidden md:flex items-center gap-3">
            <Link to="/profile" className="flex items-center gap-2 px-3 py-2 rounded-lg
                                           hover:bg-gray-50 transition-colors">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                {user?.profile_picture
                  ? <img src={user.profile_picture} alt={user.username}
                         className="w-8 h-8 rounded-full object-cover" />
                  : <FiUser className="text-primary-600" />
                }
              </div>
              <span className="text-sm font-medium text-gray-700">{user?.username}</span>
            </Link>
            <button onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium
                         text-red-500 hover:bg-red-50 transition-colors">
              <FiLogOut />
              Logout
            </button>
          </div>

          {/* Mobile menu toggle */}
          <button className="md:hidden p-2 rounded-lg hover:bg-gray-50"
            onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <FiX size={22} /> : <FiMenu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 py-3 space-y-1 animate-fade-in">
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} onClick={() => setMenuOpen(false)}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium',
                isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50'
              )}>
              <Icon /> {label}
            </NavLink>
          ))}
          <button onClick={() => { handleLogout(); setMenuOpen(false) }}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium
                       text-red-500 hover:bg-red-50 w-full">
            <FiLogOut /> Logout
          </button>
        </div>
      )}
    </nav>
  )
}
