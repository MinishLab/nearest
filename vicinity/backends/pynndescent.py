from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from numpy import typing as npt
from pynndescent import NNDescent

from vicinity.backends.base import AbstractBackend, BaseArgs
from vicinity.datatypes import Backend, QueryResult
from vicinity.utils import normalize_or_copy


@dataclass
class PyNNDescentArgs(BaseArgs):
    n_neighbors: int = 15
    metric: Literal[
        "cosine",
        "euclidean",
        "manhattan",
    ] = "cosine"


class PyNNDescentBackend(AbstractBackend):
    argument_class = PyNNDescentArgs

    def __init__(
        self,
        index: NNDescent,
        arguments: PyNNDescentArgs,
    ) -> None:
        """Initialize the backend with an NNDescent index."""
        super().__init__(arguments)
        self.index = index

    @classmethod
    def from_vectors(
        cls: type[PyNNDescentBackend],
        vectors: npt.NDArray,
        n_neighbors: int = 15,
        metric: Literal["cosine", "euclidean", "manhattan"] = "cosine",
    ) -> PyNNDescentBackend:
        """Create a new instance from vectors."""
        index = NNDescent(vectors, n_neighbors=n_neighbors, metric=metric)
        arguments = PyNNDescentArgs(n_neighbors=n_neighbors, metric=metric)
        return cls(index=index, arguments=arguments)

    def __len__(self) -> int:
        """Return the number of vectors in the index."""
        return len(self.index._raw_data)

    @property
    def backend_type(self) -> Backend:
        """The type of the backend."""
        return Backend.PYNNDESCENT

    @property
    def dim(self) -> int:
        """The size of the space."""
        return self.index.dim

    def query(self, vectors: npt.NDArray, k: int) -> QueryResult:
        """Batched approximate nearest neighbors search."""
        normalized_vectors = normalize_or_copy(vectors)
        indices, distances = self.index.query(normalized_vectors, k=k)
        return list(zip(indices, distances))

    def insert(self, vectors: npt.NDArray) -> None:
        """Insert vectors into the index (not supported by pynndescent)."""
        raise NotImplementedError("Dynamic insertion is not supported by pynndescent.")

    def delete(self, indices: list[int]) -> None:
        """Delete vectors from the index (not supported by pynndescent)."""
        raise NotImplementedError("Dynamic deletion is not supported by pynndescent.")

    def threshold(self, vectors: npt.NDArray, threshold: float) -> list[npt.NDArray]:
        """Find neighbors within a distance threshold."""
        normalized_vectors = normalize_or_copy(vectors)
        indices, distances = self.index.query(normalized_vectors, k=100)
        result = []
        for idx, dist in zip(indices, distances):
            within_threshold = idx[dist < threshold]
            result.append(within_threshold)
        return result

    def save(self, base_path: Path) -> None:
        """Save the vectors and configuration to a specified path."""
        self.arguments.dump(base_path / "arguments.json")
        np.save(Path(base_path) / "vectors.npy", self.index._raw_data)

        # Optionally save the neighbor graph if it exists and needs to be reused
        if hasattr(self.index, "_neighbor_graph"):
            np.save(Path(base_path / "neighbor_graph.npy"), self.index._neighbor_graph)

    @classmethod
    def load(cls: type[PyNNDescentBackend], base_path: Path) -> PyNNDescentBackend:
        """Load the vectors and configuration from a specified path."""
        arguments = PyNNDescentArgs.load(base_path / "arguments.json")
        vectors = np.load(Path(base_path) / "vectors.npy")
        index = NNDescent(vectors, n_neighbors=arguments.n_neighbors, metric=arguments.metric)

        # Load the neighbor graph if it was saved
        neighbor_graph_path = base_path / "neighbor_graph.npy"
        if neighbor_graph_path.exists():
            index._neighbor_graph = np.load(str(neighbor_graph_path), allow_pickle=True)

        return cls(index=index, arguments=arguments)
