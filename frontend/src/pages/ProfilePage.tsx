import { useState } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { AnimatedInput } from '../components/ui/AnimatedInput';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name ?? '');

  return (
    <PageWrapper>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold text-gray-900 mb-6"
          >
            Profile
          </motion.h1>
          <GlassCard>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-2xl font-bold">
                  {user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? '?'}
                </div>
                <div>
                  <p className="font-semibold text-lg">{user?.full_name ?? 'No name set'}</p>
                  <p className="text-gray-500 text-sm">{user?.email}</p>
                </div>
              </div>

              {isEditing ? (
                <div className="space-y-3">
                  <AnimatedInput
                    label="Full Name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your name"
                  />
                  <div className="flex gap-2">
                    <GradientButton onClick={() => setIsEditing(false)} className="flex-1">
                      Save
                    </GradientButton>
                    <GradientButton variant="secondary" onClick={() => setIsEditing(false)} className="flex-1">
                      Cancel
                    </GradientButton>
                  </div>
                </div>
              ) : (
                <GradientButton variant="secondary" onClick={() => setIsEditing(true)}>
                  Edit Profile
                </GradientButton>
              )}

              <hr className="border-gray-100" />

              <GradientButton variant="danger" onClick={logout}>
                Sign Out
              </GradientButton>
            </div>
          </GlassCard>
        </div>
      </div>
    </PageWrapper>
  );
}
