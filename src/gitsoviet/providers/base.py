from __future__ import annotations

from abc import ABC, abstractmethod

from ..request import PosterRequest


class ImageProvider(ABC):
    @abstractmethod
    def generate_image(self, *, prompt: str, request: PosterRequest) -> bytes:
        raise NotImplementedError
