from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Generic, TypeVar

from numpy import typing as npt

from vicinity.datatypes import Backend, QueryResult


@dataclass
class BaseArgs:
    def dump(self, file: Path) -> None:
        """Dump the arguments to a file."""
        with open(file, "w") as f:
            json.dump(asdict(self), f)

    @classmethod
    def load(cls: type[ArgType], file: Path) -> ArgType:
        """Load the arguments from a file."""
        with open(file, "r") as f:
            return cls(**json.load(f))

    def dict(self) -> dict[str, Any]:
        """Dump the arguments to a string."""
        return asdict(self)


ArgType = TypeVar("ArgType", bound=BaseArgs)


class AbstractBackend(ABC, Generic[ArgType]):
    argument_class: type[ArgType]

    def __init__(self, arguments: ArgType, *args: Any, **kwargs: Any) -> None:
        """Initialize the backend with vectors."""
        self.arguments = arguments

    @classmethod
    @abstractmethod
    def from_vectors(cls: type[BaseType], vectors: npt.NDArray, *args: Any, **kwargs: Any) -> BaseType:
        """Create a new instance from vectors."""
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        """The number of items in the backend."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def backend_type(self) -> Backend:
        """The type of the backend."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def dim(self) -> int:
        """The size of the space."""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def load(cls: type[BaseType], path: Path) -> BaseType:
        """Load a backend from a file."""
        raise NotImplementedError()

    @abstractmethod
    def save(self, base_path: Path) -> None:
        """Save the backend to a file."""
        raise NotImplementedError()

    @abstractmethod
    def insert(self, vectors: npt.NDArray) -> None:
        """Insert vectors into the backend."""
        raise NotImplementedError()

    @abstractmethod
    def delete(self, indices: list[int]) -> None:
        """Delete vectors from the backend."""
        raise NotImplementedError()

    @abstractmethod
    def threshold(self, vectors: npt.NDArray, threshold: float) -> list[npt.NDArray]:
        """Threshold the backend."""
        raise NotImplementedError()

    @abstractmethod
    def query(self, vectors: npt.NDArray, k: int) -> QueryResult:
        """Query the backend."""
        raise NotImplementedError()


BaseType = TypeVar("BaseType", bound=AbstractBackend)
