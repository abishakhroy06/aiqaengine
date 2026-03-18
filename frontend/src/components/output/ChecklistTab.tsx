import { ChecklistResult } from '../../types/session';
import { motion } from 'framer-motion';

interface Props {
  checklist: ChecklistResult;
}

const items: Array<{ key: keyof ChecklistResult; label: string; description: string }> = [
  { key: 'all_items_traced', label: 'All Items Traced', description: 'Every enumerated item has at least one test case' },
  { key: 'positive_negative_coverage', label: 'Positive & Negative Coverage', description: 'Both happy path and failure scenarios covered' },
  { key: 'boundary_coverage', label: 'Boundary Conditions', description: 'Min/max values and edge limits tested' },
  { key: 'edge_coverage', label: 'Edge Cases', description: 'Unusual or extreme input scenarios covered' },
  { key: 'permission_coverage', label: 'Permission Coverage', description: 'All user roles and access levels tested' },
  { key: 'integration_coverage', label: 'Integration Coverage', description: 'External system interactions tested' },
  { key: 'no_duplicates', label: 'No Duplicates', description: 'No redundant test cases' },
  { key: 'clear_expected_results', label: 'Clear Expected Results', description: 'All test cases have unambiguous expected outcomes' },
  { key: 'no_hallucinated_rules', label: 'No Hallucinated Rules', description: 'All tests grounded in the stated requirements' },
];

function isPassed(value: string): boolean {
  return value.toLowerCase().startsWith('pass');
}

export function ChecklistTab({ checklist }: Props) {
  const passed = items.filter(item => isPassed(checklist[item.key] ?? '')).length;
  const total = items.length;
  const percentage = Math.round((passed / total) * 100);

  return (
    <div>
      {/* Score */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-100 text-sm">QA Coverage Score</p>
            <p className="text-5xl font-bold mt-1">{percentage}%</p>
            <p className="text-purple-100 text-sm mt-1">{passed} of {total} criteria passed</p>
          </div>
          <div className="text-6xl">{percentage >= 80 ? '✅' : percentage >= 50 ? '⚠️' : '❌'}</div>
        </div>
        <div className="mt-4 bg-white/20 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="bg-white rounded-full h-2"
          />
        </div>
      </div>

      {/* Items */}
      <div className="space-y-3">
        {items.map(({ key, label, description }, i) => {
          const rawValue = checklist[key] ?? '';
          const itemPassed = isPassed(rawValue);
          const detail = rawValue.length > 5 ? rawValue : '';
          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`flex items-start gap-3 p-4 rounded-xl border ${
                itemPassed ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'
              }`}
            >
              <span className="text-xl shrink-0 mt-0.5">{itemPassed ? '✅' : '❌'}</span>
              <div>
                <p className={`font-medium ${itemPassed ? 'text-green-800' : 'text-red-800'}`}>{label}</p>
                <p className={`text-sm mt-0.5 ${itemPassed ? 'text-green-600' : 'text-red-600'}`}>{description}</p>
                {detail && !itemPassed && (
                  <p className="text-xs mt-1 text-red-500 italic">{detail}</p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
