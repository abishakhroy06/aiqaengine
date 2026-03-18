import { MouseEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { AnimatedList } from '../components/ui/AnimatedList';
import { StatusBadge } from '../components/ui/StatusBadge';
import { useSessions, useDeleteSession } from '../hooks/useSession';
import { QASessionListItem } from '../types/session';

export default function SessionsListPage() {
  const navigate = useNavigate();
  const { data: sessions, isLoading, error } = useSessions();
  const deleteSession = useDeleteSession();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (id: number, e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this session?')) return;
    setDeletingId(id);
    try {
      await deleteSession.mutateAsync(id);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <PageWrapper>
      <Navbar />
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 px-8 py-6">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">QA Sessions</h1>
              <p className="text-gray-500 text-sm mt-1">
                {sessions?.length ?? 0} sessions
              </p>
            </div>
            <GradientButton onClick={() => navigate('/sessions/new')}>
              + New Session
            </GradientButton>
          </div>
        </div>

        <div className="max-w-5xl mx-auto p-8">
          {isLoading && (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
            </div>
          )}

          {error && (
            <GlassCard className="text-center text-red-500">
              Failed to load sessions. Please try again.
            </GlassCard>
          )}

          {!isLoading && sessions?.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <div className="text-6xl mb-4">🧪</div>
              <h2 className="text-xl font-semibold text-gray-700 mb-2">No sessions yet</h2>
              <p className="text-gray-500 mb-6">Create your first QA session to get started</p>
              <GradientButton onClick={() => navigate('/sessions/new')}>
                Create First Session
              </GradientButton>
            </motion.div>
          )}

          {sessions && sessions.length > 0 && (
            <AnimatedList>
              {sessions.map((session: QASessionListItem) => (
                <Link key={session.id} to={`/sessions/${session.id}`} className="block mb-4">
                  <GlassCard className="cursor-pointer hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-gray-900 truncate">{session.name}</h3>
                          <StatusBadge status={session.status} />
                        </div>
                        <p className="text-sm text-gray-500 truncate">{session.requirement}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          {new Date(session.created_at).toLocaleDateString('en-US', {
                            month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
                          })}
                          {session.test_case_count
                            ? ` · ${session.test_case_count} test cases`
                            : ''}
                        </p>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={(e) => handleDelete(session.id, e)}
                        disabled={deletingId === session.id}
                        className="ml-4 p-2 text-gray-400 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                      >
                        {deletingId === session.id ? '...' : '🗑️'}
                      </motion.button>
                    </div>
                  </GlassCard>
                </Link>
              ))}
            </AnimatedList>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
