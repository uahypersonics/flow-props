"""TOML configuration loading for flow-props."""
# deprecated: use flow_props.schema.load_config instead

from __future__ import annotations

import tomllib
from pathlib import Path


def load_config(config_path: Path | None, section: str) -> dict:
    """Load a TOML config file and return merged root and section values.

    Args:
        config_path: Path to TOML file, or ``None`` to return an empty dict.
        section: Top-level key to extract (e.g. ``"profiles"``).

    Returns:
        Dict of configuration values from the root of the file merged with the
        requested section. Nested tables other than the requested section are
        ignored. Returns ``{}`` if *config_path* is ``None``.

    Raises:
        FileNotFoundError: If *config_path* does not exist.
    """
    # default empty dicts for optional arguments
    if config_path is None:
        return {}

    # validate inputs
    if not config_path.is_file():
        raise FileNotFoundError(f"config file not found: {config_path}")

    # read the full config file
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    # build root scalar values only
    root_values: dict = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            root_values[key] = value

    # build section values and merge them over the root values
    section_values = data.get(section, {})
    if not isinstance(section_values, dict):
        section_values = {}

    merged_values = dict(root_values)
    merged_values.update(section_values)
    return merged_values
