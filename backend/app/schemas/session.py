from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from app.models.session import SessionStatus


class QAContextSchema(BaseModel):
    product: str = ""
    platform: str = ""
    users_roles: str = ""
    rules_constraints: str = ""
    risks: str = ""
    environment: str = ""


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    requirement: str = Field(..., min_length=1, max_length=10000)
    context: QAContextSchema
    template: str = "full"


class UpdateSessionRequest(BaseModel):
    name: str | None = None


class TestCaseSchema(BaseModel):
    test_id: str = ""
    reference_id: str = ""
    scenario: str = ""
    requirement_ref: str = ""
    preconditions: str = ""
    steps: str = ""
    test_data: str = ""
    expected_result: str = ""
    priority: str = ""
    notes: str = ""


class TestCasesSchema(BaseModel):
    positive: list[TestCaseSchema] = []
    negative: list[TestCaseSchema] = []
    boundary: list[TestCaseSchema] = []
    edge: list[TestCaseSchema] = []
    permission: list[TestCaseSchema] = []


class ScenarioMapSchema(BaseModel):
    main_flows: list[str] = []
    alternate_flows: list[str] = []
    error_flows: list[str] = []
    permission_flows: list[str] = []
    integration_flows: list[str] = []


class ChecklistResultSchema(BaseModel):
    all_items_traced: str = ""
    positive_negative_coverage: str = ""
    boundary_coverage: str = ""
    edge_coverage: str = ""
    permission_coverage: str = ""
    integration_coverage: str = ""
    no_duplicates: str = ""
    clear_expected_results: str = ""
    no_hallucinated_rules: str = ""


class QAOutputSchema(BaseModel):
    id: int
    session_id: int
    scenario_map: ScenarioMapSchema | None = None
    test_cases: TestCasesSchema | None = None
    assumptions: list[str] = []
    questions: list[str] = []
    checklist_result: ChecklistResultSchema | None = None
    checklist: ChecklistResultSchema | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class QASessionResponse(BaseModel):
    id: int
    name: str
    requirement: str
    context: QAContextSchema | None
    template: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime | None
    output: QAOutputSchema | None = None

    class Config:
        from_attributes = True


class QASessionListItem(BaseModel):
    id: int
    name: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime | None
    test_case_count: int = 0

    class Config:
        from_attributes = True
