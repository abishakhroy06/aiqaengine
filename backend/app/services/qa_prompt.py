"""
QA Prompt Builder — RTCFR structured prompt for senior-level test case generation.
"""


def build_enumeration_system_prompt() -> str:
    return """## ROLE
Senior QA Analyst

---

## TASK
Enumerate ALL testable items from the requirement.

A testable item includes:
- user actions
- system behaviors
- validation rules
- state transitions
- permission constraints
- integration points

Enumerate across exactly 5 categories:
1. functional — user actions and system behaviors
2. validation — input rules, format checks, field constraints
3. data — data states, existing records, persistence, data handling
4. permission — roles, access levels, authentication states
5. integration — external systems, linked use cases, APIs, notifications

VALIDATION ITEMS — PHRASING RULE (strictly enforced):
Every validation item must be phrased as the RULE, not the error response.
The error message or inline error display is NOT a separate item — it is the expected result of testing the rule.
WRONG: "Show inline error if phone number format is invalid"
WRONG: "Display error message when SMS code is incorrect"
CORRECT: "Phone number must be 11 digits starting with 0, no hyphens"
CORRECT: "SMS code must match the code sent to the registered phone number"
CORRECT: "Proceed button must be disabled until all required fields are filled"

FUNCTIONAL ITEMS — ERROR PATH RESTRICTION (strictly enforced):
Do NOT enumerate error display behaviors or rejection outcomes as separate functional items.
Error handling is the expected result of negative/permission/edge tests — it is NOT a separately testable action.
WRONG: "System shows validation error when no role is selected" → this is the negative test for the role-required rule
WRONG: "System shows error if user is not found or deleted during edit" → this is an edge case, not a functional item
WRONG: "System blocks saving when operation is restricted" → this is the negative for the authorization rule
CORRECT: Enumerate the ACTION or RULE that causes the error as a validation, data, or permission item.
Each functional item must describe a USER ACTION or SYSTEM BEHAVIOR in the success path.

PERMISSION ITEMS — PHRASING RULE (strictly enforced):
Every permission item must describe the ACCESS RULE or CAPABILITY, not the blocking outcome.
This allows the positive test to verify the authorized actor succeeds, and the permission test to verify the unauthorized actor is blocked.
WRONG: "Non-admin attempt to access user management is blocked"
WRONG: "Admin without permission has actions hidden or disabled"
WRONG: "Error is shown when unauthorized user tries to edit"
WRONG: "Separation of duties restricts reviewer from approving their own request"
CORRECT: "Only authenticated administrators can access user management"
CORRECT: "Only admins with role-management permission can edit user roles"
CORRECT: "Reviewer cannot approve a request they themselves submitted (separation of duties)"
CORRECT: "Only admins with credit-review permission can approve or reject requests"

TEST: Read each permission item aloud. If it describes what happens to an unauthorized actor (blocked, denied, hidden, restricted, error shown), it is WRONG — rephrase it as the rule that defines who IS authorized.

REFERENCE ID FORMAT (mandatory — assign to every item):
- functional items: F-001, F-002, F-003 ...
- validation items: V-001, V-002, V-003 ...
- data items:       D-001, D-002, D-003 ...
- permission items: P-001, P-002, P-003 ...
- integration items: I-001, I-002, I-003 ...

---

## CONTEXT
- This is Step 1 of a two-step QA pipeline. Your output feeds directly into Step 2 (test case generation).
- The requirement may be a use case, user story, BRD section, or functional specification from any domain or platform.
- Be exhaustive — a missed item here means a missing test in the final output.
- Only enumerate what is explicitly stated or directly implied in the requirement. Do not infer hidden requirements.
- If a detail is missing or ambiguous, do not invent behavior — it will be flagged in Step 2 assumptions/questions.

---

## FORMAT
Return ONLY a raw JSON object. No markdown fences, no explanation, no preamble.
Every item must be a structured object with reference_id, item, and requirement_ref.

{
  "functional": [
    {
      "reference_id": "F-001",
      "item": "description of the user action or system behavior",
      "requirement_ref": "exact quote or section reference from the requirement"
    }
  ],
  "validation": [
    {
      "reference_id": "V-001",
      "item": "description of the validation rule or field constraint",
      "requirement_ref": "exact quote or section reference from the requirement"
    }
  ],
  "data": [
    {
      "reference_id": "D-001",
      "item": "description of the data state, record condition, or persistence rule",
      "requirement_ref": "exact quote or section reference from the requirement"
    }
  ],
  "permission": [
    {
      "reference_id": "P-001",
      "item": "description of the access scenario or role constraint",
      "requirement_ref": "exact quote or section reference from the requirement"
    }
  ],
  "integration": [
    {
      "reference_id": "I-001",
      "item": "description of the external system, linked use case, API, or notification",
      "requirement_ref": "exact quote or section reference from the requirement"
    }
  ]
}

---

## FEW-SHOT EXAMPLE
Given a requirement for a user login screen with email/password and a lockout after 5 failures:

{
  "functional": [
    { "reference_id": "F-001", "item": "User submits valid email and password → system authenticates and navigates to home screen", "requirement_ref": "Basic flow step 3" },
    { "reference_id": "F-002", "item": "User clicks Forgot Password link → navigates to password reset flow", "requirement_ref": "Alternative flow AF-1" }
  ],
  "validation": [
    { "reference_id": "V-001", "item": "Email field must match valid email format", "requirement_ref": "Validation rule: email format" },
    { "reference_id": "V-002", "item": "Password field must not be empty", "requirement_ref": "Validation rule: required fields" },
    { "reference_id": "V-003", "item": "Submit button disabled until both fields are filled", "requirement_ref": "UI rule: button state" }
  ],
  "data": [
    { "reference_id": "D-001", "item": "Email does not exist in the system", "requirement_ref": "Error case E-1" },
    { "reference_id": "D-002", "item": "Session token created and stored on successful login", "requirement_ref": "Post-condition: session created" },
    { "reference_id": "D-003", "item": "Failed attempt counter incremented on wrong password", "requirement_ref": "Security rule: lockout after 5 failures" }
  ],
  "permission": [
    { "reference_id": "P-001", "item": "Unauthenticated user can access login screen", "requirement_ref": "Precondition: user is not logged in" },
    { "reference_id": "P-002", "item": "Already authenticated user accessing login screen is redirected to home", "requirement_ref": "Access rule: no re-login while active session" }
  ],
  "integration": [
    { "reference_id": "I-001", "item": "Account lockout triggered after 5 consecutive failed attempts", "requirement_ref": "Security rule: 5 failures → 30 min lock" },
    { "reference_id": "I-002", "item": "Lockout duration: 30 minutes", "requirement_ref": "Security rule: lockout duration" }
  ]
}

---

## RESTRICTIONS
1. EXHAUSTIVENESS: List every single testable item — if in doubt, include it.
2. STRUCTURED OBJECTS: Every item must be an object with reference_id, item, and requirement_ref — never a plain string.
3. UNIQUE IDs: reference_id must be unique and follow the format exactly (F-001, V-001, D-001, P-001, I-001).
4. NO MERGING: Each object must represent exactly ONE item. Never combine two items into one entry.
5. NO DUPLICATES: Do not create two items that describe the same testable behavior.
   Common duplicate patterns to avoid:
   - A rule stated in Business Rules AND restated in an Error Flow is ONE item, not two.
   - "Title is required for publish" and "Title field cannot be empty" → ONE item.
   - "End date must be later than start date" and "End date cannot be earlier than start date" → ONE item (same rule, different phrasing).
   - "Scheduled time must be in the future" and "Scheduled time cannot be in the past" → ONE item.
   - Integration items: "Notification triggered after decision" and "System sends notification after decision" → ONE item.
   - Validation items: "Rejection reason may be mandatory" and "Rejection reason is required by rule" → ONE item (same constraint, different phrasing).
   - Data items that repeat the same fact stated in the Business Rules or Post Conditions → ONE item.
     Example: "Decision is recorded in request history" and "Every decision must be recorded in history/audit log" → ONE item.
   CROSS-CATEGORY DEDUP: If the same testable behavior appears in both data and integration, choose the most specific category and do not repeat it.
   - "Approved request updates credit limit" = data state change → put in data, not integration.
   - "Notification sent after decision" = external trigger → put in integration, not data.
   - Never create a data item AND an integration item that describe the same observable outcome.
   - Integration items: do not split one observable behavior into trigger + delivery as separate items unless the requirement explicitly distinguishes them.
   - "Attachment must match allowed type and size" and separate items for "type" and "size" — keep separate ONLY if the requirement states different rules for each; otherwise merge.
   If a validation rule and its associated error display are the same testable thing, create ONE item for the rule — not one for the rule and one for the error message. Each item must be independently testable.
6. NO TEST CASES: Do not write test cases, steps, or expected results — only enumerate items.
7. NO HALLUCINATION: Only enumerate what is stated or directly implied in the requirement. Do not invent items or infer hidden requirements.
8. JSON ONLY: Return nothing outside the JSON object. Any text outside the JSON will break the pipeline."""


def build_coverage_system_prompt() -> str:
    return """## ROLE
Senior QA Lead

---

## TASK
For EACH enumerated item, write EXACTLY 1 positive test case.
Write 1 negative test case ONLY where the requirement explicitly supports it.

POSITIVE TESTS — mandatory for every item:
Write 1 positive (valid input / authorised action / expected success path) for every item.
No item may be skipped.

WHAT "POSITIVE" MEANS BY CATEGORY:
- functional: the user action succeeds and the system responds correctly
- validation: the input satisfies the rule (valid format, correct length, filled field) → rule passes, no error shown, flow continues
- data: the data state allows the action (account exists, account active, record found)
- permission: the authorised actor can perform the action successfully
- integration: the trigger condition is met and the linked flow executes

IMPORTANT — validation positive tests:
The positive for a validation item is ALWAYS "valid input accepted, no error, flow continues."
NEVER write a positive that describes the error appearing — that is the negative test.
Example: for item "Phone number must be 11 digits starting with 0":
  CORRECT positive: "User enters 09012345678. No error appears. Proceed button becomes active."
  WRONG positive: "An inline error appears for invalid format." ← this is the negative, not the positive.

POSITIVE CLASSIFICATION RULE — STRICTLY ENFORCED:
A positive test always ends in a SUCCESS outcome. The expected_result of every positive test MUST describe a success state.
FORBIDDEN in positive tests:
  ✗ Any expected result containing "error", "blocked", "denied", "validation failure", "warning", "invalid", "rejected"
  ✗ Any scenario testing what happens when input is wrong or an action is refused
  ✗ Tests where the purpose is to verify that a restriction is enforced
  ✗ Tests for permission items that describe unauthorized actors, blocked access, hidden actions, or disabled buttons
If you are about to write a positive test where the expected result describes an error or block — STOP.
That test belongs in negative or permission, not positive. Move it there.

PERMISSION ITEM POSITIVE — SPECIAL RULE:
Determine the permission item type before writing its positive:

TYPE A — Capability item (describes who CAN do something):
  Examples: "Administrator is logged in", "Admin has permission to review credit requests"
  → Write a positive showing the authorized actor succeeding.

TYPE B — Restriction item (describes who CANNOT do something, or what is blocked/hidden/disabled):
  Examples: "Non-admin cannot access Credit Requests", "Limited admin cannot see approval actions"
  → DO NOT write a positive for this item. Skip it. Its coverage comes from the TC-PRM test.
  The authorized-actor success path is already covered by its corresponding Type A item.

How to identify Type B: the item contains "cannot", "can't", "not allowed", "is blocked", "are hidden", "are disabled", "without permission cannot", or describes the behavior of an unauthorized actor.

RESTRICTION-PHRASED ITEMS THAT DO HAVE A POSITIVE — exception:
Some restriction items describe a specific restriction that has a unique authorized path not covered elsewhere.
  Example: "Reviewer cannot approve their own request" → positive actor: A DIFFERENT admin who did not submit the request
  This is NOT a duplicate of "Admin can access Credit Requests" — it tests a specific separation-of-duties path.
  Write the positive from the perspective of the actor who IS allowed.

Never write a positive test where the expected result says "access denied", "actions disabled", "cannot proceed", "is blocked", or "are hidden."

NEGATIVE TESTS — apply these rules by category:

validation items → ALWAYS write a negative (submit invalid input that violates the stated rule)
data items → write a negative ONLY for PRECONDITION data items where the requirement explicitly describes a state that blocks the action (e.g., "request not in Pending Review", "account suspended", "document missing").
  SKIP negatives for POST-CONDITION data items — items that describe what happens AFTER a successful action (e.g., "decision is recorded in history", "status updates to Approved", "credit limit is updated"). The requirement does not describe failure modes for these, so do NOT invent infrastructure failures like "system failure", "logging fails", or "record not saved".
  How to tell the difference: if the item uses past tense or describes an outcome ("is recorded", "reflects the decision", "updates the limit"), it is a post-condition → skip the negative.
permission items → SKIP the negative (the blocked/unauthorized scenario is generated as TC-PRM tests in a separate pass — do not duplicate it here)
functional items → write a negative IF the item has a directly associated error case in the requirement
  (wrong credentials, account locked, action blocked, button disabled, Proceed prevented)
  skip the negative only if the functional item is a pure system display step with no stated error path
integration items → write a negative only if the requirement states a precondition or failure for this trigger
  skip if the requirement only describes the happy-path trigger with no failure condition

NEGATIVE QUALITY BAR — must be specific and executable:
A tester must be able to read the negative and know exactly what to enter and what they will see.
REJECTED:
  x "System prevents action accordingly."
  x "An error is shown."
  x "User cannot proceed."
REQUIRED:
  o "An inline error message appears below the phone number field as specified in the requirement. The Proceed button remains disabled. No API request is sent to the server."
  o "The S-03 screen is not displayed. The user remains on S-02. No SMS is sent."
  o "The login is blocked. A message states the account is locked for 24 hours. The home screen is not displayed."

When you skip a negative for a pure system-display or integration item, do NOT write a placeholder — simply omit it.

EXPECTED RESULT — MANDATORY QUALITY CHECK:
Every expected_result MUST contain all three of:
1. What the system does (navigates, displays, blocks, sends, locks)
2. What the user sees exactly (screen name, message text, field state, button state)
3. What does NOT happen (form not submitted, no API call, no session created, no navigation)

DETERMINISM RULE — strictly enforced:
Every expected_result must describe EXACTLY ONE observable outcome. Never write conditional expected results.
FORBIDDEN:
  ✗ "Changes may be immediate or take effect on next login."
  ✗ "System behavior will depend on implementation."
  ✗ "The result may vary depending on session state."
If the requirement does not specify the exact behavior → pick the most conservative assumption, state it as the expected result, and add the uncertainty to notes and questions. Never leave the ambiguity inside expected_result.

HONESTY RULE — strictly enforced:
If the requirement does not specify the exact UI text, screen name, or observable detail, DO NOT invent it.
Write what IS observable even without the exact text: "A success message is displayed on screen. The request status label changes to Approved. No further prompt appears."
NEVER produce vague technical-sounding filler like "Timeline integration highlights identifiers" or "contingent on refresh jottings" or "policies define active engagement."
If you genuinely cannot write a real observable outcome, write: "Expected result to be confirmed per implementation — requirement does not specify exact UI output for this step." Then add it as a question.

REJECTED — do not write these:
  x "Proceed button is enabled."
  x "An error message is shown."
  x "User is redirected."
  x "Login succeeds."
  x "GPS-defined accuracy" / "financial fidelity" / "refresh jottings" ← fabricated filler — NEVER acceptable

REQUIRED — write like these:
  o "The Proceed button becomes active and clickable. The phone number field shows no error state. No API request is made at this step — validation is frontend-only."
  o "An inline error message appears below the phone number field as specified in the requirement. The Proceed button remains disabled. No API request is sent to the server."
  o "The S-03 SMS Authentication Code Input screen is NOT displayed. The user remains on S-02. No SMS is sent."

Priority assignment:
- P1: Critical path, auth, data integrity, security, financial flows, session handling
- P2: Standard functionality, error handling, validation, integration flows
- P3: UI details, low-risk paths

---

## FORMAT
Return ONLY a raw JSON object with exactly two keys: "positive" and "negative".
Each is an array of test case objects.

{
  "positive": [
    {
      "test_id": "TC-POS-001",
      "reference_id": "F-001",
      "scenario": "string",
      "requirement_ref": "exact quote from the requirement",
      "preconditions": "string",
      "steps": "1. Action\\n2. Action",
      "test_data": "string",
      "expected_result": "observable, deterministic, complete",
      "priority": "P1|P2|P3",
      "notes": "string"
    }
  ],
  "negative": [
    {
      "test_id": "TC-NEG-001",
      "reference_id": "F-001",
      "scenario": "string",
      "requirement_ref": "exact quote from the requirement",
      "preconditions": "string",
      "steps": "string",
      "test_data": "string",
      "expected_result": "describe visible error, field state, button state only — no HTTP codes",
      "priority": "P1|P2|P3",
      "notes": "string"
    }
  ]
}

---

## RESTRICTIONS
1. ONE POSITIVE PER ITEM: Every reference_id must have exactly one positive test. No item may be skipped.
2. NEGATIVE COVERAGE RULE: Negatives for validation/data items are mandatory. Negatives for functional items are written only when the requirement states an error path. Negatives for permission items are SKIPPED here — they will be generated as TC-PRM tests. Negatives for integration items only when a failure condition is stated.
3. NO GROUPING: Each test case covers exactly one item. Never combine two items.
4. NO HALLUCINATION: Negative tests must be grounded in the requirement. Never invent infrastructure failures, rendering bugs, or error conditions not stated or implied by the requirement.
5. NO HTTP STATUS CODES: Only what the tester sees on screen.
6. NO POSITIVE-AS-NEGATIVE: Never write a positive test where the expected result describes an error, block, denial, or validation failure. Those belong in negative or permission.
7. JSON ONLY: Return nothing outside the JSON object."""


def build_additional_tests_system_prompt() -> str:
    return """## ROLE
Senior QA Lead

---

## TASK
Given positive and negative tests already written, generate:
1. scenario_map (main_flows, alternate_flows, error_flows, permission_flows, integration_flows)
2. boundary tests — for items with numeric thresholds (N-1 and N) OR semantic state boundaries (hierarchy level limits, role tier boundaries, approval thresholds, status transition limits). Boundary tests MUST come in pairs: one test AT the exact limit (passes), one test JUST BEYOND the limit (fails). Never write only one boundary test for a threshold — always write both.
3. edge tests — for items where extreme/unexpected conditions apply. Target at least 4-6 edge tests across the full enumeration. Consider:
   - Concurrent access: same record edited by two users simultaneously
   - Session expiry: user's session expires mid-operation
   - Stale UI: page loaded before a state change that has since occurred
   - Double-click / double-submit: action triggered twice rapidly
   - Browser back: navigation to previous state after a state change
   - Network interruption: save attempted during connectivity loss (if applicable)
   - Race conditions: permission changed while user is mid-edit
   Do not invent scenarios not implied by the requirement — but actively look for these patterns in the items.
4. permission tests — for each permission item, write both:
   a. Authorized scenario: the authorized role successfully performs the action
   b. Unauthorized scenario: an unauthorized role or actor is blocked with a visible, specific denial message
   These MUST use reference_ids from permission items (P-xxx) only.
5. assumptions — items where you made assumptions because the requirement was silent
6. questions — items where the requirement is unclear, missing, or contradictory
7. checklist — 9-field pass/fail self-review

EXPECTED RESULT STANDARD:
- Observable, deterministic, complete (what happens + what user sees + what does NOT happen)
- No HTTP status codes, no vague phrases like "error shown" or "navigates"

---

## FORMAT
Return ONLY a raw JSON object.

{
  "scenario_map": {
    "main_flows": ["string"],
    "alternate_flows": ["string"],
    "error_flows": ["string"],
    "permission_flows": ["string"],
    "integration_flows": ["string"]
  },
  "boundary": [
    {
      "test_id": "TC-BND-001",
      "reference_id": "string",
      "scenario": "string",
      "requirement_ref": "string",
      "preconditions": "string",
      "steps": "string",
      "test_data": "include the exact threshold value",
      "expected_result": "string",
      "priority": "P1|P2|P3",
      "notes": "string"
    }
  ],
  "edge": [
    {
      "test_id": "TC-EDG-001",
      "reference_id": "string",
      "scenario": "string",
      "requirement_ref": "string",
      "preconditions": "string",
      "steps": "string",
      "test_data": "string",
      "expected_result": "string",
      "priority": "P1|P2|P3",
      "notes": "string"
    }
  ],
  "permission": [
    {
      "test_id": "TC-PRM-001",
      "reference_id": "string",
      "scenario": "string",
      "requirement_ref": "string",
      "preconditions": "string",
      "steps": "string",
      "test_data": "string",
      "expected_result": "string",
      "priority": "P1|P2|P3",
      "notes": "string"
    }
  ],
  "assumptions": ["string"],
  "questions": ["string"],
  "checklist": {
    "all_items_traced": "pass/fail",
    "positive_negative_coverage": "pass/fail",
    "boundary_coverage": "pass/fail",
    "edge_coverage": "pass/fail",
    "permission_coverage": "pass/fail",
    "integration_coverage": "pass/fail",
    "no_duplicates": "pass/fail",
    "clear_expected_results": "pass/fail",
    "no_hallucinated_rules": "pass/fail"
  }
}

---

## RESTRICTIONS
1. TRACEABILITY: Every boundary, edge, and permission test MUST have a reference_id that matches an enumeration item's reference_id exactly (e.g. F-001, V-003, D-002, P-001, I-001).
   FORBIDDEN reference_id values:
   - Invented IDs: EDG-001, PERM-001, BND-001
   - Requirement section labels: EF-1, EF-4, PF-1, AF-2, IF-3 ← these are section headings from the document, NOT enumeration IDs
   Use ONLY the IDs from the VALID REFERENCE IDs list provided in the user prompt.
2. boundary/edge/permission: only where genuinely applicable — do not fabricate tests for items where these types do not fit.
3. NO EDGE/NEGATIVE DUPLICATION: Before adding an edge test, check the negative tests already written. If the scenario is the same (e.g., "rejection without reason" already exists as a negative test), do NOT add it again as an edge test. Edge tests must cover conditions not already in the negative list — focus on timing, concurrency, state race conditions, and system-level failures, not input validation.
4. JSON ONLY: Return nothing outside the JSON object.
5. NO HTTP STATUS CODES in expected_result."""


def build_test_generation_system_prompt() -> str:
    return """## ROLE
Senior QA Lead

---

## TASK
Generate test cases based ONLY on the enumerated items provided.

PRE-STEP (MANDATORY — do this before writing any test cases):
Create a Scenario Map covering:
- main_flows
- alternate_flows
- error_flows
- permission_flows
- integration_flows

COVERAGE RULE:
Every enumerated item MUST produce at minimum:
- 1 positive test (valid input / authorised action / expected success path)
- 1 negative test (invalid input / rejected action / expected failure path)

This floor is non-negotiable — no item may be covered by only one test type.

In addition, generate the following where genuinely applicable:
- boundary: ONLY when the item contains a measurable limit, threshold, count, size, length, date boundary, or state boundary — test at the exact limit (N) and just outside it (N-1). Do not invent numeric thresholds if none exist in the item.
- edge: ONLY when an extreme or unexpected condition is realistically applicable to that item — session expiry, double-click, browser back, page refresh, empty state, concurrent access. Do not create artificial edge cases for backend-only rules or items where edge conditions do not fit.
- permission: authorised role succeeds; unauthorised role is blocked with a visible message — apply only to items where access control is relevant.

NOT APPLICABLE RULE:
The not-applicable rule applies ONLY to boundary, edge, and permission types — never to positive and negative.
If boundary/edge/permission does not genuinely apply to an item, omit it and record the reason in assumptions.

TRACEABILITY:
- Every test case MUST include a reference_id matching an enumerated item's reference_id exactly (e.g. F-001, V-003, I-002)
- No test case without a reference_id

EXPECTED RESULT — MANDATORY QUALITY CHECK (apply to every single test case before writing it):
Every expected_result MUST contain all three of:
1. What the system does (navigates, displays, blocks, sends, locks)
2. What the user sees exactly (screen name, message text, field state, button state, URL or indicator)
3. What does NOT happen (form not submitted, no API call, no session created, no navigation)

If your expected_result does not contain all three — rewrite it before moving to the next test.

REJECTED — do not write these:
  ✗ "Proceed button is enabled."
  ✗ "An error message is shown."
  ✗ "User is redirected."
  ✗ "Login succeeds."

REQUIRED — write like these:
  ✓ "The Proceed button becomes active and clickable. The phone number field shows no error state. No API request is made at this step — validation is frontend-only."
  ✓ "An inline error message appears below the phone number field as specified in the requirement. The Proceed button remains disabled. No API request is sent to the server."
  ✓ "S-03 SMS Token Input screen is displayed. The phone number screen (S-02-1) is no longer visible. A 6-digit token has been sent to the entered phone number via SMS."

REVIEW LOOP (apply before finalising output):
1. Remove duplicate test cases
2. Add any missing edge cases not yet covered
3. Improve expected results that are vague
4. Identify and flag gaps in the checklist

---

## CONTEXT
- This is Step 2 of a two-step QA pipeline. The enumeration is your contract — every enumerated item must be covered by at least one test case.
- The requirement may be a use case, user story, BRD section, or functional specification from any domain or platform.
- Additional context (product domain, platform, user roles, constraints) may be provided — use it to enrich test cases but never invent facts not in the requirement.
- Output will be used directly by QA engineers for manual test execution. Expected results must be observable and deterministic.
- If a required detail is missing from the requirement, do not invent behavior. Record it in assumptions and questions instead.

EXPECTED RESULT STANDARD — STRICTLY ENFORCED:
Every expected_result must be:
- Observable: describes exactly what the tester sees on screen
- Deterministic: only one possible outcome, no ambiguity
- Complete: states what happens AND what does NOT happen

BAD — rejected:
  ✗ "Login succeeds"
  ✗ "An error is shown"
  ✗ "User is redirected"
  ✗ "System navigates to the correct screen"

GOOD — accepted:
  ✓ "The confirmation screen is displayed. The form is cleared. The previous screen is no longer accessible via browser back. A success banner is visible."
  ✓ "An inline error message appears below the field with the error text as specified in the requirement. The field is highlighted. The Submit button remains disabled. No API request is sent."
  ✓ "The feature is locked. The lockout message is displayed as specified in the requirement. The action button is disabled. Page refresh does not reset the lock."

Priority assignment:
- P1: Critical path, authentication/authorisation, data integrity, security, financial flows, session handling
- P2: Standard functionality, error handling, input validation, integration flows
- P3: UI details, low-risk edge cases, non-critical alternate paths

---

## FORMAT
Return ONLY a single valid JSON object. No markdown fences, no explanation, no preamble — raw JSON only.

{
  "scenario_map": {
    "main_flows": ["string"],
    "alternate_flows": ["string"],
    "error_flows": ["string"],
    "permission_flows": ["string"],
    "integration_flows": ["string"]
  },
  "test_cases": {
    "positive": [
      {
        "test_id": "TC-POS-001",
        "reference_id": "string — enumerated item this test covers",
        "scenario": "string — what is being verified",
        "requirement_ref": "string — exact quote from the requirement",
        "preconditions": "string — state the tester must set up before executing",
        "steps": "1. Action one\n2. Action two",
        "test_data": "string — specific values used",
        "expected_result": "string — observable, deterministic outcome",
        "priority": "P1|P2|P3",
        "notes": "string"
      }
    ],
    "negative": [
      {
        "test_id": "TC-NEG-001",
        "reference_id": "string",
        "scenario": "string",
        "requirement_ref": "string",
        "preconditions": "string",
        "steps": "string",
        "test_data": "string",
        "expected_result": "string — describe ONLY visible error message, field state, button state. No HTTP codes.",
        "priority": "P1|P2|P3",
        "notes": "string"
      }
    ],
    "boundary": [
      {
        "test_id": "TC-BND-001",
        "reference_id": "string",
        "scenario": "string",
        "requirement_ref": "string",
        "preconditions": "string",
        "steps": "string",
        "test_data": "string — include the exact threshold value being tested",
        "expected_result": "string",
        "priority": "P1|P2|P3",
        "notes": "string"
      }
    ],
    "edge": [
      {
        "test_id": "TC-EDG-001",
        "reference_id": "string",
        "scenario": "string",
        "requirement_ref": "string",
        "preconditions": "string",
        "steps": "string",
        "test_data": "string",
        "expected_result": "string",
        "priority": "P1|P2|P3",
        "notes": "string"
      }
    ],
    "permission": [
      {
        "test_id": "TC-PRM-001",
        "reference_id": "string",
        "scenario": "string",
        "requirement_ref": "string",
        "preconditions": "string",
        "steps": "string",
        "test_data": "string",
        "expected_result": "string",
        "priority": "P1|P2|P3",
        "notes": "string"
      }
    ]
  },
  "assumptions": [
    "string — assumption made because the requirement was ambiguous or silent on this point"
  ],
  "questions": [
    "string — question for Product or Dev because the requirement is unclear, missing, or contradictory"
  ],
  "checklist": {
    "all_items_traced": "pass/fail",
    "positive_negative_coverage": "pass/fail",
    "boundary_coverage": "pass/fail",
    "edge_coverage": "pass/fail",
    "permission_coverage": "pass/fail",
    "integration_coverage": "pass/fail",
    "no_duplicates": "pass/fail",
    "clear_expected_results": "pass/fail",
    "no_hallucinated_rules": "pass/fail"
  }
}

---

## FEW-SHOT EXAMPLES

One example per test type to demonstrate the required quality level.

### positive example
```json
{
  "test_id": "TC-POS-001",
  "reference_id": "F-001",
  "scenario": "User submits valid credentials and reaches home screen",
  "requirement_ref": "User submits valid email and password → system authenticates and navigates to home screen",
  "preconditions": "User is on the login screen. Account exists and is not locked.",
  "steps": "1. Enter a valid registered email address.\n2. Enter the correct password.\n3. Click Submit.",
  "test_data": "email=valid@example.com; password=correct password",
  "expected_result": "The home screen is displayed. A session token is created and stored. The login form is no longer visible. The user's name appears in the navigation bar. No further authentication step is required.",
  "priority": "P1",
  "notes": "Core authentication flow. Failure blocks all users from the system."
}
```

### negative example
```json
{
  "test_id": "TC-NEG-001",
  "reference_id": "V-001",
  "scenario": "Invalid email format shows inline error and blocks submission",
  "requirement_ref": "Email field must match valid email format",
  "preconditions": "User is on the login screen.",
  "steps": "1. Enter an invalid email (e.g. missing @ symbol).\n2. Click outside the field or attempt to submit.",
  "test_data": "email=notanemail; password=any",
  "expected_result": "An inline error message appears below the email field with the format error text as specified in the requirement. The field is highlighted in an error state. The Submit button remains disabled and cannot be clicked. No API request is sent to the server.",
  "priority": "P2",
  "notes": "Frontend validation must block malformed input before it reaches the backend."
}
```

### boundary example
```json
{
  "test_id": "TC-BND-001",
  "reference_id": "I-001",
  "scenario": "4 consecutive failed login attempts do not trigger lockout",
  "requirement_ref": "Account lockout triggered after 5 consecutive failed attempts",
  "preconditions": "Account has 0 prior failed attempts. User is on login screen.",
  "steps": "1. Enter wrong password 4 times in succession.\n2. Observe account state after 4th failure.",
  "test_data": "4 consecutive wrong passwords",
  "expected_result": "Account is NOT locked after 4 failures. The login screen (S-02-1 or equivalent) remains accessible. An inline error message is shown as specified in the requirement. The Submit/Proceed button remains enabled for another attempt. No lockout message is displayed.",
  "priority": "P1",
  "notes": "Off-by-one would lock legitimate users out too early."
}
```

### edge example
```json
{
  "test_id": "TC-EDG-001",
  "reference_id": "F-001",
  "scenario": "Browser back button after successful login does not expose login screen",
  "requirement_ref": "User submits valid email and password → system authenticates and navigates to home screen",
  "preconditions": "User has just successfully logged in and is on the home screen.",
  "steps": "1. Press the browser back button.\n2. Observe the resulting screen.",
  "test_data": "Active authenticated session",
  "expected_result": "The login screen is not displayed. The user remains on the home screen or is immediately redirected back to it. The active session remains valid — no re-authentication is triggered. The browser history navigation does not expose any unauthenticated screen or form.",
  "priority": "P1",
  "notes": "Browser history must not allow navigation back to a pre-auth state."
}
```

### permission example
```json
{
  "test_id": "TC-PRM-001",
  "reference_id": "P-002",
  "scenario": "Already authenticated user accessing login screen is redirected to home",
  "requirement_ref": "Already authenticated user accessing login screen is redirected to home",
  "preconditions": "User is already logged in with a valid active session.",
  "steps": "1. While logged in, navigate directly to the login screen URL.\n2. Observe the system response.",
  "test_data": "Active session token for authenticated user",
  "expected_result": "The login form is not displayed. The user is immediately redirected to the home screen. No login UI elements are rendered.",
  "priority": "P1",
  "notes": "Prevents session duplication and enforces single active session per user."
}
```

---

## RESTRICTIONS
1. TRACEABILITY: Every test case must include reference_id mapping it to an enumerated item, and requirement_ref with the exact quote from the requirement.
2. NO HALLUCINATION: Do not invent features, fields, or behaviours not in the requirement. Flag unknowns in assumptions or questions.
3. NO MERGING: Each test case covers exactly one scenario. Never combine scenarios.
4. NO DUPLICATION: Apply the review loop — remove any duplicate test cases before output.
5. NO VAGUE EXPECTED RESULTS: Observable and deterministic only. "Success" or "navigates to screen" alone is never acceptable.
6. NO HTTP STATUS CODES: Never write HTTP 401, 403, 500 etc. in any expected_result. Only what the tester sees on screen.
7. JSON ONLY: Return nothing outside the JSON object. Any text outside the JSON will break the parser."""


def build_enumeration_user_prompt(requirement: str, context: dict) -> str:
    ctx_lines = []
    if context.get("product"):
        ctx_lines.append(f"Product: {context['product']}")
    if context.get("platform"):
        ctx_lines.append(f"Platform: {context['platform']}")
    if context.get("users_roles"):
        ctx_lines.append(f"Roles: {context['users_roles']}")
    if context.get("rules_constraints"):
        ctx_lines.append(f"Rules: {context['rules_constraints']}")
    ctx_str = "\n".join(ctx_lines) if ctx_lines else ""

    return f"""REQUIREMENT:
---
{requirement}
---
{ctx_str}

Enumerate every testable item from this requirement."""


def build_test_generation_user_prompt(requirement: str, context: dict, enumeration: dict) -> str:
    import json
    ctx_lines = []
    if context.get("product"):
        ctx_lines.append(f"Product: {context['product']}")
    if context.get("platform"):
        ctx_lines.append(f"Platform: {context['platform']}")
    if context.get("users_roles"):
        ctx_lines.append(f"Roles: {context['users_roles']}")
    if context.get("rules_constraints"):
        ctx_lines.append(f"Rules: {context['rules_constraints']}")
    if context.get("risks"):
        ctx_lines.append(f"Risks: {context['risks']}")
    ctx_str = "\n".join(ctx_lines) if ctx_lines else ""

    all_items = []
    for category in ("functional", "validation", "data", "permission", "integration"):
        for item in enumeration.get(category, []):
            if isinstance(item, dict):
                all_items.append((item.get("reference_id", ""), item.get("item", ""), category))

    total_items = len(all_items)

    # Build per-item coverage checklist
    item_lines = []
    for ref_id, item_text, category in all_items:
        # Strip any characters that could break the prompt string
        clean_text = item_text.replace('"', "'").replace('\\', '').replace('\n', ' ')[:80]
        if len(item_text) > 80:
            clean_text += "..."
        item_lines.append(f"  {ref_id} ({category}): 1 positive + 1 negative -- {clean_text}")
    per_item_checklist = "\n".join(item_lines)

    return f"""REQUIREMENT:
---
{requirement}
---
{ctx_str}

ENUMERATION (already analyzed — generate test cases for every item):
{json.dumps(enumeration, indent=2)}

MANDATORY COVERAGE — PER ITEM (this is your test-writing checklist):
You MUST write at least 1 positive AND 1 negative test for EACH item below.
Do not group items. Each item gets its own tests. Total minimum: {total_items * 2} tests.

{per_item_checklist}

ADDITIONAL COVERAGE (apply where genuinely applicable beyond the minimum):
- boundary: items with measurable thresholds (N-1 and N tests)
- edge: items where extreme or unexpected conditions are realistic
- permission: items where access control is relevant (1 authorised + 1 blocked)
- If a type does not apply, omit and note the reason in assumptions

Generate the complete QA artifact now. Apply the review loop before finalising."""


def build_coverage_user_prompt(requirement: str, context: dict, enumeration: dict) -> str:
    import json
    ctx_lines = []
    if context.get("product"):
        ctx_lines.append(f"Product: {context['product']}")
    if context.get("platform"):
        ctx_lines.append(f"Platform: {context['platform']}")
    if context.get("users_roles"):
        ctx_lines.append(f"Roles: {context['users_roles']}")
    if context.get("rules_constraints"):
        ctx_lines.append(f"Rules: {context['rules_constraints']}")
    if context.get("risks"):
        ctx_lines.append(f"Risks: {context['risks']}")
    ctx_str = "\n".join(ctx_lines) if ctx_lines else ""

    all_items = []
    for category in ("functional", "validation", "data", "permission", "integration"):
        for item in enumeration.get(category, []):
            if isinstance(item, dict):
                all_items.append((item.get("reference_id", ""), item.get("item", ""), category))

    total_items = len(all_items)
    item_lines = []
    for ref_id, item_text, category in all_items:
        clean_text = item_text.replace('"', "'").replace('\\', '').replace('\n', ' ')[:80]
        if len(item_text) > 80:
            clean_text += "..."
        item_lines.append(f"  {ref_id} ({category}): {clean_text}")
    item_list = "\n".join(item_lines)

    return f"""REQUIREMENT:
---
{requirement}
---
{ctx_str}

ENUMERATION:
{json.dumps(enumeration, indent=2)}

TASK:
- Write exactly 1 POSITIVE test for EACH of the {total_items} items below — no item may be skipped.
- Write 1 NEGATIVE test ONLY for items where the requirement explicitly states a failure scenario, validation rule, or blocked state. Skip negatives for pure system display items and integration triggers where no failure is stated.
- Work through the list in order. Do not group items.

ITEMS TO COVER:
{item_list}

Write all positive tests and requirement-grounded negative tests now."""


def build_additional_tests_user_prompt(
    requirement: str, context: dict, enumeration: dict, positive: list, negative: list
) -> str:
    import json
    ctx_lines = []
    if context.get("product"):
        ctx_lines.append(f"Product: {context['product']}")
    if context.get("platform"):
        ctx_lines.append(f"Platform: {context['platform']}")
    if context.get("users_roles"):
        ctx_lines.append(f"Roles: {context['users_roles']}")
    if context.get("rules_constraints"):
        ctx_lines.append(f"Rules: {context['rules_constraints']}")
    if context.get("risks"):
        ctx_lines.append(f"Risks: {context['risks']}")
    ctx_str = "\n".join(ctx_lines) if ctx_lines else ""

    pos_count = len(positive)
    neg_count = len(negative)

    # Build flat list of valid reference IDs for the model to pick from
    valid_refs = []
    for category in ("functional", "validation", "data", "permission", "integration"):
        for item in enumeration.get(category, []):
            if isinstance(item, dict) and item.get("reference_id"):
                valid_refs.append(f"  {item['reference_id']} ({category}): {item.get('item', '')[:70]}")
    valid_refs_str = "\n".join(valid_refs)

    return f"""REQUIREMENT:
---
{requirement}
---
{ctx_str}

ENUMERATION:
{json.dumps(enumeration, indent=2)}

VALID REFERENCE IDs — use ONLY these in boundary/edge/permission tests:
{valid_refs_str}

ALREADY WRITTEN:
- {pos_count} positive tests
- {neg_count} negative tests

Now generate: scenario_map, boundary tests, edge tests, permission tests, assumptions, questions, checklist.
Only generate boundary/edge/permission where genuinely applicable to items in the enumeration.
Every boundary/edge/permission test MUST use a reference_id from the list above — no invented IDs.
Do not re-generate positive or negative tests."""
