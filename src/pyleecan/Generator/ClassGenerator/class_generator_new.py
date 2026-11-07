"""Compatibility imports for the experimental dataclass generator."""

from .class_generator import (
    _BASE_TYPES,
    _attribute_docstring,
    _class_docstring,
    _display_default,
    _field_default,
    _field_type,
    _format_source_with_ruff,
    _is_none_default,
    _parent_type,
    _property_description,
    _referenced_classes,
    generate_class_new,
)

__all__ = [
    "_BASE_TYPES",
    "_attribute_docstring",
    "_class_docstring",
    "_display_default",
    "_field_default",
    "_field_type",
    "_format_source_with_ruff",
    "_is_none_default",
    "_parent_type",
    "_property_description",
    "_referenced_classes",
    "generate_class_new",
]
