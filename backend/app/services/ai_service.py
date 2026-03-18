import json
import logging
from app.config import settings
from app.services.qa_prompt import (
    build_enumeration_system_prompt,
    build_enumeration_user_prompt,
    build_coverage_system_prompt,
    build_coverage_user_prompt,
    build_additional_tests_system_prompt,
    build_additional_tests_user_prompt,
)

logger = logging.getLogger(__name__)

_client = None
_provider: str = ""


def _get_client():
    global _client, _provider
    if _client is not None:
        return _client, _provider

    if settings.OPENAI_API_KEY:
        from openai import OpenAI
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
        _provider = "openai"
    elif settings.ANTHROPIC_API_KEY:
        from anthropic import Anthropic
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        _provider = "anthropic"
    else:
        raise ValueError("No AI API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")

    return _client, _provider


def _call_ai(system: str, user: str, max_tokens: int = 4096) -> str:
    client, provider = _get_client()
    if provider == "openai":
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        raw = response.choices[0].message.content.strip()
        logger.info("OpenAI call: %d input tokens, %d output tokens",
                    response.usage.prompt_tokens, response.usage.completion_tokens)
    else:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = message.content[0].text.strip()

    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    return raw


def _parse_json_with_retry(raw: str, call_name: str, retry_fn) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("%s parse failed (%s), retrying", call_name, e)
        raw2 = retry_fn()
        try:
            return json.loads(raw2)
        except json.JSONDecodeError as e2:
            logger.error("Failed to parse %s response as JSON: %s", call_name, e2)
            raise ValueError(f"AI returned invalid JSON for {call_name}: {e2}") from e2


def generate_qa_output(requirement: str, context: dict) -> dict:
    """
    Three-call pipeline:
      Call 1 — enumerate all testable items
      Call 2 — generate positive + negative tests (one per item, focused)
      Call 3 — generate boundary/edge/permission + scenario_map + metadata
    Returns the parsed JSON output dict.
    """
    # --- Call 1: Enumeration ---
    logger.info("Step 1: enumerating testable items")
    enum_raw = _call_ai(
        system=build_enumeration_system_prompt(),
        user=build_enumeration_user_prompt(requirement, context),
        max_tokens=2000,
    )
    try:
        enumeration = json.loads(enum_raw)
    except json.JSONDecodeError as e:
        logger.warning("Enumeration parse failed (%s), using empty enumeration", e)
        enumeration = {}

    functional_count = len(enumeration.get("functional", []))
    validation_count = len(enumeration.get("validation", []))
    data_count = len(enumeration.get("data", []))
    permission_count = len(enumeration.get("permission", []))
    integration_count = len(enumeration.get("integration", []))
    total_items = functional_count + validation_count + data_count + permission_count + integration_count
    logger.info(
        "Enumeration: %d functional, %d validation, %d data, %d permission, %d integration → %d total items",
        functional_count, validation_count, data_count, permission_count, integration_count, total_items,
    )

    # --- Call 2: Coverage — positive + negative for every item ---
    logger.info("Step 2: generating positive + negative tests (%d items → %d minimum tests)", total_items, total_items * 2)
    coverage_raw = _call_ai(
        system=build_coverage_system_prompt(),
        user=build_coverage_user_prompt(requirement, context, enumeration),
        max_tokens=16000,
    )
    coverage = _parse_json_with_retry(
        coverage_raw,
        "coverage",
        lambda: _call_ai(
            system=build_coverage_system_prompt(),
            user=build_coverage_user_prompt(requirement, context, enumeration),
            max_tokens=16000,
        ),
    )
    positive = coverage.get("positive", [])
    negative = coverage.get("negative", [])
    logger.info("Coverage: %d positive, %d negative", len(positive), len(negative))

    # --- Call 3: Additional tests + metadata ---
    logger.info("Step 3: generating boundary/edge/permission tests and metadata")
    additional_raw = _call_ai(
        system=build_additional_tests_system_prompt(),
        user=build_additional_tests_user_prompt(requirement, context, enumeration, positive, negative),
        max_tokens=8000,
    )
    additional = _parse_json_with_retry(
        additional_raw,
        "additional",
        lambda: _call_ai(
            system=build_additional_tests_system_prompt(),
            user=build_additional_tests_user_prompt(requirement, context, enumeration, positive, negative),
            max_tokens=8000,
        ),
    )

    boundary = additional.get("boundary", [])
    edge = additional.get("edge", [])
    permission = additional.get("permission", [])
    logger.info("Additional: %d boundary, %d edge, %d permission", len(boundary), len(edge), len(permission))

    result = {
        "scenario_map": additional.get("scenario_map", {}),
        "test_cases": {
            "positive": positive,
            "negative": negative,
            "boundary": boundary,
            "edge": edge,
            "permission": permission,
        },
        "assumptions": additional.get("assumptions", []),
        "questions": additional.get("questions", []),
        "checklist": additional.get("checklist", {}),
        "enumeration": enumeration,
    }
    return result
