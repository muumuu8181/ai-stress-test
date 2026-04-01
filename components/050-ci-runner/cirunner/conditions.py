import os
import re
from typing import Dict, Any, Optional

def evaluate_condition(condition: str, variables: Dict[str, str], env: Dict[str, str]) -> bool:
    """
    Evaluates a simple condition string.
    Supports variables like ${VAR} and ${env.VAR}.
    Evaluates to True if the condition string (after substitution) is truthy.

    In a more complex implementation, this could support comparisons (==, !=, etc.).
    For this simple CI runner, we'll support basic existence and simple equality checks.

    Example:
    '${VAR} == "true"'
    '${env.DEBUG}'
    """

    # 1. Substitute variables
    pattern = r'\${(.*?)}'

    def replace_var(match):
        var_name = match.group(1).strip()
        if var_name.startswith('env.'):
            env_key = var_name[4:]
            val = env.get(env_key, os.environ.get(env_key, ''))
        else:
            val = variables.get(var_name, '')
        return str(val)

    substituted = re.sub(pattern, replace_var, str(condition))

    # 2. Simple evaluation logic
    # Check for equality: A == B or A != B
    eq_match = re.match(r'^(.*?)\s*==\s*(.*)$', substituted)
    if eq_match:
        left = eq_match.group(1).strip().strip('"').strip("'")
        right = eq_match.group(2).strip().strip('"').strip("'")
        return left == right

    ne_match = re.match(r'^(.*?)\s*!=\s*(.*)$', substituted)
    if ne_match:
        left = ne_match.group(1).strip().strip('"').strip("'")
        right = ne_match.group(2).strip().strip('"').strip("'")
        return left != right

    # Otherwise, check truthiness (not empty, not 'false', not '0')
    val = substituted.strip().lower()
    if val in ('', 'false', '0', 'null', 'none'):
        return False
    return True

def should_run(if_cond: Any, unless_cond: Any, variables: Dict[str, str], env: Dict[str, str]) -> bool:
    """Determines if a job should run based on if/unless conditions."""
    if if_cond is not None:
        if isinstance(if_cond, bool):
            if not if_cond:
                return False
        elif not evaluate_condition(str(if_cond), variables, env):
            return False

    if unless_cond is not None:
        if isinstance(unless_cond, bool):
            if unless_cond:
                return False
        elif evaluate_condition(str(unless_cond), variables, env):
            return False

    return True
