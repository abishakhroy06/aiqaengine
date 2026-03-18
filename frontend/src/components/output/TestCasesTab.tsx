import { Fragment, useState } from 'react';
import { TestCase, TestCases, TestSection, Priority } from '../../types/session';
import { TemplateConfig, getTemplate } from '../../types/template';
import { motion } from 'framer-motion';

interface Props {
  testCases: TestCases;
  templateId?: string;
}

type ActiveTab = 'all' | TestSection;

const SECTIONS: Array<{ id: TestSection; label: string; color: string; badge: string }> = [
  { id: 'positive',   label: 'I. Positive',   color: 'bg-green-100 text-green-700',   badge: 'bg-green-500' },
  { id: 'negative',   label: 'II. Negative',  color: 'bg-red-100 text-red-700',       badge: 'bg-red-500' },
  { id: 'boundary',   label: 'III. Boundary', color: 'bg-orange-100 text-orange-700', badge: 'bg-orange-500' },
  { id: 'edge',       label: 'IV. Edge',      color: 'bg-purple-100 text-purple-700', badge: 'bg-purple-500' },
  { id: 'permission', label: 'V. Permission', color: 'bg-yellow-100 text-yellow-700', badge: 'bg-yellow-500' },
];

const sectionBadgeColor: Record<TestSection, string> = {
  positive:   'bg-green-100 text-green-700',
  negative:   'bg-red-100 text-red-700',
  boundary:   'bg-orange-100 text-orange-700',
  edge:       'bg-purple-100 text-purple-700',
  permission: 'bg-yellow-100 text-yellow-700',
};

const priorityColor: Record<Priority, string> = {
  P1: 'bg-red-100 text-red-700',
  P2: 'bg-yellow-100 text-yellow-700',
  P3: 'bg-green-100 text-green-700',
};

const TESTCASE_KEYS: ReadonlyArray<keyof TestCase> = [
  'test_id', 'reference_id', 'scenario', 'requirement_ref',
  'preconditions', 'steps', 'test_data', 'expected_result', 'priority', 'notes',
];

function getFieldValue(tc: TestCase, key: string): string {
  if (TESTCASE_KEYS.includes(key as keyof TestCase)) {
    return String(tc[key as keyof TestCase] ?? '');
  }
  return '';
}

function TestCaseTable({
  cases,
  showCategory,
  template,
}: {
  cases: TestCase[];
  showCategory?: boolean;
  template: TemplateConfig;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!cases || cases.length === 0) {
    return <p className="text-sm text-gray-400 italic py-4">No test cases in this section.</p>;
  }

  const tableFields = template.fields.filter(f => f.showInTable);
  const expandFields = template.fields.filter(f => f.showInExpand);

  // Category (type) column is always shown in "All" view regardless of template
  const colCount = tableFields.length + (showCategory ? 1 : 0);

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-100">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            {tableFields.map(field => (
              <th key={field.key} className="px-4 py-3 text-left">{field.label}</th>
            ))}
            {showCategory && <th className="px-4 py-3 text-left">Type</th>}
          </tr>
        </thead>
        <tbody>
          {cases.map((tc, i) => {
            const section = tc.test_id?.includes('-POS-') ? 'positive'
              : tc.test_id?.includes('-NEG-') ? 'negative'
              : tc.test_id?.includes('-BND-') ? 'boundary'
              : tc.test_id?.includes('-EDG-') ? 'edge'
              : tc.test_id?.includes('-PRM-') ? 'permission'
              : null;

            return (
              <Fragment key={tc.test_id}>
                <motion.tr
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.01 }}
                  className="border-t border-gray-50 hover:bg-gray-50 cursor-pointer"
                  onClick={() => setExpandedId(expandedId === tc.test_id ? null : tc.test_id)}
                >
                  {tableFields.map(field => {
                    const val = getFieldValue(tc, field.key);
                    if (field.key === 'priority') {
                      return (
                        <td key={field.key} className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${priorityColor[tc.priority as Priority] ?? 'bg-gray-100 text-gray-700'}`}>
                            {val}
                          </span>
                        </td>
                      );
                    }
                    if (field.key === 'test_id' || field.key === 'reference_id') {
                      return (
                        <td key={field.key} className="px-4 py-3 font-mono text-xs text-gray-500 whitespace-nowrap">
                          {val || '—'}
                        </td>
                      );
                    }
                    if (field.key === 'expected_result') {
                      return (
                        <td key={field.key} className="px-4 py-3 text-gray-600 max-w-sm text-xs">{val}</td>
                      );
                    }
                    return (
                      <td key={field.key} className="px-4 py-3 text-gray-800 max-w-xs">{val}</td>
                    );
                  })}
                  {showCategory && (
                    <td className="px-4 py-3">
                      {section && (
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sectionBadgeColor[section as TestSection]}`}>
                          {section.charAt(0).toUpperCase() + section.slice(1)}
                        </span>
                      )}
                    </td>
                  )}
                </motion.tr>

                {expandedId === tc.test_id && expandFields.length > 0 && (
                  <tr className="bg-purple-50">
                    <td colSpan={colCount} className="px-4 py-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        {expandFields.map(field => {
                          const val = getFieldValue(tc, field.key);
                          const isFullWidth = field.key === 'steps' || field.key === 'requirement_ref';
                          const isNote = field.key === 'notes';
                          if (isNote && !val) return null;
                          return (
                            <div key={field.key} className={isFullWidth ? 'col-span-2' : ''}>
                              <p className="font-medium text-gray-700 mb-1">{field.label}</p>
                              {isNote ? (
                                <p className="text-amber-700 bg-amber-50 rounded px-2 py-1">{val}</p>
                              ) : (
                                <p className={`text-gray-600 ${field.key === 'steps' ? 'whitespace-pre-line' : ''} ${field.key === 'requirement_ref' ? 'text-xs italic text-gray-500' : ''}`}>
                                  {val || '—'}
                                </p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function TestCasesTab({ testCases, templateId }: Props) {
  const [activeTab, setActiveTab] = useState<ActiveTab>('all');
  const template = getTemplate(templateId ?? 'full');

  const allCases: TestCase[] = [
    ...(testCases?.positive ?? []),
    ...(testCases?.negative ?? []),
    ...(testCases?.boundary ?? []),
    ...(testCases?.edge ?? []),
    ...(testCases?.permission ?? []),
  ];
  const totalCount = allCases.length;

  const cases = activeTab === 'all' ? allCases : (testCases?.[activeTab] ?? []);
  const currentSection = activeTab !== 'all' ? SECTIONS.find(s => s.id === activeTab) : null;

  return (
    <div>
      {/* Template badge */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs text-gray-400">
          Template: <span className="font-medium text-gray-600">{template.icon} {template.name}</span>
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {/* All tab */}
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
            activeTab === 'all'
              ? 'bg-gray-700 text-white shadow-sm'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          All
          <span className={`text-xs px-1.5 py-0.5 rounded-full ${
            activeTab === 'all' ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-500'
          }`}>
            {totalCount}
          </span>
        </button>

        {/* Category tabs */}
        {SECTIONS.map(section => {
          const count = testCases?.[section.id]?.length ?? 0;
          return (
            <button
              key={section.id}
              onClick={() => setActiveTab(section.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                activeTab === section.id
                  ? `${section.badge} text-white shadow-sm`
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {section.label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                activeTab === section.id ? 'bg-white/30 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Label row */}
      <div className="flex items-center gap-2 mb-3">
        {currentSection ? (
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${currentSection.color}`}>
            {currentSection.label}
          </span>
        ) : (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
            All Test Cases
          </span>
        )}
        <span className="text-sm text-gray-400">{cases.length} test case{cases.length !== 1 ? 's' : ''}</span>
      </div>

      <TestCaseTable cases={cases} showCategory={activeTab === 'all'} template={template} />
    </div>
  );
}
