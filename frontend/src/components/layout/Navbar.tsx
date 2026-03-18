import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', emoji: '📊' },
  { path: '/sessions', label: 'Sessions', emoji: '🧪' },
  { path: '/sessions/new', label: 'New Session', emoji: '✨' },
];

export function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white border-b border-gray-100 px-6 py-3 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2">
          <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI QA Engine
          </span>
        </Link>

        <div className="flex items-center gap-1">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === item.path || (item.path !== '/dashboard' && pathname.startsWith(item.path))
                  ? 'text-purple-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              {(pathname === item.path || (item.path !== '/dashboard' && pathname.startsWith(item.path))) && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute inset-0 bg-purple-50 rounded-lg"
                />
              )}
              <span className="relative">{item.emoji} {item.label}</span>
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <Link to="/settings" className="text-sm text-gray-500 hover:text-gray-700">
            {user?.full_name ?? user?.email?.split('@')[0] ?? 'Account'}
          </Link>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={logout}
            className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Sign out
          </motion.button>
        </div>
      </div>
    </nav>
  );
}
