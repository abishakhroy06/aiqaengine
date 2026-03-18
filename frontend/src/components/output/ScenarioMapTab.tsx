import { ScenarioMap } from '../../types/session';
import { GlassCard } from '../ui/GlassCard';
import { AnimatedList } from '../ui/AnimatedList';
import { motion } from 'framer-motion';

interface Props {
  scenarioMap: ScenarioMap;
}

const flowConfig = [
  { key: 'main_flows' as const, label: 'Main Flows', color: 'bg-green-100 text-green-700', emoji: '✅' },
  { key: 'alternate_flows' as const, label: 'Alternate Flows', color: 'bg-blue-100 text-blue-700', emoji: '🔄' },
  { key: 'error_flows' as const, label: 'Error Flows', color: 'bg-red-100 text-red-700', emoji: '❌' },
  { key: 'permission_flows' as const, label: 'Permission Flows', color: 'bg-yellow-100 text-yellow-700', emoji: '🔒' },
  { key: 'integration_flows' as const, label: 'Integration Flows', color: 'bg-purple-100 text-purple-700', emoji: '🔗' },
];

export function ScenarioMapTab({ scenarioMap }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {flowConfig.map(({ key, label, color, emoji }) => {
        const flows = scenarioMap[key] ?? [];
        return (
          <GlassCard key={key}>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-lg">{emoji}</span>
              <h3 className="font-semibold text-gray-800">{label}</h3>
              <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
                {flows.length}
              </span>
            </div>
            {flows.length === 0 ? (
              <p className="text-gray-400 text-sm italic">None identified</p>
            ) : (
              <AnimatedList>
                {flows.map((flow, i) => (
                  <motion.div
                    key={i}
                    className="flex items-start gap-2 py-1 text-sm text-gray-700 border-b border-gray-50 last:border-0"
                  >
                    <span className="text-gray-400 mt-0.5 shrink-0">{i + 1}.</span>
                    <span>{flow}</span>
                  </motion.div>
                ))}
              </AnimatedList>
            )}
          </GlassCard>
        );
      })}
    </div>
  );
}
