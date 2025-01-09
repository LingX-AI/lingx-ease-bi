import json
import re


def validate_json_string(json_str: str) -> tuple[str | None, str | None]:
    """
    Validate JSON string.
    :param json_str: JSON string to validate.
    :return: tuple (validated JSON string or None, error message or None)
    """
    error_msg = "Unable to provide correct parsing results. The query may have returned too much data. Please simplify your query conditions and try again."

    if json_str:
        try:
            json.loads(json_str, strict=False)
            return json_str, None
        except json.JSONDecodeError:
            if json_str.startswith("```json") and json_str.endswith("```"):
                match = re.match(r"```json(.*)```", json_str, re.DOTALL)
                if match:
                    option_string = match.group(1).strip()
                    return validate_json_string(option_string)

            elif json_str.startswith("```json"):
                match = re.match(r"```json(.*)", json_str, re.DOTALL)
                if match:
                    option_string = match.group(1).strip()
                    return validate_json_string(option_string)

            elif json_str.endswith("```"):
                match = re.match(r"(.*)```", json_str, re.DOTALL)
                if match:
                    option_string = match.group(1).strip()
                    return validate_json_string(option_string)

            return None, error_msg

    return None, error_msg
