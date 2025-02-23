# src/pymock/server/rules_engine.py
import logging
from functools import lru_cache
from re import Pattern
from re import compile as compile_regex
from typing import Any

from flask import Request
from jsonpath_ng import parse
from jsonschema import ValidationError, validate

from pymock.constants.operators import TARGET_OPERATOR_MAP

logger = logging.getLogger(__name__)


# Cached regex and JSONPath compilation funcs
@lru_cache(maxsize=100)
def _compile_regex(pattern: str, *, case_insensitive: bool = False) -> Pattern:
    flags = 2 if case_insensitive else 0  # 2 = re.IGNORECASE
    return compile_regex(pattern, flags)


@lru_cache(maxsize=100)
def _compile_jsonpath(expression: str):
    return parse(expression)


# Main evaluation logic
def evaluate_rules(rules: list[dict], req: Request) -> dict | None:
    """Evaluates rules and returns the first matching rule's response."""
    return next(
        (rule.get("response") for rule in rules if _match_all_conditions(rule.get("conditions", []), req)), None
    )


# Condition matching
def _match_all_conditions(conditions: list[dict], req: Request) -> bool:
    """Returns True if all conditions match."""
    return all(_match_condition(cond, req) for cond in conditions)


def _match_condition(condition: dict, req: Request) -> bool:
    """Evaluates a single condition with validation and inversion."""
    target = condition.get("target")
    operator = condition.get("operator")
    value = condition.get("value")
    invert = condition.get("invert", False)

    if target not in TARGET_OPERATOR_MAP or operator not in TARGET_OPERATOR_MAP[target]:
        logger.debug("Invalid condition: target=%s, operator=%s", target, operator)
        return False

    actual_value = _extract_property(req, target, condition.get("property"))
    result = _apply_operator(actual_value, operator, value)
    return not result if invert else result


# Property extraction
_EXTRACTORS = {
    "body": lambda req, prop: _resolve_property(req.get_json(), prop) if req.is_json else None,
    "params": lambda req, prop: _resolve_property(req.args.getlist(prop) if prop else req.args, prop),
    "headers": lambda req, prop: _resolve_property(req.headers, prop),
    "method": lambda req, _: req.method,
    "path": lambda req, _: req.path,
    "route_params": lambda req, prop: req.view_args.get(prop) if req.view_args else None,
    "cookies": lambda req, prop: _resolve_property(req.cookies, prop),
    "global_variable": lambda _, __: None,
    "data_bucket": lambda _, __: None,
    "number": lambda req, prop: _parse_number(req.args.get(prop)),
}


def _extract_property(req: Request, target: str, property_name: str | None) -> Any:
    """Extracts value from request based on target type."""
    extractor = _EXTRACTORS.get(target, lambda _, __: None)
    return extractor(req, property_name)


def _parse_number(raw_val: str | None) -> float | None:
    """Attempts to parse a string to float, returns None on failure."""
    try:
        return float(raw_val) if raw_val is not None else None
    except ValueError:
        return None


# src/pymock/server/rules_engine.py (partial update)
def _resolve_property(data: Any, property_name: str | None) -> Any:
    """Resolves a property using JSONPath or dict access."""
    if not property_name or not data:
        return data

    try:
        if property_name.startswith("$"):
            matches = _compile_jsonpath(property_name).find(data)
            return [m.value for m in matches] if matches else None
        if isinstance(data, dict):
            return _nested_get(data, property_name)
        # Handle Headers object (werkzeug.datastructures.Headers)
        if hasattr(data, "get"):
            return data.get(property_name)
        return None
    except Exception as e:
        logger.debug("Error resolving property '%s': %s", property_name, e)
        return None


def _nested_get(data: dict, property_name: str) -> Any:
    """Handles nested dictionary access with dot notation."""
    result: Any = data
    for key in property_name.split("."):
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return None
        if result is None:
            break
    return result


def _apply_operator(actual_value: Any, operator: str, expected_value: Any) -> bool:
    """Compares values using the specified operator."""
    op_func = _OPERATORS.get(operator, lambda _, __: False)
    result = op_func(actual_value, expected_value)
    if operator == "regex (case-insensitive)":
        pattern = _compile_regex(expected_value, case_insensitive=True)
        msg = f"""Debug: actual={actual_value},
        expected={expected_value},
        pattern={pattern.pattern},
        flags={pattern.flags},
        result={result}"""
        print(msg)  # noqa: T201
    return result


def _validate_json(instance: Any, schema: Any) -> bool:
    """Validates JSON against a schema."""
    try:
        validate(instance=instance, schema=schema)
        return True
    except ValidationError:
        return False


# Operator application
_OPERATORS = {
    "equals": lambda actual, expected: actual == expected,
    "regex": lambda actual, expected: bool(_compile_regex(expected).match(str(actual or ""))),
    "regex (case-insensitive)": lambda actual, expected: bool(
        _compile_regex(expected, case_insensitive=True).match(str(actual or ""))
    ),
    "null": lambda actual, _: actual is None,
    "empty array": lambda actual, _: isinstance(actual, list) and not actual,
    "array includes": lambda actual, expected: isinstance(actual, list) and expected in actual,
    "valid JSON schema": _validate_json,
}
