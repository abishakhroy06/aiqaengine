import { useState } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { AnimatedInput } from '../components/ui/AnimatedInput';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Profile update will be wired to API in a future iteration
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <PageWrapper>
      <Navbar />
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold text-gray-900 mb-6"
          >
            Settings
          </motion.h1>

          {/* Profile */}
          <GlassCard className="mb-4">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Profile</h2>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-2xl font-bold">
                {user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? '?'}
              </div>
              <div>
                <p className="font-semibold">{user?.full_name ?? 'No name set'}</p>
                <p className="text-gray-500 text-sm">{user?.email}</p>
                {user?.oauth_provider && (
                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">
                    {user.oauth_provider} account
                  </span>
                )}
              </div>
            </div>
            <div className="space-y-4">
              <AnimatedInput
                label="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your name"
              />
              <div className="flex items-center gap-3">
                <GradientButton onClick={handleSave}>
                  {saved ? '✓ Saved!' : 'Save Changes'}
                </GradientButton>
              </div>
            </div>
          </GlassCard>

          {/* Account */}
          <GlassCard>
            <h2 className="text-lg font-bold text-gray-800 mb-4">Account</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <p className="font-medium text-gray-700 text-sm">Email</p>
                  <p className="text-gray-500 text-sm">{user?.email}</p>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-600">
                  Active
                </span>
              </div>
              <GradientButton variant="danger" onClick={logout} className="w-full">
                Sign Out
              </GradientButton>
            </div>
          </GlassCard>
        </div>
      </div>
    </PageWrapper>
  );
}
