export type BuiltInTemplateId = 'full' | 'minimal' | 'manual' | 'regression';

export interface TestCaseFieldConfig {
  key: string;
  label: string;
  showInTable: boolean;   // column in main table row
  showInExpand: boolean;  // field in expanded detail panel
}

export interface TemplateConfig {
  id: BuiltInTemplateId;
  name: string;
  description: string;
  icon: string;
  badge: string;
  fields: TestCaseFieldConfig[];
}

export const BUILT_IN_TEMPLATES: TemplateConfig[] = [
  {
    id: 'full',
    name: 'Full',
    description: 'All fields — scenario map, traceability, preconditions, steps, test data, expected result, notes.',
    icon: '📋',
    badge: 'Recommended',
    fields: [
      { key: 'test_id',        label: 'ID',              showInTable: true,  showInExpand: false },
      { key: 'scenario',       label: 'Scenario',        showInTable: true,  showInExpand: false },
      { key: 'reference_id',   label: 'Ref',             showInTable: true,  showInExpand: false },
      { key: 'priority',       label: 'Priority',        showInTable: true,  showInExpand: false },
      { key: 'expected_result',label: 'Expected Result', showInTable: true,  showInExpand: false },
      { key: 'preconditions',  label: 'Preconditions',   showInTable: false, showInExpand: true  },
      { key: 'test_data',      label: 'Test Data',       showInTable: false, showInExpand: true  },
      { key: 'steps',          label: 'Steps',           showInTable: false, showInExpand: true  },
      { key: 'requirement_ref',label: 'Requirement Ref', showInTable: false, showInExpand: true  },
      { key: 'notes',          label: 'Notes',           showInTable: false, showInExpand: true  },
    ],
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Quick overview — ID, scenario, priority, and expected result only. Great for fast reviews.',
    icon: '⚡',
    badge: 'Fast',
    fields: [
      { key: 'test_id',        label: 'ID',              showInTable: true,  showInExpand: false },
      { key: 'scenario',       label: 'Scenario',        showInTable: true,  showInExpand: false },
      { key: 'priority',       label: 'Priority',        showInTable: true,  showInExpand: false },
      { key: 'expected_result',label: 'Expected Result', showInTable: true,  showInExpand: false },
      { key: 'reference_id',   label: 'Ref',             showInTable: false, showInExpand: false },
      { key: 'preconditions',  label: 'Preconditions',   showInTable: false, showInExpand: true  },
      { key: 'steps',          label: 'Steps',           showInTable: false, showInExpand: true  },
      { key: 'test_data',      label: 'Test Data',       showInTable: false, showInExpand: false },
      { key: 'requirement_ref',label: 'Requirement Ref', showInTable: false, showInExpand: false },
      { key: 'notes',          label: 'Notes',           showInTable: false, showInExpand: false },
    ],
  },
  {
    id: 'manual',
    name: 'Manual Testing',
    description: 'Step-by-step execution — includes preconditions, full steps, and test data for testers.',
    icon: '🧪',
    badge: 'Testers',
    fields: [
      { key: 'test_id',        label: 'ID',              showInTable: true,  showInExpand: false },
      { key: 'scenario',       label: 'Scenario',        showInTable: true,  showInExpand: false },
      { key: 'priority',       label: 'Priority',        showInTable: true,  showInExpand: false },
      { key: 'reference_id',   label: 'Ref',             showInTable: false, showInExpand: false },
      { key: 'expected_result',label: 'Expected Result', showInTable: false, showInExpand: true  },
      { key: 'preconditions',  label: 'Preconditions',   showInTable: false, showInExpand: true  },
      { key: 'test_data',      label: 'Test Data',       showInTable: false, showInExpand: true  },
      { key: 'steps',          label: 'Steps',           showInTable: false, showInExpand: true  },
      { key: 'requirement_ref',label: 'Requirement Ref', showInTable: false, showInExpand: false },
      { key: 'notes',          label: 'Notes',           showInTable: false, showInExpand: true  },
    ],
  },
  {
    id: 'regression',
    name: 'Regression',
    description: 'Traceability-first — ID, ref, scenario, priority, expected result. Built for regression suites.',
    icon: '🔁',
    badge: 'CI/CD',
    fields: [
      { key: 'test_id',        label: 'ID',              showInTable: true,  showInExpand: false },
      { key: 'reference_id',   label: 'Ref',             showInTable: true,  showInExpand: false },
      { key: 'scenario',       label: 'Scenario',        showInTable: true,  showInExpand: false },
      { key: 'priority',       label: 'Priority',        showInTable: true,  showInExpand: false },
      { key: 'expected_result',label: 'Expected Result', showInTable: true,  showInExpand: false },
      { key: 'preconditions',  label: 'Preconditions',   showInTable: false, showInExpand: true  },
      { key: 'steps',          label: 'Steps',           showInTable: false, showInExpand: true  },
      { key: 'test_data',      label: 'Test Data',       showInTable: false, showInExpand: false },
      { key: 'requirement_ref',label: 'Requirement Ref', showInTable: false, showInExpand: true  },
      { key: 'notes',          label: 'Notes',           showInTable: false, showInExpand: false },
    ],
  },
];

export function getTemplate(id: string): TemplateConfig {
  return BUILT_IN_TEMPLATES.find(t => t.id === id) ?? BUILT_IN_TEMPLATES[0];
}
