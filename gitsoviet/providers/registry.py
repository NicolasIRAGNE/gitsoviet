from __future__ import annotations

from typing import Any, Callable, Dict

from .base import ImageProvider


class ProviderRegistry:
    """Simple provider registry to support multiple backends."""

    def __init__(self) -> None:
        self._providers: Dict[str, Callable[..., ImageProvider]] = {}

    def register(self, name: str, factory: Callable[..., ImageProvider]) -> None:
        self._providers[name.lower()] = factory

    def create(self, name: str, **kwargs: Any) -> ImageProvider:
        key = name.lower()
        if key not in self._providers:
            available = ", ".join(sorted(self._providers)) or "<none>"
            raise ValueError(f"Unknown provider '{name}'. Available: {available}")
        return self._providers[key](**kwargs)

    def choices(self) -> Dict[str, Callable[..., ImageProvider]]:
        return dict(self._providers)
