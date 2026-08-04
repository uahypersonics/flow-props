"""Bundled example config registry for flow-props."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files


@dataclass(frozen=True)
class Example:
    """A single bundled example config."""

    # registry key and output filename stem
    name: str
    # one-line description shown in the listing
    description: str
    # filename of the TOML inside flow_props/examples/
    filename: str


# registry of bundled examples, in listing order
_EXAMPLES: tuple[Example, ...] = (
    Example(
        name="sharp_flat_plate_m5",
        description="Mach 5 sharp flat plate (velocity_ratio criterion)",
        filename="sharp_flat_plate_m5.toml",
    ),
    Example(
        name="ogive_m5pt3",
        description="Mach 5.3 ogive (htot_derivative criterion)",
        filename="ogive_m5pt3.toml",
    ),
    Example(
        name="cone_7deg_m14",
        description="7-degree cone, Mach 14.4 (velocity_ratio criterion)",
        filename="cone_7deg_m14.toml",
    ),
)

_REGISTRY: dict[str, Example] = {ex.name: ex for ex in _EXAMPLES}


def available_examples() -> tuple[Example, ...]:
    """Return all bundled examples in listing order."""
    return _EXAMPLES


def available_example_names() -> list[str]:
    """Return the names of all bundled examples."""
    return [ex.name for ex in _EXAMPLES]


def get_example_text(name: str) -> str:
    """Return the TOML text of a bundled example.

    Args:
        name: Registry key of the example.

    Returns:
        The TOML file contents as text.

    Raises:
        KeyError: If no example matches *name*.
    """
    # look up the example by name
    if name not in _REGISTRY:
        raise KeyError(name)

    # read the packaged TOML file
    example = _REGISTRY[name]
    resource = files("flow_props.examples").joinpath(example.filename)
    return resource.read_text(encoding="utf-8")
