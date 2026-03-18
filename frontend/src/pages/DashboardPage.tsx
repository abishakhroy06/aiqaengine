import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { StatusBadge } from '../components/ui/StatusBadge';
import { useSessions } from '../hooks/useSession';
import { useAuth } from '../context/AuthContext';
import { QASessionListItem } from '../types/session';

function StatCard({ label, value, emoji }: { label: string; value: string | number; emoji: string }) {
  return (
    <GlassCard className="text-center">
      <div className="text-3xl mb-2">{emoji}</div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-500 mt-1">{label}</div>
    </GlassCard>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: sessions, isLoading } = useSessions();

  const totalSessions = sessions?.length ?? 0;
  const completedSessions = sessions?.filter(s => s.status === 'complete').length ?? 0;
  const totalTestCases = sessions?.reduce((sum, s) => {
    return sum + (s.test_case_count ?? 0);
  }, 0) ?? 0;
  const recentSessions = sessions?.slice(0, 5) ?? [];

  return (
    <PageWrapper>
      <Navbar />
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Welcome */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}! 👋
            </h1>
            <p className="text-gray-500 mt-1">Here's your QA activity at a glance.</p>
          </motion.div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <StatCard label="Total Sessions" value={totalSessions} emoji="📁" />
            <StatCard label="Completed" value={completedSessions} emoji="✅" />
            <StatCard label="Test Cases Generated" value={totalTestCases} emoji="🧪" />
          </div>

          {/* Quick action */}
          <GlassCard className="mb-8 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Ready to generate test cases?</h2>
                <p className="text-gray-500 text-sm mt-0.5">
                  Paste a requirement and get a full QA artifact in seconds.
                </p>
              </div>
              <GradientButton onClick={() => navigate('/sessions/new')}>
                ✨ New Session
              </GradientButton>
            </div>
          </GlassCard>

          {/* Recent sessions */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">Recent Sessions</h2>
              <button
                onClick={() => navigate('/sessions')}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                View all →
              </button>
            </div>

            {isLoading && (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
              </div>
            )}

            {!isLoading && recentSessions.length === 0 && (
              <GlassCard className="text-center py-12">
                <div className="text-4xl mb-3">🧪</div>
                <p className="text-gray-500">No sessions yet — create your first one above!</p>
              </GlassCard>
            )}

            {recentSessions.length > 0 && (
              <div className="space-y-3">
                {recentSessions.map((session: QASessionListItem, i) => (
                  <motion.div
                    key={session.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => navigate(`/sessions/${session.id}`)}
                    className="cursor-pointer"
                  >
                    <GlassCard className="hover:shadow-lg transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3">
                            <h3 className="font-semibold text-gray-900 truncate">{session.name}</h3>
                            <StatusBadge status={session.status} />
                          </div>
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(session.created_at).toLocaleDateString('en-US', {
                              month: 'short', day: 'numeric', year: 'numeric'
                            })}
                          </p>
                        </div>
                        <span className="text-gray-300 ml-4">→</span>
                      </div>
                    </GlassCard>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
