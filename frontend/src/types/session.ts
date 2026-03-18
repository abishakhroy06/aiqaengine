export type SessionStatus = 'pending' | 'generating' | 'complete' | 'failed';
export type Priority = 'P1' | 'P2' | 'P3';
export type TestSection = 'positive' | 'negative' | 'boundary' | 'edge' | 'permission';

export interface QAContext {
  product: string;
  platform: string;
  users_roles: string;
  rules_constraints: string;
  risks: string;
  environment: string;
}

export interface TestCase {
  test_id: string;
  reference_id: string;
  scenario: string;
  requirement_ref: string;
  preconditions: string;
  steps: string;
  test_data: string;
  expected_result: string;
  priority: Priority;
  notes: string;
}

export interface TestCases {
  positive: TestCase[];
  negative: TestCase[];
  boundary: TestCase[];
  edge: TestCase[];
  permission: TestCase[];
}

export interface ScenarioMap {
  main_flows: string[];
  alternate_flows: string[];
  error_flows: string[];
  permission_flows: string[];
  integration_flows: string[];
}

export interface ChecklistResult {
  all_items_traced: string;
  positive_negative_coverage: string;
  boundary_coverage: string;
  edge_coverage: string;
  permission_coverage: string;
  integration_coverage: string;
  no_duplicates: string;
  clear_expected_results: string;
  no_hallucinated_rules: string;
}

export interface QAOutput {
  id: number;
  session_id: number;
  scenario_map: ScenarioMap;
  test_cases: TestCases;
  assumptions: string[];
  questions: string[];
  checklist_result: ChecklistResult;
  checklist: ChecklistResult;
  created_at: string;
}

export interface QASession {
  id: number;
  name: string;
  requirement: string;
  context: QAContext;
  template: string;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
  output?: QAOutput;
}

export interface QASessionListItem {
  id: number;
  name: string;
  requirement: string;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
  test_case_count: number;
}

export interface CreateSessionRequest {
  name: string;
  requirement: string;
  context: QAContext;
  template?: string;
}

export function totalTestCaseCount(testCases: TestCases | null | undefined): number {
  if (!testCases) return 0;
  return (
    (testCases.positive?.length ?? 0) +
    (testCases.negative?.length ?? 0) +
    (testCases.boundary?.length ?? 0) +
    (testCases.edge?.length ?? 0) +
    (testCases.permission?.length ?? 0)
  );
}
