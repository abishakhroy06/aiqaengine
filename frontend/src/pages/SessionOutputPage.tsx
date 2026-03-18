import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { GradientButton } from '../components/ui/GradientButton';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ScenarioMapTab } from '../components/output/ScenarioMapTab';
import { TestCasesTab } from '../components/output/TestCasesTab';
import { ChecklistTab } from '../components/output/ChecklistTab';
import { useSession, useRegenerateSession } from '../hooks/useSession';
import { sessionService } from '../services/sessionService';
import { totalTestCaseCount } from '../types/session';

type Tab = 'scenario_map' | 'test_cases' | 'assumptions' | 'questions' | 'checklist';

const tabs: Array<{ id: Tab; label: string; emoji: string }> = [
  { id: 'scenario_map', label: 'Scenario Map', emoji: '🗺️' },
  { id: 'test_cases', label: 'Test Cases', emoji: '✅' },
  { id: 'assumptions', label: 'Assumptions', emoji: '💭' },
  { id: 'questions', label: 'Questions', emoji: '❓' },
  { id: 'checklist', label: 'QA Checklist', emoji: '📋' },
];

export default function SessionOutputPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const sessionId = id ? parseInt(id, 10) : NaN;
  const [activeTab, setActiveTab] = useState<Tab>('test_cases');
  const { data: session, isLoading, error } = useSession(sessionId);
  const regenerate = useRegenerateSession();

  if (isNaN(sessionId)) {
    return (
      <PageWrapper>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-500 mb-4">Invalid session ID</p>
            <GradientButton onClick={() => navigate('/sessions')}>Back to Sessions</GradientButton>
          </div>
        </div>
      </PageWrapper>
    );
  }

  if (isLoading) {
    return (
      <PageWrapper>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
        </div>
      </PageWrapper>
    );
  }

  if (error || !session) {
    return (
      <PageWrapper>
        <Navbar />
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-500 mb-4">Session not found</p>
            <GradientButton onClick={() => navigate('/sessions')}>Back to Sessions</GradientButton>
          </div>
        </div>
      </PageWrapper>
    );
  }

  const isGenerating = session.status === 'generating' || session.status === 'pending';
  const output = session.output;

  return (
    <PageWrapper>
      <Navbar />
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 px-8 py-6 sticky top-0 z-10">
          <div className="max-w-6xl mx-auto">
            <button
              onClick={() => navigate('/sessions')}
              className="text-gray-400 hover:text-gray-600 text-sm mb-2"
            >
              ← Back to Sessions
            </button>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-gray-900">{session.name}</h1>
                <StatusBadge status={session.status} />
              </div>
              <div className="flex items-center gap-3">
                {output && (
                  <a
                    href={sessionService.getExportUrl(sessionId)}
                    download
                    className="px-4 py-2 text-sm font-medium text-purple-600 border border-purple-200 rounded-full hover:bg-purple-50 transition-colors"
                  >
                    ↓ Export CSV
                  </a>
                )}
                <GradientButton
                  variant="secondary"
                  onClick={() => regenerate.mutate(sessionId)}
                  isLoading={regenerate.isPending}
                >
                  ↻ Regenerate
                </GradientButton>
              </div>
            </div>
          </div>
        </div>

        {/* Generating state */}
        {isGenerating && (
          <div className="max-w-6xl mx-auto px-8 py-20 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="text-5xl mb-4 inline-block"
            >
              ⚙️
            </motion.div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Generating QA Artifact...</h2>
            <p className="text-gray-500">Our AI is analyzing your requirement. This typically takes 60-120 seconds.</p>
          </div>
        )}

        {/* Failed state */}
        {session.status === 'failed' && (
          <div className="max-w-6xl mx-auto px-8 py-20 text-center">
            <div className="text-5xl mb-4">❌</div>
            <h2 className="text-xl font-semibold text-red-700 mb-2">Generation Failed</h2>
            <p className="text-gray-500 mb-6">Something went wrong. Please try regenerating.</p>
            <GradientButton onClick={() => regenerate.mutate(sessionId)} isLoading={regenerate.isPending}>
              Try Again
            </GradientButton>
          </div>
        )}

        {/* Output */}
        {session.status === 'complete' && output && (
          <>
            {/* Tabs */}
            <div className="bg-white border-b border-gray-100">
              <div className="max-w-6xl mx-auto px-8">
                <div className="flex gap-1">
                  {tabs.map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`px-4 py-4 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === tab.id
                          ? 'border-purple-500 text-purple-700'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      {tab.emoji} {tab.label}
                      {tab.id === 'test_cases' && (
                        <span className="ml-2 px-1.5 py-0.5 bg-purple-100 text-purple-600 rounded-full text-xs">
                          {totalTestCaseCount(output.test_cases)}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Tab content */}
            <div className="max-w-6xl mx-auto px-8 py-6">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                {activeTab === 'scenario_map' && output.scenario_map && (
                  <ScenarioMapTab scenarioMap={output.scenario_map} />
                )}
                {activeTab === 'test_cases' && (
                  <TestCasesTab
                    testCases={output.test_cases ?? { positive: [], negative: [], boundary: [], edge: [], permission: [] }}
                    templateId={session.template}
                  />
                )}
                {activeTab === 'assumptions' && (
                  <div className="space-y-2">
                    {(output.assumptions ?? []).map((item, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="flex gap-3 p-4 bg-white rounded-xl border border-gray-100"
                      >
                        <span className="text-gray-400 font-mono text-sm shrink-0">{i + 1}.</span>
                        <p className="text-gray-700">{item}</p>
                      </motion.div>
                    ))}
                  </div>
                )}
                {activeTab === 'questions' && (
                  <div className="space-y-2">
                    {(output.questions ?? []).map((item, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="flex gap-3 p-4 bg-amber-50 rounded-xl border border-amber-100"
                      >
                        <span className="text-amber-500 shrink-0">❓</span>
                        <p className="text-gray-700">{item}</p>
                      </motion.div>
                    ))}
                  </div>
                )}
                {activeTab === 'checklist' && output.checklist_result && (
                  <ChecklistTab checklist={output.checklist_result} />
                )}
              </motion.div>
            </div>
          </>
        )}
      </div>
    </PageWrapper>
  );
}
